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


def test_grade_question_is_hidden_until_start_is_clicked():
    """The grade links live inside a closed <details>, revealed by "ابدأ من هنا"."""
    html = client.get("/").text
    details = html.split('<details class="start">')[1].split("</details>")[0]
    assert "ابدأ من هنا" in details
    assert "في أي صف أنت؟" in details
    assert "/grades/grade-10" in details
    assert '<details class="start" open' not in html


def test_each_path_row_has_its_theme_and_facts():
    html = client.get("/").text
    for path in main.paths:
        assert f'class="path-row theme-{path["theme"]}"' in html
        assert path["provider_ar"] in html
        assert path["audience_ar"] in html


def test_header_nav_on_desktop_and_phone_menu():
    html = client.get("/about").text
    header = html.split("</header>")[0]
    for label in ("حسب صفك", "المسارات", "المستجدات", "عن الدليل"):
        assert header.count(f">{label}</a>") == 2, label  # desktop nav + phone menu
    assert '<details class="menu">' in header


def test_homepage_sections_and_starting_points():
    html = client.get("/").text
    for section_id in ("start", "news", "paths", "journey"):
        assert f'id="{section_id}"' in html
    for item in main.home_text["start"] + main.home_text["journey"]:
        assert item["title_ar"] in html


def test_every_internal_link_on_the_homepage_works():
    """Every internal page link returns 200, and every #anchor points at a real section."""
    html = client.get("/").text
    ids = set(re.findall(r'id="([^"]+)"', html))
    hrefs = set(re.findall(r'href="([^"]+)"', html))
    for href in hrefs:
        if href.startswith(("https://", "mailto:")) and not href.startswith("http://testserver"):
            continue  # external links are checked by hand, not in tests
        path_part, _, anchor = href.replace("http://testserver", "").partition("#")
        if anchor:
            assert anchor in ids, f"missing section #{anchor}"
        if path_part:
            assert client.get(path_part).status_code == 200, href


def test_light_is_the_default_theme():
    """Dark mode only when chosen: no automatic switch from the device setting."""
    head = client.get("/").text.split("</head>")[0]
    assert 'localStorage.getItem("theme") === "dark"' in head
    css = client.get("/static/style.css").text
    assert "prefers-color-scheme" not in css
    assert ':root[data-theme="dark"]' in css


def test_path_photos_load_with_credit():
    html = client.get("/").text
    for path in main.paths:
        photo = path["photo"]
        assert photo["alt_ar"] in html
        assert photo["credit"] in html
        for size in ("500", "960"):
            url = f"/static/{photo['file']}-{size}.jpg"
            assert url in html
            assert client.get(url).status_code == 200, url


def test_share_preview_and_description_tags():
    html = client.get("/grades/grade-10").text
    base = main.site["base_url"]
    assert '<meta name="description"' in html
    assert f'<link rel="canonical" href="{base}/grades/grade-10">' in html
    assert f'<meta property="og:image" content="{base}/static/img/og-image.png">' in html
    assert '<meta property="og:title" content="أول ثانوي | واضح">' in html
    assert client.get("/static/img/og-image.png").status_code == 200


def test_robots_txt_points_to_sitemap():
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert f"Sitemap: {main.site['base_url']}/sitemap.xml" in response.text


def test_sitemap_lists_public_pages():
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")
    base = main.site["base_url"]
    for path in ("/", "/about", "/grades/grade-10", "/grades/grade-11", "/grades/grade-12"):
        assert f"<loc>{base}{path}</loc>" in response.text


def test_no_video_player_is_loaded_before_a_click(monkeypatch):
    """Even with a video set, the page has only a link: no iframe, nothing from YouTube loads."""
    monkeypatch.setattr(main, "SHOW_DRAFTS", True)
    monkeypatch.setitem(main.featured_quote, "youtube_id", "abcdefghijk")
    html = client.get("/").text
    assert "<iframe" not in html
    assert 'data-youtube-id="abcdefghijk"' in html
    assert 'src="https://www.youtube' not in html
    assert "video.js" in html


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
    # Only tags the browser actually downloads (scripts, stylesheets, fonts, icon).
    # Share-preview and canonical tags just describe the page, so they're not checked here.
    script_urls = re.findall(r'<script[^>]+src="([^"]+)"', head)
    link_urls = re.findall(r'<link rel="(?:stylesheet|preload|icon)" href="([^"]+)"', head)
    urls = script_urls + link_urls
    assert urls, "expected the head to load at least the stylesheet"
    for url in urls:
        assert url.startswith("http://testserver/"), f"third-party request: {url}"
