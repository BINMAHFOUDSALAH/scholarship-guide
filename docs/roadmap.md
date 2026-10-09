# Roadmap

The living plan for واضح. Update the checkboxes at the end of every step.
Why each choice was made lives in [decisions.md](decisions.md).

**Launch target:** ~2026-12-09, with the government external scholarship path fully verified.
**Pace:** ~5 hours per week.

---

## Stage 1: Live walking skeleton
Teaches HTTP, routing, templates, virtual environments, testing, and deployment.

- [x] **Step 1:** Housekeeping + `docs/decisions.md`
- [x] **Step 2:** `.venv` + FastAPI, Uvicorn, Jinja2 in `requirements.txt`
- [x] **Step 3:** First FastAPI routes (`/`, `/about`)
- [x] **Step 4:** RTL base template, home/about pages, mobile-first CSS, shared `.container`
- [ ] **Step 4b:** Brand + design foundation
  - [x] 4b.1 `data/site.json` (name, descriptor, tagline) as Jinja globals + self-hosted fonts
  - [ ] 4b.2 Design tokens + light/dark mode (toggle: system → light → dark, saved in `localStorage`, no flash on load)
  - [ ] 4b.3 Header/footer identity: wordmark + SVG path-line mark, theme toggle, "no account, no email, no data" footer
  - [ ] 4b.4 Jinja macros in `app/templates/components.html`: `path_steps`, `source_stamp`, `unverified_stamp`, `next_step`
  - [ ] 4b.5 Homepage structure + Tuwaiq section (`data/featured_quote.json`, shown only when `status: verified` or `WADIH_SHOW_DRAFTS=1`)
  - [ ] 4b.6 Remaining docs
- [ ] **Step 5:** Markdown content: 3 grade pages ("what to do this year") + scholarship path overview, `status: draft`. Homepage hero "في أي صف أنت؟" ("Which grade are you in?") links to them. Needs `markdown`, `python-frontmatter` (ask before installing).
- [ ] **Step 6:** pytest tests: pages load, RTL, theme toggle present, Tuwaiq hidden when draft, 404. Needs `pytest`, `httpx` (ask first).
- [ ] **Step 7:** Deploy to Render free tier. The owner creates the account and commits/pushes.
- [ ] **Step 8:** README + decisions update.

## Stage 2: Content model + validation
Teaches data modeling and validation with Pydantic.
- `data/paths/*.json` (one per path: requirements, steps, documents) and `data/resources/*.json` (IELTS, SAT, Calc…), linked many-to-many.
- Every requirement has `source` + `last_checked`, or the app refuses to start.
- Compare-paths table, `active_year` setting, source stamps on pages.

## Stage 3: Scholarship path content + launch
Teaches responsive/RTL polish, content workflow, and shipping.
- Full government scholarship path, verified by the owner. Mobile polish.
- Domain check/purchase (ask first), then launch.

## Later stages
4. CI (GitHub Actions), broken-source-link checker, stale-content warnings, security headers
5. More paths (Aramco, KAUST) and resources, one at a time, each verified
6. Search + RAG over verified content only, first database, eval question set
7. Chatbot with citations (paid API, ask first), refuses when unsure
8. Agents with tool use + evals
