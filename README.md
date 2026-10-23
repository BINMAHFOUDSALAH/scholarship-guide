# واضح (Wadih)

**مستقبلك بعد الثانوية، بوضوح.** Your future after high school, clearly.

A free, Arabic-first guide for Saudi high school students: the programs open to them after graduation (the government scholarship and its tracks, SDAIA, KAUST, Aramco), what each one requires, which universities are on the official lists, and what to do next.

- **Help first:** no account, no email, no trackers, no personal data collected.
- **Official sources only:** every fact on the site links to the official page it came from. Anything without an official source is left out, not guessed.
- **Independent:** a student guide. Not the Ministry of Education, not Safeer, and not affiliated with Aramco, KAUST or SDAIA.

**Live site:** https://wadihguide.com

> Status: in development, Launch 1 planned for December 2026. See [docs/roadmap.md](docs/roadmap.md).

## Run locally (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000.

## Tests

```powershell
pytest
```

Besides checking that pages load, the tests enforce the trust rules on the data: every fact needs an official `https` source, research files must follow their schema, colours must pass contrast checks, and pages may not load anything from third parties.

## How changes go live

Change → `pytest` → push → GitHub Actions runs the tests → Render deploys `main` only if they pass.

## Where things are

| Path | What |
|---|---|
| `app/` | FastAPI app, Jinja2 templates, CSS/JS (RTL, mobile-first) |
| `data/` | Official facts as JSON, each with its source (programs, universities, requirements) |
| `content/` | Page text in Markdown (grades, programs, test guides) |
| `scripts/` | Tools: rebuild the universities list from the Ministry's PDF, the stale-facts report, quote and source checkers, a browser check of the explorer |
| `tests/` | pytest |
| `docs/` | Roadmap, decisions (why), architecture (how), specs, research notes |
| `CLAUDE.md`, `.claude/` | Instructions, agents and skills for Claude Code, which helps build this project |

## Tech

Python, FastAPI, Jinja2 server-rendered HTML, plain CSS and a little JavaScript, content in Markdown and JSON, hosted on Render. The reasons for each choice are in [docs/decisions.md](docs/decisions.md).
