---
paths:
  - "app/templates/**"
  - "app/static/**"
  - "tests/test_design.py"
---

# Design rules (decision 035)

Loaded when Claude edits templates, CSS/JS or the design tests. The colours are also checked by `tests/test_design.py`.

- ivory `#F6F4EE`, charcoal `#101713`, forest `#184B3A` (headings, links, the main button), lime `#D8ED9B` only for «مفتوح الآن» and the next step, never as small text.
- Light mode first (dark via toggle).
- Plex Sans Arabic Bold headlines; Naskh only for the wordmark and quotes.
- Wide grid for the homepage, `.page-wide` for tool pages, 720px `.measure` for reading.
- Build with the shared components (buttons, `status_tag`, tags, notices, summary list, back link) instead of one-off styles; nothing under 13px.
- Panels yes; no gradients, grids of identical cards, stock photos, or decorative animation.
- Logos: the programs' official ones (decision 028), and a country flag beside the country name (pages and lists), and each university's official logo on its own page only, self-hosted with source and licence (decision 049).
- Real licensed photos with credit.
- Contrast is checked by `tests/test_design.py` (≥ 4.5:1 text, ≥ 3:1 borders and focus).
