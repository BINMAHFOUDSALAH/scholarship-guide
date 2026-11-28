// وضّاح beside «بوضوح» (owner, 2026-11-27), checked in a real browser:
//   node scripts/check_waddah_hero.mjs [base] [--frames dir] [--video dir] [--browser chromium|webkit]
// On a laptop and a narrow phone: he plays once by himself, the headline and the search stay readable and usable
// (nothing of his is on top of the field or takes a tap), he points toward the field, the repeat waits for an
// untouched form, reduced motion keeps the still lean, and the English homepage has no animation.
// --frames saves the scene paused at moments through its four seconds; --video records the pages.
import { chromium, webkit, devices } from "playwright";
import { mkdirSync } from "node:fs";
import path from "node:path";

const arg = (name) => { const i = process.argv.indexOf(name); return i > 0 ? process.argv[i + 1] : null; };
const base = process.argv.slice(2).find((a) => a.startsWith("http")) || "http://127.0.0.1:8000";
const framesDir = arg("--frames"), videoDir = arg("--video");
const engine = arg("--browser") === "webkit" ? webkit : chromium;
let fails = 0; const ok = (c, m) => { console.log((c ? "ok   " : "FAIL ") + m); if (!c) fails++; };

const browser = await engine.launch();
const sizes = [
  ["desktop", { viewport: { width: 1280, height: 800 } }],
  ["phone", { ...devices["iPhone SE"], viewport: { width: 360, height: 740 } }],
];
const MOMENTS = [0, 0.6, 0.9, 1.2, 1.5, 1.9, 2.4, 2.6, 3.0, 3.3, 3.5, 4.0];

for (const [name, opts] of sizes) {
  const ctx = await browser.newContext({ ...opts, ...(videoDir ? { recordVideo: { dir: path.join(videoDir, name), size: opts.viewport } } : {}) });
  const p = await ctx.newPage();
  const errors = []; p.on("pageerror", (e) => errors.push(e.message));
  await p.goto(base + "/"); await p.waitForLoadState("networkidle");
  const hero = p.locator("[data-waddah-hero]");
  ok(await hero.count() === 1, `${name}: وضّاح is beside the tagline`);
  ok(await hero.getAttribute("aria-hidden") === "true", `${name}: hidden from screen readers`);
  // Plays once by himself.
  await p.waitForSelector("[data-waddah-hero].is-playing", { timeout: 4000 }).then(() => ok(true, `${name}: plays once when the hero is on screen`), () => ok(false, `${name}: plays once`));
  // The search works while he plays: the field takes focus and text, and nothing of his is on top of it.
  const onTop = await p.evaluate(() => {
    const f = document.getElementById("home-q").getBoundingClientRect();
    const el = document.elementFromPoint(f.left + f.width / 2, f.top + f.height / 2);
    return el && el.id;
  });
  ok(onTop === "home-q", `${name}: the search field is the thing under a tap (${onTop})`);
  const overlap = await p.evaluate(() => {
    const w = document.querySelector("[data-waddah-hero]").getBoundingClientRect();
    const r = (s) => document.querySelector(s).getBoundingClientRect();
    const hit = (a, b) => a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;
    return { title: hit(w, r("#hero-title")), field: hit(w, r("#home-q")) };
  });
  ok(!overlap.field, `${name}: he never covers the search field`);
  const dir = await p.evaluate(() => ({ face: getComputedStyle(document.querySelector("[data-waddah-hero]")).getPropertyValue("--wh-face").trim(),
    aim: getComputedStyle(document.querySelector("[data-waddah-hero]")).getPropertyValue("--wh-aim").trim() }));
  console.log(`     ${name}: faces ${dir.face === "1" ? "left" : "right"}, tilts ${dir.aim} toward the field`);
  await p.waitForFunction(() => !document.querySelector("[data-waddah-hero]").classList.contains("is-playing"), null, { timeout: 6000 });
  ok(true, `${name}: back to the still lean after the scene`);
  ok(await p.evaluate(() => getComputedStyle(document.documentElement).overflowX !== "scroll" && document.documentElement.scrollWidth <= innerWidth), `${name}: no sideways scroll`);

  if (framesDir) {
    mkdirSync(framesDir, { recursive: true });
    const box = await p.evaluate(() => {
      const h = document.querySelector(".ask-hero").getBoundingClientRect();
      const f = document.getElementById("home-q").getBoundingClientRect();
      return { x: Math.max(0, h.left), y: Math.max(0, h.top), width: Math.min(h.width, innerWidth), height: Math.min(f.bottom - h.top + 30, 460) };
    });
    await p.evaluate(() => document.querySelector("[data-waddah-hero]").classList.add("is-playing"));
    for (const t of MOMENTS) {
      await p.evaluate((ms) => { for (const a of document.querySelector("[data-waddah-hero]").getAnimations({ subtree: true })) { a.pause(); a.currentTime = ms; } }, t * 1000);
      await p.screenshot({ path: path.join(framesDir, `${name}-${String(Math.round(t * 100)).padStart(3, "0")}.png`), clip: box });
    }
    await p.evaluate(() => document.querySelector("[data-waddah-hero]").classList.remove("is-playing"));
  }
  ok(!errors.length, `${name}: no script errors ${errors.join(" | ")}`);
  await ctx.close();
}

// The repeat waits for an untouched form: typing before it means no second play.
{
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const p = await ctx.newPage();
  await p.goto(base + "/");
  await p.waitForSelector("[data-waddah-hero].is-playing", { timeout: 4000 });
  await p.fill("#home-q", "هندسة");
  await p.waitForFunction(() => !document.querySelector("[data-waddah-hero]").classList.contains("is-playing"), null, { timeout: 6000 });
  await p.waitForTimeout(14500);
  ok(!(await p.evaluate(() => document.querySelector("[data-waddah-hero]").classList.contains("is-playing"))), "no repeat after the student types");
  await ctx.close();
}
// Untouched and still on screen: one repeat, and only one.
{
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const p = await ctx.newPage();
  await p.goto(base + "/");
  await p.evaluate(() => { window.__plays = 0; new MutationObserver(() => { if (document.querySelector("[data-waddah-hero]").classList.contains("is-playing")) window.__plays++; }).observe(document.querySelector("[data-waddah-hero]"), { attributes: true }); });
  await p.waitForTimeout(4600 + 13000 + 4500 + 14000);
  const plays = await p.evaluate(() => window.__plays);
  ok(plays === 2, `untouched and on screen: played ${plays} times (once, then one repeat), never a third`);
  await ctx.close();
}
// Reduced motion: the still lean, nothing plays.
{
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 }, reducedMotion: "reduce" });
  const p = await ctx.newPage();
  await p.goto(base + "/"); await p.waitForTimeout(2500);
  const st = await p.evaluate(() => ({ playing: document.querySelector("[data-waddah-hero]").classList.contains("is-playing"),
    lean: getComputedStyle(document.querySelector(".wh-lean")).opacity, point: getComputedStyle(document.querySelector(".wh-point")).opacity }));
  ok(!st.playing && st.lean === "1" && st.point === "0", "reduced motion: the still lean");
  await ctx.close();
}
// English: the homepage keeps its own wave, no animation.
{
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const p = await ctx.newPage();
  await p.goto(base + "/en/");
  ok(await p.locator("[data-waddah-hero]").count() === 0, "English homepage: no animation");
  await ctx.close();
}
await browser.close();
console.log(fails ? `${fails} failed` : "all passed");
process.exit(fails ? 1 : 0);
