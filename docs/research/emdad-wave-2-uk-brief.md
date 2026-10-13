# إمداد wave 2: UK universities (research brief)

**Status:** done 2026-10-13 (decision 054). 26 of 29 saved. Not saved: Durham and Bournemouth (403 on every page, from the cloud session and from the agents), and London Business School (no bachelor's listed, but not stated). Reusable for wave 3: replace the batches and the UK-specific items.

**Scope:** the 29 UK universities in the إمداد lists that have no `data/university_details/<id>.json` yet. Oxford, Cambridge, Imperial and UCL (الرواد) are done. Bangor, Cardiff and Queen Mary are listed only under البحث والتطوير and are out of scope.

## Batches (one `source-researcher` agent each, on Haiku, run in parallel)
Ordered by best إمداد rank, so the most-searched universities come first.
1. `the-university-of-edinburgh`, `the-london-school-of-economics-and-political-science-lse`, `king-s-college-london`, `university-of-birmingham`, `london-business-school`
2. `university-of-surrey`, `university-of-manchester`, `the-university-of-warwick`, `university-of-leeds`, `durham-university`
3. `university-of-st-andrews`, `university-of-bristol`, `university-of-glasgow`, `university-of-strathclyde`, `lancaster-university`
4. `university-of-york`, `university-of-greenwich`, `university-of-nottingham`, `the-university-of-sheffield`, `the-university-of-exeter`
5. `bournemouth-university`, `university-of-sussex`, `university-of-essex`, `university-of-southampton`, `soas-university-of-london`
6. `university-of-reading`, `newcastle-university`, `university-of-liverpool`, `university-of-derby`

## What matters for a UK university (in this order)
1. **The Saudi secondary certificate (الثانوية العامة / Tawjihiyya):** accepted for direct entry to year 1, or only after a foundation year, or not stated. Most UK universities have a "Saudi Arabia" page under international / country pages; read that page. Copy any grade (e.g. "85%") exactly, and say if it varies by course. This is the most useful fact for a Saudi student.
2. **English:** IELTS Academic overall and the minimum per component, for the lowest band (most universities have bands A/B/C or levels by course; record the lowest and say that it varies). TOEFL iBT and Duolingo only if the page states them.
3. **Platform:** UCAS, with the institution code if stated.
4. **Deadline:** the UCAS equal-consideration deadline for 2027 entry, read on ucas.com once (one source for all). Course-specific earlier deadlines (medicine, dentistry, Oxford/Cambridge-style) only if the university's page says so.
5. **SAT/ACT:** usually not relevant to Saudi-system applicants. Use `not_applicable` only if the page says the Saudi certificate (or "international qualifications") route doesn't need it; otherwise `unknown`.
6. **Undergraduate at all?** London Business School may teach postgraduate only. If the official page says there are no bachelor's degrees, report that and nothing else.
7. Acceptance rate: skip unless the university publishes an official figure for international or all applicants.

## Rules for the agents (on top of `.claude/agents/source-researcher.md`)
- Read each page itself (WebFetch, else `curl`). **A search snippet is never a source.** If the page won't open, the fact is not found. (The الرواد files for Oxford and UCL used snippets after 403s; don't repeat that.)
- Every fact: URL read, today's date, a short exact English quote.
- Return the JSON shape of `data/university_details/ucl-university-college-london.json` (the finished example) plus one new block per university, `saudi_certificate`:
  ```json
  "saudi_certificate": {"direct_entry": true | false | null,
                        "note_ar": "…the grade and any course exceptions, in Arabic…",
                        "quote": "…exact English words…",
                        "source_url": "https://…"}
  ```
  `null` = the page doesn't say. Never infer it from another university.
- End with: what couldn't be verified and why.

## Save checks (main session)
- Each file passes `pytest tests/test_universities.py` (schema, https sources, ISO dates, `year_stated`).
- Spot-check 1 fact per university against its quote before saving.
- `saudi_certificate` is new: before saving, add it to the schema in `docs/specs/universities-explorer.md`, to the test, and to `university.html` as its own row («الشهادة الثانوية السعودية»). Don't put it in `language_note_ar`, which the page labels «لغة الدراسة».
- Run `scripts/stale_facts.py --all` afterwards: the count should rise by the number of files saved.
