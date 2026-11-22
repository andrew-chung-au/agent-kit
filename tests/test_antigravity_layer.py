"""Tests for the Antigravity CLI layer.

Mirrors tests/test_codebuddy_settings.py:
- hooks.json registration, shape and keys
- agents role definitions, tool lists and scratch limitations
- payload translation into the shared git guard's input
- the decide-on-every-path rule: adapter emits a decision JSON on every path
  and never exits 0 silently
- START.md documentation checks
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
LAYER = KIT / "antigravity"
ADAPTER = LAYER / "guard_adapter.py"


def front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if match is None:
        raise AssertionError(f"{path} has no front matter")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


class HooksShapeTest(unittest.TestCase):
    def setUp(self):
        self.hooks_data = json.loads((LAYER / "hooks.json").read_text(encoding="utf-8"))

    def test_it_is_valid_json_with_hook_definitions(self):
        self.assertIsInstance(self.hooks_data, dict)
        self.assertIn("git-guard", self.hooks_data)

    def test_pre_tool_use_matcher_is_run_command(self):
        entry = self.hooks_data["git-guard"]
        self.assertIn("PreToolUse", entry)
        pre_tool = entry["PreToolUse"]
        self.assertEqual(len(pre_tool), 1)
        self.assertEqual(pre_tool[0]["matcher"], "run_command")

    def test_hook_command_names_adapter_script(self):
        handlers = self.hooks_data["git-guard"]["PreToolUse"][0]["hooks"]
        self.assertEqual(len(handlers), 1)
        command = handlers[0]["command"]
        self.assertTrue(command.startswith("python3 "), command)
        self.assertIn("antigravity/guard_adapter.py", command)

    def test_the_adapter_script_exists_in_the_kit(self):
        self.assertTrue(ADAPTER.is_file())


class AdapterSubprocessTest(unittest.TestCase):
    """Execute guard_adapter.py in a subprocess with various inputs."""

    def run_adapter(self, raw_input: str) -> tuple[int, dict, str]:
        proc = subprocess.run(
            [sys.executable, "-B", str(ADAPTER)],
            input=raw_input,
            text=True,
            capture_output=True,
            timeout=15,
            cwd=REPO,
        )
        self.assertNotEqual(proc.stdout.strip(), "", "adapter must never produce empty stdout")
        try:
            data = json.loads(proc.stdout)
        except Exception as exc:
            self.fail(f"adapter output is not valid JSON: {proc.stdout!r} ({exc})")
        self.assertIn("decision", data, f"missing 'decision' key in {data}")
        self.assertIn(data["decision"], ("allow", "deny"))
        return proc.returncode, data, proc.stderr

    def make_payload(self, tool_name: str, command: str | None = None, event: str = "PreToolUse") -> str:
        args = {}
        if command is not None:
            args["CommandLine"] = command
        return json.dumps({
            "hookEventName": event,
            "cwd": str(REPO),
            "toolCall": {
                "id": "call_12345",
                "name": tool_name,
                "args": args,
            },
        })

    def test_safe_command_is_allowed(self):
        code, data, _ = self.run_adapter(self.make_payload("run_command", "git status"))
        self.assertEqual(code, 0)
        self.assertEqual(data["decision"], "allow")

    def test_safe_make_test_is_allowed(self):
        code, data, _ = self.run_adapter(self.make_payload("run_command", "make test"))
        self.assertEqual(code, 0)
        self.assertEqual(data["decision"], "allow")

    def test_git_push_is_denied(self):
        code, data, _ = self.run_adapter(self.make_payload("run_command", "git push origin main"))
        self.assertEqual(code, 0)
        self.assertEqual(data["decision"], "deny")
        self.assertIn("push", data.get("reason", "").lower())

    def test_broad_staging_git_add_dot_is_denied(self):
        code, data, _ = self.run_adapter(self.make_payload("run_command", "git add ."))
        self.assertEqual(code, 0)
        self.assertEqual(data["decision"], "deny")
        self.assertIn("explicit paths", data.get("reason", "").lower())

    def test_commit_all_flag_is_denied(self):
        code, data, _ = self.run_adapter(self.make_payload("run_command", "git commit -a -m 'wip'"))
        self.assertEqual(code, 0)
        self.assertEqual(data["decision"], "deny")
        self.assertIn("commit -a", data.get("reason", "").lower())

    def test_no_verify_is_denied(self):
        code, data, _ = self.run_adapter(self.make_payload("run_command", "git commit --no-verify -m 'msg'"))
        self.assertEqual(code, 0)
        self.assertEqual(data["decision"], "deny")
        self.assertIn("no-verify", data.get("reason", "").lower())

    def test_env_file_command_is_denied(self):
        code, data, _ = self.run_adapter(self.make_payload("run_command", "cat .env"))
        self.assertEqual(code, 0)
        self.assertEqual(data["decision"], "deny")
        self.assertIn(".env", data.get("reason", "").lower())

    def test_non_run_command_tool_is_allowed(self):
        code, data, _ = self.run_adapter(self.make_payload("view_file", "AGENTS.md"))
        self.assertEqual(code, 0)
        self.assertEqual(data["decision"], "allow")

    def test_non_pre_tool_use_event_is_allowed(self):
        payload = json.dumps({"hookEventName": "SessionStart", "cwd": str(REPO)})
        code, data, _ = self.run_adapter(payload)
        self.assertEqual(code, 0)
        self.assertEqual(data["decision"], "allow")

    def test_empty_input_fails_closed_with_deny(self):
        code, data, _ = self.run_adapter("")
        self.assertEqual(code, 0)
        self.assertEqual(data["decision"], "deny")

    def test_whitespace_input_fails_closed_with_deny(self):
        code, data, _ = self.run_adapter("   \n\t  ")
        self.assertEqual(code, 0)
        self.assertEqual(data["decision"], "deny")

    def test_malformed_json_fails_closed_with_deny(self):
        code, data, _ = self.run_adapter("{not valid json")
        self.assertEqual(code, 0)
        self.assertEqual(data["decision"], "deny")

    def test_json_list_fails_closed_with_deny(self):
        code, data, _ = self.run_adapter("[1, 2, 3]")
        self.assertEqual(code, 0)
        self.assertEqual(data["decision"], "deny")

    def test_missing_tool_call_fails_closed_with_deny(self):
        code, data, _ = self.run_adapter(json.dumps({"hookEventName": "PreToolUse"}))
        self.assertEqual(code, 0)
        self.assertEqual(data["decision"], "deny")

    def test_missing_args_fails_closed_with_deny(self):
        code, data, _ = self.run_adapter(json.dumps({
            "hookEventName": "PreToolUse",
            "toolCall": {"name": "run_command"},
        }))
        self.assertEqual(code, 0)
        self.assertEqual(data["decision"], "deny")

    def test_non_string_commandline_fails_closed_with_deny(self):
        code, data, _ = self.run_adapter(json.dumps({
            "hookEventName": "PreToolUse",
            "toolCall": {"name": "run_command", "args": {"CommandLine": 12345}},
        }))
        self.assertEqual(code, 0)
        self.assertEqual(data["decision"], "deny")


class AgentsTest(unittest.TestCase):
    ROLES = {"pm": False, "qa-engineer": False, "software-engineer": True}

    def test_each_role_is_named_and_points_at_its_team_file(self):
        for role, can_edit in self.ROLES.items():
            path = LAYER / "agents" / f"{role}.md"
            with self.subTest(role=role):
                fields = front_matter(path)
                self.assertEqual(fields["name"], role)
                self.assertTrue(fields["description"])
                self.assertNotIn("\n", fields["description"])
                self.assertIn(f"_docs/agent-kit/team/{role}.md", path.read_text(encoding="utf-8"))

    def test_tool_lists_use_antigravity_names_and_keep_edits_from_pm_and_qa(self):
        for role, can_edit in self.ROLES.items():
            with self.subTest(role=role):
                fields = front_matter(LAYER / "agents" / f"{role}.md")
                tools = [t.strip() for t in fields["tools"].split(",")]
                self.assertIn("view_file", tools)
                self.assertIn("grep_search", tools)
                self.assertIn("write_file", tools)
                self.assertIn("run_command", tools)
                self.assertEqual("replace_file_content" in tools, can_edit)

    def test_pm_and_qa_text_limits_them_to_scratch(self):
        for role in ("pm", "qa-engineer"):
            with self.subTest(role=role):
                self.assertIn("`.scratch/`", (LAYER / "agents" / f"{role}.md").read_text(encoding="utf-8"))


class DocsTest(unittest.TestCase):
    def setUp(self):
        self.text = (LAYER / "START.md").read_text(encoding="utf-8")

    def flat(self) -> str:
        return " ".join(self.text.split())

    def test_it_mentions_no_rules_pointer_file_or_copy(self):
        self.assertIn("It adds no separate rules copy or pointer file", self.text)

    def test_it_explains_global_permissions_cannot_ship_in_repo(self):
        text = self.flat()
        self.assertIn("~/.gemini/antigravity-cli/settings.json", self.text)
        self.assertIn("permissions cannot ship in the repository and cannot be byte-compared", text)

    def test_it_explains_why_sweep_skill_is_omitted(self):
        text = self.flat()
        self.assertIn("No sweep skill", text)
        self.assertIn("model-invocable", text)
        self.assertIn("breaking the kit's sweep rule", text)

    def test_it_states_hook_failure_behaviour(self):
        text = self.flat()
        self.assertIn("Exit 1 blocks", text)
        self.assertIn("Timeout blocks", text)
        self.assertIn("Malformed JSON blocks", text)
        self.assertIn("Exit 0 with no output ALLOWS", text)
        self.assertIn("never exits 0 silently", text)

    def test_it_mentions_dangerously_skip_permissions_and_headless_exit_code(self):
        text = self.flat()
        self.assertIn("`--dangerously-skip-permissions` does not bypass hooks", text)
        self.assertIn("Headless mode soft-denies", text)
        self.assertIn("relying on the process exit code as a verdict", text)

    def test_it_says_where_the_protected_folder_goes(self):
        self.assertIn("'.agents/*'", self.text)
        self.assertIn("PROTECTED", self.text)


if __name__ == "__main__":
    unittest.main()
