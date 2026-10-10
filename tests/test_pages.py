"""Do the pages load, and do they behave the way we promised?"""

import re

import pytest
from fastapi.testclient import TestClient

import app.main as main

client = TestClient(main.app)


def test_home_loads_in_arabic_rtl():
    response = client.get("/")
    assert response.status_code == 200
    assert '<html lang="ar" dir="rtl">' in response.text
    assert main.site["name"] in response.text


def test_home_has_grade_picker_links():
    response = client.get("/")
    for slug in ("grade-10", "grade-11", "grade-12"):
        assert f"/grades/{slug}" in response.text


def test_home_lists_every_path():
    response = client.get("/")
    for path in main.paths:
        assert path["name_ar"] in response.text


def test_home_shows_latest_news():
    response = client.get("/")
    assert "آخر المستجدات" in response.text
    assert main.news[0]["title_ar"] in response.text


def test_theme_toggle_is_present_but_hidden_without_js():
    response = client.get("/")
    assert 'class="theme-toggle" type="button" hidden' in response.text


def test_about_loads():
    assert client.get("/about").status_code == 200


@pytest.mark.parametrize("slug", ["grade-10", "grade-11", "grade-12"])
def test_grade_pages_load(slug):
    response = client.get(f"/grades/{slug}")
    assert response.status_code == 200
    assert 'class="next-step"' in response.text


def test_draft_page_shows_unverified_stamp():
    response = client.get("/grades/grade-10")
    assert "غير مؤكد" in response.text


def test_unknown_page_shows_arabic_404():
    response = client.get("/this-page-does-not-exist")
    assert response.status_code == 404
    assert "الصفحة غير موجودة" in response.text


@pytest.mark.parametrize("slug", ["nope", "GRADE-10", "..%2F..%2F.env"])
def test_bad_grade_slugs_return_404(slug):
    assert client.get(f"/grades/{slug}").status_code == 404


def test_tuwaiq_section_hidden_while_quote_is_draft(monkeypatch):
    monkeypatch.setitem(main.featured_quote, "status", "draft")
    monkeypatch.setattr(main, "SHOW_DRAFTS", False)
    assert 'class="tuwaiq"' not in client.get("/").text


def test_tuwaiq_section_visible_when_drafts_are_shown(monkeypatch):
    monkeypatch.setattr(main, "SHOW_DRAFTS", True)
    assert 'class="tuwaiq"' in client.get("/").text


def test_no_third_party_requests_in_page():
    """Fonts and scripts are self-hosted: everything the page head loads comes from our own server."""
    head = client.get("/").text.split("</head>")[0]
    urls = re.findall(r'(?:src|href)="(https?://[^"]+)"', head)
    assert urls, "expected the head to load at least the stylesheet"
    for url in urls:
        assert url.startswith("http://testserver/"), f"third-party request: {url}"
