# Design Decisions

A short record of each design choice: what we chose, what else we considered, and why.
Newest entries go at the bottom. When a decision changes, add a new entry instead of editing the old one.

---

## 001 — Python + FastAPI for the backend
**Date:** 2026-10-09
**Decision:** Build the site with Python and FastAPI.
**Alternatives:** A static site generator (e.g. Hugo, MkDocs); Node.js; Django.
**Why:** One language for both the website and the future AI work (RAG, agents), which is mostly Python. FastAPI is small, modern, and common in AI engineering. A static site generator would be simpler for a pure guide, but we would need to add a backend later for the chatbot anyway.

## 002 — Server-rendered HTML (Jinja2), no React
**Date:** 2026-10-09
**Decision:** The server builds finished HTML pages with Jinja2 templates.
**Alternatives:** A separate React/Next.js frontend talking to a JSON API.
**Why:** Fast on phones, easy for search engines to read, and only one language to learn. We give up app-like interactivity, which v1 does not need. Small pieces of JavaScript can be added later where they help.

## 003 — Content in Markdown, facts in JSON, no database yet
**Date:** 2026-10-09
**Decision:** Pages are Markdown files with a frontmatter header (`title`, `status`, `sources`, `last_checked`). Facts that change every year (requirements, universities) are JSON files validated by Pydantic models. The active scholarship year is a setting in `data/settings.json`.
**Alternatives:** A database (SQLite/Postgres) from day one; a headless CMS.
**Why:** There is one editor, and files in git give free history and review of every change. Validation makes the app refuse to start if a fact is missing its source or date. A database will be added when there is a real need (search index and chat logs in the RAG stage).

## 004 — One Arabic site with English names inline
**Date:** 2026-10-09
**Decision:** The whole site is Arabic and right-to-left. Official names (universities, tests, majors) are also shown in English where useful, e.g. هندسة الحاسب (Computer Engineering). Data records store both `name_ar` and `name_en`.
**Alternatives:** A full English copy of every page (`/ar` and `/en`).
**Why:** Students need the English names to search and apply, but a full English site would double the writing and verification work, and a stale translation could show wrong official information.

## 005 — Every page has a verification status
**Date:** 2026-10-09
**Decision:** Every content page has `status: draft` or `status: verified`. Draft pages show "غير مؤكد". Claude may draft general explanations; official facts are only added by the maintainer, with a source and a check date.
**Alternatives:** No status; trusting all content equally.
**Why:** It makes trust visible to students, and the future chatbot will be allowed to use only verified pages.

## 006 — System fonts instead of a downloaded web font
**Date:** 2026-10-09
**Decision:** Use the Arabic font already on the visitor's device (`system-ui`, Segoe UI, Noto Sans Arabic…).
**Alternatives:** A Google Font such as IBM Plex Sans Arabic or Tajawal.
**Why:** Pages load faster on slow mobile data, and no request is sent to a third party (privacy). The cost is that the site looks slightly different on iPhone, Android, and Windows. We can revisit this at launch if the design needs one consistent look.
**Status:** Superseded by 010.

## 007 — Name: واضح, a broad brand for all high school students
**Date:** 2026-10-09
**Decision:** The site is called **واضح** (Wadih, "clear"), with the tagline "مستقبلك بعد الثانوية، بوضوح". It serves all Saudi high school students, not only scholarship applicants. The name, descriptor, and tagline live in `data/site.json`.
**Alternatives:** درب (Darb, "path"), زاد (Zad, "provisions"), سهيل (Suhail, a navigation star); a scholarship-only name.
**Why:** The name states the differentiator. Similar platforms feel complicated and push accounts or payments; this one promises clarity. It is an everyday word, so it is always shown with a descriptor to be findable in search. The domain and existing brands must be checked before launch.

## 008 — Paths with shared resources
**Date:** 2026-10-09
**Decision:** Content is organized around **paths** (government scholarship, Aramco, KAUST, more later), each with its own requirements, steps, and sources. **Resources** (IELTS, SAT, Calculus, Khan Academy) are written once and linked from every path that needs them (many-to-many).
**Alternatives:** Topic sections; copying resources into each path.
**Why:** A copied IELTS page would be written and kept up to date three times. Linking keeps one source of truth, and it is the same structure a database would use later. Launch ships one fully verified path; the rest are added one at a time.

## 009 — Visual direction: "Route + source stamps"
**Date:** 2026-10-09
**Decision:** An ivory-first editorial look with forest-green text, a thin path line as the signature motif, footnote-style source stamps next to facts, a visible "غير مؤكد" stamp, lime used only for "الخطوة التالية" (the next step), and a separately designed dark mode.
**Alternatives:** Dark premium as the main look (too close to RISALA's dark green and gold); a plain app-like UI; a night-sky "Suhail" theme.
**Why:** It makes trust visible (no competitor shows sources this way), gives color a meaning, and avoids the generic startup look: no gradients, card grids, or stock photos. Lime is only a highlight behind dark text, because lime text fails contrast standards.

## 010 — Self-hosted fonts
**Date:** 2026-10-09
**Decision:** IBM Plex Sans Arabic (body) and Noto Naskh Arabic (headings), both under the SIL Open Font License, served from `app/static/fonts/`. Each font is split into Arabic and Latin files, loaded by `unicode-range`. About 200 KB in total.
**Alternatives:** System fonts (006); loading the same fonts from Google Fonts.
**Why:** Typography is the main part of a premium, recognizable identity. Self-hosting keeps 006's privacy benefit: visitors never contact a third party.

## 011 — Mount Tuwaiq section rules
**Date:** 2026-10-09
**Decision:** A homepage section below the main resources with a Mount Tuwaiq photo, the Arabic quote, and a play button that **links out** to the original video. Its data lives in `data/featured_quote.json` and it renders only when `status` is `verified`.
**Alternatives:** An embedded YouTube player; a photo of the Crown Prince; quoting from memory.
**Why:** An embed loads third-party trackers. A portrait on an unofficial site could suggest government endorsement. Famous quotes are often misquoted, so the exact wording, date, and video come from an official source checked by the owner. The photo must be freely licensed and credited.

## 012 — Logo: the Mount Tuwaiq cliff (superseded by 036)
**Date:** 2026-10-09
**Decision:** The logo is a long ramp rising to a sharp cliff face, Mount Tuwaiq's escarpment, with the cliff in lime and two thin rock-layer lines. It is drawn as inline SVG in the header, with a simplified version as `app/static/favicon.svg`. This is the one allowed use of lime outside "الخطوة التالية" (the next step): the lit cliff is "the side you climb."
**Alternatives:** A generic pointed peak (closer to the first AI concept image, but a very common logo shape); the earlier abstract path-line mark; a cliff combined with a path line.
**Why:** The Tuwaiq shape is distinctive and true to the real mountain, it links the brand to the Tuwaiq section without flags, and SVG keeps it sharp, theme-aware, and under 1 KB. The AI concept image was only a reference and is not used directly.

## 013 — Content workflow: research → verify → publish
**Date:** 2026-10-09
**Decision:** Claude may research official facts (requirements, dates, programs), but only from official sources, with a link for each fact, recorded in `docs/research/`. Everything stays `draft` / "غير مؤكد" until the owner checks the source and marks it verified. Conflicting sources are recorded, never averaged or guessed.
**Alternatives:** The owner researches everything alone (too slow for 5 h/week); Claude writes facts directly onto pages (risk of confident mistakes).
**Why:** It splits the work: Claude does the searching and organizing, and the owner, who has been through the process, does the judging. Third-party sites already disagree (e.g. a minimum GPA of 85% vs 90% vs 95% for Arruaad), which shows why only official sources count.

## 014 — Accounts for the guided start (guides stay open)
**Date:** 2026-10-09
**Decision:** All guides and path pages stay readable without an account. The **guided start** (questions → recommended paths → personal plan with progress) **requires an account**. Accounts store the minimum: login details plus the guided-start answers (grade, school track, goal, interests). Never national ID, GPA, test scores, or passport. Shipped in two launches: Launch 1 = public guides (no accounts); Launch 2 = accounts + guided start.
**Alternatives:** Progress saved on the device only, no accounts (recommended by Claude: zero personal data, keeps the "no account" promise); optional accounts only for saving; accounts for the whole site.
**Why:** The owner wants saved progress per student and to learn real backend skills (database, authentication, security). Trade-offs accepted: the footer promise changes to "guides need no signup"; most users are minors, so a privacy policy, data deletion, and a review of Saudi PDPL obligations (including consent for under-18s) are required before Launch 2; a login wall in front of the guided start is what competitors do, so the guides must stay genuinely useful without it.

## 015 — Login like a normal website: email or Google; email alerts; visitor counting
**Date:** 2026-10-09
**Decision:**
- **Sign-in options:** email + password, or "Continue with Google" (OAuth / OpenID Connect).
- **What's open vs. behind login:** browsing stays open (guides, path pages, universities page). Logging in unlocks personal features: guided start + saved plan (014), saved universities, and **email alerts** per path (e.g. "مسار الرواد opened", a new announcement), sent only to users who opt in.
- **Usage numbers** come from privacy-friendly visitor counting on our own server (page views, popular pages), so no account is needed just to be counted.
**Alternatives:** Login for the universities page or the whole site; alerts without accounts (email-only subscription).
**Why:** The owner wants users, emails, and data, plus real-time alerts. Pages behind a login can't be indexed by Google, and students find guides through search, so public pages stay public. Google sign-in means fewer passwords to store, and it's a key skill (OAuth). Costs accepted: an email-sending service (free tier, ask before signing up), unsubscribe links, a privacy policy, PDPL obligations (users are mostly minors), and a Google Cloud project the owner creates.

## 016 — Universities explorer for the Custodian scholarship; SAT info per university
**Date:** 2026-10-09
**Decision:** A dedicated, public, interactive page: type a university name → see its rank for مسار الرواد and مسار إمداد and its rank per field/major, all from the official MoE guide (PDF). Data is extracted by a reusable script into `data/universities.json` (re-run when the new edition comes out, expected Dec 2026 / Jan 2027) and spot-checked by the owner. No logos in version 1 (trademarks, hundreds of files to maintain). SAT is removed from the homepage; whether a university requires SAT is shown per university, each with its own source, starting with the Arruaad top 30. Each path gets its own subtle visual theme based on **place**, never on another organization's logo or branding.
**Alternatives:** Linking only to the PDF; typing the data by hand; showing logos; keeping SAT on the homepage.
**Why:** It is the most useful free tool for the biggest audience, and no competitor offers it openly. A script makes the yearly update repeatable. Not every university needs SAT, so pushing it to everyone misleads students.

## 017 — Hosting: Render free tier, Frankfurt, deploy on every push
**Date:** 2026-10-09
**Decision:** The site runs on Render as a Python web service (free instance) in the Frankfurt region, at https://wadih-mqni.onrender.com. Render builds from GitHub `main` (`pip install -r requirements.txt`) and starts `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Every push to `main` redeploys automatically. No environment variables, so drafts stay hidden.
**Alternatives:** Railway, Fly.io, Koyeb (similar platforms); static hosts like GitHub Pages or Netlify (can't run Python); AWS/GCP (complex, easy to overspend); a self-managed VPS (more maintenance).
**Why:** Free, simple, runs our FastAPI backend, and offers Postgres later for accounts. Frankfurt is the closest region to users in Saudi Arabia, even though the owner is currently in the US; the region can't be changed without recreating the service. Trade-offs: free instances sleep after ~15 minutes idle (slow first visit), and the server's Python version (3.14) differs from local (3.13), to be pinned later.

## 018 — Homepage with character: hero, panels, per-path place themes
**Date:** 2026-10-09
**Decision:** The homepage opens with a hero: kicker, big tagline, and a **"ابدأ من هنا"** button (a native `<details>`) that reveals the grade question only when the student asks for it, plus a full-width Mount Tuwaiq horizon drawn in SVG. Sections get editorial labels (٠١، ٠٢، ٠٣). News and tests sit in **panels** (one raised sheet per section); each path is a wide stacked panel with a small illustrated **place scene** and its own accent: world/route for the scholarship (green), dunes for Aramco (amber), Red Sea waves for KAUST (sea teal). News is sorted by publication date, then by status (opening → deadline → closing → announcement), with colored status chips.
**Alternatives:** Keep the plain ruled lists; accent colors only; real photos per path; show the grade question immediately.
**Why:** The owner found the page dry. Panels group information so it scans faster, and place scenes give each path a recognizable identity without logos or brand colors. Hiding the grade question behind one clear action keeps the first screen calm. `<details>` works without JavaScript and with screen readers. Colors are mixed from tokens (`color-mix`), so every tint follows light/dark mode automatically; all text contrast measured ≥ 5:1. Panels are allowed; repetitive grids of identical cards still are not.

## 019 — Click-to-play video (updates decision 011)
**Date:** 2026-10-09
**Decision:** The Tuwaiq band shows the video **on the homepage** as a click-to-play box: our own artwork and a play button. Nothing is requested from YouTube until the student clicks; then `app/static/video.js` swaps in the privacy-enhanced `youtube-nocookie.com` player. Without JavaScript it is a normal link. The band stays hidden until the quote and video are verified (`youtube_id` + `source_url`).
**Alternatives:** Link out only (decision 011); a normal YouTube embed that loads on page open.
**Why:** The owner wants the video visible on the homepage. A normal embed loads Google scripts and cookies for every visitor, most of them minors; click-to-play keeps the page free of third-party requests until the student chooses to watch.

## 020 — Real, licensed photos for each path; no program logos
**Date:** 2026-10-09
**Decision:** Each path panel opens with a real photo of the program's place, from Wikimedia Commons, with the licence checked and the credit shown on the photo: Aramco, the College Preparatory Center in Dhahran (public domain, Eagleamn); KAUST, a campus building (CC BY-SA 3.0, juhotski); the Custodian scholarship, Oxford's Radcliffe Camera labeled "صورة توضيحية لجامعة عالمية" (CC BY 4.0, Julian Herzog). Files are self-hosted in `app/static/img/paths/` at 500px and 960px (`srcset`, lazy-loaded). Photo details (file, alt text, credit, licence, source page) live in `paths.json`; a test fails if a photo lacks credit, licence, or source. The drawn SVG scene stays as the fallback for a path without a photo. **No program logos.**
**Alternatives:** The program logos the owner shared; small KAUST/Aramco logos only; keep the drawn scenes.
**Why:** Expert guidance (Nielsen Norman Group) favors meaningful photos of real places over decorative art. The Custodian program's logo contains the Saudi state emblem, whose unofficial use is restricted (royal order 3587, 1440H; 2024 Ministry of Commerce decision on national symbols). Other organizations' logos are trademarks and would make "not affiliated" less credible. Wikimedia only serves certain standard thumbnail widths, so 500px and 960px were used.

## 021 — Share preview and search-engine basics
**Date:** 2026-10-09
**Decision:** Every page has a meta description (from `site.description`, frontmatter `description`, or a page block), a canonical URL, Open Graph/Twitter tags, and a 1200×630 share image (`app/static/img/og-image.png`, drawn in the browser by `scripts/og-image.js` so Arabic shaping is correct). `/robots.txt` allows all and points to `/sitemap.xml`, which lists the home, about, and every grade page found in `content/grades/`. The public address is one setting: `site.base_url`.
**Alternatives:** No share preview (bare links on WhatsApp/X); generating the image with an image library (would need an install, and many tools don't join Arabic letters).
**Why:** Students share links mostly via WhatsApp and X, and find guides through Google. When we buy a domain, changing `base_url` updates every canonical, share, and sitemap URL at once.

## 022 — Light mode first, two-state theme toggle (updates 4b.2)
**Date:** 2026-10-09
**Decision:** Every visitor starts in light mode. Dark mode applies only when chosen with the toggle (فاتح ↔ داكن), saved in `localStorage`; the browser's theme color follows. The automatic `prefers-color-scheme` switch was removed.
**Alternatives:** Follow the device setting (the previous behavior, and the usual accessibility recommendation); three states (system/light/dark).
**Why:** The owner's choice: the ivory editorial look is the brand's main presentation. Trade-off accepted: someone whose phone is in dark mode sees light first and must press the toggle once (then it's remembered).

## 023 — Wide editorial redesign of the homepage, header, and footer
**Date:** 2026-10-09
**Decision:**
- **Grid:** the page grid is ~1240px (`.container`); reading pages keep a 720px column (`.measure`).
- **Typography:** IBM Plex Sans Arabic Bold for headlines and section titles; Noto Naskh only for editorial accents (the واضح wordmark, the Tuwaiq quote, the footer brand).
- **Palette (owner's brief):** ivory `#F6F4EE`, charcoal text `#101713`, forest headings/links `#184B3A`, lime `#D8ED9B`. Lime is now used sparingly for primary/selected states, progress (current journey step), "open now" status, and small graphic accents, never as small text (updates 009).
- **Header:** a bigger wordmark, a 4-link nav, and on phones a `<details>` menu (no JavaScript needed).
- **Homepage:** a two-column hero with a signature drawing (the Tuwaiq escarpment, a route to a lime waypoint, 3 step labels) replacing the full-width mountain divider; «من أين تبدأ؟» starting points; compact news (newest 3); facts-first path rows (provider, «لمن؟», tracks with status, last review date, official links) with a smaller photo; a 5-step application journey; tests; the Tuwaiq band; «كيف نعمل». The general text lives in `data/home.json`.
- **Footer:** 3 columns.
- **No search button yet:** it comes with the universities explorer, where there is something to search.
**Alternatives:** Keep the 720px single column; a header search box now; Plex everywhere or Naskh everywhere.
**Why:** The narrow column made the desktop page feel empty. Facts first answers what students came for; numbered starting points and a journey give clear next steps (NN/g: clear starting points for the main tasks). Every link goes to a real page or section, and a test checks this.

## 024 — CI gate before deploy; `.env` locked for Claude; leaner CLAUDE.md
**Date:** 2026-10-10
**Decision:**
- **CI gate:** GitHub Actions (`.github/workflows/tests.yml`) runs `pytest` on every push and pull request, and Render's Auto-Deploy is set to "After CI Checks Pass", so a commit with failing tests never reaches the live site.
- **`.env` lock:** `.claude/settings.json` denies Claude's `Read` on `.env` and `.env.*` (except `.env.example`). Per the Claude Code docs, this covers Claude's file tools and recognized shell file commands such as `cat`, but not scripts that open files themselves; full protection would need the sandbox.
- **Leaner CLAUDE.md:** the architecture moved to `docs/architecture.md`; CLAUDE.md keeps the rules, working style, commands, and pointers. Also added: `docs/claude-workflow-guide.md` and `LEARNING_LOG.md`.
**Alternatives:** Keep deploying on every push; a git pre-commit hook (runs only on the owner's machine); a Claude Stop hook; relying on the CLAUDE.md sentence for `.env`; keeping one long CLAUDE.md.
**Why:** Render deployed every push even with failing tests. Anthropic's guidance: use enforced mechanisms for must-always rules, and keep CLAUDE.md short so rules aren't ignored. Deferred: a stale-facts test and a weekly link checker.

## 025 — Verification display: source + date everywhere, «غير مؤكد» only for real gaps (updates 005 and 013)
**Date:** 2026-10-11
**Decision:** Every consequential fact is stored with one shape (`text_ar`, `sources` [title + url], `last_checked`, `academic_year`, `status`, `owner_reviewed`, `note_ar`) and rendered by one macro (`fact` in `components.html`):
- `sourced`: the text, its official source(s), and «آخر مراجعة» (the day the source was actually read).
- `unverified`: the text + «غير مؤكد» (no official source yet, e.g. a status reported from X without the post link).
- `conflict`: the text + «غير مؤكد» + a note; both official sources are linked, and no single answer is published.
- `outdated`: hidden.

Claude may mark a fact `sourced` after reading the official page itself. The owner's review is tracked as `owner_reviewed` (not shown to students). Markdown pages use `status: draft | sourced | verified`; only `draft` shows the draft notice. Programs whose facts are sourced one by one lose the blanket «غير مؤكد» on their name.
**Alternatives:** Keep the old rule (everything stays «غير مؤكد» until the owner checks); two visible levels («تحققنا منه» vs source only).
**Why:** The owner found that blanket stamps on almost everything made the site look unreliable and hid the real gaps. A source link + date is honest about what was checked and when; the stamp now means something specific. «آخر مراجعة» is a manual reading date: the about page says the site doesn't monitor sources automatically.

## 026 — Program identity image: the generic photo is removed; the official logo is pending
**Date:** 2026-10-11
**Decision:** The Oxford photo is removed from the government scholarship (it showed one specific university and was generic). The owner wants an official image. Research found only one official visual: the program's logo on its website, which contains the Saudi state emblem (see `docs/research/custodian-scholarship-2026-27.md` §4). Nothing has been downloaded. Until the owner decides, the row shows the drawn world scene (the existing fallback from decision 020). Aramco and KAUST keep their licensed photos.
**Alternatives:** Use the logo now; a text-only name block; keep the Oxford photo.
**Why:** The owner prefers the program's real identity over a stock-style campus photo. The emblem restriction noted in decision 020 still applies, so the logo needs an explicit owner decision first.

## 027 — «البرامج» on the site; one page per program
**Date:** 2026-10-11
**Decision:** The homepage section and nav item are «البرامج» (anchor `#programs`); the Ministry's tracks keep their official name «مسار …». Code keeps the name `paths` (`data/paths.json`). A program gets its own page at `/programs/<id>` when `content/programs/<id>.md` exists: facts from `paths.json` (a comparison table with the same fields for every track, plus sourced facts) and explanations from the Markdown file. The first is the government scholarship, with all four tracks and the conditional-admission explainer. The homepage row shows only tracks open to high school graduates and links to the page.
**Alternatives:** Keep «المسارات» and explain the difference; put everything on the homepage.
**Why:** On the homepage «المسارات» meant programs, while the Ministry uses «مسار» for tracks inside one program, so students saw two meanings of one word. The conditional-admission rule needs more room than a homepage row, and a page per program is where Aramco and KAUST will go next.

## 028 — No «غير مؤكد» on the site; owner-confirmed or hidden; official logo; programs-first homepage (updates 018, 020, 025, 026)
**Date:** 2026-10-11
**Decision:**
- **No stamps:** «غير مؤكد» and the draft notice are removed everywhere. Something reaches students only if it has an official source or the owner confirmed it (`owner_confirmed: true` on a track status or news item); otherwise it's hidden. Facts with `status: unverified` are hidden; `conflict` facts show both official sources and a note.
- **No dates on screen:** «آخر مراجعة» and news dates are not shown. `last_checked` stays in the data for a future stale-facts check. A news item's date is now `added` (the day we added it, used only for ordering), because the stored date wasn't the announcement date.
- **Official logo:** the King scholarship row and page show the program's official logo (decision 026's pending question), cropped from the program homepage's first slide (`object.moe.gov.sa/.../scs6-638407626472861199.png`): the program logo only, colors and proportions unchanged, self-hosted at `app/static/img/programs/`, on a white plate, with "واضح لا يتبع وزارة التعليم" on the program page and the source on /about.
- **Photo credits** moved from the photos to /about («الصور والشعارات»). The KAUST photo's CC BY-SA licence still requires credit, so it isn't dropped.
- **Homepage:** a short hero with the grade buttons visible (no «ابدأ من هنا» reveal), then «البرامج», then «آخر المستجدات», then the Tuwaiq video. Removed: «من أين تبدأ؟», the 5-step journey (now a list on the grade 12 page), the tests (now on the grade 11 page), «كيف نعمل», and «مجاني وبدون تسجيل».
- **Tuwaiq video** is shown. The quote line is Al Arabiya's own title for its clip («همة السعوديين مثل جبل طويق ولن تنكسر»), attributed «— محمد بن سلمان».
**Alternatives:** Keep source dates and stamps (decision 025); text-only or a building photo instead of the logo; keep the hero reveal.
**Why:** The owner commits to verifying everything that's published, so a visible "unverified" label would only mark mistakes we should fix or hide. Hiding unconfirmed items keeps the "never invent facts" rule. The owner chose the official logo knowing the state-emblem concern noted in decision 020; it's shown only to identify the program, never as endorsement. Programs are the main thing students come for, so they come first.

## 029 — Universities explorer: extracted from the official PDF, searchable by university or major
**Date:** 2026-10-11
**Decision:**
- `scripts/extract_universities.py` (pdfplumber, dev only) reads the 2026–2027 guide into `data/universities.json`: 290 universities, the الرواد list (30), 5 البحث والتطوير field lists, 8 إمداد field lists, every field's majors (Arabic + English, with «درجة الماجستير فقط»), and the notes on listings (master's only, for deaf and hard-of-hearing students, bachelor's only in named majors). Countries come from each entry's flag image (hashed, mapped once by hand). The script refuses to write data if ranks have gaps the PDF doesn't explain, the الرواد list isn't 30, or a flag is unknown.
- PDF problems are recorded, never silently fixed: a hidden entry under another (p74), a numbering jump (R&D ICT 90→100), wrong flags (Groningen, Erasmus, Tilburg), a cut-off major name. We follow what a student sees on the page.
- `/universities`: search by university name or by major, in Arabic or English, with filters (track, field, country, English-speaking country or not). A major shows the 30 الرواد universities (all majors) and its إمداد field's ranked list; the doctorate lists appear only when asked for. Search runs on the server (works without JavaScript); `universities.js` updates results as you type. `/universities/<id>` shows every listing, the field's majors, the language-exception note for non-English-speaking countries, and the requirements researched from the university's own site. `/api/universities` serves the same data.
- Arabic university names are our translation (`data/university_names_ar.json`), always shown with the official English name.
- Requirements (`data/university_details/<id>.json`) come only from each university's official pages, researched by agents in parallel, starting with the 30 الرواد universities; anything not found officially is listed as not found.
**Alternatives:** Link to the PDF only; type the lists by hand; a simple name-only search; a JavaScript app with all data in the browser.
**Why:** It's the guide's most-used information, and a PDF is hard to search on a phone. A script makes the yearly update repeatable and checkable. Searching by major matches how students think ("I want AI, where can I go?").

## 030 — Live statuses from data: الرواد's deadline, واعد's latest programs, SDAIA as a program; research agents on Haiku
**Date:** 2026-10-11
**Decision:**
- **Deadlines:** a track can carry `status_until`. An open track shows «حتى <date>» and turns to «مغلق» by itself the day after (`track_status()` in `main.py`). الرواد: open until 15 November 2026 (owner-confirmed).
- **واعد:** its programs open and close every few weeks, so instead of one status the track shows a toggle with the latest programs (`data/waaid_programs.json`, copied from the Ministry's واعد page): program, company, institution, country, level, duration, application window, open/closed (computed from today's date), whether it's for high school graduates, and key requirements. The track's own status follows: «مفتوح الآن» if any listed program is open, otherwise «لا يوجد برنامج مفتوح الآن».
- **SDAIA's AI scholarship** is a program of its own (`/programs/sdaia-ai-scholarship`), with facts from its official page and its 28 target universities linked to the explorer; a university page says when SDAIA targets it. It sits on top of the King scholarship (it needs an unconditional offer and a King scholarship decision first), and the page says so.
- **Research agents run on Haiku** (owner's choice, after the main model hit its usage limit): small batches, a schema + example, save as you go, validated by tests (CLAUDE.md).
**Alternatives:** Hand-edit statuses after each deadline; one Waaid status line; SDAIA as a news item only; research on the main model.
**Why:** Statuses that change on known dates shouldn't depend on someone remembering to edit them. واعد is a stream of short programs, so the useful view is "what opened and closed recently". SDAIA's program changes what an AI-minded student should aim for (a university that's on both lists).

## 031 — Official X accounts as sources; SDAIA explained as an add-on; next deadline per university
**Date:** 2026-10-11
**Decision:**
- The King scholarship's official X account (@SA_Scholarships) is the first place to check for openings and closings; a specific post is a valid `status_source` / news `source_url`. Its 26 Aug 2026 post («يمكنك التقديم الآن… عبر منصة قبول») is the source for الرواد being open and settles the قبول vs سفير conflict (قبول). The 15 Nov 2026 end date stays owner-confirmed until a post states it. Each program row links the account so students can follow it.
- SDAIA's AI scholarship: registration open (cohort 4, SDAIA's post of 7 Oct 2026, no deadline yet). Its page opens with a warning that it is **not** a standalone scholarship (you need an unconditional offer from a listed university plus a King scholarship decision), and its news item links to that explainer instead of the post, because many students think they can apply directly. SDAIA's official university list (PDF, downloaded with the owner's OK to `data/raw/`) has **95 universities in 15 countries** (top 50 in the targeted fields in THE, QS, or Shanghai); its web page shows only 28. We use the PDF: 84 link to the explorer, and 11 aren't in the King scholarship's 2026–2027 lists, so they're shown with their country and a note to check with the official side (SDAIA requires a King scholarship decision).
- University-specific deadlines (e.g. Oxford/Cambridge's UCAS date) are not news items; the explorer shows each university's next upcoming deadline from its requirements file, and the university page marks past dates «انتهى».
- News items may carry `page` (one of our pages) in addition to `source_url`.
**Alternatives:** Ministry website only as a source; SDAIA as a plain news link to the post; deadline news items per university.
**Why:** The owner says the official account posts first. The SDAIA misunderstanding is common enough that the explainer matters more than the announcement. Deadlines belong with the university they're for.

## 032 — Explorer filter for programs with target lists; leaner footer
**Date:** 2026-10-11
**Decision:** The explorer has a «برامج إضافية» filter built from any program with `target_universities` (today: «مستهدفة في سدايا (الذكاء الاصطناعي)»), and result rows show that program's chip. Example: major «الذكاء الاصطناعي» + the SDAIA filter = universities on both the Ministry's lists and SDAIA's. The footer drops «بدون تسجيل» (accounts are planned for Launch 2) and the independence line (it stays on /about and on each program page), and the «خريطة الموقع» link: `/sitemap.xml` is for search engines and showed raw XML to people.
**Alternatives:** A checkbox only for SDAIA; an HTML sitemap page.
**Why:** The owner wanted AI-minded students to see where both programs overlap; the filter is generic so the next program with a target list (e.g. KGSP's Arruaad preference) works the same way. The footer showed promises and a link that didn't help students.

## 033 — News as a status board built from data; /news page; video ends on our cover; SDAIA logo
**Date:** 2026-10-11
**Decision:**
- **News board:** «المستجدات» is three groups built on each request from the data that already holds every status (`status_board()` in `main.py`): «مفتوح الآن» (open tracks, soonest deadline first, plus open واعد programs), «مغلق أو لم يفتح بعد» (closed until further notice / not open yet / by invitation, plus واعد programs opening later), «فُتح وأُغلق مؤخرًا» (واعد programs and dated tracks that closed in the last 120 days, newest first). Each item links to our page («التفاصيل») and its official source («المصدر»). A status is typed once (in `paths.json` / `waaid_programs.json`) and moves between groups by itself as dates pass; e.g. الرواد moves to «أُغلق مؤخرًا» on 16 Nov 2026. `news.json` now holds only announcements. The homepage shows up to 4 items per group; `/news` shows everything plus announcements, and the nav links there.
- **Video:** the YouTube player swaps back to our own cover when the clip ends, so YouTube's grid of suggested videos never shows (`video.js`, the player's documented postMessage events, no extra script). YouTube's logo/title link inside the player stays (required by its terms). Rejected: self-hosting the clip (Al Arabiya's copyright), link-only (owner wants it playable on the page).
- **Footer:** the «طريقتنا» column is gone; /about (independence statement, method, image credits) stays, linked as «عن الدليل».
- **SDAIA image:** SDAIA's logo, cut from the cover of its official university-list PDF (its website blocks direct downloads of the logo file), shown on SDAIA's own navy background. Not the X announcement poster: too much small text, a QR code, and people's photos for a small card.
**Alternatives:** A hand-maintained news list (what we had); a news feed sorted by date only; a JavaScript filter UI.
**Why:** The owner wants news that scales and is organized by what a student can do now. Deriving the board from the status data means no duplicates and no stale "open" items after a deadline. Experts' guidance for status pages and service listings (e.g. GOV.UK's "show what's open now first") puts the actionable items first.

## 034 — Explorer: majors by field on every university page, our own suggestions panel, واعد in «المسار»; target filter removed
**Date:** 2026-10-11
**Decision:**
- **University page:** every field the university is ranked in shows as a block: its rank («الترتيب»), the field's name, the guide's notes, and the field's majors (the guide's «التخصصات التابعة لكل مجال»), visible without clicking. Long lists show 10 majors and a «عرض باقي التخصصات» toggle.
- **Search box:** our own suggestions panel replaces the browser's `datalist` (unstyled, scrolled too fast): majors grouped under their إمداد field (doctorate-only majors in their own group), plus matching university names; taller rows, smooth scrolling that doesn't scroll the page behind it, keyboard support (↑ ↓ Enter Esc, an ARIA combobox). Data comes from `/api/suggestions`, loaded the first time the box is used.
- **واعد in «المسار»:** choosing it lists the latest واعد programs (company, institution, country, level, dates, open/closed, requirements, «لخريجي الثانوية»), with a note that واعد doesn't use the guide's lists. A major or name search also shows matching واعد programs (e.g. «الهندسة الكهربائية» → Maaden's Colorado School of Mines program, linked to that university's page).
- **Removed (owner):** the «برامج إضافية» filter and the «مستهدفة في سدايا» tags (decision 032), and the explorer's fine-print line. SDAIA's full list stays on SDAIA's own page.
**Why:** The owner wants each university to read simply as "fields → rank → majors", because the fields decide which majors a student can apply for there, and a calmer, grouped search list.

## 035 — UX redesign: one design system, grades + search on the homepage, a clearer explorer, «قائمتي» on the device (updates 018, 022–023, 027–028, 031–034)
**Date:** 2026-10-11
**Decision:**
- **Direction, «Editorial clarity».** Keep واضح's identity: ivory, forest, Plex Bold, the Naskh wordmark. Adopt proven GOV.UK-style patterns: back link, status tags, summary list, notices, and "filter a list" with removable selected filters. **One design system** in `style.css`:
  - one type scale (nothing under 13px)
  - a `--focus` token (a 3px ring, lime on dark bands)
  - input borders at 3:1
  - shared components: buttons, status tags, info/warn tags, notices, summary list, back link, rows, form fields
  - one `status_tag` macro instead of four copies
- **Colour meanings:**
  - Lime = only "open now" and "your next step" (الرواد's lime chip is gone).
  - Forest = headings, links, and the main action.
  - Amber = restrictions and "not open yet".
  - `tests/test_design.py` checks the contrast of every token pair in both themes.
- **Navigation:**
  - The current section is marked with `aria-current`, visible as an underline.
  - A skip link.
  - «المستجدات» → «مواعيد التقديم» (/news is titled «مواعيد التقديم والمستجدات»).
  - The footer again says, on every page, that واضح is independent and free and links «كيف نتحقق؟». This reverses part of 032, because pages show official logos and data.
- **Homepage** (in order):
  1. The tagline and a lead that says what's here.
  2. **«ابدأ من صفك»** with three large grade buttons: the main way in.
  3. A **search panel** for the official lists: the second way in, with example searches and «290 جامعة في 15 دولة».
  4. **«مفتوح للتقديم الآن»**: only the open items, with the full board on /news.
  5. Compact program rows (a smaller image, one main button, links that wrap).
  6. The Tuwaiq band.
  Removed from the homepage: the decorative Tuwaiq drawing, the 3-group board, the واعد toggle (now linked as «آخر برامجه»).
- **Explorer:**
  - Applied filters appear as removable tags plus «مسح الكل» (server-rendered links, so they work without JS).
  - A visible hint replaces placeholder-only examples.
  - Filters fold behind «الفلاتر (n)» on phones.
  - The field select explains why it's unavailable.
  - «ما الفرق بين المسارات؟» is built from `paths.json`.
  - The rank is explained once («وليس تصنيفًا عالميًا»), with a language-exception note.
  - «أقرب موعد تقديم في الجامعة» is labelled as the university's own date.
  - Proper Arabic counting.
  - Choosing a **university** in the suggestions opens its page.
  - A `role=status` line announces counts (not the whole table).
  - An error state with «حاول مرة أخرى».
- **University page:**
  - **«باختصار»** first: lists, majors, the next university deadline, platform, SAT/ACT, and «صفحة القبول في موقع الجامعة».
  - A notice that being on a list is not admission.
  - A back link to the same search results: a whitelisted `from` parameter, and `history.back()` when possible, so the scroll position is kept.
  - The doctorate lists folded.
  - The university's dates in their own section.
- **«قائمتي»:**
  - Save/remove on university pages, markers in the explorer, and a header link with a count.
  - `/my-list` (noindex), whose rows the server draws for known ids only.
  - Stored **only in this browser** (`localStorage`, ids only), and the page says so. No account, no database, nothing kept by us.
  - Future, documented here only: sync to accounts at Launch 2, a per-university checklist, a deadline view.
- **Program and grade pages:**
  - The main next step as buttons, and official links grouped.
  - «في هذه الصفحة», built from Markdown headings (toc ids; short `{#id}` anchors on the King scholarship page).
  - Grade pages: a grade switcher, «الخطوة التالية» first, and a link to the next grade.
- **Fixes found along the way:**
  - The browser's search normalisation removed every Arabic letter. Invisible combining characters were stored out of order, so the range ran U+0300–064B. Arabic typing never filtered the suggestions. It's now written with `\u` escapes and has a test.
  - A long URL widened Tsinghua's page.
  - Links that couldn't wrap widened the homepage and the program page.
  - The scrollable suggestions list was a Tab stop.

**Alternatives:**
- (B) An app-like dashboard: card grids, bottom tabs, icons. Rejected as generic, against our rules, and more JS.
- (C) A plain government-service look. Rejected because it could be mistaken for the Ministry.
- Search-first or grade-only homepages.
- Saving to an account now (needs Stage 4).
- A placeholder save button (fake functionality).
- Keeping the drawing beside the search.

**Why:**
- A first-time student on a phone had to scroll through ~7,400px where everything had the same weight.
- The most useful tool, the explorer, wasn't reachable from the hero.
- The explorer hid which filters were on, and its numbers and dates were easy to misread.
- Expert guidance (NN/g homepage and visual-design principles, Baymard and the MOJ pattern on applied filters, WCAG 2.2, the GOV.UK patterns) points the same way. Details, sources, and their limits (search summaries only, no user testing yet): `docs/research/ux-redesign-2026-10.md`.

## 036 — Logo: the ض mark (supersedes 012); the owner's X link in the footer
**Date:** 2026-10-11
**Decision:**
- **Logo.**
  - The mark is the letter **ص from Noto Naskh Arabic Bold** (the font we already self-host, OFL licence), with its dot redrawn as a **lime diamond**, on a **forest tile** (`#184b3a`, ivory letter, lime diamond).
  - The tile keeps the lime visible on ivory and makes the mark read as a logo, not a stray letter beside «واضح».
  - The wordmark stays as real text (Naskh), so it stays readable and searchable.
  - One drawing, used in three places:
    - inline in `base.html`'s header (42px; 36px under 380px)
    - `app/static/favicon.svg`
    - the share image (`scripts/og-image.js` draws `favicon.svg`; `og-image.png` regenerated)
  - The glyph outline was copied once with fonttools in a throwaway environment; it isn't a project dependency.
  - The unused `--logo-deep` token is removed. The Tuwaiq drawing stays in the share image's horizon and in the Tuwaiq band.
- **Footer:** a small X icon (the X logo, inline SVG) links to the owner's account `@salahmetaverse`.
  - It is in the global footer only, never in the nav or page content.
  - It opens in a new tab with `rel="noopener noreferrer"`.
  - Its label is «تابعني على X».

**Alternatives:** see `docs/research/` and the 8-concept sheet (2026-10-11):
- Najdi stepped parapet (podium look)
- geometric palm (too close to the state emblem)
- و lens; ح path (read as a Latin C)
- Najdi window (looked like a warning sign)
- horizon line (read as ÷)
- a refined Tuwaiq cliff (the safe option)
- a hand-drawn ص (would not match the approved sketch)

**Why:**
- The name itself becomes the identity, with no added symbol.
- The lime dot keeps the site's one meaning for lime ("your next step").
- The drawing stays legible at 16px.
- It is the most Arabic and least forced of the concepts. The owner chose it.

## 037 — A small set of project subagents, all on Haiku 5.5
**Date:** 2026-10-12
**Context:** Research (university requirements, scholarship rules) was already done by Haiku agents (decision 030), but each time the instructions were rewritten from scratch in the prompt.
**Decision:**
- Three read-only agent definitions in `.claude/agents/`, each with one job:
  - `source-researcher`: finds new facts from official sources
  - `fact-checker`: checks published facts against their cited sources
  - `reviewer`: independently reviews a big diff
- Every subagent runs on `claude-haiku-5-5`: the `model` field in each file, plus `CLAUDE_CODE_SUBAGENT_MODEL` in `.claude/settings.json` for Claude Code's built-in agents (Explore, general-purpose).
- Research agents return results instead of writing files. The main session saves them, validates them, decides, and writes code.
- If Haiku 5.5 is unavailable, Claude stops and tells the owner, rather than switching model or doing the job silently.
- **Amended 2026-10-12 (decision 039):** `source-researcher` and `fact-checker` may use Bash to read pages with `curl` / `pdftotext` (to stdout only), because WebFetch can't reach sites from the cloud environment. Read-only is by instruction; the main session checks `git status` after each agent.
**Alternatives:**
- No agent files, rules in CLAUDE.md only. This worked, but the source rules had to be retyped every time.
- More agents (a codebase explorer, a UX researcher). Rejected: the built-in Explore agent already explores, and one-off research doesn't need a permanent file.
- Agents that write their own result files. Rejected: read-only is safer and keeps one place (the main session) responsible for what lands in the repo.
**Why:** Same rules every time, at low cost, with nothing an agent can break.
**Limits:**
- Haiku is weaker at judgment than the main model, so a `reviewer` pass is a second opinion, not proof.
- Official Saudi sites are blocked from the cloud environment (they work from the owner's laptop).

## 038 — Grade pages with one structure and official sources; the finder shows what's known at a glance
**Date:** 2026-10-12 · **Research:** [docs/research/grade-pages-2026-10.md](research/grade-pages-2026-10.md)
**Context:**
- The three grade pages were public drafts with no sources. Their advice was generic and sometimes too broad, e.g. «أغلب مسارات الدراسة في الخارج تحتاج… آيلتس». Stanford and Harvard ask for no English test, and the King scholarship needs no Qudurat or Tahsili.
- The finder showed rankings, but no requirements.
- Its «لغة الدولة» filter could be read as the language of teaching.
- University dates were free-text labels with notes to ourselves inside them.
- The scholarship's own deadline wasn't on the university page.
**Decision:**
- **Grade pages:**
  - One template (`grade.html`) and one order:
    1. this week's single action
    2. what matters this year
    3. 3–4 priorities
    4. a data-driven tool
    5. up to 4 selected resources
    6. one next step on واضح
    7. official sources
  - Each grade has a distinct job:
    - أول ثانوي «اكتشف وابنِ أساسك»: the five tracks, the counsellor, GPA, an English habit; no test pressure.
    - ثاني ثانوي «ابحث وجهّز»: majors in the finder, a first shortlist, which tests, a plan.
    - ثالث ثانوي «قدّم وتابع»: three kinds of application in order, the confirmation steps, a checklist.
  - Every fact links to an official source read on 2026-10-12. Aramco's was read on 2026-10-11 and is labelled as the previous cycle.
  - Our advice is labelled «نصيحتنا».
  - Status `sourced`, `owner_reviewed: false`.
- **«الاختبارات: من يطلب ماذا؟»** (`data/test_needs.json`): one sourced row per destination. The الرواد row is computed from the requirement files (9 require SAT/ACT, 12 optional, 4 don't consider it, 5 unpublished), so it can't drift.
- **Grade 12** lists the next university deadlines straight from the data.
- **Finder:**
  - A one-line scope note («وجود الجامعة في القائمة لا يعني قبولك فيها»).
  - Tracks in the order students need them, doctorate last.
  - The language filter renamed «لغة الدولة الرسمية», with a visible hint that it isn't the language of teaching. The row tag says «لغة الدولة: الصينية».
  - **At a glance:** each row shows SAT/ACT · IELTS · the next university date · the official admissions page, or «لم نجمعها بعد». The same line appears in «قائمتي».
- **Dates are structured:** `event_ar`, `round_ar`, `cycle_ar`, `year_stated`, `note_ar`, `reference_only`, migrated by hand for all 75. The university page shows «السنة غير مذكورة في الصفحة» when the year was inferred, and «تحققنا في» with the check date.
- **University page «المواعيد»:** two blocks:
  - the scholarship's window, with its status and source, and «apply after the admission»
  - the university's own dates
- Found on the way: «ثلاث قبولات كحد أقصى» is on the official conditions page, now in `paths.json`. The age rule contradicts itself on that page, so it isn't published.
**Alternatives:**
- **An application tracker or dashboard in «قائمتي» (statuses per university).** Rejected for now: it's speculative until students say they'd track in واضح rather than in their own notes. The static checklist and the at-a-glance facts cover the need. It's a question for the usability test.
- **A bachelor's-only filter:** only 5 listings are masters-only, and they're already tagged.
- **Removing the language filter:** rewording keeps its real use (the scholarship's rule on non-English-speaking countries) without the confusion.
- **A large resource library per grade:** rejected (CLAUDE.md: choose by need, verify).
**Why:** students need to know which tests *their* targets ask for, and in which order to apply. Both answers now come from official sources and our own data, not general advice.

## 039 — «قائمتي» findable from the results; a timeline from grade 10 to university on every grade page
**Date:** 2026-10-12 · **Research:** [timeline-2026-10.md](research/timeline-2026-10.md), [product-audit-2026-10.md](research/product-audit-2026-10.md)
**Context:**
- **«قائمتي» worked, but couldn't be found.** You could save only from a university's page, and the header link stayed hidden until the first save. Blocked storage left /my-list blank.
- **Students start preparing too late.** US applications open in August before grade 12, and decisions come in December and March. The scholarship needs an unconditional offer, and its window is set each year: 4 Dec 2022 to 5 May 2023 for 2023–24, but late August to 15 Nov in 2026.
**Decision:**
- **«قائمتي»:**
  - «احفظ» on every result row.
  - The header link is always visible, with a count.
  - When storage is blocked, there are no save buttons and /my-list says why.
  - The note says where the list lives and when it can be lost.
  - Still `localStorage` only; no backend.
- **Timeline:** one shared section, «من أول ثانوي إلى الجامعة», on all three grade pages (`partials/timeline.html` + `data/timeline.json`). There's no new page or nav item.
  - The student's own grade is open and marked «أنت هنا» (`aria-current="step"`).
  - Worked example: Fall 2028.
  - Each stage has actions, «موعد رسمي» facts with sources, and «من بياناتنا» patterns counted from the requirement files (`Explorer.timeline_stats()`).
  - The scholarship sits apart, as «موعده يُعلن كل سنة، وليس ثابتًا»: the rule (unconditional offer), the current الرواد status from `paths.json`, the 2023–24 window as an example, and what happens when the dates clash (self-funded students may apply later; whether earlier time is funded isn't stated).
  - Linked from the university page's «المواعيد» and the program page.
- **Research agents read with `curl`** (Bash, read-only by instruction): WebFetch can't reach sites from the cloud environment (decision 037 amended).
**Alternatives:**
- **A separate /timeline page with a nav item:** splits the same content and adds navigation.
- **A personal planner** (enter your grade and dates): there's no evidence students would use it yet.
- **A fixed "January–February" scholarship season:** false; the windows we found differ.
- **Lime for «أنت هنا»:** lime stays for "open now" and "next step"; «أنت هنا» uses forest.
**Why:** students arrive by grade, so the timeline meets them there, with their year open. One data file means one place to update when the program announces a window.

## 040 — Grade pages: three points, one activity, each grade's own tool (supersedes the timeline placement in 039)
**Date:** 2026-10-12 · **Owner feedback:** the shared timeline "doesn't feel very good or clear"; each grade should have its own thing; remove «مثال: 2026–2027» and the past-year window.
**Evaluation (before):**
- Grade 12 was 12.6 phone screens long, with about 10 sections.
- The same 7-stage timeline appeared on all three pages and repeated each page's own priorities.
- «ما يهم» and «أولوياتك» overlapped, and «هذا الأسبوع» and «الخطوة التالية في واضح» pointed to the same place.
- Example years added noise.
**Guidance used (read directly):**
- NN/g [inverted pyramid](https://www.nngroup.com/articles/inverted-pyramid/): the main point first.
- NN/g [chunking](https://www.nngroup.com/articles/chunking/): small distinct units.
- NN/g [progressive disclosure](https://www.nngroup.com/articles/progressive-disclosure/): "the very fact that something appears on the initial display tells users that it's important", so the first display can't hold too many items.
- GOV.UK [step by step](https://design-system.service.gov.uk/patterns/step-by-step-navigation/) is for an end-to-end journey. Ours is three years, which the grade bar now shows; it isn't a set of steps to repeat on every page.
**Decision:**
- **One short order on every grade page:**
  1. «ما يهم هذه السنة», exactly three numbered points with sources
  2. «ابدأ الآن», one activity with the button that does it (lime = next step)
  3. **the grade's own tool**
  4. «لتعرف أكثر», ≤ 4 resources
  5. official sources
- **Each grade's tool:**
  - أول ثانوي: «المسارات الخمسة» (`data/school_tracks.json`, Ministry 2025 document pp. 11–15)
  - ثاني ثانوي: «الاختبارات: من يطلب ماذا؟»
  - ثالث ثانوي: «سنة التقديم شهرًا بشهر» (`data/apply_year.json`). Every month is covered once; today's row is marked «الآن» and holds the next university deadlines from our data. The scholarship sits in its own block, «والابتعاث؟ لا يتبع هذه الأشهر».
- **The whole journey** is the grade bar at the top: three steps with each year's job (اكتشف واستعد · ابحث وخطّط · قدّم وتابع), the current one filled.
- **Removed:**
  - the shared timeline (`timeline.json`, `partials/timeline.html`)
  - the example years and the 2023–24 window (kept in the research note)
  - «الخطوة التالية في واضح» (merged into «ابدأ الآن»)
  - the in-page contents list
  - the tests table on grade 12 (it links to grade 11's)
**Result:** phone page height at 360px: grade 10 5,042 → 2,984px; grade 11 6,771 → 3,398px; grade 12 9,789 → 4,898px.
**Alternatives:**
- **Keep the timeline, collapsed:** still the same content on every page.
- **A separate /timeline page:** splits content and adds a nav item.
- **Tabs per grade on one page:** hides content from search and from people sharing links to one grade.

## 041 — Final design pass: keep the identity, fix the finder's false "none" answers
**Date:** 2026-10-12 · **Audit:** [design-audit-2026-10.md](research/design-audit-2026-10.md)
**Context:**
- A full audit, with two read-only Haiku agents (UX guidance; an independent finder review) and every finding re-checked.
- The visual identity holds up: tested contrast, colours with fixed meanings, one type scale.
- The finder gave **false "none" answers:**
  - Germany showed 0 universities, though 17 are in إمداد.
  - Stanford was "not found" while a country filter was on.
  - Typing a country name found nothing.
- It also overstated (a field list shown as the major's list; «متاحة لتخصصك»), and was very long on phones.
**Decision:**
- **Keep:** the palette, typography, tokens, the applied-filter chips, the rank order, and the save model.
- **Finder:**
  - A country or language without a track shows every list with matches.
  - Name matches outside the filters are shown, with an explanation.
  - A typed country offers the country filter (`aliases` in `countries.json`).
  - Conflicting filters are explained.
  - Major searches show الرواد as a compact ranked list and say the field list is the whole field.
  - Unresearched universities are noted once per list.
  - At most 8 typed major suggestions.
  - A shorter intro, with the source below the results.
  - Plainer labels: «الجامعات في قوائم الابتعاث», «كل اللغات», «غير الإنجليزية», «المتطلبات والمواعيد», «الجامعة لا تنشر حدًا أدنى».
  - The save button moved out of the row-header cell.
- **Header:** no empty count badge.
**Alternatives:**
- **A full visual redesign:** no evidence the identity fails students. It would cost consistency and add risk for no measured gain.
- **"Show 10 then all" on long lists:** breaks scroll restoration on "back".
- **A sort control:** the official rank is the meaningful order.

## 042 — Domain: wadihguide.com
**Date:** 2026-10-12
**Decision:**
- **Domain:** the owner bought `wadihguide.com` at Cloudflare Registrar (at-cost price, private contact details). The name matches «دليل طالب الثانوية» and doesn't sound official.
- **DNS:** Cloudflare, records set to **DNS only** (no Cloudflare proxy), so Render issues and renews the HTTPS certificate.
- **Hosting:** stays on Render.
- **One public address:** `data/site.json` `base_url` is `https://wadihguide.com`. A middleware in `app/main.py` answers the old Render address and `www` with a **301** to the same path and query on the domain, so shared links keep working and search engines consolidate.
**Alternatives:**
- **Keep the onrender.com address:** looks temporary, and every link shared with testers would break at launch.
- **A `.sa` domain:** more paperwork, and not needed for a guide.
- **Cloudflare's proxy (orange cloud):** another moving part for HTTPS; not needed now.
**Note:** «قائمتي» lives in the browser per address, so lists saved on the old address don't carry over. Testers should start on the new link.

## 043 — Feedback through the owner's X account (footer)
**Date:** 2026-10-12
**Decision:** the footer's X link becomes the feedback channel for the test month: the X icon plus one line, «عندك ملاحظة أو اقتراح؟ راسلني على X», as **one link**. Same place, same safe new tab; the visible text is the link's name (WCAG 2.5.3, so no separate aria-label).
**Alternatives:**
- **A Google Form:** a third-party page and more setup, with no evidence it's needed yet.
- **WhatsApp:** shares a personal phone number with minors.
- **A form on the site:** needs a backend and storing messages.

## 044 — Launch ad «الشلة»: real product footage, minimal AI, built by script
**Date:** 2026-10-12
**Decision:**
- **The ad:** a 30s vertical ad (plus 15s and 6s cutdowns) on the owner's concept, friends at school: «وأنت؟ وش ناوي؟» → the real site → «لسّه أقرّر… بس عرفت خطوتي الجاية».
- **Real footage:** 14 of the 30 seconds are real wadihguide.com footage, captured by script from the live site.
- **AI only for 4 scene-setting shots:** framed with no identifiable face (backs, shoulders, hands, soft focus) and labelled «مشهد تمثيلي مولَّد بالذكاء الاصطناعي».
- **Toolkit:** Higgsfield for the 4 clips, ElevenLabs for the voices, ffmpeg + headless Edge for the edit. Edge renders the Arabic captions and end card in the site's own fonts. CapCut is optional.
- **Files:**
  - Scripts in `marketing/src/`.
  - Media in `marketing/assets/` and `marketing/out/`, both git-ignored.
  - The production guide and launch plan in `docs/marketing/launch-ad.md`.
- **API keys:** stored outside the repo (`%USERPROFILE%\.wadih\`), restricted, with credit limits. They are never pasted in chat.
- **Soft launch first:** organic only, measured with `?src=` links read from Render's access logs (no trackers). Any paid boost waits for 14 days of data and the owner's approval.

**Why:**
- Snapchat, Saudi Arabia's biggest youth platform, stopped recommending wholly AI-generated videos in Spotlight (July 2026).
- TikTok asks for AI labels and may restrict AI likenesses of minors.
- A guide whose promise is "real and sourced" shouldn't open with a fake teenager.
- The real screen is also the most convincing proof: every fact has its source.
- A script makes the edit repeatable: re-capture the site after a change, rebuild in two commands.

**Alternatives:**
- **A fully AI-generated ad with a realistic student:** reach and policy risk, and off-brand.
- **«وش ناوي تدرس؟» from relatives, or a founder-voice video:** strong, kept for later variants. The owner chose the school concept.
- **Higgsfield's free plan:** rejected, because it has 0 credits and no commercial use.
- **Assembling only in CapCut:** manual and hard to repeat; kept as an optional polish step.
- **Playwright for the screen capture:** a package install; Edge over the DevTools protocol needs nothing new.

## 045 — Site search first, as the retrieval step of a future RAG chatbot
**Date:** 2026-10-12
**Context:** the owner wants an AI chatbot that answers students from verified content (roadmap later stages 7–9), and wants to learn RAG, vector databases, API design and scaling along the way. A chatbot is only as good as its retrieval, so retrieval comes first, as a free feature that is useful on its own.
**Decision:**
- **The RAG plan, in steps:** (1) keyword search, (2) chunks with source tracking, (3) search by meaning (embeddings + a vector index), (4) an eval set of real student questions, (5) the chatbot «اسأل واضح» (paid API, ask first), (6) operations (rate limits, spend cap, caching, logs without personal data), (7) the update-monitor agent. Spec: `docs/specs/search.md`.
- **Sources are fetched ahead of time, never live while answering.** The owner's chosen official pages are read, reviewed, and stored with their link and date; answers come only from that store.
- **Step 1 (this decision):** `/search` and `/api/search`, using **SQLite FTS5** (built into Python's standard library, nothing to install) in memory, rebuilt at startup.
  - **Chunks:** guide pages split by h2 section; the program facts the program pages show; the «الاختبارات: من يطلب ماذا؟» rows. Each chunk carries its link and official sources.
  - **Only published, sourced content** is indexed: pages with `status: sourced` and sources, facts with status `sourced`/`conflict`.
  - **Arabic:** the explorer's `normalize()` (أ/إ/آ, ة/ه, ى/ي, short vowels), plus dropping «ال» and joined «وال/بال/فال/كال/لل» from longer words. Prefix matching (`تقدي` → `تقديم`).
  - **Ranking:** bm25, with a heading match weighing most.
  - `/search` is `noindex` and not in the nav yet.
**Alternatives:**
- **A vector database now:** skips the basics and needs a package and an embeddings model; it's step 3.
- **Search in the browser (JavaScript):** the chatbot will need retrieval on the server anyway.
- **Postgres full-text search:** needs a database server we don't have yet.
- **Live web search at answer time:** unreviewed and possibly unofficial sources (breaks the trust rule), slower, costs more.
**Why:** free, no new dependency, and it builds the exact pipeline RAG needs (chunk → index → retrieve → cite). Its known limit, matching words and not meaning («منحة» finds nothing, «مشروط» also matches «غير مشروط»), is the reason for step 3.

## 046 — KGSP: its own page, «يفتح قريبًا», search linked from the homepage
**Date:** 2026-10-12
**Decision:**
- **New status `opening_soon` («يفتح قريبًا»):** for a program whose official page says applications "will open soon" with no dates. It is shown in amber like «لم يفتح بعد» and sits in the news board's waiting group.
- **KGSP** (`kaust-kgsp`): status `opening_soon` from the [Prospective Students](https://kgsp.kaust.edu.sa/prospective-students) page, re-read 2026-10-12 («Applications for Cohort 19 will open soon»). The owner asked for it.
  - It replaces `invitation`.
  - Its own program page (`content/programs/kaust-kgsp.md`) and 8 sourced facts, from `docs/research/kgsp-2026-27.md` re-checked against the page. Last cycle's (Cohort 18) rules are labelled as such.
  - «بالدعوة فقط» vs. open application is shown as a `conflict` with both pages.
  - Summary corrected: abroad, not only the US, and you apply yourself.
- **Site search links:** one line under the homepage's university search («تبحث عن معلومة…؟ ابحث في الدليل») and a search box on the 404 page. Not in the header yet: that spot may become «اسأل واضح» later.
**Alternatives:**
- **Keep `not_open`:** true, but «يفتح قريبًا» is what the official page says and tells students to watch it.
- **A search box in the header:** too tight on phones (the iPhone header fix).

## 047 — Test resource pages (SAT, TOEFL, القدرات/التحصيلي) and three more FAQ answers
**Date:** 2026-10-12
**Decision:**
- **Three new resource pages, built like the IELTS page:** `/resources/sat`, `/resources/toefl`, `/resources/qudurat-tahsili`. They are linked from «الاختبارات: من يطلب ماذا؟», the KGSP page and the IELTS page. Research: `docs/research/tests-resources-2026-10.md`.
- **TOEFL page:** explains the new 1–6 scale (since 21 January 2026) and the comparable 0–120 score on reports, because programs still state old-scale minimums.
- **القدرات/التحصيلي page:** short on purpose. ETEC's test pages couldn't be read, so it has only what each test measures, who asks for it, and where to register. Duration, scale, fees and attempts wait for the owner's check.
- **Not published:** a total SAT fee (the page gives two parts), the Saudi TOEFL price (a per-country widget), and the conflicting TOEFL score-delivery times.
- **King's scholarship FAQ:** three more answers (no fixed high school percentage, in-person full-time study only, up to three offers). The age rule stays unpublished (the official pages conflict). Research: `docs/research/custodian-faq-2026-10.md`.
- **Aramco:** re-checked, unchanged (`docs/research/aramco-cdpne-2026-27.md`).
**Alternatives:**
- **Fill القدرات from prep-course sites:** rejected; not official.
- **One combined "tests" page:** the per-test pages match the IELTS page and are easier to link and search.
**Why:** students search for these tests by name. Each page answers "what is it, who needs it, how do I start", with the official link, and gives search and the future chatbot more verified content.

## 048 — Applied filters: a separate, large ✕ that clears only its own filter
**Date:** 2026-10-12
**Problem (reproduced in the browser):**
- The whole chip was one link; its ✕ was a 10 × 23 px glyph, 8 px from the next chip.
- The link's href was a snapshot ("this search without me"), and `universities.js` copied it into the form.
- Two removals in quick succession (country, then track) brought the country back: the second chip's href was drawn before the first removal and still contained it.
- The same happened when a near-miss on the tiny ✕ hit the neighbouring chip, or when the chips shifted after an update and a second tap landed on another chip.
**Decision:**
- **Each filter in `describe()` names the parameters it clears** (`remove`: `["country"]`, `["track", "field"]`…). `universities.js` clears only those in the **live form** and keeps every other filter. The href stays for no-JavaScript use.
- **The chip text is a plain label;** only the ✕ removes.
- **The ✕ is its own link:** a 36 × 36 px circle in a 44 px chip, an SVG cross, and `aria-label` «إزالة الدولة: الصين». WCAG 2.5.8 asks for at least 24 × 24 px; 44 px matches common mobile guidance.
- The focus ring follows the circle. After a removal, focus moves to the next ✕, or to the search box.
- **«مسح الكل»** stays a separate link, now 44 px tall.
**Alternatives:**
- **Keep the whole chip clickable:** a tap on the label removes the filter by surprise, and the chip looks like a selected value, not a button.
- **Disable the chips while results load:** hides the cause instead of fixing it.
**Note:** browsers cache `universities.js`. After this deploy, a returning visitor may run the old script until their cache refreshes (it still works, without the race fix). Cache-busting the static files is a separate task.

## 049 — University logo and country flag, on the university's own page only (updates 017, 020, CLAUDE.md "no flags"; amended below)
**Date:** 2026-10-12
**Decision (the owner's choice):**
- **Where:** each university's page (`/universities/<id>`) shows the official logo above the name (on a white plate, at most 64 × 220 px), plus a small flag before the country name. Never in result lists, «قائمتي», or on the homepage, which stay text-only for scanning and speed.
- **Flag:** decorative (`alt=""`), because the country's name is written next to it. 15 SVGs from [flag-icons](https://github.com/lipis/flag-icons) 7.2.3 (MIT), self-hosted in `app/static/img/flags/`, licence file included.
- **Logo:**
  - `alt` «شعار <name>», with the line «الشعار لتعريف الجامعة فقط، وواضح لا يتبعها».
  - No logo → the page looks as before (no placeholder).
  - Credits are listed on /about.
- **Sources for the first batch (147 of 290):**
  - Wikidata's "logo image" (P154) → the Wikimedia Commons file and its licence: 132 public domain (mostly text logos), 11 CC BY-SA, 3 CC0, 1 "copyrighted free use".
  - A script matched each university by name (the label must share most of its distinctive words) and rejected photos. Every candidate was reviewed by eye on a contact sheet.
  - Caught before publishing: UCL matched UCLouvain (dropped); Cornell's "logo" was a photo of a sign (dropped).
  - Files are Commons' PNG renderings, resized to ≤ 128 px tall and ≤ 440 px wide, then re-encoded by Pillow (pixels only, no metadata). 20 KB on average, at most 51 KB; only one loads per page.
- **Data:** `data/university_logos.json` (file, size, `source_url`, `asset_url`, `licence`, `wikidata`, `retrieved`).
- **Tests:** every country has a flag; every logo has a source, a licence and a date, is under 60 KB, and has no script; the lists show no logos or flags.
- **Remaining 143:** 107 have no logo on Wikidata, 22 had no confident match, 14 had only a photo. Next: Haiku agents find each official logo on the university's own site, in batches, with the same review.
**Alternatives:**
- **Neither (the earlier rule):** the owner wants recognition on the page students open.
- **Logos and flags in lists:** busier rows on phones and heavier pages; the country name already scans well.
- **Load logos from the universities' sites:** third-party requests (privacy rule) and links that break.
- **Emoji flags:** Windows shows letters ("US") instead of flags.
**Why:** the logo confirms "this is the university I meant" on the page where a student decides. Showing it only there keeps lists fast and calm. Self-hosting keeps the no-third-party-requests rule.
- **Amended the same day (owner):**
  - Flags also appear in list rows and «قائمتي». They are drawn by the shared `country()` macro, 20 × 15 px, lazy-loaded; the same 15 files are cached.
  - Logos stay on the university page until all 290 have one.
  - The line «الشعار لتعريف الجامعة فقط…» was removed. /about still says the logos only identify the universities.
  - In the lists, the «لم نجمع متطلبات…» note and the conditional-language sentence were removed. Only «الترتيب… وليس تصنيفًا عالميًا» remains. The language rule is still explained on each non-English university's page and on the scholarship page.

## 050 — US applications: fee + waiver on each US university page, and one short guide
**Date:** 2026-10-12
**Context:** students applying to the US ask which system to use (Common App, the UC application, a university portal) and whether they can avoid application fees. The site had only one line about platforms.
**Decision:**
- **Per university (data):** `application_fee` in `data/university_details/<id>.json`.
  - The international fee: `fee_usd` (`0` = no fee, `null` = not published).
  - The waiver class from the university's own page: `accepts_common_app` / `own_waiver` / `domestic_only` / `none` / `not_stated`. Labels are in `WAIVER_AR`.
  - A short note and the source.
  - 50 of 53 researched US universities so far.
- **On the university page:** «رسوم التقديم» under «منصة التقديم», in «باختصار» and in the requirements, plus «كيف أقدّم؟» next to the platform. «كيف تطلب الإعفاء؟» appears only when the university offers a waiver an international student can request.
- **One guide, `/resources/us-applications`:**
  - Which system, and what an application contains.
  - A five-question fee-waiver guide: system → international → does the programme cover you → does the university accept it → alternatives.
  - A folded table of the US universities in the lists, grouped by waiver policy (`Explorer.fee_groups()`, `partials/us_fees.html`).
  - Linked from the grade 12 page and every US university page.
- **Rules:**
  - Never "guaranteed"; answer with your real circumstances.
  - UC's $80 is a reduced fee, not a waiver.
  - The Common App essay word limit isn't published, because the official page doesn't state it.
  - Research: `docs/research/us-applications-2026-10.md`.
**Alternatives:**
- **Step-by-step Common App and UC walkthroughs:** the screens change every year and the official guides already exist, so ours would go stale. We link to them instead.
- **A progress tracker or separate FAQ:** site search covers the questions, and tracking needs accounts (Stage 4).
**Why:** the decision happens university by university, so the fee lives on the university page. The guide answers the general questions once, with the official link at every step.

## 051 — Cleanup, iteration 1: say each thing once
**Date:** 2026-10-12
**Research:**
- [NN/g, How users read on the web](https://www.nngroup.com/articles/how-users-read-on-the-web/): 79% of test users scanned.
- [NN/g, concise, scannable, objective](https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/): concise text scored 58% higher in measured usability.
- [NN/g, progressive disclosure](https://www.nngroup.com/articles/progressive-disclosure/): defer secondary information.
**Decision:**
- **University page:**
  - The «تحققنا منها في…» date is removed (check dates aren't shown, CLAUDE.md).
  - «السنة غير مذكورة في الصفحة» appears once under the list when it applies to every date.
  - An English-test note that repeats on every test is shown once.
  - «ما لم نجده في المصادر الرسمية» is folded.
  - The requirements intro is one line.
- **Homepage:**
  - The program row hides the provider when it equals the name (Aramco).
  - Shorter «لمن؟» for the King scholarship and SDAIA. SDAIA said "not standalone" three times.
  - The search hint is shorter, and the X link label lost its bracket.
- **Kept on purpose:** every source link, the "not affiliated" lines, and the admission ≠ scholarship notice.
**Next iterations:** program pages and the explorer's intro, measured the same way (words per page, one idea per block).

## 052 — Back to the same place in a list; versioned CSS/JS; flags load normally
**Date:** 2026-10-12
**Problem (owner, on a phone):**
- After opening a university from the الرواد list and pressing Back, the list jumped to the top. Phone browsers often reload the page on Back, and the filter panel folding on load shifts it, so the browser's own scroll restore misses.
- Some flags didn't show: they were lazy-loaded, and lazy images can stay blank after a Back.
- On desktop, the flag sat too close to the country name.
**Decision:**
- `universities.js` remembers the opened university (`sessionStorage`, this tab only, id + position, 30 minutes). On return by Back or by «الرجوع إلى نتائج البحث», it scrolls that row into view, or to the saved position if the row is gone. A fresh visit starts at the top.
- Flags load normally: the same 15 small files repeat, so lazy loading saved nothing. The gap is now 8 px.
- CSS/JS links carry `?v=<content hash>`, so a deploy reaches returning visitors at once. This resolves decision 048's cache note.
**Alternative:** rely on the browser (`scrollRestoration = auto`). That is what failed.
- **Amended the same day (still at the top on the owner's phone):**
  - `scrollRestoration` is now always `manual` on the list pages, so the browser can't jump to the top after we scroll.
  - The return is repeated while the page settles (next frame, `load`, fonts ready, 0.4 s and 1.2 s), and stops as soon as the student touches the page.
  - The "instant back" case (back-forward cache: the page comes back without running the script) is handled through `pageshow`. Not testable in the dev browser, which always reloaded.
- **Amended again (the owner saw a small "shake"):**
  - Instead of re-centering several times, the tapped university goes back to the exact height it had on the screen (saved at the tap).
  - It moves only if it's off by more than 4 px: once on load and once after the fonts are ready.
  - When the browser has already restored the place, nothing moves.
  - Tested in the dev browser: #26 and #8 returned to the same pixel row (643 px and 150 px).

## 053 — Stale facts: a report script, not a failing test
**Date:** 2026-10-13
**Problem:** the roadmap planned a test that fails when a fact's `last_checked` is over 90 days. Two issues:
- Render deploys only after CI passes, so a test based on today's date would turn CI red the day a fact ages, with no code change, and block an urgent fix.
- Every fact was checked 2026-10-09 to 10-12, so a 90-day rule stays silent until January, after Launch 1 (~2026-12-09).
**Decision:**
- `scripts/stale_facts.py` lists every checked item (132 today: program facts and track statuses, guide pages, university detail files, test and timeline rows, the PDF guide, واعد, the quote) by check date, oldest first, with its source link and whether the owner reviewed it. It reads all four date names in the data (`last_checked`, `read_on`, `checked`, `retrieved`); logos are left out.
- Options: `--as-of` (e.g. launch day), `--days` (default 90), `--all`. It always exits 0.
- `tests/test_stale_facts.py` fails if a check date exists in `data/` or `content/` that the script doesn't read, so the report can't silently miss a new file. It never depends on today's date.
- **Before Launch 1:** one full re-check pass. Run `--as-of 2026-12-09 --days 45`, re-check from the top, update each date, run again until empty.
**Alternative:** the failing test (above), or a scheduled CI job that warns without blocking deploys. The scheduled job can come later; the script is what it would run.

## 054 — UK requirements (إمداد wave 2) and a «الشهادة الثانوية السعودية» row
**Date:** 2026-10-13
**Problem:** for a Saudi student, the most useful fact about a UK university is whether the Saudi secondary certificate alone gets them into year 1, or only after a foundation year. We had no field for it; UCL's answer sat in `language_note_ar`, which the page labels «لغة الدراسة».
**Decision:**
- New optional `saudi_certificate` in `data/university_details/<id>.json`: `direct_entry` (true / false / null), `note_ar`, the exact English `quote`, `source_url`. Shown as «الشهادة الثانوية السعودية» only for true or false.
- **`false` only when the university's own page says so** (for example "not sufficient for direct entry", "must complete a foundation course", "not considered for entry"). When the page names the certificate only as a route into its foundation programme (Reading, Derby, Southampton, Bristol), or doesn't name it at all, it is `null`, and the finding goes in `not_found_ar`. Inferring "no" from a page's structure would be inventing a requirement.
- Wave 2: 26 of 29 UK إمداد universities researched by 6 `source-researcher` agents (Haiku, `curl`), every saved fact spot-checked by the main session against the live page. Results: 15 say the certificate is not enough for year 1; 11 are `null`; none accept it directly.
- Not saved: Durham and Bournemouth (their sites refuse automated reads, 403), and London Business School (only master's/MBA programmes listed, but no page says it has no bachelor's).
- Every UK file carries the UCAS equal-consideration deadline (13 Jan 2027, read on ucas.com). Course-only deadlines (medicine, LNAT) use a different `event_ar`, so they never become «أقرب موعد».
- SAT/ACT and acceptance rate are left out for the UK: the agents didn't search for them, so "not published" would overclaim.
**Alternative:** keep using `language_note_ar` (wrong label), or record "false" when a page implies it (more answers, but some invented).

## 055 — Wave 3 (Australia, Canada, Singapore); repo instructions follow the current Claude Code docs
**Date:** 2026-10-13
**Wave 3:**
- 16 of 23 saved, same rules and checks as decision 054 (every quote re-fetched with `scripts/check_quote.py`). Saudi certificate: accepted for year 1 at McGill and Guelph; not enough at NTU, Université de Montréal, UNSW and Adelaide; not stated at the other 10.
- Not saved (every page refused automated reads, 403): Melbourne, Griffith, Monash, Deakin, Macquarie, Alberta, Singapore Management University.
- **Australian deadlines:** only Semester 2 (July) 2027 dates are shown. Semester 1 2027 starts in February, before a grade-12 student graduates, so its deadlines would mislead «أقرب موعد».
- Université de Montréal teaches in French; `language_note_ar` says so.
- When two official pages of one university disagree on a deadline (Calgary, Montréal) or a score (NTU), no date or number is shown.
**Repo instructions (checked against code.claude.com docs, 2026-10-13):**
- CLAUDE.md stays short (target under 200 lines; it's ~58).
- Instructions that only matter for part of the code move to path-scoped rules: `.claude/rules/design.md` loads only when Claude edits `app/templates/` or `app/static/`.
- Repeated workflows become skills: `.claude/skills/research-wave/SKILL.md`.
- No `goal.md` / `spec.md` / `TODO.md`: CLAUDE.md, `docs/specs/` and the roadmap already do those jobs.
**Alternative:** keep everything in CLAUDE.md (loads every session, even for unrelated work).

## 056 — Wave 4 (last English-speaking universities) and a full verification pass
**Date:** 2026-10-13
**Wave 4:** 22 of 25 saved (US 15, India 7), same rules and checks as decisions 054–055. Boston University lists the Saudi certificate as accepted for admission. Not saved (admissions sites block automated reads): University of Virginia, University of Pittsburgh, Colorado School of Mines. India: the five IITs share one route (foreign nationals sit JEE (Advanced) directly, supernumerary seats up to 10%, from the official JEE Advanced and JoSAA 2026 rules); 2027 rules aren't published yet.
**Verification pass:** four `fact-checker` agents re-read about 200 published claims against their sources. Every fix below was re-checked by the main session:
- **Preparatory year is not a second exception.** The Ministry lists one exception to "final, unconditional admission" (a non-English-speaking country). The preparatory year has separate extra conditions (90% average, IELTS 5.5). Fixed on the scholarship page, its facts and tracks, the grade-12 timeline and the tests table.
- China bachelor's: added the age limit (30) from the 2025–2026 extra conditions. The general "bachelor's ≤ 30 except الرواد" line stays unpublished: the general-conditions page and the FAQ ("لا يشترط عمر محدد") contradict it.
- SAT next date (7 Nov 2026, register by 23 Oct), واعد IELTS range (5.5–7), SDAIA overlap (28 of 95 in الرواد, 82 in الرواد or إمداد), KGSP wording, "government" universities on the unified-admission platform, documents list, guide scope (no واعد), moved links (Harvard, SAT, TOEFL, Aramco).
- **Aramco:** the owner read the official page on 2026-10-13 (new URL). Requirements unchanged; registration closed; next cycle to be announced. Age limit (22 Hijri years) added to the audience line.
**Not added:** SABIC's university scholarship (in-Kingdom; students are nominated through four universities; owner: not for now, 2026-10-13), NEOM's scholarship (Tabuk region only; portal offline; no official requirements or current cycle), the Ministry's 2021 health-specialties track (superseded by the four current tracks), the full واعد list (all closed).

## 057 — Product audit: a deep core plus thin doors; trust fixes first
**Date:** 2026-10-13 · **Audit:** [product-audit-2026-10-13.md](research/product-audit-2026-10-13.md)
**Context:**
- A full product audit: the code, the live site in a headless browser at 390 and 1280px, all 129 requirement files, and primary sources.
- واضح serves one path well: studying abroad on a scholarship. The tagline («مستقبلك بعد الثانوية») promises more:
  - The undecided student has no starting point (site search for «مهارات» or «وظائف» finds nothing).
  - Neither does the student who'll study in Saudi Arabia. In SPA's 2019 figures, government seats covered about 87% of graduates.
- It also found published text that was wrong, stale or easy to misread.
**Decision:**
- **Positioning:** a deep, verified core (study abroad: scholarships plus applying to listed universities), plus thin doors that route to official tools instead of rebuilding them:
  - «لسه ما قررت؟»
  - «الدراسة في السعودية»
  - the grade pages
  - Keep the tagline; the doors make it honest.
  - No own interest quiz: official measures exist (the Ministry's in grade 10, HRDF «سبل»), O\*NET has no Arabic version and modified versions must be validated, and interests predict weakly.
  - Defer accounts, the chatbot, and the remaining 143 logos.
- **Fixed now (milestone L, items 1–2):**
  1. **Grade 12:** the timeline counts said «… جامعة في مسار الرواد» while counting every researched university (102, not 30). Now «من قوائم الابتعاث», with a test that the sentence never names a track it doesn't count.
  2. **Grade 11:** «إمداد: لم نجمع متطلباتها بعد» is now computed from the files («جمعنا متطلبات N من 223»).
  3. **«لمن» on open items:**
     - Every high-school track has `apply_with_ar` in `paths.json`. `status_board()` passes it as `who_ar`, and the homepage and /news show «لمن: …».
     - The board's "you can apply today" hint became «مفتوح اليوم لمن تنطبق عليه شروطه».
     - Why: «مفتوح الآن» alone read as "apply today" to grade 12 students who can't yet.
  4. **Explorer:** after «مسح الكل» or removing the last filter, focus went to the search box, which opened 157 suggestions over the results. Focus now goes to the tag that takes the removed one's place, or to `#results`, never the combobox. Checked in Chromium at 390 and 1280px, including the decision 048 race.
  5. **Timing note** (`window_note` macro) under an open, dated الرواد/إمداد track on the program and university pages: the window is for students who already hold an admission, and later results mean a later window.
  6. **Foundation year:** where `saudi_certificate.direct_entry` is false (19 universities), the university page shows the scholarship's foundation-year conditions (the sourced `prep-year` fact) next to «لا تكفي للسنة الأولى مباشرة».
**Alternatives:**
- **Stay a scholarship-only guide and narrow the tagline:** cheaper. It's the fallback if the usability test shows students only come for the scholarship.
- **A full career and domestic platform:** too much to verify and maintain at ~5 h/week.
- **For «لمن», reuse the long `audience_ar`:** too long for a status row. The new field is a short restatement, and the full sourced conditions stay on the program page.
**Next:** the «لسه ما قررت؟» guide (official-measure links checked from a laptop), then the 3–5 student usability test. P1/P2 lists are in the audit.

## 058 — Requirements audit: a minimum is not a recommended score; explorer and Arabic fixes
**Date:** 2026-10-13 · **Audit:** [requirements-audit-2026-10-13.md](research/requirements-audit-2026-10-13.md)
**Problem:**
- The owner saw Georgia Tech's IELTS as 6 on واضح and 7 elsewhere. The 7.0 is Georgia Tech's *graduate* requirement; first-year applicants meet the University System of Georgia floor (6, recommended 6.5). The number was right, the presentation wasn't.
- An audit of all 129 files found the same pattern widely: one `min` field held stated minimums, competitive scores (UCLA, Cornell, Purdue, USC), system floors (Georgia Tech, UCLA) and program-dependent levels, while the same kind of competitive score was hidden in a note elsewhere (NYU, Yale, Penn…). TOEFL mixed the old 0–120 and new 1–6 scales without saying which. Some notes came from search snippets (Oxford, UCL, Michigan, Columbia, NUS) and were published with "check before publishing" caveats, against decision 028.
- On a phone, the explorer's suggestions panel floated over the live results, so a tap aimed at an applied filter's ✕ could pick a suggestion instead.
**Decision:**
- **English model** (`english.<test>`): `min` = the stated minimum for full admission; `recommended` = recommended / competitive / expected (never a cut-off), with `recommended_source_url` when another official page states it; `each_min` = a uniform per-skill IELTS minimum; `varies: true` = the level depends on the program (`min` is the general or lowest); `accepted: false` = the test doesn't count as proof of English there («لا يُقبل لإثبات اللغة»; only on an explicit statement or an exhaustive list without it). `Explorer.english_rows()` and `english_compact()` turn these into words, so templates never print a bare number.
- **Display:** the university page shows each test on its own line («الحد الأدنى 6.0 · الموصى به 6.5 · ولا تقل أي مهارة عن …», «يختلف حسب التخصص», «لا يُقبل لإثبات اللغة»), says which TOEFL scale a score is on (linked to the TOEFL guide), and defines «الحد الأدنى» and «الموصى به» once. Result rows show the same distinction in short form.
- **Unverified research is hidden, not caveated:** a details file with `"draft": true` is loaded only with `WADIH_SHOW_DRAFTS=1` (Oxford and UCL, until the owner checks them in a browser). Snippet-based facts in published files were removed. A test fails if a published file mentions a search snippet.
- **Rows that held the wrong thing:** the Saudi certificate goes in `saudi_certificate` (Cambridge, Toronto), English pathways in the English note, and a new optional `admission_tests` row (Cambridge, Imperial). `language_note_ar` is only for the language of teaching.
- **Fees:** an optional `waiver_source_url` when the fee and the waiver are stated on different pages.
- **Explorer:** on the explorer, the suggestions take their own space instead of floating over the results; they close on a click outside, but never in the middle of a press (closing mid-press moved the page under the pointer); only the last of several quick ✕ presses moves focus, and never onto «مسح الكل». A track ranked per field (إمداد, البحث والتطوير) without a field now asks for the field first, with the alphabetical list folded below (49.5 → 2.1 phone screens). Flags load lazily.
- **Formal Arabic everywhere on the site** (owner, 2026-10-13): الفصحى, no dialect. The planned door is «لم تقرر بعد؟», not «لسه ما قررت؟». Test parts are «مهارات» (Listening, Reading, Writing, Speaking = الاستماع، القراءة، الكتابة، التحدث). A test fails on common dialect words in templates, content and data.
**Alternatives:**
- **Keep one `min` and explain in notes:** less data, but the number in a result row would still read as a cut-off. Rejected; this is the error the owner hit.
- **A `kind` field on one number** (minimum / recommended / floor): can't express "minimum 6, recommended 6.5", the most common case.
- **Show a "last verified" date next to each fact:** decision 028 keeps check dates in the data, not on the page; still right (dates add clutter and invite "outdated?" doubts without helping a decision).
- **Keep the floating suggestions and only close them on outside taps:** a tap on the panel still picks a suggestion when the ✕ is under it.

## 059 — Repo files follow the current Claude Code docs; no learning log; review fixes
**Date:** 2026-10-13
**Context:** the owner asked to organize the repo by what the Claude Code docs recommend (subagents, agents, MCP, goals) and to drop the learning log, which they don't read. Checked against [the .claude directory reference](https://code.claude.com/docs/en/claude-directory), [memory](https://code.claude.com/docs/en/memory), [subagents](https://code.claude.com/docs/en/sub-agents), [skills](https://code.claude.com/docs/en/skills), [MCP](https://code.claude.com/docs/en/mcp) and [/goal](https://code.claude.com/docs/en/goal) on 2026-10-13.
**Decision:**
- **The layout already matches the docs** and stays: `CLAUDE.md` at the root (~60 lines; the docs say under 200), `.claude/settings.json` (enforced settings), `.claude/agents/` (three read-only subagents with valid frontmatter), `.claude/skills/research-wave/`, `.claude/rules/design.md` (path-scoped). No `.claude/commands/` (skills replaced them), no `.mcp.json` (no project-shared MCP server is needed yet), no hooks (none needed; a hook must also work on the owner's Windows setup).
- **"Goals" is a command, not a file:** `/goal <condition>` keeps a session working until the condition holds. The plan stays in `docs/roadmap.md`; no `goal.md` (decision 055 still holds).
- **Haiku for every subagent is now enforced**, not just the default: `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` next to `CLAUDE_CODE_SUBAGENT_MODEL` in `.claude/settings.json`. Without it, the docs say the built-in Explore and Plan agents, and any model passed per call, ignore the variable.
- **`LEARNING_LOG.md` removed** (in git history if wanted). The key concept stays in each task's report; the why stays in `docs/decisions.md`.
- `docs/CLAUDE_WORKFLOW_GUIDE.md` renamed `docs/claude-workflow-guide.md` (the other docs are lower case). Both guides now list `/goal`, `.mcp.json`, `commands/`, workflows and agent memory, with when to use each.
- **Two repeatable checks** (the original audit brief asked for one): `scripts/check_sources.py` (is every university fact still on its cited page; a report, like `stale_facts.py`) and `scripts/check_explorer.mjs` (the explorer's JavaScript in a real browser; needs Playwright, preinstalled in cloud sessions; CI would need an install, so ask first).
- **Fixes from the independent review of decision 058** (`reviewer` subagent): «لا يُقبل لإثبات اللغة» instead of «لا تقبله الجامعة» (Georgia Tech still reads Duolingo as extra material); Toronto's note no longer says Duolingo isn't mentioned next to its 120 minimum; empty dates say «لا توجد لدينا مواعيد مؤكدة» instead of claiming a review that didn't happen (Michigan); the grade pages count a missing SAT policy as «لم نتحقق منه», apart from «غير محدد»; Brown's hedge («المتوقع في أغلب الحالات») is explicit; Cambridge's foundation-year sentence is back with its own source; the suggestions don't open if their first load finishes after the student left the box; the formal-Arabic test also scans Python and JavaScript strings.
**Kept, against a review finding:** Brown's 8.0 stays a minimum: its page calls the scores "minimum scores… expected in most cases", which is a minimum with exceptions, unlike Cornell's "minimum competitive". The sentence «مسار إمداد يرتّب الجامعات داخل كل مجال» stays in the template: it describes how the lists work (shown by the data itself), not an official requirement, and the guide is linked under the results.
**Alternatives:** keep the learning log for the FDE portfolio (the owner said they don't read it, and an unread log goes stale); add a Playwright job to CI now (needs an install; asked first).
