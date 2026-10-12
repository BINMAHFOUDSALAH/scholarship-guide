# Timeline: US university applications vs. the Saudi scholarship (worked example: Fall 2028)

**Date:** 2026-10-12.
**By:** two read-only research agents on Haiku (reading with `curl`), then every fact used re-checked by the main session with `curl`.
**Owner review:** not yet.
**Decision record:** [decision 039](../decisions.md).

## 1. The student problem
A student starting in **Fall 2028** is in ثاني ثانوي in 2026–2027.
- Their US applications open in **August 2027** and close in **November 2027 to January 2028**.
- Decisions come in **December 2027** (early) or **March 2028** (regular).
- The scholarship needs an **unconditional offer** first, and its application window is set by the program each year. It doesn't follow the universities' calendar.

The risk: a window that closes before your decisions arrive, or a student who starts preparing in grade 12 when the tests were needed by the summer before it.

## 2. Verified facts (official pages, read 2026-10-12)
| Fact | Exact words | Source |
|---|---|---|
| Common App opens 1 August | Harvard: "the Common Application which opens August 1" | [Harvard timeline](https://college.harvard.edu/admissions/apply/application-timeline) |
| UC application opens 1 August | "Application opens for fall 2027 applicants." (under August 1); submission in November | [UC dates](https://admission.universityofcalifornia.edu/how-to-apply/applying-as-a-first-year/dates-and-deadlines.html) |
| Early decisions in mid-December | Stanford "Decision Released: by mid-December" · Harvard "receive notification by mid-December" · MIT "released in mid-December" · Yale "Decisions Released: Mid-December" · Princeton "Mid-December Decision Notification" · Caltech "notified … by mid-December" | the six official pages |
| Regular decisions in March | MIT "released in mid-March" · Caltech "notification date of mid-March" · Yale "Late March" · Princeton "Late March" · Harvard "by the end of March" · UC "Notification of fall 2027 admission decisions" (March) | the same pages |
| Reply by 1 May | Stanford "Student Reply Date: May 1" · Yale "Admitted Student Reply Deadline: May 1" · Princeton "until May 1" · Caltech "until May 1, 2027" · UC "submit their SIR" (May 1) | the same pages |
| Scholarship needs an unconditional offer | «أن يكون القبول نهائيا غير مشروط… إلا إذا كانت الدولة غير ناطقة باللغة الإنجليزية…» | [الرواد terms](https://sites.moe.gov.sa/scholarship-program/paths/path-arruaad/info-path_terms/) |
| A past window: 2023–2024 | «بدءاً من اليوم الأحد 4 ديسمبر 2022م… حتى الخميس 5 مايو 2023م» (for الرواد، البحث والتطوير، إمداد) | [Ministry news](https://www.moe.gov.sa/ar/mediacenter/MOEnews/Pages/King-Scholarship-Program.aspx) |
| The current window: الرواد 2026 | Opened per the official X post (26 Aug 2026); until 15 Nov 2026 (owner-confirmed) | `paths.json` (unchanged) |
| Self-funded students may apply | «يمكن للطالب الدارس على حسابه الخاص التقديم عند انطباق الشروط…» | [FAQ q31](https://sites.moe.gov.sa/scholarship-program/faqs/question-31/) |
| Results timing is announced, not fixed | «يتم الإعلان عن الوقت المتوقع لصدور النتائج من خلال صفحة البرنامج…» | [FAQ](https://sites.moe.gov.sa/scholarship-program/faqs/) |

**Counted from our data** (`Explorer.timeline_stats()`, the current cycle): of the الرواد universities with researched deadlines, how many have a deadline in October or November, and how many in January. Shown live on the grade pages; never typed by hand.

## 3. What this means
- The two scholarship windows we found are very different: Dec 2022–May 2023 vs. Aug–Nov 2026. **There is no fixed scholarship season**, so the site never names one.
- If the window closes before your decisions, you have no offer to submit in it. Applying in a later window as a self-funded student is allowed by the FAQ. **No official text says whether the time before nomination is funded.** The site says so and tells students to ask the program.

## 4. Not verified (not used)
- **Common App's own page** for the opening date: not found on commonapp.org. The date comes from Harvard and UC.
- **Stanford regular decisions "by early April":** reported by an agent, but not found on the page we read. Not used.
- **Harvard:** "Early May" (table) vs "May 1" (text). Only "May 1" is used, which is the text's wording, and only together with others.
- **Caltech:** a stale passage says "May 1, 2026" next to the 2027 wording. The 2027 wording is used.
- **Blocked or JavaScript-only:** Johns Hopkins, Michigan (403), UChicago (dates not in the page's HTML).
- **Windows for 2024 and 2025:** no official announcement found.
- **Track lists differ:** the Ministry's e-service page lists six tracks; the program site lists four. Noted for the owner; the site keeps the program site's four.

## 5. Questions for students (usability test)
- When did you first hear about application windows?
- Did a window ever close before you had an offer?
- Would a "you are here" timeline have changed when you started preparing?
