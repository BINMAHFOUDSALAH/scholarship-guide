# SAT, TOEFL, القدرات/التحصيلي: facts for the resource pages (research by Claude, 2026-10-12)

**Method:** two `source-researcher` agents (Haiku) read College Board, ETS and ETEC pages. The main session re-checked the key quotes with `curl`: the SAT fee, structure and free Bluebook practice; TOEFL's 1–6 scale, 2-year validity, and the 0–120 comparable score. ETEC's site is a JavaScript app: the main session read its products list in the built-in browser. The single test pages (القدرات, التحصيلي) rendered **empty**, even in a browser. Not reviewed by the owner.

## SAT → `content/resources/sat.md`
- Two sections: Reading and Writing (64 min, 54 questions) and Math (70 min, 44 questions); total «2 hours and 14 minutes»; digital in Bluebook. [structure](https://satsuite.collegeboard.org/sat/whats-on-the-test/structure)
- Scores: 200–800 per section, 400–1600 total. [scores](https://satsuite.collegeboard.org/scores/what-scores-mean/how-scores-calculated)
- «The SAT registration fee is $68, plus a $43 international fee.»; test center fee $24 at select locations. [fees](https://satsuite.collegeboard.org/sat/registration/international-testing/fees) We don't publish a total.
- Dates apply «to all students—U.S. and international»: Dec 5 2026; Mar 6, May 1, Jun 5 2027. [dates](https://satsuite.collegeboard.org/sat/dates-deadlines)
- 4 free score sends, changeable until 9 days after the test; Score Choice doesn't apply to them; most weekend scores released in 2–4 weeks. [weekend](https://satsuite.collegeboard.org/scores/sending-sat-scores/weekend) · [score choice](https://satsuite.collegeboard.org/scores/sending-sat-scores/additional/score-choice) · [release](https://satsuite.collegeboard.org/scores/score-release-dates)
- Free: «Take a free, full-length practice test on Bluebook»; Khan Academy «Best of all, it's free!». [practice](https://satsuite.collegeboard.org/practice)
- **Not verified:** test centers in Saudi Arabia (the search tool wasn't reachable); fee waivers abroad; the 10-minute break; free paper tests.

## TOEFL iBT → `content/resources/toefl.md`
- «As of January 21, 2026, TOEFL iBT score reports feature a new 1 – 6 scale, in half point increments»; overall = average of four sections. [scores](https://www.ets.org/toefl/test-takers/ibt/scores/understand-scores.html)
- For two years, reports show «(1) CEFR level; (2) 1 – 6 overall and section scores; and (3) a comparable 0 – 120 overall score». [scale update](https://www.ets.org/toefl/institutions/ibt/score-scale-update.html)
- «Please allow approximately two hours»; test center or Home Edition. [content](https://www.ets.org/toefl/test-takers/ibt/about/content.html) · [options](https://www.ets.org/toefl/test-takers/ibt/about/testing-options.html)
- Scores in the ETS account 3 days after the test; valid 2 years. [get scores](https://www.ets.org/toefl/test-takers/ibt/scores/get-scores.html)
- Free 8-week Test Prep Planner. [prepare](https://www.ets.org/toefl/test-takers/ibt/prepare/tests)
- ⚠️ **Conflict, not published:** when universities receive scores: «approximately 4–16 business days» ([schedule](https://www.ets.org/toefl/test-takers/ibt/schedule.html)) vs. «within 11 business days» (FAQ).
- **Not verified:** the Saudi price (a per-country widget; the page links it), section times in minutes, a free full practice test.
- **Note for the owner:** KGSP (and maybe universities) still state TOEFL minimums on the old 0–120 scale (e.g. 90). The page explains the comparable score.

## القدرات / التحصيلي → `content/resources/qudurat-tahsili.md`
- From ETEC's [products list](https://etec.gov.sa/ar/centers/qiy/p?id=4aea1743-5b9c-4833-bda8-5430b00dd2fa) (rendered in a browser): القدرات «يقيس القدرات التحليلية والاستدلالية… فهم المقروء وإدراك العلاقات المنطقية وحل المسائل الرياضية المبنية على مفاهيم رياضية أساسية»; التحصيلي العلمي: «الأحياء، الكيمياء، الفيزياء، الرياضيات»; التحصيلي النظري: «المسار الشرعي ومسار إدارة الأعمال».
- Registration: «منصة التسجيل للاختبارات» → `e-services.etec.gov.sa` ([Qiyas center](https://etec.gov.sa/ar/centers/qiy)).
- **Not verified, not published:** number of questions, duration, score scale, fees, attempts, 1448 test periods, free prep material. ETEC's single-test pages render empty; its guide PDFs (e.g. the 309-page GAT guide) have Arabic text that doesn't extract.
- **Owner checklist:** open the GAT and التحصيلي pages on etec.gov.sa or the registration platform in a normal browser, and copy the duration, scale, fee and attempts with the date, so we can add them.
