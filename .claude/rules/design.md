---
paths:
  - "app/templates/**"
  - "app/static/**"
  - "tests/test_design.py"
---

# Design rules (decisions 062, 081, 083, 084)

Loaded when Claude edits templates, CSS/JS or the design tests. The tokens and their meanings are at the top of `app/static/style.css`; the colours are checked by `tests/test_design.py`. «الطريق والنجوم» (081): by day you walk the road (the grades, an application's steps), by night you read the stars (destinations); وضّاح is the light that makes both clear.

- **Act on forest, read on paper.**
  - Paper `#F6F4EE` (the logo's letter) is for everything you read.
  - Forest `#184B3A` (the logo's tile) is for links, buttons and the current place. It is also the "stage" where you act: the homepage's start, the universities search, the footer.
  - Headings and text are ink `#101713`, so green always means "you can act".
- **Lime `#D8ED9B`** only for «مفتوح الآن», the next step and "you are here" (the current grade, «صفّك», «الآن» on the year line, the chosen country, the furthest step of «خطتي»), plus the focus ring on forest. Never small text on paper. **Amber** is for restrictions and «لم يفتح بعد» (its group mark, a deadline's diamond on the year line).
- **The light is lime too (083):** وضّاح's light, the dawn on the teaser (dawn is lime, never sun), and the "light travels" motion (a saved item's light flying to «خطتي», «قُبلت» lighting its row once). The light is the logo's dot moving: it means "your next step", so it never stays lit as decoration.
- **Night (`--chart-ground`)** is the stage for destinations (the الرواد chart, the map) and for وضّاح (the dawn band; no page until launch, 084). Text on it is paper; every pair is in `text_pairs`.
- **Warm accents (decision 075):** **sun** `--sun` only for the homepage's door into «جرّب قبل أن تقرر» (ink text, on the stage); **sand** `--sand` for a closing band of paper (the homepage's quote). Not for headings or decoration.
- **Field tones (decision 075):** each broad field has five values in `.tone-<id>` (add `field-tone tone-<id>` to an element). Used for its drawing, its result card (wash, majors, labels) and a `.tone-dot` beside its name in the explorer and on a university page. A tone only names a field: never a rank, a status or an action, and its name is always written beside it. Buttons stay forest.
- **Stages:** a forest area is a `.stage`. It redefines `--ink`, `--action`, `--line`…, so shared components work unchanged. Fields and menus use the frozen tokens (`--field-bg`, `--field-ink`, `--brand`), so they stay paper-coloured inside a stage. A new text/background pair goes into `text_pairs` in the test.
- **Type:** Noto Naskh Arabic Bold for page and section titles (`--font-title`); IBM Plex Sans Arabic for text, labels and data (tabular figures). Use the scale (`--text-xs` to `--text-display`); nothing under 13px.
- **Two shapes, two jobs (083; the circle left the map in 084):**
  - the **diamond** (the logo's dot) marks a step in a real sequence: the grades, the application year, the statuses of «خطتي», a status tag, a deadline on the year line. Lime means now or next; an outline means later; amber means not open yet. Never decoration; numbered markers only on real sequences;
  - the **four-point star** is the light: وضّاح, and «المملكة», where every path of light starts; and, on a map, a university: one star each, grouped into a constellation per country (the الرواد chart, 060, and every map since 084).
- **Shared components** (buttons, `status_tag`, tags, notices, the summary list, `key_facts`, the back link, the source chip, `partials/now.html`, `partials/world_map.html`) instead of one-off styles.
- **Shapes of controls (083):** a rectangle (`--radius`, 8px) acts: `.btn--primary` (forest, the one main action), `.btn--secondary` (outlined), `.btn--small` in rows, `.btn--sun` (the explore door only). A pill chooses or keeps: «احفظ» (`.save-mini`, filled with ✓ when kept), «هذا صفّي», country chips, applied filters, the map view's toggle. A 4px label names: `.tag`, `.status`. Touch targets ≥ 32px in rows, 44px elsewhere.
- **The source chip (083):** every official source beside a fact is `<a class="src" target="_blank">`: a small forest-tinted pill, no underline, ↗ drawn after it. Quieter than the answer, the same everywhere; وضّاح's answers will number them.
- **Structure over strings:**
  - Each value goes under its own label (the summary list, `dl.key-facts`).
  - Never join values with «·» or dashes (a test checks); running text uses the Arabic comma «، ».
  - English names inside Arabic text go in `<bdi lang="en">`.
- **Icons are drawn, never typed (083):** ↗, → and ✓ aren't in the self-hosted fonts and showed as empty boxes on some phones. They are CSS masks (`--icon-ext`, `--icon-back`, `--icon-check`) in the text's colour: every `target="_blank"` link gets ↗ by itself (`.no-ext` opts out, e.g. a link with its own icon); `.icon--back` points to the start of the line and turns with the language; a kept item gets ✓. A test fails if a page prints ↗ ✓ → ←. No arrow on internal links.
- **Sources sit beside their facts:** in the margin on wide screens, under the value on phones.
- **Layout:** right-aligned (RTL start), logical properties only. Widths:
  - `--wide` (1200px) for the homepage grid and the footer;
  - `.page-wide` (1080px) for tool pages;
  - `.measure` (680px) for reading.
- **Panels are few:** the search, the university summary, the next step, and the field cards on the «جرّب قبل أن تقرر» result, the one place that compares a few things to choose from (`--radius-panel`, decision 073; each in its field's tone, 075). Elsewhere no grids of identical cards. No decorative shadows, no stock photos.
- **Data drawings (083):** a drawing shows data or does a job, never decoration. They are: the الرواد chart (060); the map (`sky.world_chart`, drawn like the الرواد chart: one star per university, a constellation per country under its name, moved apart so none overlaps, a path of light from المملكة; the chips beside it are the list you read and tap, the drawing is `aria-hidden`; 084); the route of «خطتي»'s statuses with their counts; the dawn band (how far it has come is the date).
- **Result rows (083):** each university row is rank | name and country | «احفظ», then a strip of labelled cells: the English tests in an aligned column, SAT/ACT, the university's next date; the admissions page as a source chip. The same fact sits in the same place on every row. Long lists show their top places (5 for a vague major, 10 for a precise one) and link to the whole list.
- **Motion:** one load moment (the homepage's route draws once), the theme cross-fade, and responses to the student's action: the light travels to «خطتي» on a save, «قُبلت» lights its row once and fades, a map's path of light draws when a country is in focus (on a touch screen, the first tap on its chip lights it and the second opens it, 085). Back keeps your place (`back.js`, 085). The dawn moves only with the date, never on screen. Nothing loops, and all of it is off with reduced motion.
- **Themes:** two designed themes, in `:root[data-theme="dark"]` only (no `prefers-color-scheme` in the CSS). The device decides until the student picks (060).
- **وضّاح's mark (082, 083):** the light (`partials/waddah.html`: the logo's dot drawn out into a four-point star, lime with a forest edge on paper, no edge on night) beside «وضّاح» in Naskh Bold. No face, no body. Drawing the ض's own dot as the rhombus needs the font's outlines: ask before installing a font tool for it. Until launch only the teaser band (084): the words and a drawing of a student helped by three agents (each with the light on its antenna; machines, never a human face); no link, no page.
- **The logo never changes:** the header draws `static/favicon.svg` exactly (a test checks). Don't recolour, redraw or restyle its parts; only its size and the space around it may change.
- **Images:**
  - Programs show their official logos (028).
  - A country flag goes beside a country's name (049).
  - A university's official logo appears on its own page, self-hosted with its source and licence (049), and, as a small copy on a white plate, among the 5 in الرواد's «الآن» row (084; `scripts/logo_thumbs.py`).
  - **Program pictures (084):** each «الآن» row has its program's picture (`partials/program_art.html`): our own drawing in the paper cut-out style on its own ground, the same on both themes, no text, no outside request, `aria-hidden` beside the written name, with the official logo where we have one (SDAIA's); since 085 a program (or واعد company) with an official logo shows the logo itself on its plate instead of a drawing. «الآن» shows no today's date and no countdown: the closing date is in the status tag.
  - Photos must be real, licensed and credited.
  - Each broad field has its own drawing (`static/img/fields/<id>.svg`, decision 073): paper cut-outs on the field's own ground. Our own work, no text, no script, no outside request, the same on both themes (a test checks). Colours: exactly the field's five tones and paper (decision 075). No diamond. Phones show the middle 640×320 of the 640×490 frame, so what matters stays there and only ground goes above and below.
- **Footer:** the grades, programs and guides come from the data. The copyright line is last; its year comes from `current_year()` and `site.since`. No second logo or slogan.
- **Contrast** (both themes, checked by `tests/test_design.py`): ≥ 4.5:1 for text, ≥ 3:1 for borders and focus.
