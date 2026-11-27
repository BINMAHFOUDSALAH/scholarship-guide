// The search-and-compare journey (2026-11-27), end to end in a real browser:
//   node scripts/check_compare.mjs [base] [--en] [--desktop] [--dark]
// A major in a country on the homepage, «احفظ», two universities chosen with «قارن» (one by keyboard), the comparison
// with its sources hidden then shown (Space on the switch), «الفروق فقط» with sources still on, every per-university
// source in its own column, the names kept in view down the table, «قارن الجامعات» reopening it from the homepage,
// «الرجوع إلى نتائج البحث» keeping the search (homepage and Finder), and the chooser when nothing is picked.
import { chromium, devices } from "playwright";
const en = process.argv.includes('--en'), desk = process.argv.includes('--desktop'), dark = process.argv.includes('--dark');
const base = process.argv.slice(2).find((a) => a.startsWith('http')) || 'http://127.0.0.1:8000';
const B = base + (en ? '/en' : '');
const b = await chromium.launch();
const ctx = await b.newContext({ ...(desk ? { viewport: { width: 1280, height: 900 } } : devices['iPhone 13']), colorScheme: dark ? 'dark' : 'light' });
const p = await ctx.newPage();
const errors = []; p.on('pageerror', e => errors.push(e.message));
let fails = 0; const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) fails++; };
const sideways = async () => p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);

// 1. search a major in a country on the homepage
await p.goto(B + '/'); await p.waitForLoadState('networkidle');
ok(await p.getAttribute('html', 'dir') === (en ? 'ltr' : 'rtl'), 'dir ' + (en ? 'ltr' : 'rtl'));
await p.fill('#home-q', en ? 'Artificial Intelligence' : 'الذكاء الاصطناعي');
await p.selectOption('#home-country', 'US');
await p.waitForTimeout(1200);
const title = await p.locator('.answer-title').first().innerText();
ok(/34/.test(title), 'answer: ' + title.replace(/\s+/g, ' '));
ok((await p.locator('.acard-why').first().innerText()).length > 5, 'each card says why it matched');
ok(await sideways() <= 0, 'homepage no sideways scroll');
// keyboard: the lime button and the compare link are reachable and visible on focus
await p.locator('.btn--lime').focus(); ok(await p.evaluate(() => document.activeElement.classList.contains('btn--lime')), 'keyboard reaches «اعرض الجامعات»');
await p.keyboard.press('Tab'); ok(await p.evaluate(() => document.activeElement.matches('a[data-compare-entry]')), 'Tab moves to «قارن الجامعات»');

// 2. save one, and choose two universities with «قارن» (one by keyboard)
const cards = p.locator('.acard');
const save = cards.nth(0).locator('button[data-save]');
await save.click(); await p.waitForTimeout(200);
ok(await save.getAttribute('aria-pressed') === 'true' || /خطت|plan/i.test(await save.innerText()), 'save works: ' + (await save.innerText()).trim());
await cards.nth(0).locator('button[data-compare]').click();
await cards.nth(1).locator('button[data-compare]').focus(); await p.keyboard.press('Enter');
await p.waitForTimeout(200);
ok(await cards.nth(1).locator('button[data-compare]').getAttribute('aria-pressed') === 'true', 'keyboard Enter adds to the comparison');
const ids = await p.evaluate(() => JSON.parse(localStorage.getItem('wadih:compare')));
ok(ids.length === 2, 'two picks: ' + ids.join(','));
ok((await p.getAttribute('a[data-compare-entry]', 'href')).endsWith('/compare?u=' + ids.join(',')), 'homepage link points at the comparison');

// 3. open the comparison
await p.click('[data-tray-open]'); await p.waitForLoadState('networkidle');
ok(p.url().includes('/compare?u=' + ids.join(',')), 'comparison opened: ' + p.url());
{ const sw = await sideways(); const who = await p.evaluate(() => [...document.querySelectorAll('body *')].filter(el => { const r = el.getBoundingClientRect(); return r.width && (r.right > innerWidth + 1 || r.left < -1) && !el.closest('.menu-panel'); }).slice(0, 6).map(el => el.tagName + '.' + (el.className || '').toString().slice(0, 30) + ' ' + Math.round(el.getBoundingClientRect().left) + '..' + Math.round(el.getBoundingClientRect().right))); ok(sw <= 0, 'comparison no sideways scroll ' + sw + ' ' + who.join(' / ')); }
const srcVisible = () => p.evaluate(() => [...document.querySelectorAll('.compare-src')].filter(e => e.offsetParent).length);
ok(await srcVisible() === 0, 'sources hidden by default');
ok(await p.locator('.compare-value').first().isVisible(), 'values shown');

// 4. sources on (keyboard: Space on the switch), then differences only: both apply together
await p.locator('#compare-sources').focus(); await p.keyboard.press('Space');
ok(await p.isChecked('#compare-sources'), 'keyboard Space turns sources on');
const nSrc = await srcVisible();
ok(nSrc > 0, 'sources visible: ' + nSrc);
const rowsAll = await p.evaluate(() => [...document.querySelectorAll('tr.compare-row')].filter(e => e.offsetParent).length);
await p.click('label[for=compare-diff]');
const rowsDiff = await p.evaluate(() => [...document.querySelectorAll('tr.compare-row')].filter(e => e.offsetParent).length);
const sameShown = await p.evaluate(() => [...document.querySelectorAll('[data-same]')].filter(e => e.offsetParent).length);
ok(rowsDiff < rowsAll && sameShown === 0, `differences only: ${rowsAll} → ${rowsDiff} rows`);
ok(await srcVisible() > 0 && await p.isChecked('#compare-sources'), 'sources still on with differences only');
// every visible per-cell source sits in the column of its university
const mismatch = await p.evaluate(() => {
  const names = [...document.querySelectorAll('th.compare-name')].map(th => th.id.replace('col-', ''));
  let bad = 0, n = 0;
  for (const a of document.querySelectorAll('td .compare-src')) {
    if (!a.offsetParent) continue; n++;
    const td = a.closest('td'); const col = td.getAttribute('headers').split(' ').pop().replace('col-', '');
    if (!names.includes(col)) bad++;
  }
  return { bad, n };
});
ok(mismatch.bad === 0 && mismatch.n > 0, `per-cell sources in their own column (${mismatch.n})`);
// the names stay in view several screens down
await p.evaluate(() => { const rows = [...document.querySelectorAll('tr.compare-row')].filter(e => e.offsetParent); const r = rows[rows.length - 1]; window.scrollTo(0, r.getBoundingClientRect().top + scrollY - 300); });
await p.waitForTimeout(300);
const stick = await p.evaluate(() => { const bar = document.querySelector('[data-compare-stick]'); const r = bar.getBoundingClientRect(); return { hidden: bar.hidden, top: Math.round(r.top), text: bar.textContent.replace(/\s+/g, ' ').trim() }; });
ok(!stick.hidden && stick.top >= -1 && stick.top < 5, `sticky names after scrolling (top ${stick.top}, hidden ${stick.hidden}): ${stick.text}`);

// 5. back to the homepage: «قارن الجامعات» reopens it
await p.goto(B + '/'); await p.waitForLoadState('networkidle');
await p.click('a[data-compare-entry]'); await p.waitForLoadState('networkidle');
ok(p.url().includes('/compare?u=' + ids.join(',')), 'homepage link reopens the comparison');

// 6. back to results from a university, homepage and Finder
await p.goto(B + '/'); await p.waitForLoadState('networkidle');
await p.fill('#home-q', en ? 'Artificial Intelligence' : 'الذكاء الاصطناعي'); await p.selectOption('#home-country', 'US'); await p.waitForTimeout(1200);
await p.locator('.acard a.uni-name').first().click(); await p.waitForLoadState('networkidle');
await p.click('a[data-back-link]'); await p.waitForTimeout(1500);
ok((await p.inputValue('#home-q')).length > 0 && await p.inputValue('#home-country') === 'US', 'back from a university keeps the homepage question');
await p.click('.btn--lime'); await p.waitForLoadState('networkidle');
await p.locator('.acard a.uni-name').nth(1).click(); await p.waitForLoadState('networkidle');
await p.click('a[data-back-link]'); await p.waitForLoadState('networkidle'); await p.waitForTimeout(500);
ok(/country=US/.test(p.url()) && /q=/.test(p.url()), 'back from a university keeps the Finder search: ' + decodeURIComponent(p.url()));
ok(/34/.test(await p.locator('.answer-title').first().innerText()), 'same 34 results');

// 7. an empty comparison is a place to choose
await p.evaluate(() => localStorage.removeItem('wadih:compare'));
await p.goto(B + '/'); await p.waitForLoadState('networkidle');
ok((await p.getAttribute('a[data-compare-entry]', 'href')).endsWith('/compare'), 'no picks: link opens the chooser');
await p.click('a[data-compare-entry]'); await p.waitForLoadState('networkidle');
ok(await p.locator('[data-compare-pick]').isVisible(), 'chooser shown');
ok(errors.length === 0, 'no JavaScript errors ' + errors.join(' | '));
console.log(fails ? `${fails} FAILED` : 'all passed');
await b.close();
process.exit(fails ? 1 : 0);
