# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**واضح (Wadih, "clear")**: a free, Arabic-first website that helps Saudi high school students go from confusion to action about their future. Tagline: "مستقبلك بعد الثانوية، بوضوح".

- Organized around **programs** («البرامج» on the site, `paths` in code): the government external scholarship (with the Ministry's four tracks, «مسار الرواد»…), Aramco, KAUST, more later. Each has requirements, steps, and official sources; a program with `content/programs/<id>.md` gets its own page. **Resources** (IELTS, SAT, Calculus…) are shared across programs.
- **Direction (decision 057):** a deep, verified study-abroad core, plus thin doors that route to official tools rather than rebuilding them: «لم تقرر بعد؟», «الدراسة في السعودية», and the grade pages. No scored career quiz: «جرّب قبل أن تقرر» is an unscored exploration activity (decision 070).
- **Help first.** Guides, path pages, and the universities explorer are public (Google can index them). Until accounts exist, «خطتي» keeps universities and program tracks, with a status each, on the student's device only (decisions 035, 078).
- **Where we are (owner, 2026-11-16):** a complete redesign comes first, version 3 «عالم وضّاح»; the launch dates are dropped until it is done. Built: the foundation (colours, one typeface, buttons with a lip, the header) and the homepage. **Next, one page at a time:** «خطتي», the university page, the program page, the explorer. **After the redesign:** accounts and the AI guide **وضّاح**, which answers only from verified content, with sources. The [agent](docs/specs/agent.md) and [accounts](docs/specs/accounts.md) specs predate the owner's 2026-11-16 vision (a mentor that remembers the student, Google sign-in) and must be revised with the owner before anything is built from them. **The plan, step by step: [docs/plan.md](docs/plan.md); when the owner says "do the next step", do its first step not marked done, then mark it done there.** Open to-dos: the top of [docs/log.md](docs/log.md).
- The owner is building this to become an AI-focused Forward Deployed Engineer: ship a real product **and** understand it well enough to explain, debug, and improve it.

**Docs:** [docs/architecture.md](docs/architecture.md) (how the code fits together), [docs/README.md](docs/README.md) (map of the docs and all script commands). Decision numbers in this file and the code (e.g. "decision 062") point to the old `docs/decisions.md`, removed on 2026-11-16; when the why matters, search it with `git show f7235f0:docs/decisions.md | Select-String "## 062"`, never read it whole (220 KB).

## Rules
- **Never invent official lists, deadlines, requirements, scores, or quotes.**
  - Research facts only from **official sources**, read directly; link every fact with the date it was read. Never publish from search snippets.
  - A fact with an official source shows its source link. Anything not backed by an official source or the owner's confirmation is **hidden, never stamped** (no «غير مؤكد», decision 028).
  - Research that couldn't be read on the official page stays in a `"draft": true` file (decision 058).
  - If official sources conflict, show both and publish no single answer.
  - Check dates stay in the data (`last_checked`) but aren't shown; the owner's review is `owner_reviewed`. Research notes: `docs/research/`.
- Never read, edit, or print `.env` (also enforced by `.claude/settings.json`).
- Arabic first, RTL, mobile first. The Arabic is the source; `/en/...` is the same site in English (decision 066).
  - **Every Arabic change ships with its English in the same commit:** templates/Python/JS text → `data/i18n/ui.en.json` / `js.en.json`; data → `data.en.json` or `universities.en.json` (keyed by the exact Arabic); a page → `content/en/<section>/<slug>.md` with its new `translated_from`. `tests/test_english.py` fails until it's done.
  - Translate exactly: keep numbers, dates, conditions and hedges; minimum ≠ recommended; "not listed" ≠ "not accepted". Our translation of a quote says "(our translation)".
- **Formal Arabic (الفصحى) on every page, never dialect** (decision 058; a test checks common dialect words). Keep terms consistent: test parts are «مهارات» (الاستماع، القراءة، الكتابة، التحدث); a score is «الحد الأدنى» or «الموصى به», never just a number.
- Design (version 3, «عالم وضّاح», owner 2026-11-16): the colours and shapes come from وضّاح and the logo he shares them with: a clay page to read, forest to act, lime for now / next / here; one typeface (Readex Pro); what you can press has a lip; each broad field has its own tone (075); the logo and the mascot never change. The full rules are in `.claude/rules/design.md`, which loads automatically when working on `app/templates/` or `app/static/`.
  - **Design tools (decision 076):** `design.md` always beats any design plugin or skill: never apply a plugin's palette, fonts, layouts or starter files. Build with `frontend-design` or Taste (`design-taste-frontend`); review with Taste, `web-design-guidelines` (project skill), `design:design-critique` and `design:accessibility-review`. Taste may design and review any page (owner, 2026-11-25), always inside `design.md`.
- Nothing official is hard-coded in templates: data in `data/`, page text in `content/`.

- **For each task:**
  1. Implement only what's asked; don't touch unrelated code.
  2. Verify with tests (and the browser for UI); say clearly what's untested.
  3. Report briefly: **what changed**, **how I can test it myself**, **the key concept**.
  4. **Recommend the next step** (fix, commit, push, or move on).
- The key concept goes in the report itself. At most one short, optional understanding question per feature, with the answer right after; never block the work on it.
- **Subagents** (decision 037): use them only when they add real value like when we are doing a massive research with new universities when we want to add or update or when I ask, and tell me briefly when and why. Quick lookups and small edits stay in the main session.
  - **Models (decision 077):** `source-researcher` on **Haiku** (bulk reading; the main session checks every quote); `fact-checker` and `reviewer` on **Sonnet** (judgement guards the facts). Aliases, so each always runs the latest version. Set in each agent file; any other subagent defaults to Haiku (`.claude/settings.json`). In cloud sessions settings may not apply: also pass the agent's model (`model: "haiku"` or `"sonnet"`) and ask it to report its model. If a subagent fails or reports a different model, stop and tell me; don't rerun it on another model or do the job silently in the main session.
  - The agents (`.claude/agents/`) are read-only and return results. The main session saves them, validates them with tests, makes the decisions and flags anything an agent couldn't verify.
  - `source-researcher` for new facts (~5 items per agent, in parallel, with a strict schema + a finished example file), `fact-checker` for what's already published, `reviewer` for a big or risky diff. University requirements: the `research-wave` skill. Bringing the site up to date (new announcements, passed deadlines, Aramco/KAUST/SDAIA/الرواد…): the `update-site` skill.
- Ask before installing packages, downloading files, or spending money.
- Git (owner, 2026-11-06): once a task is **verified** (all tests pass, and the browser for UI), commit on a branch, push it, open a PR and merge it after CI passes, without asking. Never merge with failing tests or CI, never push straight to `main`, never force-push. If verification fails or something is unverifiable and risky, stop and tell me instead of merging.
- Write the why of a design choice (with the alternatives) in its PR description.
- **Handoff rule:** after any fundamental change (rule, architecture, plan), update `CLAUDE.md` / `docs/architecture.md` in the same step. Repo docs are the source of truth. When a session ends, add a short dated note to `docs/log.md` and keep its "Open" list accurate (tick or delete what's done).

## Commands (Windows PowerShell, from the repo root)
```powershell
.venv\Scripts\Activate.ps1                      # enter the virtual environment
pip install -r requirements-dev.txt             # app + test tools (the live server uses requirements.txt)
uvicorn app.main:app --reload                   # run locally at http://127.0.0.1:8000
$env:WADIH_SHOW_DRAFTS="1"; uvicorn app.main:app --reload   # also show unverified drafts
pytest                                          # all tests (run before every commit)
python scripts/english_leaks.py                 # Arabic still showing on English pages (should be 0)
```
Fact-checking, watch and browser-check scripts: [docs/README.md](docs/README.md#commands).

## Deploy
- Live at https://wadihguide.com: domain at Cloudflare (DNS only), hosted on Render (Frankfurt, $7/month plan so it never sleeps). The old https://wadih-mqni.onrender.com and www redirect there with a 301 (decision 042).
- GitHub Actions runs `pytest` on every push (`.github/workflows/tests.yml`); Render auto-deploys **only after CI passes**. It installs `requirements.txt` and runs `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Never set `WADIH_SHOW_DRAFTS` on Render.
- Every morning `.github/workflows/watch.yml` runs `scripts/watch.py` and keeps one GitHub issue, «Site check», that pings the owner only for new urgent findings (decision 064). It never changes the site; the fixing is `/update-site`.
