#!/usr/bin/env python3
"""Write the kit's hash manifest, MANIFEST.sha256, into a kit folder.

A release step (see the release procedure, #9), not a make target:
    python3 -B agent-kit/scripts/kit-manifest.py <kit folder> <version>

The manifest records what a pristine kit of that version contains, so a project can
later tell with `make kit-check` whether its copy is pristine or a derivative.

Format (byte-identical for the same tree):
    # kit-version: <version>
    <sha256>  <mode>  <path>
one line per kit file, sorted by path; two spaces between fields; mode 755 if the owner
executable bit is set, else 644; path relative to the kit folder, with "/".

A kit file is a regular file anywhere under the kit folder, except MANIFEST.sha256 at
its top, any __pycache__ folder and any *.pyc file. Other modes and timestamps are not
recorded. A symlink (or any other non-regular entry) anywhere in the folder is an error,
never followed or hashed, and so is a name holding a control or invisible character (ASCII
control and DEL, C1 controls, any Unicode format character such as a bidi override or a
zero-width space, and the line and paragraph separators U+2028 and U+2029); then no file
is written. Ordinary non-ASCII names (accented letters, CJK) are accepted. The version must be a plain version (^[0-9]+(\\.[0-9]+)*$).

A manifest detects drift, not tampering: anyone who can change a kit file can change
the manifest too. Exit 0 written, 2 refused (with a one-line reason). Standard library only.
"""
from __future__ import annotations

import hashlib
import os
import re
import stat
import sys
import unicodedata
from pathlib import Path

MANIFEST = "MANIFEST.sha256"
PLAIN_VERSION = re.compile(r"[0-9]+(\.[0-9]+)*")
REFUSED_CATEGORIES = ("Cf", "Zl", "Zp")  # format (bidi, zero-width, BOM), line and paragraph separators


class _RefusedName:
    """Finds the first character a kit file name may not hold; `.search` works like a regex's.

    Refused: ASCII control and DEL, C1 controls U+0080 to U+009F, and every character whose
    Unicode category is Cf, Zl or Zp. The one place this set is defined: kit_files, kit-check
    and kit-compare all use it, so a name cannot change how a list or message is read.
    """

    @staticmethod
    def refuses(char: str) -> bool:
        return ord(char) < 0x20 or 0x7F <= ord(char) <= 0x9F or unicodedata.category(char) in REFUSED_CATEGORIES

    def search(self, text: str):
        return next((char for char in text if self.refuses(char)), None)


CONTROL = _RefusedName()


class KitError(Exception):
    """A tree or input the scripts refuse; the message is the one-line reason."""


def file_record(path: Path):
    """(sha256 hex, mode) of one regular file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    mode = "755" if os.lstat(path).st_mode & stat.S_IXUSR else "644"
    return digest.hexdigest(), mode


def kit_files(kit: Path) -> dict:
    """{relative path: (sha256, mode)} for every kit file. Raises KitError on a symlink."""
    if kit.is_symlink() or not kit.is_dir():
        raise KitError(f"kit folder {kit} is missing, not a folder or a symlink")
    found = {}
    for folder, dirs, files in os.walk(kit, followlinks=False):
        dirs.sort()
        here = Path(folder)
        for name in list(dirs):
            if name == "__pycache__":
                dirs.remove(name)
                continue
            if (here / name).is_symlink():
                raise KitError(f"symlink in the kit folder: {(here / name).relative_to(kit).as_posix()}")
        for name in sorted(files):
            path = here / name
            rel = path.relative_to(kit).as_posix()
            if name.endswith(".pyc") or rel == MANIFEST:
                continue
            mode = os.lstat(path).st_mode
            if stat.S_ISLNK(mode):
                raise KitError(f"symlink in the kit folder: {rel}")
            if not stat.S_ISREG(mode):
                raise KitError(f"not a regular file in the kit folder: {rel}")
            if CONTROL.search(rel):
                raise KitError("a kit file name holds a control character or an invisible or "
                               f"direction-changing one: {rel!r}")
            found[rel] = file_record(path)
    return found


def render(version: str, files: dict) -> str:
    lines = [f"# kit-version: {version}"]
    lines += [f"{digest}  {mode}  {rel}" for rel, (digest, mode) in sorted(files.items())]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("Usage: kit-manifest.py <kit folder> <version>", file=sys.stderr)
        return 2
    kit, version = Path(args[0]), args[1]
    if not PLAIN_VERSION.fullmatch(version):
        print(f"kit-manifest: version must be a plain version such as 1.9, not {version!r}; nothing written",
              file=sys.stderr)
        return 2
    try:
        text = render(version, kit_files(kit))
    except (KitError, OSError) as error:
        print(f"kit-manifest: {error}; nothing written", file=sys.stderr)
        return 2
    target = kit / MANIFEST
    temporary = kit / (MANIFEST + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temporary, target)
    print(f"kit-manifest: wrote {target} ({text.count(chr(10)) - 1} files, version {version})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
