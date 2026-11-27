---
name: research-wave
description: Research missing or outdated university admission requirements in batches. Use when asked to start a research wave, cover universities in a country, or fill gaps in Wadih's verified data.
---

# University requirements research

## Choose the scope

Use `data/universities.json` and the owner's request to identify the universities and gaps to cover. For a bachelor's research wave, exclude universities listed only for doctoral study. Use `docs/specs/universities-explorer.md` and a current details file as references for the schema. Keep a short brief under `docs/research/` for a wave that needs to continue across sessions.

## Find and verify evidence

- Use `source-researcher` for batches where delegation helps. Give it the universities, fields to check, and expected output. It returns evidence. The main session verifies it and writes any updates.
- Read official university, scholarship, admissions platform, or test-provider pages directly. Use search to find those pages. Record the URL, date checked, and a short excerpt supporting each claim.
- If a subagent cannot open a source, have it report the gap. The main session can try another official page or verify it in the browser. Continue with sources that can be read.
- Check that each fact applies to the intended institution, degree, program, applicant type, and cycle. Use `scripts/check_quote.py` where helpful, and read the surrounding text to verify what the quote means.

## Record findings accurately

- For `saudi_certificate`, record `true` or `false` when the source explicitly establishes whether the qualification is sufficient for direct entry. Use `null` when the evidence is unclear.
- Keep published minimums, explicit recommendations, and course-specific requirements distinct. Preserve phrases such as “typically admitted” or “competitive” in their original sense. Distinguish a test the page does not list from a test it explicitly rejects.
- Record deadlines when official evidence establishes the applicable year or cycle. Label course-specific dates clearly. When official sources conflict, record both and explain the discrepancy.
- Publish verified facts. Keep useful unverified findings in research notes or in records marked `"draft": true`.

## Save and verify

- Update `data/university_details/<id>.json` using the canonical university ID and name. Record the actual date checked. Add English translations for new public Arabic notes in `data/i18n/universities.en.json`, preserving numbers, conditions, and uncertainty.
- Run `pytest`, including the translation checks. Spot-check representative updated pages in the browser, especially when adding a requirement type or changing what a student sees.
- Report which universities were updated and which claims still need evidence. Follow the Git workflow in `CLAUDE.md`. Open the PR for the owner to review, test, and merge.