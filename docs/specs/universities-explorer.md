# Spec: Universities explorer (draft for the owner's approval)

**Status:** draft, 2026-10-11. Nothing is built yet. Approve or change the "Decisions needed" at the bottom first.

## Goal
Help a student answer, in under a minute:
1. Is university X on the official list for مسار الرواد or مسار إمداد, and at what rank, in which field?
2. Which listed universities are there for my field (and in a given country)?
3. Is this university in a non-English-speaking country, where the language-study exception might apply?

Everything comes from the official guide. The explorer never says "you are eligible". It shows what the list says and links to the PDF page.

## Source: what the official PDF actually contains
`الدليل الاسترشادي لترتيب قوائم الجامعات حسب المجالات للعام الأكاديمي 2026–2027` (75 pages, downloaded 2026-10-11 to `data/raw/`, which is git-ignored and re-downloadable).

| Pages | Content |
|---|---|
| 3 | Introduction |
| 4–5 | **مسار الرواد**: one ranked list, 30 institutions (all fields) |
| 6–42 | **مسار البحث والتطوير** (doctorate): fields, their majors, then a ranked list per field (up to ~160) |
| 43–74 | **مسار إمداد**: fields, majors per field, then a ranked list per field |

Each list entry has a **rank**, the university's **English name**, and a **country flag** (an image). Fields have Arabic + English names; each field lists its majors (Arabic + English).

**Not in the PDF:** Arabic university names, cities, which degrees (bachelor's/master's) each university offers, programs, or SAT/English requirements. The explorer won't show these in v1 (no guessing).

**Known extraction details:** the Arabic text comes out reversed (visual order) and must be put back in logical order; long English names wrap over 2–3 lines; the lists are a 3×10 grid per page, ordered right to left.

## Data: `data/universities.json`
```json
{
  "source": {"title": "...", "url": "https://object.moe.gov.sa/...pdf", "academic_year": "2026-2027", "retrieved": "2026-10-11"},
  "fields": [{"id": "ict", "track": "emdad", "name_ar": "تقنية الاتصالات والمعلومات", "name_en": "Information and Communication Technologies (ICTs)", "majors": [{"name_ar": "...", "name_en": "..."}], "pdf_pages": [63, 64]}],
  "universities": [{"id": "university-of-waterloo", "name_en": "University of Waterloo", "country": "CA",
                    "listings": [{"track": "emdad", "field": "ict", "rank": 33, "pdf_page": 64}]}]
}
```
- `country` comes from the flag: each distinct flag image is hashed, and `scripts/flag_countries.json` maps hash → country code. Filled in once by hand (about 16 countries), and the owner checks it.
- Country names in Arabic + "official language is English?" come from the program's own country pages, in a small `data/countries.json`.

## Extraction: `scripts/extract_universities.py`
- `pdfplumber` (dev only, installed 2026-10-11) reads word positions, groups them into the 3×10 grid cells (rank + name lines), and hashes each flag image.
- **Checks that make the script fail loudly:** every list's ranks run 1..N with no gaps or duplicates; every entry has a name and a known country; the Arruaad list has exactly 30.
- The owner spot-checks 20 random entries against the PDF before publishing.
- Re-run when the 2027–2028 guide is published (expected Dec 2026 / Jan 2027): update the URL, run, check, commit.

## Pages
- **`/universities`**: a search field (university name) + filters: track (الرواد / إمداد, with البحث والتطوير behind a "دكتوراه" option), field, country. Results show university · country · rank per track/field. Works without JavaScript (a normal GET form), with a little JS for instant filtering later.
- **`/universities/<id>`**: every listing for that university (track, field, rank, PDF page), its country, and, for a non-English-speaking country, a short note linking to the conditional-admission section of the program page.
- **`/api/universities`**: the same data as JSON (for the future chatbot and agents).
- A header search link arrives with this page (decision 023: "no search until there's something to search").
- Linked from the program page and the homepage program row («ابحث عن جامعتك»).

## Tests
Data rules (ranks continuous, Arruaad = 30, every country known, source URL official), page loads, filters return the right rows, unknown id → 404, no third-party requests.

## Decisions needed from the owner
1. Show the **البحث والتطوير** (doctorate) lists too, behind a filter, or leave them out for now?
2. **Arabic university names:** the PDF has English only. Keep English only (recommended, nothing invented), or add Arabic names later from an official source?
3. Is a GET-form page (no app-like instant search in v1) fine to start?
