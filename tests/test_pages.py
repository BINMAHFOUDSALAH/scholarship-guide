"""Do the pages load, and do they behave the way we promised?"""

import re

import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.content import load_page

client = TestClient(main.app)
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def test_home_loads_in_arabic_rtl():
    response = client.get("/")
    assert response.status_code == 200
    assert '<html lang="ar" dir="rtl">' in response.text
    assert main.site["name"] in response.text


def test_home_has_grade_picker_links():
    response = client.get("/")
    for slug in ("grade-10", "grade-11", "grade-12"):
        assert f"/grades/{slug}" in response.text


def test_grade_buttons_are_visible_in_the_hero():
    """The grade question is in the hero itself, no click needed; «حسب صفك» points at it."""
    html = client.get("/").text
    hero = html.split('<section class="hero"')[1].split("</section>")[0]
    assert 'id="grades"' in hero
    assert "في أي صف أنت؟" in hero
    for slug in ("grade-10", "grade-11", "grade-12"):
        assert f"/grades/{slug}" in hero
    assert "<details" not in hero


def test_each_path_row_has_its_theme_and_facts():
    html = client.get("/").text
    for path in main.paths:
        assert f'class="path-row theme-{path["theme"]}"' in html
        assert path["provider_ar"] in html
        assert path["audience_ar"] in html


def test_header_nav_on_desktop_and_phone_menu():
    html = client.get("/about").text
    header = html.split("</header>")[0]
    for label in ("حسب صفك", "البرامج", "مواعيد التقديم"):
        assert header.count(f">{label}</a>") == 2, label  # desktop nav + phone menu
    assert ">عن الدليل</a>" not in header  # removed from the menu (owner, 2026-10-12); the footer links to /about
    assert '<details class="menu">' in header


@pytest.mark.parametrize("url, label, value", [
    ("/universities", "الجامعات", "page"),
    ("/universities/stanford-university", "الجامعات", "true"),  # a page inside the section
    ("/news", "مواعيد التقديم", "page"),
    ("/grades/grade-11", "حسب صفك", "true"),
    ("/programs/custodian-scholarship", "البرامج", "true"),
])
def test_nav_marks_where_you_are(url, label, value):
    """Decision 035: the current section is marked in the nav (desktop + phone), and only that one."""
    header = client.get(url).text.split("</header>")[0]
    assert header.count(f'aria-current="{value}">{label}</a>') == 2
    assert header.count("aria-current=") == 2


def test_home_marks_no_nav_item_and_every_page_has_a_skip_link():
    html = client.get("/").text
    assert "aria-current=" not in html.split("</header>")[0]
    for page in ("/", "/universities", "/universities/harvard-university", "/news", "/grades/grade-10"):
        html = client.get(page).text
        assert '<a class="skip-link" href="#main">' in html
        assert '<main id="main" tabindex="-1">' in html


def test_footer_says_we_are_independent_and_links_the_image_credits():
    """The credits on /about must stay reachable (CC BY-SA licences), from every page's footer."""
    footer = client.get("/universities").text.split('<footer class="site-footer">')[1]
    assert "لا يتبع وزارة التعليم" in footer
    assert "/about#credits" in footer and "كيف نتحقق" not in footer
    assert 'id="credits"' in client.get("/about").text


def test_homepage_order():
    """Decision 035: hero (grades, then search) → what's open now → programs.
    The journey, tests, «كيف نعمل», and the decorative drawing are not on the homepage."""
    html = client.get("/").text
    assert html.index('id="grades"') < html.index('class="hero-search"') < html.index('id="open-now"') < html.index('id="programs"')
    for gone in ('id="start"', 'id="journey"', "كيف نعمل", "من أين تبدأ؟", "مجاني وبدون تسجيل", "hero-visual"):
        assert gone not in html


def test_homepage_search_goes_to_the_explorer_with_real_examples():
    html = client.get("/").text
    hero = html.split('<section class="hero"')[1].split("</section>")[0]
    assert 'action="http://testserver/universities"' in hero and 'name="q"' in hero
    assert 'data-suggest="http://testserver/api/suggestions"' in hero
    assert "/universities/stanford-university" in hero  # an example that opens a university
    n = len(main.explorer.universities)
    assert f"{n} جامعة في 15 دولة" in hero


@pytest.mark.parametrize("page", ["/", "/programs/custodian-scholarship", "/grades/grade-10", "/grades/grade-11",
                                  "/grades/grade-12", "/resources/ielts"])
def test_every_internal_link_works(page):
    """Every internal page link returns 200, and every #anchor points at a real section."""
    html = client.get(page).text
    hrefs = set(re.findall(r'href="([^"]+)"', html))
    for href in hrefs:
        if href.startswith(("https://", "mailto:")) and not href.startswith("http://testserver"):
            continue  # external links are checked by hand, not in tests
        path_part, _, anchor = href.replace("http://testserver", "").partition("#")
        target = client.get(path_part or page)
        assert target.status_code == 200, href
        if anchor:
            assert f'id="{anchor}"' in target.text, f"{href}: missing section #{anchor}"


def test_theme_follows_the_device_until_the_student_chooses():
    """Decision 060 (replaces 023): the device's setting until the student picks a theme; their choice wins.
    Set before the page is drawn (no flash); without JavaScript the site is light."""
    head = client.get("/").text.split("</head>")[0]
    assert 'localStorage.getItem("theme")' in head
    assert 'matchMedia("(prefers-color-scheme: dark)")' in head
    js = client.get("/static/theme.js").text
    assert 'localStorage.setItem("theme", theme)' in js  # light is saved too, so it beats a dark device
    css = client.get("/static/style.css").text
    assert "prefers-color-scheme" not in css  # dark comes only from data-theme, so the choice is never overridden
    assert ':root[data-theme="dark"]' in css


def test_path_images_load_and_are_credited_on_about():
    """Photos and logos load on the homepage; their credits live on /about, not on the image."""
    html = client.get("/").text
    about = client.get("/about").text
    assert 'class="photo-credit"' not in html
    for path in main.paths:
        image, ext = (path["logo"], "png") if path.get("logo") else (path["photo"], "jpg")
        if image is None:
            continue  # no image: the drawn scene is shown instead
        assert image["alt_ar"] in html
        for size in ("500", "960"):
            url = f"/static/{image['file']}-{size}.{ext}"
            assert url in html
            assert client.get(url).status_code == 200, url
        if path.get("logo"):
            assert path["logo"]["source_url"] in about
        else:
            assert image["credit"] in about
            assert image["source_url"] in about


def test_share_preview_and_description_tags():
    html = client.get("/grades/grade-10").text
    base = main.site["base_url"]
    assert '<meta name="description"' in html
    assert f'<link rel="canonical" href="{base}/grades/grade-10">' in html
    assert f'<meta property="og:image" content="{base}/static/img/og-image.png">' in html
    assert '<meta property="og:title" content="أول ثانوي: اكتشف واستعد | واضح">' in html
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
    for path in ("/", "/about", "/grades/grade-10", "/grades/grade-11", "/grades/grade-12",
                 "/programs/custodian-scholarship"):
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


def test_home_shows_whats_open_now_and_links_the_full_board():
    """Decision 035: the homepage shows only what's open (soonest deadline first); /news has all three groups."""
    html = client.get("/").text
    section = html.split('id="open-now"')[1].split("</section>")[0]
    assert "مفتوح للتقديم الآن" in section and "/news" in section
    for item in main.status_board()["open"][:4]:
        assert item["title_ar"] in section
    assert "فُتح وأُغلق مؤخرًا" not in html
    news = client.get("/news").text
    for title in ("مفتوح الآن", "مغلق أو لم يفتح بعد", "فُتح وأُغلق مؤخرًا"):
        assert title in news


def test_open_items_say_who_can_apply():
    """«مفتوح الآن» alone read as "apply today" to grade 12 students who can't yet (الرواد needs an admission,
    SDAIA a scholarship), so every open track carries its «لمن» line on the homepage and /news."""
    tracks = [t for p in main.paths for t in p["tracks"] if t.get("for_high_school") is not False]
    for t in tracks:
        if not t.get("latest_programs"):  # واعد: each program has its own conditions
            assert t.get("apply_with_ar"), t.get("id") or t["name_ar"]
    home = client.get("/").text.split('id="open-now"')[1].split("</section>")[0]
    news = client.get("/news").text
    for item in main.status_board()["open"]:
        if item.get("who_ar"):
            assert f"لمن: {item['who_ar']}" in news
    for item in main.status_board()["open"][:4]:
        if item.get("who_ar"):
            assert f"لمن: {item['who_ar']}" in home
    assert "يمكنك التقديم عليه اليوم" not in news


def test_open_window_warns_grade_12_students_on_program_and_university_pages(monkeypatch):
    """The window open now is for students who already hold an admission (audit 2026-10-13)."""
    import datetime

    class Day(datetime.date):
        @classmethod
        def today(cls):
            return cls(2026, 10, 13)  # الرواد open until 15 Nov 2026
    monkeypatch.setattr(main, "date", Day)
    for url in ("/programs/custodian-scholarship", "/universities/massachusetts-institute-of-technology-mit"):
        html = client.get(url).text
        assert 'class="window-note"' in html and "هذه النافذة لمن معه قبول جامعي اليوم" in html, url
        assert "15 نوفمبر 2026" in html.split('class="window-note"')[1].split("</p>")[0], url

    class Later(datetime.date):
        @classmethod
        def today(cls):
            return cls(2026, 11, 20)  # closed by its own deadline: no note
    monkeypatch.setattr(main, "date", Later)
    assert 'class="window-note"' not in client.get("/programs/custodian-scholarship").text


def test_foundation_year_conditions_show_where_the_saudi_certificate_is_not_enough():
    fact = main.PREP_YEAR_FACT
    assert fact and "90%" in fact["text_ar"] and fact["sources"]
    not_enough = [uid for uid, d in main.explorer.details.items()
                  if (d.get("saudi_certificate") or {}).get("direct_entry") is False]
    enough_or_unknown = [uid for uid, d in main.explorer.details.items()
                         if (d.get("saudi_certificate") or {}).get("direct_entry") is not False]
    assert not_enough
    for uid in not_enough:
        html = client.get(f"/universities/{uid}").text
        assert "data-foundation-note" in html and fact["text_ar"] in html, uid
    for uid in enough_or_unknown[:10]:
        assert "data-foundation-note" not in client.get(f"/universities/{uid}").text, uid


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


@pytest.mark.parametrize("page", ["/", "/about", "/programs/custodian-scholarship",
                                  "/grades/grade-10", "/grades/grade-11", "/grades/grade-12"])
def test_no_unverified_stamps_or_review_dates_anywhere(page):
    """Decision 028: unconfirmed things are hidden instead of stamped, and check dates stay in the data."""
    html = client.get(page).text
    assert "غير مؤكد" not in html
    assert "آخر مراجعة" not in html
    assert "unverified-stamp" not in html


def test_board_groups_follow_the_data():
    board = main.status_board()
    open_titles = [i["title_ar"] for i in board["open"]]
    waiting_titles = [i["title_ar"] for i in board["waiting"]]
    assert "مسار الرواد" in open_titles          # open until 15 Nov 2026
    assert "مسار إمداد" in waiting_titles        # closed until further notice
    assert board["recent"] and all(i.get("closed_on") for i in board["recent"])
    closed = [i["closed_on"] for i in board["recent"]]
    assert closed == sorted(closed, reverse=True)  # newest first
    for item in board["open"] + board["waiting"] + board["recent"]:
        assert item.get("source_url") or item.get("page"), item  # every item leads somewhere


def test_arruaad_moves_to_recently_closed_after_its_deadline(monkeypatch):
    import datetime

    class Day(datetime.date):
        @classmethod
        def today(cls):
            return cls(2026, 11, 20)
    monkeypatch.setattr(main, "date", Day)
    board = main.status_board()
    assert "مسار الرواد" in [i["title_ar"] for i in board["recent"]]
    assert "مسار الرواد" not in [i["title_ar"] for i in board["open"]]


def test_news_page_lists_everything():
    html = client.get("/news").text
    assert "المستجدات" in html and "إعلانات" in html
    for item in main.status_board()["recent"]:
        assert item["title_ar"] in html


# ---------- grade pages (decisions 038, 040) ----------

GRADES = ("grade-10", "grade-11", "grade-12")
TOOLS = {"grade-10": "tracks-title", "grade-11": "tests-title", "grade-12": "year-title"}


@pytest.mark.parametrize("slug", GRADES)
def test_grade_pages_share_one_short_structure(slug):
    """What matters (3 points) → one activity → the grade's own tool → resources → sources."""
    page = load_page("grades", slug)
    assert page["status"] == "sourced" and page["sources"] and page["stage_ar"]
    assert page["activity"]["text_ar"] and page["activity"]["href"]
    assert 1 <= len(page["resources"]) <= 4
    assert [c["title"] for c in page["contents"]] == ["ما يهم هذه السنة"]
    assert page["html"].split("<ol>")[1].split("</ol>")[0].count("<li>") == 3
    html = client.get(f"/grades/{slug}").text
    order = ['class="prose"', 'aria-label="ابدأ الآن"', f'id="{TOOLS[slug]}"', 'id="resources-title"', 'class="source-stamp"']
    positions = [html.index(marker) for marker in order]
    assert positions == sorted(positions), slug


def test_each_grade_has_its_own_tool_and_no_other():
    for slug, own in TOOLS.items():
        html = client.get(f"/grades/{slug}").text
        assert f'id="{own}"' in html
        for other in set(TOOLS.values()) - {own}:
            assert f'id="{other}"' not in html, (slug, other)


def test_grade_journey_shows_each_years_job_and_marks_the_current_one():
    html = client.get("/grades/grade-11").text
    journey = html.split('class="grade-journey"')[1].split("</nav>")[0]
    assert journey.count("<a ") == 3 and "اكتشف واستعد" in journey and "قدّم وتابع" in journey
    assert journey.count('aria-current="page"') == 1
    assert re.search(r'aria-current="page">(<svg class="journey-star".*?</svg>)?<span class="grade-journey-name">ثاني ثانوي', journey)
    assert "ماذا ينتظرك في ثالث ثانوي؟" in html
    assert "ماذا ينتظرك في" not in client.get("/grades/grade-12").text


@pytest.mark.parametrize("slug", GRADES)
def test_every_external_link_on_a_grade_page_is_a_listed_source_or_resource(slug):
    """Nothing on a grade page links outside without being declared (and so reviewed) in its frontmatter."""
    page = load_page("grades", slug)
    declared = {s["url"] for s in page["sources"]} | {r["url"] for r in page["resources"]}
    for href in re.findall(r'href="(https?://[^"]+)"', page["html"]):
        assert href in declared, (slug, href)


def test_grade_pages_show_no_example_years():
    """The owner's rule (2026-10-12): no «مثال: 2026–2027» labels, no past-year scholarship window."""
    for slug in GRADES:
        html = client.get(f"/grades/{slug}").text
        assert "مثال:" not in html and "مثال من سنة سابقة" not in html, slug


def test_test_needs_rows_are_sourced_and_dated():
    for row in main.test_needs["rows"]:
        assert row["who_ar"] and ISO_DATE.match(row["read_on"]), row["id"]
        assert row["source"]["url"].startswith(("https://", "/")), row["id"]
        assert row.get("computed") or row["need_ar"], row["id"]


def test_test_table_counts_sat_policies_from_the_university_files():
    s = main.explorer.sat_summary()
    assert sum(s["counts"].values()) == s["researched"] <= s["total"]
    for slug in ("grade-11",):
        html = client.get(f"/grades/{slug}").text
        assert 'id="tests-title"' in html
        assert f"مطلوب في {s['counts'].get('required', 0)} من {s['researched']}" in html
        # The scholarship row says plainly that Qudurat/Tahsili aren't required for it.
        assert "دون اشتراط درجة اختبار قدرات وتحصيلي" in html
    assert 'id="tests-title"' not in client.get("/grades/grade-10").text  # no test pressure in grade 10
    assert "/grades/grade-11#tests-title" in client.get("/grades/grade-12").text  # grade 12 links to it


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


# ---------- Program pages ----------

def test_program_page_compares_every_track():
    html = client.get("/programs/custodian-scholarship").text
    program = main.paths_by_id["custodian-scholarship"]
    assert '<table class="compare">' in html
    for track in program["tracks"]:
        assert track["name_ar"] in html
        assert track["levels_ar"] in html


def test_program_page_explains_conditional_admission():
    """The language exception must be on the page, next to its official source."""
    html = client.get("/programs/custodian-scholarship").text
    assert "القبول المشروط" in html
    assert "مشروطًا بدراسة لغة" in html
    assert "https://sites.moe.gov.sa/scholarship-program/conditions/info-6/" in html
    # The second accepted case: a preparatory year, with its conditions and source (owner-confirmed 2026-10-11).
    explainer = html.split('id="conditional"')[1]
    assert "السنة التحضيرية" in explainer and "90%" in explainer and "5.5" in explainer
    assert "https://sites.moe.gov.sa/scholarship-program/conditions/info-4/" in explainer


def test_program_page_shows_sources_and_conflicts():
    html = client.get("/programs/custodian-scholarship").text
    assert html.count('class="source-stamp"') >= 5
    assert "منصة قبول" in html and "منصة سفير" in html  # the conflict is shown with both names
    assert "program-kicker" not in html
    logo = main.paths_by_id["custodian-scholarship"]["logo"]
    assert logo["alt_ar"] in html


def test_homepage_links_to_program_page_and_hides_doctorate_track():
    html = client.get("/").text
    assert "/programs/custodian-scholarship" in html
    assert "مسار البحث والتطوير" not in html  # doctorate only: on the program page, not the homepage


@pytest.mark.parametrize("slug", ["nope", "aramco-cdpne", "CUSTODIAN-SCHOLARSHIP", "..%2F..%2F.env"])
def test_programs_without_a_page_return_404(slug):
    """Aramco is in paths.json but has no content file yet, so no page."""
    assert client.get(f"/programs/{slug}").status_code == 404



def test_tuwaiq_video_is_on_the_homepage():
    html = client.get("/").text
    assert 'class="tuwaiq"' in html
    assert "محمد بن سلمان" in html
    assert 'data-youtube-id="6fVtY11654w"' in html


def test_unconfirmed_items_are_hidden():
    assert main.is_confirmed({"source_url": "https://example.org"})
    assert main.is_confirmed({"source_url": None, "owner_confirmed": True})
    assert not main.is_confirmed({"source_url": None})


def test_ielts_resource_page():
    html = client.get("/resources/ielts").text
    assert "IELTS Academic" in html
    assert "https://sites.moe.gov.sa/scholarship-program/conditions/info-4/" in html
    assert 'class="source-stamp"' in html
    assert client.get("/resources/nope").status_code == 404
    assert f"<loc>{main.site['base_url']}/resources/ielts</loc>" in client.get("/sitemap.xml").text


# ---------- Waaid latest programs, deadlines, SDAIA ----------

def test_waaid_toggle_lists_latest_programs_newest_first():
    """The latest واعد programs live on the program page (decision 035); the homepage links there."""
    w = main.waaid()
    closing = [p["apply_to"] for p in w["programs"]]
    assert closing == sorted(closing, reverse=True)
    html = client.get("/programs/custodian-scholarship").text
    assert 'class="waaid-latest"' in html
    assert w["programs"][0]["program_ar"] in html
    assert main.waaid_data["source_url"] in html
    assert "/programs/custodian-scholarship#waaid-latest" in client.get("/").text


def test_open_track_closes_itself_after_its_deadline(monkeypatch):
    track = {"status": "open", "status_until": "2026-11-15"}

    class Day:
        @staticmethod
        def today():
            return Day.value
    monkeypatch.setattr(main, "date", Day)
    Day.value = __import__("datetime").date(2026, 11, 15)
    assert main.track_status(track) == "open"
    Day.value = __import__("datetime").date(2026, 11, 16)
    assert main.track_status(track) == "closed"


def test_sdaia_program_page_and_targets():
    html = client.get("/programs/sdaia-ai-scholarship").text
    assert "قرار ابتعاث" in html
    assert "https://sdaia.gov.sa/ar/Sectors/BuildingCapacity/Pages/ScholarshipProgram.aspx" in html
    sdaia = main.paths_by_id["sdaia-ai-scholarship"]
    assert len(sdaia["target_universities"]) == 95
    for target in sdaia["target_universities"]:
        if target["id"] is None:
            assert target["country_ar"], target  # not in the King lists: shown with its country
        else:
            assert target["id"] in main.explorer.universities, target


def test_sdaia_is_open_with_its_source_and_warns_it_is_not_standalone():
    sdaia = main.paths_by_id["sdaia-ai-scholarship"]
    track = sdaia["tracks"][0]
    assert track["status"] == "open" and track["status_source"].startswith("https://x.com/SDAIA_SA/")
    html = client.get("/programs/sdaia-ai-scholarship").text
    assert sdaia["not_standalone_ar"] in html


def test_board_links_sdaia_to_our_explainer():
    sdaia = [i for i in main.status_board()["open"] if i["page"] == "/programs/sdaia-ai-scholarship"]
    assert sdaia and sdaia[0]["source_url"].startswith("https://x.com/SDAIA_SA/")


def test_scholarship_links_its_official_x_account():
    assert "https://x.com/SA_Scholarships" in client.get("/").text


def test_footer_has_no_raw_sitemap_link_or_signup_promise():
    footer = client.get("/").text.split('<footer class="site-footer">')[1]
    assert "/sitemap.xml" not in footer  # the XML file is for search engines, not people
    assert "بدون تسجيل" not in footer
    assert client.get("/sitemap.xml").status_code == 200



# ---------- program and grade pages (decision 035) ----------

def test_program_page_leads_with_the_next_step_and_lists_its_sections():
    html = client.get("/programs/custodian-scholarship").text
    article = html.split('<article class="program')[1]
    assert article.index('class="back-link"') < article.index("<h1>")
    actions = article.split('class="actions"')[1].split("</div>")[0]
    assert 'class="btn btn--primary" href="http://testserver/universities"' in actions
    assert "صفحة التقديم الرسمية" in actions
    assert "روابط رسمية" in article
    contents = article.split('aria-label="في هذه الصفحة"')[1].split("</nav>")[0]
    for anchor in ("#tracks-title", "#conditional", "#admission-vs-scholarship", "#faq"):
        assert f'href="{anchor}"' in contents, anchor  # test_every_internal_link_works checks they exist


def test_owner_x_link_is_in_the_footer_only():
    """The owner's X account: in the global footer on every page, never in the nav; safe new tab; labelled."""
    for page in ("/", "/universities", "/universities/harvard-university", "/news", "/my-list"):
        html = client.get(page).text
        header, footer = html.split("</header>")[0], html.split('<footer class="site-footer">')[1]
        assert "x.com/salahmetaverse" not in header
        link = footer.split('class="footer-x"')[1].split("</a>")[0]
        assert 'href="https://x.com/salahmetaverse"' in link
        assert 'target="_blank"' in link and 'rel="noopener noreferrer"' in link
        assert "عندك ملاحظة أو اقتراح؟ راسلني على X" in link and 'aria-hidden="true"' in link
        assert "aria-label" not in link  # the visible text is the link's name (WCAG 2.5.3)
    main_part = client.get("/").text.split('<main id="main"')[1].split('<footer class="site-footer">')[0]
    assert "salahmetaverse" not in main_part


def test_logo_mark_is_the_same_in_the_header_and_the_favicon():
    """Decision 036: one drawing (ض with a lime diamond dot on a forest tile) in the header and favicon.svg."""
    header = client.get("/about").text.split("</header>")[0]
    favicon = client.get("/static/favicon.svg").text
    mark = header.split('<svg class="brand-mark"')[1].split("</svg>")[0]
    for colour in ("#184b3a", "#f6f4ee", "#d8ed9b"):
        assert colour in mark and colour in favicon
    glyph = mark.split('<path d="')[1].split('"')[0]
    assert glyph in favicon


# ---------- ثالث ثانوي month by month (decision 040) ----------

def test_year_rows_cover_every_month_once_and_facts_are_sourced():
    months = [m for r in main.apply_year["rows"] for m in r["months"]]
    assert sorted(months) == list(range(1, 13))
    for r in main.apply_year["rows"]:
        for fact in r["facts"]:
            assert fact["kind"] == "official" and ISO_DATE.match(fact["read_on"]), r["id"]
            assert fact["sources"] and all(s["url"].startswith("https://") for s in fact["sources"]), r["id"]
    sch = main.apply_year["scholarship"]
    assert sch["rule_source"].startswith("https://") and sch["conflict_source"].startswith("https://")


def test_year_marks_the_current_month_and_lists_deadlines_there():
    html = client.get("/grades/grade-12").text
    year = html.split('id="year"')[1].split("</section>")[0]
    assert year.count('aria-current="date"') == 1
    now = year.split('aria-current="date"')[1].split("</li>\n    \n")[0]
    assert "الآن" in now
    upcoming = main.explorer.upcoming_deadlines()
    if upcoming:
        assert "أقرب مواعيد الجامعات الآن" in year


def test_year_patterns_are_counted_from_the_university_files():
    s = main.explorer.timeline_stats()
    assert 0 < s["early"] <= s["with_deadlines"] and 0 < s["january"] <= s["with_deadlines"]
    html = client.get("/grades/grade-12").text
    assert f"في {s['early']} من {s['with_deadlines']} جامعة" in html
    assert "والابتعاث؟ لا يتبع هذه الأشهر" in html and "عدم التأكيد يسقط حق الطالب في الترشيح" in html


def test_year_patterns_never_name_a_track_they_dont_count():
    # timeline_stats() counts every researched university (الرواد and إمداد), so the sentence must not
    # say «مسار الرواد»: it once read «102 جامعة في مسار الرواد», and الرواد has 30.
    year = client.get("/grades/grade-12").text.split('id="year"')[1].split("year-scholarship")[0]
    assert "جامعة في مسار الرواد جمعنا" not in year
    assert "جامعة من قوائم الابتعاث جمعنا مواعيدها" in year


def test_emdad_research_count_comes_from_the_files():
    # The grade 11 tests table once said «لم نجمع متطلباتها بعد» after 99 إمداد universities were researched.
    s = main.explorer.sat_summary("emdad")
    assert 0 < s["researched"] <= s["total"]
    html = client.get("/grades/grade-11").text
    assert f"جمعنا متطلبات {s['researched']} من {s['total']}" in html
    assert "لم نجمع متطلباتها بعد" not in html


def test_year_is_linked_from_the_university_and_program_pages():
    assert "/grades/grade-12#year" in client.get("/universities/stanford-university").text
    assert "/grades/grade-12#year" in client.get("/programs/custodian-scholarship").text


# ---------- one public address (decision 042) ----------

def test_old_addresses_redirect_to_the_domain_with_path_and_query():
    for host in ("wadih-mqni.onrender.com", "www.wadihguide.com"):
        r = client.get("/universities?q=stanford&country=GB", headers={"host": host}, follow_redirects=False)
        assert r.status_code == 301, host
        assert r.headers["location"] == "https://wadihguide.com/universities?q=stanford&country=GB"
    r = client.get("/grades/grade-12", headers={"host": "wadih-mqni.onrender.com"}, follow_redirects=False)
    assert r.headers["location"] == "https://wadihguide.com/grades/grade-12"


def test_the_domain_itself_and_local_runs_are_not_redirected():
    for host in ("wadihguide.com", "testserver", "127.0.0.1:8000"):
        assert client.get("/", headers={"host": host}, follow_redirects=False).status_code == 200, host
    assert "https://wadihguide.com/grades/grade-10" in client.get("/sitemap.xml").text


def test_css_and_js_links_carry_a_content_version():
    """After a deploy, browsers fetch the new CSS/JS instead of a cached copy (?v= changes with the file)."""
    import re
    html = client.get("/universities").text
    for name in ("style.css", "universities.js", "mylist.js"):
        m = re.search(r'/static/' + re.escape(name) + r'\?v=([0-9a-f]{8})"', html)
        assert m and m.group(1) == main.asset_version(name), name


def test_rowwad_chart_places_every_university_once():
    """Decision 060: «خريطة الثلاثين» has one star per university in the الرواد list, inside the chart,
    none drawn on top of another, and each country's constellation where the drawing expects it."""
    import math
    from app.sky import CLUSTER_AT, rowwad_chart

    chart = rowwad_chart(main.explorer)
    listed = {u["id"] for _, u in main.explorer.listings("arruaad")}
    assert {s["id"] for s in chart["stars"]} == listed
    assert len(chart["stars"]) == len(listed)
    assert sum(k["count"] for k in chart["countries"]) == len(listed)
    for s in chart["stars"]:
        assert 20 < s["x"] < chart["w"] - 20 and 20 < s["y"] < chart["h"] - 20, s
    points = [(s["x"], s["y"]) for s in chart["stars"]]
    closest = min(math.dist(a, b) for i, a in enumerate(points) for b in points[i + 1:])
    assert closest > 14, closest  # a star (8 units) never overlaps another
    # A new country in the list would be placed automatically; this flags it so its place can be chosen.
    assert {k["code"] for k in chart["countries"]} <= set(CLUSTER_AT)


def test_rowwad_destination_only_on_its_track():
    """The الرواد opening shows on ?track=arruaad, with its status from data; elsewhere it's in the page but hidden."""
    html = client.get("/universities?track=arruaad").text
    opening = html[html.index("data-rowwad"):html.index("</section>", html.index("data-rowwad"))]
    assert "hidden" not in opening.split(">")[0]
    assert 'data-explorer-header hidden' in html
    track = next(t for t in main.paths_by_id["custodian-scholarship"]["tracks"] if t["id"] == "arruaad")
    assert track["note_ar"] in opening and track["levels_ar"] in opening
    if track.get("status_source"):
        assert track["status_source"] in opening
    assert "لا يعني قبولك فيها" in opening  # what the list doesn't answer (decision 038)
    # The country chips are plain links, so they work without JavaScript.
    assert '/universities?track=arruaad&amp;country=US"' in opening

    other = client.get("/universities?track=emdad").text
    assert 'data-rowwad aria-labelledby="rowwad-title" hidden' in other
    assert 'data-explorer-header hidden' not in other
