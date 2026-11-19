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
    `git config --global user.` lines hold a personal name and email) is not filtered by
    matching text, because a text filter can always be bypassed: every installed line that is
    not byte-identical to a line of the reference kit's copy of that file is WITHHELD. The
    bundle writes `line N differs (text withheld)` for it, and a count, never the text. The
    human copies a withheld line by hand after reading it.
  - a note that `human-machine` entries (the push check) are supplied by the human from
    the clean clone; their install paths are never opened.

Refused (MapError or a bad root): a map entry the parser rejects fails the run with the
parser's message and writes no bundle; a missing or non-folder root, or a project with no
readable agent-kit.conf, does the same. So does a project map entry whose install path (or
kind) is not in the REFERENCE kit's installed-files.txt: the reference kit's map is the
trusted list of files this tool may read, and the project's own map cannot choose others.
Two more layers sit under that: a name list (an env file, anything under .git/, obvious
secret names) and a hard-link check (an installed file with more than one hard link could be
a secret under an ordinary name). Messages carry no absolute path.

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

# Install paths this tool refuses to open, even when the reference kit's map names them: an
# env file, anything under .git/, and obvious secret file names. This is a second layer under
# the reference-map check (issue #116): a name list can always miss a spelling, so it is never
# the only guard. Each component is compared lower-case with trailing dots and spaces removed
# (a case-insensitive or Windows file system reads `.GIT`, `.git.` and `x.pem.` as the same).
# A folder name may hold no control character at all (kit_map.CONTROL lets newline and tab
# through because a map file has lines; a folder name must not, or it could forge a heading).
_NAME_CONTROL = re.compile("[\x00-\x1f\x7f\x85\u2028\u2029]")
_ENV_NAME = re.compile(r"^\.env")
_SECRET_NAME = re.compile(
    r"(\.(pem|key)(\.|$)"                 # x.pem, x.key, x.pem.bak, notes.pem.txt
    r"|^id_(rsa|dsa|ecdsa|ed25519)"         # ssh private keys (and .pub beside them)
    r"|^\.(netrc|npmrc)"                   # .netrc, .npmrc, .netrc.bak
    r"|^credentials"                        # credentials, credentials.json
    r"|^(tokens?|secrets?)([._-]|$))")      # token.json, secrets.txt, secret-key


def _normal_part(part: str) -> str:
    return part.rstrip(" .").lower()


def _refused_install_path(install: str) -> str | None:
    """None if install is safe to open; else the one-line reason it is refused."""
    parts = [_normal_part(part) for part in install.split("/")]
    if ".git" in parts:
        return f"install path is under .git/: {install!r}"
    name = parts[-1]
    if _ENV_NAME.search(name):
        return f"install path looks like an env file: {install!r}"
    if _SECRET_NAME.search(name):
        return f"install path looks like a secret file: {install!r}"
    return None


def _refused_hard_link(project: Path, install: str) -> str | None:
    """A reason if the installed file has more than one hard link, else None.

    A hard link under an ordinary name can point at a secret file, which no name check can
    see; a file with one name is the normal case. A missing file is not refused here.
    """
    path = project
    for part in install.split("/"):
        path = path / part
    if not _fs(path.is_file):
        return None
    if _fs(os.lstat, path).st_nlink > 1:
        return f"installed file has more than one hard link: {install!r}"
    return None


class FeedbackError(Exception):
    """Exit 2: nothing written. The message is the one-line reason."""


def _fs(call, *args, failed=None):
    """kit_map.fs() with its MapError turned into a FeedbackError (exit 2, one-line reason)."""
    try:
        return kit_map.fs(call, *args, failed=failed)
    except kit_map.MapError as error:
        raise FeedbackError(str(error))


_ABS_PATH = re.compile(r"(?<![\w.~/>-])/[\w.@+~/-]+")


def _scrub(message: str, args) -> str:
    """The message with no absolute path, home folder or working folder in it.

    The two roots the caller named (as given and resolved) become labels, the working folder
    and the home folder become labels, and any other absolute path left becomes <path>. A
    relative root is only replaced where it stands as a whole path token, so `proj` does not
    rewrite the word `project`.
    """
    forms = []
    for raw, label in ((args[0], "<project root>"), (args[1], "<reference kit root>")):
        if not raw:
            continue
        forms.append((raw, label))
        if not _NAME_CONTROL.search(raw):
            try:
                forms.append((str(Path(raw).resolve()), label))
            except OSError:
                pass
    for folder, label in ((Path.cwd(), "<working folder>"), (Path.home(), "~")):
        forms.append((str(folder), label))
    for form, label in sorted(set(forms), key=lambda item: -len(item[0])):
        if form in ("", "/", "."):
            continue
        message = re.sub(r"(?<![\w.~-])" + re.escape(form) + r"(?![\w-])", lambda _m, l=label: l, message)
    return _ABS_PATH.sub("<path>", message)


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


def withhold_differing(text: str, kit_text: str) -> tuple[list[str], int]:
    """The body lines of an installed file whose map rule is `prefix:`, and how many were withheld.

    Matching text is a blacklist and can always be bypassed (a backslash continuation, an
    option between words, a quoted key), so none is done. A line is kept only if it is
    byte-identical to a line of the kit's copy of the same file (the line ending counts);
    every other line is replaced by `line N differs (text withheld)`, N being its 1-based
    line number in the installed file. Lines between the local markers are dropped first,
    as strip_local does. The caller has already checked the markers are balanced.
    """
    kit_lines = set(kit_text.splitlines(keepends=True))
    out, withheld, depth = [], 0, 0
    for number, line in enumerate(text.splitlines(keepends=True), start=1):
        if LOCAL_BEGIN in line:
            depth += 1
        elif LOCAL_END in line:
            depth = max(depth - 1, 0)
        elif depth:
            continue
        elif line in kit_lines:
            out.append("".join(line.splitlines()))
        else:
            out.append(f"line {number} differs (text withheld)")
            withheld += 1
    return out, withheld


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


WHOLE_COPY_WARNING = ("WARNING: this file is copied whole (only the local-begin/local-end blocks are "
                      "removed). Read it before anything goes public: it may hold personal text.")


def build_bundle(project: Path, reference: Path) -> list[str]:
    """The bundle lines. Reads the project and reference read-only; writes nothing here."""
    project_kit = project_kit_dir(project)
    try:
        entries = kit_map.parse_map(project_kit, project)
        reference_entries = kit_map.parse_map(reference, project)
    except kit_map.MapError as error:
        raise FeedbackError(str(error))
    # Before anything is read. The project tree is untrusted, so its own map does not choose
    # which files are read: every entry's install path (and kind) must be in the REFERENCE
    # kit's installed-files.txt. Under that, a `repo` path is refused if its name looks like
    # an env file, a .git/ path or a secret, or if the installed file has several hard links.
    # A `human-machine` path is only named, never opened, so the name and link checks skip it.
    trusted = {e.install: e for e in reference_entries}
    for entry in entries:
        known = trusted.get(entry.install)
        if known is None:
            raise FeedbackError(f"install path is not in the reference kit's installed-files.txt: {entry.install!r}")
        if known.kind != entry.kind:
            raise FeedbackError(f"install path has a different kind in the reference kit's installed-files.txt: {entry.install!r}")
        if entry.kind == "repo":
            refused = _refused_install_path(entry.install) or _refused_hard_link(project, entry.install)
            if refused:
                raise FeedbackError(refused)
    # The rule and the kit source come from the trusted reference entry, not the project's.
    allowed_by_install = {e.install: e for e in reference_entries}
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
        text = _read_text(install, report.install)
        body, ok = strip_local(text)
        trusted_entry = allowed_by_install[report.install]
        if not ok:
            lines.append("(markers unbalanced: reported as drift; body not written, to avoid stripping it wrongly)")
        elif trusted_entry.allowed.startswith("prefix:"):
            try:
                kit_text = kit_map._read_kit_source(reference, trusted_entry.source)
            except kit_map.MapError:
                kit_text = ""  # no usable reference copy: every line is withheld
            body_lines, withheld = withhold_differing(text, kit_text)
            if withheld:
                lines.append(f"({withheld} line(s) differing from the reference kit's copy withheld; their text is not in the bundle)")
            lines.append("```")
            lines += body_lines
            lines.append("```")
        else:
            lines.append(WHOLE_COPY_WARNING)
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
