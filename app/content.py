import re
from pathlib import Path

import frontmatter
import markdown
from markdown.extensions.toc import slugify_unicode

CONTENT_DIR = Path(__file__).parent.parent / "content"

# Only lowercase letters, digits, and dashes. The slug comes from the URL, so we never
# trust it to build a file path: this blocks tricks like "../../.env".
SLUG_PATTERN = re.compile(r"^[a-z0-9-]+$")


def list_slugs(section):
    """All valid page slugs in content/<section>/, sorted (used by the sitemap)."""
    folder = CONTENT_DIR / section
    return sorted(p.stem for p in folder.glob("*.md") if SLUG_PATTERN.match(p.stem))


def load_page(section, slug):
    """Read content/<section>/<slug>.md and return its frontmatter plus rendered HTML, or None."""
    if not SLUG_PATTERN.match(slug):
        return None

    path = CONTENT_DIR / section / f"{slug}.md"
    if not path.is_file():
        return None

    post = frontmatter.load(path)
    # toc: every heading gets an id (Arabic kept, e.g. «#القبول-المشروط»), and the page gets a list of
    # its h2s for «في هذه الصفحة». attr_list: a heading can set its own short id with {#id}.
    md = markdown.Markdown(extensions=["toc", "attr_list"],
                           extension_configs={"toc": {"slugify": slugify_unicode, "toc_depth": "2"}})
    html = md.convert(post.content)
    contents = [{"id": t["id"], "title": t["name"]} for t in md.toc_tokens]
    return {**post.metadata, "slug": slug, "html": html, "contents": contents}
