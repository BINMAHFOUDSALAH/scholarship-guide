// Drives «جرّب قبل أن تقرر» (/explore) on an emulated iPhone, with touch taps (decisions 069–072, 088: 15 questions,
// 14 activities then the subjects).
// pytest checks the HTML and that the result page follows the rules; this checks what only a browser shows:
// - nothing is chosen for the student; a tap on an activity's answer moves on once, by itself (decision 072);
// - the double taps that once answered the next question for the student (owner's iPhone, 2026-11-04): a second
//   tap before or just after the move, and a double press on «تخطَّ», never answer another question;
// - changing your mind before the move keeps the last choice; «السابق» shows your answer, and tapping it moves on;
// - the keyboard: Space and the arrow keys choose without moving on, Enter moves on, and nothing is held up;
// - a reload starts clean; Back returns to where the student left off (the last step from the result);
// - the last question goes straight to the result, and a double tap on the step before it never sends the form;
// - a full run by taps only: the result's reasons show exactly what was tapped;
// - the result: each card has its picture, title, reason and majors, and its one action opens and closes in place.
//
// Needs Playwright (preinstalled in Claude Code cloud sessions; on your laptop it needs an install, ask first,
// CLAUDE.md; outside this folder, point NODE_PATH at it). Start the server, then:
//     node scripts/check_explore.mjs                      (http://127.0.0.1:8000)
//     node scripts/check_explore.mjs http://127.0.0.1:8001
//     node scripts/check_explore.mjs http://127.0.0.1:8000 --en   (the same flows on the English page)
//     node scripts/check_explore.mjs --webkit             (in Safari's engine)
// Prints PASS/FAIL per check; exits 1 if any check fails.

import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
let playwright;
try {
  playwright = require("playwright");
} catch {
  playwright = require("/opt/node22/lib/node_modules/playwright"); // global install in cloud sessions
}
const { chromium, webkit, devices } = playwright;
const english = process.argv.includes("--en");
const engine = process.argv.includes("--webkit") ? webkit : chromium; // Safari's engine (decision 073)
const host = process.argv.slice(2).find((a) => a.startsWith("http")) || "http://127.0.0.1:8000";
const url = host + (english ? "/en" : "") + "/explore";
const L = english
  ? { skip: "Skip", next: "Next", activity: (n) => `Question ${n} of 15` }
  : { skip: "تخطَّ", next: "التالي", activity: (n) => `السؤال ${n} من 15` };
const results = [];
const check = (name, ok, detail = "") => results.push([ok ? "PASS" : "FAIL", name, detail]);

const browser = await engine.launch();
const context = await browser.newContext({ ...devices["iPhone 13"] });
const page = await context.newPage();
const errors = [];
page.on("pageerror", (e) => errors.push(String(e)));

const step = () => page.locator("[data-step]:not([hidden])");
const counter = () => page.locator("[data-progress-count]").innerText();
const nextLabel = () => page.locator("[data-next]").innerText();
const checkedValues = (n) => page.evaluate((n) => [...document.querySelectorAll('[data-step][data-part="activity"]')]
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
// Where an answer is on screen, to tap it straight away. Playwright's own tap first waits for the page to settle, which
// in WebKit can take longer than the moments these checks are about: a finger doesn't wait.
const spot = async (value) => {
  const label = step().locator(`label:has(input[value="${value}"])`);
  await label.scrollIntoViewIfNeeded();
  const box = await label.boundingBox();
  return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
};
const fingerTap = (at) => page.touchscreen.tap(at.x, at.y);

// Nothing chosen for the student.
await page.goto(url);
check("no answer is pre-selected", (await page.locator("input:checked").count()) === 0);
check("with nothing chosen the button says skip", (await nextLabel()) === L.skip, await nextLabel());

// A tap on an answer moves on, once, and records only that answer.
await tapAnswer("enjoy");
await settle();
check("a tap on an answer moves on", (await counter()) === L.activity(2), await counter());
check("and records only that answer", (await checkedValues(3)) === "enjoy - -", await checkedValues(3));

// The double taps: before the move (same question) and just after it (inside the guard). One answer, one move.
for (const gap of [150, 350]) {
  await page.goto(url);
  await tapTwiceAt(step().locator('label:has(input[value="enjoy"])'), gap);
  await settle();
  check(`a double tap (${gap}ms apart) answers one question and moves once`,
    (await checkedValues(3)) === "enjoy - -" && (await counter()) === L.activity(2), `${await checkedValues(3)} at ${await counter()}`);
}

// Changing your mind before the move: the last choice wins, one move.
await page.goto(url);
const [enjoyAt, dislikeAt] = [await spot("enjoy"), await spot("dislike")];
await fingerTap(enjoyAt);
await page.waitForTimeout(100);
await fingerTap(dislikeAt);
await settle();
check("changing your mind before the move keeps the last choice", (await checkedValues(2)) === "dislike -"
  && (await counter()) === L.activity(2), `${await checkedValues(2)} at ${await counter()}`);

// A double press on «تخطَّ»: one step, nothing answered.
await page.goto(url);
await page.waitForTimeout(450);
await tapTwiceAt(page.locator("[data-next]"), 120);
check("a double press on skip moves one step and answers nothing",
  (await counter()) === L.activity(2) && (await checkedValues(2)) === "- -", `${await checkedValues(2)} at ${await counter()}`);

// «السابق» shows the student's answer; tapping it again moves on; changing it replaces it.
await page.goto(url);
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
  && (await counter()) === L.activity(1));

// A full run by taps only: answered activities move on by themselves, skipped ones with «تخطَّ».
const pattern = ["enjoy", "ok", "dislike", null];
const tapped = {};
for (let i = 0; i < 14; i++) {
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
  if (i < 13 && (await counter()) === before) { check(`activity ${i + 1} moved on`, false, before); break; }
}
await tapNext(); // subjects: skipped
// The last question: its button goes straight to the result; there is no page in between.
check("the last question has no next step, only the result's button", await page.locator("[data-submit]").isVisible()
  && !(await page.locator("[data-next]").isVisible()) && (await page.locator("[data-review]").count()) === 0);
check("and «previous» is still there to change an answer", await page.locator("[data-prev]").isVisible());
await Promise.all([page.waitForNavigation(), page.locator("[data-submit]").tap()]);
check("the answers never appear in the address", !page.url().includes("?"), page.url());
const reasons = await page.locator(".explore-why li").evaluateAll((items) => items.map((li) =>
  [li.querySelector(".explore-why-activity").textContent.trim(), li.querySelector(".explore-answer").textContent.trim()]));
check("the result's reasons are exactly what was tapped",
  reasons.length === Object.keys(tapped).length && reasons.every(([q, a]) => tapped[q] === a),
  `${reasons.length} reasons, ${Object.keys(tapped).length} tapped`);

// The result: what a student sees, and the one action on a card.
const cards = page.locator(".explore-band .explore-field");
const shown = await cards.count();
check("the result shows field cards", shown > 0, String(shown));
const complete = await cards.evaluateAll((all) => all.every((card) => {
  const art = card.querySelector(".explore-field-art");
  return card.querySelector(".explore-field-name").textContent.trim()
    && card.querySelector(".explore-majors li") && card.querySelectorAll("summary").length === 1
    && art.getAttribute("src").includes("/img/fields/");
}));
check("every card has a picture, a title, majors and one action", complete);
const firstCard = cards.first();
await firstCard.scrollIntoViewIfNeeded();
const picture = firstCard.locator(".explore-field-art");
await picture.evaluate((img) => img.complete || new Promise((done) => { img.onload = done; img.onerror = done; }));
check("a picture really loads", (await picture.evaluate((img) => img.naturalWidth)) > 0);
const noScroll = await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);
check("the page doesn't scroll sideways on a phone", noScroll);
const action = firstCard.locator("summary");
const detail = firstCard.locator(".explore-dive .summary-list");
check("the card's details start closed", !(await detail.isVisible()));
await action.tap();
await page.waitForTimeout(250);
check("the action opens the details in place", (await detail.isVisible()) && /\/explore\/result$/.test(page.url()), page.url());
await action.tap();
await page.waitForTimeout(250);
check("and closes them again", !(await detail.isVisible()));

// Back from the result.
await page.goBack();
await page.waitForTimeout(600);
check("Back from the result opens the last question", await page.locator("[data-submit]").isVisible()
  && (await counter()) === L.activity(15), await counter());
check("with the answers kept", (await page.locator("input:checked").count()) === Object.keys(tapped).length);

// A double tap on the button before the last question: the buttons are pinned in place here, the worst case, so the
// second tap lands exactly on the result's button.
await page.goto(url);
await page.addStyleTag({ content: ".explore-nav{position:fixed!important;bottom:20px;left:16px;right:16px;z-index:9;margin:0!important}" });
for (let i = 0; i < 13; i++) await tapNext();
const beforeLast = page.url();
await tapTwiceAt(page.locator("[data-next]"), 120);
check("a double tap on the step before the last never sends the form", page.url() === beforeLast
  && await page.locator("[data-submit]").isVisible(), page.url());
// The keyboard: Space and the arrow keys choose without moving on; Enter moves on; nothing is held up.
await page.goto(url);
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
await page.waitForTimeout(450);
const nextAt = await page.locator("[data-next]").boundingBox();
const answerAt = await spot("ok"); // the answers sit in the same place on the next question
await page.touchscreen.tap(nextAt.x + nextAt.width / 2, nextAt.y + nextAt.height / 2); // skip activity 1: moves to activity 2 and starts the guard
await fingerTap(answerAt); // at once: the accidental second tap
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
check("Back after leaving mid-activity returns to the same question, answers kept",
  (await checkedValues(3)) === "- dislike ok" && back === L.activity(4), back);

check("no JavaScript errors", errors.length === 0, errors.join(" | "));

await browser.close();
for (const [status, name, detail] of results) console.log(`${english ? "[en] " : ""}${status}  ${name}  ${detail}`);
process.exit(results.some((r) => r[0] === "FAIL") ? 1 : 0);
