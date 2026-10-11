# Learning Log

What we built in واضح, why, how it works, and how to talk about it. Updated after each meaningful feature.

**Honesty rules for this log**
- It records what was actually built and tested, nothing more.
- **"Who did what"** separates the owner's work (decisions, verification, research, design direction, testing by hand) from what Claude implemented.
- **"Understood?"** stays *not yet checked* until the owner has answered a check question or done an exercise on it. Being explained to doesn't count.

**The overall interview story (true today):** "I'm building and running a live, Arabic-first guidance site for Saudi high school students. I set the product rules (verified facts only, no invented data, privacy for minors), made the design and architecture decisions with an AI pair programmer, verified the official information myself, and shipped it with automated tests and CI. AI wrote most of the code; my job was product direction, decisions, verification, and making sure it's correct."

---

## 1. First web app: FastAPI + virtual environment
**Built / why:** A Python web server (FastAPI) with routes (`/`, `/about`), in an isolated environment (`.venv`) with pinned packages (`requirements.txt`). It's the base everything else (APIs, AI) will sit on.
**Key concepts:**
- request → route → function → response
- status codes (200, 404)
- a virtual environment = a private package box per project
- pinned versions = the same behavior everywhere
**Decisions:** FastAPI over Django or a static site generator, because one language (Python) also serves the future AI work.
**Tested:** opened the routes locally; later covered by automated tests.
**Limits:** a server only you can see (127.0.0.1) until it's deployed.
**Interview pitch:** "A FastAPI app with server-rendered pages; I chose it because the AI features later need a Python backend anyway."
**Who did what:** Owner chose the stack direction (Python/FastAPI) and approved installs. Claude wrote the code.
**Understood?** Not yet checked.

## 2. Templates, RTL, and the design system
**Built / why:** Jinja2 templates (`base.html` + pages), an Arabic right-to-left layout, design tokens (colors and sizes as CSS variables), a light/dark theme, and self-hosted Arabic fonts.
**Key concepts:**
- template inheritance (one layout, many pages)
- `dir="rtl"`
- CSS logical properties (`padding-inline`)
- design tokens
- contrast ratio (WCAG: at least 4.5:1)
- progressive enhancement (the site works without JavaScript)
**Decisions:**
- server-rendered HTML instead of React
- self-hosted fonts instead of Google Fonts (privacy)
- light mode first (owner's choice)
- Plex Bold headlines with Naskh accents
**Tested:** measured contrast with code in the browser; checked layouts at 320, 375, 768, 1280, and 1440px in both themes.
**Limits:** `color-mix()` and `text-wrap: balance` need modern browsers; older ones fall back to plainer looks.
**Interview pitch:** "An accessible RTL design system: tokens, a separately designed dark mode, contrast measured rather than eyeballed."
**Who did what:** Owner set the brand (name واضح, palette, Tuwaiq logo concept, light-first), wrote the redesign brief, and **found a real layout bug on tablet by testing**. Claude implemented and measured.
**Understood?** Not yet checked.

## 3. Content separate from code + trust rules as code
**Built / why:** Facts live in `data/*.json`, page text in `content/*.md`, and templates only display them. Every fact has a source and a check date. Unverified items show "غير مؤكد" or stay hidden (`status: draft`, `WADIH_SHOW_DRAFTS`).
**Key concepts:**
- separation of concerns
- a single source of truth
- feature flags through environment variables
- data validation
**Decisions:**
- JSON + Markdown files in git instead of a database for now (one editor, free history)
- research → owner verifies → publish (decision 013)
**Tested:** tests that fail if, for example, a path is marked verified without sources (I broke this on purpose once to prove the test catches it).
**Limits:** data changes need a server restart; there's no formal schema (Pydantic) yet (planned for Stage 2).
**Interview pitch:** "I encoded the product's trust rules as automated tests, so the site can't claim something is verified without a source."
**Who did what:** Owner defined the trust rules (never invent facts, "غير مؤكد"), **verified official facts from primary sources** (application platform قبول, the current universities list, track statuses from the program's official account), and made the policy calls. Claude researched drafts and wrote the code and tests.
**Understood?** Not yet checked.

## 4. Markdown pages and URL safety
**Built / why:** Grade pages ("what to do this year") written in Markdown with frontmatter, served at `/grades/{slug}`, with a friendly Arabic 404 page.
**Key concepts:**
- path parameters
- frontmatter
- **never trust URL input to build file paths** (the slug must match `^[a-z0-9-]+$`, which blocks `../../.env`)
**Decisions:** pages are read on every request (no restart needed for edits), which is fine at this size.
**Tested:** tests for valid pages, unknown pages, and attack-style slugs (`..%2F..%2F.env` → 404).
**Limits:** the grade pages are drafts written by Claude, still awaiting the owner's review.
**Interview pitch:** "User input is validated before it touches the file system; I have a test for a path-traversal attempt."
**Who did what:** Owner asked for grade-based guidance and the hidden "ابدأ من هنا" (start here) reveal. Claude implemented and tested.
**Understood?** Not yet checked.

## 5. Automated tests (51)
**Built / why:** `pytest` tests for pages, data rules, content loading, links, SEO tags, and privacy (no third-party requests). They let us change things without fear.
**Key concepts:**
- unit vs page tests
- `TestClient`
- `monkeypatch`
- "a test must be able to fail" (prove it by breaking the code on purpose)
- tests can be wrong too
**Decisions:** test the promises (trust, privacy, working links), not just "does it load".
**Tested:** the suite itself, run before every commit. One test was wrong once (it flagged our own URLs as third-party), and we fixed the test, not the site.
**Limits:** tests don't cover how the page looks; that's checked by hand in the browser.
**Interview pitch:** "51 tests that encode the product's promises, run automatically in CI before every deploy."
**Who did what:** Owner approved the test tooling. Claude wrote the tests.
**Understood?** Not yet checked.

## 6. Deployment (Render)
**Built / why:** The site is live at https://wadih-mqni.onrender.com. Render builds from GitHub and runs `uvicorn ... --host 0.0.0.0 --port $PORT`.
**Key concepts:**
- hosting
- build vs start commands
- `0.0.0.0` vs `127.0.0.1`
- `$PORT`
- continuous deployment (push = deploy)
- regions (close to the users, not the developer)
**Decisions:**
- the free tier (it sleeps when idle)
- the Frankfurt region (closest to Saudi users)
- a custom domain later (`base_url` is one setting)
**Tested:** checked every page and file on the live site after each deploy.
**Limits:** the slow first visit after the site sleeps; the server's Python version (3.14) differs from local (3.13) and isn't pinned yet.
**Interview pitch:** "Deployed on Render with continuous deployment from GitHub, gated by CI."
**Who did what:** Owner **created the Render account, configured and launched the service** (and switched off the paid plan that Render pre-selected). Claude gave the settings and verified the live site.
**Understood?** Not yet checked.

## 7. Search engines and share previews
**Built / why:** Meta descriptions, canonical URLs, Open Graph tags plus a 1200×630 share image (for WhatsApp/X), `robots.txt`, and `sitemap.xml`.
**Key concepts:**
- how Google discovers pages
- Open Graph
- why pages behind a login can't be indexed
**Decisions:** the share image was drawn in the browser, so Arabic letters join correctly.
**Tested:** tests for the tags, robots, and sitemap; checked the live URLs.
**Limits:** WhatsApp caches old previews for a while.
**Interview pitch:** "SEO and sharing basics, with one setting to change when the domain arrives."
**Who did what:** Owner chose these from a list of options. Claude implemented.
**Understood?** Not yet checked.

## 8. Homepage redesign with real, licensed photos
**Built / why:** A wide editorial layout:
- a hero with the Tuwaiq route drawing
- "where do I start" starting points
- compact news (sorted by date, then status)
- facts-first path rows with «لمن؟» (who it's for)
- a 5-step journey
- licensed photos with credits
- a click-to-play video (privacy: YouTube loads only after a click)
**Key concepts:**
- image licences (public domain, CC BY, CC BY-SA)
- responsive images (`srcset`)
- the "facade" pattern for embeds
- why not to use logos (trademarks; the state emblem)
**Decisions:**
- photos of places, not logos
- no search box until there's something to search
- the honest headline
**Tested:**
- pytest, including a test that opens every link on the homepage
- browser checks at 1440×900 and 390×844 in both themes
- contrast measured (lowest 5.4:1)
**Limits:** the Tuwaiq section stays hidden until the owner confirms the video's wording.
**Interview pitch:** "I redesigned for clarity: facts first, real sources, accessible contrast, and privacy-preserving embeds."
**Who did what:** Owner drove the design direction (briefs, feedback, which program images to use, the video request) and **found the College Preparatory Center photo**. Claude checked licences, implemented, and verified.
**Understood?** Not yet checked.

## 9. CI gate and `.env` lock (2026-10-10)
**Built / why:** GitHub Actions runs the tests on every push (`.github/workflows/tests.yml`); Render deploys only after they pass. A permission rule blocks Claude from reading `.env` (where future API keys will live).
**Key concepts:**
- CI (continuous integration)
- a "gate" before deployment
- advice (CLAUDE.md) vs enforcement (permission rules, hooks)
- least privilege
**Decisions:** chose CI and the `.env` lock first; deferred the stale-facts test and the weekly link checker.
**Tested:** pytest locally. **The CI run is proven only after the first push**; the `.env` rule was intentionally not tested by trying to read `.env`.
**Limits:** the `.env` rule blocks Claude's file tools and commands like `cat`, but not a script that opens files itself (full protection would need Claude Code's sandbox).
**Interview pitch:** "Broken code can't reach production: CI must pass before Render deploys. Secrets are protected from the AI assistant by an enforced rule, not just an instruction."
**Who did what:** Owner chose which automations to adopt after asking for plain explanations and the trade-offs. Claude implemented.
**Understood?** Not yet checked.
