# The plan: from discovering واضح to being accepted

The owner's vision of 2026-11-16 and the steps to reach it, in order. **A session does the first step that is not marked done**, then marks it done here and adds its note to [log.md](log.md). One step per session.

Items marked **(proposed)** are Claude's recommendations that the owner has not confirmed: ask before building them.

## The vision

واضح is a bridge: from the moment a student finds the site to being accepted by a university and a scholarship. A student should always be able to see their options, what they qualify to apply for, what they still need, and the one thing to do next.

- **Two sequences, both supported.** Admission first, then the scholarship (الرواد, إمداد). Program first (Aramco, KAUST).
- **Personal without an account.** General information never needs sign-in. An account adds the AI guide and the plan on every device.
- **وضّاح is the guide.** Today a character on the page; later an AI mentor who answers only from verified information, shows his sources, says «لا أعرف», and never promises acceptance.
- **Trust is the product.** Every fact from an official source, read directly; anything unverified stays hidden (CLAUDE.md's rules).

## Part 1: finish the redesign (version 3, «عالم وضّاح»)

Rules: [.claude/rules/design.md](../.claude/rules/design.md). Each step is one page rebuilt in the new design, verified by tests and in the browser at phone and desktop width, both themes, Arabic and English.

| # | Step | What done looks like | Status |
|---|---|---|---|
| 1 | Foundation and homepage | New colours, typeface, buttons, header; وضّاح's question on the homepage; university deadlines in «الآن» | **Done** 2026-11-16 (PR 66) |
| 1b | Replace the four-point sparkle (owner, 2026-11-25) | The four-point star ([references/sparkle.png](../references/sparkle.png)) is gone everywhere on واضح, Arabic and English: templates, CSS, JS, SVGs, icons, data, content, marketing. In its place, a visual specific to واضح and a **different shape**, not a restyled sparkle. Where the sparkle meant a status or an action (new, now, featured, done…), the replacement says that meaning plainly. Search by eye too: it may be drawn in SVG or CSS, not typed as a character. Today `.claude/rules/design.md` makes the star a motif (a destination on the map, «المملكة»): rewrite that rule and its tests with the new shape | Next |
| 2 | «خطتي» as a dated roadmap | The student sees their stage, their next step (specific, not "open the page"), and their dates in order. Needs the owner's answer to decision A | After 1b |
| 3 | The university page | The answer first: is it on the list, what it requires, the next date. Details and sources below. Shorter on a phone than today (5,625px) | |
| 4 | The program page | The steps in order, for that program's sequence. The scholarship page is far shorter than today (13,742px, 67 links) | |
| 5 | The explorer | Shorter rows; compare up to three universities. The الرواد list is far shorter than today (12,757px) | |
| 6 | The remaining pages | Grade pages, guides, search, 404, «جرّب قبل أن تقرر»: each looked at and brought into the design; وضّاح's poses on empty and error states | |
| 7 | Review and student sessions | The review skills run on every rebuilt page (`web-design-guidelines`, `design:design-critique`, `design:accessibility-review`); the owner's phone check in Safari; three to five students use the site; fixes from what they show | |

## Part 2: the foundation for a personal guide

| # | Step | What done looks like | Status |
|---|---|---|---|
| 8 | The owner's decisions (below) | Each of A to E answered and written here | |
| 9 | The specs rewritten | [specs/agent.md](specs/agent.md) and [specs/accounts.md](specs/accounts.md) match the decisions; today they say email and password, one call, nothing remembered | |
| 10 | Coverage | Requirements researched for the listed universities that have none (106 of 290 on 2026-11-16), with the `research-wave` skill; the new universities guide applied when it is published | |
| 11 | The questions test set grown | About 50 real student questions, each with the page or record that must answer it ([specs/eval-seed.json](specs/eval-seed.json) has 35) | |

## Part 3: accounts and وضّاح

Paid services and installs need the owner's yes first (CLAUDE.md). Accounts wait for the owner's privacy-law (PDPL) review for under-18 users.

| # | Step | What the student gets | Status |
|---|---|---|---|
| 12 | Accounts | Sign in; the plan and profile on every device; delete and export | |
| 13 | وضّاح, cited answers | Scholarships, requirements and steps explained; English-test requirements (IELTS, Duolingo, others); whether a university and major are on a scholarship's list. Every fact with its source | |
| 14 | وضّاح, plan-aware | Universities found by interests, destinations and other preferences; deadlines tracked; a practical application plan; ongoing guidance. He proposes changes to the plan and the student confirms | |
| 15 | Deadline reminders | A reminder before each date in the plan | |
| 16 | وضّاح, essay coach | Guidance from official admissions advice, cited. He asks and reacts; he never writes the essay, so the voice stays the student's | |

Each وضّاح step ships only after its test passes: no uncited fact, no wrong number, every refusal right.

**How وضّاح answers (proposed).** Retrieval alone is not enough, because most of what we know is structured records, not prose (about 6,000 words of guides beside about 550 KB of university requirements on 2026-11-16).

```
question + the student's profile and plan
  → lookups over the data (the same code the pages use)   exact facts: scores, lists, dates
  → search over the guides (app/search.py)                explanations
  → answer with citations → guards (a number not in a cited source: show the sources only)
```

- **Store:** facts stay as JSON in git; review and tests are the verification, history is the audit. A database holds only accounts, profiles and plans.
- **Update:** the daily watch, `stale_facts.py`, `check_sources.py` and the `update-site` skill. A stale fact is answered with the official link, not the number.
- **Remember:** a profile and plan the student can see and edit, not chat transcripts.
- **Uncertainty:** "meets the published minimum" is never "will be accepted"; no chances, no predictions.

## Decisions for the owner

| | Decision | Claude's recommendation |
|---|---|---|
| A | May «خطتي» ask a few questions (grade, goal, fields, destinations) and build the roadmap from them? Needed for step 2 | Yes: nothing sensitive, kept on the device only; the same profile is what وضّاح reads later |
| B | May وضّاح know grades and test scores? CLAUDE.md says never collect them | Keep them on the device, compared in the browser, until the PDPL review; then decide |
| C | What does وضّاح remember? | The confirmed profile and plan; no transcripts |
| D | Sign-in method | Google sign-in, plus an email link for students without Google; no passwords |
| E | Monthly budget and cap for وضّاح | Set a cap first; the model is chosen by the accuracy test and the cost it measures |

## Not doing

Admission chances or predictions; rankings beyond the official lists; streaks or pressure mechanics; anything that could pass for the Ministry; stock photos or AI pictures of people; shemagh red in the interface; essays written for the student.
