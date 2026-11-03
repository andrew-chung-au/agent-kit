"""Behaviour tests for the tool-versions target in agent-kit/templates/Makefile.mk (issue #95).

The target is run with a throwaway PATH that holds only a stub node. Standard
library only; nothing is installed and nothing touches the network.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import unittest

from kit_repo import KIT, new_workdir

TEMPLATE = KIT / "templates" / "Makefile.mk"
TOOLS = ("git", "gh", "node", "npm", "python3", "uv", "docker")
MAKE = shutil.which("make") or "make"


def recipe_text():
    text = TEMPLATE.read_text(encoding="utf-8")
    start = text.index("tool-versions::")
    block = text[start:text.index("\n\n", start)]
    return "\n".join(ln for ln in block.splitlines() if ln.startswith("\t"))


class ToolVersionsTest(unittest.TestCase):
    def setUp(self):
        self.work = new_workdir(prefix="tool-versions-")
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.stubs = self.work / "stubs"
        self.stubs.mkdir()
        node = self.stubs / "node"
        node.write_text("#!/bin/sh\necho v1.2.3\n", encoding="utf-8")
        node.chmod(0o755)

    def run_make(self, *args, path=None):
        env = {"PATH": str(self.stubs) if path is None else path, "HOME": str(self.work)}
        return subprocess.run([MAKE, "-f", str(TEMPLATE), "tool-versions", *args], cwd=self.work, env=env,
                              capture_output=True, text=True, timeout=60)

    def test_node_has_a_version_line_and_the_rest_are_missing(self):
        r = self.run_make()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines(),
                         ["node: v1.2.3" if t == "node" else f"{t}: missing" for t in TOOLS])

    def test_a_tool_that_prints_several_lines_gives_one_line(self):
        gh = self.stubs / "gh"
        gh.write_text("#!/bin/sh\necho 'gh version 9.9.9'\necho 'https://example.invalid/release'\n", encoding="utf-8")
        gh.chmod(0o755)
        lines = self.run_make().stdout.splitlines()
        self.assertEqual(len(lines), len(TOOLS))
        self.assertIn("gh: gh version 9.9.9", lines)

    def test_a_variable_is_not_pasted_into_the_shell(self):
        for args in (["TOOLS=x; echo injected"], ["PATH=x; echo injected"], ["TOOLS=$(echo injected)"]):
            with self.subTest(args=args):
                r = self.run_make(*args)
                self.assertNotIn("injected", r.stdout + r.stderr)

    def test_a_path_variable_on_the_command_line_does_not_run_anything(self):
        r = self.run_make("PATH=x; echo injected", path=os.environ.get("PATH", ""))
        self.assertNotIn("injected", r.stdout + r.stderr)

    def test_the_recipe_has_no_make_variable_in_it(self):
        recipe = recipe_text()
        self.assertNotRegex(recipe, r"\$\(|\$\{")
        self.assertIn("command -v", recipe)
        self.assertNotRegex(recipe, r"\b(sudo|curl|wget|pip|npm install|apt)\b")

    def test_it_is_a_double_colon_target_so_projects_can_extend_it(self):
        self.assertTrue(re.search(r"(?m)^tool-versions:: ", TEMPLATE.read_text(encoding="utf-8")))
        extra = self.work / "Makefile"
        extra.write_text(TEMPLATE.read_text(encoding="utf-8") + "\ntool-versions::\n\t@echo extra-ran; true\n", encoding="utf-8")
        r = subprocess.run([MAKE, "tool-versions"], cwd=self.work, env={"PATH": str(self.stubs)},
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("node: v1.2.3", r.stdout)
        self.assertIn("extra-ran", r.stdout)


if __name__ == "__main__":
    unittest.main()
