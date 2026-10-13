# US applications: Common App, UC, fees and waivers (research by Claude, 2026-10-12)

**Method:** Haiku `source-researcher` agents: one for the systems' rules, seven for 53 universities' fees. Two pages that only render in a browser were read by the main session in the built-in browser: Common App's fee-waiver help article and the 2026–2027 essay prompts. The main session re-checked the Caltech, Stanford and UT Austin fee quotes with `curl`. Not reviewed by the owner.

## Common App
- **Fee waiver** ([help article](https://appsupport.commonapp.org/applicantsupport/s/article/What-do-I-need-to-know-about-the-Common-App-fee-waiver), read in a browser):
  - «International students may be eligible for a Common App fee waiver. Each college has their own policies.»
  - «Colleges might only accept the Common App fee waiver for U.S. students.» / «Some colleges might not accept the Common App fee waiver for any students.» / «Colleges may offer their own fee waivers.»
  - **Eligibility:** nine qualifications, mostly US programs (FRPL, SAT/ACT fee waiver, USDA income guidelines, public assistance, TRIO/GEAR UP, public housing/foster/homeless, ward of the state, Pell). One isn't tied to a US program: «a supporting statement from a school official, college access counselor, financial aid officer, or community leader».
  - «answer the fee waiver question with your own financial circumstances».
  - **Steps:** My Common Application → Profile → Common App fee waiver → review eligibility → sign.
- **Counselor and fees** ([fees PDF](https://www.commonapp.org/static/f9d54dd41c76d04ef3e91779d03f7b93/Resource_FY_AppFees_ENG_2025.06.25_0.pdf)): the counselor confirms the waiver; «500+ colleges have no application fee for international students»; each college's fee shows under My Colleges.
- **Essays:** 7 prompts for 2026–2027 ([prompts](https://www.commonapp.org/apply/essay-prompts)). **The word limit isn't on the page, so it isn't published.**
- **Recommendations** ([PDF](https://www.commonapp.org/static/088c92645a5827f61016fd81ac42b3f4/Resource_FY_RecProcess_ENG_2025.06.25_1.pdf)): the counselor sends the School Report and transcripts; each college sets its teacher letters; ask at least three weeks ahead.

## University of California (UC)
- **Fees and waiver** ([apply now](https://admission.universityofcalifornia.edu/apply-now.html)): «The application fee is $80 for each UC campus ($95 for international and non-immigrant applicants).» «The fee waiver program is for United States citizens, permanent residents, and applicants eligible for AB540 benefits.»
- **Reduced fee, not a waiver** ([international](https://admission.universityofcalifornia.edu/admission-requirements/international-applicants/applying-for-admission/)): «international students enrolled in a U.S. institution may qualify for the $80 application fee».
- **The application:** 4 of 8 personal insight questions, 350 words each; no recommendation letters with it.
- **Filing period for Fall 2027:** 1 October – 30 November **2026**. The agent wrote 2027; UCSB's FAQ says «October 1 - November 30, 2026 for the fall 2027 term».

## Per-university fees (50 of 53 US universities)
Saved as `application_fee` in `data/university_details/<id>.json`: fee, waiver class, short note, source.
- **Waiver classes:** `accepts_common_app` 15, `own_waiver` 9, `not_stated` 12, `domestic_only` 12, `none` 2.
- **Judgment calls (owner to spot-check):**
  - `accepts_common_app` often means the page accepts the waiver without saying whether international students qualify (Georgia Tech, Northwestern, Duke, Cornell, CMU, Penn).
  - Michigan says international students are «not typically eligible», so it's `domestic_only`.
- **Not published:**
  - Columbia: its site blocked our tools.
  - South Carolina: the international page says $100, the freshman page $70.
  - Purdue: no amount, no rule.
  - Texas A&M: fee not published (catalog $90 vs. freshman page $75); its waiver isn't for international students.
- **Fee amount not on official pages** (fee null, waiver policy shown): USC, Princeton, Georgetown, Yale, UChicago.
