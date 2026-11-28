// وضّاح beside «بوضوح» (owner, 2026-11-27), checked in a real browser:
//   node scripts/check_waddah_hero.mjs [base] [--frames dir] [--browser chromium|webkit]
// On a laptop and a narrow phone: he is his own renders, he plays his scene by himself (unsure → cheer → point → wave
// → resting), the headline and the search stay readable and usable (nothing of his is on top of the field), he points
// toward the field, the field shows his magnifier, the pointer on him gets a wave, reduced motion still changes poses
// (by fading) without moving him, and the English homepage has no animation.
// --frames saves a screenshot of the hero at each pose of the scene.
import { chromium, webkit, devices } from "playwright";
import { mkdirSync } from "node:fs";
import path from "node:path";

const arg = (name) => { const i = process.argv.indexOf(name); return i > 0 ? process.argv[i + 1] : null; };
const base = process.argv.slice(2).find((a) => a.startsWith("http")) || "http://127.0.0.1:8000";
const framesDir = arg("--frames");
const engine = arg("--browser") === "webkit" ? webkit : chromium;
let fails = 0; const ok = (c, m) => { console.log((c ? "ok   " : "FAIL ") + m); if (!c) fails++; };

const browser = await engine.launch();
const sizes = [
  ["laptop", { viewport: { width: 1366, height: 680 } }],
  ["phone", { ...devices["iPhone SE"], viewport: { width: 360, height: 740 } }],
];
const pose = (p) => p.evaluate(() => document.querySelector("[data-waddah-hero]").dataset.pose);
const visible = (p) => p.evaluate(() => [...document.querySelectorAll("[data-waddah-hero] .wh-pose")]
  .filter((i) => getComputedStyle(i).opacity !== "0").map((i) => i.dataset.poseImg));

for (const [name, opts] of sizes) {
  const ctx = await browser.newContext({ ...opts, reducedMotion: "no-preference" });
  const p = await ctx.newPage();
  const errors = []; p.on("pageerror", (e) => errors.push(e.message));
  // Record each pose as it shows.
  await p.addInitScript(() => {
    window.__poses = [];
    document.addEventListener("DOMContentLoaded", () => {
      const r = document.querySelector("[data-waddah-hero]");
      if (r) new MutationObserver(() => { if (window.__poses.at(-1) !== r.dataset.pose) window.__poses.push(r.dataset.pose); })
        .observe(r, { attributes: true, attributeFilter: ["data-pose"] });
    });
  });
  await p.goto(base + "/", { waitUntil: "domcontentloaded" });
  ok((await visible(p)).join() === "logo", `${name}: resting pose on load (${await visible(p)})`);  // before the scene starts
  const hero = p.locator("[data-waddah-hero]");
  ok(await hero.count() === 1, `${name}: وضّاح is beside the tagline`);
  ok(await hero.getAttribute("aria-hidden") === "true", `${name}: hidden from screen readers`);
  ok((await p.locator("[data-waddah-hero] img.wh-pose").count()) === 7 && !(await p.locator("[data-waddah-hero] svg").count()),
    `${name}: his own renders (7 poses), no drawing`);

  const shots = [];
  if (framesDir) {
    mkdirSync(framesDir, { recursive: true });
    const box = await p.evaluate(() => {
      const h = document.querySelector(".ask-hero").getBoundingClientRect();
      const f = document.getElementById("home-q").getBoundingClientRect();
      return { x: Math.max(0, h.left), y: Math.max(0, h.top), width: Math.min(h.width, innerWidth), height: Math.min(f.bottom - h.top + 24, 420) };
    });
    p.on("console", () => {});
    await p.exposeFunction("__shot", async (label) => { shots.push(p.screenshot({ path: path.join(framesDir, `${name}-${shots.length}-${label}.png`), clip: box })); });
    await p.evaluate(() => new MutationObserver(() => setTimeout(() => window.__shot(document.querySelector("[data-waddah-hero]").dataset.pose), 380))
      .observe(document.querySelector("[data-waddah-hero]"), { attributes: true, attributeFilter: ["data-pose"] }));
  }
  await p.waitForTimeout(6800);
  await Promise.all(shots);
  const seen = await p.evaluate(() => window.__poses);
  ok(seen.slice(0, 5).join(" → ") === "unsure → cheer → point → wave → logo", `${name}: the scene plays by itself (${seen.join(" → ")})`);

  const overlap = await p.evaluate(() => {
    const w = document.querySelector("[data-waddah-hero]").getBoundingClientRect();
    const f = document.getElementById("home-q").getBoundingClientRect();
    return w.left < f.right && f.left < w.right && w.top < f.bottom && f.top < w.bottom;
  });
  ok(!overlap, `${name}: he never covers the search field`);
  const face = await p.evaluate(() => {
    const w = document.querySelector("[data-waddah-hero]").getBoundingClientRect();
    const f = document.getElementById("home-q").getBoundingClientRect();
    return { face: document.querySelector("[data-waddah-hero]").dataset.face, left: f.left + f.width / 2 < w.left + w.width / 2 };
  });
  ok(face.face === (face.left ? "left" : "right"), `${name}: points toward the field (${face.face})`);

  await p.focus("#home-q"); await p.waitForTimeout(300);
  ok(await pose(p) === "search", `${name}: the field focused → his magnifier`);
  const onTop = await p.evaluate(() => {
    const f = document.getElementById("home-q").getBoundingClientRect();
    return document.elementFromPoint(f.left + f.width / 2, f.top + f.height / 2)?.id;
  });
  ok(onTop === "home-q", `${name}: the search field is the thing under a tap (${onTop})`);
  await p.locator("#hero-title").click(); await p.waitForTimeout(300);
  ok(await pose(p) === "logo", `${name}: leaving the field → resting`);
  if (name === "laptop") {
    await p.mouse.move(0, 0); const b = await hero.boundingBox(); await p.mouse.move(b.x + b.width / 2, b.y + b.height / 2); await p.waitForTimeout(250);
    ok(await pose(p) === "wave", "laptop: the pointer on him → a wave");
  }
  ok(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${name}: no sideways scroll`);
  ok(!errors.length, `${name}: no script errors ${errors.join(" | ")}`);
  await ctx.close();
}

// Reduced motion (Windows with «Animation effects» off): the scene still changes poses, by fading, and nothing moves.
{
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 680 }, reducedMotion: "reduce" });
  const p = await ctx.newPage();
  await p.goto(base + "/");
  await p.waitForFunction(() => document.querySelector("[data-waddah-hero]").dataset.pose !== "logo", null, { timeout: 4000 })
    .then(() => ok(true, "reduced motion: the poses still change"), () => ok(false, "reduced motion: the poses still change"));
  const moving = await p.evaluate(() => document.querySelector("[data-waddah-hero]").getAnimations({ subtree: true })
    .filter((a) => a.animationName).map((a) => a.animationName));
  ok(!moving.length, `reduced motion: no movement (${moving.join(", ") || "none"})`);
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
