---
name: research-wave
description: Research admission requirements for a batch of universities (an إمداد "wave") from official pages with source-researcher agents, verify every quote, and save data/university_details/<id>.json. Use when the owner says "start wave N", "research the <country> universities", or asks to fill requirements for universities that have no details file.
---

# Research wave (university requirements)

Done three times (US wave 1, UK wave 2, AU/CA/SG wave 3; decision 054). Follow these steps in order; each one exists because skipping it caused a problem before.

## 1. Scope
- List the universities in the إمداد/الرواد lists of the target countries that have no `data/university_details/<id>.json` (read `data/universities.json`; skip البحث والتطوير-only universities, they're doctorate-only).
- Probe 3–4 of their domains with `curl -s -o /dev/null -w "%{http_code}"`. If everything fails, the session's network policy blocks them: stop and tell the owner (they change Network access, or run it from the laptop). Never fall back to search snippets.

## 2. Brief
- Write `docs/research/emdad-wave-<n>-brief.md`: status, scope, batches of ~5 (best إمداد rank first, same country together), and only what differs from the [wave 2 brief](../../../docs/research/emdad-wave-2-uk-brief.md) (intake, deadline system, platform, SAT relevance, language of instruction).

## 3. Agents
- One `source-researcher` per batch, in parallel, `run_in_background: true`. Never pass a model (they run on Haiku via their own file).
- The prompt must include: read both briefs and `data/university_details/the-university-of-exeter.json` (the example); curl **to stdout only** (no `-o`, `>`, `tee`; agents have written files into the repo before); snippets are never sources; the `saudi_certificate` rule (true/false only when the page says so, else null); return JSON per university plus an evidence list (exact quote + URL for every number, date and yes/no).

## 4. Verify (main session)
- After each report: `git status`; delete any file an agent left (look at it first).
- For every university, check at least the Saudi-certificate quote and one number with `scripts/check_quote.py URL "quote" ...`. Anything MISSING is not saved.
- Decide the agents' open questions with the rules, not by preference:
  - `false` only on an explicit statement; foundation-only mentions → `null`, finding in `not_found_ar`.
  - Two official pages disagree → no number, both in the note.
  - A deadline without a year on the page → leave it out (or use an official source that states the year, e.g. UCAS).
  - `event_ar` is exactly «آخر موعد للتقديم» only for the general bachelor's deadline; course-only dates get other wording.
  - Drop "not published" claims for things nobody searched (acceptance rate).
  - No file at all for a university with nothing verified (403 everywhere).
- Notes: plain Arabic, don't repeat what the row label already says.

## 5. Save and check
- Write the files (`checked` = today, `name_en` exactly as in `data/universities.json`).
- `pytest` (schema tests cover every file), `scripts/stale_facts.py` (count rises by the number saved), and a look at 2 pages in the browser at 375px (one with the Saudi-certificate row, one without).
- Update: the brief's status, `docs/roadmap.md` (what's left), a decision only if a rule changed, `LEARNING_LOG.md` if something new was learned.
- Report: counts (saved / true / false / null / skipped and why), what wasn't checked, then ask before committing.
