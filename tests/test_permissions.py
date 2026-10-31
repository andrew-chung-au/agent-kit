"""Configuration tests for the kit's tool permission rules.

These tests read agent-kit/claude-code/settings.json and
agent-kit/opencode/opencode.json and evaluate the rules with a small model of
each tool's matching. They check configuration, not the live tools: QA checks
the behaviour in each tool that is available.

Models used:
- Both tools: in a command rule `*` matches any characters, a trailing ` *`
  also matches the bare command (`git status *` matches `git status`), and a
  rule without `*` matches exactly.
- Claude Code: a deny rule wins over an allow rule, whatever the order.
  An Edit rule without a `/` matches the file name, and `*` there doesn't
  cross `/`.
- OpenCode: the last matching rule wins (agent-kit/opencode/START.md), so the
  general `*` rule comes first and specific rules after it. `*` matches any
  characters.
"""
from __future__ import annotations

import fnmatch
import json
import re
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent / "agent-kit"
CLAUDE = json.loads((KIT / "claude-code" / "settings.json").read_text(encoding="utf-8"))["permissions"]
OPENCODE = json.loads((KIT / "opencode" / "opencode.json").read_text(encoding="utf-8"))["permission"]

ALLOWED_COMMANDS = [
    "git remote", "git remote -v", "git remote show origin", "git remote get-url origin",
    "git cat-file -p HEAD", "gh issue view 22", "gh issue list", "gh run list",
    "gh run view 123", "sha256sum file",
]
REFUSED_COMMANDS = [
    "git remote add origin x", "git remote remove origin", "git remote rename origin up",
    "git remote set-url origin x", "git remote set-head origin -a",
    "git remote set-branches origin main", "git remote prune origin", "git remote update",
    "git remote update origin", "gh run view 123 --log", "gh run view 123 --log-failed",
    "gh run view --log 123",
]
ENV_DENIED = [".env", ".env.local", ".env.production.local"]
EDIT_DENY_RULES = ["Edit(.env)", "Edit(.env.local)", "Edit(.env.*.local)"]


def wildcard(pattern: str, text: str) -> bool:
    """`*` matches any characters; a trailing ` *` also matches the bare command."""
    optional_tail = pattern.endswith(" *")
    if optional_tail:
        pattern = pattern[:-2]
    regex = "".join(".*" if ch == "*" else re.escape(ch) for ch in pattern)
    if optional_tail:
        regex += "(?: .*)?"
    return re.fullmatch(regex, text, flags=re.DOTALL) is not None


def rule_body(rule: str, tool: str):
    prefix = tool + "("
    if rule.startswith(prefix) and rule.endswith(")"):
        return rule[len(prefix):-1]
    return None


def claude_matches(rule: str, tool: str, value: str) -> bool:
    body = rule_body(rule, tool)
    if body is None:
        return False
    if tool == "Bash":
        return wildcard(body, value)
    name = value.rsplit("/", 1)[-1]
    return "/" not in body and fnmatch.fnmatchcase(name, body) and "/" not in name


def claude_decision(tool: str, value: str) -> str:
    """Claude Code: deny wins over ask and allow, whatever the order."""
    for decision in ("deny", "ask", "allow"):
        if any(claude_matches(rule, tool, value) for rule in CLAUDE.get(decision, [])):
            return decision
    return "ask"


def opencode_decision(section: str, value: str) -> str:
    """OpenCode: the last matching rule wins."""
    decision = "ask"
    for pattern, action in OPENCODE[section].items():
        if wildcard(pattern, value):
            decision = action
    return decision


class WildcardModelTest(unittest.TestCase):
    def test_model_matches_exactly_without_star(self):
        self.assertTrue(wildcard("git remote", "git remote"))
        self.assertFalse(wildcard("git remote", "git remote add origin x"))
        self.assertTrue(wildcard("gh run view *--log*", "gh run view 1 --log-failed"))

    def test_model_deny_wins_and_last_match_wins(self):
        self.assertEqual(claude_decision("Bash", "git push origin main"), "deny")
        self.assertEqual(opencode_decision("read", ".env.example"), "allow")
        self.assertEqual(opencode_decision("read", ".env"), "deny")


class EnvEditDenyTest(unittest.TestCase):
    def test_claude_code_has_exact_env_edit_denies(self):
        for rule in EDIT_DENY_RULES:
            self.assertIn(rule, CLAUDE["deny"])
        self.assertNotIn("Edit(.env*)", CLAUDE["deny"])
        for rule in CLAUDE["deny"]:
            if rule.startswith("Edit("):
                self.assertFalse(rule.startswith("Edit(/"), rule)

    def test_claude_code_env_edit_mirrors_read_deny(self):
        reads = sorted(r[len("Read("):] for r in CLAUDE["deny"] if r.startswith("Read(.env"))
        edits = sorted(r[len("Edit("):] for r in CLAUDE["deny"] if r.startswith("Edit(.env"))
        self.assertEqual(reads, edits)

    def test_claude_code_denies_env_edits(self):
        for name in ENV_DENIED:
            self.assertEqual(claude_decision("Edit", name), "deny", name)
            self.assertEqual(claude_decision("Edit", "config/" + name), "deny", name)

    def test_claude_code_keeps_env_example_editable(self):
        for rule in EDIT_DENY_RULES:
            self.assertFalse(claude_matches(rule, "Edit", ".env.example"), rule)
        self.assertNotEqual(claude_decision("Edit", ".env.example"), "deny")

    def test_opencode_has_exact_env_edit_rules_in_order(self):
        edit = list(OPENCODE["edit"].items())
        self.assertEqual(edit[0], ("*", "allow"))
        self.assertIn(("*.env", "deny"), edit)
        self.assertIn(("*.env.*", "deny"), edit)
        self.assertIn(("*.env.example", "allow"), edit)
        self.assertNotIn("*.env*", OPENCODE["edit"])
        keys = [k for k, _ in edit]
        self.assertLess(keys.index("*.env.*"), keys.index("*.env.example"))

    def test_opencode_denies_env_edits(self):
        for name in ENV_DENIED:
            self.assertEqual(opencode_decision("edit", name), "deny", name)

    def test_opencode_keeps_env_example_editable(self):
        self.assertEqual(opencode_decision("edit", ".env.example"), "allow")


class ReadOnlyAllowTest(unittest.TestCase):
    def test_claude_code_allows_read_only_commands(self):
        for command in ALLOWED_COMMANDS:
            self.assertEqual(claude_decision("Bash", command), "allow", command)

    def test_claude_code_refuses_mutating_and_log_commands(self):
        for command in REFUSED_COMMANDS:
            self.assertEqual(claude_decision("Bash", command), "deny", command)

    def test_opencode_allows_read_only_commands(self):
        for command in ALLOWED_COMMANDS:
            self.assertEqual(opencode_decision("bash", command), "allow", command)

    def test_opencode_refuses_mutating_and_log_commands(self):
        for command in REFUSED_COMMANDS:
            self.assertEqual(opencode_decision("bash", command), "deny", command)

    def test_no_broad_git_remote_allow(self):
        self.assertNotIn("Bash(git remote *)", CLAUDE["allow"])
        self.assertNotIn("git remote*", OPENCODE["bash"])
        self.assertNotIn("git remote *", OPENCODE["bash"])

    def test_no_allow_rule_matches_a_mutating_git_remote(self):
        # The required `gh run view` allows do match `--log` forms; the denies
        # above refuse those (deny wins / last match wins), as the refused
        # command tests show.
        for command in REFUSED_COMMANDS:
            for rule in CLAUDE["allow"]:
                if command.startswith("git remote"):
                    self.assertFalse(claude_matches(rule, "Bash", command), (rule, command))
            allows = [p for p, a in OPENCODE["bash"].items() if a == "allow" and p != "*"]
            if command.startswith("git remote"):
                for pattern in allows:
                    self.assertFalse(wildcard(pattern, command), (pattern, command))

    def test_opencode_denies_come_after_their_allows(self):
        keys = list(OPENCODE["bash"])
        for deny in ("git remote add *", "git remote set-head *", "git remote set-branches *",
                     "gh run view *--log*", "gh run view *--log-failed*"):
            self.assertEqual(OPENCODE["bash"][deny], "deny")
            self.assertGreater(keys.index(deny), keys.index("gh run view*"), deny)

    def test_claude_code_has_every_listed_rule(self):
        for rule in ("Bash(git cat-file *)", "Bash(git remote)", "Bash(git remote -v)",
                     "Bash(git remote show *)", "Bash(git remote get-url *)", "Bash(gh issue view *)",
                     "Bash(gh issue list *)", "Bash(gh run list *)", "Bash(gh run view *)",
                     "Bash(sha256sum *)"):
            self.assertIn(rule, CLAUDE["allow"])
        for rule in ("Bash(git remote add *)", "Bash(git remote remove *)", "Bash(git remote rename *)",
                     "Bash(git remote set-head *)", "Bash(git remote set-branches *)",
                     "Bash(git remote set-url *)", "Bash(git remote prune *)",
                     "Bash(git remote update *)", "Bash(gh run view *--log*)",
                     "Bash(gh run view *--log-failed*)"):
            self.assertIn(rule, CLAUDE["deny"])


if __name__ == "__main__":
    unittest.main()
