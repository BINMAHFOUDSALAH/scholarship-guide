import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.content import list_slugs, load_page

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


def program_slugs():
    """Programs that have their own page: an entry in paths.json plus content/programs/<id>.md."""
    return [slug for slug in list_slugs("programs") if slug in paths_by_id]

app = FastAPI(title=site["name"])
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")
templates.env.globals["site"] = site
templates.env.globals["show_drafts"] = SHOW_DRAFTS
templates.env.globals["track_status_labels"] = TRACK_STATUS_LABELS
templates.env.filters["arabic_date"] = arabic_date


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    show_quote = featured_quote["status"] == "verified" or SHOW_DRAFTS
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "paths": paths,
            "tests": tests,
            "news": news[:3],
            "home": home_text,
            "path_names": path_names,
            "quote": featured_quote if show_quote else None,
            "program_pages": program_slugs(),
        },
    )


@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse(request, "about.html", {"paths": paths})


@app.get("/grades/{slug}", response_class=HTMLResponse)
def grade_page(request: Request, slug: str):
    # Markdown is read on every request, so content edits show up without a restart.
    page = load_page("grades", slug)
    if page is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(request, "page.html", {"page": page, "tests": tests})


@app.get("/resources/{slug}", response_class=HTMLResponse)
def resource_page(request: Request, slug: str):
    # Shared resources (IELTS, tests…), written once and linked from every program that needs them.
    page = load_page("resources", slug)
    if page is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(request, "page.html", {"page": page, "tests": tests})


@app.get("/programs/{slug}", response_class=HTMLResponse)
def program_page(request: Request, slug: str):
    # Facts come from data/paths.json; the explanations come from content/programs/<slug>.md.
    program = paths_by_id.get(slug)
    page = load_page("programs", slug) if program else None
    if page is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(request, "program.html", {"program": program, "page": page})


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots():
    # Tells search engines they may read every page, and where the sitemap is.
    return f"User-agent: *\nAllow: /\n\nSitemap: {site['base_url']}/sitemap.xml\n"


@app.get("/sitemap.xml")
def sitemap():
    # The list of public pages for search engines. Grade and program pages come from content/.
    page_paths = (
        ["/", "/about"]
        + [f"/grades/{slug}" for slug in list_slugs("grades")]
        + [f"/programs/{slug}" for slug in program_slugs()]
        + [f"/resources/{slug}" for slug in list_slugs("resources")]
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
