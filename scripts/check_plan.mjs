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
  ? { save: "Save", saved: "In your plan", empty: "Your plan is empty.", applied: "Applied on" }
  : { save: "احفظ", saved: "في خطتك", empty: "خطتك فارغة.", applied: "قدّمت في" };
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

// 2. Save a program track from «البرامج» (the homepage lists a track only while it's open or opening), and a
//    university from the results.
await page.goto(base + "/programs");
const arruaad = page.locator('button[data-save="arruaad"][data-save-type="program"]').first();
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

// 3b. Redesign v3: the next step above the rows; under them every date in order, the calendar file and the route.
const lead = page.locator("[data-plan-hub]");
check("the next step shows above the rows", await lead.isVisible() && await lead.locator(".plan-next-what").isVisible()
  && await page.evaluate(() => {
    const h = document.querySelector("[data-plan-hub]"), r = document.querySelector("[data-mylist-rows]");
    return h.compareDocumentPosition(r) & Node.DOCUMENT_POSITION_FOLLOWING;
  }));
const hub = page.locator("[data-plan-dates]");
check("the dates and the route show under the rows", await hub.isVisible() && await page.evaluate(() => {
  const d = document.querySelector("[data-plan-dates]"), r = document.querySelector("[data-mylist-rows]");
  return r.compareDocumentPosition(d) & Node.DOCUMENT_POSITION_FOLLOWING;
}));
const shownDates = await hub.locator(".plan-tl-date").evaluateAll((els) => els.map((e) => e.getAttribute("datetime")));
check("the plan's dates are in order", shownDates.length > 0 && shownDates.join() === [...shownDates].sort().join(), shownDates.join(" "));
check("the route counts one item applied, lit to that step", (await hub.locator(".plan-route-stop.is-here .plan-route-count").innerText()) === "1"
  && (await hub.locator(".plan-route-stop.is-reached").count()) === 3);
check("no template is left in the rows", (await page.locator("[data-mylist-rows] template").count()) === 0);
const [download] = await Promise.all([page.waitForEvent("download"), hub.locator("[data-plan-ics]").tap()]);
const icsPath = await download.path();
const ics = (await import("node:fs")).readFileSync(icsPath, "utf8");
check("the calendar file is an .ics with the plan's dates", download.suggestedFilename() === "wadih-plan.ics"
  && ics.startsWith("BEGIN:VCALENDAR") && ics.includes("DTSTART;VALUE=DATE:") && ics.includes("TRIGGER:-P3D"), ics.slice(0, 80));
check("the calendar file holds no name or address", !/ATTENDEE|ORGANIZER|MAILTO/i.test(ics));
const accepted = page.locator('select[data-status="program:arruaad"]');
await accepted.selectOption("accepted");
await page.waitForFunction(() => document.querySelector('[data-mylist-item="program:arruaad"].is-accepted'));
check("«قُبلت» lights its row and the route reaches it", (await hub.locator(".plan-route-stop.is-here .plan-route-name").innerText()) === (english ? "Accepted" : "قُبلت"));

// 3c. «هذا صفّي» (decision 083): the grade kept on the device, marked on the homepage.
await page.goto(base + "/grades/grade-12");
const mine = page.locator("button[data-my-grade]");
await mine.tap();
check("«هذا صفّي» keeps the grade", (await page.evaluate(() => localStorage.getItem("wadih:grade"))) === "grade-12"
  && (await mine.getAttribute("aria-pressed")) === "true");
await page.goto(base + "/");
check("the homepage marks the grade «صفّك»", await page.locator('[data-grade-stop="grade-12"] [data-grade-here]').isVisible()
  && !(await page.locator('[data-grade-stop="grade-10"] [data-grade-here]').isVisible()));
await page.goto(base + "/my-plan");
await page.waitForSelector("[data-mylist-rows]:not([hidden])");

// 4. Remove everything.
for (let i = 0; i < 3; i++) await page.locator("button[data-remove]").first().tap();
check("removing the last item shows the empty state", await page.locator("[data-mylist-empty]").isVisible()
  && (await page.locator(".mylist-empty-title").innerText()) === L.empty);
await page.goto(base + "/");
check("an empty plan hides the return strip", !(await page.locator("[data-plan-strip]").isVisible()));
check("the old address goes to the plan", (await (await page.goto(base + "/my-list")).url()).endsWith("/my-plan"));

// 5. A slow connection (2026-11-27, seen on the live site): three removals tapped quickly while every redraw takes
// 1.5s. A late redraw must not bring back a row already removed.
await page.evaluate(() => localStorage.setItem("wadih:plan", JSON.stringify({ v: 1, items: [
  { type: "university", id: "university-of-oxford", status: "thinking" },
  { type: "university", id: "harvard-university", status: "thinking" },
  { type: "university", id: "stanford-university", status: "thinking" }] })));
await page.goto(base + "/my-plan");
await page.waitForSelector("[data-mylist-rows]:not([hidden]) button[data-remove]");
await page.route("**/my-plan", async (route) => {
  if (route.request().method() === "POST") await new Promise((r) => setTimeout(r, 1500));
  await route.continue();
});
for (let i = 0; i < 3; i++) { await page.locator("button[data-remove]").first().tap(); await page.waitForTimeout(150); }
await page.waitForTimeout(4000);
const slow = await page.evaluate(() => ({ rows: document.querySelectorAll("[data-mylist-item]").length,
  empty: !document.querySelector("[data-mylist-empty]").hidden, items: JSON.parse(localStorage.getItem("wadih:plan")).items.length }));
check("quick removals on a slow connection leave the plan empty, with no row coming back",
  slow.rows === 0 && slow.empty && slow.items === 0, JSON.stringify(slow));
await page.unroute("**/my-plan");

check("no JavaScript errors", errors.length === 0, errors.join(" | "));
await browser.close();

for (const [status, name, detail] of results) console.log(`${english ? "[en] " : ""}${status}  ${name}  ${detail}`);
process.exit(results.some(([s]) => s === "FAIL") ? 1 : 0);
