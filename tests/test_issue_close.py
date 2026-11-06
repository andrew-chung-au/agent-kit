"""Tests for issue-close.sh and the `make issue-close` target (issue #119).

No network and no real GitHub: a fake `gh` is first on PATH. It logs every call as one JSON
line and answers from a config file. No test closes a real issue. Every refusal asserts the
exit code, the message, and that no close call was made.

Exit codes: 0 closed; 1 gh failed on the close; 2 bad N or REASON (no gh run); 4 refused or
could not check.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from fake_gh_rest import FAKE_GH, rest_config
from kit_repo import build_env, new_workdir

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
sys.path.insert(0, str(KIT / "scripts"))
import github_api  # noqa: E402

GH_REPO = github_api.conf_repo(str(REPO / "agent-kit.conf"))  # the repository the scripts name
SCRIPT = KIT / "scripts" / "issue-close.sh"

OWNER = "the-owner"
OTHER = "someone-else"

HEX_QA = "abc1234"
HEX_MERGE = "def5678"

# Timestamps increase with the number, so tests can order comments.
def close_call(number: int, reason: str) -> list:
    return ["api", f"repos/{GH_REPO}/issues/{number}", "--method", "PATCH", "-f", "state=closed",
            "-f", f"state_reason={reason}"]


def at(n: int) -> str:
    return f"2026-11-03T10:{n:02d}:00Z"


def comment(body: str, n: int, login: str = OWNER) -> dict:
    return {"author": {"login": login}, "body": body, "createdAt": at(n)}


def engineer(n: int = 1, login: str = OWNER) -> dict:
    return comment(f"Engineer: built it, commit 1a2b3c4 on branch x\nVerify: PASS", n, login)


def qa_pass(n: int, login: str = OWNER, commit: str = HEX_QA) -> dict:
    return comment(f"QA: PASS\n\nChecked commit {commit}. Every criterion met.", n, login)


def qa_fail(n: int, login: str = OWNER) -> dict:
    return comment("QA: FAIL\n\nCriterion 3 fails.", n, login)


def close_comment(n: int, login: str = OWNER, qa: str = HEX_QA, extra: str = "", skip: str = "") -> dict:
    lines = [f"QA PASS commit: {qa}", f"Merge commit: {HEX_MERGE}", "Verify: PASS",
             "Summary: _session-summaries/x.md"]
    if extra:
        lines.append(extra)
    lines = [ln for ln in lines if not (skip and ln.startswith(skip))]
    return comment("Orchestrator: closing.\n" + "\n".join(lines), n, login)


def issue(comments, labels=("approved",), state="OPEN", author=OWNER) -> str:
    return json.dumps({"state": state, "labels": [{"name": n} for n in labels],
                       "author": {"login": author}, "comments": comments})


STANDARD = [engineer(1), qa_pass(2), close_comment(3)]
HEAVY = [engineer(1), qa_pass(2), qa_pass(3), close_comment(4)]
LIGHT = [comment("Engineer: done.\nchanged: x\ntier-check: PASS for light (3 changed lines since abc).", 1),
         comment("Orchestrator: closing.\nMerge commit: def5678\nVerify: PASS\nSummary: s.md\n"
                 "Human approved diff: yes", 2)]
NOT_PLANNED = [comment("Orchestrator: Close as not planned\nHuman approved closure: 2026-11-03\n"
                       "Backlog review: _session-summaries/review.md", 1)]


class CloseBase(unittest.TestCase):
    def setUp(self):
        self.work = new_workdir(prefix="close-")
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.ghdir = self.work / "gh-bin"
        self.ghdir.mkdir()
        gh = self.ghdir / "gh"
        gh.write_text(FAKE_GH, encoding="utf-8")
        gh.chmod(0o755)
        self.env = build_env(self.work)
        self.env["PATH"] = f"{self.ghdir}{os.pathsep}{self.env['PATH']}"
        self.config()

    def config(self, view=None, **overrides):
        config = rest_config(view if view is not None else issue(STANDARD))
        config.update({"repo_view": {"stdout": json.dumps({"owner": {"login": OWNER}})},
                       "close": {"stdout": "{}"}})
        config.update(overrides)
        (self.ghdir / "config.json").write_text(json.dumps(config), encoding="utf-8")
        (self.ghdir / "calls.log").unlink(missing_ok=True)

    def calls(self):
        log = self.ghdir / "calls.log"
        return [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []

    def closes(self):
        return [c for c in self.calls() if "--method" in c and c[c.index("--method") + 1] == "PATCH"]

    def run_script(self, *args, env=None):
        return subprocess.run(["bash", str(SCRIPT), *args], cwd=str(REPO), env=env or self.env,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True)

    def assert_refused(self, done, fragment, code=4):
        self.assertEqual(done.returncode, code, done.stderr)
        self.assertEqual(done.stdout, "")
        self.assertIn(fragment, done.stderr)
        self.assertEqual(self.closes(), [], "a close call was made")

    def refuse_view(self, comments, fragment, labels=("approved",), state="OPEN", reason=None):
        self.config(view=issue(comments, labels=labels, state=state))
        args = ["7"] + ([reason] if reason else [])
        self.assert_refused(self.run_script(*args), fragment)

    def close_ok(self, comments, labels=("approved",), reason=None):
        self.config(view=issue(comments, labels=labels))
        args = ["7"] + ([reason] if reason else [])
        done = self.run_script(*args)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(done.stderr, "")
        return done


class SuccessTest(CloseBase):
    def test_standard(self):
        done = self.close_ok(STANDARD)
        self.assertEqual(done.stdout, "issue-close: closed issue 7 (completed)\n")
        self.assertEqual(self.calls(), [
            ["api", f"repos/{GH_REPO}/issues/7"],
            ["api", f"repos/{GH_REPO}/issues/7/comments?per_page=100&page=1"],
            ["api", f"repos/{GH_REPO}"],
            close_call(7, "completed")])

    def test_heavy(self):
        self.close_ok(HEAVY, labels=("approved", "tier:heavy"))
        self.assertEqual(len(self.closes()), 1)

    def test_light(self):
        self.close_ok(LIGHT, labels=("approved", "tier:light"))
        self.assertEqual(self.closes(), [close_call(7, "completed")])

    def test_not_planned_needs_no_label(self):
        done = self.close_ok(NOT_PLANNED, labels=(), reason="not-planned")
        self.assertEqual(done.stdout, "issue-close: closed issue 7 (not-planned)\n")
        self.assertEqual(self.closes(), [close_call(7, "not_planned")])

    def test_explicit_completed_reason(self):
        self.close_ok(STANDARD, reason="completed")

    def test_pass_at_the_same_time_as_the_engineer_comment_counts_as_after(self):
        self.close_ok([engineer(1), qa_pass(1), close_comment(2)])

    def test_pass_before_an_engineer_comment_without_a_commit_still_counts(self):
        self.close_ok([engineer(1), qa_pass(2), comment("Engineer: a note, no commit here.", 3), close_comment(4)])

    def test_a_later_pass_after_an_earlier_fail(self):
        self.close_ok([engineer(1), qa_fail(2), qa_pass(3), close_comment(4)])

    def test_highest_tier_label_wins(self):
        self.refuse_view(STANDARD, "needs 2 owner QA PASS", labels=("approved", "tier:light", "tier:heavy"))


class ArgumentTest(CloseBase):
    def test_bad_numbers_never_run_gh(self):
        for value in ("", "0123", "12 34", "1;x", "$(x)", "1234567890", "abc", "0", "-1", "1 2"):
            with self.subTest(n=value):
                (self.ghdir / "calls.log").unlink(missing_ok=True)
                done = self.run_script(value)
                self.assertEqual(done.returncode, 2)
                self.assertIn("N must", done.stderr)
                self.assertEqual(self.calls(), [])

    def test_bad_reason_never_runs_gh(self):
        for value in ("planned", "Completed", "not planned", "completed;x", "", "$(x)", "all"):
            with self.subTest(reason=value):
                (self.ghdir / "calls.log").unlink(missing_ok=True)
                done = self.run_script("7", value)
                self.assertEqual(done.returncode, 2)
                self.assertIn("REASON must be", done.stderr)
                self.assertEqual(self.calls(), [])

    def test_wrong_argument_count(self):
        for args in ((), ("1", "completed", "x")):
            done = self.run_script(*args)
            self.assertEqual(done.returncode, 2)
            self.assertIn("Usage", done.stderr)
            self.assertEqual(self.calls(), [])


class FailClosedTest(CloseBase):
    def test_gh_missing(self):
        env = dict(self.env)
        folder = self.work / "no-gh"
        folder.mkdir()
        for tool in ("python3", "bash", "head", "base64", "tr", "wc", "dirname", "cat"):
            found = shutil.which(tool)
            if found:
                os.symlink(found, folder / tool)
        env["PATH"] = str(folder)
        done = self.run_script("7", env=env)
        self.assert_refused(done, "gh was not found")

    def test_gh_view_fails(self):
        self.config(issue_view={"exit": 1})
        self.assert_refused(self.run_script("7"), "cannot read issue 7")

    def test_repo_view_fails(self):
        self.config(repo_view={"exit": 1})
        self.assert_refused(self.run_script("7"), "cannot read the repository owner")

    def test_empty_and_malformed_output(self):
        # Not a JSON object: the REST read itself fails. An object without the fields: the check cannot tell.
        for text in ("", "not json", "[]", "null", "{}", '{"state": "open"}'):
            with self.subTest(text=text):
                self.config(view=text)
                fragment = ("cannot tell whether issue 7 may be closed" if text.startswith("{")
                            else "cannot read issue 7")
                self.assert_refused(self.run_script("7"), fragment)

    def test_missing_fields(self):
        base = json.loads(issue(STANDARD))
        for field in ("state", "labels", "author"):
            with self.subTest(field=field):
                broken = dict(base)
                del broken[field]
                self.config(view=json.dumps(broken))
                self.assert_refused(self.run_script("7"), "cannot tell")

    def test_the_comments_cannot_be_read(self):
        # With `gh issue view` the comments were a field of the issue; over the REST API they are
        # a separate read, and a failed or malformed one refuses the close the same way.
        for name, comments in (("fails", {"exit": 1}), ("prints nothing", {"stdout": ""}),
                               ("not json", {"stdout": "oops"}), ("an object", {"stdout": "{}"}),
                               ("a comment is text", {"stdout": '["x"]'})):
            with self.subTest(name=name):
                self.config(comments=comments)
                self.assert_refused(self.run_script("7"), "cannot read issue 7")

    def test_malformed_comment_entry(self):
        self.config(view=issue([{"body": "QA: PASS"}]))
        self.assert_refused(self.run_script("7"), "cannot tell")

    def test_empty_owner(self):
        self.config(repo_view={"stdout": json.dumps({"owner": {"login": ""}})})
        self.assert_refused(self.run_script("7"), "cannot tell")

    def test_close_fails(self):
        self.config(close={"exit": 1})
        done = self.run_script("7")
        self.assertEqual(done.returncode, 1)
        self.assertIn("gh issue close failed", done.stderr)
        self.assertEqual(len(self.closes()), 1, "no retry")


class RefusalTest(CloseBase):
    def test_already_closed(self):
        self.refuse_view(STANDARD, "not open", state="CLOSED")

    def test_missing_approved_label(self):
        self.refuse_view(STANDARD, "approved label", labels=())
        self.refuse_view(STANDARD, "approved label", labels=("tier:heavy",))

    def test_light_needs_approved_label(self):
        self.refuse_view(LIGHT, "approved label", labels=("tier:light",))

    def test_no_qa_pass(self):
        self.refuse_view([engineer(1), close_comment(2)], "no owner QA comment")

    def test_qa_pass_from_a_non_owner_is_ignored(self):
        self.refuse_view([engineer(1), qa_pass(2, login=OTHER), close_comment(3)], "no owner QA comment")

    def test_latest_verdict_fail_even_after_an_earlier_pass(self):
        self.refuse_view([engineer(1), qa_pass(2), qa_fail(3), close_comment(4)], "latest owner QA verdict is FAIL")

    def test_a_fail_from_a_non_owner_does_not_block(self):
        self.close_ok([engineer(1), qa_pass(2), qa_fail(3, login=OTHER), close_comment(4)])

    def test_pass_older_than_an_all_digit_short_sha_commit_comment(self):
        # QA on #119 at 3af2c57: "commit 1234567" was not read as a commit, so the floor
        # stayed low and the stale PASS closed the issue.
        later = comment("Engineer: fix, commit 1234567", 3)
        self.refuse_view([engineer(1), qa_pass(2), later, close_comment(4)], "found 0")

    def test_not_pass_and_did_not_pass_are_no_verdict(self):
        for first in ("QA: NOT PASS", "QA: did not PASS", "QA: no PASS yet", "QA:PASS", "QA: passed"):
            with self.subTest(first=first):
                self.refuse_view([engineer(1), comment(first + "\n\nChecked abc1234.", 2), close_comment(3)],
                                 "no owner QA comment with a PASS verdict")

    def test_a_pass_comment_with_more_on_the_first_line_still_counts(self):
        self.close_ok([engineer(1), comment("QA: PASS (launch 1 of 1)\n\nChecked abc1234.", 2), close_comment(3)])

    def test_deleted_account_comments_are_skipped_not_blocking(self):
        ghost = {"author": None, "body": "QA: FAIL\n\nfrom a deleted account", "createdAt": at(3)}
        self.close_ok([engineer(1), qa_pass(2), ghost, close_comment(4)])

    def test_deleted_account_pass_does_not_count(self):
        ghost = {"author": None, "body": "QA: PASS\n\nChecked abc1234.", "createdAt": at(2)}
        self.refuse_view([engineer(1), ghost, close_comment(3)], "no owner QA comment")

    def test_deleted_issue_author_is_not_blocking(self):
        view = json.loads(issue(STANDARD))
        view["author"] = None
        self.config(view=json.dumps(view))
        self.assertEqual(self.run_script("7").returncode, 0)

    def test_large_comment_history_is_read_from_stdin(self):
        # QA on #119: over about 128 KB as one argument gave "Argument list too long".
        filler = [comment("Engineer: notes\n" + "x" * 4000, n) for n in range(1, 60)]
        view = issue([engineer(0)] + filler + [qa_pass(70), close_comment(71)])
        self.assertGreater(len(view), 200_000)
        self.config(view=view)
        done = self.run_script("7")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(len(self.closes()), 1)

    def test_pass_and_fail_in_one_first_line_is_fail(self):
        both = comment("QA: PASS and FAIL mixed up", 2)
        self.refuse_view([engineer(1), both, close_comment(3)], "FAIL")

    def test_pass_older_than_the_last_engineer_commit_comment(self):
        self.refuse_view([engineer(1), qa_pass(2), engineer(3), close_comment(4)], "found 0")

    def test_heavy_needs_two_passes(self):
        self.refuse_view(STANDARD, "needs 2 owner QA PASS comment(s)", labels=("approved", "tier:heavy"))

    def test_heavy_second_pass_must_be_after_the_engineer_comment(self):
        self.refuse_view([qa_pass(1), engineer(2), qa_pass(3), close_comment(4)], "found 1",
                         labels=("approved", "tier:heavy"))

    def test_heavy_passes_from_a_non_owner_do_not_count(self):
        self.refuse_view([engineer(1), qa_pass(2), qa_pass(3, login=OTHER), close_comment(4)], "found 1",
                         labels=("approved", "tier:heavy"))

    def test_no_close_comment(self):
        self.refuse_view([engineer(1), qa_pass(2)], "no owner Orchestrator Close comment")

    def test_close_comment_missing_a_line(self):
        for skip in ("QA PASS commit", "Merge commit", "Verify", "Summary"):
            with self.subTest(skip=skip):
                self.refuse_view([engineer(1), qa_pass(2), close_comment(3, skip=skip)],
                                 "no owner Orchestrator Close comment")

    def test_close_comment_with_bad_hex(self):
        for bad in ("abc12", "XYZ1234", "abc1234x", "A" * 7):
            with self.subTest(bad=bad):
                self.refuse_view([engineer(1), qa_pass(2), close_comment(3, qa=bad)],
                                 "no owner Orchestrator Close comment")

    def test_close_comment_before_the_latest_pass(self):
        self.refuse_view([engineer(1), qa_pass(2), close_comment(3), qa_pass(4)], "no owner Orchestrator Close")

    def test_close_comment_from_a_non_owner_is_ignored(self):
        self.refuse_view([engineer(1), qa_pass(2), close_comment(3, login=OTHER)], "no owner Orchestrator Close")

    def test_qa_pass_commit_must_appear_in_the_pass_comment(self):
        self.refuse_view([engineer(1), qa_pass(2), close_comment(3, qa="0badc0d")], "does not appear")

    def test_a_perfect_close_comment_from_another_account_for_light(self):
        other = [LIGHT[0], dict(LIGHT[1], author={"login": OTHER})]
        self.refuse_view(other, "no owner Orchestrator Close comment", labels=("approved", "tier:light"))

    def test_engineer_comment_from_a_non_owner_does_not_raise_the_floor(self):
        self.close_ok([engineer(1), qa_pass(2), engineer(3, login=OTHER), close_comment(4)])

    def test_light_needs_the_tier_check_line(self):
        no_check = [comment("Engineer: done.", 1), LIGHT[1]]
        self.refuse_view(no_check, "tier-check: PASS", labels=("approved", "tier:light"))

    def test_light_tier_check_from_a_non_owner_is_ignored(self):
        other = [dict(LIGHT[0], author={"login": OTHER}), LIGHT[1]]
        self.refuse_view(other, "tier-check: PASS", labels=("approved", "tier:light"))

    def test_light_needs_the_human_approved_diff_line(self):
        weak = [LIGHT[0], comment("Orchestrator: closing.\nMerge commit: def5678\nVerify: PASS\nSummary: s.md", 2)]
        self.refuse_view(weak, "Human approved diff", labels=("approved", "tier:light"))
        no = [LIGHT[0], dict(LIGHT[1], body=LIGHT[1]["body"].replace("yes", "no"))]
        self.refuse_view(no, "Human approved diff", labels=("approved", "tier:light"))

    def test_light_close_comment_before_the_tier_check_comment(self):
        self.refuse_view([LIGHT[1], dict(LIGHT[0], createdAt=at(5))], "no owner Orchestrator Close",
                         labels=("approved", "tier:light"))

    def test_not_planned_without_the_comment(self):
        self.refuse_view([], "Close as not planned", labels=(), reason="not-planned")
        self.refuse_view(STANDARD, "Close as not planned", reason="not-planned")

    def test_not_planned_comment_from_a_non_owner(self):
        self.refuse_view([dict(NOT_PLANNED[0], author={"login": OTHER})], "Close as not planned",
                         labels=(), reason="not-planned")

    def test_not_planned_needs_both_lines_and_a_real_date(self):
        base = NOT_PLANNED[0]["body"]
        for body in (base.replace("Human approved closure: 2026-11-03\n", ""),
                     base.replace("\nBacklog review: _session-summaries/review.md", ""),
                     base.replace("2026-11-03", "yesterday"),
                     base.replace("Orchestrator: Close as not planned", "Orchestrator: closing")):
            with self.subTest(body=body):
                self.refuse_view([comment(body, 1)], "Close as not planned", labels=(), reason="not-planned")

    def test_not_planned_on_a_closed_issue(self):
        self.refuse_view(NOT_PLANNED, "not open", labels=(), state="CLOSED", reason="not-planned")

    def test_not_planned_does_not_need_qa(self):
        self.close_ok(NOT_PLANNED, labels=("approved",), reason="not-planned")


class PaginationTest(CloseBase):
    """GitHub returns 100 comments at most per page: every page is read before the checks."""

    @staticmethod
    def filler(count):
        return [comment(f"Note {i}", 0) for i in range(count)]

    def comment_pages(self):
        return [c[1].rsplit("&page=", 1)[1] for c in self.calls() if "/comments?" in c[1]]

    def test_evidence_after_the_first_page_counts(self):
        # 253 comments: the Engineer, QA and Close comments are all on page 3.
        self.config(view=issue(self.filler(250) + [engineer(1), qa_pass(2), close_comment(3)]))
        done = self.run_script("7")
        self.assertEqual((done.returncode, done.stderr), (0, ""))
        self.assertEqual(self.comment_pages(), ["1", "2", "3"])
        self.assertEqual(len(self.closes()), 1)

    def test_a_fail_on_the_last_page_still_refuses(self):
        self.config(view=issue([engineer(1), qa_pass(2)] + self.filler(198) + [qa_fail(3), close_comment(4)]))
        self.assert_refused(self.run_script("7"), "the latest owner QA verdict is FAIL")
        self.assertEqual(self.comment_pages(), ["1", "2", "3"])

    def test_a_page_that_cannot_be_read_refuses(self):
        # The second page fails: the script must not decide from the first page alone.
        self.config(view=issue(self.filler(150) + STANDARD))
        gh = self.ghdir / "gh"
        gh.write_text(gh.read_text(encoding="utf-8").replace(
            "entry = config.get(kind, {})",
            'entry = config.get(kind, {})\nif query.get("page") == "2" and kind == "comments":\n    sys.exit(1)'),
            encoding="utf-8")
        self.assert_refused(self.run_script("7"), "cannot read issue 7")

    def test_exactly_one_page_of_comments_reads_a_second_empty_page(self):
        self.config(view=issue(self.filler(97) + STANDARD))
        done = self.run_script("7")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.comment_pages(), ["1", "2"])


class StaticTest(unittest.TestCase):
    def code(self):
        text = SCRIPT.read_text(encoding="utf-8")
        return [line for line in text.splitlines() if not line.lstrip().startswith("#")]

    def test_gh_is_only_called_in_the_three_allowed_shapes(self):
        found = []
        for line in self.code():
            line = re.sub(r'die [0-9] "[^"]*"', "", line)
            for match in re.finditer(r"\bgh (issue|repo|api|label|pr|auth|run)\b[^)>|]*", line):
                found.append(re.sub(r"\s+2\s*$", "", match.group(0).strip()))
        self.assertEqual(sorted(found), sorted([
            'gh api "repos/$REPO/issues/$number" --method PATCH -f state=closed -f state_reason=not_planned',
            'gh api "repos/$REPO/issues/$number" --method PATCH -f state=closed -f state_reason=completed']))

    def test_nothing_else_is_written(self):
        text = "\n".join(self.code())
        for word in ("--label", "--add-label", "issue edit", "issue reopen", "issue delete",
                     "issue comment", "--body", "eval ", "xargs"):
            self.assertNotIn(word, text)

    def test_not_run_by_verify_or_the_hooks(self):
        for path in [KIT / "scripts" / "verify.sh", KIT / "scripts" / "check-staged.sh"]:
            self.assertNotIn("issue-close", path.read_text(encoding="utf-8"))
        for folder in ("githooks", "claude-code/hooks"):
            for path in (KIT / folder).rglob("*"):
                if path.is_file():
                    self.assertNotIn("issue-close", path.read_text(encoding="utf-8", errors="ignore"))


class MakeTargetTest(CloseBase):
    def make(self, *args):
        (self.ghdir / "calls.log").unlink(missing_ok=True)
        return subprocess.run(["make", "--no-print-directory", *args], cwd=str(REPO), env=self.env,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True)

    def test_runs_the_script(self):
        done = self.make("issue-close", "N=7")
        self.assertEqual((done.returncode, done.stdout), (0, "issue-close: closed issue 7 (completed)\n"), done.stderr)
        self.assertEqual(self.closes(), [close_call(7, "completed")])

    def test_not_planned_reason(self):
        self.config(view=issue(NOT_PLANNED, labels=()))
        done = self.make("issue-close", "N=7", "REASON=not-planned")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.closes(), [close_call(7, "not_planned")])

    def test_bad_values_are_refused_before_any_shell_or_gh(self):
        for args in (["N=0123"], ["N=12 34"], ["N=1;x"], ["N=$(x)"], ["N=1234567890"], [],
                     ["N=1 2"], ["N=7", "REASON=planned"], ["N=7", "REASON=all"],
                     ["N=7", "REASON=completed;x"], ["N=7", "REASON=not planned"]):
            with self.subTest(args=args):
                done = self.make("issue-close", *args)
                self.assertNotEqual(done.returncode, 0)
                self.assertEqual(done.stdout, "")
                self.assertIn("Usage: make issue-close", done.stderr)
                self.assertEqual(self.calls(), [])

    def assert_injection_refused(self, reason, marker_name):
        marker = self.work / marker_name
        rel = os.path.relpath(marker, REPO)
        done = self.make("issue-close", "N=7", "REASON=" + reason.replace("MARKER", rel))
        self.assertNotEqual(done.returncode, 0)
        self.assertEqual(done.stdout, "")
        self.assertIn("Usage: make issue-close", done.stderr)
        self.assertNotIn("INJECTED", done.stdout + done.stderr)
        self.assertEqual(self.calls(), [], "gh was run")
        self.assertFalse(marker.exists(), "an injected command ran")

    def test_injection_through_reason_is_refused(self):
        # QA on #119 at 3af2c57: one valid word let the rest through to make and the shell.
        for name, reason in (
                ("multi-word", "completed not-planned"),
                ("valid word then junk", "completed junk"),
                ("info", "completed $(info INJECTED)"),
                ("shell", "completed $(shell touch MARKER)"),
                ("shell alone", "$(shell touch MARKER)"),
                ("quote and semicolon", 'completed " ; touch MARKER ; "'),
                ("semicolon no space", "completed;touch MARKER"),
                ("backticks", "completed `touch MARKER`"),
                ("dollar paren", "completed $$(touch MARKER)"),
                # A leading space is not tested: make strips it from a command-line
                # assignment, so the value is exactly "completed", which is valid.
                ("trailing space", "completed "),
                ("newline", "completed\ntouch MARKER")):
            with self.subTest(name=name):
                self.assert_injection_refused(reason, f"pwn-{name.replace(' ', '-')}")

    def test_dry_run_passes_reason_from_the_environment_never_expanded(self):
        done = self.make("-n", "issue-close", "N=7", "REASON=not-planned")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn('issue-close.sh "7" "$REASON"', done.stdout)
        self.assertEqual(self.calls(), [])

    def test_both_makefiles_share_the_reason_check(self):
        for path in (REPO / "Makefile", KIT / "templates" / "Makefile.github.mk"):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("issue-reason-ok = $(and $(filter 1,$(words $(1)))", text)
                self.assertIn("$(call issue-reason-ok,$(value REASON))", text)
                self.assertIn('"$$REASON"', text)
                self.assertNotIn('"$(REASON)"', text)

    def test_refused_by_the_script_closes_nothing(self):
        self.config(view=issue([engineer(1)]))
        done = self.make("issue-close", "N=7")
        self.assertNotEqual(done.returncode, 0)
        self.assertEqual(self.closes(), [])

    def test_listed_in_help_and_in_the_module_template(self):
        self.assertIn("issue-close", self.make("help").stdout)
        module = (KIT / "templates" / "Makefile.github.mk").read_text(encoding="utf-8")
        self.assertIn("issue-close:", module)
        self.assertIn("scripts/issue-close.sh", module)


class DocsTest(unittest.TestCase):
    @staticmethod
    def flat(path):
        return " ".join(path.read_text(encoding="utf-8").split())

    def test_close_layout_names_the_matched_lines(self):
        text = self.flat(KIT / "procedures" / "orchestrator-comments.md")
        for phrase in ("`QA PASS commit: <7 to 40 hex>`", "`Merge commit: <7 to 40 hex>`",
                       "`Verify: <text>`", "`Summary: <path>`", "`Human approved diff: yes`",
                       "`Orchestrator: Close as not planned`", "`Human approved closure: <YYYY-MM-DD>`",
                       "`Backlog review: <path or comment URL>`", "make issue-close"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_script_reads_the_labels_the_layout_names(self):
        script = SCRIPT.read_text(encoding="utf-8")
        for label in ("QA PASS commit", "Merge commit", "Verify", "Summary", "Human approved diff",
                      "Human approved closure", "Backlog review", "Close as not planned"):
            with self.subTest(label=label):
                self.assertIn(label, script)

    def test_process_names_the_wrapper_and_forbids_raw_close(self):
        text = self.flat(KIT / "process.md")
        self.assertIn("with `make issue-close N=<number>`", text)
        self.assertIn("never a raw `gh issue close`", text)
        self.assertIn("Editing an issue asks the human", text)
        self.assertNotIn("Editing or closing an issue asks the human", text)

    def test_qa_verdict_line_is_pinned(self):
        self.assertIn("The comment starts with `QA: PASS` or `QA: FAIL`",
                      self.flat(KIT / "team" / "qa-engineer.md"))

    def test_module_header_says_which_wrapper_closes(self):
        text = self.flat(KIT / "templates" / "Makefile.github.mk")
        self.assertIn("Only issue-close can close, one issue", text)

    def test_blueprints_names_the_script_and_target(self):
        text = self.flat(KIT / "blueprints.md")
        self.assertIn("`issue-close`", text)
        self.assertIn("`scripts/issue-close.sh`", text)

    def test_decision_record_is_committed_and_indexed(self):
        self.assertTrue((REPO / "_docs" / "decisions" / "119-issue-close.md").is_file())
        self.assertIn("_docs/decisions/119-issue-close.md", (REPO / "_docs" / "index.md").read_text())


if __name__ == "__main__":
    unittest.main()
