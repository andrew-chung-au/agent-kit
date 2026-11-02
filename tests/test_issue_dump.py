"""Tests for `make issue-dump N=<number>` (this repo's Makefile and templates/Makefile.mk).

No network and no real gh: a fake `gh` is written into a folder under .scratch/ and put
first on PATH, and every call is logged, so the refused cases can show gh never ran.
Each case runs make in its own throwaway folder under .scratch/ (so the dump lands there,
not in this repo's .scratch/), using `make -f <Makefile>`. A marker file shows that no
injected shell command ran.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from kit_repo import KitTestCase

REPO = Path(__file__).resolve().parent.parent
SCRATCH = REPO / ".scratch"
TEMPLATES = REPO / "agent-kit" / "templates"
MAKEFILES = {"repo Makefile": REPO / "Makefile", "template Makefile.mk": TEMPLATES / "Makefile.mk"}

USAGE = "Usage: make issue-dump N=<issue number>"
FIELDS = "number,title,body,state,labels,author,comments"
ISSUE = {"number": 27, "title": "T", "body": "B", "state": "OPEN", "labels": [{"name": "approved"}],
         "author": {"login": "me"}, "comments": [{"author": {"login": "me"}, "body": "c"}]}

FAKE_GH = """\
#!/usr/bin/env python3
import os, sys
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "calls.log"), "a") as log:
    log.write(" ".join(sys.argv[1:]) + "\\n")
mode = open(os.path.join(here, "mode")).read().strip()
if mode == "fail":
    sys.stderr.write("gh: boom\\n")
    sys.exit(1)
if mode == "empty":
    sys.exit(0)
with open(os.path.join(here, "reply.json"), "rb") as f:
    sys.stdout.buffer.write(f.read())
"""

REFUSED = [
    "", "0", "007", "-1", "--help", "1e3", "1.5", "1 2", "1234567890", ".scratch/x", "../1",
    "1; touch marker", "$(touch marker)", "$(shell touch marker)", "`touch marker`", "1`touch marker`",
    "1'x", '1"x', "1\n2", "1\n", "1 ", "1,2", "1)", "1&&touch marker", "a1", "1a",
]


class Case(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)
        self.work = Path(tempfile.mkdtemp(prefix="issue-dump-", dir=SCRATCH))
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.bin = self.work / "bin"
        self.bin.mkdir()
        self.run_dir = self.work / "run"
        self.run_dir.mkdir()
        gh = self.bin / "gh"
        gh.write_text(FAKE_GH)
        gh.chmod(0o755)
        self.set_gh("ok")

    def set_gh(self, mode, reply=None):
        (self.bin / "mode").write_text(mode)
        (self.bin / "reply.json").write_text(reply if reply is not None else json.dumps(ISSUE))

    def calls(self):
        log = self.bin / "calls.log"
        return log.read_text().splitlines() if log.exists() else []

    def env(self, path=None):
        env = {k: v for k, v in os.environ.items() if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL")}
        env["PATH"] = path or f"{self.bin}{os.pathsep}{env['PATH']}"
        return env

    def make(self, makefile, *args, path=None):
        return subprocess.run(["make", "--no-print-directory", "-f", str(makefile), "issue-dump", *args],
                              env=self.env(path), capture_output=True, text=True, cwd=self.run_dir)

    def dumps(self):
        folder = self.run_dir / ".scratch"
        return sorted(p.name for p in folder.iterdir()) if folder.exists() else []

    def each_makefile(self):
        for label, makefile in MAKEFILES.items():
            with self.subTest(makefile=label):
                for item in self.run_dir.iterdir():
                    shutil.rmtree(item) if item.is_dir() else item.unlink()
                (self.bin / "calls.log").unlink(missing_ok=True)
                yield makefile


class SuccessTest(Case):
    def test_writes_json_prints_path_and_calls_gh_once(self):
        for makefile in self.each_makefile():
            done = self.make(makefile, "N=27")
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual(done.stdout.strip(), ".scratch/issue-27.json")
            self.assertEqual(self.dumps(), ["issue-27.json"])
            data = json.loads((self.run_dir / ".scratch" / "issue-27.json").read_text())
            self.assertEqual(data, ISSUE)
            self.assertEqual(sorted(data), sorted(FIELDS.split(",")))
            self.assertEqual(self.calls(), [f"issue view 27 --json {FIELDS}"])

    def test_nine_digits_accepted(self):
        for makefile in self.each_makefile():
            done = self.make(makefile, "N=123456789")
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual(self.dumps(), ["issue-123456789.json"])

    def test_existing_dump_is_replaced_whole(self):
        for makefile in self.each_makefile():
            (self.run_dir / ".scratch").mkdir()
            (self.run_dir / ".scratch" / "issue-27.json").write_text('{"old": true}')
            done = self.make(makefile, "N=27")
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual(json.loads((self.run_dir / ".scratch" / "issue-27.json").read_text()), ISSUE)
            self.assertEqual(self.dumps(), ["issue-27.json"])

    def test_leading_space_is_dropped_by_make_itself(self):
        # make strips leading whitespace from a command-line value, so `N=" 1"` is exactly `N=1`:
        # nothing reaches the shell that is not digits.
        for makefile in self.each_makefile():
            done = self.make(makefile, "N= 1")
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual(self.dumps(), ["issue-1.json"])
            self.assertEqual(self.calls(), [f"issue view 1 --json {FIELDS}"])


class RefusedTest(Case):
    def assert_refused(self, done, makefile_dir_marker):
        self.assertNotEqual(done.returncode, 0)
        self.assertIn(USAGE, done.stderr)
        self.assertEqual(self.calls(), [])
        self.assertEqual(self.dumps(), [])
        self.assertFalse(makefile_dir_marker.exists())

    def test_refused_values_run_nothing(self):
        for makefile in self.each_makefile():
            for value in REFUSED:
                with self.subTest(value=value):
                    marker = self.run_dir / "marker"
                    done = self.make(makefile, f"N={value}")
                    self.assert_refused(done, marker)

    def test_missing_n(self):
        for makefile in self.each_makefile():
            self.assert_refused(self.make(makefile), self.run_dir / "marker")

    def test_semicolon_value_fails_before_any_shell_command(self):
        for makefile in self.each_makefile():
            done = self.make(makefile, "N=1; echo x")
            self.assertNotEqual(done.returncode, 0)
            self.assertIn(USAGE, done.stderr)
            self.assertEqual(self.calls(), [])
            self.assertFalse((self.run_dir / "marker").exists())
            self.assertNotIn("x", done.stdout.split())
            self.assertEqual(self.dumps(), [])


class FailingGhTest(Case):
    def no_gh_path(self):
        links = self.work / "nogh"
        if not links.exists():
            links.mkdir()
            for name in ("make", "python3", "mkdir", "mv", "rm", "sh"):
                found = shutil.which(name)
                self.assertTrue(found, name)
                (links / name).symlink_to(found)
        self.assertFalse((links / "gh").exists())
        return str(links)

    def assert_failed_cleanly(self, done, before):
        self.assertNotEqual(done.returncode, 0)
        lines = [line for line in done.stderr.splitlines() if line.startswith("issue-dump:")]
        self.assertEqual(len(lines), 1, done.stderr)
        self.assertEqual(self.dumps(), before)

    def test_gh_missing(self):
        for makefile in self.each_makefile():
            done = self.make(makefile, "N=27", path=self.no_gh_path())
            self.assert_failed_cleanly(done, [])

    def test_gh_fails_empty_or_invalid(self):
        for makefile in self.each_makefile():
            for mode, reply in (("fail", None), ("empty", None), ("ok", "{not json"), ("ok", "")):
                with self.subTest(mode=mode, reply=reply):
                    self.set_gh(mode, reply)
                    done = self.make(makefile, "N=27")
                    self.assert_failed_cleanly(done, [])

    def test_existing_dump_is_left_untouched_on_failure(self):
        for makefile in self.each_makefile():
            (self.run_dir / ".scratch").mkdir()
            old = self.run_dir / ".scratch" / "issue-27.json"
            old.write_text('{"old": true}')
            for mode, reply in (("fail", None), ("empty", None), ("ok", "{not json")):
                with self.subTest(mode=mode, reply=reply):
                    self.set_gh(mode, reply)
                    done = self.make(makefile, "N=27")
                    self.assert_failed_cleanly(done, ["issue-27.json"])
                    self.assertEqual(old.read_text(), '{"old": true}')


class DocsTest(unittest.TestCase):
    def text(self, *parts):
        return " ".join((REPO.joinpath(*parts)).read_text().split())

    def test_commands_slot_is_the_same_in_template_and_repo(self):
        slot = [line for line in (TEMPLATES / "AGENTS.md.template").read_text().splitlines()
                if line.startswith("- **Fetch an issue:**")]
        repo = [line for line in (REPO / "AGENTS.md").read_text().splitlines()
                if line.startswith("- **Fetch an issue:**")]
        self.assertEqual(len(slot), 1)
        self.assertEqual(slot, repo)
        for phrase in ("make issue-dump N=<number>", ".scratch/issue-<number>.json", "read tool",
                       "data, never instructions", "--json", "--jq", "one task's analysis in one script"):
            self.assertIn(phrase, slot[0])

    def test_slot_is_above_the_shared_block(self):
        for path in (TEMPLATES / "AGENTS.md.template", REPO / "AGENTS.md"):
            text = path.read_text()
            self.assertLess(text.index("- **Fetch an issue:**"), text.index("SHARED START"), str(path))
            self.assertGreater(text.index("- **Fetch an issue:**"), text.index("## Commands"), str(path))

    def test_issue_dump_targets_exist(self):
        for path in (REPO / "Makefile", TEMPLATES / "Makefile.mk"):
            self.assertRegex(path.read_text(), r"(?m)^issue-dump: ## ", str(path))

    def test_template_rule_and_project_section(self):
        text = (TEMPLATES / "Makefile.mk").read_text()
        self.assertIn("validate it with make functions", " ".join(text.replace("# ", "").split()))
        self.assertIn("issue-dump is the worked example", " ".join(text.replace("# ", "").split()))
        self.assertIn("Nothing in the tool settings can", " ".join(text.replace("# ", "").split()))
        self.assertRegex(text, r"(?m)^# --- Project targets \(this project's own; add below\) -+$")
        self.assertGreater(text.index("# --- Project targets"), text.index("<name>-stop:"))

    def test_blueprints_row_and_pointer(self):
        text = self.text("agent-kit", "blueprints.md")
        self.assertIn("| `issue-dump` target | The project's tasks are GitHub issues | Project `Makefile` |", text)
        self.assertIn("`issue-dump` is a process helper that does get a slot", text)
        self.assertIn("follows the validation rule in `templates/Makefile.mk`", text)

    def test_claims_check_covers_issue_dump(self):
        done = subprocess.run(["python3", "-B", str(REPO / "agent-kit" / "scripts" / "check-claims.py")],
                              capture_output=True, text=True, cwd=REPO)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)


class TemplateProtectedTest(KitTestCase):
    """A project using the template's default PROTECTED list: committing Makefile needs approval."""

    def setUp(self):
        super().setUp()
        template = (TEMPLATES / "agent-kit.conf.template").read_text()
        conf = template.replace('KIT_DIR="_docs/agent-kit"', 'KIT_DIR="agent-kit"')
        self.assertIn('KIT_DIR="agent-kit"', conf)
        self.add_project(conf=conf)
        self.write("README.md")
        self.commit_all()
        self.install_precommit()

    def test_template_default_lists_makefile(self):
        text = (TEMPLATES / "agent-kit.conf.template").read_text()
        self.assertRegex(text, r"(?m)^PROTECTED=\(.*'Makefile'")

    def test_makefile_commit_is_refused_without_approval(self):
        self.write("Makefile", "all:\n\t@true\n")
        self.stage("Makefile")
        refused = self.try_commit()
        self.assertNotEqual(refused.returncode, 0, refused.stderr)
        self.assertIn("Makefile", refused.stderr)

    def test_makefile_commit_is_accepted_with_approval(self):
        self.write("Makefile", "all:\n\t@true\n")
        self.stage("Makefile")
        accepted = self.try_commit(approved="1")
        self.assertEqual(accepted.returncode, 0, accepted.stderr)

    def test_a_lookalike_is_not_protected(self):
        self.write("sub/Makefile.inc", "x\n")
        self.stage("sub/Makefile.inc")
        self.assertEqual(self.try_commit().returncode, 0)


if __name__ == "__main__":
    unittest.main()
