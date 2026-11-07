// The explainer video (marketing/README.md §9): the universities explorer, its filters and order, a university's
// requirements and next date with their sources, and وضّاح coming in December, told by وضّاح's own agent.
// $0: Microsoft Edge (already installed) films explainer_stage.html frame by frame over the DevTools protocol,
// ffmpeg encodes. Nothing is uploaded anywhere.
//
//   1. Start the site:  uvicorn app.main:app   (or the preview server)
//   2. node marketing/src/explainer.mjs [--site http://127.0.0.1:8000] [--lang ar|en|both] [--skip-capture] [--stills 3,12,40]
//
// Output: marketing/out/wadih-explainer-<lang>-9x16.mp4 (1080×1920, 30 fps). Screens are re-captured from the site on
// every run (so dates on screen are today's), into marketing/assets/explainer/<lang>/.
// Words: explainer_script.json. Voice (optional): marketing/assets/explainer/voice/<lang>/<line id>.wav|.mp3; a scene
// grows to fit its clips and the music ducks under them. Without clips the video is captions + music.

import { spawn, execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const argv = process.argv.slice(2);
const opt = (name, dflt) => { const i = argv.indexOf(`--${name}`); return i >= 0 && argv[i + 1] ? argv[i + 1] : dflt; };
const SITE = opt("site", "http://127.0.0.1:8000").replace(/\/$/, "");
const LANGS = opt("lang", "both") === "both" ? ["ar", "en"] : [opt("lang")];
const FPS = Number(opt("fps", "30"));
const STILLS = opt("stills", null);
const SKIP_CAPTURE = argv.includes("--skip-capture");
const EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const ASSETS = join(ROOT, "marketing", "assets", "explainer");
const OUT = join(ROOT, "marketing", "out");
const SCRIPT = JSON.parse(readFileSync(join(ROOT, "marketing", "src", "explainer_script.json"), "utf8"));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

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
const W = 390, H = 755, DSF = 2;

async function capture(lang) {
  const dir = join(ASSETS, lang);
  rmSync(dir, { recursive: true, force: true });
  mkdirSync(dir, { recursive: true });
  const b = await edge(9351, [`--lang=${lang}`]);
  const metrics = (h = H) => b.send("Emulation.setDeviceMetricsOverride", { width: W, height: h, deviceScaleFactor: DSF, mobile: true });
  await metrics();
  await b.send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });
  await b.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }, { name: "prefers-reduced-motion", value: "reduce" }] });
  const pre = lang === "en" ? "/en" : "";
  const screens = {}, rects = {};

  async function go(path) {
    const loaded = b.once("Page.loadEventFired");
    await b.send("Page.navigate", { url: SITE + path });
    await loaded;
    await b.js("document.fonts.ready.then(() => true)");
    await sleep(700);
  }
  const scrollY = () => b.js("window.scrollY");
  // The top of the page, as the phone shows it. (Edge at 2× density shifts any capture that doesn't start at the
  // page's top, by the scroll or a clip's y, so every capture here starts at y = 0 and the stage does the scrolling.)
  async function shot(name) {
    await b.js("window.scrollTo({ top: 0, behavior: 'instant' })");
    const { data } = await b.send("Page.captureScreenshot", { format: "png" });
    writeFileSync(join(dir, `${name}.png`), Buffer.from(data, "base64"));
    screens[name] = { file: `${name}.png`, h: H, vh: H, scroll: 0 };
  }
  // The page from the top down to maxH CSS px, as one tall image (the stage scrolls it).
  async function full(name, maxH) {
    await b.js("window.scrollTo(0, 0)");
    const h = Math.min(await b.js("document.documentElement.scrollHeight"), maxH);
    const { data } = await b.send("Page.captureScreenshot", {
      format: "png", captureBeyondViewport: true, clip: { x: 0, y: 0, width: W, height: h, scale: 1 },
    });
    writeFileSync(join(dir, `${name}.png`), Buffer.from(data, "base64"));
    await metrics();
    screens[name] = { file: `${name}.png`, h, vh: H, scroll: 0 };
  }
  // A visible element's box in page coordinates (CSS px).
  const box = (expr) => b.js(`(() => { const e = ${expr}; if (!e) return null; const r = e.getBoundingClientRect();
    return { x: r.x, y: r.y + window.scrollY, w: r.width, h: r.height }; })()`);
  const need = (v, what) => { if (!v) throw new Error(`not found on the ${lang} site: ${what}`); return v; };

  // The explorer, then its filters one by one.
  await go(`${pre}/universities`);
  rects.explorer = {
    q: need(await box("document.querySelector('#q')"), "#q"),
    toggle: need(await box("document.querySelector('[data-filters-toggle]')"), "the filters button"),
  };
  await shot("explorer");
  // Tap «الفلاتر»: the panel opens below it. Captured whole (from the top), so the stage can scroll down to it.
  await b.js("document.querySelector('[data-filters-toggle]').click()");
  await sleep(400);
  // Each filter can reflow the page (الرواد's opening leaves when the track changes), so every state is held with
  // the «المسار» menu at the same height on screen, and measured on its own.
  const TRACK_Y = 200;
  // A whole-page capture resizes the page for a moment, which can fold the panel again: reopen it if so.
  const reopen = async () => {
    await b.js(`(() => { const t = document.querySelector('[data-filters-toggle]'); if (t.getAttribute('aria-expanded') !== 'true') t.click(); })()`);
    await sleep(300);
  };
  const selects = async () => ({
    track: need(await box("document.querySelector('#track')"), "#track"),
    field: need(await box("document.querySelector('#field')"), "#field"),
    country: need(await box("document.querySelector('#country')"), "#country"),
  });
  rects.f0 = await selects();
  await full("f0", 2400);
  screens.f0.hold = Math.max(0, Math.round(rects.f0.track.y - TRACK_Y));
  const choose = async (id, value, name) => {
    await b.js(`(() => { const s = document.getElementById('${id}'); s.value = '${value}'; s.dispatchEvent(new Event('change', { bubbles: true })); })()`);
    await sleep(1200);
    await reopen();
    rects[name] = await selects();
    await full(name, 2400);
    screens[name].scroll = Math.max(0, Math.round(rects[name].track.y - TRACK_Y));
  };
  await choose("track", "emdad", "f1");
  await choose("field", "ict", "f2");
  await choose("country", "GB", "f3");

  // The results: the order on the track's list, then each row's English tests and next date.
  await go(`${pre}/universities?track=emdad&field=ict&country=GB`);
  rects.results = {
    applied: need(await box("document.querySelector('.applied')"), "the applied filters"),
    explain: need(await box("document.querySelector('.result-explain')"), "the rank note"),
    rows: await b.js(`[...document.querySelectorAll('table.uni-table tbody tr')].map((tr) => {
      const b = (e) => { if (!e) return null; const r = e.getBoundingClientRect(); return { x: r.x, y: r.y + window.scrollY, w: r.width, h: r.height }; };
      const link = tr.querySelector('a[href*="/universities/"]');
      const cells = [...tr.querySelectorAll('.kf-cell')];
      return { href: link.getAttribute('href'), manchester: link.getAttribute('href').includes('university-of-manchester'),
        row: b(tr), rank: b(tr.querySelector('.uni-rank')), name: b(link),
        english: b(tr.querySelector('.kf-cell--english')), date: b(cells.find((c) => c.querySelector('.kf-date')) || cells[cells.length - 1]) };
    })`),
  };
  if (rects.results.rows.length < 2) throw new Error("expected at least 2 rows in the results");
  await full("results", 3600);

  // A university's page: its summary, the next date and that date's official source.
  const manc = rects.results.rows.find((r) => r.manchester) || rects.results.rows.at(-1);
  await go(new URL(manc.href, SITE).pathname + new URL(manc.href, SITE).search);
  rects.uni = {
    date: need(await box("[...document.querySelectorAll('.uni-summary .summary-row')].find((r) => r.querySelector('.summary-date'))"), "the next date"),
    src: need(await box("[...document.querySelectorAll('.uni-summary .summary-row')].find((r) => r.querySelector('.summary-date'))?.querySelector('a.src')"), "the date's source"),
  };
  await full("uni", 2600);

  writeFileSync(join(dir, "screens.json"), JSON.stringify({ W, H, DSF, site: SITE, captured: new Date().toISOString(), screens, rects }, null, 2));
  await b.close();
  console.log(`[${lang}] captured ${Object.keys(screens).length} screens`);
}

// ---------- 2. The plan: scene times, stretched to fit any voice clips ----------
function probe(file) {
  return Number(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", file]).toString().trim());
}
function voiceFile(lang, id) {
  for (const ext of ["wav", "mp3", "m4a"]) {
    const f = join(ASSETS, "voice", lang, `${id}.${ext}`);
    if (existsSync(f)) return f;
  }
  return null;
}
function plan(lang) {
  let t = 0;
  const scenes = [];
  for (const s of SCRIPT.scenes) {
    let cursor = 0, end = 0;
    const lines = s.lines.map((l) => {
      const voice = voiceFile(lang, l.id);
      const vdur = voice ? probe(voice) : null;
      const at = Math.max(l.at, cursor);
      const dur = vdur ?? 0;
      cursor = at + dur + (vdur ? 0.25 : 0);
      end = Math.max(end, at + dur);
      return { id: l.id, text: l[lang], at, voice, vdur };
    });
    const dur = Math.max(s.dur, end + 0.7);
    scenes.push({ id: s.id, start: t, dur, lines });
    t += dur;
  }
  return { scenes, total: t };
}

// ---------- 3. Music and sounds, synthesised here (no outside library, no licence question) ----------
const SR = 48000;
const NOTE = { D2: 73.42, E2: 82.41, G2: 98.0, A2: 110.0, B2: 123.47, D3: 146.83, E3: 164.81, Fs3: 185.0, G3: 196.0, A3: 220.0, B3: 246.94,
  Cs4: 277.18, D4: 293.66, E4: 329.63, Fs4: 369.99, D5: 587.33, Fs5: 739.99, A5: 880.0, D6: 1174.66 };
const CHORDS = {
  Dmaj9: ["D3", "A3", "Cs4", "E4", "Fs4"], Bm7: ["B2", "Fs3", "A3", "D4", "Fs4"], Gmaj9: ["G2", "D3", "Fs3", "A3", "B3"],
  Asus: ["A2", "E3", "A3", "B3", "D4"], Em9: ["E2", "B2", "D3", "Fs3", "G3"],
};
const SCENE_CHORD = { hook: "Bm7", brand: "Dmaj9", explorer: "Gmaj9", filters: "Asus", results: "Dmaj9", row: "Bm7", uni: "Gmaj9", waddah: "Em9", end: "Dmaj9" };

function decodeVoice(file) {
  const raw = execFileSync("ffmpeg", ["-v", "error", "-i", file, "-f", "f32le", "-ac", "1", "-ar", String(SR), "-"], { maxBuffer: 1 << 28 });
  return new Float32Array(raw.buffer, raw.byteOffset, raw.byteLength / 4);
}

function soundtrack(p, events, file) {
  const n = Math.ceil((p.total + 0.5) * SR);
  const L = new Float32Array(n), Rr = new Float32Array(n);
  // The pad: one soft chord per scene, crossfading.
  p.scenes.forEach((s, i) => {
    const notes = CHORDS[SCENE_CHORD[s.id] || "Dmaj9"];
    const a = s.start, b = s.start + s.dur, att = 0.9, rel = 1.6;
    const i0 = Math.max(0, Math.floor((a - 0.2) * SR)), i1 = Math.min(n, Math.ceil((b + rel) * SR));
    notes.forEach((name, j) => {
      const f = NOTE[name], amp = 0.05 * (j === 0 ? 1.15 : 1), pan = (j / (notes.length - 1)) * 0.6 - 0.3;
      for (let k = i0; k < i1; k++) {
        const t = k / SR;
        const env = t < a ? 0 : Math.min(1, (t - a) / att) * (t > b ? Math.max(0, 1 - (t - b) / rel) : 1);
        if (env <= 0) continue;
        const v = (Math.sin(2 * Math.PI * f * t) + Math.sin(2 * Math.PI * f * 1.0018 * t + j) * 0.7 + Math.sin(4 * Math.PI * f * t) * 0.12)
          * amp * env * (0.85 + 0.15 * Math.sin(2 * Math.PI * 0.21 * t + j * 1.3));
        L[k] += v * (0.5 - pan); Rr[k] += v * (0.5 + pan);
      }
    });
  });
  // Events: a bell for reveals, a soft tick for taps, a breath of air for big moves.
  const add = (t0, dur, fn) => {
    const i0 = Math.max(0, Math.floor(t0 * SR)), i1 = Math.min(n, Math.ceil((t0 + dur) * SR));
    for (let k = i0; k < i1; k++) { const [l, r] = fn((k - i0) / SR); L[k] += l; Rr[k] += r; }
  };
  const bell = (t0, f, amp, pan) => add(t0, 2.2, (t) => {
    const v = (Math.sin(2 * Math.PI * f * t) + 0.25 * Math.sin(2 * Math.PI * f * 2.76 * t) * Math.exp(-t * 6)) * Math.exp(-t * 2.4) * amp;
    return [v * (0.5 - pan), v * (0.5 + pan)];
  });
  let seed = 3;
  const noise = () => ((seed = (seed * 16807) % 2147483647) / 2147483647) * 2 - 1;
  for (const e of events) {
    if (e.type === "chime" || e.type === "spark") {
      const seq = e.type === "spark" ? ["A5", "D6"] : ["D5", "Fs5", "A5", "D6"];
      seq.forEach((nm, i) => bell(e.t + i * 0.11, NOTE[nm], e.type === "spark" ? 0.05 : 0.045, (i - 1.5) * 0.12));
    } else if (e.type === "tap") {
      add(e.t, 0.08, (t) => { const v = (Math.sin(2 * Math.PI * 1700 * t) * 0.6 + Math.sin(2 * Math.PI * 2550 * t) * 0.4) * Math.exp(-t * 70) * 0.09; return [v, v]; });
    } else if (e.type === "whoosh") {
      let lp = 0;
      add(e.t - 0.1, 0.9, (t) => {
        const env = Math.sin(Math.PI * Math.min(1, t / 0.9)) ** 2;
        const c = 0.02 + 0.12 * env; lp += c * (noise() - lp);
        const v = lp * env * 0.22; return [v, v];
      });
    }
  }
  // Voice clips on top; the music steps back under them.
  const duck = new Float32Array(n).fill(1);
  const voice = new Float32Array(n);
  for (const s of p.scenes) for (const l of s.lines) {
    if (!l.voice) continue;
    const v = decodeVoice(l.voice), i0 = Math.floor((s.start + l.at) * SR);
    for (let k = 0; k < v.length && i0 + k < n; k++) voice[i0 + k] += v[k];
    const d0 = Math.max(0, i0 - SR * 0.25), d1 = Math.min(n, i0 + v.length + SR * 0.35);
    for (let k = d0; k < d1; k++) duck[k] = 0.38;
  }
  let g = 1;
  for (let k = 0; k < n; k++) { g += (duck[k] - g) * 0.0004; L[k] = L[k] * g + voice[k]; Rr[k] = Rr[k] * g + voice[k]; }
  // Fades and a gentle ceiling.
  let peak = 0;
  for (let k = 0; k < n; k++) {
    const t = k / SR, f = Math.min(1, t / 0.3) * Math.min(1, Math.max(0, (p.total + 0.3 - t) / 1.6));
    L[k] *= f; Rr[k] *= f; peak = Math.max(peak, Math.abs(L[k]), Math.abs(Rr[k]));
  }
  // With a voice, the voice sets the level (only a ceiling); without one, the music is all there is: bring it up.
  const voiced = voice.some((v) => v !== 0);
  const scale = voiced ? (peak > 0.89 ? 0.89 / peak : 1) : 0.56 / peak;
  const buf = Buffer.alloc(44 + n * 4);
  buf.write("RIFF", 0); buf.writeUInt32LE(36 + n * 4, 4); buf.write("WAVE", 8); buf.write("fmt ", 12);
  buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22); buf.writeUInt32LE(SR, 24);
  buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write("data", 36); buf.writeUInt32LE(n * 4, 40);
  for (let k = 0; k < n; k++) {
    buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, L[k] * scale)) * 32767), 44 + k * 4);
    buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, Rr[k] * scale)) * 32767), 46 + k * 4);
  }
  writeFileSync(file, buf);
}

// ---------- 4. Film the stage ----------
async function render(lang) {
  const cap = JSON.parse(readFileSync(join(ASSETS, lang, "screens.json"), "utf8"));
  const p = plan(lang);
  const text = Object.fromEntries(Object.entries(SCRIPT.screen).map(([k, v]) => [k, v[lang]]));
  const screens = Object.fromEntries(Object.entries(cap.screens).map(([k, v]) => [k, { ...v, src: pathToFileURL(join(ASSETS, lang, v.file)).href }]));
  const config = { lang, plan: p, screens, rects: cap.rects, text, logo: pathToFileURL(join(ROOT, "app", "static", "favicon.svg")).href };

  const b = await edge(9352, ["--allow-file-access-from-files", "--force-color-profile=srgb"]);
  await b.send("Emulation.setDeviceMetricsOverride", { width: 1080, height: 1920, deviceScaleFactor: 1, mobile: false });
  const loaded = b.once("Page.loadEventFired");
  await b.send("Page.navigate", { url: pathToFileURL(join(ROOT, "marketing", "src", "explainer_stage.html")).href });
  await loaded;
  await b.js(`setup(${JSON.stringify(config)})`);
  const voiced = p.scenes.flatMap((s) => s.lines).filter((l) => l.voice).length;
  console.log(`[${lang}] ${p.total.toFixed(1)} s, ${voiced} voice clip(s)`);

  if (STILLS) {
    const dir = join(OUT, "explainer-stills");
    mkdirSync(dir, { recursive: true });
    for (const t of STILLS.split(",").map(Number)) {
      await b.js(`render(${t})`);
      const { data } = await b.send("Page.captureScreenshot", { format: "png" });
      writeFileSync(join(dir, `${lang}-${String(t).padStart(5, "0")}.png`), Buffer.from(data, "base64"));
    }
    await b.close();
    console.log(`[${lang}] stills in ${dir}`);
    return;
  }

  const events = await b.js("events()");
  const wav = join(ASSETS, lang, "soundtrack.wav");
  soundtrack(p, events, wav);
  mkdirSync(OUT, { recursive: true });
  const out = join(OUT, `wadih-explainer-${lang}-9x16.mp4`);
  const ff = spawn("ffmpeg", ["-y", "-v", "error", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-", "-i", wav,
    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", String(FPS),
    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], { stdio: ["pipe", "inherit", "inherit"] });
  const done = new Promise((ok, fail) => ff.on("close", (c) => (c === 0 ? ok() : fail(new Error(`ffmpeg exited ${c}`)))));
  const frames = Math.ceil(p.total * FPS);
  const t0 = Date.now();
  for (let f = 0; f < frames; f++) {
    await b.js(`render(${f / FPS})`);
    const { data } = await b.send("Page.captureScreenshot", { format: "jpeg", quality: 94 });
    if (!ff.stdin.write(Buffer.from(data, "base64"))) await new Promise((r) => ff.stdin.once("drain", r));
    if (f % 150 === 0) console.log(`[${lang}] frame ${f}/${frames} (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
  }
  ff.stdin.end();
  await done;
  await b.close();
  console.log(`[${lang}] wrote ${out}`);
}

for (const lang of LANGS) {
  if (!SKIP_CAPTURE) await capture(lang);
  await render(lang);
}
