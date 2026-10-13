# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**واضح (Wadih, "clear")**: a free, Arabic-first website that helps Saudi high school students go from confusion to action about their future. Tagline: "مستقبلك بعد الثانوية، بوضوح".

- Organized around **programs** («البرامج» on the site, `paths` in code): the government external scholarship (with the Ministry's four tracks, «مسار الرواد»…), Aramco, KAUST, more later. Each has requirements, steps, and official sources; a program with `content/programs/<id>.md` gets its own page. **Resources** (IELTS, SAT, Calculus…) are shared across programs.
- **Help first.** Guides, path pages, and the universities explorer are public (Google can index them). Login (email + password or Google) unlocks personal features: guided start + saved plan, saved universities, opt-in email alerts (decisions 014–016). Until then, «قائمتي» saves universities on the student's device only (decision 035).
- Launch 1 (~2026-12-09): public guides + the government scholarship path, fully verified. Launch 2: accounts + guided start. Later: a chatbot and agents that answer only from verified content, with sources.
- The owner is building this to become an AI-focused Forward Deployed Engineer: ship a real product **and** understand it well enough to explain, debug, and improve it.

**Read first:** [docs/roadmap.md](docs/roadmap.md) (current step), [docs/decisions.md](docs/decisions.md) (why), [docs/architecture.md](docs/architecture.md) (how the code fits together). Also: [docs/CLAUDE_WORKFLOW_GUIDE.md](docs/CLAUDE_WORKFLOW_GUIDE.md), [docs/project-files-guide.md](docs/project-files-guide.md) (check before adding a new kind of project file), [LEARNING_LOG.md](LEARNING_LOG.md).

## Rules
- A student guide: NOT the Ministry of Education, NOT Safeer, not affiliated with Aramco or KAUST.
- Never invent official lists, deadlines, requirements, scores, or quotes. Claude may research facts only from **official sources**, read directly (link every fact, with the date it was read). A fact with an official source shows its source link; anything not backed by an official source or the owner's confirmation is **hidden, never stamped** (no «غير مؤكد», decision 028). Check dates stay in the data (`last_checked`) but aren't shown. The owner's review is tracked as `owner_reviewed`. If official sources conflict, show both and publish no single answer. Research notes: `docs/research/`.
- Every important page shows its official sources.
- Never collect sensitive data (no national ID, GPA, test scores, passport). Users are mostly minors: privacy and security are requirements. No third-party requests until the user acts (self-hosted fonts, no trackers; the only embed is click-to-play video).
- Never read, edit, or print `.env` (also enforced by `.claude/settings.json`).
- Arabic first, RTL, mobile first. One Arabic site with English names inline.
- Design (decision 035): ivory `#F6F4EE`, charcoal `#101713`, forest `#184B3A` (headings, links, the main button), lime `#D8ED9B` only for «مفتوح الآن» and the next step, never as small text. Light mode first (dark via toggle). Plex Sans Arabic Bold headlines; Naskh only for the wordmark and quotes. Wide grid for the homepage, `.page-wide` for tool pages, 720px `.measure` for reading. Build with the shared components (buttons, `status_tag`, tags, notices, summary list, back link) instead of one-off styles; nothing under 13px. Panels yes; no gradients, grids of identical cards, stock photos, or decorative animation. Logos: the programs' official ones (decision 028), and a country flag beside the country name (pages and lists), and each university's official logo on its own page only, self-hosted with source and licence (decision 049). Real licensed photos with credit. Contrast is checked by `tests/test_design.py` (≥ 4.5:1 text, ≥ 3:1 borders and focus).
- Nothing official is hard-coded in templates: data in `data/`, page text in `content/`.

## How to work with me
- I'm a beginner. Keep it concise and practical: ship a useful product, avoid overengineering, explain important decisions without overwhelming me. Separate what I must understand deeply from details I can safely delegate.
- **For each task:**
  1. Implement only what's asked; don't touch unrelated code.
  2. Verify with tests (and the browser for UI); say clearly what's untested.
  3. Report briefly: **what changed**, **how I can test it myself**, **the key concept**.
  4. **Recommend the next step** (fix, commit, push, or move on).
- After a meaningful feature, update `LEARNING_LOG.md` accurately. Never mark something as understood just because it was explained. At most one short, optional understanding question per feature, with the answer right after; never block the work on it.
- **Subagents** (decision 037): use them only when they add real value or when I ask, and tell me briefly when and why. Every subagent runs on **Haiku 5.5** (`claude-haiku-5-5`, set in each `.claude/agents/*.md` and in `.claude/settings.json` for built-in agents); never pass another model. If a subagent fails or reports a different model, stop and tell me; don't rerun it on another model or do the job silently in the main session.
  - `source-researcher`: new facts from official sources, ~5 items per agent, in parallel, with a strict schema + a finished example file.
  - `fact-checker`: checks what's already published against its cited sources.
  - `reviewer`: an independent check of a big or risky diff.
  - Research agents are read-only: they read pages directly, with WebFetch or, where it can't reach a site (e.g. in a cloud session), with `curl`, and return results, and the main session saves them, validates them with tests, makes the decisions, writes the code, and flags anything an agent couldn't verify. Quick lookups and small edits stay in the main session.
- Ask before installing packages, downloading files, or spending money. Never commit or push unless I ask.
- Record design choices (with alternatives) in `docs/decisions.md`; tick progress in `docs/roadmap.md`.
- **Handoff rule:** after any fundamental change (rule, decision, architecture, plan), update `CLAUDE.md` / `docs/roadmap.md` / `docs/decisions.md` / `docs/architecture.md` in the same step. Repo docs are the source of truth. When I say a session is ending, make sure the roadmap's "next session" note is accurate.

## Commands (Windows PowerShell, from the repo root)
```powershell
.venv\Scripts\Activate.ps1                      # enter the virtual environment
pip install -r requirements-dev.txt             # app + test tools (the live server uses requirements.txt)
uvicorn app.main:app --reload                   # run locally at http://127.0.0.1:8000
$env:WADIH_SHOW_DRAFTS="1"; uvicorn app.main:app --reload   # also show unverified drafts
pytest                                          # all tests (run before every commit)
pytest tests/test_data.py -v                    # one file
pytest tests/test_pages.py::test_about_loads    # one test
```

## Deploy
Live at https://wadihguide.com (domain at Cloudflare, DNS only; hosted on Render free tier, Frankfurt). The old address https://wadih-mqni.onrender.com and www redirect there with a 301 (decision 042). GitHub Actions runs `pytest` on every push (`.github/workflows/tests.yml`); Render auto-deploys **only after CI passes**. Render installs `requirements.txt` and runs `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Never set `WADIH_SHOW_DRAFTS` on Render. Free instances sleep when idle.
