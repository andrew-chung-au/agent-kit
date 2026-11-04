#!/usr/bin/env python3
"""Report repeated sentences and repeated decision keys in Markdown docs. Read-only, never a gate.

Run through the make target, from the project folder:
    make dup-report
or directly:
    python3 -B _docs/agent-kit/scripts/dup-report.py [--exclude <prefix>]... <path>...

Each <path> is a file or a folder; folders are walked for `*.md` and `*.md.template`
files. `--exclude <prefix>` (repeatable) skips any file whose path, relative to the
current folder and written with `/`, starts with <prefix>. `.git/` is always skipped,
and so is any symlink (file or folder), so the walk never leaves the tree it was given.
Only regular files are read: a FIFO, device or socket named `*.md` is skipped, and the
read itself opens non-blocking and re-checks the type, so the report never hangs.
Decision keys are sorted without converting their digits to a number, so a key with
thousands of digits cannot crash it.

It prints, to standard output only:
  1. Repeated sentences: text between `.` `!` `?` and a space, 12 words or more, with
     fenced code dropped, markdown marks and case folded and whitespace collapsed (the
     rule of the docs-structure research script `dup68.py`, #68), found in 2 or more
     files, with the files that hold each one.
  2. Decision keys (`D<n>`, `H<n>`, `F<n>`, `Q<n>`, `A<n>`) found in 2 or more files,
     and, as a separate line, each such key whose status words differ: a line holding
     the key also holds `open` in one file and `decided` in another.

It is a report, never a gate: it exits 0 whenever it runs, duplicates or not, and a
file it cannot read is listed as unreadable, not fatal. Exit 2 only for bad usage (no
path given, or a path that does not exist). It opens files read-only, writes nothing,
runs no subprocess and uses no network. It never decides which duplicates are
deliberate; that is the human's or QA's call. Standard library only.
"""
from __future__ import annotations

import argparse
import collections
import os
import re
import stat
import sys
from pathlib import Path

MIN_WORDS = 12
SUFFIXES = (".md", ".md.template")
KEY = re.compile(r"\b([DHFQA][0-9]+)\b")
STATUS = re.compile(r"\b(open|decided)\b", re.IGNORECASE)
FENCE = re.compile(r"```.*?```", re.S)
MARKS = re.compile(r"[`*_>|#\[\]()-]")
SPACE = re.compile(r"\s+")
SPLIT = re.compile(r"(?<=[.!?]) ")
PREVIEW = 80


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def excluded(name: str, prefixes) -> bool:
    return name == ".git" or name.startswith(".git/") or any(name.startswith(p) for p in prefixes)


def regular(path: Path) -> bool:
    """True only for a regular file that is not a symlink (lstat: never follows a link)."""
    try:
        return stat.S_ISREG(os.lstat(path).st_mode)
    except OSError:
        return False


def key_order(key: str):
    """Sort D2 before D10 without int(): the digits may be thousands long, and int()
    refuses more than 4300. Compare by letter, digits without leading zeros by length,
    then by text, then the full key so D01 and D1 keep a fixed order."""
    digits = key[1:].lstrip("0")
    return (key[0], len(digits), digits, key)


def collect(paths, prefixes):
    """Return (sorted relative names of the files to scan, list of usage errors)."""
    found, errors = set(), []
    for raw in paths:
        start = Path(raw)
        if start.is_symlink():
            continue
        if start.exists() and not start.is_dir():
            # A named file: only a regular one is read (a FIFO would block the read).
            if (start.name.endswith(SUFFIXES) and regular(start)
                    and not excluded(rel(start), prefixes)):
                found.add(rel(start))
            continue
        if not start.is_dir():
            errors.append(f"not a file or folder: {raw}")
            continue
        for folder, dirs, files in os.walk(start, followlinks=False):
            here = Path(folder)
            dirs[:] = sorted(d for d in dirs if not (here / d).is_symlink()
                             and not excluded(rel(here / d) + "/", prefixes))
            for name in files:
                path = here / name
                if not name.endswith(SUFFIXES) or not regular(path):
                    continue
                name_rel = rel(path)
                if not excluded(name_rel, prefixes):
                    found.add(name_rel)
    return sorted(found), errors


def read(name: str):
    """Return the file's text, or None when it is not a regular file or cannot be read.

    Opened with O_NONBLOCK and checked with fstat on the open descriptor, so a FIFO,
    device or socket is refused without ever blocking, and a file swapped for one after
    the walk is refused too.
    """
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))
    except OSError:
        return None
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            return None
        os.set_blocking(fd, True)
        with os.fdopen(fd, "rb") as handle:
            fd = None
            return handle.read().decode("utf-8", errors="replace")
    except OSError:
        return None
    finally:
        if fd is not None:
            os.close(fd)


def sentences(text: str) -> set:
    text = FENCE.sub(" ", text)
    text = MARKS.sub(" ", text)
    text = SPACE.sub(" ", text)
    out = set()
    for piece in SPLIT.split(text):
        piece = piece.strip().lower()
        if len(piece.split()) >= MIN_WORDS:
            out.add(piece)
    return out


def keys(text: str):
    """Return {key: set of status words on the lines that hold it} for one file."""
    found = collections.defaultdict(set)
    for line in text.splitlines():
        line_keys = set(KEY.findall(line))
        if not line_keys:
            continue
        words = {w.lower() for w in STATUS.findall(line)}
        for key in line_keys:
            found[key] |= words
    return found


def report(names):
    lines = []
    where = collections.defaultdict(set)
    key_files = collections.defaultdict(dict)
    unreadable = []
    for name in names:
        text = read(name)
        if text is None:
            unreadable.append(name)
            continue
        for sentence in sentences(text):
            where[sentence].add(name)
        for key, words in keys(text).items():
            key_files[key][name] = words
    repeated = {s: fs for s, fs in where.items() if len(fs) >= 2}
    lines.append(f"dup-report: read-only report, never a gate. Files scanned: {len(names) - len(unreadable)}.")
    for name in unreadable:
        lines.append(f"unreadable (skipped): {name}")
    lines.append(f"Repeated sentences ({MIN_WORDS}+ words, in 2+ files): {len(repeated)}")
    for sentence, files in sorted(repeated.items(), key=lambda kv: (sorted(kv[1]), kv[0])):
        preview = sentence if len(sentence) <= PREVIEW else sentence[:PREVIEW] + "..."
        lines.append(f"- {' | '.join(sorted(files))} :: {preview}")
    shared = {k: v for k, v in key_files.items() if len(v) >= 2}
    lines.append(f"Decision keys in 2+ files: {len(shared)}")
    order = sorted(shared, key=key_order)
    for key in order:
        lines.append(f"- {key}: {', '.join(sorted(shared[key]))}")
    for key in order:
        files = shared[key]
        with_open = sorted(f for f, w in files.items() if "open" in w)
        with_decided = sorted(f for f, w in files.items() if "decided" in w)
        if with_open and with_decided and set(with_open) != set(with_decided):
            lines.append(f"- {key}: status differs: open in {', '.join(with_open)}; "
                         f"decided in {', '.join(with_decided)}")
    return lines


def main(argv) -> int:
    parser = argparse.ArgumentParser(prog="dup-report.py", add_help=True)
    parser.add_argument("--exclude", action="append", default=[], metavar="PREFIX")
    parser.add_argument("paths", nargs="*")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2
    if not args.paths:
        print("dup-report: give at least one file or folder to scan", file=sys.stderr)
        return 2
    names, errors = collect(args.paths, args.exclude)
    if errors:
        for error in errors:
            print(f"dup-report: {error}", file=sys.stderr)
        return 2
    try:
        print("\n".join(report(names)))
        sys.stdout.flush()
    except BrokenPipeError:
        # The reader stopped early (`make dup-report | head`). The report is done, not
        # failed: point stdout at devnull so the exit-time flush stays quiet, and exit 0.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
