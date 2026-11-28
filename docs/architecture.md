# Wadih architecture

Wadih is a FastAPI app that renders HTML with Jinja. Published facts live in JSON under `data/`, editorial content lives in Markdown under `content/`, and the browser uses CSS and JavaScript from `app/static/`.

See [`CLAUDE.md`](../CLAUDE.md) for project workflow, [design guidance](../.claude/rules/design.md) for visual decisions, and [the roadmap](plan.md) for upcoming work.

## Where features live

| Area | Start here |
| --- | --- |
| Routes and page rendering | `app/main.py`, `app/templates/` |
| The question «أريد دراسة … في …» and its answer | `app/answer.py`, `app/templates/partials/ask.html`, `app/templates/partials/answer.html`, `app/static/ask.js` |
| University Finder and profiles | `app/universities.py`, `app/static/universities.js` |
| «قارن» (comparing universities) | `app/compare.py`, `app/templates/compare.html`, `app/static/compare.js` |
| Site search and guide retrieval | `app/search.py` |
| Saved choices and calendar export | `app/plan.py`, `app/static/mylist.js` |
| «جرّب قبل أن تقرر» | `app/exploration.py`, `data/exploration.json`, `app/static/explore.js` |
| Markdown pages and translations | `app/content.py`, `app/i18n.py`, `content/`, `data/i18n/` |
| Shared presentation | `app/templates/components.html`, `app/static/style.css`, `app/static/fonts.css` |

## Published data

- `data/paths.json` defines scholarship programs and tracks, including their application stages and statuses. `data/waaid_programs.json` holds individual واعد announcements.
- `data/universities.json` is generated from the official guide by `scripts/extract_universities.py`. University-level requirements, fees, and deadlines live in `data/university_details/`. See [the Finder spec](specs/universities-explorer.md) for the schema.
- Keep scholarship list membership distinct from university admission. Keep minimum, recommended, per-skill, and course-specific scores distinct. Preserve source links and verification metadata in the records that support each claim.
- Draft records can be previewed locally with `WADIH_SHOW_DRAFTS=1`. Published pages and search use the published data.

## How updates reach the site

- The app loads its JSON data and builds its search indexes at startup. Restart the local server to see data changes and refresh the search index.
- `app/content.py` reads Markdown pages on request. A guide edit can appear on its page before the search index has refreshed.
- `/en/` uses the same routes with English translations. UI translations live in `data/i18n/`, and translated Markdown pages live in `content/en/`.
- «خطتي» currently stores saved items and progress in the browser. `app/plan.py` validates the submitted plan and builds its display and calendar file.

## Search and وضّاح

`app/search.py` builds an in-memory SQLite FTS5 index from published guides and facts. `retrieve()` provides an existing way to find passages for explanations. University lists, admission requirements, and deadlines can be looked up from the records already used by the Finder.

`app/answer.py` turns a typed question into a major and a country, and a search result into an answer: the universities grouped by why they appear (the track's list), each with the university's own admission facts and their sources. The homepage, the Finder, and `/api/answer` share it; the API returns plain data with the actions a student can take on each university (open, save to «خطتي», compare), so وضّاح can use the same records and actions. `/compare?u=a,b,c` draws a comparison from its address: first «ترتيب الجامعة حسب المجال» (every track, one row per field any of the universities is listed in, each rank with its page in the Ministry's guide, from the same listings as the university pages; «غير مدرجة في هذا المجال» when the guide doesn't list it, «الترتيب غير متوفر» when our data has no rank), then each value as its answer and its condition, with the official sources behind «عرض المصادر» (once per row when every university's value comes from the same document). A university without a logo file shows its initials in the same tile. Scholarship programs are found by name too: `program_entries()` in `app/main.py` feeds the search box's «برامج الابتعاث» group from each program's names and `aliases` in `data/paths.json`, and a program's name submitted as it is opens its page.

The homepage currently shows a sourced example of what وضّاح could do. Google sign-in and the live agent are the next milestone after the redesign. Keep implementation decisions in [the agent spec](specs/agent.md) and [the accounts spec](specs/accounts.md).

## Verification and deployment

- GitHub Actions runs `pytest`. See [the docs index](README.md) for browser checks and data maintenance commands. Run `python scripts/english_leaks.py` when changing translated content.
- `scripts/watch.py`, `scripts/check_sources.py`, and `scripts/stale_facts.py` help identify source changes and records that need review.
- Some tests check specific layouts or visual choices from earlier versions. During a redesign, review those assertions when the intended behavior changes. Keep coverage for data accuracy, accessibility, translations, and working student flows.
- Render hosts the live site. Follow the PR workflow in `CLAUDE.md`. The owner tests and merges changes to `main`.