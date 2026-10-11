# UX redesign, October 2026: audit, research, direction

**Date:** 2026-10-11 · **Scope:** homepage, navigation, universities explorer, university pages, «قائمتي», design system.
**Decision record:** [decision 035](../decisions.md).

## 1. How this was done (and its limits)
- **The current site:** every template, the CSS, and the JS were read. The site was run locally; it is the same commit as the live site (`bac1345`). Screenshots were taken with Playwright at 360, 768, and 1280px wide, in light and dark. axe-core (WCAG 2.0–2.2 A/AA rules) ran on 14 routes at 320px and 1280px in both themes.
- **The research:** this environment can't open web pages directly (network policy), but web search works. The guidance below comes from **search-result summaries** of the sources, not from reading each article in full. Where a point comes from a secondary summary, it says so. No user testing was done; nothing here claims "students said…".

## 2. Baseline (before), measured
| Check | Result |
|---|---|
| Homepage length on a 360px phone | ~7,400px (about 9.5 screens) |
| Horizontal scroll at 320px (WCAG 1.4.10 Reflow) | Homepage +62px, Tsinghua page +23px, King scholarship page +35px (long `nowrap` links and chips) |
| Explorer on a phone | Results start below the first screen (the form is ~600px tall) |
| axe-core (automated) | No violations on any route. Automated tools catch only part of the issues, so the manual review below matters more. |

## 3. What a first-time student on a phone would struggle with (ranked)
1. **Finding the universities tool.** The explorer, our most useful and most unique tool, isn't on the homepage hero. It's one link inside the first program row, plus the nav.
2. **Too much at the same volume on the homepage.** For each of 4 programs: a 180px image, three long facts, the tracks, a toggle, and up to 7 links. Then 3 news groups of up to 4 items each. Nothing says "start here, then this".
3. **The explorer's filters.**
   - Nothing shows which filters are on, and there is no reset.
   - The "المجال" select is greyed out with no reason given.
   - The only examples are placeholder text, which is cut off on phones and disappears on typing.
   - Choosing a university from the suggestions filters a list of one instead of opening the university.
4. **Meaning of numbers and dates.**
   - "الترتيب 2" can be mistaken for a world ranking (it's the position in the Ministry's list).
   - "أقرب موعد: 15 أكتوبر" doesn't say it's the university's deadline (UCAS), not the scholarship's.
5. **The university page answers late.**
   - On Stanford's page, the doctorate lists (useless for a high-school student) come before SAT and deadlines.
   - Nothing on the page says that being on the list doesn't guarantee admission.
6. **Where am I / how do I go back?**
   - The nav has no current-page marker and there is no skip link.
   - «→ كل الجامعات» throws away the search the student came from.
7. **Visual language.**
   - Lime means "open now", but الرواد's chip is also lime, so it looks "open".
   - There are 7 different chip styles.
   - 12px Arabic text appears in chips and notes.
   - The focus ring is invisible on the green band.
8. **Independence.** Official logos are shown, but "not the Ministry" appears only on /about and the program pages.

## 4. What the guidance says, and how we used it
- **Homepage: say what you do, show examples, prompt actions, keep it simple.** NN/g's five homepage principles: easy access, say who you are and what you do, show examples of content, prompt actions, keep it simple; summarized by [principles.design](https://principles.design/examples/5-fundamental-principles-of-homepage-design) from [NN/g](https://www.nngroup.com/articles/homepage-design-principles/). → A shorter lead that names what's here. One primary action (your grade) and one secondary (search), with real example searches. The 12-item board is reduced to what's open now.
- **Visual hierarchy: few sizes, bright for key, muted for secondary.** [NN/g, principles of visual design](https://www.nngroup.com/articles/principles-visual-design/) (search summary: 2–3 type sizes; scale, hierarchy, balance, contrast, Gestalt). → One type scale. Lime only for "open now" and "your next step"; everything else muted.
- **Applied filters must be visible and removable one by one; there should be a "clear all".**
  - [Baymard, applied filters](https://baymard.com/blog/how-to-design-applied-filters): users without an overview narrow more slowly and get disoriented; their benchmark says 28% of sites show none. Baymard also has a [mobile guideline](https://baymard.com/guidelines/2572-applied-filters-on-mobile).
  - The UK Ministry of Justice's [filter a list](https://design-patterns.service.justice.gov.uk/patterns/filter-a-list) pattern: selected filters as removable tags plus "Clear filters".
  - DWP's [filter research](https://design-system.dwp.gov.uk/research/filters) and DfE's [decision to reuse it](https://dfedigital.blog.gov.uk/2025/03/03/applying-filters-consistently-in-dfe).
  - → A server-rendered "applied filters" bar with ✕ links and «مسح الكل».
- **Mobile filtering.**
  - Baymard: mobile filters are usually behind a toggle, which hides which filters are active.
  - Contentsquare (a commercial source, so weaker): [far fewer phone users open filters](https://contentsquare.com/blog/mobile-filter-ux/).
  - DfE: [users look at results first, then narrow](https://becoming-a-teacher.design-history.education.gov.uk/find-teacher-training/researching-filters-across-government).
  - → On phones, results come first. Filters sit behind «الفلاتر (n)», and the active ones stay visible as tags above the results.
- **Autocomplete teaches the vocabulary.** [Baymard, autocomplete](https://baymard.com/research-articles/autocomplete-design): suggestions help users phrase queries and pick the right scope; they trust what's suggested, so suggestions must be accurate. → Majors grouped by their official field (already built). Choosing a university is now a confirmed selection that opens that university.
- **Don't rely on placeholders.** NN/g "Placeholders in form fields are harmful", via [Deque](https://www.deque.com/blog/accessible-forms-the-problem-with-placeholders/) and [Digital.gov](https://digital.gov/2014/11/24/placeholder-text-think-outside-the-box): the hint vanishes on typing, is often low-contrast, and isn't reliably read aloud. → Examples move to visible hint text linked with `aria-describedby`.
- **Status as text tags, never colour alone.** [GOV.UK tag component](https://components.publishing.service.gov.uk/component-guide/tag): tags show status, text contrast above 4.5:1, never only colour, never interactive. → One `status_tag` macro; restriction tags are kept apart from status tags.
- **Breadcrumbs show hierarchy, not history; back links restore history.** [NN/g breadcrumbs](https://www.nngroup.com/articles/breadcrumbs/) (summary: supplement the nav, current page not linked, one line on mobile). → A back link to the student's own search results on university pages, and «→ كل البرامج» on program pages. No deep trail, because the site is only two levels deep.
- **Journeys with an order work best as steps.** [GOV.UK step by step](https://design-system.service.gov.uk/patterns/step-by-step-navigation), tested over eight rounds per [GDS](https://gds.blog.gov.uk/2018/10/17/building-a-better-gov-uk-step-by-step/). → Kept for later (grade task lists, roadmap Stage 1e step 3); the grade pages now put «خطوتك القادمة» first.
- **WCAG 2.2 AA.**
  - Targets at least 24×24 CSS px (2.5.8).
  - Focus not hidden (2.4.11).
  - Reflow at 320px (1.4.10).
  - Status messages announced without moving focus (4.1.3), [per this summary](https://tabnav.com/academy/wcag/success-criterion-4.1.3): announce the result count in a small `role="status"` line, not the whole table.
  - Sources: [WCAG 2.2 quick reference](https://www.w3.org/WAI/WCAG22/quickref/) and [TetraLogical's summary](https://tetralogical.com/blog/2023/10/05/whats-new-wcag-2.2).
- **Arabic type size.**
  - The [UAE government design system](https://designsystem.gov.ae/guidelines/typography): body at least 16px, line height at least 1.5.
  - A study of 73 Saudi sites found 12–16px common and possibly too small (via a [secondary summary](https://hackernoon.com/arabic-website-design-must-bridge-usability-gaps-in-fonts-and-images), weaker).
  - → Body stays 17px / 1.8; nothing smaller than 13px (chips).

## 5. Real tools we looked at (what fits, what doesn't)
- **Discover Uni (UK, official):** [search, filter, save, compare up to 7](https://discoveruni.gov.uk/how-to). The save-then-compare idea fits «قائمتي»; we start with save only.
- **BigFuture (College Board):**
  - [Mobile-first college search](https://allaccess.collegeboard.org/bigfuture-reimagined).
  - Its [filters](https://counselors.collegeboard.org/pdf/pptbigfuturebuildbuildalist.pdf) cover location, major, type, cost, admissions.
  - Our filters are fewer because our question is narrower ("is it on the Ministry's list?").
- **UCAS:** [moved the most-used filters to the main search page](https://www.ucas.com/providers/services/news/updates-search-0). → The track and country filters stay first.
- **Arabic guides such as [dirasaabroad.com](https://www.dirasaabroad.com/pioneers-track/):** long articles copying the list. None searches the official lists by major. That is still واضح's unique value (decision 016).
- **What we don't copy:**
  - E-commerce sorting by popularity or price: rank order is the official list's order.
  - Ratings.
  - Dark-pattern urgency.

## 6. Direction
Three directions were compared:
- **A. Editorial clarity (chosen).** Keep واضح's identity: ivory, forest, Plex Bold, the Naskh wordmark, lime only for "open now" and "next step". Add GOV.UK-grade patterns: back link, status tags, summary list, notices, filter-a-list.
- **B. App-like dashboard (rejected).** Card grids, bottom tabs, icons everywhere. Generic, against the project's rules, and more JS.
- **C. Plain government service (rejected).** Very usable, but it could be mistaken for the Ministry. That's a trust problem for an independent guide, and it loses warmth.

## 7. Data issue noticed (not changed)
In the R&D natural-sciences majors, «الاحياء الدقيقة» (microbiology) is paired with "General biology" in `data/universities.json`; the إمداد list pairs it with "Microbiology". It's either a typo in the guide or an extraction slip. **Owner: check the guide (pages 7–13)**. Nothing was changed, because the data is generated from the PDF.

## 8. What changed and how it was verified
See [decision 035](../decisions.md) and the verification notes at the end of this file (filled in after implementation).
