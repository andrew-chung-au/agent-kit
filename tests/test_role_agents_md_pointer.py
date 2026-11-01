"""Pins the opening pointer of the role definitions (issue #35, commit 3).

A role definition must not tell the role to read `AGENTS.md` (the tool already
loads it), and must name its own `team/<role>.md`, never another role's or none.
TOOLS lists the tool folders checked: both Claude Code and OpenCode.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent / "agent-kit"
ROLES = ("pm", "software-engineer", "qa-engineer")
TOOLS = ("claude-code", "opencode")

READS_AGENTS_MD = re.compile(r"\bread\b[^.\n]*AGENTS\.md", re.IGNORECASE)
TEAM_REF = re.compile(r"team/([a-z-]+)\.md")


def check(role: str, text: str) -> list:
    """Return the problems found in one definition's text."""
    problems = []
    if READS_AGENTS_MD.search(text):
        problems.append("tells the role to read AGENTS.md")
    named = set(TEAM_REF.findall(text))
    if role not in named:
        problems.append(f"does not name team/{role}.md")
    for other in sorted(named - {role}):
        problems.append(f"names the wrong role's team/{other}.md")
    return problems


class RoleDefinitionPointerTest(unittest.TestCase):
    def test_definitions_point_to_own_team_file_and_not_agents_md(self):
        for tool in TOOLS:
            for role in ROLES:
                path = KIT / tool / "agents" / f"{role}.md"
                with self.subTest(tool=tool, role=role):
                    self.assertEqual(check(role, path.read_text(encoding="utf-8")), [])


class CheckRefusesTest(unittest.TestCase):
    def test_refuses_read_agents_md(self):
        text = "Read `AGENTS.md`, then `_docs/agent-kit/team/pm.md`, and follow both."
        self.assertIn("tells the role to read AGENTS.md", check("pm", text))

    def test_refuses_wrong_role_file(self):
        text = "Read `_docs/agent-kit/team/qa-engineer.md` and follow it."
        problems = check("pm", text)
        self.assertIn("does not name team/pm.md", problems)
        self.assertIn("names the wrong role's team/qa-engineer.md", problems)

    def test_refuses_no_team_file(self):
        self.assertIn("does not name team/pm.md", check("pm", "Follow the rules."))

    def test_accepts_reworded_line(self):
        text = "Read `_docs/agent-kit/team/pm.md` and follow it."
        self.assertEqual(check("pm", text), [])


if __name__ == "__main__":
    unittest.main()
