"""The human-only push-check comparison documented in environments.md (issue #117).

Text only: nothing here runs a script. The doc must describe a read-only, human-only, git
and coreutils comparison of the installed push check, and the install paths it names must
come from installed-files.txt (not hard-coded in a second place).
"""
from __future__ import annotations

import importlib.util
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
DOC = KIT / "environments.md"
MAP_SCRIPT = KIT / "scripts" / "kit-map.py"

spec = importlib.util.spec_from_file_location("kit_map", MAP_SCRIPT)
kit_map = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit_map)


def flat(path):
    return " ".join(path.read_text(encoding="utf-8").split())


class PushCheckComparisonDocTest(unittest.TestCase):
    def setUp(self):
        self.text = DOC.read_text(encoding="utf-8")
        self.flat = flat(DOC)
        # The comparison subsection only.
        start = self.text.index("### Comparing the installed push check")
        end = self.text.find("\n## ", start)
        self.section = self.text[start: end if end != -1 else len(self.text)]

    def human_machine_install_paths(self):
        entries = kit_map.parse_map(KIT, REPO)
        return sorted(e.install for e in entries if e.kind == "human-machine")

    def test_section_exists_and_is_human_only(self):
        self.assertIn("### Comparing the installed push check", self.text)
        self.assertIn("human only", self.section.lower())
        self.assertIn("from the clean clone", self.section)

    def recipe_block(self):
        text = self.section
        start = text.index("```")
        end = text.index("```", start + 3)
        return text[start + 3: end].strip("\n")

    def test_it_is_git_and_coreutils_only_never_make_or_running_a_repo_file(self):
        low = self.section.lower()
        self.assertIn("git diff --no-index", self.section)
        self.assertIn("git and coreutils only", low)
        self.assertIn("never `make`", self.section)
        self.assertIn("never by running or sourcing a repo file", self.section)
        block = self.recipe_block()
        # No `make`, `docker`, `cp`, `mv`, `bash` anywhere in the recipe block, and no
        # redirect into an install path (only `git diff --no-index -- -` on stdin).
        for forbidden in ("make ", "make\t", "docker", " cp ", " mv ", "bash"):
            self.assertNotIn(forbidden, block)
        # No redirect into an install path: '>' only appears inside the '<ref>' placeholder.
        self.assertEqual(re.sub(r"<ref>", "", block).count(">"), 0)

    def test_it_states_sandbox_tools_never_open_the_human_machine_paths(self):
        self.assertIn("A sandbox tool never opens a `human-machine` install path", self.section)
        self.assertIn("can never prove the installed push check is current", self.section)

    def test_the_install_paths_come_from_the_map_not_a_second_hard_coding(self):
        for install in self.human_machine_install_paths():
            self.assertIn(install, self.section, f"map install path {install} missing from the doc")
        self.assertIn("installed-files.txt", self.section)
        self.assertIn("not hard-coded in a second place", self.section)
        # Both install paths appear as the recipe's own `p=` assignment, not just prose.
        block = self.recipe_block()
        for install in self.human_machine_install_paths():
            self.assertIn(f"p={install};", block)

    def expected_line(self, entry):
        # The one recipe line for a map entry, built from the map's own install path and
        # kit source path: symlink first (reported, not followed), then a regular-file check
        # (a missing path is reported), then the diff from stdin.
        return (f'p={entry.install}; if test -h "$p"; then echo "symlink: $p, resolve it by hand"; '
                f'elif test -f "$p"; then git show <ref>:_docs/agent-kit/{entry.source} '
                f'| git diff --no-index -- - "$p"; else echo "missing: $p"; fi')

    def test_the_refused_case_is_documented(self):
        low = self.section.lower()
        self.assertIn("symlink", low)
        self.assertIn("missing", low)
        self.assertIn("never followed", low)
        # cmp follows symlinks, so it is not offered as an alternative.
        self.assertNotIn("(or `cmp`)", self.section)
        self.assertIn("`cmp` follows symlinks", self.section)

    def test_the_recipe_block_is_exactly_the_map_driven_lines(self):
        # Any removed, added, reordered or edited line fails: a dropped diff, a dropped
        # `test -h`, a changed `git show` path, an added bash/make/cp line, a redirect.
        entries = [e for e in kit_map.parse_map(KIT, REPO) if e.kind == "human-machine"]
        self.assertEqual(len(entries), 2)
        actual = [l for l in self.recipe_block().splitlines()]
        self.assertEqual(actual, [self.expected_line(e) for e in entries])

    def test_match_and_mismatch_are_described(self):
        low = self.section.lower()
        self.assertIn("match prints nothing and exits 0", low)
        self.assertIn("mismatch prints the diff and exits 1", low)

    def test_each_clone_wording_matches_the_recipe(self):
        # The recipe runs in one clone at a time; the doc must say so, not claim it
        # covers every clone at once.
        self.assertIn("one clone at a time", self.section)
        self.assertIn("repeat it in each clean clone", self.section)

    def test_no_fixed_shared_temp_file(self):
        self.assertNotIn("/tmp/", self.section)
        block = self.recipe_block()
        # The kit text is piped to stdin (`-- -`), never written to a named temp file.
        self.assertIn("git diff --no-index -- -", block)

    def test_the_push_check_source_is_named_and_not_edited_here(self):
        self.assertIn("environments/local-sandbox/pre-push", self.section)


if __name__ == "__main__":
    unittest.main()
