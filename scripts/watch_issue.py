"""Keep one GitHub issue in step with the morning site check (decision 064). Run by .github/workflows/watch.yml:

    python scripts/watch.py --json site-check.json
    python scripts/watch_issue.py site-check.json        (needs GITHUB_TOKEN and GITHUB_REPOSITORY)

How the issue behaves, so a notification always means something new and urgent:
- It's opened when something urgent appears (a new announcement, a broken page, failing tests).
- Each morning its body is replaced with the full report, urgent and routine. Editing a body doesn't notify.
- A comment, which notifies, lists only urgent findings that are new. A finding that was there on the
  previous run is ongoing and never announced again, however long ago that run was (GitHub sometimes delays
  or skips scheduled runs). One that went away and comes back within QUIET_DAYS days is a flap (a page that
  failed one morning and worked the next) and isn't announced either.
- It closes itself when nothing urgent is left (routine upkeep is /update-site's job).
- Closing it by hand mutes what's in it: it reopens only for an urgent finding that's new.
The previous run's date and when each finding was last seen are kept in a hidden comment at the end of the
body: no other storage needed.
"""

import json
import os
import re
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

MARKER = "<!-- wadih-site-check"
QUIET_DAYS = 7  # an urgent finding seen within this many days isn't announced again
FORGET_DAYS = 30  # findings not seen for this long are dropped from the hidden list
HOW = ("<details><summary>How this issue works</summary>\n\n"
       "- Every morning at 07:23 (Riyadh) `.github/workflows/watch.yml` runs `scripts/watch.py` and rewrites this "
       "issue. Run it by hand: Actions → watch → Run workflow.\n"
       "- You're notified only by a comment, and a comment lists only urgent findings that are new.\n"
       "- It closes itself when nothing urgent is left. Close it yourself to mute what's in it; it reopens only "
       "for something new.\n"
       "- To fix things: type `/update-site` in Claude Code, then merge. The next morning's check closes this.\n\n"
       "</details>")


def github_api(method, path, payload=None):
    request = urllib.request.Request(
        "https://api.github.com" + path, method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "wadih-site-check"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read() or "null")


def find_issue(repo, api):
    """The latest site-check issue, open or closed, or None."""
    issues = api("GET", f"/repos/{repo}/issues?state=all&sort=created&direction=desc&per_page=50")
    return next((i for i in issues if MARKER in (i.get("body") or "") and "pull_request" not in i), None)


def state_in(issue):
    """{"last_run": the previous run's date, "seen": {finding key: the last day it was seen}} from the issue."""
    found = re.search(rf"{MARKER} (\{{.*\}}) -->", (issue or {}).get("body") or "", re.S)
    state = json.loads(found.group(1)) if found else {}
    return {"last_run": state.get("last_run"), "seen": state.get("seen", {})}


def sync(check, repo, api=github_api):
    """Open, update, reopen or close the issue for today's findings. Returns what it did."""
    today, items = check["today"], check["items"]
    urgent = [i for i in items if i["urgent"]]
    issue = find_issue(repo, api)
    state = state_in(issue)
    seen, last_run = state["seen"], state["last_run"]
    quiet_since = (date.fromisoformat(today) - timedelta(days=QUIET_DAYS)).isoformat()
    ongoing = {k for k, d in seen.items() if d == last_run}  # present on the previous run
    new = [i for i in urgent if i["key"] not in ongoing and seen.get(i["key"], "") < quiet_since]

    forget_before = (date.fromisoformat(today) - timedelta(days=FORGET_DAYS)).isoformat()
    seen = {k: d for k, d in seen.items() if d >= forget_before} | {i["key"]: today for i in items}
    hidden = json.dumps({"last_run": today, "seen": seen}, ensure_ascii=False, sort_keys=True)
    body = check["report"][:60000] + "\n\n" + HOW + "\n\n" + f"{MARKER} {hidden} -->"
    title = f"Site check: {len(urgent)} urgent" + (f", {len(items) - len(urgent)} routine" if items else "")
    announce = {"body": f"New on {today}:\n\n" + "\n".join(f"- {i['text']}" for i in new)}

    if issue is None:
        if not urgent:
            return "nothing to do"
        created = api("POST", f"/repos/{repo}/issues", {"title": title, "body": body})
        return f"opened #{created['number']}"
    path = f"/repos/{repo}/issues/{issue['number']}"
    if issue["state"] == "open":
        if not urgent:
            api("PATCH", path, {"title": title, "body": body, "state": "closed", "state_reason": "completed"})
            api("POST", f"{path}/comments", {"body": f"Nothing urgent left on {today}. Closing; routine upkeep "
                                                     "stays listed above and in `/update-site`."})
            return f"closed #{issue['number']}"
        api("PATCH", path, {"title": title, "body": body})
        if new:
            api("POST", f"{path}/comments", announce)
        return f"updated #{issue['number']} ({len(new)} new)"
    if new:  # closed, by hand or when all was clear: reopen only for something new and urgent
        api("PATCH", path, {"title": title, "body": body, "state": "open"})
        api("POST", f"{path}/comments", announce)
        return f"reopened #{issue['number']} ({len(new)} new)"
    api("PATCH", path, {"body": body})  # stays closed; the hidden list stays current so muted findings stay muted
    return f"left #{issue['number']} closed"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    check = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    print("Issue:", sync(check, os.environ["GITHUB_REPOSITORY"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
