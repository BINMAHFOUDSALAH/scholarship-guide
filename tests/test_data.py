"""Our trust rules, written as code: if the data breaks a rule, a test fails."""

import re

import app.main as main

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TRACK_STATUSES = {"open", "closed", "not_open", "invitation"}
NEWS_TYPES = {"opening", "closing", "deadline", "announcement"}


def test_every_path_has_an_official_https_link():
    for path in main.paths:
        assert path["official_url"].startswith("https://"), path["id"]


def test_path_ids_are_unique():
    ids = [path["id"] for path in main.paths]
    assert len(ids) == len(set(ids))


def test_verified_paths_have_sourced_track_statuses():
    """A path may only be marked verified when every track status has a source."""
    for path in main.paths:
        if path["verified"]:
            for track in path["tracks"]:
                assert track["status_source"], f"{path['id']}: {track['name_ar']} has no source"


def test_track_statuses_and_dates_are_valid():
    for path in main.paths:
        for track in path["tracks"]:
            assert track["status"] in TRACK_STATUSES
            assert ISO_DATE.match(track["last_checked"])


def test_news_items_are_valid():
    for item in main.news:
        assert ISO_DATE.match(item["date"])
        assert item["type"] in NEWS_TYPES
        assert item["path_id"] in main.path_names, f"unknown path: {item['path_id']}"
        assert item["source_url"] is None or item["source_url"].startswith("https://")


def test_news_is_sorted_newest_first():
    dates = [item["date"] for item in main.news]
    assert dates == sorted(dates, reverse=True)


def test_quote_can_only_be_verified_with_a_video_and_source():
    quote = main.featured_quote
    if quote["status"] == "verified":
        assert quote["video_url"] and quote["source_url"]


def test_arabic_date():
    assert main.arabic_date("2026-10-09") == "9 أكتوبر 2026"
    assert main.arabic_date("2027-01-01") == "1 يناير 2027"
