#!/usr/bin/env python3
"""List how the live kit folder differs from another kit copy, file by file.

Run from the project folder (the one holding agent-kit.conf), normally as
`make kit-compare OTHER=.scratch/<folder>`:
    python3 -B _docs/agent-kit/scripts/kit-compare.py <other kit folder>

The other folder is a freshly unpacked release or a project's kit, in a plain relative
path under .scratch/ (letters, digits, "." "_" "/" "-" only; no leading "/", no "..").
The live kit folder is found as kit-check.py finds it: KIT_DIR in agent-kit.conf, read as
TEXT, never sourced (the lookup is kit-check.py's own read_conf, not a copy).

Output: one line per kit file in the union of both trees, in path order, exactly one of
    unchanged <path> | modified <path> | added <path> | missing <path>
measuring the live kit against the other copy as the baseline (modified: content or
executable bit differs; added: only in the live kit; missing: only in the other copy),
then one summary line: `kit-compare: identical` or `kit-compare: <n> differ`. The scan is
the one kit-manifest.py shares with kit-check.py, so MANIFEST.sha256 (a record, not a kit
file), __pycache__ and *.pyc are left out. The helper lists differences only; it decides
nothing. Classification and the per-file decisions stay with procedures/kit-import.md.

Exit codes: 0 identical; 1 something differs; 2 error, nothing compared (a one-line
`kit-compare: ...` reason on stderr): not exactly one argument, an other folder that is
not a plain path under .scratch/, missing, not a folder, a symlink, or the live kit
folder itself, a symlink or other non-regular entry or a control-character name in
either tree, a name that is not valid UTF-8, or an unreadable file.

Read-only: it opens files only to read and hash them, creates nothing and writes nothing.
The other folder is untrusted data: the script hashes files and prints paths. It never
prints file contents, never imports or runs anything from the other folder and never
follows a path found inside it. A name that reads like an instruction is still only a
name. Standard library only.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

_here = Path(__file__).parent


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, _here / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kit_manifest = _load("kit_manifest", "kit-manifest.py")
kit_check = _load("kit_check", "kit-check.py")

SCRATCH = ".scratch"
PLAIN_PATH = re.compile(r"[A-Za-z0-9._/-]+")


class CompareError(Exception):
    """Exit 2: nothing compared. The message is the one-line reason."""


def other_folder(root: Path, arg: str) -> Path:
    """The other kit folder, validated: a plain relative path under .scratch/, a real folder."""
    if not arg or not PLAIN_PATH.fullmatch(arg):
        raise CompareError("the other folder must be a plain path: letters, digits, . _ / - only")
    parts = arg.split("/")
    if arg.startswith("/") or ".." in parts or "" in parts or "." in parts:
        raise CompareError(f"the other folder must be a plain relative path without .. or empty parts: {arg}")
    if parts[0] != SCRATCH or len(parts) < 2:
        raise CompareError(f"the other folder must be a folder under {SCRATCH}/: {arg}")
    path = root
    for part in parts:
        path = path / part
        if path.is_symlink():
            raise CompareError(f"the other folder path holds a symlink: {arg}")
    if not path.is_dir():
        raise CompareError(f"the other folder is missing or not a folder: {arg}")
    return path


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Usage: kit-compare.py <other kit folder under .scratch/>", file=sys.stderr)
        return 2
    try:
        root = Path.cwd()
        try:
            live_dir, _claim = kit_check.read_conf(root)
        except kit_check.CheckError as error:
            raise CompareError(str(error))
        other_dir = other_folder(root, args[0])
        if other_dir.resolve() == live_dir.resolve():
            raise CompareError("the other folder is the live kit folder itself")
        try:
            live = kit_manifest.kit_files(live_dir)
            other = kit_manifest.kit_files(other_dir)
        except (kit_manifest.KitError, OSError) as error:
            raise CompareError(str(error))
        names = sorted(set(live) | set(other))
        for name in names:
            try:
                name.encode("utf-8")
            except UnicodeEncodeError:
                raise CompareError("a kit file name is not valid UTF-8")
    except CompareError as error:
        print(f"kit-compare: {error}", file=sys.stderr)
        return 2
    lines = []
    differ = 0
    for name in names:
        if name not in other:
            state = "added"
        elif name not in live:
            state = "missing"
        else:
            state = "unchanged" if live[name] == other[name] else "modified"
        differ += state != "unchanged"
        lines.append(f"{state} {name}")
    lines.append("kit-compare: identical" if not differ else f"kit-compare: {differ} differ")
    print("\n".join(lines))
    return 1 if differ else 0


if __name__ == "__main__":
    sys.exit(main())
