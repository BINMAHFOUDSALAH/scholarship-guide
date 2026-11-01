"""The site check (scripts/watch.py, step 1 of /update-site, decision 064). No test here touches the internet:
pages and the live site are replaced by small fakes, and dates are passed in, so CI can't turn red as days go by."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("watch", ROOT / "scripts" / "watch.py")
watch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch)

SOURCE = "https://sites.moe.gov.sa/scholarship-program/paths/path-waaid/"


@pytest.mark.parametrize("text, window", [
    ("من 1 نوفمبر 2026م إلى 10 نوفمبر 2026م", ("2026-11-01", "2026-11-10")),
    ("من 25 أكتوبر 2026م إلى 5 نوفمبر 202​​6م", ("2026-10-25", "2026-11-05")),  # invisible characters
    ("25\xa0أكتوبر 2026م إلى 5 نوفمبر 2026م", ("2026-10-25", "2026-11-05")),  # no «من», a no-break space
    ("من  3 أغسطس إلى 17 أغسطس 2026", ("2026-08-03", "2026-08-17")),  # the year said once
    ("من 2 أغسطس إلى13 أغسطس 2026م", ("2026-08-02", "2026-08-13")),
    ("من 30 أغسطس 2026م وحتى 3 سبتمبر 2026م", ("2026-08-30", "2026-09-03")),
    ("من 2 أغسطس 2026م إل​ى 6 أغسطس 2026م", ("2026-08-02", "2026-08-06")),
    ("من ٢٠ ديسمبر إلى ٥ يناير ٢٠٢٧", ("2026-12-20", "2027-01-05")),  # Arabic-Indic digits, across a new year
    ("بمعدل 3.5 من 4 أو ما يعادلها", None),
    ("من 31 نوفمبر 2026 إلى 5 ديسمبر 2026", None),  # a typo on the page isn't a date
])
def test_reads_every_window_wording_the_waaid_page_uses(text, window):
    assert watch.parse_window(text) == window


def block(title, company, window_text):
    return (f"<h3>{title}</h3><p>{watch.ANNOUNCEMENT} الابتعاث المبتدئ بالتوظيف في {company}<br>ضمن مسار واعد</p>"
            f"<p>فترة التقديم:</p><p>{window_text}</p><p>شارك:</p>")


PAGE = ("<nav>المسارات</nav>"
        + block("تدريب في قطاع السكك الحديدية", "شركة الخطوط الحديدية السعودية (سار)",
                "من 1 نوفمبر 2026م إلى 10 نوفمبر 2026م")
        + block("بكالوريوس في علوم الحاسب", "شركة الاتصالات السعودية (STC)", "من 25 أكتوبر 2026م إلى 5 نوفمبر 2026م")
        + block("ماجستير في إدارة الفعاليات", "شركة نادي الاتحاد", "من 13 سبتمبر 2026م إلى 17 سبتمبر 2026م"))


def program(pid, start, end, company="شركة"):
    return {"id": pid, "company_ar": company, "apply_from": start, "apply_to": end, "for_high_school": True}


def test_reads_each_announcement_on_the_page_with_its_company_and_window():
    found = watch.waaid_announcements(watch.page_lines(PAGE))
    assert [(a["title"], a["company"], a["window"]) for a in found] == [
        ("تدريب في قطاع السكك الحديدية", "شركة الخطوط الحديدية السعودية (سار)", ("2026-11-01", "2026-11-10")),
        ("بكالوريوس في علوم الحاسب", "شركة الاتصالات السعودية (STC)", ("2026-10-25", "2026-11-05")),
        ("ماجستير في إدارة الفعاليات", "شركة نادي الاتحاد", ("2026-09-13", "2026-09-17")),
    ]


def test_flags_a_new_waaid_announcement_but_not_old_closed_ones_we_left_out():
    found = watch.waaid_announcements(watch.page_lines(PAGE))
    ours = [program("stc", "2026-10-25", "2026-11-05")]  # SAR missing; the closed الاتحاد one isn't our concern
    items = watch.waaid_items(found, ours, "2026-11-01", SOURCE)
    assert [i["key"] for i in items] == ["waaid:2026-11-01:2026-11-10:1"]
    assert "تدريب في قطاع السكك الحديدية" in items[0]["text"] and "شركة الخطوط الحديدية السعودية" in items[0]["text"]
    ours.append(program("sar", "2026-11-01", "2026-11-10"))
    assert watch.waaid_items(found, ours, "2026-11-01", SOURCE) == []


def test_flags_a_program_we_list_that_the_page_no_longer_shows():
    found = watch.waaid_announcements(watch.page_lines(PAGE))
    ours = [program("sar", "2026-11-01", "2026-11-10"), program("stc", "2026-10-25", "2026-11-05"),
            program("stc2", "2026-10-25", "2026-11-05")]
    assert [i["key"] for i in watch.waaid_items(found, ours, "2026-11-01", SOURCE)] == \
        ["waaid-gone:2026-10-25:2026-11-05:1"]


def test_flags_an_unreadable_window_at_the_top_and_an_unreadable_page():
    page = block("برنامج جديد", "شركة جديدة", "يعلن لاحقًا") + PAGE
    found = watch.waaid_announcements(watch.page_lines(page))
    ours = [program("sar", "2026-11-01", "2026-11-10"), program("stc", "2026-10-25", "2026-11-05")]
    assert [i["key"] for i in watch.waaid_items(found, ours, "2026-11-01", SOURCE)] == ["waaid-unread:برنامج جديد"]
    assert [i["key"] for i in watch.waaid_items([], ours, "2026-11-01", SOURCE)] == ["waaid-page"]


def test_lists_waaid_windows_closing_within_three_days():
    ours = [program("a", "2026-10-25", "2026-11-05", "شركة أ"), program("b", "2026-11-01", "2026-11-10", "شركة ب")]
    assert watch.waaid_closing_soon(ours, "2026-11-03") == [
        "واعد closes 5 Nov 2026: شركة أ (1 program, 1 for high school graduates)"]
    assert watch.waaid_closing_soon(ours, "2026-10-20") == []


def test_flags_tracks_past_their_deadline_and_open_tracks_not_rechecked():
    paths = [{"id": "p", "name_ar": "برنامج", "tracks": [
        {"id": "dated", "name_ar": "مسار بموعد", "status": "open", "status_until": "2026-11-15",
         "last_checked": "2026-11-01"},
        {"id": "undated", "name_ar": "مسار بلا موعد", "status": "open", "last_checked": "2026-10-11"},
        {"id": "waaid", "name_ar": "مسار واعد", "status": "none_open", "latest_programs": True,
         "last_checked": "2026-01-01"},
    ]}]
    assert [i["key"] for i in watch.deadline_items(paths, [], "2026-10-20")] == []
    assert [i["key"] for i in watch.deadline_items(paths, [], "2026-11-16")] == [
        "track-closed:dated:2026-11-15", "track-open:undated:2026-10-11"]


def test_flags_a_university_whose_every_date_has_passed():
    details = [{"id": "u", "name_en": "U", "admissions_url": "https://u.example",
                "dates": [{"date": "2026-10-15"}, {"date": "2027-01-01", "reference_only": True}, {"date": None}]}]
    assert watch.deadline_items([], details, "2026-10-15") == []
    assert [i["key"] for i in watch.deadline_items([], details, "2026-10-16")] == ["uni-dates:u:2026-10-15"]


def fake_fetcher(pages):
    return lambda url, read=True: pages.get(url, (None, None))


def test_a_watched_page_is_flagged_when_its_phrase_goes_or_its_alert_appears():
    entries = [{"id": "k", "name": "KGSP", "url": "https://k", "expect": ["Cohort 19 will open soon"],
                "then": "Update KGSP."},
               {"id": "g", "name": "Guide", "url": "https://g", "expect": ["guide-2027-2026.pdf"],
                "alert_if": ["2028-2027"], "then": "New guide."},
               {"id": "a", "name": "Aramco", "url": "https://a", "expect": ["باب التسجيل مغلق"],
                "often_blocked": True, "then": "Update Aramco."}]
    same = {"https://k": (200, "<p>Applications for Cohort 19\n will\xa0open soon</p>"),
            "https://g": (200, '<a href="/files/guide-2027-2026.pdf">الدليل</a>')}
    assert watch.page_watch_items(entries, fake_fetcher(same)) == \
        ([], ["Aramco: [the page](https://a) didn't open (no answer); this site often refuses scripts, so check it "
              "in a browser now and then."])
    changed = {"https://k": (200, "<p>Applications for Cohort 19 are open</p>"),
               "https://g": (200, '<a href="guide-2027-2026.pdf">old</a> <a href="guide-2028-2027.pdf">new</a>')}
    items, _ = watch.page_watch_items(entries, fake_fetcher(changed))
    assert [i["key"] for i in items] == ["page:k:Cohort 19 will open soon", "page:g:2028-2027"]


def test_every_watched_page_says_what_to_watch_and_what_to_do():
    pages = json.loads((ROOT / "scripts" / "watch_pages.json").read_text(encoding="utf-8"))["pages"]
    assert len({p["id"] for p in pages}) == len(pages)
    for p in pages:
        assert p["url"].startswith("https://") and p["then"] and p["confirmed_on"]
        assert p.get("expect") or p.get("alert_if")


def test_live_site_problems_are_bugs():
    programs = [{"id": "sar-railway-training"}, {"id": "stc-nus-bcomp-cs"}]
    base = "https://wadihguide.com"
    pages = {f"{base}/sitemap.xml": (200, f"<loc>{base}/</loc><loc>{base}/waaid</loc>"),
             f"{base}/waaid": (200, '<li id="stc-nus-bcomp-cs">')}
    statuses = lambda urls: {u: ((500, None) if u == f"{base}/" else (200, None)) for u in urls}  # noqa: E731
    items, count = watch.live_items(base, programs, fake_fetcher(pages), statuses)
    assert count == 2
    assert [i["key"] for i in items] == [f"live:{base}/:500", "live-behind:sar-railway-training"]
    items, _ = watch.live_items(base, programs, fake_fetcher({}), statuses)
    assert [i["key"] for i in items] == ["live-down"]


def test_only_404_and_410_count_as_broken_links():
    links = {"https://gone": "data/paths.json", "https://blocked": "data/paths.json", "https://fine": "x"}
    results = {"https://gone": (404, None), "https://blocked": (403, None), "https://fine": (200, None)}
    items, other = watch.link_items(links, results)
    assert [i["key"] for i in items] == ["link:https://gone:404"] and other == 1


def test_the_official_links_skip_x_and_the_site_itself():
    links = watch.program_links()
    assert links and all("x.com/" not in u and "wadihguide.com" not in u for u in links)
    assert SOURCE in links


def test_removes_waaid_programs_once_they_leave_the_homepage_board():
    from app import main
    assert watch.REMOVE_WAAID_AFTER_DAYS == main.RECENT_DAYS
    ours = [program("m1", "2026-07-19", "2026-08-02", "معادن"), program("m2", "2026-07-19", "2026-08-02", "معادن"),
            program("stc", "2026-10-25", "2026-11-05", "STC")]
    assert watch.waaid_old_items(ours, "2026-11-30") == []  # 120 days after 2 Aug: still on the board
    assert [i["key"] for i in watch.waaid_old_items(ours, "2026-12-01")] == ["waaid-old:m1,m2"]


def test_the_offline_report_runs_on_the_real_data():
    items, fyi, checked = watch.run("2026-11-01", offline=True)
    assert all(i["section"] in watch.SECTIONS for i in items)
    report = watch.render(items, fyi, checked, "2026-11-01")
    assert report.startswith("## Site check, 1 Nov 2026") and "### Past or due for a re-check" in report
