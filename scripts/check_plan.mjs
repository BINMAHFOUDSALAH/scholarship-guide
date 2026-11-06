// Drives «خطتي» (/my-plan, decision 078, Part B) in a browser on an emulated iPhone.
// pytest checks the rows the server draws; this checks what only a browser shows:
// - saves from the old «قائمتي» ("wadih:saved") move into the plan once, and the old key goes;
// - «احفظ» on a university result row and on a program track adds it; the header count and the homepage's
//   return strip follow;
// - the plan page draws every item; changing a status saves it (with today's date), redraws the next step,
//   and keeps the keyboard on the same select; a reload keeps it;
// - «إزالة» removes an item, and an empty plan says so;
// - what's stored is ids, statuses and dates only.
//
// Needs Playwright (preinstalled in Claude Code cloud sessions; on your laptop ask before installing, CLAUDE.md).
// Start the server, then:
//     node scripts/check_plan.mjs                         (http://127.0.0.1:8000)
//     node scripts/check_plan.mjs http://127.0.0.1:8000 --en   (the English pages)
// Prints PASS/FAIL per check; exits 1 if any check fails.

import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
let playwright;
try {
  playwright = require("playwright");
} catch {
  playwright = require("/opt/node22/lib/node_modules/playwright"); // global install in cloud sessions
}
const { chromium, devices } = playwright;
const english = process.argv.includes("--en");
const host = process.argv.slice(2).find((a) => a.startsWith("http")) || "http://127.0.0.1:8000";
const base = host + (english ? "/en" : "");
const L = english
  ? { save: "Save", saved: "✓ In your plan", empty: "Your plan is empty.", applied: "Applied on" }
  : { save: "احفظ", saved: "✓ في خطتك", empty: "خطتك فارغة.", applied: "قدّمت في" };
const results = [];
const check = (name, ok, detail = "") => results.push([ok ? "PASS" : "FAIL", name, detail]);

const browser = await chromium.launch();
const context = await browser.newContext({ ...devices["iPhone 13"] });
const page = await context.newPage();
const errors = [];
page.on("pageerror", (e) => errors.push(String(e)));
const stored = () => page.evaluate(() => JSON.parse(localStorage.getItem("wadih:plan") || "null"));

// 1. The old «قائمتي» moves in.
await page.goto(base + "/");
await page.evaluate(() => {
  localStorage.clear();
  localStorage.setItem("wadih:saved", JSON.stringify(["harvard-university", "nope-university"]));
});
await page.reload();
let plan = await stored();
check("old «قائمتي» moves into the plan", plan && plan.items.length === 2 && plan.items[0].id === "harvard-university"
  && plan.items[0].type === "university" && plan.items[0].status === "thinking", JSON.stringify(plan));
check("the old key is removed", (await page.evaluate(() => localStorage.getItem("wadih:saved"))) === null);
check("the homepage's return strip shows", await page.locator("[data-plan-strip]").isVisible());
check("the header count shows 2", (await page.locator("[data-mylist-count]").first().innerText()) === "2");

// 2. Save a program track from the homepage, and a university from the results.
const arruaad = page.locator('button[data-save="arruaad"][data-save-type="program"]');
await arruaad.scrollIntoViewIfNeeded();
await arruaad.tap();
check("«احفظ» on الرواد marks it saved", (await arruaad.innerText()).trim() === L.saved);
await page.goto(base + "/universities?track=arruaad");
const stanford = page.locator('button[data-save="stanford-university"]').first();
await stanford.scrollIntoViewIfNeeded();
await stanford.tap();
plan = await stored();
check("both are in the plan, newest first", plan.items.map((i) => i.type + ":" + i.id).slice(0, 2).join(" ")
  === "university:stanford-university program:arruaad", JSON.stringify(plan.items));
check("only ids, statuses and dates are stored", plan.items.every((i) =>
  Object.keys(i).sort().join() === "id,status,type,updated"));

// 3. The plan page: rows, a status change, a reload.
await page.goto(base + "/my-plan");
await page.waitForSelector("[data-mylist-rows]:not([hidden])");
const keys = await page.locator("[data-mylist-item]").evaluateAll((els) => els.map((e) => e.dataset.mylistItem));
check("the plan page draws the known items (an unknown one is dropped)", keys.join(" ")
  === "university:stanford-university program:arruaad university:harvard-university", keys.join(" "));
check("the dropped item leaves the stored plan", (await stored()).items.length === 3);
const select = page.locator('select[data-status="university:stanford-university"]');
await select.selectOption("applied");
await page.waitForFunction(() => document.querySelector('[data-mylist-item="university:stanford-university"] .plan-date'));
const row = page.locator('[data-mylist-item="university:stanford-university"]');
check("a status change shows its date", (await row.locator(".plan-date").innerText()).startsWith(L.applied));
check("the next step follows the status", (await row.locator(".plan-step a").getAttribute("href")).endsWith("/programs/custodian-scholarship#ready"));
check("the keyboard stays on the same select", await page.evaluate(() =>
  document.activeElement && document.activeElement.dataset.status === "university:stanford-university"));
check("the status is saved", (await stored()).items[0].status === "applied");
await page.reload();
await page.waitForSelector("[data-mylist-rows]:not([hidden])");
check("a reload keeps the status", (await page.locator('select[data-status="university:stanford-university"]').inputValue()) === "applied");

// 4. Remove everything.
for (let i = 0; i < 3; i++) await page.locator("button[data-remove]").first().tap();
check("removing the last item shows the empty state", await page.locator("[data-mylist-empty]").isVisible()
  && (await page.locator(".mylist-empty-title").innerText()) === L.empty);
await page.goto(base + "/");
check("an empty plan hides the return strip", !(await page.locator("[data-plan-strip]").isVisible()));
check("the old address goes to the plan", (await (await page.goto(base + "/my-list")).url()).endsWith("/my-plan"));

check("no JavaScript errors", errors.length === 0, errors.join(" | "));
await browser.close();

for (const [status, name, detail] of results) console.log(`${english ? "[en] " : ""}${status}  ${name}  ${detail}`);
process.exit(results.some(([s]) => s === "FAIL") ? 1 : 0);
