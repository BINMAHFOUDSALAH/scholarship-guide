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
- `main.py`: the FastAPI app. Loads `data/*.json` once at startup with `load_json()` (data changes need a server restart). Exposes `site` (from `data/site.json`) to every template as a Jinja global, plus the `arabic_date` filter (`2026-10-09` → `9 أكتوبر 2026`). Routes: `/`, `/about`, `/grades/{slug}`, `/robots.txt`, `/sitemap.xml`; unknown pages raise 404 → Arabic `404.html`.
- `sort_news()`: publication date, newest first; on the same date opening → deadline → closing → announcement.
- `content.py`: `load_page(section, slug)` reads `content/<section>/<slug>.md` (frontmatter + Markdown → HTML) on every request, so content edits need no restart. The slug must match `^[a-z0-9-]+$`, so URLs can never reach other files. `list_slugs()` feeds the sitemap.
- `WADIH_SHOW_DRAFTS=1` (local only, never on Render) shows unverified drafts such as the Tuwaiq section.

## Data (`data/`)
- `site.json`: name, descriptor, tagline, `base_url` (the one place to change when the custom domain arrives), description.
- `paths.json`: each path has `id`, `theme` (world/desert/sea), `photo` (file, alt, credit, licence, source page), names, `provider_ar`, `audience_ar` («لمن؟»), summary, official/apply/universities links, `verified`, and `tracks` (`status`: open/closed/not_open/invitation, `status_source`, `last_checked`).
- `news.json`: `date`, `type` (opening/closing/deadline/announcement), `path_id`, `title_ar`, `source_url`. The homepage shows the newest 3.
- `tests.json`: IELTS, Qudurat, Tahsili.
- `home.json`: homepage text (lead, hero labels, starting points, journey steps, trust points).
- `featured_quote.json`: the Tuwaiq quote; renders only when `status` is `verified` (or drafts are shown locally). Video via `youtube_id`.
- Trust rule: anything with `verified: false`, `status_source: null`, `source_url: null`, or `status: draft` renders with the "غير مؤكد" stamp or stays hidden. Dates are ISO in data.

## Templates (`app/templates/`)
- `base.html`: `<html lang="ar" dir="rtl">`, head (description, canonical, Open Graph tags, light-first theme script), header, footer. Blocks: `hero` (full width), `content` (inside `.container`), `after_content` (full-width bands like `partials/tuwaiq.html`), `scripts` (page-only JS such as `video.js`), `title`, `description`.
- The nav links are one Jinja list (`nav_links`) used by the desktop nav, the phone `<details>` menu, and the footer.
- `home.html`, `page.html` (Markdown pages, inside `.measure`), `about.html`, `404.html`.
- `components.html`: macros `path_steps`, `source_stamp`, `unverified_stamp`, `next_step`.
- `partials/path-art.html`: SVG macros: `hero_visual` (Tuwaiq escarpment + route + labels) and `scene(theme)` (fallback when a path has no photo).

## Static (`app/static/`)
- `style.css`: design tokens at the top (light default; dark only via `data-theme="dark"`), mobile-first, logical properties (`padding-inline`, never left/right). `.container` = the wide grid (~1240px), `.measure` = the 720px reading column. Tints use `color-mix()` on tokens.
- `fonts.css` + `fonts/`: self-hosted IBM Plex Sans Arabic (400/600/700) and Noto Naskh Arabic (700), OFL.
- `theme.js` (light ↔ dark toggle, saved in `localStorage`), `video.js` (click-to-play: YouTube loads only after a click).
- `img/paths/*-500.jpg|960.jpg` (licensed photos), `img/og-image.png` (share image; regenerate with `scripts/og-image.js` in the browser console), `favicon.svg`.
- After CSS changes, browsers may serve a cached copy: hard-refresh with Ctrl+Shift+R.

## Tests (`tests/`)
- `test_pages.py`: pages load, 404s, slug safety, draft gating, nav, every homepage link works, share tags, robots/sitemap, no third-party requests, light-first theme.
- `test_data.py`: the trust rules as code (e.g. a path can't be `verified` unless every track status has a source; photos need credit and licence).
- `test_content.py`: the Markdown loader.

## Tooling
- `.github/workflows/tests.yml`: runs `pytest` on every push and pull request (CI). Render deploys only after it passes.
- `.claude/settings.json`: a permission rule that blocks Claude from reading `.env`.
- `.claude/launch.json`: starts the dev server in the Claude desktop app's browser pane.
