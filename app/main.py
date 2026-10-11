import json
import os
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.content import SLUG_PATTERN, list_slugs, load_page
from app.universities import COUNT_FORMS, SAT_POLICY_AR, TRACKS, Explorer, count_ar

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
tests = load_json("tests.json")
featured_quote = load_json("featured_quote.json")
home_text = load_json("home.json")
news = sort_news([item for item in load_json("news.json") if is_confirmed(item)])
path_names = {path["id"]: path["name_ar"] for path in paths}
paths_by_id = {path["id"]: path for path in paths}
explorer = Explorer()
waaid_data = load_json("waaid_programs.json")


def waaid():
    """The latest واعد programs, newest first, each marked open or closed for today."""
    today = date.today().isoformat()
    programs = [
        {**p, "is_open": p["apply_from"] <= today <= p["apply_to"]}
        for p in sorted(waaid_data["programs"], key=lambda p: p["apply_to"], reverse=True)
    ]
    return {"programs": programs, "any_open": any(p["is_open"] for p in programs),
            "source_url": waaid_data["source_url"]}


# How long a closed program stays in «فُتح وأُغلق مؤخرًا» before it drops out of the board.
RECENT_DAYS = 120


def status_board():
    """The news board, built from the data that already holds each status (decision 033):
    - open: tracks open today (soonest deadline first) and واعد programs open today
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

    w = waaid()
    for p in w["programs"]:
        item = {
            "title_ar": p["program_ar"], "program_ar": f"مسار واعد · {p['company_ar']}",
            "page": "/programs/custodian-scholarship#waaid-latest", "source_url": w["source_url"],
            "for_high_school": p["for_high_school"],
        }
        if p["is_open"]:
            groups["open"].append({**item, "status": "open", "until": p["apply_to"]})
        elif p["apply_from"] > iso:
            groups["waiting"].append({**item, "status": "not_open", "opens": p["apply_from"]})
        elif (today - date.fromisoformat(p["apply_to"])).days <= RECENT_DAYS:
            groups["recent"].append({**item, "status": "closed", "closed_on": p["apply_to"]})

    groups["open"].sort(key=lambda i: (i.get("until") is None, i.get("until") or ""))
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

app = FastAPI(title=site["name"])
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")
templates.env.globals["site"] = site
templates.env.globals["show_drafts"] = SHOW_DRAFTS
templates.env.globals["track_status_labels"] = TRACK_STATUS_LABELS
templates.env.globals["tracks"] = TRACKS
explorer.waaid = waaid  # the explorer lists واعد programs from the same data as the homepage
templates.env.globals["waaid"] = waaid
templates.env.globals["track_status"] = track_status
templates.env.globals["sat_policy_ar"] = SAT_POLICY_AR
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
            "tests": tests,
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
    return templates.TemplateResponse(request, "about.html", {"paths": paths})


@app.get("/grades/{slug}", response_class=HTMLResponse)
def grade_page(request: Request, slug: str):
    # Markdown is read on every request, so content edits show up without a restart.
    page = load_page("grades", slug)
    if page is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(request, "page.html",
                                      {"page": page, "tests": tests, "section": "grades", "grades": home_text["grades"]})


@app.get("/resources/{slug}", response_class=HTMLResponse)
def resource_page(request: Request, slug: str):
    # Shared resources (IELTS, tests…), written once and linked from every program that needs them.
    page = load_page("resources", slug)
    if page is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(request, "page.html", {"page": page, "tests": tests, "section": "resources"})


@app.get("/programs/{slug}", response_class=HTMLResponse)
def program_page(request: Request, slug: str):
    # Facts come from data/paths.json; the explanations come from content/programs/<slug>.md.
    program = paths_by_id.get(slug)
    page = load_page("programs", slug) if program else None
    if page is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(request, "program.html", {"program": program, "page": page, "explorer": explorer})


@app.get("/universities", response_class=HTMLResponse)
def universities_page(request: Request, q: str = "", track: str = "", field: str = "",
                      country: str = "", lang: str = "", partial: bool = False):
    # Search runs on the server, so the page works without JavaScript; universities.js asks for
    # partial=1 to swap in just the results as the student types.
    result = explorer.search(q=q[:100], track=track, field=field, country=country, language=lang)
    # The King scholarship's tracks (name, who it's for, levels) for «ما الفرق بين المسارات؟».
    scholarship_tracks = [t for t in paths_by_id["custodian-scholarship"]["tracks"] if t.get("id") in TRACKS]
    context = {"result": result, "explorer": explorer, "view": explorer.describe(result),
               "scholarship_tracks": scholarship_tracks}
    template = "partials/uni_results.html" if partial else "universities.html"
    return templates.TemplateResponse(request, template, context)


@app.get("/universities/{uid}", response_class=HTMLResponse)
def university_page(request: Request, uid: str, from_: str | None = Query(None, alias="from")):
    profile = explorer.profile(uid) if SLUG_PATTERN.match(uid) else None
    if profile is None:
        raise HTTPException(status_code=404)
    # `from` is the search the student came from (set on result links), so the page can link back
    # to the same results. Only known parameters survive (see Explorer.back_url).
    return templates.TemplateResponse(request, "university.html",
                                      {"p": profile, "explorer": explorer, "today": date.today().isoformat(),
                                       "back_url": explorer.back_url(from_)})


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
