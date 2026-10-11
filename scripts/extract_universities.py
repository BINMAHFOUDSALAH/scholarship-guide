"""Extract the official universities guide (PDF) into data/universities.json.

Source: «الدليل الاسترشادي لترتيب قوائم الجامعات حسب المجالات» (Ministry of Education).
Run from the repo root, after downloading the PDF into data/raw/ (see SOURCE below):

    .venv\\Scripts\\python.exe scripts\\extract_universities.py

What it reads:
- Ranked lists: every entry is a grid cell with [name][rank][flag]. The flag image anchors
  the cell; the flag's image data is hashed and mapped to a country (scripts/flag_countries.json).
- Majors: every major is a box with its Arabic name, English name, and sometimes a
  «درجة الماجستير فقط» (master's only) tag.

The script fails loudly instead of guessing: ranks must run 1..N with no gaps, every flag
must map to a known country, and the Arruaad list must have exactly 30 entries.
When the new edition is published: update SOURCE, download, run, check the output, commit.
"""

import hashlib
import json
import unicodedata
import re
import sys
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "data" / "raw" / "universities-guide-2026-2027.pdf"
FLAGS = ROOT / "scripts" / "flag_countries.json"
ALIASES = ROOT / "scripts" / "university_aliases.json"
OVERRIDES = ROOT / "scripts" / "list_overrides.json"
OUT = ROOT / "data" / "universities.json"

SOURCE = {
    "title_ar": "الدليل الاسترشادي لترتيب قوائم الجامعات حسب المجالات للعام الأكاديمي 2026–2027",
    "url": "https://object.moe.gov.sa/nasaq/cm/files/aldlyl-alastrshady-ltrtyb-qwaaem-aljamaeat-hsb-almjalat-2027-2026.pdf",
    "academic_year": "2026-2027",
    "retrieved": "2026-10-11",
    "publisher_ar": "وزارة التعليم",
}

# Which pages hold what (1-based page numbers, from the guide's table of contents and headings).
ARRUAAD_LIST_PAGE = 5
RND_MAJOR_PAGES = range(8, 14)
RND_LIST_PAGES = range(14, 43)
EMDAD_MAJOR_PAGES = range(45, 51)
EMDAD_LIST_PAGES = range(51, 75)

# Clean English names per field (the PDF's headings have stray brackets, e.g. "(ICTs (").
FIELD_NAMES_EN = {
    "natural-sciences": "Natural sciences, mathematics and statistics",
    "ict": "Information and Communication Technologies (ICTs)",
    "engineering": "Engineering, manufacturing and construction",
    "agriculture": "Agriculture, forestry, fisheries and veterinary",
    "social-sciences": "Social sciences, journalism and information",
    "arts-humanities": "Arts and humanities",
    "business-law": "Business, administration and law",
    "services": "Services",
}

# The English field headings in the guide → our field ids.
FIELD_IDS = {
    "natural sciences, mathematics and statistics": "natural-sciences",
    "information and communication technologies icts": "ict",
    "engineering, manufacturing and construction": "engineering",
    "agriculture, forestry, fisheries and veterinary": "agriculture",
    "social sciences, journalism and information": "social-sciences",
    "arts and humanities": "arts-humanities",
    "business, administration and law": "business-law",
    "services": "services",
}

ARABIC = re.compile(r"[؀-ۿ]")
LATIN = re.compile(r"[A-Za-z]")


def arabic_word(word):
    """pdfplumber gives Arabic in visual order. Reverse the glyphs (not the letters), so a
    joined lam-alef glyph («لا») stays in the right order, and drop the stretching tatweel."""
    glyphs = [c["text"] for c in sorted(word["chars"], key=lambda c: c["x0"])]
    return "".join(reversed(glyphs)).replace("ـ", "")


def words_of(page):
    words = page.extract_words(return_chars=True, keep_blank_chars=False)
    for w in words:
        w["ar"] = bool(ARABIC.search(w["text"]))
        w["fixed"] = arabic_word(w) if w["ar"] else w["text"]
    return words


def line_text(words):
    """Join words on one visual line: Arabic words right-to-left, Latin words left-to-right."""
    ar = [w for w in words if w["ar"]]
    la = [w for w in words if not w["ar"]]
    ar_text = " ".join(w["fixed"] for w in sorted(ar, key=lambda w: -w["x0"]))
    la_text = " ".join(w["fixed"] for w in sorted(la, key=lambda w: w["x0"]))
    return ar_text, la_text


def group_lines(words, tolerance=3):
    lines = []
    for w in sorted(words, key=lambda w: w["top"]):
        if lines and abs(lines[-1][0]["top"] - w["top"]) <= tolerance:
            lines[-1].append(w)
        else:
            lines.append([w])
    return lines


def clean(text):
    text = text.replace(" ", " ").replace("›", "'")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^[,\s]+|\s*-\s*$", "", text)  # stray leading comma / trailing hyphen
    text = re.sub(r"(\w)- (\w)", r"\1-\2", text)  # hyphen at a line break: "Ludwig-Maximilians- Universität"
    text = re.sub(r"(\w)\(", r"\1 (", text)  # "University(SKKU)" → "University (SKKU)"
    return text


def fix_line(line):
    """The PDF lays out English names right-to-left, so a closing ")" at the end of a wrapped
    line shows up as "(" at its start: "(of Technology (MIT" → "of Technology (MIT)"."""
    line = line.strip()
    if line.startswith("(") and line.count("(") > line.count(")"):
        line = line[1:] + ")"
    return line


def field_id_from(heading_en):
    key = re.sub(r"[()|]", " ", heading_en).lower()
    key = re.sub(r"technologiesicts", "technologies icts", key)
    key = re.sub(r"\s+", " ", key).strip()
    for name, fid in FIELD_IDS.items():
        if key.startswith(name):
            return fid
    raise SystemExit(f"Unknown field heading: {heading_en!r}")


def all_headings(words):
    """Field headings: 'English name | الاسم العربي'. The «|» sits a few points lower than the
    English words, so everything within 8pt of it vertically belongs to the heading."""
    out = []
    for bar in (w for w in words if "|" in w["text"]):
        if any(abs(bar["top"] - top) < 8 for top, *_ in out):
            continue
        line = [w for w in words if abs(w["top"] - bar["top"]) <= 8 and w["text"] != "|"]
        ar, en = line_text(line)
        out.append((min(w["top"] for w in line), clean(en.replace("|", "")), clean(ar.replace("|", ""))))
    return sorted(out)


def page_heading(words):
    headings = all_headings(words)
    return headings[0] if headings else None


def flag_hash(image):
    return hashlib.md5(image["stream"].get_data()).hexdigest()[:12]


def is_flag(image):
    # Flag-sized, and above the page footer (stray flags sit beside the page number there).
    return 20 <= image["width"] <= 36 and 20 <= image["height"] <= 36 and image["top"] < 780


def visible_flags(page):
    """Flag images a student actually sees. Where two flags are stacked on the same spot, the one
    drawn later (higher index) is on top, so the earlier one is dropped."""
    flags = [(i, img) for i, img in enumerate(page.images) if is_flag(img)]
    hidden = {i for i, a in flags for j, b in flags
              if j > i and abs(a["x0"] - b["x0"]) < 6 and abs(a["top"] - b["top"]) < 6}
    return [img for i, img in flags if i not in hidden]


def cell_notes(words, img):
    """Notes the guide attaches to one list entry:
    - a small label above the cell: «درجة الماجستير فقط» or «للأشخاص ذوي الإعاقة (الإعاقة السمعية)»
    - a box under the cell: «درجة البكالوريوس للتخصصات التالية فقط:» + "* Major" lines in English."""
    x_left, x_right = img["x0"] - 185, img["x1"] + 2
    in_cell = [w for w in words if w["x0"] >= x_left and w["x1"] <= x_right]
    label = [w for w in in_cell if w["ar"] and img["top"] - 24 <= w["top"] <= img["top"] + 2]
    label_ar = line_text(label)[0] if label else ""

    below = [w for w in in_cell if img["bottom"] + 2 <= w["top"] <= img["bottom"] + 48]
    only_majors, box_ar = [], ""
    if any("البكالوريوس" in w["fixed"] for w in below if w["ar"]):
        box_ar = " ".join(line_text(line)[0] for line in group_lines([w for w in below if w["ar"]]))
        for line in group_lines([w for w in below if not w["ar"]]):
            text = " ".join(w["text"] for w in sorted(line, key=lambda w: w["x0"]))
            if text.startswith("*"):
                only_majors.append(clean(text.lstrip("* ")))
            elif only_majors:
                only_majors[-1] = clean(only_majors[-1] + " " + text)

    notes = {}
    if "الماجستير" in label_ar:
        notes["masters_only"] = True
    if "الإعاقة" in label_ar:
        notes["hearing_impaired_only"] = True
    if label_ar:
        notes["label_ar"] = clean(label_ar)
    if only_majors:
        notes["bachelors_only_majors"] = only_majors
        notes["box_ar"] = clean(box_ar)
    return notes


def list_entries(page, overrides):
    """[(rank, name_en, flag_hash, notes)] for one ranked-list page."""
    words = words_of(page)
    entries = []
    for img in visible_flags(page):
        key = f"{page.page_number}:{round(img['x0'])}:{round(img['top'])}"
        if key in overrides:
            o = overrides[key]
            entries.append((o["rank"], o["name_en"], flag_hash(img), cell_notes(words, img)))
            continue
        x_right = img["x0"]
        top, bottom = img["top"] - 11, img["bottom"] + 11
        # Stop above a «درجة البكالوريوس…» box under the cell, so its major list isn't read as the name.
        box = [w for w in words if w["ar"] and "البكالوريوس" in w["fixed"]
               and x_right - 185 <= w["x0"] <= x_right + 30 and img["bottom"] - 2 <= w["top"] <= bottom]
        if box:
            bottom = min(w["top"] for w in box) - 1
        cell = [w for w in words
                if not w["ar"] and not w["text"].startswith("*")
                and w["x1"] <= x_right + 1 and w["x0"] >= x_right - 185
                and w["top"] >= top and w["bottom"] <= bottom]
        numbers = [w for w in cell if re.fullmatch(r"\d{1,3}", w["text"])]
        if not numbers:
            # A stray flag outside the grid (e.g. in the page footer) with no entry next to it.
            # Safe to skip: the rank-continuity check below catches any real entry we miss.
            print(f"  note: p{page.page_number} skips a flag with no rank at x={img['x0']:.0f}, y={img['top']:.0f}")
            continue
        rank_word = max(numbers, key=lambda w: w["x0"])  # the number right beside the flag
        name_words = [w for w in cell if w is not rank_word and w["x1"] <= rank_word["x0"] + 1]
        name = " ".join(fix_line(" ".join(w["text"] for w in sorted(line, key=lambda w: w["x0"])))
                        for line in group_lines(name_words))
        entries.append((int(rank_word["text"]), clean(name), flag_hash(img), cell_notes(words, img)))
    return entries


def majors_on(page):
    """{(field_id, heading_ar): [major, ...]} for one majors page."""
    words = words_of(page)
    headings = sorted(all_headings(words))
    boxes = [r for r in page.rects if 150 <= r["width"] <= 170 and 35 <= r["height"] <= 50]
    result = {}
    for box in sorted(boxes, key=lambda r: (round(r["top"]), -r["x0"])):
        inside = [w for w in words
                  if w["x0"] >= box["x0"] - 2 and w["x1"] <= box["x1"] + 2
                  and w["top"] >= box["top"] - 14 and w["bottom"] <= box["bottom"] + 2]
        masters_only = any("الماجستير" in w["fixed"] for w in inside)
        inside = [w for w in inside if w["top"] >= box["top"] - 1
                  and not any(t in w["fixed"] for t in ("الماجستير", "درجة", "فقط"))]
        name_ar = " ".join(line_text(line)[0] for line in group_lines([w for w in inside if w["ar"]]))
        name_en = " ".join(line_text(line)[1] for line in group_lines([w for w in inside if not w["ar"]]))
        if not name_ar and not name_en:
            continue
        above = [h for h in headings if h[0] < box["top"]]
        if not above:
            raise SystemExit(f"p{page.page_number}: a major box has no field heading above it")
        _, h_en, h_ar = above[-1]
        key = (field_id_from(h_en), h_ar, h_en)
        result.setdefault(key, []).append({
            "name_ar": clean(name_ar), "name_en": clean(name_en), "masters_only": masters_only,
        })
    return result


def slug(name):
    # "Université Paris-Saclay" → "universite-paris-saclay": accents become plain letters first.
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def norm(name):
    s = name.lower().replace("–", "-").replace("’", "'")
    s = re.sub(r"\bthe\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def main():
    # Windows consoles default to a non-Unicode code page; print Arabic and names safely.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if not PDF.is_file():
        raise SystemExit(f"Missing {PDF}. Download it from:\n{SOURCE['url']}")
    flags = json.loads(FLAGS.read_text(encoding="utf-8")) if FLAGS.is_file() else {}
    raw_aliases = json.loads(ALIASES.read_text(encoding="utf-8")) if ALIASES.is_file() else {}
    aliases = {norm(k): v for k, v in raw_aliases.items() if not k.startswith("_")}
    overrides = json.loads(OVERRIDES.read_text(encoding="utf-8")) if OVERRIDES.is_file() else {}

    lists = {}      # (track, field_id) -> [(rank, name, hash, page)]
    fields = {}     # (track, field_id) -> field record
    unknown_flags = {}

    with pdfplumber.open(PDF) as pdf:
        # Majors per field.
        for track, pages in (("rnd", RND_MAJOR_PAGES), ("emdad", EMDAD_MAJOR_PAGES)):
            for n in pages:
                for (fid, h_ar, h_en), majors in majors_on(pdf.pages[n - 1]).items():
                    f = fields.setdefault((track, fid), {
                        "id": fid, "track": track, "name_ar": h_ar, "name_en": h_en,
                        "majors": [], "majors_pages": [], "list_pages": [],
                    })
                    f["majors"].extend(majors)
                    if n not in f["majors_pages"]:
                        f["majors_pages"].append(n)

        # Ranked lists.
        list_pages = [("arruaad", [ARRUAAD_LIST_PAGE])] + [("rnd", RND_LIST_PAGES), ("emdad", EMDAD_LIST_PAGES)]
        for track, pages in list_pages:
            for n in pages:
                page = pdf.pages[n - 1]
                if track == "arruaad":
                    fid = None
                else:
                    heading = page_heading(words_of(page))
                    fid = field_id_from(heading[1])
                    f = fields.setdefault((track, fid), {
                        "id": fid, "track": track, "name_ar": heading[2], "name_en": heading[1],
                        "majors": [], "majors_pages": [], "list_pages": [],
                    })
                    f["list_pages"].append(n)
                for rank, name, h, notes in list_entries(page, overrides):
                    lists.setdefault((track, fid), []).append((rank, name, h, n, notes))
                    if h not in flags:
                        unknown_flags.setdefault(h, (n, name))

    if unknown_flags:
        print("Unknown flags (add them to scripts/flag_countries.json):", file=sys.stderr)
        for h, (n, name) in sorted(unknown_flags.items(), key=lambda kv: kv[1]):
            print(f'  "{h}": "??",   # p{n} {name}', file=sys.stderr)
        raise SystemExit(1)

    # Checks: continuous ranks (except gaps the PDF itself has, listed in list_overrides.json), Arruaad = 30.
    problems = []
    gaps = overrides.get("_gaps", {})
    for key, entries in lists.items():
        ranks = sorted(r for r, *_ in entries)
        known = set(gaps.get(f"{key[0]}:{key[1]}", {}).get("missing", []))
        expected = [r for r in range(1, max(ranks) + 1) if r not in known]
        if ranks != expected:
            missing = sorted(set(expected) - set(ranks))
            dupes = sorted({r for r in ranks if ranks.count(r) > 1})
            problems.append(f"{key}: ranks not 1..N (missing {missing[:10]}, duplicates {dupes[:10]})")
    if len(lists.get(("arruaad", None), [])) != 30:
        problems.append(f"Arruaad list has {len(lists.get(('arruaad', None), []))} entries, expected 30")
    if problems:
        raise SystemExit("Checks failed:\n  " + "\n  ".join(problems))

    # Merge the same university across lists (names are compared loosely; known variants in aliases).
    universities = {}
    for (track, fid), entries in lists.items():
        for rank, name, h, n, notes in sorted(entries, key=lambda e: e[0]):
            canonical = aliases.get(norm(name), name)
            key = norm(canonical)
            u = universities.setdefault(key, {"id": slug(canonical), "name_en": canonical, "listings": []})
            u["listings"].append({"track": track, "field": fid, "rank": rank, "pdf_page": n, "flag": flags[h], **notes})

    # Country = the flag the guide shows most often for that university. Where a page shows a
    # different flag, the mismatch is kept on record instead of silently picking one.
    for u in universities.values():
        counts = {}
        for listing in u["listings"]:
            counts[listing["flag"]] = counts.get(listing["flag"], 0) + 1
        u["country"] = max(counts, key=counts.get)
        u["flag_mismatches"] = [{"pdf_page": l["pdf_page"], "flag": l["flag"]}
                                for l in u["listings"] if l["flag"] != u["country"]]
        for listing in u["listings"]:
            del listing["flag"]
        fix = overrides.get("_country", {}).get(u["name_en"])
        if fix:
            u["country"] = fix["country"]
            u["country_note"] = fix["note"]
        for m in u["flag_mismatches"]:
            print(f"  note: {u['name_en']} shows the {m['flag']} flag on p{m['pdf_page']}, {u['country']} elsewhere")

    ids = [u["id"] for u in universities.values()]
    if len(ids) != len(set(ids)):
        raise SystemExit("Duplicate university ids")

    for f in fields.values():
        f["name_en"] = FIELD_NAMES_EN[f["id"]]

    data = {
        "source": SOURCE,
        "fields": sorted(fields.values(), key=lambda f: (f["track"], min(f["list_pages"] or [999]))),
        "universities": sorted(universities.values(), key=lambda u: u["name_en"].lower()),
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    counts = {k: len(v) for k, v in lists.items()}
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(universities)} universities, {len(fields)} fields")
    for (track, fid), c in sorted(counts.items(), key=lambda kv: (kv[0][0], str(kv[0][1]))):
        print(f"  {track:8} {str(fid):18} {c} ranked")


if __name__ == "__main__":
    main()
