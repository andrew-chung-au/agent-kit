#!/usr/bin/env python3
"""List how one kit folder differs from another, file by file, with two explicit roots.

Run from the project folder, normally as `make kit-compare KIT_A=<folder> KIT_B=<folder>`:
    python3 -B agent-kit/scripts/kit-compare.py <kit root A> <kit root B>

Both roots are required and there is no default: neither is read from agent-kit.conf, and
neither vuln-triage/ copy of the kit is authoritative. Each is a plain relative path from
the project folder (letters, digits, "." "_" "/" "-" only; no leading "/" or "-", no "..",
no empty or "." part, no symlink anywhere on the path) naming a kit folder: the live kit,
a freshly unpacked release under .scratch/, or a project's kit.

Output: one line per kit file in the union of both trees, in path order, exactly one of
    unchanged <path> | modified <path> | added <path> | missing <path>
measuring A against B as the baseline (modified: content or executable bit differs; added:
only in A; missing: only in B), then one summary line: `kit-compare: identical` or
`kit-compare: <n> differ`. The scan is the one kit-manifest.py shares with kit-check.py,
so MANIFEST.sha256 (a record, not a kit file), __pycache__ and *.pyc are left out. The
helper lists differences only; it decides nothing. Classification and the per-file
decisions stay with procedures/kit-import.md.

Before it reads any kit file, each root that carries installed-files.txt has that map
read by the shared parser, kit_map.parse_map (the one kit-check.py uses; there is no
second parser). A map entry the parser rejects makes the whole run exit 2, naming the
root and the entry, with nothing compared and no kit file read. A root with no map is
compared as before. Only the map text is read: no install path is opened here.

Exit codes: 0 identical; 1 something differs; 2 error, nothing compared (a one-line
`kit-compare: ...` reason on stderr): not exactly two arguments, a root that is not a
plain path, missing, not a folder or a symlink, the two roots being the same folder, a
map entry the parser rejects, a filesystem error (every file call goes through kit_map.fs()), a symlink or other non-regular entry or a control-character
name in either tree, a name that is not valid UTF-8, or an unreadable file.

Read-only: it opens files only to read and hash them, creates nothing and writes nothing
under either root. Both folders are untrusted data: the script hashes files and prints
paths. It never prints file contents, never imports or runs anything from either folder and
never follows a path found inside one. A name that reads like an instruction is still only
a name. The scripts it loads (kit-manifest.py, kit-map.py) are the live ones next to it, and
they run live from the working tree. Standard library only.
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
kit_map = _load("kit_map", "kit-map.py")

PLAIN_PATH = re.compile(r"[A-Za-z0-9._/-]+")


class CompareError(Exception):
    """Exit 2: nothing compared. The message is the one-line reason."""


def _fs(call, *args, failed=None):
    """kit_map.fs() with its MapError turned into a CompareError (exit 2, one-line reason)."""
    try:
        return kit_map.fs(call, *args, failed=failed)
    except kit_map.MapError as error:
        raise CompareError(str(error)) from None


def kit_root(root: Path, arg: str, label: str) -> Path:
    """A kit folder, validated: a plain relative path from the project folder, a real folder."""
    if not arg or not PLAIN_PATH.fullmatch(arg):
        raise CompareError(f"kit {label} must be a plain path: letters, digits, . _ / - only")
    parts = arg.split("/")
    if arg.startswith(("/", "-")) or ".." in parts or "" in parts or "." in parts:
        raise CompareError(f"kit {label} must be a plain relative path without .. or empty parts: {arg}")
    path = root
    for part in parts:
        path = path / part
        if _fs(path.is_symlink):
            raise CompareError(f"kit {label} path holds a symlink: {arg}")
    if not _fs(path.is_dir):
        raise CompareError(f"kit {label} is missing or not a folder: {arg}")
    return path


def read_maps(root: Path, roots) -> None:
    """Run the shared parser on each root's map before anything else is read."""
    for label, folder in roots:
        map_path = folder / kit_map.MAP_NAME
        if not _fs(map_path.exists) and not _fs(map_path.is_symlink):
            continue
        try:
            kit_map.parse_map(folder, root)
        except kit_map.MapError as error:
            raise CompareError(f"kit {label} {kit_map.MAP_NAME}: {error}")


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("Usage: kit-compare.py <kit root A> <kit root B>", file=sys.stderr)
        return 2
    try:
        root = _fs(Path.cwd, failed="cannot read the working folder")
        dir_a = kit_root(root, args[0], "A")
        dir_b = kit_root(root, args[1], "B")
        if _fs(dir_a.resolve) == _fs(dir_b.resolve):
            raise CompareError("kit A and kit B are the same folder")
        read_maps(root, (("A", dir_a), ("B", dir_b)))
        try:
            tree_a = kit_manifest.kit_files(dir_a)
            tree_b = kit_manifest.kit_files(dir_b)
        except (kit_manifest.KitError, OSError) as error:
            raise CompareError(str(error))
        names = sorted(set(tree_a) | set(tree_b))
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
        if name not in tree_b:
            state = "added"
        elif name not in tree_a:
            state = "missing"
        else:
            state = "unchanged" if tree_a[name] == tree_b[name] else "modified"
        differ += state != "unchanged"
        lines.append(f"{state} {name}")
    lines.append("kit-compare: identical" if not differ else f"kit-compare: {differ} differ")
    print("\n".join(lines))
    return 1 if differ else 0


if __name__ == "__main__":
    sys.exit(main())
