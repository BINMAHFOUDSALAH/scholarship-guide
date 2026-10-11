# Custodian Scholarship: fact-check, 2026–2027 (research by Claude)

**Checked:** 2026-10-11, by Claude, reading the official pages directly (built-in browser). Nothing here is reviewed by the owner yet (`owner_reviewed: false` in the data).
**Scope:** برنامج خادم الحرمين الشريفين للابتعاث only. Aramco and KAUST are unchanged (see [paths-research.md](paths-research.md)).
**Not read:** the 2026–2027 universities guide PDF (opening it starts a file download; it is read in Stage 2 with the extraction script). So there is **no per-university table yet**, only the rule per track and per country.

Verdicts: ✅ verified · 🕓 outdated · ❌ contradicted · ⚠️ ambiguous / conflicting · ❔ not yet verified

---

## 1. What واضح showed before this step

| # | Claim on واضح | Where | Verdict | Official evidence | Correction |
|---|---|---|---|---|---|
| 1 | «خريجو الثانوية الحاصلون على قبول نهائي غير مشروط من جامعة ضمن قائمة المسار» | `paths.json` → homepage «لمن؟» | ⚠️ incomplete | Track conditions ([info-6](https://sites.moe.gov.sa/scholarship-program/conditions/info-6/), [info-5](https://sites.moe.gov.sa/scholarship-program/conditions/info-5/), [info-7](https://sites.moe.gov.sa/scholarship-program/conditions/info-7/)): unconditional offer required, **except** in non-English-speaking countries, where the offer may be conditional on studying the country's language. The program also targets university graduates ([home](https://sites.moe.gov.sa/scholarship-program/): «خريجو المرحلة الثانوية أو الجامعية…»). | Mention the language exception; say "من خريجي الثانوية" for our audience. |
| 2 | «تحتاج قبولًا نهائيًا غير مشروط… ويكون التقديم عبر منصة قبول» | homepage «باختصار» | ⚠️ exception missing + platform conflict | Same as #1. Platform: see #3. | Reworded; platform shown as a conflict fact. |
| 3 | Apply link = MoE e-service → منصة قبول (uap.sa) | «صفحة التقديم» link | ⚠️ conflicting official sources | [MoE e-service page](https://www.moe.gov.sa/ar/knowledgecenter/eservices/Pages/scholarshipprog.aspx): «ابدأ الخدمة» → uap.sa; steps say «منصة قبول». The program site's [submitting page](https://sites.moe.gov.sa/scholarship-program/submitting/) and [FAQ](https://sites.moe.gov.sa/scholarship-program/faqs/) still say «سفير». | Keep the e-service link (owner confirmed قبول on 2026-10-09); show the conflict, no single answer. |
| 4 | مسار الرواد = «أفضل 30 جامعة في العالم» | track note | ✅ with wording fix | [info-6](https://sites.moe.gov.sa/scholarship-program/conditions/info-6/): «أفضل 30 مؤسسة تعليمية **حسب قائمة البرنامج**». Bachelor's + master's, all majors, in person ([path page](https://sites.moe.gov.sa/scholarship-program/paths/path-arruaad/)). | «أفضل 30 مؤسسة حسب قائمة البرنامج». |
| 5 | مسار إمداد = «أفضل 200 جامعة، في تخصصات يحتاجها سوق العمل» | track note | ✅ | [info-5](https://sites.moe.gov.sa/scholarship-program/conditions/info-5/) + [FAQ](https://sites.moe.gov.sa/scholarship-program/faqs/): top 200 on the program's list, fields with high labor-market need, bachelor's + master's. | «حسب قائمة البرنامج» added. |
| 6 | الرواد «مفتوح الآن», إمداد «مغلق حتى إشعار آخر» | track status | ❔ | No status page on the official site. Owner's report from the program's X account; post links still missing. | Unchanged; keeps «غير مؤكد» until the X links are added. |
| 7 | Universities guide PDF 2026–2027 is current | link + news item | ✅ (owner, 2026-10-09) | The program home page itself says: «الموقع تحت التحديث. للاطلاع على ترتيب قوائم الجامعات حسب المجالات، يرجى تصفح الدليل الاسترشادي». | Keep; say the PDF is the reference while the site is updated. |
| 8 | «في بعض المسارات، مثل مسار الرواد، تحتاج قبولًا جامعيًا نهائيًا» | `grade-12.md` | ⚠️ incomplete | Same rule for الرواد, إمداد, البحث والتطوير, with the language exception. | Rewritten with the exception + link to the program page. |
| 9 | Only 2 tracks shown | homepage | ⚠️ incomplete | [FAQ](https://sites.moe.gov.sa/scholarship-program/faqs/): 4 tracks (الرواد، البحث والتطوير، إمداد، واعد). | All 4 on the program page; homepage shows the ones open to high school graduates. |
| 10 | Grade 11: «القدرات: بعض البرامج تشترط درجة معيّنة» | `grade-11.md` | ✅ (for some programs) | Custodian program: **no** Qudurat/Tahsili score required ([conditions page FAQ](https://sites.moe.gov.sa/scholarship-program/conditions/)). Some واعد programs do (e.g. طيران الرياض: Qudurat ≥ 80%, Tahsili ≥ 75%, [path-waaid](https://sites.moe.gov.sa/scholarship-program/paths/path-waaid/)). Aramco: ≥ 90% (2025–26 cycle, see paths-research). | No change now (grade pages are a later step). |

## 2. New facts found (shown on the program page)

| Fact | Source | Notes |
|---|---|---|
| 4 tracks: الرواد، البحث والتطوير، إمداد، واعد | [FAQ](https://sites.moe.gov.sa/scholarship-program/faqs/) | |
| البحث والتطوير = **doctorate only**, top 200 in priority fields | [info-7](https://sites.moe.gov.sa/scholarship-program/conditions/info-7/), [path page](https://sites.moe.gov.sa/scholarship-program/paths/path-albahthwaltatwir/) | Not for high school graduates. |
| واعد = programs linked to an employer; each program has its own conditions, institution, and a short application window | [path-waaid](https://sites.moe.gov.sa/scholarship-program/paths/path-waaid/) | 178 programs listed (2024–2026). Some accept high school graduates (e.g. MBC and طيران الرياض bachelor's programs, 2026). Windows are usually 1–2 weeks. On 2026-10-11 every listed program says «انتهت فترة التقديم». |
| General conditions: Saudi, good conduct, admission from an institution per the track's list, major in the year's approved list, study mode per track, full-time residence, pass المفاضلة ومنع التكدس | [info-1](https://sites.moe.gov.sa/scholarship-program/conditions/info-1/) | |
| You may submit several admissions; **one** application is accepted, by المفاضلة or available seats | [info-2](https://sites.moe.gov.sa/scholarship-program/conditions/info-2/) | The old "up to 3" claim is **not** on the official page. |
| No Qudurat/Tahsili score required; no general minimum %; no age limit | [conditions page FAQ](https://sites.moe.gov.sa/scholarship-program/conditions/) | ⚠️ but see the next row: specific cases have minimums. |
| **Extra conditions from 2025–2026:** preparatory year (undergraduate): HS GPA ≥ 90% and IELTS ≥ 5.5. China (undergraduate): age ≤ 30, HS GPA ≥ 85%, IELTS ≥ 4.5. Germany: German A2. | [info-4](https://sites.moe.gov.sa/scholarship-program/conditions/info-4/) | Not a contradiction of the FAQ: general rule vs. specific cases. Shown together. |
| An English-language year is **not** covered in English-speaking countries (e.g. USA, UK) | [conditions page FAQ](https://sites.moe.gov.sa/scholarship-program/conditions/) | |
| Documents: valid passport; previous qualification (+ equivalency if from abroad); official **unconditional** admission letter showing major, start date, university; transcript; national address | [submitting](https://sites.moe.gov.sa/scholarship-program/submitting/) | That page still describes Safeer (see #3). |
| Visa is applied for by the student; financial guarantee only after nomination | [FAQ](https://sites.moe.gov.sa/scholarship-program/faqs/) | |
| Bachelor's funded up to 5 years | [FAQ](https://sites.moe.gov.sa/scholarship-program/faqs/) | |
| Contact: تواصل (tawasul.moe.gov.sa), 19996 | [FAQ](https://sites.moe.gov.sa/scholarship-program/faqs/), [e-service](https://www.moe.gov.sa/ar/knowledgecenter/eservices/Pages/scholarshipprog.aspx) | |
| Official university search: Safeer «البحث عن جامعة» | [safeer2 portal](https://safeer2.moe.gov.sa/Portal/SearchUniversities/) | Public search by country/major/university; not tested in depth. |

## 3. Conditional admission (القبول المشروط)

### The rule (identical text on info-5, info-6, info-7 and the three path pages)
> «أن يكون القبول نهائياً غير مشروط وأن يكون صادراً من مكتب القبول والتسجيل في الجامعة المعتمدة في قائمة البرنامج، إلا إذا كانت الدولة غير ناطقة باللغة الإنجليزية فيمكن أن يكون القبول مشروطاً بدراسة لغة الدولة ويتاح الابتعاث لدراسة اللغة.»

Applies to: **الرواد, إمداد, البحث والتطوير**. Not to **واعد** (its programs are pre-arranged with an institution and have their own conditions; the exception text does not appear there).

### What the rule does and doesn't say
| Kind of offer | What the official text supports |
|---|---|
| Final, unconditional | ✅ Required (default). |
| Conditional on studying the **destination country's language**, in a **non-English-speaking country** | ✅ Allowed by the exception, and language study can be funded. |
| Conditional on grades / finishing high school | ❔ Not covered by the exception. Don't assume it's accepted. |
| Conditional on an English test (IELTS/TOEFL) | ❔ Not covered. The FAQ also says an English-language year isn't funded in English-speaking countries. |
| Through a preparatory / foundation year | ⚠️ info-4 sets conditions for "دراسة السنة التحضيرية" (GPA ≥ 90%, IELTS ≥ 5.5), so it exists in some form, but how a foundation-year offer fits the "unconditional" rule isn't stated. Ask officially. |
| Any other condition | ❔ Not covered. |

### Country level (official country pages, 2026-10-11)
Official language **not English** per the program's [country pages](https://sites.moe.gov.sa/scholarship-program/countries/): China, Japan, South Korea, France, Germany, Italy, Spain, Netherlands, Switzerland. English: USA, UK, Canada, Australia, Singapore, Malaysia, India.
- Extra conditions: China (age ≤ 30, GPA ≥ 85%, IELTS ≥ 4.5 for undergraduate) and Germany (German A2), from [info-4](https://sites.moe.gov.sa/scholarship-program/conditions/info-4/).
- ⚠️ **Undefined:** whether "دولة غير ناطقة باللغة الإنجليزية" means the country's language or the program's language of instruction (e.g. an English-taught program in the Netherlands). Canada's page lists English only. Students should ask officially.
- ⚠️ **Errors in the official country directory:** China lists "Imperial College London" and "National University of Singapore" under Beijing; France lists "University of Cambridge" under Orsay; Japan lists "University of California San Diego" under Tokyo. The site says it's "under update". Use the guide PDF for the track lists, not the country pages.

### Per-university matrix
**Deferred to Stage 2.** It needs the 2026–2027 guide PDF extracted into `data/universities.json`. Then each university in a non-English-speaking country on the الرواد/إمداد lists can be marked "potentially eligible under the published exception", never "guaranteed".

## 4. Official image of the program
- The only official visual found is the **program logo** in the home page carousel (`object.moe.gov.sa/nasaq/cm/files/scs*.png`, shown with the Vision 2030 and Human Capability Development Program logos). It contains the **Saudi state emblem** (palm and swords) in the center of a dotted ring.
- No emblem-free asset, photo, or press image of the program was found on the program site.
- Decision 020's concern still applies (state emblem use is restricted). **Owner decides** before anything is downloaded. Until then the program card uses a text-only name block (no generic photo).

## 5. Owner checklist for this file
- [ ] Spot-check the rule quote on info-6 / info-5.
- [ ] Decide on the logo (section 4).
- [ ] X post links for الرواد open / إمداد closed.
- [ ] If you can, ask تواصل: does a language-conditional offer in an English-taught program (e.g. Netherlands) count? Does a foundation-year offer count as unconditional?
