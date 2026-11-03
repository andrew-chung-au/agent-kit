"""The permission log (issue #20): the OpenCode plugin source, the record format doc and the wiring.

The kit has no Node, so nothing here runs the JavaScript. The plugin is checked three ways:
- as text: size, imports, no decision change, no processes or network, the fixed paths and limits;
- through a Python model of the documented redaction, against the one fixture list
  (tests/secret_fixtures.py, created by #44) that the secret scanner also uses;
- by hand under Node in the Engineer's report, and in a real OpenCode session by the human.
The text checks say what they are: they catch a careless edit, they do not prove behaviour.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from kit_repo import KitTestCase
from secret_fixtures import MATCH, NON_MATCH

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
PLUGIN = KIT / "opencode" / "plugins" / "permission-log.js"
DOC = KIT / "procedures" / "permission-log.md"
PATTERNS = KIT / "scripts" / "secret-patterns.txt"
FIELDS = {"event", "tool", "time", "sessionID", "id", "type", "pattern", "response", "source"}
REQUIRED = {
    "ask": {"event", "tool", "time", "sessionID", "id", "type", "pattern"},
    "reply": {"event", "tool", "time", "sessionID", "id", "response"},
    "unknown": {"event", "tool", "time", "source"},
    "truncated": {"event", "tool", "time"},
}
ISO_UTC = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?Z")

# What the plugin source must not contain. Each is (regex, why).
FORBIDDEN = [
    (r"output\s*\.\s*status\s*=(?!=)", "assigns output.status (changes a decision)"),
    (r"\boutput\s*\[", "indexes output"),
    (r"child_process|\bspawn|\bexec(Sync|File)?\s*\(", "starts a process"),
    (r"\bfetch\s*\(|http|XMLHttpRequest|\bnet\b|WebSocket", "uses the network"),
    (r"\"permission\.ask\"|'permission\.ask'", "hooks permission.ask (the decision hook)"),
    (r"\bwriteFile(Sync)?\b|\brm(Sync)?\b|\bunlink|\brename|\bcopyFile|\bcreateWriteStream|\btruncate(Sync)?\s*\(", "writes or removes beyond appending the log"),
    (r"process\.exit|\.env\b|process\.env", "exits or reads the environment"),
    (r"\.(metadata|title|command|output|diff|content)\b", "reads a field that must never be logged"),
    (r"\brequire\s*\(", "uses require"),
    (r"\.\s*status\s*=(?!=)|\[\s*['\"]status['\"]\s*\]\s*=(?!=)", "assigns a status property (an aliased output.status change)"),
    (r"\bObject\s*\.\s*assign\s*\(", "uses Object.assign (can overwrite output)"),
    (r"\bglobalThis\s*\[", "reaches a global through a computed globalThis[...] access"),
    (r"\beval\s*\(|\bnew\s+Function\b|\bFunction\s*\(", "builds code at run time (eval or Function)"),
]

# The plugin's cap and cut, read from the source so a test cannot pass on a stale copy of the numbers.
CUT_LINE = re.compile(r"return out\.length > MAX_PATTERN \? out\.slice\(0, MAX_PATTERN - (\d+)\) \+ \"\.\.\.\" : out")


def const(source: str, name: str) -> int:
    return int(re.search(r"^const %s = (\d+)" % name, source, re.M).group(1))


def cut_problems(source: str, pattern: str) -> list:
    """Apply the source's own cut expression to a pattern; say what is wrong with the result."""
    found = CUT_LINE.search(source)
    if not found:
        return ["the cut line is missing or changed"]
    limit = const(source, "MAX_PATTERN")
    out = pattern if len(pattern) <= limit else pattern[:limit - int(found.group(1))] + "..."
    if len(pattern) > limit and (len(out) != 200 or not out.endswith("...")):
        return ["a long pattern is cut to %d characters, not 200 ending in ..." % len(out)]
    return []


def model_append(source: str, size: int, line: int, marked: bool, capped: bool, looked: bool):
    """The plugin's append decision, mirrored from its constants: (action, capped, looked).

    Action is "append", "drop", or "append+truncated" (the record is dropped and the marker written).
    `marked` is whether the file already ends in a truncated record; `capped` and `looked` are the
    plugin's in-memory sets for this file (empty after a restart).
    """
    cap, near = const(source, "CAP"), const(source, "NEAR")
    if not capped and size > 0 and (not looked or size > cap - near):
        looked = True
        capped = marked
    if capped:
        return "drop", capped, looked
    if size + line <= cap:
        return "append", capped, looked
    return ("drop" if marked else "append+truncated"), True, looked


def problems(source: str) -> list:
    """Why a plugin source is not acceptable (empty list: it is)."""
    found = [why for regex, why in FORBIDDEN if re.search(regex, source)]
    lines = source.count("\n")
    if lines > 150:
        found.append("longer than 150 lines")
    imports = re.findall(r"^import .* from ['\"]([^'\"]+)['\"]", source, re.M)
    if sorted(imports) != ["node:fs", "node:path"]:
        found.append("imports other than node:fs and node:path: %r" % imports)
    if len(re.findall(r"^export ", source, re.M)) != 1:
        found.append("not exactly one export (OpenCode loads every export as a plugin)")
    return found


def model_redact(patterns_text: str, value: str) -> str:
    """The documented redaction: every pattern replaced by [redacted], then cut to 200 characters."""
    for line in patterns_text.split("\n"):
        if line:
            value = re.sub(line, "[redacted]", value)
    return value if len(value) <= 200 else value[:197] + "..."


class PluginSourceTest(unittest.TestCase):
    source = PLUGIN.read_text(encoding="utf-8")

    def test_the_real_plugin_has_no_problems(self):
        self.assertEqual(problems(self.source), [])

    def test_plain_javascript_at_most_150_lines(self):
        self.assertEqual(PLUGIN.suffix, ".js")
        self.assertFalse(PLUGIN.with_suffix(".ts").exists())
        self.assertLessEqual(len(self.source.splitlines()), 150)
        self.assertNotRegex(self.source, r"(?m)^\s*(interface|type)\s+\w+|:\s*(string|number|boolean)\b|\bas const\b")

    def test_the_checker_refuses_what_it_is_meant_to_refuse(self):
        """The limit of a text check, stated once: it catches common shapes, not every way to write them.

        It is a guard against a careless edit, not a proof that the plugin is observe-only.
        """
        bad = {
            "decision change": 'event: async ({ event }) => {}, "x": 1\n output.status = "allow"',
            "decision change, spaced": "output . status = 'deny'",
            "child process": 'import cp from "node:child_process"',
            "spawn": "spawn('ls')",
            "network": "await fetch(url)",
            "network text": "const u = 'https://example.invalid'",
            "decision hook": 'return { "permission.ask": async () => {} }',
            "rewrites a file": "fs.writeFileSync(file, data)",
            "removes a file": "fs.rmSync(dir)",
            "logs the command": "const c = p.metadata.command",
            "logs a title": "const t = p.title",
            "environment": "process.env.HOME",
            "require": "const fs = require('fs')",
            "two exports": self.source + "\nexport const Second = async () => ({})",
            "too long": self.source + "\n" * 150,
            "extra import": self.source.replace('"node:path"', '"node:os"'),
        }
        for name, source in bad.items():
            with self.subTest(name=name):
                self.assertNotEqual(problems(source), [], name)

    def test_the_checker_names_each_new_refusal(self):
        cases = {
            "aliased assignment": ("event: async (o) => { o.status = 'allow' }", "assigns a status property"),
            "bracket assignment": ("o['status'] = 'deny'", "assigns a status property"),
            "Object.assign": ("Object.assign(output, { status: 'allow' })", "uses Object.assign"),
            "string-built global": ("globalThis['fe' + 'tch'](url)", "computed globalThis[...]"),
            "any computed global": ("const f = globalThis[name]", "computed globalThis[...]"),
            "eval": ("eval(code)", "builds code at run time"),
            "new Function": ("const f = new Function('return 1')", "builds code at run time"),
        }
        for name, (snippet, why) in cases.items():
            with self.subTest(name=name):
                found = problems(self.source + "\n" + snippet)
                self.assertTrue(any(why in w for w in found), (name, found))
        self.assertEqual(problems(self.source), [])

    def test_the_checker_accepts_a_comparison_with_status(self):
        self.assertEqual([w for w in problems(self.source + "\nif (output.status === 1) {}") if "decision" in w], [])

    def test_only_the_event_hook_is_returned_and_it_runs_inside_try_catch(self):
        self.assertEqual(len(re.findall(r"\bevent: async \(\{ event \}\) =>", self.source)), 1)
        handler = self.source[self.source.index("event: async"):]
        self.assertIn("try {", handler)
        self.assertRegex(handler, r"} catch \(error\) {")
        self.assertIn("client.app.log", self.source)
        self.assertIn('level: "warn"', self.source)

    def test_it_appends_to_one_folder_and_nothing_else(self):
        self.assertIn('".agent-kit", "logs", "permissions"', self.source)
        self.assertIn(".jsonl", self.source)
        self.assertIn("toISOString()", self.source)
        self.assertIn("slice(0, 10)", self.source)
        calls = set(re.findall(r"\bfs\.(\w+)\(", self.source))
        self.assertEqual(calls, {"readFileSync", "statSync", "mkdirSync", "appendFileSync"})
        self.assertNotIn(".scratch", self.source)

    def test_the_limits_and_markers_are_the_documented_ones(self):
        self.assertIn("const CAP = 1048576", self.source)
        self.assertIn("const MAX_PATTERN = 200", self.source)
        self.assertIn('"[redacted]"', self.source)
        self.assertIn('"[redacted: no patterns]"', self.source)
        self.assertIn('"event":"truncated"', self.source)
        self.assertIn('event: "truncated"', self.source)
        self.assertIn('"..."', self.source)

    def test_it_knows_both_request_shapes_and_the_reply(self):
        for name in ("permission.asked", "permission.updated", "permission.replied"):
            self.assertIn(name, self.source)
        self.assertIn('event: "unknown"', self.source)
        for key in ("requestID", "permissionID", "reply", "response", "patterns", "pattern"):
            self.assertIn(key, self.source)

    def test_only_whitelisted_field_names_are_written(self):
        written = set()
        for obj in re.findall(r"return \{ (event: [^}]*) \}", self.source):
            written |= set(re.findall(r"(?:^|, )(\w+):", obj))
        self.assertTrue(written)
        self.assertLessEqual(written, FIELDS, written - FIELDS)

    def test_it_keeps_no_second_copy_of_the_patterns(self):
        for line in PATTERNS.read_text(encoding="utf-8").split("\n"):
            if line:
                self.assertNotIn(line, self.source, line)
        for fragment in ("ghp_", "github_pat_", "AKIA", "PRIVATE KEY", "Bearer", "xox"):
            self.assertNotIn(fragment, self.source, fragment)
        self.assertIn("secret-patterns.txt", self.source)
        self.assertIn("KIT_DIR", self.source)
        self.assertIn("_docs/agent-kit", self.source)
        self.assertIn("agent-kit.conf", self.source)

    def test_the_patterns_are_applied_to_the_pattern_text_only(self):
        self.assertEqual(len(re.findall(r"redact\(", self.source)), 2)  # the definition and one call
        self.assertIn("record.pattern", self.source)


class CutEffectTest(unittest.TestCase):
    """The 200-character cut, tested by what the plugin's own cut expression does."""

    source = PLUGIN.read_text(encoding="utf-8")

    def test_the_real_cut_gives_200_characters_ending_in_three_dots(self):
        self.assertEqual(cut_problems(self.source, "a" * 500), [])
        self.assertEqual(cut_problems(self.source, "a" * 200), [])

    def test_deleting_the_cut_line_fails_even_with_the_constant_kept(self):
        mutated = CUT_LINE.sub("return out", self.source)
        self.assertIn("const MAX_PATTERN = 200", mutated)
        self.assertNotEqual(cut_problems(mutated, "a" * 500), [])

    def test_changing_the_offset_fails(self):
        for offset in (2, 4, 0):
            with self.subTest(offset=offset):
                mutated = self.source.replace("MAX_PATTERN - 3", "MAX_PATTERN - %d" % offset)
                self.assertNotEqual(cut_problems(mutated, "a" * 500), [])

    def test_changing_the_limit_fails(self):
        mutated = self.source.replace("const MAX_PATTERN = 200", "const MAX_PATTERN = 300")
        self.assertNotEqual(cut_problems(mutated, "a" * 500), [])


class CapBehaviourTest(unittest.TestCase):
    """Nothing is appended after the truncated marker (issue #71). A Python model of the append
    decision, driven by the source's constants, plus text checks on the order in the source."""

    source = PLUGIN.read_text(encoding="utf-8")
    cap = const(source, "CAP")
    line = 300

    def test_a_record_that_fits_and_no_marker_is_appended(self):
        self.assertEqual(model_append(self.source, 1000, self.line, False, False, False)[0], "append")
        self.assertEqual(model_append(self.source, self.cap - self.line, self.line, False, False, True)[0], "append")

    def test_the_first_record_that_does_not_fit_writes_one_marker(self):
        action, capped, _ = model_append(self.source, self.cap - 100, self.line, False, False, True)
        self.assertEqual((action, capped), ("append+truncated", True))

    def test_a_smaller_record_after_the_marker_is_dropped_in_the_same_process(self):
        _, capped, looked = model_append(self.source, self.cap - 100, self.line, False, False, True)
        action, _, _ = model_append(self.source, self.cap + 80, 100, True, capped, looked)
        self.assertEqual(action, "drop")

    def test_a_smaller_record_after_the_marker_is_dropped_after_a_restart(self):
        # Size is under the cap on purpose: the small record would fit. A restart empties both sets.
        for size in (self.cap - 50, self.cap - 3000, self.cap - 5000):
            with self.subTest(size=size):
                action, capped, _ = model_append(self.source, size, 20, True, False, False)
                self.assertEqual((action, capped), ("drop", True))

    def test_a_marker_written_by_another_process_is_seen_near_the_cap(self):
        action, _, _ = model_append(self.source, self.cap - 60, 20, True, False, True)
        self.assertEqual(action, "drop")

    def test_never_a_second_marker(self):
        action, _, _ = model_append(self.source, self.cap - 50, self.line, True, False, False)
        self.assertEqual(action, "drop")
        action, _, _ = model_append(self.source, self.cap - 50, self.line, True, True, True)
        self.assertEqual(action, "drop")

    def test_the_marker_check_comes_before_any_append_of_a_normal_record(self):
        body = self.source[self.source.index("function append("):self.source.index("export const")]
        first_check = body.index("hasMarker(file)")
        normal_append = body.index("fs.appendFileSync(file, line)")
        marker_append = body.index('fs.appendFileSync(file, JSON.stringify({ event: "truncated"')
        self.assertLess(first_check, normal_append)
        self.assertLess(body.index("if (capped.has(file)) return"), normal_append)
        self.assertLess(normal_append, marker_append)
        self.assertEqual(body.count("fs.appendFileSync("), 2)
        self.assertIn("const NEAR = ", self.source)

    def test_the_marker_is_looked_for_in_the_file_not_only_in_memory(self):
        self.assertRegex(self.source, r"const hasMarker = \(file\) => fs\.readFileSync\(file, \"utf8\"\)")
        self.assertIn('.includes(\'"event":"truncated"\')', self.source)


class RedactionModelTest(unittest.TestCase):
    """The documented redaction, modelled in Python against the shared fixture list."""

    patterns = PATTERNS.read_text(encoding="utf-8")

    def test_each_secret_fixture_is_redacted(self):
        for name, text, _, secret in MATCH:
            with self.subTest(name=name):
                out = model_redact(self.patterns, f"run {text} now")
                self.assertIn("[redacted]", out)
                self.assertNotIn(secret, out)
                self.assertNotIn(text, out)

    def test_each_non_secret_fixture_is_left_as_it_is(self):
        for name, text in NON_MATCH:
            with self.subTest(name=name):
                value = f"run {text} now"
                self.assertEqual(model_redact(self.patterns, value), value)

    def test_the_cut_is_200_characters_ending_in_three_dots(self):
        self.assertEqual(model_redact(self.patterns, "a" * 200), "a" * 200)
        for length in (201, 500):
            out = model_redact(self.patterns, "a" * length)
            self.assertEqual((len(out), out[-3:]), (200, "..."))

    def test_redaction_comes_before_the_cut(self):
        secret = MATCH[1][1]
        out = model_redact(self.patterns, "x" * 190 + secret)
        self.assertNotIn(secret[:12], out)
        self.assertEqual(len(out), 200)


class RecordFormatDocTest(unittest.TestCase):
    text = DOC.read_text(encoding="utf-8")

    def examples(self):
        return [json.loads(line) for line in self.text.splitlines() if line.startswith("{")]

    def test_every_example_line_is_valid_json_with_only_whitelisted_fields(self):
        lines = [line for line in self.text.splitlines() if line.startswith("{")]
        self.assertGreaterEqual(len(lines), 4)
        for line in lines:
            with self.subTest(line=line[:60]):
                record = json.loads(line)
                self.assertLessEqual(set(record), FIELDS, set(record) - FIELDS)

    def test_each_record_type_has_an_example_with_its_required_fields(self):
        by_type = {}
        for record in self.examples():
            by_type.setdefault(record["event"], record)
        self.assertEqual(set(by_type), set(REQUIRED))
        for kind, needed in REQUIRED.items():
            with self.subTest(kind=kind):
                self.assertGreaterEqual(set(by_type[kind]), needed)

    def test_times_are_iso_8601_utc_and_a_reply_answers_its_ask(self):
        records = self.examples()
        for record in records:
            self.assertRegex(record["time"], ISO_UTC)
        ask = next(r for r in records if r["event"] == "ask")
        reply = next(r for r in records if r["event"] == "reply")
        self.assertEqual(ask["id"], reply["id"])
        self.assertEqual(ask["sessionID"], reply["sessionID"])
        self.assertIn(reply["response"], ("once", "always", "reject"))

    def test_the_doc_states_what_the_issue_requires(self):
        for needle in (".agent-kit/logs/permissions/YYYY-MM-DD.jsonl", "UTC", "git-ignored", ".scratch/",
                       "`once` is allowed", "`always` is always", "`reject` is denied", "id of the ask",
                       "[redacted]", "200 characters", "1048576", "scripts/secret-patterns.txt",
                       "Never logged", "commands, titles, tool output, file contents, diffs",
                       "`unknown`", "`truncated`", "1.19.0", "2.2.5", "#36", "claude-code",
                       "subagent", "Hand check", "[redacted: no patterns]"):
            self.assertIn(needle, self.text)

    def test_the_doc_names_every_whitelisted_field(self):
        fields_line = next(p for p in self.text.split("\n\n") if p.startswith("**Fields**"))
        named = set(re.findall(r"`(\w+)`", fields_line))
        self.assertTrue(FIELDS <= named, FIELDS - named)

    def test_the_doc_is_about_250_words(self):
        words = len(self.text.split())
        self.assertGreaterEqual(words, 200)
        self.assertLessEqual(words, 320)

    def test_the_example_patterns_hold_no_secret_shaped_text(self):
        patterns = PATTERNS.read_text(encoding="utf-8")
        for record in self.examples():
            value = record.get("pattern", "")
            self.assertEqual(model_redact(patterns, value), value)


class WiringTest(unittest.TestCase):
    def read(self, rel):
        return (REPO / rel).read_text(encoding="utf-8")

    def test_gitignore_has_the_log_folder(self):
        self.assertIn(".agent-kit/logs/", self.read(".gitignore").split("\n"))

    def test_blueprints_names_the_doc_the_plugin_and_the_ignore_rule(self):
        text = self.read("agent-kit/blueprints.md")
        self.assertIn("procedures/permission-log.md", text)
        self.assertIn("opencode/plugins/permission-log.js", text)
        self.assertIn("scripts/secret-patterns.txt", text)
        block = text[text.index("**Ignore rules.**"):]
        block = block[:block.index("```", block.index("```") + 3)]
        self.assertIn("\n.agent-kit/logs/\n", block)

    def test_the_readme_layout_names_the_doc(self):
        text = self.read("agent-kit/README.md")
        self.assertRegex(text, r"procedures/ .*permission-log\.md")
        self.assertRegex(text, r"opencode/ .*permission log plugin")

    def test_start_md_has_the_row_the_install_step_the_check_and_the_limit(self):
        text = self.read("agent-kit/opencode/START.md")
        self.assertIn("| `plugins/permission-log.js` | `.opencode/plugins/permission-log.js` |", text)
        self.assertRegex(text, r"(?m)^5\. \*\*Permission log \(optional\):\*\* copy `opencode/plugins/permission-log\.js` into `\.opencode/plugins/`")
        self.assertIn("restart it", text)
        self.assertRegex(text, r"(?m)^6\. \*\*Check it\.\*\*")
        self.assertIn(".agent-kit/logs/permissions/<today>.jsonl", text)
        self.assertRegex(text, r"permission log is complete for OpenCode only.*#36.*1\.19\.0", )


class GitIgnoreBehaviourTest(KitTestCase):
    def test_a_log_file_does_not_appear_in_git_status(self):
        self.write(".gitignore", (REPO / ".gitignore").read_text(encoding="utf-8"))
        self.write("README.md", "x\n")
        self.write(".agent-kit/logs/permissions/2026-11-03.jsonl", '{"event":"ask"}\n')
        status = self.git("status", "--short", "--untracked-files=all").stdout
        self.assertIn("README.md", status)
        self.assertNotIn(".agent-kit", status)
        self.assertEqual(self.git("check-ignore", "-q", ".agent-kit/logs/permissions/2026-11-03.jsonl",
                                  check=False).returncode, 0)

    def test_other_files_in_agent_kit_are_not_hidden(self):
        self.write(".gitignore", (REPO / ".gitignore").read_text(encoding="utf-8"))
        self.write(".agent-kit/notes.md", "x\n")
        self.assertIn(".agent-kit/notes.md", self.git("status", "--short", "--untracked-files=all").stdout)


if __name__ == "__main__":
    unittest.main()
