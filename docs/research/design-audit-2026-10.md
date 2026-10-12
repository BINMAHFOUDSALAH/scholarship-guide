# Design audit and improvement pass (2026-10-12)

**How:**
- Main session:
  - read the code
  - screenshots at 360/768/1280px, light and dark
  - measured page heights
  - computed contrast (`tests/test_design.py`)
  - browser flows (Playwright/Chromium) and axe-core
- Two read-only Haiku agents:
  - one collected search and filter guidance from NN/g and Baymard, read with `curl`
  - one independently reviewed the finder through real URLs and the source
- Every finding used below was **re-checked by me** before acting.
- **Not done:** no students, no Safari, no screen reader.
- **Decision:** [041](../decisions.md).

## 1. What works and was kept (and why)
- **Palette and tokens:** ivory `#F6F4EE`, charcoal, forest `#184B3A`, lime only for "open now" and "next step", amber for restrictions, plus a designed dark theme.
  - Every text pair is contrast-tested.
  - Colours carry fixed meanings (decision 035).
  - The palette is distinctive without being loud.
  - There was no evidence-based reason to change it, so it stays.
- **Typography:** Plex Sans Arabic at a 17px body, Naskh only for the wordmark and quotes, nothing under 13px. Kept.
- **The applied-filter chips with «مسح الكل»:** Baymard: "Display 'Applied Filters' in an Overview (28% Don't)", which gives users "immediate confirmation, a streamlined way to remove selections" ([Baymard](https://baymard.com/blog/how-to-design-applied-filters)). Kept.
- **The default order is the official rank:** NN/g: "prioritization by importance or frequency are usually better than A-Z listings" ([NN/g](https://www.nngroup.com/articles/alphabetical-sorting-must-mostly-die/)). No sort control added.
- **Choosing a university in the suggestions opens its page,** so the other filters don't apply to that choice. Kept.
- **Saving without an account:** Baymard: "Make It Easy to Access and Use 'Save' Features (89% Don't)" ([Baymard](https://baymard.com/blog/current-state-ecommerce-product-page-ux)). Kept (decision 039).

## 2. Problems found, ranked by impact on students
| # | Problem (verified) | Why it matters | Fixed? |
|---|---|---|---|
| 1 | **Filtering by Germany said "0 universities"**: no track meant الرواد only, which has no German university; 17 are in إمداد | A false "none": the worst kind of error for a trust product | ✅ Every list with matches is shown |
| 2 | **A name search excluded by filters said "no university by this name"**, e.g. Stanford with بريطانيا set | Tells students Stanford isn't on the lists | ✅ Shown, with «خارج الفلاتر التي اخترتها» and a link to drop the filters |
| 3 | **A country typed in the search box** (ألمانيا, Germany, UK) said "no university by this name" | A dead end. NN/g: no-results pages should offer "Suggestions for similar queries that do return results" ([NN/g](https://www.nngroup.com/articles/search-no-results-serp/)) | ✅ «هل تقصد الدولة «ألمانيا»؟» links to the country filter (`aliases` in `countries.json`) |
| 4 | **A major search showed the whole field as if it were that major's list** («علوم الحاسب» → 69 universities in ICT) | Overstates what the lists say | ✅ Note: «هذا ترتيب مجال … كله، وليس قائمة بتخصص … وحده» |
| 5 | **«متاحة لتخصصك» / «فيمكنك دراسة أي تخصص»** read as "you can get in" | Contradicts «وجود الجامعة في القائمة لا يعني قبولك فيها» | ✅ «قائمة الرواد لا تحدد تخصصات… والقبول تقرره الجامعة» |
| 6 | **A major search was 21,927px on a phone**: 30 الرواد rows (the same for every major) before the field list | The specific answer was buried | ✅ الرواد as a compact ranked list, with a link to the full table: 13,901px |
| 7 | **«المتطلبات والمواعيد: لم نجمعها بعد» repeated on all 69 إمداد rows** | Noise that hides the rows | ✅ Said once per list |
| 8 | **Confusing labels:** «كل الدول» in the language filter, «لغة أخرى», «باختصار», «لا حد أدنى منشور», «الجامعات المعتمدة» (sounds like accreditation) | Students decode labels instead of deciding | ✅ «كل اللغات», «غير الإنجليزية», «المتطلبات والمواعيد», «الجامعة لا تنشر حدًا أدنى», «الجامعات في قوائم الابتعاث» |
| 9 | **Conflicting filters** (بريطانيا + غير الإنجليزية) showed a bare "0" | The student can't tell which filter to drop | ✅ Names the conflict and links to the fix |
| 10 | **Typed suggestions had no limit on majors** | Baymard: users ignore lists over ~10 and "a target of 4–8 will work for most mobile users" ([Baymard](https://baymard.com/blog/autocomplete-design)) | ✅ At most 8 majors when typing (an empty box still browses by field) |
| 11 | **On phones, the search box sat ~630px down** behind intro text and the source line | The main task should come first ([NN/g inverted pyramid](https://www.nngroup.com/articles/inverted-pyramid/)) | ✅ A one-line intro; the source moved below the results |
| 12 | **The save button sat inside the row-header cell**; the rank had no label on phones | Screen-reader row names included «احفظ»; a bare number | ✅ The button moved to the last cell; the rank says «المرتبة» to screen readers |
| 13 | **The header «قائمتي» showed an empty badge** on phones | Looked broken | ✅ Hidden when empty |

## 3. Left unchanged on purpose
- **A "show 10, then all" collapse for long lists:** a collapsed state breaks "back to results" scroll restoration (tested earlier). Compact rows and one note per list cut most of the height instead.
- **A sort control:** the official rank is the meaningful order (above).
- **Comparison tables:** NN/g says they suit "a small number of offerings" (usually under 5–7) ([NN/g](https://www.nngroup.com/articles/comparison-tables/)), which fits «قائمتي» later, not the 200-row lists. Its rows already show the same key facts per university. Worth testing with students first.
- **Duplicate field values without JavaScript** (`engineering` under إمداد and البحث والتطوير): low impact, since JavaScript filters them. Logged.
- **The homepage program rows** (~1,000px each on a phone): a real cost, but each holds the decision-critical «لمن؟». Revisit after the usability test.
- **The default theme ignores the phone's dark mode** (light first, by decision 023). Kept.

## 4. The hub vision: how the parts connect
1. **Homepage:** two ways in (grade or search).
2. **Grade page:** what matters, one activity, a tool. It sends students to:
   - the finder (grade 11)
   - «قائمتي» (grade 12)
   - the program page
3. **The finder:** finds and saves universities. Each university page holds its requirements and the scholarship and university dates.
4. **«قائمتي»:** the student's own short list, which they come back to.

**Why students return:** their list, and dates that change (open now, the next deadlines).

**Next, to validate with students:**
- copy my list as a link
- compare saved universities
- a stale-facts check, so the dates students return for stay true

## 5. Not verified
- Safari/iOS and Firefox.
- A screen reader on a real phone.
- Real students.
