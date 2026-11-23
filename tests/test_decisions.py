"""The decision ledger and `make decisions` (issue #204, C1 to C5 and C7).

The script (agent-kit/scripts/decisions.py) runs as a subprocess with `python3 -I -B` in a
throwaway project folder under .scratch/ holding an agent-kit.conf, ledger files in
_docs/records/decisions/ and, with N, the issue's dump, as `make decisions N=<n>` runs it
after writing the dump.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
SCRIPT = KIT / "scripts" / "decisions.py"
SCRATCH = REPO / ".scratch"
OWNER = "owner-account"
N = 12


def load_script():
    spec = importlib.util.spec_from_file_location("kit_decisions_for_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stamp(days_ago: int = 0) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%MZ")


def question(index: int = 1, letters: str = "AB", recommended="A") -> dict:
    item = {"q": f"q{index}", "text": f"Question {index}?",
            "options": {letter: f"option {letter}" for letter in letters}}
    if recommended is not None:
        item["recommended"] = recommended
    return item


def point(k: int, effort: str = "S", mode: str = "continue", kind: str = "choice", impact: str = "L",
          issue: int = N, at: str | None = None, questions=None, dependents=("agent-kit/process.md",),
          rollback: str | None = "revert the edit in agent-kit/process.md", **extra) -> dict:
    item = {"event": "open", "id": f"D-{issue}-{k}", "at": at or stamp(), "kind": kind, "mode": mode,
            "impact": impact, "effort": effort, "questions": questions or [question()],
            "dependents": list(dependents)}
    if rollback is not None and mode == "continue":
        item["rollback"] = rollback
    item.update(extra)
    return item


def answer(k: int, text: str, issue: int = N) -> dict:
    return {"event": "answer", "id": f"D-{issue}-{k}", "at": stamp(), "answer": text}


def reworked(k: int, commit: str = "1a2b3c4", issue: int = N) -> dict:
    return {"event": "reworked", "id": f"D-{issue}-{k}", "at": stamp(), "commit": commit}


def ruling(*lines: str) -> dict:
    return {"author": {"login": OWNER}, "body": "Orchestrator: Ruling\nHuman ruled: 2026-11-23\n" + "\n".join(lines),
            "createdAt": "2026-11-23T10:00:00Z"}


class Fixture(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)
        self.project = Path(tempfile.mkdtemp(prefix="test-decisions-", dir=SCRATCH))
        self.addCleanup(shutil.rmtree, self.project, True)
        (self.project / ".scratch").mkdir()
        (self.project / "agent-kit.conf").write_text("\n", encoding="utf-8")
        self.ledger = self.project / "_docs" / "records" / "decisions"
        self.dump()

    def dump(self, comments=(), number: int = N) -> None:
        data = {"number": number, "title": "T", "body": "", "state": "OPEN", "labels": [],
                "author": {"login": OWNER}, "comments": list(comments), "repositoryOwner": {"login": OWNER}}
        (self.project / ".scratch" / f"issue-{number}.json").write_text(json.dumps(data), encoding="utf-8")

    def write(self, *entries, issue: int = N, raw: str | None = None) -> Path:
        self.ledger.mkdir(parents=True, exist_ok=True)
        path = self.ledger / f"{issue}.jsonl"
        text = raw if raw is not None else "".join(json.dumps(e) + "\n" for e in entries)
        path.write_text(text, encoding="utf-8")
        return path

    def run_script(self, *args):
        return subprocess.run([sys.executable, "-I", "-B", str(SCRIPT), *args], cwd=self.project,
                              capture_output=True, text=True, timeout=60)

    def lines(self, *args, code: int = 0) -> list:
        done = self.run_script(*args)
        self.assertEqual((done.returncode, done.stderr), (code, ""), done.stdout + done.stderr)
        return done.stdout.splitlines()

    def refused(self, reason: str, line: int | None = 1, issue: int = N) -> str:
        done = self.run_script(str(N))
        self.assertEqual((done.returncode, done.stdout), (1, ""), done.stderr)
        self.assertEqual(len(done.stderr.splitlines()), 1, done.stderr)
        place = f"decisions: _docs/records/decisions/{issue}.jsonl"
        if line is not None:
            place += f" line {line}: "
        self.assertTrue(done.stderr.startswith(place), done.stderr)
        self.assertIn(reason, done.stderr)
        return done.stderr


class EntryTest(Fixture):
    """C1: a decision point's fields, and what an entry may not hold."""

    def test_a_good_entry_is_listed(self):
        self.write(point(4, effort="R", impact="M", dependents=("agent-kit/process.md", "1a2b3c4", "#207"),
                         at=stamp(3)))
        self.assertEqual(self.lines(str(N)), [
            "D-12-4 impact M effort R points 2 mode continue age 3 dependents agent-kit/process.md, 1a2b3c4, #207",
            "open points 2, budget 3: within budget"])

    def test_refused_entries(self):
        no_effort = point(1)
        del no_effort["effort"]
        no_impact = point(1)
        del no_impact["impact"]
        cases = {
            "no effort": (no_effort, "missing key effort"),
            "effort 2": (point(1, effort="2"), "key effort must be one of S, R, E, not '2'"),
            "effort s": (point(1, effort="s"), "key effort must be one of S, R, E, not 's'"),
            "effort L": (point(1, effort="L"), "key effort must be one of S, R, E"),
            "no impact": (no_impact, "missing key impact"),
            "impact H": (point(1, impact="H"), "key impact must be one of L, M, C"),
            "impact S": (point(1, impact="S"), "key impact must be one of L, M, C"),
            "stored points": (point(1, points=1), "key points is not stored"),
            "stored points on a stop": (point(1, mode="stop", kind="spec", points=2), "key points is not stored"),
            "no recommendation": (point(1, questions=[question(recommended=None)]), "has no recommendation"),
            "second question without one": (point(1, questions=[question(), question(2, recommended=None)]),
                                            "question 2 has no recommendation"),
            "recommendation not offered": (point(1, questions=[question(recommended="C")]),
                                           "recommends 'C', which is not an offered option"),
            "recommendation lowercase": (point(1, questions=[question(recommended="a")]), "not an offered option"),
            "id of another issue": (point(1, issue=13), "id D-13-1 is not of issue 12"),
            "bad id": (dict(point(1), id="D12"), "key id must be `D-<issue>-<n>`"),
            "one option": (point(1, questions=[question(letters="A")]), "at least two lettered options"),
            "options out of order": (point(1, questions=[question(letters="AC")]), "lettered A, B, ... in order"),
            "question ids out of order": (point(1, questions=[question(2)]), "must have q `q1`"),
            "no questions": (point(1, questions=[]) | {"questions": []}, "at least one question"),
            "unknown key": (point(1, weight=2), "unknown key 'weight'"),
            "bad time": (point(1, at="2026-11-23 10:00"), "key at must be a UTC time"),
            "not a real time": (point(1, at="2026-13-40T10:00Z"), "key at is not a real time"),
            "dependents not a list": (point(1) | {"dependents": "a.md"}, "key dependents must be a list"),
            "stop point with a rollback": (point(1, mode="stop", kind="spec") | {"rollback": "x"},
                                           "a stop point has no rollback"),
        }
        for name, (entry, reason) in cases.items():
            with self.subTest(case=name):
                self.write(entry)
                self.refused(reason)

    def test_a_repeated_id(self):
        self.write(point(1), point(1, effort="R"))
        self.refused("id D-12-1 is used twice", line=2)

    def test_not_one_json_object(self):
        for raw, reason in (("{\"event\": \"open\"\n", "not one JSON object"), ("[1, 2]\n", "must be one JSON object"),
                            ("\n", "not one JSON object"), ('{"event": "open", "event": "answer"}\n', "written twice"),
                            (json.dumps(point(1)) + " " + json.dumps(point(2)) + "\n", "not one JSON object")):
            with self.subTest(raw=raw):
                self.write(raw=raw)
                self.refused(reason)

    def test_a_bad_line_is_named_by_its_number(self):
        self.write(raw=json.dumps(point(1)) + "\n" + json.dumps(point(2)) + "\nnot json\n")
        self.refused("not one JSON object", line=3)


class KindTest(Fixture):
    """C2 and C4: the kind names match process.md; a stop kind is never a continue point."""

    def test_kind_names_match_process_md(self):
        module = load_script()
        text = (KIT / "process.md").read_text(encoding="utf-8")
        section = text[text.index("**Stop kinds**"):text.index("**The continue kind**")]
        self.assertEqual(tuple(re.findall(r"(?m)^- `([a-z]+)`: ", section)), module.STOP_KINDS)
        self.assertEqual(len(module.STOP_KINDS), 13)
        self.assertEqual(module.CONTINUE_KINDS, ("choice",))
        after = text[text.index("**The continue kind**"):]
        self.assertIn("`choice`", after.split("\n\n", 1)[0])
        self.assertIn("`Needs the human: yes`", section)

    def test_every_stop_kind_is_refused_as_a_continue_point_and_accepted_as_a_stop(self):
        for kind in load_script().STOP_KINDS:
            with self.subTest(kind=kind):
                self.write(point(1, kind=kind))
                self.refused(f"kind {kind} is a stop kind")
                self.write(point(1, kind=kind, mode="stop"))
                self.assertEqual(self.lines(str(N)), [
                    "D-12-1 impact L effort S points 1 mode stop age 0 dependents agent-kit/process.md",
                    "open points 0, budget 3: within budget"])

    def test_refusals(self):
        no_rollback = point(1)
        del no_rollback["rollback"]
        cases = {
            "security as continue": (point(1, kind="security"), "kind security is a stop kind"),
            "unknown kind": (point(1, kind="hunch"), "key kind must be one of"),
            "unknown event": ({"event": "close", "id": "D-12-1", "at": stamp()}, "key event must be one of open, answer, reworked"),
            "no event": ({"id": "D-12-1"}, "key event must be one of"),
            "continue with no rollback": (no_rollback, "a continue point has no rollback"),
            "empty rollback": (point(1, rollback=" "), "key rollback must be one line of text"),
            "unknown mode": (point(1, mode="maybe"), "key mode must be stop or continue"),
        }
        for name, (entry, reason) in cases.items():
            with self.subTest(case=name):
                self.write(entry)
                self.refused(reason)

    def test_a_choice_may_be_a_stop_point(self):
        self.write(point(1, mode="stop", effort="E"))
        self.assertEqual(self.lines(str(N))[-1], "open points 0, budget 3: within budget")


class BudgetTest(Fixture):
    """C3: points from effort, counted over every ledger file, against DECISION_BUDGET."""

    def test_budget_reached_with_one_e(self):
        self.write(point(1, effort="E"))
        self.assertEqual(self.lines(str(N))[-1], "open points 3, budget 3: budget reached")

    def test_budget_reached_with_an_s_and_an_r(self):
        self.write(point(1, effort="S"), point(2, effort="R"))
        self.assertEqual(self.lines(str(N))[-1], "open points 3, budget 3: budget reached")

    def test_within_budget_with_one_r(self):
        self.write(point(1, effort="R"))
        self.assertEqual(self.lines(str(N))[-1], "open points 2, budget 3: within budget")

    def test_over_budget_with_an_e_and_an_s(self):
        self.write(point(1, effort="E"), point(2, effort="S"))
        self.assertEqual(self.lines(str(N), code=1)[-1], "open points 4, budget 3: over budget")

    def test_budget_0_with_one_open_continue_point(self):
        (self.project / "agent-kit.conf").write_text("DECISION_BUDGET=0\n", encoding="utf-8")
        self.write(point(1))
        self.assertEqual(self.lines(str(N), code=1)[-1], "open points 1, budget 0: over budget")
        self.assertEqual(self.lines(code=1)[-1], "open points 1, budget 0: over budget")

    def test_one_point_with_three_questions_counts_once(self):
        # The human's ruling of 2026-11-23: the questions met at one stop are one point.
        self.write(point(1, effort="S", questions=[question(1), question(2), question(3)]))
        self.assertEqual(self.lines(str(N)), [
            "D-12-1 impact L effort S points 1 mode continue age 0 dependents agent-kit/process.md",
            "open points 1, budget 3: within budget"])

    def test_a_session_ruling_applies(self):
        self.dump(comments=[ruling("Ruling: DECISION_BUDGET=8")])
        self.write(point(1, effort="E"))
        self.assertEqual(self.lines(str(N))[-1], "open points 3, budget 8: within budget")

    def test_a_project_line_applies(self):
        (self.project / "agent-kit.conf").write_text("DECISION_BUDGET=2\n", encoding="utf-8")
        self.write(point(1, effort="R"))
        self.assertEqual(self.lines(str(N))[-1], "open points 2, budget 2: budget reached")

    def test_stop_points_and_closed_points_do_not_count(self):
        self.write(point(1, effort="E", mode="stop", kind="money"), point(2, effort="E"), answer(2, "approve"),
                   point(3, effort="R"))
        self.assertEqual(self.lines(str(N))[-1], "open points 2, budget 3: within budget")

    def test_open_points_count_over_every_issue(self):
        self.write(point(1, effort="R"))
        self.write(point(1, effort="R", issue=13), issue=13)
        lines = self.lines(str(N), code=1)
        self.assertEqual(lines, [
            "D-12-1 impact L effort R points 2 mode continue age 0 dependents agent-kit/process.md",
            "open points 4, budget 3: over budget"])
        self.assertEqual(len(self.lines(code=1)), 3)

    def test_another_issues_open_points_show_without_its_lines(self):
        self.write(point(1, effort="R", issue=13), issue=13)
        self.assertEqual(self.lines(str(N)), ["open points 2, budget 3: within budget"])

    def test_policy_values_come_from_the_settings(self):
        code = SCRIPT.read_text(encoding="utf-8").split('"""', 2)[2]
        self.assertIn('check_format.setting(values, "DECISION_BUDGET")', code)
        self.assertIn("enumerate(EFFORTS)", code)
        for literal in ('"S": 1', "= 3\n", "budget = 3"):
            self.assertNotIn(literal, code)


class AnswerTest(Fixture):
    """C5: per-point answers, rework items and their refusals."""

    def two_questions(self, k: int, mode: str = "continue", kind: str = "choice") -> dict:
        return point(k, effort="R", mode=mode, kind=kind,
                     questions=[question(1, "AB", "A"), question(2, "ABC", "B")])

    def test_approve_closes_without_rework(self):
        self.write(self.two_questions(1), answer(1, "approve"))
        self.assertEqual(self.lines(str(N)), ["none"])

    def test_the_option_taken_adds_no_rework(self):
        for text in ("q1=A", "q2=B", "q1=A, q2=B", "q1=A,q2=B"):
            with self.subTest(answer=text):
                self.write(self.two_questions(1), answer(1, text))
                self.assertEqual(self.lines(str(N)), ["none"])

    def test_another_option_adds_a_rework_item_until_reworked(self):
        for text in ("q2=A", "q1=A, q2=C", "q1=B"):
            with self.subTest(answer=text):
                self.write(self.two_questions(1), answer(1, text))
                self.assertEqual(self.lines(str(N)), [
                    f"rework D-12-1 answer {text} rollback revert the edit in agent-kit/process.md",
                    "open points 0, budget 3: within budget"])
                self.write(self.two_questions(1), answer(1, text), reworked(1))
                self.assertEqual(self.lines(str(N)), ["none"])

    def test_reject_adds_a_rework_item(self):
        self.write(self.two_questions(1), point(2, effort="S"), answer(1, "reject"))
        self.assertEqual(self.lines(str(N)), [
            "D-12-2 impact L effort S points 1 mode continue age 0 dependents agent-kit/process.md",
            "rework D-12-1 answer reject rollback revert the edit in agent-kit/process.md",
            "open points 1, budget 3: within budget"])

    def test_answers_lower_the_open_points(self):
        entries = [point(1, effort="E"), point(2, effort="S")]
        self.write(*entries)
        self.assertEqual(self.lines(str(N), code=1)[-1], "open points 4, budget 3: over budget")
        self.write(*entries, answer(2, "approve"))
        self.assertEqual(self.lines(str(N))[-1], "open points 3, budget 3: budget reached")
        self.write(*entries, answer(2, "approve"), answer(1, "q1=A"))
        self.assertEqual(self.lines(str(N)), ["none"])

    def test_a_stop_point_answered_another_way_adds_no_rework(self):
        for text in ("reject", "q2=A"):
            with self.subTest(answer=text):
                self.write(self.two_questions(1, mode="stop", kind="scope"), answer(1, text))
                self.assertEqual(self.lines(str(N)), ["none"])

    def test_refusals(self):
        base = self.two_questions(1)
        cases = {
            "second answer": ([base, answer(1, "approve"), answer(1, "reject")], 3, "already closed"),
            "unknown id": ([base, answer(9, "approve")], 2, "D-12-9 has no open entry"),
            "answer before open": ([answer(1, "approve"), base], 1, "has no open entry"),
            "question not offered": ([base, answer(1, "q3=A")], 2, "has no question q3"),
            "option not offered": ([base, answer(1, "q1=C")], 2, "q1 offers no option C"),
            "lowercase option": ([base, answer(1, "q1=a")], 2, "is not approve, reject or q<n>=<option>"),
            "free text": ([base, answer(1, "yes please")], 2, "is not approve, reject"),
            "question twice": ([base, answer(1, "q1=A, q1=B")], 2, "names q1 twice"),
            "empty answer": ([base, answer(1, "")], 2, "key answer must be"),
            "answer of another issue": ([base, answer(1, "approve", issue=13)], 2, "is not of issue 12"),
            "reworked without rework": ([base, answer(1, "approve"), reworked(1)], 3, "has no rework item"),
            "reworked while open": ([base, reworked(1)], 2, "has no rework item"),
            "reworked twice": ([base, answer(1, "reject"), reworked(1), reworked(1, "2b3c4d5")], 4, "already reworked"),
            "bad commit": ([base, answer(1, "reject"), reworked(1, "HEAD")], 3, "key commit must be"),
            "missing key": ([base, {"event": "answer", "id": "D-12-1", "at": stamp()}], 2, "missing key answer"),
        }
        for name, (entries, line, reason) in cases.items():
            with self.subTest(case=name):
                self.write(*entries)
                self.refused(reason, line=line)


class ListingTest(Fixture):
    """C7: the listing, `none`, usage and the target."""

    def test_no_ledger_folder_prints_none(self):
        self.assertEqual(self.lines(str(N)), ["none"])
        self.assertEqual(self.lines(), ["none"])

    def test_an_empty_ledger_folder_and_an_empty_file_print_none(self):
        self.ledger.mkdir(parents=True)
        self.assertEqual(self.lines(str(N)), ["none"])
        self.write(raw="")
        self.assertEqual(self.lines(str(N)), ["none"])

    def test_a_fixture_ledger(self):
        self.write(point(1, effort="R", at=stamp(5)), answer(1, "q1=B"),
                   point(2, effort="E", mode="stop", kind="protected", impact="C", dependents=(), at=stamp(2)),
                   point(3, effort="S", impact="M", dependents=("tests/test_x.py",), at=stamp(1)))
        self.write(point(1, effort="R", issue=13, at=stamp(9)), issue=13)
        self.assertEqual(self.lines(str(N)), [
            "D-12-2 impact C effort E points 3 mode stop age 2 dependents none",
            "D-12-3 impact M effort S points 1 mode continue age 1 dependents tests/test_x.py",
            "rework D-12-1 answer q1=B rollback revert the edit in agent-kit/process.md",
            "open points 3, budget 3: budget reached"])
        self.assertEqual(self.lines(), [
            "D-12-2 impact C effort E points 3 mode stop age 2 dependents none",
            "D-12-3 impact M effort S points 1 mode continue age 1 dependents tests/test_x.py",
            "D-13-1 impact L effort R points 2 mode continue age 9 dependents agent-kit/process.md",
            "rework D-12-1 answer q1=B rollback revert the edit in agent-kit/process.md",
            "open points 3, budget 3: budget reached"])

    def test_the_formats_example_is_a_valid_ledger(self):
        text = (KIT / "procedures" / "formats.md").read_text(encoding="utf-8")
        block = next(b for b in re.findall(r"```\n(.*?)```", text, re.S) if b.startswith('{"event": "open"'))
        self.write(raw=block)
        self.assertEqual(self.lines(str(N)), ["none"])
        opened = block.splitlines()[0] + "\n"
        self.write(raw=opened)
        self.assertEqual(self.lines(str(N))[-1], "open points 2, budget 3: within budget")
        self.write(raw="\n".join(block.splitlines()[:2]) + "\n")
        self.assertTrue(self.lines(str(N))[0].startswith("rework D-12-3 answer q1=B rollback "))

    def test_the_folder_holds_ledger_files_only(self):
        self.ledger.mkdir(parents=True)
        (self.ledger / "notes.md").write_text("x\n", encoding="utf-8")
        done = self.run_script(str(N))
        self.assertEqual(done.returncode, 1)
        self.assertIn("a ledger file must be named <issue number>.jsonl", done.stderr)

    def test_a_byte_order_mark_is_refused(self):
        self.write(raw="﻿" + json.dumps(point(1)) + "\n")
        self.refused("byte order mark")

    def test_a_missing_dump_and_a_settings_refusal(self):
        done = self.run_script("998")
        self.assertEqual((done.returncode, done.stdout), (1, ""))
        self.assertEqual(done.stderr, "decisions: .scratch/issue-998.json: missing or not a regular file; "
                                      "run `make settings N=998` first\n")
        (self.project / "agent-kit.conf").write_text("DECISION_BUDGET=x\n", encoding="utf-8")
        done = self.run_script()
        self.assertEqual(done.returncode, 1)
        self.assertTrue(done.stderr.startswith("decisions: settings: agent-kit.conf line 1: "), done.stderr)

    def test_usage(self):
        for args in (("x",), ("01",), ("1", "2"), ("-1",), ("1;x",)):
            with self.subTest(args=args):
                done = self.run_script(*args)
                self.assertEqual((done.returncode, done.stdout), (2, ""))
                self.assertIn("Usage: make decisions [N=<issue number>]", done.stderr)


class TargetTest(unittest.TestCase):
    """C7: the target in both Makefiles; a crafted N runs nothing."""

    def test_both_makefiles_define_the_target(self):
        for path, root in ((REPO / "Makefile", "agent-kit"), (KIT / "templates" / "Makefile.mk", "_docs/agent-kit")):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertRegex(text, r"(?m)^decisions: ## ")
                self.assertIn(f'@python3 -B {root}/scripts/decisions.py $(if $(value N),"$$N")', text)
                self.assertIn("$(if $(value N),$(if $(call issue-number-ok,$(value N)),,"
                              "$(error Usage: make decisions [N=<issue number>])))", text)
                self.assertIn(f'python3 -B {root}/scripts/github_api.py dump "$(N)"', text)

    def test_make_refuses_a_bad_n_without_running_anything(self):
        for value in ("1;x", "01", "x", "1 2", "$(shell touch .scratch/pwned-204)", "1; touch .scratch/pwned-204",
                      "`touch .scratch/pwned-204`"):
            with self.subTest(value=value):
                done = subprocess.run(["make", "-s", "--no-print-directory", "decisions", f"N={value}"],
                                      cwd=REPO, capture_output=True, text=True, timeout=60)
                self.assertEqual(done.returncode, 2, done.stderr)
                self.assertIn("Usage: make decisions [N=<issue number>]", done.stderr)
                self.assertEqual(done.stdout, "")
        self.assertFalse((SCRATCH / "pwned-204").exists())

    def test_make_with_n_writes_the_dump_and_applies_a_ruling(self):
        """C3 and C7 through both Makefiles, with a fake gh (never a live issue)."""
        from fake_gh_rest import FAKE_GH, rest_config
        SCRATCH.mkdir(exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix="test-decisions-make-", dir=SCRATCH))
        self.addCleanup(shutil.rmtree, work, True)
        bin_dir = work / "bin"
        bin_dir.mkdir()
        (bin_dir / "gh").write_text(FAKE_GH)
        (bin_dir / "gh").chmod(0o755)
        view = {"number": 5, "title": "T", "body": "", "state": "OPEN", "labels": [], "author": {"login": OWNER},
                "comments": [ruling("Ruling: DECISION_BUDGET=8")]}
        config = rest_config(json.dumps(view))
        config["repo_view"] = {"stdout": json.dumps({"owner": {"login": OWNER}})}
        (bin_dir / "config.json").write_text(json.dumps(config))
        env = {k: v for k, v in os.environ.items() if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "N")}
        env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
        entry = json.dumps(point(1, effort="E", issue=5)) + "\n"
        for makefile, kit in ((REPO / "Makefile", "agent-kit"), (KIT / "templates" / "Makefile.mk", "_docs/agent-kit")):
            with self.subTest(makefile=makefile.name):
                run = work / ("run-" + kit.replace("/", "-"))
                (run / kit / "scripts").mkdir(parents=True)
                for name in ("decisions.py", "check-format.py", "settings.py", "github_api.py"):
                    shutil.copy(KIT / "scripts" / name, run / kit / "scripts" / name)
                (run / "agent-kit.conf").write_text('GITHUB_REPO="example-org/example-repo"\n')
                (run / "_docs" / "records" / "decisions").mkdir(parents=True)
                (run / "_docs" / "records" / "decisions" / "5.jsonl").write_text(entry)

                def make(*args):
                    return subprocess.run(["make", "-s", "--no-print-directory", "-f", str(makefile), "decisions", *args],
                                          cwd=run, env=env, capture_output=True, text=True, timeout=120)
                done = make("N=5")
                self.assertEqual((done.returncode, done.stderr), (0, ""), done.stderr)
                self.assertEqual(done.stdout.splitlines()[-1], "open points 3, budget 8: within budget")
                self.assertTrue((run / ".scratch" / "issue-5.json").exists())
                done = make()
                self.assertEqual(done.stdout.splitlines()[-1], "open points 3, budget 3: budget reached")

    def test_it_reuses_check_format_and_starts_no_process(self):
        source = SCRIPT.read_text(encoding="utf-8")
        names = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                names.add((node.module or "").split(".")[0])
        self.assertEqual(names - set(sys.stdlib_module_names), set())
        for forbidden in ("subprocess", "os.system", "eval(", "write_text", "write_bytes", "mkdir"):
            self.assertNotIn(forbidden, source.replace("exec_module", ""))
        self.assertNotRegex(source, r"\bopen\(")
        for used in ("check_format.load_issue_settings", "check_format.DECISION_ID", "check_format.SRE"):
            self.assertIn(used, source)


if __name__ == "__main__":
    unittest.main()
