# واضح (Wadih)

**مستقبلك بعد الثانوية، بوضوح.** Your future after high school, clearly.

A free, Arabic-first guide for Saudi high school students: the paths open to them after graduation (government scholarship, Aramco, KAUST, and more), what each one requires, and what to do next.

- **Help first:** no account, no email, no data collected.
- **Verified:** every official fact shows its source and the date it was last checked. Anything unconfirmed is labeled "غير مؤكد".
- **Independent:** this is a student guide. It is not the Ministry of Education, not Safeer, and not affiliated with Aramco or KAUST.

**Live site:** https://wadih-mqni.onrender.com (free hosting, so the first visit after a quiet period can take up to a minute to wake up)

> Status: in development. See [docs/roadmap.md](docs/roadmap.md).

## Run locally (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000.

## Tests

```powershell
pip install -r requirements-dev.txt
pytest
```

The tests check that pages load and also enforce the trust rules on the data (for example, nothing can be marked verified without a source).

## How changes go live

Change → check locally → `pytest` → commit and push to `main` → Render rebuilds the live site automatically (about 2 minutes).

## Tech

Python, FastAPI, Jinja2 server-rendered HTML, plain CSS (RTL, mobile-first), content in Markdown and JSON. The reasons for each choice are in [docs/decisions.md](docs/decisions.md).
