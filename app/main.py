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

# When two news items share a date, the more urgent kind comes first.
NEWS_PRIORITY = {"opening": 0, "deadline": 1, "closing": 2, "announcement": 3}


def load_json(name):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def arabic_date(iso_date):
    """'2026-10-09' -> '9 أكتوبر 2026'"""
    year, month, day = (int(part) for part in iso_date.split("-"))
    return f"{day} {ARABIC_MONTHS[month - 1]} {year}"


def sort_news(items):
    """Newest publication date first; on the same date, by NEWS_PRIORITY.

    Python's sort is stable, so sorting by priority first and then by date keeps
    the priority order inside each date.
    """
    by_priority = sorted(items, key=lambda item: NEWS_PRIORITY[item["type"]])
    # ISO dates (YYYY-MM-DD) sort correctly as plain text.
    return sorted(by_priority, key=lambda item: item["date"], reverse=True)


site = load_json("site.json")
paths = load_json("paths.json")
tests = load_json("tests.json")
featured_quote = load_json("featured_quote.json")
home_text = load_json("home.json")
news = sort_news(load_json("news.json"))
path_names = {path["id"]: path["name_ar"] for path in paths}

app = FastAPI(title=site["name"])
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")
templates.env.globals["site"] = site
templates.env.globals["show_drafts"] = SHOW_DRAFTS
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
        },
    )


@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse(request, "about.html")


@app.get("/grades/{slug}", response_class=HTMLResponse)
def grade_page(request: Request, slug: str):
    # Markdown is read on every request, so content edits show up without a restart.
    page = load_page("grades", slug)
    if page is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(request, "page.html", {"page": page})


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots():
    # Tells search engines they may read every page, and where the sitemap is.
    return f"User-agent: *\nAllow: /\n\nSitemap: {site['base_url']}/sitemap.xml\n"


@app.get("/sitemap.xml")
def sitemap():
    # The list of public pages for search engines. Grade pages come from content/grades/.
    page_paths = ["/", "/about"] + [f"/grades/{slug}" for slug in list_slugs("grades")]
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
