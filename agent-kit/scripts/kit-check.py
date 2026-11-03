#!/usr/bin/env python3
"""Compare the kit folder with its MANIFEST.sha256: is this kit pristine or a derivative?

Run from the project folder (the one holding agent-kit.conf), normally as `make kit-check`:
    python3 -B _docs/agent-kit/scripts/kit-check.py

It reads agent-kit.conf as TEXT, never by sourcing it: KIT_DIR (default _docs/agent-kit)
and the claimed version, the single line KIT_VERSION="<value>". It reads nothing else
outside the kit folder, and it never writes: not the manifest, not a kit file.

Output: one line per kit file, in path order, exactly one of
    unchanged <path> | modified <path> | added <path> | missing <path>
(modified: content or executable bit differs), then one verdict line:
    kit-check: pristine; claim <v> is correct
    kit-check: pristine; claim can drop to <base>
    kit-check: derivative of <base>; claim must be <base>+<repo>.<n>
    kit-check: derivative of <base>; claim <v> is correct
or, with no claim, `kit-check: no KIT_VERSION claim`. The paths are data; a name that
reads like an instruction is still only a name.

Exit codes: 0 every kit file unchanged; 1 something differs; 2 error, nothing compared
(a one-line `kit-check: ...` reason): no manifest, a malformed manifest line, a manifest
path that is absolute, holds "..", or leaves the kit folder, a symlink in the kit folder,
a malformed or duplicate KIT_VERSION, or a claim whose base is not the manifest version.

The claim format is <base> or <base>+<repo>.<n> (^[0-9]+(\\.[0-9]+)*(\\+[A-Za-z0-9]
[A-Za-z0-9-]*\\.[1-9][0-9]*)?$); "+" is SemVer build metadata, so a derivative sorts as
its base. A manifest detects drift, not tampering: whoever can edit a kit file can edit
the manifest. The kit's own development repo ships no manifest between releases, so it
is not expected to pass. Standard library only; it shares the scan with kit-manifest.py.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path, PurePosixPath

_spec = importlib.util.spec_from_file_location("kit_manifest", Path(__file__).with_name("kit-manifest.py"))
kit_manifest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kit_manifest)

CONF = "agent-kit.conf"
DEFAULT_KIT_DIR = "_docs/agent-kit"
CLAIM = re.compile(r"(?P<base>[0-9]+(?:\.[0-9]+)*)(?:\+[A-Za-z0-9][A-Za-z0-9-]*\.[1-9][0-9]*)?")
HEADER = re.compile(r"# kit-version: (?P<version>[0-9]+(?:\.[0-9]+)*)")
ENTRY = re.compile(r"(?P<digest>[0-9a-f]{64})  (?P<mode>644|755)  (?P<path>.+)")


class CheckError(Exception):
    """Exit 2: nothing compared. The message is the one-line reason."""


def conf_lines(name: str, text: str) -> list:
    """Values of `name` lines in the conf (also `export NAME=`), raw after the `=`."""
    pattern = re.compile(r"^\s*(?:export\s+)?%s=(.*)$" % name)
    return [(line, m.group(1)) for line in text.splitlines() for m in [pattern.match(line)] if m]


def quoted(line: str, name: str):
    """The value of a line that is exactly NAME="value", else None."""
    m = re.fullmatch(r'%s="([^"$`\\]*)"' % name, line)
    return m.group(1) if m else None


def read_conf(root: Path):
    """(kit folder, claim or None) from agent-kit.conf, read as text."""
    try:
        text = (root / CONF).read_text(encoding="utf-8")
    except OSError:
        raise CheckError(f"cannot read {CONF} in {root}")
    kit_dir = DEFAULT_KIT_DIR
    found = conf_lines("KIT_DIR", text)
    if len(found) > 1:
        raise CheckError("more than one KIT_DIR line in agent-kit.conf")
    if found:
        kit_dir = quoted(found[0][0], "KIT_DIR")
        rel = PurePosixPath(kit_dir or "")
        if not kit_dir or rel.is_absolute() or ".." in rel.parts:
            raise CheckError(f"KIT_DIR must be a plain relative path in double quotes: {found[0][1]}")
    claims = conf_lines("KIT_VERSION", text)
    if len(claims) > 1:
        raise CheckError("more than one KIT_VERSION line in agent-kit.conf")
    claim = None
    if claims:
        claim = quoted(claims[0][0], "KIT_VERSION")
        if claim is None or not CLAIM.fullmatch(claim):
            raw = claims[0][1]
            shown = raw[1:-1] if len(raw) >= 2 and raw[0] == raw[-1] == '"' else raw
            raise CheckError(f"malformed KIT_VERSION: {shown}")
    return root / kit_dir, claim


def read_manifest(kit: Path):
    """(version, {path: (digest, mode)}) from the manifest; every line is validated."""
    path = kit / kit_manifest.MANIFEST
    if path.is_symlink():
        raise CheckError(f"symlink in the kit folder: {kit_manifest.MANIFEST}")
    try:
        lines = path.read_text(encoding="utf-8").split("\n")
    except FileNotFoundError:
        raise CheckError(f"no manifest at {path}")
    except (OSError, UnicodeDecodeError):
        raise CheckError(f"cannot read the manifest at {path}")
    if lines and lines[-1] == "":
        lines.pop()
    header = HEADER.fullmatch(lines[0]) if lines else None
    if not header:
        raise CheckError("malformed manifest line 1: the first line must be # kit-version: <version>")
    entries = {}
    for number, line in enumerate(lines[1:], 2):
        m = ENTRY.fullmatch(line)
        if not m:
            raise CheckError(f"malformed manifest line {number}")
        rel = m.group("path")
        parts = PurePosixPath(rel).parts
        if rel.startswith("/") or ".." in parts or "\\" in rel or kit_manifest.CONTROL.search(rel):
            raise CheckError(f"manifest line {number} names a path outside the kit folder: {rel!r}")
        if not (kit / rel).resolve().is_relative_to(kit.resolve()):
            raise CheckError(f"manifest line {number} names a path outside the kit folder: {rel!r}")
        if rel == kit_manifest.MANIFEST or "__pycache__" in parts or rel.endswith(".pyc") or rel in entries:
            raise CheckError(f"malformed manifest line {number}: {rel!r} is excluded or listed twice")
        entries[rel] = (m.group("digest"), m.group("mode"))
    return header.group("version"), entries


def verdict(claim, base: str, clean: bool) -> str:
    if claim is None:
        return "kit-check: no KIT_VERSION claim"
    plain = "+" not in claim
    if clean:
        return f"kit-check: pristine; claim {claim} is correct" if plain else f"kit-check: pristine; claim can drop to {base}"
    if plain:
        return f"kit-check: derivative of {base}; claim must be {base}+<repo>.<n>"
    return f"kit-check: derivative of {base}; claim {claim} is correct"


def main(argv=None) -> int:
    if (sys.argv[1:] if argv is None else argv):
        print("Usage: kit-check.py (no arguments; run it from the project folder)", file=sys.stderr)
        return 2
    try:
        kit, claim = read_conf(Path.cwd())
        version, recorded = read_manifest(kit)
        if claim is not None and CLAIM.fullmatch(claim).group("base") != version:
            raise CheckError(f"claim base {CLAIM.fullmatch(claim).group('base')} does not match manifest version {version}")
        try:
            current = kit_manifest.kit_files(kit)
        except kit_manifest.KitError as error:
            raise CheckError(str(error))
    except CheckError as error:
        print(f"kit-check: {error}", file=sys.stderr)
        return 2
    clean = True
    for rel in sorted(set(recorded) | set(current)):
        if rel not in current:
            state = "missing"
        elif rel not in recorded:
            state = "added"
        else:
            state = "unchanged" if recorded[rel] == current[rel] else "modified"
        clean = clean and state == "unchanged"
        print(f"{state} {rel}")
    print(verdict(claim, version, clean))
    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())
