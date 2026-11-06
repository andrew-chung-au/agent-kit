"""The GitHub wrappers take the repository from one place and refuse without a valid one.

`GITHUB_REPO="<owner>/<name>"` in agent-kit.conf is read as text (never sourced) and checked
against ^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$ before any `gh` call. With no valid value every wrapper
(issue-create, issue-comment, issue-close, issue-hash, sweep-due and the issue-dump helper)
refuses and runs no gh command. A fake `gh` records every call; these tests need it to record none.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from fake_gh_rest import FAKE_GH
from kit_repo import build_env, new_workdir

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
sys.path.insert(0, str(KIT / "scripts"))
import github_api  # noqa: E402

BAD_VALUES = [
    "", "a", "a b/c", "a/b c", " a/b", "a/b ", "owner/..", "../name", "a/../b", "a/./b", "./b", "owner/.",
    "a/b/c", "a//b", "/a/b", "a/b/", "a/b;touch x", "a/b$(touch x)", "a/b`touch x`", "a/b&c", "a/b|c", "a/b>c",
    "a/b'c", "a/b\\c", "a/b*", "a/b?x=1", "a/b#x", "a/b%2e", "<owner>/<name>", "a/b..c", "é/b", "a/日本", "-",
]
GOOD = "example-org/example.repo_1-x"


class Project(unittest.TestCase):
    """A throwaway project: the kit's scripts, an agent-kit.conf, .scratch/ and a recording fake gh."""

    def setUp(self):
        self.work = new_workdir(prefix="repo-")
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.ghdir = self.work / "gh-bin"
        self.ghdir.mkdir()
        gh = self.ghdir / "gh"
        gh.write_text(FAKE_GH, encoding="utf-8")
        gh.chmod(0o755)
        (self.ghdir / "config.json").write_text("{}", encoding="utf-8")
        self.env = build_env(self.work)
        self.env["PATH"] = f"{self.ghdir}{os.pathsep}{self.env['PATH']}"
        self.project = self.work / "project"
        (self.project / ".scratch").mkdir(parents=True)
        shutil.copytree(KIT / "scripts", self.project / "agent-kit" / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        (self.project / ".scratch" / "post.md").write_text("QA: PASS\n", encoding="utf-8")
        (self.project / ".scratch" / "new.md").write_text("Title: t\n\nbody\n", encoding="utf-8")
        (self.project / "records").mkdir()
        (self.project / "records" / "2026-10-31T0642Z-measure-pm-sweep.md").write_text("x\n")

    def conf(self, text):
        """Write agent-kit.conf; the scanner needs KIT_DIR, so it is always there, first."""
        text = text if text.startswith("KIT_DIR=") else 'KIT_DIR="agent-kit"\n' + text
        (self.project / "agent-kit.conf").write_text(text, encoding="utf-8")

    def calls(self):
        log = self.ghdir / "calls.log"
        return log.read_text(encoding="utf-8").splitlines() if log.exists() else []

    def run_cmd(self, *argv):
        return subprocess.run(list(argv), cwd=str(self.project), env=self.env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, encoding="utf-8")

    def wrappers(self):
        """(name, command, exit code of a refusal) for every wrapper that talks to GitHub."""
        s = "agent-kit/scripts/"
        return [
            ("issue-create", ["bash", s + "issue-create.sh", ".scratch/new.md"], 1),
            ("issue-comment", ["bash", s + "issue-comment.sh", "5", ".scratch/post.md"], 4),
            ("issue-close", ["bash", s + "issue-close.sh", "5"], 4),
            ("issue-close not-planned", ["bash", s + "issue-close.sh", "5", "not-planned"], 4),
            ("issue-hash", [sys.executable, "-B", s + "issue-hash.py", "5"], 1),
            ("sweep-due", [sys.executable, "-B", s + "sweep-due.py", "--dir", "records"], 1),
            ("issue-dump", [sys.executable, "-B", s + "github_api.py", "dump", "5"], 1),
        ]

    def assert_all_refuse(self, label):
        for name, command, code in self.wrappers():
            with self.subTest(case=label, wrapper=name):
                done = self.run_cmd(*command)
                self.assertEqual(done.returncode, code, done.stdout + done.stderr)
                self.assertTrue(done.stderr.strip(), "a refusal needs a reason")
                self.assertEqual(self.calls(), [], "gh was run")
                if name == "issue-hash":
                    self.assertEqual(done.stdout.splitlines()[:1], ["Body sha256: unknown"])
                    self.assertEqual(len(done.stdout.splitlines()), 5)
                elif name == "sweep-due":
                    self.assertEqual(done.stdout, "unknown: could not read issues\n")
                else:
                    self.assertEqual(done.stdout, "")


class ConfRepoTest(Project):
    def test_a_valid_value_is_read(self):
        for value in (GOOD, "a/b", "A-1/b_2.c", "-x/.y"):
            with self.subTest(value=value):
                self.conf(f'KIT_DIR="agent-kit"\nGITHUB_REPO="{value}"\n')
                self.assertEqual(github_api.conf_repo(str(self.project / "agent-kit.conf")), value)

    def test_single_quotes_and_trailing_blanks_are_accepted(self):
        for line in ("GITHUB_REPO='a/b'", 'GITHUB_REPO="a/b"  ', 'GITHUB_REPO="a/b"\t'):
            with self.subTest(line=line):
                self.conf(line + "\n")
                self.assertEqual(github_api.conf_repo(str(self.project / "agent-kit.conf")), "a/b")

    def test_bad_values_are_refused(self):
        for value in BAD_VALUES:
            with self.subTest(value=value):
                self.conf(f'GITHUB_REPO="{value}"\n')
                with self.assertRaises(ValueError):
                    github_api.conf_repo(str(self.project / "agent-kit.conf"))

    def test_bad_conf_shapes_are_refused(self):
        shapes = {
            "no file": None,
            "empty file": "",
            "no line": 'KIT_DIR="agent-kit"\n',
            "commented out": '# GITHUB_REPO="a/b"\n',
            "unquoted": "GITHUB_REPO=a/b\n",
            "unterminated quote": 'GITHUB_REPO="a/b\n',
            "mixed quotes": "GITHUB_REPO=\"a/b'\n",
            "trailing comment": 'GITHUB_REPO="a/b" # mine\n',
            "trailing text": 'GITHUB_REPO="a/b" x\n',
            "after another word": 'x GITHUB_REPO="a/b"\n',
            "export": 'export GITHUB_REPO="a/b"\n',
            "leading space": ' GITHUB_REPO="a/b"\n',
            "two lines": 'GITHUB_REPO="a/b"\nGITHUB_REPO="c/d"\n',
            "same value twice": 'GITHUB_REPO="a/b"\nGITHUB_REPO="a/b"\n',
            "valid then invalid": 'GITHUB_REPO="a/b"\nGITHUB_REPO="x y"\n',
            "other name": 'GITHUB_REPOS="a/b"\n',
            "carriage return": 'GITHUB_REPO="a/b"\r\n',
            "expansion": 'GITHUB_REPO="${OWNER}/b"\n',
            "command substitution": 'GITHUB_REPO="$(echo a)/b"\n',
            "not utf-8": b'GITHUB_REPO="a/b"\n\xff\xfe\n',
        }
        path = self.project / "agent-kit.conf"
        for name, text in shapes.items():
            with self.subTest(shape=name):
                path.unlink(missing_ok=True)
                if isinstance(text, bytes):
                    path.write_bytes(text)
                elif text is not None:
                    path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    github_api.conf_repo(str(path))

    def test_the_conf_is_never_sourced_or_run(self):
        self.conf('GITHUB_REPO="a/b"\ntouch marker\n$(touch marker)\nGITHUB_REPO2=$(touch marker)\n')
        self.assertEqual(github_api.conf_repo(str(self.project / "agent-kit.conf")), "a/b")
        self.assertFalse((self.project / "marker").exists())

    def test_repo_and_numbers_checks(self):
        self.assertEqual(github_api.check_repo(GOOD), GOOD)
        for value in BAD_VALUES + [None, 5, ["a/b"]]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    github_api.check_repo(value)
        for value in ("0", "007", "1 2", "1;x", "", "-1", "1\n", None):
            with self.subTest(number=value):
                with self.assertRaises(ValueError):
                    github_api.check_number(value)


class RefusalTest(Project):
    """Every wrapper, with a bad conf: refused, and the recording gh saw nothing."""

    def test_every_bad_value_is_refused_before_any_gh_call(self):
        for value in BAD_VALUES:
            self.conf(f'KIT_DIR="agent-kit"\nGITHUB_REPO="{value}"\n')
            self.assert_all_refuse(f"value {value!r}")

    def test_a_missing_conf_line_is_refused(self):
        self.conf('KIT_DIR="agent-kit"\n')
        self.assert_all_refuse("no GITHUB_REPO line")

    def test_two_lines_are_refused(self):
        self.conf('GITHUB_REPO="a/b"\nGITHUB_REPO="c/d"\n')
        self.assert_all_refuse("two lines")

    def test_a_command_in_the_value_is_not_run(self):
        self.conf('GITHUB_REPO="a/b$(touch marker)"\n')
        self.assert_all_refuse("command substitution")
        self.conf('GITHUB_REPO="a/b"; touch marker\n')
        self.assert_all_refuse("command after the value")

    def test_reading_the_repository_never_runs_the_conf(self):
        # (The secret scanner sources agent-kit.conf for KIT_DIR, as it always has; this is about
        # the GITHUB_REPO reader and the wrappers written in Python, which never source it.)
        for text in ('GITHUB_REPO="a/b$(touch marker)"\n', 'GITHUB_REPO="a/b"; touch marker\n',
                     'GITHUB_REPO="a/b"\n$(touch marker)\ntouch marker\n'):
            self.conf(text)
            for command in (["agent-kit/scripts/github_api.py", "repo"],
                            ["agent-kit/scripts/issue-hash.py", "5"],
                            ["agent-kit/scripts/sweep-due.py", "--dir", "records"]):
                self.run_cmd(sys.executable, "-B", *command)
                self.assertFalse((self.project / "marker").exists(), (text, command))

    def test_the_environment_cannot_supply_the_repository(self):
        self.conf('KIT_DIR="agent-kit"\n')
        self.env["GITHUB_REPO"] = GOOD
        self.env["GH_REPO"] = GOOD
        self.assert_all_refuse("repository in the environment")

    def test_a_valid_value_names_the_repository_in_every_call(self):
        self.conf(f'GITHUB_REPO="{GOOD}"\n')
        self.ghdir.joinpath("config.json").write_text(json.dumps({
            "issue_view": {"stdout": json.dumps({"labels": [{"name": "approved"}], "user": {"login": "o"}})},
            "repo_view": {"stdout": json.dumps({"owner": {"login": "o"}})},
            "create": {"stdout": json.dumps({"html_url": "https://github.com/x/y/issues/1"})},
            "comment": {"stdout": json.dumps({"html_url": "https://github.com/x/y/issues/1#c"})}}))
        for name, command, _ in self.wrappers()[:2]:
            with self.subTest(wrapper=name):
                done = self.run_cmd(*command)
                self.assertEqual(done.returncode, 0, done.stderr)
        calls = [json.loads(line) for line in self.calls()]
        self.assertTrue(calls)
        for call in calls:
            self.assertEqual(call[0], "api")
            self.assertTrue(call[1].startswith(f"repos/{GOOD}"), call)


if __name__ == "__main__":
    unittest.main()
