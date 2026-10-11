# Architecture

How واضح is put together. Why each choice was made lives in [decisions.md](decisions.md).

## Big picture

```
Browser ──request──▶ FastAPI app (app/main.py) ──reads──▶ data/*.json     (facts, settings)
   ▲                        │                            content/**/*.md (page text)
   └──── HTML page ─────────┘ uses templates/ (Jinja2, RTL) + static/ (CSS, JS, fonts, images)
```

Server-rendered pages, no frontend framework. GitHub → Render deploys on push (only after CI passes).

## App (`app/`)
- `main.py`: the FastAPI app. Loads `data/*.json` once at startup with `load_json()` (data changes need a server restart). Exposes `site` (from `data/site.json`) to every template as a Jinja global, plus the `arabic_date` filter (`2026-10-09` → `9 أكتوبر 2026`). Routes: `/`, `/about`, `/grades/{slug}`, `/programs/{slug}`, `/resources/{slug}`, `/universities`, `/universities/{id}`, `/api/universities`, `/robots.txt`, `/sitemap.xml`; unknown pages raise 404 → Arabic `404.html`. `TRACK_STATUS_LABELS` (status → Arabic label) is a Jinja global. `program_slugs()` = programs that have both a `paths.json` entry and `content/programs/<id>.md`. `is_confirmed()` filters news: only items with `source_url` or `owner_confirmed` are shown. `track_status(track)` (Jinja global) gives today's status: واعد follows `waaid()` (latest programs, open/closed computed from dates); an open track with `status_until` closes itself after that date. `program_targets` maps university ids to programs that target them (SDAIA).
- `sort_news()`: publication date, newest first; on the same date opening → deadline → closing → announcement.
- `universities.py`: the explorer. `Explorer` loads `data/universities.json`, `university_names_ar.json`, `countries.json`, and `university_details/*.json` once at startup; `search()` returns sections of rows in three modes (major / name / browse); `normalize()` makes search forgiving (أ/إ/آ, ة/ه, ى/ي, accents, case).
- `content.py`: `load_page(section, slug)` reads `content/<section>/<slug>.md` (frontmatter + Markdown → HTML) on every request, so content edits need no restart. The slug must match `^[a-z0-9-]+$`, so URLs can never reach other files. `list_slugs()` feeds the sitemap.
- `WADIH_SHOW_DRAFTS=1` (local only, never on Render) shows unverified drafts such as the Tuwaiq section.

## Data (`data/`)
- `site.json`: name, descriptor, tagline, `base_url` (the one place to change when the custom domain arrives), description.
- `paths.json` (shown as «البرامج»): each program has `id`, `theme` (world/desert/sea), `photo` (or `null` → drawn scene), optional `logo` (official, self-hosted, with `source_url`/`asset_url`/`retrieved`; shown instead of a photo), names, `provider_ar`, `audience_ar` («لمن؟»), summary, official/apply/universities links, `verified`, optional `facts`, and `tracks` (`status`: open/closed/not_open/invitation/none_open, or `null` only when `for_high_school` is false; `status_source`, `owner_confirmed`, `last_checked`; a status shows only with a source or owner confirmation). Converted tracks also have `id`, `name_en`, `levels_ar`, `for_high_school`, `high_school_ar`, `admission_ar`, `facts`.
- **Fact shape** (decision 025), used in `facts` lists: `id`, `text_ar`, `sources` [{`title`, `url`}], `last_checked`, `academic_year`, `status` (sourced/unverified/conflict/outdated), `owner_reviewed`, `note_ar`. Rendered only through the `fact` macro.
- `waaid_programs.json`: the latest واعد programs (from the Ministry's واعد page), shown in a toggle under the واعد track (`partials/waaid_programs.html`). Add new programs at the top.
- `news.json`: `added` (when we added it; ordering only, never shown), `type` (opening/closing/deadline/announcement), `path_id`, `title_ar`, `source_url`, optional `page` (our own explainer, linked instead of the source), `owner_confirmed`. The homepage shows the newest 3 confirmed items.
- `tests.json`: IELTS, Qudurat, Tahsili.
- `home.json`: homepage text (lead, hero labels).
- `featured_quote.json`: the Tuwaiq quote; renders only when `status` is `verified` (or drafts are shown locally). Video via `youtube_id`.
- Trust rule (decision 028): a sourced fact shows its source link; anything without an official source or owner confirmation is hidden (no stamps on the site). Dates are ISO in data and not shown.

## Templates (`app/templates/`)
- `base.html`: `<html lang="ar" dir="rtl">`, head (description, canonical, Open Graph tags, light-first theme script), header, footer. Blocks: `hero` (full width), `content` (inside `.container`), `after_content` (full-width bands like `partials/tuwaiq.html`), `scripts` (page-only JS such as `video.js`), `title`, `description`.
- The nav links are one Jinja list (`nav_links`) used by the desktop nav, the phone `<details>` menu, and the footer.
- `home.html` (hero with grade buttons → programs → news → Tuwaiq band), `page.html` (Markdown pages, inside `.measure`; `show_tests: true` in frontmatter adds the tests list), `program.html` (program page: header, track comparison table, sourced facts, then the Markdown from `content/programs/`), `about.html`, `404.html`.
- `components.html`: macros `path_steps`, `source_stamp(sources)`, `fact(f, label)`, `next_step`.
- `partials/path-art.html`: SVG macros: `hero_visual` (Tuwaiq escarpment + route + labels) and `scene(theme)` (fallback when a path has no photo).

- `universities.json` (generated by `scripts/extract_universities.py`; never edit by hand), `university_names_ar.json` (our Arabic translations), `countries.json` (Arabic name + whether English is official, from the program's country pages), `university_details/<id>.json` (requirements from each university's official site; schema in `docs/specs/universities-explorer.md`).
- `content/`: `grades/` (grade pages), `programs/` (one page per program), `resources/` (shared resources such as `ielts.md`).
- `data/raw/` (git-ignored): official source files we extract from, e.g. the universities guide PDF.

## Static (`app/static/`)
- `style.css`: design tokens at the top (light default; dark only via `data-theme="dark"`), mobile-first, logical properties (`padding-inline`, never left/right). `.container` = the wide grid (~1240px), `.measure` = the 720px reading column. Tints use `color-mix()` on tokens.
- `fonts.css` + `fonts/`: self-hosted IBM Plex Sans Arabic (400/600/700) and Noto Naskh Arabic (700), OFL.
- `theme.js` (light ↔ dark toggle, saved in `localStorage`), `video.js` (click-to-play: YouTube loads only after a click), `universities.js` (live results in the explorer; the page works without it).
- `img/paths/*-500.jpg|960.jpg` (licensed photos; credits on /about), `img/programs/*-500.png|960.png` (official logos), `img/og-image.png` (share image; regenerate with `scripts/og-image.js` in the browser console), `favicon.svg`.
- After CSS changes, browsers may serve a cached copy: hard-refresh with Ctrl+Shift+R.

## Tests (`tests/`)
- `test_pages.py`: pages load, 404s, slug safety, draft gating, nav, every homepage link works, share tags, robots/sitemap, no third-party requests, light-first theme.
- `test_data.py`: the trust rules as code (e.g. a path can't be `verified` unless every track status has a source; photos need credit and licence; every fact follows decision 025; a conflict needs both sources and a note).
- `test_content.py`: the Markdown loader.
- `test_universities.py`: the extracted lists (الرواد = 30, ranks continuous except documented gaps, notes kept), Arabic names, requirement-file schema, search modes and filters, explorer pages, API, sitemap.

## Scripts and specs
- `scripts/extract_universities.py` (+ `flag_countries.json`, `university_aliases.json`, `list_overrides.json`): rebuilds `data/universities.json` from the PDF in `data/raw/`. Run: `.venv\Scripts\python.exe scripts\extract_universities.py`. `pdfplumber` is dev only.
- `docs/specs/universities-explorer.md`: the explorer spec and the requirements schema.

## Tooling
- `.github/workflows/tests.yml`: runs `pytest` on every push and pull request (CI). Render deploys only after it passes.
- `.claude/settings.json`: a permission rule that blocks Claude from reading `.env`.
- `.claude/launch.json`: starts the dev server in the Claude desktop app's browser pane.
