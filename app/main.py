import hashlib
import json
import os
from functools import cache
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.content import SLUG_PATTERN, list_slugs, load_page
from app.search import SiteSearch
from app.sky import rowwad_chart, star_field
from app.universities import COUNT_FORMS, NOT_LISTED_AR, PROGRAMS_AR, SAT_POLICY_AR, TRACKS, WAIVER_AR, Explorer, count_ar

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR.parent / "data"

# Set WADIH_SHOW_DRAFTS=1 on your own machine to preview content that isn't verified yet.
# It is never set on the live site, so drafts stay hidden there.
SHOW_DRAFTS = os.environ.get("WADIH_SHOW_DRAFTS") == "1"


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

# When two news items were added on the same day, the more urgent kind comes first.
NEWS_PRIORITY = {"opening": 0, "deadline": 1, "closing": 2, "announcement": 3}


def load_json(name):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def arabic_date(iso_date):
    """'2026-10-09' -> '9 أكتوبر 2026'. Also accepts a date object (Markdown frontmatter dates)."""
    year, month, day = (int(part) for part in str(iso_date).split("-"))
    return f"{day} {ARABIC_MONTHS[month - 1]} {year}"


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
        return f"{count_ar(hs, PROGRAMS_AR)} لخريجي الثانوية، و{count_ar(other, PROGRAMS_AR)} لغير خريجي الثانوية"
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
            "title_ar": first["program_ar"] if single else f"برامج {g['company_ar']}",
            "program_ar": f"مسار واعد، {g['company_ar'] if single else count_ar(len(g['programs']), PROGRAMS_AR)}",
            "page": f"/waaid#{g['id']}", "source_url": w["source_url"],
            "who_ar": waaid_who(g),  # every واعد row says who it is for, one way (no tag)
            "sort_last": g["hs_count"] == 0,
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


def track_status(track):
    """A track's status for today: واعد follows its latest programs; a deadline closes an open track."""
    if track.get("latest_programs"):
        return "open" if waaid()["any_open"] else "none_open"
    status = track.get("status")
    until = track.get("status_until")
    if status == "open" and until and date.today().isoformat() > until:
        return "closed"
    return status


def program_slugs():
    """Programs that have their own page: an entry in paths.json plus content/programs/<id>.md."""
    return [slug for slug in list_slugs("programs") if slug in paths_by_id]


# Site search (decision 045): built once at startup from the published pages and facts.
site_search = SiteSearch(program_slugs(), paths_by_id, test_needs, explorer)

app = FastAPI(title=site["name"])

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
templates.env.globals["site"] = site
templates.env.globals["asset_version"] = asset_version
templates.env.globals["show_drafts"] = SHOW_DRAFTS
templates.env.globals["track_status_labels"] = TRACK_STATUS_LABELS
templates.env.globals["tracks"] = TRACKS
explorer.waaid = waaid  # the explorer lists واعد programs from the same data as the homepage
templates.env.globals["waaid"] = waaid
templates.env.globals["waaid_who"] = waaid_who
templates.env.globals["track_status"] = track_status
# The sky drawings (decisions 060, 062): the homepage's night stars and the الرواد chart, computed once.
templates.env.globals["sky_stars"] = {
    "hero": star_field(70, 1440, 560, seed=7),
    "chart": star_field(90, 1000, 520, seed=5),
}
templates.env.globals["rowwad_chart"] = rowwad_chart(explorer)
templates.env.globals["sat_policy_ar"] = SAT_POLICY_AR
templates.env.globals["waiver_ar"] = WAIVER_AR
templates.env.globals["not_listed_ar"] = NOT_LISTED_AR
# The shared ways around the site (decision 062): the homepage's guides section and every page's footer
# list the same grades, program pages and guides. Guide titles come from their Markdown (read at startup).
resource_titles = {slug: load_page("resources", slug)["title"] for slug in list_slugs("resources")}
templates.env.globals["grade_links"] = home_text["grades"]
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
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "paths": paths,
            "board": status_board(),
            "home": home_text,
            "path_names": path_names,
            "quote": featured_quote if show_quote else None,
            "program_pages": program_slugs(),
            "explorer": explorer,
        },
    )


@app.get("/news", response_class=HTMLResponse)
def news_page(request: Request):
    # Everything on the board (no limits) plus the announcements from data/news.json.
    return templates.TemplateResponse(request, "news.html",
                                      {"board": status_board(), "announcements": news, "path_names": path_names})


@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse(request, "about.html", {"paths": paths, "explorer": explorer})


@app.get("/grades/{slug}", response_class=HTMLResponse)
def grade_page(request: Request, slug: str):
    # Markdown is read on every request, so content edits show up without a restart.
    page = load_page("grades", slug)
    if page is None:
        raise HTTPException(status_code=404)
    # Each grade page has the same structure (grade.html, decision 040); its own tool comes from data/.
    return templates.TemplateResponse(request, "grade.html", {
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
    return templates.TemplateResponse(request, "page.html", {"page": page, "explorer": explorer})


@app.get("/programs/{slug}", response_class=HTMLResponse)
def program_page(request: Request, slug: str):
    # Facts come from data/paths.json; the explanations come from content/programs/<slug>.md.
    program = paths_by_id.get(slug)
    page = load_page("programs", slug) if program else None
    if page is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(request, "program.html", {"program": program, "page": page, "explorer": explorer})


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
    return templates.TemplateResponse(request, "waaid.html", {
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
    return templates.TemplateResponse(request, template, context)


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
    return templates.TemplateResponse(request, "university.html",
                                      {"p": profile, "explorer": explorer, "today": date.today().isoformat(),
                                       "back_url": explorer.back_url(from_),
                                       # The scholarship's own dates, shown apart from the university's (decision 038).
                                       "scholarship": {t["id"]: t for t in paths_by_id["custodian-scholarship"]["tracks"]
                                                       if t.get("id")},
                                       # Shown where the Saudi certificate isn't enough for year 1 (foundation year).
                                       "prep_year_fact": PREP_YEAR_FACT})


@app.get("/my-list", response_class=HTMLResponse)
def my_list(request: Request, ids: str = "", partial: bool = False):
    """«قائمتي» (decision 035). The list itself lives in the student's browser (mylist.js); the page
    asks for its rows with ?partial=1&ids=a,b. Only ids of universities we know are drawn, in the
    student's order, at most 100. Nothing is stored here."""
    if not partial:
        return templates.TemplateResponse(request, "my_list.html", {})
    wanted = []
    for uid in ids.split(",")[:100]:
        uid = uid.strip()
        if SLUG_PATTERN.match(uid) and uid in explorer.universities and uid not in wanted:
            wanted.append(uid)
    return templates.TemplateResponse(request, "partials/my_list_rows.html",
                                      {"unis": [explorer.universities[uid] for uid in wanted], "explorer": explorer})


@app.get("/search", response_class=HTMLResponse)
def search_page(request: Request, q: str = ""):
    # Works without JavaScript: the form reloads this page with ?q=.
    q = q.strip()[:200]
    return templates.TemplateResponse(request, "search.html", {"q": q, "results": site_search.search(q) if q else []})


@app.get("/api/search")
def search_api(q: str = ""):
    # The same results as /search, as JSON: the retrieval step the future chatbot will call.
    q = q.strip()[:200]
    return JSONResponse({"query": q, "results": site_search.search(q) if q else []})


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
        ["/", "/about", "/news"]
        + [f"/grades/{slug}" for slug in list_slugs("grades")]
        + [f"/programs/{slug}" for slug in program_slugs()]
        + ["/waaid"]
        + [f"/resources/{slug}" for slug in list_slugs("resources")]
        + ["/universities"]
        + [f"/universities/{uid}" for uid in sorted(explorer.universities)]
    )
    urls = "".join(f"  <url><loc>{site['base_url']}{path}</loc></url>\n" for path in page_paths)
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
        return templates.TemplateResponse(request, "404.html", status_code=404)
    return await http_exception_handler(request, exc)
