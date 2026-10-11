"""The Markdown page loader."""

import pytest

from app.content import load_page


def test_loads_frontmatter_and_html():
    page = load_page("grades", "grade-10")
    assert page["title"] == "أول ثانوي"
    assert page["status"] in {"draft", "verified"}
    assert "<h2 " in page["html"]


def test_headings_get_ids_and_a_contents_list():
    """Every h2 gets an id (Arabic kept) for links and «في هذه الصفحة»; {#id} sets a short one."""
    page = load_page("grades", "grade-10")
    assert '<h2 id="معدلك-يبدأ-من-الآن">' in page["html"]
    program = load_page("programs", "custodian-scholarship")
    assert {"id": "conditional", "title": "القبول المشروط: متى يُقبل؟"} in program["contents"]
    assert '<h2 id="conditional">' in program["html"]


def test_missing_page_returns_none():
    assert load_page("grades", "grade-99") is None


@pytest.mark.parametrize("slug", ["../../.env", "..", "Grade-10", "grade_10", "a/b", ""])
def test_unsafe_or_invalid_slugs_are_rejected(slug):
    assert load_page("grades", slug) is None
