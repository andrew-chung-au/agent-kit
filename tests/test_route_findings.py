"""Points and routes for failing QA findings (issue #199, C5 and C6).

The script (agent-kit/scripts/route-findings.py) runs as a subprocess with `python3 -I -B`
in a throwaway project folder under .scratch/ holding an agent-kit.conf and the issue's dump,
as `make route-findings N=<n>` runs it after writing the dump.
"""
from __future__ import annotations

import ast
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
SCRIPT = KIT / "scripts" / "route-findings.py"
SCRATCH = REPO / ".scratch"
OWNER = "owner-account"
N = 199


def block(fid, impact="M", effort="S", scope="in", category="defect", related="none") -> str:
    return (f"Id: {fid}\nImpact: {impact}\nEffort: {effort}\nScope: {scope}\nCriterion: C1\n"
            f"Category: {category}\nGroup: g\nRelated: {related}\nRecommendation: Fix it.\n"
            "What: x (a.py line 1).\nHow found: Read the diff.\n")


def qa(*blocks: str, fail_at: str = "M", strict: str = "yes") -> str:
    """A QA comment whose verdict and counts follow from its blocks under the given settings."""
    order = "LMC"
    fails = 0
    for text in blocks:
        fields = dict(line.split(": ", 1) for line in text.splitlines())
        if order.index(fields["Impact"]) >= order.index(fail_at) and (fields["Scope"] == "in" or strict == "no"):
            fails += 1
    verdict = "FAIL" if fails else "PASS"
    return (f"QA: {verdict}\nCommit: 1a2b3c4\nFindings: {fails} fail / {len(blocks) - fails} log\n\n"
            + "".join(b + "\n" for b in blocks) + "Criteria\n- [x] C1. x\n")


def comment(body: str, author: str = OWNER, day: int = 1) -> dict:
    return {"author": {"login": author}, "body": body, "createdAt": f"2026-11-{day:02d}T10:00:00Z"}


def ruling(*lines: str, day: int = 1) -> dict:
    return comment("Orchestrator: Ruling\nHuman ruled: 2026-11-22\n" + "\n".join(lines), day=day)


class Fixture(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)
        self.project = Path(tempfile.mkdtemp(prefix="test-route-findings-", dir=SCRATCH))
        self.addCleanup(shutil.rmtree, self.project, True)
        (self.project / ".scratch").mkdir()
        (self.project / "agent-kit.conf").write_text("\n", encoding="utf-8")

    def write(self, comments, body: str = "", labels=(), number: int = N) -> None:
        data = {"number": number, "title": "T", "body": body, "state": "OPEN",
                "labels": [{"name": name} for name in labels], "author": {"login": OWNER},
                "comments": list(comments), "repositoryOwner": {"login": OWNER}}
        (self.project / ".scratch" / f"issue-{number}.json").write_text(json.dumps(data), encoding="utf-8")

    def run_script(self, *args):
        return subprocess.run([sys.executable, "-I", "-B", str(SCRIPT), *args], cwd=self.project,
                              capture_output=True, text=True, timeout=60)

    def route(self, *bodies, extra=(), number: int = N) -> list:
        """The output lines for owner QA comments `bodies` (days 2, 3, ...) plus `extra` comments."""
        comments = list(extra) + [comment(body, day=2 + i) for i, body in enumerate(bodies)]
        self.write(comments, number=number)
        done = self.run_script(str(number))
        self.assertEqual((done.returncode, done.stderr), (0, ""), done.stderr)
        return done.stdout.splitlines()

    def refused(self, comments, reason: str, body: str = "", labels=()) -> str:
        self.write(comments, body=body, labels=labels)
        done = self.run_script(str(N))
        self.assertEqual((done.returncode, done.stdout), (1, ""))
        self.assertEqual(len(done.stderr.splitlines()), 1, done.stderr)
        self.assertTrue(done.stderr.startswith("route-findings: "), done.stderr)
        self.assertIn(reason, done.stderr)
        return done.stderr


class PointsTableTest(Fixture):
    """C5: the table of customizing.md (Points) with the kit defaults."""

    def test_the_table(self):
        for effort, asked_after in (("E", 1), ("R", 2), ("S", 3)):
            bodies = []
            for rounds in range(asked_after + 1):
                bodies.append(qa(block("F-199-1", effort=effort)))
                points = "SRE".index(effort) + 1 + rounds
                route = "human" if rounds == asked_after else "engineer"
                guard = "yes" if rounds >= 1 else "no"
                with self.subTest(effort=effort, rounds=rounds):
                    self.assertEqual(self.route(*bodies),
                                     [f"F-199-1 points {points} rounds {rounds} route {route} guard {guard}"])
            self.assertEqual(len(bodies), asked_after + 1)  # QA runs at most

    def test_effort_as_last_posted(self):
        lines = self.route(qa(block("F-199-1", effort="S")), qa(block("F-199-1", effort="E")))
        self.assertEqual(lines, ["F-199-1 points 4 rounds 1 route human guard yes"])

    def test_only_failing_findings_of_the_latest_comment(self):
        latest = qa(block("F-199-2", "L"), block("F-199-3", "M", scope="out"), block("F-199-4", "C", effort="R"))
        self.assertEqual(self.route(qa(block("F-199-1")), latest),
                         ["F-199-4 points 2 rounds 0 route engineer guard no"])


class ChainTest(Fixture):
    """C5: chains, cycles, the Heavy second launch and non-owner comments."""

    def test_a_chain_as_on_198(self):
        first = qa(block("F-198-4"))
        second = qa(block("F-198-7", related="F-198-4"))
        self.assertEqual(self.route(first, second, number=198),
                         ["F-198-7 points 2 rounds 1 route engineer guard yes"])

    def test_a_chain_through_several_links(self):
        bodies = [qa(block("F-199-1")), qa(block("F-199-2", related="F-199-1")),
                  qa(block("F-199-3", related="F-199-2"))]
        self.assertEqual(self.route(*bodies), ["F-199-3 points 3 rounds 2 route engineer guard yes"])

    def test_a_cycle_counts_each_comment_once(self):
        first = qa(block("F-197-6", related="F-197-8"), block("F-197-8", related="F-197-6"))
        self.assertEqual(self.route(first, number=197), [
            "F-197-6 points 1 rounds 0 route engineer guard no",
            "F-197-8 points 1 rounds 0 route engineer guard no"])
        second = qa(block("F-197-8", related="F-197-6"))
        self.assertEqual(self.route(first, second, number=197),
                         ["F-197-8 points 2 rounds 1 route engineer guard yes"])

    def test_a_logged_finding_adds_no_failure(self):
        first = qa(block("F-199-1", "L"))
        second = qa(block("F-199-2", related="F-199-1"))
        self.assertEqual(self.route(first, second), ["F-199-2 points 1 rounds 0 route engineer guard no"])

    def test_the_heavy_second_launchs_new_finding(self):
        bodies = [qa(block("F-199-1")), qa(block("F-199-1", "L")), qa(block("F-199-2", effort="R"))]
        self.assertEqual(self.route(*bodies), ["F-199-2 points 2 rounds 0 route engineer guard no"])

    def test_a_non_owner_qa_comment_is_ignored(self):
        other = comment(qa(block("F-199-9")), author="someone", day=9)
        self.assertEqual(self.route(qa(block("F-199-1", "L")), extra=[other]), ["none"])
        self.assertEqual(self.route(qa(block("F-199-1")), extra=[other, comment(qa(block("F-199-1")),
                                                                                 author="someone", day=1)]),
                         ["F-199-1 points 1 rounds 0 route engineer guard no"])

    def test_none(self):
        self.assertEqual(self.route(), ["none"])
        self.assertEqual(self.route(qa(block("F-199-1")), qa()), ["none"])


class RouteTest(Fixture):
    """C5 and C6: the route order, ASK_AT and SHIP_RULE."""

    def test_criterion_goes_to_the_human(self):
        self.assertEqual(self.route(qa(block("F-199-1", category="criterion"))),
                         ["F-199-1 points 1 rounds 0 route human guard no"])

    def test_ask_at_1_by_ruling(self):
        lines = self.route(qa(block("F-199-1"), block("F-199-2", "C", effort="E")), extra=[ruling("Ruling: ASK_AT=1")])
        self.assertEqual(lines, ["F-199-1 points 1 rounds 0 route human guard no",
                                 "F-199-2 points 3 rounds 0 route human guard no"])

    def test_the_default_never_ships(self):
        bodies = [qa(block("F-199-1", effort="E")), qa(block("F-199-1", effort="E"))]
        self.assertEqual(self.route(*bodies), ["F-199-1 points 4 rounds 1 route human guard yes"])

    def test_a_ship_rule(self):
        rule = [ruling("Ruling: SHIP_RULE=impact:M,effort:E,rounds:1")]
        once = [qa(block("F-199-1", effort="E"))]
        twice = once * 2
        self.assertEqual(self.route(*once, extra=rule), ["F-199-1 points 3 rounds 0 route engineer guard no"])
        self.assertEqual(self.route(*twice, extra=rule), ["F-199-1 points 4 rounds 1 route ship guard yes"])
        low = [qa(block("F-199-1", "L", effort="E"), fail_at="L")] * 2
        self.assertEqual(self.route(*low, extra=rule + [ruling("Ruling: QA_FAIL_AT=L", day=1)]),
                         ["F-199-1 points 4 rounds 1 route ship guard yes"])
        critical = [qa(block("F-199-1", "C", effort="E"))] * 2
        self.assertEqual(self.route(*critical, extra=rule), ["F-199-1 points 4 rounds 1 route human guard yes"])
        regular = [qa(block("F-199-1", effort="R"))] * 2
        self.assertEqual(self.route(*regular, extra=rule), ["F-199-1 points 3 rounds 1 route engineer guard yes"])

    def test_rounds_0_alone_ships_at_the_first_fail(self):
        lines = self.route(qa(block("F-199-1", "C", effort="S")), extra=[ruling("Ruling: SHIP_RULE=rounds:0")])
        self.assertEqual(lines, ["F-199-1 points 1 rounds 0 route ship guard no"])

    def test_criterion_comes_before_the_ship_rule(self):
        lines = self.route(qa(block("F-199-1", category="criterion")), extra=[ruling("Ruling: SHIP_RULE=rounds:0")])
        self.assertEqual(lines, ["F-199-1 points 1 rounds 0 route human guard no"])

    def test_scope_strict_no_by_ruling(self):
        lines = self.route(qa(block("F-199-1", scope="out"), strict="no"),
                           extra=[ruling("Ruling: QA_SCOPE_STRICT=no")])
        self.assertEqual(lines, ["F-199-1 points 1 rounds 0 route engineer guard no"])


class RefusalTest(Fixture):
    """C5: refusals, and usage."""

    def test_a_latest_comment_check_format_refuses(self):
        bad = qa(block("F-199-1")).replace("1 fail / 0 log", "0 fail / 1 log")
        self.refused([comment(bad, day=2)], "issue #199 latest QA: comment line 3: Findings counts 0 fail / 1 log")
        self.refused([comment(qa(block("F-199-2", related="F-199-1")), day=2)], "Related names 'F-199-1'")
        self.refused([comment(qa(block("F-199-1", "L")).replace("QA: PASS", "QA: FAIL"), day=2)],
                     "QA: FAIL with no fail finding")

    def test_an_earlier_comment_that_does_not_parse_is_read_as_far_as_it_goes(self):
        old = "QA: FAIL\n\nChecked at `1a2b3c4`. Criterion 2 fails.\n"
        self.assertEqual(self.route(old, qa(block("F-199-1"))), ["F-199-1 points 1 rounds 0 route engineer guard no"])

    def test_a_missing_dump(self):
        done = self.run_script("998")
        self.assertEqual((done.returncode, done.stdout), (1, ""))
        self.assertEqual(done.stderr, "route-findings: .scratch/issue-998.json: missing or not a regular file; "
                                      "run `make settings N=998` first\n")

    def test_a_settings_refusal(self):
        stderr = self.refused([], "body line 1", body="Overrides: ASK_AT=1\n")
        self.assertTrue(stderr.startswith("route-findings: settings: issue #199 body line 1: "), stderr)

    def test_usage(self):
        for args in ((), ("x",), ("01",), ("1", "2"), ("-1",)):
            with self.subTest(args=args):
                done = self.run_script(*args)
                self.assertEqual(done.returncode, 2)
                self.assertIn("Usage: make route-findings N=<issue number>", done.stderr)


class TargetTest(unittest.TestCase):
    """C5: the target in both Makefiles, and one parser."""

    def test_both_makefiles_define_the_target(self):
        for path, root in ((REPO / "Makefile", "agent-kit"), (KIT / "templates" / "Makefile.mk", "_docs/agent-kit")):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertRegex(text, r"(?m)^route-findings: ## ")
                self.assertIn(f'@python3 -B {root}/scripts/route-findings.py "$$N"', text)
                self.assertIn("$(error Usage: make route-findings N=<issue number>)", text)
                self.assertIn(f'python3 -B {root}/scripts/github_api.py dump "$(N)"', text)

    def test_make_refuses_a_bad_n_without_running_anything(self):
        for value in ("", "01", "x", "1 2", "$(shell touch .scratch/pwned-199)"):
            with self.subTest(value=value):
                done = subprocess.run(["make", "-s", "--no-print-directory", "route-findings", f"N={value}"],
                                      cwd=REPO, capture_output=True, text=True, timeout=60)
                self.assertEqual(done.returncode, 2, done.stderr)
                self.assertIn("Usage: make route-findings N=<issue number>", done.stderr)
        self.assertFalse((SCRATCH / "pwned-199").exists())

    def test_it_reuses_check_formats_parser_and_starts_no_process(self):
        source = SCRIPT.read_text(encoding="utf-8")
        tree = ast.parse(source)
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                names.add((node.module or "").split(".")[0])
        self.assertEqual(names - set(sys.stdlib_module_names), set())
        for forbidden in ("subprocess", "os.system", "eval(", "lines_of", "re.compile", "FINDING_FIELDS"):
            self.assertNotIn(forbidden, source.replace("exec_module", ""))
        for used in ("check_format.read_qa", "check_format.finding_fails", "check_format.load_issue_settings",
                     "check_format.owner_qa_comments"):
            self.assertIn(used, source)

    def test_policy_values_come_from_the_settings(self):
        # ASK_AT and SHIP_RULE come from the settings, the points from the Effort order.
        code = SCRIPT.read_text(encoding="utf-8").split('"""', 2)[2]
        for setting in ("ASK_AT", "SHIP_RULE"):
            self.assertIn(f'check_format.setting(values, "{setting}")', code)
        self.assertIn("enumerate(EFFORTS)", code)
        for literal in ("= 4", ">= 4", "99", '"S": 1'):
            self.assertNotIn(literal, code)

    def test_the_docs(self):
        process = " ".join((KIT / "process.md").read_text(encoding="utf-8").split())
        self.assertIn("run `make route-findings N=<number>`", process)
        custom = (KIT / "customizing.md").read_text(encoding="utf-8")
        self.assertIn("## Points", custom)


if __name__ == "__main__":
    unittest.main()
