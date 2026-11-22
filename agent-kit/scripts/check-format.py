#!/usr/bin/env python3
"""Check the fixed fields of a role return, a finding, a QA comment or a message to the
human (issue #198). It checks shape, not truth.

Run from the project folder as
    make check-format KIND=<return|finding|qa|message> FILE=.scratch/<name> [N=<issue number>]
or directly: python3 -B <kit>/scripts/check-format.py KIND FILE [N]. N is required for
`finding` and `qa` and refused for the others.

The layouts are defined once each: the role return and the finding in
procedures/formats.md, the QA comment in team/qa-engineer.md, the message to the human in
procedures/asking-the-human.md. This file holds them in one table, FORMATS (KIND to its
fields, each with its allowed values); a later KIND adds a row there.

The line rule (procedures/orchestrator-comments.md, "Lines scripts read"): every field is
`<Label>: <value>` alone on its line from column 1, the label worded exactly (case
included), one space after the colon, and a one-line value that is not empty. A line
ending in CRLF reads as LF; a file starting with a UTF-8 byte order mark is refused.

Output: `ok` and exit 0, or one line per problem on standard error,
    check-format: <FILE> line <l>: <reason>
(or `check-format: <FILE>: <reason>` when the file can't be read) and exit 1. A usage
error prints the usage and exits 2 without reading anything. File text in a reason goes
through settings.py's clip()/echo(). The script reads only FILE, as data, and starts no
process.

Interface for other kit scripts: FINDING_FIELDS (the eleven findings-log JSON keys in
order) and check_finding(finding, issue), which checks a finding given as a dict of key to
value and returns a list of (key, reason); the text form goes through the same function.
Standard library only, plus settings.py, loaded by path from this folder so that it works
under `python3 -I`.
"""
from __future__ import annotations

import importlib.util
import os
import re
import sys
from pathlib import Path

_SETTINGS_PATH = Path(__file__).resolve().parent / "settings.py"
_spec = importlib.util.spec_from_file_location("kit_settings_for_check_format", _SETTINGS_PATH)
settings = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(settings)

clip = settings.clip
echo = settings.echo
lines_of = settings.lines_of

PROG = "check-format"
BOM = settings.BOM
WHOLE = r"(?:0|[1-9][0-9]{0,5})"  # bounded, so int() never meets a huge digit string
POSITIVE = r"[1-9][0-9]*"
ISSUE = r"[1-9][0-9]{0,8}"  # as the Makefile's issue-number-ok

# Allowed-value kinds, in the style of settings.allowed():
#   ("choice", (v1, v2, ...))       exactly one of the listed tokens (case matters)
#   ("pattern", regex, described)   the whole value matches regex
#   ("text",)                       any value (the line rule already refuses an empty one)
#   ("recommendation",)             any value, but `none` only as `none, because <reason>`
#   ("slug", most)                  lowercase letters and digits in parts joined by single
#                                   hyphens, at most `most` characters
#   ("path",)                       a relative path inside the project, no `..`
#   ("finding_id",)                 F-<N>-<n>, N the issue number checked
#   ("related",)                    `none`, or a finding id F-<n>-<n> other than its own
LMC = ("choice", ("L", "M", "C"))
SRE = ("choice", ("S", "R", "E"))
COUNTS = ("pattern", rf"{WHOLE} fail / {WHOLE} log", "`<n> fail / <n> log`")
DECISION_ID = rf"D-{ISSUE}-{POSITIVE}"
FINDING_ID = rf"F-{ISSUE}-{POSITIVE}"
SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"

RETURN_FIELDS = (
    ("Status", ("choice", ("done", "blocked", "stopped-early"))),
    ("Issue", ("pattern", rf"#{ISSUE}", "`#<n>`")),
    ("Commit", ("pattern", r"[0-9a-f]{7,40}|none", "7 to 40 lowercase hex, or `none`")),
    ("Verdict", ("choice", ("PASS", "FAIL", "none"))),
    ("Findings", ("pattern", COUNTS[1] + "|none", "`<n> fail / <n> log`, or `none`")),
    ("Decisions", ("pattern", rf"none|{DECISION_ID}(?:, {DECISION_ID})*",
                   "`none`, or `D-<issue>-<n>` ids separated by a comma and one space")),
    ("Needs the human", ("choice", ("none", "yes"))),
    ("Recommendation", ("recommendation",)),
    ("Detail", ("pattern", r"https://\S+|(?!/)(?!.*\.\.)[A-Za-z0-9_.][A-Za-z0-9_./-]*",
                "an `https://` link, or a relative path inside the project with no `..`")),
    ("Checkpoint", ("pattern", r"none|(?!.*\.\.)[A-Za-z0-9_.][A-Za-z0-9_./-]*",
                    "a relative path with no `..`, or `none`")),
)

# The findings-log JSON keys, in the order of _docs/records/findings/196.json and 197.json.
# Each label is its key with the first letter capitalised and `_` as a space.
FINDING_FIELDS = ("id", "impact", "effort", "scope", "criterion", "category", "group",
                  "related", "recommendation", "what", "how_found")
FINDING_KINDS = {
    "id": ("finding_id",),
    "impact": LMC,
    "effort": SRE,
    "scope": ("choice", ("in", "out")),
    "criterion": ("pattern", rf"C{POSITIVE}|none", "`C<n>` with no leading zero, or `none`"),
    "category": ("choice", ("defect", "debt", "standard")),
    "group": ("slug", 40),
    "related": ("related",),
    "recommendation": ("recommendation",),
    "what": ("text",),
    "how_found": ("text",),
}


def label_of(key: str) -> str:
    """`how_found` -> `How found`: the mapping rule run backwards."""
    return key.replace("_", " ").capitalize()


def key_of(label: str) -> str:
    """`How found` -> `how_found`: lower-case the label and replace the space with `_`."""
    return label.lower().replace(" ", "_")


FINDING_LABELS = tuple((label_of(key), FINDING_KINDS[key]) for key in FINDING_FIELDS)

DECISION_BLOCK = (
    ("Decision", ("pattern", DECISION_ID, "`D-<issue>-<n>`")),
    ("Question", ("text",)),
    ("Impact", LMC),
    ("Recommended", ("recommendation",)),
)
SHIP_OR_FIX_BLOCK = (
    ("Ship-or-fix", ("pattern", FINDING_ID, "`F-<issue>-<n>`")),
    ("Impact", LMC),
    ("Effort", SRE),
    ("Recommended", ("recommendation",)),
)

# The one table. Each row: the first line (a fixed pattern, or None), the field lines that
# follow it, the blocks (first label -> fields; each block after one blank line), which
# head field holds the block counts, the tail fields (after one blank line) and what may
# follow ("nothing", "requests" after `Needs the human: yes`, "detail" unchecked, or
# "detail-no-findings": unchecked but holding no finding label).
FORMATS = {
    "return": {"first": None, "head": RETURN_FIELDS, "blocks": {}, "counts": None,
               "tail": (), "after": "requests"},
    "finding": {"first": None, "head": (), "blocks": {"Id": FINDING_LABELS}, "counts": None,
                "tail": (), "after": "nothing"},
    "qa": {"first": (re.compile(r"QA: (PASS|FAIL) *"), "`QA: PASS` or `QA: FAIL`"),
           "head": (("Commit", ("pattern", r"[0-9a-f]{7,40}", "7 to 40 lowercase hex")),
                    ("Findings", COUNTS)),
           "blocks": {"Id": FINDING_LABELS}, "counts": "Findings", "tail": (),
           "after": "detail-no-findings"},
    "message": {"first": None,
                "head": (("Needs you", ("pattern", rf"{WHOLE} decision points, {WHOLE} ship-or-fix",
                                        "`<n> decision points, <n> ship-or-fix`")),),
                "blocks": {"Decision": DECISION_BLOCK, "Ship-or-fix": SHIP_OR_FIX_BLOCK},
                "counts": "Needs you", "tail": (("Status", ("text",)),), "after": "detail"},
}
NEEDS_N = ("finding", "qa")
REQUEST_LABELS = ("Approval needed", "Decision needed")
ALL_LABELS = sorted({label for row in FORMATS.values()
                     for fields in [row["head"], row["tail"], *row["blocks"].values()]
                     for label, _ in fields}, key=len, reverse=True)
# A line that carries a label, perhaps indented or after a list marker, any case, any spacing.
LABELLED = re.compile(r"([ \t]*(?:(?:[-*+]|[0-9]+\.)[ \t]+)?)(" + "|".join(re.escape(x) for x in ALL_LABELS)
                      + r"):(.*)", re.I | re.S)


def recommendation_ok(value: str) -> bool:
    first = re.match(r"[A-Za-z]*", value).group(0)
    if first.lower() != "none":
        return True
    match = re.fullmatch(r"none, because (.*)", value, re.S)
    return bool(match and match.group(1).strip())


def allowed(value: str, kind: tuple, own_id: str = "", issue: int | None = None) -> bool:
    """True when value is one of the values `kind` allows (settings.allowed() for choices)."""
    tag = kind[0]
    if tag == "choice":
        return settings.allowed(value, kind)
    if tag == "pattern":
        return re.fullmatch(kind[1], value) is not None
    if tag == "text":
        return value.strip() != ""
    if tag == "recommendation":
        return value.strip() != "" and recommendation_ok(value)
    if tag == "slug":
        return len(value) <= kind[1] and re.fullmatch(SLUG, value) is not None
    if tag == "finding_id":
        return issue is not None and re.fullmatch(rf"F-{issue}-{POSITIVE}", value) is not None
    if tag == "related":
        return value == "none" or (re.fullmatch(FINDING_ID, value) is not None and value != own_id)
    raise ValueError(f"unknown kind {tag!r}")


def describe(kind: tuple, issue: int | None = None) -> str:
    tag = kind[0]
    if tag == "choice":
        return settings.describe(kind)
    if tag == "pattern":
        return kind[2]
    if tag == "text":
        return "any text"
    if tag == "recommendation":
        return "a recommendation; `none` only as `none, because <reason>`"
    if tag == "slug":
        return f"a slug: lowercase letters and digits in parts joined by single hyphens, at most {kind[1]} characters"
    if tag == "finding_id":
        return f"`F-{issue}-<n>` with n a whole number from 1, no leading zero"
    if tag == "related":
        return "a finding id `F-<n>-<n>` other than its own, or `none`"
    raise ValueError(f"unknown kind {tag!r}")


def value_problem(label: str, value: str, kind: tuple, own_id: str = "", issue: int | None = None):
    if allowed(value, kind, own_id, issue):
        return None
    if kind[0] == "related" and value == own_id:
        return f"{label} names the finding's own id {echo(value)}"
    return f"{label} has {echo(value)}; allowed: {describe(kind, issue)}"


def check_finding(finding, issue: int) -> list:
    """Check one finding given as a dict of key to value (the findings-log JSON form).
    Returns a list of (key, reason); key is None for a problem with the whole dict."""
    if not isinstance(finding, dict):
        return [(None, "a finding must be an object of key to value")]
    problems = []
    keys = tuple(finding)
    if keys != FINDING_FIELDS:
        missing = [k for k in FINDING_FIELDS if k not in finding]
        extra = [k for k in keys if k not in FINDING_FIELDS]
        if missing:
            problems.append((None, "missing " + ", ".join(missing)))
        if extra:
            problems.append((None, "unknown key " + ", ".join(echo(str(k)) for k in extra)))
        if not missing and not extra:
            problems.append((None, "keys are out of order; the order is " + ", ".join(FINDING_FIELDS)))
    own_id = finding.get("id") if isinstance(finding.get("id"), str) else ""
    for key in FINDING_FIELDS:
        if key not in finding:
            continue
        value = finding[key]
        label = label_of(key)
        if not isinstance(value, str):
            problems.append((key, f"{label} is not text"))
        elif value == "" or value.strip(" \t") == "":
            problems.append((key, f"{label} has an empty value"))
        elif "\n" in value or "\r" in value:
            problems.append((key, f"{label} must be one line"))
        else:
            reason = value_problem(label, value, FINDING_KINDS[key], own_id, issue)
            if reason:
                problems.append((key, reason))
    return problems


class Checker:
    def __init__(self, lines: list, issue: int | None):
        self.lines = lines
        self.issue = issue
        self.problems = []  # (line number, reason)
        self.ids = {}

    def problem(self, index: int, reason: str) -> None:
        self.problems.append((index + 1, reason))

    def line(self, index: int):
        return self.lines[index] if index < len(self.lines) else None

    def form_problem(self, line: str, label: str):
        """None when line is `label: <value>` by the line rule; else (is this label, reason)."""
        match = LABELLED.fullmatch(line)
        if match is None or match.group(2).lower() != label.lower():
            return False, None
        lead, found, rest = match.groups()
        if lead:
            return True, f"a {label}: line must start at column 1, with no indent or list marker"
        if found != label:
            return True, f"label {echo(found + ':')} must be written `{label}:`"
        if rest.strip(" \t") == "":
            return True, f"{label} has an empty value"
        if not rest.startswith(" ") or rest[1:2] in (" ", "\t"):
            return True, f"`{label}:` must be followed by exactly one space, then the value"
        return True, None

    def read_fields(self, i: int, fields: tuple, what: str):
        """Read field lines in order from line index i. Returns (next index, {label: (value, index)})."""
        values = {}
        labels = [label for label, _ in fields]
        for position, (label, kind) in enumerate(fields):
            line = self.line(i)
            if line is None or line.strip(" \t") == "":
                self.problem(i, f"missing the {label}: line of the {what}")
                continue
            mine, reason = self.form_problem(line, label)
            if mine:
                if reason:
                    self.problem(i, reason)
                else:
                    value = line[len(label) + 2:].rstrip(" \t")
                    values[label] = (value, i)
                i += 1
                continue
            later = [x for x in labels[position + 1:] if self.form_problem(line, x)[0]]
            if later:
                self.problem(i, f"missing the {label}: line of the {what} (found {later[0]}: here)")
                continue
            self.problem(i, f"expected `{label}: <value>` in the {what}, found {echo(line)}")
            i += 1
        return i, values

    def check_values(self, values: dict, fields: tuple) -> None:
        for label, kind in fields:
            if label in values:
                value, index = values[label]
                reason = value_problem(label, value, kind, issue=self.issue)
                if reason:
                    self.problem(index, reason)

    def check_finding_block(self, values: dict, start: int) -> None:
        as_dict = {key_of(label): value for label, (value, _) in values.items()}
        index_of = {key_of(label): index for label, (_, index) in values.items()}
        for key, reason in check_finding(as_dict, self.issue):
            if key is None:
                continue  # a missing line was already reported by read_fields
            self.problem(index_of[key], reason)
        if "Id" in values:
            value, index = values["Id"]
            if value in self.ids:
                self.problem(index, f"finding id {echo(value)} is used twice (first at line {self.ids[value] + 1})")
            else:
                self.ids[value] = index

    def block_start(self, i: int, blocks: dict):
        """The block label when line i is blank and line i+1 starts a block, else None."""
        if self.line(i) != "" or self.line(i + 1) is None:
            return None
        for label in blocks:
            if self.form_problem(self.line(i + 1), label)[0]:
                return label
        return None

    def run(self, row: dict) -> None:
        i = 0
        if row["first"] is not None:
            pattern, described = row["first"]
            if not pattern.fullmatch(self.line(0) or ""):
                self.problem(0, f"line 1 must be exactly {described} (only spaces may follow), found "
                                f"{echo(self.line(0) or '')}")
            i = 1
        i, head = self.read_fields(i, row["head"], "header")
        self.check_values(head, row["head"])
        counts = {label: 0 for label in row["blocks"]}
        while True:
            label = self.block_start(i, row["blocks"])
            if label is None:
                break
            start = i + 1
            i, values = self.read_fields(start, row["blocks"][label], f"{label} block")
            if row["blocks"][label] is FINDING_LABELS:
                self.check_finding_block(values, start)
            else:
                self.check_values(values, row["blocks"][label])
            counts[label] += 1
        if row["counts"] and row["counts"] in head:
            self.check_counts(row, head[row["counts"]], counts)
        if row["tail"]:
            if self.line(i) != "":
                self.problem(i, f"expected a blank line, then the {row['tail'][0][0]}: line")
            else:
                i += 1
            i, tail = self.read_fields(i, row["tail"], "message")
            self.check_values(tail, row["tail"])
        self.check_after(row, i, head)

    def check_counts(self, row: dict, head_value: tuple, counts: dict) -> None:
        value, index = head_value
        kind = dict(row["head"])[row["counts"]]
        if not allowed(value, kind):
            return  # already refused as a value
        numbers = [int(n) for n in re.findall(r"[0-9]+", value)]
        if row["counts"] == "Findings":
            fail, log = numbers
            if fail + log != counts["Id"]:
                self.problem(index, f"Findings counts {fail} + {log} do not match the {counts['Id']} finding block(s)")
            verdict = (self.line(0) or "").startswith("QA: PASS")
            if verdict and fail > 0:
                self.problem(index, f"QA: PASS with {fail} fail finding(s); a fail finding means QA: FAIL")
        else:
            decisions, ships = numbers
            if decisions != counts["Decision"]:
                self.problem(index, f"Needs you counts {decisions} decision points but there are "
                                    f"{counts['Decision']} Decision block(s)")
            if ships != counts["Ship-or-fix"]:
                self.problem(index, f"Needs you counts {ships} ship-or-fix but there are "
                                    f"{counts['Ship-or-fix']} Ship-or-fix block(s)")

    def check_after(self, row: dict, i: int, head: dict) -> None:
        rest = self.lines[i:]
        after = row["after"]
        if after == "requests" and head.get("Needs the human", ("",))[0] == "yes":
            self.check_requests(i)
            return
        if after in ("nothing", "requests"):
            for offset, line in enumerate(rest):
                if line.strip(" \t"):
                    why = ("with `Needs the human: none` nothing may follow the ten lines"
                           if after == "requests" and head.get("Needs the human", ("",))[0] == "none"
                           else "nothing may follow here")
                    self.problem(i + offset, f"unexpected text {echo(line)}: {why}")
                    return
            return
        if after == "detail-no-findings":
            if rest and rest[0].strip(" \t"):
                self.problem(i, "expected a blank line before the detail")
            for offset, line in enumerate(rest):
                for label, _ in FINDING_LABELS:
                    if self.form_problem(line, label)[0]:
                        self.problem(i + offset, f"a {label}: line outside a finding block; each finding is "
                                                 "a block after one blank line, before the detail")
                        break

    def check_requests(self, i: int) -> None:
        if self.line(i) != "" or not (self.line(i + 1) or "").strip(" \t"):
            self.problem(i, "with `Needs the human: yes`, one blank line and then a request must follow")
            return
        # A new request starts only at a column-1 line after an empty line, outside a fenced
        # block. Lines inside a fence, indented lines and whitespace-only lines (a diff's empty
        # context line is one space) belong to the request before them.
        previous_empty = True
        fenced = False
        for index in range(i + 1, len(self.lines)):
            line = self.lines[index]
            if fenced:
                if line.lstrip(" ").startswith("```"):
                    fenced = False
                previous_empty = False
                continue
            if line == "":
                previous_empty = True
                continue
            fence = line.lstrip(" ").startswith("```")
            starts = previous_empty and line[0] not in " \t" and not fence
            previous_empty = False
            if starts and not re.match(r"(?:Approval needed|Decision needed): \S", line):
                self.problem(index, f"a request must start `Approval needed: ` or `Decision needed: `, "
                                    f"found {echo(line)}")
            if fence:
                fenced = True


def check_text(kind: str, text: str, issue: int | None) -> list:
    """(line number, reason) for each problem in a file's text."""
    if text.startswith(BOM):
        return [(1, "starts with a UTF-8 byte order mark; save the file without one")]
    lines = lines_of(text)
    while lines and lines[-1] == "":
        lines.pop()  # the final newline, and blank lines at the end
    row = FORMATS[kind]
    if row["blocks"] and not row["head"] and row["first"] is None:
        # A file of findings only: read as if a blank line came before the first block.
        checker = Checker([""] + lines, issue)
        checker.run(row)
        if not checker.ids and not checker.problems:
            checker.problem(1, "no finding block; a finding starts with an Id: line")
        return [(max(n - 1, 1), reason) for n, reason in checker.problems]
    checker = Checker(lines, issue)
    checker.run(row)
    return checker.problems


USAGE = ("Usage: make check-format KIND=<return|finding|qa|message> FILE=.scratch/<name> [N=<issue number>] "
         "(N is required for finding and qa, and not used for the others)")
FILE_CHARS = re.compile(r"[A-Za-z0-9._/-]+")


def file_ok(name: str) -> bool:
    """The rule issue-comment applies: one word under .scratch/, letters digits . _ / - only, no `..`."""
    return (FILE_CHARS.fullmatch(name) is not None and name.startswith(".scratch/")
            and ".." not in name and not name.startswith("-"))


def symlink_on_path(name: str) -> bool:
    parts = name.split("/")
    return any(os.path.islink("/".join(parts[:n])) for n in range(1, len(parts) + 1))


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) not in (2, 3) or args[0] not in FORMATS or not file_ok(args[1]):
        print(USAGE, file=sys.stderr)
        return 2
    kind, name = args[0], args[1]
    if kind in NEEDS_N:
        if len(args) != 3 or not re.fullmatch(ISSUE, args[2]):
            print(USAGE, file=sys.stderr)
            return 2
        issue = int(args[2])
    else:
        if len(args) == 3:
            print(USAGE, file=sys.stderr)
            return 2
        issue = None
    path = Path(name)
    if symlink_on_path(name):
        print(f"{PROG}: {name}: FILE or a folder on its path is a symbolic link", file=sys.stderr)
        return 1
    try:
        if not path.is_file():
            reason = "not found" if not path.exists() else "not a regular file"
            print(f"{PROG}: {name}: {reason}", file=sys.stderr)
            return 1
        data = path.read_bytes()
    except OSError as error:
        print(f"{PROG}: {name}: cannot be opened ({error.strerror or type(error).__name__})", file=sys.stderr)
        return 1
    try:
        text = data.decode("utf-8")
    except ValueError:
        print(f"{PROG}: {name}: cannot be read as UTF-8 text", file=sys.stderr)
        return 1
    problems = check_text(kind, text, issue)
    if not problems:
        print("ok")
        return 0
    for number, reason in problems:
        print(f"{PROG}: {name} line {number}: {reason}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
