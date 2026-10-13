---
paths:
  - "app/templates/**"
  - "app/static/**"
  - "tests/test_design.py"
---

# Design rules (decisions 035, 060)

Loaded when Claude edits templates, CSS/JS or the design tests. The colours are also checked by `tests/test_design.py`.

- ivory `#F6F4EE`, charcoal `#101713`, forest `#184B3A` (headings, links, the main button), lime `#D8ED9B` only for «مفتوح الآن» and the next step, never as small text.
- Two designed themes (decision 060): light = dawn, dark = the same sky at night. The device's setting until the student picks; their pick wins. Never scroll-driven.
- Plex Sans Arabic Bold headlines; Naskh for the wordmark, quotes and display titles only (homepage, الرواد).
- Wide grid for the homepage, `.page-wide` for tool pages, 720px `.measure` for reading.
- Build with the shared components (buttons, `status_tag`, tags, notices, summary list, back link) instead of one-off styles; nothing under 13px.
- The sky (`partials/sky.html`, `app/sky.py`) is the one visual language: astrolabe hairlines, diamond stars, one sun/moon, the lime guiding star. Atmosphere only in the sky layers and bands; content sits on panels or paper, never on the sky alone.
- Motion: one opening on the homepage, theme switching, and responses to the student's action. No looping motion, nothing that delays an action; everything off with reduced motion.
- Panels (`--radius-panel`, one `--lift` shadow) yes; no grids of identical cards, stock photos, or decoration that means nothing. A page gets its own look only when it means something (today only الرواد).
- Logos: the programs' official ones (decision 028), and a country flag beside the country name (pages and lists), and each university's official logo on its own page only, self-hosted with source and licence (decision 049).
- Real licensed photos with credit.
- Contrast is checked by `tests/test_design.py` (≥ 4.5:1 text, ≥ 3:1 borders and focus).
