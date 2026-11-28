// Draws the link-preview image that WhatsApp, X and other apps show (app/static/img/share-wadih.png, 1200x630).
//
//   node scripts/share_image.mjs
//
// Warm ivory, the folded-ticket logo, the tagline, and وضّاح waving. It renders in Chromium (Playwright) from local
// files, so the site's own font joins the Arabic letters correctly. base.html points og:image and twitter:image at the
// file's full public address; give a redrawn image a new file name so WhatsApp and X don't keep showing a cached one.
import { chromium } from "playwright";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";
import { writeFileSync, mkdtempSync, rmSync } from "node:fs";
import os from "node:os";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const asset = (p) => pathToFileURL(path.join(root, "app", "static", p)).href;
const out = path.join(root, "app", "static", "img", "share-wadih.png");

const html = `<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>
@font-face { font-family: "Readex Pro"; font-weight: 300 700; src: url("${asset("fonts/readex-pro-arabic.woff2")}") format("woff2"); unicode-range: U+0600-06FF, U+FB50-FDFF, U+FE70-FEFC; }
@font-face { font-family: "Readex Pro"; font-weight: 300 700; src: url("${asset("fonts/readex-pro-latin.woff2")}") format("woff2"); unicode-range: U+0000-00FF; }
html, body { margin: 0; }
body { width: 1200px; height: 630px; overflow: hidden; background: #fbf5ea; font-family: "Readex Pro", sans-serif; color: #11231d; position: relative; }
.glow { position: absolute; inset: auto -120px -260px auto; width: 760px; height: 760px; border-radius: 50%;
        background: radial-gradient(closest-side, rgba(130, 222, 159, 0.28), rgba(130, 222, 159, 0)); }
.text { position: absolute; top: 84px; right: 88px; width: 700px; }
.logo { display: block; height: 180px; width: auto; }
h1 { margin: 44px 0 0; font-size: 46px; white-space: nowrap; font-weight: 600; line-height: 1.25; letter-spacing: 0; }
p { margin: 16px 0 0; font-size: 28px; font-weight: 400; color: #45564f; }
.site { position: absolute; bottom: 52px; right: 88px; font-size: 24px; font-weight: 500; color: #00483a; direction: ltr; }
.waddah { position: absolute; left: 24px; bottom: 0; height: 410px; width: auto; }
</style></head><body>
<div class="glow"></div>
<div class="text">
  <img class="logo" src="${asset("img/brand/wadih-logo.svg")}" alt="">
  <h1>مستقبلك بعد الثانوية، بوضوح</h1>
  <p>دليل مجاني لطلاب الثانوية في السعودية</p>
</div>
<div class="site">wadihguide.com</div>
<img class="waddah" src="${asset("img/waddah/wave-520.webp")}" alt="">
</body></html>`;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
// A file page (not setContent's about:blank), so Chromium lets it load the local font and images.
const dir = mkdtempSync(path.join(os.tmpdir(), "wadih-share-"));
writeFileSync(path.join(dir, "share.html"), html);
await page.goto(pathToFileURL(path.join(dir, "share.html")).href, { waitUntil: "load" });
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: out, type: "png" });
await browser.close();
rmSync(dir, { recursive: true, force: true });
console.log("wrote", path.relative(root, out));
