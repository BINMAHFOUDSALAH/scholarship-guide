# Roadmap

Where واضح stands and what comes next. Why each choice was made: [decisions.md](decisions.md). What each session did: [log.md](log.md).

Keep this page short: update the sections below in place, tick the stages, and put the dated story in the log.

## Where we are

- **Live:** https://wadihguide.com (Arabic) and https://wadihguide.com/en/ (English).
- **Launch 1 (~2026-12-09):** public guides + the government scholarship path, fully verified. No accounts.
- **Launch 2 (after Stage 4):** accounts + guided start + personal plan (decision 014).
- **Pace:** ~5 hours per week.
- **Just merged:** the colour pass, a tone for each field (decision 075, PR #38), after «جرّب قبل أن تقرر»'s redesigned result (073, PR #35).
- **Next session:** the owner's iPhone check of that journey and the new colours, then next step 1.

## Next steps

In order (direction: a deep study-abroad core plus thin doors to official tools, decision 057).

1. **Usability test with 3–5 students.** Write the script (`docs/research/usability-test.md`, Stage 1e step 5) from the questions in the grade-pages, timeline and audit notes. Add "can you apply to الرواد today?" and "Duolingo or IELTS?". For «جرّب قبل أن تقرر»: can they name a field to explore and one action; does anyone read it as "the site told me what to study"? ([research note](research/career-exploration-evaluation-2026-11.md) §9). Act on the feedback before the full launch.
2. **Stale facts, before Launch 1.** Run `python scripts/stale_facts.py --as-of 2026-12-09 --days 45`, re-check from the top, update the dates, repeat until empty.
3. **P1 from the [product audit](research/product-audit-2026-10-13.md):** «الدراسة في السعودية», the alternatives section, the fee-waiver class split.
4. **Accessibility:** a screen-reader run on a real phone and the broken-link check (Stage 1e step 6).
5. **Search, the road to RAG ([spec](specs/search.md), decision 045):** keyword search is done. Next: chunks with `last_checked` / `owner_reviewed`, then search by meaning (embeddings; ask before installing), then an eval set. The chatbot (paid API) comes after; ask first.
6. **إمداد requirements, the rest:** China 40, Korea 9, Japan 5 (counted 2026-10-13). They need their own brief (language of instruction, the conditional-admission exception) and a scope decision against Launch 1.

**Later or optional:**
- FAQ from real student questions (Stage 1e step 4).
- Page-view counts without trackers (for now, Render's Metrics tab).
- The remaining 143 university logos (deferred, audit F).
- The launch ad: paused, no budget for paid tools yet; a $0 route exists ([marketing/README.md](../marketing/README.md)).

## Owner to-dos

Gathered from the session notes in [log.md](log.md). The ones that could be checked in the repo or on GitHub on 2026-11-04 are accurate; the rest may already be done, so tick or delete them.

### On a real phone (Safari especially)
- [ ] The whole «جرّب قبل أن تقرر» journey on an iPhone, Arabic and English (checked on emulated iPhones only); read the 10 titles and the why sentences (decision 073).
- [ ] The live site in both themes, and `/en` (decisions 062, 066).
- [ ] Back to a list can still move slightly before settling (decision 052, low priority): note the phone, the browser and how Back was done.

### With other people
- [ ] Share https://wadihguide.com with testers; feedback comes through the footer's X link (decision 043).
- [ ] One Saudi school counsellor (and, if possible, a career-development specialist) reviews the 30 activities, the subject map and the wording; then set `expert_reviewed: true` in `data/exploration.json`.
- [ ] Optional: a native English reader for the short list in pull request 27.
- [ ] Optional: export the Telegram group (JSON) for the FAQ step.

### Official sources that scripts can't read
- [ ] X: [@SDAIA_SA](https://x.com/SDAIA_SA) (is the 4th cohort still open, any closing date?) and [@SA_Scholarships](https://x.com/SA_Scholarships) (does الرواد still close 15 Nov, has إمداد opened?). Then run `/update-site` with what you found.
- [ ] Links to X posts that state الرواد's end date and إمداد's closing → `source_url` in `data/news.json`, `status_source` in `data/paths.json`.
- [ ] The Ministry's grade 10 interest measure on an official page (press says it counts in placement; not published).
- [ ] In a browser, sites that block scripts:
  - to read: Durham, Bournemouth, LBS, Griffith, Deakin, Macquarie, Alberta, SMU, Tilburg, Humboldt, Barcelona;
  - to confirm: Virginia (dates, platform), NUS (2027 dates), Michigan (essays, dates, SAT policy), NYU (fee, dates), Saskatchewan (deadline), UChicago (undergraduate English page), UCL (SAT), Gallaudet (SAT).
- [ ] The Saudi certificate for German universities on anabin (a form query).
- [ ] القدرات/التحصيلي details (duration, scale, fee, attempts) from etec.gov.sa, and the Saudi TOEFL price from the ETS fee page.
- [ ] Optional: spot-check Aramco's numbers in a browser (`curl` to aramco.com times out).

### Review and decide
- [ ] The fact-check tables (§5 of each research file), including KGSP's 8 facts (`owner_reviewed`).
- [ ] The checklist at the bottom of [paths-research.md](research/paths-research.md).
- [ ] The 15 least-certain Arabic university names ([arabic-names-to-check.md](research/arabic-names-to-check.md)).
- [ ] The copy: the route's lines and the guides' hints (`data/home.json`).
- [ ] Toulouse (which member institution the list means) and L'Institut Agro.
- [ ] Whether to say "English" anywhere on the homepage or in the X bio.

### GitHub
- [ ] Install the GitHub app on your phone to get the morning check's pings.
- [ ] Optional, off as of 2026-11-04: a ruleset on `main` (require the `pytest` check, block force pushes; changes then reach `main` only through pull requests), Dependabot security updates, private vulnerability reporting (decision 074).
- GitHub pauses scheduled workflows after 60 days with no commits; the next commit turns it back on.

## Waiting on something

- **The next universities guide PDF** (expected Dec 2026 / Jan 2027):
  1. re-run `scripts/extract_universities.py`; the test `test_every_requirement_file_belongs_to_a_listed_university` flags universities that left the lists;
  2. add Arabic names for new universities (`university_names_ar.json`);
  3. research what's missing in waves (`research-wave` skill);
  4. update the guide link and year everywhere it appears.
- **New rounds on official pages:** KGSP Cohort 19's dates, Aramco's next cycle, Cambridge's next-cycle dates. `/update-site` checks them.
- **Ask before installing:** `httpx2` (the test client warns that `httpx` with it is deprecated); Playwright in CI for `scripts/check_explorer.mjs`.

## Stages

| Stage | Goal | Status |
|---|---|---|
| 1, 1b–1e | Live skeleton, design, tooling, accuracy | Live; 1e steps 4–6 open |
| 2 | Universities explorer + content model | Shipped; إمداد requirements, Pydantic models and shared resources open |
| 3 | The scholarship path + polish → **Launch 1** | In progress |
| 4 | Accounts, email alerts, guided start → **Launch 2** | Not started |
| 5–9 | Operations, more programs, search + RAG, chatbot, agents | Keyword search started early (decision 045) |

### Stage 1: Live walking skeleton
Teaches HTTP, routing, templates, virtual environments, testing, and deployment.

- [x] **Step 1:** Housekeeping + `docs/decisions.md`
- [x] **Step 2:** `.venv` + FastAPI, Uvicorn, Jinja2 in `requirements.txt`
- [x] **Step 3:** First FastAPI routes (`/`, `/about`)
- [x] **Step 4:** RTL base template, home/about pages, mobile-first CSS, shared `.container`
- [x] **Step 4b:** Brand + design foundation
  - [x] 4b.1 `data/site.json` (name, descriptor, tagline) as Jinja globals + self-hosted fonts
  - [x] 4b.2 Design tokens + light/dark mode (toggle: system → light → dark, saved in `localStorage`, no flash on load)
  - [x] 4b.3 Header/footer identity: wordmark + Tuwaiq cliff logo (decision 012) + favicon, theme toggle, footer
  - [x] 4b.4 Jinja macros in `app/templates/components.html`: `path_steps`, `source_stamp`, `unverified_stamp`, `next_step`
  - [x] 4b.5 Homepage structure (paths at a glance from `data/paths.json`, tests from `data/tests.json`, how we verify) + Tuwaiq section (`data/featured_quote.json`, shown only when `status: verified` or `WADIH_SHOW_DRAFTS=1`)
  - [x] 4b.6 Remaining docs (handoff rule in CLAUDE.md)
- [x] **Step 5:** Markdown content: 3 grade pages ("what to do this year") + scholarship path overview, `status: draft`. Homepage hero "في أي صف أنت؟" ("Which grade are you in?") links to them. Needs `markdown`, `python-frontmatter` (ask before installing).
- [x] **Step 5b:** "آخر المستجدات" (latest news) on the homepage from `data/news.json` (later fed by the update-monitor agent and linked to email alerts)
- [x] **Step 6:** pytest tests (33): pages, 404s, slug safety, draft gating, trust rules for data, no third-party requests. `requirements-dev.txt` + `pytest.ini`.
- [x] **Step 7:** Live on Render (free, Frankfurt): https://wadih-mqni.onrender.com. Every push to `main` redeploys (decision 017). Later: pin the Python version.
- [x] **Step 8:** README (live link, tests, how changes go live) + decisions 001–017.

**Stage 1 complete:** the site is live, tested, and deploys on every push.

### Stage 1b: Homepage design pass
- [x] Hero with Tuwaiq horizon + "ابدأ من هنا" revealing the grade question (decision 018)
- [x] News + tests in panels; news sorted by date then status, with status chips
- [x] Path panels with place scenes and accents (world / desert / sea)
- [x] Click-to-play video slot in the Tuwaiq band (decision 019)
- [x] Real licensed photos per path with credits (decision 020)
- [x] Share preview (Open Graph + share image), meta descriptions, robots.txt, sitemap.xml (decision 021)
- [x] Tuwaiq video: Al Arabiya's own clip `6fVtY11654w` added as draft, with a source line
- [x] Owner: watch the clip, confirm the wording matches `quote_ar` → set `status: verified` in `featured_quote.json`

### Stage 1c: Wide editorial redesign (decisions 022–023)
- [x] Light-first theme, two-state toggle
- [x] Plex Bold headlines + Naskh accents; owner's palette; wide grid + reading column
- [x] Header with nav + phone menu; 3-column footer
- [x] Hero with signature drawing; «من أين تبدأ؟»; compact news; facts-first path rows with «لمن؟»; 5-step journey; «كيف نعمل»

### Stage 1d: Tooling and learning docs (decision 024)
- [x] CI: GitHub Actions runs pytest on every push (`.github/workflows/tests.yml`)
- [x] Owner: Render → wadih → Settings → Auto-Deploy → "After CI Checks Pass" (after the first CI run is green)
- [x] `.env` permission lock (`.claude/settings.json`)
- [x] `docs/claude-workflow-guide.md`, `docs/architecture.md`; CLAUDE.md trimmed (a `LEARNING_LOG.md` too, removed 2026-10-13, decision 059)
- [x] Stale-facts report `scripts/stale_facts.py` (decision 053; a report, not a failing test)
- [x] `/update-site` (skill) + a morning check that keeps one GitHub issue (`watch.yml`): new واعد announcements, changed official pages, passed deadlines, broken pages and links, facts over 90 days (decision 064)
- [ ] Later: pin the server's Python version

### Stage 1e: Accuracy + clarity pass (owner's design brief, 2026-10-10; decisions 025–027)
Order chosen by the owner: facts first, then layout.
- [x] **Step 1: facts + program page.** Official-source fact-check (`docs/research/custodian-scholarship-2026-27.md`); one fact shape with source + date (decision 025); «غير مؤكد» only for real gaps; `/programs/custodian-scholarship` with all 4 tracks, a comparison table, the conditional-admission explainer + 5-question checklist, admission vs. scholarship; «المسارات» → «البرامج» (decision 027); Oxford photo removed (decision 026); grade 12 wording fixed. 64 tests.
- [x] Owner chose the official logo (decision 028)
- [x] **Step 2: homepage restructure (decision 028):** short hero with visible grade buttons → programs → news → Tuwaiq video; journey moved to grade 12, tests to grade 11; «من أين تبدأ؟», «كيف نعمل», and all «غير مؤكد» stamps and on-screen dates removed; photo credits moved to /about.
- [x] **IELTS resource page** `/resources/ielts` (official IELTS + MoE + KGSP sources).
- [x] KGSP and Aramco research by two parallel research agents → `docs/research/`.
- [x] Universities explorer: PDF downloaded to `data/raw/` (git-ignored), `pdfplumber` installed (dev), structure inspected, spec written. **Awaiting owner approval.**
- [x] **Step 3: grade pages (decision 038):** one structure for every grade (this week → what matters → 3–4 priorities → tool → ≤ 4 resources → next step on واضح → sources); every fact sourced (`docs/research/grade-pages-2026-10.md`); «الاختبارات: من يطلب ماذا؟» from `data/test_needs.json`; grade 12: three kinds of application in order, confirmation steps, checklist, next university deadlines from data. Status `sourced`, owner review pending.
- [x] **Finder, at a glance (decision 038):** scope note, tracks reordered, «لغة الدولة الرسمية» with a hint, SAT/IELTS/next date/admissions link per row and in «قائمتي», structured university dates (75 migrated), scholarship window shown apart from university dates.
- [ ] **Step 4: FAQ from real student questions.** The owner exports the Telegram group (Telegram Desktop → JSON); the raw export never enters the repo. Claude extracts only the questions, strips names/usernames/numbers, groups duplicates, counts them. Answers go in a data file with the fact shape; unanswered ones stay hidden. No automatic scraping.
- [x] **UX redesign (decision 035):** one design system; homepage (grades + search, open now, compact programs); explorer (filter tags, labels, back to results, Arabic suggestions fix); university pages («باختصار», not-admission notice); «قائمتي» on the device; program/grade pages; accessibility pass. Audit + research: `docs/research/ux-redesign-2026-10.md`.
- [x] Owner: review the redesign branch and merge it to `main`.
- [ ] **Step 5: usability test script** (`docs/research/usability-test.md`) for 3–5 students; the owner runs it. Include: find a major's universities on a phone, tell «الترتيب» from a world ranking, find a university's own deadline vs. the scholarship's, save two universities and find them again.
- [ ] **Step 6: accessibility + broken-link pass.** Accessibility half done in decision 035 (axe on 14 routes, 320px reflow, keyboard path, contrast tests); still to do: a screen-reader run on a real phone (VoiceOver/TalkBack) and the broken-link check.
- Later (Stage 2): per-university conditional-admission table for non-English-speaking destinations, generated from `data/universities.json` ("potentially eligible under the published exception", never "guaranteed").

### Research (alongside Stage 1)
- [x] First draft of the 3 paths + Tuwaiq quote sources: [research/paths-research.md](research/paths-research.md)

### Stage 2: Universities explorer + content model (headline of Launch 1)
- [x] **Shipped 2026-10-11** (decisions 029–032): extraction script → `data/universities.json` (290 universities, all track/field lists, majors, notes), `/universities` (search by university or major, filters incl. SDAIA targets), `/universities/<id>`, `/api/universities`, requirements for the 30 الرواد universities, Arabic names. Still open below: requirements for إمداد universities, Pydantic models, shared resources beyond IELTS.
Teaches data extraction, data modeling + validation (Pydantic), a JSON API, and client-side search.
- Spec first: `docs/specs/universities-explorer.md`.
- Extraction script `scripts/extract_universities.py` (needs a PDF library, ask before installing) → `data/universities.json`: `name_ar`, `name_en`, country, rank per track (الرواد / إمداد), rank per field/major, source = the MoE guide PDF, `last_checked`. Re-run when the new edition comes out (Dec 2026 / Jan 2027). The owner spot-checks a sample against the PDF.
- Public page `/universities`: type a name → the university appears with its track ranks and field ranks. JSON endpoint `/api/universities`. No logos in v1 (decision 016).
- Owner's design idea (2026-10-09): a "course finder" style box (search field + quick chips) that lets students browse by **target degree, country, and major**, then open a **university page** showing its available programs, degrees, and ranks per track (الرواد / إمداد) and per field, all exactly as the official list says. Which filters are possible depends on what the PDF contains; inspect it first. This is also where the header search arrives.
- SAT policy per university (required / optional / not considered + source link), starting with the Arruaad top 30.
- Pydantic models for paths, tracks, and universities: every fact has `source` + `last_checked`, or the app refuses to start. `active_year` setting.
- Shared resources (English/IELTS, Qudurat, math/Calc, Khan Academy links), linked many-to-many from paths.

### Stage 3: Scholarship path content + design polish + Launch 1
Teaches responsive/RTL polish, content workflow, CI, and shipping.
- Full government scholarship path page, verified by the owner, with live track status (each with a source link).
- ~~A subtle visual theme per path, based on place (decision 016)~~: dropped. Programs show their official logos or licensed photos (decisions 028, 062).
- [x] Visual identity: the sky, two designed themes, the homepage opening, the الرواد destination (decision 060). Real-phone check still to do.
- [x] Redesign «الطريق» (decision 062): the logo's colours, act on forest and read on paper, the route of the grades, labelled facts, a guides index, a full footer with a self-updating copyright line. Real-phone check still to do.
- Privacy-friendly visitor counting on our own server (decision 015).
- [x] CI basics: GitHub Actions runs the tests on every push.
- [x] Domain: wadihguide.com (decision 042).
- Then **Launch 1**.

### Stage 4: Accounts, email alerts, guided start → Launch 2
- «قائمتي» exists on the device (decision 035): at sign-in, offer to move the device list into the account; later a per-university checklist and a deadlines view built from the saved list.
Teaches databases, authentication (incl. OAuth), email delivery, security, privacy, and rules-based recommendation logic.
- Specs first: `docs/specs/accounts.md`, `docs/specs/email-alerts.md`, `docs/specs/guided-start.md`.
- Database: SQLite locally → Postgres in production (check free-tier limits then); tables like `users`, `plans`, `saved_universities`, `alert_subscriptions`; migrations (Alembic).
- Sign-in: **email + password** (hashed passwords, email verification, password reset) and **"Continue with Google"** (OAuth / OpenID Connect; the owner creates the Google Cloud project). Secure session cookies, CSRF protection, rate limiting.
- **Email alerts:** users pick paths to follow and get an email when a track opens/closes or there's an important announcement. Email service with a free tier (ask before signing up), unsubscribe link in every email.
- Privacy: minimum data (no national ID, GPA, test scores, passport), privacy policy, "delete my account", PDPL review incl. users under 18.
- Guided start: rules-based (not AI) recommendations + "your next 3 steps" + progress saved to the account. Then **Launch 2**.

### Later stages
5. Operations: broken-source-link checker, stale-content warnings, security headers, backups
6. More paths (Aramco, KAUST) and resources, one at a time, each verified
7. Search + RAG over verified content only, eval question set. **Started early (decision 045):** keyword search done; the steps are in `docs/specs/search.md`
8. Chatbot with citations (paid API, ask first), refuses when unsure
9. Agents with tool use + evals, e.g. an **update monitor** that watches official pages, drafts changes with links, and waits for the owner's approval (never auto-publishes). Once approved, the change can trigger the email alerts from Stage 4.
