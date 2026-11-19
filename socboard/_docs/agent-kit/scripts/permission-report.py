#!/usr/bin/env python3
"""Permission report: what the agent tools asked the human to approve (issue #36).

Run from the project folder as `make permission-report [SINCE=<YYYY-MM-DD or YYYY-MM-DDTHH:MMZ>]`, or:
    python3 -B agent-kit/scripts/permission-report.py [YYYY-MM-DD | YYYY-MM-DDTHH:MMZ]

Reads the log files in .agent-kit/logs/permissions/ (procedures/permission-log.md) and
prints, per tool, permission type and pattern: times asked, replies (allowed, always,
denied), distinct sessions, first and last time. Sessions are counted, not log lines.

- SINCE limits the report by record time, in UTC. It is a real date written YYYY-MM-DD (the
  start of that UTC day) or a real UTC minute written YYYY-MM-DDTHH:MMZ (a session summary's
  start; records at or after the start of that minute count). Anything else (seconds, an
  offset, a lower-case z, a commit) is refused before any file is read.
- Lines that are not JSON objects are skipped and counted. Nothing in a log is executed.
- Every text field shown is redacted again with scripts/secret-patterns.txt, so a log file
  edited or written by something else cannot make the report print a secret.
- A tool with no reply records (Claude Code's hook events carry no outcome) shows "-" for
  the reply columns: unknown, not zero.

Prints a short line and exits 0 when there are no logs. Standard library only.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import permission_log_lib as lib  # noqa: E402

FOLDER = Path(".agent-kit") / "logs" / "permissions"
FILE_NAME = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\.jsonl")
DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
MINUTE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}Z")
TIME = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\.([0-9]{1,9}))?Z")
OUTCOME = {"once": "allowed", "always": "always", "reject": "denied"}


def refuse(message: str) -> None:
    sys.stderr.write("permission-report: " + message + "\n")
    sys.exit(2)


def parse_since(value: str):
    """None for no limit; otherwise the start instant (naive UTC datetime). Anything else is refused.

    A date means the start of that UTC day; a timestamp means the start of that UTC minute.
    Both patterns are full matches on ASCII digits, then a real-calendar parse.
    """
    if value == "":
        return None
    try:
        if DATE.fullmatch(value):
            return datetime(int(value[:4]), int(value[5:7]), int(value[8:10]))
        if MINUTE.fullmatch(value):
            return datetime(int(value[:4]), int(value[5:7]), int(value[8:10]), int(value[11:13]), int(value[14:16]))
    except ValueError:
        pass
    refuse("SINCE must be a real date written YYYY-MM-DD or a UTC minute written YYYY-MM-DDTHH:MMZ, "
           "for example 2026-11-03 or 2026-11-03T10:30Z (a commit is not a time). Got: " + ascii(value[:40]))


def parse_time(value):
    found = TIME.fullmatch(value) if isinstance(value, str) else None
    if not found:
        return None
    try:
        moment = datetime.strptime(found.group(1), "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None
    return moment.replace(microsecond=int((found.group(2) or "0")[:6].ljust(6, "0")))


def text(record: dict, key: str):
    value = record.get(key)
    return value if isinstance(value, str) and value else None


class Group:
    def __init__(self):
        self.asked = 0
        self.sessions = set()
        self.outcomes = {"allowed": 0, "always": 0, "denied": 0}
        self.first = self.last = None


def read(files, since):
    """Returns (groups, asks, replies, counts)."""
    groups, asks, replies = {}, {}, []
    counts = {"skipped": 0, "unknown": 0, "truncated": []}
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except (ValueError, RecursionError):
                    record = None
                if not isinstance(record, dict):
                    counts["skipped"] += 1
                    continue
                moment = parse_time(record.get("time"))
                kind, tool, session = record.get("event"), text(record, "tool"), text(record, "sessionID")
                if moment and since and moment < since:
                    continue
                if moment is None or tool is None or kind not in ("ask", "reply", "truncated"):
                    counts["unknown"] += 1  # an unknown record, or one this report cannot read
                    continue
                if kind == "truncated":
                    counts["truncated"].append((tool, moment.date().isoformat()))
                elif kind == "ask" and session and text(record, "type"):
                    pattern = record.get("pattern")
                    key = (tool, text(record, "type"), pattern if isinstance(pattern, str) else "")
                    group = groups.setdefault(key, Group())
                    group.asked += 1
                    group.sessions.add(session)
                    group.first = min(group.first or moment, moment)
                    group.last = max(group.last or moment, moment)
                    if text(record, "id"):
                        asks[(tool, session, text(record, "id"))] = key
                elif kind == "reply" and session and text(record, "id"):
                    replies.append((tool, session, text(record, "id"), record.get("response")))
                else:
                    counts["unknown"] += 1
    return groups, asks, replies, counts


def main(argv) -> int:
    if len(argv) > 2:
        refuse("usage: permission-report.py [YYYY-MM-DD | YYYY-MM-DDTHH:MMZ]")
    since = parse_since(argv[1] if len(argv) == 2 else "")
    files = []
    if FOLDER.is_dir():
        files = sorted(p for p in FOLDER.iterdir() if FILE_NAME.fullmatch(p.name) and p.is_file() and not p.is_symlink())
    if not files:
        print("No permission logs found in %s/ (nothing to report)." % FOLDER.as_posix())
        return 0
    groups, asks, replies, counts = read(files, since)
    reply_tools, answered, unmatched = set(), set(), 0
    for tool, session, ident, response in replies:
        reply_tools.add(tool)
        key = (tool, session, ident)
        if key not in asks:
            unmatched += 1
        elif key not in answered:
            answered.add(key)
            outcome = OUTCOME.get(response) if isinstance(response, str) else None
            if outcome:
                groups[asks[key]].outcomes[outcome] += 1
            else:
                counts["unknown"] += 1
    given = argv[1] if len(argv) == 2 else ""
    shown = "from %s " % given if since else ""
    print("Permission report %s(%d log file%s, %s to %s)" % (
        shown, len(files), "" if len(files) == 1 else "s", files[0].name[:10], files[-1].name[:10]))
    rows = []
    for (tool, kind, pattern), group in groups.items():
        known = tool in reply_tools
        rows.append((lib.plain(tool, 40), lib.plain(kind, 40), group.asked,
                     *(str(group.outcomes[k]) if known else "-" for k in ("allowed", "always", "denied")),
                     len(group.sessions), group.first.strftime("%Y-%m-%dT%H:%M:%SZ"),
                     group.last.strftime("%Y-%m-%dT%H:%M:%SZ"), lib.redact(pattern)))
    rows.sort(key=lambda r: (r[0], -r[2], r[1], r[9]))
    if rows:
        head = ("TOOL", "TYPE", "ASKED", "ALLOWED", "ALWAYS", "DENIED", "SESSIONS", "FIRST", "LAST", "PATTERN")
        table = [head] + [tuple(str(c) for c in r) for r in rows]
        widths = [max(len(r[i]) for r in table) for i in range(9)]
        for r in table:
            print("  ".join(r[i].ljust(widths[i]) for i in range(9)) + "  " + r[9])
    else:
        print("No permission requests in this range.")
    blind = sorted({t for t, _, _ in groups} - reply_tools)
    if blind:
        print("Outcomes not recorded for: %s (\"-\"). Asked counts only; the tool's hook events carry no reply." % ", ".join(
            lib.plain(t, 40) for t in blind))
    print("Skipped lines (not JSON objects): %d" % counts["skipped"])
    print("Unknown or unrecognised records: %d" % counts["unknown"])
    if unmatched:
        print("Replies with no matching ask in range: %d" % unmatched)
    if counts["truncated"]:
        print("Size cap reached (later records that day were dropped): " + ", ".join(
            "%s %s" % (lib.plain(t, 40), d) for t, d in sorted(set(counts["truncated"]))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
