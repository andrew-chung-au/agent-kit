#!/usr/bin/env python3
"""Say whether a sweep is due: print one line, read-only.

Run through the make target, from the project root:
    make sweep-due
or directly:
    python3 -B agent-kit/scripts/sweep-due.py [--dir <records folder>]

It finds the newest `*-measure-pm-sweep*.md` entry in the records folder
(default `_docs/records`), takes the cutoff time from the entry's name
(`<YYYY-MM-DDTHHMMZ>-measure-pm-sweep[-<n>].md`, UTC), and counts issues closed
at or after that time through the REST API (`gh api "repos/<repo>/issues?state=closed&since=<cutoff>&per_page=100&page=<P>"`,
every page, pull requests left out; <repo> is the GITHUB_REPO line of agent-kit.conf, read by
github_api.py). It prints one line:

    due: <count> closed since <date>       <count> has reached SWEEP_EVERY_N
    not due: <count> closed since <date>   it has not
    due: no sweep recorded                 no entry exists (gh is not run)
    unknown: could not read issues         gh failed or answered something odd

Exit codes: 0 for the three answers above, 1 for `unknown`. A failed `gh`
never reads as "not due". Standard library only; it never writes anything.
The repository and the `gh api` helper live in github_api.py, next to this file.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import github_api  # noqa: E402  (the repository and the gh api reads, shared with issue-hash.py)

# The one place the cadence lives: a sweep is due after this many closed issues.
# A draft placeholder. The human sets the real value.
SWEEP_EVERY_N = 5

MEASUREMENTS = "_docs/records"
ISSUE_LIMIT = 1000
ENTRY = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{4}Z)-measure-pm-sweep(?:-(\d+))?\.md")


def newest_entry(folder: Path):
    """Return (cutoff datetime in UTC, file name) of the newest sweep entry, or None."""
    found = []
    if folder.is_dir():
        for path in folder.iterdir():
            match = ENTRY.fullmatch(path.name)
            if match and path.is_file():
                try:
                    moment = datetime.strptime(match.group(1), "%Y-%m-%dT%H%MZ")
                except ValueError:
                    continue
                found.append((moment, int(match.group(2) or 1), path.name))
    if not found:
        return None
    moment, _, name = max(found)
    return moment.replace(tzinfo=timezone.utc), name


def closed_since(cutoff: datetime) -> int:
    """Count issues closed at or after cutoff; raise ValueError if they can't be read."""
    repo = github_api.conf_repo()
    # `since` keeps issues updated at or after the cutoff; closing updates an issue, so no
    # issue closed since the cutoff is missed. closed_at is checked below.
    since = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
    items = github_api.gh_api_pages(f"repos/{repo}/issues?state=closed&since={since}", ISSUE_LIMIT)
    count = 0
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("an issue has no closedAt time")
        if "pull_request" in item:
            continue  # the issues list also returns pull requests; `gh issue list` did not
        stamp = item.get("closed_at")
        if not isinstance(stamp, str):
            raise ValueError("an issue has no closedAt time")
        try:
            closed = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except ValueError:
            raise ValueError("an issue has an unreadable closedAt time")
        if closed >= cutoff:
            count += 1
    return count


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Say whether a sweep is due.")
    parser.add_argument("--dir", default=MEASUREMENTS, help="records folder")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    entry = newest_entry(Path(args.dir))
    if entry is None:
        print("due: no sweep recorded")
        return 0
    cutoff, _ = entry
    try:
        count = closed_since(cutoff)
    except ValueError as error:
        print("unknown: could not read issues")
        print(f"sweep-due: {error}", file=sys.stderr)
        return 1
    label = "due" if count >= SWEEP_EVERY_N else "not due"
    print(f"{label}: {count} closed since {cutoff.date().isoformat()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
