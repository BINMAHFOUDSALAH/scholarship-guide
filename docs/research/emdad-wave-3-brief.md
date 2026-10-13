# إمداد wave 3: Australia, Canada, Singapore (research brief)

**Status:** done 2026-10-13 (decision 055): 16 of 23 saved. Not saved (403 everywhere): Melbourne, Griffith, Monash, Deakin, Macquarie, Alberta, SMU. Same rules and save checks as [wave 2](emdad-wave-2-uk-brief.md) (decision 054); this file lists only what differs.

**Scope:** 23 universities in the إمداد lists without a `data/university_details/<id>.json`: Australia 13, Canada 8, Singapore 2.

## Batches (one `source-researcher` agent each, on Haiku)
1. `the-university-of-queensland`, `australian-national-university`, `university-of-melbourne`, `griffith-university`, `the-university-of-sydney`
2. `the-university-of-western-australia`, `monash-university`, `curtin-university`, `the-university-of-new-south-wales-unsw-sydney`, `adelaide-university`
3. `deakin-university`, `macquarie-university`, `rmit-university`, `nanyang-technological-university-singapore-ntu`, `singapore-management-university`
4. `university-of-british-columbia`, `university-of-waterloo`, `universite-de-montreal`, `university-of-alberta`
5. `university-of-calgary`, `mcgill-university`, `university-of-guelph`, `university-of-saskatchewan`

## What differs from the UK
1. **Saudi certificate:** Australian and Canadian universities often publish a country table (e.g. "Saudi Arabia: General Secondary Education Certificate, 85% average"). `direct_entry: true` is now possible, but only when the page says the certificate is accepted for year-1 entry; copy the grade exactly. Same `false`/`null` rule as wave 2.
2. **Intake and deadlines:** no shared deadline. Record the university's own international application deadline for bachelor's entry, with the intake it's for:
   - Canada: Fall (September) 2027 → `entry_ar: "القبول لخريف 2027"`, `cycle_ar: "خريف 2027"`.
   - Australia: the academic year starts in February/March. A Saudi student finishing in June 2027 enters in July 2027 (Semester 2) or February/March 2028 (Semester 1). Record whatever deadline the page states and name its intake in `cycle_ar` (e.g. «الفصل الثاني 2027 (يوليو)»); set `entry_ar` to match.
   - Singapore: August 2027 intake; NTU and SMU publish application windows per qualification.
   - `event_ar` is «آخر موعد للتقديم» only for the general bachelor's deadline; course-only dates use a different wording.
3. **Platform:** state the real route: the university's own portal, OUAC (Ontario: Waterloo, Guelph; international applicants use the 105 form), UAC/VTAC/QTAC (Australian admissions centres, often optional for internationals), or the university portal (Singapore).
4. **SAT/ACT:** research it properly for Singapore and Canada (some ask Saudi-system applicants for SAT). Use `required`/`optional`/`not_considered` only with a quote; otherwise leave `sat_act` out.
5. **Université de Montréal teaches in French.** Fill `language_note_ar` with the language of instruction and the French requirement, from its own page.
6. Acceptance rate: skip.
