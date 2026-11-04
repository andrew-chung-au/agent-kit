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

    def test_it_is_git_and_coreutils_only_never_make_or_running_a_repo_file(self):
        low = self.section.lower()
        self.assertIn("git diff --no-index", self.section)
        self.assertIn("git and coreutils only", low)
        self.assertIn("never `make`", self.section)
        self.assertIn("never by running or sourcing a repo file", self.section)
        # No `make` target is invoked in the comparison recipe itself.
        for line in self.section.splitlines():
            if line.strip().startswith("git ") or line.strip().startswith("test "):
                self.assertNotIn("make ", line)

    def test_it_states_sandbox_tools_never_open_the_human_machine_paths(self):
        self.assertIn("A sandbox tool never opens a `human-machine` install path", self.section)
        self.assertIn("can never prove the installed push check is current", self.section)

    def test_the_install_paths_come_from_the_map_not_a_second_hard_coding(self):
        for install in self.human_machine_install_paths():
            self.assertIn(install, self.section, f"map install path {install} missing from the doc")
        self.assertIn("installed-files.txt", self.section)
        self.assertIn("not hard-coded in a second place", self.section)

    def test_the_refused_case_is_documented(self):
        low = self.section.lower()
        self.assertIn("symlink", low)
        self.assertIn("missing", low)
        self.assertIn("you do not follow it", low)

    def test_the_push_check_source_is_named_and_not_edited_here(self):
        self.assertIn("environments/local-sandbox/pre-push", self.section)


if __name__ == "__main__":
    unittest.main()
