#!/usr/bin/env python3
"""Read the kit's installed-file map, and compare one installed file with its kit source.

The map, `installed-files.txt` in the kit folder, names each kit file that is installed
outside the kit folder. Readers (kit-check, kit-compare, the import steps) load this
module and call parse_map() and scan_installed(); none of them reads the map its own way
or compares files its own way, so they cannot disagree. Standard library only.

    python3 -B agent-kit/scripts/kit-map.py <kit root> <repo root>
    python3 -B agent-kit/scripts/kit-map.py --installed <kit root> <repo root>

The first form prints one line per entry (`kind | source | install | allowed`) and exits
0. The second (`--installed`) compares each installed file with its kit source and prints
one line per entry: `unchanged`, `drift`, `missing` or, for a human-machine entry,
`not checked here (human compares from the clean clone) <path>`; it exits 1 on any drift
or missing, 0 otherwise. Either form prints a one-line `kit-map: ...` reason on stderr and
exits 2 on a refused map. Both roots are required: there is no default kit root, and
neither vuln-triage/ copy of the kit is authoritative.

Every filesystem call in kit-map.py, kit-check.py and kit-compare.py goes through fs(), which
turns an OSError (a folder that cannot be searched, a file that cannot be read) into a
MapError, so the run exits 2 with a one-line reason and never exits 1, the drift code.

scan_installed() is the one driver every reader shares: it calls parse_map() for the
entries and scan_text() per file, reads a `repo` entry's install path from the repo root,
reports a `human-machine` entry as `not checked` without ever opening its install path,
and writes nothing.

Map format (text only; the file is never sourced and nothing in it is run):
    # comment lines start with "#"; blank lines are skipped
    <path inside the kit> | <install path> | <kind> | <allowed-to-differ>
kind is `repo` (installed inside the repository) or `human-machine` (installed by the
human on their own machine, outside this folder). allowed-to-differ is one of
    none            any difference is drift
    markers         lines between `agent-kit: local-begin` and `agent-kit: local-end`
                    (in a comment) may differ; both copies must hold exactly one pair
    prefix:<text>   lines starting with <text> may differ (for files without comments)

Refused, always the whole read (MapError, never a skipped line): a wrong number of
fields, an unknown kind, an unknown allowed rule, a duplicate install path, a control
character or line break other than newline anywhere in the file (comments included; the
text is split on newline only), an empty root argument, a source path that is absolute, holds `..` or starts with `~`, and, for a
`repo` entry, an install path that is absolute, holds `..`, starts with `~`, resolves
outside the repo, or resolves through a symlink (the path or any parent).

A `human-machine` install path is returned as data only: the parser never opens, stats or
expands it.
"""
from __future__ import annotations

import difflib
import os
import re
import sys
from pathlib import Path
from typing import NamedTuple

MAP_NAME = "installed-files.txt"
KINDS = ("repo", "human-machine")
LOCAL_BEGIN = "agent-kit: local-begin"
LOCAL_END = "agent-kit: local-end"
# Anywhere in the map, comments included: every control character but tab and newline
# (so a bare CR, VT, FF and FS/GS/RS too), DEL, and the Unicode line breaks NEL, LS and PS.
# They are refused before the text is split, because str.splitlines() would treat them
# as line ends, and a line that reads as a comment could then parse as an entry.
CONTROL = re.compile("[\x00-\x08\x0b-\x1f\x7f\x85\u2028\u2029]")


class MapError(Exception):
    """The map or an argument is refused. The message is the one-line reason."""


def fs(call, *args, failed=None):
    """Run one filesystem call; a failure becomes a MapError, never a traceback.

    The failures caught are OSError, RuntimeError and ValueError: Path.resolve() raises
    RuntimeError("Symlink loop") on Python up to 3.12 and OSError after, and a path with an
    embedded NUL raises ValueError. Any other exception is a bug and is left to surface.

    Every filesystem call in kit-map.py, kit-check.py and kit-compare.py goes through this
    one helper (a stat such as is_file(), is_dir(), is_symlink(), exists() or resolve(), or
    a read). A permission error, a loop or any other OSError then exits 2 with a one-line
    reason; exit 1 is the code for drift, and a crash must never read as drift. `failed` is
    the caller's own message, used in place of the generic one. The call is a bound Path
    method or a function with its arguments, so the path in the reason is call.__self__ or
    the first argument; it is shown quoted.
    """
    try:
        return call(*args)
    except (OSError, RuntimeError, ValueError) as exc:
        subject = args[0] if args else getattr(call, "__self__", "")
        reason = " ".join((getattr(exc, "strerror", None) or str(exc) or type(exc).__name__).split())
        if failed:
            raise MapError(f"{failed} ({reason})") from None
        raise MapError(f"cannot read {str(subject)!r}: {reason}") from None


def read_utf8(path, failed: str) -> str:
    """The text of one file, read as raw bytes and decoded as UTF-8, through fs()."""
    data = fs(path.read_bytes, failed=failed)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise MapError(f"{failed} (not valid UTF-8)") from None


class Entry(NamedTuple):
    source: str   # path inside the kit folder
    install: str  # install path: repo-relative for `repo`, data only for `human-machine`
    kind: str     # "repo" or "human-machine"
    allowed: str  # "none", "markers" or "prefix:<text>"
    line: int     # line number in the map


class Finding(NamedTuple):
    status: str   # "local, ignored" or "drift"
    where: str    # "kit", "installed" or "both"
    line: int     # 1-based line number in that copy, 0 when it applies to the whole file
    note: str


def _plain_relative(path: str, what: str, number: int) -> None:
    parts = path.split("/")
    if (not path or path.startswith("/") or path.startswith("~") or "\\" in path
            or re.match(r"[A-Za-z]:", path)):
        raise MapError(f"line {number}: {what} must be a plain relative path: {path!r}")
    if ".." in parts:
        raise MapError(f"line {number}: {what} must not contain '..': {path!r}")
    if "" in parts or "." in parts:
        raise MapError(f"line {number}: {what} must not have empty or '.' parts: {path!r}")


def _check_repo_install(repo_root: Path, install: str, number: int) -> None:
    _plain_relative(install, "install path", number)
    real_root = fs(os.path.realpath, repo_root)
    current = Path(repo_root)
    for part in install.split("/"):
        current = current / part
        if fs(current.is_symlink):
            raise MapError(f"line {number}: install path goes through a symlink: {install!r}")
    real = fs(os.path.realpath, current)
    if os.path.commonpath([real_root, real]) != real_root:
        raise MapError(f"line {number}: install path resolves outside the repo: {install!r}")


def _check_allowed(allowed: str, number: int) -> None:
    if allowed in ("none", "markers"):
        return
    if allowed.startswith("prefix:") and allowed[len("prefix:"):]:
        return
    raise MapError(f"line {number}: unknown allowed-to-differ rule: {allowed!r}")


def parse_map(kit_root, repo_root) -> list[Entry]:
    """Read <kit_root>/installed-files.txt and return its entries, or raise MapError.

    kit_root and repo_root are required and explicit. The map is read as text and never
    run. `repo` install paths are checked against repo_root; `human-machine` install
    paths are returned untouched and never opened, stat'ed or expanded.
    """
    if kit_root is None or repo_root is None or str(kit_root) == "" or str(repo_root) == "":
        raise MapError("a kit root and a repo root are both required, and neither may be empty")
    kit_root, repo_root = Path(kit_root), Path(repo_root)
    if not fs(kit_root.is_dir) or fs(kit_root.is_symlink):
        raise MapError(f"the kit root is not a plain folder: {kit_root}")
    if not fs(repo_root.is_dir):
        raise MapError(f"the repo root is not a folder: {repo_root}")
    path = kit_root / MAP_NAME
    if fs(path.is_symlink) or not fs(path.is_file):
        raise MapError(f"{MAP_NAME} is missing or not a regular file in {kit_root}")
    # Raw bytes, decoded in read_utf8: read_text() would translate a bare CR into a newline
    # before the control check below could refuse it.
    text = read_utf8(path, f"{MAP_NAME} cannot be read as UTF-8 text")

    bad = CONTROL.search(text)
    if bad:
        number = text.count("\n", 0, bad.start()) + 1
        raise MapError(f"line {number}: control character or line break other than newline "
                       f"(U+{ord(bad.group()):04X})")

    entries: list[Entry] = []
    seen: set[str] = set()
    for number, raw in enumerate(text.split("\n"), start=1):
        line = raw.strip(" \t")
        if not line or line.startswith("#"):
            continue
        fields = [f.strip() for f in line.split("|")]
        if len(fields) != 4:
            raise MapError(f"line {number}: expected 4 fields, found {len(fields)}")
        source, install, kind, allowed = fields
        if kind not in KINDS:
            raise MapError(f"line {number}: unknown kind {kind!r} (use repo or human-machine)")
        if not install:
            raise MapError(f"line {number}: empty install path")
        _plain_relative(source, "source path", number)
        _check_allowed(allowed, number)
        if kind == "repo":
            _check_repo_install(repo_root, install, number)
        if install in seen:
            raise MapError(f"line {number}: duplicate install path {install!r}")
        seen.add(install)
        entries.append(Entry(source, install, kind, allowed, number))
    return entries


def _marker_ranges(lines: list[str], where: str):
    """Return (ignored line indexes, findings) for the marker pair in one copy."""
    findings: list[Finding] = []
    ignored: set[int] = set()
    begin = None
    pairs = 0
    for index, text in enumerate(lines):
        has_begin, has_end = LOCAL_BEGIN in text, LOCAL_END in text
        if has_begin and has_end:
            findings.append(Finding("drift", where, index + 1, "begin and end marker on one line"))
        elif has_begin:
            if begin is not None:
                findings.append(Finding("drift", where, index + 1, "local-begin inside an open block"))
            else:
                begin = index
        elif has_end:
            if begin is None:
                findings.append(Finding("drift", where, index + 1, "local-end without local-begin"))
            else:
                ignored.update(range(begin + 1, index))
                pairs += 1
                begin = None
    if begin is not None:
        findings.append(Finding("drift", where, begin + 1, "unclosed local-begin"))
    if pairs == 0 and not findings:
        findings.append(Finding("drift", where, 0, "missing local-begin/local-end marker pair"))
    elif pairs > 1:
        findings.append(Finding("drift", where, 0, "more than one marker pair"))
    return ignored, findings


def scan_text(allowed: str, kit_text: str, installed_text: str) -> list[Finding]:
    """Compare an installed file's text with its kit source's text.

    Pure: it reads no file. Returns findings only (line numbers, never line contents, so
    a personal value never reaches a report): `local, ignored` for lines inside the
    allowed-to-differ rule, `drift` for any other difference. No findings means the
    copies match. A file that needs a marker pair and lacks one is drift.
    """
    _check_allowed(allowed, 0)
    kit_lines, inst_lines = kit_text.splitlines(), installed_text.splitlines()
    findings: list[Finding] = []
    ignored = {"kit": set(), "installed": set()}
    if allowed == "markers":
        for where, lines in (("kit", kit_lines), ("installed", inst_lines)):
            marks, found = _marker_ranges(lines, where)
            ignored[where] = marks
            findings += found
    elif allowed.startswith("prefix:"):
        prefix = allowed[len("prefix:"):]
        for where, lines in (("kit", kit_lines), ("installed", inst_lines)):
            ignored[where] = {i for i, t in enumerate(lines) if t.startswith(prefix)}
    for where in ("kit", "installed"):
        for index in sorted(ignored[where]):
            findings.append(Finding("local, ignored", where, index + 1, "allowed to differ"))
    kit_kept = [(i, t) for i, t in enumerate(kit_lines) if i not in ignored["kit"]]
    inst_kept = [(i, t) for i, t in enumerate(inst_lines) if i not in ignored["installed"]]
    matcher = difflib.SequenceMatcher(None, [t for _, t in kit_kept], [t for _, t in inst_kept],
                                      autojunk=False)
    for tag, a1, a2, b1, b2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        for k in range(a1, a2):
            findings.append(Finding("drift", "kit", kit_kept[k][0] + 1, "line differs"))
        for k in range(b1, b2):
            findings.append(Finding("drift", "installed", inst_kept[k][0] + 1, "line differs"))
    return findings


class Report(NamedTuple):
    install: str   # the install path from the map (data for a human-machine entry)
    kind: str      # "repo" or "human-machine"
    state: str     # repo: "unchanged", "drift" or "missing"; human-machine: "not checked"
    findings: list  # the Findings behind a "drift" state; [] otherwise


# One line per entry, exactly as kit-check, the import step and the reverse import print it.
# `drift` and `missing` are the states that fail a run; `unchanged` and the human-machine
# `not checked here` line never do. A human-machine entry is named but never opened.
HUMAN_MACHINE_LINE = "not checked here (human compares from the clean clone)"


def _read_kit_source(kit_root: Path, source: str) -> str:
    """The kit copy of one installed file, read as text through the same symlink rule."""
    current = kit_root
    for part in source.split("/"):
        current = current / part
        if fs(current.is_symlink):
            raise MapError(f"the kit source goes through a symlink: {source!r}")
    if not fs(current.is_file, failed=f"the kit source cannot be read as UTF-8 text: {source!r}"):
        raise MapError(f"the kit source is missing: {source!r}")
    return read_utf8(current, f"the kit source cannot be read as UTF-8 text: {source!r}")


def scan_installed(kit_root, repo_root) -> list[Report]:
    """Compare each installed file in the map with its kit source, read-only.

    One driver for every reader (kit-check, the import step, the reverse import): it calls
    parse_map() for the entries and scan_text() per file, so there is no second parser and
    no second comparison. A `repo` entry's install path is read from repo_root; a
    `human-machine` entry is reported as `not checked` and its install path is never opened
    or stat'ed. A map the parser rejects raises MapError and nothing is read. Nothing is
    written. Returns one Report per entry, in map order.
    """
    entries = parse_map(kit_root, repo_root)
    kit_root, repo_root = Path(kit_root), Path(repo_root)
    reports: list[Report] = []
    for entry in entries:
        if entry.kind == "human-machine":
            reports.append(Report(entry.install, entry.kind, "not checked", []))
            continue
        kit_text = _read_kit_source(kit_root, entry.source)
        install = repo_root
        for part in entry.install.split("/"):
            install = install / part
            if fs(install.is_symlink):
                raise MapError(f"the install path goes through a symlink: {entry.install!r}")
        failed = f"the installed file cannot be read as UTF-8 text: {entry.install!r}"
        if not fs(install.is_file, failed=failed):
            reports.append(Report(entry.install, entry.kind, "missing", []))
            continue
        installed_text = read_utf8(install, failed)
        findings = scan_text(entry.allowed, kit_text, installed_text)
        drift = [f for f in findings if f.status == "drift"]
        reports.append(Report(entry.install, entry.kind, "drift" if drift else "unchanged", findings))
    return reports


def report_lines(reports: list[Report]) -> list[str]:
    """One text line per Report, for a verdict or a human-read list. Never a file's content."""
    lines = []
    for report in reports:
        if report.kind == "human-machine":
            lines.append(f"{HUMAN_MACHINE_LINE} {report.install}")
        elif report.state == "unchanged" and any(f.status == "local, ignored" for f in report.findings):
            lines.append(f"local, ignored {report.install}")
        else:
            lines.append(f"{report.state} {report.install}")
    return lines


def main(argv: list[str]) -> int:
    installed = argv and argv[0] == "--installed"
    rest = argv[1:] if installed else argv
    if len(rest) != 2:
        print("kit-map: usage: kit-map.py [--installed] <kit root> <repo root>", file=sys.stderr)
        return 2
    try:
        if installed:
            reports = scan_installed(rest[0], rest[1])
        else:
            entries = parse_map(rest[0], rest[1])
    except MapError as exc:
        print(f"kit-map: {exc}", file=sys.stderr)
        return 2
    if installed:
        failed = False
        for line in report_lines(reports):
            print(line)
            failed = failed or line.startswith(("drift ", "missing "))
        return 1 if failed else 0
    for entry in entries:
        print(f"{entry.kind} | {entry.source} | {entry.install} | {entry.allowed}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
