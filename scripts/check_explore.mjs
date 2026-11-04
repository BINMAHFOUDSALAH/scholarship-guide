// Drives «جرّب قبل أن تقرر» (/explore) on an emulated iPhone, with touch taps (decisions 069–072).
// pytest checks the HTML and that the result page follows the rules; this checks what only a browser shows:
// - nothing is chosen for the student; a tap on an activity's answer moves on once, by itself (decision 072);
// - the double taps that once answered the next question for the student (owner's iPhone, 2026-11-04): a second
//   tap before or just after the move, and a double press on «تخطَّ», never answer another question;
// - changing your mind before the move keeps the last choice; «السابق» shows your answer, and tapping it moves on;
// - the keyboard: Space and the arrow keys choose without moving on, Enter moves on, and nothing is held up;
// - a reload starts clean; Back returns to where the student left off (the review from the result);
// - a full run by taps only: the review and the result's reasons show exactly what was tapped.
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

const settle = () => page.waitForTimeout(800); // past the 300ms move and the 400ms guard

// Nothing chosen for the student.
await page.goto(url);
check("no answer is pre-selected", (await page.locator("input:checked").count()) === 0);
check("with nothing chosen the button says skip", (await nextLabel()) === L.skip, await nextLabel());

// A tap on an answer moves on, once, and records only that answer.
await tapNext();
await tapAnswer("enjoy");
await settle();
check("a tap on an answer moves on", (await counter()) === L.activity(2), await counter());
check("and records only that answer", (await checkedValues(3)) === "enjoy - -", await checkedValues(3));

// The double taps: before the move (same question) and just after it (inside the guard). One answer, one move.
for (const gap of [150, 350]) {
  await page.goto(url);
  await tapNext();
  await tapTwiceAt(step().locator('label:has(input[value="enjoy"])'), gap);
  await settle();
  check(`a double tap (${gap}ms apart) answers one question and moves once`,
    (await checkedValues(3)) === "enjoy - -" && (await counter()) === L.activity(2), `${await checkedValues(3)} at ${await counter()}`);
}

// Changing your mind before the move: the last choice wins, one move.
await page.goto(url);
await tapNext();
await tapAnswer("enjoy");
await page.waitForTimeout(100);
await tapAnswer("dislike");
await settle();
check("changing your mind before the move keeps the last choice", (await checkedValues(2)) === "dislike -"
  && (await counter()) === L.activity(2), `${await checkedValues(2)} at ${await counter()}`);

// A double press on «تخطَّ»: one step, nothing answered.
await page.goto(url);
await tapNext();
await tapTwiceAt(page.locator("[data-next]"), 120);
check("a double press on skip moves one step and answers nothing",
  (await counter()) === L.activity(2) && (await checkedValues(2)) === "- -", `${await checkedValues(2)} at ${await counter()}`);

// «السابق» shows the student's answer; tapping it again moves on; changing it replaces it.
await page.goto(url);
await tapNext();
await tapAnswer("enjoy");
await settle();
await page.locator("[data-prev]").tap();
await page.waitForTimeout(450);
check("previous shows the student's own answer", (await counter()) === L.activity(1)
  && (await step().locator('input[value="enjoy"]').isChecked()) && (await nextLabel()) === L.next);
await tapAnswer("enjoy");
await settle();
check("tapping your own answer again moves on", (await counter()) === L.activity(2), await counter());
await page.locator("[data-prev]").tap();
await page.waitForTimeout(450);
await tapAnswer("ok");
await settle();
check("changing an answer replaces it", (await checkedValues(2)) === "ok -" && (await counter()) === L.activity(2),
  `${await checkedValues(2)} at ${await counter()}`);
await page.reload();
await page.waitForTimeout(400);
check("a reload starts clean", (await page.locator("input:checked").count()) === 0
  && (await page.locator("[data-progress-part]").innerText()) === L.part1);

// A full run by taps only: answered activities move on by themselves, skipped ones with «تخطَّ».
const pattern = ["enjoy", "curious", "ok", "dislike", null, "cold"];
const tapped = {};
await page.locator("input[name=grade]").first().tap();
await tapNext();
for (let i = 0; i < 30; i++) {
  const value = pattern[i % pattern.length];
  const before = await counter();
  if (value) {
    const text = (await step().locator("legend").innerText()).trim();
    await tapAnswer(value);
    tapped[text] = (await step().locator(`label:has(input[value="${value}"]) span`).innerText()).trim();
    await settle();
  } else {
    await tapNext();
  }
  if (i < 29 && (await counter()) === before) { check(`activity ${i + 1} moved on`, false, before); break; }
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
// The keyboard: Space and the arrow keys choose without moving on; Enter moves on; nothing is held up.
await page.goto(url);
await page.locator("[data-next]").focus();
await page.keyboard.press("Enter");
await step().locator('input[value="enjoy"]').focus();
await page.keyboard.press("Space");
await page.waitForTimeout(600);
check("a key press chooses without moving on", (await counter()) === L.activity(1) && (await checkedValues(1)) === "enjoy",
  `${await checkedValues(1)} at ${await counter()}`);
await page.keyboard.press("ArrowDown");
await page.waitForTimeout(600);
check("an arrow key changes the choice without moving on", (await counter()) === L.activity(1)
  && (await checkedValues(1)) !== "enjoy" && (await checkedValues(1)) !== "-", `${await checkedValues(1)} at ${await counter()}`);
await page.keyboard.press("Enter");
for (let i = 0; i < 3; i++) { // fast: Space then Enter, no waiting
  await step().locator('input[value="enjoy"]').focus();
  await page.keyboard.press("Space");
  await page.keyboard.press("Enter");
}
check("Enter moves on, and fast key presses all count", (await counter()) === L.activity(5)
  && (await checkedValues(4)).endsWith("enjoy enjoy enjoy"), `${await checkedValues(4)} at ${await counter()}`);

// The guard's own job: a tap on an answer right after moving on (the second tap of a double tap) is ignored.
await page.goto(url);
await tapNext();
await page.locator("[data-next]").tap(); // skip activity 1: moves to activity 2 and starts the guard
await step().locator('label:has(input[value="dislike"])').tap(); // at once: the accidental second tap
await page.waitForTimeout(100);
check("a tap right after moving on is ignored", (await checkedValues(2)) === "- -" && (await counter()) === L.activity(2),
  `${await checkedValues(2)} at ${await counter()}`);
await page.waitForTimeout(400);
await tapAnswer("dislike"); // a moment later: a real choice
await settle();
check("a moment later the same tap counts", (await checkedValues(2)) === "- dislike" && (await counter()) === L.activity(3),
  `${await checkedValues(2)} at ${await counter()}`);
await tapAnswer("ok");
await settle();

// Leaving mid-activity and coming back with Back: the answers are kept, never shown as a fresh start.
await Promise.all([page.waitForURL(/\/resources\/undecided/), page.locator(".doc-kind a").tap()]); // the guide link above the title
// The browser's own Back (Playwright's goBack reports a restore from the browser's memory as "aborted").
await page.evaluate(() => history.back()).catch(() => {}); // the page it ran on is left: expected
await page.waitForURL(/\/explore$/);
await page.waitForTimeout(800);
const back = await counter().catch(() => "");
const reviewShown = await page.locator("[data-review]").isVisible();
check("Back after leaving mid-activity returns to the same question, answers kept",
  (await checkedValues(3)) === "- dislike ok" && back === L.activity(4) && !reviewShown, reviewShown ? "review" : back);

check("no JavaScript errors", errors.length === 0, errors.join(" | "));

await browser.close();
for (const [status, name, detail] of results) console.log(`${english ? "[en] " : ""}${status}  ${name}  ${detail}`);
process.exit(results.some((r) => r[0] === "FAIL") ? 1 : 0);
