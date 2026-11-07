"""Phase 1 Part C (decisions 081–083): «خطتي» as a hub, the calendar file, «السنة في سطر», the map, وضّاح's teaser
and the Phase 2 switches. The pages' own structure is in test_pages.py; these are the new pieces' rules."""

import datetime
import json
import re

import pytest
from fastapi.testclient import TestClient

import app.main as main
from app import plan
from scripts.english_leaks import arabic_outside_lang_ar

client = TestClient(main.app)

PLAN = {"v": 1, "items": [
    {"type": "university", "id": "stanford-university", "status": "preparing", "updated": "2026-11-01"},
    {"type": "program", "id": "arruaad", "status": "thinking", "updated": "2026-11-05"},
    {"type": "university", "id": "university-of-oxford", "status": "applied", "updated": "2026-10-12"},
    {"type": "university", "id": "national-university-of-singapore-nus", "status": "accepted", "updated": "2026-11-06"},
]}


def on(monkeypatch, y, m, d):
    class Day(datetime.date):
        @classmethod
        def today(cls):
            return cls(y, m, d)
    monkeypatch.setattr(main, "date", Day)


# ---------- «خطتي» as a hub ----------

def test_the_hub_counts_each_step_and_lights_the_furthest(monkeypatch):
    on(monkeypatch, 2026, 11, 7)
    html = client.post("/my-plan", json=PLAN).text
    hub = html.split('<template data-plan-part="hub">')[1].split("</template>")[0]
    counts = re.findall(r'class="plan-route-count">(\d+)<', hub)
    assert counts == ["1", "1", "1", "1"]  # أفكّر، أستعد، قدّمت، قُبلت
    assert hub.count("is-reached") == 4 and hub.count("is-here") == 1


def test_soon_lists_the_next_30_days_with_sources_and_skips_finished_items(monkeypatch):
    on(monkeypatch, 2026, 11, 7)
    items = plan.clean(PLAN, main.explorer.universities, main.plan_programs)
    dates = plan.dates(items, main.explorer, main.plan_programs, main.track_status, "2026-11-07")
    assert [d["date"] for d in dates] == sorted(d["date"] for d in dates)
    assert all(d["source_url"] for d in dates)
    assert not any(d.get("university", {}).get("id") == "national-university-of-singapore-nus" for d in dates)  # «قُبلت»
    html = client.post("/my-plan", json=PLAN).text
    soon = html.split('id="plan-soon-title"')[1].split("</section>")[0]
    assert "مسار الرواد" in soon and "15 نوفمبر 2026" in soon  # الرواد's deadline, from its sourced status_until
    for d in re.findall(r'datetime="(\d{4}-\d{2}-\d{2})"', soon):
        assert "2026-11-07" <= d <= "2026-12-07"


def test_the_calendar_file_is_valid_and_holds_no_personal_data(monkeypatch):
    on(monkeypatch, 2026, 11, 7)
    r = client.post("/my-plan.ics", json=PLAN)
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/calendar")
    assert 'filename="wadih-plan.ics"' in r.headers["content-disposition"] and r.headers["cache-control"] == "no-store"
    text = r.text
    assert text.startswith("BEGIN:VCALENDAR\r\n") and text.endswith("END:VCALENDAR\r\n")
    assert text.count("BEGIN:VEVENT") == text.count("END:VEVENT") >= 2
    assert "TRIGGER:-P3D" in text and "DTSTART;VALUE=DATE:20261115" in text
    assert all(len(line.encode()) <= 75 for line in text.split("\r\n")), "lines are folded at 75 octets"
    assert not re.search(r"ATTENDEE|ORGANIZER|MAILTO", text)
    unfolded = text.replace("\r\n ", "")
    assert "https://x.com/SA_Scholarships" in unfolded  # each event names its official source


def test_the_calendar_and_hub_refuse_what_they_dont_know():
    assert client.post("/my-plan.ics", content=b"not json").status_code == 400
    assert client.post("/my-plan.ics", content=b"x" * 20_001).status_code == 413
    junk = {"items": [{"type": "university", "id": "../etc", "status": "x"}, {"type": "program", "id": "nope"}]}
    assert "BEGIN:VEVENT" not in client.post("/my-plan.ics", json=junk).text


def test_the_hub_in_english_is_english(monkeypatch):
    on(monkeypatch, 2026, 11, 7)
    html = client.post("/en/my-plan", json=PLAN).text
    assert not arabic_outside_lang_ar(html), arabic_outside_lang_ar(html)[:5]
    ics = client.post("/en/my-plan.ics", json=PLAN).text
    assert "My plan on Wadih" in ics and "Official source:" in ics.replace("\r\n ", "")


def test_your_constellation_maps_only_your_universities(monkeypatch):
    on(monkeypatch, 2026, 11, 7)
    hub = client.post("/my-plan", json=PLAN).text.split('<template data-plan-part="hub">')[1].split("</template>")[0]
    codes = re.findall(r'data-world-chip="([A-Z]{2})"', hub)
    assert sorted(codes) == ["GB", "SG", "US"]


# ---------- «السنة في سطر» ----------

def test_the_year_line_draws_only_dated_facts(monkeypatch):
    on(monkeypatch, 2026, 11, 7)
    y = main.year_line()
    assert y["start"] == "2026-08-01" and len(y["months"]) == 12 and sum(m["days"] for m in y["months"]) == 365
    assert 0 < y["today_at"] < 100
    assert [m["title_ar"] for m in y["marks"]] == ["مسار الرواد"] and y["marks"][0]["source_url"]
    assert all(w["href"].startswith("/waaid#") for w in y["windows"])
    names = " ".join(m["title_ar"] for m in y["marks"]) + " ".join(w["title_ar"] for w in y["windows"])
    assert "أرامكو" not in names and "كاوست" not in names  # no announced date, so not on the line
    assert sum(1 for p in y["phases"] if p["is_now"]) == 1


def test_the_year_line_starts_in_august_even_in_spring(monkeypatch):
    on(monkeypatch, 2027, 3, 1)
    y = main.year_line()
    assert y["start"] == "2026-08-01" and [m["n"] for m in y["months"] if m["is_now"]] == [3]


# ---------- the map ----------

def test_the_homepage_map_has_every_country_with_its_count():
    html = client.get("/").text.split('id="where"')[1].split("</section>")[0]
    for code, info in main.explorer.countries.items():
        n = sum(1 for u in main.explorer.universities.values() if u["country"] == code)
        if n:
            assert f'country={code}" data-world-chip="{code}"' in html, code
    assert 'aria-hidden="true" focusable="false"' in html  # the drawing is a picture; the chips are the list


def test_the_explorer_offers_a_map_for_lists_across_countries_only():
    assert 'class="map-view"' in client.get("/universities?track=emdad&field=ict").text
    assert 'class="map-view"' not in client.get("/universities?track=emdad&field=ict&country=GB").text
    assert 'class="map-view"' not in client.get("/universities?track=arruaad").text  # «خريطة الثلاثين» is there


# ---------- وضّاح ----------

def test_dawn_rises_by_the_riyadh_date_and_holds_until_launch(monkeypatch):
    d = datetime.date
    assert main.waddah_dawn(d(2026, 11, 7)) == 0.0
    assert 0 < main.waddah_dawn(d(2026, 11, 20)) < main.waddah_dawn(d(2026, 11, 28)) < 0.9
    assert main.waddah_dawn(d(2026, 12, 20)) == 0.9
    monkeypatch.setitem(main.waddah, "launched", True)
    assert main.waddah_dawn(d(2026, 11, 7)) == 1.0


@pytest.mark.parametrize("prefix", ["", "/en"])
def test_waddah_page_says_what_it_will_and_wont_do(prefix):
    r = client.get(prefix + "/waddah")
    assert r.status_code == 200
    html = r.text
    assert "waddah-og.png" in html and f"{main.site['base_url']}{prefix}/waddah</loc>" in client.get("/sitemap.xml").text
    if not prefix:
        for p in main.waddah["promises"]:
            assert p["title_ar"] in html
        for x in main.waddah["wont_ar"] + main.waddah["examples_ar"]:
            assert x in html
        assert "قادم في ديسمبر" in html and "ذكاء اصطناعي" in html  # it says it's AI
    assert client.get(prefix + "/static/img/waddah-og.png").status_code == 200


def test_the_teaser_band_is_on_the_homepage_with_todays_dawn(monkeypatch):
    on(monkeypatch, 2026, 11, 20)
    html = client.get("/").text
    band = html.split('class="waddah-band"')[1].split("</section>")[0]
    assert f'--dawn: {main.waddah_dawn(datetime.date(2026, 11, 20))}' in band and "/waddah" in band


def test_sign_in_waits_for_its_switch(monkeypatch):
    """Phase 2's «دخول» (decisions 078, 082): the slot exists, and stays empty until data/waddah.json opens accounts.
    The site never needs it."""
    assert main.waddah["accounts_open"] is False
    assert 'class="signin-link"' not in client.get("/").text
    monkeypatch.setitem(main.waddah, "accounts_open", True)
    header = client.get("/about").text.split("</header>")[0]
    assert 'class="signin-link" href="/signin">دخول</a>' in header


def test_the_data_file_has_its_switches_and_no_fixed_day():
    data = json.loads((main.DATA_DIR / "waddah.json").read_text(encoding="utf-8"))
    assert data["launched"] is False and data["launch_date"] is None  # «في ديسمبر», no day (decision 082)
    assert data["dawn_from"] < data["dawn_to"]


# ---------- «هذا صفّي» ----------

@pytest.mark.parametrize("slug", ["grade-10", "grade-11", "grade-12"])
def test_each_grade_page_can_be_marked_as_mine(slug):
    html = client.get(f"/grades/{slug}").text
    assert f'data-my-grade="{slug}" aria-pressed="false" hidden' in html


def test_the_homepage_route_can_mark_the_students_grade():
    html = client.get("/").text
    for g in main.home_text["grades"]:
        assert f'data-grade-stop="{g["slug"]}"' in html
    assert html.count("data-grade-here hidden") == 3
