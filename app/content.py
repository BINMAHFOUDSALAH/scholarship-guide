import hashlib
import re
from pathlib import Path

import frontmatter
import markdown
from markdown.extensions.toc import slugify_unicode

from app.i18n import is_english

CONTENT_DIR = Path(__file__).parent.parent / "content"
EN_DIR = CONTENT_DIR / "en"

# Only lowercase letters, digits, and dashes. The slug comes from the URL, so we never
# trust it to build a file path: this blocks tricks like "../../.env".
SLUG_PATTERN = re.compile(r"^[a-z0-9-]+$")


def list_slugs(section):
    """All valid page slugs in content/<section>/, sorted (used by the sitemap)."""
    folder = CONTENT_DIR / section
    return sorted(p.stem for p in folder.glob("*.md") if SLUG_PATTERN.match(p.stem))


def source_hash(section, slug):
    """A fingerprint of the Arabic page. Its English file records it, so a test can tell when the Arabic changed."""
    text = (CONTENT_DIR / section / f"{slug}.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def load_page(section, slug):
    """Read content/<section>/<slug>.md and return its frontmatter plus rendered HTML, or None.

    On English pages (decision 066) the text comes from content/en/<section>/<slug>.md. Its frontmatter holds
    only what's translated (title, description…): sources, status and check dates stay in the Arabic file,
    so they exist once."""
    if not SLUG_PATTERN.match(slug):
        return None

    path = CONTENT_DIR / section / f"{slug}.md"
    if not path.is_file():
        return None

    post = frontmatter.load(path)
    metadata, text = post.metadata, post.content
    english = EN_DIR / section / f"{slug}.md"
    if is_english() and english.is_file():
        en_post = frontmatter.load(english)
        metadata, text = {**metadata, **en_post.metadata}, en_post.content
    # toc: every heading gets an id (Arabic kept, e.g. «#القبول-المشروط»), and the page gets a list of
    # its h2s for «في هذه الصفحة». attr_list: a heading can set its own short id with {#id}.
    md = markdown.Markdown(extensions=["toc", "attr_list"],
                           extension_configs={"toc": {"slugify": slugify_unicode, "toc_depth": "2"}})
    html = md.convert(text)
    contents = [{"id": t["id"], "title": t["name"]} for t in md.toc_tokens]
    return {**metadata, "slug": slug, "html": html, "contents": contents}
