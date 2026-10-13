# University requirements audit (2026-10-13)

**Why:** the owner found Georgia Tech's IELTS shown as 6 while a Georgia Tech page said 7. This audit checks every requirement واضح shows for the 129 universities in `data/university_details/`, not just that one. Decision 058 records what changed in the data model and the pages.

## How it was checked

1. **Every cited page fetched once** (456 URLs, `curl` from this cloud session; pages that block `curl` or render with JavaScript were retried in headless Chromium). 433 opened with `curl`, 9 more in Chromium.
2. **Mechanical check of every displayed number against its own cited page:** IELTS / TOEFL / Duolingo scores (near the test's name), application fees, dates (day + month), acceptance rates (recomputed from Common Data Set C1 rows: applicants and admits summed by sex), Saudi-certificate quotes, SAT/ACT policy keywords.
3. **Semantic review of every English requirement by hand:** the text around each score on the official page was read to decide what the number *means*: a stated minimum, a recommended / competitive / expected score, a state-system floor, a level that depends on the program, a per-skill minimum, or a test the university doesn't accept.
4. **Every "not found" mismatch from step 2 was opened and read**, and either confirmed (the checker was too strict: tables, embedded JSON, a long distance between label and number) or corrected.

Not done: no source was taken from search snippets or third-party sites. Pages that refused every automated read are listed below as unverified, not guessed.

## Results

| | Count |
|---|---|
| Requirement files audited | 129 |
| Displayed facts checked mechanically | 638 (587 matched directly; the rest checked by hand, below) |
| Acceptance rates recomputed from CDS C1 | 27 of 27 exact (incl. Northwestern, whose third row the checker missed) |
| Files corrected | 76 (incl. the 2 drafts) |
| Files hidden until verified (drafts) | 2 (Oxford, UCL) |

### Georgia Tech, the reported case
- **Georgia Tech's first-year page** sets no score of its own: "The University System of Georgia requires that all international applicants demonstrate English proficiency using one of the USG approved methods" ([GT](https://admission.gatech.edu/international/first-year)).
- **USG's table** gives IELTS **6 minimum, 6.5 recommended** (TOEFL 3.5 / 4.0 on the new scale) ([USG](https://www.usg.edu/international_education/esl_programs/english_proficiency_requirements)).
- **The 7.0** is Georgia Tech's **graduate** requirement: "IELTS Academic Overall Band Score 7.0, Writing 5.5, Speaking 6.5, Listening 6.5, Reading 6.5" ([GT catalog, graduate](https://catalog.gatech.edu/admissions/grad/english-proficiency-intl-students/)).
- So the number 6 was right for a first-year applicant, but a bare «6» was misleading: it hid that it is a system floor, that 6.5 is recommended, and why the student had seen 7. The page now shows «الحد الأدنى 6.0 · الموصى به 6.5» and explains the 7.0.

### Corrected: a score shown as a minimum that the university calls something else
| University | Was | Now | Official wording |
|---|---|---|---|
| UCLA | 7.5 | min 6.5 (UC), recommended 7.5 | "We look for competitive English proficiency scores… 7.5 or above on the IELTS" ([UCLA](https://admission.ucla.edu/apply/international-applicants)); UC minimum 6.5 ([UC](https://admission.universityofcalifornia.edu/admission-requirements/international-applicants/english-language-proficiency-toefl-ielts.html)) |
| Cornell | 7.5 | recommended 7.5 | "IELTS Academic — minimum competitive score: 7.5" ([Cornell](https://admissions.cornell.edu/resources/submit-english-language-proficiency)) |
| Purdue | 6.5 | recommended 6.5 | "Generally, applicants have a score of 6.5 or higher" ([Purdue](https://admissions.purdue.edu/become-student/english-proficiency/)) |
| USC | 7 | recommended 7 (TOEFL 5 likewise) | "Applicants are admissible with scores below the recommended minimums, although at reduced rates of admission" ([USC](https://admission.usc.edu/prospective-students/how-to-apply/international-students/)). Duolingo stays a hard minimum: "You must achieve a minimum score of 130", and only for students who can't sit an approved exam |
| Tokyo (Design) | 6.0 | recommended 6.0 | expected scores, not cut-offs ([UTokyo](https://design.adm.u-tokyo.ac.jp/admissions/admissions-overview-2027/)) |
| JHU TOEFL | 5 (min) | recommended 5 | "To be competitive, applicants should typically receive…" ([JHU](https://apply.jhu.edu/how-to-apply/application-deadlines-requirements/standardized-testing/)) |

And the reverse: NYU, Duke, JHU (IELTS), Yale, Penn and UNC showed «لا حد أدنى منشور» with the competitive number hidden in a note; they now show it as «الموصى به».

### Corrected: hidden or contradictory facts
- **WashU** was marked "conflicting sources, no number". The two pages don't conflict: the university-wide minimum is IELTS 6.5 / Duolingo 125 ([OISS](https://oiss.washu.edu/english-proficiency-requirements/)), and admissions says its most competitive applicants have 7.0 / 130 ([WashU](https://admissions.washu.edu/how-to-apply/english-testing-requirements/)). Now min + recommended. TOEFL: OISS's line is ambiguous ("5.0 overall (new scale) OR 4.5 ≥ 90"), so only the recommended 5.0 is shown.
- **UNSW:** "The new TOEFL format is currently under review and is not being accepted until further notice" ([UNSW](https://www.unsw.edu.au/study/how-to-apply/english-language-requirements)). Wadih showed TOEFL 90 with no warning.
- **UWA, Curtin:** only the old 0–120 TOEFL score was shown; both publish the new 1–6 requirement (4.5). Now shown, with the old score in the note.
- **Toronto:** publishes a Duolingo minimum (120, with 120 in Production) that wasn't shown; its country table lists "Saudi Arabia — Minimum Admission Requirements: General Secondary Education Certificate" ([UofT](https://future.utoronto.ca/international-high-school-requirements-country?page=5)), now the Saudi-certificate row (was under «لغة الدراسة»).
- **Boston University:** competitive TOEFL (5.0) and Duolingo (125–135) now shown as recommended.
- **Duolingo not accepted** (now «لا تقبله الجامعة»): Georgia Tech (doesn't satisfy the USG requirement), Michigan, RMIT, UNSW, King's College London (exhaustive lists without it).
- **Cambridge SAT:** the 1500/750 and 1460/730 thresholds are no longer on Cambridge's page (it now says "a high score on the SAT or ACT"); the numbers were removed. Its Saudi guidance ("Applicants with the Tawjihiyah alone will not be competitive", updated June 2026) moved from «لغة الدراسة» to the Saudi-certificate row; admission tests got their own row.
- **Imperial:** a published TOEFL note said "we'll check this before publishing"; the page does map Standard → 92 / 4.5 and Higher → 100 / 5.0. Its SAT note quoted an unverified search result; removed.
- **Fees:** Harvard ($95) and MIT ($75) were right but cited pages that don't state the amount; now cite [Harvard](https://college.harvard.edu/admissions/apply) and [MIT](https://mitadmissions.org/apply/firstyear/deadlines-requirements/) (the waiver pages stay as a second link). UW's fee page was a 404; now [UW how to apply](https://admit.washington.edu/apply/first-year/how-to-apply/) ($95, no waiver for international students).
- **UChicago:** dates, platforms and English policy were from snippets; now verified in Chromium (ED I / EA 2 Nov 2026, ED II 4 Jan 2027, Common App or Apply Coalition, no minimum, no ESL). QuestBridge removed from the platform line (a US programme).
- **NUS:** snippet-based notes replaced by the rendered page: for "Other High School Qualifications", SAT/ACT/AP required and no English test; whether the Saudi certificate falls in that group isn't stated.
- **Five files** (Temple, Delaware, Minnesota, Nebraska, WSU) had English conditional-admission notes under «لغة الدراسة»; moved to the English row.

### Hidden until verified (pages refuse every automated read: curl, WebFetch and Chromium all 403)
- **Oxford, UCL:** their English scores, Saudi-certificate notes and some dates came from search snippets and were published with "needs checking" notes. Both files are now drafts (`"draft": true`), shown only with `WADIH_SHOW_DRAFTS=1`. **Owner:** open these in a browser and confirm, then remove `draft`:
  - Oxford [English requirements](https://www.ox.ac.uk/admissions/undergraduate/applying-to-oxford/for-international-students/ELR): IELTS 7.5 with 7.0 in each skill? TOEFL: new 1–6 format accepted or not?
  - Oxford [international qualifications](https://www.ox.ac.uk/admissions/undergraduate/courses/admissions-requirements/international-qualifications): what it says about Saudi Arabia.
  - UCL [English requirements](https://www.ucl.ac.uk/prospective-students/undergraduate/application/entry-requirements/english-language-requirements) (Level 1 = 6.5 with 6.0?) and its Saudi Arabia country page (from UCL's international-students section; we have no verified link for it).
- **Michigan:** English verified (rendered page); deadlines and SAT/ACT policy came from snippets (pages 403) and are hidden.
- **Columbia:** its SAT/ACT note quoted "summaries" with no source; hidden.

### Not re-verified in this pass (shown as before; check from a browser)
- **NYU** (every page 403): fee $85, ED I 1 Nov, ED II 1 Jan, RD 5 Jan, SAT optional, competitive English scores.
- **Stanford** English pages (403); its SAT policy and fee were verified.
- **Saskatchewan** deadline (1 May 2027): behind an interactive country selector.
- **Purdue, Houston** acceptance rates (Excel files), **Delaware, Maryland** (PDFs with no text layer).
- **Stanford** acceptance rate cites the CDS index page, not the PDF itself.

## What the model now distinguishes (decision 058)
`english.<test>`: `min` (the stated minimum for full admission), `recommended` (recommended / competitive / expected; never a cut-off), `recommended_source_url`, `each_min` (a uniform per-skill IELTS minimum), `varies` (the level depends on the program; `min` is the general or lowest), `accepted: false` (the university doesn't accept the test). The page explains «الحد الأدنى» and «الموصى به» once, under the scores, and every TOEFL score says which scale it's on.

## Repeatable checks
- `tests/test_universities.py` now enforces the model (recommended > min, per-skill ≤ overall, refused tests have no score) and fails if a published file mentions a search snippet («مقتطف», «ملخص البحث», «نتيجة البحث», «قبل النشر») or puts the Saudi certificate under «لغة الدراسة».
- `scripts/stale_facts.py` still lists every check date.
- The fetch + check scripts used here were one-off (scratch); worth turning into `scripts/check_sources.py` if this audit is repeated (P2).
