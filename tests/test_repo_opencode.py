"""This repo's own opencode.json against the kit template (issue #47).

Structure and order only, under the last-match-wins model in
tests/test_permissions.py. They never run OpenCode's real matcher.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))["permission"]
TEMPLATE = json.loads(
    (ROOT / "agent-kit" / "opencode" / "opencode.json").read_text(encoding="utf-8"))["permission"]


class RepoOpencodeTest(unittest.TestCase):
    def test_same_bash_rules_in_the_same_order_as_the_template(self):
        self.assertEqual(list(REPO["bash"].items()), list(TEMPLATE["bash"].items()))

    def test_bash_order(self):
        keys = list(REPO["bash"])
        self.assertEqual(keys[0], "*")
        self.assertEqual(keys[-1], "*.env*")
        first_deny = next(i for i, k in enumerate(keys) if REPO["bash"][k] == "deny")
        for key in keys[first_deny:]:
            self.assertEqual(REPO["bash"][key], "deny", key)
        last_allow = max(i for i, k in enumerate(keys) if REPO["bash"][k] == "allow")
        self.assertLess(last_allow, keys.index("*$*"))
        self.assertLess(keys.index("*<*"), first_deny)

    def test_edit_rules_keep_protected_paths_and_add_env_rules(self):
        edit = REPO["edit"]
        keys = list(edit)
        self.assertEqual(keys[0], "*")
        for key, value in (("*.env", "deny"), ("*.env.*", "deny"), ("*.env.example", "allow")):
            self.assertEqual(edit[key], value)
        self.assertLess(keys.index("*.env.*"), keys.index("*.env.example"))
        for key in ("AGENTS.md", "CLAUDE.md", "agent-kit.conf", "_docs/specs.md", "agent-kit/*",
                    "Makefile", ".claude/*", "opencode.json", ".opencode/*", ".githooks/*",
                    ".github/*"):
            self.assertEqual(edit[key], "ask", key)
            self.assertGreater(keys.index(key), keys.index("*.env.example"), key)
        self.assertEqual(edit[".devcontainer/*"], "deny")
        self.assertEqual(edit["agent-kit/environments/local-sandbox/pre-push"], "deny")

    def test_read_rules_match_the_template(self):
        self.assertEqual(REPO["read"], TEMPLATE["read"])


if __name__ == "__main__":
    unittest.main()
