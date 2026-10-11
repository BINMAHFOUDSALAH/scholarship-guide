# Roadmap

The living plan for واضح. Update the checkboxes at the end of every step.
Why each choice was made lives in [decisions.md](decisions.md).

> **Next session (as of 2026-10-11):**
> 1. **Owner approves `docs/specs/universities-explorer.md`** (3 decisions at the bottom), then build the explorer: extraction script → `data/universities.json` → `/universities`.
> 2. Apply the KGSP and Aramco research (`docs/research/kgsp-2026-27.md`, `aramco-cdpne-2026-27.md`) to `paths.json` once the owner has reviewed them.
> 3. Then Stage 1e step 3 (grade-page task lists) and step 4 (FAQ from real student questions).
> 4. Check that the owner flipped Render's Auto-Deploy to "After CI Checks Pass".
>
> Owner to-dos still open: review the fact-check tables (§5 of each research file), send the X post links for الرواد/إمداد, optionally export the Telegram group (JSON) for the FAQ step.

**Launch 1 (~2026-12-09):** public guides + the government scholarship path, fully verified. No accounts.
**Launch 2 (after Stage 4):** accounts + guided start + personal plan (decision 014).
**Pace:** ~5 hours per week.

---

## Stage 1: Live walking skeleton
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

## Stage 1b: Homepage design pass
- [x] Hero with Tuwaiq horizon + "ابدأ من هنا" revealing the grade question (decision 018)
- [x] News + tests in panels; news sorted by date then status, with status chips
- [x] Path panels with place scenes and accents (world / desert / sea)
- [x] Click-to-play video slot in the Tuwaiq band (decision 019)
- [x] Real licensed photos per path with credits (decision 020)
- [x] Share preview (Open Graph + share image), meta descriptions, robots.txt, sitemap.xml (decision 021)
- [x] Tuwaiq video: Al Arabiya's own clip `6fVtY11654w` added as draft, with a source line
- [ ] Owner: watch the clip, confirm the wording matches `quote_ar` → set `status: verified` in `featured_quote.json`

## Stage 1d: Tooling and learning docs (decision 024)
- [x] CI: GitHub Actions runs pytest on every push (`.github/workflows/tests.yml`)
- [ ] Owner: Render → wadih → Settings → Auto-Deploy → "After CI Checks Pass" (after the first CI run is green)
- [x] `.env` permission lock (`.claude/settings.json`)
- [x] `docs/CLAUDE_WORKFLOW_GUIDE.md`, `LEARNING_LOG.md`, `docs/architecture.md`; CLAUDE.md trimmed
- [ ] Later: stale-facts test (fail when `last_checked` > 90 days), weekly broken-link check, pin the server's Python version

## Stage 1c: Wide editorial redesign (decisions 022–023)
- [x] Light-first theme, two-state toggle
- [x] Plex Bold headlines + Naskh accents; owner's palette; wide grid + reading column
- [x] Header with nav + phone menu; 3-column footer
- [x] Hero with signature drawing; «من أين تبدأ؟»; compact news; facts-first path rows with «لمن؟»; 5-step journey; «كيف نعمل»
- [ ] Owner: X post links for الرواد open / إمداد closed → `source_url` in `news.json` and `status_source` in `paths.json`

## Stage 1e: Accuracy + clarity pass (owner's design brief, 2026-10-10; decisions 025–027)
Order chosen by the owner: facts first, then layout.
- [x] **Step 1: facts + program page.** Official-source fact-check (`docs/research/custodian-scholarship-2026-27.md`); one fact shape with source + date (decision 025); «غير مؤكد» only for real gaps; `/programs/custodian-scholarship` with all 4 tracks, a comparison table, the conditional-admission explainer + 5-question checklist, admission vs. scholarship; «المسارات» → «البرامج» (decision 027); Oxford photo removed (decision 026); grade 12 wording fixed. 64 tests.
- [x] Owner chose the official logo (decision 028)
- [ ] Owner: review the fact-check table
- [x] **Step 2: homepage restructure (decision 028):** short hero with visible grade buttons → programs → news → Tuwaiq video; journey moved to grade 12, tests to grade 11; «من أين تبدأ؟», «كيف نعمل», and all «غير مؤكد» stamps and on-screen dates removed; photo credits moved to /about.
- [x] **IELTS resource page** `/resources/ielts` (official IELTS + MoE + KGSP sources).
- [x] KGSP and Aramco research by two parallel research agents → `docs/research/`.
- [x] Universities explorer: PDF downloaded to `data/raw/` (git-ignored), `pdfplumber` installed (dev), structure inspected, spec written. **Awaiting owner approval.**
- [ ] **Step 3: grade pages «خطوتك القادمة»:** a short task list per grade (action, why, source, now/later; dates only when verified). Grade pages get sources (end their draft status).
- [ ] **Step 4: FAQ from real student questions.** The owner exports the Telegram group (Telegram Desktop → JSON); the raw export never enters the repo. Claude extracts only the questions, strips names/usernames/numbers, groups duplicates, counts them. Answers go in a data file with the fact shape; unanswered ones stay hidden. No automatic scraping.
- [ ] **Step 5: usability test script** (`docs/research/usability-test.md`) for 3–5 students; the owner runs it.
- [ ] **Step 6: accessibility + broken-link pass.**
- Later (Stage 2): per-university conditional-admission table for non-English-speaking destinations, generated from `data/universities.json` ("potentially eligible under the published exception", never "guaranteed").

## Research (in progress, alongside Stage 1)
- [x] First draft of the 3 paths + Tuwaiq quote sources: [research/paths-research.md](research/paths-research.md)
- [ ] Owner verifies (checklist at the bottom of that file)

## Stage 2: Universities explorer + content model (headline of Launch 1)
Teaches data extraction, data modeling + validation (Pydantic), a JSON API, and client-side search.
- Spec first: `docs/specs/universities-explorer.md`.
- Extraction script `scripts/extract_universities.py` (needs a PDF library, ask before installing) → `data/universities.json`: `name_ar`, `name_en`, country, rank per track (الرواد / إمداد), rank per field/major, source = the MoE guide PDF, `last_checked`. Re-run when the new edition comes out (Dec 2026 / Jan 2027). The owner spot-checks a sample against the PDF.
- Public page `/universities`: type a name → the university appears with its track ranks and field ranks. JSON endpoint `/api/universities`. No logos in v1 (decision 016).
- Owner's design idea (2026-10-09): a "course finder" style box (search field + quick chips) that lets students browse by **target degree, country, and major**, then open a **university page** showing its available programs, degrees, and ranks per track (الرواد / إمداد) and per field, all exactly as the official list says. Which filters are possible depends on what the PDF contains; inspect it first. This is also where the header search arrives.
- SAT policy per university (required / optional / not considered + source link), starting with the Arruaad top 30.
- Pydantic models for paths, tracks, and universities: every fact has `source` + `last_checked`, or the app refuses to start. `active_year` setting.
- Shared resources (English/IELTS, Qudurat, math/Calc, Khan Academy links), linked many-to-many from paths.

## Stage 3: Scholarship path content + design polish + Launch 1
Teaches responsive/RTL polish, content workflow, CI, and shipping.
- Full government scholarship path page, verified by the owner, with live track status (each with a source link).
- A subtle visual theme per path, based on place (decision 016): world/cities (scholarship), eastern desert (Aramco), Red Sea coast (KAUST). No logos.
- Privacy-friendly visitor counting on our own server (decision 015).
- CI basics: GitHub Actions runs the tests on every push.
- Domain check/purchase (ask first), then **Launch 1**.

## Stage 4: Accounts, email alerts, guided start → Launch 2
Teaches databases, authentication (incl. OAuth), email delivery, security, privacy, and rules-based recommendation logic.
- Specs first: `docs/specs/accounts.md`, `docs/specs/email-alerts.md`, `docs/specs/guided-start.md`.
- Database: SQLite locally → Postgres in production (check free-tier limits then); tables like `users`, `plans`, `saved_universities`, `alert_subscriptions`; migrations (Alembic).
- Sign-in: **email + password** (hashed passwords, email verification, password reset) and **"Continue with Google"** (OAuth / OpenID Connect; the owner creates the Google Cloud project). Secure session cookies, CSRF protection, rate limiting.
- **Email alerts:** users pick paths to follow and get an email when a track opens/closes or there's an important announcement. Email service with a free tier (ask before signing up), unsubscribe link in every email.
- Privacy: minimum data (no national ID, GPA, test scores, passport), privacy policy, "delete my account", PDPL review incl. users under 18.
- Guided start: rules-based (not AI) recommendations + "your next 3 steps" + progress saved to the account. Then **Launch 2**.

## Later stages
5. Operations: broken-source-link checker, stale-content warnings, security headers, backups
6. More paths (Aramco, KAUST) and resources, one at a time, each verified
7. Search + RAG over verified content only, eval question set
8. Chatbot with citations (paid API, ask first), refuses when unsure
9. Agents with tool use + evals, e.g. an **update monitor** that watches official pages, drafts changes with links, and waits for the owner's approval (never auto-publishes). Once approved, the change can trigger the email alerts from Stage 4.
