"""Fixed fields for role returns, findings, QA comments and messages to the human (issue #198).

The script (agent-kit/scripts/check-format.py) runs as a subprocess with `python3 -I -B` on
files written under .scratch/, from the repo root, as `make check-format` runs it. The
accepted examples are read from the docs that define each layout, so a doc example and the
script cannot drift apart.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
SCRIPT = KIT / "scripts" / "check-format.py"
SETTINGS = KIT / "scripts" / "settings.py"
SCRATCH = REPO / ".scratch"
FORMATS_DOC = KIT / "procedures" / "formats.md"
QA_DOC = KIT / "team" / "qa-engineer.md"
ASK_DOC = KIT / "procedures" / "asking-the-human.md"
FINDINGS = REPO / "_docs" / "records" / "findings"

_spec = importlib.util.spec_from_file_location("kit_check_format", SCRIPT)
check_format = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_format)

BOM = chr(0xFEFF)


def example(path: Path, first: str) -> str:
    """The fenced example in a doc whose first line starts with `first`."""
    for block in re.findall(r"```\n(.*?)```", path.read_text(encoding="utf-8"), re.S):
        if block.startswith(first):
            return block
    raise AssertionError(f"no example starting {first!r} in {path}")


RETURN = example(FORMATS_DOC, "Status:")
FINDING = example(FORMATS_DOC, "Id:")
QA = example(QA_DOC, "QA:")
MESSAGE = example(ASK_DOC, "Needs you:")
QA_N = "12"
FINDING_N = "198"
# The return example without its request, for the `Needs the human: none` cases.
RETURN_NONE = RETURN.split("\n\n", 1)[0].replace("Needs the human: yes", "Needs the human: none") + "\n"


def swap(text: str, old: str, new: str) -> str:
    assert old in text, old
    return text.replace(old, new, 1)


class Runner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SCRATCH.mkdir(exist_ok=True)
        cls.folder = Path(tempfile.mkdtemp(prefix="test-check-format-", dir=SCRATCH))
        cls.count = 0

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.folder, ignore_errors=True)

    def put(self, data) -> str:
        type(self).count += 1
        path = self.folder / f"case-{self.count}.md"
        if isinstance(data, str):
            path.write_text(data, encoding="utf-8", newline="")
        else:
            path.write_bytes(data)
        return str(path.relative_to(REPO))

    def run_script(self, *args):
        return subprocess.run([sys.executable, "-I", "-B", str(SCRIPT), *args], cwd=REPO,
                              capture_output=True, text=True, timeout=60)

    def check(self, kind: str, text, n: str | None = None):
        args = [kind, self.put(text)] + ([n] if n else [])
        return self.run_script(*args)

    def assert_ok(self, kind, text, n=None):
        done = self.check(kind, text, n)
        self.assertEqual((done.returncode, done.stdout, done.stderr), (0, "ok\n", ""))

    def assert_refused(self, kind, text, n=None, reason=None):
        done = self.check(kind, text, n)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(done.stdout, "")
        lines = done.stderr.splitlines()
        self.assertTrue(lines)
        for line in lines:
            self.assertRegex(line, r"^check-format: \.scratch/\S+ line [0-9]+: ")
        if reason:
            self.assertIn(reason, done.stderr)
        return done


class LineRuleTest(Runner):
    """C1: the line rule, each refused case for a finding and a role return."""

    CASES = {
        "indented": "  {l}: {v}",
        "tab indent": "\t{l}: {v}",
        "list marker": "- {l}: {v}",
        "star marker": "* {l}: {v}",
        "numbered": "1. {l}: {v}",
        "wrong case": "{lower}: {v}",
        "no space": "{l}:{v}",
        "two spaces": "{l}:  {v}",
        "tab after colon": "{l}:\t{v}",
        "empty value": "{l}:",
        "only a space": "{l}: ",
    }

    def cases(self, label, value):
        for name, form in self.CASES.items():
            yield name, form.format(l=label, v=value, lower=label.lower())

    def test_each_refused_form_in_a_finding(self):
        for name, line in self.cases("Impact", "L"):
            with self.subTest(case=name):
                self.assert_refused("finding", swap(FINDING, "Impact: L", line), FINDING_N)

    def test_each_refused_form_in_a_role_return(self):
        for name, line in self.cases("Verdict", "none"):
            with self.subTest(case=name):
                self.assert_refused("return", swap(RETURN_NONE, "Verdict: none", line))

    def test_reasons_name_the_rule(self):
        self.assert_refused("finding", swap(FINDING, "Impact: L", "- Impact: L"), FINDING_N,
                            "must start at column 1, with no indent or list marker")
        self.assert_refused("finding", swap(FINDING, "Impact: L", "impact: L"), FINDING_N,
                            "must be written `Impact:`")
        self.assert_refused("finding", swap(FINDING, "Impact: L", "Impact:  L"), FINDING_N,
                            "exactly one space")
        self.assert_refused("finding", swap(FINDING, "Impact: L", "Impact:"), FINDING_N, "empty value")

    def test_crlf_reads_as_lf(self):
        self.assert_ok("finding", FINDING.replace("\n", "\r\n"), FINDING_N)
        self.assert_ok("return", RETURN.replace("\n", "\r\n"))

    def test_a_byte_order_mark_is_refused(self):
        for kind, text, n in (("finding", FINDING, FINDING_N), ("return", RETURN, None)):
            with self.subTest(kind=kind):
                self.assert_refused(kind, BOM + text, n, "line 1: starts with a UTF-8 byte order mark")


class ReturnTest(Runner):
    """C2: the role return."""

    def test_the_formats_example_is_accepted(self):
        self.assert_ok("return", RETURN)
        self.assert_ok("return", RETURN_NONE)

    def test_example_has_ten_fields_and_a_request(self):
        head, request = RETURN.split("\n\n", 1)
        self.assertEqual([line.split(":")[0] for line in head.splitlines()],
                         ["Status", "Issue", "Commit", "Verdict", "Findings", "Decisions",
                          "Needs the human", "Recommendation", "Detail", "Checkpoint"])
        self.assertTrue(request.startswith("Approval needed: "))

    def test_refused(self):
        cases = {
            "an eleventh field line": (RETURN_NONE + "Extra: x\n", "nothing may follow"),
            "missing Recommendation": (re.sub(r"Recommendation: .*\n", "", RETURN_NONE), "Recommendation"),
            "Status: finished": (swap(RETURN_NONE, "Status: done", "Status: finished"), "'finished'"),
            "missing Verdict": (swap(RETURN_NONE, "Verdict: none\n", ""), "Verdict"),
            "two lines swapped": (swap(RETURN_NONE, "Status: done\nIssue: #198", "Issue: #198\nStatus: done"), None),
            "yes with nothing after": (swap(RETURN_NONE, "Needs the human: none", "Needs the human: yes"),
                                       "with `Needs the human: yes`"),
            "none with a request after": (swap(RETURN, "Needs the human: yes", "Needs the human: none"),
                                          "nothing may follow"),
            "a request with neither label": (swap(RETURN, "Approval needed: ", "Please approve: "),
                                             "`Approval needed: ` or `Decision needed: `"),
            "a second request with neither label": (RETURN + "\nCan you look?\n", "found 'Can you look?'"),
            "no blank line before the request": (swap(RETURN, "Checkpoint: none\n\n", "Checkpoint: none\n"),
                                                 "one blank line"),
            "Commit in capitals": (swap(RETURN_NONE, "Commit: 1a2b3c4", "Commit: 1A2B3C4"), "Commit has"),
            "Commit too short": (swap(RETURN_NONE, "Commit: 1a2b3c4", "Commit: 1a2b3c"), "Commit has"),
            "Issue without #": (swap(RETURN_NONE, "Issue: #198", "Issue: 198"), "Issue has"),
            "Verdict pass": (swap(RETURN_NONE, "Verdict: none", "Verdict: pass"), "Verdict has"),
            "Findings other grammar": (swap(RETURN_NONE, "Findings: none", "Findings: 1 fail, 2 log"), "Findings has"),
            "Decisions without the space": (swap(RETURN_NONE, "Decisions: none", "Decisions: D-1-1,D-1-2"), "Decisions has"),
            "Needs the human no": (swap(RETURN_NONE, "Needs the human: none", "Needs the human: no"), None),
            "Detail with ..": (swap(RETURN_NONE, "Detail: .scratch/engineer-198.md", "Detail: ../x.md"), "Detail has"),
            "Detail absolute": (swap(RETURN_NONE, "Detail: .scratch/engineer-198.md", "Detail: /etc/passwd"), "Detail has"),
            "Detail http": (swap(RETURN_NONE, "Detail: .scratch/engineer-198.md", "Detail: http://x.y/z"), "Detail has"),
            "Checkpoint with ..": (swap(RETURN_NONE, "Checkpoint: none", "Checkpoint: a/../b"), "Checkpoint has"),
        }
        for name, (text, reason) in cases.items():
            with self.subTest(case=name):
                self.assert_refused("return", text, reason=reason)

    def test_accepted_values(self):
        for old, new in (("Commit: 1a2b3c4", "Commit: none"), ("Commit: 1a2b3c4", "Commit: " + "a" * 40),
                         ("Findings: none", "Findings: 0 fail / 3 log"),
                         ("Decisions: none", "Decisions: D-198-1, D-12-30"),
                         ("Detail: .scratch/engineer-198.md", "Detail: https://github.com/o/r/issues/1#issuecomment-2"),
                         ("Checkpoint: none", "Checkpoint: _session-summaries/x.md"),
                         ("Status: done", "Status: stopped-early"), ("Verdict: none", "Verdict: FAIL")):
            with self.subTest(value=new):
                self.assert_ok("return", swap(RETURN_NONE, old, new))
        self.assert_ok("return", RETURN + "\nDecision needed: which option?\n- Context: x\n")

    def test_a_request_may_keep_its_diff_in_full(self):
        # F-198-4: a diff's empty context line (one space) or a blank line inside a fence
        # does not start a new request.
        diff = "diff --git a/x b/x\n@@ -1,3 +1,3 @@\n context\n{gap}\n-old\n+new\n"
        for name, gap in (("no empty context line", " same"), ("an empty context line", " "),
                          ("an empty line", "")):
            body = diff.format(gap=gap)
            with self.subTest(case=name, form="fenced"):
                self.assert_ok("return", RETURN + "\n```diff\n" + body + "```\n")
            if gap != "":
                with self.subTest(case=name, form="bare"):
                    self.assert_ok("return", RETURN + body)
        self.assert_ok("return", RETURN + "  indented line after the request\n\n    more indented\n")
        self.assert_refused("return", RETURN + "\nNot a request\n", reason="found 'Not a request'")
        self.assert_refused("return", RETURN + "\n```\nx\n```\n\n-old\n", reason="found '-old'")

    def test_the_role_files_end_with_the_return(self):
        for role in ("pm", "software-engineer", "qa-engineer"):
            text = " ".join((KIT / "team" / f"{role}.md").read_text(encoding="utf-8").split())
            with self.subTest(role=role):
                self.assertIn("Your final message is the role return of `_docs/agent-kit/procedures/formats.md`", text)


class FindingTest(Runner):
    """C3 and C4: the finding and its id."""

    def test_the_formats_example_is_accepted(self):
        self.assert_ok("finding", FINDING, FINDING_N)

    def test_labels_map_to_the_json_keys(self):
        labels = [line.split(":")[0] for line in FINDING.splitlines()]
        self.assertEqual([check_format.key_of(label) for label in labels], list(check_format.FINDING_FIELDS))
        self.assertEqual(check_format.FINDING_FIELDS,
                         ("id", "impact", "effort", "scope", "criterion", "category", "group",
                          "related", "recommendation", "what", "how_found"))
        self.assertEqual(check_format.key_of("How found"), "how_found")

    def test_refused(self):
        cases = {
            "Impact: medium": (swap(FINDING, "Impact: L", "Impact: medium"), "Impact has 'medium'"),
            "missing Scope": (swap(FINDING, "Scope: in\n", ""), "Scope"),
            "Category: style": (swap(FINDING, "Category: defect", "Category: style"), "Category has"),
            "Criterion: 3": (swap(FINDING, "Criterion: C8", "Criterion: 3"), "Criterion has"),
            "Criterion: C03": (swap(FINDING, "Criterion: C8", "Criterion: C03"), "Criterion has"),
            "Related: its own id": (swap(FINDING, "Related: none", "Related: F-198-1"), "own id"),
            "Group: Restore Checks": (swap(FINDING, "Group: check-format-usage", "Group: Restore Checks"), "Group has"),
            "Group: double hyphen": (swap(FINDING, "Group: check-format-usage", "Group: a--b"), "Group has"),
            "Group: a dot": (swap(FINDING, "Group: check-format-usage", "Group: python-3.13"), "Group has"),
            "Group: 41 characters": (swap(FINDING, "Group: check-format-usage", "Group: " + "a" * 41), "Group has"),
            "Effort: M": (swap(FINDING, "Effort: S", "Effort: M"), "Effort has"),
            "Scope: inside": (swap(FINDING, "Scope: in", "Scope: inside"), "Scope has"),
            "a twelfth line": (FINDING + "Extra: x\n", "nothing may follow"),
            "no finding": ("\n", "no finding block"),
        }
        for name, (text, reason) in cases.items():
            with self.subTest(case=name):
                self.assert_refused("finding", text, FINDING_N, reason)

    def test_ids(self):
        cases = {
            "L1": "Id: L1", "N2": "Id: N2", "leading zero": "Id: F-198-01",
            "other issue": "Id: F-196-1", "zero": "Id: F-198-0",
        }
        for name, line in cases.items():
            with self.subTest(case=name):
                self.assert_refused("finding", swap(FINDING, "Id: F-198-1", line), FINDING_N, "Id has")

    def test_ids_need_not_start_at_1_but_are_unique(self):
        self.assert_ok("finding", swap(FINDING, "Id: F-198-1", "Id: F-198-7"), FINDING_N)
        second = swap(FINDING, "Related: none", "Related: F-198-1")
        self.assert_refused("finding", FINDING + "\n" + second, FINDING_N, "used twice")
        self.assert_ok("finding", FINDING + "\n" + swap(second, "Id: F-198-1", "Id: F-198-2"), FINDING_N)

    def test_the_logged_findings_pass_the_dict_check(self):
        for number in (196, 197):
            data = json.loads((FINDINGS / f"{number}.json").read_text(encoding="utf-8"))
            for finding in data["findings"]:
                with self.subTest(finding=finding["id"]):
                    self.assertEqual(tuple(finding), check_format.FINDING_FIELDS)
                    self.assertEqual(check_format.check_finding(finding, number), [])

    def test_the_dict_check_refuses_what_the_text_check_refuses(self):
        good = {key: value for key, value in zip(check_format.FINDING_FIELDS,
                                                 [line.split(": ", 1)[1] for line in FINDING.splitlines()])}
        self.assertEqual(check_format.check_finding(good, 198), [])
        for key, value in (("impact", "medium"), ("related", "F-198-1"), ("group", "Restore Checks"),
                           ("recommendation", "none"), ("what", ""), ("what", "a\nb"), ("id", "F-197-1")):
            with self.subTest(key=key, value=value):
                bad = dict(good, **{key: value})
                self.assertEqual([k for k, _ in check_format.check_finding(bad, 198)], [key])
        missing = {k: v for k, v in good.items() if k != "scope"}
        self.assertNotEqual(check_format.check_finding(missing, 198), [])
        self.assertNotEqual(check_format.check_finding(dict(good, extra="x"), 198), [])
        self.assertNotEqual(check_format.check_finding(dict(good, impact=1), 198), [])


def qa_comment(ids, verdict="FAIL", counts=None):
    blocks = []
    for number, finding_id in enumerate(ids):
        blocks.append(swap(FINDING, "Id: F-198-1", f"Id: {finding_id}"))
    counts = counts or f"0 fail / {len(ids)} log"
    return f"QA: {verdict}\nCommit: 1a2b3c4\nFindings: {counts}\n\n" + "\n".join(blocks) + "\nCriteria\n- [x] C1. x - PASS\n"


class QaCommentTest(Runner):
    """C4 and C5: the QA comment."""

    def test_the_qa_engineer_example_is_accepted(self):
        self.assert_ok("qa", QA, QA_N)

    def test_findings_numbered_as_in_197s_first_launch_are_refused(self):
        text = qa_comment([f"L{n}" for n in range(1, 7)], counts="0 fail / 6 log")
        done = self.assert_refused("qa", text, "197", "Id has 'L1'")
        self.assertEqual(done.stderr.count("Id has"), 6)

    def test_ids_continue_and_must_be_this_issues(self):
        self.assert_ok("qa", qa_comment(["F-197-7", "F-197-8"]), "197")
        self.assert_refused("qa", qa_comment(["F-197-01"]), "197", "Id has")
        self.assert_refused("qa", qa_comment(["F-196-1"]), "197", "Id has")
        self.assert_refused("qa", qa_comment(["F-197-1", "F-197-1"]), "197", "used twice")

    def test_refused(self):
        cases = {
            "PASS with notes": (swap(QA, "QA: FAIL", "QA: PASS (with notes)"), "line 1 must be exactly"),
            "lower case": (swap(QA, "QA: FAIL", "QA: fail"), "line 1 must be exactly"),
            "missing Commit": (swap(QA, "Commit: 1a2b3c4\n", ""), "Commit"),
            "Checked at instead": (swap(QA, "Commit: 1a2b3c4", "Checked at `1a2b3c4`."), "Commit"),
            "counts above the blocks": (swap(QA, "Findings: 1 fail / 1 log", "Findings: 1 fail / 2 log"), "do not match"),
            "counts below the blocks": (swap(QA, "Findings: 1 fail / 1 log", "Findings: 0 fail / 1 log"), "do not match"),
            "PASS with a fail": (swap(QA, "QA: FAIL", "QA: PASS"), "QA: PASS with 1 fail"),
            "a listed finding label in the detail": (QA + "- Impact: L\n", "outside a finding block"),
            "an indented label in the detail": (QA + "  What: x\n", "outside a finding block"),
            "a label at column 1 in the detail": (QA + "Recommendation: x\n", "outside a finding block"),
            "no blank line before the detail": (swap(QA, "How found: Read the diff.\n\n", "How found: Read the diff.\n"),
                                                "blank line before the detail"),
        }
        for name, (text, reason) in cases.items():
            with self.subTest(case=name):
                self.assert_refused("qa", text, QA_N, reason)

    def test_trailing_spaces_after_the_verdict_are_allowed(self):
        self.assert_ok("qa", swap(QA, "QA: FAIL\n", "QA: FAIL  \n"), QA_N)
        self.assert_ok("qa", "QA: PASS\nCommit: 1a2b3c4\nFindings: 0 fail / 0 log\n\nCriteria\n- [x] C1. x - PASS\n", QA_N)

    def test_issue_close_reads_the_new_layout(self):
        script = (KIT / "scripts" / "issue-close.sh").read_text(encoding="utf-8")
        self.assertIn(r're.match(r"QA: PASS\b", first)', script)
        self.assertIn("if named not in latest[2]:", script)  # the commit appears in line 2

    def test_the_layout_doc(self):
        text = " ".join(QA_DOC.read_text(encoding="utf-8").split())
        self.assertIn("make check-format KIND=qa N=<n> FILE=<file>", text)
        self.assertIn("a finding with `Criterion: none`", text)


class MessageTest(Runner):
    """C6: the message to the human."""

    def test_the_asking_the_human_example_is_accepted(self):
        self.assert_ok("message", MESSAGE)
        self.assert_ok("message", MESSAGE + "\nApproval needed: anything\n- Why: x\n")

    def test_refused(self):
        cases = {
            "decision without Recommended": (swap(MESSAGE, "Recommended: No; drop the log line in #14.\n", ""), "Recommended"),
            "decision without Impact": (swap(MESSAGE, "Question: Should signup log usernames at all?\nImpact: L\n",
                                             "Question: Should signup log usernames at all?\n"), "Impact"),
            "Impact: High": (swap(MESSAGE, "Impact: L", "Impact: High"), "Impact has 'High'"),
            "counts above the blocks": (swap(MESSAGE, "1 decision points", "2 decision points"), "Decision block"),
            "ship-or-fix counts": (swap(MESSAGE, "1 ship-or-fix", "0 ship-or-fix"), "Ship-or-fix block"),
            "missing Status": (MESSAGE.rsplit("\nStatus:", 1)[0], "Status"),
            "first line wording": (swap(MESSAGE, "Needs you: 1 decision points", "Needs you: 1 decisions"), "Needs you has"),
            "Effort: L": (swap(MESSAGE, "Effort: S", "Effort: L"), "Effort has"),
            "decision id": (swap(MESSAGE, "Decision: D-12-1", "Decision: D12"), "Decision has"),
            "ship-or-fix id": (swap(MESSAGE, "Ship-or-fix: F-12-2", "Ship-or-fix: L2"), "Ship-or-fix has"),
        }
        for name, (text, reason) in cases.items():
            with self.subTest(case=name):
                self.assert_refused("message", text, reason=reason)

    def test_the_doc_keeps_its_other_layouts(self):
        text = ASK_DOC.read_text(encoding="utf-8")
        for heading in ("## Approval request", "## Decision question", "## Message to the human", "## Spec note"):
            self.assertIn(heading, text)


class RecommendationTest(Runner):
    """C7: a recommendation is required, in each format that carries one."""

    REFUSED = ("none", "none,", "none because x", "none, because", "None, because x", "none, because   ")

    def test_refused_values(self):
        targets = (
            ("return", RETURN_NONE, "Recommendation: Approve the staged commit, then launch QA.", "Recommendation", None),
            ("finding", FINDING, "Recommendation: Name the allowed kinds in the usage line.", "Recommendation", FINDING_N),
            ("message", MESSAGE, "Recommended: No; drop the log line in #14.", "Recommended", None),
        )
        for kind, text, line, label, n in targets:
            for value in self.REFUSED:
                with self.subTest(kind=kind, value=value):
                    self.assert_refused(kind, swap(text, line, f"{label}: {value}"), n, label)

    def test_none_with_a_reason_is_accepted(self):
        self.assert_ok("return", swap(RETURN_NONE, "Recommendation: Approve the staged commit, then launch QA.",
                                      "Recommendation: none, because the work is done."))
        self.assert_ok("message", swap(MESSAGE, "Recommended: Ship; fix it with #14.", "Recommended: none, because x"))
        self.assert_ok("return", swap(RETURN_NONE, "Recommendation: Approve the staged commit, then launch QA.",
                                      "Recommendation: Nonetheless, launch QA."))


class CommandTest(Runner):
    """C8: the command, its usage errors and its output."""

    def make(self, *args):
        return subprocess.run(["make", "-s", "--no-print-directory", "check-format", *args], cwd=REPO,
                              capture_output=True, text=True, timeout=60)

    def test_make_prints_ok_for_each_doc_example(self):
        for kind, text, n in (("return", RETURN, None), ("finding", FINDING, FINDING_N),
                              ("qa", QA, QA_N), ("message", MESSAGE, None)):
            with self.subTest(kind=kind):
                done = self.make(f"KIND={kind}", f"FILE={self.put(text)}", *([f"N={n}"] if n else []))
                self.assertEqual((done.returncode, done.stdout, done.stderr), (0, "ok\n", ""))

    def test_make_refuses_and_reports(self):
        done = self.make("KIND=finding", f"FILE={self.put(FINDING)}", "N=197")
        self.assertEqual(done.returncode, 2)  # make's exit for a failed recipe
        self.assertIn("Id has 'F-198-1'", done.stderr)

    def test_usage_errors_exit_2_and_read_nothing(self):
        file = self.put(RETURN)
        cases = {
            "unknown kind": ("KIND=bogus", "FILE=.scratch/x"),
            "two kinds": ("KIND=qa return", f"FILE={file}", "N=1"),
            "outside scratch": ("KIND=return", "FILE=../x"),
            "dot dot inside": ("KIND=return", "FILE=.scratch/../x"),
            "not under scratch": ("KIND=return", "FILE=README.md"),
            "no file": ("KIND=return",),
            "two words": ("KIND=return", f"FILE={file} {file}"),
            "qa without N": ("KIND=qa", f"FILE={file}"),
            "finding with a bad N": ("KIND=finding", f"FILE={file}", "N=01"),
            "finding with a word N": ("KIND=finding", f"FILE={file}", "N=x"),
            "shell in N": ("KIND=qa", f"FILE={file}", "N=$(shell touch .scratch/pwned)"),
        }
        for name, args in cases.items():
            with self.subTest(case=name):
                done = self.make(*args)
                self.assertEqual(done.returncode, 2, done.stderr)
                self.assertIn("Usage: make check-format", done.stderr)
                self.assertEqual(done.stdout, "")
        self.assertFalse((SCRATCH / "pwned").exists())

    def test_the_script_refuses_bad_arguments_with_2(self):
        file = self.put(RETURN)
        for args in ((), ("bogus", file), ("return", "../x"), ("return", "/etc/passwd"), ("return", ".scratch/a b"),
                     ("qa", file), ("qa", file, "0"), ("return", file, "5"), ("return", file, "5", "6")):
            with self.subTest(args=args):
                done = self.run_script(*args)
                self.assertEqual(done.returncode, 2)
                self.assertIn("Usage:", done.stderr)

    def test_unreadable_files_give_one_problem_line(self):
        cases = {
            "missing": (".scratch/no-such-file-198.md", "not found"),
            "non-UTF-8": (self.put(b"Status: \xff\n"), "cannot be read as UTF-8 text"),
            "a folder": (str(self.folder.relative_to(REPO)), "not a regular file"),
        }
        for name, (file, reason) in cases.items():
            with self.subTest(case=name):
                done = self.run_script("return", file)
                self.assertEqual(done.returncode, 1)
                self.assertEqual(done.stderr, f"check-format: {file}: {reason}\n")

    def test_a_symlink_is_not_followed(self):
        link = self.folder / "link.md"
        link.symlink_to(REPO / "README.md")
        done = self.run_script("return", str(link.relative_to(REPO)))
        self.assertEqual(done.returncode, 1)
        self.assertIn("symbolic link", done.stderr)

    def test_a_long_bad_value_gives_a_short_reason(self):
        done = self.assert_refused("finding", swap(FINDING, "Impact: L", "Impact: " + "x" * 5000), FINDING_N)
        for line in done.stderr.splitlines():
            self.assertLess(len(line), 200, line)
        done = self.assert_refused("return", swap(RETURN_NONE, "Status: done", "S" * 5000))
        for line in done.stderr.splitlines():
            self.assertLess(len(line), 200, line)

    def test_both_makefiles_define_the_target(self):
        for path, root in ((REPO / "Makefile", "agent-kit"), (KIT / "templates" / "Makefile.mk", "_docs/agent-kit")):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertRegex(text, r"(?m)^check-format: ## ")
                self.assertIn(f'@python3 -B {root}/scripts/check-format.py "$$KIND" "$$FILE"', text)
                self.assertIn("$(call issue-file-ok,$(value FILE))", text)
        self.assertRegex((KIT / "templates" / "Makefile.mk").read_text(encoding="utf-8"), r"(?m)^issue-file-ok = ")
        self.assertNotRegex((KIT / "templates" / "Makefile.github.mk").read_text(encoding="utf-8"), r"(?m)^issue-file-ok = ")


class ParserStyleTest(unittest.TestCase):
    """C9: one parser style, standard library only."""

    def test_it_reuses_the_settings_helpers(self):
        self.assertIs(check_format.clip, check_format.settings.clip)
        self.assertIs(check_format.echo, check_format.settings.echo)
        self.assertIs(check_format.lines_of, check_format.settings.lines_of)
        self.assertEqual(Path(check_format.settings.__file__).resolve(), SETTINGS.resolve())

    def test_it_runs_isolated(self):
        done = subprocess.run([sys.executable, "-I", "-B", "-c",
                               "import importlib.util, sys; s = importlib.util.spec_from_file_location('c', sys.argv[1]);"
                               " m = importlib.util.module_from_spec(s); s.loader.exec_module(m);"
                               " print(m.clip is m.settings.clip)", str(SCRIPT)],
                              cwd="/", capture_output=True, text=True, timeout=60)
        self.assertEqual(done.stdout, "True\n", done.stderr)

    def test_imports_are_standard_library_only(self):
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                names.add((node.module or "").split(".")[0])
        self.assertEqual(names - set(sys.stdlib_module_names), set())

    def test_one_table_of_formats(self):
        self.assertEqual(set(check_format.FORMATS), {"return", "finding", "qa", "message"})
        self.assertIn("starts no process", " ".join(check_format.__doc__.split()))
        source = SCRIPT.read_text(encoding="utf-8")
        for forbidden in ("subprocess", "os.system", "eval(", "exec("):
            self.assertNotIn(forbidden, source.replace("exec_module", ""))


class DocsTest(unittest.TestCase):
    """C10: each format is defined once, and the pointers to it."""

    def flat(self, path):
        return " ".join(path.read_text(encoding="utf-8").split())

    def test_formats_doc_holds_the_return_and_the_finding(self):
        text = FORMATS_DOC.read_text(encoding="utf-8")
        self.assertIn("## Role return", text)
        self.assertIn("## Finding", text)
        self.assertNotIn("QA: PASS", text)
        self.assertNotIn("Needs you:", text)

    def test_process_says_to_read_the_fields(self):
        text = self.flat(KIT / "process.md")
        self.assertIn("Read its fields, and open `Detail:` only when", text)

    def test_readme_lists_the_new_files(self):
        text = (KIT / "README.md").read_text(encoding="utf-8")
        self.assertRegex(text, r"procedures/ .*formats\.md")
        self.assertIn("check-format.py", text)


if __name__ == "__main__":
    unittest.main()
