"""The findings log and `make findings` (issue #200, C1 to C10).

The script (agent-kit/scripts/findings.py) runs as a subprocess with `python3 -I -B` in a
throwaway project folder under .scratch/ holding an agent-kit.conf, `_docs/records/findings/`,
the rulings file and sweep entry names, as `make findings` runs it from the project folder.
"""
from __future__ import annotations

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
SCRIPT = KIT / "scripts" / "findings.py"
SCRATCH = REPO / ".scratch"

_spec = importlib.util.spec_from_file_location("findings_under_test", SCRIPT)
findings = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(findings)

KEYS = ("id", "impact", "effort", "scope", "criterion", "category", "group", "related",
        "recommendation", "what", "how_found")


def entry(issue: int, number: int, group: str = "g", impact: str = "L", category: str = "defect") -> dict:
    return {"id": f"F-{issue}-{number}", "impact": impact, "effort": "S", "scope": "in", "criterion": "C1",
            "category": category, "group": group, "related": "none", "recommendation": "Fix it.",
            "what": f"Problem {number} (a.py line 1).", "how_found": "Read the diff."}


def file_data(issue: int, entries: list, logged: str = "2026-11-01T10:00Z") -> dict:
    return {"issue": issue, "logged": logged, "findings": entries}


def sweep_name(day: int, suffix: str = "") -> str:
    return f"2026-11-{day:02d}T0900Z-measure-pm-sweep{suffix}.md"


class Fixture(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)
        self.project = Path(tempfile.mkdtemp(prefix="test-findings-", dir=SCRATCH))
        self.addCleanup(shutil.rmtree, self.project, True)
        self.records = self.project / "_docs" / "records"
        self.folder = self.records / "findings"
        self.folder.mkdir(parents=True)
        self.conf("")

    def conf(self, text: str) -> None:
        (self.project / "agent-kit.conf").write_text(text + "\n", encoding="utf-8")

    def put(self, issue: int, entries: list, logged: str = "2026-11-01T10:00Z", name=None) -> Path:
        path = self.folder / (name or f"{issue}.json")
        path.write_text(json.dumps(file_data(issue, entries, logged), indent=2) + "\n", encoding="utf-8")
        return path

    def raw(self, name: str, text: str) -> Path:
        path = self.folder / name
        path.write_text(text, encoding="utf-8")
        return path

    def rulings(self, *items) -> Path:
        path = self.records / "findings-rulings.jsonl"
        path.write_text("".join(json.dumps(item) + "\n" for item in items), encoding="utf-8")
        return path

    def sweeps(self, *names: str) -> None:
        for name in names:
            (self.records / name).write_text("entry\n", encoding="utf-8")

    def run_script(self, *args):
        return subprocess.run([sys.executable, "-I", "-B", str(SCRIPT), *args], cwd=self.project,
                              capture_output=True, text=True, timeout=60)

    def lines(self) -> list:
        done = self.run_script()
        self.assertEqual((done.returncode, done.stderr), (0, ""), done.stderr)
        return done.stdout.splitlines()

    def refused(self, *needles: str) -> str:
        done = self.run_script()
        self.assertEqual((done.returncode, done.stdout), (1, ""), done.stdout)
        self.assertEqual(len(done.stderr.splitlines()), 1, done.stderr)
        self.assertTrue(done.stderr.startswith("findings: "), done.stderr)
        for needle in needles:
            self.assertIn(needle, done.stderr)
        return done.stderr


class WhereItGoesTest(unittest.TestCase):
    """C1: impact at or above FINDINGS_TO_ISSUE_AT gets an issue; below it is logged."""

    def test_at_l_everything_gets_an_issue(self):
        self.assertEqual([findings.destination(i, "L") for i in "LMC"], ["issue", "issue", "issue"])

    def test_at_m_low_is_logged(self):
        self.assertEqual([findings.destination(i, "M") for i in "LMC"], ["log", "issue", "issue"])

    def test_at_c_only_critical_gets_an_issue(self):
        self.assertEqual([findings.destination(i, "C") for i in "LMC"], ["log", "log", "issue"])


class ListTest(Fixture):
    def test_no_findings_prints_none(self):
        self.assertEqual(self.lines(), ["none"])

    def test_no_folder_prints_none(self):
        shutil.rmtree(self.folder)
        self.assertEqual(self.lines(), ["none"])

    def test_a_file_is_written_and_read(self):
        self.put(7, [entry(7, 1, "alpha", "M"), entry(7, 2, "alpha", "L", "debt")])
        self.assertEqual(self.lines(), ["alpha: 2 open, 1 debt (F-7-2)",
                                        "  F-7-1 impact M age 0",
                                        "  F-7-2 impact L age 0",
                                        "total: 2 open, 1 groups, 1 debt"])

    def test_groups_largest_first_then_by_name(self):
        self.put(7, [entry(7, 1, "b"), entry(7, 2, "a"), entry(7, 3, "c"), entry(7, 4, "c")])
        heads = [line for line in self.lines() if not line.startswith(("  ", "total"))]
        self.assertEqual(heads, ["c: 2 open, 0 debt", "a: 1 open, 0 debt", "b: 1 open, 0 debt"])

    def test_entries_sort_by_issue_and_number(self):
        self.put(10, [entry(10, 2), entry(10, 1)])
        self.put(9, [entry(9, 3)])
        rows = [line.split()[0] for line in self.lines() if line.startswith("  ")]
        self.assertEqual(rows, ["F-9-3", "F-10-1", "F-10-2"])

    def test_groups_of_four_and_five_at_the_default(self):
        self.put(7, [entry(7, n, "four") for n in range(1, 5)] + [entry(7, n, "five") for n in range(5, 10)])
        heads = [line for line in self.lines() if not line.startswith(("  ", "total"))]
        self.assertEqual(heads, ["five: 5 open, 0 debt - draft one issue", "four: 4 open, 0 debt"])

    def test_group_at_from_the_conf(self):
        self.conf("FINDINGS_GROUP_AT=4")
        self.put(7, [entry(7, n, "four") for n in range(1, 5)] + [entry(7, n, "five") for n in range(5, 10)])
        heads = [line for line in self.lines() if not line.startswith(("  ", "total"))]
        self.assertEqual(heads, ["five: 5 open, 0 debt - draft one issue", "four: 4 open, 0 debt - draft one issue"])
        self.conf("FINDINGS_GROUP_AT=6")
        heads = [line for line in self.lines() if not line.startswith(("  ", "total"))]
        self.assertEqual(heads, ["five: 5 open, 0 debt", "four: 4 open, 0 debt"])

    def test_debt_totals(self):
        self.put(7, [entry(7, 1, "a", category="debt"), entry(7, 2, "a", category="debt"), entry(7, 3, "b", category="debt"),
                     entry(7, 4, "b")])
        lines = self.lines()
        self.assertIn("a: 2 open, 2 debt (F-7-1, F-7-2)", lines)
        self.assertIn("b: 2 open, 1 debt (F-7-3)", lines)
        self.assertEqual(lines[-1], "total: 4 open, 2 groups, 3 debt")

    def test_read_only(self):
        self.put(7, [entry(7, 1)])
        self.sweeps(sweep_name(5))
        before = sorted((p.relative_to(self.project).as_posix(), p.read_bytes()) for p in self.project.rglob("*") if p.is_file())
        self.lines()
        after = sorted((p.relative_to(self.project).as_posix(), p.read_bytes()) for p in self.project.rglob("*") if p.is_file())
        self.assertEqual(before, after)

    def test_a_usage_error_exits_2(self):
        done = self.run_script("extra")
        self.assertEqual((done.returncode, done.stdout), (2, ""))
        self.assertIn("Usage: make findings", done.stderr)


class AgeTest(Fixture):
    """C5: age counts sweep entries named later than `logged`."""

    def ages(self) -> dict:
        found = {}
        for line in self.lines():
            if line.startswith("  "):
                parts = line.split()
                found[parts[0]] = (int(parts[4]), line.endswith("keep or drop"))
        return found

    def test_no_sweep_means_age_zero_and_no_flag(self):
        self.put(7, [entry(7, 1)])
        self.assertEqual(self.ages(), {"F-7-1": (0, False)})

    def test_ages_four_and_five_at_the_default(self):
        self.put(7, [entry(7, 1)], logged="2026-11-01T10:00Z")
        self.put(8, [entry(8, 1)], logged="2026-11-02T10:00Z")
        self.sweeps(*(sweep_name(day) for day in (2, 3, 4, 5, 6)))
        # F-7-1 is older than all five; F-8-1 is older than the last four (day 2 09:00 is before 10:00).
        self.assertEqual(self.ages(), {"F-7-1": (5, True), "F-8-1": (4, False)})

    def test_keep_sweeps_from_the_conf(self):
        self.conf("FINDINGS_KEEP_SWEEPS=4")
        self.put(7, [entry(7, 1)], logged="2026-11-01T10:00Z")
        self.put(8, [entry(8, 1)], logged="2026-11-02T10:00Z")
        self.sweeps(*(sweep_name(day) for day in (2, 3, 4, 5, 6)))
        self.assertEqual(self.ages(), {"F-7-1": (5, True), "F-8-1": (4, True)})
        self.conf("FINDINGS_KEEP_SWEEPS=6")
        self.assertEqual(self.ages(), {"F-7-1": (5, False), "F-8-1": (4, False)})

    def test_only_later_sweep_entries_count(self):
        self.put(7, [entry(7, 1)], logged="2026-11-05T09:00Z")
        self.sweeps(sweep_name(4), sweep_name(5), sweep_name(6), sweep_name(7, "-2"),
                    "2026-11-08T0900Z-measure-pm-sweepx.md", "2026-11-08T0900Z-measure-other.md",
                    "2026-11-09T0900Z-measure-pm-sweep.txt", "notes.md")
        # Day 5 at 09:00 is not later than 09:00; day 6 and the `-2` entry of day 7 are.
        self.assertEqual(self.ages(), {"F-7-1": (2, False)})


class RulingsTest(Fixture):
    """C4: one ruling of each kind."""

    def setUp(self):
        super().setUp()
        self.put(7, [entry(7, 1, "a"), entry(7, 2, "a"), entry(7, 3, "a"), entry(7, 4, "b")])
        self.sweeps(*(sweep_name(day) for day in (2, 3, 4, 5, 6)))

    def ids(self) -> list:
        return [line.split()[0] for line in self.lines() if line.startswith("  ")]

    def test_issued_and_dropped_close_an_entry(self):
        self.rulings({"id": "F-7-1", "ruling": "issued", "at": "2026-11-06T0900Z", "issue": 30},
                     {"id": "F-7-2", "ruling": "dropped", "at": "2026-11-06T0900Z"})
        self.assertEqual(self.ids(), ["F-7-3", "F-7-4"])

    def test_everything_closed_prints_none(self):
        self.rulings(*({"id": f"F-7-{n}", "ruling": "dropped", "at": "2026-11-06T0900Z"} for n in range(1, 5)))
        self.assertEqual(self.lines(), ["none"])

    def test_kept_restarts_the_age_at_that_sweep(self):
        self.rulings({"id": "F-7-1", "ruling": "kept", "at": "2026-11-04T0900Z"})
        rows = {line.split()[0]: int(line.split()[4]) for line in self.lines() if line.startswith("  ")}
        # Five sweeps are later than `logged`; two (days 5 and 6) are later than the kept sweep.
        self.assertEqual(rows["F-7-1"], 2)
        self.assertEqual(rows["F-7-2"], 5)

    def test_kept_again_restarts_again(self):
        self.rulings({"id": "F-7-1", "ruling": "kept", "at": "2026-11-04T0900Z"},
                     {"id": "F-7-1", "ruling": "kept", "at": "2026-11-05T0900Z"})
        rows = {line.split()[0]: int(line.split()[4]) for line in self.lines() if line.startswith("  ")}
        self.assertEqual(rows["F-7-1"], 1)

    def test_regroup_replaces_the_group(self):
        self.rulings({"id": "F-7-3", "ruling": "regroup", "at": "2026-11-06T0900Z", "group": "b"})
        heads = [line for line in self.lines() if not line.startswith(("  ", "total"))]
        self.assertEqual(heads, ["a: 2 open, 0 debt", "b: 2 open, 0 debt"])

    def test_a_regrouped_entry_can_then_be_dropped(self):
        self.rulings({"id": "F-7-3", "ruling": "regroup", "at": "2026-11-06T0900Z", "group": "b"},
                     {"id": "F-7-3", "ruling": "dropped", "at": "2026-11-06T0900Z"})
        self.assertEqual(self.ids(), ["F-7-1", "F-7-2", "F-7-4"])

    def test_an_unknown_id_is_refused(self):
        path = self.rulings({"id": "F-7-1", "ruling": "dropped", "at": "2026-11-06T0900Z"},
                            {"id": "F-7-9", "ruling": "dropped", "at": "2026-11-06T0900Z"})
        self.refused(path.as_posix().rsplit("/", 1)[1], "line 2", "key id", "F-7-9")

    def test_a_ruling_for_a_closed_entry_is_refused(self):
        path = self.rulings({"id": "F-7-1", "ruling": "issued", "at": "2026-11-06T0900Z", "issue": 30},
                            {"id": "F-7-1", "ruling": "kept", "at": "2026-11-06T0900Z"})
        self.refused(path.name, "line 2", "already closed")

    def test_the_rulings_file_may_be_empty(self):
        (self.records / "findings-rulings.jsonl").write_text("", encoding="utf-8")
        self.assertEqual(len(self.ids()), 4)


class RefusalTest(Fixture):
    """C3: one case per rule; each names the file and the line or key, and prints nothing else."""

    def test_a_file_that_is_not_json_names_the_line(self):
        path = self.raw("7.json", '{\n  "issue": 7,\n  oops\n}\n')
        self.refused(path.name, "line 3", "not valid JSON")

    def test_an_empty_file(self):
        path = self.raw("7.json", "")
        self.refused(path.name, "not valid JSON")

    def test_a_duplicate_json_key(self):
        path = self.raw("7.json", '{"issue": 7, "issue": 7, "logged": "2026-11-01T10:00Z", "findings": []}')
        self.refused(path.name, "written twice")

    def test_a_missing_top_level_key(self):
        for key in ("issue", "logged", "findings"):
            with self.subTest(key=key):
                data = file_data(7, [entry(7, 1)])
                del data[key]
                path = self.raw("7.json", json.dumps(data))
                self.refused(path.name, f"key {key}", "missing")

    def test_an_extra_top_level_key(self):
        data = file_data(7, [entry(7, 1)])
        data["provisional"] = "x"
        path = self.raw("7.json", json.dumps(data))
        self.refused(path.name, "key provisional", "unknown top-level key")

    def test_a_file_name_that_does_not_match_issue(self):
        path = self.put(7, [entry(7, 1)], name="8.json")
        self.refused(path.name, "key issue", "file name says 8")

    def test_a_file_name_that_is_not_an_issue_number(self):
        path = self.put(7, [entry(7, 1)], name="notes.json")
        self.refused(path.name, "named <issue number>.json")

    def test_a_stray_file_is_not_skipped(self):
        path = self.raw("README.md", "hello\n")
        self.refused(path.name, "named <issue number>.json")

    def test_a_bad_logged_stamp(self):
        for logged in ("2026-11-01", "2026-11-01T1000Z", "2026-13-01T10:00Z", 5):
            with self.subTest(logged=logged):
                data = file_data(7, [entry(7, 1)])
                data["logged"] = logged
                path = self.raw("7.json", json.dumps(data))
                self.refused(path.name, "key logged")

    def test_an_issue_that_is_not_a_number(self):
        for value in ("7", 0, True, 7.5):
            with self.subTest(value=value):
                data = file_data(7, [entry(7, 1)])
                data["issue"] = value
                path = self.raw("7.json", json.dumps(data))
                self.refused(path.name, "key issue")

    def test_findings_that_are_not_a_list_or_are_empty(self):
        for value in ([], {}, "x"):
            with self.subTest(value=value):
                data = file_data(7, [entry(7, 1)])
                data["findings"] = value
                path = self.raw("7.json", json.dumps(data))
                self.refused(path.name, "key findings")

    def test_an_entry_without_a_group_or_an_impact(self):
        for key in ("group", "impact"):
            with self.subTest(key=key):
                bad = entry(7, 2)
                del bad[key]
                path = self.put(7, [entry(7, 1), bad])
                self.refused(path.name, "findings[1]", f"missing {key}")

    def test_an_entry_with_an_extra_key_or_a_bad_value(self):
        extra = dict(entry(7, 1), status="open")
        path = self.put(7, [extra])
        self.refused(path.name, "findings[0]", "unknown key 'status'")
        path = self.put(7, [dict(entry(7, 1), impact="H")])
        self.refused(path.name, "findings[0]", "key impact")
        path = self.put(7, [dict(entry(7, 1), group="Bad Group")])
        self.refused(path.name, "findings[0]", "key group")

    def test_an_id_of_another_issue(self):
        path = self.put(7, [entry(8, 1)])
        self.refused(path.name, "findings[0]", "key id")

    def test_a_duplicate_id(self):
        path = self.put(7, [entry(7, 1), entry(7, 1)])
        self.refused(path.name, "findings[1]", "duplicate id F-7-1")

    def test_one_bad_file_refuses_the_whole_list(self):
        self.put(7, [entry(7, 1)])
        self.raw("8.json", "{")
        self.refused("8.json")

    def test_ruling_lines(self):
        self.put(7, [entry(7, 1), entry(7, 2)])
        good = {"id": "F-7-1", "ruling": "dropped", "at": "2026-11-06T0900Z"}
        cases = {
            "not json": ("{oops", "not valid JSON", "line 2"),
            "not an object": ("[1]", "one JSON object", "line 2"),
            "a blank line": ("", "not valid JSON", "line 2"),
            "no ruling": (json.dumps({"id": "F-7-2", "at": "2026-11-06T0900Z"}), "key ruling", "line 2"),
            "bad ruling": (json.dumps(dict(good, id="F-7-2", ruling="deleted")), "key ruling", "line 2"),
            "missing at": (json.dumps({"id": "F-7-2", "ruling": "dropped"}), "key at", "line 2"),
            "missing issue": (json.dumps({"id": "F-7-2", "ruling": "issued", "at": "2026-11-06T0900Z"}), "key issue", "line 2"),
            "missing group": (json.dumps({"id": "F-7-2", "ruling": "regroup", "at": "2026-11-06T0900Z"}), "key group", "line 2"),
            "extra key": (json.dumps(dict(good, id="F-7-2", group="x")), "key group", "line 2"),
            "bad at": (json.dumps(dict(good, id="F-7-2", at="2026-11-06")), "key at", "line 2"),
            "impossible at": (json.dumps(dict(good, id="F-7-2", at="2026-13-06T0900Z")), "key at", "line 2"),
            "bad issue": (json.dumps({"id": "F-7-2", "ruling": "issued", "at": "2026-11-06T0900Z", "issue": "30"}), "key issue", "line 2"),
            "bad group": (json.dumps({"id": "F-7-2", "ruling": "regroup", "at": "2026-11-06T0900Z", "group": "No Good"}), "key group", "line 2"),
            "duplicate key": ('{"id": "F-7-2", "id": "F-7-2", "ruling": "dropped", "at": "2026-11-06T0900Z"}', "written twice", "findings-rulings.jsonl"),
        }
        for name, (line, *needles) in cases.items():
            with self.subTest(name):
                (self.records / "findings-rulings.jsonl").write_text(json.dumps(good) + "\n" + line + "\n", encoding="utf-8")
                self.refused("findings-rulings.jsonl", *needles)

    def test_a_settings_refusal(self):
        self.put(7, [entry(7, 1)])
        self.conf("FINDINGS_GROUP_AT=0")
        self.refused("settings: agent-kit.conf line 1", "FINDINGS_GROUP_AT")

    def test_a_missing_conf(self):
        (self.project / "agent-kit.conf").unlink()
        self.refused("settings:", "not found")


class NoSecondValidatorTest(unittest.TestCase):
    def test_findings_py_reuses_check_finding_and_holds_no_finding_pattern(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("check_format.check_finding(", source)
        self.assertIn("settings.read_settings(", source)
        for needle in ("[a-z0-9]", "F-[0-9]", r"F-\d", "SLUG", "POSITIVE", "FINDING_ID", "re.compile(r\"F-"):
            with self.subTest(needle=needle):
                self.assertNotIn(needle, source)
        # The only patterns in the script are for file names and times, not finding keys.
        patterns = re.findall(r"re\.compile\((.*)\)", source)
        for pattern in patterns:
            self.assertNotRegex(pattern, r"F-|impact|effort|scope|category|group|slug", pattern)


class MigratedFilesTest(unittest.TestCase):
    """C2 and C8: 196.json to 199.json are in the new format."""

    def load(self, number: int) -> dict:
        return json.loads((REPO / "_docs" / "records" / "findings" / f"{number}.json").read_text(encoding="utf-8"))

    def test_the_four_files_have_the_three_keys_and_26_entries(self):
        total = 0
        for number in (196, 197, 198, 199):
            data = self.load(number)
            self.assertEqual(list(data), ["issue", "logged", "findings"])
            self.assertEqual(data["issue"], number)
            self.assertRegex(data["logged"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z$")
            total += len(data["findings"])
            for item in data["findings"]:
                self.assertEqual(tuple(item), KEYS)
        self.assertEqual(total, 26)

    def test_199_uses_one_slug_for_f_199_2_and_f_199_4(self):
        groups = {item["id"]: item["group"] for item in self.load(199)["findings"]}
        self.assertEqual(groups["F-199-2"], groups["F-199-4"])

    def test_make_findings_reads_the_four_files(self):
        done = subprocess.run(["make", "--no-print-directory", "findings"], cwd=REPO, capture_output=True,
                              text=True, timeout=60)
        self.assertEqual((done.returncode, done.stderr), (0, ""), done.stderr)
        if not (REPO / "_docs" / "records" / "findings-rulings.jsonl").exists():
            for number in (196, 197, 198, 199):
                for item in self.load(number)["findings"]:
                    self.assertIn(item["id"], done.stdout)
            # No pinned counts: the live log grows when a new issue's file is written at close.
            self.assertRegex(done.stdout, r"(?m)^route-findings-settings-time: \d+ open, \d+ debt .*F-199-2")
            self.assertRegex(done.stdout, r"(?m)^total: (\d+) open")


class WiringAndDocsTest(unittest.TestCase):
    def test_the_makefile_and_the_template_have_the_target(self):
        for path, root in ((REPO / "Makefile", "agent-kit"), (KIT / "templates" / "Makefile.mk", "_docs/agent-kit")):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertRegex(text, r"(?m)^findings: ## ")
                self.assertIn(f"@python3 -B {root}/scripts/findings.py\n", text)

    def test_the_readme_lists_the_script(self):
        self.assertIn("findings.py", (KIT / "README.md").read_text(encoding="utf-8"))

    def test_the_formats_page_documents_the_log(self):
        text = " ".join((KIT / "procedures" / "formats.md").read_text(encoding="utf-8").split())
        for phrase in ("## Findings log", "_docs/records/findings/<issue>.json", "_docs/records/findings-rulings.jsonl",
                       "`issued`", "`dropped`", "`kept`", "`regroup`", "draft one issue", "keep or drop",
                       "never edits it", "`FINDINGS_TO_ISSUE_AT`"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_engineer_and_qa_phrases(self):
        engineer = " ".join((KIT / "team" / "software-engineer.md").read_text(encoding="utf-8").split())
        qa = " ".join((KIT / "team" / "qa-engineer.md").read_text(encoding="utf-8").split())
        self.assertIn("`shortcut: <the limit>, <when to upgrade>`", engineer)
        self.assertIn("a finding with `Category: debt` in your role return", engineer)
        self.assertIn("every `shortcut:` comment in the diff with no finding", qa)
        self.assertIn("`Category: debt`", qa)
        self.assertIn("Before naming a `Group:`, run `make findings` and reuse a listed slug that fits", qa)

    def test_the_human_messages_name_grade_and_outcome(self):
        asking = " ".join((KIT / "procedures" / "asking-the-human.md").read_text(encoding="utf-8").split())
        close = " ".join((KIT / "procedures" / "orchestrator-comments.md").read_text(encoding="utf-8").split())
        for phrase in ("Findings (Low: logged)", "Findings (Medium, out of scope: logged)",
                       "one bullet per finding", "one or two plain sentences",
                       "Findings that fail or come to the human keep the ship-or-fix block",
                       "`check-format KIND=message` does not check this layout"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, asking)
        self.assertIn("`Findings (<grade>: logged)` headings, one bullet each", close)

    def test_process_logs_findings_at_close_without_naming_the_sweep(self):
        lines = [l for l in (KIT / "process.md").read_text(encoding="utf-8").splitlines() if "Findings log" in l]
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith("9. Close the issue."))
        self.assertNotIn("sweep", lines[0])
        self.assertIn("unlabelled PM draft issue", lines[0])
        self.assertIn("`_docs/records/findings/<number>.json`", lines[0])

    def test_pm_drafts_the_issue_from_a_finding(self):
        pm = " ".join((KIT / "team" / "pm.md").read_text(encoding="utf-8").split())
        self.assertIn("An unfixed finding at or above `FINDINGS_TO_ISSUE_AT`", pm)

    def test_customizing_says_the_settings_act_now(self):
        text = " ".join((KIT / "customizing.md").read_text(encoding="utf-8").split())
        self.assertIn("The findings settings of #200 act now too", text)

    def test_the_changelog_has_one_entry_with_the_old_behaviour_lines(self):
        text = (KIT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertEqual(text.count("#200)"), 1)
        for line in ("`FINDINGS_TO_ISSUE_AT=L`", "`FINDINGS_GROUP_AT=99`", "`FINDINGS_KEEP_SWEEPS=99`",
                     "add the `findings` target", "copy `scripts/findings.py`"):
            with self.subTest(line=line):
                self.assertIn(line, text)

    def test_the_decision_record_and_index_rows_exist(self):
        self.assertTrue((REPO / "_docs" / "decisions" / "200-findings-log.md").is_file())
        index = (REPO / "_docs" / "index.md").read_text(encoding="utf-8")
        self.assertIn("`_docs/decisions/200-findings-log.md`", index)
        self.assertIn("`_docs/records/findings/`", index)
        self.assertIn("`_docs/records/findings-rulings.jsonl`", index)

    def test_installed_files_does_not_list_the_script(self):
        self.assertNotIn("findings.py", (KIT / "installed-files.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
