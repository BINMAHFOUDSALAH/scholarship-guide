// وضّاح's teaser kit (decisions 082–084), drawn in a headless browser with the site's own fonts (they join Arabic
// correctly, which many image tools don't). $0, nothing uploaded anywhere.
//   1. marketing/out/waddah-og.png         1200×630, a share image (no page uses it: وضّاح has no page until launch, 084)
//   2. marketing/out/waddah-story.png      1080×1920, a still for Snapchat / X / WhatsApp status
//   3. marketing/out/waddah-dawn.mp4       1080×1920, 6 s: the night lightening until the light rises (needs ffmpeg)
//
// Start the site, then:   node marketing/src/waddah_cards.mjs [http://127.0.0.1:8000] [--no-clip]
// The words come from data/waddah.json, the homepage teaser's own copy, so the kit never says what the site doesn't.

import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
let playwright;
try {
  playwright = require("playwright");
} catch {
  playwright = require("/opt/node22/lib/node_modules/playwright");
}
const root = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const host = process.argv.slice(2).find((a) => a.startsWith("http")) || "http://127.0.0.1:8000";
const clip = !process.argv.includes("--no-clip");
const data = JSON.parse(readFileSync(join(root, "data", "waddah.json"), "utf8"));
const out = join(root, "marketing", "out");
mkdirSync(join(out, "frames"), { recursive: true });

const star = "M0 -26 Q4.2 -4.2 26 0 Q4.2 4.2 0 26 Q-4.2 4.2 -26 0 Q-4.2 -4.2 0 -26Z";

// One card: the night, the paper-cut horizon, the light; the name, «قادم في ديسمبر», the line, the address.
function card(w, h, dawn) {
  const tall = h > w;
  const title = tall ? 190 : 150;
  return `<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<link rel="stylesheet" href="${host}/static/fonts.css">
<style>
  html, body { margin: 0; width: ${w}px; height: ${h}px; overflow: hidden; background: #10372a; }
  body { position: relative; font-family: "IBM Plex Sans Arabic", sans-serif; color: #f6f4ee; --dawn: ${dawn}; }
  svg.sky { position: absolute; inset: 0; width: 100%; height: 100%; }
  .glow-in { stop-color: color-mix(in oklab, #d8ed9b calc(var(--dawn) * 50%), #10372a); }
  .text { position: absolute; inset-inline: ${tall ? 90 : 80}px; top: ${tall ? 300 : 44}px; }
  .kicker { font-size: ${tall ? 44 : 30}px; font-weight: 700; color: #c3cdc6; margin: 0 0 12px; }
  .name { font-family: "Noto Naskh Arabic", serif; font-weight: 700; font-size: ${title}px; line-height: 1.35; margin: 0; }
  .when { font-size: ${tall ? 72 : 52}px; font-weight: 700; color: #d8ed9b; margin: 0 0 ${tall ? 40 : 22}px; }
  .line { font-size: ${tall ? 44 : 28}px; line-height: 1.7; color: #dfe5e1; margin: 0; max-width: ${tall ? 900 : 760}px; }
  .site { position: absolute; bottom: ${tall ? 90 : 34}px; right: ${tall ? 90 : 80}px; font-size: ${tall ? 40 : 28}px; font-weight: 700; direction: ltr; }
</style></head><body>
<svg class="sky" viewBox="0 0 1440 ${tall ? 2560 : 756}" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
  <defs><radialGradient id="g" cx="0.23" cy="1" r="0.6"><stop offset="0" class="glow-in"/><stop offset="1" stop-color="#10372a" stop-opacity="0"/></radialGradient></defs>
  <rect width="1440" height="${tall ? 2560 : 756}" fill="#10372a"/>
  <rect width="1440" height="${tall ? 2560 : 756}" fill="url(#g)" style="opacity: calc(0.25 + var(--dawn) * 0.75)"/>
  <g transform="translate(0 ${tall ? 2140 : 336})">
    <g transform="translate(330 250)"><g style="transform: translateY(calc((1 - var(--dawn)) * 110px))">
      <circle r="70" fill="#d8ed9b" style="opacity: calc(0.08 + var(--dawn) * 0.25)"/>
      <path d="${star}" fill="#d8ed9b" transform="scale(1.4)"/></g></g>
    <path fill="#245a46" d="M0 330 C180 300 300 318 470 306 C640 294 760 262 940 286 C1110 308 1240 290 1440 300 L1440 420 L0 420Z"/>
    <path fill="#174a39" d="M0 360 C150 340 330 352 520 336 C700 322 860 344 1030 334 C1200 324 1320 344 1440 338 L1440 420 L0 420Z"/>
    <path fill="#0e3125" d="M0 392 C220 378 420 396 640 384 C860 372 1060 394 1260 386 C1350 382 1400 388 1440 386 L1440 420 L0 420Z"/>
  </g>
</svg>
<div class="text">
  <p class="kicker">${data.teaser.kicker_ar}</p>
  <p class="name">${data.name_ar}</p>
  <p class="when">قادم في ديسمبر</p>
  <p class="line">${data.teaser.line_ar}</p>
</div>
<p class="site">wadihguide.com</p>
</body></html>`;
}

const browser = await playwright.chromium.launch();
async function shoot(w, h, dawn, path) {
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  await page.goto(host + "/robots.txt"); // the site's own origin, so its fonts load (fonts need the same origin)
  await page.setContent(card(w, h, dawn), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path });
  await page.close();
}

// The stills show the edge of dawn, as the band will look late in November.
await shoot(1200, 630, 0.85, join(out, "waddah-og.png"));
await shoot(1080, 1920, 0.85, join(out, "waddah-story.png"));
console.log("wrote marketing/out/waddah-og.png and marketing/out/waddah-story.png");

if (clip) {
  // 6 seconds at 30 frames: night for a second, then dawn rises and holds.
  const frames = 180;
  for (let i = 0; i < frames; i++) {
    const t = Math.max(0, (i - 30) / (frames - 60));
    const dawn = Math.min(1, 1 - Math.pow(1 - t, 3)); // ease out
    await shoot(1080, 1920, dawn.toFixed(3), join(out, "frames", `f${String(i).padStart(3, "0")}.png`));
  }
  execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-framerate", "30", "-i", join(out, "frames", "f%03d.png"),
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", join(out, "waddah-dawn.mp4")]);
  console.log("wrote marketing/out/waddah-dawn.mp4");
}
await browser.close();
