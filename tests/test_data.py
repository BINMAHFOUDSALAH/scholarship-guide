"""Our trust rules, written as code: if the data breaks a rule, a test fails."""

import re

import app.main as main

STATIC = main.APP_DIR / "static"
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
YOUTUBE_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
TRACK_STATUSES = {"open", "closed", "not_open", "invitation", "none_open"}
FACT_STATUSES = {"sourced", "unverified", "conflict", "outdated"}
NEWS_TYPES = {"opening", "closing", "deadline", "announcement"}
PATH_THEMES = {"world", "desert", "sea"}


def test_every_path_has_a_known_theme():
    for path in main.paths:
        assert path["theme"] in PATH_THEMES, path["id"]


def test_every_photo_is_credited_with_its_license_and_source():
    """Photos come from Wikimedia Commons; the licences require credit and a link."""
    for path in main.paths:
        photo = path.get("photo")
        if photo is None:
            continue
        assert photo["credit"], path["id"]
        assert photo["license"], path["id"]
        assert photo["alt_ar"], path["id"]
        assert photo["source_url"].startswith("https://commons.wikimedia.org/"), path["id"]
        if photo["license"].startswith("CC"):
            assert photo["license_url"].startswith("https://creativecommons.org/"), path["id"]


def test_every_path_says_who_it_is_for():
    for path in main.paths:
        assert path["audience_ar"], path["id"]
        assert path["provider_ar"], path["id"]


def test_home_text_entries_are_complete():
    home = main.home_text
    assert home["lead_ar"]
    assert len(home["hero_labels"]) == 3


def test_program_logos_are_official_and_self_hosted():
    """Decision 028: an official logo must come from the program's own official site, served by us."""
    for path in main.paths:
        logo = path.get("logo")
        if logo is None:
            continue
        assert logo["alt_ar"], path["id"]
        assert logo["source_url"].startswith("https://sites.moe.gov.sa/"), path["id"]
        assert ISO_DATE.match(logo["retrieved"]), path["id"]
        for size in ("500", "960"):
            assert (STATIC / f"{logo['file']}-{size}.png").is_file(), path["id"]


def test_site_has_public_address_and_description():
    assert main.site["base_url"].startswith("https://")
    assert not main.site["base_url"].endswith("/")
    assert main.site["description"]


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
            if track["status"] is None:
                # No status = we don't track it (e.g. doctorate only, or a program without a
                # published window); the page then says so instead of showing a chip.
                assert not track.get("status_source"), track["name_ar"]
            else:
                assert track["status"] in TRACK_STATUSES
                assert track["status"] in main.TRACK_STATUS_LABELS
            assert ISO_DATE.match(track["last_checked"])


def all_facts():
    for path in main.paths:
        yield from path.get("facts", [])
        for track in path["tracks"]:
            yield from track.get("facts", [])


def test_every_fact_follows_the_display_rule():
    """Decision 025: a fact is shown as sourced only with an official https source and a check date."""
    for fact in all_facts():
        assert fact["text_ar"], fact["id"]
        assert fact["status"] in FACT_STATUSES, fact["id"]
        assert ISO_DATE.match(fact["last_checked"]), fact["id"]
        assert isinstance(fact["owner_reviewed"], bool), fact["id"]
        if fact["status"] in ("sourced", "conflict"):
            assert fact["sources"], fact["id"]
            for source in fact["sources"]:
                assert source["title"], fact["id"]
                assert source["url"].startswith("https://"), fact["id"]
        if fact["status"] == "conflict":
            assert len(fact["sources"]) >= 2, f"{fact['id']}: a conflict needs both sources"
            assert fact["note_ar"], f"{fact['id']}: a conflict needs a note for students"


def test_fact_ids_are_unique():
    ids = [fact["id"] for fact in all_facts()]
    assert len(ids) == len(set(ids))


def test_news_items_are_valid():
    for item in main.news:
        assert ISO_DATE.match(item["added"])
        assert item["type"] in NEWS_TYPES
        assert item["path_id"] in main.path_names, f"unknown path: {item['path_id']}"
        assert item["source_url"] is None or item["source_url"].startswith("https://")


def test_news_is_sorted_newest_first():
    dates = [item["added"] for item in main.news]
    assert dates == sorted(dates, reverse=True)


def test_sort_news_by_date_then_status():
    items = [
        {"added": "2026-10-01", "type": "announcement"},
        {"added": "2026-10-09", "type": "closing"},
        {"added": "2026-10-09", "type": "announcement"},
        {"added": "2026-10-09", "type": "opening"},
        {"added": "2026-10-05", "type": "deadline"},
    ]
    result = [(item["added"], item["type"]) for item in main.sort_news(items)]
    assert result == [
        ("2026-10-09", "opening"),
        ("2026-10-09", "closing"),
        ("2026-10-09", "announcement"),
        ("2026-10-05", "deadline"),
        ("2026-10-01", "announcement"),
    ]


def test_quote_video_fields_are_valid():
    quote = main.featured_quote
    if quote["youtube_id"] is not None:
        assert YOUTUBE_ID.match(quote["youtube_id"])
    if quote["video_url"] is not None:
        assert quote["video_url"].startswith("https://")


def test_quote_can_only_be_verified_with_a_video_and_source():
    quote = main.featured_quote
    if quote["status"] == "verified":
        assert quote["youtube_id"] or quote["video_url"]
        assert quote["source_url"]


def test_arabic_date():
    assert main.arabic_date("2026-10-09") == "9 أكتوبر 2026"
    assert main.arabic_date("2027-01-01") == "1 يناير 2027"
