import json
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR.parent / "data"

# Set WADIH_SHOW_DRAFTS=1 on your own machine to preview content that isn't verified yet.
# It is never set on the live site, so drafts stay hidden there.
SHOW_DRAFTS = os.environ.get("WADIH_SHOW_DRAFTS") == "1"


def load_json(name):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


site = load_json("site.json")
paths = load_json("paths.json")
tests = load_json("tests.json")
featured_quote = load_json("featured_quote.json")

app = FastAPI(title=site["name"])
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")
templates.env.globals["site"] = site
templates.env.globals["show_drafts"] = SHOW_DRAFTS


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    show_quote = featured_quote["status"] == "verified" or SHOW_DRAFTS
    return templates.TemplateResponse(
        request,
        "home.html",
        {"paths": paths, "tests": tests, "quote": featured_quote if show_quote else None},
    )


@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse(request, "about.html")
