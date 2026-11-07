import hashlib
import json
import os
from functools import cache
from datetime import timedelta

from app.clock import date
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import exploration, i18n, plan
from app.content import SLUG_PATTERN, english_titles, list_slugs, load_page
from app.i18n import tf, tr
from app.search import SiteSearch
from app.sky import rowwad_chart, star_field
from app.universities import COUNT_FORMS, NOT_LISTED_AR, PROGRAMS_AR, SAT_POLICY_AR, TRACKS, WAIVER_AR, Explorer, count_ar

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR.parent / "data"

# Set WADIH_SHOW_DRAFTS=1 on your own machine to preview content that isn't verified yet.
# It is never set on the live site, so drafts stay hidden there.
SHOW_DRAFTS = os.environ.get("WADIH_SHOW_DRAFTS") == "1"


ENGLISH_MONTHS = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
ARABIC_MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
                 "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]

# How each application status reads on the site (homepage rows and program pages).
TRACK_STATUS_LABELS = {
    "open": "مفتوح الآن",
    "closed": "مغلق حتى إشعار آخر",
    "not_open": "لم يفتح بعد",
    "opening_soon": "يفتح قريبًا",  # the official page says so, with no date yet
    "invitation": "بالترشيح والدعوة",
    "none_open": "لا يوجد برنامج مفتوح الآن",
}

# When a student can apply (decision 078, A2): each track in paths.json has an apply_when, and the homepage
# and «البرامج» group by it, so «مفتوح الآن» doesn't read as "apply today" to a school student who can't.
# In the order a student meets them. Each label restates a sourced fact on the program's page («لمن؟»).
APPLY_WHEN = {
    "in_school": "تتقدم وأنت في ثالث ثانوي",
    "after_school": "تتقدم بعد التخرج من الثانوية",
    "after_admission": "تتقدم بعد قبول من جامعة في القائمة",
    "with_scholarship": "تتقدم بعد أن تُبتعث",
}

# When two news items were added on the same day, the more urgent kind comes first.
NEWS_PRIORITY = {"opening": 0, "deadline": 1, "closing": 2, "announcement": 3}


def load_json(name):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def arabic_date(iso_date):
    """'2026-10-09' -> '9 أكتوبر 2026', or '9 October 2026' on English pages. Also accepts a date object
    (Markdown frontmatter dates)."""
    year, month, day = (int(part) for part in str(iso_date).split("-"))
    months = ENGLISH_MONTHS if i18n.is_english() else ARABIC_MONTHS
    return f"{day} {months[month - 1]} {year}"


def sort_news(items):
    """Most recently added first; on the same day, by NEWS_PRIORITY.

    "added" is the day we added the item, not the announcement date, so it's used for
    ordering only and never shown. Python's sort is stable, so sorting by priority first
    and then by date keeps the priority order inside each day.
    """
    by_priority = sorted(items, key=lambda item: NEWS_PRIORITY[item["type"]])
    # ISO dates (YYYY-MM-DD) sort correctly as plain text.
    return sorted(by_priority, key=lambda item: item["added"], reverse=True)


def is_confirmed(item):
    """Shown to students only with an official link or the owner's confirmation (decision 028)."""
    return bool(item.get("source_url") or item.get("owner_confirmed"))


i18n.load()  # the English texts, data/i18n/*.en.json (decision 066)
# Page titles are read from the Arabic Markdown in places computed once (the footer, the guides list, search):
# their English comes from content/en, so a translated page translates its title everywhere.
i18n.add_from_data(english_titles())
site = load_json("site.json")
paths = load_json("paths.json")
test_needs = load_json("test_needs.json")
apply_year = load_json("apply_year.json")
school_tracks = load_json("school_tracks.json")
featured_quote = load_json("featured_quote.json")
home_text = load_json("home.json")
news = sort_news([item for item in load_json("news.json") if is_confirmed(item)])
path_names = {path["id"]: path["name_ar"] for path in paths}
paths_by_id = {path["id"]: path for path in paths}
explorer = Explorer(show_drafts=SHOW_DRAFTS)
waaid_data = load_json("waaid_programs.json")
waddah = load_json("waddah.json")  # the AI guide's identity, teaser and Phase 2 switches (decisions 082, 083)


def waaid():
    """The latest واعد programs, newest first, each marked open or closed for today."""
    today = date.today().isoformat()
    programs = [
        {**p, "is_open": p["apply_from"] <= today <= p["apply_to"]}
        for p in sorted(waaid_data["programs"], key=lambda p: p["apply_to"], reverse=True)
    ]
    return {"programs": programs, "any_open": any(p["is_open"] for p in programs), "groups": waaid_groups(programs),
            "source_url": waaid_data["source_url"], "apply_url": waaid_data.get("apply_url")}


def waaid_groups(programs):
    """واعد programs grouped by announcement (one company, one application window), in the order given (decision 063).
    A group's id is its anchor on /waaid. It comes from the group's first-added program (the last in the data,
    since new programs go at the top), so a program added to an open window later doesn't break shared links.
    Inside a group, programs for high school graduates come first."""
    by_key = {}
    for p in programs:
        by_key.setdefault((p["company_ar"], p["apply_from"], p["apply_to"]), []).append(p)
    groups = []
    for (company, start, end), ps in by_key.items():
        hs = [p for p in ps if p["for_high_school"]]
        groups.append({"id": f"g-{ps[-1]['id']}", "company_ar": company, "apply_from": start, "apply_to": end,
                       "is_open": ps[0]["is_open"], "programs": hs + [p for p in ps if not p["for_high_school"]],
                       "hs_count": len(hs), "other_count": len(ps) - len(hs)})
    return groups


def waaid_who(group):
    """«لمن» for an announcement: how many of its programs take high school graduates."""
    hs, other = group["hs_count"], group["other_count"]
    if hs and other:
        return tf("{hs} لخريجي الثانوية، و{other} لغير خريجي الثانوية", hs=count_ar(hs, PROGRAMS_AR), other=count_ar(other, PROGRAMS_AR))
    return "لخريجي الثانوية" if hs else "لغير خريجي الثانوية"


# How long a closed program stays in «فُتح وأُغلق مؤخرًا» before it drops out of the board.
RECENT_DAYS = 120


def status_board():
    """The news board, built from the data that already holds each status (decision 033):
    - open: tracks open today (soonest deadline first) and واعد programs open today (those not for
      high school graduates last)
    - waiting: tracks closed until further notice or not open yet, and واعد programs opening later
    - recent: واعد programs and dated tracks that closed in the last RECENT_DAYS days (newest first)
    Nothing is typed twice: a status lives in paths.json / waaid_programs.json and shows up here.
    """
    today = date.today()
    iso = today.isoformat()
    pages = set(program_slugs())
    groups = {"open": [], "waiting": [], "recent": []}

    for path in paths:
        page = f"/programs/{path['id']}" if path["id"] in pages else None
        for track in path["tracks"]:
            confirmed = track.get("status_source") or track.get("owner_confirmed")
            if track.get("for_high_school") is False or track.get("latest_programs") or not confirmed:
                continue
            status = track_status(track)
            if not status:
                continue
            item = {
                "title_ar": track["name_ar"] if len(path["tracks"]) > 1 else path["name_ar"],
                "program_ar": path["name_ar"] if len(path["tracks"]) > 1 else path["provider_ar"],
                "status": status, "page": page, "source_url": track.get("status_source"),
                "until": track.get("status_until") if status == "open" else None,
                # Who can act on it: «مفتوح الآن» alone read as "apply today" to students who can't yet
                # (الرواد needs a university admission first; SDAIA needs a scholarship).
                "who_ar": track.get("apply_with_ar"),
                # «تقدم الآن ↗» while open, for tracks whose data names where to apply (sourced in the track).
                "apply_url": track.get("apply_url") if status == "open" else None,
                "when": track.get("apply_when"),
                "pid": plan_ids.get((path["id"], track.get("id"))),  # «احفظ» in «خطتي»
            }
            until = track.get("status_until")
            if status == "open":
                groups["open"].append(item)
            elif track.get("status") == "open" and until and until < iso:
                item["closed_on"] = until  # closed by its own deadline
                recent = (today - date.fromisoformat(until)).days <= RECENT_DAYS
                groups["recent" if recent else "waiting"].append(item)
            else:
                groups["waiting"].append(item)

    # واعد: one item per announcement (a company's programs with one window), not one per program, so a batch
    # of 11 programs takes one row; the row opens that announcement on /waaid (decision 063).
    w = waaid()
    for g in w["groups"]:
        single = len(g["programs"]) == 1
        first = g["programs"][0]
        item = {
            "title_ar": first["program_ar"] if single else tf("برامج {company}", company=g["company_ar"]),
            "program_ar": tf("مسار واعد، {what}", what=g["company_ar"] if single else count_ar(len(g["programs"]), PROGRAMS_AR)),
            "page": f"/waaid#{g['id']}", "source_url": w["source_url"],
            "who_ar": waaid_who(g),  # every واعد row says who it is for, one way (no tag)
            "sort_last": g["hs_count"] == 0,
            "when": "after_school",
        }
        if g["is_open"]:
            groups["open"].append({**item, "status": "open", "until": g["apply_to"], "apply_url": w["apply_url"]})
        elif g["apply_from"] > iso:
            groups["waiting"].append({**item, "status": "not_open", "opens": g["apply_from"]})
        elif (today - date.fromisoformat(g["apply_to"])).days <= RECENT_DAYS:
            groups["recent"].append({**item, "status": "closed", "closed_on": g["apply_to"]})

    # Soonest deadline first, but واعد announcements with nothing for high school graduates go last:
    # a company's batch of master's programs shouldn't push الرواد off the homepage.
    groups["open"].sort(key=lambda i: (i.get("sort_last", False), i.get("until") is None, i.get("until") or ""))
    groups["recent"].sort(key=lambda i: i["closed_on"], reverse=True)
    return groups


def now_board(board):
    """The homepage's «الآن» (2026-11-07, decision 083): what is open today, then what hasn't opened yet, each under
    its own heading. «مفتوح للتقديم الآن» used to list Aramco and KAUST, which hadn't opened, because it merged the two.
    Each open item with a deadline carries the days left, on Riyadh's date (app/clock.py)."""
    today = date.today()
    opened = [{**i, "days_left": (date.fromisoformat(i["until"]) - today).days if i.get("until") else None}
              for i in board["open"]]
    upcoming = [i for i in board["waiting"] if i["status"] in ("not_open", "opening_soon")]
    return {"open": opened, "upcoming": upcoming, "today": today.isoformat()}


def programs_by_when():
    """«البرامج» grouped by when you apply, in APPLY_WHEN's order; groups with no program are left out."""
    return [{"when": w, "title_ar": label, "paths": [p for p in paths if p.get("apply_when") == w]}
            for w, label in APPLY_WHEN.items() if any(p.get("apply_when") == w for p in paths)]


def track_status(track):
    """A track's status for today: واعد follows its latest programs; a deadline closes an open track."""
    if track.get("latest_programs"):
        return "open" if waaid()["any_open"] else "none_open"
    status = track.get("status")
    until = track.get("status_until")
    if status == "open" and until and date.today().isoformat() > until:
        return "closed"
    return status


def waddah_dawn(today=None):
    """How far dawn has come on the teaser (decision 082): 0 = night on dawn_from, rising a little each night on
    Riyadh's date, holding at the edge of dawn (0.9) until launch day, which is a switch in the data, never a date."""
    if waddah["launched"]:
        return 1.0
    today = today or date.today()
    start, end = date.fromisoformat(waddah["dawn_from"]), date.fromisoformat(waddah["dawn_to"])
    step = (today - start).days / max(1, (end - start).days)
    return round(max(0.0, min(0.9, step * 0.9)), 3)


# The application year runs from August to July (the US applications open in August, apply_year.json).
YEAR_MONTHS = (8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7)


def year_line(today=None):
    """«السنة في سطر» (decision 083): the application year as one line, with today on it.

    Only what the data dates: the six phases of a university application year (apply_year.json, with the counts
    the Explorer computes), the scholarship's dated deadline (a track's status_until, with its source), and the
    واعد windows that include programs for high school graduates. A program with no announced date isn't drawn."""
    today = today or date.today()
    year = today.year if today.month >= 8 else today.year - 1
    start, end = date(year, 8, 1), date(year + 1, 8, 1)
    span = (end - start).days

    def at(d):
        return round(max(0.0, min(1.0, (d - start).days / span)) * 100, 2)

    months = []
    for m in YEAR_MONTHS:
        first = date(year if m >= 8 else year + 1, m, 1)
        nxt = date(first.year + (m == 12), m % 12 + 1, 1)
        months.append({"n": m, "days": (nxt - first).days, "is_now": m == today.month})
    stats = explorer.timeline_stats()
    phases = []
    for r in apply_year["rows"]:
        first, last = YEAR_MONTHS.index(r["months"][0]), YEAR_MONTHS.index(r["months"][-1])
        count = stats.get("early") if r.get("computed") == "early" else stats.get("january") if r.get("computed") == "regular" else None
        phases.append({"title_ar": r["title_ar"], "when_ar": r["when_ar"], "col": first + 1, "span": last - first + 1,
                       "is_now": today.month in r["months"], "count": count})
    marks, windows = [], []
    for path in paths:
        for track in path["tracks"]:
            until = track.get("status_until")
            if track.get("status") == "open" and until and track.get("status_source") and start <= date.fromisoformat(until) < end:
                marks.append({"title_ar": track["name_ar"], "date": until, "at": at(date.fromisoformat(until)),
                              "past": until < today.isoformat(), "source_url": track["status_source"],
                              "page": f"/programs/{path['id']}" if path["id"] in program_slugs() else None})
    for g in waaid()["groups"]:
        a, b = date.fromisoformat(g["apply_from"]), date.fromisoformat(g["apply_to"])
        if g["hs_count"] and b >= start and a < end:
            windows.append({"title_ar": g["company_ar"], "from": g["apply_from"], "to": g["apply_to"], "at": at(a),
                            "width": max(0.6, round(at(b + timedelta(days=1)) - at(a), 2)), "href": f"/waaid#{g['id']}",
                            "is_open": g["is_open"], "past": g["apply_to"] < today.isoformat()})
    return {"start": start.isoformat(), "months": months, "phases": phases, "marks": marks, "windows": windows,
            "today": today.isoformat(), "today_at": at(today), "stats": stats}


def program_slugs():
    """Programs that have their own page: an entry in paths.json plus content/programs/<id>.md."""
    return [slug for slug in list_slugs("programs") if slug in paths_by_id]


# Site search (decision 045): built once at startup from the published pages and facts.
site_search = SiteSearch(program_slugs(), paths_by_id, test_needs, explorer)
with i18n.use_lang("en"):
    site_search_en = SiteSearch(program_slugs(), paths_by_id, test_needs, explorer)


def current_search():
    """The search index of the page's language."""
    return site_search_en if i18n.is_english() else site_search

app = FastAPI(title=site["name"])
app.add_middleware(i18n.LanguageMiddleware)  # /en/... is the same page in English (decision 066)

# One public address (decision 042): visits to the old Render address or to www are sent, with the same
# path and query, to base_url. Other hosts (local runs, tests) are left alone.
CANONICAL_HOST = site["base_url"].split("://", 1)[1].rstrip("/")
OLD_HOSTS = {"wadih-mqni.onrender.com", "www." + CANONICAL_HOST} - {CANONICAL_HOST}


@app.middleware("http")
async def redirect_to_canonical_host(request: Request, call_next):
    host = request.headers.get("host", "").split(":")[0].lower()
    if host in OLD_HOSTS:
        target = site["base_url"].rstrip("/") + request.url.path
        if request.url.query:
            target += "?" + request.url.query
        return RedirectResponse(target, status_code=301)
    return await call_next(request)

app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")


@cache
def asset_version(path):
    """A short hash of a static file's contents, added as ?v= to CSS/JS links. It changes only when
    the file changes, so browsers fetch a new version right after a deploy instead of a cached one."""
    data = (APP_DIR / "static" / path).read_bytes()
    return hashlib.sha256(data).hexdigest()[:8]
templates = Jinja2Templates(directory=APP_DIR / "templates")


@pass_context
def url_for_language(context, name, /, **path_params):
    """url_for that stays in the page's language. Static files have one address for both."""
    url = context["request"].url_for(name, **path_params)
    return url if name == "static" or not i18n.is_english() else url.replace(path=i18n.EN_PREFIX + url.path)


def render(request, name, context=None, status_code=200):
    """Draw a page. On English pages, links written as /path get /en in front (i18n.localize_links)."""
    response = templates.TemplateResponse(request, name, context or {}, status_code=status_code)
    if i18n.is_english():
        response.body = i18n.localize_links(response.body.decode("utf-8")).encode("utf-8")
        response.headers["content-length"] = str(len(response.body))
    return response


def language_links(request):
    """This page in Arabic and in English, as paths with the query kept. Used by the toggle and Google's tags."""
    # One leading slash: a path like //example.com must never become a link to another site.
    path, query = "/" + request.url.path.lstrip("/"), request.url.query
    tail = "?" + query if query else ""
    return {"ar": path + tail, "en": i18n.EN_PREFIX + path + tail, "ar_path": path, "en_path": i18n.EN_PREFIX + path}


# Everything {{ value }} prints goes through this, so data shows in the page's language.
templates.env.finalize = i18n.finalize
templates.env.globals.update({
    "_": i18n.t, "_f": i18n.tfm, "tr": tr, "ar": i18n.keep_arabic, "is_en": i18n.is_english,
    "language_links": language_links, "url_for": url_for_language,
    "js_strings": lambda: i18n.js_strings(),
})
templates.env.globals["site"] = site
templates.env.globals["asset_version"] = asset_version
templates.env.globals["show_drafts"] = SHOW_DRAFTS
templates.env.globals["track_status_labels"] = TRACK_STATUS_LABELS
templates.env.globals["apply_when_labels"] = APPLY_WHEN
templates.env.globals["tracks"] = TRACKS
explorer.waaid = waaid  # the explorer lists واعد programs from the same data as the homepage
templates.env.globals["waaid"] = waaid
templates.env.globals["waaid_who"] = waaid_who
templates.env.globals["track_status"] = track_status
templates.env.globals["waddah"] = waddah
templates.env.globals["waddah_dawn"] = waddah_dawn
templates.env.globals["month_names"] = ARABIC_MONTHS
# The sky drawings (decisions 060, 062): the homepage's night stars and the الرواد chart, computed once.
templates.env.globals["sky_stars"] = {
    "hero": star_field(70, 1440, 560, seed=7),
    "chart": star_field(90, 1000, 520, seed=5),
}
templates.env.globals["rowwad_chart"] = rowwad_chart(explorer)
# «جرّب قبل أن تقرر» (decision 069): its door on the «لم تقرر بعد؟» guide shows only while the activity is public.
templates.env.globals["explore_public"] = lambda: exploration.is_public(SHOW_DRAFTS)
templates.env.globals["explore_why"] = exploration.why_text
templates.env.globals["explore_list"] = exploration.list_text
templates.env.globals["explore_field_ids"] = lambda: list(exploration.FIELDS)  # the homepage door's tones
templates.env.globals["sat_policy_ar"] = SAT_POLICY_AR
templates.env.globals["waiver_ar"] = WAIVER_AR
templates.env.globals["not_listed_ar"] = NOT_LISTED_AR
# The shared ways around the site (decision 062): the homepage's guides section and every page's footer
# list the same grades, program pages and guides. Guide titles come from their Markdown (read at startup).
resource_titles = {slug: load_page("resources", slug)["title"] for slug in list_slugs("resources")}
templates.env.globals["grade_links"] = home_text["grades"]
# «خطتي» (decision 078, Part B): the programs a student can add, by id (a track's id, or Aramco's program id).
plan_programs = plan.program_targets(paths)
plan_ids = {(path["id"], track.get("id")): pid for pid, (path, track) in plan_programs.items()}
templates.env.globals["plan_id"] = lambda path, track: plan_ids.get((path["id"], track.get("id")))
templates.env.globals["program_links"] = [{"slug": p["id"], "name_ar": load_page("programs", p["id"])["title"]}
                                          for p in paths if p["id"] in program_slugs()]
templates.env.globals["guide_groups"] = [
    {**group, "items": [{**item, "title_ar": resource_titles[item["slug"]]}
                        for item in group["items"] if item["slug"] in resource_titles]}
    for group in home_text["guides"]
]
# The copyright line runs from the first year of publication to this year, so it updates itself.
templates.env.globals["current_year"] = lambda: date.today().year
templates.env.filters["arabic_date"] = arabic_date
# {{ 5 | count_ar("universities") }} → «5 جامعات» (Arabic counting rules, see universities.count_ar).
templates.env.filters["count_ar"] = lambda n, noun: count_ar(n, COUNT_FORMS[noun])


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    show_quote = featured_quote["status"] == "verified" or SHOW_DRAFTS
    board = status_board()
    return render(
        request,
        "home.html",
        {
            "paths": paths,
            "board": board,
            "now": now_board(board),
            "program_groups": programs_by_when(),
            "home": home_text,
            "path_names": path_names,
            "quote": featured_quote if show_quote else None,
            "program_pages": program_slugs(),
            "explorer": explorer,
        },
    )


@app.get("/programs", response_class=HTMLResponse)
def programs_index(request: Request):
    # «البرامج» (decision 083): what's open, what opens later, every program by when you apply, and the
    # announcements. One place for programs and their dates (/news redirects here).
    board = status_board()
    return render(request, "programs.html", {
        "board": board, "now": now_board(board), "program_groups": programs_by_when(),
        "announcements": news, "path_names": path_names, "program_pages": program_slugs(),
        "year": year_line(),
    })


@app.get("/news")
def news_page(request: Request):
    # «مواعيد التقديم» is now part of «البرامج» (decision 083).
    return RedirectResponse(str(url_for_language({"request": request}, "programs_index")), status_code=301)


@app.get("/waddah", response_class=HTMLResponse)
def waddah_page(request: Request):
    # وضّاح's page (decision 082): what it will do and won't, example questions, the FAQ. Nothing to sign up for yet.
    return render(request, "waddah.html", {})


@app.get("/guides", response_class=HTMLResponse)
def guides_index(request: Request):
    # «الأدلة» as a page of its own (decision 083): the same groups as the homepage and the footer.
    return render(request, "guides.html", {})


@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return render(request, "about.html", {"paths": paths, "explorer": explorer})


@app.get("/grades/{slug}", response_class=HTMLResponse)
def grade_page(request: Request, slug: str):
    # Markdown is read on every request, so content edits show up without a restart.
    page = load_page("grades", slug)
    if page is None:
        raise HTTPException(status_code=404)
    # Each grade page has the same structure (grade.html, decision 040); its own tool comes from data/.
    return render(request, "grade.html", {
        "page": page, "grades": home_text["grades"], "explorer": explorer,
        "test_needs": test_needs, "sat_summary": explorer.sat_summary(),  # ثاني ثانوي
        "school_tracks": school_tracks,  # أول ثانوي
        # ثالث ثانوي: the year month by month, «الآن» from today's month
        "apply_year": apply_year, "timeline_stats": explorer.timeline_stats(),
        "deadlines": explorer.upcoming_deadlines(), "this_month": date.today().month,
        "arruaad_track": next(t for t in paths_by_id["custodian-scholarship"]["tracks"] if t.get("id") == "arruaad"),
    })


@app.get("/resources/{slug}", response_class=HTMLResponse)
def resource_page(request: Request, slug: str):
    # Shared resources (IELTS, tests…), written once and linked from every program that needs them.
    page = load_page("resources", slug)
    if page is None:
        raise HTTPException(status_code=404)
    return render(request, "page.html", {"page": page, "explorer": explorer})


@app.get("/programs/{slug}", response_class=HTMLResponse)
def program_page(request: Request, slug: str):
    # Facts come from data/paths.json; the explanations come from content/programs/<slug>.md.
    program = paths_by_id.get(slug)
    page = load_page("programs", slug) if program else None
    if page is None:
        raise HTTPException(status_code=404)
    return render(request, "program.html", {"program": program, "page": page, "explorer": explorer,
                                            "ready_facts": ready_facts(program)})


def ready_facts(program):
    """The program's shown facts by id, each with the track it belongs to (or None).

    «معي قبول جامعي» (#ready) links these instead of repeating them, so every step points at a sourced fact on
    the same page. Only facts the page shows (sourced or conflict, like components.fact) are kept."""
    facts = {f["id"]: {"fact": f, "track": None} for f in program.get("facts", [])}
    for track in program.get("tracks", []):
        facts.update({f["id"]: {"fact": f, "track": track} for f in track.get("facts", [])})
    return {fid: v for fid, v in facts.items() if v["fact"].get("status") in ("sourced", "conflict")}


@app.get("/waaid", response_class=HTMLResponse)
def waaid_page(request: Request):
    # مسار واعد on its own page (decision 063): one block per announcement (company + window), each program
    # under its own anchor. The homepage and the board open the announcement a student tapped.
    groups = waaid_groups(explorer.waaid_matches())  # with university_id, for the link to the university page
    today = date.today().isoformat()
    sections = {
        "open": [g for g in groups if g["is_open"]],
        "upcoming": sorted((g for g in groups if g["apply_from"] > today), key=lambda g: g["apply_from"]),
        "closed": [g for g in groups if g["apply_to"] < today],
    }
    track = next(t for t in paths_by_id["custodian-scholarship"]["tracks"] if t.get("latest_programs"))
    return render(request, "waaid.html", {
        "sections": sections, "track": track, "w": waaid(), "explorer": explorer,
    })


@app.get("/universities", response_class=HTMLResponse)
def universities_page(request: Request, q: str = "", track: str = "", field: str = "",
                      country: str = "", lang: str = "", partial: bool = False):
    # Search runs on the server, so the page works without JavaScript; universities.js asks for
    # partial=1 to swap in just the results as the student types.
    result = explorer.search(q=q[:100], track=track, field=field, country=country, language=lang)
    # The King scholarship's tracks (name, who it's for, levels) for «ما الفرق بين المسارات؟».
    scholarship_tracks = [t for t in paths_by_id["custodian-scholarship"]["tracks"] if t.get("id") in TRACKS]
    context = {"result": result, "explorer": explorer, "view": explorer.describe(result),
               "scholarship_tracks": scholarship_tracks,
               # The الرواد destination at the top of the page (decision 060).
               "arruaad_track": next(t for t in scholarship_tracks if t["id"] == "arruaad")}
    template = "partials/uni_results.html" if partial else "universities.html"
    return render(request, template, context)


# The scholarship's extra conditions for a foundation year (a sourced fact in paths.json), or None if unpublished.
PREP_YEAR_FACT = next((f for f in paths_by_id["custodian-scholarship"].get("facts", [])
                       if f["id"] == "prep-year" and f["status"] == "sourced" and f.get("sources")), None)


@app.get("/universities/{uid}", response_class=HTMLResponse)
def university_page(request: Request, uid: str, from_: str | None = Query(None, alias="from")):
    profile = explorer.profile(uid) if SLUG_PATTERN.match(uid) else None
    if profile is None:
        raise HTTPException(status_code=404)
    # `from` is the search the student came from (set on result links), so the page can link back
    # to the same results. Only known parameters survive (see Explorer.back_url).
    return render(request, "university.html",
                                      {"p": profile, "explorer": explorer, "today": date.today().isoformat(),
                                       "back_url": explorer.back_url(from_),
                                       # The scholarship's own dates, shown apart from the university's (decision 038).
                                       "scholarship": {t["id"]: t for t in paths_by_id["custodian-scholarship"]["tracks"]
                                                       if t.get("id")},
                                       # Shown where the Saudi certificate isn't enough for year 1 (foundation year).
                                       "prep_year_fact": PREP_YEAR_FACT})


@app.get("/my-list")
def my_list_moved(request: Request):
    """«قائمتي» became «خطتي» (decision 078, Part B); old links and bookmarks land on the plan."""
    return RedirectResponse(str(url_for_language({"request": request}, "my_plan")), status_code=301)


@app.get("/my-plan", response_class=HTMLResponse)
def my_plan(request: Request):
    """«خطتي»: the page. The plan itself lives in the student's browser (mylist.js), which POSTs it here."""
    return render(request, "my_plan.html", {"statuses": plan.STATUSES})


@app.post("/my-plan", response_class=HTMLResponse)
async def my_plan_rows(request: Request):
    """Draws the rows for the plan the browser sends (JSON: {"items": [...]}). Only valid items are drawn,
    in the student's order, at most 100; nothing is stored or logged here (decision 078)."""
    body = await request.body()
    if len(body) > 20_000:
        raise HTTPException(status_code=413)
    try:
        raw = json.loads(body or b"{}")
    except ValueError:
        raise HTTPException(status_code=400)
    items = plan.clean(raw, explorer.universities, plan_programs)
    return render(request, "partials/my_plan_rows.html", {
        "rows": plan.rows(items, explorer, plan_programs, track_status, APPLY_WHEN, program_slugs()),
        "statuses": plan.STATUSES, "explorer": explorer})


def explore_or_404():
    """The activity is a draft until reviewed (decision 069): on the live site it doesn't exist yet."""
    if not exploration.is_public(SHOW_DRAFTS):
        raise HTTPException(status_code=404)


@app.get("/explore", response_class=HTMLResponse)
def explore_page(request: Request):
    """«جرّب قبل أن تقرر»: the whole activity is one form, so it works without JavaScript; explore.js turns it
    into one question per screen, with progress, and the last step goes straight to the result."""
    explore_or_404()
    return render(request, "explore.html", {"x": exploration.DATA, "activities": exploration.activities()})


@app.get("/explore/result")
def explore_result_reload():
    # The result exists only as the answer to the form (nothing is stored), so a reload starts again.
    explore_or_404()
    return RedirectResponse("/explore", status_code=303)


@app.post("/explore/result", response_class=HTMLResponse)
async def explore_result(request: Request):
    """The result, drawn from the posted answers and then forgotten: nothing is saved or logged."""
    explore_or_404()
    length = request.headers.get("content-length") or "0"
    if not length.isdigit():
        raise HTTPException(status_code=400)
    if int(length) > exploration.MAX_BODY:
        raise HTTPException(status_code=413)
    body = b""
    async for chunk in request.stream():  # also caps a body sent without a length (chunked)
        body += chunk
        if len(body) > exploration.MAX_BODY:
            raise HTTPException(status_code=413)
    result = exploration.score(exploration.parse(body))
    shown = [f["id"] for band in result["bands"].values() for f in band]
    if result["considered"]:
        shown.append(result["considered"]["id"])
    views = {fid: exploration.field_view(fid, explorer, school_tracks) for fid in shown}
    return render(request, "explore_result.html", {
        "r": result, "views": views, "x": exploration.DATA, "program_names": path_names,
        "lead_titles": [views[f["id"]]["title_ar"] for f in (result["bands"]["draws"] or result["bands"]["try"])[:3]],
        "sources": [{"title": school_tracks["source"]["title"], "url": school_tracks["source"]["url"]},
                    {"title": explorer.source["title_ar"], "url": explorer.source["url"]}] + exploration.DATA["sources"],
    })


def lists_answer(q):
    """The one box (decision 083): what the university lists say about q, shown above the guides' results.
    Universities by name (the first few, and how many), a major (its lists in the explorer), a country, or the
    health answer: each one link into the explorer, which holds the details and the sources."""
    if not q:
        return None
    r = explorer.search(q=q)
    hits = next((s["universities"] for s in r["sections"] if "universities" in s and not s.get("outside_filters")), [])
    answer = {"href": f"/universities?q={quote(q)}", "mode": r["mode"], "universities": hits[:5], "total": len(hits),
              "majors": r.get("major_names", []), "country": r.get("country_match"), "health": r["health"]}
    return answer if (hits or answer["majors"] or answer["country"] or answer["health"]) else None


@app.get("/search", response_class=HTMLResponse)
def search_page(request: Request, q: str = ""):
    # Works without JavaScript: the form reloads this page with ?q=.
    q = q.strip()[:200]
    return render(request, "search.html", {"q": q, "results": current_search().search(q) if q else [],
                                           "lists": lists_answer(q), "explorer": explorer})


@app.get("/api/search")
def search_api(q: str = ""):
    # The same results as /search, as JSON: the retrieval step the future chatbot will call.
    q = q.strip()[:200]
    return JSONResponse({"query": q, "results": [{**r, "url": i18n.prefix() + r["url"]} for r in current_search().search(q)] if q else []})


@app.get("/api/suggestions")
def suggestions_api():
    # Majors grouped by field + university names, loaded by the search box the first time it's used.
    return JSONResponse(explorer.suggestions())


@app.get("/api/universities")
def universities_api():
    # The same data as the explorer, for the future chatbot and agents.
    return JSONResponse(explorer.api())


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots():
    # Tells search engines they may read every page, and where the sitemap is.
    return f"User-agent: *\nAllow: /\n\nSitemap: {site['base_url']}/sitemap.xml\n"


@app.get("/sitemap.xml")
def sitemap():
    # The list of public pages for search engines. Grade and program pages come from content/.
    page_paths = (
        ["/", "/about", "/programs", "/guides", "/waddah"]
        + [f"/grades/{slug}" for slug in list_slugs("grades")]
        + [f"/programs/{slug}" for slug in program_slugs()]
        + ["/waaid"]
        + [f"/resources/{slug}" for slug in list_slugs("resources")]
        + ["/universities"]
        + (["/explore"] if exploration.is_public(SHOW_DRAFTS) else [])
        + [f"/universities/{uid}" for uid in sorted(explorer.universities)]
    )
    # Every page exists in both languages (decision 066); Google reads the pairs from each page's own tags.
    urls = "".join(f"  <url><loc>{site['base_url']}{prefix}{path}</loc></url>\n"
                   for prefix in ("", i18n.EN_PREFIX) for path in page_paths)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}</urlset>\n"
    )
    return Response(content=xml, media_type="application/xml")


@app.exception_handler(StarletteHTTPException)
async def not_found(request: Request, exc: StarletteHTTPException):
    # A friendly Arabic page for unknown addresses; other errors keep FastAPI's default.
    if exc.status_code == 404:
        return render(request, "404.html", status_code=404)
    return await http_exception_handler(request, exc)
