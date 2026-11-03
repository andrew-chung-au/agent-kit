"""Checks for the repository's root README.md (issue #2).

`check(text)` returns the problems found in a README text; empty means it
passes. The real README must pass, and each refused case below edits an
in-memory copy of it and must fail with a matching message.

What it proves: relative links resolve and their #anchors exist, backticked
repo paths exist, `make <target>` names are in the repo's Makefile, no email
address or profile link is present, the required sections are there, and the
lifecycle section is short. What it cannot prove: that a sentence is true.
That is read by a person at the diff review.

It reuses code_lines, make_claims, makefile_targets and heading_slugs from
agent-kit/scripts/check-claims.py (imported, never edited).
"""
from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
README = REPO / "README.md"
CHECKER = REPO / "agent-kit" / "scripts" / "check-claims.py"

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("check_claims", CHECKER)
claims = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(claims)

PATH_PREFIXES = ("agent-kit/", "tests/", "_session-summaries/", "_human-tasks/", ".github/", "_docs/agent-kit/")
PATH_NAMES = ("Makefile", "LICENSE", "AGENTS.md", "agent-kit.conf")
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
PROFILE = re.compile(r"github\.com/[^/\s)>\]`\"']+/?(?=[\s)>\]`\"']|$)", re.IGNORECASE)
LINKEDIN = re.compile(r"linkedin\.com", re.IGNORECASE)
VERSION = re.compile(r"\bversion\s+v?\d|\bv\d+\.\d+", re.IGNORECASE)
BANNED_WORDS = ("powerful", "robust", "seamless", "blazing", "cutting-edge", "production-ready")
HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
MAX_LIFECYCLE_WORDS = 250


def headings(text: str):
    """Return (level, title, line index) for each heading outside fenced code."""
    result, fence = [], None
    for index, line in enumerate(text.splitlines()):
        match = FENCE.match(line)
        if fence:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                fence = None
            continue
        if match:
            fence = match.group(1)
            continue
        found = HEADING.match(line)
        if found:
            result.append((len(found.group(1)), found.group(2), index))
    return result


def section(text: str, title_prefix: str):
    """Return the lines under the first heading starting with title_prefix, or None."""
    lines = text.splitlines()
    found = headings(text)
    for position, (level, title, index) in enumerate(found):
        if title.lower().startswith(title_prefix.lower()):
            end = len(lines)
            for next_level, _, next_index in found[position + 1:]:
                if next_level <= level:
                    end = next_index
                    break
            return lines[index + 1:end]
    return None


def resolve_span(span: str, root: Path):
    for prefix in ("_docs/agent-kit/",):
        if span.startswith(prefix):
            return root / "agent-kit" / span[len(prefix):]
    return root / span


def is_repo_path(span: str) -> bool:
    if not (span.startswith(PATH_PREFIXES) or span in PATH_NAMES):
        return False
    if any(ch.isspace() for ch in span):
        return False
    return not any(mark in span for mark in ("<", ">", "$", "~", "...", "=", "://"))


def check(text: str, root: Path = REPO) -> list[str]:
    """Return the problems found in a README text; empty means it passes."""
    errors: list[str] = []
    own_slugs = claims.heading_slugs(text)

    # 1. Relative Markdown links and their anchors.
    for match in LINK.finditer(text):
        target = match.group(1)
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
            continue  # external URL or mailto: handled by the contact checks
        path, _, anchor = target.partition("#")
        if not path:
            if anchor and anchor not in own_slugs:
                errors.append(f"link `{target}`: no heading with that anchor in this README")
            continue
        found = (root / path).resolve()
        if not found.exists():
            errors.append(f"link `{target}`: file does not exist")
        elif anchor:
            if found.suffix != ".md" or anchor not in claims.heading_slugs(found.read_text(encoding="utf-8")):
                errors.append(f"link `{target}`: no heading with anchor `#{anchor}`")

    # 2. Backticked repo paths, and 3. make targets in code.
    targets = claims.makefile_targets(root / "Makefile")
    for number, code, inline in claims.code_lines(text):
        if inline and is_repo_path(code.split("#", 1)[0]):
            path = code.split("#", 1)[0]
            if "*" in path:
                folder, _, pattern = path.rpartition("/")
                if not list(resolve_span(folder + "/", root).glob(pattern)):
                    errors.append(f"line {number}: pattern `{code}` matches nothing")
            elif path.endswith("/"):
                if not resolve_span(path, root).is_dir():
                    errors.append(f"line {number}: directory `{code}` does not exist")
            elif not resolve_span(path, root).exists():
                errors.append(f"line {number}: path `{code}` does not exist")
        for target in claims.make_claims(code):
            if target not in targets:
                errors.append(f"line {number}: make target `{target}` is not in the Makefile")

    # 4. Contact details and profile links.
    if EMAIL.search(text):
        errors.append("contains an email address")
    if PROFILE.search(text):
        errors.append("contains a link to a GitHub profile")
    if LINKEDIN.search(text):
        errors.append("mentions linkedin.com")

    # 5. Required content.
    link_targets = [m.group(1).split("#", 1)[0] for m in LINK.finditer(text)]
    for needed in ("agent-kit/README.md", "LICENSE"):
        if needed not in link_targets:
            errors.append(f"no link to {needed}")
    works = section(text, "How it works")
    if works is None:
        errors.append("no 'How it works' section")
    else:
        body = "\n".join(works)
        numbered = [l for l in works if re.match(r"^\s*\d+\.\s", l)]
        if "```mermaid" not in body and len(numbered) < 5:
            errors.append("'How it works' has neither a Mermaid block nor a numbered lifecycle")
        if len(body.split()) > MAX_LIFECYCLE_WORDS:
            errors.append(f"'How it works' is over {MAX_LIFECYCLE_WORDS} words")
    for title in ("Limits", "Not verified by automation", "Problem and design principles",
                  "Evidence of quality", "Install and quick start"):
        if section(text, title) is None:
            errors.append(f"no '{title}' section")

    # 6. Things the README must not do.
    if VERSION.search(text):
        errors.append("states a version number")
    if "proposals/" in text:
        errors.append("mentions proposals/")
    lowered = text.lower()
    for word in BANNED_WORDS:
        if word in lowered:
            errors.append(f"uses the word '{word}'")
    return errors


class RealReadmeTest(unittest.TestCase):
    def test_root_readme_exists_and_passes(self):
        self.assertTrue(README.is_file(), "README.md is missing at the repo root")
        self.assertEqual(check(README.read_text(encoding="utf-8")), [])


class RefusedCasesTest(unittest.TestCase):
    """Each case edits a copy of the real README and must make the checker fail."""

    @classmethod
    def setUpClass(cls):
        cls.text = README.read_text(encoding="utf-8")

    def assertRefused(self, text: str, fragment: str):
        errors = check(text)
        self.assertTrue(any(fragment in e for e in errors), f"{fragment!r} not in {errors}")

    def test_missing_link_target(self):
        self.assertRefused(self.text + "\nSee [more](agent-kit/nope.md).\n", "agent-kit/nope.md")

    def test_missing_anchor_in_repo_file(self):
        self.assertRefused(self.text + "\n[x](agent-kit/process.md#no-such-heading)\n", "no-such-heading")

    def test_missing_anchor_in_this_readme(self):
        self.assertRefused(self.text + "\n[x](#no-such-heading)\n", "no-such-heading")

    def test_unknown_make_target(self):
        self.assertRefused(self.text + "\nRun `make no-such-target`.\n", "no-such-target")

    def test_known_make_target_with_variable_passes(self):
        self.assertEqual(check(self.text + "\nRun `make issue-hash N=2`.\n"), [])

    def test_missing_backticked_path(self):
        self.assertRefused(self.text + "\nSee `tests/test_missing.py`.\n", "tests/test_missing.py")

    def test_missing_kit_path_through_docs_alias(self):
        self.assertRefused(self.text + "\nSee `_docs/agent-kit/nope.md`.\n", "_docs/agent-kit/nope.md")

    def test_missing_directory_and_glob(self):
        self.assertRefused(self.text + "\nSee `tests/nope/`.\n", "tests/nope/")
        self.assertRefused(self.text + "\nSee `tests/zzz_*.py`.\n", "matches nothing")

    def test_limits_heading_removed(self):
        text = re.sub(r"^## Limits.*$", "## Something else", self.text, flags=re.M)
        self.assertRefused(text, "no 'Limits' section")

    def test_not_verified_heading_removed(self):
        text = self.text.replace("## Not verified by automation", "## Other")
        self.assertRefused(text, "Not verified by automation")

    def test_lifecycle_removed(self):
        text = re.sub(r"^## How it works.*$", "## Process", self.text, flags=re.M)
        self.assertRefused(text, "How it works")

    def test_lifecycle_too_long(self):
        text = self.text.replace("## Evidence of quality", "word " * 260 + "\n\n## Evidence of quality")
        self.assertRefused(text, "over")

    def test_required_links_removed(self):
        self.assertRefused(self.text.replace("(LICENSE)", "(README.md)"), "no link to LICENSE")
        text = re.sub(r"\(agent-kit/README\.md(#[^)]*)?\)", "(AGENTS.md)", self.text)
        self.assertRefused(text, "no link to agent-kit/README.md")

    def test_email_added(self):
        self.assertRefused(self.text + "\nContact: someone@example.com\n", "email")

    def test_profile_links_added(self):
        self.assertRefused(self.text + "\n[me](https://github.com/someone)\n", "GitHub profile")
        self.assertRefused(self.text + "\nhttps://github.com/someone/\n", "GitHub profile")
        self.assertRefused(self.text + "\n[me](https://www.linkedin.com/in/someone)\n", "linkedin")

    def test_link_to_a_repository_file_is_allowed(self):
        self.assertEqual(check(self.text + "\n[x](https://github.com/someone/repo/issues/9)\n"), [])

    def test_version_number_added(self):
        self.assertRefused(self.text + "\nThis is version 1.9 of the kit.\n", "version number")

    def test_proposals_and_superlatives(self):
        self.assertRefused(self.text + "\nSee proposals/plan.md\n", "proposals/")
        self.assertRefused(self.text + "\nA powerful kit.\n", "powerful")


if __name__ == "__main__":
    unittest.main()
