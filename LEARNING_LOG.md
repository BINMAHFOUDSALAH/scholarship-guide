# Learning Log

What we built in واضح, why, how it works, and how to talk about it. Updated after each meaningful feature.

**Honesty rules for this log**
- It records what was actually built and tested, nothing more.
- **"Who did what"** separates the owner's work (decisions, verification, research, design direction, testing by hand) from what Claude implemented.
- **"Understood?"** stays *not yet checked* until the owner has answered a check question or done an exercise on it. Being explained to doesn't count.

**The overall interview story (true today):** "I'm building and running a live, Arabic-first guidance site for Saudi high school students. I set the product rules (verified facts only, no invented data, privacy for minors), made the design and architecture decisions with an AI pair programmer, verified the official information myself, and shipped it with automated tests and CI. AI wrote most of the code; my job was product direction, decisions, verification, and making sure it's correct."

---

## 1. First web app: FastAPI + virtual environment
**Built / why:** A Python web server (FastAPI) with routes (`/`, `/about`), in an isolated environment (`.venv`) with pinned packages (`requirements.txt`). It's the base everything else (APIs, AI) will sit on.
**Key concepts:**
- request → route → function → response
- status codes (200, 404)
- a virtual environment = a private package box per project
- pinned versions = the same behavior everywhere
**Decisions:** FastAPI over Django or a static site generator, because one language (Python) also serves the future AI work.
**Tested:** opened the routes locally; later covered by automated tests.
**Limits:** a server only you can see (127.0.0.1) until it's deployed.
**Interview pitch:** "A FastAPI app with server-rendered pages; I chose it because the AI features later need a Python backend anyway."
**Who did what:** Owner chose the stack direction (Python/FastAPI) and approved installs. Claude wrote the code.
**Understood?** Not yet checked.

## 2. Templates, RTL, and the design system
**Built / why:** Jinja2 templates (`base.html` + pages), an Arabic right-to-left layout, design tokens (colors and sizes as CSS variables), a light/dark theme, and self-hosted Arabic fonts.
**Key concepts:**
- template inheritance (one layout, many pages)
- `dir="rtl"`
- CSS logical properties (`padding-inline`)
- design tokens
- contrast ratio (WCAG: at least 4.5:1)
- progressive enhancement (the site works without JavaScript)
**Decisions:**
- server-rendered HTML instead of React
- self-hosted fonts instead of Google Fonts (privacy)
- light mode first (owner's choice)
- Plex Bold headlines with Naskh accents
**Tested:** measured contrast with code in the browser; checked layouts at 320, 375, 768, 1280, and 1440px in both themes.
**Limits:** `color-mix()` and `text-wrap: balance` need modern browsers; older ones fall back to plainer looks.
**Interview pitch:** "An accessible RTL design system: tokens, a separately designed dark mode, contrast measured rather than eyeballed."
**Who did what:** Owner set the brand (name واضح, palette, Tuwaiq logo concept, light-first), wrote the redesign brief, and **found a real layout bug on tablet by testing**. Claude implemented and measured.
**Understood?** Not yet checked.

## 3. Content separate from code + trust rules as code
**Built / why:** Facts live in `data/*.json`, page text in `content/*.md`, and templates only display them. Every fact has a source and a check date. Unverified items show "غير مؤكد" or stay hidden (`status: draft`, `WADIH_SHOW_DRAFTS`).
**Key concepts:**
- separation of concerns
- a single source of truth
- feature flags through environment variables
- data validation
**Decisions:**
- JSON + Markdown files in git instead of a database for now (one editor, free history)
- research → owner verifies → publish (decision 013)
**Tested:** tests that fail if, for example, a path is marked verified without sources (I broke this on purpose once to prove the test catches it).
**Limits:** data changes need a server restart; there's no formal schema (Pydantic) yet (planned for Stage 2).
**Interview pitch:** "I encoded the product's trust rules as automated tests, so the site can't claim something is verified without a source."
**Who did what:** Owner defined the trust rules (never invent facts, "غير مؤكد"), **verified official facts from primary sources** (application platform قبول, the current universities list, track statuses from the program's official account), and made the policy calls. Claude researched drafts and wrote the code and tests.
**Understood?** Not yet checked.

## 4. Markdown pages and URL safety
**Built / why:** Grade pages ("what to do this year") written in Markdown with frontmatter, served at `/grades/{slug}`, with a friendly Arabic 404 page.
**Key concepts:**
- path parameters
- frontmatter
- **never trust URL input to build file paths** (the slug must match `^[a-z0-9-]+$`, which blocks `../../.env`)
**Decisions:** pages are read on every request (no restart needed for edits), which is fine at this size.
**Tested:** tests for valid pages, unknown pages, and attack-style slugs (`..%2F..%2F.env` → 404).
**Limits:** the grade pages are drafts written by Claude, still awaiting the owner's review.
**Interview pitch:** "User input is validated before it touches the file system; I have a test for a path-traversal attempt."
**Who did what:** Owner asked for grade-based guidance and the hidden "ابدأ من هنا" (start here) reveal. Claude implemented and tested.
**Understood?** Not yet checked.

## 5. Automated tests (51)
**Built / why:** `pytest` tests for pages, data rules, content loading, links, SEO tags, and privacy (no third-party requests). They let us change things without fear.
**Key concepts:**
- unit vs page tests
- `TestClient`
- `monkeypatch`
- "a test must be able to fail" (prove it by breaking the code on purpose)
- tests can be wrong too
**Decisions:** test the promises (trust, privacy, working links), not just "does it load".
**Tested:** the suite itself, run before every commit. One test was wrong once (it flagged our own URLs as third-party), and we fixed the test, not the site.
**Limits:** tests don't cover how the page looks; that's checked by hand in the browser.
**Interview pitch:** "51 tests that encode the product's promises, run automatically in CI before every deploy."
**Who did what:** Owner approved the test tooling. Claude wrote the tests.
**Understood?** Not yet checked.

## 6. Deployment (Render)
**Built / why:** The site is live at https://wadih-mqni.onrender.com. Render builds from GitHub and runs `uvicorn ... --host 0.0.0.0 --port $PORT`.
**Key concepts:**
- hosting
- build vs start commands
- `0.0.0.0` vs `127.0.0.1`
- `$PORT`
- continuous deployment (push = deploy)
- regions (close to the users, not the developer)
**Decisions:**
- the free tier (it sleeps when idle)
- the Frankfurt region (closest to Saudi users)
- a custom domain later (`base_url` is one setting)
**Tested:** checked every page and file on the live site after each deploy.
**Limits:** the slow first visit after the site sleeps; the server's Python version (3.14) differs from local (3.13) and isn't pinned yet.
**Interview pitch:** "Deployed on Render with continuous deployment from GitHub, gated by CI."
**Who did what:** Owner **created the Render account, configured and launched the service** (and switched off the paid plan that Render pre-selected). Claude gave the settings and verified the live site.
**Understood?** Not yet checked.

## 7. Search engines and share previews
**Built / why:** Meta descriptions, canonical URLs, Open Graph tags plus a 1200×630 share image (for WhatsApp/X), `robots.txt`, and `sitemap.xml`.
**Key concepts:**
- how Google discovers pages
- Open Graph
- why pages behind a login can't be indexed
**Decisions:** the share image was drawn in the browser, so Arabic letters join correctly.
**Tested:** tests for the tags, robots, and sitemap; checked the live URLs.
**Limits:** WhatsApp caches old previews for a while.
**Interview pitch:** "SEO and sharing basics, with one setting to change when the domain arrives."
**Who did what:** Owner chose these from a list of options. Claude implemented.
**Understood?** Not yet checked.

## 8. Homepage redesign with real, licensed photos
**Built / why:** A wide editorial layout:
- a hero with the Tuwaiq route drawing
- "where do I start" starting points
- compact news (sorted by date, then status)
- facts-first path rows with «لمن؟» (who it's for)
- a 5-step journey
- licensed photos with credits
- a click-to-play video (privacy: YouTube loads only after a click)
**Key concepts:**
- image licences (public domain, CC BY, CC BY-SA)
- responsive images (`srcset`)
- the "facade" pattern for embeds
- why not to use logos (trademarks; the state emblem)
**Decisions:**
- photos of places, not logos
- no search box until there's something to search
- the honest headline
**Tested:**
- pytest, including a test that opens every link on the homepage
- browser checks at 1440×900 and 390×844 in both themes
- contrast measured (lowest 5.4:1)
**Limits:** the Tuwaiq section stays hidden until the owner confirms the video's wording.
**Interview pitch:** "I redesigned for clarity: facts first, real sources, accessible contrast, and privacy-preserving embeds."
**Who did what:** Owner drove the design direction (briefs, feedback, which program images to use, the video request) and **found the College Preparatory Center photo**. Claude checked licences, implemented, and verified.
**Understood?** Not yet checked.

## 9. CI gate and `.env` lock (2026-10-10)
**Built / why:** GitHub Actions runs the tests on every push (`.github/workflows/tests.yml`); Render deploys only after they pass. A permission rule blocks Claude from reading `.env` (where future API keys will live).
**Key concepts:**
- CI (continuous integration)
- a "gate" before deployment
- advice (CLAUDE.md) vs enforcement (permission rules, hooks)
- least privilege
**Decisions:** chose CI and the `.env` lock first; deferred the stale-facts test and the weekly link checker.
**Tested:** pytest locally. **The CI run is proven only after the first push**; the `.env` rule was intentionally not tested by trying to read `.env`.
**Limits:** the `.env` rule blocks Claude's file tools and commands like `cat`, but not a script that opens files itself (full protection would need Claude Code's sandbox).
**Interview pitch:** "Broken code can't reach production: CI must pass before Render deploys. Secrets are protected from the AI assistant by an enforced rule, not just an instruction."
**Who did what:** Owner chose which automations to adopt after asking for plain explanations and the trade-offs. Claude implemented.
**Understood?** Not yet checked.

## 10. Fact-checking, one fact shape, and the first program page (2026-10-11)
**Built / why:**
- a claim-by-claim fact-check of the government scholarship from official Ministry pages (`docs/research/custodian-scholarship-2026-27.md`)
- one data shape for every fact (text, sources, check date, status) rendered by one macro, so every fact looks and behaves the same
- `/programs/custodian-scholarship`: the 4 tracks in a comparison table, sourced facts, and the conditional-admission explainer
- fixed a real error: the site said "unconditional offer" with no mention of the official language-study exception
**Key concepts:**
- a data model as a contract (the same fields everywhere → reusable templates and tests)
- the difference between "we found an official source" and "the owner reviewed it"
- recording conflicting official sources instead of picking one
- accessible tables (`<th scope>`, caption) that stack on phones
**Decisions:** 025 (verification display), 026 (official logo pending), 027 («البرامج» + program pages).
**Tested:** 64 pytest tests (new: fact rules, program page, 404s, links on the new page). Browser checks at 1280px and 375px, light and dark, no horizontal scroll, no console errors. Not tested: real students using the page.
**Limits:**
- the universities PDF wasn't read (needs Stage 2's extraction)
- the track statuses (open/closed) still lack their X post links
- «آخر مراجعة» is a manual date, not monitoring
**Interview pitch:** "I found that my own site overstated a rule. I traced every claim to an official page, modeled facts with sources and statuses, and made the UI show uncertainty only where it actually exists."
**Who did what:** Owner wrote the audit brief, chose the verification display, the naming, and the order of work, and suggested mining real student questions for an FAQ. Claude researched the official pages, wrote the fact-check, and implemented and tested.
**Understood?** Not yet checked.


## 11. Programs-first homepage, official logo, IELTS page, explorer spec (2026-10-11)
**Built / why:**
- The homepage now leads with the programs, with the grade buttons visible in a shorter hero.
- «غير مؤكد» stamps and on-screen dates were removed: unconfirmed things are hidden instead.
- The King scholarship shows its official logo, cropped cleanly from the program's own site.
- A first shared resource page: `/resources/ielts`.
- A spec for the universities explorer, based on what the official PDF actually contains.
**Key concepts:**
- "hide vs. label" as two ways to handle uncertainty
- image licences (why CC BY-SA credit can move but not disappear)
- inspecting a data source before designing the feature (the PDF has English names and flags, but no Arabic names or degrees)
- running independent research in parallel with subagents
**Decisions:** 028.
**Tested:** 77 pytest tests (no stamps or review dates on any page, programs before news, IELTS page, logo files and source). Browser checks at 1440px and 375px, light and dark.
**Limits:**
- the logo includes the state emblem (the owner's informed choice)
- the explorer isn't built yet
- the KGSP/Aramco research isn't on the site yet
**Who did what:** Owner reviewed the live page and set the direction (programs first, no stamps or dates, the official logo, the video, the King-scholarship focus, using subagents). Claude researched, implemented, and tested; two research agents wrote the KGSP and Aramco notes.
**Understood?** Not yet checked.

## 12. Universities explorer, live statuses, SDAIA (2026-10-11)
**Built / why:**
- `scripts/extract_universities.py` turns the Ministry's 75-page PDF into data: 290 universities, every track and field list, the majors, the guide's notes, and countries from the flag images.
- `/universities`: search by university or by major, in Arabic or English, with filters; a page per university with its ranks, its majors, and requirements from its own site.
- Statuses now follow data and dates: الرواد closes itself after 15 Nov 2026, and واعد shows its latest programs in a toggle.
- SDAIA's AI scholarship has its own page, linked to its 28 target universities.
**Key concepts:**
- extracting structured data from a PDF by position (pdfplumber), and refusing to write when checks fail
- right-to-left text extraction: reverse the glyphs, not the letters
- recording a source's own errors instead of silently fixing them
- server-side search with progressive enhancement (works without JavaScript)
- computing a status from today's date instead of editing it by hand
- delegating research to cheaper parallel agents and validating their output
**Decisions:** 029–032 (later the same day: official X posts as sources, SDAIA's full list of 95 universities from its PDF, the «برامج إضافية» filter, the next deadline per university).
**Tested:** 171 pytest tests by the end of the day (133 when this entry was first written) (lists, notes, Arabic names, requirement-file schema, search modes, pages, API, deadlines, the واعد toggle, SDAIA); browser checks on desktop and phone.
**Limits:**
- the Arabic university names are our translation
- some requirement values need a hand check: Michigan and Columbia pages blocked the agent, and some years are inferred
- the explorer covers the 2026–2027 guide only
**Who did what:** Owner chose the features (an advanced search, Arabic + English names, the doctorate lists, the requirements per university, the Waaid toggle, SDAIA) and the cheaper agents, and supplied the الرواد deadline and the Waaid and SDAIA news. Claude built the extraction, explorer, and pages; research agents gathered the requirements and Arabic names.
**Understood?** Not yet checked.

## 13. UX redesign: one design system, a clearer explorer, «قائمتي» (2026-10-11)
**Built / why:**
- **One design system:** colour tokens with fixed meanings (lime = open now / next step only), one type scale, shared components (buttons, status tags, notices, summary list, back link), and a test that checks the contrast of every colour pair.
- **Homepage:** your grade is the main way in; searching the official lists is the second; then what's open now; then compact program rows.
- **Explorer:**
  - Applied filters as removable tags + «مسح الكل».
  - Clear labels («الترتيب» isn't a world ranking; «أقرب موعد تقديم في الجامعة» is the university's date).
  - Choosing a university opens its page.
  - «الرجوع إلى نتائج البحث» comes back to the same list and scroll position.
  - Filters fold on phones.
  - An error state.
- **University page:** «باختصار» first, and a notice that being on a list isn't admission.
- **«قائمتي»:** save universities on this device (localStorage), see them on /my-list, remove them.
- **Bugs found by testing in a real browser:**
  - Arabic typing never filtered the suggestions.
  - Three pages scrolled sideways at 320px.
  - The suggestions list was a Tab stop.

**Key concepts:**
- **Design tokens and components:** decide once (colour meanings, sizes, a button), reuse everywhere, test the rules.
- **Visual hierarchy:** one main action and one second action, instead of giving everything the same weight (NN/g).
- **Applied filters:** show what's active and make each part removable (Baymard, the UK MOJ pattern).
- **Progressive enhancement:** filter tags are plain links the server draws; JavaScript only makes them instant.
- **Accessibility:**
  - status messages (`role="status"`) instead of a live region around a whole table
  - visible focus
  - reflow at 320px
  - targets of at least 24px
  - `aria-current`
  - a skip link
- **Security in small things:** the "back to results" link rebuilds the address from a whitelist, so a crafted link can't send students elsewhere.
- **Unicode:** invisible combining marks can be reordered by tools. Write them as `\u` escapes in code.
- **Honest persistence:** localStorage is real but device-only, and the page says exactly that.

**Decisions:** 035.

**Tested:**
- 216 pytest tests. New ones cover the nav marker, skip link, footer, applied-filter links, the `from` whitelist, Arabic counting, the university summary, «قائمتي» rows, program/grade pages, contrast, and the type floor.
- Playwright scripts:
  - Typing and keyboard-choosing suggestions.
  - Filters, tag removal, «مسح الكل».
  - The phone filter toggle.
  - A failed request + retry.
  - Back to results with the same scroll.
  - Save/remove/empty state/corrupted storage.
  - No-JavaScript mode.
- axe-core on 14 routes × 320/1280px × light/dark: no violations.
- Before/after screenshots at 360/768/1280px.
- **Not tested:** real students; a screen reader on a real phone; Safari/Firefox.

**Limits:**
- The research came from search summaries (the articles themselves couldn't be opened from the work environment).
- «قائمتي» doesn't follow the student to another device until accounts exist.
- The homepage on a phone is still long (~6,400px), mostly the program rows.

**Interview pitch:** "I audited my own product as a first-time student on a phone, then redesigned it around one design system and two clear ways in. Testing in a real browser exposed a bug no unit test caught: an invisible Unicode mistake made Arabic search suggestions useless. I fixed it and locked it with a regression test."

**Who did what:**
- **Owner:** asked for a research-backed, honest redesign; chose device-only saving, replacing the hero drawing with search, the test tooling, and commit/push per step.
- **Claude:** audited, researched, implemented, and tested.

**Understood?** Not yet checked.

## 14. Grade pages that answer real questions; the finder at a glance (2026-10-12)
**Built / why:**
- **Grade pages, one structure:** this week's single action → what matters → 3–4 priorities → a tool → ≤ 4 resources → one next step on واضح → official sources. Each grade has its own job: discover (10), research and prepare (11), apply and track (12).
- **Facts, not general advice:** every claim links to an official page read directly:
  - the Ministry's tracks page and 2025 document
  - the vocational guidance manual
  - the unified admission page
  - the scholarship conditions
  - KGSP
  - Aramco (previous cycle)
  - Our own advice is labelled «نصيحتنا».
- **«الاختبارات: من يطلب ماذا؟»:** one row per destination. The الرواد row is *computed* from the 30 requirement files, so it updates itself when the data changes.
- **Finder:**
  - Each row shows SAT/ACT · IELTS · the next university date · the official admissions page, or says «لم نجمعها بعد».
  - The language filter now says it's the country's language, not the language of teaching.
  - The university page keeps the scholarship's deadline apart from the university's.
- **Data cleanup:** 75 free-text dates became structured fields (what, which round, which intake, is the year on the page?). Notes to ourselves no longer leak onto the site.

**Key concepts:**
- **Computed vs. typed facts:** a number typed into a page («9 universities require SAT») goes stale silently; one counted from the data can't drift.
- **Structured data beats labels:** once a date has `year_stated: false`, the site can warn about it everywhere, consistently.
- **Bidirectional text:** brackets around English inside Arabic flip visually. A separator («·») plus `<bdi>` avoids it.
- **Scope discipline:** a stateful application tracker was tempting, but there's no evidence students want it. Ask them first (usability test).

**Decisions:** 038.

**Tested:**
- 233 pytest tests. New ones cover:
  - the grade structure and order, and every external link on a grade page being a declared source or resource
  - the sourced test table and the computed SAT counts
  - the next deadlines on grade 12
  - the scholarship and university dates apart
  - the structured date schema
  - the track order, the language hint, and key facts in results and «قائمتي»
- Playwright: the explorer flow (33 checks) and «قائمتي» flow (23 checks) still pass.
- axe-core: 13 routes × 320/1280px × light/dark, no violations, no sideways scroll.
- Every new source link loads, except aramco.com, which times out from the cloud environment.
- **Not tested:** real students; Safari/Firefox; a screen reader.

**Limits:**
- ETEC's site blocks automated reading (Cloudflare), so the site only links to it and says nothing about what Qudurat or Tahsili contain.
- The إمداد universities have no requirements yet.

**Who did what:**
- **Owner:** asked for a product-focused iteration on the finder and grade pages, and opened network access for official sources.
- **Claude:** read the sources, audited the old claims, built and tested.

**Understood?** Not yet checked.

## 15. «قائمتي» you can find, a timeline to university, and a product audit (2026-10-12)
**Built / why:**
- **«قائمتي»:** it worked, but nobody could find it. Now there's «احفظ» on every result row and an always-visible link. If the browser blocks storage, the page says so instead of staying blank.
- **«من أول ثانوي إلى الجامعة»:** one timeline on all three grade pages, with your grade open and marked «أنت هنا».
  - Official US dates: applications open 1 August, early results mid-December, regular results in March, reply by 1 May.
  - Counted patterns from our data.
  - A separate block explaining that the scholarship window changes every year (Dec 2022–May 2023 vs. Aug–Nov 2026) and needs an unconditional offer.
- **Product audit:** ranked findings in `docs/research/product-audit-2026-10.md`. The best next task is a stale-facts check.
- **إمداد:** postponed until the new guide, with a reminder checklist in the roadmap and a test that catches universities that leave the lists.

**Key concepts:**
- **Discoverability:** a feature nobody can find doesn't exist for users. Hidden-until-used UI hides the feature itself.
- **Event delegation:** one click listener on the document handles buttons that don't exist yet (rows from live updates).
- **Graceful failure:** when storage is blocked, show nothing that pretends to work, and explain.
- **"Pattern" vs "official" dates:** label each; never turn a pattern into a promise.
- **Agents as researchers, main session as editor:** an agent reported Stanford "early April". It wasn't on the page I read, so it wasn't used.

**Decisions:** 039 (and 037 amended).

**Tested:**
- 243 pytest tests.
- «قائمتي» browser flow: 36 checks, including saving from results, refresh, sync with the university page, blocked storage, and no JavaScript.
- The explorer flow.
- axe-core, overflow at 320px, and the source links (see the final report).

**Not tested:** Safari/iPhone; real students.

**Understood?** Not yet checked.

## 16. Grade pages, take two: less, but each grade its own (2026-10-12)
**Built / why:** the owner said the shared timeline wasn't clear. Measured against NN/g (main point first, chunking, progressive disclosure), the pages had ~10 sections, repeated each other, and grade 12 was 12.6 phone screens long.

**Now every grade page has:**
- three points
- one activity
- its own tool:
  - grade 10: the five tracks
  - grade 11: which tests
  - grade 12: the year month by month, with «الآن» set from today's date
- a few resources

The whole journey is the grade bar at the top. Pages are about half as long.

**Key concepts:**
- **Duplication is a design smell:** the same section on three pages means none of them is "its own".
- **Measure before and after:** page height on a phone is a cheap proxy for effort.
- **Show "now" from data:** the current month's row is computed, not written.

**Decision:** 040. **Tested:** 241 pytest tests; axe-core and 320px overflow on the grade, program and university pages; screenshots at 360/1280px in light and dark. **Not tested:** students; Safari.

**Understood?** Not yet checked.

## 17. Final design pass: trust before looks (2026-10-12)
**Built / why:**
- The audit found the design itself sound: tested colours, one type scale, clear components. So it was **kept**.
- The real problems were **false "none" answers** in the finder:
  - Germany showed 0 universities.
  - Stanford was "not found" under a filter.
  - A typed country found nothing.
- Also: overstatements («متاحة لتخصصك»), a 22,000px phone page for a major search, repeated «لم نجمعها بعد», and unclear labels.
- All fixed, with regression tests.

**Key concepts:**
- **The worst search error is a false "no results":** the student concludes something doesn't exist.
- **Don't redesign what works:** the evidence decides what changes, not the wish for something new.
- **Independent review catches what the author misses:** a Haiku agent found the Germany bug by walking real student tasks; I verified it before fixing.
- **Say unknowns once,** not on every row.

**Decision:** 041. **Tested:** 247 pytest tests; the explorer and «قائمتي» browser flows; axe-core and 320px overflow on 8 routes × 2 sizes × 2 themes. **Not tested:** Safari, students, a screen reader.

**Understood?** Not yet checked.

## 18. A real domain: wadihguide.com (2026-10-12)
**Built / why:** a real address before sharing with testers, so their links keep working after launch.
- **DNS** maps the name to Render: CNAME records at Cloudflare, "DNS only".
- **HTTPS:** Render issues the certificate itself.
- **The code:** `base_url` changed, and a 301 redirect sends the old onrender address and www to the new domain.

**Key concepts:**
- **DNS:** the internet's phone book, name → server.
- **CNAME:** this name is an alias of that one.
- **301:** "moved permanently", so browsers and Google update the link.
- **Order matters:** turn on the redirect only after the new address works.

**Tested:** 249 pytest tests, including the redirect. The live checks wait for DNS verification.

**Understood?** Not yet checked.
