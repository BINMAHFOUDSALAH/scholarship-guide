"""Redesign v3: the question «أريد دراسة X في Y», its answer (app/answer.py), /api/answer, and «قارن» (app/compare.py).

The answer keeps the scholarship's two gates apart on every university: 1 the track's list for the major, 2 the
university's own admission (the Saudi certificate, English, the next deadline). Every fact comes from data/ with its
source; an unknown is said, never guessed.
"""

import re

import pytest
from fastapi.testclient import TestClient

import app.main as main
from app import answer, compare

client = TestClient(main.app)
ex = main.explorer
CS_UK = "أريد دراسة علوم الحاسب في بريطانيا. من أين أبدأ؟"


def build(q="", country="", today="2026-11-26"):
    return answer.build(ex.search(q=q, country=country), ex, main.CUSTODIAN_TRACKS, main.PREP_YEAR_FACT, today=today)


# ---------- reading the question ----------

@pytest.mark.parametrize("text, q, country", [
    (CS_UK, "علوم الحاسب", "GB"),
    ("علوم الحاسب في بريطانيا", "علوم الحاسب", "GB"),
    ("I want to study computer science in the UK", "computer science", "GB"),
    ("أبغى أدرس هندسة في ألمانيا", "هندسة", "DE"),
    ("الذكاء الاصطناعي في أمريكا", "الذكاء الاصطناعي", "US"),
    ("جامعات كوريا الجنوبية", "", "KR"),
    ("بريطانيا", "", "GB"),
])
def test_a_typed_question_is_read_into_its_major_and_country(text, q, country):
    assert answer.parse(text, ex) == {"q": q, "country": country}
    r = ex.search(q=text)
    assert r["q"] == q and r["country"] == country and r["parsed"]["from"] == text


def test_the_subject_keeps_the_students_spelling():
    """The slot shows «هندسة» as typed, not the search key «هندسه»."""
    assert answer.parse("أريد دراسة هندسة في ألمانيا", ex)["q"] == "هندسة"


@pytest.mark.parametrize("text", ["Stanford", "جامعة ستانفورد", "هندسة البرمجيات", "طب", "علوم الحاسب"])
def test_majors_universities_and_health_words_are_searched_as_before(text):
    assert ex.search(q=text)["parsed"] is None


def test_a_question_we_cant_read_is_not_guessed():
    assert answer.parse("ماذا أفعل؟", ex) is None
    assert ex.search(q="ماذا أفعل")["parsed"] is None


def test_the_question_that_found_nothing_now_has_its_answer():
    """2026-11-26: «علوم الحاسب في بريطانيا» was a name search with no result."""
    html = client.get("/universities", params={"q": CS_UK}).text
    assert "لا توجد جامعة بهذا الاسم" not in html
    assert 'data-parsed-q="علوم الحاسب"' in html and 'data-parsed-country="GB"' in html
    assert html.count('class="acard"') == build("علوم الحاسب", "GB")["total"] == 7


# ---------- the answer ----------

def test_computer_science_in_the_uk_groups_universities_by_why_they_appear():
    a = build("علوم الحاسب", "GB")
    assert a["kind"] == "major" and a["country"] == "GB" and a["major_ar"] == "البرمجة وعلوم الحاسب"
    tracks = [(g["track"], (g["field"] or {}).get("id"), g["count"]) for g in a["groups"]]
    assert tracks == [("arruaad", None, 4), ("emdad", "ict", 3)]
    arruaad, emdad = a["groups"]
    assert arruaad["source"]["url"] == "https://sites.moe.gov.sa/scholarship-program/conditions/info-6/"
    assert emdad["source"]["url"] == ex.source["url"] and "البرمجة وعلوم الحاسب" in emdad["why_ar"]
    for g in a["groups"]:
        for i in g["items"]:
            assert any(l["track"] == g["track"] and l["rank"] == i["rank"] for l in i["university"]["listings"])
            assert i["university"]["country"] == "GB"


def test_each_card_keeps_the_admission_facts_with_their_sources():
    a = build("علوم الحاسب", "GB")
    cards = {i["id"]: i for g in a["groups"] for i in g["items"]}
    edinburgh = cards["the-university-of-edinburgh"]
    assert edinburgh["certificate"]["state"] == "no" and edinburgh["certificate"]["source_url"].startswith("https://www.ed.ac.uk/")
    assert edinburgh["deadline"]["state"] == "upcoming" and edinburgh["deadline"]["date"] == "2027-01-13"
    assert edinburgh["deadline"]["source_url"]
    # Oxford and Cambridge closed for 2027 entry on 15 October 2026: said, not hidden.
    for uid in ("university-of-oxford", "university-of-cambridge"):
        assert cards[uid]["deadline"]["state"] == "passed" and cards[uid]["deadline"]["date"] == "2026-10-15"
    # A UK university whose pages we haven't read on the Saudi certificate says so.
    assert cards["imperial-college-london"]["certificate"]["state"] == "unknown"
    assert a["foundation"] and a["prep_fact"]["id"] == "prep-year"
    assert a["soonest"]["deadline"]["date"] == "2027-01-13"


def test_the_card_shows_both_gates_and_the_unknowns():
    html = client.get("/universities", params={"q": "علوم الحاسب", "country": "GB"}).text
    card = html.split('data-acard="university-of-oxford"')[1].split("</li>")[0]
    assert "الابتعاث" in card and "القبول" in card and "المرتبة 6" in card
    assert "لا تكفي وحدها للسنة الأولى" in card and "انتهى لـخريف 2027 في" in card
    imperial = html.split('data-acard="imperial-college-london"')[1].split("</li>")[0]
    assert "لم نجد حكمها في صفحاتها" in imperial
    # The foundation-year rule, with its source, in the next step.
    nxt = html.split('class="next"')[1].split("</section>")[0]
    assert "90%" in nxt and "5.5" in nxt and main.PREP_YEAR_FACT["sources"][0]["url"] in nxt
    assert nxt.index("قدّم على الجامعات أولًا") < nxt.index("احصل على قبول غير مشروط") < nxt.index("قدّم على الابتعاث بقبولك")


def test_country_chips_count_the_same_major_elsewhere():
    a = build("علوم الحاسب")
    counts = {f["code"]: f["count"] for f in a["facets"]}
    assert counts["GB"] == 7 and sum(counts.values()) == a["total"]
    assert [f["count"] for f in a["facets"]] == sorted((f["count"] for f in a["facets"]), reverse=True)


def test_an_empty_list_is_one_line_not_an_empty_group():
    a = build("هندسة", "DE")
    assert all(g["count"] for g in a["groups"])
    assert {"track": "arruaad", "field": None} in a["empty"]
    html = client.get("/universities", params={"q": "هندسة", "country": "DE"}).text
    assert "لا جامعة في ألمانيا في قائمة الرواد." in html


def test_a_country_alone_shows_rawwad_there_and_emdads_fields():
    a = build("", "GB")
    assert a["kind"] == "country" and [g["track"] for g in a["groups"]] == ["arruaad"]
    assert a["fields"] and all(f["count"] and "country=GB" in f["href"] for f in a["fields"])


@pytest.mark.parametrize("params", [{"q": "Stanford"}, {"track": "arruaad"}, {"track": "waaid"},
                                    {"country": "GB", "lang": "other"}])
def test_other_searches_keep_their_own_views(params):
    assert main.answer_for(ex.search(**{("language" if k == "lang" else k): v for k, v in params.items()})) is None


def test_the_answer_api_is_data_with_sources_and_actions():
    """/api/answer: the same answer as plain data for وضّاح: ids, facts with sources, and the student's actions."""
    data = client.get("/api/answer", params={"q": CS_UK}).json()
    assert data["query"]["read_as"]["country"] == "GB"
    a = data["answer"]
    assert a["total"] == 7 and [g["track"] for g in a["groups"]] == ["arruaad", "emdad"]
    item = a["groups"][1]["items"][0]
    assert item["list"]["track"] == "emdad" and item["list"]["field"] == "ict"
    assert {x["type"] for x in item["actions"]} == {"open", "save", "compare"}
    assert {"type": "save", "item": {"type": "university", "id": item["id"]}} in item["actions"]
    assert a["foundation_rule"]["sources"][0]["url"].startswith("https://sites.moe.gov.sa/")
    assert client.get("/api/answer", params={"q": "Stanford"}).json()["answer"] is None


def test_the_homepage_answer_updates_from_its_own_route():
    html = client.get("/answer", params={"q": "علوم الحاسب في بريطانيا"}).text
    assert 'data-parsed-q="علوم الحاسب"' in html and html.count('class="acard"') == 6  # three per group, compact
    assert "/universities?q=" in html and "country=GB" in html
    miss = client.get("/answer", params={"q": "شيء لا يوجد"}).text
    assert "لم نجد «شيء لا يوجد»" in miss and "/search?q=" in miss
    names = client.get("/answer", params={"q": "Stanford"}).text
    assert "/universities/stanford-university" in names


def test_the_answer_in_english_is_english():
    html = client.get("/en/universities", params={"q": "computer science in the UK"}).text
    assert 'data-parsed-country="GB"' in html
    answer_part = html.split('class="answer-head"')[1].split('class="next"')[0]
    assert "universities in the United Kingdom" in answer_part and "Admission" in answer_part
    assert not re.search(r">[^<]*[؀-ۿ][^<]*<", answer_part.split("<bdi")[0])


# ---------- «قارن» ----------

def test_compare_ids_are_cleaned_and_capped():
    raw = "university-of-oxford,nope,university-of-oxford,ucl-university-college-london,a,b,harvard-university,mit,stanford-university,yale-university"
    assert compare.ids_from(raw, ex) == ["university-of-oxford", "ucl-university-college-london", "harvard-university",
                                         "stanford-university"]


def test_the_comparison_keeps_the_two_gates_and_every_source():
    uids = ["university-of-cambridge", "imperial-college-london", "the-university-of-edinburgh"]
    c = compare.build(uids, ex, answer, "2026-11-26")
    groups = {g["id"]: g for g in c["groups"]}
    assert groups["lists"]["gate"] == 1 and groups["admission"]["gate"] == 2
    cert = next(r for r in groups["admission"]["rows"] if r["label_ar"] == "الثانوية السعودية للسنة الأولى")
    assert [x["state"] for x in cert["cells"]] == ["no", "unknown", "no"]
    country = next(r for r in groups["place"]["rows"] if r["label_ar"] == "الدولة")
    assert country["same"]
    for g in c["groups"]:
        for r in g["rows"]:
            assert len(r["cells"]) == 3
    html = client.get("/compare?u=" + ",".join(uids)).text
    assert html.count('scope="col"') == 3 and "data-same" in html and 'class="compare-diff-input"' in html
    # Each value names its row and its university for screen readers.
    assert re.search(r'headers="cg-admission r-admission-\d+ col-imperial-college-london"', html)
    assert 'name="robots" content="noindex"' in html


def test_the_comparison_page_says_what_to_do_when_empty_or_alone():
    assert "لم تختر جامعات بعد." in client.get("/compare").text
    assert "أضف جامعة أخرى على الأقل" in client.get("/compare?u=university-of-oxford").text
    assert client.get("/compare?u=../../etc,<script>").status_code == 200


def test_the_finder_shows_the_country_as_a_chip_you_can_remove():
    """2026-11-27: with the answer showing, «بريطانيا» was only in the sentence; the chip says it and clears it."""
    html = client.get("/universities", params={"q": "علوم الحاسب", "country": "GB", "track": "emdad"}).text
    applied = html.split('class="applied"')[1].split("</ul>")[0]
    assert 'data-remove="country"' in applied and "بريطانيا" in applied
    assert 'data-remove="q"' in applied and 'data-remove="track field"' in applied
    assert "مسح الكل" in applied


def test_the_homepage_answer_route_starts_with_the_overview():
    html = client.get("/answer").text
    assert f'<span class="answer-count">{len(ex.universities)}</span>' in html and 'data-set-country="US"' in html


def test_cards_and_the_university_page_offer_compare_and_save():
    html = client.get("/universities", params={"q": "علوم الحاسب", "country": "GB"}).text
    assert html.count('class="compare-toggle"') == 7 and html.count('class="save-mini"') == 7
    page = client.get("/universities/the-university-of-edinburgh").text
    assert 'data-compare="the-university-of-edinburgh"' in page and 'class="uni-gates"' in page
    assert "لا تكفي وحدها للسنة الأولى" in page


def test_the_plan_offers_to_compare_its_universities(monkeypatch):
    plan = {"items": [{"type": "university", "id": "university-of-oxford", "status": "thinking"},
                      {"type": "university", "id": "the-university-of-edinburgh", "status": "preparing"}]}
    html = client.post("/my-plan", json=plan).text
    hub = html.split('<template data-plan-part="hub">')[1].split("</template>")[0]
    assert "/compare?u=university-of-oxford,the-university-of-edinburgh" in hub


def test_explore_results_ask_the_question_for_a_major():
    view = main.exploration.field_view("ict", ex, main.school_tracks) if "ict" in main.exploration.FIELDS else None
    if view is None or not view.get("ask_majors"):
        pytest.skip("no ICT field in the activity")
    assert all(ex.matching_majors(m) for m in view["ask_majors"])
