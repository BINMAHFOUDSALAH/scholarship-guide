---
paths:
  - "app/templates/**"
  - "app/static/**"
  - "tests/test_design.py"
---

# Design rules, version 3: «عالم وضّاح» (owner, 2026-11-16)

Loaded when Claude edits templates, CSS/JS or the design tests. The tokens and their meanings are at the top of `app/static/style.css`; the colours are checked by `tests/test_design.py`. Version 3 replaces «الطريق والنجوم» (decisions 062–093): the site now looks like the world وضّاح, the guide, comes from. His colours were always the logo's (forest visor, lime eyes); the page takes his clay body, his softness and his sense of touch. The road (steps in order) and the stars (destinations) keep their jobs.

**Status:** the foundation (tokens, typeface, buttons, header) and the homepage are built. The other pages inherit the tokens and still have their older layouts; rebuild them one at a time, in this order: «خطتي», the university page, the program page, the explorer.

- **Three colours, three jobs.**
  - **Clay** `--paper #F8F1E4` (his body) is the page: everything you read. Cards on it are `--surface-strong`.
  - **Forest** `#184B3A` (his visor, the logo's tile) is where you act: links, buttons, «خطتي» in the header, and the "stage" panels (the homepage's panel of stops, the universities search, the footer).
  - **Lime** `#D8ED9B` (his eyes, the logo's dot) is now, next and here: «مفتوح الآن», the stop under your finger, your own grade, the chosen country, the furthest step of «خطتي», the focus ring on forest. It may fill a whole key, with ink text. Never small text on clay.
  - Headings and text are ink `#11201A`, so green always means "you can act". **Amber** is for restrictions and «لم يفتح بعد». **Sun** `--sun` only for the door into «جرّب قبل أن تقرر»; **sand** `--sand` for a closing band (the homepage's quote).
  - **Shemagh red is his alone:** it appears in his pictures and nowhere in the interface (red reads as an error).
- **Field tones (decision 075):** each broad field has five values in `.tone-<id>` (add `field-tone tone-<id>`). A tone only names a field: never a rank, a status or an action, and its name is always written beside it.
- **Stages:** a forest area is a `.stage`. It redefines `--ink`, `--action`, `--line`…, so shared components work unchanged. Fields and menus use the frozen tokens (`--field-bg`, `--field-ink`, `--brand`). A stage inside a page is a rounded panel (`--radius-stage`). A new text/background pair goes into `text_pairs` in the test.
- **Type: one family, Readex Pro** (self-hosted, variable 300–700, OFL), chosen for reading ease in Arabic and Latin after a phone-size comparison with Alexandria and Rubik. Titles are its 700, set tight (line-height about 1.3); body is 16px at 1.75. Use the scale (`--text-xs` to `--text-display`); nothing under 13px. Never letter-spacing on Arabic.
- **The lip: what you can press, and only that.** A button, a stop, a card that opens something has a solid edge under it (`box-shadow: 0 var(--lip) 0 …`) and sinks onto it when pressed. A card that only holds things (a «الآن» row with several actions, a notice) has a border and no lip. No blurred or decorative shadows anywhere.
- **Shapes of controls:**
  - a rounded rectangle (`--radius`, 12px) acts: `.btn--primary` (forest, the one main action), `.btn--secondary` (outlined), `.btn--small` in rows, `.btn--sun` (the explore door only);
  - a pill chooses, keeps or names a place: the header's tools, «احفظ» (`.save-mini`), «هذا صفّي», country chips, applied filters;
  - a card (`--radius-panel`, 20px) groups; a 4px label names: `.tag`, `.status`.
  - Touch targets ≥ 32px in rows, 44px elsewhere.
- **Two motifs, two jobs:**
  - the **diamond** (the logo's dot) marks a step in a real sequence: the grades, the application year, the statuses of «خطتي», a status tag. Lime means now or next; an outline means later; amber means not open yet. Never decoration; numbered markers only on real sequences;
  - the **four-point star** is a destination on a map (one star per university, a constellation per country) and «المملكة», where every path of light starts.
- **وضّاح on the page (owner's mascot; decisions 082, 093):** a figure in a red shemagh and black agal, a dark-green visor with two lime lights: a machine, never a human face. His poses are the owner's files (`marketing/assets/waddah/`, web copies in `static/img/waddah/`); don't redraw or restyle him.
  - He appears only where he does something, and at most once on a screen: he asks the homepage's question (`wave`); later he searches (`search`), shows sources (`sources`), waits (`wait`), doesn't know (`unsure`), says a page is missing (`sorry`), points at a next step (`point`), celebrates «قُبلت» (`cheer`).
  - He is decorative (`alt=""`, `aria-hidden`): what he "says" is always written beside him as the page's own words. Until the AI guide launches he never speaks as a chat, and the teaser stays as it is (084, 093).
- **Shared components** (buttons, `status_tag`, tags, notices, the summary list, `key_facts`, the back link, the source chip, `partials/now.html`, `partials/world_map.html`) instead of one-off styles.
- **The source chip (083):** every official source beside a fact is `<a class="src" target="_blank">`: a small forest-tinted pill, no underline, ↗ drawn after it. Quieter than the answer, the same everywhere; وضّاح's answers will number them.
- **Structure over strings:**
  - Each value goes under its own label (the summary list, `dl.key-facts`).
  - Never join values with «·» or dashes (a test checks); running text uses the Arabic comma «، ».
  - English names inside Arabic text go in `<bdi lang="en">`.
- **Icons are drawn, never typed (083):** ↗, → and ✓ are CSS masks (`--icon-ext`, `--icon-back`, `--icon-check`) in the text's colour: every `target="_blank"` link gets ↗ by itself (`.no-ext` opts out); `.icon--back` turns with the language; a kept item gets ✓. A test fails if a page prints ↗ ✓ → ←. No arrow on internal links.
- **Sources sit beside their facts:** in the margin on wide screens, under the value on phones.
- **Layout:** right-aligned (RTL start), logical properties only. Widths: `--wide` (1200px) for the homepage grid and the footer; `.page-wide` (1080px) for tool pages; `.measure` (680px) for reading.
- **One thing leads each screen.** The homepage's start is وضّاح's question on the one forest panel; everything else on it is quiet. Cards are for a few things to choose between (stops, programs, deadlines, field cards); long lists stay rows, with the same fact in the same place on every row. No stock photos.
- **The header:** the logo, the language, «خطتي» by name (forest), the menu. On phones the theme switch is a row of the menu, said in full; on wide screens the four sections and the search show.
- **Data drawings (083):** a drawing shows data or does a job, never decoration: the الرواد chart (060); the map (`sky.world_chart`; the chips beside it are the list you read and tap, the drawing is `aria-hidden`; 084); the route of «خطتي»'s statuses with their counts.
- **Result rows (083):** each university row is rank | name and country | «احفظ», then a strip of labelled cells: the English tests in an aligned column, SAT/ACT, the university's next date; the admissions page as a source chip. Long lists show their top places and link to the whole list.
- **Motion:** one load moment (on the homepage وضّاح arrives, then the four stops rise in order), the theme cross-fade, and answers to the student's action: a key sinks when pressed, the light travels to «خطتي» on a save, «قُبلت» lights its row once, a map's path of light draws for the country in focus. Back keeps your place (`back.js`, 085). Nothing loops, and all of it is off with reduced motion.
- **Themes:** two designed themes, in `:root[data-theme="dark"]` only (no `prefers-color-scheme` in the CSS). The device decides until the student picks (060). Dark is midnight forest with the same meanings; وضّاح's pictures have transparent grounds and work on both.
- **The logo never changes:** the header draws `static/favicon.svg` exactly (a test checks). Don't recolour, redraw or restyle its parts; only its size and the space around it may change.
- **Images:**
  - Programs show their official logos (028); a country flag goes beside a country's name (049).
  - A university's official logo appears on its own page, self-hosted with its source and licence (049), and as a small copy among the 5 in الرواد's «الآن» row (084; `scripts/logo_thumbs.py`).
  - **Program pictures (084, 085):** a program (or واعد company) with an official logo shows it on its plate; otherwise our own paper cut-out drawing (`partials/program_art.html`), `aria-hidden` beside the written name. «الآن» shows no today's date and no countdown: the closing date is in the status tag.
  - Photos must be real, licensed and credited.
  - Each broad field has its own drawing (`static/img/fields/<id>.svg`, decision 073): paper cut-outs on the field's own ground, exactly the field's five tones and paper (075). No diamond.
- **Footer:** the grades, programs and guides come from the data. The copyright line is last; its year comes from `current_year()` and `site.since`. No second logo or slogan.
- **Contrast** (both themes, checked by `tests/test_design.py`): ≥ 4.5:1 for text, ≥ 3:1 for borders and focus.
- **Design tools:** this file beats any design plugin or skill. Build with `frontend-design`; review with `web-design-guidelines`, `design:design-critique`, `design:accessibility-review`. Taste (`design-taste-frontend`) is a review lens for the homepage only (one job per screen, equal edges, plain copy): never its palette, starter files or photographs rule.
