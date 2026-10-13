# Aramco CDPNE + CPP: fact-check for students in grade 12 in 2026–2027 (research by Claude)

**Checked:** 2026-10-11, by Claude, with WebFetch on aramco.com (EN + AR pages and the official PDF). Nothing here is reviewed by the owner yet.
**Scope:** برنامج الابتعاث الجامعي لخريجي الثانوية (College Degree Program for Non-Employees, **CDPNE**) and برنامج الإعداد الجامعي (College Preparatory Program, **CPP**). Short notes on the other Aramco student programs listed in the same official section.
**Not accessed:**
- Aramco's X accounts (not readable with my tools), so **no official post** was found for the last registration window or for the next cycle.
- The sample screening-test PDF (44 pages): its text could not be extracted without installing a PDF tool (not installed, per the rules).
- The 2025 eligibility PDF (`2025_eligibility_criteria.pdf`): now **404**, so no comparison with the older cycle.
- The application portal (jobs.aramco.com, needs login): not tried.
- HTTP redirects on aramco.com (curl timed out), so I can't say which of the two CDPNE URLs is canonical (see C3).
- WebFetch returns a model's reading of the page. I asked for verbatim quotes, but the owner should spot-check the key numbers.
- Side effect: WebFetch cached two PDFs in Claude's own session folder (outside the repo). Nothing was saved in the repo except this file.

Verdicts: ✅ verified (on the official page today) · 🕓 outdated (official, but for the 2025–2026 cycle) · ⚠️ ambiguous / conflicting · ❔ not found

---

**Re-checked 2026-10-12** (Haiku agent, WebFetch; `curl` to aramco.com timed out from the laptop too): **no change**. The page still shows 1447–1448 H (2025–2026), «باب التسجيل مغلق في الوقت الحالي، وسوف يتم الإعلان لاحقًا عن الفترة المخصصة للتسجيل», the same numbers and dates; the 2027 PDF is still 404. New small details: the AR requirements write the years «2026/2025م» (the AR FAQ: «2025-2026م»); the AR "registration guide" section shows «قد تم حظر هذا المحتوى»; only the AR page says «التواريخ المعلنة أعلاه قابلة للتغيير».

## 0. The key point: which cycle is online?

The official page (EN + AR) still shows the **1447–1448 H (2025–2026 G)** cycle: applicants were in grade 12 in 2025–2026, tested in May 2026, and started on 2 August 2026. Registration status today: «Registration is currently closed», with the period «announced later» ([EN](https://www.aramco.com/en/careers/saudi-applicants/non-employee-programs/high-school-and-diploma-graduates/cdpne); [AR](https://www.aramco.com/ar/careers/saudi-applicants/non-employee-programs/high-school-and-diploma-graduates/cdpne): «باب التسجيل مغلق في الوقت الحالي، وسوف يتم الإعلان لاحقًا»).

**Nothing official is published yet for the 1448–1449 H (2026–2027) cycle**, the one that matters for students in grade 12 today. The analogous PDF URL for 2027 returns 404. So every number below is from the **previous cycle** and must be shown as «في الدورة السابقة 2025–2026، وقد تتغير».

---

## 1. Check of the earlier draft ([paths-research.md](paths-research.md) §2)

| # | Draft claim | Verdict | Official evidence | Correction |
|---|---|---|---|---|
| 1 | Official page URL `aramco.com/en/careers/saudi-applicants/non-employee-programs/high-school-and-diploma-graduates/cdpne` | ✅ | Loads, CDPNE content. | A second URL shows the same content (see C3). |
| 2 | Cycle on page: 1447–1448 H (2025–2026) | ✅ 🕓 | EN + AR pages. | Still the old cycle on 2026-10-11. |
| 3 | Second semester of grade 12, General / CS & Engineering / Health & Life Science | ✅ 🕓 | EN page. FAQ adds: Business Administration and Sharia paths **not eligible**. | Add the excluded paths. |
| 4 | GPA ≥ 85% "for the whole of high school" | ✅ 🕓, wording fix | Page: 85% for grades **10, 11 and the first semester of grade 12**. | Name the grades. |
| 5 | Math & science GPA ≥ 85% | ✅ 🕓 | Math, physics, chemistry, biology, same grades. | List the 4 subjects. |
| 6 | Qudurat or GAT ≥ 90% | ✅ 🕓, ⚠️ detail | EN «Qudurat or GAT»; AR «اختبار القدرات العامة». Below 90 you may still register and raise it by **23 Apr 2026**. The international PDF says **only the Scientific** Qudurat counts; the regular page doesn't say (C1). | Add the "register first, update later" rule. |
| 7 | Age ≤ 22 (Hijri) | ✅ 🕓 | «must not exceed the age of 22 years according to the Hijri calendar». | — |
| 8 | Valid ID or passport for the test | ✅ 🕓 | EN + AR. | — |
| 9 | International systems: Scientific Qudurat/GAT ≥ 90 **or** SAT Math ≥ 630 **or** ACT Math ≥ 27, + GPA rules + equivalency | ✅ 🕓, incomplete | [2026 PDF](https://www.aramco.com/-/media/downloads/careers/2026_cdpne_eligibility_criteria_public-website.pdf). Missing from the draft: GPAs for international systems cover **grades 9, 10, 11 + first term of 12**; applications are **case by case**; recent graduates of those systems may apply. | Add these 3 points. |
| 10 | Steps: online form → English + math test → medical → career fair → agreement → orientation | ✅ 🕓 | EN page "How to apply". Also: submit official transcripts + passport photo copy before CPP; get an Aramco ID card at signing. | — |
| 11 | CPP: a full academic year in Dhahran (IELTS prep, university applications) | ✅, incomplete | Also SAT support and an intensive academic program; **SR 4,000/month** stipend, housing, bus, medical care. | Add stipend + SAT. |
| 12 | Major "assigned by Aramco" | ✅ | «a discipline required by the company», «assigned field of study». | — |
| 13 | CPP exemption: unconditional offer, QS top 30, required field, case by case | ✅ 🕓, incomplete | Also: QS **by subject**; entry level = US Freshman Year / UK Foundation Year / equivalent; must already be accepted into CDPNE (eligibility + test); documents before **1 Jun 2026**. | Add the details. |
| 14 | Registration "currently closed", "will be announced later" | ✅ | Same wording today. | — |
| 15 | Dates: test 1–2 May, fair 3–4 Jun, orientation 2 Aug, Qiyas update 23 Apr 2026 | ✅ 🕓 | Same on the page. Missing: CPP waiver documents before 1 Jun 2026; the program start-up is also 2 Aug. AR page: «التواريخ المعلنة أعلاه قابلة للتغيير». | Mark all as the 2025–2026 cycle. |
| 16 | Cross-path note: Qudurat required (≥ 90%) for Aramco | ✅ 🕓 | As above. | Keep "in the last cycle". |

No draft claim is contradicted. The draft is **incomplete** (rows 3, 9, 11, 13, 15), and every number is from the old cycle.

---

## 2. Facts for the path page

All from the [EN CDPNE page](https://www.aramco.com/en/careers/saudi-applicants/non-employee-programs/high-school-and-diploma-graduates/cdpne) / [AR page](https://www.aramco.com/ar/careers/saudi-applicants/non-employee-programs/high-school-and-diploma-graduates/cdpne) unless another source is named. Cycle: 1447–1448 H / 2025–2026 G.

### 2.1 What CDPNE is

| Fact | Verdict | Suggested Arabic for students |
|---|---|---|
| A «highly-selective scholarship program» for Saudi male and female high school graduates; one of Aramco's «primary sources for entry-level Saudi professionals». | ✅ | «برنامج ابتعاث تنافسي جدًا من أرامكو السعودية لخريجي وخريجات الثانوية السعوديين.» |
| Bachelor's degree, in a discipline **required by the company**; the student studies in the «assigned field of study». AR: «حسب احتياجات الشركة». | ✅ | «تدرس البكالوريوس في تخصص تحدده أرامكو حسب احتياجها، لا تختاره بحرية.» |
| Study at an **out-of-Kingdom** university (AR: «أفضل الجامعات العالمية»). No countries or universities are named. | ✅ | «الدراسة في جامعة خارج المملكة. الصفحة الرسمية لا تحدد دولًا بعينها.» |
| Aramco counselors in many study countries support students. | ✅ | «يتابعك مرشدون من أرامكو في بلد الدراسة.» |
| After graduation: EN «targeted for employment at the professional level with Aramco»; AR «يتم توظيف الخريجين والخريجات في وظائف مهنية». | ⚠️ (EN softer than AR) | «بعد التخرج تستهدف أرامكو توظيفك في وظيفة مهنية لديها.» |
| A training agreement is signed; its terms (e.g. years of service) are **not** published. | ❔ | Don't mention a service period. |
| How the major is assigned in practice: the AR page calls the 3–4 June event «الندوة التعريفية الخاصة بالتخصصات المطروحة للمرشحين». How the final choice is made is not stated. | ❔ | «تتعرّف على التخصصات المطروحة في لقاء تعريفي بعد الترشيح.» |
| University-phase benefits: tuition, location-based stipend, computer + book allowances, settling-in allowance, achievement award, yearly return ticket, medical cover, counseling. Aramco «reserves the right to change» entitlements. | ✅ 🕓 | «تغطي أرامكو الرسوم ومكافأة شهرية ومزايا أخرى، وقد تتغير.» |

### 2.2 Eligibility: Saudi (regular) system

| Fact | Verdict | Suggested Arabic |
|---|---|---|
| Currently in the **second semester of grade 12**, current academic year only (FAQ: last year's graduates are not eligible). | ✅ 🕓 | «تتقدم وأنت في الفصل الثاني من الصف الثالث الثانوي. خريجو السنوات السابقة لا يحق لهم التقديم.» |
| Paths: General, Computer Science & Engineering, Health & Life Science. **Not** Business Administration or Sharia. | ✅ 🕓 | «المسارات المقبولة: العام، وعلوم الحاسب والهندسة، والصحة والحياة. مسار إدارة الأعمال والمسار الشرعي غير مقبولين.» |
| Cumulative GPA ≥ **85%** for grades 10, 11 and first semester of 12. | ✅ 🕓 | «معدل تراكمي 85% أو أكثر (أول وثاني ثانوي والفصل الأول من ثالث) في الدورة السابقة.» |
| Math & science GPA ≥ **85%** (math, physics, chemistry, biology), same grades. | ✅ 🕓 | «و85% أو أكثر في الرياضيات والفيزياء والكيمياء والأحياء.» |
| Qudurat / GAT ≥ **90%**. Below 90: you may still register; you get a regret message until you update the score by **23 Apr 2026** (by phone). | ✅ 🕓 | «القدرات 90% أو أكثر. يمكنك التسجيل بدرجة أقل ثم تحديثها قبل الموعد الذي تحدده أرامكو.» |
| Age ≤ **22 Hijri years**. | ✅ 🕓 | «ألا يزيد عمرك على 22 سنة هجرية.» |
| Valid national ID or passport, brought to the test. | ✅ 🕓 | «هوية وطنية أو جواز سفر ساري يوم الاختبار.» |
| Applicant must register and upload documents **personally**; not from Aramco computers; no late applications. | ✅ | «سجّل بنفسك، ولا تُقبل الطلبات بعد إغلاق التسجيل.» |
| Tahsili, IELTS, SAT are **not** listed as entry requirements for the regular system. | ✅ (absence) | Don't add them as requirements. |

### 2.3 Eligibility: international high-school systems

Source: [2026 Eligibility Criteria PDF](https://www.aramco.com/-/media/downloads/careers/2026_cdpne_eligibility_criteria_public-website.pdf) («2026 applicants», PDF metadata: created 21 Oct 2025) + EN page.

| Fact | Verdict | Suggested Arabic |
|---|---|---|
| For Saudi applicants from in- or out-of-Kingdom schools using international systems; considered «case-by-case». Science-track students, currently enrolled **or recent graduates** in the current year. | ✅ 🕓 | «لطلاب المناهج الدولية داخل المملكة وخارجها، وتُدرس كل حالة على حدة.» |
| One of: **Scientific** Qudurat/GAT ≥ 90 (only the Scientific version counts) **or** SAT Math ≥ 630 **or** ACT Math ≥ 27. | ✅ 🕓 | «القدرات (علمي) 90 أو أكثر، أو رياضيات SAT ‏630 أو أكثر، أو رياضيات ACT ‏27 أو أكثر.» |
| Cumulative GPA ≥ 85.00% and math & science GPA ≥ 85.00%, computed for **grades 9, 10, 11 + first term of 12**. | ✅ 🕓 | «معدل 85% وأكثر، ويُحسب من الصف التاسع حتى الفصل الأول من الثاني عشر.» |
| Diploma authenticated, showing **equivalency** to the Saudi high school certificate. | ✅ 🕓 | «تحتاج معادلة شهادتك بالشهادة الثانوية السعودية.» |

### 2.4 Steps (2025–2026 cycle)

| Step | Verdict | Suggested Arabic |
|---|---|---|
| 1. Online application form (only during the announced window). | ✅ | «١. التسجيل الإلكتروني في الفترة التي تعلنها أرامكو.» |
| 2. English + math screening test, **1–2 May**. Locations: Riyadh, Dhahran, Jeddah, Mubarraz, Ras Tanura, Abha, Medina. Appointments can't be changed. A sample-test PDF is linked ([PDF](https://www.aramco.com/-/media/downloads/careers/cdpne-screening-test-preparation---02-20--2025.pdf), not read). | ✅ 🕓 | «٢. اختبار إنجليزي ورياضيات (كان في 1–2 مايو 2026). توجد نماذج تدريبية على موقع أرامكو.» |
| 3. If nominated: pre-employment medical exam (invite by email). | ✅ | «٣. فحص طبي لمن يُرشَّح.» |
| 4. CDPNE Career Fair, **3–4 June** (AR: الندوة التعريفية بالتخصصات المطروحة). | ✅ 🕓 | «٤. لقاء تعريفي بالتخصصات المطروحة.» |
| 5. Sign the training agreement; Aramco ID card issued. | ✅ | «٥. توقيع اتفاقية التدريب.» |
| 6. Orientation + program start-up, **2 August**. Before CPP: official transcripts + passport photo copy. | ✅ 🕓 | «٦. اللقاء التعريفي وبدء البرنامج (كان في 2 أغسطس 2026).» |
| 7. CPP: one full academic year in **Dhahran** (see 2.5), then the bachelor's abroad. | ✅ | «٧. سنة إعداد جامعي في الظهران، ثم الابتعاث.» |

### 2.5 CPP (برنامج الإعداد الجامعي)

| Fact | Verdict | Suggested Arabic |
|---|---|---|
| A full academic year in Dhahran **before** the scholarship starts. | ✅ | «سنة دراسية كاملة في الظهران قبل السفر.» |
| Includes IELTS preparation, SAT support, help with university applications and registration, and an intensive academic program by the College Preparatory Center (CPC). | ✅ | «تستعد فيها لاختبار IELTS وSAT، وتساعدك أرامكو في التقديم على الجامعات.» |
| During CPP: **SR 4,000/month**, housing per Aramco policy, free Aramco bus, medical care, access to recreation facilities. | ✅ 🕓 | «مكافأة شهرية 4,000 ريال في الدورة السابقة، مع سكن ومواصلات وعلاج حسب سياسة الشركة.» |

### 2.6 CPP exemption (الإعفاء من برنامج الإعداد الجامعي)

| Fact | Verdict | Suggested Arabic |
|---|---|---|
| Considered for high-caliber graduates of in-Kingdom and high-quality international schools. | ✅ | «قد تُعفى من سنة الإعداد في حالات محدودة.» |
| Conditions: (a) accepted into CDPNE (eligibility + English & math test); (b) **unconditional** offer from a **QS top 30 by subject** university, in a major the company requires that year; (c) entry level = US Freshman Year, UK Foundation Year, or equivalent. | ✅ 🕓 | «بشرط قبولك في البرنامج أولًا، وقبول غير مشروط من جامعة ضمن أفضل 30 في التخصص حسب تصنيف QS، وفي تخصص تحتاجه أرامكو.» |
| Reviewed case by case; documents before **1 June 2026**. | ✅ 🕓 | «يُدرس كل طلب على حدة، وللدورة موعد نهائي للمستندات.» |

### 2.7 Dates and registration status

| Fact | Verdict | Suggested Arabic |
|---|---|---|
| Registration closed; window «announced later». | ✅ (today) | «التسجيل مغلق حاليًا، وستعلن أرامكو موعده لاحقًا.» |
| 2025–2026 cycle dates: Qiyas update by 23 Apr 2026; test 1–2 May; CPP waiver documents before 1 Jun 2026; fair 3–4 Jun; orientation + start 2 Aug. AR adds «قابلة للتغيير». | 🕓 | «في الدورة السابقة كان الاختبار في مايو وبدء البرنامج في أغسطس. مواعيد الدورة القادمة لم تُعلن.» |
| 2026–2027 cycle (1448–1449 H): criteria, dates, window. | ❔ not published | «لم تُعلن شروط ومواعيد دورة 2026–2027 حتى الآن.» |
| **Hint only, not a source:** a job-news site (ewdifh.com/jobs/84513) says the 2026 window ran **2–9 March 2026** (one week). No official post found. | ❔ | Don't publish a date. Possible wording: «فترة التسجيل قد تكون قصيرة، فتابع حسابات أرامكو الرسمية.» (after the owner confirms). |

### 2.8 Contact

| Channel | Source | Verdict |
|---|---|---|
| 800 302 4444 (KSA, toll free) · +966 13 877 2828 (outside KSA) | CDPNE page (score updates, weekdays 7:00–16:00) + [student programs page](https://www.aramco.com/en/careers/saudi-applicants/non-employee-programs/high-school-and-diploma-graduates) | ✅ |
| G-SAED@aramco.com | [Student programs page](https://www.aramco.com/en/careers/saudi-applicants/non-employee-programs/high-school-and-diploma-graduates) "Contact us" (purpose not stated) | ✅ |
| Candidate profile: https://jobs.aramco.com/myprofile/ | CDPNE page | ✅ (not opened) |
| Official X: https://x.com/aramco | Site footer | ✅ link, posts not read |

---

## 3. Other Aramco student programs (same official section)

From the [student programs page](https://www.aramco.com/en/careers/saudi-applicants/non-employee-programs/high-school-and-diploma-graduates) ([AR](https://www.aramco.com/ar/careers/saudi-applicants/non-employee-programs/high-school-and-diploma-graduates)). Each has its own criteria; shown here only as names + one line.

| Program (AR / EN) | One line (from the official page) | Link | Notes |
|---|---|---|---|
| **برنامجي التدريب الصيفي وطموح** / Summer Training Program & **Tomooh** | Summer: 3 weeks of English, life skills, safety, for grades 10–12. Tomooh: for **grades 10–11** with a valid IELTS/TOEFL/STEP certificate; SAT, AP, IELTS classes, aimed at «best-in-class and Ivy League universities». Online (Blackboard). | [page](https://www.aramco.com/en/careers/for-saudi-applicants/student-opportunities/high-school-students) | 🕓 2026 edition: registration closed 15 Feb 2026, programs July–Aug 2026. **Very relevant for the grade 10–11 pages.** |
| **برنامج التدرج للمرحلة الثانوية** / Apprenticeship Program (APNE) | Training for Saudi high school graduates (science and arts streams) for entry-level jobs; listed criteria: average ≥ 75, GAT ≥ 72, age ≤ 24 Hijri. | [page](https://www.aramco.com/en/careers/for-saudi-applicants/student-opportunities/apprenticeship-program) | 🕓 graduation years listed end at 1446 H (old cycle). Registration closed. |
| **برنامج التدرج للخريجين من الكليات** / Vocational College Graduates (VCGNE) | Training for technical/industrial/community college diploma graduates. | [page](https://www.aramco.com/en/careers/for-saudi-applicants/student-opportunities/vocational-colleges-graduates) | 🕓 2025 cycle. Not for high school graduates. |
| **برنامج المتابعة الجامعية** / College Continuation Program | For Saudi students «currently pursuing a bachelor's degree». | [page](https://www.aramco.com/en/careers/for-saudi-applicants/student-opportunities/college-continuation-program) | University students, not high school. |
| University & vocational college internships | Internships for current college students. | [page](https://www.aramco.com/en/careers/for-saudi-applicants/student-opportunities/university-and-vocational-college-internship-programs) | Not for high school. |

---

## 4. Conflicts and ambiguities

- **C1. Scientific Qudurat only?** The international PDF says only the **Scientific** Qudurat/GAT counts. The regular-system page says just «Qudurat or GAT» (AR «اختبار القدرات العامة»). Unclear whether regular applicants also need the scientific version. Don't state it for regular applicants.
- **C2. GPA years differ by system:** regular = grades 10, 11, first semester of 12; international = grades 9–11 + first term of 12. Not a conflict (different systems), but show them separately.
- **C3. Two official URLs with the same content:** `/en/careers/saudi-applicants/non-employee-programs/high-school-and-diploma-graduates/cdpne` and `/en/careers/for-saudi-applicants/student-opportunities/college-degree-program` (the student programs index links to the second one). Both show the same cycle and dates today.
- **C4. EN vs AR wording:** "Career Fair" vs «الندوة التعريفية الخاصة بالتخصصات المطروحة»; employment "targeted" (EN) vs «يتم توظيف» (AR); only the AR page says dates are subject to change. Use the more cautious wording.
- **C5. SAT/ACT in the regular FAQ:** the FAQ (EN + AR) mentions updating SAT/ACT math scores, while the regular requirements list only Qudurat. Fits the international criteria; no conflict for regular students.
- **C6. Phone format:** +966138772828 vs 00966138772828: same number.

---

## 5. What this means for the grade 10–12 pages (suggestion, owner decides)

- Grades 10–11 count for the GPA (regular system), so «حافظ على معدلك من أول ثانوي» is supported by the official criteria.
- Qudurat was the hard filter in the last cycle (≥ 90%), and it can be raised until a deadline in the spring of grade 12.
- Tomooh (grades 10–11) is the official Aramco route for SAT/IELTS preparation before grade 12.
- Business Administration and Sharia paths close the CDPNE door, which matters when choosing a path in grade 10. Show this with the cycle label.

---

## 6. Owner checklist

- [ ] Spot-check on the EN + AR CDPNE pages: 85% / 85% / 90% / 22 Hijri, the excluded paths, and the 2025–2026 dates.
- [ ] Spot-check the international PDF: Scientific Qudurat ≥ 90 / SAT Math ≥ 630 / ACT Math ≥ 27, GPA over grades 9–12.
- [ ] Find the official Aramco post (X or aramco.com news) for the March 2026 window, to confirm whether it really lasted one week.
- [ ] Decide which CDPNE URL واضح links to (C3).
- [ ] Decide whether the page says «تحدد أرامكو التخصص» and «تستهدف أرامكو توظيفك» (cautious wording, C4).
- [ ] Optional, via 800 302 4444 or G-SAED@aramco.com: do regular-system applicants need the **Scientific** Qudurat (C1)? Are the training agreement terms (service years) public?
- [ ] Re-check the page in **Jan–Feb 2027** for the 1448–1449 H criteria, and update every 🕓 row.
- [ ] Decide whether Tomooh / Summer Training get a mention on the grade 10–11 pages (separate fact-check needed).
