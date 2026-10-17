"""Site search (decision 045): finds published content, never drafts, always with official sources."""

from fastapi.testclient import TestClient

import app.main as main
from app.search import SiteSearch, plain, search_form, snippet

client = TestClient(main.app)


def test_search_form_drops_arabic_prefixes_and_letter_variants():
    assert search_form("المنحة") == search_form("منحه")
    assert search_form("والابتعاث") == search_form("ابتعاث")
    assert search_form("أرامكو") == search_form("ارامكو")
    assert search_form("الى") == "الي"  # short words are kept whole


def test_plain_text_has_no_tags_or_stray_spaces():
    assert plain('<p>مثل القدرات (<a href="x">وزارة التعليم</a>).</p>') == "مثل القدرات (وزارة التعليم)."


def test_finds_a_guide_section_in_arabic_and_english():
    for q in ("آيلتس", "IELTS", "ايلتس"):
        results = main.site_search.search(q)
        assert results and results[0]["url"].startswith("/resources/ielts"), q


def test_test_names_match_in_arabic_and_english():
    """Decision 061: «دولينجو» and «Duolingo» are the same word to search."""
    assert search_form("دولينجو") == search_form("Duolingo") == search_form("الدولينجو")
    assert search_form("التوفل") == search_form("TOEFL")
    for q in ("duolingo", "Duolingo", "دولينجو"):
        urls = [r["url"] for r in main.site_search.search(q)]
        assert urls and urls[0].startswith("/resources/duolingo"), q


def test_search_answers_which_universities_accept_a_test():
    """One computed chunk per English test, from the requirement files (decision 061)."""
    hit = next(r for r in main.site_search.search("Duolingo") if r["url"] == "/resources/duolingo#universities")
    summary = main.explorer.test_summary("duolingo")
    assert str(summary["researched"]) in hit["snippet"] and hit["sources"]


def test_finds_facts_from_data():
    urls = [r["url"] for r in main.site_search.search("SAT")]
    assert "/grades/grade-11#tests-title" in urls
    assert any(r["url"].startswith("/programs/custodian-scholarship#fact-")
               for r in main.site_search.search("مسارات"))


def test_a_section_named_after_the_question_comes_first():
    assert main.site_search.search("القبول المشروط")[0]["url"] == "/programs/custodian-scholarship#conditional"


def test_prefix_matching():
    assert main.site_search.search("تقدي")  # «تقديم», «التقديم»


def test_every_result_has_an_official_source():
    for chunk in main.site_search.chunks:
        assert chunk["sources"], chunk["url"]
        assert all(s["url"].startswith("https://") for s in chunk["sources"]), chunk["url"]


def test_every_result_links_to_a_page_that_loads():
    for page in {c["url"].split("#")[0] for c in main.site_search.chunks}:
        assert client.get(page).status_code == 200, page


def test_hidden_facts_and_drafts_are_not_indexed(monkeypatch):
    import app.search as search
    program = main.paths_by_id["custodian-scholarship"]
    hidden = {"id": "hidden-test", "text_ar": "كلمةسريةللاختبار", "sources": [{"title": "x", "url": "https://x"}],
              "status": "unverified"}
    monkeypatch.setitem(program, "facts", [*program["facts"], hidden])
    real_load = search.load_page
    monkeypatch.setattr(search, "load_page",
                        lambda section, slug: {**real_load(section, slug), "status": "draft"}
                        if slug == "ielts" else real_load(section, slug))
    index = SiteSearch(main.program_slugs(), main.paths_by_id, main.test_needs)
    assert index.search("كلمةسريةللاختبار") == []
    assert not any(c["url"].startswith("/resources/ielts") for c in index.chunks)


def test_odd_queries_are_safe():
    for q in ['"', "AND", "OR NOT", "*", "()", "a" * 500, "؟؟؟"]:
        main.site_search.search(q)  # no FTS5 syntax error
    assert main.site_search.search("   ") == []


def test_snippet_starts_near_the_match():
    text = "كلمة " * 60 + "آيلتس هنا"
    assert "آيلتس" in snippet(text, [search_form("آيلتس")])


def test_kgsp_is_searchable():
    urls = [r["url"] for r in main.site_search.search("كاوست")]
    assert any(u.startswith("/programs/kaust-kgsp") for u in urls)


def test_guide_search_is_linked_from_home_and_404():
    assert '/search">ابحث في الدليل' in client.get("/").text
    assert '/search" role="search"' in client.get("/no-such-page").text


def test_search_page():
    html = client.get("/search?q=آيلتس").text
    assert 'role="search"' in html
    assert 'href="/resources/ielts' in html
    assert "المصدر:" in html
    assert 'name="robots" content="noindex"' in html


def test_search_page_without_results_explains_why():
    html = client.get("/search?q=زرافة").text
    assert "لا نتائج" in html
    assert "ابتعاث" in html


def test_search_page_escapes_the_query():
    html = client.get("/search?q=<script>alert(1)</script>").text
    assert "<script>alert(1)" not in html


def test_search_api():
    data = client.get("/api/search?q=IELTS").json()
    assert data["query"] == "IELTS"
    first = data["results"][0]
    assert set(first) == {"title", "heading", "url", "snippet", "sources"}
    assert client.get("/api/search").json() == {"query": "", "results": []}
