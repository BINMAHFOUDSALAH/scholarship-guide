# Grade pages and "which tests do I need": sources, audit, open questions

**Date:** 2026-10-12 · **By:** Claude (main session, no subagents) · **Owner review:** not yet
**Decision record:** [decision 038](../decisions.md).

## 1. How this was read (and its limits)
- **Method:** pages read directly with `curl` (HTML → text) and PDFs with `pdftotext`, after the owner opened network access on 2026-10-12. Quotes are copied from the text. Ligature artifacts from PDF extraction, such as «األوىل» for «الأولى», are fixed in the quotes below.
- **Couldn't read:**
  - **ETEC (etec.gov.sa):** the site is a JavaScript app, and its content API returns a Cloudflare block (403) to this environment. So nothing on the site says what Qudurat or Tahsili contain; it only links to etec.gov.sa.
  - **aramco.com:** times out (HTTP/2 error), as it did on 2026-10-11. Aramco facts come from the 2026-10-11 reading in [aramco-cdpne-2026-27.md](aramco-cdpne-2026-27.md), which covers the **previous cycle (2025–2026)**. Shown that way.
  - **British Council LearnEnglish (Teens):** times out. Not used.

## 2. Sources and what each one supports
| # | Source (read 2026-10-12 unless noted) | Exact words | Used for |
|---|---|---|---|
| S1 | [Ministry: المسارات الثانوية](https://www.moe.gov.sa/ar/education/generaleducation/StudyPlans/Pages/SecondarySchoolTracks.aspx) | «ويشتمل نظام المسارات على خمسة مسارات رئيسة هي: المسار العام، مسار علوم الحاسب والهندسة، مسار الصحة والحياة، مسار إدارة الأعمال، المسار الشرعي» · «تبدأ بالسنة الأولى المشتركة التي يدرس فيها الطالب مجالات علمية وإنسانية متنوّعة، تليها سنتان تخصصيتان» · «نظام مرن يتيح للطالب فرصة التحويل بين المسارات وفق آلية محددة» | Grade 10: the five tracks, the common first year, switching |
| S2 | [Ministry: الثانوية العامة، وثيقة تعريفية 2025 (PDF)](https://www.moe.gov.sa/ar/education/generaleducation/StudyPlans/Documents/Pathways_documents_2025.pdf), p. 9 | «السنة الأولى (الصف الأول الثانوي): سنة تمهيدية… ويُهيأ للالتحاق بالمسارات التخصصية عبر عمليات التسكين التي تحدد مسار الطالب الذي يتناسب مع ميوله واتجاهاته وقدراته» | Grade 10: this year leads to the track placement |
| S3 | [Ministry: دليل التوجيه المهني 1444 (PDF)](https://www.moe.gov.sa/ar/aboutus/aboutministry/RPRLibrary/دليل%20التوجيه%20المهني%20١٤٤٤.pdf), printed pp. 31–32 | Role of the counsellor: «اكتشاف قدرات وميول الطلاب، وتنميتها، وتوجيههم للتخصصات المناسبة لهم» · Activity: «يكتب عدد من المهارات التي يمتلكها، ونقاط القوة لديه في ورقة ويكتب في ورقة أخرى ميوله» · «وضع قائمة بالمسارات، وقائمة أخرى بالتخصصات الجامعية المرتبطة بهذه المسارات ومتطلبات الالتحاق بهذه التخصصات» | Grade 10: talk to the الموجه الطالبي; two activities adapted for students |
| S4 | [Ministry: القبول الموحد في الجامعات والجهات التعليمية](https://www.moe.gov.sa/ar/knowledgecenter/eservices/pages/unified-admission.aspx) | «توحيد وتسهيل إجراءات القبول للطلاب والطالبات في الجامعات الحكومية والكليات التقنية السعودية» · «اجتياز أي اختبارات أو مقابلات شخصية تطلبها الجامعة (مثل اختبار القدرات والاختبار التحصيلي)» · «تطبق معايير تنافسية بناءً على النسب الموزونة أو المركبة» · «بعد إعلان نتائج الفرز، يجب على الطالب الدخول لتأكيد القبول… (عدم التأكيد يسقط حق الطالب في الترشيح)» · «قد تشترط بعض الكليات (مثل الطب والتمريض) أن يكون المتقدم من خريجي الثانوية العامة لنفس العام» | Grades 11–12: Saudi universities; which tests; the confirmation step |
| S5 | [المنصة الوطنية للقبول الموحد](https://www.uap.sa/) | Page title «المنصة الوطنية للقبول الموحد»; linked from S4 | Grade 12: where to apply |
| S6 | [Scholarship program: الشروط](https://sites.moe.gov.sa/scholarship-program/conditions/) | «التقديم متاح دون اشتراط درجة اختبار قدرات وتحصيلي» · «يجوز للمتقدم تقديم ثلاث قبولات كحد أقصى، ويتم اختيار طلب واحد وفق نتائج المفاضلة…» · «أن يكون لدى المتقدم قبول من إحدى المؤسسات التعليمية المحددة» · Prep year: «ألا يقل المعدل التراكمي العام في الثانوية العامة عن 90%… ألا تقل درجة اختبار اللغة (آيلتس) عن 5.5» | Grades 11–12: scholarship tests; admission first; up to three admissions |
| S7 | [KGSP: Prospective students](https://kgsp.kaust.edu.sa/prospective-students) | «You must be a Saudi national who is a current Grade 12 student.» · Cohort 18: «will open Monday, January 12, 2026, and the form will close on Wednesday, February 11, 2026» · «SAT 1350 (with a minimum of 700 SAT Math)» · «TOEFL IBT 90 (or 7.0 for IELTS Academic or 650 for SAT English)» · «Applications for Cohort 19 will open soon» | Grades 11–12: KGSP tests; last cycle's dates labelled as past |
| S8 | Aramco CDPNE, [Arabic page](https://www.aramco.com/ar/careers/saudi-applicants/non-employee-programs/high-school-and-diploma-graduates/cdpne) **read 2026-10-11**, previous cycle | «المسارات المقبولة: العام، وعلوم الحاسب والهندسة، والصحة والحياة. مسار إدارة الأعمال والمسار الشرعي غير مقبولين.» · «معدل تراكمي 85% أو أكثر (أول وثاني ثانوي والفصل الأول من ثالث)» · «القدرات 90% أو أكثر» | Grade 10: track choice and GPA matter; grade 11: Qudurat |
| S9 | [Aramco: high-school students](https://www.aramco.com/en/careers/for-saudi-applicants/student-opportunities/high-school-students), **read 2026-10-11** | Tomooh: for grades 10–11 with a valid IELTS/TOEFL/STEP certificate; 2026 registration closed 15 Feb 2026 | Grade 11: one resource, dated |
| S10 | [College Board: SAT practice and preparation](https://satsuite.collegeboard.org/sat/practice-preparation) | «find your free practice resources here» · «Download Bluebook to take official digital practice tests» | Grade 11: SAT prep |
| S11 | [IELTS: preparation resources](https://ielts.org/take-a-test/preparation-resources) | «Official sample tests: Get ready for your test by reviewing sample questions and answers.» | Grade 11: IELTS prep |
| S12 | [BBC Learning English](https://www.bbc.co.uk/learningenglish) | «Start here: Choose your level» · «Test Your Level» · «6 Minute English» | Grade 10: English routine |
| S13 | `data/university_details/*.json` (30 الرواد universities, each from its own site, 2026-10-11) | SAT/ACT policy, IELTS minimum, platform, dates | Grade 11–12 test table (computed, not retyped) |

## 3. Audit of the old grade-page claims (before → now)
| Page | Old claim | Verdict | Now |
|---|---|---|---|
| 10 | «بعض البرامج تنظر إلى معدلك في كل سنوات الثانوية» | Vague but true for Aramco (S8) | Named: Aramco counts grades 10, 11 + the first term of 12 (previous cycle) |
| 10 | «أغلب مسارات الدراسة في الخارج تحتاج… آيلتس» | **Too broad**: Stanford and Harvard ask for no English test from first-year applicants, and others exempt students from English-taught schools (Princeton, Yale, Penn) (S13); the scholarship asks for IELTS only for a prep year (S6) | Removed; English is framed as a skill, and the test as "depends on the university" |
| 10 | Tracks «مثل العام، أو علوم الحاسب والهندسة، أو الصحة والحياة» | True but incomplete | All five tracks named (S1) |
| 10 | «بعض برامج الابتعاث تشترط مسارات معينة» | Aramco does (S8); the custodian scholarship doesn't say so | Says Aramco, with its source |
| 10 | Activities: «بعض البرامج والجامعات تهتم بها» | Unsourced | Removed; replaced by the counsellor activities (S3) |
| 11 | «القدرات: بعض البرامج تشترط درجة معيّنة فيه» | True (Aramco ≥ 90, Saudi universities per S4), but the custodian scholarship does **not** (S6) | Replaced by the test table |
| 11 | «سات: لا تطلبه كل الجامعات» | True | Now with numbers: of the 30 الرواد universities we researched, 9 require it (S13) |
| 11 | «المعدل… الرياضيات والعلوم… بعض البرامج تنظر لها بشكل منفصل» | True for Aramco (math + science ≥ 85%) | Named |
| 11 | «برامج تختار الطلاب بالترشيح… الإنجازات… لها وزن كبير» | Unsourced | Removed |
| 12 | «أنهِ اختبارات القدرات والتحصيلي وآيلتس (وسات…)» | **Too broad**: which tests depends on the target (S4, S6, S7, S13) | Replaced by the test table |
| 12 | «تحتاج قبولًا من جامعة في قائمة المسار قبل التقديم» | True (S6) | Kept, sourced |
| 12 | Prep-year conditions | True (S6) | Kept, sourced |
| 12 | «جواز السفر، كشوف الدرجات، نتائج الاختبارات» | Partly sourced (paths.json `documents`) | Uses the program's official list |

## 4. Things found on the way
- **«ثلاث قبولات كحد أقصى» is on the conditions page** (S6, «سياسات التقديم والابتعاث», read 2026-10-12). This resolves the owner's to-do from [custodian-scholarship-2026-27.md](custodian-scholarship-2026-27.md) §3. `paths.json` `one-application` now says it.
- **The age rule conflicts on the same official page** (S6):
  - General condition 9: «ألا يتجاوز عمر المتقدم لمرحلة البكالوريوس 30 عاماً، ويستثنى من ذلك المتقدمون في مسار الرواد».
  - The page's FAQ: «لا يشترط عمر محدد للتقديم على المسارات».
  - Per the rules, neither is published as the answer. It doesn't matter for high-school students, so the site says nothing about age.

## 5. Questions only students can answer (not facts; for the usability test)
1. When, in practice, do students choose their track, and how much does the school decide (S2 says «التسكين… وفق معايير»)?
2. Do students know their school's الموجه الطالبي, and have they ever talked to one about tracks?
3. Which tests do grade 11 students *think* they need, and is that different from the table?
4. Do grade 12 students apply in Saudi Arabia (uap.sa) and abroad at the same time, or choose one?
5. Would they keep a list of applications in واضح, or in their own notes? This decides whether «قائمتي» should ever track status.
6. Does the English routine (20 minutes a day) feel doable next to school?
