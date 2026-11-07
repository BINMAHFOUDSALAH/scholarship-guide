"""Phase 1 Part C (decisions 081–083): «خطتي» as a hub, the calendar file, the map, وضّاح's teaser
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
    ics = client.post("/en/my-plan.ics", json=PLAN).text.replace("\r\n ", "")
    assert "My plan on Wadih" in ics and "Official source:" in ics
    # Stanford's dates have a round («Regular Decision»): each part is translated, never a joined Arabic string.
    assert "Regular Decision" in ics and not re.search(r"[\u0600-\u06ff]", ics), re.findall(r"SUMMARY:.*", ics)


def test_two_dates_on_one_day_are_two_events():
    items = plan.clean(PLAN, main.explorer.universities, main.plan_programs)
    uids = [d["uid"] for d in plan.dates(items, main.explorer, main.plan_programs, main.track_status, "2026-01-01")]
    assert len(uids) == len(set(uids))


def test_your_constellation_maps_only_your_universities(monkeypatch):
    on(monkeypatch, 2026, 11, 7)
    hub = client.post("/my-plan", json=PLAN).text.split('<template data-plan-part="hub">')[1].split("</template>")[0]
    codes = re.findall(r'data-world-chip="([A-Z]{2})"', hub)
    assert sorted(codes) == ["GB", "SG", "US"]


# ---------- the map ----------

def test_the_homepage_map_has_every_country_with_its_count():
    html = client.get("/").text.split('id="where"')[1].split("</section>")[0]
    for code, info in main.explorer.countries.items():
        n = sum(1 for u in main.explorer.universities.values() if u["country"] == code)
        if n:
            assert f'country={code}" data-world-chip="{code}"' in html, code
    assert 'aria-hidden="true" focusable="false"' in html  # the drawing is a picture; the chips are the list


@pytest.mark.parametrize("counts", [None, {"US": 3, "GB": 2, "SG": 1}, {"FR": 1}])
def test_the_map_is_drawn_like_the_rowwad_chart(counts):
    """Decision 084: one four-point star per university, a constellation per country under its name, all inside the
    frame, and no constellation (with its name) on top of another or of home. counts=None is the homepage's 290."""
    from app.sky import CHART_H, CHART_W, CHAR_W, HOME_BOX, LABEL_GAP, LABEL_H, WORLD_AT, world_chart
    if counts is None:
        counts = {}
        for u in main.explorer.universities.values():
            counts[u["country"]] = counts.get(u["country"], 0) + 1
    names = {c: main.explorer.countries[c]["name_ar"] for c in counts}
    chart = world_chart(counts, names)
    assert {k["code"]: len(k["stars"]) for k in chart["countries"]} == counts
    assert all(k["stars_d"].count("z") == k["count"] for k in chart["countries"])
    assert set(counts) <= set(WORLD_AT)  # a new country in the lists gets a place chosen for it
    boxes = []
    for k in chart["countries"]:
        xs, ys = [x for x, _ in k["stars"]], [y for _, y in k["stars"]]
        half = len(k["name_ar"]) * CHAR_W / 2
        box = (min(min(xs), k["x"] - half), min(ys), max(max(xs), k["x"] + half), k["label_y"] + 4)
        assert 0 < box[0] and box[2] < CHART_W and 0 < box[1] and box[3] < CHART_H, (k["code"], box)
        boxes.append((k["code"], box))
    for i, (a, ba) in enumerate(boxes):
        for b, bb in boxes[i + 1:] + [("home", HOME_BOX)]:
            apart = ba[2] <= bb[0] or bb[2] <= ba[0] or ba[3] <= bb[1] or bb[3] <= ba[1]
            assert apart, (a, b)


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


def test_the_teaser_waits_for_the_owners_name_check(monkeypatch):
    """Decision 082: the owner checks the name (SAIP, app stores, X) before the teaser. Until data/waddah.json says
    public, the live site has no band, no /waddah and no sitemap entry; WADIH_SHOW_DRAFTS shows it locally."""
    monkeypatch.setitem(main.waddah, "public", False)
    monkeypatch.setattr(main, "SHOW_DRAFTS", False)
    assert 'class="waddah-band"' not in client.get("/").text
    assert client.get("/waddah").status_code == 404 and client.get("/en/waddah").status_code == 404
    monkeypatch.setattr(main, "SHOW_DRAFTS", True)
    assert 'class="waddah-band"' in client.get("/").text


@pytest.fixture
def teaser_public(monkeypatch):
    monkeypatch.setitem(main.waddah, "public", True)


@pytest.mark.parametrize("prefix", ["", "/en"])
def test_waddah_is_only_a_teaser_until_launch(prefix, teaser_public):
    """Decision 084: no page and no details before launch. A /waddah link already shared lands on the homepage's
    teaser (a temporary redirect: the page comes back with the guide), and the sitemap doesn't list it."""
    r = client.get(prefix + "/waddah", follow_redirects=False)
    assert r.status_code == 302 and r.headers["location"].endswith(f"{prefix}/#waddah")
    assert "/waddah</loc>" not in client.get("/sitemap.xml").text
    assert not (main.APP_DIR / "templates" / "waddah.html").exists()
    for key in ("promises", "wont_ar", "examples_ar", "faq"):  # the page's details aren't published, even as data
        assert key not in main.waddah


def test_the_teaser_band_is_on_the_homepage_with_todays_dawn(monkeypatch, teaser_public):
    on(monkeypatch, 2026, 11, 20)
    html = client.get("/").text
    band = html.split('class="waddah-band"')[1].split("</section>")[0]
    assert f'--dawn: {main.waddah_dawn(datetime.date(2026, 11, 20))}' in band
    assert 'id="waddah"' in html.split('class="waddah-band"')[0][-200:]
    assert "/waddah" not in band and "<a " not in band  # nothing to open yet
    assert "فيجيبك من المصادر الرسمية" not in band and main.waddah["teaser"]["line_ar"] in band
    # What وضّاح will do, drawn: a student and three agents, each with the light on its antenna; no faces.
    art = band.split('class="waddah-help"')[1].split("</svg>")[0]
    assert art.count('class="agent"') == 3 and art.count('class="agent-light"') == 3
    assert 'class="help-head"' in art


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


# ---------- the eval seed (docs/specs/eval-seed.json, agent.md §8) ----------

def test_every_eval_question_points_at_a_section_that_exists():
    seed = json.loads((main.APP_DIR.parent / "docs" / "specs" / "eval-seed.json").read_text(encoding="utf-8"))
    ids = [q["id"] for q in seed["questions"]]
    assert len(ids) == len(set(ids))
    for q in seed["questions"]:
        assert q["kind"] in ("answer", "explorer", "no_date", "unknown", "refuse"), q["id"]
        if q["kind"] in ("answer", "explorer"):
            assert q["expected"], q["id"]
        for url in q["expected"]:
            path, _, anchor = url.partition("#")
            r = client.get(path)
            assert r.status_code == 200, (q["id"], url)
            if anchor:
                assert f'id="{anchor}"' in r.text, (q["id"], url)


def test_retrieval_already_finds_most_guide_questions():
    """agent.md §8: before any paid call, retrieval should find an expected section in its top 5 for the seed's
    answerable questions. A floor that rises as retrieval improves (measured 23/28 on 2026-11-07), not the launch bar."""
    seed = json.loads((main.APP_DIR.parent / "docs" / "specs" / "eval-seed.json").read_text(encoding="utf-8"))
    guide = [q for q in seed["questions"] if q["kind"] == "answer"]
    found = sum(1 for q in guide if any(r["url"] in q["expected"] for r in main.site_search.retrieve(q["q_ar"])))
    assert found / len(guide) >= 0.8, f"{found}/{len(guide)}"
    # A whole question finds sections where the strict site search finds none.
    assert not main.site_search.search("هل أستطيع التقديم على مسار الرواد وأنا في ثالث ثانوي؟")
    assert main.site_search.retrieve("هل أستطيع التقديم على مسار الرواد وأنا في ثالث ثانوي؟")


def test_now_says_so_when_nothing_is_open(monkeypatch):
    """An empty «الآن»: a plain sentence, no bare zero, and no «لم يفتح بعد» heading over nothing."""
    monkeypatch.setattr(main, "status_board", lambda: {"open": [], "waiting": [], "recent": []})
    html = client.get("/").text.split('id="now"')[1].split("</section>")[0]
    assert "لا يوجد الآن برنامج نتابعه مفتوحًا للتقديم." in html
    assert 'id="now-upcoming-3"' not in html and ">0<" not in html.replace(" ", "")
    en = client.get("/en/").text.split('id="now"')[1].split("</section>")[0]
    assert "None of the programs we follow is open for applications right now." in en


def test_the_teaser_in_english_is_english(teaser_public):
    """The English homepage's band, checked here whether or not the teaser is public on the live site."""
    html = client.get("/en/").text
    assert not arabic_outside_lang_ar(html), arabic_outside_lang_ar(html)[:5]
    assert "is coming in December" in html and "ask it about scholarships, universities and tests." in html
