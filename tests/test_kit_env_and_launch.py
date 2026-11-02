"""Tests for issue #35 (kit side): the .env rule, the launch message and the upgrade note.

They read the real kit files, so they fail if a later change drops one of these.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent / "agent-kit"


def read(rel):
    return (KIT / rel).read_text(encoding="utf-8")


class EnvRuleTest(unittest.TestCase):
    def test_template_states_env_rule_including_shell(self):
        text = read("templates/AGENTS.md.template")
        self.assertRegex(text, r"Never open, print or copy `\.env` files, including through the shell")
        self.assertIn("use `.env.example`", text)

    def test_hook_line_says_claude_code_hook_and_opencode_text_rule_block_shell_env(self):
        text = read("templates/AGENTS.md.template")
        line = next(l for l in text.splitlines() if l.startswith("Hooks and tool settings block"))
        self.assertIn("shell commands naming `.env` files (Claude Code's hook; in OpenCode a text-pattern rule)", line)
        self.assertNotIn("OpenCode does not", line)
        self.assertNotIn("(not shell commands)", line)

    def test_claude_code_still_denies_env_read_and_edit(self):
        deny = json.loads(read("claude-code/settings.json"))["permissions"]["deny"]
        for rule in ("Read(.env)", "Edit(.env)"):
            self.assertIn(rule, deny)

    def test_opencode_still_denies_env_read_and_edit(self):
        perms = json.loads(read("opencode/opencode.json"))["permission"]
        for tool in ("read", "edit"):
            self.assertEqual(perms[tool].get("*.env"), "deny", tool)


class LaunchMessageTest(unittest.TestCase):
    def test_generic_launch_message_still_tells_tools_to_read_agents_md(self):
        text = read("process.md")
        self.assertRegex(text, r'start every launch message with: "Read `AGENTS\.md`, then ')


class UpgradeNoteTest(unittest.TestCase):
    def note(self):
        text = read("README.md")
        m = re.search(r"^\*\*Note for projects last upgraded[^\n]*", text, re.M)
        self.assertIsNotNone(m, "upgrade note is missing")
        return m.group(0)

    def test_note_names_both_markers_and_the_human_approved_diff(self):
        note = self.note()
        for needle in ("<!-- SHARED START ... -->", "<!-- SHARED END -->", "<!-- SHARED: ... -->",
                       "never replaces a project's `AGENTS.md` wholesale", "diff you approve"):
            self.assertIn(needle, note)

    def test_note_is_short(self):
        self.assertLessEqual(len(self.note().split()), 110)


class NoDanglingConventionsTest(unittest.TestCase):
    def test_only_the_changelog_entry_mentions_conventions(self):
        hits = []
        for path in KIT.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".py", ".json", ".template", ".sh"}:
                for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if re.search(r"Conventions", line):
                        hits.append((path.relative_to(KIT).as_posix(), line))
        self.assertEqual([h[0] for h in hits], ["README.md"], hits)
        self.assertTrue(hits[0][1].startswith("- **Conventions:**"))


if __name__ == "__main__":
    unittest.main()
