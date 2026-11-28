// Draws the link-preview images that WhatsApp, Telegram, X and other apps show (1200x630):
//   app/static/img/share-wadih-programs.png     (Arabic pages)
//   app/static/img/share-wadih-programs-en.png  (English pages under /en/)
//
//   node scripts/share_image.mjs
//
// Ivory, the folded-ticket logo, «برامج الابتعاث» in forest green and a smaller line under it (owner, 2026-11-27).
// It renders in Chromium (Playwright) from local files, so the site's own font joins the Arabic letters correctly.
// base.html points og:image and twitter:image at each file's full public address; give a redrawn image a new file
// name so WhatsApp, Telegram and X don't keep showing a cached one.
import { chromium } from "playwright";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";
import { writeFileSync, mkdtempSync, rmSync } from "node:fs";
import os from "node:os";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const asset = (p) => pathToFileURL(path.join(root, "app", "static", p)).href;

const versions = [
  { file: "share-wadih-programs.png", lang: "ar", dir: "rtl", title: "برامج الابتعاث", line: "الشروط · المواعيد · الجامعات" },
  { file: "share-wadih-programs-en.png", lang: "en", dir: "ltr", title: "Scholarship programs", line: "Requirements · Deadlines · Universities" },
];

const page_html = (v) => `<!doctype html><html lang="${v.lang}" dir="${v.dir}"><head><meta charset="utf-8"><style>
@font-face { font-family: "Readex Pro"; font-weight: 300 700; src: url("${asset("fonts/readex-pro-arabic.woff2")}") format("woff2"); unicode-range: U+0600-06FF, U+FB50-FDFF, U+FE70-FEFC; }
@font-face { font-family: "Readex Pro"; font-weight: 300 700; src: url("${asset("fonts/readex-pro-latin.woff2")}") format("woff2"); unicode-range: U+0000-00FF, U+2000-206F; }
html, body { margin: 0; }
body { width: 1200px; height: 630px; overflow: hidden; background: #fbf5ea; font-family: "Readex Pro", sans-serif; color: #00483a;
       display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
.logo { display: block; height: 200px; width: auto; }
h1 { margin: 52px 0 0; font-size: 84px; font-weight: 700; line-height: 1.15; letter-spacing: 0; white-space: nowrap; }
p { margin: 22px 0 0; font-size: 36px; font-weight: 500; color: #2f5f52; white-space: nowrap; }
.sep { color: #82a596; margin: 0 18px; font-weight: 700; }
</style></head><body>
<img class="logo" src="${asset("img/brand/wadih-logo.svg")}" alt="">
<h1>${v.title}</h1>
<p>${v.line.split(" · ").join('<span class="sep">·</span>')}</p>
</body></html>`;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
// A file page (not setContent's about:blank), so Chromium lets it load the local font and images.
const dir = mkdtempSync(path.join(os.tmpdir(), "wadih-share-"));
for (const v of versions) {
  const file = path.join(dir, `${v.lang}.html`);
  writeFileSync(file, page_html(v));
  await page.goto(pathToFileURL(file).href, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  const out = path.join(root, "app", "static", "img", v.file);
  await page.screenshot({ path: out, type: "png" });
  console.log("wrote", path.relative(root, out));
}
await browser.close();
rmSync(dir, { recursive: true, force: true });
