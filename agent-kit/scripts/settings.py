#!/usr/bin/env python3
"""The kit's settings: one table, and the reader that resolves them from agent-kit.conf.

Run from the project folder (the one holding agent-kit.conf), normally as `make settings`,
with no arguments.

What each setting does, and which issue makes it take effect, is in the kit's
customizing.md. This file holds the only definition of the settings: SETTINGS below,
with each name, its default (one per profile for the profile settings) and its allowed
values. Nothing else defines them.

Resolution, lowest to highest: kit default, then the profile (PROFILE=solo|team|fleet,
unset meaning solo), then a project line in agent-kit.conf. A written line always beats
the profile. Nothing else changes a value: environment variables and make variables with
a setting's name are ignored.

agent-kit.conf is read as TEXT, never sourced or run, and this reader starts no shell or
other process (as github_api.py reads GITHUB_REPO). A setting line starts at column 1 as
NAME=value, NAME="value" or NAME='value', with nothing after it but spaces or tabs.
Comment lines, blank lines, indented lines and the existing conf names (KNOWN_CONF) are
passed over unread. Refused, with the line number: an unknown name at the start of a
line, an unknown profile, a value outside the allowed values (empty or wrong case
included), the same setting or PROFILE written twice, anything after the value, and an
indented or `export` assignment to a setting or PROFILE. A missing conf is refused too.

Output: PROFILE first, then one line per setting in table order,
    <NAME>=<value> (<source>)
where the source is `kit default`, `profile <name>` or `agent-kit.conf line <n>`.
A refusal prints nothing on standard output and one line on standard error,
    settings: agent-kit.conf line <n>: <reason>
and exits 1.

Interface for other kit scripts: import this module and call read_settings(conf_path).
It returns a dict, in table order, of name -> (value, source), or raises SettingsError
with the line-numbered reason. Values are returned as the text written.
Standard library only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CONF = "agent-kit.conf"
PROFILES = ("solo", "team", "fleet")
DEFAULT_PROFILE = "solo"

# Allowed-value kinds:
#   ("choice", (v1, v2, ...))   exactly one of the listed tokens (case matters)
#   ("whole", lo, hi)           a whole number lo..hi: "0" or digits with no leading zero, no sign
#   ("minutes", lo, hi)         "milestone", or "<n>m" with n a whole number lo..hi
#   ("ship_rule",)              "none", or one to three comma-separated key:value pairs,
#                               no spaces, each key at most once (SHIP_RULE_KEYS)
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
# An assignment bash would also apply but that does not start at column 1: indented, or
# after export (or declare, typeset, readonly, local, with or without options).
LOOSE_ASSIGNMENT = re.compile(r"[ \t]*(?:(?:export|declare|typeset|readonly|local)"
                              r"(?:[ \t]+-[A-Za-z]+)*[ \t]+)?([A-Za-z_][A-Za-z0-9_]*)\+?=")
VALUE = re.compile(r"(?:\"([^\"]*)\"|'([^']*)'|([^\s\"']*))([ \t]*)(.*)", re.S)
WHOLE = re.compile(r"0|[1-9][0-9]*")


class SettingsError(Exception):
    """A refusal: the message is the reason, naming the file and line where there is one."""


def whole_in(value: str, lo: int, hi: int) -> bool:
    return bool(WHOLE.fullmatch(value)) and lo <= int(value) <= hi


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
        text = conf.read_bytes().decode("utf-8")
    except FileNotFoundError:
        raise SettingsError(f"{label}: not found (run from the folder that holds {CONF})")
    except (OSError, ValueError):
        raise SettingsError(f"{label}: cannot be read as UTF-8 text")
    found = {}
    for number, line in enumerate(text.split("\n"), 1):
        where = f"{conf.name} line {number}"
        match = ASSIGNMENT.match(line)
        if match is None:
            loose = LOOSE_ASSIGNMENT.match(line)
            if loose and loose.group(1) in TABLE:
                raise SettingsError(f"{where}: {loose.group(1)} must start at column 1 as NAME=value, "
                                    "not indented or after export")
            continue  # comment, blank or indented line: passed over
        name, operator, rest = match.groups()
        if name in KNOWN_CONF:
            continue
        if name not in TABLE:
            raise SettingsError(f"{where}: unknown setting {name} (see customizing.md for the settings)")
        if operator != "=":
            raise SettingsError(f"{where}: {name} must be set with =, not {operator}")
        if name in found:
            raise SettingsError(f"{where}: {name} is written twice (first at line {found[name][1]})")
        value, trailing = parse_value(rest)
        if trailing:
            raise SettingsError(f"{where}: {name} has text after its value; only spaces may follow")
        if not allowed(value, TABLE[name][2]):
            if name == "PROFILE":
                raise SettingsError(f"{where}: unknown profile {value!r}; allowed: {', '.join(PROFILES)}")
            shown = repr(value) if value else "an empty value"
            raise SettingsError(f"{where}: {name} has {shown}; allowed: {describe(TABLE[name][2])}")
        found[name] = (value, number)
    return found


def read_settings(conf_path) -> dict:
    """name -> (value, source) for PROFILE and every setting, in table order.

    Raises SettingsError with the reason (naming the file and line) on any refusal.
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
    return result


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args:
        print("Usage: make settings (no arguments; run from the project folder)", file=sys.stderr)
        return 2
    try:
        values = read_settings(CONF)
    except SettingsError as error:
        print(f"settings: {error}", file=sys.stderr)
        return 1
    for name, (value, source) in values.items():
        print(f"{name}={value} ({source})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
