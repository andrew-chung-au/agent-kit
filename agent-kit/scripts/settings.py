#!/usr/bin/env python3
"""The kit's settings: one table, and the reader that resolves them from agent-kit.conf
and, for one issue, from the issue's dump.

Run from the project folder (the one holding agent-kit.conf), normally as `make settings`
(no arguments) or `make settings N=<issue number>` (one argument, the issue number; the
target first writes .scratch/issue-<n>.json with `make issue-dump`'s recipe).

What each setting does, and which issue makes it take effect, is in the kit's
customizing.md. This file holds the only definition of the settings: SETTINGS below,
with each name, its default (one per profile for the profile settings) and its allowed
values. Nothing else defines them.

Resolution, lowest to highest: kit default, then the profile (PROFILE=solo|team|fleet,
unset meaning solo), then a project line in agent-kit.conf, then, with an issue, the issue
override, then the session ruling. A written line always beats the profile. Nothing else
changes a value: environment variables and make variables with a setting's name are ignored.

agent-kit.conf is read as TEXT, never sourced or run, and this reader starts no shell or
other process (as github_api.py reads GITHUB_REPO). A setting line starts at column 1 as
NAME=value, NAME="value" or NAME='value', with nothing after it but spaces or tabs.
Comment lines, blank lines, indented lines and the existing conf names (KNOWN_CONF) are
passed over unread. Refused, with the line number: an unknown name at the start of a
line, an unknown profile, a value outside the allowed values (empty or wrong case
included), the same setting or PROFILE written twice, anything after the value, a setting
or PROFILE followed by = anywhere but its own line at column 1 (indented, after export,
after another assignment or `;`, inside `if ... fi`), and a leading UTF-8 byte order mark.
A missing conf is refused too.

The issue is read from the JSON `make issue-dump N=<n>` writes (.scratch/issue-<n>.json,
with the repositoryOwner field github_api.py dump adds); the reader never calls GitHub.
- Issue override: a body line `Overrides: NAME=value, NAME=value` at column 1, applied
  only when the issue has the `overrides` label. The approved body hash covers it; the
  orchestrator checks the hash before `make settings N=<n>`, and this reader does not.
- Session ruling: in a comment by the repository owner's account whose first line starts
  `Orchestrator: Ruling` and that has a `Human ruled: <YYYY-MM-DD>` line, each line
  `Ruling: NAME=value` sets a value for this issue. A `Ruling:` line that does not start
  with NAME= is a process ruling: recorded, passed over here. A line
  `Waiver: <gate> - <reason>` records a QA gate the human waived; the gate must be in the
  resolved WAIVABLE_GATES value. A waiver changes no setting; nothing here acts on it.
  Later ruling comments beat earlier ones (createdAt, ties by list order).
At both issue levels these are refused: a name that is not a setting, a name in
PROJECT_ONLY, a value outside the allowed values, a value in BOUNDS (bounds no level can
cross), the same name twice, and a bullet or indented line with the label.

Output: PROFILE first, then one line per setting in table order,
    <NAME>=<value> (<source>)
where the source is `kit default`, `profile <name>`, `agent-kit.conf line <n>`,
`issue #<n> body line <l>` or `issue #<n> ruling <createdAt> line <l>`.
A refusal prints nothing on standard output and one line on standard error,
    settings: <place>: <reason>
(the place is `agent-kit.conf line <n>`, `issue #<n> body line <l>`,
`issue #<n> ruling <createdAt> line <l>` or a file name) and exits 1.

Interface for other kit scripts: import this module and call
read_settings(conf_path, issue_path=None). It returns a dict, in table order, of
name -> (value, source), or raises SettingsError with the reason. Values are returned as
the text written. The issue file must be named issue-<n>.json; <n> is the issue asked for.
read_rulings(issue, owner, waivable) parses the ruling comments of an issue already
parsed from JSON (the closing gate reuses it). Standard library only.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CONF = "agent-kit.conf"
DUMP_FOLDER = ".scratch"
PROFILES = ("solo", "team", "fleet")
DEFAULT_PROFILE = "solo"

# Allowed-value kinds:
#   ("choice", (v1, v2, ...))   exactly one of the listed tokens (case matters)
#   ("whole", lo, hi)           a whole number lo..hi: "0" or digits with no leading zero, no sign
#   ("minutes", lo, hi)         "milestone", or "<n>m" with n a whole number lo..hi
#   ("ship_rule",)              "none", or one to three comma-separated key:value pairs,
#                               no spaces, each key at most once (SHIP_RULE_KEYS)
#   ("subset", (v1, v2, ...))   "none", or one or more of the listed tokens, comma-separated,
#                               no spaces, each at most once, in any order
SHIP_RULE_KEYS = (
    ("impact", ("choice", ("L", "M", "C"))),
    ("effort", ("choice", ("S", "R", "E"))),
    ("rounds", ("whole", 0, 99)),
)

# The one table. A default is a string, or a dict with one value per profile.
SETTINGS = (
    ("PROFILE", DEFAULT_PROFILE, ("choice", PROFILES)),
    ("GROOM_AHEAD", {"solo": "2", "team": "4", "fleet": "6"}, ("whole", 0, 99)),
    ("LANES", {"solo": "1", "team": "2", "fleet": "3"}, ("whole", 1, 99)),
    ("DELIVERY_LEAD", {"solo": "off", "team": "off", "fleet": "on"}, ("choice", ("on", "off"))),
    ("STATUS_EVERY", {"solo": "milestone", "team": "milestone", "fleet": "15m"}, ("minutes", 1, 999)),
    ("DECISION_BUDGET", "3", ("whole", 0, 99)),
    ("QA_FAIL_AT", "M", ("choice", ("L", "M", "C"))),
    ("QA_SCOPE_STRICT", "yes", ("choice", ("yes", "no"))),
    ("RECHECK", "changed", ("choice", ("changed", "full"))),
    ("FIX_CHECK_LOOPS", "2", ("whole", 1, 99)),
    ("ASK_AT", "4", ("whole", 1, 99)),
    ("SHIP_RULE", "none", ("ship_rule",)),
    ("STEP_UP", "ask", ("choice", ("auto", "ask", "off"))),
    ("FINDINGS_TO_ISSUE_AT", "C", ("choice", ("L", "M", "C"))),
    ("FINDINGS_GROUP_AT", "5", ("whole", 1, 99)),
    ("FINDINGS_KEEP_SWEEPS", "5", ("whole", 1, 99)),
    ("HEAVY_SECOND_QA", "on", ("choice", ("on", "off"))),
    # The subset's list is the kit's only list of QA gates that can be waived. Every other
    # gate (the approved and tier: labels, the body hash, the tier, protected files, push,
    # QA itself) is not in it, so no level can name it.
    ("WAIVABLE_GATES", "heavy-second-qa,qa-recheck", ("subset", ("heavy-second-qa", "qa-recheck"))),
)

# Settings only a project line in agent-kit.conf may set: refused as an issue override or
# a session ruling, so an issue can't change its own rules.
PROJECT_ONLY = frozenset(("PROFILE", "WAIVABLE_GATES"))

# Bounds no level can cross (customizing.md): (setting, refused value, reason), applied
# to the issue override and session ruling levels.
BOUNDS = (
    ("HEAVY_SECOND_QA", "off", "no issue may drop the Heavy second QA launch; only a project line can set it"),
)

# Existing agent-kit.conf names, read elsewhere (lib.sh, check-tier.sh, github_api.py,
# kit-check.py); passed over unread.
KNOWN_CONF = frozenset((
    "KIT_DIR", "KIT_VERSION", "GITHUB_REPO", "TEST_CMD", "LINT_CMD", "TYPECHECK_CMD",
    "TEST_FILES", "FORBIDDEN", "ALLOWED", "LIGHT_ALLOWED", "LIGHT_MAX_LINES", "PROTECTED",
))

NAMES = tuple(row[0] for row in SETTINGS)
TABLE = {row[0]: row for row in SETTINGS}

ASSIGNMENT = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)(\+?=)(.*)", re.S)
# A setting name followed by = or += anywhere in a line. Outside a setting's own line at
# column 1, bash (when lib.sh sources the conf) might apply it: indented, after export or
# declare, after another assignment (`KIT_DIR=x LANES=5`), after `;`, inside `if ... fi`.
# This reader does not parse bash, so any such line is refused, including some that bash
# would not apply (an array element or a line inside a multi-line quoted value).
ANYWHERE = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(re.escape(n) for n in NAMES) + r")\+?=")
BOM = chr(0xFEFF)  # the UTF-8 byte order mark, decoded
VALUE = re.compile(r"(?:\"([^\"]*)\"|'([^']*)'|([^\s\"']*))([ \t]*)(.*)", re.S)
WHOLE = re.compile(r"0|[1-9][0-9]*")

# The issue levels.
ISSUE_NUMBER = re.compile(r"[1-9][0-9]{0,8}")  # as the Makefile's issue-number-ok
DUMP_NAME = re.compile(r"issue-([1-9][0-9]{0,8})\.json")
OVERRIDES_LABEL = "overrides"
RULING_FIRST_LINE = "Orchestrator: Ruling"
HUMAN_RULED = re.compile(r"Human ruled: [0-9]{4}-[0-9]{2}-[0-9]{2}[ \t]*")
ITEM = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=(\S*)")
# A Ruling: text that starts with a name and = (spaces before the = included, then refused)
# is a setting ruling; any other text is a process ruling.
SETTING_TEXT = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)([ \t]*)=(.*)", re.S)
# A line with the label that is not at column 1: indented, or after a list marker.
NOT_AT_COLUMN_1 = re.compile(r"[ \t]*(?:(?:[-*+]|[0-9]+\.)[ \t]+)?(Overrides|Ruling|Waiver):")


class SettingsError(Exception):
    """A refusal: the message is the reason, naming the file and line where there is one."""


ECHO_LIMIT = 40


def clip(text: str) -> str:
    """Conf text as echoed in a reason: at most ECHO_LIMIT characters, then a length marker."""
    if len(text) <= ECHO_LIMIT:
        return text
    return f"{text[:ECHO_LIMIT]}... ({len(text)} characters)"


def echo(value: str) -> str:
    """A conf value quoted for a reason, shortened the same way as clip()."""
    if len(value) <= ECHO_LIMIT:
        return repr(value)
    return f"{value[:ECHO_LIMIT]!r}... ({len(value)} characters)"


def whole_in(value: str, lo: int, hi: int) -> bool:
    # Length first: a value with more digits than hi is out of range, and int() on very long
    # digit strings raises ValueError (Python 3.11+ limit), which would escape the refusal.
    if len(value) > len(str(hi)) or not WHOLE.fullmatch(value):
        return False
    return lo <= int(value) <= hi


def allowed(value: str, kind: tuple) -> bool:
    """True when value is one of the values `kind` allows."""
    tag = kind[0]
    if tag == "choice":
        return value in kind[1]
    if tag == "whole":
        return whole_in(value, kind[1], kind[2])
    if tag == "minutes":
        return value == "milestone" or (value.endswith("m") and whole_in(value[:-1], kind[1], kind[2]))
    if tag == "ship_rule":
        if value == "none":
            return True
        pairs = value.split(",")
        if not 1 <= len(pairs) <= len(SHIP_RULE_KEYS):
            return False
        keys = dict(SHIP_RULE_KEYS)
        seen = set()
        for pair in pairs:
            key, sep, part = pair.partition(":")
            if not sep or key not in keys or key in seen or not allowed(part, keys[key]):
                return False
            seen.add(key)
        return True
    if tag == "subset":
        if value == "none":
            return True
        parts = value.split(",")
        return all(part in kind[1] for part in parts) and len(set(parts)) == len(parts)
    raise ValueError(f"unknown kind {tag!r}")


def describe(kind: tuple) -> str:
    """The allowed values as customizing.md writes them (its tables are tested against this)."""
    tag = kind[0]
    if tag == "choice":
        return ", ".join(f"`{v}`" for v in kind[1])
    if tag == "whole":
        return f"whole number {kind[1]} to {kind[2]}"
    if tag == "minutes":
        return f"`milestone`, or `<n>m` with n a whole number {kind[1]} to {kind[2]}"
    if tag == "ship_rule":
        parts = []
        for key, sub in SHIP_RULE_KEYS:
            shown = "/".join(f"`{v}`" for v in sub[1]) if sub[0] == "choice" else describe(sub)
            parts.append(f"`{key}:` {shown}")
        return ("`none`, or one to three comma-separated `key:value` pairs, no spaces, "
                "each key at most once: " + ", ".join(parts))
    if tag == "subset":
        listed = ", ".join(f"`{v}`" for v in kind[1])
        return f"`none`, or one or more of {listed}, comma-separated, no spaces, each at most once"
    raise ValueError(f"unknown kind {tag!r}")


def default_for(name: str, profile: str) -> str:
    default = TABLE[name][1]
    return default[profile] if isinstance(default, dict) else default


def is_profile_setting(name: str) -> bool:
    return isinstance(TABLE[name][1], dict)


def parse_value(rest: str):
    """(value, trailing text) from what follows `NAME=`; an unclosed quote is trailing text."""
    match = VALUE.fullmatch(rest)
    value = next((g for g in match.group(1, 2, 3) if g is not None), "")
    return value, match.group(5)


def scan(conf: Path, label: str) -> dict:
    """name -> (value, line number) for each setting or PROFILE written in the conf."""
    try:
        data = conf.read_bytes()
    except FileNotFoundError:
        raise SettingsError(f"{label}: not found (run from the folder that holds {CONF})")
    except OSError as error:
        cause = error.strerror or type(error).__name__
        raise SettingsError(f"{label}: cannot be opened ({cause})")
    try:
        text = data.decode("utf-8")
    except ValueError:
        raise SettingsError(f"{label}: cannot be read as UTF-8 text")
    if text.startswith(BOM):
        # bash reads the mark as part of the first word, so a first-line assignment would
        # not apply there; refused rather than stripped, so the two readers never disagree.
        raise SettingsError(f"{conf.name} line 1: starts with a UTF-8 byte order mark; save the file without one")
    found = {}
    for number, line in enumerate(text.split("\n"), 1):
        where = f"{conf.name} line {number}"
        if line.lstrip(" \t").startswith("#"):
            continue  # comment line: passed over
        match = ASSIGNMENT.match(line)
        if match is None or match.group(1) not in TABLE:
            elsewhere = ANYWHERE.search(line)
            if elsewhere:
                raise SettingsError(f"{where}: {elsewhere.group(1)} must be on a line of its own, at column 1 "
                                    "as NAME=value (not indented, after export, or after other text)")
        if match is None:
            continue  # blank or indented line: passed over
        name, operator, rest = match.groups()
        if name in KNOWN_CONF:
            continue
        if name not in TABLE:
            raise SettingsError(f"{where}: unknown setting {clip(name)} (see customizing.md for the settings)")
        if operator != "=":
            raise SettingsError(f"{where}: {name} must be set with =, not {operator}")
        if name in found:
            raise SettingsError(f"{where}: {name} is written twice (first at line {found[name][1]})")
        value, trailing = parse_value(rest)
        if trailing:
            raise SettingsError(f"{where}: {name} has text after its value; only spaces may follow")
        if not allowed(value, TABLE[name][2]):
            if name == "PROFILE":
                raise SettingsError(f"{where}: unknown profile {echo(value)}; allowed: {', '.join(PROFILES)}")
            shown = echo(value) if value else "an empty value"
            raise SettingsError(f"{where}: {name} has {shown}; allowed: {describe(TABLE[name][2])}")
        found[name] = (value, number)
    return found


# --- The issue levels -------------------------------------------------------------------


def lines_of(text: str) -> list:
    """The lines of a body or comment; a line ending in CRLF is read as ending in LF."""
    return text.replace("\r\n", "\n").split("\n")


def check_issue_value(where: str, name: str, value: str, level: str) -> None:
    """Refuse a NAME=value written at an issue level (an override or a setting ruling)."""
    if name not in TABLE:
        raise SettingsError(f"{where}: unknown setting {clip(name)} (see customizing.md for the settings)")
    if name in PROJECT_ONLY:
        raise SettingsError(f"{where}: {name} can be set only by a project line in {CONF}, not {level}")
    if not allowed(value, TABLE[name][2]):
        shown = echo(value) if value else "an empty value"
        raise SettingsError(f"{where}: {name} has {shown}; allowed: {describe(TABLE[name][2])}")
    for bound_name, refused, reason in BOUNDS:
        if name == bound_name and value == refused:
            raise SettingsError(f"{where}: {name}={value} crosses a bound no level can cross: {reason}")


def refuse_not_at_column_1(where: str, line: str, labels: tuple) -> None:
    """Refuse a bullet or indented line that carries one of the labels, so it isn't ignored."""
    match = NOT_AT_COLUMN_1.match(line)
    if match and match.group(1) in labels and not line.startswith(match.group(1) + ":"):
        raise SettingsError(f"{where}: a {match.group(1)}: line must start at column 1, "
                            "with no indent or list marker")


def text_field(item: dict, key: str, where: str) -> str:
    value = item.get(key)
    if not isinstance(value, str):
        raise SettingsError(f"{where}: field {key} is missing or not text")
    return value


def issue_number_of(issue, where: str) -> int:
    if not isinstance(issue, dict):
        raise SettingsError(f"{where}: is not a JSON object")
    number = issue.get("number")
    if not isinstance(number, int) or isinstance(number, bool) or number < 1:
        raise SettingsError(f"{where}: field number is missing or not a whole number")
    return number


def read_overrides(issue: dict, number: int) -> dict:
    """name -> (value, body line) from the issue's `Overrides:` line, if the label allows it."""
    labelled = any(label.get("name") == OVERRIDES_LABEL for label in issue["labels"])
    found: dict = {}
    seen_line = None
    for index, line in enumerate(lines_of(issue["body"]), 1):
        where = f"issue #{number} body line {index}"
        refuse_not_at_column_1(where, line, ("Overrides",))
        if not line.startswith("Overrides:"):
            continue
        if not labelled:
            raise SettingsError(f"{where}: an Overrides: line applies only with the `{OVERRIDES_LABEL}` label, "
                                "which the issue does not have")
        if seen_line is not None:
            raise SettingsError(f"{where}: a second Overrides: line (the first is at body line {seen_line})")
        seen_line = index
        rest = line[len("Overrides:"):].rstrip(" \t")
        if not rest.strip(" \t"):
            raise SettingsError(f"{where}: the Overrides: line lists no setting")
        if not rest.startswith(" ") or rest.startswith("  "):
            raise SettingsError(f"{where}: write the line as `Overrides: NAME=value, NAME=value`")
        items = rest[1:]
        if items.endswith(","):
            raise SettingsError(f"{where}: the Overrides: list ends with a comma")
        for item in items.split(", "):
            match = ITEM.fullmatch(item)
            if match is None:
                raise SettingsError(f"{where}: {echo(item) if item else 'an empty item'} is not NAME=value "
                                    "(items are separated by a comma and one space)")
            name, value = match.groups()
            check_issue_value(where, name, value, "as an issue override")
            if name in found:
                raise SettingsError(f"{where}: {name} is listed twice")
            found[name] = (value, index)
    return found


def read_rulings(issue, owner, waivable) -> list:
    """The counted ruling comments of an issue, in order, each as a dict:
        {"createdAt": str, "index": int, "rulings": [(name, value, line)],
         "waivers": [(gate, reason, line)]}
    `issue` is parsed JSON in the dump's shape or the `github_api.py issue` shape (only
    `number` and `comments` are read here); `owner` is the repository owner's login;
    `waivable` is the gates the resolved WAIVABLE_GATES allows (empty for `none`).
    Raises SettingsError on a refused line. Starts no process and reads no file.
    """
    number = issue_number_of(issue, "issue")
    label = f"issue #{number}"
    comments = issue.get("comments")
    if not isinstance(comments, list):
        raise SettingsError(f"{label}: field comments is missing or not a list")
    if not isinstance(owner, str) or not owner:
        raise SettingsError(f"{label}: the repository owner is not known")
    waivable = tuple(waivable)
    known_gates = TABLE["WAIVABLE_GATES"][2][1]
    counted = []
    for index, item in enumerate(comments):
        where = f"{label} comment {index + 1}"
        if not isinstance(item, dict) or "author" not in item:
            raise SettingsError(f"{where}: is malformed (no author field)")
        body = text_field(item, "body", where)
        stamp = text_field(item, "createdAt", where)
        author = item["author"]
        if author is None:
            continue  # a deleted account: not the owner's, skipped as issue-close.sh does
        if not isinstance(author, dict) or not isinstance(author.get("login"), str):
            raise SettingsError(f"{where}: field author is malformed")
        if author["login"] != owner or not body.startswith(RULING_FIRST_LINE):
            continue
        counted.append((stamp, index, body))
    counted.sort(key=lambda c: (c[0], c[1]))
    result = []
    for stamp, index, body in counted:
        lines = lines_of(body)
        if not any(HUMAN_RULED.fullmatch(line) for line in lines):
            raise SettingsError(f"{label} ruling {stamp} line 1: a ruling comment needs a "
                                "`Human ruled: <YYYY-MM-DD>` line")
        rulings, waivers, names, gates = [], [], {}, {}
        for line_number, line in enumerate(lines, 1):
            where = f"{label} ruling {stamp} line {line_number}"
            refuse_not_at_column_1(where, line, ("Ruling", "Waiver"))
            if line.startswith("Ruling:"):
                text = line[len("Ruling:"):].strip(" \t")
                match = SETTING_TEXT.fullmatch(text)
                if match is None:
                    continue  # a process ruling: recorded in the comment, not applied
                name, spaces, value = match.groups()
                if spaces:
                    raise SettingsError(f"{where}: write the ruling as `Ruling: {clip(name)}=value`, "
                                        "with no space before the =")
                check_issue_value(where, name, value, "by a session ruling")
                if name in names:
                    raise SettingsError(f"{where}: {name} is ruled twice in this comment "
                                        f"(first at line {names[name]})")
                names[name] = line_number
                rulings.append((name, value, line_number))
            elif line.startswith("Waiver:"):
                gate, sep, reason = line[len("Waiver:"):].partition(" - ")
                if not gate.startswith(" ") or not sep:
                    raise SettingsError(f"{where}: write the line as `Waiver: <gate> - <reason>`")
                gate, reason = gate[1:], reason.strip(" \t")
                if gate not in waivable:
                    if gate in known_gates:
                        value = ",".join(waivable) or "none"
                        raise SettingsError(f"{where}: {gate} is not in WAIVABLE_GATES ({value}), "
                                            "so this project does not let it be waived")
                    raise SettingsError(f"{where}: {echo(gate)} is not a gate that can be waived "
                                        f"(only {', '.join(known_gates)}, as WAIVABLE_GATES allows)")
                if not reason:
                    raise SettingsError(f"{where}: the waiver of {gate} gives no reason")
                if gate in gates:
                    raise SettingsError(f"{where}: {gate} is waived twice in this comment "
                                        f"(first at line {gates[gate]})")
                gates[gate] = line_number
                waivers.append((gate, reason, line_number))
        result.append({"createdAt": stamp, "index": index, "rulings": rulings, "waivers": waivers})
    return result


def load_issue(issue_path) -> dict:
    """The issue dump at issue_path, checked; SettingsError naming the file otherwise."""
    path = Path(issue_path)
    label = str(issue_path)
    named = DUMP_NAME.fullmatch(path.name)
    if named is None:
        raise SettingsError(f"{label}: an issue dump must be named issue-<n>.json")
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        raise SettingsError(f"{label}: not found (make settings N=<n> writes it with the issue-dump recipe)")
    except OSError as error:
        cause = error.strerror or type(error).__name__
        raise SettingsError(f"{label}: cannot be opened ({cause})")
    try:
        issue = json.loads(data.decode("utf-8"))
    except ValueError:
        raise SettingsError(f"{label}: is not JSON")
    number = issue_number_of(issue, label)
    if number != int(named.group(1)):
        raise SettingsError(f"{label}: holds issue #{number}, not #{named.group(1)}")
    labels = issue.get("labels")
    if not isinstance(labels, list) or not all(isinstance(x, dict) and isinstance(x.get("name"), str)
                                               for x in labels):
        raise SettingsError(f"{label}: field labels is missing or malformed")
    text_field(issue, "body", label)
    if not isinstance(issue.get("comments"), list):
        raise SettingsError(f"{label}: field comments is missing or not a list")
    owner = issue.get("repositoryOwner")
    if not isinstance(owner, dict) or not isinstance(owner.get("login"), str) or not owner["login"]:
        raise SettingsError(f"{label}: field repositoryOwner is missing or malformed")
    return issue


def read_settings(conf_path, issue_path=None) -> dict:
    """name -> (value, source) for PROFILE and every setting, in table order.

    With issue_path (the dump .scratch/issue-<n>.json), the issue override and session
    rulings of issue <n> apply above the project lines. Raises SettingsError with the
    reason (naming the file and line) on any refusal.
    """
    conf = Path(conf_path)
    written = scan(conf, str(conf_path))
    result = {}
    if "PROFILE" in written:
        profile, number = written["PROFILE"]
        result["PROFILE"] = (profile, f"{conf.name} line {number}")
    else:
        profile = DEFAULT_PROFILE
        result["PROFILE"] = (profile, "kit default")
    for name in NAMES[1:]:
        if name in written:
            value, number = written[name]
            result[name] = (value, f"{conf.name} line {number}")
        elif is_profile_setting(name) and "PROFILE" in written:
            result[name] = (default_for(name, profile), f"profile {profile}")
        else:
            result[name] = (default_for(name, profile), "kit default")
    if issue_path is None:
        return result
    issue = load_issue(issue_path)
    number = issue["number"]
    for name, (value, line) in read_overrides(issue, number).items():
        result[name] = (value, f"issue #{number} body line {line}")
    gates = result["WAIVABLE_GATES"][0]
    waivable = () if gates == "none" else tuple(gates.split(","))
    for comment in read_rulings(issue, issue["repositoryOwner"]["login"], waivable):
        for name, value, line in comment["rulings"]:
            result[name] = (value, f"issue #{number} ruling {comment['createdAt']} line {line}")
    return result


USAGE = "Usage: make settings [N=<issue number>] (run from the project folder)"


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) > 1 or (args and not ISSUE_NUMBER.fullmatch(args[0])):
        print(USAGE, file=sys.stderr)
        return 2
    issue_path = Path(DUMP_FOLDER) / f"issue-{args[0]}.json" if args else None
    try:
        values = read_settings(CONF, issue_path)
    except SettingsError as error:
        print(f"settings: {error}", file=sys.stderr)
        return 1
    for name, (value, source) in values.items():
        print(f"{name}={value} ({source})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
