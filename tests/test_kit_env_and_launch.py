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

    def test_no_doc_says_opencode_lacks_a_shell_guard_until_13(self):
        files = ("README.md", "opencode/START.md", "templates/AGENTS.md.template",
                 "../AGENTS.md", "environments.md")
        for rel in files:
            text = read(rel)
            for stale in ("no shell guard until #13", "not blocked until #13"):
                self.assertNotIn(stale, text, (rel, stale))

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
        text = read("install-and-upgrade.md")
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
        self.assertEqual([h[0] for h in hits], ["CHANGELOG.md"], hits)
        self.assertTrue(hits[0][1].startswith("- **Conventions:**"))


UPGRADE_HEADING = "## Situation 4: kit 1.10 or later and a dev container, upgrade the kit, local sandbox"
UNCHANGED_RULES = (
    "**Never run `make` in a clean clone.**",
    "**From Ubuntu, touch the sandbox folder only with `git fetch sandbox`, run from the clean clone.**",
    "**Copy these files only from a clean clone, never from a sandbox.**",
)
UPGRADE_PHRASES = (
    "Prompt A",
    "SANDBOX WINDOW",
    "Explorer's `.scratch/`",
    "Do not copy it in from Ubuntu",
    "make kit-check",
    "HUMAN_APPROVED=1",
    "git fetch sandbox",
    "`make hooks`",
    "(never run `make` here)",
    "never from the container",
)


def upgrade_problems(env_doc: str, install_doc: str) -> list:
    """Problems with the local-sandbox upgrade steps (issue #77; moved by #182).

    The steps live in install-and-upgrade.md, situation 4; the rules that protect the human's machine
    stay in environments.md. It checks wording only: that the steps name the import prompt, the drop
    through the container's VS Code window, the approval-gated commit, the fetch from the clean clone,
    and that the rules are still there and the old unzip wording is not back.
    """
    problems = []
    if UPGRADE_HEADING not in install_doc:
        return ["the upgrade section is missing"]
    section = install_doc.split(UPGRADE_HEADING, 1)[1].split("\n## ", 1)[0]
    for phrase in UPGRADE_PHRASES:
        if phrase not in section:
            problems.append("upgrade steps lack: " + phrase)
    for rule in UNCHANGED_RULES:
        if rule not in env_doc:
            problems.append("rule changed or missing: " + rule)
    for stale in ("Unzip the new kit in the clean clone", "git pull"):
        if stale in env_doc:
            problems.append("stale instruction is back: " + stale)
    return problems


class LocalSandboxUpgradeStepsTest(unittest.TestCase):
    def setUp(self):
        self.env = read("environments.md")
        self.doc = read("install-and-upgrade.md")

    def test_the_real_doc_has_no_problems(self):
        self.assertEqual(upgrade_problems(self.env, self.doc), [])

    def test_the_link_target_exists(self):
        self.assertTrue((KIT / "procedures" / "kit-import.md").is_file())

    def test_the_commit_waits_for_approval_and_the_human_only_fetches_and_pushes(self):
        section = self.doc.split(UPGRADE_HEADING, 1)[1].split("\n## ", 1)[0]
        self.assertRegex(section, r"Approved\. Commit it with HUMAN_APPROVED=1")
        self.assertNotRegex(section, r"(?i)you (review, )?commit")

    def test_each_removed_phrase_is_refused(self):
        for phrase in UPGRADE_PHRASES:
            with self.subTest(phrase=phrase):
                start = self.doc.index(UPGRADE_HEADING)
                mutated = self.doc[:start] + self.doc[start:].replace(phrase, "x")
                self.assertTrue(upgrade_problems(self.env, mutated), phrase)

    def test_each_changed_rule_is_refused(self):
        for rule in UNCHANGED_RULES:
            with self.subTest(rule=rule):
                self.assertTrue(upgrade_problems(self.env.replace(rule, rule.replace("Never", "Sometimes")
                                                                  .replace("only", "mostly"), 1), self.doc))

    def test_the_old_wording_is_refused(self):
        for stale in ("Unzip the new kit in the clean clone, then review, commit and push it yourself.",
                      "In the container: `git pull`, then `make hooks`."):
            with self.subTest(stale=stale):
                self.assertTrue(upgrade_problems(self.env + "\n" + stale + "\n", self.doc))

    def test_a_missing_section_is_refused(self):
        self.assertEqual(upgrade_problems(self.env, self.doc.replace(UPGRADE_HEADING, "## Other")),
                         ["the upgrade section is missing"])


if __name__ == "__main__":
    unittest.main()
