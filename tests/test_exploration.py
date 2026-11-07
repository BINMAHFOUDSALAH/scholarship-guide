"""«جرّب قبل أن تقرر» and the «لم تقرر بعد؟» guide (decisions 069, 088).

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
from app import i18n
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
    return {f"a-{a['id']}": answer for a in ex.DATA["activities"] if field in a["fields"]}


# ---------- the data ----------

def test_data_hangs_together():
    fields = set(ex.FIELDS)
    tracks = {t["name_ar"] for t in main.school_tracks["tracks"]}
    assert len(fields) == 10  # UNESCO's broad fields, as in the research note
    for f in ex.DATA["fields"]:
        assert sum(f["id"] in a["fields"] for a in ex.DATA["activities"]) >= 2, f["id"]
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
    assert all(1 <= len(a["fields"]) <= 3 and set(a["fields"]) <= fields for a in ex.DATA["activities"])


def test_fifteen_questions_three_answers():
    """Decision 088 (owner, 2026-11-07): 15 questions, 14 activities and the subjects; three answers; no grade, no
    "what makes it hard", no field the family expects."""
    assert len(ex.DATA["activities"]) == 14
    assert [a["label_ar"] for a in ex.DATA["answers"]] == ["يعجبني", "لا بأس", "لا يجذبني"]
    assert not {"difficulties", "grades"} & set(ex.DATA)
    html = client.get("/explore").text
    assert html.count("data-step") == 15
    assert 'name="grade"' not in html and 'name="difficulty"' not in html and 'name="considered"' not in html


def test_health_and_education_are_the_fields_the_guide_does_not_list():
    """The Ministry's 2026–2027 guide has no health or education field (read 2026-11-04): the result says so
    instead of dropping them."""
    guide = {fid for (track, fid) in main.explorer.fields if track == "emdad"}
    missing = {f["id"] for f in ex.DATA["fields"] if not f.get("guide_field")}
    assert missing == {"health", "education"}
    assert not missing & guide


def test_activities_cover_holland_s_six_types_and_move_round_them():
    """Short interest measures spread their items over Holland's six types (O*NET Mini-IP, 18REST; decision 088):
    every type is asked, none more than three times, and no type comes twice in a row."""
    order = [a["type"] for a in ex.activities()]
    assert set(order) == set("RIASEC")
    assert max(order.count(t) for t in "RIASEC") <= 3
    assert all(a != b for a, b in zip(order, order[1:]))


def test_every_field_has_a_clear_title_and_real_majors():
    """Decision 073: a plain title and up to four example majors for each card. Every name is real: from the Ministry's
    guide (checked here against the guide's own list) or, where the guide has none or one, from the Ministry's Saudi
    unified classification (read directly, docs/research/field-majors-classification-2026-11.md)."""
    titles = [f["title_ar"] for f in ex.DATA["fields"]]
    assert all(titles) and len(set(titles)) == len(titles)
    sources = {s.get("id") for s in ex.DATA["sources"]}
    for f in ex.DATA["fields"]:
        assert 1 <= len(f["majors_ar"]) <= 4, f["id"]
        if f["majors_from"] == "guide":
            assert set(f["majors_ar"]) <= set(ex.guide_majors(main.explorer, f["guide_field"])), f["id"]
        else:
            assert f["majors_from"] == "classification" and "classification" in sources, f["id"]
    from_classification = {f["id"] for f in ex.DATA["fields"] if f["majors_from"] == "classification"}
    assert from_classification == {"health", "education", "arts-humanities"}  # the guide has too little for these


def field_tones(fid):
    """A field's five tones, from its .tone-<id> rule in style.css (decision 075): the one source of its colours."""
    css = (main.APP_DIR / "static" / "style.css").read_text(encoding="utf-8")
    rule = re.search(r"\.tone-%s \{([^}]*)\}" % re.escape(fid), css)
    assert rule, f"no .tone-{fid} in style.css"
    return dict(re.findall(r"--tone(?:-([a-z]+))?:\s*(#[0-9a-f]{6})", rule.group(1)))


@pytest.mark.parametrize("fid", list(ex.FIELDS))
def test_every_field_has_its_picture_and_nothing_else_comes_with_it(fid):
    """Our own drawings (decision 073): one shape, each in its field's own tones and paper (decision 075), and
    self-contained, so no third-party request and no script can ever come with a picture on a minor's result page."""
    svg = (main.APP_DIR / "static" / "img" / "fields" / f"{fid}.svg").read_text(encoding="utf-8")
    assert svg.startswith("<svg ") and 'viewBox="0 -85 640 490"' in svg  # phones show the middle 640x320
    assert not re.search(r"<(script|image|foreignObject|text|style)\b|\bon\w+=", svg), fid
    assert not re.findall(r'(?:href|src)="(?!#)', svg), fid
    assert not re.findall(r"url\(", svg), fid
    tones = field_tones(fid)
    assert set(tones) == {"", "deep", "mid", "light", "glow"}, fid
    assert set(c.lower() for c in re.findall(r"#[0-9a-fA-F]{6}\b", svg)) <= set(tones.values()) | {"#f6f4ee"}, fid
    assert f'<rect y="-85" width="640" height="490" fill="{tones[""]}"/>' in svg, fid  # drawn on the field's ground


def test_every_field_has_a_tone_of_its_own():
    """Ten fields, ten grounds: no two fields share a colour, and none is the brand's forest, lime or amber, which
    mean "act", "now" and "restriction" (decision 075)."""
    grounds = [field_tones(fid)[""] for fid in ex.FIELDS]
    assert len(set(grounds)) == len(grounds)
    assert not set(grounds) & {"#184b3a", "#d8ed9b", "#774c0c", "#e0b26a"}


def test_published_and_the_review_still_recorded_as_to_come():
    """Published by the owner before the counsellor review (decision 070); the data keeps saying so."""
    assert ex.DATA["draft"] is False and ex.DATA["expert_reviewed"] is False


# ---------- the rules ----------

def counts(**given):
    return {aid: given.get(aid, 0) for aid in ex.ANSWERS}


@pytest.mark.parametrize("given, progress, expected", [
    ({"enjoy": 2}, False, "draws"),
    ({"enjoy": 3}, False, "draws"),
    ({"enjoy": 2, "dislike": 1}, False, "try"),      # mixed: worth trying, not "draws"
    ({"enjoy": 1}, False, "try"),
    ({"enjoy": 1}, True, "draws"),                   # liked + progress in a close subject
    ({"enjoy": 1, "dislike": 1}, True, "try"),
    ({"ok": 1}, False, "try"),                       # «لا بأس»: worth trying
    ({"ok": 1, "dislike": 2}, False, "try"),
    ({"dislike": 3}, False, "not_now"),
    ({}, True, "not_now"),
])
def test_bands(given, progress, expected):
    assert ex.band(counts(**given), progress) == expected


def test_parse_keeps_only_our_own_ids():
    body = urlencode({"a-care-someone": "enjoy", "a-nope": "enjoy", "a-design-poster": "maybe",
                      "subject": ["math", "math", "evil"], "grade": "12"}, doseq=True).encode()
    choices = ex.parse(body)
    assert choices == {"answers": {"care-someone": "enjoy"}, "subjects": ["math"]}


def test_no_answers_means_try_first():
    r = ex.score(ex.parse(b""))
    assert r["nothing_yet"] and r["thin"] and r["answered"] == 0 and r["skipped"] == len(ex.DATA["activities"])
    assert not r["bands"]["draws"] and not r["bands"]["try"]


def test_enjoying_everything_draws_every_field():
    r = ex.score(ex.parse(urlencode({f"a-{a['id']}": "enjoy" for a in ex.DATA["activities"]}).encode()))
    assert len(r["bands"]["draws"]) == 10 and not r["thin"] and not r["nothing_yet"]


def test_strongest_first():
    data = {**answers_for("ict", "enjoy"), "subject": "digital", "a-care-someone": "dislike"}
    r = ex.score(ex.parse(urlencode(data).encode()))
    assert [f["id"] for f in r["bands"]["draws"]] == ["ict", "engineering"]  # three liked, then two; both have progress
    assert [f["id"] for f in r["bands"]["try"]] == ["business-law", "natural-sciences"]  # one liked each: data order
    assert "health" in [f["id"] for f in r["bands"]["not_now"]]
    assert len([f for band in r["bands"].values() for f in band]) == 10


def field_of(data, fid):
    r = ex.score(ex.parse(urlencode(data, doseq=True).encode()))
    return next(f for band in r["bands"].values() for f in band if f["id"] == fid)


@pytest.mark.parametrize("data, expected", [
    ({"a-take-apart": "enjoy"}, "لأنك تحب تفكيك جهاز أو إصلاحه لمعرفة كيف يعمل."),
    ({"a-take-apart": "enjoy", "a-data-table": "enjoy", "subject": "digital"},
     "لأنك تحب تفكيك جهاز أو إصلاحه لمعرفة كيف يعمل، وترتيب بيانات في جدول ومراجعتها بدقة، ولاحظت تقدمك في الحاسب والتقنية الرقمية."),
    ({"a-take-apart": "enjoy", "a-data-table": "enjoy", "a-hard-problem": "enjoy"},
     "لأنك تحب تفكيك جهاز أو إصلاحه لمعرفة كيف يعمل، وترتيب بيانات في جدول ومراجعتها بدقة، ونشاطًا آخر منه."),
    ({"a-take-apart": "enjoy", "a-data-table": "ok"}, "لأنك تحب تفكيك جهاز أو إصلاحه لمعرفة كيف يعمل."),
    ({"a-data-table": "ok"}, "لأنك قلت «لا بأس» عن ترتيب بيانات في جدول ومراجعتها بدقة."),
    ({"a-data-table": "ok", "a-hard-problem": "ok"},
     "لأنك قلت «لا بأس» عن ترتيب بيانات في جدول ومراجعتها بدقة، وحل مسألة صعبة في الرياضيات أو البرمجة."),
    ({"a-data-table": "dislike", "subject": ["math", "digital"]}, "لأنك لاحظت تقدمك في الرياضيات والحاسب والتقنية الرقمية."),
])
def test_why_is_one_short_sentence_from_the_students_own_answers(data, expected):
    assert ex.why_text(field_of(data, "ict")) == expected


def test_why_in_english():
    data = {"a-take-apart": "enjoy", "a-data-table": "ok", "subject": ["math", "digital"]}
    with i18n.use_lang("en"):
        assert ex.why_text(field_of(data, "ict")) == ("You like taking apart or fixing a device to see how it works. "
                                                      "You've noticed your progress in: Mathematics, Computing and digital technology.")
        assert ex.why_text(field_of({"a-data-table": "ok"}, "ict")) == (
            "You said \u201cit's okay\u201d to organising data in a table and checking it carefully.")


def test_the_lead_names_the_fields_clearly_in_both_languages():
    assert ex.list_text(["التقنية وعلوم الحاسب", "الهندسة والبناء"]) == "التقنية وعلوم الحاسب، والهندسة والبناء"
    with i18n.use_lang("en"):
        assert ex.list_text(["التقنية وعلوم الحاسب", "الهندسة والبناء"]) == "Technology and computer science; Engineering and construction"


# ---------- the pages ----------

def test_live_on_the_site(live):
    assert client.get("/explore").status_code == 200
    assert post({"a-care-someone": "enjoy"}).status_code == 200
    assert "/explore</loc>" in client.get("/sitemap.xml").text and "/en/explore</loc>" in client.get("/sitemap.xml").text
    assert 'href="/explore"' in client.get("/resources/undecided").text  # the guide's door
    home = client.get("/").text
    assert "لم تقرر ماذا تدرس؟" in home and '/explore"' in home  # the homepage's door, under the grades
    # Decision 083: the grades first, then the one box, then the smaller door for students who haven't decided.
    assert home.index('id="grades"') < home.index("hero-search") < home.index("hero-door")
    assert 'name="robots" content="noindex"' not in client.get("/explore").text  # public now: search engines may list it


def test_the_draft_switch_still_hides_it(live, monkeypatch):
    """Setting "draft": true again hides the page, its doors and its sitemap entry."""
    monkeypatch.setitem(ex.DATA, "draft", True)
    assert client.get("/explore").status_code == 404
    assert post({"a-care-someone": "enjoy"}).status_code == 404
    assert "/explore</loc>" not in client.get("/sitemap.xml").text
    assert 'href="/explore"' not in client.get("/resources/undecided").text
    assert "hero-door" not in client.get("/").text


def test_form_works_without_javascript(drafts):
    r = client.get("/explore")
    assert r.status_code == 200
    html = r.text
    assert '<form class="explore-form" method="post" action="/explore/result"' in html
    assert html.count('class="explore-step explore-card" data-step data-part="activity"') == len(ex.DATA["activities"])
    assert " checked" not in html.split("<form", 1)[1]  # no answer is ever chosen for the student
    assert html.count('type="radio" name="a-') == len(ex.DATA["activities"]) * len(ex.DATA["answers"])
    assert "explore.js" in html


def test_the_last_question_goes_straight_to_the_result():
    """No page between the answers and the result (decision 073): «السابق» changes an answer on the way."""
    html = client.get("/explore").text
    js = (main.APP_DIR / "static" / "explore.js").read_text(encoding="utf-8")
    assert "data-review" not in html and "راجع إجاباتك" not in html
    assert "غيّر" not in js and "buildReview" not in js
    assert '<button type="submit" class="btn btn--primary" data-submit>' in html  # shows without JavaScript too
    # A double tap must never send the form: the button appears where «التالي» was.
    assert "[data-submit]" in js.split("lockedUntil &&", 1)[1].split("\n", 1)[0]


def test_a_card_says_what_it_is_why_what_you_study_and_one_thing_to_do(drafts):
    html = post({**answers_for("ict", "enjoy"), **answers_for("health", "dislike"), **answers_for("arts-humanities", "ok"),
                 "subject": "digital"}).text
    card = html.split('id="field-ict"', 1)[1].split('<section class="explore-field', 1)[0]
    assert "/static/img/fields/ict.svg" in card and 'alt=""' in card  # the title says it; a screen reader needn't hear it twice
    assert "التقنية وعلوم الحاسب" in card                             # the plain title…
    assert "تقنية الاتصالات والمعلومات" in card                        # …and the guide's name beside the explorer link
    assert "لأنك تحب تفكيك جهاز" in card
    assert "الذكاء الاصطناعي" in card
    assert main.explorer.source["url"] in card                         # the majors' source beside them
    assert card.count("<summary") == 1 and "استكشف هذا المجال" in card  # one action
    assert "/universities?track=emdad&amp;field=ict" in card           # it leads on to the universities
    assert card.index("<summary") < card.index("جرّب هذا الأسبوع")     # the details come after the action
    # The first thing on the page says which fields; the counts that read like a score are gone.
    assert html.index("أقربها إليك الآن:") < html.index('id="draws-title"')
    assert "أنشطة جرّبتها" not in html and 'class="summary-list explore-counts"' not in html
    # The fields where the guide has none or one: the examples name their own source, and the card says so.
    classification = next(s["url"] for s in ex.DATA["sources"] if s.get("id") == "classification")
    arts = html.split('id="field-arts-humanities"', 1)[1].split('<section class="explore-field', 1)[0]
    assert classification in arts and "التاريخ" in arts
    assert "تخصصًا واحدًا: تصميم المنتجات" in arts
    # A field that doesn't draw the student gets no "because": there is none to give.
    health = html.split('id="field-health"', 1)[1].split('<section class="explore-field', 1)[0]
    assert "explore-field--compact" in html.split('id="field-health"', 1)[0].rsplit("<section", 1)[1]
    assert 'class="explore-field-why"' not in health and classification in health and "الطب" in health


def test_only_the_three_strongest_fields_of_a_band_stay_open(drafts):
    html = post({f"a-{a['id']}": "enjoy" for a in ex.DATA["activities"]}).text
    section = html.split('id="draws-title"', 1)[1]
    opened, folded = section.split('class="explore-more-fields"', 1)
    assert len(re.findall(FIELD_CARD, opened)) == 3 and len(re.findall(FIELD_CARD, folded)) == 7


def test_result_explains_itself(drafts):
    data = {**answers_for("ict", "enjoy"), **answers_for("arts-humanities", "ok"), "a-explain-lesson": "ok"}
    r = post(data)
    assert r.status_code == 200
    html = r.text
    assert 'name="robots" content="noindex"' in html
    assert "تجذبك الآن" in html and "تستحق التجربة" in html
    assert "/universities?track=emdad&amp;field=ict" in html          # its majors and universities
    assert 'href="/programs/sdaia-ai-scholarship"' in html            # a program for one of its majors
    assert "لا يذكر دليل الوزارة لقوائم الجامعات 2026–2027 هذا المجال" in html  # education
    assert 'href="/grades/grade-10#tracks"' in html                   # grade 10's next step, for whoever is there
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
    """Every activity answered (all three answers used) and every subject: the result then shows every field's text
    and every answer label."""
    labels = list(ex.ANSWERS)
    data = {f"a-{a['id']}": labels[i % len(labels)] for i, a in enumerate(ex.DATA["activities"])}
    return {**data, "subject": list(ex.SUBJECTS)}


def test_english_pages_are_english(drafts):
    form = client.get("/en/explore").text
    assert 'action="/en/explore/result"' in form
    pages = [form, post(every_answer(), prefix="/en").text]
    ict = [a["id"] for a in ex.DATA["activities"] if "ict" in a["fields"]]
    for answers in (["enjoy"], ["enjoy", "enjoy"], ["enjoy"] * 3, ["enjoy", "ok"], ["ok"], ["ok"] * 2, ["ok"] * 3):
        pages.append(post({f"a-{aid}": answer for aid, answer in zip(ict, answers)}, prefix="/en").text)
    pages.append(post({f"a-{ict[0]}": "ok", "subject": "math"}, prefix="/en").text)
    pages.append(post({f"a-{a['id']}": "enjoy" for a in ex.DATA["activities"]}, prefix="/en").text)  # «مجالات أخرى»
    for html in pages:
        assert '<html lang="en" dir="ltr"' in html
        assert not arabic_outside_lang_ar(html), arabic_outside_lang_ar(html)[:5]
    shown = "\n".join(pages).replace("&#39;", "'").replace("&amp;", "&")
    for f in ex.DATA["fields"]:  # every field's title, ideas and majors reached an English page, in English
        for text in [f["title_ar"], *f["try_ar"], *f["majors_ar"]]:
            assert main.i18n.lookup(text) and main.i18n.lookup(text) in shown, text


# ---------- the guide ----------

def test_the_guide_is_public_and_routes_onward(live):
    r = client.get("/resources/undecided")
    assert r.status_code == 200
    for href in ("/grades/grade-10#tracks", "/universities?track=emdad&amp;field=ict", "#family"):
        assert href in r.text, href
    assert "moe.gov.sa" in r.text  # the official handbook and track pages
    assert '/resources/undecided"' in client.get("/").text  # in the homepage's guides (absolute links there)
    assert 'href="/resources/undecided"' in client.get("/grades/grade-10").text


def test_the_guide_opens_the_activity_when_it_is_public(drafts):
    assert 'href="/explore"' in client.get("/resources/undecided").text


# ---------- the result page shows exactly what the rules say ----------

BAND_MARKERS = {'id="draws-title"': "draws", 'id="try-title"': "try",
                'class="explore-not-now"': "not_now", 'id="next-title"': None}
FIELD_CARD = r'<section class="explore-field[^"]*" id="field-([\w-]+)"'


def page_bands(html):
    """Field ids per band, in page order: each field belongs to the last band heading above it."""
    marks = sorted((html.index(m), band) for m, band in BAND_MARKERS.items() if m in html)
    bands = {"draws": [], "try": [], "not_now": []}
    for found in re.finditer(FIELD_CARD, html):
        band = [b for pos, b in marks if pos < found.start()][-1]
        bands[band].append(found.group(1))
    return bands


def test_result_page_matches_the_rules_for_random_students(live):
    """40 random students (fixed seed): every field sits in the band score() gives it, in its order, and each
    field's reasons are exactly its activities with the answers given, and only the three strongest of a band stay
    open (owner's check, 2026-11-04; decision 073 folds «تجذبك الآن» the same way)."""
    import random
    rng = random.Random(2026)
    choices = list(ex.ANSWERS) + [None]  # None = skipped
    for _ in range(40):
        data = {f"a-{a['id']}": v for a in ex.DATA["activities"] if (v := rng.choice(choices))}
        data["subject"] = rng.sample(list(ex.SUBJECTS), rng.randint(0, 3))
        html = post(data).text
        r = ex.score(ex.parse(urlencode(data, doseq=True).encode()))
        expected = {band: [f["id"] for f in fields] for band, fields in r["bands"].items()}
        shown = page_bands(html)
        assert shown["draws"] == expected["draws"], data
        assert shown["try"] == expected["try"], data
        assert shown["not_now"] == expected["not_now"], data
        for fields in r["bands"].values():
            for f in fields:
                block = html.split(f'id="field-{f["id"]}"', 1)[1].split('<section class="explore-field', 1)[0]
                reasons = re.findall(r'<span class="explore-why-activity">([^<]+)</span> '
                                     r'<span class="explore-answer explore-answer--\w+">([^<]+)</span>', block)
                assert reasons == [(w["activity_ar"], w["answer_ar"]) for w in f["why"]], (f["id"], data)
        for marker, ids in (('id="draws-title"', expected["draws"]), ('id="try-title"', expected["try"])):
            if not ids:  # an empty band has no heading
                assert marker not in html, data
                continue
            start = html.index(marker)
            end = min(html.index(m, start + 1) for m in BAND_MARKERS if m != marker and m in html[start + 1:])
            section = html[start:end]
            if len(ids) > 3:  # a shortlist: the three strongest open, the rest folded, in order
                opened, folded = section.split('class="explore-more-fields"', 1)
                assert re.findall(FIELD_CARD, opened) == ids[:3], data
                assert re.findall(FIELD_CARD, folded) == ids[3:], data
            else:
                assert 'class="explore-more-fields"' not in section, data
