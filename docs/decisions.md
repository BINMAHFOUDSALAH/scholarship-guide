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
