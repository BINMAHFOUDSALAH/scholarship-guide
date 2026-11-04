// Drives «جرّب قبل أن تقرر» (/explore) on an emulated iPhone, with touch taps (decisions 069–070).
// pytest checks the HTML and that the result page follows the rules; this checks what only a browser shows:
// - nothing is chosen for the student, and a tap only selects (no moving on by itself);
// - the double taps that once answered the next question for the student (owner's iPhone, 2026-11-04):
//   a second tap on an answer, and a double press on «التالي», change nothing else;
// - «تخطَّ» / «التالي», «السابق», a reload starts clean, Back from the result opens the review;
// - a full run by taps: the review and the result's reasons show exactly what was tapped;
// - fast keyboard presses are never ignored.
//
// Needs Playwright (preinstalled in Claude Code cloud sessions; on your laptop it would need an install, ask
// first, CLAUDE.md). Start the server, then:
//     node scripts/check_explore.mjs                      (http://127.0.0.1:8000)
//     node scripts/check_explore.mjs http://127.0.0.1:8001
//     node scripts/check_explore.mjs http://127.0.0.1:8000 --en   (the same flows on the English page)
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
const url = host + (english ? "/en" : "") + "/explore";
const L = english
  ? { skip: "Skip", next: "Next", part1: "Part 1 of 3", activity: (n) => `Activity ${n} of 30`, none: "Not answered" }
  : { skip: "تخطَّ", next: "التالي", part1: "الجزء 1 من 3", activity: (n) => `النشاط ${n} من 30`, none: "لم تُجب" };
const results = [];
const check = (name, ok, detail = "") => results.push([ok ? "PASS" : "FAIL", name, detail]);

const browser = await chromium.launch();
const context = await browser.newContext({ ...devices["iPhone 13"] });
const page = await context.newPage();
const errors = [];
page.on("pageerror", (e) => errors.push(String(e)));

const step = () => page.locator("[data-step]:not([hidden])");
const counter = () => page.locator("[data-progress-count]").innerText();
const nextLabel = () => page.locator("[data-next]").innerText();
const checkedValues = (n) => page.evaluate((n) => [...document.querySelectorAll('[data-step][data-part="2"]')]
  .slice(0, n).map((s) => (s.querySelector("input:checked") || {}).value || "-").join(" "), n);
const tapAnswer = async (value) => {
  const label = step().locator(`label:has(input[value="${value}"])`);
  await label.scrollIntoViewIfNeeded();
  await label.tap();
};
const tapNext = async () => {
  await page.locator("[data-next]").tap();
  await page.waitForTimeout(450); // past the 400ms guard, like a student reading the next question
};
const tapTwiceAt = async (locator, gap) => {
  await locator.scrollIntoViewIfNeeded();
  const box = await locator.boundingBox();
  await page.touchscreen.tap(box.x + box.width / 2, box.y + box.height / 2);
  await page.waitForTimeout(gap);
  await page.touchscreen.tap(box.x + box.width / 2, box.y + box.height / 2);
  await page.waitForTimeout(600);
};

// Nothing chosen for the student; a tap only selects.
await page.goto(url);
check("no answer is pre-selected", (await page.locator("input:checked").count()) === 0);
check("with nothing chosen the button says skip", (await nextLabel()) === L.skip, await nextLabel());
await tapNext();
await tapAnswer("enjoy");
await page.waitForTimeout(600);
check("a tap selects and stays on the question", (await counter()) === L.activity(1), await counter());
check("after choosing the button says next", (await nextLabel()) === L.next, await nextLabel());

// The double taps.
await tapTwiceAt(step().locator('label:has(input[value="enjoy"])'), 300);
check("a double tap answers only this question", (await checkedValues(4)) === "enjoy - - -", await checkedValues(4));
await tapTwiceAt(page.locator("[data-next]"), 120);
check("a double press on next moves one step", (await counter()) === L.activity(2), await counter());
check("and leaves the next question unanswered", (await checkedValues(4)) === "enjoy - - -", await checkedValues(4));

// Back to the answer, change it, reload.
await page.locator("[data-prev]").tap();
await page.waitForTimeout(450);
check("previous shows the student's own answer", await step().locator('input[value="enjoy"]').isChecked());
await tapAnswer("ok");
check("changing an answer replaces it", (await step().locator('input[value="ok"]').isChecked())
  && !(await step().locator('input[value="enjoy"]').isChecked()));
await page.reload();
await page.waitForTimeout(400);
check("a reload starts clean", (await page.locator("input:checked").count()) === 0
  && (await page.locator("[data-progress-part]").innerText()) === L.part1);

// A full run by taps: every fifth activity skipped, the rest in turn.
const pattern = ["enjoy", "curious", "ok", "dislike", null, "cold"];
const tapped = {};
await page.locator("input[name=grade]").first().tap();
await tapNext();
for (let i = 0; i < 30; i++) {
  const value = pattern[i % pattern.length];
  if (value) {
    const text = (await step().locator("legend").innerText()).trim();
    await tapAnswer(value);
    tapped[text] = (await step().locator(`label:has(input[value="${value}"]) span`).innerText()).trim();
  }
  await tapNext();
}
await tapNext(); // subjects: skipped
await tapNext(); // the field you have in mind: skipped
const review = await page.locator("[data-review-list] .summary-row").evaluateAll((rows) =>
  rows.map((r) => [r.querySelector("dt").textContent.trim(), r.querySelector("dd > span").textContent.trim()]));
const reviewed = Object.fromEntries(review);
check("the review lists every question", review.length === 34, String(review.length));
check("the review shows exactly what was tapped",
  Object.entries(tapped).every(([q, a]) => reviewed[q] === a)
  && review.filter(([, a]) => a !== L.none).length === Object.keys(tapped).length + 1); // + the grade
await Promise.all([page.waitForNavigation(), page.locator("[data-submit-area] button").tap()]);
check("the answers never appear in the address", !page.url().includes("?"), page.url());
const reasons = await page.locator(".explore-why li").evaluateAll((items) => items.map((li) =>
  [li.querySelector(".explore-why-activity").textContent.trim(), li.querySelector(".explore-answer").textContent.trim()]));
check("the result's reasons are exactly what was tapped",
  reasons.length === Object.keys(tapped).length && reasons.every(([q, a]) => tapped[q] === a),
  `${reasons.length} reasons, ${Object.keys(tapped).length} tapped`);

// Back from the result.
await page.goBack();
await page.waitForTimeout(600);
check("Back from the result opens the review", await page.locator("[data-review]").isVisible());
check("with the answers kept", (await page.locator("input:checked").count()) === Object.keys(tapped).length + 1);
// The keyboard is never held up: fast Space / Enter presses all count (the tap guard is for taps only).
await page.goto(url);
await page.locator("[data-next]").focus();
await page.keyboard.press("Enter");
for (let i = 0; i < 3; i++) {
  await step().locator('input[value="enjoy"]').focus();
  await page.keyboard.press("Space");
  await page.locator("[data-next]").focus();
  await page.keyboard.press("Enter");
}
check("fast keyboard choices all count", (await checkedValues(3)) === "enjoy enjoy enjoy"
  && (await counter()) === L.activity(4), `${await checkedValues(3)} at ${await counter()}`);
check("no JavaScript errors", errors.length === 0, errors.join(" | "));

await browser.close();
for (const [status, name, detail] of results) console.log(`${english ? "[en] " : ""}${status}  ${name}  ${detail}`);
process.exit(results.some((r) => r[0] === "FAIL") ? 1 : 0);
