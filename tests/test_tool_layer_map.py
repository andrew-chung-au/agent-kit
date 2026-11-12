"""The installed-file map covers the files the tool layers copy into projects (issue #170).

opencode/START.md and claude-code/START.md tell the human to copy some kit files as they are
(role definitions, the sweep skill, the permission-log plugin). Each has a line in
agent-kit/installed-files.txt with the rule `optional`, so `make kit-check` reports a stale copy as
`drift` and a copy the project never installed as `not installed (optional)`, not as a failure.
Files that are merged rather than copied are not on the map.

Nothing here writes outside a throwaway folder under .scratch/.
"""
from __future__ import annotations

import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
MAP_SCRIPT = KIT / "scripts" / "kit-map.py"
SCRATCH = REPO / ".scratch"

_spec = importlib.util.spec_from_file_location("kit_map", MAP_SCRIPT)
kit_map = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kit_map)

LAYERS = {"opencode": "opencode/START.md", "claude-code": "claude-code/START.md"}
MERGED = ("opencode.json", ".claude/settings.json", "CLAUDE.md")
OLD_PLUGIN = "// V1 plugin: OpenCode 2.2.5 refuses to load this one\nexport default { name: 'permission-log' }\n"


def start_rows(layer: str):
    """(kit source, install path) for each row of a START file's table that copies files as they are."""
    found = []
    for line in (KIT / LAYERS[layer]).read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.startswith("| `") or len(cells) != 3:
            continue
        installed = re.match(r"`([^`]+)`", cells[1])
        if not installed or not installed.group(1).startswith((".opencode/", ".claude/")):
            continue  # merged, run in place or placed outside a tool folder: not a copy
        for name in re.findall(r"`([^`]+)`", cells[0]):
            target = installed.group(1)
            if target.endswith("/"):
                target += name.rsplit("/", 1)[1]
            found.append((f"{layer}/{name}", target))
    return found


def scratch_dir(prefix: str) -> Path:
    SCRATCH.mkdir(exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=SCRATCH))


class MapCoversTheStartFilesTest(unittest.TestCase):
    def setUp(self):
        self.entries = {(e.source, e.install): e for e in kit_map.parse_map(KIT, REPO)}

    def test_every_file_a_start_file_says_to_copy_has_a_map_line(self):
        # The two cannot drift apart: a new row in a START table with no map line fails here.
        rows = [row for layer in LAYERS for row in start_rows(layer)]
        self.assertGreaterEqual(len(rows), 9, rows)  # 3 agents + sweep + plugin, 3 agents + sweep
        for source, install in rows:
            with self.subTest(source=source, install=install):
                self.assertIn((source, install), self.entries, "a START file copies it; the map has no line")

    def test_the_start_rows_are_the_ones_the_issue_names(self):
        rows = sorted(row for layer in LAYERS for row in start_rows(layer))
        self.assertEqual(rows, sorted([
            ("opencode/agents/pm.md", ".opencode/agents/pm.md"),
            ("opencode/agents/qa-engineer.md", ".opencode/agents/qa-engineer.md"),
            ("opencode/agents/software-engineer.md", ".opencode/agents/software-engineer.md"),
            ("opencode/skills/sweep/SKILL.md", ".opencode/skills/sweep/SKILL.md"),
            ("opencode/plugins/permission-log.js", ".opencode/plugins/permission-log.js"),
            ("claude-code/agents/pm.md", ".claude/agents/pm.md"),
            ("claude-code/agents/qa-engineer.md", ".claude/agents/qa-engineer.md"),
            ("claude-code/agents/software-engineer.md", ".claude/agents/software-engineer.md"),
            ("claude-code/skills/sweep/SKILL.md", ".claude/skills/sweep/SKILL.md"),
        ]))

    def test_every_tool_layer_map_line_is_a_start_row(self):
        rows = {row for layer in LAYERS for row in start_rows(layer)}
        for (source, install), entry in self.entries.items():
            if install.startswith((".opencode/", ".claude/")):
                with self.subTest(install=install):
                    self.assertIn((source, install), rows, "a map line no START file asks for")

    def test_tool_layer_lines_are_repo_entries_with_the_optional_rule_and_a_real_source(self):
        for (source, install), entry in self.entries.items():
            if install.startswith((".opencode/", ".claude/")):
                with self.subTest(install=install):
                    self.assertEqual((entry.kind, entry.allowed), ("repo", "optional"))
                    self.assertTrue((KIT / source).is_file(), source)

    def test_merged_files_have_no_byte_compare_line(self):
        installs = [install for _, install in self.entries]
        for path in MERGED:
            with self.subTest(path=path):
                self.assertNotIn(path, installs)
        sources = [source for source, _ in self.entries]
        for source in ("opencode/opencode.json", "claude-code/settings.json", "claude-code/CLAUDE.md.template"):
            self.assertNotIn(source, sources)

    def test_the_existing_lines_are_unchanged(self):
        # The five lines the map had before #170 are still there, with their rules.
        keep = {
            ("environments/local-sandbox/devcontainer.json", ".devcontainer/devcontainer.json"): ("repo", "none"),
            ("environments/local-sandbox/setup.sh", ".devcontainer/setup.sh"): ("repo", "prefix:git config --global user."),
            ("templates/ci-verify.yml.template", ".github/workflows/verify.yml"): ("repo", "none"),
            ("environments/local-sandbox/pre-push", "~/.agent-hooks/pre-push"): ("human-machine", "none"),
            ("environments/local-sandbox/pre-push", ".git/hooks/pre-push"): ("human-machine", "none"),
        }
        for key, (kind, allowed) in keep.items():
            with self.subTest(key=key):
                self.assertEqual((self.entries[key].kind, self.entries[key].allowed), (kind, allowed))


class ProjectScanTest(unittest.TestCase):
    """The real map and the real kit, against a throwaway project."""

    def setUp(self):
        self.project = scratch_dir("tool-layer-")
        self.addCleanup(shutil.rmtree, self.project, ignore_errors=True)

    def install(self, source, text=None):
        path = self.project / dict((s, i) for s, i in
                                   [row for layer in LAYERS for row in start_rows(layer)])[source]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text if text is not None else (KIT / source).read_text(encoding="utf-8"), encoding="utf-8")
        return path

    def lines(self):
        """The scan's lines for the tool-layer entries only."""
        reports = kit_map.scan_installed(KIT, self.project)
        return {r.install: line for r, line in zip(reports, kit_map.report_lines(reports))
                if r.install.startswith((".opencode/", ".claude/"))}

    def test_a_v1_permission_log_plugin_is_drift_not_unchanged(self):
        # The case that motivated #170: a project's old plugin against the current map.
        self.install("opencode/plugins/permission-log.js", OLD_PLUGIN)
        line = self.lines()[".opencode/plugins/permission-log.js"]
        self.assertEqual(line, "drift .opencode/plugins/permission-log.js")
        self.assertNotIn("unchanged", line)

    def test_the_current_plugin_is_unchanged(self):
        self.install("opencode/plugins/permission-log.js")
        self.assertEqual(self.lines()[".opencode/plugins/permission-log.js"],
                         "unchanged .opencode/plugins/permission-log.js")

    def test_a_plugin_that_is_not_installed_is_not_a_failure(self):
        line = self.lines()[".opencode/plugins/permission-log.js"]
        self.assertEqual(line, "not installed (optional) .opencode/plugins/permission-log.js")
        self.assertFalse(line.startswith(("drift ", "missing ")))

    def test_every_copied_file_is_unchanged_when_copied_and_drift_when_edited(self):
        rows = [row for layer in LAYERS for row in start_rows(layer)]
        for source, install in rows:
            with self.subTest(install=install):
                self.install(source)
                self.assertEqual(self.lines()[install], f"unchanged {install}")
                self.install(source, (KIT / source).read_text(encoding="utf-8") + "\nlocal edit\n")
                self.assertEqual(self.lines()[install], f"drift {install}")
                self.install(source, "")
                self.assertEqual(self.lines()[install], f"drift {install}")
                (self.project / install).unlink()
                self.assertEqual(self.lines()[install], f"not installed (optional) {install}")

    def test_the_command_line_names_drift_and_exits_one_but_not_for_a_missing_optional_file(self):
        self.install("opencode/plugins/permission-log.js", OLD_PLUGIN)
        done = subprocess.run([sys.executable, "-B", str(MAP_SCRIPT), "--installed", str(KIT), str(self.project)],
                              capture_output=True, text=True, timeout=60)
        self.assertEqual(done.returncode, 1, done.stderr)
        self.assertIn("drift .opencode/plugins/permission-log.js", done.stdout.splitlines())
        self.assertIn("not installed (optional) .claude/agents/pm.md", done.stdout.splitlines())


class OptionalRuleTest(unittest.TestCase):
    """The `optional` rule in a small map of its own: parser, report line and exit code."""

    def setUp(self):
        self.root = scratch_dir("optional-rule-")
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.kit, self.repo = self.root / "kit", self.root / "repo"
        self.kit.mkdir()
        self.repo.mkdir()
        (self.kit / "f.txt").write_text("a\nb\n", encoding="utf-8")

    def write_map(self, rule, kind="repo"):
        (self.kit / "installed-files.txt").write_text(f"f.txt | out/f.txt | {kind} | {rule}\n", encoding="utf-8")

    def run_map(self, *flags):
        return subprocess.run([sys.executable, "-B", str(MAP_SCRIPT), *flags, str(self.kit), str(self.repo)],
                              capture_output=True, text=True, timeout=60)

    def put(self, text):
        (self.repo / "out").mkdir(exist_ok=True)
        (self.repo / "out" / "f.txt").write_text(text, encoding="utf-8")

    def test_optional_is_a_known_rule(self):
        self.write_map("optional")
        entries = kit_map.parse_map(self.kit, self.repo)
        self.assertEqual([(e.install, e.allowed) for e in entries], [("out/f.txt", "optional")])
        self.assertEqual(self.run_map().stdout, "repo | f.txt | out/f.txt | optional\n")

    def test_near_misses_are_refused_like_any_unknown_rule(self):
        for rule in ("Optional", "OPTIONAL", "optional:x", "optional,none", "none,optional", "optional optional",
                     "optionally", "opt", "optional:", "prefix:", "optional|none"):
            with self.subTest(rule=rule):
                self.write_map(rule)
                done = self.run_map("--installed")
                self.assertEqual(done.returncode, 2, done.stdout)
                self.assertIn("kit-map:", done.stderr)
                self.assertEqual(done.stdout, "")

    def test_a_missing_optional_file_is_reported_and_exits_zero(self):
        self.write_map("optional")
        done = self.run_map("--installed")
        self.assertEqual((done.returncode, done.stdout), (0, "not installed (optional) out/f.txt\n"), done.stderr)

    def test_a_missing_file_without_the_rule_is_still_missing(self):
        self.write_map("none")
        done = self.run_map("--installed")
        self.assertEqual((done.returncode, done.stdout), (1, "missing out/f.txt\n"))

    def test_an_installed_optional_file_must_match_exactly(self):
        self.write_map("optional")
        self.put("a\nb\n")
        self.assertEqual(self.run_map("--installed").stdout, "unchanged out/f.txt\n")
        for text in ("a\nb\nc\n", "a\n", "", "a\nB\n"):
            with self.subTest(text=text):
                self.put(text)
                done = self.run_map("--installed")
                self.assertEqual((done.returncode, done.stdout), (1, "drift out/f.txt\n"))

    def test_optional_never_hides_a_symlinked_install_path(self):
        self.write_map("optional")
        real = self.root / "real"
        real.mkdir()
        (self.repo / "out").symlink_to(real)
        done = self.run_map("--installed")
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertIn("symlink", done.stderr)

    def test_a_human_machine_line_with_optional_is_still_only_named(self):
        self.write_map("optional", kind="human-machine")
        done = self.run_map("--installed")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("not checked here", done.stdout)


class DocsTest(unittest.TestCase):
    def flat(self, *parts):
        return " ".join(KIT.joinpath(*parts).read_text(encoding="utf-8").split())

    def test_readme_states_the_chosen_behaviour(self):
        text = self.flat("README.md")
        for phrase in ("`.opencode/plugins/permission-log.js`", "rule `optional`", "`not installed (optional)`",
                       "is not a failure", "an old copy is `drift`", "`opencode.json`, `.claude/settings.json`, `CLAUDE.md`",
                       "make kit-check` does not compare them"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_the_import_procedure_points_at_the_one_home_of_the_report_lines(self):
        # The report lines are explained once, in the README's "Installed files" (#182); the
        # procedure only points there and states the one exit-code fact an importer needs.
        text = self.flat("procedures", "kit-import.md")
        self.assertIn('`README.md`, "Installed files"', text)
        self.assertIn("`missing <path>` exits 1", text)

    def test_the_blueprints_row_points_at_the_one_home_of_the_report_lines(self):
        # The kit-check row names what the check does and links to the one explanation (#182).
        text = (KIT / "blueprints.md").read_text(encoding="utf-8")
        row = next(line for line in text.splitlines() if line.startswith("| `kit-check` target |"))
        self.assertIn('`README.md`, "Installed files"', row)
        for line_name in ("`unchanged`", "`local, ignored`", "`drift`", "`missing`"):
            self.assertNotIn(line_name, row)

    def test_kit_check_describes_the_new_line(self):
        text = self.flat("scripts", "kit-check.py")
        self.assertIn("not installed (optional) <install>", text)

    def test_the_map_file_explains_itself(self):
        text = (KIT / "installed-files.txt").read_text(encoding="utf-8")
        self.assertIn("optional (like none, and a file that is not installed is not a failure)", text)
        self.assertIn("Files that are merged rather", text)
        self.assertIn("opencode.json, .claude/settings.json, CLAUDE.md", text)


if __name__ == "__main__":
    unittest.main()
