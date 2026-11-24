"""Tests for scripts/pr-open.sh and the pr-open make target (issue #239, C3 and C4).

No network and no real GitHub. The fake `gh` of fake_gh_rest.py is first on PATH: it logs
every call, records the body of a pull request create on standard input, and answers from a
config file. So the refused cases can show that no write call (no POST) was made, and the
successful ones exactly which calls were.

Each test runs in a throwaway git project under .scratch/: a copy of the kit's scripts/, an
agent-kit.conf naming a test repository, a .scratch/ folder for FILE, and a session branch
whose origin copy (the remote-tracking ref) is set by the test. Nothing is pushed or fetched.

Exit codes: 1 gh failed, 2 bad N, FILE, title or body, 3 the secret scan refused, 4 the
branch is refused.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path

from fake_gh_rest import FAKE_GH
from kit_repo import build_env, new_workdir
from secret_fixtures import MATCH

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
TEST_REPO = "example-org/example-repo"
BRANCH = "claude/session-1"
PR_URL = "https://github.com/example-org/example-repo/pull/7"
OLD_PR_URL = "https://github.com/example-org/example-repo/pull/5"
BODY = "Refs #23\n\n## What changed\n\nA fine change.\n"
GOOD = "Title: Open a fine change\n\n" + BODY
REPO_VIEW = json.dumps({"default_branch": "main", "owner": {"login": "example-org"}})
CLOSE_KEYWORDS = ["close", "closes", "closed", "fix", "fixes", "fixed", "resolve", "resolves", "resolved"]


def is_write(argv: list) -> bool:
    """Any gh call with a method other than GET (POST, PATCH, PUT, DELETE) is a write."""
    if "--method" in argv:
        return argv[argv.index("--method") + 1] != "GET"
    return any(a in ("-X", "-f", "-F", "--field", "--raw-field", "--input") for a in argv)


class PrOpenBase(unittest.TestCase):
    def setUp(self):
        self.work = new_workdir(prefix="pr-open-")
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.ghdir = self.work / "gh-bin"
        self.ghdir.mkdir()
        gh = self.ghdir / "gh"
        gh.write_text(FAKE_GH, encoding="utf-8")
        gh.chmod(0o755)
        self.env = build_env(self.work)
        self.env["PATH"] = f"{self.ghdir}{os.pathsep}{self.env['PATH']}"
        self.project = self.work / "project"
        self.project.mkdir()
        shutil.copytree(KIT / "scripts", self.project / "agent-kit" / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        (self.project / "agent-kit.conf").write_text(f'KIT_DIR="agent-kit"\nGITHUB_REPO="{TEST_REPO}"\n',
                                                     encoding="utf-8")
        (self.project / ".scratch").mkdir()
        (self.project / ".gitignore").write_text(".scratch/\n", encoding="utf-8")
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Kit Test")
        self.git("config", "user.email", "kit-test@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.git("add", "--", ".gitignore", "agent-kit.conf", "agent-kit")
        self.git("commit", "-q", "--no-verify", "-m", "base")
        self.git("checkout", "-q", "-b", BRANCH)
        (self.project / "change.txt").write_text("change\n", encoding="utf-8")
        self.git("add", "--", "change.txt")
        self.git("commit", "-q", "--no-verify", "-m", "change")
        self.push(BRANCH)
        self.config()

    def git(self, *args):
        done = subprocess.run(["git", *args], cwd=str(self.project), env=self.env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True)
        if done.returncode != 0:
            raise AssertionError(f"git {' '.join(args)} failed: {done.stderr}")
        return done.stdout.strip()

    def push(self, branch, ref="HEAD"):
        """Stand in for a push: set origin's copy of the branch (the remote-tracking ref)."""
        self.git("update-ref", f"refs/remotes/origin/{branch}", ref)

    def config(self, **overrides):
        config = {"repo_view": {"stdout": REPO_VIEW}, "pulls": {"stdout": "[]"},
                  "pull_create": {"stdout": json.dumps({"html_url": PR_URL, "draft": True})}}
        config.update(overrides)
        (self.ghdir / "config.json").write_text(json.dumps(config), encoding="utf-8")
        for name in ("calls.log", "stdin.bin"):
            (self.ghdir / name).unlink(missing_ok=True)

    def calls(self):
        log = self.ghdir / "calls.log"
        return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []

    def writes(self):
        return [c for c in self.calls() if is_write(c)]

    def gh_stdin(self):
        path = self.ghdir / "stdin.bin"
        return path.read_bytes() if path.exists() else b""

    def put(self, text, name="pr.md"):
        (self.project / ".scratch" / name).write_bytes(text.encode("utf-8"))
        return f".scratch/{name}"

    def run_script(self, *args):
        return subprocess.run(["bash", "agent-kit/scripts/pr-open.sh", *args], cwd=str(self.project),
                              env=self.env, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                              errors="replace")

    def open(self, text=GOOD, number="23"):
        self.config_keep()
        return self.run_script(number, self.put(text))

    def config_keep(self):
        for name in ("calls.log", "stdin.bin"):
            (self.ghdir / name).unlink(missing_ok=True)

    def assert_refused(self, done, code, reason, gh_ran=False):
        """Refused: the exit code, a reason, nothing on stdout and no GitHub write call."""
        self.assertEqual(done.returncode, code, done.stdout + done.stderr)
        self.assertEqual(done.stdout, "")
        self.assertIn(reason, done.stderr)
        self.assertEqual(self.writes(), [], "a GitHub write call was made")
        if not gh_ran:
            self.assertEqual(self.calls(), [], "gh was run")


class OpenTest(PrOpenBase):
    def test_opens_one_draft_pull_request_and_prints_its_url(self):
        done = self.open()
        self.assertEqual((done.returncode, done.stdout), (0, PR_URL + "\n"), done.stderr)
        self.assertEqual(self.calls(), [
            ["api", f"repos/{TEST_REPO}"],
            ["api", f"repos/{TEST_REPO}/pulls?state=open&head=example-org:{BRANCH}&per_page=100"],
            ["api", f"repos/{TEST_REPO}/pulls", "--method", "POST", "-f", "title=Open a fine change",
             "-f", f"head={BRANCH}", "-f", "base=main", "-F", "draft=true", "-F", "body=@-"],
        ])
        creates = [c for c in self.calls() if is_write(c)]
        self.assertEqual(len(creates), 1)
        self.assertIn("draft=true", creates[0])
        self.assertEqual(self.gh_stdin(), BODY.encode())

    def test_an_open_pull_request_for_the_head_prints_its_url_and_creates_nothing(self):
        self.config(pulls={"stdout": json.dumps([{"html_url": OLD_PR_URL, "draft": True}])})
        done = self.open()
        self.assertEqual((done.returncode, done.stdout), (0, OLD_PR_URL + "\n"), done.stderr)
        self.assertIn("already exists", done.stderr)
        self.assertEqual(self.writes(), [])
        self.assertEqual(self.gh_stdin(), b"")
        self.assertEqual(len(self.calls()), 2)

    def test_the_kit_template_body_is_accepted(self):
        template = (KIT / "templates" / "github" / "pull_request_template.md").read_text(encoding="utf-8")
        self.assertIn("Refs #N\n", template)
        body = template.replace("Refs #N", "Refs #23")
        done = self.open("Title: From the template\n\n" + body)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.gh_stdin(), body.encode())

    def test_words_that_only_look_like_keywords_are_accepted(self):
        for text in ("Refs #23\nFixtures #3 and prefix #4 and closest #5.\n",
                     "Refs #23\nNever write Closes, Fixes or Resolves: only the orchestrator closes.\n",
                     "Refs #23\nThis fixes the layout; see #12 for why.\n"):
            with self.subTest(text=text):
                self.assertEqual(self.open("Title: t\n\n" + text).returncode, 0)

    def test_a_failed_create_says_so_and_does_not_retry(self):
        self.config(pull_create={"stdout": "", "exit": 1})
        done = self.open()
        self.assertEqual(done.returncode, 1)
        self.assertEqual(done.stdout, "")
        self.assertIn("nothing was retried", done.stderr)
        self.assertEqual(len(self.writes()), 1)


class BodyRefusalTest(PrOpenBase):
    def test_a_closing_keyword_before_an_issue_reference_is_refused(self):
        forms = []
        for word in CLOSE_KEYWORDS:
            forms += [f"{word} #23", f"{word.upper()} #23", f"{word.capitalize()}: #9"]
        forms += ["Closes example-org/example-repo#23", "**Fixes** #23", "resolves\t#1",
                  "Fixed https://github.com/example-org/example-repo/issues/23", "see below. Closes #23."]
        for line in forms:
            with self.subTest(line=line):
                self.assert_refused(self.open(f"Title: t\n\nRefs #23\n{line}\n"), 2, "closing keyword")
        self.assert_refused(self.open("Title: Fixes #23\n\nRefs #23\n"), 2, "closing keyword")

    def test_a_body_without_the_refs_line_is_refused(self):
        for body in ("No reference here.\n", "Refs 23\n", "Refs #2\n", "Refs #230\n", "Refs: #23\n",
                     "See Refs #23 inline\n", "refs #23\n"):
            with self.subTest(body=body):
                self.assert_refused(self.open("Title: t\n\n" + body), 2, "no line Refs #23")

    def test_a_secret_is_refused(self):
        for name, text, _number, shown in MATCH[:3]:
            with self.subTest(name=name):
                done = self.open(f"Title: t\n\nRefs #23\n{text}\n")
                self.assert_refused(done, 3, "secret scan refused")
                self.assertNotIn(shown, done.stderr)

    def test_a_bad_title_line_is_refused(self):
        for text in ("Refs #23\n", "Title: t\nRefs #23\n", "Title: \n\nRefs #23\n", "Title: -x\n\nRefs #23\n",
                     "Title: t\n\n   \n"):
            with self.subTest(text=text):
                self.assertEqual(self.open(text).returncode, 2)
                self.assertEqual(self.calls(), [])


class BranchRefusalTest(PrOpenBase):
    def test_the_default_branch_is_refused(self):
        self.git("checkout", "-q", "main")
        self.push("main")
        self.assert_refused(self.open(), 4, "default branch", gh_ran=True)
        self.assertEqual(self.calls(), [["api", f"repos/{TEST_REPO}"]])

    def test_a_detached_head_is_refused(self):
        self.git("checkout", "-q", "--detach")
        self.assert_refused(self.open(), 4, "detached")

    def test_a_branch_never_pushed_is_refused(self):
        self.git("update-ref", "-d", f"refs/remotes/origin/{BRANCH}")
        self.assert_refused(self.open(), 4, "push it first")

    def test_a_branch_whose_origin_copy_is_behind_head_is_refused(self):
        (self.project / "more.txt").write_text("more\n", encoding="utf-8")
        self.git("add", "--", "more.txt")
        self.git("commit", "-q", "--no-verify", "-m", "more")
        self.assert_refused(self.open(), 4, "not at HEAD")

    def test_a_branch_name_outside_the_allowed_characters_is_refused(self):
        self.git("checkout", "-q", "-b", "claude/a&b")
        self.push("claude/a&b")
        self.assert_refused(self.open(), 4, "branch name")


class ArgumentRefusalTest(PrOpenBase):
    def test_bad_numbers_are_refused_by_the_script(self):
        file = self.put(GOOD)
        for value in ("", "0", "023", "-1", "1 2", "1234567890", "$(touch x)", "1;x"):
            with self.subTest(n=value):
                self.assert_refused(self.run_script(value, file), 2, "N must")

    def test_bad_files_are_refused_by_the_script(self):
        self.put(GOOD, "real.md")
        (self.project / "outside.md").write_text(GOOD, encoding="utf-8")
        for file in ("", "outside.md", ".scratch/../outside.md", ".scratch/missing.md", ".scratch/a b",
                     "-x", ".scratch/real.md/"):
            with self.subTest(file=file):
                done = self.run_script("23", file)
                self.assert_refused(done, 2, "FILE")

    def test_wrong_argument_count_is_refused(self):
        self.assert_refused(self.run_script("23"), 2, "Usage")


class MakeTargetTest(PrOpenBase):
    """The repo Makefile's pr-open target, run in the throwaway project."""

    def setUp(self):
        super().setUp()
        self.makefile = self.work / "Makefile"
        shutil.copyfile(REPO / "Makefile", self.makefile)

    def make(self, *args):
        self.config_keep()
        env = {k: v for k, v in self.env.items() if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL")}
        return subprocess.run(["make", "--no-print-directory", "-f", str(self.makefile), *args],
                              cwd=str(self.project), env=env, stdin=subprocess.DEVNULL, capture_output=True,
                              text=True, errors="replace")

    def test_make_pr_open_runs_the_script(self):
        done = self.make("pr-open", "N=23", "FILE=" + self.put(GOOD))
        self.assertEqual((done.returncode, done.stdout), (0, PR_URL + "\n"), done.stderr)
        self.assertEqual(len(self.writes()), 1)

    def test_numbers_and_files_failing_the_make_checks_are_refused_before_the_script(self):
        good = self.put(GOOD)
        marker = self.project / "MARKER"
        for args in (["N=0", f"FILE={good}"], ["N=1 2", f"FILE={good}"], ["N=$(shell touch MARKER)", f"FILE={good}"],
                     ["N=23", "FILE=outside.md"], ["N=23", "FILE=.scratch/../x.md"],
                     ["N=23", "FILE=.scratch/$(shell touch MARKER)"], ["N=23"], [f"FILE={good}"]):
            with self.subTest(args=args):
                done = self.make("pr-open", *args)
                self.assertNotEqual(done.returncode, 0)
                self.assertIn("Usage: make pr-open", done.stderr)
                self.assertEqual(self.calls(), [])
                self.assertFalse(marker.exists())


class TargetTextTest(unittest.TestCase):
    def test_both_makefiles_define_the_target_with_the_existing_checks(self):
        for path, root in ((REPO / "Makefile", "agent-kit"),
                           (KIT / "templates" / "Makefile.github.mk", "_docs/agent-kit")):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertRegex(text, r"(?m)^pr-open: ## ")
                self.assertIn("$(call issue-number-ok,$(value N))", text.split("pr-open: ## ", 1)[1])
                self.assertIn("$(call issue-file-ok,$(value FILE))", text.split("pr-open: ## ", 1)[1])
                self.assertIn(f'@bash {root}/scripts/pr-open.sh "$(N)" "$(FILE)"', text)

    def test_make_is_pre_approved_so_opening_asks_nothing(self):
        for path in (REPO / ".claude" / "settings.json", KIT / "claude-code" / "settings.json"):
            with self.subTest(path=str(path.relative_to(REPO))):
                allow = json.loads(path.read_text(encoding="utf-8"))["permissions"]["allow"]
                self.assertIn("Bash(make *)", allow)

    def test_the_script_never_readies_merges_closes_labels_or_pushes(self):
        script = (KIT / "scripts" / "pr-open.sh").read_text(encoding="utf-8")
        code = "\n".join(line for line in script.splitlines() if not line.lstrip().startswith("#"))
        for word in ("draft=false", "/merge", "--method PATCH", "--method PUT", "/labels",
                     "graphql", "markPullRequestReadyForReview"):
            with self.subTest(word=word):
                self.assertNotIn(word, code)
        self.assertNotRegex(code, r"(?m)^\s*git push")  # named only in a refusal's hint
        self.assertEqual(code.count("--method POST"), 1)


if __name__ == "__main__":
    unittest.main()
