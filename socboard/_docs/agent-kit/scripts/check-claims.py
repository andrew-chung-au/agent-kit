#!/usr/bin/env python3
"""Claims check: fail when the kit's docs promise something the kit doesn't ship.

Run from the repo root as part of `make test`, or directly:
    python3 -B agent-kit/scripts/check-claims.py [--kit <kit folder>]

It reads every Markdown file under the kit folder (default: the folder above
this script) and nothing outside it. Only inline code spans and fenced code
blocks are read; prose is never a claim. Three checks:

1. Make targets. In code, the target of `make` is the first bare token after
   skipping VAR=value, options starting with `-`, and the values of options
   that take one (-C, -f, -I, -o, -W and their long forms). A target with a
   placeholder (`<name>-start`) is skipped, as is `make` with no target. The
   known targets are those in templates/Makefile.mk, plus those in any kit
   `*.mk` file the same doc names. The repo's own Makefile is not a source.

2. Kit paths. An inline code span is checked as a path when it starts with a
   kit prefix (templates/, procedures/, scripts/, team/, githooks/,
   environments/, claude-code/, opencode/, agents/, hooks/, agent-kit/,
   _docs/agent-kit/). `agent-kit/<p>` and `_docs/agent-kit/<p>` resolve to the
   kit root; any other path resolves against the doc's folder first, then the
   kit root, and passes if either exists. A trailing `/` must be a directory.
   Spans with `<`, `>`, `*`, `$`, `~`, `...`, `=`, `://` or whitespace are
   skipped as placeholders, globs or commands. A span with `#` is checked only
   when the part before the first `#` ends in `.md` and the anchor is not empty:
   the file must exist and have a heading whose GitHub-style slug (lowercase,
   punctuation other than hyphens removed, spaces turned into hyphens) is the
   anchor; any other span with `#` is skipped. Bare filenames without
   a `/` (such as `settings.json`) are deliberately not checked: the same name
   can mean a kit file or a project file.

3. Blueprints coverage. Every installable path must be named in blueprints.md
   (in backticks or a table cell). Installable means every top-level entry of
   the kit except its own docs (README.md, blueprints.md, environments.md,
   setup.md, process.md), plus every first-level directory with a file in it
   under templates/, scripts/, githooks/, claude-code/, opencode/,
   environments/, procedures/ and team/. A path is covered when blueprints.md
   names it, names a parent directory ending in `/`, or (for a directory)
   names a path inside it. So a directory row covers new files inside it,
   but a new module or first-level directory without a row fails.

Prints `doc:line: claim` for each failure and exits 1, or prints one pass line.
Standard library only.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

KIT_PREFIXES = (
    "templates/", "procedures/", "scripts/", "team/", "githooks/", "environments/",
    "claude-code/", "opencode/", "agents/", "hooks/", "agent-kit/", "_docs/agent-kit/",
)
ROOT_PREFIXES = ("_docs/agent-kit/", "agent-kit/")
PATH_SKIP = ("<", ">", "*", "$", "~", "...", "=", "://")
MAKE_OPTS_WITH_VALUE = {
    "-C", "-f", "-I", "-o", "-W",
    "--directory", "--file", "--include", "--old-file", "--assume-old",
}
KIT_DOCS = {"README.md", "blueprints.md", "environments.md", "setup.md", "process.md"}
MODULE_DIRS = ("templates", "scripts", "githooks", "claude-code", "opencode",
               "environments", "procedures", "team")
IGNORED_NAMES = {"__pycache__"}
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING = re.compile(r"^ {0,3}#{1,6}\s+(.*?)\s*#*\s*$")
INLINE = re.compile(r"(`+)(.+?)(?<!`)\1(?!`)")
OPERATORS = re.compile(r"&&|\|\||[;|()`]")
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
TARGET_LINE = re.compile(r"^([^\s:#=][^:#=]*?)\s*::?(?!=)")


def code_lines(text: str):
    """Yield (line number, code text, is_inline) for every code span and fenced line."""
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        match = FENCE.match(line)
        if fence:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                fence = None
            else:
                yield number, line, False
            continue
        if match:
            fence = match.group(1)
            continue
        for span in INLINE.finditer(line):
            yield number, span.group(2).strip(), True


def make_target(tokens):
    """Return the target of a make command given the tokens after `make`, or None."""
    rest = list(tokens)
    while rest:
        token = rest.pop(0)
        if ASSIGNMENT.match(token):
            continue
        if token.startswith("-"):
            if token in MAKE_OPTS_WITH_VALUE and rest:
                rest.pop(0)
            continue
        return token
    return None


def make_claims(code: str):
    """Yield every make target named in one line of code."""
    for segment in OPERATORS.split(code):
        tokens = segment.split()
        for index, token in enumerate(tokens):
            if token != "make":
                continue
            target = make_target(tokens[index + 1:])
            if target and not any(ch in target for ch in "<>*$[]{}\"'"):
                yield target
            break


def makefile_targets(path: Path):
    targets = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(("\t", " ", ".")):
            continue
        match = TARGET_LINE.match(line)
        if match:
            targets.update(t for t in match.group(1).split() if "<" not in t)
    return targets


def resolve(span: str, doc: Path, kit: Path):
    """Return the candidate paths for a kit path span."""
    for prefix in ROOT_PREFIXES:
        if span.startswith(prefix):
            return [kit / span[len(prefix):]]
    return [doc.parent / span, kit / span]


def is_kit_path(span: str) -> bool:
    if not span.startswith(KIT_PREFIXES):
        return False
    if any(mark in span for mark in PATH_SKIP):
        return False
    if any(ch.isspace() for ch in span):
        return False
    if "#" in span:
        path, _, anchor = span.partition("#")
        return path.endswith(".md") and bool(anchor) and "#" not in anchor
    return True


def heading_slugs(text: str) -> set:
    """Return the GitHub-style anchor of every heading outside fenced code."""
    slugs, seen, fence = set(), {}, None
    for line in text.splitlines():
        match = FENCE.match(line)
        if fence:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                fence = None
            continue
        if match:
            fence = match.group(1)
            continue
        heading = HEADING.match(line)
        if not heading:
            continue
        slug = re.sub(r"[^\w\- ]", "", heading.group(1).lower()).replace(" ", "-")
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        slugs.add(slug if count == 0 else f"{slug}-{count}")
    return slugs


def path_exists(candidate: Path, want_dir: bool) -> bool:
    return candidate.is_dir() if want_dir else candidate.exists()


def check_docs(kit: Path, failures: list, counts: dict):
    base_targets = makefile_targets(kit / "templates" / "Makefile.mk")
    for doc in sorted(kit.rglob("*.md")):
        if any(part in IGNORED_NAMES for part in doc.parts):
            continue
        counts["docs"] += 1
        label = doc_label(doc, kit)
        entries = list(code_lines(doc.read_text(encoding="utf-8")))
        targets = set(base_targets)
        for _, code, inline in entries:
            if inline and is_kit_path(code) and code.endswith(".mk"):
                for candidate in resolve(code, doc, kit):
                    if candidate.is_file():
                        targets |= makefile_targets(candidate)
                        break
        for number, code, inline in entries:
            for target in make_claims(code):
                counts["targets"] += 1
                if target not in targets:
                    failures.append(f"{label}:{number}: make target `{target}` is not in templates/Makefile.mk "
                                    f"or a .mk file this doc names (claim: `{code.strip()}`)")
            if inline and is_kit_path(code):
                counts["paths"] += 1
                path, _, anchor = code.partition("#")
                want_dir = path.endswith("/")
                found = [c for c in resolve(path, doc, kit) if path_exists(c, want_dir)]
                if not found:
                    kind = "directory" if want_dir else "path"
                    failures.append(f"{label}:{number}: kit {kind} `{code}` does not exist")
                elif anchor and anchor not in heading_slugs(found[0].read_text(encoding="utf-8")):
                    failures.append(f"{label}:{number}: kit path `{code}` has no heading with anchor `#{anchor}`")


def installable(kit: Path):
    """Return (relative path, is_dir) for every path blueprints.md must cover."""
    result = []
    for entry in sorted(kit.iterdir()):
        if entry.name in KIT_DOCS or entry.name in IGNORED_NAMES or entry.name.startswith("."):
            continue
        result.append((entry.name, entry.is_dir()))
    for module in MODULE_DIRS:
        folder = kit / module
        if not folder.is_dir():
            continue
        for sub in sorted(folder.iterdir()):
            if not sub.is_dir() or sub.name in IGNORED_NAMES or sub.name.startswith("."):
                continue
            if any(f.is_file() for f in sub.rglob("*")):
                result.append((f"{module}/{sub.name}", True))
    return result


def blueprint_names(blueprints: Path):
    names = set()
    text = blueprints.read_text(encoding="utf-8")
    candidates = [code for _, code, inline in code_lines(text) if inline]
    for line in text.splitlines():
        if line.lstrip().startswith("|"):
            candidates += [cell.strip() for cell in line.strip().strip("|").split("|")]
    for name in candidates:
        if not name or any(ch.isspace() for ch in name):
            continue
        if name.startswith("./"):
            name = name[2:]
        for prefix in ROOT_PREFIXES:
            if name.startswith(prefix):
                name = name[len(prefix):]
                break
        if name:
            names.add(name)
    return names


def covered(path: str, is_dir: bool, names) -> bool:
    for name in names:
        if name.rstrip("/") == path:
            return True
        if name.endswith("/") and path.startswith(name):
            return True
        if is_dir and name.startswith(path + "/"):
            return True
    return False


def check_coverage(kit: Path, failures: list, counts: dict):
    blueprints = kit / "blueprints.md"
    if not blueprints.is_file():
        failures.append(f"{doc_label(blueprints, kit)}: missing, so nothing is covered")
        return
    names = blueprint_names(blueprints)
    for path, is_dir in installable(kit):
        counts["installable"] += 1
        if not covered(path, is_dir, names):
            shown = path + "/" if is_dir else path
            failures.append(f"{doc_label(blueprints, kit)}: no row or path names installable `{shown}`")


def doc_label(doc: Path, kit: Path) -> str:
    try:
        return os.path.relpath(doc)
    except ValueError:
        return str(doc)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Check that the kit's docs only promise what it ships.")
    parser.add_argument("--kit", default=str(Path(__file__).resolve().parent.parent),
                        help="kit folder to check (default: the folder above this script)")
    args = parser.parse_args(argv)
    kit = Path(args.kit).resolve()
    if not (kit / "templates" / "Makefile.mk").is_file():
        print(f"claims: FAIL. {kit} has no templates/Makefile.mk", file=sys.stderr)
        return 1
    failures: list = []
    counts = {"docs": 0, "targets": 0, "paths": 0, "installable": 0}
    check_docs(kit, failures, counts)
    check_coverage(kit, failures, counts)
    if failures:
        for failure in failures:
            print(failure)
        print(f"claims: FAIL ({len(failures)} unshipped claim(s))")
        return 1
    print(f"claims: OK ({counts['docs']} docs, {counts['targets']} make targets, "
          f"{counts['paths']} kit paths, {counts['installable']} installable paths covered)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
