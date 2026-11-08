// The explainer video (marketing/README.md §9, decisions 089–091): the mess students start from, then the site's best
// features, each opened with a cursor: the programs and when to apply, the الرواد star map, the explorer's filters,
// the universities in their order, the University of Minnesota's next date and English tests, its official admissions
// page one tap away, then وضّاح «قادم في ديسمبر» answering two questions in a chat. Arabic only.
// $0: Microsoft Edge (already installed) films explainer_stage.html frame by frame over the DevTools protocol, the
// music is synthesised in explainer_music.mjs, ffmpeg encodes. Nothing is uploaded anywhere.
//
//   1. Start the site:  uvicorn app.main:app   (or the preview server)
//   2. node marketing/src/explainer.mjs [--site http://127.0.0.1:8000] [--voice <folder>] [--skip-capture]
//                                       [--stills 3,12,40] [--fps 60] [--audio-only]
//
// Output: marketing/out/wadih-explainer-ar-9x16.mp4 (1080×1920), or …-9x16-<voice>.mp4 with --voice. Screens are
// re-captured from the site on every run (so dates on screen are today's), into marketing/assets/explainer/ar/; the
// university's official page is captured live from its own site.
// Words: explainer_script.json. Voice (optional, --voice nourah): marketing/assets/explainer/voice/ar/<folder>/<line id>.wav
// (make_voice_humain.mjs makes them): a scene grows (in half bars, to stay on the beat) to fit its clips and the music
// steps back under them. Without --voice the video has music and sounds only.
// Music (optional): marketing/assets/explainer/music.mp3|.wav replaces the synthesised track (the sounds stay).

import { spawn, execFileSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, readFileSync, readdirSync, renameSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { soundtrack } from "./explainer_music.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const argv = process.argv.slice(2);
const opt = (name, dflt) => { const i = argv.indexOf(`--${name}`); return i >= 0 && argv[i + 1] ? argv[i + 1] : dflt; };
const SITE = opt("site", "http://127.0.0.1:8000").replace(/\/$/, "");
const FPS = 60; // the composition's (marketing/video/src/Root.tsx)
const STILLS = opt("stills", null);
const VOICE = opt("voice", null);
const SKIP_CAPTURE = argv.includes("--skip-capture");
// Rebuild only the soundtrack and swap it into the last video (same timing only: no new voice clips).
const AUDIO_ONLY = argv.includes("--audio-only");
const EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const ASSETS = join(ROOT, "marketing", "assets", "explainer");
const SHOTS = join(ASSETS, "ar");
const OUT = join(ROOT, "marketing", "out");
const SCRIPT = JSON.parse(readFileSync(join(ROOT, "marketing", "src", "explainer_script.json"), "utf8"));
const F = SCRIPT.filters;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const details = (id) => JSON.parse(readFileSync(join(ROOT, "data", "university_details", `${id}.json`), "utf8"));

// ---------- Edge over the Chrome DevTools Protocol (as in capture_site.mjs) ----------
async function edge(port, flags = []) {
  const profile = join(ROOT, "marketing", ".edge-profile", `explainer-${port}`);
  rmSync(profile, { recursive: true, force: true, maxRetries: 20, retryDelay: 250 });
  const proc = spawn(EDGE, ["--headless=new", `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`,
    "--hide-scrollbars", "--no-first-run", "--mute-audio", ...flags, "about:blank"], { stdio: "ignore" });
  let target;
  for (let i = 0; i < 60 && !target; i++) {
    await sleep(250);
    try { target = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find((t) => t.type === "page"); } catch {}
  }
  if (!target) throw new Error("Edge did not start");
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener("open", r, { once: true }));
  let nextId = 1;
  const pending = new Map(), waiters = [];
  ws.addEventListener("message", (e) => {
    const msg = JSON.parse(e.data);
    if (msg.id && pending.has(msg.id)) {
      const { ok, fail } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? fail(new Error(JSON.stringify(msg.error))) : ok(msg.result);
    } else if (msg.method) {
      for (const w of [...waiters]) if (w.method === msg.method) { waiters.splice(waiters.indexOf(w), 1); w.ok(msg.params); }
    }
  });
  const send = (method, params = {}) => new Promise((ok, fail) => {
    const id = nextId++;
    pending.set(id, { ok, fail });
    ws.send(JSON.stringify({ id, method, params }));
  });
  const once = (method) => new Promise((ok) => waiters.push({ method, ok }));
  const js = async (expr) => {
    const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text);
    return r.result.value;
  };
  await send("Page.enable");
  await send("Runtime.enable");
  // Closing waits for Edge to exit, so the next run can reuse its profile folder.
  const exited = new Promise((r) => proc.once("exit", r));
  return { send, once, js, close: async () => { ws.close(); proc.kill(); await exited; } };
}

// ---------- 1. Capture the site at phone size ----------
// 390 CSS px wide on a 640 px screen; the page sits under a 52 px status bar, so 724 CSS px of it show.
const W = 390, H = 724, DSF = 2;

async function capture() {
  rmSync(SHOTS, { recursive: true, force: true });
  mkdirSync(SHOTS, { recursive: true });
  const b = await edge(9351, ["--lang=ar"]);
  const metrics = () => b.send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: DSF, mobile: true });
  await metrics();
  await b.send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });
  await b.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }, { name: "prefers-reduced-motion", value: "reduce" }] });
  const screens = {}, rects = {}, menus = {};

  async function go(url) {
    const loaded = b.once("Page.loadEventFired");
    await b.send("Page.navigate", { url: url.startsWith("http") ? url : SITE + url });
    await Promise.race([loaded, sleep(25000)]);
    await b.js("document.fonts.ready.then(() => true)");
    // Lazy images below the fold never load in a whole-page capture: load them all first (the program logos).
    await b.js(`Promise.all([...document.images].map((i) => { i.loading = "eager"; return i.decode().catch(() => null); })).then(() => true)`);
    await sleep(900);
  }
  // Every capture starts at the page's top: Edge at 2× density shifts any capture that doesn't (by the scroll, or a
  // clip's y), so the stage does all the scrolling.
  async function shot(name) {
    await b.js("window.scrollTo({ top: 0, behavior: 'instant' })");
    const { data } = await b.send("Page.captureScreenshot", { format: "png" });
    writeFileSync(join(SHOTS, `${name}.png`), Buffer.from(data, "base64"));
    screens[name] = { file: `${name}.png`, h: H, vh: H };
  }
  async function full(name, maxH) {
    await b.js("window.scrollTo({ top: 0, behavior: 'instant' })");
    const h = Math.min(await b.js("document.documentElement.scrollHeight"), Math.ceil(maxH));
    const { data } = await b.send("Page.captureScreenshot", {
      format: "png", captureBeyondViewport: true, clip: { x: 0, y: 0, width: W, height: h, scale: 1 },
    });
    writeFileSync(join(SHOTS, `${name}.png`), Buffer.from(data, "base64"));
    await metrics();
    screens[name] = { file: `${name}.png`, h, vh: H };
  }
  // A visible element's box in page coordinates (CSS px).
  const BOX = `(e) => { if (!e) return null; const r = e.getBoundingClientRect(); return { x: r.x, y: r.y + window.scrollY, w: r.width, h: r.height }; }`;
  const box = (expr) => b.js(`(${BOX})(${expr})`);
  const need = (v, what) => { if (!v) throw new Error(`not found on the site: ${what}`); return v; };

  // The homepage: «الآن», the programs with their dates, one card each.
  await go("/");
  rects.home = need(await b.js(`(() => {
    const B = ${BOX};
    const sec = document.querySelector('section.now');
    if (!sec) return null;
    const items = [...sec.querySelectorAll('.now-item')].map((it) => ({ card: B(it), status: B(it.querySelector('.now-status')) }));
    return { now: B(sec.querySelector('h2')), items };
  })()`), "the «الآن» section");
  if (!rects.home.items.length || !rects.home.items[0].status) throw new Error("no program card with a status in «الآن»");
  const lastCard = rects.home.items[rects.home.items.length - 1].card;
  await full("home", lastCard.y + lastCard.h + 200);

  // The الرواد page: its star chart (each star with its rank and name), the line under it, the filters button.
  await go("/universities?track=arruaad");
  rects.rw = need(await b.js(`(() => {
    const B = ${BOX};
    const chart = document.querySelector('[data-chart]');
    if (!chart) return null;
    const stars = [...chart.querySelectorAll('.chart-star')].map((s) => {
      const r = B(s.querySelector('.chart-star-shape') || s);
      return { rank: s.dataset.rank, name: s.dataset.name, x: r.x + r.w / 2, y: r.y + r.h / 2 };
    });
    return { chart: B(chart), readout: B(chart.querySelector('[data-chart-readout]')), stars,
      toggle: B(document.querySelector('[data-filters-toggle]')) };
  })()`), "the الرواد chart");
  if (!rects.rw.toggle) throw new Error("not found on the site: the filters button");
  const star = rects.rw.stars.find((s) => s.rank === F.star_rank) || rects.rw.stars[0];
  rects.rw.star = star;
  await full("rw0", rects.rw.toggle.y + 1400);
  // Pointing at a star names it under the chart (universities.js).
  rects.rw.hover = await b.js(`(() => {
    const s = document.querySelector('.chart-star[data-rank="${star.rank}"]');
    s.dispatchEvent(new PointerEvent('pointerover', { bubbles: true }));
    return document.querySelector('[data-chart-readout]').textContent.trim();
  })()`);
  await full("rw1", rects.rw.toggle.y + 1400);
  await b.js(`document.querySelector('.chart-star[data-rank="${star.rank}"]').dispatchEvent(new PointerEvent('pointerout', { bubbles: true }))`);

  // The filters, opened on the same page, then each menu's real options with them.
  await b.js("document.querySelector('[data-filters-toggle]').click()");
  await sleep(400);
  const reopen = async () => {
    // A whole-page capture resizes the page for a moment, which can fold the panel again.
    await b.js(`(() => { const t = document.querySelector('[data-filters-toggle]'); if (t.getAttribute('aria-expanded') !== 'true') t.click(); })()`);
    await sleep(300);
  };
  const state = async () => ({
    toggle: need(await box("document.querySelector('[data-filters-toggle]')"), "the filters button"),
    track: need(await box("document.querySelector('#track')"), "#track"),
    field: need(await box("document.querySelector('#field')"), "#field"),
    country: need(await box("document.querySelector('#country')"), "#country"),
    applied: await box("document.querySelector('.applied')"),
  });
  // The options a menu shows now (the field menu shows only the chosen track's group), and which one we pick.
  const options = (id, value) => b.js(`(() => {
    const s = document.getElementById('${id}');
    const opts = [...s.options].filter((o) => !o.disabled && !o.hidden && !(o.parentElement.tagName === 'OPTGROUP' && (o.parentElement.disabled || o.parentElement.hidden)));
    const track = document.getElementById('track').value;
    const shown = opts.filter((o) => o.parentElement.tagName !== 'OPTGROUP' || o.parentElement.dataset.track === track);
    return { items: shown.map((o) => o.textContent.trim()), current: shown.findIndex((o) => o.selected), pick: shown.findIndex((o) => o.value === '${value}') };
  })()`);
  const TRACK_Y = 190;
  await reopen();
  rects.f0 = await state();
  menus.track = await options("track", F.track);
  await full("f0", rects.f0.track.y + 2200);
  screens.f0.hold = Math.max(0, Math.round(rects.f0.track.y - TRACK_Y));
  const choose = async (id, value, name, nextId, nextValue) => {
    await b.js(`(() => { const s = document.getElementById('${id}'); s.value = '${value}'; s.dispatchEvent(new Event('change', { bubbles: true })); })()`);
    await sleep(1400);
    await reopen();
    rects[name] = await state();
    if (nextId) menus[nextId] = await options(nextId, nextValue);
    await full(name, rects[name].track.y + 2600);
    screens[name].hold = Math.max(0, Math.round(rects[name].track.y - TRACK_Y));
  };
  await choose("track", F.track, "f1", "field", F.field);
  await choose("field", F.field, "f2", "country", F.country);
  await choose("country", F.country, "f3");
  for (const [k, m] of Object.entries(menus)) if (m.pick < 0) throw new Error(`the ${k} menu has no option «${F[k]}»`);

  // The results, in their order on the list, down to the University of Minnesota.
  await go(`/universities?track=${F.track}&field=${F.field}&country=${F.country}`);
  rects.results = {
    applied: need(await box("document.querySelector('.applied')"), "the applied filters"),
    rows: await b.js(`[...document.querySelectorAll('table.uni-table tbody tr')].map((tr) => {
      const b = ${BOX};
      const link = tr.querySelector('a[href*="/universities/"]');
      return { href: link.getAttribute('href'), mine: link.getAttribute('href').includes('/${F.university}'),
        row: b(tr), rank: b(tr.querySelector('.uni-rank')), name: b(link) };
    })`),
  };
  const mine = rects.results.rows.find((r) => r.mine);
  if (!mine) throw new Error(`${F.university} is not in the results for these filters`);
  await full("results", Math.ceil(mine.row.y + mine.row.h + 900));

  // Its own page: the next date, the English tests, and the button to its official admissions page.
  const u = new URL(mine.href, SITE);
  await go(u.pathname + u.search);
  const row = (label) => `[...document.querySelectorAll('.uni-summary .summary-row')].find((r) => r.querySelector('${label}'))`;
  rects.uni = {
    date: need(await box(row(".summary-date")), "the next date"),
    english: need(await box(row(".glance-tests")), "the English tests"),
    button: need(await box("document.querySelector('.uni-summary .actions .btn--primary') || document.querySelector('.actions .btn--primary')"), "the admissions button"),
    href: await b.js("(document.querySelector('.uni-summary .actions .btn--primary') || document.querySelector('.actions .btn--primary')).href"),
  };
  await full("uni", rects.uni.button.y + 900);

  // Where that button goes: the university's own page, as a student's phone would open it.
  await go(rects.uni.href);
  rects.official = { url: await b.js("location.href"), host: await b.js("location.hostname") };
  await shot("official");

  writeFileSync(join(SHOTS, "screens.json"), JSON.stringify({ W, H, DSF, site: SITE, captured: new Date().toISOString(), screens, rects, menus }, null, 2));
  await b.close();
  console.log(`captured ${Object.keys(screens).length} screens; the button opens ${rects.official.host}; hovering star ${star.rank} reads «${rects.rw.hover}»`);
}

// ---------- 2. The plan: scene times on the beat, stretched to fit any voice clips ----------
const BEAT = 60 / SCRIPT.bpm, BAR = 4 * BEAT;
function probe(file) {
  return Number(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", file]).toString().trim());
}
function voiceFile(id) {
  if (!VOICE) return null;
  for (const ext of ["wav", "mp3", "m4a"]) {
    const f = join(ASSETS, "voice", "ar", VOICE, `${id}.${ext}`);
    if (existsSync(f)) return f;
  }
  return null;
}
function plan() {
  let t = 0;
  const scenes = [];
  for (const s of SCRIPT.scenes) {
    let cursor = 0, end = 0;
    const lines = s.lines.map((l) => {
      const voice = voiceFile(l.id);
      const vdur = voice ? probe(voice) : null;
      const at = Math.max(l.at * BEAT, cursor);
      cursor = at + (vdur ? vdur + 0.25 : 0);
      end = Math.max(end, at + (vdur || 0));
      const until = l.until != null ? Math.max(l.until * BEAT, at + (vdur || 0) + 0.3) : null;
      return { id: l.id, text: l.text, at, until, voice, vdur };
    });
    const base = s.bars * BAR;
    const dur = Math.max(base, Math.ceil((end + 0.6) / (BAR / 2)) * (BAR / 2));
    scenes.push({ id: s.id, start: t, dur, lines });
    t += dur;
  }
  if (VOICE && !scenes.some((s) => s.lines.some((l) => l.voice))) throw new Error(`no clips in marketing/assets/explainer/voice/ar/${VOICE}/`);
  return { scenes, total: t, beat: BEAT, bar: BAR };
}

// وضّاح's answers come from the site itself: the first is the Duolingo guide's own steps (checked against the page,
// so it can't drift from it), the second is the university's sourced minimum from its data file.
function chatConfig() {
  const c = SCRIPT.chat;
  const page = readFileSync(join(ROOT, c.a1_page), "utf8");
  for (const bit of c.a1_check) if (!page.includes(bit)) throw new Error(`${c.a1_page} no longer says «${bit}»: update the chat's first answer`);
  const d = details(c.a2_university);
  const test = d.english?.[c.a2_test];
  if (!test?.note_ar || !test.source_url) throw new Error(`${c.a2_university}: no sourced ${c.a2_test} note to answer with`);
  return {
    greeting: c.greeting, placeholder: c.placeholder,
    q1: c.q1, a1: c.a1, src1: new URL(c.a1_source).hostname,
    q2: c.q2, a2: `${c.a2_prefix} ${test.note_ar}`, src2: new URL(test.source_url).hostname,
  };
}

// ---------- 3. Film it with Remotion (marketing/video) ----------
// The composition reads public/: data.json (the plan, the captured screens and their rects, the menus, the chat), the
// screens, the site's fonts and logo, وضّاح's poses, and the soundtrack. timeline.mjs gives the picture and the music
// the same times.
const VIDEO = join(ROOT, "marketing", "video");
const PUB = join(VIDEO, "public");
const POSES = ["wave", "present", "point", "clipboard", "cheer", "laptop", "read"];
function copyInto(dir, files) {
  rmSync(dir, { recursive: true, force: true });
  mkdirSync(dir, { recursive: true });
  for (const [from, name] of files) copyFileSync(from, join(dir, name));
}
function remotion(args) {
  execFileSync("npx", ["remotion", ...args], { cwd: VIDEO, stdio: "inherit", shell: true });
}
async function render() {
  const cap = JSON.parse(readFileSync(join(SHOTS, "screens.json"), "utf8"));
  const p = plan();
  const data = { plan: p, screens: cap.screens, rects: cap.rects, menus: cap.menus, text: SCRIPT.screen, chat: chatConfig() };
  const mascot = join(ASSETS, "..", "waddah");
  for (const pose of POSES) if (!existsSync(join(mascot, `${pose}.webp`))) throw new Error(`وضّاح's pose is missing: marketing/assets/waddah/${pose}.webp`);
  copyInto(join(PUB, "shots"), Object.values(cap.screens).map((s) => [join(SHOTS, s.file), s.file]));
  const fonts = join(ROOT, "app", "static", "fonts");
  copyInto(join(PUB, "fonts"), readdirSync(fonts).filter((f) => f.endsWith(".woff2")).map((f) => [join(fonts, f), f]));
  copyInto(join(PUB, "waddah"), POSES.map((pose) => [join(mascot, `${pose}.webp`), `${pose}.webp`]));
  copyFileSync(join(ROOT, "app", "static", "favicon.svg"), join(PUB, "logo.svg"));
  writeFileSync(join(PUB, "data.json"), JSON.stringify(data));
  const { buildTimeline } = await import(pathToFileURL(join(VIDEO, "src", "timeline.mjs")).href);
  const tl = buildTimeline(data);
  const voiced = p.scenes.flatMap((s) => s.lines).filter((l) => l.voice).length;
  console.log(`${p.total.toFixed(1)} s, ${voiced} voice clip(s), ${FPS} fps`);

  if (STILLS) {
    const dir = join(OUT, "explainer-stills");
    rmSync(dir, { recursive: true, force: true });
    const frames = STILLS.split(",").map((s) => Math.round(Number(s) * FPS));
    mkdirSync(dir, { recursive: true });
    const props = join(dir, "props.json");
    writeFileSync(props, JSON.stringify({ audio: null }));
    remotion(["render", "WadihExplainer", dir, "--sequence", `--frames=${frames.join(",")}`, "--image-format=png", `--props=${props}`, "--log=error"]);
    rmSync(props);
    console.log(`stills in ${dir}`);
    return;
  }

  const music = ["mp3", "wav", "m4a"].map((e) => join(ASSETS, `music.${e}`)).find(existsSync) || null;
  soundtrack(p, tl.events, join(PUB, "soundtrack.wav"), { music, sfxOnly: join(PUB, "sfx-only.wav") });
  mkdirSync(OUT, { recursive: true });
  const out = join(OUT, `wadih-explainer-ar-9x16${VOICE ? `-${VOICE}` : ""}.mp4`);
  // The same picture with the sounds but no music (Shotcraft's rule: so a licensed track can go under it later).
  const swap = (wav, to) => execFileSync("ffmpeg", ["-y", "-v", "error", "-i", out, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", to]);
  if (AUDIO_ONLY) {
    if (!existsSync(out)) throw new Error("no video to put the soundtrack in: run without --audio-only first");
    if (Math.abs(probe(out) - p.total) > 0.1) throw new Error("the timing changed (a new voice clip?): run without --audio-only");
    const tmp = out.replace(/\.mp4$/, ".tmp.mp4");
    swap(join(PUB, "soundtrack.wav"), tmp);
    rmSync(out);
    renameSync(tmp, out);
  } else {
    remotion(["render", "WadihExplainer", out, "--codec=h264", "--crf=17", "--pixel-format=yuv420p", "--audio-codec=aac", "--audio-bitrate=256k", "--log=error"]);
  }
  swap(join(PUB, "sfx-only.wav"), out.replace(/\.mp4$/, "-no-music.mp4"));
  console.log(`wrote ${out} (and …-no-music.mp4)`);
}

if (!SKIP_CAPTURE && !AUDIO_ONLY) await capture();
if (!argv.includes("--capture-only")) await render();
