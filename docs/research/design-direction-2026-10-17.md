# Design direction and redesign (2026-10-17, decision 062)

**Brief (owner, 2026-10-17):** a substantial UI/UX redesign: study the live site and nine references, choose a direction that is Wadih's own, redesign every page type and the footer (with a copyright line), keep the logo exactly as it is, and inspect the rendered result. Palette and typography were open.

**How it was done:** the site rendered locally in Chromium (Playwright) at 320, 390, 768, 1024, 1280 and 1440px, light and dark, every page type; the code and data read; the references opened in the same browser through the session proxy (desktop and phone screenshots) and their guidance pages read. **Not done:** no students talked to, no analytics, no real phone (Safari), no screen reader. **[V]** = seen on the rendered site or in the code.

## 1. What the audit found (before)

**Problems, by impact on a student's task:**
1. **Run-on values [V].** Result rows and the university summary joined facts with «·» and «label: value» runs that mixed English and Arabic in one sentence («SAT/ACT: مطلوب   IELTS: لا يوجد حد أدنى منشور   TOEFL iBT: …»). The colon moved around the English label in RTL, the same «لا يوجد حد أدنى منشور» repeated three times per row, and a date read as «1 نوفمبر 2026 · آخر موعد للتقديم · Early Action · لخريف 2027 المصدر ↗ · موعد الابتعاث منفصل».
2. **Flat hierarchy [V].** Headings, links, buttons, labels and university names were all forest bold on ivory; a section title (24px) barely differed from a row title (19px). A link and a heading looked the same.
3. **The first screen spent on decoration [V].** On desktop the sun and astrolabe took about 40% of the opening; the three grade buttons, the main way in, were small (180 × 80px) and staggered for a visual effect.
4. **Status far from its subject [V].** In «مفتوح للتقديم الآن» the status and deadline sat about 800px from the name on desktop.
5. **A lopsided deadlines page [V].** /news was three columns; the least actionable one (11 recently closed واعد programs) ran 2,000px while «مفتوح الآن» had a narrow column.
6. **Guides without a way in [V].** Eight guides (IELTS, TOEFL, Duolingo, SAT, القدرات, US and UK applications, essays) had no index, nav item or footer link; only contextual links and search reached them.
7. **A footer that ended nothing [V].** Brand, one line, a credits link, the X link; no navigation, no copyright.
8. **Navigation:** four items, two of them anchors into the homepage, and the guides not among them.

**What worked and stays:** the trust model (a source beside every fact, computed lists that can't drift); grades as the main way in; the explorer's filters, removable tags and server-rendered results (decisions 048, 057, 058); the university page's order; minimum vs recommended (058); accessibility basics (skip link, focus ring, `aria-current`, contrast tests, 13px floor); privacy (no third parties); the two designed themes; the logo.

## 2. References: what was borrowed, what wasn't

| Reference | Borrowed | Rejected |
|---|---|---|
| **Stripe** (home, Payments) | Show the real thing as the visual: Wadih's "product demo" is its live data (what's open, a university's requirements), not illustration. A claim plus its explanation in one typographic block. | Gradients, bento grids of cards, logo walls. |
| **Apple** (home, HIG Typography) | Restraint and rhythm: one message per band, generous space around the key element; HIG's run-in bold lead («**الجامعات في الخارج:** …», already in the grade pages) and hairline tables. | Centred giant product heroes that delay the task. |
| **GOV.UK** (Design System, summary list, step-by-step, principles) | Summary list (label | value) for every fact; step-by-step's numbered line for a real sequence (the three years, the application year); "Be consistent, not uniform"; grouped footer with the licence line last. | The government look (Wadih must not pass for the Ministry). |
| **UCAS** (home, Applying) | Navigation by the student's stage (discover → apply → money); search as a first-screen utility; a heart/shortlist in the header (= «قائمتي»). | Stock photos, ads, an icon row of nine categories. |
| **Khan Academy** | "Get started" as large self-identification rows (Student / Family / Teacher): the model for «في أي صف أنت؟». | The mascot and the illustration beside the title. |
| **The Pudding** (index, «english vocab lists» essay) | The data itself is the visual (the الرواد star chart stays, smaller); a narrow reading column. | Stickers, loud colour blocks, highlighting single words, monospace dates. |
| **Linear** | Precision: one tag style, status as a mark + words («◆ مفتوح الآن»), counts beside group titles, tabular figures. | Dark SaaS dashboard look, monospace labels. |
| **MoE, scholarship help, Study in Saudi** | Vocabulary: «رحلة الابتعاث»، «حدد مسارك». The official help page shows the journey as a row of cards («تعرف على البرنامج»، «تعرّف على الشروط»، «حدد مسارك»); a sequence should look like one. | The government platform look (photo heroes, the Ministry's green dot pattern, sans Arabic in every title): Wadih must be told apart from official sites at a glance. |
| **NN/g visual hierarchy** | Few type sizes per screen, at most two large elements, grouping by proximity and common region, the squint test. Read 2026-10-17: "Limit how many elements are big to a maximum of 2". | — |
| **W3C 1.4.3** | 4.5:1 for text, 3:1 for large text and boundaries ("14pt and 18pt are equivalent to approximately 18.5px and 24px"); logos exempt. | — |

The hypothesis in the brief (Stripe sophistication + Apple restraint + GOV.UK/UCAS clarity + Pudding storytelling) was used only in part: Stripe's visual language and Pudding's colour were rejected; what survived from each is the method (show real data, restraint, plain structure, data as the picture).

## 3. The direction: «الطريق» on paper and forest

**Plan (written before the code, then reviewed):**
- **Colour (6):** paper `#F6F4EE` (the logo's letter: the mark reads as cut from the page), ink `#101713` (all headings), forest `#184B3A` (the logo's tile: action + the "stage" surfaces + footer), lime `#D8ED9B` (the logo's diamond: now / next / you are here), amber `#774C0C` (wait / restricted), muted ink `#4F5A54`.
- **Type:** Noto Naskh Arabic Bold for titles (page titles, section titles, the homepage title, the route's stops, the quote); IBM Plex Sans Arabic for text, labels and data (tabular figures). Both already self-hosted: no new download.
- **Layout:** right-aligned (RTL start) everywhere; forest "stage" where you act (homepage start, universities search), paper where you read; facts with their sources in the margin on wide screens.
- **Principles:** act on forest, read on paper; the diamond is a step, never decoration; structure over strings (every value under its own label); sources beside facts; one motion (the route draws itself once).

**Review against the brief and against generic defaults (what changed after the review):**
- *Cream page + serif display* is a common generated look. Kept the paper because it is the logo's own letter colour (a reason specific to this brief), but the **first screen is forest**, not cream, and there is no terracotta accent.
- *Hairline broadsheet* look: rules only where they structure data (a list's top, a table head); reading sections are separated by space.
- *Card kit:* no grid of identical cards; programs are rows, guides a list, the only panels are the search, the university summary and the next step.
- *Template chrome:* no eyebrow above every heading; «·» chains removed from every page (a test checks); decorative «←» removed from internal links (↗ stays: it means "an official page in a new tab"; → stays: "back").
- *Numbered markers* only where the content is a sequence: the three years, the year's months, the grade pages' three points.
- *A stepper* is a common UI pattern; here it carries a real sequence and is drawn with the logo's diamond, ending at the programs.

## 4. What changed

- **Tokens:** headings are ink; forest means "you can act" (links, buttons, the current nav item). Stage tokens (`--stage`, `--on-stage`, `--stage-amber`…) redefine the page colours inside forest surfaces, so shared components work on both. Fields keep paper colours through frozen tokens (`--field-bg`, `--brand`).
- **Header:** five sections (الأدلة added), the logo unchanged (a test now checks it equals the favicon's drawing).
- **Homepage:** forest start: the title (Naskh, display size), one line, **the route** (أول → ثاني → ثالث ثانوي → «بعد الثانوية: برامج الابتعاث»), then the search of the official lists. Paper below: what's open (status beside the name), the programs (identity small, facts lead), the new **guides index**, the Tuwaiq quote as a pull quote.
- **Explorer:** title and search on the forest stage (الرواد's chart beside its facts, not a full screen above them); each row's facts as a labelled list (English tests as test + words, identical words said once, scores never joined), actions under the facts; rows stack below 1024px.
- **University page:** a summary sheet whose values are short lines (the date large, what it is and its source under it); the fee as amount / waiver / note / links; English tests in two aligned columns.
- **Grade pages:** the three years as the same route (current year lit); the three points numbered large; grade 12's year as a vertical route with «الآن» lit.
- **Program pages:** facts with their sources in the margin; the timing note marked in amber.
- **Deadlines (/news):** one column in the order a student acts: open (full rows, «لمن»), closed or not yet, recently closed as a compact dated list.
- **Guides:** a reading column with «في هذه الصفحة» kept in view beside it on wide screens.
- **Footer:** forest, the brand line, the X feedback link, three groups (grades; scholarships and universities; guides), then the copyright line: «© 2026 واضح. جميع الحقوق محفوظة.» with «الشعارات والصور لأصحابها» and the credits link. The year runs from `site.since` to the current year, computed per request.
- **Removed:** the sun, the astrolabe rings and the decorative bands (the stars stay, at night, over the homepage start); the drawn program scenes (every program has a logo or a licensed photo).

## 5. Verification

- **Rendered, both themes:** home, explorer (all, الرواد, إمداد, a major, filters, a name, واعد, no result, a country), Harvard, MIT, Cambridge, Manchester, TUM, Stanford, grades 10–12, the three program pages, /news, IELTS, US applications, about, «قائمتي», search, 404; at 1280 and 390px; key pages at 320, 768, 1024 and 1440px. No horizontal overflow and no JavaScript error on any of them.
- **Interactions (Chromium):** `scripts/check_explorer.mjs` 30/30 (filters, ✕, «مسح الكل», field picker, suggestions, keyboard) at 390 and 1280px; plus the homepage suggestions over the start, the theme switch (saved), saving two universities and finding them in «قائمتي», a الرواد country chip, the phone menu, the university save toggle, keyboard focus on the route (lime ring), and the opening animation's end state.
- **Found and fixed during review:** suggestions clipped by the start's edge; per-letter wrapping in the explorer at 768px (rows now stack below 1024px); the side column squeezing facts; SDAIA's plate losing its navy; fee links without spaces; the phone footer at ~1,150px (now two columns, ~840px).
- **Tests:** 616 pass (11 new: the copyright line and its year, the logo equals the favicon, the route's order, every guide indexed, no «·» chains, labelled row facts; the contrast test now covers the stage and footer pairs).
- **Page height (px, light):** desktop 1280 / phone 390, before → after: home 4,230 / 5,948 → 4,276 / 7,008; explorer 5,588 / 10,365 → 6,393 / 12,533; MIT 3,572 / 4,961 → 4,285 / 6,005; grade 12 3,766 / 4,942 → 4,157 / 5,869; /news 2,748 / 3,893 → 2,645 / 4,301. Phones are longer, from the guides index, the fuller footer (841px at 390) and the labelled facts; each row now scans without reading a sentence. Worth watching in the usability test.

## 6. Limits and open questions

- Not seen on a real iPhone (Safari), and not with VoiceOver or TalkBack.
- No students have used the new version: the route, the labelled facts and the guides index are judgements from the audit and the references, to be tested (questions: "where do you start?", "is MIT's IELTS a minimum?", "which guide tells you about Duolingo?").
- The route's one-line descriptions and the guides' hints are new copy, written from the pages' own descriptions; the owner should read them.
- «الأدلة» in the nav is a third anchor into the homepage (/#guides): there is no guides page of its own yet.
