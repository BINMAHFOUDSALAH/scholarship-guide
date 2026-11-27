# CLAUDE.md

## Project

**واضح (Wadih)** is a pre-launch, Arabic-first scholarship and university guide for Saudi high school students. Help students find opportunities, understand requirements, and decide what to do next. The tagline is «مستقبلك بعد الثانوية، بوضوح».

- Programs («البرامج», `paths` in code), university discovery, grade guides, and shared resources are the core of the site. A program with `content/programs/<id>.md` has a dedicated page.
- Keep the public guide and University Finder free to browse. Finish the redesign, then deploy وضّاح with Google sign-in for students who choose to use the agent.
- وضّاح uses the same verified scholarship and university data as Wadih, cites official sources, and lets students control changes to «خطتي». When agent work begins, review `docs/specs/agent.md` and `docs/specs/accounts.md` and update them to reflect the current plan.
- «جرّب قبل أن تقرر» is an unscored exploration activity. Explain why each suggested field appears.

## Design and language

- Use `.claude/rules/design.md` for visual guidance and design skill selection.
- Use clear Modern Standard Arabic and RTL layouts. Arabic is the source for the English site under `/en/`.
- Update the corresponding English content alongside Arabic copy and data changes. UI and JavaScript strings live in `data/i18n/ui.en.json` and `data/i18n/js.en.json`. Data translations use `data.en.json` or `universities.en.json` keyed by the exact Arabic. Pages use `content/en/<section>/<slug>.md` with `translated_from`.
- Preserve numbers, dates, conditions, and uncertainty in translation. Keep minimum scores distinct from recommended scores and list status distinct from admission eligibility. Run `pytest tests/test_english.py` and `python scripts/english_leaks.py` when relevant.

## Data and sources

- Verify official lists, deadlines, requirements, scores, and quotes directly with official sources. Record the source and `last_checked` in the data. Place source links beside the claims they support.
- Keep unverified claims in draft data. If information is missing, explain what still needs checking. If official sources disagree, show the discrepancy with both links.
- Keep scholarship eligibility distinct from university admission. Store shared facts in `data/` and editorial copy in `content/`. Reuse those records across features.

## Working in this repo

- Follow the current request. Use `docs/plan.md` for roadmap context. When asked to do the next step, complete the first open step that fits the current direction and mark it done after verification.
- Use `research-wave` for larger university data research and `update-site` when its workflow fits the update. Research and review agents are read-only. Verify their findings in the main session before saving or publishing them.
- Keep `.env` untouched and its contents out of output. Use documented environment variables for configuration.
- Verify changes with relevant tests and browser checks for UI work. Briefly report what changed, how to verify it, and any gaps. Explain a technical decision when it helps me understand the work.
- Update relevant docs when a change makes them inaccurate. See `docs/README.md` for commands and `docs/architecture.md` for the code structure.

## Local commands

Run from the repo root in Windows PowerShell.

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
pytest
python scripts/english_leaks.py
```

## Git and deployment

- Work on a branch. Verify the changes locally, run browser checks for UI work, then commit, push the branch, and open a PR. Share the PR link, CI status, and steps I can follow to test the changes myself. Leave the PR open for my review. I handle the merge to `main` after testing and checking CI. Push changes through the PR workflow and avoid force-pushing.
- Wadih runs on Render at `https://wadihguide.com`. GitHub Actions runs the tests and Render deploys after CI passes. Use `WADIH_SHOW_DRAFTS` for local development only.
- The scheduled site watch reports findings in the GitHub issue «Site check». Review those findings when updating site data.