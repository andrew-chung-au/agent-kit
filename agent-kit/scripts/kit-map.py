#!/usr/bin/env python3
"""Read the kit's installed-file map, and compare one installed file with its kit source.

The map, `installed-files.txt` in the kit folder, names each kit file that is installed
outside the kit folder. Readers (kit-check, kit-compare, the import steps) load this
module and call parse_map(); none of them reads the map its own way, so they cannot
disagree. Standard library only.

    python3 -B agent-kit/scripts/kit-map.py <kit root> <repo root>

prints one line per entry (`kind | source | install | allowed`) and exits 0, or prints a
one-line `kit-map: ...` reason on stderr and exits 2. Both arguments are required: there
is no default kit root, and neither vuln-triage/ copy of the kit is authoritative.

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
character, a source path that is absolute, holds `..` or starts with `~`, and, for a
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
CONTROL = re.compile(r"[\x00-\x08\x0a-\x1f\x7f]")


class MapError(Exception):
    """The map or an argument is refused. The message is the one-line reason."""


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
    real_root = os.path.realpath(repo_root)
    current = Path(repo_root)
    for part in install.split("/"):
        current = current / part
        if os.path.islink(current):
            raise MapError(f"line {number}: install path goes through a symlink: {install!r}")
    real = os.path.realpath(current)
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
    if kit_root is None or repo_root is None:
        raise MapError("a kit root and a repo root are both required")
    kit_root, repo_root = Path(kit_root), Path(repo_root)
    if not kit_root.is_dir() or kit_root.is_symlink():
        raise MapError(f"the kit root is not a plain folder: {kit_root}")
    if not repo_root.is_dir():
        raise MapError(f"the repo root is not a folder: {repo_root}")
    path = kit_root / MAP_NAME
    if path.is_symlink() or not path.is_file():
        raise MapError(f"{MAP_NAME} is missing or not a regular file in {kit_root}")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise MapError(f"{MAP_NAME} cannot be read as UTF-8 text: {exc}") from None

    entries: list[Entry] = []
    seen: set[str] = set()
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if CONTROL.search(raw):
            raise MapError(f"line {number}: control character in an entry")
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


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("kit-map: usage: kit-map.py <kit root> <repo root>", file=sys.stderr)
        return 2
    try:
        entries = parse_map(argv[0], argv[1])
    except MapError as exc:
        print(f"kit-map: {exc}", file=sys.stderr)
        return 2
    for entry in entries:
        print(f"{entry.kind} | {entry.source} | {entry.install} | {entry.allowed}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
