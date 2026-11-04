# Should واضح build an interests-and-majors assessment? (2026-11-04)

An evaluation of the owner's proposed feature: an interactive assessment of a student's interests and abilities that ends in a shortlist of majors or careers. It was done from four perspectives: research scientist, career guidance, assessment (psychometrics) and UI/UX. It revisits the "no own quiz" part of decision 057. **Outcome (same day): decision 069.** The guide is live; the activity is built as a draft, without scores.

**Evidence labels** (same as the October audit):
- **[V]** verified by me in the code, the live site or a primary source
- **[R]** published research (abstract or report read directly unless marked *secondary*)
- **[J]** professional judgment
- **[H]** a hypothesis to test with students

**What I did:**
- Read decision 057, the October product audit's questionnaire section, the roadmap, `data/universities.json` and `data/school_tracks.json`, and the grade 10 page.
- Fetched the live homepage and tried the live site search.
- Read primary abstracts (via Europe PMC), O\*NET's licence page and Mini-IP report, and the Ministry of Education's career-guidance handbook (دليل التوجيه المهني 1444هـ, PDF).

**What I could not do:**
- Read full papers behind paywalls (ScienceDirect returned 403). Two career-intervention findings come from *secondary* summaries; they're marked.
- Read the Ministry's grade 10 interest measure or HRDF «سبل» on official pages. What I report about the Ministry measure comes from Saudi press (*unverified*).
- Find, in a source I could read, a published validation of any RIASEC measure with Saudi high school students.
- Talk to students or counsellors.
- Test anything in a browser. No UI was built.

---

## 1. Honest assessment (short version)

**The problem is real; the proposed solution is the weakest way to solve it.**

- **The gap is real [V].** An undecided student has no starting point on واضح. The homepage has grades, programs, universities and guides, but no door for "I don't know what to study". Site search for «ميول» finds one sentence on the grade 10 page. The «لم تقرر بعد؟» guide planned in decision 057 isn't built yet.
- **But "answer questions → get a shortlist of majors" has four problems:**
  1. **It duplicates an official measure that may count.**
     - The Ministry already gives a career-interest measure (مقياس الميول المهنية) in grade 10 for track placement [V: defined in the Ministry's handbook].
     - Press reports say it is about 20% of the placement score and comes with a report that suggests majors and universities [*unverified*, press only].
     - A second, unofficial "result" from واضح could contradict it and confuse a 15-year-old at a decision that counts.
  2. **The science supports exploration, not prescription [R].**
     - A teenager's interests are only moderately stable. They settle in the college years.
     - Interest-environment fit predicts performance and persistence, but modestly.
     - Self-rated ability correlates with measured ability at about r = .33.
     - "Future potential" can't be measured by a web questionnaire at all.
  3. **A trustworthy Arabic measure is a research project, not a feature [V/R].**
     - O\*NET's Interest Profiler has no Arabic version.
     - Modified versions need the Developer License, which requires you to "validate all products incorporating content from the Tools".
     - Cross-cultural fit of the RIASEC structure is mixed.
     - Naive interest inventories produce large gender differences that would steer girls away from engineering and boys away from caring work.
  4. **The tool isn't the active ingredient [R, *secondary*].**
     - Career interventions work moderately.
     - Expert-supported ones beat self-directed or computer-only ones.
     - The ingredients that matter are written reflection, individual interpretation, information about the world of work, models (people in the job) and support.
     - A score alone adds little.
- **What is genuinely strong in the idea [J]:**
  - Interactivity on a phone, in Arabic.
  - A link from "what I enjoy" to "which school track, which majors, where I can study it on a scholarship". Nobody does that well, and واضح already has verified data for most of it.

**Recommendation in one line:** don't build an assessment that tells students what they are or what to study. Build a short, transparent **exploration activity** («جرّب قبل أن تقرر») that:
- helps a student pick **two or three fields to try this term**
- explains why, in the student's own answers
- connects each field to the school track, its majors, and واضح's universities and programs
- hands off to the official measure and the school counsellor

No score, no ability rating, nothing stored. It comes **after** the planned «لم تقرر بعد؟» guide and the student usability test, and after Launch 1.

---

## 2. Is it worth building?

### What student problem would it solve?
Different undecided students are stuck for different reasons [J; the categories follow Gati's decision-difficulty model, used here as a lens, not a measure]:

| Why they're stuck | What actually helps | Does a quiz help? |
|---|---|---|
| **Little exposure:** "I've never tried most things" | Trying things: a course, a visit, a project, a conversation | Partly: it can show *what to try*, not what they like |
| **Lack of information:** "I know what I like, not what majors exist" | Field and major profiles, school track, where it's studied | Only if it leads to good information |
| **Conflict:** "my family expects medicine" / "I like two things" | A respectful way to compare, and a conversation | A verdict makes this worse |
| **Doubt about ability:** "can I even do engineering?" | Facts: track, requirements, preparation; evidence of progress | Self-rated ability is weak [R] |
| **Not ready:** "I'm in grade 10, why decide now?" | Permission to explore, and what counts now (track, average) | No |

So the feature only belongs in واضح if it **routes each kind of stuck to the right help**. A "your type is…" result doesn't do that.

### Does it belong in واضح?
- **Yes, as a door [J]:**
  - The tagline promises «مستقبلك بعد الثانوية».
  - Decision 057 already plans thin doors that route to official tools.
  - واضح's real advantage is the verified link from field to majors to universities to scholarships.
- **No, as a psychometric product [J]:**
  - The owner works about 5 hours a week.
  - The users are mostly minors.
  - The project rule is "never invent". A home-made test that labels students conflicts with all three.

### Strengths
- Arabic-first, mobile-first. Most career tools are in English [J].
- It can reuse sourced data: the Ministry's field → major lists (`universities.json`) and the five school tracks (`school_tracks.json`) [V].
- It can widen horizons. OECD's *Dream Jobs?* found that about half of 15-year-olds expect to work in just 10 jobs, so exposure to unfamiliar fields matters (cited in the October audit) [R].
- It's engaging, and it gives a reason to come back.

### Weaknesses and risks
- **Over-trust [J]:** people tend to accept any personal result as accurate. That's the Barnum effect, a well-known finding I didn't re-verify here. Teenagers under pressure may read «يناسبك» as a verdict.
- **Conflict with the Ministry measure** [press-reported stakes; *unverified*].
- **Gender steering:**
  - Across 47 inventories and 503,188 people, men scored much higher on "things" interests and women on "people" interests (d = 0.93) [R].
  - Item-writing choices changed the size of the gap substantially [R]. Badly written items would steer students by gender.
- **Data gap [V]:**
  - واضح's field data is the scholarship guide's: 8 إمداد fields and 5 الرواد fields.
  - It has **no health, medicine, nursing, pharmacy, dentistry or education field.** The only health-adjacent majors are things like medical physics, health informatics and biomedical engineering.
  - A result built only on that data would silently drop what may be the most common aspiration [H].
- **Maintenance:** every field profile is new content to source and keep current (decision 028: nothing unsourced is shown).

### Questionable assumptions in the proposal
1. *"Students need to discover their interests."* Many need **experiences and information** first. You can't like or dislike what you've never done [J; consistent with social cognitive career theory, which holds that interests grow from experiences of success].
2. *"We can assess abilities."* Self-estimates are moderately accurate at best [R]. Real ability evidence (grades, القدرات/التحصيلي) is what the project rule forbids collecting, and rightly so.
3. *"A shortlist of majors is the useful output."* For a grade 10 student, the useful output is **what to try next and which track keeps doors open**. A major is a grade 12 decision.
4. *"More precision is better."* Percentages and rankings look scientific. They aren't, without validation [J].

### Simpler or different approaches (cheapest first)
1. **The «لم تقرر بعد؟» guide** (already planned, content only). It routes by "why you're stuck", points to the official measure, and pushes "explore by doing".
2. **Field profiles** for the 10 broad fields: what you study, typical work, school track, majors, where it's studied, "try this week". Every other option needs these anyway.
3. **A paper or Figma prototype** of the activity cards, tested with 5 students before any code.
4. **The interactive activity** (section 6), only if 1–3 show students want it.
5. **A validated Arabic interest measure:** only with a university research partner, and probably never, since official measures exist.

### What evidence would justify moving forward
**Go signals:**
- In the planned usability test, at least some participants are undecided, read the guide, and still ask "but which fields should *I* look at?" [H].
- They can't use the official measure's result: they didn't get the report, don't remember it, or are in grades 11–12. Ask 2–3 school counsellors too.
- On a paper prototype, students **choose an action** afterwards ("I'll try X this week") and don't say "the site told me to study X".
- The Ministry measure's facts are checked on official pages: stakes, report contents, who gets it.

**Stop signals:**
- Students treat the result as a verdict despite the wording.
- Counsellors say it conflicts with their work.
- The guide alone satisfies the need.

---

## 3. The scientific foundation

### What assessments can reasonably tell us

| Question | What the evidence supports | Label |
|---|---|---|
| **Interests now** | Self-report inventories reliably describe *relative* preferences among activity types today. The O\*NET Mini-IP's 6 scales have α = .70–.75 with 5 items each, in US samples. | [R] |
| **Will interests last?** | Moderately. In 66 longitudinal studies, stability "remained unchanged during much of adolescence and increased dramatically during the college years (age 18–21.9)". Rank-order stability at ages 12–18 is about .55–.58 (*secondary* for the numbers). Hands-on and artistic interests were the most stable. | [R] |
| **Do interests predict success?** | Yes, modestly. 60 studies and about 568 correlations: interests relate to performance and persistence, and person-environment **fit predicts better than interest scores alone**. The October audit cites r ≈ .32 for congruence (Nye et al. 2017). | [R] |
| **Current abilities** | Self-estimates vs. measured ability: **r = .33** (41 studies). Better with clear comparison groups and for numerical ability. Self-estimates mostly show **self-concept**, which is useful for conversation, not as a measurement. | [R] |
| **Future potential** | Not measurable by a short questionnaire. Ability grows with teaching and effort; any "potential" claim would be invented. | [J] |
| **Values, constraints, context** | Family, location, gender norms, scholarship rules and track all shape real choices. Counselling theory treats them as part of the decision, not noise. | [J] |

**Bottom line:** an interest activity can start a useful reflection and suggest **where to explore**. It can't tell a teenager what they're suited to.

### Established tools and frameworks

| Framework / tool | What it is | Research quality | Licence | Arabic / Saudi | Fit for واضح |
|---|---|---|---|---|---|
| **Holland RIASEC** (6 types) | The dominant interest model. The Ministry's handbook names Holland's theory [V]. | Strong in the US. Cross-cultural structure is mixed (Rounds & Tracey 1996, abstract not read). | Theory is free. | Used, but I found no readable Saudi high school validation [V: searched]. | Good **organising idea** for activities, not for scoring a person. |
| **O\*NET Interest Profiler** (60 items; Mini-IP 30) | US Department of Labor's RIASEC measure | Technical reports. Mini-IP α = .70–.75 in US samples [V]. | CC BY-ND (verbatim only) or Developer License (modify, but "validate all products") [V]. | English and Spanish only [V]. | Translating = modifying = must validate. **Not now.** |
| **IIP RIASEC Markers** (Armstrong, Allison & Rounds 2008) | Brief public-domain RIASEC scales, 8 items each | Acceptable reliability and convergent validity reported (*secondary*). | Public domain (*secondary*; IIP site not reached). | None found. | Best candidate **if** a validated measure is ever pursued with a partner. |
| **Strong Interest Inventory, Self-Directed Search** | Commercial inventories | Long research records | Proprietary, paid (not checked in detail) | Unknown | Not suitable (cost, licence, minors). |
| **Prediger's dimensions** (Data/Ideas × People/Things) | Two dimensions under RIASEC, used in the 2009 gender meta-analysis | Established [R] | Theory is free | n/a | A simple, honest way to *describe* a pattern ("you like working with ideas and people"). |
| **Gati's decision-difficulties model (CDDQ)** | Classifies *why* someone can't decide: readiness, information, conflict | Many adaptations. An Arabic version (Yaghi & Alabed 2021, 500 university students) exists (*secondary*). | Check before use | Arabic for university students, not teens | Use the **idea** as a routing question, not the scored instrument. |
| **Social cognitive career theory** | Interests grow from experiences of success, and expectations shape choices | Widely supported theory | Free | n/a | Justifies «لم أجرّبه بعد» and "try first" results. |
| **OECD career readiness** (explore / experience / think) | Teenage activities linked to adult outcomes in 10 datasets | [R], mostly Anglophone | Free | n/a | Defines the **outcome**: did the student explore or experience something? |
| **Ministry «ملف الإنجاز المهني»** | The student career file in the Ministry's handbook, with an «اكتشف ذاتك» section (values, skills, career interests, hobbies) [V] | n/a (official practice) | Official | Saudi, official | A natural **hand-off**: the result becomes a page for this file and the counsellor. |
| **Personality typing** (e.g. MBTI-style "types") | Type labels | Weak for career prediction [J; not re-verified here] | Mixed | n/a | **Reject.** Labels limit ambition. |

### What validation would be needed before making any claim

| What we'd say | What it requires |
|---|---|
| «نشاط استكشافي، ليس اختبارًا» (an exploration activity, not a test): **the only claim for v1** | Content review by a Saudi school counsellor and a career-development specialist; Arabic editing; cognitive interviews with students; usability testing. |
| «يساعدك على اختيار مجالات لتجربتها» (helps you choose fields to try) | The above, plus evidence from testing that students do choose and try something. |
| «يقيس ميولك» (measures your interests), or any score or percentage | Full test adaptation under the International Test Commission's guidelines for translating and adapting tests [J: standard practice]:<br>• several independent translations and a back-translation<br>• expert content review and cognitive interviews with Saudi teens<br>• a pilot large enough to test the factor or circular structure (several hundred students [J])<br>• reliability and a 2–4 week retest<br>• **equivalence across gender and region**<br>• correlation with the Ministry measure<br>• ethics approval and parental consent for minors<br><br>A university psychometrics partner, many months. |
| «التخصص المناسب لك» (the right major for you) | Predictive validity: follow students into university and check persistence and satisfaction. Years. **Don't make this claim.** |

---

## 4. Recommended direction

**«جرّب قبل أن تقرر»: an exploration activity, not an assessment.**

**Principles:**
1. **Transparent, not clever.** Every suggestion shows the student's own answers that caused it. Same answers, same result.
2. **No scores, ranks or percentages.** Fields are grouped into three bands («تجذبك الآن»، «تستحق التجربة»، «لا تجذبك الآن»), each explained in words.
3. **"Haven't tried" is a first-class answer.** It feeds a "try first" plan, not a low score.
4. **No ability rating.** Ask instead where the student has *seen themselves progress*, and show the facts of what each field requires (track, tests) from official sources.
5. **Everything ends in an action:** try something, talk to someone, take the official measure, add the page to the career file, and come back in a month.
6. **Covers every broad field, honestly.**
   - Use the 10 broad fields of UNESCO's ISCED-F 2013, which the guide's إمداد fields closely follow.
   - Where واضح has no data (health, education), say so and route to official sources. Never drop the field.
7. **Defers to the official measure and the counsellor.** The activity says it isn't the Ministry's measure. In grade 10, it tells students to take that measure on مدرستي (wording to verify on an official page first).

**Why this over the original idea:**
- It keeps the engaging part, the interaction.
- It removes the parts that need validation: scores, ability, verdicts.
- It aims at the ingredients research links to benefit: writing it down, information, people in the job, support [R, *secondary*].

---

## 5. Interaction design

### Structure (about 8–10 minutes, 3 parts)
0. **Framing (1 screen).** What it is, how long it takes, that nothing is saved or sent, and «ليس اختبارًا ولا يحدد تخصصك». One button: «ابدأ».
1. **«ما الذي يصعّب عليك القرار؟»** (pick any; can skip). Lack of exposure, information, a conflict or doubt; the answer changes the result's emphasis:
   - «لم أجرّب أشياء كثيرة بعد»
   - «أعرف ما أحب، ولا أعرف التخصصات»
   - «يعجبني أكثر من مجال»
   - «أهلي يتوقعون تخصصًا معينًا»
   - «لا أعرف هل أقدر عليه»
   - «لا شيء مما سبق»
2. **Activities (about 24–30 cards, 2–3 per field).**
   - Concrete school-age activities, not job titles. Job titles carry prestige and gender associations, and teenagers know few of them [J].
   - Four answers: «أستمتع به» / «لا بأس به» / «لا أستمتع به» / «لم أجرّبه بعد».
   - «لم أجرّبه بعد» opens one follow-up: «هل تودّ أن تجرّبه؟» نعم / ربما / لا.
   - Note: O\*NET moved *away* from a "not sure" option to raise reliability [V]. That's right for a measure. For exploration, separating *dislike* from *never tried* is the point.
3. **What you've seen yourself do (2 short questions).**
   - «في أي المواد أو الأنشطة لاحظت أنك تتقدم؟» Pick up to 3; no grades.
   - «ما الذي يهمك في عملك مستقبلًا؟» Pick up to 3: مساعدة الناس، الإبداع، حل المشكلات التقنية، الاستقرار، القيادة، العمل في الميدان، العمل مع البيانات.
   - Optional: «هل هناك مجال تفكر فيه أو يتوقعه منك أهلك؟» Pick one field or skip. It's always shown in the result, respectfully, with its facts.
4. **Review screen.** All answers grouped by part. Tap any to change. Then «اعرض النتيجة».

**Example activity cards** (formal Arabic; each maps to one field; written to be gender-neutral and Saudi-relevant):

| Field | Activity |
|---|---|
| الصحة والرعاية | «قراءة كيف يتعامل جسم الإنسان مع المرض» |
| التعليم | «شرح درس صعب لزميل حتى يفهمه» |
| الهندسة | «تفكيك جهاز قديم لمعرفة كيف يعمل» |
| تقنية المعلومات | «كتابة برنامج صغير أو تعديل لعبة» |
| العلوم الطبيعية | «إجراء تجربة في المختبر وتسجيل نتائجها» |
| الأعمال والإدارة | «تنظيم بيع منتجات في فعالية مدرسية وحساب الربح» |
| العلوم الاجتماعية والإعلام | «إعداد تقرير مصوّر عن حدث في مدرستك» |
| الفنون والعلوم الإنسانية | «تصميم شعار أو ملصق لنادٍ مدرسي» |
| الزراعة | «العناية بنباتات أو حيوانات ومتابعة نموها» |
| الخدمات | «تنظيم رحلة أو فعالية لمجموعة» |

The real list needs counsellor review (section 9).

### Navigation and feedback: what helps and why

| Feature | Use it? | Why |
|---|---|---|
| **Progress indicator** | Yes: «الجزء 2 من 3 · 12 من 26» | Lowers drop-off on long mobile forms [J]. Parts matter more than a percentage bar. |
| **Back and revisit answers** | Yes: back on every card, plus the review screen | Students change their minds; an answer they can't change feels like a test. |
| **«لم أجرّبه بعد»** | Yes, essential | Separates lack of exposure from dislike; drives the "try first" result. |
| **Skip** | Yes, everywhere | Nothing is required. A skipped card counts as missing, never as dislike. |
| **Running score or live result** | No | Invites gaming and early conclusions. |
| **Micro-feedback between parts** | Yes, reflective, not evaluative. E.g. «لم تجرّب بعد 9 من 26 نشاطًا، وهذا طبيعي في عمرك. ستجد في النتيجة طرقًا لتجربتها.» | Normalises uncertainty; keeps the student going. |
| **Swipe cards (left or right)** | No, or only as an extra to buttons | Fun, but error-prone, and gestures are a barrier for screen-reader and motor-impaired users. Swipe direction is also ambiguous in RTL. |
| **Timers, streaks, badges** | No | Pressure, not reflection. |
| **Scenarios** («تخيّل يومًا في…») | Later, inside field profiles | A good way to show what work looks like. Too long inside the activity. |

### Arabic, RTL, mobile, accessibility
- Formal Arabic (project rule), short sentences, second person. One idea per card.
- RTL throughout: "next" points left; progress fills from the right; numbers follow the site's existing style.
- One card per screen at 320–390px. Answer buttons at least 48px, full width, stacked.
- Each card is a `fieldset` with a `legend` and native radio inputs, so screen readers announce "1 of 4" and it works by keyboard. Focus moves to the next card's heading.
- No colour-only meaning; works at 200% zoom; respects reduced motion; works in both themes (the design rules in `.claude/rules/design.md` apply).
- English at `/en/...` with the same structure (decision 066).

### Students with little exposure, uncertainty or pressure
- **Little exposure:** many «لم أجرّبه بعد» answers lead with «جرّب أولًا» and a 4-week plan. No field bands are forced.
- **Unsure:** «لا بأس به», skips and the review screen are all valid. The result says how much it's based on: «بنيناها على 14 نشاطًا جرّبته».
- **Pressure:** the family's field is shown with facts (what you study, the track, what it takes, how to try it) and a short guide to talking with family. No judgement either way.
- **Ambition:** never say «لا يناسبك». The weakest band is «لا تجذبك الآن», and it can be expanded. Every field shows "how to try it".

---

## 6. Data, scoring, uncertainty, results

### What information to collect, and why
| Collect | Why | Stored? |
|---|---|---|
| Activity answers | The core of the reflection | **No.** Computed in the browser; optional "save on this device" like «قائمتي» (decision 035), with a clear button |
| Difficulty choice(s) | Changes what the result emphasises | No |
| Progress areas and values (up to 3 each) | Explanation text, not ranking | No |
| Grade (optional: 10/11/12) | Tailors next steps (grade 10: track and official measure; grade 12: applying) | No |
| **Not collected** | Name, email, gender, age, city, school, grades, test scores, free text | n/a |

**Why not gender:**
- It isn't needed.
- Asking for it invites gendered results.

**Why no free text:**
- Minors may write sensitive things.
- There's nothing to do with it without AI or storage.

### Scoring (transparent rules)
For each field:
- **Enjoyed:** activities answered «أستمتع به»
- **Curious:** «لم أجرّبه بعد» + «نعم» or «ربما»
- **Disliked:** «لا أستمتع به»
- **Progress:** one of the student's progress areas maps to this field (an explicit, reviewed mapping)

Bands:
- **«تجذبك الآن»:** at least 2 enjoyed and no more than 1 disliked. Show at most 3, ordered by enjoyed count, then progress. Ties are shown together, not broken arbitrarily.
- **«تستحق التجربة»:** mostly curious, or mixed (enjoyed and disliked both present).
- **«لا تجذبك الآن»:** mostly disliked. Collapsed but visible.

Special cases:
- **Flat profile** (enjoys almost everything or almost nothing): «إجاباتك متقاربة، وهذا شائع». Show an exploration plan instead of bands.
- **Thin evidence** (fewer than about 10 tried activities): lead with «جرّب أولًا»; bands are secondary.
- **Mixed interests** (two strong, distant fields, e.g. arts and engineering): name it as a strength. Show majors that combine them where the official lists have them (e.g. product design, architecture), and only those.

The thresholds are a starting point to tune in testing, not science [J]. That's exactly why no number is shown to students.

### Does AI have a useful role?
**Not in scoring** [J]:
- A rule-based result can be audited, tested and explained, and it's identical every time.
- An LLM result would be an unvalidated assessment that varies between runs.
- It would also send minors' answers to a third party.

**Useful later**, in line with the roadmap's chatbot that "answers only from verified content":
1. **Questions about a field, with sources:** «ما الفرق بين علوم الحاسب وهندسة الحاسب؟», answered from the verified field profiles. Builds on `/api/search` (decision 045).
2. **Help preparing a conversation:** «ماذا أسأل مهندسًا أعرفه؟» Generic, with no personal data.
3. **For the owner, not students:** drafting activity items and field-profile drafts for human verification, and checking Arabic consistency.

Any AI feature needs:
- an eval set
- a rule that it never recommends a major
- rate limits and a spend cap
- a privacy review

### What the results should show
1. A framing line: «هذه مجالات لتستكشفها، لا قرار.»
2. The three bands, each field card with:
   - **why:** the student's own answers
   - **what you'd study:** example majors from the official lists
   - **which school track** prepares for it (sourced, from `school_tracks.json`)
   - **one thing to try this week**
   - **where it's studied:** a link to the explorer filtered by field, with counts computed from data
   - **programs that fund it**, only where the official list names the field (e.g. SDAIA for AI)
3. Next steps:
   - Grade 10: take the official measure.
   - Talk to the counsellor; three questions to ask.
   - Ask someone in the job.
   - Print or save the sheet for the career file.
   - «أعد النشاط بعد شهر».
4. The sources for every fact on the page (project rule).

### Connecting to universities and scholarships
- **Already possible [V]:**
  - `universities.json` has 13 fields (8 إمداد, 5 الرواد) with their majors and the universities listed under each.
  - The explorer already filters by field.
  - Program pages say who each program is for.
- **Needed:**
  - Field profiles that sit between the activity and the explorer.
  - Honest coverage notes:
    - **Health and education are not in the scholarship field lists [V].** Their cards route to «الدراسة في السعودية» (planned) and official sources.
    - Never imply a scholarship exists for a field unless an official list says so.
- **Important trap:** in grade 10 the next real decision is the **school track**, not a university. The result for grade 10 should lead with "which tracks keep this field open" (sourced). Aramco's previous cycle accepted only some tracks (already on the grade 10 page).

### Privacy
- v1 stores nothing and sends nothing: no server calls with answers, no analytics, no third-party requests (project rules).
- "Save on this device" is optional and clearable (shared family phones are common [H]).
- A shareable link must not carry the answers. At most, field IDs ("my 3 fields to explore").
- If accounts come later (Launch 2): store only the fields chosen and the actions planned, opt-in and deletable, after checking Saudi personal-data law (PDPL) obligations for minors on official pages. Not verified here.

---

## 7. Concrete example

**The student:** Noor (they), grade 10, general school.
- Enjoys drawing and helping a younger sibling with maths.
- Has never coded.
- Their family hopes for medicine.
- Arrives from the grade 10 page's «لم تقرر بعد؟» link, on a phone.

**The journey:**
1. **Framing.** Noor reads «نشاط استكشافي، ليس اختبارًا. 10 دقائق. لا نحفظ إجاباتك.» and taps «ابدأ».
2. **Difficulty.** Picks «لم أجرّب أشياء كثيرة بعد» and «أهلي يتوقعون تخصصًا معينًا».
3. **Activities.** 26 cards, about 6 minutes.
   - Enjoys: the poster, the logo, explaining a lesson, organising an event.
   - Not tried: «كتابة برنامج صغير» → «نعم، أودّ أن أجرّبه».
   - Dislikes: the lab experiment.
   - Between parts: «لم تجرّب بعد 9 من 26 نشاطًا، وهذا طبيعي.»
4. **Progress and values.** Progress in art and English. Values: الإبداع, مساعدة الناس. Field the family expects: الصحة.
5. **Review.** Noor changes the lab answer to «لا بأس به» and taps «اعرض النتيجة».

**The result screen (phone, RTL; Arabic as students see it, notes in brackets):**

> **مجالات لتستكشفها**
> هذه مجالات لتستكشفها، لا قرار. بنيناها على 17 نشاطًا جرّبته، و9 لم تجرّبها بعد.
>
> **تجذبك الآن**
>
> **الفنون والتصميم**
> لماذا؟ استمتعت بـ«تصميم شعار» و«تصميم ملصق»، ولاحظت تقدمك في التربية الفنية.
> ماذا تدرس؟ مثل: تصميم المنتجات [من القوائم الرسمية]
> المسار الثانوي: [المسار الذي يهيئ له، من وثيقة الوزارة، أو يُخفى إن لم يُذكر]
> جرّب هذا الأسبوع: صمّم ملصقًا لنادٍ في مدرستك، واطلب رأي معلمك.
> أين يُدرس؟ ← [عدد من البيانات] جامعة في قوائم الابتعاث
>
> **التعليم**
> لماذا؟ استمتعت بـ«شرح درس صعب لزميل».
> ⓘ هذا المجال ليس في قوائم الابتعاث. ← الدراسة في السعودية [باب مخطط]
>
> **تستحق التجربة**
>
> **تقنية المعلومات**
> لم تجرّبها بعد، وقلت إنك تودّ ذلك.
> جرّب: [دورة مجانية رسمية، بعد التحقق منها]
> المسار الثانوي: علوم الحاسب والهندسة يهيئ لتخصصاتها [وثيقة الوزارة 2025]
> برامج تموّلها: برنامج الابتعاث في الذكاء الاصطناعي (سدايا) ←
>
> **المجال الذي ذكرته: الصحة**
> لم تختر من أنشطته ما يجذبك بعد، وهذا لا يعني أنه لا يناسبك.
> ماذا تدرس؟ [من مصدر رسمي]
> المسار الثانوي: الصحة والحياة يهيئ للتخصصات الصحية [وثيقة الوزارة 2025]
> جرّب: تطوّع في فعالية صحية مدرسية، أو اسأل طبيبًا تعرفه هذه الأسئلة الثلاثة ←
> كيف تتحدث مع أهلك عن اختيارك ←
>
> **لا تجذبك الآن** (٣ مجالات) ▸
>
> **خطوتك التالية**
> ☐ أنت في أول ثانوي: أدِّ مقياس الميول المهنية من وزارة التعليم في مدرستي [بعد التحقق من الصفحة الرسمية]
> ☐ اختر مجالًا واحدًا وجرّبه هذا الأسبوع
> ☐ اعرض هذه الصفحة على الموجه الطالبي، وضعها في ملفك المهني (قسم «اكتشف ذاتك»)
> ☐ أعد النشاط بعد شهر، وقارن
>
> [اطبع أو احفظ صورة] [احفظ على جهازي] [امسح إجاباتي]
> المصادر: …

**What Noor leaves with:**
- Two fields to look into, and one to try.
- A respectful, factual view of the family's field.
- The track decision in front of them.
- Three concrete actions.
- Nothing said about what Noor "is".

---

## 8. A realistic first version (how a professional team would do it, at 5 h/week)

| Step | What | Effort | Gate to the next step |
|---|---|---|---|
| 0 | **Before Launch 1: nothing new.** Finish the planned «لم تقرر بعد؟» guide (content, decision 057): the "why you're stuck" routes as plain links, plus the official-measure facts checked from the laptop. | S–M | Live and sourced |
| 1 | **Usability test** (planned): add undecided-student tasks and a **paper prototype** of 10 activity cards and one result card. | S | Go and stop signals (section 2) |
| 2 | **Field profiles** for the 10 broad fields (8 with واضح data, health and education with routing). Sourced, `last_checked`, English. | M–L | Counsellor review of wording |
| 3 | **Activity items:** about 30 drafted, reviewed by 1–2 counsellors and a career-development specialist (relevance rating per item, keep the agreed ones), cognitive interviews with 5 students (mixed genders, tracks, regions if possible). | M | Items understood; no field drawn only by one gender in the pilot |
| 4 | **Build v1:** a server-rendered page plus a small JS file. Rules in a reviewed JSON (`data/exploration.json`, nothing official hard-coded). No storage, no requests. Tests for the scoring rules, Arabic/English parity and accessibility basics. | M | Tests green; browser check at 320–1280px |
| 5 | **Pilot** with 8–10 students, plus a follow-up after 2–4 weeks via a counsellor | S | Outcome measures (section 9) |
| Later | AI Q&A over field profiles; saving "fields to explore" with accounts | n/a | Eval set; privacy review |
| Probably never | A home-made scored interest measure | n/a | Only with a research partner and full validation |

---

## 9. Testing scientific quality, usability, and whether students leave better informed

### Scientific quality (appropriate to a non-scored activity)
- **Content review:**
  - 2–3 experts rate each activity's relevance to its field.
  - Keep the items they agree on. A content validity index is a standard way to do this [J].
- **Cognitive interviews:** students think aloud. Does «لم أجرّبه بعد» mean what we think? Are any items dialect-dependent, gendered or class-dependent (e.g. activities needing money or travel)?
- **Gender check:** in the pilot, compare which fields reach «تجذبك الآن» by gender. Large gaps on single items mean rewrite them. This draws on the item-development finding in Su et al. 2009 [R].
- **Stability check:** the same students a week later. Do the bands mostly repeat? If not, the result is noise and must be reworded or dropped.
- **Agreement with the official measure** (if students share it voluntarily, without storing it): rough consistency only, never to claim validity.

### Usability
- 5 students on their own phones, moderated:
  - completion
  - time (target under 10 minutes)
  - where they hesitate or go back
  - whether they find the review screen and the "haven't tried" option
- Accessibility:
  - keyboard only
  - VoiceOver and TalkBack in Arabic
  - 200% zoom
  - both themes
  - An automated checker (axe) needs a download, so ask first.

### Did they leave better informed? (the real outcome)
**Before and after, in sessions:**
- Can they name 2–3 fields to explore and **one concrete action**?
- Can they say, for one field, what you study and which track prepares for it?

**Follow-up after 2–4 weeks:**
- Did they do the action: a course, a conversation, a visit? This matches what OECD links to later outcomes.

**Harm checks:**
- How many say "the site told me what to study" (over-trust)? Should be near zero.
- How many feel discouraged about a field they care about?

**On the live site** (no trackers, no IDs):
- Optional aggregate counts only: completions, and clicks on "try this" and explorer links (the roadmap's own-counter idea).

Note: three or four home-made "how sure do you feel" questions are fine for learning in sessions. Don't publish them as a validated measure.

---

## 10. Sources

Read 2026-11-04 unless noted.

**Project (V):**
- `docs/decisions.md` decision 057
- `docs/research/product-audit-2026-10-13.md` §"Should واضح build a questionnaire?"
- `data/universities.json` (13 fields; no health or education field)
- `data/school_tracks.json`
- `content/grades/grade-10.md`
- the live homepage and `/api/search` at https://wadihguide.com

**Official:**
- Ministry of Education, دليل التوجيه المهني 1444هـ (PDF): definitions of «مقياس الميول المهنية» and «ملف الإنجاز المهني»; names Holland's, Ginzberg's and Super's theories; the school counsellor's role. https://www.moe.gov.sa/ar/aboutus/aboutministry/RPRLibrary/دليل%20التوجيه%20المهني%20١٤٤٤.pdf
- O\*NET licence options: https://www.onetcenter.org/license_tools.html
- O\*NET Interest Profiler versions and languages: https://www.onetcenter.org/IP.html
- O\*NET Mini-IP report (30 items; α .70–.75; the switch from like/dislike/not sure to a 5-point scale): https://www.onetcenter.org/dl_files/Mini-IP.pdf

**Research (abstracts read via Europe PMC):**
- Low, Yoon, Roberts & Rounds (2005), stability of vocational interests, *Psychological Bulletin* 131, doi:10.1037/0033-2909.131.5.713
- Freund & Kasten (2012), validity of self-estimates of cognitive ability (r = .33), *Psychological Bulletin* 138, doi:10.1037/a0026556
- Su, Rounds & Armstrong (2009), sex differences in interests, *Psychological Bulletin*, doi:10.1037/a0017364
- Nye, Su, Rounds & Drasgow (2012), interests and performance, *Perspectives on Psychological Science*, doi:10.1177/1745691612449021

**Research (secondary summaries only; read the paper before quoting):**
- Whiston, Li, Goodrich Mitts & Wright (2017), *Journal of Vocational Behavior* 100, doi:10.1016/j.jvb.2017.03.010 (ScienceDirect 403)
- Brown, Ryan Krane et al. (2003), critical ingredients, *Journal of Vocational Behavior* 62
- Armstrong, Allison & Rounds (2008), public-domain RIASEC markers, *Journal of Vocational Behavior* 73, doi:10.1016/j.jvb.2008.06.003
- Yaghi & Alabed (2021), Arabic CDDQ
- Rounds & Tracey (1996), *Journal of Counseling Psychology* 43, doi:10.1037/0022-0167.43.3.310 (title and DOI confirmed; abstract not read)
- Low et al.'s 12–18 coefficients (.55–.58)

**Cited from the October audit (read then):**
- OECD Working Paper 258 (2021)
- OECD *Dream Jobs?* (2020)
- Nye et al. (2017)

**Press only, unverified:** the Ministry measure's weight in track placement (about 20%) and its report of suggested majors and universities (sabq.org, alwatan.com.sa, okaz.com.sa, via search). **Check on an official page before using anywhere.**
