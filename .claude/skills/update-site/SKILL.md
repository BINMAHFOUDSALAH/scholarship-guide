---
name: update-site
description: Refresh Wadih's published scholarship programs, application dates, university lists, and official source links. Use when asked to check for new announcements, verify current deadlines, or update published program data.
---

# Update Wadih's published information

## Find what changed

- For a site-wide refresh, run `python scripts/watch.py` and use its findings as a starting point. For a specific announcement or correction, start with the program or university the owner named.
- Check the relevant official pages directly. For a site-wide refresh, cover الرواد، إمداد، واعد، the official university guide, Aramco, KAUST, and SDAIA. A screenshot, forwarded message, or search result can help locate the original source.
- Verify the application cycle, audience, and published dates. If a source is inaccessible or official sources disagree, report what you could verify and where the gap is. Continue with the other sources in scope.

## Update the data

- Update program and track information in `data/paths.json` and the relevant pages in `content/programs/`. Record the official source and the actual date checked. If a fact is unchanged after rechecking, update its verification date.
- For new واعد announcements, follow the current schema in `data/waaid_programs.json`. Keep existing IDs stable because they are used in public links. Set high-school eligibility from the published qualifications.
- Use the site's existing date logic for openings and closures. Update wording that has become inaccurate and apply the existing retention policy for old واعد entries.
- If the Ministry publishes a new university guide, regenerate `data/universities.json` with `scripts/extract_universities.py`. Review additions and removals, update the guide link and year, and check affected pages and requirements. Use `research-wave` for batches that need deeper research.
- Update the English version alongside public Arabic changes. Preserve dates, numbers, conditions, and the distinction between required and recommended scores. Update `translated_from` when changing a translated Markdown page.
- Update `scripts/watch_pages.json` when a verified change makes a watched phrase stale.

## Verify and report

- Run `pytest` and `python scripts/watch.py --offline` after changes. Run the English checks when translations change. Report unrelated failures separately.
- For visible changes, check representative pages in the browser. Verify that the status, deadline, audience, and application link agree with the source.
- Summarize what was added, updated, removed, or rechecked. Flag information you could not verify and any deadlines that need prompt review.
- Follow the Git workflow in `CLAUDE.md`. Put verified changes on a branch and open a PR. Share the checks and leave the PR open for the owner to test and merge.