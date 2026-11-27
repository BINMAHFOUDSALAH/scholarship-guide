// Redesign v3: the main student journeys in a real browser, on an emulated phone (add --desktop for a wide screen,
// --en for the English pages, --webkit for Safari's engine).
//   node scripts/check_journeys.mjs [base] [--en] [--desktop] [--webkit]
// 1. A first-time student types «أريد دراسة علوم الحاسب في بريطانيا. من أين أبدأ؟» on the homepage: the answer
//    redraws, and the sentence's slots take the major and the country once they leave the box.
// 2. They narrow by another country with a chip, then open the full answer in the Finder.
// 3. They add two universities to the comparison, open it, and turn on «الفروق فقط».
// 4. They save a university and find it in «خطتي», which opens on their next step.
// 5. Keyboard: the question is reachable by Tab, the grade radios by arrows. Reduced motion: nothing animates.
// 6. Error and empty states: the homepage answer when the network fails, an empty comparison, an empty plan.
// Needs Playwright (npm i playwright; npx playwright install chromium).
import { chromium, webkit, devices } from "playwright";

const args = process.argv.slice(2);
const base = (args.find((a) => a.startsWith("http")) || "http://127.0.0.1:8000").replace(/\/$/, "");
const en = args.includes("--en");
const desktop = args.includes("--desktop");
const engine = args.includes("--webkit") ? webkit : chromium;
const P = en ? "/en" : "";
const failures = [];
const ok = (cond, what) => { console.log((cond ? "ok   " : "FAIL ") + what); if (!cond) failures.push(what); };

const browser = await engine.launch();
const context = await browser.newContext(desktop ? { viewport: { width: 1280, height: 900 } } : { ...devices["iPhone 13"] });
const page = await context.newPage();
const errors = [];
page.on("pageerror", (e) => errors.push(e.message));

// 1. The question on the homepage.
await page.goto(base + P + "/", { waitUntil: "networkidle" });
const q = page.locator("#home-q");
ok(await q.isVisible(), "the question's first slot is visible on the first screen");
ok((await q.inputValue()) === "" && (await page.locator("#home-country").inputValue()) === "", "the question starts empty, «أي دولة» (no example country)");
const firstCount = await page.locator(".answer-count").first().textContent();
ok(Number(firstCount) > 200, `the homepage opens on every university by country (${firstCount})`);
ok(await page.locator("a[data-set-country]").count() >= 10, "every country is one tap away");
await q.fill(en ? "I want to study computer science in the UK. Where do I start?" : "أريد دراسة علوم الحاسب في بريطانيا. من أين أبدأ؟");
await page.waitForResponse((r) => r.url().includes("/answer?"));
await page.waitForTimeout(300);
await q.blur();
await page.waitForTimeout(200);
ok((await q.inputValue()) === (en ? "computer science" : "علوم الحاسب"), "the typed question comes back as the major: " + (await q.inputValue()));
ok((await page.locator("#home-country").inputValue()) === "GB", "…and the country slot reads the UK");
ok((await page.locator(".answer-count").first().textContent()).trim() === "7", "the answer counts 7 universities in the UK");
ok(await page.locator(".acard").count() === 6, "the homepage shows three cards per list (compact)");
const status = await page.locator("[data-answer-status]").textContent();
ok(status.includes("7"), "the new answer is announced to screen readers");

// 2. Another country by chip, then the full answer.
await page.locator('a[data-set-country="US"]').first().click();
await page.waitForResponse((r) => r.url().includes("/answer?") && r.url().includes("country=US"));
await page.waitForTimeout(200);
ok((await page.locator("#home-country").inputValue()) === "US", "a country chip refills «في»");
ok(await page.evaluate(() => document.activeElement && document.activeElement.id !== "home-country" && document.activeElement.classList.contains("answer-title")),
  "…and focus lands on the new answer, not on «في» (a focused <select> opens the picker on iOS)");
// Back (owner, 2026-11-27): a flag is a step, so Back returns to the previous answer instead of leaving the site.
await page.goBack();
await page.waitForTimeout(600);
ok(page.url() === base + P + "/" && (await page.locator("#home-country").inputValue()) === "GB",
  "Back after a flag stays on the homepage with the previous answer");
await page.goForward();
await page.waitForTimeout(600);
ok((await page.locator("#home-country").inputValue()) === "US", "…and Forward brings the flag's answer back");
await page.locator("#home-country").selectOption("GB");
await page.waitForResponse((r) => r.url().includes("country=GB"));
await page.waitForTimeout(200);
await page.locator(".answer-full a").click();
await page.waitForLoadState("networkidle");
ok(page.url().includes("/universities") && page.url().includes("country=GB"), "«اعرض الإجابة كاملة» opens the Finder with the same question");
ok(await page.locator(".acard").count() === 7, "the Finder shows all 7 cards");
// A flag in the Finder is a step too: Back returns to the previous results, still in the Finder.
{
  const before = page.url();
  const chip = page.locator('#results a[data-set-country]:not([data-set-country="GB"]):not([data-set-country=""])').first();
  if (await chip.count()) {
    await chip.click();
    await page.waitForTimeout(800);
    const after = page.url();
    await page.goBack();
    await page.waitForTimeout(800);
    const same = (a, b) => new URL(a).searchParams.toString() === new URL(b).searchParams.toString();
    ok(!same(after, before) && same(page.url(), before) && (await page.locator("form[data-explorer] [name=country]").inputValue()) === "GB",
      "Back after a flag in the Finder returns to the previous results");
  }
}
ok(await page.locator(".next").isVisible(), "the Finder's answer ends on the next step");
// The grade radios: «ثاني ثانوي» shows its own steps (CSS :has, no script needed).
await page.locator('label[for="next-grade-11"]').click();
ok(await page.locator('[data-next-panel="grade-11"]').isVisible() && !(await page.locator('[data-next-panel="grade-12"]').isVisible()), "the grade switch shows that grade's steps");

// 2b. The country must never be stuck: a filter change keeps it visible as a chip, and its ✕ clears it.
await page.locator("#track").selectOption("emdad").catch(async () => {
  await page.locator("[data-filters-toggle]").click();
  await page.locator("#track").selectOption("emdad");
});
await page.waitForResponse((r) => r.url().includes("partial=1"));
await page.waitForTimeout(200);
const countryChip = page.locator('a.applied-x[data-remove="country"]');
ok(await countryChip.isVisible(), "after a filter change, the country shows as a chip with ✕");
await countryChip.click();
await page.waitForResponse((r) => r.url().includes("partial=1"));
await page.waitForTimeout(300);
ok((await page.locator("#country").inputValue()) === "", "its ✕ clears the country in the sentence too");
const flags = await page.locator("#results .uni-flag, #results .facet-flag").evaluateAll((els) => new Set(els.map((e) => e.getAttribute("src").split("/").pop())).size);
ok(flags > 1, `…and the results span several countries again (${flags} flags)`);
await page.goto(base + P + "/universities?q=" + encodeURIComponent(en ? "computer science" : "علوم الحاسب") + "&country=GB", { waitUntil: "networkidle" });

// 3. Compare two, then differences only.
const toggles = page.locator("button[data-compare]");
await toggles.nth(0).click();
await toggles.nth(4).click();
ok((await toggles.nth(0).getAttribute("aria-pressed")) === "true", "«قارن» says it's pressed");
const tray = page.locator(".compare-tray");
ok(await tray.isVisible(), "the comparison tray appears");
await tray.locator("a[data-tray-open]").click();
await page.waitForLoadState("networkidle");
ok(page.url().includes("/compare?u="), "the tray opens the comparison");
ok(await page.locator(".compare-name").count() === 2, "the comparison has two columns");
const rowsBefore = await page.locator(".compare-row:visible").count();
await page.locator("label.compare-diff").click();
const rowsAfter = await page.locator(".compare-row:visible").count();
ok(rowsAfter < rowsBefore && rowsAfter > 0, `«الفروق فقط» hides the rows that agree (${rowsBefore} → ${rowsAfter})`);

// 4. Save, then «خطتي».
await page.locator(".compare-name button[data-save]").first().click();
await page.goto(base + P + "/my-plan", { waitUntil: "networkidle" });
await page.waitForSelector("[data-mylist-item]");
ok(await page.locator(".plan-next").isVisible(), "«خطتي» opens on the next step");
const nextBox = await page.locator(".plan-next").boundingBox();
const firstRow = await page.locator("[data-mylist-item]").first().boundingBox();
ok(nextBox.y < firstRow.y, "the next step comes before the saved items");

// 5. Keyboard: Tab from the top reaches the question; reduced motion.
await page.goto(base + P + "/", { waitUntil: "networkidle" });
let reached = false;
for (let i = 0; i < 12 && !reached; i++) {
  await page.keyboard.press("Tab");
  reached = await page.evaluate(() => document.activeElement && document.activeElement.id === "home-q");
}
ok(reached, "Tab reaches the question within 12 presses");
const ring = await page.evaluate(() => getComputedStyle(document.activeElement).outlineStyle);
ok(ring !== "none", "the focused slot shows a focus ring");
await page.emulateMedia({ reducedMotion: "reduce" });
await q.fill(en ? "law" : "القانون");
await page.waitForResponse((r) => r.url().includes("/answer?"));
await page.waitForTimeout(150);
const anim = await page.evaluate(() => getComputedStyle(document.querySelector(".acard")).animationName);
ok(anim === "none", "with reduced motion the cards don't animate in");

// 6. Errors and empty states.
await page.route("**/answer?**", (route) => route.abort());
await q.fill(en ? "engineering" : "هندسة");
await page.waitForTimeout(900);
ok(await page.locator("[data-answer-target] [role=alert]").isVisible(), "a failed answer says so, with a retry");
await page.unroute("**/answer?**");
await page.goto(base + P + "/compare", { waitUntil: "networkidle" });
ok(await page.locator(".compare-empty").isVisible(), "an empty comparison says what to do");
await page.evaluate(() => localStorage.clear());
await page.goto(base + P + "/my-plan", { waitUntil: "networkidle" });
await page.waitForTimeout(300);
ok(await page.locator("[data-mylist-empty]").isVisible(), "an empty plan says what to do");

// RTL / LTR and no sideways scroll on the main pages.
for (const path of ["/", "/universities?q=" + encodeURIComponent(en ? "computer science" : "علوم الحاسب") + "&country=GB", "/compare?u=university-of-oxford,the-university-of-edinburgh", "/universities/the-university-of-edinburgh"]) {
  await page.goto(base + P + path, { waitUntil: "networkidle" });
  const dir = await page.evaluate(() => document.documentElement.dir);
  ok(dir === (en ? "ltr" : "rtl"), `${path}: dir=${dir}`);
  const wide = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  ok(wide <= 1, `${path}: no sideways scroll (${wide}px)`);
}

ok(errors.length === 0, "no JavaScript errors" + (errors.length ? ": " + errors.join(" | ") : ""));
await browser.close();
console.log(failures.length ? `\n${failures.length} FAILED` : "\nall passed");
process.exit(failures.length ? 1 : 0);
