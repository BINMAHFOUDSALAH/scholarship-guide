# Paths Research (draft, غير مؤكد)

**Status:** Draft researched by Claude on 2026-10-09. **Nothing here is verified.** Every fact needs the owner to open the source, confirm it is current, and then mark it verified.
**How this is used:** after verification, these facts become `data/paths/*.json` in Stage 2, each with `source` and `last_checked`.

Legend: 🟢 from an official page · 🟡 official but the page may be outdated · 🔴 sources conflict / unconfirmed

---

## 1. برنامج خادم الحرمين الشريفين للابتعاث (Custodian of the Two Holy Mosques Scholarship Program)

**Official site:** https://sites.moe.gov.sa/scholarship-program/
**Apply on:** منصة سفير (Safeer): https://safeer2.moe.gov.sa/Portal 🟡 (the FAQ says Safeer; some third-party sites mention "قبول". **Verify for the current cycle.**)

### Current status (reported by the owner from the program's official X account, 2026-10-09) ✅
| Track | Status now | Note |
|---|---|---|
| **مسار الرواد** | **Open** | |
| **مسار إمداد** | **Closed until further notice** | |
| **مسار واعد** | Changes with new announcements | The owner tracks this and will update it |
- To publish these statuses, add the link to each specific X post as the `source` (statuses change, so each one needs its own dated proof).

### Tracks (المسارات) 🟡 (program home page, last updated 13 Jan 2024)
| Track | Short description | Levels | Relevant for high school graduates? |
|---|---|---|---|
| **مسار الرواد** (Arruaad) | Top 30 institutions worldwide, all fields | Bachelor's, Master's 🟢 | ✅ Yes |
| **مسار إمداد** (Emdad) | Top 200 institutions, fields with high labor-market need | Bachelor's, Master's 🟢 | ✅ Yes |
| **مسار واعد** (Waaid) | Study and training in promising sectors, ending in employment | ? | ❓ Check: it may be partner-specific |
| **مسار البحث والتطوير** (R&D) | Top 200 institutions in research priority fields | ? | ❓ Probably graduate level. Check |

"مسار التميز" (Excellence) appears in older pages and on MIFT, but I found **no current official page** for it. 🔴

### General conditions (الشروط العامة) 🟢
Source: https://sites.moe.gov.sa/scholarship-program/conditions/info-1/
1. Saudi nationality.
2. Good conduct.
3. An admission from an institution on the track's approved list.
4. The major is in the approved majors for the application year.
5. The study mode matches the track.
6. The admitted program meets the track's rules.
7. Full-time study, living in the country of study.
8. Passing the Ministry's ranking and anti-overcrowding policies (المفاضلة ومنع التكدس).
9. Someone currently on a scholarship can apply but cannot be sent on a second one.

### مسار الرواد: special conditions 🟢 (page updated 18 Mar 2025)
Source: https://sites.moe.gov.sa/scholarship-program/paths/path-arruaad/
- Admission from one of the **top 30** institutions on the program's list.
- Admission must be **final and unconditional**, issued by the university's admissions office. Exception: in non-English-speaking countries it may be conditional on language study, which is funded.
- In-person study.

### مسار إمداد: special conditions 🟢 (page updated 27 Apr 2025)
Source: https://sites.moe.gov.sa/scholarship-program/paths/path-emdad/
- Admission from one of the **top 200** institutions on the track's list, in the approved majors.
- Final, unconditional admission (same language exception).
- In-person study.

### Tests and grades
- **No Qudurat/Tahsili score required to apply** 🟢: FAQ: "التقديم متاح دون اشتراط درجة اختبار قدرات وتحصيلي". Source: https://sites.moe.gov.sa/scholarship-program/faqs/
  - A 2026 news headline says the same for Arruaad, adding no age limit (Al Yaum, "لا عمر محدد ولا «قدرات وتحصيلي»"). I couldn't read the full article. 🟡
- **Minimum high school GPA:** 🔴 **Not stated on the official pages I read.** Third-party sites claim 85%, 90% (Emdad), or 95% (Arruaad). They conflict, so **do not publish any number** until it's confirmed officially.
- **Number of admissions:** You may submit several (third parties say up to 3), but only **one** is accepted, based on ranking. 🟢 FAQ (the "3" is from the general rules page per search results; **verify**).
- **English test:** The FAQ gives no fixed requirement. Universities set their own (IELTS/TOEFL). 🟡

### Dates 🔴
- No current-cycle dates on the official pages I read.
- Third parties mention "10 Jan – 7 May 2026" and "until 15 Nov 2026". These conflict and are unofficial. **Verify on Safeer / official accounts.**

### University and majors lists (needed later for the universities feature) 🟢
- Official guide PDF: **الدليل الإرشادي لترتيب قوائم الجامعات حسب المجالات 2026–2027**
  https://object.moe.gov.sa/nasaq/cm/files/aldlyl-alastrshady-ltrtyb-qwaaem-aljamaeat-hsb-almjalat-2027-2026.pdf
  → This is the official source for the top 30 / top 200 lists by field. In Stage 2/3 it becomes `data/universities.json` (each entry with `name_ar`, `name_en`, field, track, source, last_checked).

---

## 2. Aramco: College Degree Program (CDPNE)

**Official page:** https://aramco.com/en/careers/saudi-applicants/non-employee-programs/high-school-and-diploma-graduates/cdpne
**Cycle on page:** 1447–1448 H (2025–2026). 🟡 (the next cycle's criteria may differ)

### Eligibility 🟢 (as written on the page)
- Currently in the **second semester of grade 12**, in the General, Computer Science & Engineering, or Health & Life Science path. Alternative/international systems have separate criteria.
- High school cumulative GPA **≥ 85%** for the whole of high school.
- Math & science cumulative GPA **≥ 85%**.
- **Qudurat or GAT ≥ 90%**.
- Age **≤ 22 (Hijri)**.
- A valid government ID or passport for the screening test.

International-system applicants (2026 criteria PDF): Scientific Qudurat/GAT ≥ 90 **or** SAT Math ≥ 630 **or** ACT Math ≥ 27, plus the GPA rules and an authenticated diploma equivalency. 🟢
Source: https://www.aramco.com/-/media/downloads/careers/2026_cdpne_eligibility_criteria_public-website.pdf

### Steps 🟢
1. Online application (registration is **currently closed**: "will be announced later").
2. English + Math screening test.
3. If nominated: medical exam → career fair → training agreement → orientation.
4. **College Preparatory Program (CPP)**: a full academic year in Dhahran (IELTS prep, university applications).
5. Sponsored bachelor's study abroad in a field **assigned by Aramco**, then targeted employment at Aramco.
- A CPP exemption may be considered case by case for an unconditional offer from a QS top-30 university in a required field.

### Dates 🟡 (2025–2026 cycle, so the next cycle will change)
Testing May 1–2, career fair June 3–4, orientation August 2, Qiyas score update deadline April 23, 2026.

---

## 3. KAUST Gifted Student Program (KGSP)

**Official site:** https://kgsp.kaust.edu.sa/ · details: https://kgsp.kaust.edu.sa/about-kgsp/scholarship-details

### Eligibility and selection 🟢
- Saudi students in their **final year of high school** with strong STEM results and meaningful extracurricular achievements.
- "Selection to the KGSP is extremely competitive, and currently **by invitation only**."
- Nominations come from partners (the search results list Mawhiba, MiSK, SRSI, Olympiad, schools) 🟡 (not shown on the details page I read). Non-nominated students may submit an **interest form** 🟡.
- **Cohort 17 change (Oct 2024 announcement):** no more Foundation Year. Candidates need **valid offers from high-value undergraduate universities**, preferably ones approved for **Arruaad**. 🟢 https://kgsp.kaust.edu.sa/news/news/2024/10/22/kgsp-announces-new-recruitment-strategy-for-cohort-17
- Fully funded STEM bachelor's degrees at top **U.S.** universities, preparing for graduate study at KAUST 🟡.

### Dates 🔴
No current-cycle dates found. Check the official site.

---

## Cross-path insight (useful for the compare table)
- **Arruaad and KGSP both depend on getting a top-university offer yourself.** The student applies to universities first, then to the scholarship. Aramco is different: you apply to Aramco first, and it assigns the field and handles placement.
- **Qudurat:** not required for the government scholarship, but **required (≥ 90%) for Aramco**.
- A strong "what to do in grades 10–11" page follows from this: grades, Qudurat (for Aramco), English (IELTS), SAT, and extracurriculars (for KGSP and top universities).

---

## Tuwaiq quote (for the homepage section) 🔴 needs an official source

- **Wording (from Saudipedia):** "همة السعوديين مثل جبل طويق، ولن تنكسر إلا إذا انهدّ هذا الجبل وتساوى بالأرض"
  ("The ambition of Saudis is like Mount Tuwaiq; it will not break unless this mountain collapses and is leveled with the ground.") The exact punctuation and connecting words vary between sources.
- **Context per Saudipedia:** said by Crown Prince Mohammed bin Salman at the **Future Investment Initiative (مبادرة مستقبل الاستثمار), Riyadh, 2018**.
  Source (secondary): https://saudipedia.com/ar/ما-المقصود-بهمة-طويق؟ (it cites no specific video).
- **Still needed:** the original video from an official channel (e.g. the FII Institute, SPA (واس), or Saudi TV), to confirm the exact wording and to be the play-button link. Until then the section stays hidden (decision 011).

---

## Owner's verification checklist
- [ ] Current application platform for the government scholarship (Safeer vs قبول) and this cycle's dates
- [ ] Whether any minimum high school GPA applies to Arruaad / Emdad
- [ ] Whether Waaid / R&D apply to high school graduates
- [ ] Whether "مسار التميز" still exists
- [ ] Aramco CDPNE criteria for the **next** cycle (2026–2027)
- [ ] KGSP current process: nominations, interest form, dates
- [ ] Tuwaiq quote: official video + exact wording
