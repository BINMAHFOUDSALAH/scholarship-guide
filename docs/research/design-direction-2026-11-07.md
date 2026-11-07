# واضح, the next level: design direction, the AI guide «وضّاح», and its announcement

**Status:** approved by the owner on 2026-11-07 (decisions 081–082). This is Phase 1 Part C's plan; the steps and their order are also in [roadmap.md](../roadmap.md). Kept as approved; where a later decision changes it, the decision wins.

**Direction board** (step 1, a private design canvas, created empty on 2026-11-07): https://claude.ai/artifact/BVq4dD2Rzmeyx9iEGUdjWh. Read it first (Artifact tool, `action: "read"`), then fill it.

**API prices in §7** come from Anthropic's Claude API reference as cached on 2026-10-06; re-check them on Anthropic's pricing page before Phase 2's budget is decided.

## Context

**The ask (owner, 2026-11-07):** make واضح the most useful, intuitive, visually impressive and trusted student-guidance site in Saudi Arabia: loved by students, shared by counsellors, credible enough for the Ministry to notice. Study the site, the code and 8 references; propose the direction, the AI guide's identity, and a creative announcement. Investigate and propose first.

**Owner's decisions (2026-11-07, this session):**
- **Name: وضّاح (Waddah).**
- **Scope:** evolve the look, rebuild the structure (no full rebrand).
- **Now (Phase 1 → Launch 1):** the redesign and overhaul, the guide's identity (name, look, voice), its teaser, and everything Phase 2 needs prepared.
- **Phase 2:** build the guide, with **sign-in for students who want to use it** (as decision 078).
- **The teaser says «في ديسمبر»**, with no fixed day.

**Dates:** Phase 2 starts **Wed 25 Nov** · Launch 1 **~Wed 9 Dec**, after a 5-student test of the new design · وضّاح: **in December**. Owner time ≈ 5 h/week: Claude builds, the owner decides, reviews and tests on a phone.

**How I studied it:** the live site in Chromium at 390px and 1280px, both themes, 15 page types (plus a saved plan, the activity's result, the الرواد chart in use); the code (`home.html`, `base.html`, `style.css` tokens, `sky.py`, `plan.py`, `search.py`, `rowwad.html`); decisions 057–080, the roadmap, the design rules, the 062 design research, the search/RAG spec, the marketing guide. References opened live: BigFuture, Stripe, Duolingo, Unifrog, Linear, Apple, and an ArcGIS StoryMaps story. **Limits:** Niche blocks automated browsers (its patterns are used from what's well known about it, not a live read); no real phone, no students, no analytics.

---

## 1. What I found

### Keep: real assets, rare in this space
1. **The trust model:** every fact sourced, computed lists that can't drift, conflicts shown, nothing invented. The moat.
2. **The logo and its meanings:** ض with a lime rhombic dot = "your next step"; act on forest, read on paper; lime = now / next / here.
3. **The الرواد star chart:** a country chip draws **a path of light from المملكة to your destination**. The one moment where emotion, data and interaction meet: the seed of the direction.
4. **The paper cut-out field drawings and field tones:** the most original visuals on the site.
5. **Privacy:** no trackers, no third-party requests. A selling point to parents, counsellors and the Ministry.
6. **Engineering:** 700+ tests (741 at decision 073), CI-gated deploys, English kept in step by tests.

### Fix: what holds it back (measured on the live site)
1. **A library, not a journey:** organised by content type, not by "what do I do now?". The student assembles the plan alone.
2. **Too long on phones** (390px): home 8,146px (~10 screens), a major search **24,717px (~29 screens)**, الرواد list 13,443, program page 13,545, IELTS guide 12,815. Every row shows every fact.
3. **Everything weighs the same:** below the hero, grey labelled rows; no focal point, few moments, illustrations only on the activity's result.
4. **Sources compete with answers:** Stanford's page shows 15 «المصدر» links, the program page 18 (105 links in all), the IELTS guide 203 links.
5. **Overlaps a beginner can't untangle:** programs listed twice on the homepage; «البرامج» vs «مواعيد التقديم»; **two search boxes**; program / track / مسار.
6. **Personalisation is minimal and hidden:** the grade isn't remembered; the plan's return line sits ~1,250px down on a phone.
7. **«خطتي» is a form, not a place:** a status menu per row; nothing happens on «قُبلت»; no "this week".
8. **Nothing is built to be shared:** one generic share image, no "send to a friend", nothing for counsellors.
9. **Credibility for adults is invisible:** no page a counsellor or the Ministry can read about how facts are verified.

---

## 2. The recommendation in one line, and two cautions

**Restructure around the student's journey, give the site one signature visual system that grows from the star chart, and make وضّاح the light of the logo's dot**, announced by a teaser in which dawn comes a little closer every night.

- **Warmth without words:** you've rightly cut reassuring sentences (069, 079). Warmth comes from moments (a light flying to «خطتي», a path completing on «قُبلت», dawn on the teaser), not from more copy.
- **"The Ministry will want it"** comes from counsellor adoption and visible rigour (a method page, a changelog), never from looking official. Wadih stays clearly independent.

---

## 3. Design direction: «الطريق والنجوم» (Road & Stars)

**The idea:** the student is a traveller setting out from home. **By day you walk the road** (the grades, the steps of an application: 062's route). **By night you read the stars** (where you could go: the star chart). **وضّاح is the light that makes both clear.** The route is for sequences, the stars for destinations, and **every star is data or a function, never decoration** (why 062 retired the decorative sky still holds).

| | Keep | Evolve | Add |
|---|---|---|---|
| Colour | paper, ink, forest, lime, amber, sun, sand, field tones and their meanings | the chart's night (`--chart-ground`) becomes the "sky stage" for destinations and وضّاح | no new hues |
| Type | Noto Naskh Bold titles, IBM Plex Sans Arabic text | **display numerals** (Plex 700 tabular, 48–72px) for countdowns and key facts | no new font (a download would need asking) |
| Motif | the diamond = a step; lime = now, outline = later | the logo's dot is also **وضّاح's light** (§5) | one **source chip**, the same on pages and in وضّاح's answers |
| Drawings | paper cut-outs, own work, SVG, no text | extend to the 3 grades, empty states, 404, وضّاح's scenes | a paper-layer horizon for the teaser |
| Motion | the route draws once; reduced motion respected | **"light travels"** as the signature: save → a light flies to «خطتي»; «قدّمت» lights a waypoint; «قُبلت» completes the path | وضّاح's states (§5); nothing loops while idle |
| Layout | RTL logical properties, the 3 widths, rows over card grids | **progressive disclosure**: the answer first, details and sources one tap away | a sticky action bar on phones (status + the one action) |

**Principles, from the references:** one answer and one action at the top of every page (Duolingo, Apple) · show live data as the picture (Stripe, Linear) · progressive disclosure (NN/g) · data as narrative over a map (StoryMaps) · visible progress without streaks or pressure, since users are minors (BigFuture, Unifrog) · serve the counsellor and they bring the students (Unifrog) · at a glance, then compare, never scores or "chances" (Niche) · peak–end: design the peaks (the activity's result, «قُبلت», the reveal) and end every page on one next step.

---

## 4. Structure and the student's journey

### Navigation: 5 → 4 sections, one box, «خطتي» as the hub
- **حسب صفك** (grades + «لم تقرر بعد؟») · **البرامج** (programs **and** their dates; «مواعيد التقديم» becomes its calendar view, `/news` redirects) · **الجامعات** (explorer, map, compare) · **الأدلة** (a real `/guides` index page). **خطتي** always visible; a slot beside it for «دخول» in Phase 2.
- **One box, «ابحث أو اسأل»:** universities, majors and guides now (ends the two-search confusion); it becomes «اسأل وضّاح» in Phase 2.

### Homepage, two states (device only, nothing sent)
- **First visit:** the forest start (title, «في أي صف أنت؟», «لم تقرر بعد؟», the box) → **«الآن»**: the 3 things that matter this week as big numbers, each sourced → **«إلى أين؟»**: the star map of 15 countries → programs as short rows by when you apply (no second list) → guides → وضّاح's teaser.
- **Returning** (grade remembered and/or a plan): the start becomes **your board**: your grade (changeable), next step, nearest date, progress. The grade is remembered on the device like the plan.

### Key screens
- **Explorer:** compact rows (name, flag, list rank, three labelled facts: English minimum, SAT/ACT, next date), expand for the rest; target: the 29-screen search down to about 8. A **map view** for any filter (`sky.py` already lays out any listing). **Compare** up to 3.
- **University page:** a glance card of big values, each with its source chip; long sections below.
- **Program page as a story:** a sticky status card (status, date, «تقدم الآن» or «احفظ»), a sticky bottom bar on phones; chapters: ما هو؟ · هل يناسبني؟ (routes to a next step, never "you're eligible", nothing stored) · كيف تتقدم؟ · أسئلة شائعة; long conditions folded.
- **«السنة في سطر»:** the year as a timeline: each program's window a bar, a "today" line, tap for details, "my plan only".
- **Grade pages:** "this month" first, then the year route.
- **«خطتي», the hub:** your constellation (saved universities as stars, a path of light from home to each), **this week** (dates within 30 days), progress along the route, the status rows, **«أضف المواعيد إلى تقويمك»** (an `.ics` built from the posted plan, nothing stored), **«شارك خريطتك»** (a 9:16 image drawn in the browser, no names), a celebration on «قُبلت».

### New interactive experiences, by value
| # | Experience | Job | When |
|---|---|---|---|
| 1 | «السنة في سطر» | when each program opens and closes, relative to today | before Launch 1 |
| 2 | The map everywhere + your constellation | where you could go; where you're going | before Launch 1 |
| 3 | «اسأل وضّاح» | answers in your words, with sources | Phase 2 (designed now) |
| 4 | Compare | decide between 2–3 universities | after Launch 1 |
| 5 | «من الثانوية إلى الحرم الجامعي» scroll story | admission ≠ scholarship, told over the map | after Launch 1 |
| 6 | «هل يناسبني؟» on program pages | route to the right next step | after Launch 1 |

**How pages connect:** every page ends on one next step; «احفظ» wherever you meet a university or program; وضّاح is contextual (on Stanford's page: «اسأل وضّاح عن ستانفورد» with suggested questions); «خطتي» turns saves into dated steps.

---

## 5. وضّاح: identity

### The name
- **وضّاح** = "radiant, the one who makes things clear", from the same root as **واضح** (و ض ح), like Duo and Duolingo. **The name carries the logo's letter ض at its centre.** Classical Arabic uses «الوضّاح» for bright morning light («الصبح الوضّاح»): it fits a light that shows the way.
- **English:** "Waddah", always spelled the same way; the English pages say once that both names share a root meaning "clear, bright".
- **To check (owner):** the Saudi trademark register (SAIP), the app stores, an X handle; and, in a quick name test with ~10 students (girls and boys) and 2 counsellors, any associations (it is a man's given name, and the name of a classical poet, وضّاح اليمن).

### Look
- **Wordmark:** «وضّاح» in Naskh Bold with **the ض's dot drawn as the logo's lime rhombus**: the same construction as the logo, so they read as one family while the logo stays untouched (typeset with care: the shadda sits beside the dot).
- **The light:** the logo's dot drawn out into a four-point star. Lime with a forest edge on paper (the existing `--guide-edge` token), lime with a soft glow on the night stage.
- **No face, no body.** An abstract light with motion keeps an AI from passing for a person (honesty with minors) and isn't read as a man or a woman.
- **States** (each with a word; reduced motion shows a still icon): still (idle) · a slow breath (listening) · rays sweeping like a lighthouse (searching the sources) · steady, each cited source lighting as a chip (answering) · **outline only** when it doesn't know (the route's "not yet").
- Answers in Plex; paper cut-out scenes for marketing (the light over a paper road, a horizon at dawn).

### Personality and voice
- **صادق:** answers only from واضح's verified pages, a source under every answer, says «لا أعرف» readily.
- **مختصر:** the answer in one or two lines, details on request.
- **عملي:** ends on one next step (a page, «احفظ في خطتي»).
- **هادئ:** never hype; never «مضمون» or «أكيد ستُقبل».
- **يعرف حدوده:** no admission predictions, no rankings beyond the official lists, no medical, psychological or legal advice; points to the school counsellor or the official channel.
- **Language:** understands dialect, answers in simple فصحى.
- Sample lines (owner to review):
  - «أنا وضّاح، دليلك الذكي في واضح. أجيبك من صفحات واضح الموثّقة، ومع كل جواب مصدره. لا تكتب اسمك أو بياناتك الشخصية.»
  - «لم أجد جوابًا لهذا في المصادر التي أعتمد عليها. أقرب صفحة رسمية لسؤالك: …»
  - «لا أستطيع أن أتوقع قبولك، لكن أستطيع أن أريك ما تطلبه الجامعة ومتى تتقدم.»

### Trust built into the interface
- Every factual sentence carries a source chip; a sentence the model can't cite isn't shown.
- **Number guard:** every date, score or count must appear in a cited passage, or the answer falls back to **sources mode** (the verified passages that answer the question, with links, nothing generated). Sources mode is also the safety net when the daily spend cap is reached or the API is down.
- «كيف أجبت؟» shows the passages used; a thumbs up/down with no text.

---

## 6. The announcement: «وضّاح قادم في ديسمبر»

**Concept: dawn is coming.** On the homepage's night band, behind a paper-layer horizon, **the sky lightens a little every night** through November, from night towards first light (the step computed from the date on the Riyadh clock, `app/clock.py`); in December it holds at the edge of dawn. On launch day (a switch in the data, not a date), dawn breaks: the lime light rises, and the box becomes «اسأل وضّاح». People come back to see it change; nothing loops, nothing is tracked.

**Two stages:**
1. **Now:** «وضّاح قادم في ديسمبر», no day.
2. **Once the day is certain:** the day appears, with «ذكّرني» (a calendar `.ics` file, so the reminder lives on the student's phone and we collect nothing) and a count in nights.

**Placements**
1. **Homepage band** on the homepage.
2. **`/waddah`** (and `/en/waddah`): what it will do (three promises), what it won't do, example questions labelled as examples, a short FAQ: free? (yes) · account? («ستحتاج إلى حساب بالبريد الإلكتروني لتستخدمه») · data? (we never ask for names, grades or ID).
3. **«ماذا ستسأل وضّاح؟»:** invite questions as replies on your X account: engagement now, and real student questions for Phase 2's accuracy check.
4. **Social, $0:** a 9:16 clip of dawn breaking over the horizon, recorded from the real page with the existing `marketing/src` pipeline (headless browser + ffmpeg), plus 3 still posts, one per promise. Snapchat first.
5. **Counsellors:** a printable one-page announcement with a QR to `/waddah`.

**Draft copy (owner to review)**
- Title: «وضّاح قادم في ديسمبر»
- Line: «دليلك الذكي في واضح: اسأله عن الابتعاث والجامعات والاختبارات، فيجيبك من المصادر الرسمية ويريك من أين عرف.»
- Promises: «من المصدر: مع كل جواب رابط مصدره الرسمي.» · «بلا تخمين: إن لم يجد الجواب قال لا أعرف، ودلّك على الجهة المختصة.» · «بلا بياناتك: لا يسألك عن اسمك أو درجاتك.»
- Call to action: «ماذا ستسأل وضّاح؟» → the X link.

**Guardrails:** say it's AI; no accuracy figures; privacy claims only once the Phase 2 review confirms them; no factual claims without a source.

---

## 7. Preparing Phase 2 (done now, so Phase 2 is a build, not a redesign)

**Designed and built now:**
- The header slot for «دخول» beside «خطتي»; the «ابحث أو اسأل» box and its future states (signed out: a sheet explaining the account; signed in: ask).
- وضّاح's answer view designed (answer, source chips, states, «لا أعرف», sources mode) in the direction board, ready to wire.
- `data/waddah.json` (name, copy, `launched` switch) driving the teaser and later the box.
- The source chip shared by pages and answers.

**Written now:**
- `docs/specs/agent.md`: retrieval (the existing `SiteSearch` exposed as one tool, `search_guide(query)`, its results returned as **`search_result` blocks with citations**), guards (number guard, sources mode), rate limit, daily cap, no question text stored or logged by us, POST only, personal data stripped before sending, the eval bar.
- `docs/specs/accounts.md`: email + password, what's stored (email, the plan's ids and statuses: the same JSON as `plan.py`), deletion, the PDPL questions (under-18 consent, transfer abroad), the sign-in moment framed as a benefit («احفظ خطتك على كل أجهزتك، وفعّل تنبيهات المواعيد»).
- **The eval seed:** questions from the guides and from the teaser's X replies, each with its expected source page.
- Optional, if time allows: search spec step 2 (chunks with `last_checked` / `owner_reviewed`), testable without any paid API.

**Built in Phase 2:** accounts; `app/agent.py` (API call, streaming, guards); the box goes live; plan-aware answers for signed-in students (the plan holds no grades or IDs by design); email alerts later.

**For Phase 2's budget (estimates, to re-measure with real Arabic chunks):** default model Claude Opus 5.5 (`claude-opus-5-5`), the strongest at faithful Arabic with citations: ≈ $0.028 per question (~1.5k cached + ~3k fresh input tokens, ~0.8k output); 200 questions a day ≈ $170 a month. Sonnet 5.5 ≈ $0.014, Haiku 5.5 ≈ $0.001. A cheaper model is your call, decided by the accuracy check. Effort set explicitly, the system prompt cached, streaming, the API's refusal fallback on.

---

## 8. Growth and credibility
- **«أرسلها لصديق»** on universities, programs, guides and the activity's result: the phone's own share sheet (Web Share API), so WhatsApp and Snapchat work with no third-party script.
- **Share images per page** (a university's name and key facts) made on our server (probably a library: ask first). Later.
- **«للمرشدين»:** how to use واضح in a 20-minute class session, A4 posters with a QR per grade, a printable monthly «ما المفتوح الآن». After Launch 1.
- **«كيف نتحقق»** (the method, live counts) and **«ما الجديد»** (a changelog fed by `/update-site`): credibility for adults, a reason to come back. After Launch 1.

---

## 9. Roadmap

| When | Step | Priority |
|---|---|---|
| Nov 8–10 | **Direction board:** a private page (artifact) with phone-first mockups: homepage (both states), «خطتي» hub, compact explorer row, program story, «السنة في سطر», وضّاح's wordmark, light and states, the answer view, the teaser band at three nights, `/waddah`, the share card. No site code in this step. | must |
| Nov 10–11 | **Record and prepare:** decisions 081 (direction) and 082 (وضّاح and the teaser), `design.md` (the dot's second meaning, data drawings beyond the الرواد chart, the source chip, the signature motion), roadmap, CLAUDE.md, architecture. Name check (you). | must |
| Nov 11–13 | **Teaser live:** the dawn band, `/waddah` in both languages, its share image, the X post, the clip. | must |
| Nov 12–24 | **Structure pass:** nav and the one box, homepage «الآن» and the returning state, compact explorer rows, programs + dates merged, the source chip, the «دخول» slot. | must |
| Nov 22–30 | «خطتي» hub v2 (constellation, this week, `.ics`, share, celebration), «السنة في سطر», the map view. | should |
| Nov 25–30 | **Phase 2 specs** (`agent.md`, `accounts.md`) and the eval seed; your decisions on API billing and the PDPL review. | must |
| Dec 1–7 | **5-student test** of the new design; fixes. | must |
| ~Dec 9 | **Launch 1.** | must |
| December | **Phase 2 build:** accounts, then وضّاح; launch day chosen when it passes the accuracy check; the teaser's second stage when the day is certain. | must |
| After | Compare, the counsellor kit, program stories, the scroll story, «كيف نتحقق», «ما الجديد», share images per page, email alerts. | later |

**Not doing:** streaks or pressure mechanics, confetti everywhere, a mascot with a face, stock photos or AI images of people, a chat bubble over content, "chance of admission" scores, anything that could pass for the Ministry.

## 10. Your to-dos
- The name check (SAIP, app stores, X), and optionally the 10-student name test.
- Look at the direction board and say what to change.
- Before Phase 2: API key, billing and a spend limit; the PDPL review for accounts and under-18 users.
- 5 students for the test before Launch 1.

## 11. What will change, by step (nothing until approved)
- **Decisions and rules:** `docs/decisions.md` (081, 082), `.claude/rules/design.md`, `CLAUDE.md`, `docs/roadmap.md`, `docs/architecture.md`, `docs/log.md`.
- **Teaser:** `data/waddah.json`; `app/templates/partials/waddah_teaser.html`, `app/templates/waddah.html`; a `/waddah` route in `app/main.py`; the light and wordmark SVGs in `app/static/img/waddah/`; `style.css`; `data/i18n/ui.en.json` (and the English page); a share image.
- **Structure pass:** `base.html` (nav, one box, «دخول» slot), `home.html` (two states, «الآن»), `partials/uni_results.html` and `partials/uni_macros.html` (compact rows), `universities.js` (expand, the box), `news.html` → the programs calendar, `components.html` (the source chip), `mylist.js` (remember the grade).
- **Hub and timeline:** `my_plan.html`, `partials/my_plan_rows.html`, `mylist.js`, `app/plan.py` (`.ics`, this week), a timeline partial fed by `paths.json` and `apply_year.json`.
- **Reuse, don't rebuild:** `SiteSearch` (the box now, retrieval in Phase 2), `sky.rowwad_chart()` and its helpers (any map, the constellation), `plan.clean()` / `plan.rows()` (hub, `.ics`, plan-aware answers), `app/clock.py` (the dawn), `count_ar`, the `marketing/src` capture pipeline (the clip), `status_tag`, `key_facts`, the field tones and drawings.
- **Phase 2 only:** `app/agent.py`, `app/templates/partials/ask.html`, `app/static/ask.js`, accounts, the `anthropic` package (ask before installing).

## 12. Verification (each step)
- `pytest`, with new tests: the teaser and `/waddah` in both languages, the dawn step by date (and the `launched` switch), no third-party requests, contrast of every new pair (`tests/test_design.py`), English coverage (`tests/test_english.py`); later the `.ics` and the compact rows.
- Browser checks: `node scripts/check_explorer.mjs`, `check_plan.mjs`, `check_explore.mjs` (Arabic and `--en`); screenshots at 320, 390 and 1280px in both themes; `python scripts/english_leaks.py` at 0.
- Reviews (decision 076): `web-design-guidelines`, `design:design-critique`, `design:accessibility-review`; the `reviewer` subagent (Sonnet) on the big diffs.
- Your phone (Safari) on each step; the 5-student test before Launch 1.
- Git per CLAUDE.md: a branch per step, PR, merge after CI.
