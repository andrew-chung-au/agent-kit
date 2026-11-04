#!/usr/bin/env python3
"""Say whether a sweep is due: print one line, read-only.

Run through the make target, from the project root:
    make sweep-due
or directly:
    python3 -B agent-kit/scripts/sweep-due.py [--dir <records folder>]

It finds the newest `*-measure-pm-sweep*.md` entry in the records folder
(default `_docs/records`), takes the cutoff time from the entry's name
(`<YYYY-MM-DDTHHMMZ>-measure-pm-sweep[-<n>].md`, UTC), and counts issues closed
at or after that time with `gh issue list --state closed`. It prints one line:

    due: <count> closed since <date>       <count> has reached SWEEP_EVERY_N
    not due: <count> closed since <date>   it has not
    due: no sweep recorded                 no entry exists (gh is not run)
    unknown: could not read issues         gh failed or answered something odd

Exit codes: 0 for the three answers above, 1 for `unknown`. A failed `gh`
never reads as "not due". Standard library only; it never writes anything.
The `gh` helper is copied from issue-hash.py on purpose, so each script runs
alone (that file's hyphenated name can't be imported).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# The one place the cadence lives: a sweep is due after this many closed issues.
# A draft placeholder. The human sets the real value.
SWEEP_EVERY_N = 5

MEASUREMENTS = "_docs/records"
ISSUE_LIMIT = 1000
ENTRY = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{4}Z)-measure-pm-sweep(?:-(\d+))?\.md")


def run_gh(args):
    """Run gh and return its parsed JSON, or raise ValueError with a short reason."""
    try:
        done = subprocess.run(["gh", *args], capture_output=True, text=True,
                              encoding="utf-8", timeout=60)
    except (OSError, subprocess.SubprocessError) as error:
        raise ValueError(f"cannot run gh: {error}")
    if done.returncode != 0:
        raise ValueError(f"gh {' '.join(args[:2])} failed (exit {done.returncode})")
    try:
        return json.loads(done.stdout)
    except ValueError:
        raise ValueError(f"gh {' '.join(args[:2])} returned malformed JSON")


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
    issues = run_gh(["issue", "list", "--state", "closed", "--limit", str(ISSUE_LIMIT),
                     "--json", "number,closedAt"])
    if not isinstance(issues, list):
        raise ValueError("gh issue list returned unexpected JSON")
    if len(issues) >= ISSUE_LIMIT:
        raise ValueError("too many closed issues to count safely")
    count = 0
    for issue in issues:
        stamp = issue.get("closedAt") if isinstance(issue, dict) else None
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
