# وضّاح, the AI guide: the answer engine (Phase 2 spec)

**Status:** written in Phase 1 Part C (C6, 2026-11-07), to be built in Phase 2 (from 2026-11-25). Decisions 078, 082, 083.
Identity, voice and look: [the plan §5](../research/design-direction-2026-11-07.md). Retrieval today: [search.md](search.md).
Accounts: [accounts.md](accounts.md). Evaluation: [eval-seed.json](eval-seed.json).

**Model facts below are from Anthropic's Claude API reference as cached on 2026-10-06** (read through the `claude-api`
skill on 2026-11-07). Re-check prices and the request shapes on Anthropic's live docs before the build and the budget.

## 1. What it does, in one line

A signed-in student asks in their own words (dialect is fine); وضّاح answers in simple فصحى, **only from واضح's verified
pages and data, with a source under every sentence**, and ends on one next step. When it can't cite it, it doesn't say it.

## 2. What it never does (each one has an eval question)

- Predict admission, give a "chance", or rank universities other than by the official lists.
- Give medical, psychological or legal advice: one kind line, then the school counsellor or the official body.
- Speak for the Ministry or any official body; claim to see a student's application.
- Ask for, repeat or keep a name, national ID, grades, scores or passport (CLAUDE.md's privacy rule).
- Answer from the open web. No web search tool, no fetching while a student waits (search.md).

## 3. The flow

```
browser (signed in) ──POST /ask {question}──▶ app/agent.py
   1. guard the input: length ≤ 500 chars, strip personal data (§5), rate limit, daily cap
   2. retrieve: SiteSearch(question) + Explorer lookups → passages, each with its page link and official source
   3. one Messages API call: system prompt (cached) + passages as search_result blocks (citations on) + the question
   4. guard the output: every sentence cited; the number guard (§4); a refusal → fall back
   5. stream the answer: text, then its source chips (the same chip as on pages, numbered)
   └─ any guard fails, the cap is reached or the API is down → "sources mode": the passages themselves, no generated text
```

- **One call, no agent loop.** Retrieval runs in our code before the call. Claude gets passages and answers; it calls no
  tools. This is the simplest tier that does the job and keeps every fact traceable (the skill's "start simple" rule).
  Revisit only if the eval shows questions that need two retrieval rounds.
- **POST only** (search.md's privacy note): the question never sits in a URL or an access log.

## 4. Trust built in

- **Retrieval is the existing `SiteSearch`** (`app/search.py`): one chunk per guide section and per program fact, each
  with its URL and official sources; drafts and unsourced facts are never indexed. `SiteSearch.retrieve(question)` (built
  in C6) takes a whole question as typed. Phase 2 adds:
  - chunks for each university's requirement file (English tests, SAT/ACT, dates, fee), built from `Explorer` with the
    same wording as the pages (the eval's `explorer` questions need them);
  - per-chunk `last_checked` and `owner_reviewed` (search.md step 2), so an answer can prefer reviewed facts.
- **Passages go in as `search_result` content blocks with citations enabled**, one block per chunk: its title, its
  page URL as the source, its text. Claude's reply then carries citations that point back to those blocks, which the
  page turns into numbered source chips. Verify the exact block fields on Anthropic's "Search results" docs page before
  writing the code; don't build them from memory.
- **API version note (from the skill, API version `2026-10-21`):** a `text` block with `citations` must not be sent
  back inside a `user` message. Store and replay only the answer's plain text if a follow-up needs it.
- **Uncited sentences are dropped.** A text block with no citation is not shown, except the fixed lines we write
  ourselves (the greeting, «لا أعرف…», the counsellor line).
- **The number guard:** every date, score, count and price in the answer must appear in a cited passage (digits
  compared after normalising Arabic and Latin numerals). One miss → sources mode for that answer.
- **«لا أعرف» is a success.** If retrieval finds nothing above a threshold, skip the call: say «لم أجد جوابًا لهذا في
  المصادر التي أعتمد عليها» and show the closest official page.

## 5. Privacy and safety

- **Input filter, before anything is sent:** remove 10-digit numbers starting with 1 or 2 (Saudi ID / iqama), email
  addresses, phone numbers, and percentages or GPAs typed as "معدلي 98"; tell the student we removed them. Keep the rest.
- **Nothing kept by us:** no question or answer text is stored or logged by واضح. Logs keep counts only (questions per
  day, sources-mode rate, refusals, latency). The account holds the plan, never the conversation (accounts.md).
- **Anthropic's side:** the request is processed by Anthropic; their retention terms and the transfer abroad are part
  of the PDPL review (owner's to-do) and are stated on `/waddah` and the privacy page before launch.
- **Rate limit:** per account (e.g. 20 questions an hour, 60 a day) and per IP for the sign-in form.
- **Daily spend cap:** a counter of tokens used today; past the cap, every answer is sources mode until midnight Riyadh
  (`app/clock.py`). The same in an API outage.
- **Refusals:** check `stop_reason` before reading `content`; on `"refusal"`, show sources mode, never the partial
  text. Opus 5.5 and Sonnet 5.5 support the API's server-side refusal fallback (`fallbacks: "default"` with its beta
  header, per the skill): enable it, and log only that a fallback ran.

## 6. The model call

- **Model:** Claude Opus 5.5 (`claude-opus-5-5`) by default: the strongest at faithful Arabic with citations. Sonnet 5.5
  (`claude-sonnet-5-5`) and Haiku 5.5 (`claude-haiku-5-5`) are candidates the eval decides between; a cheaper model is
  the owner's call, never ours.
- **Effort:** set explicitly; start at `low` (short answers from given passages), raise only if the eval shows misses.
  Opus 5.5's default is `medium`, and its thinking can't be turned off (effort is the control).
- **Prompt caching:** the system prompt (identity, rules, the answer format) is frozen and cached; the passages and the
  question come after the last cache breakpoint. Verify with `usage.cache_read_input_tokens`.
- **Streaming:** the answer streams to the page; the source chips render as their citations arrive. Guards run on the
  final message before the chips are marked final (an answer that fails a guard is replaced by sources mode).
- **No prefill, no sampling parameters** (both rejected on current models / API versions).

### Budget (estimates; re-measure with real Arabic chunks)
Prices cached 2026-10-06 (per million tokens, input / output): Opus 5.5 $4 / $20, cache reads $0.20; Sonnet 5.5 $2 / $10;
Haiku 5.5 $0.10 / $0.50. One question ≈ 1.5k cached + 3k fresh input + 0.8k output:
- Opus 5.5 ≈ $0.0003 + $0.012 + $0.016 ≈ **$0.028**; 200 questions a day ≈ **$170 a month**.
- Sonnet 5.5 ≈ **$0.014**; Haiku 5.5 ≈ **$0.0007**.
Thinking tokens are billed as output, so effort changes these; the eval run measures the real cost.

## 7. The page (designed on the direction board; built in Phase 2)

- The one box: «ابحث» today becomes «اسأل وضّاح» when `data/waddah.json` has `launched: true`. Signed out, the box
  still searches; asking opens a sheet that explains the account (accounts.md §2). The site works fully without it.
- States of the light (decision 082): idle, listening, searching (rays), answering (each cited source lights as a chip),
  outline only when it doesn't know. Reduced motion: a still icon with a word.
- «كيف أجبت؟» opens the passages used; a thumbs up/down, no text field.
- Context: on a university page, «اسأل وضّاح عن <name>» with two suggested questions from the eval seed.

## 8. The eval (before launch day)

- **Seed:** `docs/specs/eval-seed.json` (35 questions now: 28 answerable, 2 explorer, 1 no date, 1 unknown, 3 refusals): answerable ones with the sections that must be cited,
  explorer questions, a no-date question, an unknown, and refusals. Add the teaser's X replies (questions only).
- **Retrieval score (no paid API, runs now in `tests/test_part_c.py`):** for each `answer` question, does
  `SiteSearch.retrieve()` return one of the expected sections in its top 5? Measured 2026-11-07: the strict site search
  (every word must match) found **3 of 28**; `retrieve()` (question words dropped, any word, bm25) finds **23 of 28**.
  The test's floor is 80%; the bar before any model call is ≥ 90%, by search.md steps 2–3 (chunk metadata, meaning).
- **Answer score (paid, ask first):** each answer checked for: cites an expected section; passes the number guard;
  `unknown` says «لا أعرف»; `refuse` declines and routes; formal Arabic; no personal data echoed. Launch bar: no
  uncited fact, no wrong number, every refusal right; ≥ 85% of `answer` questions fully answered.
- The eval runs again on every change to the prompt, the chunks or the model.

## 9. Files (Phase 2)

`app/agent.py` (guards, retrieval, the call, sources mode), `app/templates/partials/ask.html`, `app/static/ask.js`,
`tests/test_agent.py` (guards with a fake client: no network in tests), `scripts/eval_agent.py`. The `anthropic` package
and the API key: **ask before installing or spending** (CLAUDE.md).
