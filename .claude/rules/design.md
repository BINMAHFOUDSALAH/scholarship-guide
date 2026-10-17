---
paths:
  - "app/templates/**"
  - "app/static/**"
  - "tests/test_design.py"
---

# Design rules (decision 062)

Loaded when Claude edits templates, CSS/JS or the design tests. The tokens and their meanings are at the top of `app/static/style.css`; the colours are checked by `tests/test_design.py`.

- **Act on forest, read on paper.**
  - Paper `#F6F4EE` (the logo's letter) is for everything you read.
  - Forest `#184B3A` (the logo's tile) is for links, buttons and the current place. It is also the "stage" where you act: the homepage's start, the universities search, the footer.
  - Headings and text are ink `#101713`, so green always means "you can act".
- **Lime `#D8ED9B`** only for «مفتوح الآن», the next step and "you are here" (the current grade, «الآن», the chosen country), plus the focus ring on forest. Never small text on paper. **Amber** is for restrictions and «لم يفتح بعد».
- **Stages:** a forest area is a `.stage`. It redefines `--ink`, `--action`, `--line`…, so shared components work unchanged. Fields and menus use the frozen tokens (`--field-bg`, `--field-ink`, `--brand`), so they stay paper-coloured inside a stage. A new text/background pair goes into `text_pairs` in the test.
- **Type:** Noto Naskh Arabic Bold for page and section titles (`--font-title`); IBM Plex Sans Arabic for text, labels and data (tabular figures). Use the scale (`--text-xs` to `--text-display`); nothing under 13px.
- **One motif, the route:** the logo's diamond marks a step in a real sequence (the grades, the application year, the next step). Lime means now or next; an outline means later.
  - Never use the diamond as decoration.
  - Numbered markers only on real sequences.
- **Shared components** (buttons, `status_tag`, tags, notices, the summary list, `key_facts`, the back link) instead of one-off styles.
- **Structure over strings:**
  - Each value goes under its own label (the summary list, `dl.key-facts`).
  - Never join values with «·» or dashes (a test checks); running text uses the Arabic comma «، ».
  - English names inside Arabic text go in `<bdi lang="en">`.
- **Arrows:** ↗ only for an official page that opens in a new tab, → only for "back to…". No ← on internal links.
- **Sources sit beside their facts:** in the margin on wide screens, under the value on phones.
- **Layout:** right-aligned (RTL start), logical properties only. Widths:
  - `--wide` (1200px) for the homepage grid and the footer;
  - `.page-wide` (1080px) for tool pages;
  - `.measure` (680px) for reading.
- **Panels are few:** the search, the university summary, the next step (`--radius-panel`). No grids of identical cards, no decorative shadows, no stock photos. The الرواد star chart is the only drawing of data.
- **Motion:** one load moment (the homepage's route draws once), the theme cross-fade, and responses to the student's action. Nothing loops, and all of it is off with reduced motion.
- **Themes:** two designed themes, in `:root[data-theme="dark"]` only (no `prefers-color-scheme` in the CSS). The device decides until the student picks (060).
- **The logo never changes:** the header draws `static/favicon.svg` exactly (a test checks). Don't recolour, redraw or restyle its parts; only its size and the space around it may change.
- **Images:**
  - Programs show their official logos (028).
  - A country flag goes beside a country's name (049).
  - A university's official logo appears only on its own page, self-hosted with its source and licence (049).
  - Photos must be real, licensed and credited.
- **Footer:** the grades, programs and guides come from the data. The copyright line is last; its year comes from `current_year()` and `site.since`. No second logo or slogan.
- **Contrast** (both themes, checked by `tests/test_design.py`): ≥ 4.5:1 for text, ≥ 3:1 for borders and focus.
