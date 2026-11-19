#!/usr/bin/env python3
"""Delete old permission logs (issue #36).

Run from the project folder as `make permission-logs-prune DAYS=<n>`, or:
    python3 -B agent-kit/scripts/permission-logs-prune.py <n>

Deletes only regular files named YYYY-MM-DD.jsonl directly in .agent-kit/logs/permissions/
whose name date is more than n days before today (UTC). A file dated exactly n days ago is
kept. n must be a whole number from 1 to 3650, checked before anything is looked at.
Other files, folders, symlinks and anything outside that folder are never touched; if the
folder is reached through a symlink the script refuses. The human runs it on real logs.
Standard library only.
"""
from __future__ import annotations

import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

FOLDER = Path(".agent-kit") / "logs" / "permissions"
FILE_NAME = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})\.jsonl")


def refuse(message: str, code: int = 2) -> None:
    sys.stderr.write("permission-logs-prune: " + message + "\n")
    sys.exit(code)


def main(argv) -> int:
    value = argv[1] if len(argv) == 2 else ""
    if not re.fullmatch(r"[1-9][0-9]{0,3}", value) or int(value) > 3650:
        refuse("DAYS must be a whole number from 1 to 3650. Got: " + ascii(value[:40]))
    days = int(value)
    if not FOLDER.is_dir():
        print("No permission logs found in %s/ (nothing to prune)." % FOLDER.as_posix())
        return 0
    if FOLDER.resolve() != Path.cwd().resolve() / FOLDER:
        refuse("%s/ is reached through a symlink; nothing was deleted." % FOLDER.as_posix(), 1)
    cutoff = datetime.now(timezone.utc).date() - timedelta(days=days)
    deleted = kept = 0
    for path in sorted(FOLDER.iterdir()):
        found = FILE_NAME.fullmatch(path.name)
        try:
            when = date(*(int(g) for g in found.groups())) if found else None
        except ValueError:
            when = None
        if when is None or path.is_symlink() or not path.is_file():
            continue
        if when < cutoff:
            os.unlink(path)
            deleted += 1
            print("deleted " + path.name)
        else:
            kept += 1
    print("Deleted %d log file%s older than %d days (before %s); kept %d." % (
        deleted, "" if deleted == 1 else "s", days, cutoff.isoformat(), kept))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
