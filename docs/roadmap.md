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
- [ ] **Step 5:** Markdown content: 3 grade pages ("what to do this year") + scholarship path overview, `status: draft`. Homepage hero "في أي صف أنت؟" ("Which grade are you in?") links to them. Needs `markdown`, `python-frontmatter` (ask before installing).
- [ ] **Step 6:** pytest tests: pages load, RTL, theme toggle present, Tuwaiq hidden when draft, 404. Needs `pytest`, `httpx` (ask first).
- [ ] **Step 7:** Deploy to Render free tier. The owner creates the account and commits/pushes.
- [ ] **Step 8:** README + decisions update.

## Research (in progress, alongside Stage 1)
- [x] First draft of the 3 paths + Tuwaiq quote sources: [research/paths-research.md](research/paths-research.md)
- [ ] Owner verifies (checklist at the bottom of that file)

## Stage 2: Content model + validation
Teaches data modeling and validation with Pydantic.
- `data/paths/*.json` (one per path: requirements, steps, documents) and `data/resources/*.json` (IELTS, SAT, Calc…), linked many-to-many.
- Every requirement has `source` + `last_checked`, or the app refuses to start.
- Compare-paths table, `active_year` setting, source stamps on pages.
- `data/universities.json` from the official MoE guide (top 30 / top 200 by field), each with `name_ar`, `name_en`, source, `last_checked`.
- First shared resources: English/IELTS, SAT, Qudurat, math (Calc), with Khan Academy and other free links.

## Stage 3: Scholarship path content + Launch 1
Teaches responsive/RTL polish, content workflow, and shipping.
- Full government scholarship path, verified by the owner, with live track status (الرواد open, إمداد closed…), each with a source link. Mobile polish.
- CI basics: GitHub Actions runs the tests on every push.
- Domain check/purchase (ask first), then **Launch 1**.

## Stage 4: Accounts + guided start → Launch 2
Teaches databases, authentication, security, privacy, and rules-based recommendation logic.
- Spec first: `docs/specs/guided-start.md` (questions, the rules from verified data, the plan output, edge cases).
- Database: SQLite locally → Postgres in production (check free-tier limits at that time); tables `users`, `plans`; migrations (Alembic).
- Authentication: sign up / log in / log out / password reset, hashed passwords, secure session cookies, CSRF protection, rate limiting. Choose the login method (email + password vs email link vs Google) in the spec.
- Privacy: minimum data (no national ID, GPA, test scores, passport), privacy policy page, "delete my account", review Saudi PDPL obligations incl. users under 18.
- Guided start: rules-based (not AI) recommendations + "your next 3 steps" + progress checklist saved to the account. Then **Launch 2**.

## Later stages
5. Operations: broken-source-link checker, stale-content warnings, security headers, backups
6. More paths (Aramco, KAUST) and resources, one at a time, each verified
7. Search + RAG over verified content only, eval question set
8. Chatbot with citations (paid API, ask first), refuses when unsure
9. Agents with tool use + evals, e.g. an **update monitor** that watches official pages, drafts changes with links, and waits for the owner's approval (never auto-publishes)
