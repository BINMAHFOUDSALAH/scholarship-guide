"""The universities explorer: the extracted official lists, the search, and the pages."""

import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.content import SLUG_PATTERN
from app.universities import SAT_POLICY_AR, TRACKS, normalize

client = TestClient(main.app)
ex = main.explorer
DATA = Path(main.DATA_DIR)
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
GAPS = json.loads((DATA.parent / "scripts" / "list_overrides.json").read_text(encoding="utf-8"))["_gaps"]


# ---------- the extracted official lists ----------

def test_source_is_the_official_guide():
    assert ex.source["url"].startswith("https://object.moe.gov.sa/")
    assert ex.source["academic_year"] == "2026-2027"


def test_arruaad_list_has_exactly_30_ranked_1_to_30():
    ranks = [l["rank"] for l, _ in ex.listings("arruaad")]
    assert ranks == list(range(1, 31))


def test_every_list_is_ranked_without_gaps_except_the_documented_ones():
    for (track, fid) in ex.fields:
        ranks = [l["rank"] for l, _ in ex.listings(track, fid)]
        known = set(GAPS.get(f"{track}:{fid}", {}).get("missing", []))
        assert ranks == [r for r in range(1, max(ranks) + 1) if r not in known], (track, fid)


def test_every_university_has_a_safe_id_a_known_country_and_listings():
    for uid, u in ex.universities.items():
        assert SLUG_PATTERN.match(uid), uid
        assert u["country"] in ex.countries, uid
        assert u["listings"], uid


def test_every_field_has_names_and_majors_have_names():
    for (track, fid), f in ex.fields.items():
        assert f["name_ar"] and f["name_en"], (track, fid)
        assert f["list_pages"], (track, fid)
        for m in f["majors"]:
            assert m["name_ar"] and m["name_en"], (track, fid, m)


def test_masters_only_and_special_notes_were_kept():
    """The guide's notes change what a high school student can do, so they must survive extraction."""
    law = [m for m in ex.field("emdad", "business-law")["majors"] if m["name_en"] == "Law"]
    assert law and law[0]["masters_only"]
    gallaudet = ex.universities["gallaudet-university"]
    assert all(l.get("hearing_impaired_only") for l in gallaudet["listings"])
    digipen = ex.universities["digipen-institute-of-technology"]
    assert any(l.get("bachelors_only_majors") for l in digipen["listings"])


def test_every_university_has_an_arabic_name():
    names = json.loads((DATA / "university_names_ar.json").read_text(encoding="utf-8"))
    for uid, u in ex.universities.items():
        assert names.get(uid), f"missing Arabic name: {uid}"
        assert re.search(r"[؀-ۿ]", names[uid]), uid


def test_countries_say_whether_english_is_official():
    for code, c in ex.countries.items():
        assert c["name_ar"]
        assert isinstance(c["english"], bool)
        assert c["source_url"].startswith("https://sites.moe.gov.sa/scholarship-program/countries/")


# ---------- researched requirements ----------

DETAIL_FILES = sorted((DATA / "university_details").glob("*.json"))


@pytest.mark.parametrize("path", DETAIL_FILES, ids=[p.stem for p in DETAIL_FILES])
def test_requirement_files_follow_the_schema(path):
    d = json.loads(path.read_text(encoding="utf-8"))
    assert d["id"] == path.stem and d["id"] in ex.universities
    assert ISO_DATE.match(d["checked"])

    def sourced(item):
        if item is None:
            return
        assert str(item.get("source_url", "")).startswith("https://"), (path.stem, item)

    sourced(d.get("platform"))
    for key in ("ielts", "toefl_ibt", "duolingo"):
        sourced((d.get("english") or {}).get(key))
    if d.get("sat_act"):
        assert d["sat_act"]["policy"] in SAT_POLICY_AR, path.stem
    for date in d.get("dates") or []:
        sourced(date)
        assert date["date"] is None or ISO_DATE.match(date["date"]), (path.stem, date)
        # Structured, not free text (decision 038): what happens, for which intake, and whether
        # the official page states the year.
        assert date["event_ar"] and date["cycle_ar"], (path.stem, date)
        assert isinstance(date["year_stated"], bool), (path.stem, date)
        assert "label_ar" not in date, (path.stem, date)
    sourced(d.get("acceptance_rate"))
    assert d.get("admissions_url") is None or d["admissions_url"].startswith("https://")


# ---------- search ----------

def test_search_by_major_shows_arruaad_then_the_emdad_field_by_rank():
    r = ex.search(q="هندسة البرمجيات")
    assert r["mode"] == "major"
    tracks = [s["track"] for s in r["sections"]]
    assert tracks[0] == "arruaad" and "emdad" in tracks
    emdad = [s for s in r["sections"] if s["track"] == "emdad"][0]
    assert emdad["field"]["id"] == "ict"
    ranks = [l["rank"] for l, _ in emdad["rows"]]
    assert ranks == sorted(ranks)


def test_search_tolerates_arabic_letter_variants_and_english():
    assert ex.search(q="الذكاء الاصطناعى")["mode"] == "major"  # ى instead of ي
    assert ex.search(q="artificial intelligence")["mode"] == "major"
    assert normalize("أإآة") == normalize("ااAه".replace("A", "ا"))


def test_search_by_university_name():
    r = ex.search(q="stanford")
    assert r["mode"] == "name"
    assert [u["id"] for u in r["sections"][0]["universities"]] == ["stanford-university"]


def test_filters_by_country_and_language():
    r = ex.search(track="arruaad", country="GB")
    assert {u["country"] for _, u in r["sections"][0]["rows"]} == {"GB"}
    r = ex.search(track="arruaad", language="other")
    assert all(not u["country_info"]["english"] for _, u in r["sections"][0]["rows"])
    assert r["sections"][0]["rows"]


def test_doctorate_lists_only_when_asked():
    tracks = [s["track"] for s in ex.search(q="الذكاء الاصطناعي")["sections"]]
    assert "rnd" not in tracks
    tracks = [s["track"] for s in ex.search(q="الذكاء الاصطناعي", track="rnd")["sections"]]
    assert tracks == ["rnd"]


# ---------- pages ----------

@pytest.mark.parametrize("url", ["/universities", "/universities?q=stanford", "/universities?track=emdad&field=ict",
                                 "/universities/harvard-university", "/universities/tsinghua-university"])
def test_explorer_pages_load(url):
    assert client.get(url).status_code == 200


@pytest.mark.parametrize("uid", ["nope", "Harvard-University", "..%2F..%2F.env"])
def test_unknown_university_is_404(uid):
    assert client.get(f"/universities/{uid}").status_code == 404


def test_partial_results_are_just_the_results():
    html = client.get("/universities?q=stanford&partial=1").text
    assert "<html" not in html and "stanford-university" in html


def test_non_english_country_links_to_the_language_exception():
    html = client.get("/universities/tsinghua-university").text
    assert "/programs/custodian-scholarship" in html
    assert "مشروطًا بدراسة لغتها" in html


def test_api_and_sitemap_and_nav():
    data = client.get("/api/universities").json()
    assert len(data["universities"]) == len(ex.universities)
    sitemap = client.get("/sitemap.xml").text
    assert f"<loc>{main.site['base_url']}/universities/harvard-university</loc>" in sitemap
    header = client.get("/").text.split("</header>")[0]
    assert header.count(">الجامعات</a>") == 2


def test_explorer_loads_nothing_from_third_parties():
    html = client.get("/universities").text
    for url in re.findall(r'<(?:script|link)[^>]+(?:src|href)="([^"]+)"', html.split("</head>")[0] + html.split("<footer")[-1]):
        assert url.startswith("http://testserver/") or url.startswith("https://wadih"), url


@pytest.mark.parametrize("path", DETAIL_FILES, ids=[p.stem for p in DETAIL_FILES])
def test_every_researched_university_page_renders(path):
    html = client.get(f"/universities/{path.stem}").text
    assert "متطلبات القبول في الجامعة" in html
    assert "لم نجمع متطلبات هذه الجامعة بعد" not in html


def test_next_deadline_skips_past_dates():
    uid = next(iter(ex.details))
    dated = sorted(d["date"] for d in ex.details[uid]["dates"] if d.get("date"))
    if not dated:
        pytest.skip("no dated items")
    assert ex.next_deadline(uid, today="2000-01-01")["date"] == dated[0]
    assert ex.next_deadline(uid, today="2999-01-01") is None


def test_waaid_track_lists_its_programs():
    r = ex.search(track="waaid")
    assert r["mode"] == "waaid"
    programs = r["sections"][0]["waaid"]
    assert programs and all("is_open" in p for p in programs)
    html = client.get("/universities?track=waaid").text
    head = html.split('class="result-head"')[1].split("</header>")[0]
    assert f"{len(programs)} برنامج" in head and programs[0]["program_ar"] not in head
    assert programs[0]["program_ar"] in html


def test_major_search_also_shows_matching_waaid_programs():
    r = ex.search(q="الهندسة الكهربائية")
    waaid = [s for s in r["sections"] if s["track"] == "waaid"]
    assert waaid and any("معادن" in p["company_ar"] for p in waaid[0]["waaid"])
    mines = [p for p in waaid[0]["waaid"] if p["institution"] == "Colorado School of Mines"]
    assert mines and mines[0]["university_id"] == "colorado-school-of-mines"


def test_suggestions_group_majors_by_field():
    data = client.get("/api/suggestions").json()
    titles = [g["title_ar"] for g in data["fields"]]
    assert "تقنية الاتصالات والمعلومات" in titles
    ict = [g for g in data["fields"] if g["title_ar"] == "تقنية الاتصالات والمعلومات"][0]
    assert any(m["name_ar"] == "الذكاء الاصطناعي" for m in ict["majors"])
    assert len(data["universities"]) == len(ex.universities)


def test_university_page_shows_every_field_with_rank_and_majors():
    html = client.get("/universities/university-of-wisconsin-madison").text
    assert html.count('class="field-block"') == len(ex.universities["university-of-wisconsin-madison"]["listings"])
    assert "زراعة المناطق الجافة" in html  # a major of the agriculture field, visible without clicking
    assert "<details>" not in html.split('class="field-blocks"')[1].split('class="field-src"')[0]


def test_no_target_filter_or_fineprint_on_the_explorer():
    html = client.get("/universities").text
    assert "برامج إضافية" not in html and "مستهدفة في" not in html
    assert "ترجمتنا للتسهيل" not in html



# ---------- explorer redesign (decision 035) ----------

def test_arabic_counting():
    from app.universities import PROGRAMS_AR, UNIVERSITIES_AR, count_ar
    assert count_ar(1, UNIVERSITIES_AR) == "جامعة واحدة"
    assert count_ar(2, UNIVERSITIES_AR) == "جامعتان"
    assert count_ar(5, UNIVERSITIES_AR) == "5 جامعات"
    assert count_ar(30, UNIVERSITIES_AR) == "30 جامعة"
    assert count_ar(11, PROGRAMS_AR) == "11 برنامجًا"
    assert count_ar(200, PROGRAMS_AR) == "200 برنامج"
    assert count_ar(103, UNIVERSITIES_AR) == "103 جامعات"


def test_applied_filters_each_have_a_remove_link():
    view = ex.describe(ex.search(q="الذكاء الاصطناعي", track="emdad", field="ict", country="GB", language="english"))
    labels = [a["label_ar"] for a in view["applied"]]
    assert labels == ["التخصص", "المسار", "المجال", "الدولة", "لغة الدولة"]
    track = view["applied"][1]
    assert "track=" not in track["href"] and "field=" not in track["href"]  # the field goes with its track
    assert "country=GB" in track["href"]
    country = view["applied"][3]
    assert "country=" not in country["href"] and "track=emdad" in country["href"]
    assert ex.describe(ex.search())["applied"] == []


def test_explorer_page_shows_applied_tags_clear_all_and_a_summary():
    html = client.get("/universities?track=emdad&field=ict&country=CN").text
    assert html.count('class="applied-chip"') == 3
    assert 'class="applied-clear" href="http://testserver/universities"' in html
    assert 'data-summary="مسار إمداد (تقنية الاتصالات والمعلومات): 17 جامعة"' in html
    assert 'role="status"' in html
    assert 'aria-live="polite"' not in html.split('id="results"')[1]  # the big region is not live
    assert "وليس تصنيفًا عالميًا" in html  # what the rank means
    assert "/programs/custodian-scholarship#conditional" in html  # non-English countries in the list
    assert "<bdi>" in html  # filter values are isolated from the Arabic sentence


def test_no_filter_tags_and_no_clear_all_by_default():
    html = client.get("/universities").text
    assert 'class="applied-chip"' not in html and 'class="applied-clear"' not in html


def test_result_links_carry_the_search_back():
    html = client.get("/universities?q=stanford").text
    assert "/universities/stanford-university?from=q%3Dstanford" in html


@pytest.mark.parametrize("raw, expected", [
    ("q=AI&track=emdad&field=ict", "/universities?q=AI&track=emdad&field=ict"),
    ("track=arruaad&field=ict", "/universities?track=arruaad"),       # a field only belongs to إمداد / R&D
    ("country=ZZ&lang=klingon&evil=1", "/universities"),               # unknown values are dropped
    ("//evil.example/path", "/universities"),                          # never another site
    ("", "/universities"),
])
def test_back_url_keeps_only_known_search_params(raw, expected):
    assert ex.back_url(raw) == expected


def test_university_page_links_back_to_the_search():
    html = client.get("/universities/stanford-university?from=q%3Dstanford%26country%3DUS").text
    assert 'href="/universities?q=stanford&amp;country=US"' in html
    plain = client.get("/universities/stanford-university").text
    assert 'href="/universities?' not in plain


def test_a_field_without_a_track_means_emdad():
    r = ex.search(field="ict")
    assert r["track"] == "emdad" and r["sections"][0]["field"]["id"] == "ict"


def test_suggestions_name_the_country():
    data = client.get("/api/suggestions").json()
    stanford = [u for u in data["universities"] if u["id"] == "stanford-university"][0]
    assert stanford["country_ar"] == "الولايات المتحدة الأمريكية"


def test_suggestion_search_keeps_arabic_letters():
    """The browser's normalize() removes marks only. Its character class once ran U+0300–064B by a
    typo (invisible combining characters), which removed every Arabic letter, so Arabic typing never
    filtered the suggestions. It's written with \\u escapes now; this keeps it that way."""
    js = (main.APP_DIR / "static" / "universities.js").read_text(encoding="utf-8")
    line = [l for l in js.splitlines() if '.normalize("NFKD")' in l][0]
    bs = chr(92)  # a backslash, spelled out so no tool can turn the escapes into real marks
    expected = "[" + bs + "u0300-" + bs + "u036f" + bs + "u064b-" + bs + "u0652" + bs + "u0640]"
    assert expected in line
    assert not any(0x0300 <= ord(ch) <= 0x036F or 0x064B <= ord(ch) <= 0x0652 for ch in line)


# ---------- university page + «قائمتي» (decision 035) ----------

def test_university_page_answers_first():
    html = client.get("/universities/stanford-university").text
    summary = html.split('id="summary-title"')[1].split("</section>")[0]
    assert "قوائم الابتعاث" in summary and "التخصصات" in summary
    assert "أقرب موعد في الجامعة" in summary and "SAT / ACT" in summary and "IELTS" in summary
    assert "لا يعني قبولك فيها" in summary  # being on a list is not admission
    assert "/programs/custodian-scholarship#admission-vs-scholarship" in summary
    assert html.index('id="summary-title"') < html.index('id="lists-title"') < html.index('id="req-title"')
    assert 'id="dates-title"' in html


def test_scholarship_dates_are_separate_from_university_dates():
    """Decision 038: the scholarship's window and the university's dates, as two labelled blocks."""
    html = client.get("/universities/stanford-university").text
    dates = html.split('id="dates-title"')[1].split("</section>")[0]
    scholarship = dates.index("موعد التقديم على الابتعاث")
    university = dates.index("مواعيد التقديم على الجامعة")
    assert scholarship < university
    assert "مسار الرواد" in dates[scholarship:university]  # Stanford is in الرواد
    assert "بعد</strong> أن يصلك قبول الجامعة" in dates
    # University dates: event, round and intake in words; the year flag when the page omits the year.
    assert "Restrictive Early Action" in dates and "لخريف 2027" in dates
    assert "السنة غير مذكورة في الصفحة" in dates


def test_reference_only_dates_never_count_as_the_next_deadline():
    for uid, d in ex.details.items():
        nxt = ex.next_deadline(uid, today="2000-01-01")
        assert nxt is None or not nxt.get("reference_only"), uid


def test_doctorate_lists_are_folded_unless_they_are_all_there_is():
    stanford = client.get("/universities/stanford-university").text
    assert '<details class="uni-track rnd-lists">' in stanford
    only_rnd = next(uid for uid, u in ex.universities.items() if all(l["track"] == "rnd" for l in u["listings"]))
    assert '<details class="uni-track rnd-lists" open>' in client.get(f"/universities/{only_rnd}").text


def test_save_buttons_need_javascript_and_the_header_link_is_always_there():
    """Decision 039: «قائمتي» is findable before anything is saved; save buttons appear only with JS."""
    html = client.get("/universities/harvard-university").text
    assert 'data-save="harvard-university" hidden' in html
    assert "data-mylist-link hidden" not in html and "data-mylist-link" in html
    assert 'role="status" data-save-status' in html
    assert "/static/mylist.js" in html


def test_result_rows_can_be_saved_from_the_list():
    for url in ("/universities?track=arruaad", "/universities?q=stanford"):
        html = client.get(url).text
        assert 'class="save-mini" type="button" data-save="stanford-university"' in html, url
        assert "data-pending" in html  # invisible until mylist.js is ready
        assert 'data-save-name="جامعة ستانفورد"' in html or "data-save-name=" in html


def test_my_list_explains_where_the_list_lives_and_when_storage_is_blocked():
    html = client.get("/my-list").text
    assert "لا تنتقل إلى جهاز أو متصفح آخر" in html and "التصفح الخاص" in html
    assert "data-mylist-blocked hidden" in html


def test_my_list_page_is_private_and_not_indexed():
    html = client.get("/my-list").text
    assert '<meta name="robots" content="noindex">' in html
    assert "في هذا المتصفح فقط" in html and "<noscript>" in html
    assert "/my-list" not in client.get("/sitemap.xml").text


def test_my_list_rows_keep_known_ids_in_order():
    html = client.get("/my-list?partial=1&ids=yale-university,nope,../../.env,harvard-university,yale-university").text
    assert re.findall(r'data-mylist-item="([^"]+)"', html) == ["yale-university", "harvard-university"]
    assert "<html" not in html
    assert 'aria-label="إزالة جامعة ييل من قائمتي"' in html  # the visible «إزالة» is in the name (WCAG 2.5.3)
    assert "data-mylist-item" not in client.get("/my-list?partial=1&ids=").text


def test_my_list_rows_are_capped_at_100():
    ids = ",".join(sorted(ex.universities)[:150])
    html = client.get(f"/my-list?partial=1&ids={ids}").text
    assert len(re.findall(r"data-mylist-item=", html)) == 100


# ---------- at a glance (decision 038) ----------

def test_tracks_list_puts_the_doctorate_track_last():
    assert list(TRACKS) == ["arruaad", "emdad", "waaid", "rnd"]
    html = client.get("/universities").text
    select = html.split('id="track"')[1].split("</select>")[0]
    assert select.index('value="waaid"') < select.index('value="rnd"')


def test_language_filter_says_it_is_the_country_language_not_the_teaching_language():
    html = client.get("/universities").text
    assert "لغة الدولة الرسمية" in html and "وليست لغة الدراسة" in html
    assert 'aria-describedby="lang-hint"' in html
    tsinghua = client.get("/universities?q=tsinghua").text
    assert "لغة الدولة: الصينية" in tsinghua


def test_results_show_key_facts_or_say_they_are_not_collected():
    stanford = ex.key_facts("stanford-university", today="2000-01-01")
    assert stanford["researched"] and stanford["sat_ar"] == "مطلوب"
    assert stanford["admissions_url"].startswith("https://")
    unknown = next(uid for uid in ex.universities if uid not in ex.details)
    assert ex.key_facts(unknown) == {"researched": False}
    html = client.get("/universities?track=arruaad").text
    assert "صفحة القبول الرسمية" in html
    emdad = client.get("/universities?track=emdad&field=ict").text
    # Said once for the whole list (decision 041), not repeated on every row.
    assert emdad.count("لم نجمع متطلبات جامعات هذه القائمة") == 1
    assert "لم نجمعها بعد" not in emdad
    assert "لم نجمعها بعد" in client.get("/my-list?partial=1&ids=adelaide-university").text


def test_explorer_says_being_on_a_list_is_not_admission():
    html = client.get("/universities").text
    header = html.split('class="explorer-header"')[1].split("</header>")[0]
    assert "لا يعني قبولك فيها" in header and "#admission-vs-scholarship" in header


def test_saved_list_rows_show_key_facts():
    html = client.get("/my-list?partial=1&ids=stanford-university").text
    assert "SAT/ACT" in html and "صفحة القبول الرسمية" in html


def test_every_requirement_file_belongs_to_a_listed_university():
    """When a new guide drops a university, its researched file must be noticed, not silently ignored."""
    listed = {u["id"] for u in json.loads((Path(__file__).parent.parent / "data" / "universities.json")
                                          .read_text(encoding="utf-8"))["universities"]}
    orphans = [p.stem for p in DETAIL_FILES if p.stem not in listed]
    assert not orphans, f"requirement files for universities no longer in the guide: {orphans}"


# ---------- trust fixes (decision 041) ----------

def test_a_country_without_a_track_shows_every_list_it_is_in():
    """Germany has no الرواد university but 17 in إمداد: never answer «none»."""
    r = ex.search(country="DE")
    assert [s["track"] for s in r["sections"]] == ["emdad"]
    assert len(r["sections"][0]["universities"]) > 0
    us = ex.search(country="US")
    assert [s["track"] for s in us["sections"]] == ["arruaad", "emdad"]
    assert [s["track"] for s in ex.search()["sections"]] == ["arruaad"]  # no filter: الرواد only


def test_a_university_outside_the_filters_is_shown_with_an_explanation():
    r = ex.search(q="stanford", country="GB")
    section = r["sections"][0]
    assert section.get("outside_filters") and [u["id"] for u in section["universities"]] == ["stanford-university"]
    html = client.get("/universities?q=stanford&country=GB").text
    assert "خارج الفلاتر التي اخترتها" in html and "لا توجد جامعة بهذا الاسم" not in html


def test_a_country_typed_in_the_search_box_offers_the_country_filter():
    for q in ("Germany", "ألمانيا", "UK"):
        r = ex.search(q=q)
        assert r["country_match"] in ("DE", "GB"), q
    html = client.get("/universities?q=Germany").text
    assert "هل تقصد الدولة «ألمانيا»" in html and "?country=DE" in html
    assert "لا توجد جامعة بهذا الاسم" not in html


def test_conflicting_country_and_language_filters_say_why():
    html = client.get("/universities?country=GB&lang=other").text
    assert "بريطانيا لغتها الرسمية الإنجليزية" in html


def test_major_search_explains_the_field_list_and_keeps_rawwad_compact():
    r = ex.search(q="هندسة البرمجيات")
    rawwad, emdad = r["sections"][0], [s for s in r["sections"] if s["track"] == "emdad"][0]
    assert rawwad.get("compact") and rawwad["full_href"].startswith("/universities?track=arruaad")
    assert "وليس قائمة بتخصص" in emdad["note_ar"]
    assert "متاحة لتخصصك" not in client.get("/universities?q=" + "هندسة البرمجيات").text


def test_finder_labels_are_plain():
    html = client.get("/universities?lang=other").text
    assert "كل اللغات" in html and "لغة الدولة: <bdi>غير الإنجليزية</bdi>" in html
    assert "<h1>الجامعات في قوائم الابتعاث</h1>" in html
    rows = client.get("/universities?track=arruaad").text
    assert "المتطلبات والمواعيد</th>" in rows and '<span class="sr-only">المرتبة </span>' in rows
    # The save button is not inside the row header cell (a cleaner screen-reader row name).
    th = rows.split('<th scope="row">')[1].split("</th>")[0]
    assert "save-mini" not in th
