"""The English version of the site (decision 066).

Arabic stays the source. Every English text is stored against the exact Arabic it translates, in
data/i18n/*.json: {"Arabic text": "English text"}. So if the Arabic changes, the old English stops matching
and a test fails until it's translated again; a stale translation can't reach a student.

The language comes from the address (/en/... is English, anything else is Arabic). Data and logic always
work on the Arabic; translation happens only when text is shown. Arabic pages never go through a lookup.
"""

import json
import re
from contextvars import ContextVar
from pathlib import Path

from jinja2 import pass_context
from markupsafe import Markup

I18N_DIR = Path(__file__).parent.parent / "data" / "i18n"
EN_PREFIX = "/en"

_lang = ContextVar("wadih_lang", default="ar")
_english = {}
_from_data = {}  # Arabic name -> official English name, from the data itself (universities, fields, majors)


class KeepArabic(str):
    """A string shown as it is on English pages too: an official Arabic name a student will meet."""


def load():
    """Read every translation file. Called once at startup."""
    _english.clear()
    for path in sorted(I18N_DIR.glob("*.en.json")):
        _english.update(json.loads(path.read_text(encoding="utf-8")))


def js_strings():
    """The texts the page's JavaScript shows (data/i18n/js.en.json). Written into English pages only."""
    path = I18N_DIR / "js.en.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def add_from_data(pairs):
    """Names whose English comes from the data itself. A written translation wins over these."""
    _from_data.update({ar: en for ar, en in pairs if ar and en})


def is_english():
    return _lang.get() == "en"


def lang():
    return _lang.get()


def prefix():
    """What every address of this language starts with."""
    return EN_PREFIX if is_english() else ""


def set_lang(code):
    """Returns the token to give back to reset_lang."""
    return _lang.set(code)


def reset_lang(token):
    _lang.reset(token)


class use_lang:
    """`with use_lang("en"):` runs code in a language outside a request (the search index, tests)."""

    def __init__(self, code):
        self.code = code

    def __enter__(self):
        self.token = set_lang(self.code)

    def __exit__(self, *exc):
        reset_lang(self.token)


def lookup(text):
    """The English for this exact Arabic, or None."""
    found = _english.get(text)
    return found if found is not None else _from_data.get(text)


def tr(text):
    """The text in the current language. Text with no translation comes back as it is, and tests fail on it."""
    if not is_english() or not isinstance(text, str) or isinstance(text, KeepArabic):
        return text
    found = lookup(text)
    if found is None:
        return text
    return Markup(found) if isinstance(text, Markup) else found


def tf(pattern, **values):
    """A sentence with values in it: tf("{n} في مسار واعد", n=5). Each language puts them where it needs them."""
    return tr(pattern).format(**{key: tr(value) for key, value in values.items()})


# ---------- for the templates ----------


def t(text):
    """{{ _("نص") }}: text written in a template. It comes from us, so it may hold tags like <strong>."""
    return Markup(tr(text))


def tfm(pattern, **values):
    """{{ _f("نص {x}", x=value) }}: the same with values, which are escaped unless they are already safe HTML."""
    return Markup(tr(pattern)).format(**{key: tr(value) for key, value in values.items()})


@pass_context
def finalize(_context, value):
    """Runs on every {{ value }} in a template, so data such as note_ar shows in the page's language.
    pass_context makes it run per request, not once when the template is compiled."""
    return tr(value) if is_english() else value


def keep_arabic(text):
    """{{ ar(name) }}: stays Arabic on every page. Tests only accept Arabic on English pages inside lang="ar"."""
    return KeepArabic(text) if text else text


# ---------- addresses ----------

# Links written as /path in templates, Markdown, the data and the Python code. Files and the language
# switch itself are left alone; so are addresses already in English.
_LINK = re.compile(r'(?<!data-lang-switch )((?:href|action)=")/(?!/|static/|en(?:["/?#]))')


def localize_links(html):
    """Keep English readers in English: /about becomes /en/about, in one place, whoever wrote the link."""
    return _LINK.sub(lambda m: f"{m.group(1)}{EN_PREFIX}/", html)


class LanguageMiddleware:
    """/en/... → the same page in English. The routes never see the prefix, so each page exists once."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        path = scope.get("path", "")
        if scope["type"] != "http" or not (path == EN_PREFIX or path.startswith(EN_PREFIX + "/")):
            await self.app(scope, receive, send)
            return

        scope = dict(scope, path=path[len(EN_PREFIX):] or "/")
        if scope.get("raw_path"):
            scope["raw_path"] = scope["raw_path"][len(EN_PREFIX):] or b"/"

        async def send_keeping_english(message):
            # A redirect from inside the app (an extra slash, the old address) stays in English.
            if message["type"] == "http.response.start" and 300 <= message["status"] < 400:
                message = dict(message, headers=[
                    (name, _english_location(value) if name.lower() == b"location" else value)
                    for name, value in message["headers"]])
            await send(message)

        token = set_lang("en")
        try:
            await self.app(scope, receive, send_keeping_english)
        finally:
            reset_lang(token)


def _english_location(value):
    """Put /en in front of a redirect's path, relative or absolute."""
    text = value.decode("latin-1")
    match = re.match(r"^(https?://[^/]+)?(/.*)?$", text)
    if not match or (match.group(2) or "").startswith(("/en/", "/static/")) or match.group(2) == "/en":
        return value
    return f"{match.group(1) or ''}{EN_PREFIX}{match.group(2) or '/'}".encode("latin-1")
