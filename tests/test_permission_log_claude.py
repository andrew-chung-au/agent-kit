"""The Claude Code permission logger (issue #36): agent-kit/claude-code/hooks/log_permission.py.

Every case runs the real hook as a process, as Claude Code does (payload on stdin,
CLAUDE_PROJECT_DIR set), in a throwaway project under .scratch/. No live Claude Code is used.
The payloads follow the PermissionRequest input in the hooks reference: session_id,
hook_event_name, tool_name, tool_input, permission_suggestions.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

from kit_repo import new_workdir
from secret_fixtures import MATCH, NON_MATCH

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
HOOK = KIT / "claude-code" / "hooks" / "log_permission.py"
FIELDS = {"event", "tool", "time", "sessionID", "id", "type", "pattern", "response", "source"}
ISO_UTC = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z")
CAP = 1048576


def ask(tool="Bash", tool_input=None, session="ses-1", **extra):
    payload = {"session_id": session, "transcript_path": "/x/t.jsonl", "cwd": "/x", "permission_mode": "default",
               "hook_event_name": "PermissionRequest", "tool_name": tool,
               "tool_input": {"command": "git status"} if tool_input is None else tool_input,
               "permission_suggestions": []}
    payload.update(extra)
    return json.dumps(payload)


class HookCase(unittest.TestCase):
    def setUp(self):
        self.work = new_workdir(prefix="perm-claude-")
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.project = self.work / "project"
        self.project.mkdir()

    @property
    def folder(self) -> Path:
        return self.project / ".agent-kit" / "logs" / "permissions"

    def run_hook(self, stdin, hook=HOOK, project=None, env_project=True):
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        if env_project:
            env["CLAUDE_PROJECT_DIR"] = str(project or self.project)
        data = stdin if isinstance(stdin, bytes) else stdin.encode("utf-8")
        return subprocess.run([sys.executable, "-B", str(hook)], input=data, cwd=str(project or self.project),
                              env=env, capture_output=True, timeout=60)

    def files(self):
        return sorted(self.folder.glob("*.jsonl")) if self.folder.exists() else []

    def records(self):
        out = []
        for path in self.files():
            out += [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        return out

    def today_file(self) -> Path:
        return self.folder / (datetime.now(timezone.utc).strftime("%Y-%m-%d") + ".jsonl")

    def logged_once(self, stdin) -> dict:
        done = self.run_hook(stdin)
        self.assertEqual((done.returncode, done.stdout), (0, b""), done.stderr)
        records = self.records()
        self.assertEqual(len(records), 1, records)
        return records[0]


class AskRecordTest(HookCase):
    def test_a_permission_request_becomes_one_ask_record_with_the_documented_shape(self):
        record = self.logged_once(ask("Bash", {"command": "git push origin main", "description": "Push"}))
        self.assertEqual(record["event"], "ask")
        self.assertEqual(record["tool"], "claude-code")
        self.assertEqual(record["sessionID"], "ses-1")
        self.assertEqual(record["type"], "bash")
        self.assertEqual(record["pattern"], "git push origin main")
        self.assertEqual(record["source"], "PermissionRequest")
        self.assertRegex(record["time"], ISO_UTC)
        self.assertLessEqual(set(record), FIELDS)
        self.assertNotIn("id", record)  # the event carries no per-call id
        self.assertNotIn("response", record)  # nor an outcome: no reply record is ever written
        self.assertEqual(self.files(), [self.today_file()])
        self.assertTrue(self.today_file().read_text(encoding="utf-8").endswith("}\n"))

    def test_the_pattern_comes_from_the_one_field_per_tool_and_nothing_else(self):
        cases = [("Read", {"file_path": "/a/b.txt"}, "read", "/a/b.txt"),
                 ("Edit", {"file_path": "/a/c.py", "old_string": "OLD-TEXT", "new_string": "NEW-TEXT"}, "edit", "/a/c.py"),
                 ("Write", {"file_path": "/a/d.py", "content": "FILE-CONTENTS"}, "write", "/a/d.py"),
                 ("WebFetch", {"url": "https://example.invalid/x", "prompt": "SUMMARISE-THIS"}, "webfetch",
                  "https://example.invalid/x"),
                 ("mcp__memory__store", {"text": "PRIVATE-NOTE"}, "mcp__memory__store", ""),
                 ("Grep", {"pattern": "SEARCH-TERM", "path": "/a"}, "grep", "")]
        for tool, tool_input, kind, pattern in cases:
            with self.subTest(tool=tool):
                shutil.rmtree(self.project / ".agent-kit", ignore_errors=True)
                record = self.logged_once(ask(tool, tool_input))
                self.assertEqual((record["type"], record["pattern"]), (kind, pattern))
                line = self.today_file().read_text(encoding="utf-8")
                for hidden in ("OLD-TEXT", "NEW-TEXT", "FILE-CONTENTS", "SUMMARISE-THIS", "PRIVATE-NOTE", "SEARCH-TERM",
                               "/x/t.jsonl", "permission_suggestions"):
                    self.assertNotIn(hidden, line)

    def test_a_multi_line_command_logs_its_first_line_only(self):
        record = self.logged_once(ask("Bash", {"command": "cat > f.txt <<'EOF'\nBODY-OF-THE-FILE\nEOF"}))
        self.assertEqual(record["pattern"], "cat > f.txt <<'EOF'")
        self.assertNotIn("BODY-OF-THE-FILE", self.today_file().read_text(encoding="utf-8"))

    def test_a_long_pattern_is_cut_to_200_characters_ending_in_three_dots(self):
        record = self.logged_once(ask("Bash", {"command": "echo " + "a" * 500}))
        self.assertEqual(len(record["pattern"]), 200)
        self.assertTrue(record["pattern"].endswith("..."))

    def test_a_200_character_pattern_is_not_cut(self):
        record = self.logged_once(ask("Bash", {"command": "a" * 200}))
        self.assertEqual(record["pattern"], "a" * 200)

    def test_control_characters_in_a_pattern_become_spaces(self):
        record = self.logged_once(ask("Bash", {"command": "echo \x1b[31mred\x00\x07 \u2028x"}))
        self.assertNotRegex(record["pattern"], r"[\x00-\x1f\x7f\u2028]")

    def test_the_session_id_and_tool_name_are_cut_not_trusted(self):
        record = self.logged_once(ask("B" * 500, session="s" * 500))
        self.assertEqual((len(record["type"]), len(record["sessionID"])), (200, 200))


class RedactionTest(HookCase):
    def test_no_secret_shape_from_the_shared_fixture_list_is_written(self):
        for name, text, _, secret in MATCH:
            with self.subTest(name=name):
                shutil.rmtree(self.project / ".agent-kit", ignore_errors=True)
                done = self.run_hook(ask("Bash", {"command": "curl -H '%s' https://example.invalid/%s" % (text, "x")}))
                self.assertEqual((done.returncode, done.stdout), (0, b""))
                written = self.today_file().read_text(encoding="utf-8")
                self.assertIn("[redacted]", written)
                self.assertNotIn(secret, written)
                self.assertNotIn(text, written)

    def test_an_api_key_a_bearer_token_and_a_dotenv_path_are_all_removed(self):
        key = "sk-" + "A1b2C3d4E5f6G7h8I9j0"
        bearer = "abcdefghij" + "0123456789"
        command = "curl -H 'Authorization: Bearer %s' -d key=%s --data @.env.production https://example.invalid" % (bearer, key)
        record = self.logged_once(ask("Bash", {"command": command}))
        for secret in (key, bearer, ".env.production", "Bearer"):
            self.assertNotIn(secret, json.dumps(record))
        self.assertIn("[redacted]", record["pattern"])

    def test_a_dotenv_file_path_for_a_file_tool_is_removed_too(self):
        record = self.logged_once(ask("Read", {"file_path": "/app/config/.env.local"}))
        self.assertNotIn(".env", record["pattern"])

    def test_values_that_are_not_secrets_are_left_alone(self):
        for name, text in NON_MATCH:
            with self.subTest(name=name):
                shutil.rmtree(self.project / ".agent-kit", ignore_errors=True)
                record = self.logged_once(ask("Bash", {"command": "run " + text + " now"}))
                self.assertEqual(record["pattern"], "run " + text + " now")

    def test_redaction_comes_before_the_cut(self):
        secret = MATCH[1][1]
        record = self.logged_once(ask("Bash", {"command": "x" * 190 + secret}))
        self.assertNotIn(secret[:12], record["pattern"])
        self.assertEqual(len(record["pattern"]), 200)

    def test_unreadable_patterns_log_a_marker_instead_of_the_pattern(self):
        for name, body in (("missing", None), ("empty", ""), ("matches everything", "a*\n"), ("bad regex", "(\n")):
            with self.subTest(name=name):
                shutil.rmtree(self.project / ".agent-kit", ignore_errors=True)
                kit = self.work / ("kit-" + name.replace(" ", "-"))
                (kit / "claude-code" / "hooks").mkdir(parents=True)
                shutil.copytree(KIT / "scripts", kit / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
                hook = kit / "claude-code" / "hooks" / "log_permission.py"
                shutil.copyfile(HOOK, hook)
                patterns = kit / "scripts" / "secret-patterns.txt"
                if body is None:
                    patterns.unlink()
                else:
                    patterns.write_text(body, encoding="utf-8")
                secret = "ghp_" + "A1b2" * 9
                done = self.run_hook(ask("Bash", {"command": "echo " + secret}), hook=hook)
                self.assertEqual((done.returncode, done.stdout), (0, b""))
                self.assertEqual([r["pattern"] for r in self.records()], ["[redacted: no patterns]"])
                self.assertNotIn(secret, self.today_file().read_text(encoding="utf-8"))

    def test_the_hook_keeps_no_second_copy_of_the_patterns(self):
        source = HOOK.read_text(encoding="utf-8") + (KIT / "scripts" / "permission_log_lib.py").read_text(encoding="utf-8")
        for line in (KIT / "scripts" / "secret-patterns.txt").read_text(encoding="utf-8").split("\n"):
            if line:
                self.assertNotIn(line, source)
        for fragment in ("ghp_", "github_pat_", "AKIA", "PRIVATE KEY", "Bearer", "xox"):
            self.assertNotIn(fragment, source)
        self.assertIn("secret-patterns.txt", source)


class ObserveOnlyTest(HookCase):
    """Exit 0 and nothing on stdout, whatever arrives. Anything unrecognised is an unknown record."""

    def assert_observe_only(self, stdin, source):
        shutil.rmtree(self.project / ".agent-kit", ignore_errors=True)
        done = self.run_hook(stdin)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(done.stdout, b"")
        records = self.records()
        self.assertEqual(len(records), 1, records)
        self.assertEqual((records[0]["event"], records[0]["tool"], records[0]["source"]), ("unknown", "claude-code", source))
        self.assertLessEqual(set(records[0]), FIELDS)
        return records[0]

    def test_malformed_input(self):
        for stdin in ("{not json", "{", '{"hook_event_name": "PermissionRequest"', "\x00\x01garbage", b"\xff\xfe\xfd"):
            with self.subTest(stdin=stdin):
                self.assert_observe_only(stdin, "unparsed")

    def test_an_empty_payload(self):
        for stdin in ("", "   \n", "{}", "[]", "null", "5", '"text"'):
            with self.subTest(stdin=stdin):
                self.assert_observe_only(stdin, "unparsed")

    def test_input_nested_too_deeply_to_parse(self):
        self.assert_observe_only("[" * 200000, "unparsed")

    def test_an_unknown_event_shape_keeps_the_event_name_only(self):
        payload = json.dumps({"hook_event_name": "PermissionDenied", "session_id": "ses-1", "tool_name": "Bash",
                              "tool_input": {"command": "SECRET-COMMAND-TEXT"}, "reason": "REASON-TEXT"})
        record = self.assert_observe_only(payload, "PermissionDenied")
        self.assertEqual(set(record), {"event", "tool", "time", "source"})
        self.assertNotIn("SECRET-COMMAND-TEXT", self.today_file().read_text(encoding="utf-8"))

    def test_a_permission_request_without_the_fields_that_make_an_ask_is_unknown(self):
        for name, payload in {
            "no session": {"hook_event_name": "PermissionRequest", "tool_name": "Bash", "tool_input": {"command": "ls"}},
            "no tool": {"hook_event_name": "PermissionRequest", "session_id": "s", "tool_input": {}},
            "tool is a number": {"hook_event_name": "PermissionRequest", "session_id": "s", "tool_name": 5},
            "empty session": {"hook_event_name": "PermissionRequest", "session_id": "", "tool_name": "Bash"},
        }.items():
            with self.subTest(name=name):
                self.assert_observe_only(json.dumps(payload), "PermissionRequest")

    def test_a_permission_request_with_odd_tool_input_is_still_an_ask(self):
        for tool_input in (None, "a string", ["list"], {"command": 5}, {"command": None}, {}):
            with self.subTest(tool_input=tool_input):
                shutil.rmtree(self.project / ".agent-kit", ignore_errors=True)
                payload = json.loads(ask("Bash"))
                payload["tool_input"] = tool_input
                done = self.run_hook(json.dumps(payload))
                self.assertEqual((done.returncode, done.stdout), (0, b""))
                self.assertEqual([(r["event"], r["pattern"]) for r in self.records()], [("ask", "")])

    def test_a_hook_event_name_that_is_not_text_is_unparsed(self):
        self.assert_observe_only(json.dumps({"hook_event_name": {"x": 1}}), "unparsed")

    def test_a_log_problem_still_exits_zero_and_prints_nothing_on_stdout(self):
        (self.project / ".agent-kit").write_text("a file where the folder should be\n", encoding="utf-8")
        done = self.run_hook(ask())
        self.assertEqual((done.returncode, done.stdout), (0, b""))
        self.assertIn(b"not logged", done.stderr)

    def test_without_claude_project_dir_it_logs_in_the_working_folder(self):
        done = self.run_hook(ask(), env_project=False)
        self.assertEqual((done.returncode, done.stdout), (0, b""))
        self.assertEqual(len(self.records()), 1)

    def test_the_source_prints_nothing_and_never_emits_a_decision(self):
        source = HOOK.read_text(encoding="utf-8")
        for needle in ("print(", "sys.stdout", "hookSpecificOutput", "permissionDecision", '"decision"', "behavior",
                       "sys.exit(2", "return 2", "subprocess", "urllib", "socket", "os.system", "os.remove", "unlink"):
            self.assertNotIn(needle, source)
        self.assertTrue(source.rstrip().endswith("sys.exit(main())"))


class CapTest(HookCase):
    """One file per day, 1 MiB each. The first record that does not fit ends the day (issue #71)."""

    def seed(self, size: int, marked: bool = False) -> Path:
        self.folder.mkdir(parents=True, exist_ok=True)
        path = self.today_file()
        record = '{"event":"unknown","tool":"claude-code","time":"2026-01-01T00:00:00.000Z","source":"x"}\n'
        text = record * (size // len(record))
        text += "\n" * (size - len(text.encode("utf-8")))
        if marked:
            text = text[:size - 80] + '{"event":"truncated","tool":"claude-code","time":"2026-01-01T00:00:00.000Z"}\n'
        path.write_text(text, encoding="utf-8")
        self.assertEqual(path.stat().st_size, len(text.encode("utf-8")))
        return path

    def run_and_size(self, stdin=None):
        done = self.run_hook(stdin or ask())
        self.assertEqual((done.returncode, done.stdout), (0, b""), done.stderr)
        return self.today_file().stat().st_size

    def markers(self, path: Path) -> int:
        return path.read_text(encoding="utf-8").count('"event":"truncated"')

    def test_a_record_that_fits_is_appended(self):
        path = self.seed(CAP - 5000)
        before = path.stat().st_size
        self.assertGreater(self.run_and_size(), before)
        self.assertEqual(self.markers(path), 0)

    def test_the_first_record_that_does_not_fit_writes_one_truncated_record(self):
        path = self.seed(CAP - 100)
        self.run_and_size()
        lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(self.markers(path), 1)
        last = json.loads(lines[-1])
        self.assertEqual((last["event"], last["tool"]), ("truncated", "claude-code"))
        self.assertEqual(set(last), {"event", "tool", "time"})
        self.assertFalse(any('"event":"ask"' in line for line in lines))

    def test_nothing_is_appended_after_the_marker_not_even_a_smaller_record_in_a_new_process(self):
        path = self.seed(CAP - 100)
        self.run_and_size()
        frozen = path.read_bytes()
        for _ in range(3):
            self.run_and_size(ask("Read", {"file_path": "/a"}))
            self.run_and_size("{bad json")
        self.assertEqual(path.read_bytes(), frozen)
        self.assertEqual(self.markers(path), 1)

    def one_record_size(self) -> int:
        """Bytes one ask record takes for the fixed payload (the time field has a fixed width)."""
        self.run_and_size()
        size = self.today_file().stat().st_size
        self.today_file().unlink()
        return size

    def test_the_cap_boundary_a_record_that_exactly_fits_is_appended_and_one_byte_over_is_not(self):
        line = self.one_record_size()
        path = self.seed(CAP - line)
        self.assertEqual(self.run_and_size(), CAP)
        self.assertEqual(self.markers(path), 0)
        self.assertIn('"event":"ask"', path.read_text(encoding="utf-8").splitlines()[-1])
        path = self.seed(CAP - line + 1)
        self.run_and_size()
        last = json.loads(path.read_text(encoding="utf-8").splitlines()[-1])
        self.assertEqual((last["event"], self.markers(path)), ("truncated", 1))
        self.assertFalse(any('"event":"ask"' in x for x in path.read_text(encoding="utf-8").splitlines()))

    def test_a_new_log_file_is_created_with_mode_0600(self):
        self.assertEqual(self.run_hook(ask()).returncode, 0)
        self.assertEqual(stat.S_IMODE(self.today_file().stat().st_mode), 0o600)

    def test_a_marker_far_from_the_cap_still_stops_appending(self):
        # The file is well under the cap, so the small record would fit: only the marker stops it.
        for size in (CAP - 50, CAP - 3000, CAP - 5000, CAP - 100000):
            with self.subTest(size=size):
                path = self.seed(size, marked=True)
                frozen = path.read_bytes()
                self.run_and_size()
                self.assertEqual(path.read_bytes(), frozen)

    def test_the_marker_check_comes_before_the_normal_append_in_the_source(self):
        body = HOOK.read_text(encoding="utf-8")
        body = body[body.index("def append("):body.index("def main(")]
        self.assertLess(body.index("has_marker(path)"), body.index("write(path, line)"))
        self.assertLess(body.index("write(path, line)"), body.index('"event": "truncated"'))
        self.assertEqual(body.count("write(path,"), 2)
        self.assertIn("CAP = 1048576", HOOK.read_text(encoding="utf-8"))


class SymlinkTest(HookCase):
    """The logger writes nothing through a symlink (issue #85): not the folder, an ancestor or the file."""

    def setUp(self):
        super().setUp()
        self.outside = self.work / "outside"
        self.outside.mkdir()

    def assert_refused(self, expect_outside=()):
        done = self.run_hook(ask())
        self.assertEqual((done.returncode, done.stdout, done.stderr), (0, b"", b""))
        self.assertEqual(sorted(p.name for p in self.outside.rglob("*")), sorted(expect_outside))
        return done

    def test_case_1_a_symlinked_log_folder_writes_nothing_through_it(self):
        (self.project / ".agent-kit" / "logs").mkdir(parents=True)
        self.folder.symlink_to(self.outside, target_is_directory=True)
        self.assert_refused()

    def test_case_2a_a_symlinked_agent_kit_folder_writes_nothing_through_it(self):
        (self.project / ".agent-kit").symlink_to(self.outside, target_is_directory=True)
        self.assert_refused()

    def test_case_2b_a_symlinked_logs_folder_writes_nothing_through_it(self):
        (self.project / ".agent-kit").mkdir()
        (self.project / ".agent-kit" / "logs").symlink_to(self.outside, target_is_directory=True)
        self.assert_refused()

    def test_case_3a_a_file_symlink_to_an_existing_file_appends_nothing(self):
        self.folder.mkdir(parents=True)
        target = self.outside / "target.jsonl"
        target.write_text("keep\n", encoding="utf-8")
        self.today_file().symlink_to(target)
        self.assert_refused(expect_outside=["target.jsonl"])
        self.assertEqual(target.read_text(encoding="utf-8"), "keep\n")

    def test_case_3b_a_file_symlink_to_a_missing_target_does_not_create_it(self):
        self.folder.mkdir(parents=True)
        target = self.outside / "missing.jsonl"
        self.today_file().symlink_to(target)
        self.assert_refused()
        self.assertFalse(target.exists())

    def test_case_4_a_dangling_folder_symlink_is_not_created_through(self):
        (self.project / ".agent-kit" / "logs").mkdir(parents=True)
        target = self.outside / "missing"
        self.folder.symlink_to(target, target_is_directory=True)
        self.assert_refused()
        self.assertFalse(target.exists())

    def test_a_dangling_agent_kit_symlink_is_not_created_through(self):
        target = self.outside / "missing"
        (self.project / ".agent-kit").symlink_to(target, target_is_directory=True)
        self.assert_refused()
        self.assertFalse(target.exists())

    def test_the_file_is_opened_with_no_follow(self):
        body = HOOK.read_text(encoding="utf-8")
        self.assertIn("O_NOFOLLOW", body[body.index("def write("):body.index("def append(")])

    def test_a_project_root_reached_through_a_symlink_still_logs(self):
        link = self.work / "project-link"
        link.symlink_to(self.project, target_is_directory=True)
        done = self.run_hook(ask(), project=link)
        self.assertEqual((done.returncode, done.stdout, done.stderr), (0, b"", b""))
        self.assertEqual(len(self.records()), 1)

    def test_with_no_symlinks_it_logs_as_before(self):
        self.assertEqual(self.logged_once(ask())["type"], "bash")


class ScopeTest(unittest.TestCase):
    def test_guard_git_stays_single_purpose(self):
        source = (KIT / "claude-code" / "hooks" / "guard_git.py").read_text(encoding="utf-8")
        for needle in (".agent-kit", "permissions/", "jsonl", "log_permission", "PermissionRequest", "write_text",
                       "os.open", "O_APPEND", "with open"):
            self.assertNotIn(needle, source)

    def test_the_settings_register_the_logger_for_permission_requests_only(self):
        hooks = json.loads((KIT / "claude-code" / "settings.json").read_text(encoding="utf-8"))["hooks"]
        by_event = {event: [h["command"] for group in groups for h in group["hooks"]] for event, groups in hooks.items()}
        self.assertEqual(set(by_event), {"PreToolUse", "PermissionRequest"})
        self.assertEqual(len(by_event["PermissionRequest"]), 1)
        self.assertTrue(by_event["PermissionRequest"][0].endswith("/_docs/agent-kit/claude-code/hooks/log_permission.py"))
        self.assertTrue(by_event["PreToolUse"][0].endswith("/guard_git.py"))
        self.assertEqual(len(by_event["PreToolUse"]), 1)
        self.assertNotIn("log_permission", json.dumps(hooks["PreToolUse"]))
        self.assertEqual([g.get("matcher") for g in hooks["PermissionRequest"]], [None])

    def test_the_docs_name_the_logger_the_targets_the_gap_and_the_version(self):
        def read(rel):
            return (KIT / rel).read_text(encoding="utf-8")
        start, blueprints, setup = read("claude-code/START.md"), read("blueprints.md"), read("setup.md")
        self.assertRegex(start, r"\| `hooks/log_permission\.py` \| Runs in place from the kit \|")
        self.assertIn("PermissionRequest", start)
        self.assertIn("2.1.221", start)
        self.assertRegex(start, r"complete for OpenCode and, for Claude Code, only to that extent")
        self.assertIn("no real session has run it yet", start)
        self.assertRegex(start, r"Install, step 6")
        self.assertIn("| Permission log (Claude Code) |", blueprints)
        self.assertIn("claude-code/hooks/log_permission.py", blueprints)
        self.assertIn("| `permission-report` and `permission-logs-prune` targets |", blueprints)
        self.assertIn("scripts/permission-report.py", blueprints)
        self.assertIn("scripts/permission-logs-prune.py", blueprints)
        self.assertIn("`permission-report` and `permission-logs-prune` targets", setup)
        self.assertIn("make permission-report", read("procedures/permission-log.md"))

    def test_no_kit_text_tells_agents_to_record_their_own_approvals(self):
        for path in KIT.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            for needle in ("Permission review", "permission-sweep", "Recording requests"):
                self.assertNotIn(needle, text, str(path))

    def test_the_hook_ships_where_the_settings_say(self):
        self.assertTrue(HOOK.is_file())
        self.assertTrue((KIT / "scripts" / "permission_log_lib.py").is_file())


if __name__ == "__main__":
    unittest.main()
