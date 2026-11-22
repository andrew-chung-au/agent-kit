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

`qa` also checks the verdict against the issue's settings (issue #199): it reads
agent-kit.conf and the dump .scratch/issue-<N>.json (written by `make settings N=<N>`)
through settings.read_settings at the issue level, then checks that the comment is
`QA: FAIL` exactly when a finding block fails (finding_fails below), that the `Findings:`
counts match the failing and logged blocks, and that a `Related:` id of this issue is in a
block of the same comment or of an earlier owner `QA:` comment in the dump.

Output: `ok` and exit 0, or one line per problem on standard error,
    check-format: <FILE> line <l>: <reason>
(or `check-format: <FILE>: <reason>` when the file or, for `qa`, the dump or the settings
can't be read) and exit 1. A usage error prints the usage and exits 2 without reading
anything. File text in a reason goes through settings.py's clip()/echo(). The script reads
FILE, and for `qa` the conf and the dump, as data, and starts no process.

Interface for other kit scripts: FINDING_FIELDS (the eleven findings-log JSON keys in
order) and check_finding(finding, issue), which checks a finding given as a dict of key to
value and returns a list of (key, reason); the text form goes through the same function.
read_qa(text, issue, values, known) parses a QA comment into (problems, verdict, findings);
finding_fails(finding, values) says whether one finding fails under the settings;
owner_qa_comments(issue) lists the owner `QA:` comment bodies of a dump, oldest first; and
load_issue_settings(number) reads the conf and the dump (CheckError on a refusal).
scripts/route-findings.py uses them. Standard library only, plus settings.py, loaded by
path from this folder so that it works under `python3 -I`.
"""
from __future__ import annotations

import importlib.util
import json
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
    "category": ("choice", ("defect", "debt", "standard", "criterion")),
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
    ("Points", ("pattern", r"[1-9][0-9]{0,5}", "a whole number from 1, no leading zero")),
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


def verdict_of(first_line: str):
    """`PASS` or `FAIL` from a QA comment's first line, or None when it is not the verdict line."""
    match = FORMATS["qa"]["first"][0].fullmatch(first_line)
    return match.group(1) if match else None
REQUEST_LABELS = ("Approval needed", "Decision needed")
REQUEST_HEADER = re.compile(r"(?:Approval needed|Decision needed): \S")
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


def setting(values: dict, name: str) -> str:
    """A setting's value from read_settings' dict (name -> (value, source)) or a plain dict."""
    value = values[name]
    return value[0] if isinstance(value, tuple) else value


def finding_fails(finding: dict, values: dict) -> bool:
    """True when a finding fails (customizing.md, team/qa-engineer.md): its impact is at or
    above QA_FAIL_AT, and it is `Scope: in` or QA_SCOPE_STRICT is `no`. `finding` holds at
    least the impact and scope keys, with allowed values; `values` is read_settings' result.
    The impact order is the grade table's (L, M, C), not a policy value."""
    order = LMC[1]
    high_enough = order.index(finding["impact"]) >= order.index(setting(values, "QA_FAIL_AT"))
    return high_enough and (finding["scope"] == "in" or setting(values, "QA_SCOPE_STRICT") == "no")


def gradable(finding: dict) -> bool:
    """True when the fields finding_fails and the router read have allowed values."""
    return (finding.get("impact") in LMC[1] and finding.get("effort") in SRE[1]
            and finding.get("scope") in ("in", "out"))


class Checker:
    def __init__(self, lines: list, issue: int | None, values: dict | None = None, known=None):
        self.lines = lines
        self.issue = issue
        self.values = values  # read_settings' result, for the verdict checks of `qa`
        self.known = known  # finding ids of earlier owner QA: comments, for `Related:` in `qa`
        self.problems = []  # (line number, reason)
        self.ids = {}
        self.findings = []  # (dict of key -> value, dict of key -> line index) per finding block

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
        self.findings.append((as_dict, index_of))

    def check_related(self) -> None:
        """`qa` with known ids: a Related: id of this issue must be in a block of this comment
        or of an earlier owner QA: comment. An id of another issue is checked for shape only."""
        if self.known is None:
            return
        own = re.compile(rf"F-{self.issue}-{POSITIVE}")
        for finding, index_of in self.findings:
            value = finding.get("related", "none")
            if own.fullmatch(value) and value != finding.get("id") and value not in self.ids \
                    and value not in self.known:
                self.problem(index_of["related"],f"Related names {echo(value)}, which no finding of this comment or of an "
                                    f"earlier owner QA: comment on issue #{self.issue} holds")

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
        self.check_related()
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
                return
            if self.values is None:
                passed = (self.line(0) or "").startswith("QA: PASS")
                if passed and fail > 0:
                    self.problem(index, f"QA: PASS with {fail} fail finding(s); a fail finding means QA: FAIL")
                return
            self.check_verdict(index, fail, log)
        else:
            decisions, ships = numbers
            if decisions != counts["Decision"]:
                self.problem(index, f"Needs you counts {decisions} decision points but there are "
                                    f"{counts['Decision']} Decision block(s)")
            if ships != counts["Ship-or-fix"]:
                self.problem(index, f"Needs you counts {ships} ship-or-fix but there are "
                                    f"{counts['Ship-or-fix']} Ship-or-fix block(s)")

    def check_verdict(self, index: int, fail: int, log: int) -> None:
        """`qa` with settings: the counts and line 1 follow from finding_fails."""
        findings = [finding for finding, _ in self.findings]
        if not all(gradable(finding) for finding in findings):
            return  # a block's Impact, Effort or Scope was already refused
        failing = sum(1 for finding in findings if finding_fails(finding, self.values))
        rule = (f"QA_FAIL_AT={setting(self.values, 'QA_FAIL_AT')}, "
                f"QA_SCOPE_STRICT={setting(self.values, 'QA_SCOPE_STRICT')}")
        if fail != failing or log != len(findings) - failing:
            self.problem(index, f"Findings counts {fail} fail / {log} log, but under the settings ({rule}) "
                                f"{failing} block(s) fail and {len(findings) - failing} log")
        verdict = verdict_of(self.line(0) or "")
        if verdict == "PASS" and failing > 0:
            self.problem(0, f"QA: PASS with {failing} fail finding(s) under the settings ({rule}); "
                            "a fail finding means QA: FAIL")
        elif verdict == "FAIL" and failing == 0:
            self.problem(0, f"QA: FAIL with no fail finding under the settings ({rule}); "
                            "QA fails only on a finding that fails")

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
        # The tail is a list of requests. Each is a header line at column 1 starting
        # `Approval needed: ` or `Decision needed: `, then its body. The first line after the
        # blank is always a header, whatever it looks like. A later header starts only at a
        # column-1 line after an empty line, outside a fenced block (``` or ~~~); lines inside
        # a fence, fence lines, indented lines and whitespace-only lines (a diff's empty
        # context line is one space) are body lines of the request before them.
        first = i + 1
        previous_empty = False
        fence = None  # the marker of the open fence, if any
        for index in range(first, len(self.lines)):
            line = self.lines[index]
            marker = next((m for m in ("```", "~~~") if line.lstrip(" ").startswith(m)), None)
            if fence is not None:
                if marker == fence:
                    fence = None
                previous_empty = False
                continue
            if line == "":
                previous_empty = True
                continue
            header = index == first or (previous_empty and line[0] not in " \t" and marker is None)
            previous_empty = False
            if header and not REQUEST_HEADER.match(line):
                self.problem(index, f"a request must start at column 1 with `Approval needed: ` or "
                                    f"`Decision needed: `, found {echo(line)}")
            if marker is not None:
                fence = marker


def run_checker(kind: str, text: str, issue: int | None, values=None, known=None):
    """The problems of a file's text, and the Checker that read it (None after a BOM)."""
    if text.startswith(BOM):
        return [(1, "starts with a UTF-8 byte order mark; save the file without one")], None
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
        return [(max(n - 1, 1), reason) for n, reason in checker.problems], checker
    checker = Checker(lines, issue, values, known)
    checker.run(row)
    return checker.problems, checker


def check_text(kind: str, text: str, issue: int | None, values=None, known=None) -> list:
    """(line number, reason) for each problem in a file's text. For `qa`, `values` (read_settings'
    result) turns on the verdict checks and `known` (ids of earlier owner QA: comments) the
    Related: check."""
    return run_checker(kind, text, issue, values, known)[0]


def read_qa(text: str, issue: int, values=None, known=None):
    """Parse a QA comment with the `qa` row: (problems, verdict, findings). verdict is `PASS`,
    `FAIL` or None; findings is one dict of key -> value per finding block, in order, holding
    the keys whose lines were read. With values and known, problems include the verdict and
    Related: checks, as `make check-format KIND=qa` prints them."""
    problems, checker = run_checker("qa", text, issue, values, known)
    if checker is None:
        return problems, None, []
    return problems, verdict_of(checker.line(0) or ""), [dict(f) for f, _ in checker.findings]


class CheckError(Exception):
    """A refusal before the text is checked: the place (a file name) and the reason."""

    def __init__(self, place: str, reason: str):
        super().__init__(f"{place}: {reason}")
        self.place, self.reason = place, reason


def owner_qa_comments(issue: dict) -> list:
    """The bodies of the owner `QA:` comments of a dump read by settings.load_issue, oldest
    first (createdAt, ties by list order). A comment counts when its author is the repository
    owner's account and its first line starts `QA:`; a deleted author is skipped."""
    owner = issue["repositoryOwner"]["login"]
    found = []
    for index, item in enumerate(issue["comments"]):
        author = item.get("author") if isinstance(item, dict) else None
        body = item.get("body") if isinstance(item, dict) else None
        if not isinstance(author, dict) or author.get("login") != owner or not isinstance(body, str):
            continue
        if lines_of(body)[0].startswith("QA:"):
            found.append((str(item.get("createdAt", "")), index, body))
    found.sort(key=lambda c: (c[0], c[1]))
    return [body for _, _, body in found]


def load_issue_settings(number: int):
    """(values, issue) for issue `number`: read_settings over agent-kit.conf and the dump
    .scratch/issue-<number>.json, and the dump itself. CheckError on a missing or unreadable
    dump (run `make settings N=<n>` first) and on a settings refusal (the reader's reason)."""
    dump = Path(settings.DUMP_FOLDER) / f"issue-{number}.json"
    first = f"run `make settings N={number}` first"
    try:
        if symlink_on_path(str(dump)) or not dump.is_file():
            raise CheckError(str(dump), f"missing or not a regular file; {first}")
        json.loads(dump.read_bytes().decode("utf-8"))
    except OSError as error:
        raise CheckError(str(dump), f"cannot be opened ({error.strerror or type(error).__name__}); {first}")
    except ValueError:
        raise CheckError(str(dump), f"cannot be read as JSON; {first}")
    try:
        values = settings.read_settings(settings.CONF, dump)
        issue = settings.load_issue(dump)
    except settings.SettingsError as error:
        raise CheckError("settings", str(error))
    return values, issue


def finding_ids(bodies, issue: int) -> set:
    """The finding ids in the finding blocks of the given QA comment bodies (problems ignored)."""
    ids = set()
    for body in bodies:
        ids.update(f["id"] for f in read_qa(body, issue)[2] if "id" in f)
    return ids


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
    values = known = None
    if kind == "qa":
        try:
            values, dumped = load_issue_settings(issue)
        except CheckError as error:
            print(f"{PROG}: {error.place}: {error.reason}", file=sys.stderr)
            return 1
        known = finding_ids(owner_qa_comments(dumped), issue)
    problems = check_text(kind, text, issue, values, known)
    if not problems:
        print("ok")
        return 0
    for number, reason in problems:
        print(f"{PROG}: {name} line {number}: {reason}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
