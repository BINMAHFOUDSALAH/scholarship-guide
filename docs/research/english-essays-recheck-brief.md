# English tests re-check + US essays (research brief)

**Status:** done 2026-10-16 (decision 061). 14 agents; every saved value's quote checked on its page.
- **Saved:** English updates for 33 universities (13 of them Duolingo `listed: false`), and essays for 56 US universities (+ 6 UC campuses from UC's page; every UK file from UCAS).
- **Not saved:** Columbia's English (every page 403), NUS (bot wall), Michigan's and Gallaudet's essays (403), Northeastern, Oregon State and UNLV essays (not on a public page), Temple (two official pages disagree: optional vs required essay).
- **Kept null on purpose:** the Duolingo rows of UGA (read only through WebFetch), Edinburgh and Glasgow IELTS numbers (per programme only).

**Why:** 35 published university files leave IELTS, TOEFL iBT or Duolingo empty (`null`): the site then says «لم نتحقق منه». And no file says what essays a university asks for. Both are among the first things a Saudi applicant needs.

## Part A: English tests (batches A1–A6)
For each university, fill **only the tests listed as missing** in your batch. Read the university's own undergraduate English-language page (for the UK and Australia it is usually a page or PDF of "English language requirements" with bands/levels/profiles).

Rules (decision 058, do not deviate):
- `min` only for a stated minimum. "Competitive", "recommended", "expected", "typically", "most admitted students" → `recommended`.
- Program-dependent levels → the lowest undergraduate level as `min` plus `"varies": true`, and say in `note_ar` which level it is.
- A per-skill minimum → `each_min` (IELTS only).
- The page says the test is not accepted → `"accepted": false`, `min: null`.
- The page says the university has no English-test requirement, or doesn't publish a minimum → `min: null` with a `note_ar` saying exactly that.
- The page doesn't mention the test at all → report `not_found` (we keep `null`). Never infer from another university, an agency, or a graduate page.
- TOEFL iBT: since 21 January 2026 it has a 1–6 scale. Copy whichever scale the page gives; if it gives both, record the 1–6 value as `min` and mention the 0–120 value in `note_ar`.
- Duolingo: copy the overall score and any subscore minimum ("Integrated subscores", "Literacy"…) into `note_ar`.

Return per test:
```json
"duolingo": {"min": 110, "recommended": null, "varies": false, "accepted": true,
             "note_ar": "…Arabic…", "source_url": "https://…",
             "quote": "…exact English words…"}
```

## Part B: US essays (batches E1–E8)
For each US university, the writing it asks first-year applicants for, **for fall 2027 entry** (2026–27 cycle) if published, otherwise the latest cycle the page states (say which).
- Read the university's own admissions page (often "Essays", "Writing supplement", "Application requirements", "Questions"). Common App's public pages may also be used (commonapp.org); a login-only page can't.
- Return:
```json
"essays": {"cycle_ar": "خريف 2027",
           "personal_essay": "common_app" | "coalition" | "own" | "none" | null,
           "count": 2,
           "summary_ar": "…in Arabic: how many supplemental essays / short answers, their word limits, whether optional…",
           "quote": "…exact English words…",
           "source_url": "https://…"}
```
  - `count` = required university-specific essays plus short answers; `null` if the page doesn't let you count them. Optional prompts don't count; mention them in `summary_ar`.
  - Summarise prompts in Arabic in a few words each; **never copy prompts in full**.
  - No supplemental essays, stated → `count: 0` with the quote.
  - If you can't find a public official page with the essays → `not_found`.

## Rules for every agent (on top of `.claude/agents/source-researcher.md`)
- Read the page itself: WebFetch, else `curl -sL -m 30 -A "Mozilla/5.0" URL` **to stdout only** (never `-o`, `>`, `tee`; agents have written files into the repo before).
- A search snippet is never a source. A page you couldn't open → not found.
- Every number, date and yes/no needs an exact quote (in the page's words) + the URL read. Today's date is 2026-10-16.
- Undergraduate first-year international applicants only.
- Example of a finished file: `data/university_details/the-university-of-exeter.json` (English) and `data/university_details/stanford-university.json` (a US file).
- End with: **what you could not verify, and why**.

## Batches
**A1** adelaide-university (toefl_ibt, duolingo) · australian-national-university (duolingo) · curtin-university (duolingo) · the-university-of-queensland (duolingo) · the-university-of-sydney (toefl_ibt, duolingo) · universite-de-montreal (all three)
**A2** nanyang-technological-university-singapore-ntu (all three) · national-university-of-singapore-nus (all three) · lancaster-university (duolingo) · the-london-school-of-economics-and-political-science-lse (duolingo) · university-of-cambridge (duolingo) · university-of-derby (duolingo)
**A3** the-university-of-edinburgh (all three) · the-university-of-sheffield (all three) · university-of-glasgow (all three) · university-of-nottingham (all three) · university-of-birmingham (duolingo) · university-of-bristol (duolingo)
**A4** university-of-southampton (all three) · university-of-surrey (all three) · university-of-york (all three) · university-of-essex (duolingo) · university-of-leeds (duolingo) · university-of-liverpool (toefl_ibt)
**A5** university-of-manchester (toefl_ibt, duolingo) · university-of-reading (toefl_ibt) · babson-college (all three) · columbia-university (all three) · gallaudet-university (all three) · northeastern-university (all three)
**A6** texas-a-m-university (all three) · the-university-of-georgia (duolingo) · university-of-florida (duolingo) · university-of-south-florida (all three) · virginia-polytechnic-institute-and-state-university (toefl_ibt)

**E1** arizona-state-university · babson-college · boston-university · brown-university · california-institute-of-technology-caltech · carnegie-mellon-university · colorado-state-university · columbia-university
**E2** cornell-university · digipen-institute-of-technology · duke-university · florida-state-university · gallaudet-university · george-washington-university · georgetown-university · georgia-institute-of-technology
**E3** harvard-university · indiana-university-bloomington · iowa-state-university · johns-hopkins-university · kansas-state-university · massachusetts-institute-of-technology-mit · michigan-state-university · new-york-university-nyu
**E4** north-carolina-state-university · northeastern-university · northwestern-university · oregon-state-university · pennsylvania-state-university · princeton-university · purdue-university · stanford-university
**E5** temple-university · texas-a-m-university · the-ohio-state-university · the-university-of-georgia · university-of-central-florida · university-of-chicago · university-of-colorado-boulder · university-of-delaware
**E6** university-of-florida · university-of-houston · university-of-illinois-at-urbana-champaign · university-of-maryland-college-park · university-of-massachusetts-amherst · university-of-michigan-ann-arbor · university-of-minnesota-twin-cities · university-of-nebraska-lincoln
**E7** university-of-nevada-las-vegas · university-of-north-carolina-at-chapel-hill · university-of-notre-dame · university-of-pennsylvania · university-of-south-carolina · university-of-south-florida · university-of-southern-california · university-of-texas-at-austin
**E8** university-of-washington · university-of-wisconsin-madison · virginia-polytechnic-institute-and-state-university · washington-state-university · washington-university-in-st-louis · yale-university

The six University of California campuses share the Personal Insight Questions: the main session fills them from the UC page.
