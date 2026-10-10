"""The Markdown page loader."""

import pytest

from app.content import load_page


def test_loads_frontmatter_and_html():
    page = load_page("grades", "grade-10")
    assert page["title"] == "أول ثانوي"
    assert page["status"] in {"draft", "verified"}
    assert "<h2>" in page["html"]


def test_missing_page_returns_none():
    assert load_page("grades", "grade-99") is None


@pytest.mark.parametrize("slug", ["../../.env", "..", "Grade-10", "grade_10", "a/b", ""])
def test_unsafe_or_invalid_slugs_are_rejected(slug):
    assert load_page("grades", slug) is None
