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

## 012 — Logo: the Mount Tuwaiq cliff
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
- **Leaner CLAUDE.md:** the architecture moved to `docs/architecture.md`; CLAUDE.md keeps the rules, working style, commands, and pointers. Also added: `docs/CLAUDE_WORKFLOW_GUIDE.md` and `LEARNING_LOG.md`.
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
- SDAIA's AI scholarship: registration open (cohort 4, SDAIA's post of 7 Oct 2026, no deadline yet). Its page opens with a warning that it is **not** a standalone scholarship (you need an unconditional offer from a listed university plus a King scholarship decision), and its news item links to that explainer instead of the post, because many students think they can apply directly. The post says "more than 50 universities" while SDAIA's page lists 28: both are shown.
- University-specific deadlines (e.g. Oxford/Cambridge's UCAS date) are not news items; the explorer shows each university's next upcoming deadline from its requirements file, and the university page marks past dates «انتهى».
- News items may carry `page` (one of our pages) in addition to `source_url`.
**Alternatives:** Ministry website only as a source; SDAIA as a plain news link to the post; deadline news items per university.
**Why:** The owner says the official account posts first. The SDAIA misunderstanding is common enough that the explainer matters more than the announcement. Deadlines belong with the university they're for.
