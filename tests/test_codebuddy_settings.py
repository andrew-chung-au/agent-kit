"""The CodeBuddy layer against the 2026-11-21 spike on 2.185.0.

Nothing here runs CodeBuddy. The settings, agents and skill are checked for the shape the spike
settled, and one shell behaviour is run for real: CodeBuddy treats any non-zero exit other than 2
as a non-blocking error, so a guard crash (exit 1, 127, ...) must go through the command's
`|| exit 2` wrapper or the command would run anyway.

Every file this writes lives under .scratch/ and is deleted.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
LAYER = KIT / "codebuddy"
SCRATCH = REPO / ".scratch"


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


class SettingsShapeTest(unittest.TestCase):
    def setUp(self):
        self.settings = json.loads((LAYER / "settings.json").read_text(encoding="utf-8"))
        self.permissions = self.settings["permissions"]

    def test_it_is_json_and_uses_only_documented_top_level_keys(self):
        self.assertLessEqual(set(self.settings),
                             {"permissions", "hooks", "includeCoAuthoredBy", "memory", "disableAllHooks"})

    def test_parent_discovery_ships_commented_out(self):
        # The default (walk upward) suits a single project; START.md shows the block for a monorepo.
        self.assertNotIn("memory", self.settings)

    def test_bypass_mode_is_disabled_with_the_string(self):
        self.assertEqual(self.permissions["disableBypassPermissionsMode"], "disable")

    def test_no_coauthor_line(self):
        self.assertIs(self.settings["includeCoAuthoredBy"], False)

    def test_deny_covers_env_push_remotes_and_logs(self):
        deny = self.permissions["deny"]
        for rule in ("Read(.env)", "Read(.env.local)", "Read(.env.*.local)", "Edit(.env)",
                     "Bash(git push:*)", "Bash(git remote add:*)", "Bash(git remote set-url:*)",
                     "Bash(gh run view --log:*)"):
            with self.subTest(rule=rule):
                self.assertIn(rule, deny)

    def test_allow_is_read_only_and_never_gh_run_view(self):
        allow = self.permissions["allow"]
        self.assertIn("Bash(make:*)", allow)
        self.assertNotIn("Bash(gh run view:*)", allow)
        self.assertNotIn("Bash(git push:*)", allow)
        for rule in allow:
            with self.subTest(rule=rule):
                self.assertTrue(rule.startswith("Bash("), rule)
                self.assertNotIn("gh api", rule)

    def test_ask_rules_are_relative_to_the_project_folder(self):
        # A leading `/` is relative to the settings file, not the project root, so the template
        # never writes one; a folder pattern ends `/**`, because `*` does not cross subfolders.
        ask = self.permissions["ask"]
        edits = [rule for rule in ask if rule.startswith("Edit(")]
        self.assertIn("Edit(AGENTS.md)", edits)
        self.assertIn("Edit(.codebuddy/**)", edits)
        for rule in edits:
            with self.subTest(rule=rule):
                path = rule[len("Edit("):-1]
                self.assertFalse(path.startswith("/"), "a leading / is settings-file-relative")
                self.assertFalse(path.endswith("/*"), "a folder pattern must end /**")

    def test_the_guard_is_registered_for_bash_with_the_wrapper(self):
        hooks = self.settings["hooks"]["PreToolUse"]
        self.assertEqual(len(hooks), 1)
        self.assertEqual(hooks[0]["matcher"], "Bash")
        commands = [h["command"] for h in hooks[0]["hooks"] if h["type"] == "command"]
        self.assertEqual(len(commands), 1)
        command = commands[0]
        self.assertIn("claude-code/hooks/guard_git.py", command)
        self.assertTrue(command.startswith("python3 "), command)
        self.assertTrue(command.endswith("|| exit 2"), command)

    def test_the_guard_it_names_exists_in_the_kit(self):
        self.assertTrue((KIT / "claude-code" / "hooks" / "guard_git.py").is_file())


class WrapperTest(unittest.TestCase):
    """A hook that exits non-2 must still block, through the command's own `|| exit 2`."""

    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)
        self.dir = Path(tempfile.mkdtemp(prefix="codebuddy-hook-", dir=SCRATCH))
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)
        self.settings = json.loads((LAYER / "settings.json").read_text(encoding="utf-8"))
        command = self.settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        self.wrapper = command[command.index("||"):]

    def run_hook(self, exit_code):
        stub = self.dir / "hook.py"
        stub.write_text(f"import sys\nsys.exit({exit_code})\n", encoding="utf-8")
        wrapped = subprocess.run(["sh", "-c", f'python3 "{stub}" {self.wrapper}'],
                                 capture_output=True, text=True, timeout=60)
        bare = subprocess.run(["sh", "-c", f'python3 "{stub}"'],
                              capture_output=True, text=True, timeout=60)
        return wrapped.returncode, bare.returncode

    def test_exit_zero_allows_and_exit_two_blocks(self):
        self.assertEqual(self.run_hook(0), (0, 0))
        self.assertEqual(self.run_hook(2), (2, 2))

    def test_a_hook_that_exits_one_blocks_through_the_wrapper(self):
        # CodeBuddy: exit 1 is a non-blocking error. The wrapper turns it into 2, so a guard crash
        # (a traceback, a missing file) blocks instead of letting the command run.
        wrapped, bare = self.run_hook(1)
        self.assertEqual(bare, 1)
        self.assertEqual(wrapped, 2)

    def test_a_missing_interpreter_blocks_through_the_wrapper(self):
        # 127: python3 absent, or the hook path wrong. Same wrapper, same block.
        done = subprocess.run(["sh", "-c", f"definitely-not-a-real-command-9f2 {self.wrapper}"],
                              capture_output=True, text=True, timeout=60)
        self.assertEqual(done.returncode, 2, done.stderr)


class AgentsTest(unittest.TestCase):
    ROLES = {"pm": False, "qa-engineer": False, "software-engineer": True}

    def test_each_role_is_named_and_points_at_its_team_file(self):
        for role, edits in self.ROLES.items():
            path = LAYER / "agents" / f"{role}.md"
            with self.subTest(role=role):
                fields = front_matter(path)
                self.assertEqual(fields["name"], role)
                self.assertTrue(fields["description"])
                self.assertNotIn("\n", fields["description"])
                self.assertIn(f"_docs/agent-kit/team/{role}.md", path.read_text(encoding="utf-8"))

    def test_tool_lists_keep_edits_from_the_pm_and_qa(self):
        for role, edits in self.ROLES.items():
            with self.subTest(role=role):
                tools = [t.strip() for t in front_matter(LAYER / "agents" / f"{role}.md")["tools"].split(",")]
                self.assertIn("Write", tools)
                self.assertEqual("Edit" in tools, edits)

    def test_the_pm_and_qa_text_limits_them_to_scratch(self):
        for role in ("pm", "qa-engineer"):
            with self.subTest(role=role):
                self.assertIn("`.scratch/`", (LAYER / "agents" / f"{role}.md").read_text(encoding="utf-8"))

    def test_the_sweep_skill_is_manual(self):
        fields = front_matter(LAYER / "skills" / "sweep" / "SKILL.md")
        self.assertEqual(fields["name"], "sweep")
        self.assertEqual(fields["disable-model-invocation"], "true")
        self.assertIn("procedures/sweep.md", (LAYER / "skills" / "sweep" / "SKILL.md").read_text(encoding="utf-8"))


class DocsTest(unittest.TestCase):
    def setUp(self):
        self.text = (LAYER / "START.md").read_text(encoding="utf-8")

    def flat(self) -> str:
        return " ".join(self.text.split())

    def test_it_adds_no_codebuddy_md(self):
        self.assertIn("It adds no `CODEBUDDY.md`", self.text)
        self.assertIn("a `CODEBUDDY.md` in the same folder shadows `AGENTS.md`", self.flat())

    def test_it_states_the_exit_codes_and_the_wrapper(self):
        text = self.flat()
        self.assertIn("**Any other non-zero exit** is a non-blocking error", text)
        self.assertIn("a guard crash (exit 1, 3, 127, ...) becomes 2 and blocks", text)
        self.assertIn("the default is 60 seconds", text)

    def test_the_parent_discovery_block_is_commented_out(self):
        for line in ('// "memory": {', '//   "parentDiscovery": false', "// }"):
            with self.subTest(line=line):
                self.assertIn(line, self.text)
        self.assertIn("Monorepos only", self.text)

    def test_it_says_where_the_protected_folder_goes(self):
        self.assertIn("'.codebuddy/*'", self.text)
        self.assertIn("PROTECTED", self.text)

    def test_it_does_not_turn_on_frontmatter_hooks(self):
        text = self.flat()
        self.assertIn("`allowUntrustedFrontmatterHooks` defaults to `false`", text)
        self.assertIn("The layer does not enable it", text)


if __name__ == "__main__":
    unittest.main()
