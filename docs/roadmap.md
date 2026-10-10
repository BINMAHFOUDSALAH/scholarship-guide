# Roadmap

The living plan for واضح. Update the checkboxes at the end of every step.
Why each choice was made lives in [decisions.md](decisions.md).

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
- [ ] **Step 6:** pytest tests: pages load, RTL, theme toggle present, Tuwaiq hidden when draft, 404. Needs `pytest`, `httpx` (ask first).
- [ ] **Step 7:** Deploy to Render free tier. The owner creates the account and commits/pushes.
- [ ] **Step 8:** README + decisions update.

## Research (in progress, alongside Stage 1)
- [x] First draft of the 3 paths + Tuwaiq quote sources: [research/paths-research.md](research/paths-research.md)
- [ ] Owner verifies (checklist at the bottom of that file)

## Stage 2: Universities explorer + content model (headline of Launch 1)
Teaches data extraction, data modeling + validation (Pydantic), a JSON API, and client-side search.
- Spec first: `docs/specs/universities-explorer.md`.
- Extraction script `scripts/extract_universities.py` (needs a PDF library, ask before installing) → `data/universities.json`: `name_ar`, `name_en`, country, rank per track (الرواد / إمداد), rank per field/major, source = the MoE guide PDF, `last_checked`. Re-run when the new edition comes out (Dec 2026 / Jan 2027). The owner spot-checks a sample against the PDF.
- Public page `/universities`: type a name → the university appears with its track ranks and field ranks. JSON endpoint `/api/universities`. No logos in v1 (decision 016).
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
