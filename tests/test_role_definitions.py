"""Pins the Claude Code PM and QA role definitions (issue #28).

The PM may use the Edit tool (limited to .scratch/ by role text only, not by a
hook); NotebookEdit stays disallowed. QA keeps both disallowed. The OpenCode PM
keeps edits denied except under .scratch/.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

AGENTS = Path(__file__).resolve().parent.parent / "agent-kit"


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if match is None:
        raise AssertionError(f"{path} has no front matter")
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def disallowed(role: str) -> list:
    fields = front_matter(AGENTS / "claude-code" / "agents" / f"{role}.md")
    return [t.strip() for t in fields.get("disallowedTools", "").split(",") if t.strip()]


class RoleDefinitionTest(unittest.TestCase):
    def test_pm_may_edit_but_not_edit_notebooks(self):
        tools = disallowed("pm")
        self.assertNotIn("Edit", tools)
        self.assertIn("NotebookEdit", tools)

    def test_qa_cannot_edit_or_edit_notebooks(self):
        tools = disallowed("qa-engineer")
        self.assertIn("Edit", tools)
        self.assertIn("NotebookEdit", tools)

    def test_pm_text_limits_writes_to_scratch(self):
        text = (AGENTS / "claude-code" / "agents" / "pm.md").read_text(encoding="utf-8")
        self.assertIn("edit only under `.scratch/`", text)

    def test_opencode_pm_edits_only_under_scratch(self):
        text = (AGENTS / "opencode" / "agents" / "pm.md").read_text(encoding="utf-8")
        self.assertRegex(text, r'"\*": deny\n\s+"\.scratch/\*": allow')


# Tool layers with role prompts (#198 ruling). Adding a layer is one line here.
LAYERS = ("claude-code", "opencode", "codebuddy", "antigravity")
ROLES = ("pm", "software-engineer", "qa-engineer")
POINTER = re.compile(r"Read `_docs/agent-kit/team/([a-z-]+\.md)` and follow it\.")


class LayersInStepTest(unittest.TestCase):
    def test_every_layer_points_each_role_at_its_own_team_file(self):
        for layer in LAYERS:
            for role in ROLES:
                with self.subTest(layer=layer, role=role):
                    text = (AGENTS / layer / "agents" / f"{role}.md").read_text(encoding="utf-8")
                    self.assertEqual(POINTER.findall(text), [f"{role}.md"])

    def test_the_team_files_name_the_role_return(self):
        # The return format lives in the team files, so no prompt needs its own line.
        for role in ROLES:
            text = " ".join((AGENTS / "team" / f"{role}.md").read_text(encoding="utf-8").split())
            with self.subTest(role=role):
                self.assertIn("the role return of `_docs/agent-kit/procedures/formats.md`", text)


if __name__ == "__main__":
    unittest.main()
