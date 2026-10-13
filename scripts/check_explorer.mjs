// Drives the universities explorer in a real browser, at phone and desktop widths (decision 058):
// filter tags and their ✕, «مسح الكل», two quick removals, the keyboard, the field picker under
// إمداد, and the search suggestions (typing, Escape, Tab, outside click, choosing a major).
// pytest checks the HTML; this checks the JavaScript behaviour that pytest can't see.
//
// Needs Playwright. It's preinstalled in Claude Code cloud sessions; on your laptop it would need
// an install (ask first, CLAUDE.md). Start the server, then:
//     node scripts/check_explorer.mjs                      (http://127.0.0.1:8000)
//     node scripts/check_explorer.mjs http://127.0.0.1:8001
// Prints PASS/FAIL per check; exits 1 if any check fails.

import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
let playwright;
try {
  playwright = require("playwright");
} catch {
  playwright = require("/opt/node22/lib/node_modules/playwright"); // global install in cloud sessions
}
const { chromium } = playwright;
const base = process.argv[2] || "http://127.0.0.1:8000";
const results = [];
const check = (name, ok, detail = "") => results.push([ok ? "PASS" : "FAIL", name, detail]);
const chips = (page) => page.$$eval("#results a.applied-x", (as) => as.map((a) => a.getAttribute("aria-label")));
const settle = async (page) => {
  await page.waitForFunction(() => !document.getElementById("results").hasAttribute("aria-busy"));
  await page.waitForTimeout(150);
};
const param = (page, name) => new URL(page.url()).searchParams.get(name);

const browser = await chromium.launch();
for (const [width, tag] of [[390, "phone"], [1280, "desktop"]]) {
  const ctx = await browser.newContext({ viewport: { width, height: 900 }, hasTouch: tag === "phone" });
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  const hidden = () => page.$eval("#q-suggest", (e) => e.hidden);

  // Filters built through the form, including a typed search (the suggestions open while typing).
  await page.goto(base + "/universities", { waitUntil: "networkidle" });
  if (tag === "phone") await page.click("[data-filters-toggle]");
  await page.selectOption("select[name=track]", "emdad"); await settle(page);
  await page.selectOption("select[name=field]", { index: 1 }); await settle(page);
  await page.selectOption("select[name=country]", "GB"); await settle(page);
  await page.fill("input[name=q]", "London"); await page.waitForTimeout(400); await settle(page);
  check(`${tag}: four tags`, (await chips(page)).length === 4);

  // ✕ on one tag, while the suggestions are open: only that filter goes.
  await page.click('#results a.applied-x[aria-label^="إزالة الدولة"]'); await settle(page);
  check(`${tag}: ✕ removes only its filter`, !param(page, "country") && param(page, "track") === "emdad"
    && param(page, "field") && param(page, "q") === "London", page.url());
  check(`${tag}: suggestions closed after ✕`, await hidden());
  const focused = await page.evaluate(() => document.activeElement.getAttribute("aria-label") || "");
  check(`${tag}: focus on a remaining tag`, focused.startsWith("إزالة"), focused);

  await page.click('#results a.applied-x[aria-label^="إزالة المسار"]'); await settle(page);
  check(`${tag}: ✕ track also clears its field`, !param(page, "track") && !param(page, "field") && param(page, "q") === "London");

  // Two quick ✕ before the first answer arrives.
  await page.goto(base + "/universities?q=AI&track=emdad&country=US&lang=english", { waitUntil: "networkidle" });
  await page.route("**/universities?*partial=1*", async (route) => { await new Promise((r) => setTimeout(r, 400)); await route.continue(); });
  await page.click('#results a.applied-x[aria-label^="إزالة الدولة"]');
  await page.click('#results a.applied-x[aria-label^="إزالة لغة الدولة"]');
  await page.waitForTimeout(1200); await settle(page);
  await page.unroute("**/universities?*partial=1*");
  check(`${tag}: two quick ✕ remove both, nothing returns`, !param(page, "country") && !param(page, "lang")
    && param(page, "track") === "emdad" && param(page, "q") === "AI", page.url());

  await page.click("#results a.applied-clear"); await settle(page);
  check(`${tag}: «مسح الكل» clears everything`, page.url().endsWith("/universities") && (await chips(page)).length === 0);
  check(`${tag}: suggestions closed after «مسح الكل»`, await hidden());

  await page.goto(base + "/universities?track=emdad&country=US", { waitUntil: "networkidle" });
  await page.focus('#results a.applied-x[aria-label^="إزالة الدولة"]');
  await page.keyboard.press("Enter"); await settle(page);
  check(`${tag}: Enter on ✕ works`, !param(page, "country") && param(page, "track") === "emdad");

  // إمداد without a field: pick a field in place.
  await page.goto(base + "/universities?track=emdad", { waitUntil: "networkidle" });
  await page.click('#results a[data-pick-field="ict"]'); await settle(page);
  check(`${tag}: field picker updates in place`, param(page, "field") === "ict"
    && (await page.inputValue("select[name=field]")) === "ict");

  // The suggestions themselves.
  await page.goto(base + "/universities", { waitUntil: "networkidle" });
  await page.fill("#q", "هندسة"); await page.waitForTimeout(300);
  check(`${tag}: suggestions open on typing`, !(await hidden()));
  await page.keyboard.press("Escape");
  check(`${tag}: Escape closes and keeps the text`, (await hidden()) && (await page.inputValue("#q")) === "هندسة");
  await page.mouse.click(5, 300); await page.waitForTimeout(400);
  check(`${tag}: outside click keeps them closed`, await hidden());
  await page.fill("#q", "هندسة البرمجيات"); await page.waitForTimeout(300);
  await page.keyboard.press("ArrowDown"); await page.keyboard.press("Enter"); await page.waitForTimeout(800);
  check(`${tag}: Enter on a major searches it`, param(page, "q") !== null && (await hidden()));

  check(`${tag}: no JavaScript errors`, errors.length === 0, errors.join(" / "));
  await ctx.close();
}
await browser.close();
for (const r of results) console.log(r.join("  "));
process.exit(results.some((r) => r[0] === "FAIL") ? 1 : 0);
