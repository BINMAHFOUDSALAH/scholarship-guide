> **Status (2026-10-13):** approved by the owner. Milestone L items 1–2 (P0-1…P0-4, P1-3) were implemented the same day (decision 057). Still open from the milestone: the «لسه ما قررت؟» guide and the usability test. Earlier audit: [product-audit-2026-10.md](product-audit-2026-10.md).

# واضح: product audit and strategic roadmap (2026-10-13)

## How this audit was done, and its limits

**What I did**
- Read the code: `app/main.py`, `universities.py`, `search.py`, `content.py`, `universities.js`, the explorer and university templates, all grade, program and resource content, `docs/decisions.md` (001–056), the roadmap, the architecture doc, and the earlier audits (`product-audit-2026-10.md`, `design-audit-2026-10.md`).
- Walked **the live site** (wadihguide.com) in headless Chromium at 390px and 1280px: page text, page heights, requests, filter interactions, and timing on an emulated slow 4G connection.
- Analysed every file in `data/university_details/` (129).
- Probed inputs for reflected XSS, path traversal, odd search input, and the `from` whitelist.
- Scanned all git history for key patterns.
- Read CI history: the last 5 runs on `main` are green, and the suite has 177 tests.
- Read primary sources: Common App and UC fee rules, the O*NET licence, the WEF Future of Jobs PDF, the OECD career-readiness work, the SPA admission figures, and the Ministry of Education's SAMAI release.

**What I could not do**
- **Tests:** I didn't run pytest or pip-audit. They'd need package installs, which you ruled out; CI covers pytest.
- **Accessibility:** no axe run (it would mean downloading a library) and no screen reader.
- **Devices:** no Safari, iPhone or real phone.
- **Students:** none talked to.
- **Sources I couldn't read directly** (marked *unverified* where cited):
  - Common App's fee-waiver help article (it didn't render here). The repo read it on 2026-10-12.
  - The HRDF «سبل» and my.gov.sa pages (403 or client-rendered).

**Evidence labels:** **[V]** verified by me in code, the live site or a primary source · **[R]** published research · **[J]** my professional judgment · **[H]** a hypothesis to test with students.

**A note on the WEF dates** (you asked why 2025): the *Future of Jobs Report* comes out every two years (2020, 2023, Jan 2025). WEF's publications page still lists 2025 as the latest edition. The 2027 edition is in preparation (its employer survey closed in September 2026). For anything newer I used WEF's **January 2026** briefing on AI and entry-level work.

---

## A. Executive assessment

**What واضح is today [V].** A carefully engineered, source-first Arabic guide to **studying abroad on Saudi scholarships**. It has:
- the King's scholarship (4 tracks), SDAIA, Aramco and KGSP
- an explorer over the Ministry's 290-university guide, with requirements for 129 universities
- a US-applications/fee-waiver guide
- test pages (IELTS, TOEFL, SAT, القدرات/التحصيلي)
- three grade pages

The engineering is unusually disciplined for a solo project: a trust rule enforced by tests, no third-party requests (verified: all 17 homepage requests go to wadihguide.com), good performance, 177 tests, and CI-gated deploys.

**What's working**
- The trust model: sources on every fact, and conflicts shown rather than resolved.
- The university page: a model of "what a Saudi student needs on one page".
- The admission ≠ scholarship message.
- Arabic counting and RTL care.
- Speed: homepage LCP about 1.5 s on emulated slow 4G, a cold cache in Chromium.

**Biggest weakness [J].** The **promise is far wider than the product**. The tagline is «مستقبلك بعد الثانوية، بوضوح», but the site serves one path, study abroad on a scholarship, which most graduates won't take:
- In the most recent official figures I could find (SPA, 2019), Saudi government universities and technical training had **311,572 seats for 356,269 graduates**, enough for about 87% ([SPA](https://www.spa.gov.sa/1936828)) [V; old data].
- The **undecided student has no door at all**. Searching «مهارات» or «وظائف» on the live site returns 0 results [V].

**How close to the mission?** For Student A (scholarship) and Student C (US/UK applicant): about 60–70%, and well-sourced. For Student B (undecided): about 5%. For the student who'll study in Saudi Arabia (the majority): about 10% (a few lines on القبول الموحد on the grade pages).

---

## B. The three highest-impact problems

1. **Published facts are wrong or out of date in places, on a site whose whole value is trust [V].**
   - The grade 12 page says «في 60 من **102** جامعة في **مسار الرواد**…» and «69 من 102 جامعة في مسار الرواد». الرواد has 30 universities.
     - Cause: `partials/apply_year.html:19,21` hard-codes «مسار الرواد», while `Explorer.timeline_stats()` counts all researched universities, which since waves 2–4 includes إمداد.
   - The grade 11 tests table says «جامعات مسار إمداد: **لم نجمع متطلباتها بعد**» (`partials/test_needs.html:26`). In fact 99 of 223 have been researched.
   - The homepage «مفتوح للتقديم الآن» lists الرواد and SDAIA in lime ("open now / your next step"), without saying who can act. In October, a grade 12 student can't apply to either:
     - الرواد needs an unconditional admission first.
     - SDAIA needs an existing scholarship.

     A reader can easily conclude "I should apply now" or "I'm missing it".
2. **The undecided student (B) and the student staying in Saudi Arabia have no starting point [V].**
   - No page answers "what should I study?". Grade 10 only says to list your strengths and ask the counsellor.
   - Free official interest measures already exist and aren't mentioned:
     - the Ministry's track-placement measure in grade 10 via مدرستي
     - HRDF's «سبل» measure for Saudis aged 16+ (secondary sources; *unverified* on the official page)
   - The Saudi-university path (قبول, composite score, confirming the seat, TVTC) is scattered across sentences on grade pages.
3. **The scholarship-vs-admission timing trap isn't surfaced where students decide [V/J].**
   - The current الرواد window closes 15 Nov 2026. A grade 12 student's admission results arrive in Dec–Mar.
   - The site explains this well, but only deep in the grade 12 page («والابتعاث؟ لا يتبع هذه الأشهر»).
   - It isn't explained on the homepage card, the program page's opening, or next to «مفتوح الآن» on university pages (e.g. MIT shows "Early Action 1 Nov 2026" and "الرواد مفتوح حتى 15 نوفمبر" side by side).
   - Same pattern for the UK: 15 of 26 UK universities say the Saudi certificate **isn't enough for year 1**. But the page doesn't connect that to the scholarship's foundation-year conditions (90% average + IELTS 5.5) (`university.html:192–195`). That's the single most decision-relevant link for a UK applicant.

---

## C. Student journeys

### Student A: the scholarship applicant
| Step | What happens | Verdict |
|---|---|---|
| First question | "Can I get a scholarship? What are the conditions?" | — |
| Entry | Homepage → «البرامج» → King's scholarship card → program page | ✓ findable |
| Understanding | The program page is clear on "admission first, then scholarship", ≤3 offers, conditional-offer rules, no minimum high-school %. It's 12.2 phone screens long [V]. | ✓ content, ✗ length |
| Vocabulary | «الرواد / إمداد / مسار / قائمة / ترتيب / مجال» are used before they're taught. The «ما الفرق بين المسارات؟» help is folded inside the explorer's filters. | ✗ needs prior knowledge |
| Misreading risk | Lime «مفتوح الآن» on the homepage with no "لمن معه قبول" qualifier | ✗ (Problem B1) |
| Dead end | **Nothing on "if I don't get الرواد/إمداد, what then?"** (self-funded then join later; Saudi universities; Aramco/KGSP; واعد programs) | ✗ discouraging |

**Most important improvements:**
- a 4-step «طريقك للابتعاث» strip at the top of the program page (admission → upload → selection → nomination), with the current window's "for whom"
- an «إذا ما ضبط؟» alternatives section
- the «لمن» line on every «مفتوح الآن» card

### Student B: the undecided student
| Step | What happens | Verdict |
|---|---|---|
| First question | "وش أتخصص؟" / "وش يناسبني؟" | — |
| Entry | No door. Nav = grade, programs, universities, deadlines. Search «تخصص» returns test pages; «مهارات», «وظائف» return 0 [V]. | ✗ stuck immediately |
| Grade 10 page | "Write your strengths… pick two tracks… ask the counsellor" | partial |
| Majors | The explorer has the official field → major list (good raw material), but it's framed as "which universities are on the lists", not "what is this field". | ✗ |

**Most important improvement:** one honest «لسه ما قررت؟» guide (see H). It should route to the official interest measures, push exploration *by doing*, and map fields → majors → school track → where they're studied, using data واضح already has.

### Student C: already preparing (e.g. US or UK)
| Step | What happens | Verdict |
|---|---|---|
| Entry | Explorer → university page | ✓ strong |
| University page | Platform, fee, waiver, IELTS/TOEFL/Duolingo, SAT, dates, acceptance rate, sources [V] | ✓ best part of the site |
| US system | `/resources/us-applications`: systems, contents, a 5-question waiver flow, a waiver table (checked against UC's page today [V]) | ✓ good |
| UK system | **No UCAS guide**, though 36 UK universities are on the lists and the UCAS 13 Jan deadline is in the data | ✗ gap |
| English tests | Lists show **IELTS only** at a glance. Duolingo is never mentioned outside university pages (see the Duolingo section). | ✗ |
| Organising | «قائمتي» works (device-only); no compare, no checklist | ok |
| Saudi-specific friction | **[H]** Whose role is the "counselor" in a Saudi school? Are transcripts in Arabic? Who writes English recommendations? Students likely trip on these; nothing covers them. | ✗ unknown |

**Biggest gaps vs. needs:**
1. B has nothing.
2. Saudi-university students have nothing.
3. Timing/foundation-year connections are missing at the point of decision.
4. A UK system guide is missing.
5. The English-test answer is IELTS-centric.

---

## D. Product strategy and positioning

The strongest realistic options:

| Option | Pros | Cons | Fit with ~5 h/week |
|---|---|---|---|
| 1. Stay a scholarship-abroad guide | Deep, maintainable, already good | Tagline mismatch; serves a minority; B unserved | ✓ |
| 2. Become a full career + domestic + abroad platform | Matches the tagline | Content and maintenance explode; trust drops; can't verify at that breadth | ✗ |
| **3. A deep core, plus thin honest doors (recommended)** | Keeps the verified depth. B and domestic students get a real first step that routes to *official* tools instead of rebuilding them. | Needs discipline: doors stay thin | ✓ |

**Recommendation [J]:**
- **Positioning:** «واضح: من الحيرة إلى خطوتك الجاية بعد الثانوية — بمصادرها الرسمية».
- **Core (deep, verified):** study abroad, i.e. scholarships plus applying to universities on the lists.
- **Doors (one page each, sourced, mostly routing):**
  1. «لسه ما قررت؟»
  2. «الدراسة في السعودية»
  3. the existing grade pages as the zero-knowledge entry
- **Defer:** accounts, a quiz engine, a chatbot, personalisation.
- **Keep the tagline.** The doors make it honest.
- **What would change this:** if the usability test shows students only come for the scholarship, narrow the tagline instead (cheaper than building the doors).

---

## E. Recommended information architecture

**Homepage (top to bottom, phone):**
1. Tagline and lead (keep).
2. **«ابدأ من صفك»** (keep: the zero-knowledge entry).
3. **New: three goal doors** under it, as text links, not cards:
   - «أبي أدرس برا»: program page / explorer
   - «أبي أدرس في السعودية»: the new page
   - «لسه ما قررت»: the new guide
4. **«الآن» for the current month (change):**
   - lead with the actionable item for grade 12, the next university deadlines (already computed by `Explorer.upcoming_deadlines()`)
   - then open scholarships, each with its «لمن»
5. Programs (keep, compact).
6. The university search panel (keep).
7. Tuwaiq band: no task value. Move it lower or to /about. This one's your call, low priority.

**Nav:** keep the 4 items. Don't add more on phones. Add a **`/guides` index** (footer plus homepage link) listing every guide. Today resource pages are reachable only through in-page links [V].

**Retain / change / merge / remove / add:**
- **Retain:** university pages, explorer, grade pages, US guide, test pages, «قائمتي», /news.
- **Change:**
  - the «مفتوح الآن» cards (add «لمن»)
  - the program page: a 4-step strip at the top; fold the FAQ
  - the explorer's إمداد-without-field view: 223 names, **49.5 phone screens**, 3,969 DOM nodes [V]. Default to "pick a field" instead, since rank exists only per field.
- **Merge:** /news «فُتح وأُغلق مؤخرًا» (11 closed واعد items) into one folded line.
- **Remove / deprioritise:** the remaining 143 logos (see F).
- **Add:** «لسه ما قررت؟», «الدراسة في السعودية», `/guides`, `/resources/duolingo`, `/resources/uk-applications` (P2).

---

## F. UX and visual design

**Overall [J]:** the visual identity isn't the bottleneck. Contrast is tested, the type scale is consistent, the colours have fixed meanings. The problems are **coverage, page length, and context at the point of decision**. Don't redesign.

### Applied-filter ✕: diagnosis and fix
- **The ✕ itself now works [V].** I applied search + track + country + language, then removed the country: the other three stayed. Two rapid removals kept the right filter. The chips are 44px with 36px ✕ targets at both 390px and 1280px. The earlier race (decision 048: stale hrefs copied into the form) is fixed.
- **The real remaining bug [V]:** after **«مسح الكل»** or removing the **last** chip:
  - the code focuses the search box: `universities.js:331-332`, `(next || input).focus()`
  - the box's `focus` listener (`universities.js:159`) opens the **suggestions panel: 157 options, 420px tall**, over the results, and the page jumps to the top
  - on a phone this reads as "the ✕ did something else"
- **Second inaccuracy:** focus goes to the *first* remaining ✕, not the "next" one that decision 048 describes.
- **Recommended fix:**
  1. After removal, focus `(next || results)` (`#results` already has `tabindex="-1"`). Never focus the combobox programmatically.
  2. Open the suggestions on `input`, or on a pointer focus of the box, not on every programmatic `focus`.
  3. Focus the ✕ that took the removed chip's position.
- **Verify:** a Playwright script on 390px and 1280px:
  - apply 3 filters → tap «مسح الكل»
  - assert `#q-suggest[hidden]`, `document.activeElement === #results`, URL empty
  - repeat with the last single chip
  - keep the existing two-rapid-removals check
  - keyboard: Tab to a ✕, Enter, then focus is on the neighbouring ✕
- CI runs no browser tests today. All JS behaviour (filters, «قائمتي», back-restore) is checked only by hand (see I).

### Logos and flags (evaluated, not assumed)
- **University logo, on its own page only:**
  - **Keep.** It answers "is this the one I meant?" where confusion is real: UCL vs UCLouvain, which the logo matching already caught; University of Washington vs Washington University in St. Louis.
- **The remaining 143 logos: defer [J].**
  - Each takes agent batches plus a manual review plus licence tracking.
  - The gain is recognition on pages that already show the English name.
  - Spend those hours on the doors.
- **Flags in lists (20×15, decorative):**
  - **Keep, as is.** They're cheap (15 cached SVGs), help scan mixed-country lists, and the text carries the meaning.
- **Never add logos to lists or the homepage:** density on phones, weight, and an implied endorsement.

### Other UX
- **Page length on phones [V]:** program page 12.2 screens, explorer 10.6, إمداد browse 49.5. Fix the last two first.
- **Vocabulary:** add a short «كلمات تحتاجها» glossary (مسار، قائمة، ترتيب، مجال، قبول مشروط، Early Decision، UCAS، Foundation) linked inline. **[H]** first-timers don't know these terms; check in the usability test.
- **Accessibility:** no regressions found in spot checks. Outstanding: the focus bug above, a real screen-reader pass (VoiceOver/TalkBack), and Safari.
- **«قائمتي» on Safari:** WebKit's 7-day storage cap may wipe lists [unverified for this site]. Test on an iPhone.

---

## G. Scholarship and admissions guidance

**What's strong [V]:**
- conditional-offer rules
- admission ≠ scholarship
- ≤3 offers
- no high-school minimum
- the foundation-year conditions
- conflicts shown, not resolved (the age rule)
- per-university fee and waiver data

**Gaps, ranked:**
1. **Timing for current grade 12 students.**
   - "The window open now is for students who already hold admission. Yours will be next year's window, announced each year."
   - Say it on the homepage card, the program page top, and university pages.
2. **UK foundation-year link.**
   - Where `saudi_certificate.direct_entry == false`, add one line linking to the scholarship's foundation-year conditions (90% + IELTS 5.5, «أو ما يعادله»).
   - Small template change, data already there.
3. **"If not this, then what?"** Alternatives, each linked to its official page:
   - self-funded study, then the program's rule for self-funded students (already sourced on grade 12)
   - Saudi universities via قبول
   - Aramco / KGSP / واعد
4. **UK system guide (P2):** UCAS basics, the 13 Jan equal-consideration date, foundation years, Saudi certificate status. The data for 26 UK universities already exists.
5. **Saudi-specific application friction (research first [H]):**
   - who acts as "counselor": Common App's international guide reportedly allows "any school official"; that PDF link has moved, so re-verify
   - transcript language and translation, per university
   - English recommendation letters

### Fee waivers: what's verified, and how to explain it
- **UC [V, read today on [UC Apply now](https://admission.universityofcalifornia.edu/apply-now.html)]:**
  - $80 per campus; $95 for international and non-immigrant applicants
  - the waiver is "for United States citizens, permanent residents, and applicants eligible for AB540 benefits"
  - waivers can't cover more than four campuses
  - The site states this correctly, including "$80 reduced fee ≠ waiver".
- **Common App [repo-verified 2026-10-12; I couldn't re-render it]:**
  - "International students may be eligible… Each college has their own policies."
  - Colleges may accept it only for US students, or not at all.
  - Eight of the nine indicators are US programmes. One is "a supporting statement from a school official…".
  - Steps: Profile → Common App fee waiver → sign. The counselor confirms.
  - The site's 5-question flow is the right structure.
- **Improve:**
  - **Split the `accepts_common_app` class.** 18 universities sit in it, but per the repo's own research note, many pages don't say whether international students qualify.
    - Show «تقبل إعفاء Common App (لم تذكر الطلاب الدوليين)» unless the page says international students qualify.
    - Today the table header can read as "you'll get it".
  - **Add one line:** «لا تجيب بمعلومات غير صحيحة لتتأهل», with Common App's own wording ("answer with your own financial circumstances"). It's already partly there; make it a visible notice.
  - **Correct fact:** none of the 65 researched US universities lists a $0 fee [V]. Common App says "500+ colleges" have no international fee, but none of them are on our lists. Say so, so students don't hunt for it.
  - **Maintenance:** fees and waivers change each August, so tag `application_fee` for an August re-check in `stale_facts.py` (seasonal, not 90-day).

### Duolingo (your question)
**[V] What's in the data:**
- The schema has a `duolingo` slot next to `ielts` and `toefl_ibt`. Of the 129 researched files:
  - **62 give a Duolingo minimum** (US 43, UK 10, Canada 6, other 3)
  - **15 accept it with no published minimum, or have a conflict** (Harvard, Stanford, Yale, Penn, NYU, WashU…)
  - **44 have `null`**: UK 20, US 9, Australia 7, other 8
  - **8 have no English block at all**: 7 in India + Gallaudet
- `null` mixes three things: *not accepted*, *accepted but no number*, and *not checked*. The wave briefs said "TOEFL iBT and Duolingo only if the page states them".
  - "Doesn't accept" lives only in free-text notes: Michigan doesn't accept it; Georgia Tech says Duolingo doesn't satisfy the USG requirement.

**What students see:**
- Duolingo appears only on university pages.
- The explorer row and «قائمتي» show **IELTS only**.
- There's no Duolingo resource page.

**Why it matters [J]:** Duolingo is taken online at home with results in about 2 days ([official](https://englishtest.duolingo.com/applicants), price *unverified*). It's often the cheapest option, so a cost-sensitive student may plan around it, and it's risky in two places:
1. Universities that refuse it.
2. **The scholarship's own English conditions name IELTS («آيلتس 5.5 أو ما يعادله»).** Whether Duolingo counts as "equivalent" isn't stated. Never imply it does; tell students to ask the Ministry (19996 / تواصل).

**Recommended:**
1. **Data:** `accepted: true | false | null` on each English test object. Backfill from the existing notes and sources (no new research for the 77 with a number or a note).
2. **Display:**
   - University page: «Duolingo: لا تقبله» shown explicitly.
   - Explorer and «قائمتي» rows: IELTS · TOEFL · Duolingo, compact.
3. **Content:** a short `/resources/duolingo` page like the IELTS one, with the scholarship-equivalence caveat.
4. **Research:** re-check the 44 nulls only when the wave re-check runs (no special wave).

---

## H. Career discovery, future skills, high-school preparation

### Should واضح build a questionnaire? Not now.
- **Free official measures already exist [V/unverified]:**
  - the Ministry's interest measure for track placement (grade 10, مدرستي)
  - HRDF «سبل» (Saudis 16–40, free, 30–45 min; secondary sources, *verify in a browser*)
- **The O\*NET Interest Profiler has no Arabic version [V]** ([O\*NET](https://www.onetcenter.org/IP.html): English/Spanish).
  - Its CC BY-ND option forbids modified versions.
  - Its Developer License option requires attribution and that you "validate all products that incorporate Tools content" ([licence page](https://www.onetcenter.org/license_tools.html)).
  - An Arabic adaptation is therefore a psychometrics project, not a feature.
- **Interests are useful but weak predictors [R]:**
  - Nye et al. (2017, 92 studies): interest congruence predicts performance at about r = .32.
  - Congruence and satisfaction effects are small and depend on the method.
  - So: good for *exploration*, wrong for *telling a teenager what to study*.
- **What evidence links to better adult outcomes is doing, not scoring [R]:**
  - OECD's career-readiness work (10 longitudinal datasets, 8 countries) finds teenagers who **explore** (career conversations, workplace visits), **experience** (volunteering, part-time work, placements) and **think** about work (certainty, alignment) have lower unemployment, higher wages and more career satisfaction as adults ([OECD WP 258, 2021](https://one.oecd.org/document/EDU/WKP%282021%2915/en/pdf)).
  - Caveat: mostly Anglophone data.
  - OECD's *Dream Jobs?* (2020): about half of 15-year-olds expect to land in just 10 jobs, and the narrowing is strongest among disadvantaged students. Exposure to unfamiliar fields matters.

**Recommended instead: one «لسه ما قررت؟» guide (P1), content only, no storage:**
1. **Take the official measure you already have** (grade 10 Ministry measure / سبل at 16+). Read the result as "fields to explore", not a verdict.
2. **Explore three fields by doing this term:**
   - a free official course
   - a talk with someone in the job
   - a volunteering hour, a competition or a project
   - each with "what to notice about yourself"
3. **Map field → majors → school track → where it's studied:**
   - reuse the explorer's official field/major groups (already in `universities.json`)
   - reuse the grade 10 «المسارات الخمسة»
4. **Interest ≠ aptitude ≠ eligibility ≠ demand.** One short box. A hobby doesn't dictate a major, and changing your mind is normal.

**Later (P2), only after the usability test:**
- **Field profiles** keyed to the guide's إمداد fields: what you study, typical work, school track, majors, "try this week".
- **Demand claims stay hidden unless officially sourced** (decision 028 applies).
- Then, maybe, an "explore by activity" picker: pick activities → fields to explore, explained, no score, nothing stored.

### Future skills and AI literacy: one short section, not a pillar
- **[V] WEF Future of Jobs 2025** ([PDF](https://reports.weforum.org/docs/WEF_Future_of_Jobs_Report_2025.pdf)):
  - Analytical thinking is the top core skill (69% of employers); creative thinking 57%.
  - AI & big data is the fastest-growing skill.
  - Employers expect 39% of core skills to change by 2030 (Saudi Arabia: 40%).
  - In Saudi Arabia, over 70% of employers see technological literacy rising, followed by networks/cybersecurity and AI & big data.
  - 38% of companies in Saudi Arabia plan to remove degree requirements (19% globally).
- **[V] WEF, Jan 2026 entry-level briefing** ([PDF](https://reports.weforum.org/docs/WEF_Briefing_AI_and_Entry-Level_Jobs_January_2026.pdf)): 36% of executives expect AI to increase entry-level jobs and 38% expect a reduction. Projections are uncertain, so don't promise any field.
- **AI literacy for a high-school student [R/J]:**
  - Use the UNESCO *AI Competency Framework for Students* (2024: human-centred mindset, ethics, techniques, system design) and the EC–OECD *AILit* framework (Engage / Create / Manage / Shape; [ailiteracyframework.org](https://ailiteracyframework.org/)).
  - In practice:
    - check AI output against sources
    - don't paste personal data
    - know when not to use it, including each university's rules on AI in application essays (*to verify per university*)
  - Free official route: **SAMAI** (SDAIA with the Ministry of Education and HRSD; over 1M trained; the Ministry "welcomed university and school students") ([Ministry of Education](https://www.moe.gov.sa/en/mediacenter/MOEnews/Pages/news1_09112025.aspx)). Cost isn't stated on that page.
- **Framing [J]:** foundational capabilities that travel across fields (analytical thinking, writing/communication, quantitative reasoning, tech/AI literacy, independent learning). Not "everyone must code".

### High-school preparation
- The grade pages are the right container. Don't add a separate "prep" section.
- **Add one block per grade:** «تجارب منخفضة التكلفة» (volunteering, competitions, KAUST/Mawhiba enrichment where official, reading, a small project).
- **Explicit equity line:** "you don't need an impressive CV".
- **Branch where systems differ [J]:**
  - US: holistic (activities, essays)
  - UK: subject-focused and certificate/foundation-sensitive
  - Saudi: composite score (القدرات/التحصيلي + GPA)

---

## I. Security, reliability, performance, architecture

| # | Finding | Severity | Evidence | Fix |
|---|---|---|---|---|
| 1 | **No security headers**: no CSP, X-Content-Type-Options, Referrer-Policy, frame-ancestors/X-Frame-Options, HSTS, Permissions-Policy | Low–Med (no user data or auth; defence in depth, clickjacking) | [V] live response headers | A small middleware. Start the CSP as Report-Only: inline theme script by hash; YouTube frame only after the click. HSTS once stable. |
| 2 | **HEAD requests return 405** | Low | [V] `curl -I /` | Uptime monitors and some link checkers use HEAD. Allow HEAD on GET routes. |
| 3 | Versioned static files (`?v=hash`) sent without long `Cache-Control` | Low (perf) | [V] | `max-age=31536000, immutable` for `/static` when `v` is present |
| 4 | Python version not pinned on Render | Low (reliability) | [V] no `.python-version`/`runtime.txt`; the roadmap also notes it | Pin to 3.13, matching CI |
| 5 | No dependency audit | Low–Med | [V] no Dependabot or pip-audit in CI; I couldn't run pip-audit | Enable GitHub Dependabot alerts (no code), or pip-audit in CI (asks for an install) |
| 6 | No browser tests in CI; filters, «قائمتي», back-restore, combobox are untested by CI | Med (regression risk) | [V] tests are pytest + httpx only; the focus bug got through | A small Playwright smoke suite in CI (an install, so ask first) |
| 7 | Reflected input / XSS / traversal | None found | [V] `<script>` in q is escaped; `..%2F` → 400; `from=javascript:` ignored; FTS5 input quoted; SQL parameterised | — |
| 8 | Secrets | None found | [V] git-history pattern scan clean; `.env` ignored and permission-locked; ElevenLabs key read from outside the repo | — |
| 9 | `| safe` on Markdown | Acceptable | [V] owner-authored content only | Keep it that way. If the planned update-monitor agent ever writes content, it goes through human review (already planned). |
| 10 | No rate limiting on `/api/*` | Low now, **High once a paid chatbot exists** | [V] Cloudflare DNS-only, no WAF | Not now. Before any LLM endpoint: rate limit, spend cap, cache. |
| 11 | Privacy | Strong | [V] no third-party requests until a click; «قائمتي» stores ids only in localStorage; no forms | Keep. Don't add accounts until a proven need. |

**Performance [V]:** emulated slow 4G, cold cache, Chromium:
- homepage: LCP about 1.5 s, 396 KB uncompressed, 251 KB of it fonts (4 woff2)
- university page: LCP about 0.3 s
- No action needed. The heavy case is DOM size on the long إمداد list (fixed by E).

**Architecture [J]:**
- JSON + Markdown + in-memory FTS5 fits up to thousands of records.
- **Don't add a database** until accounts exist. Keep "one fact shape" as the contract.
- The thing that will hurt first is **maintenance load, not scale**:
  - 129 detail files with several dated fields each
  - fees changing every August
  - scholarship windows changing every year
- **Invest in:**
  - `stale_facts.py` seasonal tags
  - a public «بلّغ عن خطأ» path (see J)
  - the planned weekly broken-link check (P2)

---

## J. New opportunities, and ideas to reject

**Worth doing:**
- **«بلّغ عن خطأ» on every fact block.**
  - Problem: trust decays silently.
  - Simplest version: a `mailto:` or X DM deep link with the page URL and fact id prefilled. No backend, no stored data.
  - Risk: spam (low).
  - Beats building monitoring.
- **«كلمات تحتاجها» glossary.**
  - Problem: first-timers lack the vocabulary [H].
  - One Markdown page plus inline links. Cheap, searchable.
- **EducationUSA as a free human-help route for US applicants.**
  - Official advising offices at the US Embassy Riyadh and Consulate Dhahran ([EducationUSA](https://educationusa.state.gov/node/502)); some pages are dated, so verify they're current.
  - One sourced line in the US guide.
  - Better than واضح building "expert review".
- **«شارك قائمتي كرابط»** (ids in the URL). Moves the list between phone and laptop with no account. P2, needs evidence from the test first.

**Reject or defer:**
- **Accounts / dashboard / progress tracking:** a privacy cost for minors; «قائمتي» plus a link covers the need until students ask. *Defer.*
- **Own interest quiz / personality typing:** duplicates official tools; validation and licensing burden; false precision. *Reject for now.*
- **AI chatbot:** retrieval is ready, but the content gaps (B, Saudi path) matter more, and it needs rate limits and a spend cap. *Defer* until the doors exist and an eval set is built.
- **Remaining 143 logos:** *defer* (see F).
- **Rankings / popularity sort:** contradicts "the official list is the order". *Reject.*
- **Non-English-country إمداد wave (111 universities) before Launch 1:** *defer.* Lower demand [H]; language-of-instruction research is harder. Revisit after the new guide PDF.
- **Paid launch ad:** *defer* until the usability test shows the site converts.

---

## K. Prioritised roadmap

Effort: S < ½ day, M 1–3 sessions, L > 3 sessions (~5 h/week).

### P0: trust and broken core
| # | Problem | Approach (why this one) | Benefit | Effort | Evidence / confidence | Verify |
|---|---|---|---|---|---|---|
| P0-1 | "102 universities in الرواد" on grade 12 | Reword `apply_year.html:19,21` to «من الجامعات التي جمعنا مواعيدها (الرواد وإمداد)», or count by track; computing beats hard-coding | No false fact | S | [V] high | Test: the rendered text never names a track whose count it didn't compute |
| P0-2 | "إمداد: لم نجمع متطلباتها بعد" is stale | Compute «جمعنا متطلبات N من 223» from `Explorer.details` | Accurate | S | [V] high | Test asserts the number equals the detail count |
| P0-3 | «مفتوح الآن» with no «لمن» | Use the existing track field (`admission_ar` / `high_school_ar`): a one-line «لمن معه قبول جامعي» on homepage, /news and university-page cards; SDAIA «لمن لديه ابتعاث قائم» | Prevents misreading | S | [V] facts; [H] misreading | Usability: "Can you apply to الرواد today?" Correct answer rate |
| P0-4 | Clearing filters pops a 157-item suggestions panel | Focus `#results`; open suggestions only on user input (F) | The core tool behaves | S | [V] high | Playwright script in F |

### P1: highest value
| # | Problem | Approach | Benefit | Effort | Evidence | Verify |
|---|---|---|---|---|---|---|
| P1-1 | B has no door | «لسه ما قررت؟» guide (H), linked from home, grade 10/11 and 404; indexed by search | Unserved majority gets a first step | M | [R] OECD; [H] demand | Usability task: "You don't know what to study. Find what to do this week." Completion + confidence |
| P1-2 | Saudi-university path missing | «الدراسة في السعودية»: قبول, composite score, confirm the seat (sourced), TVTC, القدرات/التحصيلي links; routing, not rebuilding | Serves most graduates | M | [V] SPA 2019 seats; official pages | Usability task + search «الجامعات السعودية» lands here |
| P1-3 | Timing trap + UK foundation link | Program-page 4-step strip; grade 12 "your window is next year's"; `saudi_certificate=false` → foundation-year conditions link | Prevents the costliest mistake | S–M | [V] | Task: "You'll get MIT's result in December. Can you apply to الرواد this year?" |
| P1-4 | Duolingo invisible / ambiguous | `accepted` field; rows show all three tests; `/resources/duolingo` with the scholarship caveat | Saves money, prevents a wrong test | M | [V] data | Test: every `null` with a "not accepted" note becomes `accepted:false`; page renders the caveat |
| P1-5 | "If not this, then what?" | Alternatives section on the program page | Less discouragement | S | [J] | Task completion |
| P1-6 | Fee-waiver ambiguity | Split `accepts_common_app` by whether international students are stated; add the honesty notice; "none of ours is $0" | Fewer wrong expectations | S | [V] | Test: table labels match the class |
| P1-7 | Validate before building more | **Run the 3–5 student usability test** with the three journeys (scripts exist in `docs/research/`) | Every [H] above gets answered | M (owner) | [R] usability practice | Task success, wrong answers, quotes |

### P2: valuable later
- UK/UCAS guide.
- `/guides` index plus glossary.
- إمداد browse defaults to "pick a field".
- Program page folds.
- «بلّغ عن خطأ» links.
- Security headers (Report-Only first) + HEAD + static caching + Python pin + Dependabot.
- Playwright smoke tests in CI (ask before installing).
- Field profiles.
- «قائمتي» share-link and compare.
- August fee re-check tag in `stale_facts.py`.
- A screen-reader pass and iPhone/Safari checks.

### Deferred / rejected
Accounts, dashboards, email alerts, own quiz, chatbot, 143 logos, rankings, non-English إمداد wave before Launch 1, paid ads (reasons in J).

---

## L. First implementation milestone: «ثقة + باب للمتردد»

**Scope (about 3–4 sessions):**
1. **P0-1…P0-4:** fix the false and stale facts, add «لمن» on open cards, fix the filter-clear focus bug.
2. **P1-3:** the timing and foundation-year connections (template plus existing data).
3. **P1-1 as a first version:** the «لسه ما قررت؟» guide, Markdown only, sourced, with the official-measure links verified from your laptop (Saudi sites block cloud reads intermittently).
4. **Then P1-7:** the usability test with 3–5 students, covering:
   - the three journeys
   - the "can you apply to الرواد today?" check
   - Duolingo vs IELTS: "which test would you take, and why?"

**Why first:**
- Items 1–2 fix things that are **wrong today** on a trust product. They're small and need no student evidence.
- Item 3 is the cheapest way to test the biggest gap (B) without committing to a quiz or field profiles.
- Item 4 decides P1-2, P1-4 and everything in P2 using evidence instead of guesses.

**Deliberately excluded:** Duolingo data migration (next milestone), the Saudi-university page (after the test confirms demand), security headers, logos, UK guide, accounts, AI.

**How to test:**
- `pytest`, with new tests for P0-1/P0-2 counts and the open-card «لمن».
- The Playwright filter script (F) at 390px and 1280px.
- A manual read of grade 12, the homepage and one UK university page on a real phone.
- Then the usability sessions: task success, wrong answers, time, and verbatim confusion points, recorded in `docs/research/usability-2026-11.md`.

**Docs to update when implementing (per CLAUDE.md handoff rule):** `docs/decisions.md` (new decision for positioning: deep core + doors), `docs/roadmap.md`, `docs/architecture.md` (new pages), `LEARNING_LOG.md`.

---

## Sources (primary unless noted)
- UC fees and waivers: https://admission.universityofcalifornia.edu/apply-now.html (read 2026-10-13)
- Common App fee waiver (repo, read 2026-10-12): https://appsupport.commonapp.org/applicantsupport/s/article/What-do-I-need-to-know-about-the-Common-App-fee-waiver
- O\*NET Interest Profiler: https://www.onetcenter.org/IP.html · licence: https://www.onetcenter.org/license_tools.html
- WEF Future of Jobs 2025: https://reports.weforum.org/docs/WEF_Future_of_Jobs_Report_2025.pdf · WEF Jan 2026 briefing: https://reports.weforum.org/docs/WEF_Briefing_AI_and_Entry-Level_Jobs_January_2026.pdf
- OECD career readiness (WP 258): https://one.oecd.org/document/EDU/WKP%282021%2915/en/pdf · Dream Jobs? (2020), via secondary coverage
- SPA admission figures (2019): https://www.spa.gov.sa/1936828
- Ministry of Education on SAMAI (2025-11-09): https://www.moe.gov.sa/en/mediacenter/MOEnews/Pages/news1_09112025.aspx
- EC–OECD AILit: https://ailiteracyframework.org/ · UNESCO AI competency framework for students (2024), via secondary summaries
- Duolingo English Test: https://englishtest.duolingo.com/applicants
- EducationUSA Riyadh: https://educationusa.state.gov/node/502
- Nye et al. 2017 interest congruence (secondary summary); HRDF «سبل» (secondary; verify)
