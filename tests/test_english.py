"""The English version of the site (decision 066).

The owner doesn't read the English, so these tests are the guard rails:
- every Arabic text on an English page has English, and the English adds or drops no number, date, link or Latin name;
- a translation whose Arabic changed stops matching, so it can't be shown stale;
- every English page is fully English (Arabic only inside lang="ar"), left to right, and keeps readers in /en.
"""

import json
import re
from functools import cache
from pathlib import Path

import frontmatter
import pytest
from fastapi.testclient import TestClient

import app.main as main
from app import i18n
from app.content import CONTENT_DIR, EN_DIR, list_slugs, source_hash
from scripts.english_leaks import arabic_outside_lang_ar, english_urls

client = TestClient(main.app)
ROOT = Path(__file__).resolve().parent.parent
I18N = ROOT / "data" / "i18n"
AR = re.compile(r"[؀-ۿ]")
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def translations(name=None):
    files = [I18N / f"{name}.en.json"] if name else sorted(I18N.glob("*.en.json"))
    out = {}
    for path in files:
        out.update(json.loads(path.read_text(encoding="utf-8")))
    return out


# ---------- the translation files ----------

def test_translation_files_are_valid_and_english():
    for path in sorted(I18N.glob("*.en.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data, path.name
        for ar, en in data.items():
            assert AR.search(ar) or set(ar) <= set("«»→ .؟،") or path.name == "js.en.json", f"{path.name}: key without Arabic: {ar!r}"
            assert isinstance(en, str) and en.strip(), f"{path.name}: empty English for {ar!r}"
            assert not AR.search(en), f"{path.name}: Arabic left in the English for {ar!r}: {en!r}"
            assert "«" not in en and "»" not in en, f"{path.name}: Arabic quotes in {en!r}"


def test_a_key_has_one_english_across_files():
    seen = {}
    for path in sorted(I18N.glob("*.en.json")):
        for ar, en in json.loads(path.read_text(encoding="utf-8")).items():
            assert seen.setdefault(ar, (en, path.name))[0] == en, f"{ar!r}: {path.name} and {seen[ar][1]} disagree"


@cache
def all_data_strings():
    """Every string in data/ and content/ (Arabic files), to find keys nothing uses any more."""
    found = set()

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str):
            found.add(o)

    for path in (ROOT / "data").rglob("*.json"):
        if "i18n" not in path.parts:
            walk(json.loads(path.read_text(encoding="utf-8")))
    for path in CONTENT_DIR.glob("[!e]*/*.md"):
        walk(frontmatter.load(path).metadata)
    return found


@cache
def app_source():
    parts = [p.read_text(encoding="utf-8") for p in (ROOT / "app").rglob("*") if p.suffix in (".py", ".html", ".js")]
    return "\n".join(parts)


def test_no_unused_translations():
    """A translation nothing shows is a sign the Arabic changed: retranslate it, then delete the old key."""
    data = all_data_strings()
    source = app_source()
    unused = []
    for name in ("data", "universities", "content"):
        unused += [k for k in translations(name) if k not in data]
    unused += [k for k in translations("ui") if k not in source and k not in data]
    js = (ROOT / "app" / "static").glob("*.js")
    js_source = "\n".join(p.read_text(encoding="utf-8") for p in js)
    built = {"التبديل إلى الوضع الفاتح", "التبديل إلى الوضع الداكن"}  # theme.js builds these two from «ال» + فاتح/داكن
    unused += [k for k in translations("js") if k not in js_source and k not in built]
    assert not unused, f"{len(unused)} unused translations, e.g. {unused[:5]}"


def test_every_shown_university_and_data_text_has_english():
    """University requirement files and the shared data: every Arabic text a page can show has English.
    Fields that are never shown (sources' quotes, notes for the owner, search aliases) are skipped, and so are names
    whose English comes from the data itself (name_ar; majors_ar, checked in test_exploration's English test)."""
    known = translations()
    skip_keys = {"quote", "aliases", "evidence", "note_for_owner", "_note", "note", "status_note", "apply_url_note",
                 "apply_note", "institution_note", "name_ar", "majors_ar"}
    missing = []

    def walk(o, key=None):
        if isinstance(o, dict):
            for k, v in o.items():
                if k not in skip_keys:
                    walk(v, k)
        elif isinstance(o, list):
            for v in o:
                walk(v, key)
        elif isinstance(o, str) and AR.search(o) and o not in known:
            missing.append((key, o))

    for path in sorted((ROOT / "data" / "university_details").glob("*.json")):
        walk(json.loads(path.read_text(encoding="utf-8")))
    for name in ("paths", "home", "site", "test_needs", "apply_year", "school_tracks", "waaid_programs", "news", "exploration"):
        walk(json.loads((ROOT / "data" / f"{name}.json").read_text(encoding="utf-8")))
    assert not missing, f"{len(missing)} texts without English, e.g. {missing[:5]}"


# ---------- facts survive translation ----------

NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
URL = re.compile(r"https?://[^\s)\"'»”]+|[\w.+-]+@[\w-]+\.[\w.]+")
LATIN = re.compile(r"[A-Za-z][A-Za-z0-9&+'’.-]*[A-Za-z0-9+]|[A-Za-z]")
# Arabic words for numbers that English writes with digits (12 شهرًا is already a digit; سنتان isn't).
NUMBER_WORDS = {
    "1": ("واحد", "سنة واحدة", "مرة", "سنة", "الأول", "الأولى", "أول"),
    "2": ("سنتان", "سنتين", "يومين", "مقالين", "اثنين", "مهارتين", "ثاني", "الثانية", "الثاني"),
    "3": ("ثلاث", "الثالث", "ثالث"), "4": ("أربع",), "5": ("خمس",), "7": ("سبع", "السابع"), "8": ("ثماني",),
    "10": ("أول",), "11": ("ثاني",), "12": ("ثالث", "الثاني عشر"), "30": ("الثلاثون", "الثلاثين"),
}


def numbers(text):
    text = text.translate(ARABIC_DIGITS).replace("‏", "").replace("‎", "")
    text = URL.sub(" ", text)
    return {n.rstrip(".,") for n in NUMBER.findall(text)}


def fact_problems(ar, en):
    problems = []
    if sorted(re.findall(r"\{(\w+)\}", ar)) != sorted(re.findall(r"\{(\w+)\}", en)):
        problems.append("placeholders differ")
    if "{" in ar:  # placeholders are filled later, from data
        ar, en = re.sub(r"\{\w+\}", "", ar), re.sub(r"\{\w+\}", "", en)
    a, e = numbers(ar), numbers(en)
    dropped = a - e
    added = {n for n in e - a if not any(w in ar for w in NUMBER_WORDS.get(n, ()))}
    if dropped:
        problems.append(f"numbers dropped {sorted(dropped)}")
    if added:
        problems.append(f"numbers added {sorted(added)}")
    if set(URL.findall(ar)) - set(URL.findall(en)):
        problems.append("link dropped")
    latin_ar = {w for w in LATIN.findall(URL.sub(" ", ar)) if len(w) > 1}
    flat = en.replace("’", "'").lower()
    missing = {w for w in latin_ar if w.replace("’", "'").lower() not in flat}
    if missing:
        problems.append(f"Latin names dropped {sorted(missing)}")
    return problems


def test_translations_keep_every_number_link_and_latin_name():
    bad = []
    for name in ("ui", "data", "content", "universities", "js"):
        for ar, en in translations(name).items():
            problems = fact_problems(ar, en)
            if problems:
                bad.append(f"{name}: {ar[:70]!r} -> {problems}")
    assert not bad, f"{len(bad)} translations change a fact:\n" + "\n".join(bad[:15])


def test_minimum_and_recommended_stay_apart():
    """«الحد الأدنى» is a cut-off and «الموصى به» isn't (decision 058): the English must keep the same word."""
    bad = []
    for ar, en in translations().items():
        low = en.lower()
        if "الحد الأدنى" in ar and "minimum" not in low and "lowest" not in low:
            bad.append(ar)
        if re.search(r"الموصى بها?|موصى بها?", ar) and "recommend" not in low:
            bad.append(ar)
        if "recommend" in low and not re.search(r"موص|ينصح|تنصح|نصيحة|نوصي|ننصح|يوصى|توصي|يُنصح|توصية|ينصح|يُوصى", ar):
            bad.append(ar)
    assert not bad, bad[:10]


def test_not_listed_is_never_translated_as_not_accepted():
    """«ليس ضمن الاختبارات التي تذكرها» / «لا تذكر» mean the page doesn't list it, not that it refuses it (decision 061)."""
    bad = [ar for ar, en in translations().items()
           if re.search(r"لا تذكر|لا يذكر|غير مذكور|ليس ضمن|لم تذكر", ar) and not re.search(r"يُقبل|مقبول|تقبل|لا يقبل", ar)
           and re.search(r"not accepted|doesn't accept|does not accept|rejects", en, re.I)]
    assert not bad, bad[:10]


def test_glossary_terms():
    t = translations()
    assert t["خطتي"] == "My plan"
    assert t["الأدلة"] == "Guides"
    assert t["واضح"] == "Wadih"
    assert t["لا يُقبل لإثبات اللغة"] == "Not accepted as proof of English"
    assert t["ليس ضمن الاختبارات التي تذكرها الجامعة"] == "Not among the tests the university lists"
    assert t["لم نتحقق منه"] == "Not verified by us"
    assert t["لا يوجد حد أدنى منشور"] == "No published minimum"
    assert t["مفتوح الآن"] == "Open now"
    assert t["لم يفتح بعد"] == "Not open yet"
    for ar, grade in (("أول ثانوي", "Grade 10"), ("ثاني ثانوي", "Grade 11"), ("ثالث ثانوي", "Grade 12")):
        assert t[ar] == grade
    # Names stay spelled one way (paths.json name_en), never a second transliteration.
    for en in t.values():
        assert not re.search(r"Al-?Rowad|Rowad|Ruwad|Wa'?ed\b|Waed\b|Imdad", en), en
    # Formal tone: no slang or exclamation marks in what we wrote.
    for en in t.values():
        assert "!" not in en and not re.search(r"\b(gonna|wanna|kinda|guys)\b", en, re.I), en


# ---------- pages written in Markdown ----------

ENGLISH_KEYS = {"translated_from", "title", "description", "stage_ar", "activity", "resources", "next_step",
                "ready", "admission_types", "start"}


@pytest.mark.parametrize("section", ["grades", "programs", "resources"])
def test_every_page_has_a_current_english_file(section):
    for slug in list_slugs(section):
        path = EN_DIR / section / f"{slug}.md"
        assert path.is_file(), f"no English page for {section}/{slug}"
        en = frontmatter.load(path)
        assert en.metadata.get("translated_from") == source_hash(section, slug), \
            f"{section}/{slug}: the Arabic page changed since it was translated; update the English, then translated_from"
        assert set(en.metadata) <= ENGLISH_KEYS, f"{section}/{slug}: only translated keys belong here"


def test_english_pages_keep_facts_links_and_anchors():
    for path in sorted(EN_DIR.glob("*/*.md")):
        ar = (CONTENT_DIR / path.parent.name / path.name).read_text(encoding="utf-8")
        en = path.read_text(encoding="utf-8")
        ar_body, en_body = ar.split("\n---\n", 1)[1], en.split("\n---\n", 1)[1]
        assert re.findall(r"\{#[\w-]+\}", ar_body) == re.findall(r"\{#[\w-]+\}", en_body), path
        links = lambda t: sorted(re.findall(r"\]\(([^)]+)\)", t))  # noqa: E731
        assert links(ar_body) == links(en_body), path
        assert not AR.search(en), f"{path}: Arabic left"
        assert "«" not in en, path
        problems = fact_problems(ar_body, en_body)
        assert not problems, f"{path}: {problems}"
        ar_meta, en_meta = frontmatter.loads(ar).metadata, frontmatter.loads(en).metadata
        for key in ("activity", "resources"):
            if key in ar_meta:
                urls = lambda m: sorted(re.findall(r"'(?:url|href)': '([^']+)'", str(m.get(key))))  # noqa: E731
                assert urls(ar_meta) == urls(en_meta), f"{path}: {key} links differ"


# ---------- every English page ----------

@cache
def english_pages():
    return {url: client.get(url) for url in english_urls(client)}


def test_english_pages_load():
    for url, r in english_pages().items():
        expected = 404 if url in ("/en/nope-404", "/en/grades/nope") else 200
        assert r.status_code == expected, url


def test_english_pages_are_english_and_left_to_right():
    leaks = {}
    for url, r in english_pages().items():
        if "partial=1" not in url:
            assert '<html lang="en" dir="ltr"' in r.text, url
        for text in arabic_outside_lang_ar(r.text):
            leaks.setdefault(text, url)
    assert not leaks, f"{len(leaks)} Arabic texts on English pages, e.g. {list(leaks.items())[:8]}"


def test_english_pages_link_within_english():
    for url, r in english_pages().items():
        for href in re.findall(r'(?:href|action)="(/[^"]*)"', r.text):
            assert not href.startswith("//"), f"{url}: protocol-relative link {href}"
            if href.startswith(("/static/", "/en/")) or href == "/en":
                continue
            assert 'data-lang-switch' in r.text and href in r.text, url
            # the only Arabic link is the language switch back to the same page
            assert re.search(rf'data-lang-switch href="{re.escape(href)}"', r.text), f"{url} links to Arabic {href}"


def test_english_anchors_exist():
    """A link to /en/page#id lands on an element with that id."""
    ids = {}
    for url, r in english_pages().items():
        ids[url] = set(re.findall(r'id="([^"]+)"', r.text))
    for url, r in english_pages().items():
        for path, anchor in re.findall(r'href="(/en[^"#?]*)#([^"]+)"', r.text):
            path = path if path != "/en/" else "/en/"
            target = ids.get(path) or set(re.findall(r'id="([^"]+)"', client.get(path).text))
            assert anchor in target, f"{url}: {path}#{anchor} has no target"
        for anchor in re.findall(r'href="#([^"]+)"', r.text):
            assert anchor in ids[url], f"{url}: #{anchor}"


def test_english_switch_points_to_the_same_page():
    r = client.get("/en/universities?track=emdad")
    assert 'data-lang-switch href="/universities?track=emdad"' in r.text
    assert '<a class="lang-toggle" href="/en/universities?track=emdad"' in client.get("/universities?track=emdad").text


def test_english_redirects_stay_in_english():
    r = client.get("/en/", follow_redirects=False)
    assert r.status_code == 200
    # The old Render address redirects to the same English page on the public one.
    r = client.get("/en/about?x=1", headers={"host": "wadih-mqni.onrender.com"}, follow_redirects=False)
    assert r.status_code == 301 and r.headers["location"] == main.site["base_url"] + "/en/about?x=1"


def test_language_switch_never_leaves_the_site():
    r = client.get("/en//example.com")
    assert r.status_code == 404
    assert 'href="//' not in r.text


def test_english_api_and_search():
    data = client.get("/en/api/suggestions").json()
    assert not AR.search(json.dumps(data, ensure_ascii=False))
    results = client.get("/en/api/search?q=ielts").json()["results"]
    assert results and all(r["url"].startswith("/en/") for r in results)
    assert not AR.search(json.dumps(results, ensure_ascii=False))
    # The Arabic API is unchanged.
    assert all(not r["url"].startswith("/en") for r in client.get("/api/search?q=ielts").json()["results"])


def test_english_pages_say_the_english_is_a_translation():
    about = english_pages()["/en/about"].text
    assert "our translation" in about
    assert "our translation" in english_pages()["/en/"].text  # the footer line on every page


def test_drafts_and_third_parties_stay_out_of_english_pages():
    assert not main.SHOW_DRAFTS
    for url, r in english_pages().items():
        for tag in re.findall(r'<(?:script|link|img|iframe)\b[^>]*>', r.text):
            if 'rel="canonical"' in tag or 'rel="alternate"' in tag:
                continue
            assert not re.search(r'(?:src|href)="https?://(?!testserver/)', tag), f"{url}: {tag}"


def test_english_dates_and_counts():
    with i18n.use_lang("en"):
        assert main.arabic_date("2026-10-09") == "9 October 2026"
    n, countries = len(main.explorer.universities), len(main.explorer.country_options())
    assert f"{n} universities in {countries} countries" in english_pages()["/en/"].text
