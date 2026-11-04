"""«جرّب قبل أن تقرر» and the «لم تقرر بعد؟» guide (decision 069).

The activity is an exploration, not a test: these tests pin down the rules a student can read on the result
page, that nothing is stored or put in a URL, that it stays hidden on the live site while it's a draft, and that
the English page is fully English.
"""

import re
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient

import app.main as main
from app import exploration as ex
from scripts.english_leaks import arabic_outside_lang_ar

client = TestClient(main.app)
FORM = {"content-type": "application/x-www-form-urlencoded"}


@pytest.fixture
def drafts(monkeypatch):
    monkeypatch.setattr(main, "SHOW_DRAFTS", True)


@pytest.fixture
def live(monkeypatch):
    monkeypatch.setattr(main, "SHOW_DRAFTS", False)


def post(data, prefix=""):
    return client.post(f"{prefix}/explore/result", content=urlencode(data, doseq=True), headers=FORM)


def answers_for(field, answer):
    return {f"a-{a['id']}": answer for a in ex.DATA["activities"] if a["field"] == field}


# ---------- the data ----------

def test_data_hangs_together():
    fields = set(ex.FIELDS)
    tracks = {t["name_ar"] for t in main.school_tracks["tracks"]}
    assert len(fields) == 10  # UNESCO's broad fields, as in the research note
    for f in ex.DATA["fields"]:
        assert sum(a["field"] == f["id"] for a in ex.DATA["activities"]) >= 2, f["id"]
        assert set(f["tracks"]) <= tracks and "المسار العام" in f["tracks"], f["id"]
        assert len(f["try_ar"]) >= 1
        if f.get("guide_field"):
            assert main.explorer.field("emdad", f["guide_field"]), f["id"]
        else:
            assert f["name_ar"], f["id"]  # health and education: not in the Ministry's guide
        for pid in f.get("programs", []):
            assert pid in main.paths_by_id
    for s in ex.DATA["subjects"]:
        assert set(s["fields"]) <= fields, s["id"]
    assert len({a["id"] for a in ex.DATA["activities"]}) == len(ex.DATA["activities"])
    assert {a["group"] for a in ex.DATA["answers"]} == {"tried", "untried"}


def test_health_and_education_are_the_fields_the_guide_does_not_list():
    """The Ministry's 2026–2027 guide has no health or education field (read 2026-11-04): the result says so
    instead of dropping them."""
    guide = {fid for (track, fid) in main.explorer.fields if track == "emdad"}
    missing = {f["id"] for f in ex.DATA["fields"] if not f.get("guide_field")}
    assert missing == {"health", "education"}
    assert not missing & guide


def test_activities_never_ask_the_same_field_twice_in_a_row():
    order = [a["field"] for a in ex.activities()]
    assert len(order) == len(ex.DATA["activities"])
    assert all(a != b for a, b in zip(order, order[1:]))


def test_it_stays_a_draft_until_reviewed():
    """Flip this only after the counsellor review and the student test (decision 069)."""
    assert ex.DATA["draft"] is True and ex.DATA["expert_reviewed"] is False


# ---------- the rules ----------

def counts(**given):
    return {aid: given.get(aid, 0) for aid in ex.ANSWERS}


@pytest.mark.parametrize("given, progress, expected", [
    ({"enjoy": 2}, False, "draws"),
    ({"enjoy": 3}, False, "draws"),
    ({"enjoy": 2, "dislike": 1}, False, "try"),      # mixed: worth trying, not "draws"
    ({"enjoy": 1}, False, "try"),
    ({"curious": 1, "dislike": 2}, False, "try"),    # wanting to try counts
    ({"ok": 2}, True, "try"),                        # fine + progress in a close subject
    ({"ok": 3}, False, "not_now"),
    ({"dislike": 3}, False, "not_now"),
    ({"cold": 3}, False, "not_now"),
    ({}, False, "not_now"),
])
def test_bands(given, progress, expected):
    assert ex.band(counts(**given), progress) == expected


def test_parse_keeps_only_our_own_ids():
    body = urlencode({"a-first-aid": "enjoy", "a-nope": "enjoy", "a-design-poster": "maybe",
                      "difficulty": ["family", "evil"], "subject": ["math", "math"], "grade": "13",
                      "considered": "health"}, doseq=True).encode()
    choices = ex.parse(body)
    assert choices["answers"] == {"first-aid": "enjoy"}
    assert choices["difficulties"] == ["family"]
    assert choices["subjects"] == ["math"]
    assert choices["grade"] is None and choices["considered"] == "health"


def test_no_answers_means_try_first():
    r = ex.score(ex.parse(b""))
    assert r["nothing_yet"] and r["thin"] and r["tried"] == 0 and r["skipped"] == len(ex.DATA["activities"])
    assert not r["bands"]["draws"] and not r["bands"]["try"]


def test_enjoying_everything_says_the_answers_are_close():
    r = ex.score(ex.parse(urlencode({f"a-{a['id']}": "enjoy" for a in ex.DATA["activities"]}).encode()))
    assert r["many_draws"] and len(r["bands"]["draws"]) == 10 and not r["thin"]


def test_strongest_first_and_the_considered_field_apart():
    data = {**answers_for("engineering", "enjoy"), **answers_for("ict", "enjoy"), "subject": "digital",
            **answers_for("health", "cold"), "considered": "health"}
    r = ex.score(ex.parse(urlencode(data).encode()))
    draws = [f["id"] for f in r["bands"]["draws"]]
    assert draws[:2] == ["ict", "engineering"]  # same enjoyment; ICT first in the data's order, both have progress
    assert r["considered"]["id"] == "health" and r["considered"]["band"] == "not_now"
    assert "health" not in [f["id"] for band in r["bands"].values() for f in band]


# ---------- the pages ----------

def test_hidden_on_the_live_site(live):
    assert client.get("/explore").status_code == 404
    assert post({"a-first-aid": "enjoy"}).status_code == 404
    assert "/explore" not in client.get("/sitemap.xml").text
    assert 'href="/explore"' not in client.get("/resources/undecided").text


def test_form_works_without_javascript(drafts):
    r = client.get("/explore")
    assert r.status_code == 200
    html = r.text
    assert '<form class="explore-form" method="post" action="/explore/result"' in html
    assert html.count('data-auto id="q-') == len(ex.DATA["activities"])
    assert html.count('type="radio" name="a-') == len(ex.DATA["activities"]) * len(ex.DATA["answers"])
    assert 'name="robots" content="noindex"' in html  # a draft isn't for search engines
    assert "explore.js" in html


def test_result_explains_itself(drafts):
    data = {**answers_for("ict", "enjoy"), **answers_for("arts-humanities", "curious"),
            "difficulty": "family", "grade": "10", "considered": "education"}
    r = post(data)
    assert r.status_code == 200
    html = r.text
    assert 'name="robots" content="noindex"' in html
    assert "تجذبك الآن" in html and "تستحق التجربة" in html and "المجال الذي ذكرته" in html
    assert "/universities?track=emdad&amp;field=ict" in html          # its majors and universities
    assert 'href="/programs/sdaia-ai-scholarship"' in html            # a program for one of its majors
    assert "لا يذكر دليل الوزارة لقوائم الجامعات 2026–2027 هذا المجال" in html  # education
    assert 'href="/resources/undecided#family"' in html               # the family tip
    assert 'href="/grades/grade-10#tracks"' in html                   # grade 10's next step
    assert main.explorer.source["url"] in html and main.school_tracks["source"]["url"] in html
    text = re.sub(r"<[^>]+>", " ", html.split("<main", 1)[1].split("</main>", 1)[0])  # the words, not the links
    assert not re.search(r"\d+\s*%", text)  # no percentages


def test_a_reload_starts_again(drafts):
    r = client.get("/explore/result", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/explore"


def test_nothing_is_stored_or_put_in_a_url():
    js = (main.APP_DIR / "static" / "explore.js").read_text(encoding="utf-8")
    assert "localStorage" not in js and "sessionStorage" not in js and "fetch(" not in js
    assert 'method="post"' in (main.APP_DIR / "templates" / "explore.html").read_text(encoding="utf-8")


def test_oversized_posts_are_refused(drafts):
    r = client.post("/explore/result", content=b"a=" + b"x" * (ex.MAX_BODY + 1), headers=FORM)
    assert r.status_code == 413
    # Sent without a length (chunked), the body is still capped while it's read.
    chunks = (b"a=" + b"x" * 1000 for _ in range(ex.MAX_BODY // 1000 + 2))
    assert client.post("/explore/result", content=chunks, headers=FORM).status_code == 413
    bad = client.post("/explore/result", content=b"a=b", headers={**FORM, "content-length": "abc"})
    assert bad.status_code in (400, 413)  # a bad length is refused, never a server error


def every_answer():
    """Every activity answered (all five answers used), every difficulty, subject and grade 12: the result then
    shows every field's text, every tip and every answer label."""
    labels = list(ex.ANSWERS)
    data = {f"a-{a['id']}": labels[i % len(labels)] for i, a in enumerate(ex.DATA["activities"])}
    return {**data, "difficulty": list(ex.DIFFICULTIES), "subject": list(ex.SUBJECTS), "grade": "12"}


def test_english_pages_are_english(drafts):
    form = client.get("/en/explore").text
    assert 'action="/en/explore/result"' in form
    pages = [form] + [post({**every_answer(), "considered": fid}, prefix="/en").text for fid in ("", "health", "ict")]
    for grade in ("10", "11"):
        pages.append(post({**every_answer(), "grade": grade}, prefix="/en").text)
    for html in pages:
        assert '<html lang="en" dir="ltr"' in html
        assert not arabic_outside_lang_ar(html), arabic_outside_lang_ar(html)[:5]
    shown = "\n".join(pages)
    for f in ex.DATA["fields"]:  # every field's ideas reached an English page, in English
        for idea in f["try_ar"]:
            assert main.i18n.lookup(idea) and main.i18n.lookup(idea) in shown.replace("&#39;", "'"), idea


# ---------- the guide ----------

def test_the_guide_is_public_and_routes_onward(live):
    r = client.get("/resources/undecided")
    assert r.status_code == 200
    for href in ("/grades/grade-10#tracks", "/universities?track=emdad&amp;field=ict", "#family", "#not-the-same"):
        assert href in r.text, href
    assert "moe.gov.sa" in r.text  # the official handbook and track pages
    assert '/resources/undecided"' in client.get("/").text  # in the homepage's guides (absolute links there)
    assert 'href="/resources/undecided"' in client.get("/grades/grade-10").text


def test_the_guide_opens_the_activity_when_it_is_public(drafts):
    assert 'href="/explore"' in client.get("/resources/undecided").text
