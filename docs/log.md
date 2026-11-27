# Project notes

See [plan.md](plan.md) for the current roadmap and [CLAUDE.md](../CLAUDE.md) for project instructions.

- Redesign review still to verify: a real iPhone in Safari and a screen-reader walkthrough. Playwright's WebKit isn't installed on the development machine, so `--webkit` runs were not done for the «سؤالك» pass (2026-11-26).
- The Saudi certificate for year 1 at UCL, Imperial and King's College London is still unconfirmed: their pages refused automated reading (2026-11-26). Check them in a browser (UCL's country page for Saudi Arabia, Imperial's accepted qualifications, King's prospectus selector) and record `direct_entry` with the quote. Oxford's own pages also refused the re-check; UCAS confirmed its 15 October 2026 deadline.
- No university record holds a verified degree title or an official program directory (2026-11-27), so search results don't show one; الرواد's group says the program name is the student's to confirm. Add them to `data/university_details/` with the source before showing a title as verified.
- The comparison names each per-university source by its site (`compare.site_of`): a source on a content network shows «ملف PDF». Add a host to `_FILE_HOSTS` when a new one appears.
- Before the وضّاح pilot, check any unresolved university requirements used in its test cases. Start with the [requirements audit](research/requirements-audit-2026-10-13.md).

Record a note here when a decision or verification gap will matter in a future session.