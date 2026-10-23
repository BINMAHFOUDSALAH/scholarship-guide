# الرواد top 30 + every US university: English tests, SAT, dates (research brief)

**Status:** done 2026-10-23. 7 agents (Haiku); every saved value's quote checked on its page by the main session (curl, or browser headers for Pitt and Mines). 25 files changed or created; 620 tests pass.
- **New files:** Pittsburgh, Colorado School of Mines. **Not saved:** Virginia (Cloudflare challenge on every page, nothing read).
- **Changed:** Columbia English + SAT (owner read the pages: every Columbia domain is 403); SAT policy filled or corrected for Kansas State, UCF (required), WSU (not considered), Michigan (optional, from umich's own support pages), Cambridge and Toronto (`optional` → `unknown`: the pages mention SAT only for US-curriculum applicants); English for USF (not accepted), NUS (IELTS 6.5, TOEFL 4.5, Duolingo not listed), Michigan source; ETH's 2027-03-31 deadline removed (no year on the page, conflicts with "31 March 2026"); Tsinghua round 2 opening date.
- **Confirmed unchanged (read via WebFetch, curl blocked):** Purdue, JHU, UGA, Colorado State, Northeastern.
- **Owner read in a browser (2026-10-23):** Oxford and UCL English pages match the files (Duolingo now `accepted: false`, owner confirmed); Oxford doesn't require SAT; UChicago SAT optional; UVA's international page (English tests strongly encouraged, no published minimum) → a UVA file with English and SAT (optional for Fall 2027, owner-confirmed; source the deadlines page, which blocks scripts). Not used: a UCL "SAT pathways" text (an AI summary, not the page) and a UChicago English table (Division of the Social Sciences, graduate programs only).
- **Not verifiable:** UChicago undergraduate English (JavaScript-only pages), UCL SAT, Gallaudet SAT (skipped by the owner), Peking/Zhejiang 2027 notices (not published yet).

**Why:** the owner wants IELTS, Duolingo and the SAT policy (required / optional / not considered) checked and cited for every الرواد university and every US university, and dates refreshed as of 2026-10-23.

**Scope:** 92 universities (30 الرواد + all US). 80 have a file; of the 12 without one, 9 are البحث والتطوير-only (doctorate, skipped) and 3 are on إمداد (Colorado School of Mines, Pittsburgh, Virginia: new full files, owner's choice).

**What was already confirmed automatically (2026-10-23):**
- `scripts/check_sources.py` on the 80 files: 364 of 403 published facts found on their cited page. 9 not found, 14 pages didn't open (listed per batch below).
- A scratch keyword check of each `sat_act.policy` against its cited page: ~50 consistent. The rest are listed below.
- English entries with no number (e.g. Harvard, Stanford, Northwestern: "accepted, no minimum published") are deliberate, sourced statements and stay.

## Rules
Same as the [English re-check brief](english-essays-recheck-brief.md) (decision 058, 061) and the `research-wave` skill. Also:
- SAT/ACT policy for **international first-year applicants entering fall 2027** (the 2026–27 cycle): `required` / `optional` / `not_considered` (test-blind) / `not_applicable` (the university doesn't use SAT at all for its own route, e.g. an entrance exam) / `unknown` (the page doesn't say). If a future cycle changes, say so in `note_ar`.
- Outside the US/Canada: SAT is a yes/no only if the page mentions SAT. Silence → report not found.
- Dates: only for the 2027 intake (fall 2027 / September 2027), with the year on the page.

## Batches (one `source-researcher` agent each, on Haiku)
1. **US pages that didn't check out:** `purdue-university` (IELTS rec 6.5, TOEFL 4.5, Duolingo rec 115, EA 2026-11-01, RD 2027-01-15 not found on cited pages), `university-of-chicago` (EA/ED1 2026-11-02, RD/ED2 2027-01-04 not found; SAT source is a CDS PDF that didn't open), `johns-hopkins-university` (all apply.jhu.edu pages didn't open), `the-university-of-georgia` (deadlines, fee, SAT pages didn't open; Duolingo empty), `colorado-state-university` (English and SAT pages didn't open)
2. **US gaps:** `university-of-south-florida` (IELTS, Duolingo empty), `gallaudet-university` (no SAT, Duolingo empty), `kansas-state-university` (no SAT), `university-of-central-florida`, `north-carolina-state-university` (SAT `unknown`)
3. **US gaps 2:** `washington-state-university` (SAT `unknown`), `university-of-houston` (SAT not confirmed on page), `university-of-michigan-ann-arbor` (no SAT; English page didn't open), `northeastern-university` (English page didn't open)
4. **UK + Switzerland:** `imperial-college-london` (TOEFL 4.5 not found; SAT `unknown`), `ucl-university-college-london` (English page didn't open; no SAT), `university-of-oxford` (English, international-qualifications and timeline pages didn't open), `university-of-cambridge` (SAT `optional` not confirmed on page), `eth-zurich` (2027-01-18 exam date not found; Duolingo empty; SAT `unknown`)
5. **China + Singapore:** `national-university-of-singapore-nus` (IELTS, Duolingo empty; SAT `unknown`), `peking-university` (IELTS, Duolingo empty; dates are for the 2026 intake), `tsinghua-university` (Duolingo empty; SAT), `zhejiang-university` (SAT; dates are for the 2026 intake; PDF didn't open)
6. **Japan, Canada, France:** `the-university-of-tokyo`, `university-of-toronto`, `universite-paris-saclay` (SAT not confirmed; Paris-Saclay Duolingo empty)
7. **New files (full, like wave 4):** `university-of-pittsburgh`, `university-of-virginia`, `colorado-school-of-mines`

**Columbia:** every Columbia domain returns 403 to curl and WebFetch. The owner read the English page and pasted it (2026-10-23); the SAT policy comes from Columbia's testing-policy update (the owner confirms the page).
