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
    reported as drift and its body is NOT written (never stripped silently).
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


class FeedbackError(Exception):
    """Exit 2: nothing written. The message is the one-line reason."""


def _folder(arg: str, what: str) -> Path:
    if not arg:
        raise FeedbackError(f"the {what} is required")
    path = Path(arg)
    if path.is_symlink() or not path.is_dir():
        raise FeedbackError(f"the {what} is missing, not a folder or a symlink: {arg}")
    return path


def project_kit_dir(project: Path) -> Path:
    """The project's kit folder, from its agent-kit.conf KIT_DIR (read as text)."""
    try:
        kit, _claim = kit_check.read_conf(project)
    except kit_check.CheckError as error:
        raise FeedbackError(f"the project has no readable agent-kit.conf: {error}")
    if kit.is_symlink() or not kit.is_dir():
        raise FeedbackError(f"the project's kit folder is missing or a symlink: {kit}")
    return kit


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
    reports = installed_report(project_kit, project)
    kit_states = kit_file_diff(project_kit, reference)

    lines = ["# kit-feedback bundle",
             f"# project: {project}", f"# reference kit: {reference}",
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
        body, ok = strip_local(install.read_bytes().decode("utf-8"))
        if not ok:
            lines.append("(markers unbalanced: reported as drift; body not written, to avoid stripping it wrongly)")
        else:
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
    except FeedbackError as error:
        print(f"kit-feedback: {error}; nothing written", file=sys.stderr)
        return 2
    scratch = Path.cwd() / ".scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    out = scratch / f"kit-feedback-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
    out.mkdir()
    bundle = out / "bundle.md"
    bundle.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"kit-feedback: wrote {bundle}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
