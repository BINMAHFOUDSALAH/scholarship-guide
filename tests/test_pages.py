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
    hero = html.split('<section class="hero')[1].split("</section>")[0]
    assert 'id="grades"' in hero
    assert "في أي صف أنت؟" in hero
    for slug in ("grade-10", "grade-11", "grade-12"):
        assert f"/grades/{slug}" in hero
    assert "<details" not in hero


def test_each_path_row_has_its_theme_and_facts():
    """The full program rows live on «البرامج» (decision 083); the homepage has one short row each."""
    html = client.get("/programs").text
    for path in main.paths:
        assert f'class="path-row theme-{path["theme"]}"' in html
        assert path["provider_ar"] in html
        assert path["audience_ar"] in html


def test_header_nav_on_desktop_and_phone_menu():
    html = client.get("/about").text
    header = html.split("</header>")[0]
    for label in ("حسب صفك", "البرامج", "الجامعات", "الأدلة"):
        assert header.count(f">{label}</a>") == 2, label  # desktop nav + phone menu
    assert ">مواعيد التقديم</a>" not in header  # folded into «البرامج» (decision 083)
    assert ">عن الدليل</a>" not in header  # removed from the menu (owner, 2026-10-12); the footer links to /about
    assert '<details class="menu">' in header


@pytest.mark.parametrize("url, label, value", [
    ("/universities", "الجامعات", "page"),
    ("/universities/stanford-university", "الجامعات", "true"),  # a page inside the section
    ("/programs", "البرامج", "page"),
    ("/waaid", "البرامج", "true"),
    ("/guides", "الأدلة", "page"),
    ("/resources/ielts", "الأدلة", "true"),
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
    for page in ("/", "/universities", "/universities/harvard-university", "/programs", "/grades/grade-10"):
        html = client.get(page).text
        assert '<a class="skip-link" href="#main">' in html
        assert '<main id="main" tabindex="-1">' in html


def test_footer_says_we_are_independent_and_links_the_image_credits():
    """The credits on /about must stay reachable (CC BY-SA licences), from every page's footer."""
    footer = client.get("/universities").text.split('<footer class="site-footer">')[1]
    assert "دليل طلابي مستقل" in footer  # the full "not affiliated" statement lives on /about (owner, 2026-11-06)
    assert "لا يتبع وزارة التعليم" in client.get("/about").text
    assert "/about#credits" in footer and "كيف نتحقق" not in footer
    assert 'id="credits"' in client.get("/about").text


def test_homepage_order():
    """Decision 083: the start (grades, then the one box, then the door for the undecided) → «الآن» → the programs →
    وضّاح → the guides. The journey, tests, «كيف نعمل», and the decorative drawing are not on the homepage."""
    html = client.get("/").text
    order = ['id="grades"', 'class="hero-search"', 'class="hero-door"', 'id="now"', 'id="programs"',
             *(['class="waddah-band"'] if main.waddah_public() else []), 'id="guides"']
    positions = [html.index(x) for x in order]
    assert positions == sorted(positions)
    for gone in ('id="start"', 'id="journey"', "كيف نعمل", "من أين تبدأ؟", "مجاني وبدون تسجيل", "hero-visual"):
        assert gone not in html


def test_homepage_search_goes_to_the_explorer_with_real_examples():
    """The one box (decision 083) submits to the site search, which answers from the lists and the guides."""
    html = client.get("/").text
    hero = html.split('<section class="hero')[1].split("</section>")[0]
    assert 'action="http://testserver/search"' in hero and 'name="q"' in hero and "data-suggest" in hero
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
    """Photos and logos load on «البرامج»; their credits live on /about, not on the image."""
    html = client.get("/programs").text
    about = client.get("/about").text
    assert 'class="photo-credit"' not in html
    for path in main.paths:
        image, ext = (path["logo"], "png") if path.get("logo") else (path["photo"], "jpg")
        if image is None:
            continue  # no image: the row shows the program's name alone (decision 062)
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
    """Decision 083: «الآن» shows what's open (soonest deadline first) and, under its own heading, what hasn't opened.
    «البرامج» has the whole board; /news redirects there."""
    html = client.get("/").text
    section = html.split('id="now"')[1].split("</section>")[0]
    assert "مفتوح للتقديم الآن" not in html  # the old heading that sat over programs not open yet
    assert "/programs" in section
    for item in main.status_board()["open"][:4]:
        assert item["title_ar"] in section
    assert "أُغلق في" not in section
    programs = client.get("/programs").text
    for title in ("مفتوح الآن", "لم يفتح بعد", "مغلق الآن"):
        assert title in programs
    r = client.get("/news", follow_redirects=False)
    assert r.status_code == 301 and r.headers["location"].endswith("/programs")
    assert client.get("/en/news", follow_redirects=False).headers["location"].endswith("/en/programs")


def test_open_and_not_yet_open_never_share_a_heading(monkeypatch):
    """2026-11-07: «مفتوح للتقديم الآن» listed Aramco («لم يفتح بعد») and KAUST («يفتح قريبًا»). Every row under
    «مفتوح الآن» is open today; the others sit under «لم يفتح بعد»."""
    now = main.now_board(main.status_board())
    assert now["open"] and all(i["status"] == "open" for i in now["open"])
    assert all(i["status"] in ("not_open", "opening_soon") for i in now["upcoming"])
    html = client.get("/").text.split('id="now"')[1].split("</section>")[0]
    opened = html.split('id="now-open-3"')[1].split('id="now-upcoming-3"')[0]
    upcoming = html.split('id="now-upcoming-3"')[1]
    assert 'status--not_open"' not in opened and 'status--opening_soon"' not in opened
    assert 'status--open"' not in upcoming
    for item in now["upcoming"]:
        assert item["title_ar"] in upcoming


def test_open_rows_show_their_closing_date_not_a_countdown():
    """Decision 084: an open row says when it closes (its status tag, «حتى 15 نوفمبر 2026»), with no countdown, and
    «الآن» shows no today's date: the site isn't updated every day, so a date that moves would look stale."""
    html = client.get("/").text
    now = html.split('id="now"')[1].split("</section>")[0]
    assert "now-count" not in now and "now-today" not in now and "يُغلق بعد" not in now
    track = next(t for t in main.paths_by_id["custodian-scholarship"]["tracks"] if t["id"] == "arruaad")
    if main.track_status(track) == "open":
        row = now.split("مسار الرواد")[1].split("</li>")[0]
        assert main.arabic_date(track["status_until"]) in row


def test_each_now_row_has_its_programs_picture():
    """Decision 084: every program in «الآن» has its own drawing (no text, no outside request); SDAIA's has its logo,
    and الرواد's row shows a few of its universities by their logos, each opening its page."""
    now = client.get("/").text.split('id="now"')[1].split("</section>")[0]
    rows = now.split('<li class="now-item')[1:]
    assert rows and all('program-art program-art--' in r for r in rows)
    for r in rows:
        assert 'aria-hidden="true"' in r.split("program-art--")[1].split(">")[0]
        if "program-art--logo" in r:  # an official logo, self-hosted (decision 085)
            tile = r.split('<span class="program-art')[1].split("</span>")[0]
            assert re.search(r'src="[^"]*/static/img/(programs|paths)/[a-z0-9-]+(-160\.png|\.svg)"', tile), tile
            continue
        art = r.split('<span class="program-art')[1].split("</svg>")[0]
        assert "http" not in art and "<script" not in art and "<text" not in art
    rowwad = next((r for r in rows if "مسار الرواد" in r), None)
    if rowwad:  # the King scholarship's logo (decision 085)
        assert "program-art--logo" in rowwad and "custodian-logo-160.png" in rowwad
    sdaia = next((r for r in rows if "program-art--sdaia" in r), None)
    if sdaia:
        assert "sdaia-logo-320.png" in sdaia
    rowwad = next((r for r in rows if "مسار الرواد" in r), None)
    if rowwad:
        logos = re.findall(r'href="[^"]*/universities/([a-z0-9-]+)"><img src="[^"]*/static/img/universities/small/\1\.png"',
                           rowwad)
        assert len(logos) == main.LOGO_COUNT
        listed = [u["id"] for _, u in sorted(main.explorer.listings("arruaad"), key=lambda r: r[0]["rank"])]
        assert logos == [uid for uid in listed if uid in main.explorer.logos][:main.LOGO_COUNT]  # the list's order
        assert '/universities?track=arruaad"' in rowwad


def test_every_logo_has_its_small_copy():
    """scripts/logo_thumbs.py makes the small logos the rows show (decision 084): one per logo, light enough to show
    several at once."""
    small = main.APP_DIR / "static" / "img" / "universities" / "small"
    for uid in main.explorer.logos:
        f = small / f"{uid}.png"
        assert f.is_file(), f"{uid}: run python scripts/logo_thumbs.py"
        assert f.stat().st_size < 8_000, uid


def test_open_items_say_who_can_apply():
    """«مفتوح الآن» alone read as "apply today" to grade 12 students who can't yet (الرواد needs an admission,
    SDAIA a scholarship), so every open track carries its «لمن» line on the homepage and «البرامج»."""
    tracks = [t for p in main.paths for t in p["tracks"] if t.get("for_high_school") is not False]
    for t in tracks:
        if not t.get("latest_programs"):  # واعد: each program has its own conditions
            assert t.get("apply_with_ar"), t.get("id") or t["name_ar"]
    home = client.get("/").text.split('id="now"')[1].split("</section>")[0]
    programs = client.get("/programs").text
    for item in main.status_board()["open"]:
        if item.get("who_ar"):
            assert f'لمن:</span> {item["who_ar"]}' in programs
    for item in main.status_board()["open"][:4]:
        if item.get("who_ar"):
            assert f'لمن:</span> {item["who_ar"]}' in home
    assert "يمكنك التقديم عليه اليوم" not in programs


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


def test_programs_page_lists_everything():
    """«البرامج» (decision 083) holds the whole board and the announcements, where /news used to."""
    html = client.get("/programs").text
    assert "إعلانات" in html and 'id="year-line"' not in html  # «السنة في سطر» removed (decision 086)
    board = main.status_board()
    for item in board["recent"] + board["open"] + board["waiting"]:
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


def test_ready_steps_link_existing_sourced_facts():
    """«معي قبول جامعي» (A1) repeats no official fact: every step and admission type links a sourced fact
    that the page shows, and the English page links the same facts in the same order."""
    program = main.paths_by_id["custodian-scholarship"]
    shown = main.ready_facts(program)
    page = load_page("programs", "custodian-scholarship")
    assert page["ready"] and page["admission_types"]
    for item in page["ready"] + page["admission_types"]:
        assert set(item.get("facts", [])) <= set(shown), item
    assert all(t["facts"] for t in page["admission_types"])
    html = client.get("/programs/custodian-scholarship").text
    for fid in {f for item in page["ready"] + page["admission_types"] for f in item.get("facts", [])}:
        assert f'href="#fact-{fid}"' in html and f'id="fact-{fid}"' in html, fid
    assert 'id="ready"' in html and 'href="#ready"' in html

    import frontmatter
    from app.content import CONTENT_DIR, EN_DIR
    ar = frontmatter.load(CONTENT_DIR / "programs" / "custodian-scholarship.md").metadata
    en = frontmatter.load(EN_DIR / "programs" / "custodian-scholarship.md").metadata
    for key in ("ready", "admission_types"):
        strip = lambda items: [(i.get("facts"), i.get("show"), i.get("href")) for i in items]  # noqa: E731
        assert strip(ar[key]) == strip(en[key]), key


@pytest.mark.parametrize("status", ["open", "closed"])
def test_ready_step_says_when_applying_is_open(monkeypatch, status):
    """Open: the apply link, with no extra disclaimer (owner, 2026-11-06). Closed: no link, and the honest «window closed» line."""
    monkeypatch.setitem(main.templates.env.globals, "track_status", lambda track: status)
    ready = client.get("/programs/custodian-scholarship").text.split('id="ready"')[1].split("</section>")[0]
    if status == "open":
        assert "https://www.uap.sa/" in ready and "ولا يرى طلبك" not in ready
    else:
        assert "https://www.uap.sa/" not in ready and "لم يُعلن موعد النافذة القادمة" in ready


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

def test_waaid_programs_are_newest_first_and_linked_from_the_program_page():
    """The program page links to /waaid (decision 063); the old #waaid-latest anchor still lands there."""
    w = main.waaid()
    closing = [p["apply_to"] for p in w["programs"]]
    assert closing == sorted(closing, reverse=True)
    html = client.get("/programs/custodian-scholarship").text
    assert 'id="waaid-latest"' in html and '/waaid"' in html
    assert '/waaid"' in client.get("/programs").text


def test_waaid_page_lists_every_program_under_its_own_anchor():
    r = client.get("/waaid")
    assert r.status_code == 200
    html = r.text
    for p in main.waaid_data["programs"]:
        assert f'id="{p["id"]}"' in html, p["id"]
    assert main.waaid_data["source_url"] in html
    assert f"<loc>{main.site['base_url']}/waaid</loc>" in client.get("/sitemap.xml").text


def test_waaid_page_puts_open_high_school_programs_first(monkeypatch):
    def program(pid, hs, apply_to):
        return {"id": pid, "company_ar": "شركة", "program_ar": pid, "level_ar": "بكالوريوس",
                "institution": "X", "country_ar": "Y", "duration_ar": "سنة", "start_ar": None,
                "apply_from": "2000-01-01", "apply_to": apply_to, "for_high_school": hs, "requirements_ar": []}
    monkeypatch.setitem(main.waaid_data, "programs", [
        program("old-closed", True, "2001-01-01"),
        program("open-master", False, "2999-01-01"),
        program("open-bachelor", True, "2999-01-01"),
    ])
    html = client.get("/waaid").text
    assert html.index('id="open-bachelor"') < html.index('id="open-master"') < html.index('id="old-closed"')
    assert "https://www.uap.sa/" in html  # the official «تقدم الآن» destination, shown while something is open


def test_board_links_each_waaid_announcement_to_its_block_on_the_page():
    board = main.status_board()
    items = [i for g in board.values() for i in g if i["program_ar"].startswith("مسار واعد")]
    html = client.get("/waaid").text
    assert items and all(i["page"].startswith("/waaid#g-") for i in items)
    for i in items:
        assert f'id="{i["page"].split("#")[1]}"' in html, i["page"]


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


def waaid_program(pid, hs, apply_from, apply_to, company="شركة"):
    return {"id": pid, "company_ar": company, "program_ar": f"برنامج {pid}", "level_ar": "بكالوريوس",
            "institution": "X", "country_ar": "Y", "duration_ar": "سنة", "start_ar": None,
            "apply_from": apply_from, "apply_to": apply_to, "for_high_school": hs, "requirements_ar": []}


def fix_today(monkeypatch, day):
    import datetime

    class Fixed(datetime.date):
        @classmethod
        def today(cls):
            return datetime.date.fromisoformat(day)
    monkeypatch.setattr(main, "date", Fixed)


def test_open_board_puts_waaid_announcements_with_nothing_for_high_school_last(monkeypatch):
    """A batch of واعد master's programs closing before الرواد must not push it off the homepage."""
    fix_today(monkeypatch, "2026-11-01")  # الرواد is open until 2026-11-15
    monkeypatch.setitem(main.waaid_data, "programs",
                        [waaid_program(f"m{n}", False, "2026-10-25", "2026-11-05") for n in range(5)])
    titles = [i["title_ar"] for i in main.status_board()["open"]]
    assert titles.index("مسار الرواد") < titles.index("برامج شركة")  # the batch closes sooner but comes after
    assert titles.index("مسار الرواد") < 4


def test_a_waaid_announcement_is_one_row_with_who_and_apply(monkeypatch):
    """11 programs from one company in one window: one homepage row that says who they are for, with «تقدم الآن»."""
    fix_today(monkeypatch, "2026-10-30")
    programs = ([waaid_program(f"b{n}", True, "2026-10-25", "2026-11-05", "شركة الاتصالات") for n in range(3)]
                + [waaid_program(f"m{n}", False, "2026-10-25", "2026-11-05", "شركة الاتصالات") for n in range(8)])
    monkeypatch.setitem(main.waaid_data, "programs", programs)
    rows = [i for i in main.status_board()["open"] if i["program_ar"].startswith("مسار واعد")]
    assert len(rows) == 1
    row = rows[0]
    assert row["title_ar"] == "برامج شركة الاتصالات" and row["page"] == "/waaid#g-m7"
    assert row["who_ar"] == "3 برامج لخريجي الثانوية، و8 برامج لغير خريجي الثانوية"
    assert row["apply_url"] == main.waaid_data["apply_url"] == "https://www.uap.sa/"
    home = client.get("/").text
    assert "برامج شركة الاتصالات" in home and "تقدم الآن" in home and "https://www.uap.sa/" in home


def test_announcement_anchor_survives_a_program_added_later(monkeypatch):
    """Programs are added at the top of the data; a link shared before that must still open the announcement."""
    fix_today(monkeypatch, "2026-10-30")
    first = [waaid_program("a", True, "2026-10-25", "2026-11-05"), waaid_program("b", False, "2026-10-25", "2026-11-05")]
    monkeypatch.setitem(main.waaid_data, "programs", first)
    anchor = main.waaid()["groups"][0]["id"]
    monkeypatch.setitem(main.waaid_data, "programs", [waaid_program("new", True, "2026-10-25", "2026-11-05")] + first)
    assert main.waaid()["groups"][0]["id"] == anchor
    assert f'id="{anchor}"' in client.get("/waaid").text


def test_waaid_lifecycle_before_during_after(monkeypatch):
    """Nothing is edited by hand: the same data reads «لم يفتح بعد», then open with «تقدم الآن», then closed."""
    monkeypatch.setitem(main.waaid_data, "programs", [waaid_program("p1", True, "2026-10-25", "2026-11-05")])
    for day, group, page_has, page_lacks in (
        ("2026-10-20", "waiting", 'id="waaid-upcoming"', "تقدم الآن"),
        ("2026-10-25", "open", "تقدم الآن", 'id="waaid-upcoming"'),
        ("2026-11-05", "open", "تقدم الآن", 'id="waaid-closed"'),
        ("2026-11-06", "recent", 'id="waaid-closed"', "تقدم الآن"),
    ):
        fix_today(monkeypatch, day)
        board = main.status_board()
        row = next(i for i in board[group] if i["page"] == "/waaid#g-p1")
        assert bool(row.get("apply_url")) == (group == "open"), (day, "apply link only while open")
        html = client.get("/waaid").text
        waaid_part = html[html.index("<h1>"):]
        assert page_has in waaid_part, (day, page_has)
        assert page_lacks not in waaid_part, (day, page_lacks)


def test_arruaad_apply_link_only_while_open(monkeypatch):
    track = next(t for t in main.paths_by_id["custodian-scholarship"]["tracks"] if t.get("id") == "arruaad")
    assert track["apply_url"] == "https://www.uap.sa/"
    fix_today(monkeypatch, track["status_until"])
    row = next(i for i in main.status_board()["open"] if i["title_ar"] == "مسار الرواد")
    assert row["apply_url"] == "https://www.uap.sa/"
    fix_today(monkeypatch, "2026-11-16")  # the day after its deadline
    assert not any(i["title_ar"] == "مسار الرواد" for i in main.status_board()["open"])


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
    for page in ("/", "/universities", "/universities/harvard-university", "/programs", "/my-plan"):
        html = client.get(page).text
        header, footer = html.split("</header>")[0], html.split('<footer class="site-footer">')[1]
        assert "x.com/salahmetaverse" not in header
        link = footer.split('class="footer-x no-ext"')[1].split("</a>")[0]
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
    # Counted in Arabic (decision 078, A5): «من 108 جامعات», never «من 108 جامعة».
    total = main.count_ar(s["with_deadlines"], main.COUNT_FORMS["universities"])
    assert f"في {s['early']} من {total} من قوائم" in html
    assert "والابتعاث؟ لا يتبع هذه الأشهر" in html and "عدم التأكيد يسقط حق الطالب في الترشيح" in html


def test_year_patterns_never_name_a_track_they_dont_count():
    # timeline_stats() counts every researched university (الرواد and إمداد), so the sentence must not
    # say «مسار الرواد»: it once read «102 جامعة في مسار الرواد», and الرواد has 30.
    year = client.get("/grades/grade-12").text.split('id="year"')[1].split("year-scholarship")[0]
    assert "في مسار الرواد جمعنا" not in year
    assert "من قوائم الابتعاث جمعنا مواعيدها" in year


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
    assert "لا يعني قبولك فيها" not in opening  # removed at the owner's request (decision 061)
    # The country chips are plain links, so they work without JavaScript.
    assert '/universities?track=arruaad&amp;country=US"' in opening

    other = client.get("/universities?track=emdad").text
    assert 'data-rowwad aria-labelledby="rowwad-title" hidden' in other
    assert 'data-explorer-header hidden' not in other


# ---------- the redesign (decision 062) ----------

def test_copyright_line_ends_every_footer_and_updates_itself(monkeypatch):
    """The last line of the footer: © from the first year of publication to the current year, computed on
    each request (never a hard-coded year), with the credits for what isn't ours on the same line."""
    import datetime

    class Fixed(datetime.date):
        year_now = 2026

        @classmethod
        def today(cls):
            return datetime.date(cls.year_now, 6, 1)

    monkeypatch.setattr(main, "date", Fixed)
    since = main.site["since"]
    for year, shown in ((since, f"© {since} واضح. جميع الحقوق محفوظة."),
                        (since + 2, f"© {since}–{since + 2} واضح. جميع الحقوق محفوظة.")):
        Fixed.year_now = year
        for page in ("/", "/universities", "/grades/grade-10", "/nope"):
            footer = client.get(page).text.split('<footer class="site-footer">')[1]
            legal = footer.split('class="footer-legal"')[1].split("</p>")[0]
            assert shown in legal, (page, year)
            assert "/about#credits" in legal and "لأصحابها" in legal
            assert footer.index('class="footer-legal"') > footer.index('class="footer-nav"')  # the very end


def test_logo_markup_is_exactly_the_favicon():
    """The logo never changes (owner, 2026-10-17): the header draws the favicon's own tile, letter and diamond."""
    header = client.get("/").text.split("</header>")[0]
    favicon = client.get("/static/favicon.svg").text
    mark = header.split('<svg class="brand-mark"')[1].split(">", 1)[1].split("</svg>")[0]
    drawing = favicon.split("-->", 1)[1].split("</svg>")[0].strip()
    assert mark == drawing


def test_homepage_route_leads_from_the_grades_to_the_programs():
    """The start (decision 062): one route of four stops, the three grades in order, then the programs."""
    hero = client.get("/").text.split('<section class="hero')[1].split("</section>")[0]
    route = hero.split('class="route-stops"')[1].split("</ol>")[0]
    hrefs = re.findall(r'class="route-link" href="([^"]+)"', route)
    assert hrefs == [f"http://testserver/grades/{g['slug']}" for g in main.home_text["grades"]] + ["http://testserver/programs"]
    assert route.count('class="route-mark" aria-hidden="true"') == 4


def test_every_guide_is_in_the_homepage_index_and_the_footer():
    """No guide without a way in: each page in content/resources is listed under «الأدلة»
    on the homepage and in every footer (titles come from the pages themselves)."""
    from app.content import list_slugs, load_page

    listed = [item["slug"] for group in main.home_text["guides"] for item in group["items"]]
    assert sorted(listed) == list_slugs("resources")
    home = client.get("/").text
    guides = home.split('id="guides"')[1].split("</section>")[0]
    footer = client.get("/about").text.split('<footer class="site-footer">')[1]
    for slug in listed:
        title = load_page("resources", slug)["title"]
        assert f"/resources/{slug}" in guides and title in guides, slug
        assert f"/resources/{slug}" in footer, slug


@pytest.mark.parametrize("page", ["/", "/universities?track=arruaad", "/universities/university-of-cambridge",
                                  "/programs", "/grades/grade-12", "/programs/custodian-scholarship"])
def test_no_values_joined_by_dots(page):
    """Values sit under their own labels or are joined by Arabic punctuation, never chained with «·» (decision 062)."""
    assert "·" not in client.get(page).text


def test_deadlines_follow_the_day_in_riyadh_not_the_server_clock(monkeypatch):
    """The live server runs on UTC. At 11 pm UTC on 5 Nov it is already 6 Nov in Riyadh, so a واعد
    program closing on 5 Nov must show as closed, not «تقدم الآن» for three more hours."""
    import datetime
    from app import clock

    class LateUTC(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime.datetime(2026, 11, 5, 23, 0, tzinfo=datetime.timezone.utc).astimezone(tz)

    monkeypatch.setattr(clock, "datetime", LateUTC)
    assert main.date is clock.date
    assert main.date.today() == datetime.date(2026, 11, 6)
    monkeypatch.setitem(main.waaid_data, "programs", [
        {**main.waaid_data["programs"][0], "id": "closing-5-nov", "apply_from": "2026-10-25", "apply_to": "2026-11-05"}])
    assert [p["is_open"] for p in main.waaid()["programs"]] == [False]


def test_every_program_and_track_says_when_you_apply():
    """A2 (decision 078): «البرامج» and «مفتوح للتقديم الآن» group by apply_when, so each needs one."""
    for p in main.paths:
        assert p.get("apply_when") in main.APPLY_WHEN, p["id"]
        for t in p["tracks"]:
            if t.get("for_high_school") is not False:
                assert t.get("apply_when") in main.APPLY_WHEN, t.get("id") or t["name_ar"]


def test_programs_are_grouped_by_when_you_apply():
    groups = main.programs_by_when()
    assert sum(len(g["paths"]) for g in groups) == len(main.paths)
    for url, split in (("/", 'id="programs"'), ("/programs", 'id="all-programs"')):
        html = client.get(url).text.split(split)[1].split("</section>")[0]
        positions = [html.index(f'id="programs-{g["when"]}"') for g in groups]
        assert positions == sorted(positions)
        # KGSP (in grade 12) comes before the Custodian program (after an admission).
        assert html.index("كاوست") < html.index("برنامج خادم الحرمين الشريفين")


def test_grade_12_says_where_to_start_and_promises_only_what_the_site_does():
    """A4 (decision 078): «من أين تبدأ؟» routes by what the student wants; «ابدأ الآن» no longer asks them to
    write notes «لكل جامعة في «قائمتي»», which «قائمتي» can't hold."""
    html = client.get("/grades/grade-12").text
    start = html.split('id="start-title"')[1].split("</section>")[0]
    for href in ("/programs/custodian-scholarship#ready", "/#programs-in_school", "https://www.uap.sa/", "/resources/undecided"):
        assert f'href="{href}"' in start, href
    assert "لكل جامعة في «قائمتي»" not in html
    assert 'id="programs-in_school"' in client.get("/").text  # the anchor the second row links to
    assert "Where to start?" in client.get("/en/grades/grade-12").text


def test_no_bare_zero_counts(monkeypatch):
    """A5 (decision 078): «منها 0 لخريجي الثانوية» and «0 جامعة» read as broken; say it in words or hide it."""
    custodian = client.get("/programs/custodian-scholarship").text
    assert "منها 0" not in custodian
    empty = client.get("/universities", params={"q": "zzzz"}).text
    assert not re.search(r"(?<![\d٠-٩])0 جامعة", empty)
    assert ">0<" not in client.get("/programs").text.replace(" ", "")


@pytest.mark.parametrize("url", ["/", "/universities?track=arruaad", "/universities/stanford-university",
                                 "/programs/custodian-scholarship", "/grades/grade-12", "/resources/ielts", "/waaid"])
def test_no_symbol_characters_that_fonts_lack(url):
    """Decision 083: ↗, ✓ and → aren't in the self-hosted fonts and showed as empty boxes on some phones.
    They are drawn in CSS now (a new-tab link gets ↗ by itself), so no page prints them."""
    for lang in ("", "/en"):
        html = client.get(lang + url).text
        body = html.split("<body", 1)[1]
        for ch in "↗✓→←":
            assert ch not in body, f"{lang + url}: {ch!r} in the page"


def test_every_page_keeps_its_place_on_back():
    """Decision 085: Safari on iPhone sometimes lands at the top on Back; back.js puts the student where they were."""
    for page in ("/", "/programs", "/about", "/en/"):
        assert "/static/back.js?v=" in client.get(page).text, page
    js = (main.APP_DIR / "static" / "back.js").read_text(encoding="utf-8")
    assert "back_forward" in js and "sessionStorage" in js and 'getElementById("results")' in js


def test_a_touch_lights_a_country_before_opening_it():
    """Decision 085: on a phone the first tap on a country's chip lights it on the map; the second opens it."""
    js = (main.APP_DIR / "static" / "map.js").read_text(encoding="utf-8")
    assert '"touch"' in js and "preventDefault" in js and "is-picked" in js
    assert ".country-chip.is-picked" in (main.APP_DIR / "static" / "style.css").read_text(encoding="utf-8")


def test_rowwad_title_opens_its_universities_map():
    """«مسار الرواد» in «الآن» opens the الرواد map (/universities?track=arruaad), not the scholarship's page."""
    rows = [i for g in main.status_board().values() for i in g if i.get("unis_track") == "arruaad"]
    assert rows and all(i["page"] == "/universities?track=arruaad" for i in rows)
    assert 'class="rowwad-title"' in client.get("/universities?track=arruaad").text
