---
name: update-site
description: Bring واضح up to date. Find and add what's new (واعد programs, new rounds of الرواد/إمداد, Aramco, KAUST KGSP, SDAIA, a new universities guide), clear what's past, re-check what's due, and fix broken pages and links, all from official pages. Use when the owner says /update-site, "update the site", "check for new stuff", or sends a new announcement (a screenshot or link).
---

# Update the site

The owner runs this when they want the site current (decision 064), often after the morning «Site check» issue on GitHub pinged them. That issue is the alarm and lists the same findings; this skill does the work. Work in the main session; a `source-researcher` agent is worth it only when more than ~5 new items need research (CLAUDE.md). Never commit or push unless the owner asks.

## 1. Find what changed
- `pytest -q` first. If it's red before you change anything, that's the first bug to fix.
- `python scripts/watch.py` (about 2 minutes). It compares the data with the official pages and the live site and lists what to act on, **urgent first** (a new announcement, a changed official page, a broken page), then routine (past or due for a re-check, broken links, facts over 90 days). That list is your starting to-do. Run it yourself rather than copying the GitHub issue, which may be from this morning.
- It can't see X posts, Aramco's page (it refuses scripts) or pages without a watch phrase. Step 2 covers them.

## 2. Go through every program, even when the check found nothing
Read each program's official page directly (`curl` to stdout, `scripts/check_quote.py`, or WebFetch for pages built with JavaScript). Never use search snippets. A screenshot or forwarded message from the owner tells you where to look; the facts come from the official page.

| Program | Where it lives | Official pages | Look for |
|---|---|---|---|
| Custodian scholarship: الرواد | `data/paths.json` › custodian-scholarship › `arruaad` | [scholarship site](https://sites.moe.gov.sa/scholarship-program/) and its «الشروط» pages; X [@SA_Scholarships](https://x.com/SA_Scholarships) | still open? a new deadline? the next round? |
| Custodian: إمداد | › `emdad` | same | an opening announcement, its dates |
| Custodian: واعد | `data/waaid_programs.json` | [واعد page](https://sites.moe.gov.sa/scholarship-program/paths/path-waaid/) | new announcements (step 3a) |
| Custodian: universities guide | `data/universities.json`, `universities_guide_url` in `paths.json`, `data/news.json` | the scholarship site's «الدليل الاسترشادي» link | a new edition (2027–2028, expected Dec 2026/Jan 2027): follow the roadmap's «When the next universities guide PDF is out» steps |
| Aramco CDPNE | `data/paths.json` › `aramco-cdpne` | [CDPNE page](https://www.aramco.com/ar/careers/for-saudi-applicants/student-opportunities/college-degree-program) | 2026–2027 registration dates, changed requirements. `curl` fails here; try WebFetch, and if that fails too, ask the owner to open it in a browser and paste the text |
| KAUST KGSP | `data/paths.json` › `kaust-kgsp`, `content/programs/kaust-kgsp.md` | [Prospective Students](https://kgsp.kaust.edu.sa/prospective-students) | Cohort 19 dates (the page says «will open soon»; its FAQ still shows Cohort 18) |
| SDAIA AI scholarship | `data/paths.json` › `sdaia-ai-scholarship`, `content/programs/sdaia-ai-scholarship.md` | [SDAIA page](https://sdaia.gov.sa/ar/Sectors/BuildingCapacity/Pages/ScholarshipProgram.aspx); X [@SDAIA_SA](https://x.com/SDAIA_SA) | closing date, a new cohort |
| A program added later | its `paths.json` entry | its `status_source` and `official_url` | the same questions |

X can't be read by scripts. List what needs an X check for the owner, or ask them to paste the post.

## 3. Make the changes
**a. New**
- **A واعد announcement:** one entry per program at the **top** of `data/waaid_programs.json`, in the same shape as `sar-railway-training` (the example).
  - `id`: short, lowercase, stable (it's the program's link on `/waaid`; never rename it later).
  - `for_high_school`: `true` only if the page accepts a high school certificate. A bachelor's or master's requirement means `false`.
  - `requirements_ar`: the academic and English requirements in formal Arabic, minimums as «لا يقل عن». Copy unclear values exactly as the page writes them; don't interpret.
  - `level_ar`: one of the values already used. If the page gives the institution only in Arabic, add an `institution_note`. Set `checked` to today.
- **A track opens:** `status: "open"`, `status_source` (the official link), `status_until` only if an official source or the owner gives it (then `owner_confirmed`), `apply_with_ar`, `status_note`, `last_checked`.
- **A new round's requirements (Aramco, KGSP, SDAIA):** update the facts in `paths.json` and the program's page in `content/programs/`, with `last_checked` set to today and `owner_reviewed: false`.

**b. Past.** The site already closes things by their dates. A track past `status_until` shows «أُغلق» with that date, and a university's past date gets «انتهى». Don't edit what the site handles.
- A track past its deadline: leave its `status`. Look for the next round, and add it when it's announced (3a).
- واعد programs the check lists as closed over 120 days ago: remove them from `data/waaid_programs.json`.
- A university whose dates have all passed: add the next round's dates from its admissions page when they're published (the `research-wave` rules for dates). Until then, leave it.
- Page text that is now wrong ("opens in …", "this year's guide …"): `grep` in `content/` and `data/home.json` for the months that have passed, and fix the wording.
- An outdated item in `data/news.json` (e.g. the guide after a new edition): update or remove it.

**c. Re-checks.** An open track with no deadline, or a fact over 90 days old: read its source again. If nothing changed, update only the date (`last_checked` / `checked`).

**d. Bugs.** A failing test: fix the cause, never the test. A live page that isn't 200: find the cause; Render's logs are the owner's to check. A 404 official link: find the page's new address on the official site.

**Rules that always apply:** what couldn't be read on an official page isn't published (keep it in a `"draft": true` file or leave it out). If two official sources disagree, show both and publish no single answer. Formal Arabic only.

## 4. Keep the check accurate
After acting on a watched page, update its phrase in `scripts/watch_pages.json` (new `expect` text and `confirmed_on`). For example, when KGSP publishes Cohort 19 dates, watch for the next change. Add a phrase for any newly awaited page.

## 5. Verify
- `pytest`, then `python scripts/watch.py --offline`. What you fixed should be gone from the list.
- Browser at 390px for each changed page (`/waaid`, the homepage, the program's page): the right status and «لمن», «تقدم الآن» only while open, no sideways scrolling.

## 6. Report to the owner
- A short table: **added**, **removed**, **updated**, **re-checked and unchanged**, **couldn't check** (owner to-dos: X posts, Aramco in a browser).
- What's time-sensitive: windows closing soon (the check's FYI lines). Open windows mean merge soon.
- `docs/decisions.md` only if a rule changed; the roadmap's next-session note if something big changed.
- Ask before committing. Once the owner merges, the next morning's check closes the GitHub issue by itself if nothing urgent is left.
