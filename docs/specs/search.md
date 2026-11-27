# Search and retrieval

Wadih’s public search helps students find guides and sourced facts. وضّاح uses the same published material for explanations and structured university records for exact answers. See [agent.md](agent.md) for answer behavior and [accounts.md](accounts.md) for sign-in.

## Public search contract

- `GET /search?q=…` renders results as a page, works without JavaScript, and uses `noindex`.
- `GET /api/search?q=…` returns `query` and `results`. Each result has `title`, `heading`, `url`, `snippet`, and `sources` with `title` and `url`.
- An empty query returns no results. Queries are capped at 200 characters and responses return up to 10 results.
- The SQLite FTS5 index uses published guide sections, sourced program facts, documented source conflicts, and sourced rows from `test_needs.json`. Each indexed result links to its Wadih page and official sources. Keep drafts out of the published index.

## Retrieval for وضّاح

- Use `SiteSearch.retrieve()` in `app/search.py` to find relevant guide passages for explanations. Use the records and logic behind the University Finder for exact scores, deadlines, and list membership.
- Keep source links and verification metadata with the underlying records. Preserve the applicable institution, program, applicant type, and admissions cycle where relevant.
- Serve questions from Wadih’s prepared data and guides. Use the site’s source-checking workflow to refresh records when official information changes.
- Send private agent questions in the request body and keep raw questions out of application logs.

## How to improve it

- Use [eval-seed.json](eval-seed.json) to check whether the expected guide section or record appears among the top results. Include Arabic spelling variants, student phrasing, and English university names.
- Diagnose misses before changing the search stack. If a record is missing or stale, fix the data. If a relevant record exists but is hard to find, improve aliases, indexing, or ranking.
- Consider embeddings or hybrid search when the same test cases show that they improve retrieval. Compare relevance, response time, and cost against the existing search.