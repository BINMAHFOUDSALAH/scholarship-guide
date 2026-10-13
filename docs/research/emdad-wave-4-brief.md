# إمداد wave 4: the other US universities + India (research brief)

**Status:** done 2026-10-13 (decision 056): 22 of 25 saved. Not saved (403): Virginia, Pittsburgh, Colorado School of Mines. Same rules and save checks as [wave 2](emdad-wave-2-uk-brief.md) (decision 054) and the `research-wave` skill; this file lists only what differs.

**Scope:** the last 25 universities in English-speaking countries without a details file: US 18, India 7. After this wave, only the non-English-speaking countries remain (decision 055).

## Batches (one `source-researcher` agent each, on Haiku)
1. `arizona-state-university`, `university-of-colorado-boulder`, `university-of-massachusetts-amherst`, `boston-university`, `kansas-state-university`
2. `university-of-nevada-las-vegas`, `university-of-notre-dame`, `oregon-state-university`, `university-of-california-irvine`, `northeastern-university`
3. `university-of-virginia`, `virginia-polytechnic-institute-and-state-university`, `university-of-pittsburgh`, `gallaudet-university`, `george-washington-university`
4. `digipen-institute-of-technology`, `babson-college`, `colorado-school-of-mines`, `indian-institute-of-science`, `amity-university`
5. The five IITs: Delhi, Madras, Kanpur, Bombay, Kharagpur

(Exact ids: `data/universities.json`.)

## United States (same shape as wave 1, example `data/university_details/brown-university.json`)
- Fields: `platform` (Common App / Coalition / own portal), `english`, `sat_act` (required / optional / not_considered, for international first-year applicants), `dates` (Early Decision / Early Action / Regular Decision for Fall 2027; `event_ar` «آخر موعد للتقديم» with the round in `round_ar`), `acceptance_rate` (only an official figure, e.g. the Common Data Set), `application_fee` (`fee_usd`, `waiver` one of `accepts_common_app` / `own_waiver` / `domestic_only` / `none` / `not_stated`, `note_ar`, `source_url`).
- `saudi_certificate`: only if the international admissions page names Saudi Arabia or the Saudi certificate. US universities usually don't; then leave it out.

## India
- Foreign nationals enter Indian institutes through special routes, not the normal Indian exams. Find, on the institute's own site, the **route for international / foreign-national undergraduate applicants**: for IITs, direct admission of foreign nationals (often via JEE Advanced or a dedicated scheme; DASA covers NITs, not IITs); IISc offers a Bachelor of Science (Research) with its own channels; Amity has an international admissions office.
- Record that route in `platform.value_ar`, English and SAT rules if stated, the deadline for August 2027 entry if stated, and whether the Saudi certificate is accepted (`saudi_certificate`, same true/false/null rule).
- If an institute says foreign nationals can't join its bachelor's programmes, report that with the quote.
