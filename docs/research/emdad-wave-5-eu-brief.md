# إمداد wave 5: European universities (research brief)

**Status:** done 2026-10-16 (decision 061). 12 agents (5a first, then 5b and 5c together). **50 of 57 saved**; every saved fact's quote was checked on its page (`check_quote.py`, PDFs via `pdftotext`, Leiden in the browser).
- **Not saved:**
  - Tilburg and Humboldt (every page blocked)
  - INSEAD (graduate only)
  - Montpellier (key quote not on the page; the platform differs between the university and Campus France)
  - L'Institut Agro (no high-school entry found)
  - Toulouse (the list's entry may mean a different member institution)
  - Universitat de Barcelona (pages blocked)
- **Saudi certificate:**
  - `false` for 7: EPFL (entrance exam), HSG, Zurich, Geneva and Lausanne (a 3-year degree), Wageningen and Delft (a year of university first).
  - `true` for 1: Sapienza (named in its table).
  - `null` elsewhere. German universities point to anabin, which only a form query can read; uni-assist's Saudi page covers private and industrial schools only.
- **Deadlines:** most are published without a year, so they were left out. With a year: TU Berlin, Groningen, VU, Erasmus, TU/e, Sciences Po, Polytechnique, Bocconi, Padova.

**Scope:** the 57 universities in the الرواد/إمداد lists of NL, CH, DE, FR, IT, ES with no `data/university_details/<id>.json` (البحث والتطوير-only universities skipped). Read the [wave 2 brief](emdad-wave-2-uk-brief.md) and the agent rules there first; only the differences are below. Finished examples: `data/university_details/eth-zurich.json` (German-taught, Switzerland) and `data/university_details/the-university-of-exeter.json` (structure of every block).

## What matters for a European university (in this order)
1. **Language of teaching of its bachelor's degrees** → `language_note_ar`. Most bachelor's programmes in these countries are taught in the national language. Say plainly, from the university's own page: are there bachelor's programmes taught **entirely in English**? Name up to three as examples (English names), or say the page lists none. The language test the national-language programmes ask for (e.g. German C1/DSH/TestDaF, French DELF/DALF B2, Italian B2, Dutch NT2) goes in the same note, with its level.
2. **The Saudi secondary certificate** → `saudi_certificate` (true/false/null, exactly as in wave 2). In these countries the answer often comes from a national rule the university links to. A national body's official page **counts as official** for this item:
   - Germany: **uni-assist**, **DAAD**, the KMK's **anabin** database. A Saudi certificate usually gives access to a Studienkolleg (foundation course) and then the Feststellungsprüfung, unless extra conditions are met. Copy the exact rule; never summarise from memory.
   - Netherlands: **Nuffic** and the university's own country page ("Saudi Arabia", "international diploma requirements").
   - Switzerland: **swissuniversities** country lists and the university's page.
   - France: **Campus France / Études en France** and the university's page.
   - Italy: **Universitaly** and the Ministry's "studiare in Italia" pages (12 years of schooling, entrance exams).
   - Spain: the university's page and **UNEDasiss** (homologación / credencial).
   If the page says "one year of university study in the home country is required", that's `direct_entry: false`, with the rule in `note_ar`.
3. **English tests (IELTS / TOEFL iBT / Duolingo)**: only for English-taught bachelor's programmes, from the university's own page, with decision 058's rules (`min` only for a stated minimum; "recommended"/"typically" → `recommended`; per programme → `varies: true`; not among the listed tests → `listed: false`; the page says English isn't required (national-language teaching) → leave the tests `null` and report it, the main session sets `"required": false`).
4. **Platform**: Studielink (NL), uni-assist or the university portal (DE), Parcoursup or Études en France (FR), Universitaly + the university portal (IT), the university portal (ES/CH). With the URL.
5. **Deadline** for fall 2027 entry for non-EU applicants, **only with a year stated on the page**. Non-EU deadlines are often earlier than EU ones (e.g. 1 April or 15 January); say which group it applies to in `note_ar`.
6. **SAT/ACT**: usually not relevant; leave `sat_act: null` unless the page names it (e.g. some Italian/Dutch English-taught programmes accept SAT).
7. Acceptance rate: skip.

## Rules for every agent (on top of `.claude/agents/source-researcher.md`)
- Read the page itself: WebFetch, else `curl -sL -m 30 -A "Mozilla/5.0" URL` **to stdout only** (never `-o`, `>`, `tee`, never a temp file). If a PDF won't read from stdout, report it as not readable; don't save it.
- A search snippet is never a source. A page you couldn't open → not found.
- Pages in German/French/Italian/Spanish/Dutch are fine: quote them in their own language.
- Every number, date and yes/no: exact quote + URL. Today's date: 2026-10-16.
- Return the JSON blocks of the example file, plus an evidence list, plus **what you could not verify and why**.

## Batches
**5a (Netherlands + Switzerland)**
- N1: wageningen-university-research · erasmus-university-rotterdam · delft-university-of-technology · university-of-amsterdam · leiden-university
- N2: tilburg-university · utrecht-university · vrije-universiteit-amsterdam · university-of-groningen · eindhoven-university-of-technology
- C1: epfl · university-of-st-gallen-hsg · university-of-zurich · university-of-geneva · university-of-lausanne

**5b (Germany)**
- G1: ludwig-maximilians-universitat-munchen · technical-university-of-munich · humboldt-universitat-zu-berlin · freie-universitaet-berlin
- G2: university-of-gottingen · rheinische-friedrich-wilhelms-universitat-bonn · ruprecht-karls-universitat-heidelberg · universitat-mannheim
- G3: eberhard-karls-universitat-tubingen · albert-ludwigs-universitaet-freiburg · technische-universitat-berlin-tu-berlin · rwth-aachen-university · karlsruhe-institute-of-technology-kit
- G4: university-of-cologne · universitat-hamburg · university-of-hohenheim · universitat-konstanz

**5c (France, Italy, Spain)**
- F1: sorbonne-university · universite-psl · insead-france · universite-paris-1-pantheon-sorbonne · sciences-po
- F2: universite-de-montpellier · institut-polytechnique-de-paris · l-institut-agro-l-institut-agro-dijon-l-institut-agro-montpellier-l-institut-agro-rennes-angers · university-of-toulouse
- I1: universita-commerciale-luigi-bocconi-bocconi-university · sapienza-university-of-rome · alma-mater-studiorum-university-of-bologna · politecnico-di-milano · university-of-naples-federico-ii
- I2: universita-di-padova · university-of-milan · university-of-florence · ca-foscari-university-of-venice · university-of-turin
- S1: university-of-granada · complutense-university-of-madrid · universitat-de-barcelona · universitat-pompeu-fabra-barcelona · universitat-autonoma-de-barcelona · universitat-ramon-llull

INSEAD teaches postgraduate only as far as we know: if its official page says there is no bachelor's, report that and nothing else.
