#!/usr/bin/env python3
"""Reverse import: read a project's kit and write a feedback bundle under .scratch/.

Run from the folder that holds .scratch/ (normally the kit's own repo), as
`make kit-feedback PROJECT=<project root> KIT=<reference kit>`:
    python3 -B agent-kit/scripts/kit-feedback.py <project root> <reference kit root>

Both roots are explicit and required; there is no default. The project root is a checkout
that carries a kit (it holds agent-kit.conf, read as TEXT for KIT_DIR, never sourced). The
reference kit root is the kit to compare against. Neither vuln-triage/ copy of the kit is
authoritative, so the caller names the two roots and the tool treats neither as the source
of truth: it lists differences and the human decides.

The bundle, written to .scratch/kit-feedback-<timestamp>/, lists:
  - changed installed files (`repo` map entries): one line per entry from the one shared
    scan (kit_map.scan_installed), `unchanged`, `local, ignored`, `drift` or `missing`;
  - changed kit files: the two-way kit-file list (the scan kit-manifest shares), one line
    per file, `modified`, `added` or `missing`;
  - for each changed `repo` entry, a copy of the project's file with the lines between
    `agent-kit: local-begin` and `agent-kit: local-end` stripped, so a personal value
    inside the markers never reaches the bundle. A file whose markers are unclosed is
    reported as drift and its body is NOT written (never stripped silently). An entry whose
    allowed-to-differ rule is `prefix:<text>` (the real map uses it for setup.sh, whose
    `git config --global user.` lines hold a personal name and email) also has every line
    that starts with that text stripped, the same lines the shared scan ignores; the bundle
    says how many were removed, never what they held.
  - a note that `human-machine` entries (the push check) are supplied by the human from
    the clean clone; their install paths are never opened.

Refused (MapError or a bad root): a map entry the parser rejects fails the run with the
parser's message and writes no bundle; a missing or non-folder root, or a project with no
readable agent-kit.conf, does the same.

Read-only over both trees: the tool opens the project's kit and `repo` install files only
to read them, and writes only under .scratch/. It never writes an installed file or a kit
file, never opens a `human-machine` install path, and never deletes a vuln-triage/ copy;
pointed at a vuln-triage/ kit copy it writes the same read-only comparison under .scratch/
so the human can decide which copy to keep (record item 8, option 3). The project tree is
untrusted data: the tool hashes and lists; it never runs or follows anything found in it.
Standard library only.
"""
from __future__ import annotations

import importlib.util
import os
import re
import sys
import time
from pathlib import Path

_here = Path(__file__).parent


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, _here / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kit_manifest = _load("kit_manifest", "kit-manifest.py")
kit_check = _load("kit_check", "kit-check.py")
kit_map = _load("kit_map", "kit-map.py")

LOCAL_BEGIN = kit_map.LOCAL_BEGIN
LOCAL_END = kit_map.LOCAL_END

# Install paths this tool refuses to open, even when the project's own map names them: an
# env file, anything under .git/, and a short list of obvious secret file names. The
# project's installed-files.txt is untrusted (issue #116, QA launch 2 item 2): a crafted map
# must not be able to make this read-only tool copy a secret into a public bundle.
# A folder name may hold no control character at all (kit_map.CONTROL lets newline and tab
# through because a map file has lines; a folder name must not, or it could forge a heading).
_NAME_CONTROL = re.compile("[\x00-\x1f\x7f\x85\u2028\u2029]")
_ENV_NAME = re.compile(r"(?i)^\.env")
_SECRET_NAME = re.compile(r"(?i)(\.pem$|\.key$|^id_rsa|^\.netrc$|^\.npmrc$|^credentials)")


def _refused_install_path(install: str) -> str | None:
    """None if install is safe to open; else the one-line reason it is refused."""
    parts = install.split("/")
    if ".git" in parts:
        return f"install path is under .git/: {install!r}"
    name = parts[-1]
    if _ENV_NAME.search(name):
        return f"install path looks like an env file: {install!r}"
    if _SECRET_NAME.search(name):
        return f"install path looks like a secret file: {install!r}"
    return None


class FeedbackError(Exception):
    """Exit 2: nothing written. The message is the one-line reason."""


def _fs(call, *args, failed=None):
    """kit_map.fs() with its MapError turned into a FeedbackError (exit 2, one-line reason)."""
    try:
        return kit_map.fs(call, *args, failed=failed)
    except kit_map.MapError as error:
        raise FeedbackError(str(error))


def _scrub(message: str, args) -> str:
    """The message with the caller's folder paths replaced by labels (no absolute path out)."""
    for raw, label in ((args[0], "<project root>"), (args[1], "<reference kit root>")):
        for form in {raw, str(Path(raw).resolve()) if raw and not _NAME_CONTROL.search(raw) else raw}:
            if form:
                message = message.replace(form, label)
    return message


def _folder(arg: str, what: str) -> Path:
    if not arg:
        raise FeedbackError(f"the {what} is required")
    if _NAME_CONTROL.search(arg):
        raise FeedbackError(f"the {what} holds a control character or line break")
    path = Path(arg)
    if _fs(path.is_symlink) or not _fs(path.is_dir):
        raise FeedbackError(f"the {what} is missing, not a folder or a symlink")
    return path


def project_kit_dir(project: Path) -> Path:
    """The project's kit folder, from its agent-kit.conf KIT_DIR (read as text)."""
    try:
        kit, _claim = kit_check.read_conf(project)
    except kit_check.CheckError as error:
        raise FeedbackError(f"the project has no readable agent-kit.conf: {error}")
    if _fs(kit.is_symlink) or not _fs(kit.is_dir):
        raise FeedbackError("the project's kit folder is missing or a symlink")
    return kit


def _read_text(path: Path, shown: str) -> str:
    """One installed file as UTF-8 text, read through kit_map.fs()."""
    try:
        return kit_map.read_utf8(path, f"cannot read the installed file {shown!r}")
    except kit_map.MapError as error:
        raise FeedbackError(str(error))


def strip_local(text: str) -> tuple[str, bool]:
    """Return (text with marker blocks removed, markers_ok).

    markers_ok is False when the markers are unbalanced (an unclosed begin, an end with no
    begin, or a nested begin): the body is then returned unchanged, so the caller can refuse
    to write it instead of stripping silently.
    """
    out = []
    depth = 0
    ok = True
    for line in text.splitlines(keepends=True):
        has_begin, has_end = LOCAL_BEGIN in line, LOCAL_END in line
        if has_begin and has_end:
            ok = False
            out.append(line)
        elif has_begin:
            if depth:
                ok = False
            depth += 1
        elif has_end:
            if depth:
                depth -= 1
            else:
                ok = False
                out.append(line)
        elif depth == 0:
            out.append(line)
    if depth:
        ok = False
    return ("".join(out) if ok else text), ok


def strip_prefix(text: str, prefix: str) -> tuple[str, int]:
    """Return (text without the lines that start with prefix, how many were removed).

    The shared scan (kit_map.scan_text) only ignores a line that starts with prefix exactly,
    for the drift comparison. In the bundle, broader: a line is dropped if it CONTAINS prefix
    once both are normalised (whitespace collapsed, lowercased), so leading whitespace, extra
    spaces inside the rule's own words, and a `sudo` in front of the same command do not leave
    identity text in a public bundle. This only affects what the bundle shows, never the scan.
    """
    norm_prefix = " ".join(prefix.lower().split())
    kept, removed = [], 0
    for line in text.splitlines(keepends=True):
        norm_line = " ".join(line.lower().split())
        if norm_prefix and norm_prefix in norm_line:
            removed += 1
        else:
            kept.append(line)
    return "".join(kept), removed


def installed_report(project_kit: Path, project: Path):
    """The shared installed-file scan for the project, or raise FeedbackError on a bad map."""
    try:
        return kit_map.scan_installed(project_kit, project)
    except kit_map.MapError as error:
        raise FeedbackError(str(error))


def kit_file_diff(project_kit: Path, reference: Path):
    """Two-way kit-file list: {rel: state} with state modified/added/missing/unchanged."""
    try:
        theirs = kit_manifest.kit_files(project_kit)
        ours = kit_manifest.kit_files(reference)
    except (kit_manifest.KitError, OSError) as error:
        raise FeedbackError(str(error))
    states = {}
    for rel in sorted(set(theirs) | set(ours)):
        if rel not in ours:
            states[rel] = "added"
        elif rel not in theirs:
            states[rel] = "missing"
        else:
            states[rel] = "unchanged" if theirs[rel] == ours[rel] else "modified"
    return states


def build_bundle(project: Path, reference: Path) -> list[str]:
    """The bundle lines. Reads the project and reference read-only; writes nothing here."""
    project_kit = project_kit_dir(project)
    try:
        entries = kit_map.parse_map(project_kit, project)
    except kit_map.MapError as error:
        raise FeedbackError(str(error))
    # Before anything is read: the project's own map is untrusted, so refuse a `repo` install
    # path that names an env file, anything under .git/, or an obvious secret file name. A
    # `human-machine` path is only named, never opened, so it is not checked here.
    for entry in entries:
        if entry.kind == "repo":
            refused = _refused_install_path(entry.install)
            if refused:
                raise FeedbackError(refused)
    allowed_by_install = {e.install: e.allowed for e in entries}
    reports = installed_report(project_kit, project)
    kit_states = kit_file_diff(project_kit, reference)

    lines = ["# kit-feedback bundle",
             "# project: <project root>", "# reference kit: <reference kit root>",
             "",
             "## Installed files (repo entries)"]
    lines += kit_map.report_lines([r for r in reports if r.kind == "repo"]) or ["(none)"]
    lines += ["",
              "## Human-machine entries (the human supplies these from the clean clone)"]
    human = [r for r in reports if r.kind == "human-machine"]
    lines += [f"- {r.install}" for r in human] or ["(none)"]
    lines += ["", "## Kit files that differ"]
    differ = [f"{state} {rel}" for rel, state in kit_states.items() if state != "unchanged"]
    lines += differ or ["(none)"]

    for report in reports:
        if report.kind != "repo" or report.state not in ("drift", "missing"):
            continue
        lines += ["", f"## Changed installed file: {report.install}"]
        if report.state == "missing":
            lines.append("(missing in the project; nothing to bundle)")
            continue
        install = project
        for part in report.install.split("/"):
            install = install / part
        body, ok = strip_local(_read_text(install, report.install))
        allowed = allowed_by_install.get(report.install, "none")
        removed = 0
        if ok and allowed.startswith("prefix:"):
            body, removed = strip_prefix(body, allowed[len("prefix:"):])
        if not ok:
            lines.append("(markers unbalanced: reported as drift; body not written, to avoid stripping it wrongly)")
        else:
            if removed:
                lines.append(f"({removed} line(s) allowed to differ by the map's prefix rule removed; their text is not in the bundle)")
            lines.append("```")
            lines += body.splitlines()
            lines.append("```")
    return lines


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("Usage: kit-feedback.py <project root> <reference kit root>", file=sys.stderr)
        return 2
    try:
        project = _folder(args[0], "project root")
        reference = _folder(args[1], "reference kit root")
        lines = build_bundle(project, reference)
        try:
            data = ("\n".join(lines) + "\n").encode("utf-8")
        except UnicodeEncodeError:
            raise FeedbackError("a file name in the bundle is not valid UTF-8 text")
        scratch = _fs(Path.cwd, failed="cannot read the working folder") / ".scratch"
        if _fs(scratch.is_symlink):
            raise FeedbackError("the .scratch folder is a symlink; the bundle would land outside it")
        _fs(lambda: scratch.mkdir(parents=True, exist_ok=True), failed="cannot create the .scratch folder")
        out = scratch / f"kit-feedback-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
        bundle = out / "bundle.md"
        # Everything that can fail on the content has happened above, in memory. Now the
        # bytes go to a temp file in .scratch/, the folder is made, and the file is renamed
        # in, so a failure never leaves a partial or empty bundle.md (and the folder is
        # removed again if the rename fails).
        tmp = scratch / f".kit-feedback-{os.getpid()}.tmp"
        try:
            _fs(lambda: tmp.write_bytes(data), failed="cannot write the bundle")
            _fs(out.mkdir, failed="cannot create the bundle folder")
            try:
                _fs(lambda: tmp.rename(bundle), failed="cannot write the bundle")
            except FeedbackError:
                _fs(out.rmdir)
                raise
        finally:
            if tmp.exists():
                tmp.unlink()
    except FeedbackError as error:
        print(f"kit-feedback: {_scrub(str(error), args)}; nothing written", file=sys.stderr)
        return 2
    print(f"kit-feedback: wrote {bundle.relative_to(Path.cwd())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
