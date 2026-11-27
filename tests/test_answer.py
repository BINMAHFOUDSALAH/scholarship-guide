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
    assert html.count('scope="col"') == 3 and "data-same" in html and "compare-diff-input" in html
    # Each value names its row and its university for screen readers.
    assert re.search(r'headers="cg-admission r-admission-\d+ col-imperial-college-london"', html)
    assert 'name="robots" content="noindex"' in html


def test_the_comparison_page_says_what_to_do_when_empty_or_alone():
    """2026-11-27: with nothing chosen, the page is where a student chooses: a name box with the site's suggestions
    (compare.js adds the university), which without JavaScript searches the Finder."""
    empty = client.get("/compare").text
    assert "اختر جامعتين للمقارنة" in empty and "data-compare-pick" in empty
    assert 'action="http://testserver/universities"' in empty or 'action="/universities"' in empty
    alone = client.get("/compare?u=university-of-oxford").text
    assert "أضف جامعة أخرى للمقارنة" in alone and "data-compare-pick" in alone
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


# ---------- 2026-11-27: the search kept, the comparison readable, programs found by name ----------

AI = "الذكاء الاصطناعي"


def test_a_university_opened_from_the_homepage_answer_leads_back_to_the_same_search():
    """The owner chose «الذكاء الاصطناعي في أمريكا», opened Harvard and pressed «الرجوع إلى نتائج البحث»: the link carried
    an empty `from`, so the Finder opened empty. Every university link in the live answer now carries the question."""
    html = client.get("/answer", params={"q": AI, "country": "US"}).text
    links = re.findall(r'href="[^"]*/universities/harvard-university(\?[^"]*)?"', html)
    assert links and all(l.startswith("?from=") and l != "?from=" for l in links)
    raw = re.search(r'/universities/harvard-university\?from=([^"]+)"', html).group(1)
    page = client.get("/universities/harvard-university?from=" + raw).text
    back = re.search(r'<a class="back-link" href="([^"]+)" data-back-link>', page).group(1)
    assert back.startswith("/universities?") and "country=US" in back
    assert "%D8%A7%D9%84%D8%B0%D9%83%D8%A7%D8%A1" in back  # the major, as the Finder reads it
    assert "الرجوع إلى نتائج البحث" in page


def test_the_finder_links_keep_the_major_the_country_and_the_filters():
    html = client.get("/universities", params={"q": "علوم الحاسب", "country": "GB", "track": "emdad"}).text
    m = re.search(r'class="uni-name" href="http://testserver(/universities/[a-z0-9-]+\?from=[^"]+)"', html)
    page = client.get(m.group(1).replace("&amp;", "&")).text
    back = re.search(r'<a class="back-link" href="([^"]+)" data-back-link>', page).group(1)
    assert "country=GB" in back and "track=emdad" in back and "q=" in back


def cell_of(c, label, uid):
    row = next(r for g in c["groups"] for r in g["rows"] if r["label_ar"] == label)
    return row, row["cells"][[u["id"] for u in c["universities"]].index(uid)]


def test_the_comparison_leads_with_the_figure_and_keeps_its_conditions():
    c = compare.build(["university-of-oxford", "harvard-university", "cornell-university"], ex, answer, "2026-11-27")
    _, ox = cell_of(c, "IELTS", "university-of-oxford")
    assert ox["value"] == "7.5" and ox["note"] == "لا تقل أي مهارة عن 7.0" and ox["state"] is None
    _, harvard = cell_of(c, "IELTS", "harvard-university")
    assert harvard["value"] == "لا يوجد حد أدنى منشور" and harvard["state"] == "nomin"
    # A recommended score is never set as a minimum.
    _, cornell = cell_of(c, "IELTS", "cornell-university")
    assert cornell["value"] == "لا يوجد حد أدنى منشور" and cornell["note"] == "الموصى به 7.5"
    # Oxford isn't in the SAT/ACT countries: it says so, apart from a fact we haven't checked.
    _, sat = cell_of(c, "SAT/ACT", "university-of-oxford")
    assert sat["value"] == "لا ينطبق" and sat["state"] == "none"


def test_a_rank_says_what_it_measures_and_one_ministry_document_is_cited_once():
    c = compare.build(["university-of-oxford", "harvard-university"], ex, answer, "2026-11-27")
    row, ox = cell_of(c, "المرتبة في قائمة الرواد", "university-of-oxford")
    assert ox["value"] == "6" and cell_of(c, "المرتبة في قائمة الرواد", "harvard-university")[1]["value"] == "1"
    assert row["source"] == {"url": ex.source["url"], "label": "دليل الوزارة لقوائم الجامعات"}
    html = client.get("/compare?u=university-of-oxford,harvard-university").text
    label_row = html.split("المرتبة في قائمة الرواد")[1].split("</tr>")[0]
    assert ex.source["url"] in label_row and "compare-src--row" in label_row


def test_each_university_keeps_its_own_source():
    uids = ["university-of-oxford", "harvard-university"]
    c = compare.build(uids, ex, answer, "2026-11-27")
    row, ox = cell_of(c, "IELTS", "university-of-oxford")
    _, harvard = cell_of(c, "IELTS", "harvard-university")
    assert row["source"] is None
    assert [s["url"] for s in ox["sources"]] == [ex.details["university-of-oxford"]["english"]["ielts"]["source_url"]]
    assert [s["url"] for s in harvard["sources"]] == [ex.details["harvard-university"]["english"]["ielts"]["source_url"]]
    assert ox["sources"][0]["site"] == "ox.ac.uk" and harvard["sources"][0]["site"] == "harvard.edu"
    html = client.get("/compare?u=" + ",".join(uids)).text
    # The link sits in the cell headed by its own university, named for screen readers.
    cell = re.search(r'<td[^>]*headers="cg-admission r-admission-\d+ col-university-of-oxford"[^>]*>((?:(?!</td>).)*ox\.ac\.uk(?:(?!</td>).)*)</td>', html, re.S)
    assert cell and "harvard.edu" not in cell.group(1) and "جامعة أكسفورد" in cell.group(1)
    # Sources start hidden, behind one switch beside «الفروق فقط»; the names stay in view on a long table.
    assert 'id="compare-sources"' in html and 'id="compare-diff"' in html and "data-compare-stick" in html
    css = (main.APP_DIR / "static" / "style.css").read_text(encoding="utf-8")
    assert ".compare-src,\n.compare-src-list {\n  display: none;" in css
    assert ".compare-page:has(.compare-sources-input:checked) .compare-src" in css


def test_a_source_on_a_file_host_is_named_by_what_it_is():
    assert compare.site_of("https://www.ox.ac.uk/admissions") == "ox.ac.uk"
    assert compare.site_of("https://teamdynamix.umich.edu/x") == "umich.edu"
    assert compare.site_of("https://www.nus.edu.sg/a.pdf") == "nus.edu.sg"
    assert compare.site_of("https://edge.sitecorecloud.io/msu/cds.pdf") == "ملف PDF"


def test_answer_cards_group_their_sources_under_the_facts():
    html = client.get("/universities", params={"q": AI, "country": "US"}).text
    assert "src--tiny" not in html
    card = html.split('data-acard="harvard-university"')[1].split("</li>")[0]
    assert card.count('class="acard-source"') == 2 and "مصدر الموعد لـجامعة هارفارد" in card
    # Why it is here: its list, its place, and what that list covers.
    assert "ضمن قائمة الرواد، المرتبة 1" in card and "والمسار يشمل جميع التخصصات" in card
    assert "في الرواد، لكل التخصصات" in html and "في إمداد، مجال «" in html


def test_finder_rows_offer_compare_beside_save():
    html = client.get("/universities", params={"track": "emdad", "field": "ict"}).text
    rows = html.split('<table class="uni-table">')[1].split("</table>")[0]
    assert rows.count('class="save-mini"') == rows.count('class="compare-toggle"') > 0


def test_the_homepage_offers_the_comparison_beside_the_question():
    html = client.get("/").text
    actions = html.split('class="ask-actions"')[1].split("</div>")[0]
    assert 'class="btn btn--lime"' in actions and "data-compare-entry" in actions and "قارن الجامعات" in actions
    assert 'class="ask-door-link"' in actions


@pytest.mark.parametrize("q", ["كاوست", "KAUST", "KGSP", "kgsp"])
def test_kaust_by_any_of_its_names(q):
    r = client.get("/universities", params={"q": q}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/programs/kaust-kgsp"
    assert 'data-program-match="/programs/kaust-kgsp"' in client.get("/answer", params={"q": q}).text
    names = next(p for p in client.get("/api/suggestions").json()["programs"] if p["slug"] == "kaust-kgsp")
    assert any(k.startswith(q.lower()) for k in names["keys"])


def test_georgia_tech_and_majors_keep_their_own_results():
    r = client.get("/universities", params={"q": "Georgia Tech"}, follow_redirects=False)
    assert r.status_code == 200 and "georgia-institute-of-technology" in r.text and "data-program-match" not in r.text
    assert client.get("/universities", params={"q": AI}, follow_redirects=False).status_code == 200
    assert client.get("/en/universities", params={"q": "KAUST"}, follow_redirects=False).headers["location"] == "/en/programs/kaust-kgsp"


def test_a_program_page_says_its_status_above_the_official_link():
    html = client.get("/programs/kaust-kgsp").text
    head = html.split('class="program-header')[1].split("</header>")[0]
    status, link = head.index('class="apply-status"'), head.index("صفحة التقديم الرسمية")
    assert status < link and main.TRACK_STATUS_LABELS[main.track_status(main.paths_by_id["kaust-kgsp"]["tracks"][0])] in head


def test_the_university_page_puts_the_deadline_and_tests_before_the_fee():
    html = client.get("/universities/harvard-university").text
    gate = html.split("ما تطلبه الجامعة نفسها")[1].split("</dl>")[0]
    assert gate.index("أقرب موعد في الجامعة") < gate.index("اختبارات الإنجليزية") < gate.index("رسوم التقديم")
    # Every date from one page: one named link for the list.
    assert "مصدر كل المواعيد: harvard.edu" in html


def test_no_decorative_diamonds_are_left():
    css = (main.APP_DIR / "static" / "style.css").read_text(encoding="utf-8")
    js = (main.APP_DIR / "static" / "mylist.js").read_text(encoding="utf-8")
    assert "rotate(45deg)" not in css and "rotate(45deg)" not in js
    assert 'class="diamond"' not in client.get("/").text
    # The logo keeps its own drawing (its lime dot included): tests/test_pages.py checks it against favicon.svg.
    assert 'class="brand-mark"' in client.get("/").text


def test_english_suggestions_know_georgia_tech_and_kaust_by_short_names():
    data = client.get("/en/api/suggestions").json()
    gt = next(u for u in data["universities"] if u["id"] == "georgia-institute-of-technology")
    assert gt.get("alias") == "Georgia Tech"
    kaust = next(p for p in data["programs"] if p["slug"] == "kaust-kgsp")
    assert {"kaust", "kgsp"} <= set(kaust["keys"]) and kaust["href"] == "/en/programs/kaust-kgsp"
