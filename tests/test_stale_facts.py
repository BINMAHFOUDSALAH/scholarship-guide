"""The stale-facts report (scripts/stale_facts.py) must see every check date in the data.

These tests never depend on today's date, so an aging fact can't turn CI red.
"""

import importlib.util
import json
from datetime import timedelta
from pathlib import Path

import frontmatter

ROOT = Path(__file__).resolve().parent.parent
CHECK_KEYS = {"last_checked", "read_on", "checked", "retrieved"}

spec = importlib.util.spec_from_file_location("stale_facts", ROOT / "scripts" / "stale_facts.py")
stale_facts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stale_facts)


def count_check_dates(node, parent_key=None):
    """Check-date fields anywhere in a JSON tree, skipping logos (images, not facts)."""
    if parent_key == "logo":
        return 0
    if isinstance(node, dict):
        return sum((key in CHECK_KEYS and isinstance(value, str)) + count_check_dates(value, key)
                   for key, value in node.items())
    if isinstance(node, list):
        return sum(count_check_dates(item, parent_key) for item in node)
    return 0


def test_the_report_finds_every_check_date():
    """A new data file or field with a check date must be added to the report, or this fails."""
    files = [f for f in (ROOT / "data").glob("*.json") if f.name != "university_logos.json"]
    files += (ROOT / "data" / "university_details").glob("*.json")
    expected = sum(count_check_dates(json.loads(f.read_text(encoding="utf-8"))) for f in files)
    expected += sum("last_checked" in frontmatter.load(f).metadata
                    for f in (ROOT / "content").glob("*/*.md"))
    assert len(stale_facts.collect()) == expected


def test_the_report_flags_by_age(capsys):
    items = stale_facts.collect()
    newest = items[-1]["checked"]
    stale_facts.main(["--as-of", newest.isoformat()])
    assert f"0 of {len(items)} checked items" in capsys.readouterr().out
    stale_facts.main(["--as-of", (newest + timedelta(days=91)).isoformat()])
    assert f"{len(items)} of {len(items)} checked items" in capsys.readouterr().out
