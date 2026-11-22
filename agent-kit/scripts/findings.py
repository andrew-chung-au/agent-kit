#!/usr/bin/env python3
"""List the open findings of the findings log by group (issue #200).

Run from the project folder as `make findings`, or directly:
    python3 -B <kit>/scripts/findings.py
It is read-only: it reads agent-kit.conf, `_docs/records/findings/<issue>.json`,
`_docs/records/findings-rulings.jsonl` and the sweep entries in `_docs/records/` as data,
writes nothing and starts no process. The format is in procedures/formats.md (Findings log);
the rules are in procedures/sweep.md and customizing.md (the FINDINGS_ settings).

What it reads, through check-format.py (loaded by path from this folder), so there is one
validator: every entry of every findings file goes through check_finding; the settings come
from settings.read_settings, which check-format.py loads.

Terms:
- A findings file is `{"issue": <n>, "logged": "<YYYY-MM-DDTHH:MMZ>", "findings": [...]}`,
  named `<n>.json`; each entry has the eleven keys of FINDING_FIELDS. It is written once.
- A ruling is one line of the rulings file, in the order written:
    {"id": "F-<n>-<n>", "ruling": "issued", "at": "<sweep entry time>", "issue": <n>}
    {"id": ..., "ruling": "dropped", "at": ...}   {"id": ..., "ruling": "kept", "at": ...}
    {"id": ..., "ruling": "regroup", "at": ..., "group": "<slug>"}
  `at` is the time in a sweep entry's name (`YYYY-MM-DDTHHMMZ`). `issued` and `dropped`
  close an entry; `kept` restarts its age at `at`; `regroup` replaces its group.
- An entry's age is the number of sweep entries (`<time>-measure-pm-sweep[-<n>].md`, the
  pattern of sweep-due.py) in `_docs/records/` whose name time is later than the entry's
  `logged` time, or than its last `kept` ruling's `at`.
- A group with at least FINDINGS_GROUP_AT open entries is flagged `draft one issue`; an
  entry whose age is at least FINDINGS_KEEP_SWEEPS is flagged `keep or drop`.

Output, groups largest first (ties by name), entries by issue and number:
    <group>: <n> open, <d> debt[ (<debt ids>)][ - draft one issue]
      <id> impact <L|M|C> age <n>[ - keep or drop]
    total: <n> open, <g> groups, <d> debt
or `none` with no open entry; exit 0. A refusal prints one line on standard error,
    findings: <file> <line or key>: <reason>
and exits 1: a file or line that is not valid JSON (duplicate keys included), a missing or
extra top-level key, a file name that does not match `issue`, an entry check_finding
refuses (or a duplicate id), a ruling with a missing or extra key, a bad value, an unknown id
or an id that is already closed, and a settings refusal. Nothing is skipped silently.
A usage error exits 2. Standard library only.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, _HERE / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check_format = _load("kit_check_format_for_findings", "check-format.py")
sweep_due = _load("kit_sweep_due_for_findings", "sweep-due.py")
settings = check_format.settings

PROG = "findings"
USAGE = "Usage: make findings (no arguments; run from the project folder)"
RECORDS = Path("_docs/records")
FINDINGS_DIR = RECORDS / "findings"
RULINGS = RECORDS / "findings-rulings.jsonl"
FILE_NAME = re.compile(r"([1-9][0-9]{0,8})\.json")
LOGGED = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}Z")
LOGGED_FORMAT = "%Y-%m-%dT%H:%MZ"
AT = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{4}Z")
AT_FORMAT = "%Y-%m-%dT%H%MZ"
TOP_KEYS = ("issue", "logged", "findings")
RULING_KEYS = {
    "issued": ("id", "ruling", "at", "issue"),
    "dropped": ("id", "ruling", "at"),
    "kept": ("id", "ruling", "at"),
    "regroup": ("id", "ruling", "at", "group"),
}


class Refusal(Exception):
    """A refusal: the place (file and line or key) and the reason."""

    def __init__(self, place: str, reason: str):
        super().__init__(f"{place}: {reason}")
        self.place, self.reason = place, reason


def destination(impact: str, to_issue_at: str) -> str:
    """`issue` when an unfixed finding of this impact gets its own draft issue, `log` when it
    becomes an entry in the findings log: impact at or above FINDINGS_TO_ISSUE_AT goes to an
    issue (the grade order is check-format's). The orchestrator applies this at close
    (process.md, Lifecycle step 9); `make findings` does not call it."""
    order = check_format.LMC[1]
    return "issue" if order.index(impact) >= order.index(to_issue_at) else "log"


def pairs_without_duplicates(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f"key {settings.echo(key)} is written twice")
        seen[key] = value
    return seen


def parse(text: str, place: str, in_line: bool = False):
    """The JSON value of `text`; Refusal naming `place`, with the line of a syntax error unless
    `place` is already one line (`in_line`)."""
    try:
        return json.loads(text, object_pairs_hook=pairs_without_duplicates)
    except json.JSONDecodeError as error:
        where = place if in_line else f"{place} line {error.lineno}"
        raise Refusal(where, f"not valid JSON ({error.msg})")
    except ValueError as error:
        raise Refusal(place, f"not valid JSON ({error})")


def read_text(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        raise Refusal(str(path), "cannot be read as UTF-8 text")
    except OSError as error:
        raise Refusal(str(path), f"cannot be opened ({error.strerror or type(error).__name__})")


def whole(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 1


def read_file(path: Path) -> list:
    """The entries of one findings file, each a dict of the eleven keys plus `logged` (a
    datetime) and `file`; Refusal on any problem."""
    named = FILE_NAME.fullmatch(path.name)
    if named is None:
        raise Refusal(str(path), "a findings file must be named <issue number>.json")
    data = parse(read_text(path), str(path))
    if not isinstance(data, dict):
        raise Refusal(str(path), "must hold one JSON object")
    missing = [k for k in TOP_KEYS if k not in data]
    extra = [k for k in data if k not in TOP_KEYS]
    if missing:
        raise Refusal(f"{path} key {missing[0]}", "missing top-level key")
    if extra:
        raise Refusal(f"{path} key {extra[0]}", "unknown top-level key; allowed: " + ", ".join(TOP_KEYS))
    issue = data["issue"]
    if not whole(issue):
        raise Refusal(f"{path} key issue", "must be the issue number, a whole number from 1")
    if issue != int(named.group(1)):
        raise Refusal(f"{path} key issue", f"holds {issue}, but the file name says {named.group(1)}")
    logged = data["logged"]
    if not isinstance(logged, str) or not LOGGED.fullmatch(logged):
        raise Refusal(f"{path} key logged", "must be a UTC time as YYYY-MM-DDTHH:MMZ")
    try:
        stamp = datetime.strptime(logged, LOGGED_FORMAT)
    except ValueError:
        raise Refusal(f"{path} key logged", "is not a real time")
    entries = data["findings"]
    if not isinstance(entries, list) or not entries:
        raise Refusal(f"{path} key findings", "must be a list with at least one finding")
    found, seen = [], set()
    for index, entry in enumerate(entries):
        problems = check_format.check_finding(entry, issue)
        if problems:
            key, reason = problems[0]
            where = f"{path} findings[{index}]" + (f" key {key}" if key else "")
            raise Refusal(where, reason)
        if entry["id"] in seen:
            raise Refusal(f"{path} findings[{index}] key id", f"duplicate id {entry['id']}")
        seen.add(entry["id"])
        found.append(dict(entry, logged=stamp, file=str(path)))
    return found


def read_findings(folder: Path) -> dict:
    """id -> entry for every findings file in `folder`; Refusal on any problem."""
    entries = {}
    if folder.is_dir():
        for path in sorted(folder.iterdir()):
            if path.is_file():
                for entry in read_file(path):
                    entries[entry["id"]] = entry
            else:
                raise Refusal(str(path), "only findings files belong here")
    return entries


def read_rulings(path: Path, entries: dict) -> list:
    """The rulings in file order as (ruling dict, `at` datetime); Refusal on any problem.
    Applying a ruling to `entries` is left to the caller's replay (apply_rulings)."""
    if not path.exists():
        return []
    text = read_text(path)
    if text.startswith(settings.BOM):
        raise Refusal(f"{path} line 1", "starts with a UTF-8 byte order mark")
    rulings = []
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()  # the newline that ends the last line
    for number, line in enumerate(lines, 1):
        place = f"{path} line {number}"
        item = parse(line, place, in_line=True)
        if not isinstance(item, dict):
            raise Refusal(place, "must be one JSON object")
        kind = item.get("ruling")
        if kind not in RULING_KEYS:
            raise Refusal(place, f"key ruling must be one of {', '.join(RULING_KEYS)}")
        for key in RULING_KEYS[kind]:
            if key not in item:
                raise Refusal(f"{place} key {key}", f"missing for a {kind} ruling")
        for key in item:
            if key not in RULING_KEYS[kind]:
                raise Refusal(f"{place} key {key}", f"not allowed in a {kind} ruling")
        if item["id"] not in entries:
            raise Refusal(f"{place} key id", f"{settings.echo(str(item['id']))} is not an id in any findings file")
        at = item["at"]
        if not isinstance(at, str) or not AT.fullmatch(at):
            raise Refusal(f"{place} key at", "must be a sweep entry's name time, YYYY-MM-DDTHHMMZ")
        try:
            moment = datetime.strptime(at, AT_FORMAT)
        except ValueError:
            raise Refusal(f"{place} key at", "is not a real time")
        if kind == "issued" and not whole(item["issue"]):
            raise Refusal(f"{place} key issue", "must be the new issue's number, a whole number from 1")
        if kind == "regroup":
            kind_of_group = check_format.FINDING_KINDS["group"]
            if not isinstance(item["group"], str) or not check_format.allowed(item["group"], kind_of_group):
                raise Refusal(f"{place} key group", "must be " + check_format.describe(kind_of_group))
        rulings.append((item, moment, number))
    return rulings


def apply_rulings(entries: dict, rulings: list, path: Path) -> dict:
    """id -> state {group, anchor, closed} after replaying the rulings in order."""
    state = {fid: {"group": e["group"], "anchor": e["logged"], "closed": None} for fid, e in entries.items()}
    for item, moment, number in rulings:
        current = state[item["id"]]
        if current["closed"]:
            raise Refusal(f"{path} line {number} key id",
                          f"{item['id']} is already closed by an earlier {current['closed']} ruling")
        if item["ruling"] in ("issued", "dropped"):
            current["closed"] = item["ruling"]
        elif item["ruling"] == "kept":
            current["anchor"] = moment
        else:
            current["group"] = item["group"]
    return state


def sweep_times(folder: Path) -> list:
    """The name times of the sweep entries in `folder`, one per entry file."""
    times = []
    if folder.is_dir():
        for path in folder.iterdir():
            match = sweep_due.ENTRY.fullmatch(path.name)
            if match and path.is_file():
                try:
                    times.append(datetime.strptime(match.group(1), "%Y-%m-%dT%H%MZ"))
                except ValueError:
                    continue
    return times


def report(entries: dict, state: dict, sweeps: list, group_at: int, keep_sweeps: int) -> list:
    """The output lines for the open entries."""
    groups = {}
    for fid, entry in entries.items():
        if state[fid]["closed"]:
            continue
        age = sum(1 for moment in sweeps if moment > state[fid]["anchor"])
        groups.setdefault(state[fid]["group"], []).append((entry, age))
    if not groups:
        return ["none"]
    lines, total, debt_total = [], 0, 0
    for name in sorted(groups, key=lambda g: (-len(groups[g]), g)):
        rows = sorted(groups[name], key=lambda row: tuple(int(p) for p in row[0]["id"].split("-")[1:]))
        debt = [entry["id"] for entry, _ in rows if entry["category"] == "debt"]
        head = f"{name}: {len(rows)} open, {len(debt)} debt"
        if debt:
            head += " (" + ", ".join(debt) + ")"
        if len(rows) >= group_at:
            head += " - draft one issue"
        lines.append(head)
        for entry, age in rows:
            line = f"  {entry['id']} impact {entry['impact']} age {age}"
            if age >= keep_sweeps:
                line += " - keep or drop"
            lines.append(line)
        total += len(rows)
        debt_total += len(debt)
    lines.append(f"total: {total} open, {len(groups)} groups, {debt_total} debt")
    return lines


def run() -> list:
    try:
        values = settings.read_settings(settings.CONF)
    except settings.SettingsError as error:
        raise Refusal("settings", str(error))
    entries = read_findings(FINDINGS_DIR)
    state = apply_rulings(entries, read_rulings(RULINGS, entries), RULINGS)
    return report(entries, state, sweep_times(RECORDS),
                  int(values["FINDINGS_GROUP_AT"][0]), int(values["FINDINGS_KEEP_SWEEPS"][0]))


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        lines = run()
    except Refusal as error:
        print(f"{PROG}: {error.place}: {error.reason}", file=sys.stderr)
        return 1
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
