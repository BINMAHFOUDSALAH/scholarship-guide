# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**واضح (Wadih, "clear")**: a free, Arabic-first website that helps Saudi high school students go from confusion to action about their future. Tagline: "مستقبلك بعد الثانوية، بوضوح" ("your future after high school, clearly").

- Organized around **paths** (مسارات), the programs a student can aim for: the government external scholarship, Aramco, KAUST, more later. Each path has requirements, steps, documents, and official sources. **Resources** (IELTS, SAT, Calculus, Khan Academy…) are shared and linked from many paths.
- **Help first.** Guides, path pages, and the universities explorer are open without an account (so Google can index them). Logging in (email + password or Google) unlocks personal features: guided start + saved plan, saved universities, and opt-in email alerts (decisions 014–015). No memberships or consultations.
- **Universities explorer** (decision 016): a public page to search the official MoE universities list by name and see ranks per track (الرواد / إمداد) and per field. Data comes from the official PDF via a re-runnable script. No logos. SAT is shown per university, not pushed to everyone.
- Launch 1 (~2026-12-09): public guides + the government scholarship path, fully verified, no accounts. Launch 2: accounts + guided start (roadmap Stage 4). Other paths come one at a time.
- Later: a chatbot and agents that answer only from verified content and always show sources.

**Before starting work, read [docs/roadmap.md](docs/roadmap.md) (current step) and [docs/decisions.md](docs/decisions.md) (why things are the way they are).** Before adding a new kind of project file (spec, skill, settings…), check [docs/project-files-guide.md](docs/project-files-guide.md).

## Rules
- This is a student guide. It is NOT the Ministry of Education, NOT Safeer, and not affiliated with Aramco or KAUST.
- Never invent official lists, deadlines, requirements, scores, or quotes. Claude may research official facts, but only from **official sources** (link every fact), and everything Claude researches stays `draft` / "غير مؤكد" until the owner verifies it. When sources conflict, record the conflict and publish no number. Research notes live in `docs/research/`.
- If something is not confirmed, label it "غير مؤكد" instead of guessing.
- Every important page shows a source and a last-updated date.
- Never collect sensitive data (no national ID, GPA, test scores, passport). Accounts store only login details and guided-start answers. Most users are minors, so treat privacy and security as requirements, not extras. No third-party requests until the user acts: fonts are self-hosted, no trackers, and the only embed is the click-to-play video (YouTube loads only after a click, decision 019).
- Never read, edit, or print the .env file.
- Arabic first, right-to-left, mobile first. One Arabic site with English names inline (universities, tests, majors). No separate English site.
- Design: ivory editorial look (palette: ivory `#F6F4EE`, charcoal text `#101713`, forest `#184B3A`, lime `#D8ED9B`). **Light mode first**; dark only via the toggle (decision 022). Lime sparingly for primary/selected states, progress, "open now", and small accents, never as small text (decision 023). Headlines in IBM Plex Sans Arabic Bold; Noto Naskh only for the wordmark and quotes. Wide grid ~1240px for the homepage; reading pages in a 720px `.measure`. No search UI until there's something to search (the universities explorer). Panels (one raised sheet per section) are fine; no gradients, grids of identical cards, stock photos, flags, or decorative animation (short functional reveals are OK, off under `prefers-reduced-motion`). Each path has a place-based accent (`theme` in `paths.json`: world/desert/sea) and a real, licensed photo of its place (`photo` in `paths.json`, files in `app/static/img/paths/` at 500/960px, credit + licence always shown; the SVG scene is the fallback). Never program logos (the Custodian logo contains the state emblem) (decisions 018, 020). Tints use `color-mix()` on tokens so dark mode follows automatically; check text contrast ≥ 4.5:1.
- Nothing official is hard-coded into templates. Names and settings live in `data/`, page text in content files.

## How to work with me
- I am a beginner learning applied AI engineering. Work in small steps and explain in plain words.
- Claude writes the code and runs/verifies it. Don't give me homework or tasks.
- After each step, keep the report short: **what I did** (a few bullets), **how to verify**, and **anything off** (errors, risks, things not checked). Add a key concept only when it's new and important. Then stop and wait.
- Ask before installing packages, downloading files, or spending money. Never commit or push unless I ask.
- Record every design choice (with the alternatives) in `docs/decisions.md`, and tick progress in `docs/roadmap.md`.
- **Handoff rule:** after any fundamental change (new rule, decision, architecture, or plan change), update `CLAUDE.md` / `docs/roadmap.md` / `docs/decisions.md` in the same step. These repo docs are the source of truth; Claude's local memory is only a backup. When I say a session is ending, make sure the roadmap's next step is accurate.

## Commands (Windows PowerShell, from the repo root)
```powershell
.venv\Scripts\Activate.ps1          # enter the virtual environment
pip install -r requirements.txt     # install dependencies
uvicorn app.main:app --reload       # run locally at http://127.0.0.1:8000
$env:WADIH_SHOW_DRAFTS="1"; uvicorn app.main:app --reload   # same, but also show unverified drafts (e.g. the Tuwaiq section)
pip install -r requirements-dev.txt # adds pytest + httpx (dev only; the live server uses requirements.txt)
pytest                              # run all tests
pytest tests/test_data.py -v        # one file
pytest tests/test_pages.py::test_about_loads   # one test
```
Tests: `test_pages.py` (pages load, 404s, draft gating, no third-party requests), `test_data.py` (the trust rules as code, e.g. a path can't be `verified` unless every track status has a source), `test_content.py` (Markdown loader + slug safety). Run `pytest` before every commit.

## Deploy
Live at https://wadih-mqni.onrender.com (Render free web service, Frankfurt). **Pushing to `main` deploys automatically**, so run `pytest` before every push. Render installs `requirements.txt` only (not the dev file) and starts `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Never set `WADIH_SHOW_DRAFTS` on Render. Free instances sleep when idle.

## Architecture
- `app/main.py`: the FastAPI app. Loads `data/site.json` once at startup and exposes it to every template as the Jinja global `site`. Routes return server-rendered Jinja2 templates (no frontend framework).
- `app/templates/`: `base.html` is the shared layout (`<html lang="ar" dir="rtl">`, header, footer). Pages `{% extends "base.html" %}`. Header, main, and footer all use the `.container` class so their edges line up.
- `app/static/`: `style.css` (mobile-first; use logical properties like `padding-inline`, never left/right), `fonts.css` + `fonts/` (self-hosted IBM Plex Sans Arabic for body, Noto Naskh Arabic for headings, OFL).
- `data/`: settings and facts as JSON (`site.json`, `paths.json`, `tests.json`, `news.json`, `featured_quote.json`), loaded once at startup by `load_json()` in `app/main.py`. `news.json` items (`date`, `type`: opening/closing/deadline/announcement, `path_id`, `title_ar`, `source_url`) are sorted newest first, and the homepage shows the latest 5. Items without `source_url` get the "غير مؤكد" stamp. Dates are ISO in data and shown via the `arabic_date` Jinja filter. Anything with `verified: false` / `status_source: null` / `status: draft` renders with the "غير مؤكد" stamp or stays hidden. `featured_quote.json` renders only when `status` is `verified` or `WADIH_SHOW_DRAFTS=1`. Data changes need a server restart.
- `content/<section>/<slug>.md`: Markdown pages with frontmatter (`title`, `description`, `status`, `sources`, `last_checked`, `next_step`). `app/content.py` `load_page()` validates the slug (`^[a-z0-9-]+$`, so URLs can never reach other files) and renders the Markdown on every request, so content edits need no restart. Routes like `/grades/{slug}` render `page.html`; unknown pages raise 404, which shows the Arabic `404.html`.
- Header/footer (`base.html`): the nav links are one Jinja list (`nav_links`) used by the desktop nav, the phone `<details>` menu, and the footer. Homepage text (lead, hero labels, starting points, journey steps, trust points) lives in `data/home.json`; paths have `audience_ar` («لمن؟»). `.container` = wide grid, `.measure` = reading column.
- Template blocks in `base.html`: `{% block hero %}` (full width, above the reading column), `{% block content %}` (inside the reading column), `{% block after_content %}` (full-width bands such as `partials/tuwaiq.html`), `{% block scripts %}` (page-only JS, e.g. `video.js`). SVG illustrations live as macros in `partials/path-art.html`.
- SEO and sharing (decision 021): `base.html` sets meta description (`{% block description %}`), canonical URL, Open Graph/Twitter tags, and the share image `static/img/og-image.png` (regenerate with `scripts/og-image.js` in the browser console). `/robots.txt` and `/sitemap.xml` are routes in `app/main.py`; the sitemap lists grade pages via `list_slugs()` in `app/content.py`. All absolute URLs use `site.base_url` in `data/site.json`; change it there when the custom domain arrives.
- News order: `sort_news()` in `app/main.py` (publication date desc, then opening → deadline → closing → announcement). The quote's video uses `youtube_id` in `featured_quote.json`.
- After CSS changes, browsers may serve a cached copy: hard-refresh with Ctrl+Shift+R.
