"""The universities explorer: the extracted official lists, the search, and the pages."""

import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.content import SLUG_PATTERN
from app.universities import SAT_POLICY_AR, normalize

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


def test_filter_by_sdaia_targets():
    """A student into AI can keep only universities that are on SDAIA's list too."""
    r = ex.search(q="الذكاء الاصطناعي", target="sdaia-ai-scholarship")
    ids = ex.target_programs["sdaia-ai-scholarship"]["ids"]
    rows = [u for s in r["sections"] for _, u in s.get("rows", [])]
    assert rows and all(u["id"] in ids for u in rows)
    assert ex.search(target="not-a-program")["target"] == ""
    html = client.get("/universities?target=sdaia-ai-scholarship").text
    assert 'value="sdaia-ai-scholarship" selected' in html

