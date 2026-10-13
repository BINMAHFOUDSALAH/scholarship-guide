# Search and the road to «اسأل واضح» (decision 045)

## Why
Students ask questions in their own words. Retrieval, finding the right verified passage, is the foundation of the future RAG chatbot, and it's useful on its own as site search.

## How RAG will work here
1. **Ingest (ahead of time):** read the owner's chosen official sources and the guide's own pages; the owner reviews them; split them into chunks; store each chunk with its link and date.
2. **Retrieve (per question):** find the few chunks most related to the question.
3. **Generate:** the model answers only from those chunks, cites them, and says it doesn't know when nothing fits.

Nothing is fetched from the internet while a student waits.

## Steps
| # | Step | Status |
|---|---|---|
| 1 | Keyword search: `/search`, `/api/search` (SQLite FTS5) | done |
| 2 | Chunks with full source tracking (`last_checked`, `owner_reviewed` per chunk) | next |
| 3 | Search by meaning: embeddings + vector index, combined with keywords (hybrid) | |
| 4 | Eval set: ~50 real student questions, each with its expected chunk; a test scores retrieval | |
| 5 | Chatbot «اسأل واضح»: answers only from retrieved chunks, with citations; refuses when unsure | ask first (paid API) |
| 6 | Operations: rate limits, daily spend cap, caching, logs without personal data | |
| 7 | Update-monitor agent: watches official pages, drafts changes, waits for the owner's approval | |

## Step 1 contract
- `GET /api/search?q=…` → `{"query": "…", "results": [{"title", "heading", "url", "snippet", "sources": [{"title", "url"}]}]}`. Empty `q` → no results. At most 10 results; `q` is cut to 200 characters.
- `GET /search?q=…`: the same results as a page (works without JavaScript), `noindex`.
- What's indexed: guide pages with `status: sourced` and sources (one chunk per h2 section, plus the intro); program facts with status `sourced`/`conflict` (link: `/programs/<id>#fact-<fact id>`); `test_needs.json` rows with an official source.
- Every result has at least one official (`https://`) source.

## Privacy
The app doesn't store queries. But `/search?q=…` is a normal web address, so Render's access logs record it, like every page address. That's acceptable for short search words. The chatbot, where students type longer questions, must send them in the request body (POST) so they stay out of the logs. The chatbot (step 5) will follow the same rule: no accounts needed, a notice not to type personal data, no chat text stored with anything identifying.
