#!/usr/bin/env python3
"""Find the commit of the kit's own repository that a live kit folder was copied from.

For a live kit with no MANIFEST.sha256 (every project that took the kit before it shipped
manifests), the forward import (procedures/kit-import.md, step 2) needs a baseline. This
read-only script compares the live kit's files with the history of a clone of the kit's
repository and prints the commits that match most files.

Run through the make target, from the project root:
    make kit-baseline KIT=<live kit folder> SOURCE=<clone of the kit repository>
or directly:
    python3 -B <kit>/scripts/kit-baseline.py <live kit folder> <clone of the kit repository>

Both are plain relative paths (letters, digits . _ / - only), as for `make kit-compare`;
put the clone under `.scratch/`. In the clone the kit is the `agent-kit/` folder. A path in a
commit holding a control or invisible character is skipped, as in kit-manifest.py. Only
commits that changed `agent-kit/` are looked at, newest first, at most 2000. A file counts
as matching when its path (inside the kit folder) and its content are the same. File modes
are ignored, because a copy or an unzip may drop them.

Output, all of it data (a commit's message is never printed, and nothing is run from either
folder), at most three candidates, best first:

    live kit: <n> files
    candidate <k>: <40 hex> <YYYY-MM-DD>: matches <m> of <n> live files; <a> differ; <b> only in the live kit; <c> only in the commit[; <d> other commits hold the same files]
    differs <path>              (for candidate 1: the same path, different content)
    only in the live kit <path>
    only in the commit <path>
    baseline: <40 hex> (<m> of <n> live files)       a clear unique best: the human approves it
    baseline: none; <reason>                         no clear best: the human decides

Candidates are ordered by most matches, then fewest files only in the commit, then newest.
Two different trees that tie on both are a tie, not a pick. A clear best matches at least
three quarters of the live files and is not tied. Commits whose kit files are identical are
one candidate (the newest is named).

Exit codes: 0 a clear unique best (the `baseline:` line names it); 1 no clear best, the
candidates are listed for the human; 2 an error, nothing compared (a one-line `kit-baseline:`
reason): a bad argument, a symlink in the live kit, a clone that is not a git work tree, a shallow clone.

It writes nothing (the `git` commands it runs only read: rev-parse, log, ls-tree), refuses a
symlink in the live kit like kit-manifest.py, and ignores `*.pyc`, `__pycache__` and
MANIFEST.sha256 as it does. To produce the baseline's manifest from the chosen commit, use
the commands in procedures/kit-import.md. Standard library and git only.
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

_here = Path(__file__).parent
KIT_IN_SOURCE = "agent-kit"
MAX_COMMITS = 2000
SHOWN = 3
PLAIN_PATH = re.compile(r"[A-Za-z0-9._/-]+")
HEX40 = re.compile(r"[0-9a-f]{40}")
MODES = ("100644", "100755")


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, _here / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kit_manifest = _load("kit_manifest", "kit-manifest.py")


class BaselineError(Exception):
    """Exit 2: nothing compared. The message is the one-line reason."""


def plain_folder(arg: str, label: str) -> Path:
    """A plain relative path to a real folder with no symlink on the way."""
    parts = arg.split("/")
    if (not arg or not PLAIN_PATH.fullmatch(arg) or arg.startswith(("/", "-")) or ".." in parts
            or "" in parts or "." in parts):
        raise BaselineError(f"{label} must be a plain relative path: letters, digits . _ / - only, "
                            f"no .. or empty parts: {arg!r}")
    path = Path(".")
    for part in parts:
        path = path / part
        if path.is_symlink():
            raise BaselineError(f"{label} path holds a symlink: {arg}")
    if not path.is_dir():
        raise BaselineError(f"{label} is missing or not a folder: {arg}")
    return path


def git(source: Path, *args: str) -> bytes:
    """Run one read-only git command in the clone; BaselineError with a short reason on failure."""
    try:
        done = subprocess.run(["git", "-C", str(source), *args], capture_output=True,
                              stdin=subprocess.DEVNULL, timeout=120)
    except (OSError, subprocess.SubprocessError) as error:
        raise BaselineError(f"cannot run git: {error}")
    if done.returncode != 0:
        raise BaselineError(f"git {args[0]} failed in the source clone (exit {done.returncode})")
    return done.stdout


def blob_id(data: bytes) -> str:
    """The id git gives a file's content (sha1 of 'blob <size>' NUL content)."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def live_blobs(live: Path) -> dict:
    """{path inside the kit: git blob id} for every kit file; symlinks are refused."""
    try:
        files = kit_manifest.kit_files(live)
    except (kit_manifest.KitError, OSError) as error:
        raise BaselineError(str(error))
    try:
        return {rel: blob_id((live / rel).read_bytes()) for rel in files}
    except OSError as error:
        raise BaselineError(f"cannot read a live kit file: {error.strerror or error}")


def skipped(rel: str) -> bool:
    return rel == kit_manifest.MANIFEST or rel.endswith(".pyc") or "__pycache__" in rel.split("/")


def commit_blobs(source: Path, commit: str) -> dict:
    """{path inside the kit: blob id} of the regular files the commit holds under agent-kit/."""
    out = git(source, "ls-tree", "-r", "-z", commit, "--", KIT_IN_SOURCE)
    found = {}
    prefix = KIT_IN_SOURCE + "/"
    for entry in out.split(b"\0"):
        if not entry:
            continue
        head, _, raw = entry.partition(b"\t")
        fields = head.decode("ascii", "replace").split()
        if len(fields) != 3 or fields[0] not in MODES or fields[1] != "blob":
            continue
        try:
            path = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if kit_manifest.CONTROL.search(path):
            continue  # same check as kit-manifest.py: a name cannot forge or hide output lines
        if path.startswith(prefix) and not skipped(path[len(prefix):]):
            found[path[len(prefix):]] = fields[2]
    return found


def history(source: Path) -> list:
    """[(commit, date)] of the commits that changed the kit folder, newest first."""
    # The clone must be the top of its own work tree: a plain folder inside another repository
    # (the project's own) would otherwise read that repository's history.
    top = git(source, "rev-parse", "--show-toplevel").decode("utf-8", "replace").strip()
    if os.path.realpath(top) != os.path.realpath(source):
        raise BaselineError("the source is not the top folder of a git work tree")
    if git(source, "rev-parse", "--is-shallow-repository").strip() != b"false":
        raise BaselineError("the source clone is shallow; use a full clone, not --depth")
    out = git(source, "log", f"--max-count={MAX_COMMITS}", "--format=%H %cs", "--", KIT_IN_SOURCE)
    commits = []
    for line in out.decode("ascii", "replace").splitlines():
        commit, _, date = line.partition(" ")
        if HEX40.fullmatch(commit) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            commits.append((commit, date))
    return commits


def candidates(live: dict, commits: list, source: Path) -> list:
    """Distinct candidate trees, best first: dicts with the counts and the file lists."""
    seen = {}
    order = []
    for index, (commit, date) in enumerate(commits):
        theirs = commit_blobs(source, commit)
        key = frozenset(theirs.items())
        if key in seen:
            seen[key]["same"] += 1
            continue
        matches = sorted(p for p in live if theirs.get(p) == live[p])
        differ = sorted(p for p in live if p in theirs and theirs[p] != live[p])
        only_live = sorted(p for p in live if p not in theirs)
        only_commit = sorted(p for p in theirs if p not in live)
        item = {"commit": commit, "date": date, "index": index, "same": 0, "matches": len(matches),
                "differ": differ, "only_live": only_live, "only_commit": only_commit}
        seen[key] = item
        order.append(item)
    order.sort(key=lambda c: (-c["matches"], len(c["only_commit"]), c["index"]))
    return order


def verdict(best: list, total: int):
    """(exit code, the `baseline:` line)."""
    if not best:
        return 1, "baseline: none; the source clone has no commit that changed agent-kit/"
    top = best[0]
    if top["matches"] * 4 < total * 3:
        return 1, (f"baseline: none; the best commit matches {top['matches']} of {total} live files, "
                   "less than three quarters")
    if len(best) > 1 and (best[1]["matches"], len(best[1]["only_commit"])) == (
            top["matches"], len(top["only_commit"])):
        return 1, "baseline: none; two different trees tie for the best match"
    return 0, f"baseline: {top['commit']} ({top['matches']} of {total} live files)"


def report(live: dict, best: list) -> int:
    total = len(live)
    print(f"live kit: {total} files")
    for number, item in enumerate(best[:SHOWN], start=1):
        extra = f"; {item['same']} other commits hold the same files" if item["same"] else ""
        print(f"candidate {number}: {item['commit']} {item['date']}: matches {item['matches']} of {total} "
              f"live files; {len(item['differ'])} differ; {len(item['only_live'])} only in the live kit; "
              f"{len(item['only_commit'])} only in the commit{extra}")
    if best:
        top = best[0]
        for label, key in (("differs", "differ"), ("only in the live kit", "only_live"),
                           ("only in the commit", "only_commit")):
            for path in top[key]:
                print(f"{label} {path}")
    code, line = verdict(best, total)
    print(line)
    return code


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else list(argv)
    if len(args) != 2:
        print("kit-baseline: usage: kit-baseline.py <live kit folder> <clone of the kit repository>",
              file=sys.stderr)
        return 2
    try:
        live_dir = plain_folder(args[0], "the live kit folder")
        source = plain_folder(args[1], "the source clone")
        live = {rel: blob for rel, blob in live_blobs(live_dir).items() if not skipped(rel)}
        if not live:
            raise BaselineError("the live kit folder holds no files")
        best = candidates(live, history(source), source)
    except BaselineError as error:
        print(f"kit-baseline: {error}", file=sys.stderr)
        return 2
    return report(live, best)


if __name__ == "__main__":
    sys.exit(main())
