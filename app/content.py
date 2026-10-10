import re
from pathlib import Path

import frontmatter
import markdown

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
    return {**post.metadata, "slug": slug, "html": markdown.markdown(post.content)}
