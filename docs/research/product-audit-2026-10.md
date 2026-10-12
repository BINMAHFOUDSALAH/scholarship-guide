# Product audit: what واضح needs next (2026-10-12)

**How:**
- I read the live site and the code.
- Browser tests: Playwright/Chromium against the live site and locally.
- I measured page lengths on a 360px phone and walked the journey grade by grade.
- Research: Ministry, ETEC and program pages (read directly), and UX guidance from the 2026-10 redesign research ([ux-redesign-2026-10.md](ux-redesign-2026-10.md)).

**Limits:**
- No real students yet. Everything about student behaviour below is an **assumption to test**.
- Only Chromium was tested (no Safari or iPhone).
- A screen reader wasn't tested.

## 1. What works (verified)
- **Accessibility:** axe-core finds no violations on 13 key routes at 320 and 1280px in both themes. No sideways scroll at 320px.
- **The explorer:** search by major or university, filter tags, back to results, the phone filter toggle, and an error state. 33 browser checks pass.
- **Sourcing:** every official fact on the grade, program and university pages has a link. Tests enforce it, e.g. every external link on a grade page must be a declared source.
- **«قائمتي»:** stores ids in `localStorage` (`wadih:saved`), at most 100, ids validated. Unknown ids are dropped, corrupted storage doesn't break it, and it says without JavaScript that it needs JavaScript. 36 browser checks pass after this iteration.

## 2. «قائمتي»: the owner's questions, answered
| Question | Answer (tested in Chromium, live and local) |
|---|---|
| Storage | Browser `localStorage`, key `wadih:saved`, ids only. Nothing on our server. |
| Add, remove, refresh, revisit | Work. Saved items survive a refresh and a new visit in the same browser. |
| In sync across the finder, university page and list | Yes, including rows that arrive with a live search update, and other open tabs (the `storage` event). |
| Empty list | An empty state with how to save and a link to the finder. |
| Invalid data | Unknown or invalid ids are dropped and storage is cleaned. |
| Storage fails (private mode, blocked) | **Was a gap:** save buttons hid silently and /my-list showed nothing. **Now:** no save buttons (nothing pretends to save), and /my-list explains why. |
| Does it say the list doesn't travel? | Yes, on /my-list: «لا تنتقل إلى جهاز أو متصفح آخر، وتُحذف إذا مسحت بيانات المتصفح أو استخدمت التصفح الخاص». |
| Backend needed? | **No.** Accounts would only be needed to sync across devices (Launch 2). |
| **The real problem found** | **Nobody could find it:** you could save only from a university page, and the «قائمتي» link stayed hidden until the first save. **Fixed:** «احفظ» on every result row; the link is always in the header. |
| Not tested | Safari/iOS (only Chromium available here). WebKit announced a ["7-Day Cap on All Script-Writeable Storage"](https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/) (2020), so Safari users who don't visit for a week may lose the list. Unverified for our site; say so on /my-list if students confirm it. |

## 3. Findings, ranked
Scores: impact on students (H/M/L) · evidence (verified / assumption) · effort · maintenance.

### Fix now
| # | Problem | Evidence | Impact | Effort | Maintenance |
|---|---|---|---|---|---|
| 1 | «قائمتي» couldn't be found | Verified (code + test) | H | Done in this iteration | None |
| 2 | **Data goes stale silently.** All 65 dated checks are from 9–12 Oct 2026. Nothing warns when they get old, and deadlines like الرواد's 15 Nov pass. | Verified (data) | H: trust is the product | Small: a test that fails when `last_checked` is over 90 days, plus a list of what to re-check | Low |
| 3 | **Slow first visit.** Render's free tier "spins down a Free web service that goes 15 minutes without receiving any inbound traffic"; waking "takes about one minute" ([Render docs](https://render.com/docs/free)). A student's first click may wait a minute. | Verified (docs); not measured on our site | H for first impressions | **Owner decision:** a paid instance (costs money) | — |
| 4 | **Long pages on phones:** grade 12 is 12.6 screens at 360px, the program page 13.3, the explorer 10.8. | Verified (measured) | M | Medium: fold secondary sections; on grade 12, keep the timeline's other grades closed (already) and fold «تابع كل طلب» | Low |
| 5 | **Official sources differ on the number of tracks:** the Ministry e-service page lists six, the program site four. | Verified (agent, not re-read by me) | L | Small (owner decides what to show) | — |
| 6 | **Aramco's page can't be reached from the cloud environment**, so its facts are from 2026-10-11 (previous cycle). | Verified | M | Owner re-checks from a laptop | — |

### Consider building (worth it, but test with students first)
| # | Idea | Student problem | Evidence | Value | Cost |
|---|---|---|---|---|---|
| A | **"Copy my list as a link":** «قائمتي» ids in a URL, opened on another device | The list doesn't travel; students switch between phone and laptop | Our own limitation (verified); the need is an assumption | M | Small, no backend, nothing personal stored |
| B | **Compare saved universities** (SAT, IELTS, next date, lists, side by side) | Choosing between 5–8 universities means opening each page | Discover Uni lets users compare up to 7 (see the redesign research); our data exists for 30 | M–H | Medium: a table from data we already have |
| C | **إمداد requirements**, after the next guide | 223 universities say «لم نجمعها بعد» | Verified gap | H for إمداد students | Large (about 45 research batches) and the list may change. **Postponed by the owner until the new PDF** (reminder in the roadmap). |
| D | **Per-application status in «قائمتي»** (planning, applied, result) | Tracking many applications | Assumption | M? | Medium; more stored state |

### Postpone (not justified yet)
- **Accounts and cross-device sync:** the Launch 2 plan; a privacy cost for minors.
- **Email deadline alerts:** needs accounts and consent.
- **A chatbot:** the roadmap's later stage; needs verified content first.
- **Rankings and popularity sorting:** against the rule that the official list is the order; risk of dark patterns.
- **A full application planner:** wait for the usability test (Questions in [timeline-2026-10.md](timeline-2026-10.md) §5 and [grade-pages-2026-10.md](grade-pages-2026-10.md) §5).

## 4. The single best next implementation task
**The stale-facts check (Fix now #2).**
- واضح's whole value is official facts you can trust, and every check on the site is from the same week. Within three months they all reach 90 days old, and dated items (الرواد's 15 Nov, university deadlines) keep passing.
- A small test that fails CI when a fact is older than 90 days turns "remember to re-check" into something the project can't forget. It also gives the owner a re-check list before Launch 1 (~9 Dec 2026).
- It's small, it protects every page, and it needs no student validation.
- **Ahead of the alternatives:**
  - the "copy my list" link and the comparison need student evidence first
  - the cold start is a money decision, not a build
  - إمداد waits for the new guide

**Not code, but more valuable than any code:** the 3–5 student usability test. Every "assumption" above gets answered there.
