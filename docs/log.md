# Project log

What each working session did and left open, newest first. Notes are kept as they were written, so older
ones can be out of date. Today's plan and to-dos are in [roadmap.md](roadmap.md); the reasons for each
choice are in [decisions.md](decisions.md).

## 2026-11-06

**2026-11-06 (owner):** «لم تقرر بعد؟»: removed the section «الميل غير القدرة، والقدرة غير القبول» and the line that linked to it (owner: vague, not helpful).

**2026-11-06 (decision 080, Phase 1 Part B done):** «خطتي» replaces «قائمتي»: universities and program tracks with a status and its date, on the device (`wadih:plan`); the server draws each row's next step from a POST and stores nothing (`app/plan.py`); «احفظ» on every high-school track; the homepage's return line; old saves move in. New check: `node scripts/check_plan.mjs` (18 checks, Arabic and English).
- **Not checked:** a real phone, Safari, screen reader. **Owner to-dos:** save a university and الرواد on your phone, change a status, come back.

**2026-11-06 (decision 079, Phase 1 Part A done):** A2: «مفتوح للتقديم الآن» and «البرامج» grouped by when you apply (`apply_when`); A3: whole-word major search, a sourced answer for health majors; A4: grade 12's «من أين تبدأ؟» and an honest «ابدأ الآن»; A5: no bare zeros, «108 جامعات», the dead handbook no longer cited. Owner: removed lines that tell students what they know (the Qabool notice, «القرار… للوزارة وحدها», the footer's "not affiliated", kept on /about).
- **Checked:** pytest, both explorer checks (Arabic, English), the activity check; screenshots at 390px and 1280px. **Not checked:** a real phone, screen reader.

**2026-11-06 (decision 078, Phase 1 A1):** the Phase 1 plan is in the repo (decision 078: Part A fixes, Part B «خطتي» on the device, Phase 2 accounts + the AI assistant from 25 Nov). A1 built on `feature/phase1-part-a`: «معي قبول جامعي» on the Custodian program page (`#ready`), five steps from the page's frontmatter, each linking a sourced fact on the same page; step 4 shows الرواد/إمداد status and «قدّم عبر منصة قبول ↗» only while open. Tests: every step links an existing sourced fact; open and closed windows.
- **Not checked:** a real phone, screen reader, keyboard. **Owner to-dos:** look at `#ready` on your phone.
- **Git rule (owner):** once verified, Claude commits, pushes a branch, opens a PR and merges after CI, without asking (CLAUDE.md).

## 2026-11-05

**2026-11-05 (/update-site):** nothing new or past to change (KGSP, the universities guide, الرواد, إمداد, Aramco and Cambridge unchanged; SDAIA refused scripts). Fixed: the site read "today" on the server's UTC clock, so a deadline lasted until 3 am in Riyadh; now `app/clock.py` gives the day in Riyadh (UTC+3) and every deadline follows it.
- **Left open:** the career guidance handbook 404 (as on 4 Nov). **Owner to-dos:** check @SA_Scholarships and @SDAIA_SA on X; الرواد closes 15 Nov.

**2026-11-05 (decision 077):** subagent models: `source-researcher` stays on Haiku; `fact-checker` and `reviewer` move to Sonnet. Haiku is now the default, no longer forced. Written as aliases (`haiku`, `sonnet`), so they follow the latest versions.
- **Owner to-dos:** none; the first `fact-checker` run on Sonnet is a chance to compare.

**2026-11-05 (decision 076):** design tools chosen: `frontend-design` to build; `web-design-guidelines` (new project skill, pinned rules with واضح overrides), `design-critique` and `accessibility-review` to review. Taste, UI/UX Pro Max and Impeccable not installed (they compete with `design.md`). CLAUDE.md: `design.md` beats any plugin.
- First run on the homepage (fixed): the «وغيرها (n)» links were split strings (English read "And more (3) in Application dates"), now one string each; the dropdown arrow sat over the text on English pages, now on the end side in both directions. Left as polish: announce the number of search suggestions; `touch-action`.

**2026-11-05 (decision 075):** a colour pass. Each of the 10 fields has its own tone (drawings recoloured; result cards, explorer field picker and university pages use it), a sun-yellow door to «جرّب قبل أن تقرر» with the ten tones beside it, «تقدم الآن» filled, a sand band under the homepage's quote.
- **Owner to-dos:** look at the result on your phone in both themes; say if any two fields still feel too alike.

## 2026-11-04

**2026-11-04 (/update-site):** nothing to remove (the oldest واعد program closed 2 Aug, inside the 120 days; the site closes programs by date). SAT: next date now 5 Dec, since registration for 7 Nov has closed. The Ministry rebuilt its site: the tracks document has a new address.
- **Left open (owner chose to skip):** the career guidance handbook (دليل التوجيه المهني 1444هـ) is a 404 and wasn't found on the new site. Still cited in `content/resources/undecided.md`, `content/grades/grade-10.md`, `data/exploration.json` and `app/templates/explore_result.html`; the daily check keeps listing it.
- **Owner to-dos:** check [@SA_Scholarships](https://x.com/SA_Scholarships) for news on الرواد and إمداد.

**2026-11-04 (decision 074):** the repository tidied for visitors: a rewritten README with a screenshot, this log split out of the roadmap, a map of `docs/`, the ad's guide moved to `marketing/README.md`, an MIT licence for the code. On GitHub: the About box, the unused tabs off, 15 merged branches deleted.

**2026-11-04 (decision 073, merged in PR #35):** «جرّب قبل أن تقرر»: no «غيّر» page (the last question goes straight to the result), and a redesigned result in both languages: a lead naming the closest fields, then one card per field with its own drawing, a plain title, one sentence of why, real majors and one action that opens in place. The majors for health, education and arts come from the Ministry's Saudi unified classification, read directly.
- **Owner to-dos:** try the whole journey on your own iPhone in Safari, Arabic and English (checked on emulated iPhones only, Chromium and WebKit); read the 10 titles and the why sentences.

**2026-11-04 (decision 072):** a tap on an activity's answer moves on by itself again (owner: «التالي» 30 times is too slow), with the safeguards: a second tap before the move stays on the same question, one just after it is ignored, keys never move on. `node scripts/check_explore.mjs`: 25 checks.

**2026-11-04 (decision 071):** «جرّب قبل أن تقرر» fixed after the owner's iPhone test: a tap only selects (no moving on by itself, which let a second tap answer the next question), nothing pre-chosen, «تخطَّ» / «التالي», a reload starts clean, a shortlist of three in «تستحق التجربة». New check: `node scripts/check_explore.mjs`. The line «لا نحفظ إجاباتك…» is removed (owner).

**2026-11-04 (decision 070):** «جرّب قبل أن تقرر» (`/explore`) is **live**, with a door on the homepage under the grades («لم تقرر ماذا تدرس؟»). Published by the owner before the counsellor review.

**2026-11-04 (decision 069, merged in PR #31):** the «لم تقرر بعد؟» guide (`/resources/undecided`, in the homepage guides and on the grade 10 page), and «جرّب قبل أن تقرر» built as an unscored exploration activity (research: `docs/research/career-exploration-evaluation-2026-11.md`). Checked: 717 tests; a UI sweep at 320–1280px in both themes and languages, keyboard only, without JavaScript and in print.
- **Owner to-dos:**
  - open /explore and the homepage on a real phone (Safari especially);
  - get one Saudi school counsellor (and, if possible, a career-development specialist) to review the 30 activities, the subject map and the wording; then set `expert_reviewed: true` in `data/exploration.json`;
  - try it with 5 students in the usability test (research note §9: can they name a field to explore and one action; does anyone read it as "the site told me what to study"?);
  - check the Ministry's grade 10 interest measure on an official page (press says it counts in placement; not published).

**2026-11-04 (decision 068):** phone header: four 48px controls (language, «قائمتي», theme, «القائمة» with its label from 480px; 44px up to 389px); the menu opens full width with 48px rows.

**2026-11-04 (decision 067):** the header fits on one line at every width (320–1400px swept, both languages): icon tools below 1100px, the full nav from 1100px, no descriptor below 600px. SDAIA: no date on its page = nothing to update (`no_deadline_ok`).

**2026-11-04 (decision 066): the English version, merged in PR #27 (owner-approved) and live at https://wadihguide.com/en/ after CI.**
- `/update-site` run the same day: nothing to change. Re-checked and unchanged on their official pages: KGSP (Cohort 19 «will open soon», no dates), Aramco CDPNE (registration closed, still 1447–1448), the universities guide (still 2026–2027), the الرواد and إمداد pages; no new واعد announcements (190 listed). Cambridge's next-cycle dates aren't published yet. **Owner to-do:** SDAIA's status comes from an X post scripts can't read: check [@SDAIA_SA](https://x.com/SDAIA_SA) for a closing date (its site rejects scripts too). STC's واعد programs close 5 Nov.
- Every page exists at `/en/...` in English: interface, data, the 14 guide/grade/program pages, all 1,419 university notes. A toggle in the header switches between the same page in each language.
- Checked: 688 tests (22 new in `tests/test_english.py`: no Arabic on any English page, facts kept, minimum vs recommended, links stay in English); a meaning check of every Arabic/English pair plus a sampled read; the explorer's browser flows in both languages (30/30 each); every Arabic page unchanged against `main` (336 pages); layouts at 320, 360, 390 and 1280px in both themes.
- Fixed on the way: the theme toggle never loaded (a script clash from the English groundwork; Arabic pages too).
- **From now on, every Arabic change needs its English in the same commit** (CLAUDE.md, `/update-site`, `research-wave`).
- **Owner to-dos:** look at `/en` on a real phone (Safari); if you want, ask a native English reader to read the short list in the pull request; merge when happy. Decide whether to say "English" anywhere on the homepage or in the X bio.

## 2026-11-01

**2026-11-01 (decisions 064–065):**
- **Live (PR #25):**
  - SAR's railway training added to واعد. It isn't for high school graduates (engineering graduates 2024–2026); applications 1–10 Nov.
  - **`/update-site`** (skill) does the updating: it checks every program on its official page (الرواد, إمداد, واعد, the universities guide, Aramco, KGSP, SDAIA), adds what's new, clears what's past and fixes bugs.
  - A **morning check** (`.github/workflows/watch.yml`) is the alarm: one GitHub issue, «Site check», that pings only for something new and urgent. The dry run on GitHub passed (it read all 190 واعد programs).
- **On branch `claude/sharp-volta-tii6mj`, not merged yet:**
  - the first `/update-site` run (Aramco, KGSP and واعد re-checked: unchanged);
  - README «Keeping it current» and the tests badge;
  - the Git rule's cloud exception (decision 065).

**Owner to-dos:**
- Check X: [@SDAIA_SA](https://x.com/SDAIA_SA) (is the 4th cohort still open, any closing date?) and [@SA_Scholarships](https://x.com/SA_Scholarships) (does الرواد still close 15 Nov, has إمداد opened?). Then run `/update-site` with what you found.
- Install the GitHub app on your phone to get the morning check's pings.
- GitHub settings: a ruleset on `main` (require the `pytest` check, block force pushes) and "Automatically delete head branches". Decide on a licence.
- GitHub pauses scheduled workflows after 60 days with no commits; the next commit turns it back on.

## 2026-10-23

**Tests re-check (2026-10-23, `docs/research/rowwad-us-tests-recheck-brief.md`):** IELTS, Duolingo and SAT checked for the 30 الرواد + every US university; 3 new files (Pittsburgh, Colorado School of Mines, and Virginia with English and SAT only). The owner read Columbia, Oxford, UCL and UVA in a browser (their sites block scripts). Still open: Virginia's dates and platform (SAT optional, owner-confirmed); UChicago's undergraduate English page (JavaScript-only); UCL's SAT; Gallaudet's SAT.

## 2026-10-17

**Next session (as of 2026-10-17):** the «الطريق» redesign (decision 062) is merged (PR #19) and live on wadihguide.com; 616 tests and a live check of every page type passed. Audit, references and checks: `docs/research/design-direction-2026-10-17.md`.
- Act on forest, read on paper, in the logo's own colours; Naskh titles; the route of the grades; values under labels; a guides index and «الأدلة» in the nav; a footer with a self-updating copyright line. The logo is unchanged (a test checks).

**Owner to-dos:**
- Look at the live site on a real phone, Safari especially, in both themes. Not checked yet.
- Read the new copy: the route's lines and the guides' hints (`data/home.json`).
- GitHub: delete the six merged branches (`claude/brave-hopper-2a6fg7`, `claude/clever-bardeen-bei0zs`, `claude/funny-noether-nyj81u`, `claude/loving-hopper-sai8de`, `claude/wadih-design-overhaul-ahizpb`, `wadih-cleanup-requirements-guides`), and turn on Settings → General → "Automatically delete head branches" and Settings → Advanced Security → Dependabot security updates.
- Ask before installing: `httpx2` (the test client warns that `httpx` with it is deprecated).

**Small fixes (2026-10-17 repo check):** CI moved to `actions/checkout@v7` and `actions/setup-python@v7` (v4/v5 ran on the deprecated Node 20) with read-only permissions; Dependabot keeps the Actions versions current (monthly).

## 2026-10-16

Earlier (decision 061, merged in PR #18): text about the site removed; every English test shown at a glance; new guides (Duolingo, UK applications, essays); essays for 62 US universities and every UK one; EU wave 5 (50 of 57).
**Owner to-dos from it:**
- Check in a browser the sites that block scripts: Durham, Bournemouth, LBS, Griffith, Deakin, Macquarie, Alberta, Virginia, NUS (2027 dates), Michigan's essays and dates, Tilburg, Humboldt and Barcelona.
- Look up the Saudi certificate for German universities on anabin (a form query).
- Decide on Toulouse (which member institution the list means) and L'Institut Agro.

## 2026-10-13

Earlier (latest cloud session on branch `claude/wadih-design-overhaul-ahizpb`, decision 060, merged in PR #17):
**Design overhaul (decision 060):** one visual language, the sky (dawn in light mode, night in dark; the sun turns into a crescent when the theme switches); the theme follows the device until the student picks; the homepage title in Naskh, the grades as a constellation, a closing night band; `/universities?track=arruaad` opens with «خريطة الثلاثين» (30 stars in 8 country constellations; country chips filter the table). **Owner to-do:** look at it on a real phone (Safari especially) in both themes before merging; that hasn't been checked.

Earlier (branch `claude/brave-hopper-2a6fg7`, decisions 058–059, merged in PR #16):
**Requirements audit + explorer fixes (decision 058, `docs/research/requirements-audit-2026-10-13.md`):** all 129 files checked against their sources; English scores now separate «الحد الأدنى» from «الموصى به» (the Georgia Tech 6-vs-7 case: 7.0 is the graduate requirement); the filter-✕ bug (suggestions floating over the tags) fixed; إمداد asks for a field first; formal Arabic rule + test.
**Owner to-dos from it (browser, ~15 min):** confirm Oxford and UCL (hidden as drafts until then; exact pages in the audit), Michigan's deadlines and SAT policy, NYU's fee/dates, Saskatchewan's deadline. Then remove `"draft": true` or fix the values.
**Repo tidy (decision 059):** layout checked against the current Claude Code docs; `LEARNING_LOG.md` removed; every subagent forced onto Haiku; `scripts/check_sources.py` (facts vs their pages) and `scripts/check_explorer.mjs` (explorer JS in a browser) added.
**Ask before installing:** run `scripts/check_explorer.mjs` in CI (Playwright install); today it runs in cloud sessions only.

## 2026-10-12 and 13

Earlier (the audit session ran in the cloud on branch `claude/clever-bardeen-bei0zs`):
Live on `main` at **https://wadihguide.com** (decision 042; the old onrender address and www redirect with a 301): decisions 035–043, including the finder trust fixes (041), the footer feedback line (043), and the iPhone header fix (header icons only up to 479px).
Owner's laptop: `git checkout main` then `git pull`, and work on `main` or a new branch. The cloud branch `claude/loving-hopper-sai8de` is fully merged.

⏰ **When the next universities guide PDF is out (reminder):**
1. re-run `scripts/extract_universities.py`; the test `test_every_requirement_file_belongs_to_a_listed_university` flags universities that left the lists
2. add Arabic names for new universities (`university_names_ar.json`)
3. research **إمداد** requirements in waves, English-speaking countries first (US 53, UK 29, Australia 13, Canada 8, Singapore 2 in the current guide), with `source-researcher` agents on Haiku (`curl`), ~5 per batch
4. update the guide link and year everywhere it appears

**Next steps:**
0. **Product audit (decision 057, `docs/research/product-audit-2026-10-13.md`):** direction = a deep study-abroad core plus thin doors to official tools («لم تقرر بعد؟», «الدراسة في السعودية»). **Milestone L, items 1–2 done 2026-10-13 (not yet committed or deployed when this was written):**
   - false and stale counts on grades 11/12
   - «لمن» on open items
   - the explorer's focus bug after clearing filters
   - the timing note on program and university pages
   - foundation-year conditions on the 19 «لا تكفي» university pages

   **Still open, in order:**
   1. ~~the «لم تقرر بعد؟» guide~~ **done 2026-11-04 (decision 069)**; HRDF «سبل» left out (not read on an official page). «جرّب قبل أن تقرر» built as a draft: review + student test before publishing.
   2. the usability test (item 3 below), adding "can you apply to الرواد today?" and "Duolingo or IELTS?"
   3. then P1 from the audit: «الدراسة في السعودية», Duolingo `accepted` field + page, alternatives section, fee-waiver class split

   The remaining 143 logos are **deferred** (audit F).
1. **Testers:** share https://wadihguide.com; feedback comes through the footer's X link (decision 043). **Done 2026-10-12:** the service is on Render's $7/month compute plan (0.5 CPU, 512 MB), so it never sleeps. It is billed by the second; to stop, switch Compute back to Free.
   - **Launch ad «الشلة» (decision 044, guide in `marketing/README.md`):** the pipeline and the real site footage are done.
   - **Paused (2026-10-12): no budget for paid tools yet.** Missing: the 4 AI clips (the Higgsfield free plan has no credits or commercial use; Starter $19, or the Veo API ~$5) and the voices (the ElevenLabs free plan has no commercial licence; Starter $6).
   - A $0 route exists if wanted: the owner's own phone shots + the owner's own voice, or caption cards instead of AI shots.
   - Then rebuild, review, and post organically with `?src=` links.
2. **Stale-facts check: done 2026-10-13 (decision 053).** `scripts/stale_facts.py` lists all 132 checked items by date; not a CI test, so it can't block a deploy. **Before Launch 1:** run it with `--as-of 2026-12-09 --days 45`, re-check from the top, update dates, repeat until empty. Its 90-day list is now part of `/update-site` (decision 064).
3. **Usability test with 3–5 students** (questions in the grade-pages, timeline and audit research notes), then act on feedback before the full launch (~one month).
4. **Aramco:** re-checked 2026-10-12 with WebFetch, unchanged (still the 2025–2026 cycle, registration closed). `curl` to aramco.com times out even from the laptop. Watch for the 2026–2027 cycle; the owner may spot-check the numbers in a browser.
5. **RAG learning path (decision 045, `docs/specs/search.md`):** step 1 done 2026-10-12, keyword search at `/search` and `/api/search`, linked under the homepage search and on the 404 page (decision 046). **KGSP** now has its own page and «يفتح قريبًا» (decision 046): watch the Prospective Students page for Cohort 19 dates, and review its 8 facts (`owner_reviewed`). **Also 2026-10-12 (decision 047):** test pages for SAT, TOEFL, القدرات/التحصيلي; 3 more scholarship FAQ answers; Aramco re-checked. **Filters fixed (decision 048); logos + flags on university pages (decision 049): 147/290 logos done, next the other 143 from the universities' own sites (Haiku agents, batches, reviewed on a contact sheet).** **إمداد wave 1 done (2026-10-12): 35 US universities researched (65 detail files).** Next: waves 2–3, the other English-speaking universities (UK 29, Australia 13, Canada 8, Singapore 2). **UK wave 2 done 2026-10-13 (decision 054):** 26 UK universities, with a new «الشهادة الثانوية السعودية» row; Durham, Bournemouth (403) and LBS left out. Remaining (counted 2026-10-13): **wave 3 done 2026-10-13** (decision 055: 16 of 23 saved; Melbourne, Griffith, Monash, Deakin, Macquarie, Alberta and SMU block automated reads, so check them by hand in a browser or leave them); **wave 4 done 2026-10-13** (decision 056: 22 of 25 saved). The English-speaking countries are done (129 universities with requirements). **Check by hand in a browser (sites block automated reads):** Durham, Bournemouth, Melbourne, Griffith, Monash, Deakin, Macquarie, Alberta, SMU, Virginia, Pittsburgh, Colorado School of Mines, plus Oxford and UCL (filled from snippets). The 111 in non-English-speaking countries (China 40, Germany 17, Italy 10, Netherlands 10, Korea 9, France 9, Spain 6, Switzerland 5, Japan 5) need a different brief (language of instruction, the conditional-admission exception) and a scope decision against Launch 1. **Re-check Oxford and UCL** (`fact-checker`): their الرواد files were filled from search snippets after 403s. **US applications (decision 050):** guide at `/resources/us-applications`, fee + waiver on 50 US university pages. **Cleanup iteration 1 (decision 051).** **Known small issue (decision 052):** on the owner's phone, Back to a list can still move slightly before settling. Low priority; to look at, note the phone, browser and how Back was done (swipe, button, link). **Owner to-do:** copy القدرات/التحصيلي details (duration, scale, fee, attempts) from etec.gov.sa in a browser, and the Saudi TOEFL price from the ETS fee page. Next: step 2 (chunks with `last_checked`/`owner_reviewed`), then search by meaning (embeddings, ask before installing), then an eval set. The chatbot (paid API) comes after; ask first.
6. **Optional:** page-view counts without trackers (a small counter of our own); for now, Render's Metrics tab.

Resolved 2026-10-12: «ثلاث قبولات كحد أقصى» (on the site); the age rule contradicts itself on the conditions page (not published).

## 2026-10-11

Also done 2026-10-11:
- official X accounts as sources (@SA_Scholarships, @SDAIA_SA)
- SDAIA open (cohort 4) with a 'not standalone' warning; next deadline per university (decision 031)
- SDAIA's full list of 95 universities from its PDF (decision 032)
- news as a status board + /news page; SDAIA logo (decision 033)
- explorer majors by field, own suggestions panel, واعد in «المسار» (decision 034)
Owner to-dos still open: review the fact-check tables (§5 of each research file), send a post that states الرواد's 15 Nov end date and one for إمداد closing, review the 15 least-certain Arabic university names (`docs/research/arabic-names-to-check.md`), optionally export the Telegram group (JSON) for the FAQ step.
