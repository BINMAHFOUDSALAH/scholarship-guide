// Captures the real wadihguide.com flow at phone size for the launch ad (decision 044).
// Drives the already-installed Microsoft Edge in headless mode over the Chrome DevTools Protocol,
// so nothing extra is installed. Output: PNG frames + rects.json (where each tap happens).
// Run from the repo root:  node marketing/src/capture_site.mjs
import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync, rmSync } from "node:fs";
import { resolve } from "node:path";

const SITE = "https://wadihguide.com";
const OUT = resolve("marketing/assets/screen");
const PROFILE = resolve("marketing/.edge-profile");
const EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const PORT = 9333;
// 390 CSS px wide × 2.7692 = 1080 px: the frames come out exactly 1080 wide.
const W = 390, H = 693, DSF = 1080 / 390;

rmSync(OUT, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });
rmSync(PROFILE, { recursive: true, force: true });

const edge = spawn(EDGE, [
  "--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${PROFILE}`,
  "--hide-scrollbars", "--no-first-run", "--lang=ar", "about:blank",
], { stdio: "ignore" });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let target;
for (let i = 0; i < 40 && !target; i++) {
  await sleep(250);
  try {
    const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
    target = list.find((t) => t.type === "page");
  } catch {}
}
if (!target) throw new Error("Edge did not start");

const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r, { once: true }));
let nextId = 1;
const pending = new Map();
const waiters = [];
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
const js = async (expr) => (await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true })).result.value;

await send("Page.enable");
await send("Runtime.enable");
await send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: DSF, mobile: true });
await send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });
await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }, { name: "prefers-reduced-motion", value: "reduce" }] });

const rects = {};
let n = 0;
async function shot(name) {
  const { data } = await send("Page.captureScreenshot", { format: "png" });
  const file = `${String(++n).padStart(3, "0")}_${name}.png`;
  writeFileSync(`${OUT}/${file}`, Buffer.from(data, "base64"));
  return file;
}
// Whole page as one tall image (1080 px wide), for smooth scrolling in the edit.
async function fullPage(name) {
  const h = await js("document.documentElement.scrollHeight");
  const { data } = await send("Page.captureScreenshot", {
    format: "png", captureBeyondViewport: true, clip: { x: 0, y: 0, width: W, height: h, scale: 1 },
  });
  const file = `${String(++n).padStart(3, "0")}_${name}.png`;
  writeFileSync(`${OUT}/${file}`, Buffer.from(data, "base64"));
  await send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: DSF, mobile: true });
  return { file, cssHeight: h };
}
async function go(path) {
  const loaded = once("Page.loadEventFired");
  await send("Page.navigate", { url: SITE + path });
  await loaded;
  await js("document.fonts.ready.then(() => true)");
  await sleep(600);
}
// Center of the first element matching a selector + text, in CSS px of the viewport.
async function rectOf(selector, text = "") {
  return js(`(() => {
    const els = [...document.querySelectorAll(${JSON.stringify(selector)})]
      .filter(e => e.offsetParent !== null && e.textContent.includes(${JSON.stringify(text)}));
    if (!els.length) return null;
    const r = els[0].getBoundingClientRect();
    return { x: r.x + r.width / 2, y: r.y + r.height / 2, w: r.width, h: r.height };
  })()`);
}
async function scrollTo(selector, text = "", offset = 220) {
  await js(`(() => {
    const el = [...document.querySelectorAll(${JSON.stringify(selector)})].find(e => e.textContent.includes(${JSON.stringify(text)}));
    if (el) window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - ${offset});
  })()`);
  await sleep(400);
}
async function tap(x, y) {
  for (const type of ["mousePressed", "mouseReleased"]) {
    await send("Input.dispatchMouseEvent", { type, x, y, button: "left", clickCount: 1 });
  }
}

// 1. Homepage: the grade buttons. Tap «ثالث ثانوي».
await go("/");
rects.home = await shot("home");
rects.grade12_tap = await rectOf("a", "ثالث ثانوي");

// 2. Grade 12 page (top).
await go("/grades/grade-12");
rects.grade12 = await shot("grade12");

// 3. Homepage search: type «الذكاء الاصطناعي» one letter at a time.
await go("/");
await scrollTo("#home-q", "", 260);
rects.search_tap = await rectOf("#home-q");
await js("document.querySelector('#home-q').focus()");
const query = "الذكاء الاصطناعي";
rects.typing = [];
for (let i = 1; i <= query.length; i++) {
  await send("Input.insertText", { text: query[i - 1] });
  await sleep(120);
  if (i % 2 === 0 || i === query.length) rects.typing.push(await shot(`type_${String(i).padStart(2, "0")}`));
}
await sleep(700);
rects.typed = await shot("typed");

// 4. Tap the suggestion «الذكاء الاصطناعي · Artificial intelligence» → results page.
rects.suggest_tap = await rectOf(".suggest-option", "Artificial intelligence");
const loadedResults = once("Page.loadEventFired");
await tap(rects.suggest_tap.x, rects.suggest_tap.y);
await loadedResults;
await js("document.fonts.ready.then(() => true)");
await sleep(600);
rects.results_url = await js("location.pathname + location.search");
rects.results = await shot("results");
rects.results_full = await fullPage("results_full");
const firstUni = await js(`(() => { const a = [...document.querySelectorAll('main a')].find(a => a.offsetParent !== null && a.pathname.startsWith('/universities/') && a.pathname.split('/').length === 3); return a ? a.pathname : null; })()`);
rects.first_uni = firstUni;
rects.first_uni_pagey = await js(`(() => { const a = [...document.querySelectorAll('main a')].find(a => a.pathname === ${JSON.stringify(firstUni)}); return a.getBoundingClientRect().top + window.scrollY; })()`);

// 5. University page: top, the official source link, then «احفظ في قائمتي».
await go(firstUni);
rects.uni = await shot("uni");
rects.uni_full = await fullPage("uni_full");
// Where «المصدر: الدليل الاسترشادي، صفحة …» sits on the page (CSS px from the top).
rects.uni_source_pagey = await js(`(() => { const a = [...document.querySelectorAll('main a')].find(a => a.textContent.includes('الدليل الاسترشادي، صفحة')); return a ? a.getBoundingClientRect().top + window.scrollY : null; })()`);
rects.save_tap = await rectOf("button[data-save]");
if (rects.save_tap) {
  await tap(rects.save_tap.x, rects.save_tap.y);
  await sleep(500);
  rects.uni_saved = await shot("uni_saved");
}
await scrollTo("a", "المصدر", 300);
rects.source_tap = await rectOf("a", "المصدر");
rects.uni_source = await shot("uni_source");

// 6. «قائمتي».
await go("/my-list");
rects.mylist = await shot("mylist");

writeFileSync(`${OUT}/rects.json`, JSON.stringify({ W, H, DSF, ...rects }, null, 2));
ws.close();
edge.kill();
console.log("captured", n, "frames; first university:", firstUni);
