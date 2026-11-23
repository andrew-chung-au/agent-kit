#!/usr/bin/env python3
"""Check the decision ledger and list its open points, rework items and budget (issue #204).

Run from the project folder as `make decisions [N=<issue number>]`. With N the target first
writes .scratch/issue-<n>.json as `make settings N=<n>` does, then runs
    python3 -B <kit>/scripts/decisions.py <n>
and without N it runs the script with no argument. It is read-only: it reads
agent-kit.conf, the dump (with N) and `_docs/records/decisions/<issue>.jsonl` as data,
writes nothing and starts no process. The format is in procedures/formats.md (Decision
ledger); the rules are in process.md (Orchestrator, Stop points, Lifecycle steps 3, 4, 7
and 9) and customizing.md (DECISION_BUDGET).

What it reads: the settings through check-format.py (loaded by path from this folder), at
the issue level with N (load_issue_settings, so an override or session ruling applies) and
at the project level without; every ledger file, one JSON object per line, append-only.

Terms:
- A ledger file is `<n>.jsonl`, one per issue, each line one event:
    open      {"event": "open", "id": "D-<n>-<k>", "at": "<YYYY-MM-DDTHH:MMZ>", "kind": <kind>,
               "mode": "stop" | "continue", "impact": "L"|"M"|"C", "effort": "S"|"R"|"E",
               "questions": [{"q": "q1", "text": ..., "options": {"A": ..., "B": ...},
               "recommended": "A"}, ...], "dependents": [<path, commit or issue id>, ...],
               "rollback": <what to undo, and where>}   (rollback for `continue` only)
    answer    {"event": "answer", "id": ..., "at": ..., "answer": "approve" | "reject" |
               "q<n>=<letter>[, q<n>=<letter>...]"}
    reworked  {"event": "reworked", "id": ..., "at": ..., "commit": "<7 to 40 hex>"}
- The kinds are STOP_KINDS (always wait for the human) and CONTINUE_KINDS (`choice`, the one
  kind a role may continue past). process.md lists the same names; a test compares them.
- A point's points are its effort converted as for findings (customizing.md, Points: S=1,
  R=2, E=3), derived from the `effort` letter and never stored.
- A point is open until an answer closes it. The open points are the total points of open
  `continue` points in every ledger file.
- A rework item is a `continue` point whose answer is `reject` or names, for some question,
  an option other than the recommended one (the one taken); it stays listed until a
  `reworked` entry names the commit.
- Budget: with B = DECISION_BUDGET and P the open points, `within budget` when P < B, or
  when nothing is open; `budget reached` when P == B and P > 0; `over budget` when P > B.

Output, the open points of issue N (of every issue without N) by id, then its rework items,
then the budget line:
    <id> impact <L|M|C> effort <S|R|E> points <p> mode <stop|continue> age <days> dependents <list or none>
    rework <id> answer <answer> rollback <rollback>
    open points <P>, budget <B>: <within budget|budget reached|over budget>
`none` when there is no ledger folder or nothing to list and no open points; exit 0, or 1
after the output when over budget. A refusal prints one line on standard error,
    decisions: <file> line <l>: <reason>
(or `decisions: <place>: <reason>` for the dump or settings) and exits 1: a line that is not
one JSON object (duplicate keys included), an unknown event, kind or key, a missing key, a
stored points field, a bad value, a `continue` point with a stop kind or no rollback, an id
of another issue or used twice, a question without a recommendation or with one that names
no offered option, an answer to an unknown or closed point or naming a question or option the
point doesn't offer, and a `reworked` entry with no rework item. Nothing is skipped silently.
A usage error exits 2. Standard library only.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("kit_check_format_for_decisions", _HERE / "check-format.py")
check_format = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_format)
settings = check_format.settings

PROG = "decisions"
USAGE = "Usage: make decisions [N=<issue number>]"
LEDGER = Path("_docs/records/decisions")
FILE_NAME = re.compile(r"([1-9][0-9]{0,8})\.jsonl")

# The stop kinds, in the order of process.md (Stop points). Each always waits for the human.
STOP_KINDS = ("spec", "security", "money", "irreversible", "outside", "dependency", "protected",
              "scope", "reasoning", "approach", "ship", "amend", "gate")
# The one kind a role may continue past, within DECISION_BUDGET.
CONTINUE_KINDS = ("choice",)
KINDS = STOP_KINDS + CONTINUE_KINDS
MODES = ("stop", "continue")
EVENTS = ("open", "answer", "reworked")
IMPACTS = check_format.LMC[1]
EFFORTS = check_format.SRE[1]
# The grade table's points (customizing.md, Points): S=1, R=2, E=3, in the Effort order.
EFFORT_POINTS = {effort: position + 1 for position, effort in enumerate(EFFORTS)}

AT = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}Z")
AT_FORMAT = "%Y-%m-%dT%H:%MZ"
COMMIT = re.compile(r"[0-9a-f]{7,40}")
QUESTION_ID = re.compile(r"q[1-9][0-9]*")
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
PAIR = re.compile(r"(q[1-9][0-9]*)=([A-Z])")

KEYS = {
    "open": ("event", "id", "at", "kind", "mode", "impact", "effort", "questions", "dependents", "rollback"),
    "answer": ("event", "id", "at", "answer"),
    "reworked": ("event", "id", "at", "commit"),
}
QUESTION_KEYS = ("q", "text", "options", "recommended")


class Refusal(Exception):
    """A refusal: the place (file and line) and the reason."""

    def __init__(self, place: str, reason: str):
        super().__init__(f"{place}: {reason}")
        self.place, self.reason = place, reason


def pairs_without_duplicates(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f"key {settings.echo(key)} is written twice")
        seen[key] = value
    return seen


def text_ok(value) -> bool:
    return isinstance(value, str) and value.strip() != "" and "\n" not in value and "\r" not in value


def parse_line(line: str, place: str) -> dict:
    try:
        item = json.loads(line, object_pairs_hook=pairs_without_duplicates)
    except json.JSONDecodeError as error:
        raise Refusal(place, f"not one JSON object ({error.msg})")
    except ValueError as error:
        raise Refusal(place, f"not one JSON object ({error})")
    if not isinstance(item, dict):
        raise Refusal(place, "must be one JSON object")
    return item


def check_keys(item: dict, place: str) -> str:
    """The event of an entry whose keys are allowed for it; Refusal otherwise."""
    event = item.get("event")
    if event not in EVENTS:
        raise Refusal(place, f"key event must be one of {', '.join(EVENTS)}, not {settings.echo(str(event))}")
    if "points" in item:
        raise Refusal(place, "key points is not stored: a point's points are derived from its effort "
                             "(S=1, R=2, E=3)")
    allowed = KEYS[event]
    for key in item:
        if key not in allowed:
            raise Refusal(place, f"unknown key {settings.echo(str(key))} in an {event} entry; "
                                 f"allowed: {', '.join(allowed)}")
    required = [k for k in allowed if k != "rollback"]
    for key in required:
        if key not in item:
            raise Refusal(place, f"missing key {key} in an {event} entry")
    return event


def check_common(item: dict, place: str, issue: int) -> datetime:
    point = item["id"]
    if not isinstance(point, str) or not re.fullmatch(check_format.DECISION_ID, point):
        raise Refusal(place, "key id must be `D-<issue>-<n>`")
    if int(point.split("-")[1]) != issue:
        raise Refusal(place, f"id {point} is not of issue {issue}, which the file name names")
    at = item["at"]
    if not isinstance(at, str) or not AT.fullmatch(at):
        raise Refusal(place, "key at must be a UTC time as YYYY-MM-DDTHH:MMZ")
    try:
        return datetime.strptime(at, AT_FORMAT).replace(tzinfo=timezone.utc)
    except ValueError:
        raise Refusal(place, "key at is not a real time")


def check_questions(questions, place: str) -> dict:
    """q id -> (offered letters, recommended letter); Refusal on any problem."""
    if not isinstance(questions, list) or not questions:
        raise Refusal(place, "key questions must be a list with at least one question")
    found = {}
    for index, question in enumerate(questions, 1):
        where = f"question {index}"
        if not isinstance(question, dict):
            raise Refusal(place, f"{where} must be an object")
        if "recommended" not in question:
            raise Refusal(place, f"{where} has no recommendation (key recommended)")
        for key in question:
            if key not in QUESTION_KEYS:
                raise Refusal(place, f"{where} has an unknown key {settings.echo(str(key))}; "
                                     f"allowed: {', '.join(QUESTION_KEYS)}")
        for key in QUESTION_KEYS:
            if key not in question:
                raise Refusal(place, f"{where} is missing key {key}")
        if question["q"] != f"q{index}":
            raise Refusal(place, f"{where} must have q `q{index}` (questions are q1, q2, ... in order)")
        if not text_ok(question["text"]):
            raise Refusal(place, f"q{index} key text must be one line of text")
        options = question["options"]
        if not isinstance(options, dict) or len(options) < 2:
            raise Refusal(place, f"q{index} key options must offer at least two lettered options")
        letters = tuple(options)
        if letters != tuple(LETTERS[:len(letters)]):
            raise Refusal(place, f"q{index} options must be lettered A, B, ... in order")
        if not all(text_ok(value) for value in options.values()):
            raise Refusal(place, f"q{index} each option must be one line of text")
        recommended = question["recommended"]
        if recommended not in letters:
            raise Refusal(place, f"q{index} recommends {settings.echo(str(recommended))}, which is not an "
                                 f"offered option ({', '.join(letters)})")
        found[f"q{index}"] = (letters, recommended)
    return found


def check_open(item: dict, place: str, issue: int) -> dict:
    stamp = check_common(item, place, issue)
    kind, mode = item["kind"], item["mode"]
    if kind not in KINDS:
        raise Refusal(place, f"key kind must be one of {', '.join(KINDS)}, not {settings.echo(str(kind))}")
    if mode not in MODES:
        raise Refusal(place, f"key mode must be stop or continue, not {settings.echo(str(mode))}")
    if mode == "continue" and kind not in CONTINUE_KINDS:
        raise Refusal(place, f"kind {kind} is a stop kind: it always waits for the human and can't be "
                             "logged as a continue point")
    if item["impact"] not in IMPACTS:
        raise Refusal(place, f"key impact must be one of {', '.join(IMPACTS)}, not "
                             f"{settings.echo(str(item['impact']))}")
    if item["effort"] not in EFFORTS:
        raise Refusal(place, f"key effort must be one of {', '.join(EFFORTS)}, not "
                             f"{settings.echo(str(item['effort']))}")
    questions = check_questions(item["questions"], place)
    dependents = item["dependents"]
    if not isinstance(dependents, list) or not all(text_ok(d) for d in dependents):
        raise Refusal(place, "key dependents must be a list of paths, commits or issue ids (one line each)")
    if mode == "continue":
        if "rollback" not in item:
            raise Refusal(place, "a continue point has no rollback (what to undo, and where)")
        if not text_ok(item["rollback"]):
            raise Refusal(place, "key rollback must be one line of text: what to undo, and where")
    elif "rollback" in item:
        raise Refusal(place, "a stop point has no rollback: nothing was built on it")
    return {"id": item["id"], "file": issue, "at": stamp, "mode": mode, "impact": item["impact"],
            "effort": item["effort"], "questions": questions, "dependents": list(dependents),
            "rollback": item.get("rollback"), "answer": None, "rework": False, "reworked": None}


def parse_answer(value, point: dict, place: str) -> bool:
    """True when the answer makes a rework item (a continue point only); Refusal on a bad answer."""
    if value in ("approve", "reject"):
        return point["mode"] == "continue" and value == "reject"
    if not isinstance(value, str) or not value:
        raise Refusal(place, "key answer must be approve, reject or q<n>=<option>, comma-separated")
    differs, seen = False, set()
    for part in re.split(r", ?", value):
        match = PAIR.fullmatch(part)
        if match is None:
            raise Refusal(place, f"answer part {settings.echo(part)} is not approve, reject or q<n>=<option>")
        question, letter = match.groups()
        if question not in point["questions"]:
            raise Refusal(place, f"{point['id']} has no question {question}")
        if question in seen:
            raise Refusal(place, f"the answer names {question} twice")
        seen.add(question)
        letters, recommended = point["questions"][question]
        if letter not in letters:
            raise Refusal(place, f"{point['id']} {question} offers no option {letter} ({', '.join(letters)})")
        differs = differs or letter != recommended
    return point["mode"] == "continue" and differs


def read_file(path: Path) -> dict:
    """id -> point state for one ledger file, in file order; Refusal on any problem."""
    named = FILE_NAME.fullmatch(path.name)
    if named is None:
        raise Refusal(str(path), "a ledger file must be named <issue number>.jsonl")
    issue = int(named.group(1))
    try:
        text = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        raise Refusal(str(path), "cannot be read as UTF-8 text")
    except OSError as error:
        raise Refusal(str(path), f"cannot be opened ({error.strerror or type(error).__name__})")
    if text.startswith(settings.BOM):
        raise Refusal(f"{path} line 1", "starts with a UTF-8 byte order mark")
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()  # the newline that ends the last line
    points = {}
    for number, line in enumerate(lines, 1):
        place = f"{path} line {number}"
        item = parse_line(line, place)
        event = check_keys(item, place)
        if event == "open":
            point = check_open(item, place, issue)
            if point["id"] in points:
                raise Refusal(place, f"id {point['id']} is used twice (an open entry already has it)")
            points[point["id"]] = point
            continue
        check_common(item, place, issue)
        point = points.get(item["id"])
        if point is None:
            raise Refusal(place, f"{item['id']} has no open entry earlier in this file")
        if event == "answer":
            if point["answer"] is not None:
                raise Refusal(place, f"{point['id']} is already closed by an earlier answer")
            point["rework"] = parse_answer(item["answer"], point, place)
            point["answer"] = item["answer"]
        else:
            if not isinstance(item["commit"], str) or not COMMIT.fullmatch(item["commit"]):
                raise Refusal(place, "key commit must be 7 to 40 lowercase hex")
            if not point["rework"]:
                raise Refusal(place, f"{point['id']} has no rework item")
            if point["reworked"] is not None:
                raise Refusal(place, f"{point['id']} is already reworked in {point['reworked']}")
            point["reworked"] = item["commit"]
    return points


def read_ledger(folder: Path) -> dict:
    """issue -> its points, for every ledger file in `folder`; Refusal on any problem."""
    ledger = {}
    if folder.is_dir():
        for path in sorted(folder.iterdir()):
            if not path.is_file():
                raise Refusal(str(path), "only ledger files belong here")
            points = read_file(path)
            ledger[int(path.name.split(".")[0])] = points
    return ledger


def open_points(ledger: dict) -> int:
    return sum(EFFORT_POINTS[p["effort"]] for points in ledger.values() for p in points.values()
               if p["answer"] is None and p["mode"] == "continue")


def budget_state(total: int, budget: int) -> str:
    if total > budget:
        return "over budget"
    if total == budget and total > 0:
        return "budget reached"
    return "within budget"


def report(ledger: dict, budget: int, issue, now: datetime):
    """(output lines, over budget) for issue `issue`, or every issue when it is None."""
    scope = [ledger.get(issue, {})] if issue is not None else [ledger[n] for n in sorted(ledger)]
    total = open_points(ledger)
    lines = []
    for points in scope:
        for p in points.values():
            if p["answer"] is None:
                age = max(0, (now - p["at"]).days)
                dependents = ", ".join(p["dependents"]) or "none"
                lines.append(f"{p['id']} impact {p['impact']} effort {p['effort']} "
                             f"points {EFFORT_POINTS[p['effort']]} mode {p['mode']} age {age} "
                             f"dependents {dependents}")
    for points in scope:
        for p in points.values():
            if p["rework"] and p["reworked"] is None:
                lines.append(f"rework {p['id']} answer {p['answer']} rollback {p['rollback']}")
    if not lines and total == 0:
        return ["none"], False
    state = budget_state(total, budget)
    lines.append(f"open points {total}, budget {budget}: {state}")
    return lines, state == "over budget"


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) > 1 or (args and not re.fullmatch(check_format.ISSUE, args[0])):
        print(USAGE, file=sys.stderr)
        return 2
    issue = int(args[0]) if args else None
    try:
        if issue is None:
            try:
                values = settings.read_settings(settings.CONF)
            except settings.SettingsError as error:
                raise Refusal("settings", str(error))
        else:
            try:
                values = check_format.load_issue_settings(issue)[0]
            except check_format.CheckError as error:
                raise Refusal(error.place, error.reason)
        budget = int(check_format.setting(values, "DECISION_BUDGET"))
        lines, over = report(read_ledger(LEDGER), budget, issue, datetime.now(timezone.utc))
    except Refusal as error:
        print(f"{PROG}: {error.place}: {error.reason}", file=sys.stderr)
        return 1
    for line in lines:
        print(line)
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
