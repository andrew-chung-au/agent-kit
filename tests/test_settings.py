"""Kit settings, profiles and the grade vocabulary (issue #196).

The reader (agent-kit/scripts/settings.py) runs on fixture confs in throwaway folders
under .scratch/, never on this repo's own agent-kit.conf. The expected table below is
written from the issue's Design table, not read from the reader.
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
SCRIPT = KIT / "scripts" / "settings.py"
DOC = KIT / "customizing.md"
CONF_TEMPLATE = KIT / "templates" / "agent-kit.conf.template"
SCRATCH = REPO / ".scratch"

_spec = importlib.util.spec_from_file_location("kit_settings", SCRIPT)
settings = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(settings)

LMC = ("choice", ("L", "M", "C"))
ON_OFF = ("choice", ("on", "off"))

# From the issue #196 Design table: name, default (per profile or single), allowed values.
EXPECTED = (
    ("PROFILE", "solo", ("choice", ("solo", "team", "fleet"))),
    ("GROOM_AHEAD", {"solo": "2", "team": "4", "fleet": "6"}, ("whole", 0, 99)),
    ("LANES", {"solo": "1", "team": "2", "fleet": "3"}, ("whole", 1, 99)),
    ("DELIVERY_LEAD", {"solo": "off", "team": "off", "fleet": "on"}, ON_OFF),
    ("STATUS_EVERY", {"solo": "milestone", "team": "milestone", "fleet": "15m"}, ("minutes", 1, 999)),
    ("DECISION_BUDGET", "3", ("whole", 0, 99)),
    ("QA_FAIL_AT", "M", LMC),
    ("QA_SCOPE_STRICT", "yes", ("choice", ("yes", "no"))),
    ("RECHECK", "changed", ("choice", ("changed", "full"))),
    ("FIX_CHECK_LOOPS", "2", ("whole", 1, 99)),
    ("ASK_AT", "4", ("whole", 1, 99)),
    ("SHIP_RULE", "none", ("ship_rule",)),
    ("STEP_UP", "ask", ("choice", ("auto", "ask", "off"))),
    ("FINDINGS_TO_ISSUE_AT", "C", LMC),
    ("FINDINGS_GROUP_AT", "5", ("whole", 1, 99)),
    ("FINDINGS_KEEP_SWEEPS", "5", ("whole", 1, 99)),
    ("HEAVY_SECOND_QA", "on", ON_OFF),
)
EXPECTED_SHIP_RULE_KEYS = (("impact", LMC), ("effort", ("choice", ("S", "R", "E"))), ("rounds", ("whole", 0, 99)))
# The Design table's allowed-values cells, as customizing.md writes them.
EXPECTED_ALLOWED_TEXT = {
    "PROFILE": "`solo`, `team`, `fleet`",
    "GROOM_AHEAD": "whole number 0 to 99",
    "LANES": "whole number 1 to 99",
    "STATUS_EVERY": "`milestone`, or `<n>m` with n a whole number 1 to 999",
    "SHIP_RULE": ("`none`, or one to three comma-separated `key:value` pairs, no spaces, each key at most once: "
                  "`impact:` `L`/`M`/`C`, `effort:` `S`/`R`/`E`, `rounds:` whole number 0 to 99"),
    "STEP_UP": "`auto`, `ask`, `off`",
}
TAKES_EFFECT = {
    "PROFILE": "#196", "GROOM_AHEAD": "#203", "LANES": "#214", "DELIVERY_LEAD": "#214",
    "STATUS_EVERY": "#214, #215", "DECISION_BUDGET": "#204", "QA_FAIL_AT": "#199",
    "QA_SCOPE_STRICT": "#199", "RECHECK": "#199", "FIX_CHECK_LOOPS": "#199", "ASK_AT": "#199",
    "SHIP_RULE": "#199", "STEP_UP": "#199; `auto` acts as `ask` until #210", "FINDINGS_TO_ISSUE_AT": "#200",
    "FINDINGS_GROUP_AT": "#200", "FINDINGS_KEEP_SWEEPS": "#200",
    "HEAVY_SECOND_QA": "no 1.11 issue wires `off` yet; `on` is what the kit does today",
}
NAMES = [row[0] for row in EXPECTED]
PROFILE_NAMES = ["GROOM_AHEAD", "LANES", "DELIVERY_LEAD", "STATUS_EVERY"]
LINE = re.compile(r"([A-Z_]+)=(\S*) \((kit default|profile (?:solo|team|fleet)|agent-kit\.conf line [1-9][0-9]*)\)")


def flat(text: str) -> str:
    return " ".join(text.split())


def table_after(text: str, marker: str) -> list[list[str]]:
    """The cells of the first Markdown table after `marker`, header and separator dropped."""
    lines = text[text.index(marker):].splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("|"))
    rows = []
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    return rows[2:]


def bare(cell: str) -> str:
    return cell.strip("`")


def kit_default(name: str, profile: str = "solo") -> str:
    default = dict((row[0], row[1]) for row in EXPECTED)[name]
    return default[profile] if isinstance(default, dict) else default


class Fixture(unittest.TestCase):
    """Each test gets a throwaway folder under .scratch/ holding its own agent-kit.conf."""

    def setUp(self):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        self.work = Path(tempfile.mkdtemp(prefix="settings-", dir=SCRATCH))
        self.addCleanup(shutil.rmtree, self.work, True)

    def run_reader(self, conf: str | None, env_extra: dict | None = None):
        if conf is not None:
            (self.work / "agent-kit.conf").write_text(conf, encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if k not in NAMES}
        env.update(env_extra or {})
        return subprocess.run([sys.executable, "-B", str(SCRIPT)], cwd=self.work, env=env,
                              capture_output=True, text=True, timeout=60)

    def values(self, conf: str, env_extra: dict | None = None) -> dict:
        result = self.run_reader(conf, env_extra)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        found = {}
        for line in result.stdout.splitlines():
            match = LINE.fullmatch(line)
            self.assertIsNotNone(match, line)
            found[match.group(1)] = (match.group(2), match.group(3))
        return found

    def assert_refused(self, conf: str, line: int, reason: str = ""):
        result = self.run_reader(conf)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr.startswith(f"settings: agent-kit.conf line {line}: "), result.stderr)
        self.assertEqual(len(result.stderr.strip().splitlines()), 1, result.stderr)
        self.assertIn(reason, result.stderr)
        return result


class TableTest(unittest.TestCase):
    """C4: one table in the reader, equal to the Design table."""

    def test_reader_table_equals_the_design_table(self):
        self.assertEqual(tuple(settings.SETTINGS), EXPECTED)
        self.assertEqual(tuple(settings.SHIP_RULE_KEYS), EXPECTED_SHIP_RULE_KEYS)

    def test_allowed_value_text_matches_the_design_table(self):
        for name, text in EXPECTED_ALLOWED_TEXT.items():
            self.assertEqual(settings.describe(settings.TABLE[name][2]), text, name)

    def test_allowed_values(self):
        cases = {
            "GROOM_AHEAD": (["0", "2", "99"], ["", "-1", "01", "100", "2.0", " 2", "+2"]),
            "LANES": (["1", "99"], ["0", "100"]),
            "STATUS_EVERY": (["milestone", "15m", "1m", "999m"], ["15", "0m", "1000m", "015m", "Milestone", "m"]),
            "QA_FAIL_AT": (["L", "M", "C"], ["X", "m", "", "MM"]),
            "RECHECK": (["changed", "full"], ["some", "Full"]),
            "STEP_UP": (["auto", "ask", "off"], ["on", "ASK"]),
            "SHIP_RULE": (["none", "impact:M", "impact:M,effort:E,rounds:1", "rounds:0,impact:C"],
                          ["", "None", "impact:X", "impact:M,impact:C", "impact:M, effort:E", "rounds:01",
                           "impact:M,effort:E,rounds:1,impact:L", "speed:1", "impact", "impact:M,", "rounds:100"]),
        }
        for name, (good, bad) in cases.items():
            kind = settings.TABLE[name][2]
            for value in good:
                self.assertTrue(settings.allowed(value, kind), f"{name}={value!r}")
            for value in bad:
                self.assertFalse(settings.allowed(value, kind), f"{name}={value!r}")


class DocTest(unittest.TestCase):
    """C1 and C2: customizing.md."""

    @classmethod
    def setUpClass(cls):
        cls.text = DOC.read_text(encoding="utf-8")
        cls.flat = flat(cls.text)

    def test_settings_tables_equal_the_reader_both_ways(self):
        profile_rows = table_after(self.text, "**Profile settings**")
        standalone_rows = table_after(self.text, "**Standalone settings**")
        documented = {}
        for row in profile_rows:
            self.assertEqual(len(row), 7, row)
            documented[bare(row[0])] = ({"solo": bare(row[1]), "team": bare(row[2]), "fleet": bare(row[3])},
                                        row[4], row[5], row[6])
        for row in standalone_rows:
            self.assertEqual(len(row), 5, row)
            documented[bare(row[0])] = (bare(row[1]), row[2], row[3], row[4])
        self.assertEqual(len(documented), len(profile_rows) + len(standalone_rows), "a name is listed twice")
        self.assertEqual(set(documented), set(settings.NAMES))
        self.assertEqual(sorted(bare(r[0]) for r in profile_rows), sorted(PROFILE_NAMES))
        for name, default, kind in settings.SETTINGS:
            doc_default, doc_allowed, does, effect = documented[name]
            self.assertEqual(doc_default, default, name)
            self.assertEqual(doc_allowed, settings.describe(kind), name)
            self.assertTrue(does, name)
            self.assertEqual(effect, TAKES_EFFECT[name], name)

    def test_levels_table_has_six_rows_with_the_two_197_rows_marked(self):
        rows = table_after(self.text, "## Levels")
        self.assertEqual([r[0] for r in rows], [
            "Kit default", "Profile", "Project setting", "Path rule",
            "Issue override (added by #197)", "Session ruling (added by #197)"])

    def test_required_statements(self):
        for needle in (
            "`FIX_CHECK_LOOPS` and `ASK_AT` are not duplicates. They limit different loops",
            "**`STEP_UP` applies in Claude Code only.** OpenCode and Kiro ignore it",
            "The model for each reasoning level: it is set in the project's role definitions",
            "`LIGHT_ALLOWED` (the path rule level) and `LIGHT_MAX_LINES` stay as they are. "
            "`scripts/check-tier.sh` reads them, not `scripts/settings.py`",
            "explained by the comments in `templates/agent-kit.conf.template`",
            "**A profile never stops you customizing.**",
            "the kit adds a setting only when there's evidence that projects need different values",
            "When a setting is added, its default is the value the kit used before",
            "`HEAVY_SECOND_QA=off` has no effect yet",
        ):
            self.assertIn(needle, self.flat, needle)

    def test_profile_guide(self):
        rows = table_after(self.text, "## Profiles follow your usage")
        self.assertEqual([bare(r[0]) for r in rows], ["solo", "team", "fleet"])
        self.assertTrue(all(r[1] and r[2] for r in rows))

    def test_points_routing_and_bounds_are_left_to_later_issues(self):
        self.assertNotIn("Bounds no level can cross", self.text)
        self.assertNotIn("Points at the first FAIL", self.text)

    def test_three_grades_share_no_word_or_letter(self):
        rows = table_after(self.text, "## Grades")
        self.assertEqual([r[0] for r in rows], ["Reasoning", "Effort", "Impact"])
        levels = [cell for r in rows for cell in r[1:4]]
        found = [re.fullmatch(r"(\w+) \(([A-Z])\)", cell) for cell in levels]
        self.assertTrue(all(found), levels)
        words = [m.group(1) for m in found]
        letters = [m.group(2) for m in found]
        self.assertEqual(len(set(words)), 9, words)
        self.assertEqual(len(set(letters)), 9, letters)
        self.assertEqual(letters, ["B", "N", "D", "S", "R", "E", "L", "M", "C"])
        for row in rows:
            self.assertTrue(row[4] and row[5], row)

    def test_nine_level_rows_each_with_a_test_and_an_example(self):
        rows = table_after(self.text, "Agents need more than the table")
        self.assertEqual([r[1] for r in rows], ["B", "N", "D", "S", "R", "E", "L", "M", "C"])
        self.assertEqual([r[0] for r in rows if r[0]], ["Reasoning", "Effort", "Impact"])
        for row in rows:
            self.assertEqual(len(row), 4, row)
            self.assertTrue(row[2], row)
            self.assertTrue(row[3], row)

    def test_tie_break_and_effort_thresholds(self):
        for needle in (
            "**Tie-break rule:** when unsure between two levels, take the higher one for Impact and Reasoning "
            "(the cost of under-grading is a missed defect or a weak model), and the lower for Effort "
            "(an underestimate is found out at the fix check, cheaply).",
            "Each grade comes with one line of reason",
            "Short is under 10 minutes, Regular 10 to 30 minutes, Extended over 30 minutes",
        ):
            self.assertIn(needle, self.flat, needle)

    def test_the_readme_points_here(self):
        readme = (KIT / "README.md").read_text(encoding="utf-8")
        self.assertEqual(sum(1 for line in readme.splitlines() if "`customizing.md`" in line), 1)


class ResolutionTest(Fixture):
    """C5: kit default, then profile, then the conf line; nothing else."""

    def test_no_setting_lines_gives_every_kit_default(self):
        found = self.values('KIT_DIR="agent-kit"\nTEST_CMD="make test"\n')
        self.assertEqual(list(found), NAMES)
        for name in NAMES:
            self.assertEqual(found[name], (kit_default(name), "kit default"), name)

    def test_team_profile(self):
        found = self.values("PROFILE=team\n")
        self.assertEqual(found["PROFILE"], ("team", "agent-kit.conf line 1"))
        self.assertEqual({n: found[n][0] for n in PROFILE_NAMES},
                         {"GROOM_AHEAD": "4", "LANES": "2", "DELIVERY_LEAD": "off", "STATUS_EVERY": "milestone"})
        self.assertTrue(all(found[n][1] == "profile team" for n in PROFILE_NAMES))

    def test_fleet_profile(self):
        found = self.values("# comment\nPROFILE=fleet\n")
        self.assertEqual({n: found[n] for n in PROFILE_NAMES}, {
            "GROOM_AHEAD": ("6", "profile fleet"), "LANES": ("3", "profile fleet"),
            "DELIVERY_LEAD": ("on", "profile fleet"), "STATUS_EVERY": ("15m", "profile fleet")})

    def test_a_written_line_beats_the_profile(self):
        found = self.values("PROFILE=fleet\nLANES=2\n")
        self.assertEqual(found["LANES"], ("2", "agent-kit.conf line 2"))
        self.assertEqual(found["GROOM_AHEAD"], ("6", "profile fleet"))
        self.assertEqual(found["DELIVERY_LEAD"], ("on", "profile fleet"))
        self.assertEqual(found["STATUS_EVERY"], ("15m", "profile fleet"))

    def test_a_standalone_line_leaves_the_other_standalone_defaults(self):
        found = self.values("PROFILE=fleet\nQA_FAIL_AT=C\n")
        self.assertEqual(found["QA_FAIL_AT"], ("C", "agent-kit.conf line 2"))
        for name in NAMES[5:]:
            if name != "QA_FAIL_AT":
                self.assertEqual(found[name], (kit_default(name), "kit default"), name)

    def test_the_environment_is_ignored(self):
        found = self.values("PROFILE=solo\n", {"LANES": "5", "QA_FAIL_AT": "C", "PROFILE": "fleet"})
        self.assertEqual(found["LANES"], ("1", "profile solo"))
        self.assertEqual(found["QA_FAIL_AT"], ("M", "kit default"))
        self.assertEqual(found["PROFILE"], ("solo", "agent-kit.conf line 1"))

    def test_the_environment_is_ignored_with_no_lines(self):
        found = self.values("\n", {"LANES": "5"})
        self.assertEqual(found["LANES"], ("1", "kit default"))

    def test_quoted_values(self):
        found = self.values("QA_FAIL_AT=\"C\"\nRECHECK='full'   \nSHIP_RULE=impact:M,effort:E,rounds:1\t\n")
        self.assertEqual(found["QA_FAIL_AT"], ("C", "agent-kit.conf line 1"))
        self.assertEqual(found["RECHECK"], ("full", "agent-kit.conf line 2"))
        self.assertEqual(found["SHIP_RULE"], ("impact:M,effort:E,rounds:1", "agent-kit.conf line 3"))

    def test_existing_conf_names_and_array_lines_are_passed_over(self):
        conf = ('KIT_VERSION="1.10+x.1"\nPROTECTED=( \'a\'\n            \'b\' )\nLIGHT_MAX_LINES=20\n'
                "  NOT_A_SETTING=1\nexport OTHER=1\n")
        found = self.values(conf)
        self.assertTrue(all(source == "kit default" for _, source in found.values()))

    def test_the_conf_template_gives_every_kit_default(self):
        """C9."""
        found = self.values(CONF_TEMPLATE.read_text(encoding="utf-8"))
        self.assertEqual(list(found), NAMES)
        for name in NAMES:
            self.assertEqual(found[name], (kit_default(name), "kit default"), name)

    def test_the_conf_template_lists_every_setting_commented_out_with_its_default(self):
        text = CONF_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("customizing.md", text)
        for name in NAMES:
            self.assertEqual(text.count(f"\n# {name}={kit_default(name)}\n"), 1, name)

    def test_the_interface_function(self):
        conf = self.work / "agent-kit.conf"
        conf.write_text("PROFILE=team\nLANES=3\n", encoding="utf-8")
        result = settings.read_settings(conf)
        self.assertEqual(list(result), NAMES)
        self.assertEqual(result["LANES"], ("3", "agent-kit.conf line 2"))
        conf.write_text("LANES=0\n", encoding="utf-8")
        with self.assertRaisesRegex(settings.SettingsError, r"^agent-kit\.conf line 1: "):
            settings.read_settings(conf)


class OutputTest(Fixture):
    """C6: make settings and its output."""

    def test_line_format_order_and_the_three_source_forms(self):
        result = self.run_reader("PROFILE=team\nASK_AT=3\n")
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 17)
        self.assertEqual([line.split("=")[0] for line in lines], NAMES)
        self.assertIn("PROFILE=team (agent-kit.conf line 1)", lines)
        self.assertIn("ASK_AT=3 (agent-kit.conf line 2)", lines)
        self.assertIn("LANES=2 (profile team)", lines)
        self.assertIn("QA_FAIL_AT=M (kit default)", lines)

    def test_extra_arguments_are_refused(self):
        (self.work / "agent-kit.conf").write_text("\n", encoding="utf-8")
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "other.conf"], cwd=self.work,
                                capture_output=True, text=True, timeout=60)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_both_makefiles_have_the_read_only_target(self):
        for path, kit in ((REPO / "Makefile", "agent-kit"), (KIT / "templates" / "Makefile.mk", "_docs/agent-kit")):
            lines = path.read_text(encoding="utf-8").splitlines()
            index = next(i for i, line in enumerate(lines) if line.startswith("settings:"))
            self.assertEqual(lines[index + 1], f"\t@python3 -B {kit}/scripts/settings.py", path)
            self.assertFalse(lines[index + 2].startswith("\t"), path)


class RefusalTest(Fixture):
    """C7: each refusal exits 1 with nothing on standard output and the line number in the reason."""

    def test_unknown_name(self):
        self.assert_refused('KIT_DIR="agent-kit"\nQA_FAIL=M\n', 2, "unknown setting QA_FAIL")

    def test_unknown_lowercase_name(self):
        self.assert_refused("lanes=2\n", 1, "unknown setting lanes")

    def test_unknown_profile(self):
        self.assert_refused("PROFILE=big\n", 1, "unknown profile")

    def test_profile_wrong_case(self):
        self.assert_refused("PROFILE=Team\n", 1, "unknown profile")

    def test_values_outside_the_allowed_values(self):
        for line in ("QA_FAIL_AT=X", "QA_FAIL_AT=m", "RECHECK=some", "LANES=0", "GROOM_AHEAD=-1",
                     "STATUS_EVERY=15", "QA_FAIL_AT=", 'QA_FAIL_AT=""', "SHIP_RULE=impact:M,impact:C"):
            with self.subTest(line=line):
                self.assert_refused(f"# settings\n\n{line}\n", 3, line.split("=")[0])

    def test_empty_value_is_named(self):
        self.assert_refused("QA_FAIL_AT=\n", 1, "an empty value")

    def test_a_setting_written_twice(self):
        self.assert_refused("LANES=2\n# again\nLANES=2\n", 3, "written twice (first at line 1)")

    def test_profile_written_twice(self):
        self.assert_refused("PROFILE=team\nPROFILE=team\n", 2, "PROFILE is written twice")

    def test_text_after_the_value(self):
        for line in ("QA_FAIL_AT=M # strict", 'QA_FAIL_AT="M" # strict', "QA_FAIL_AT=M;", 'QA_FAIL_AT="M"x',
                     "QA_FAIL_AT=M\r", 'QA_FAIL_AT="M'):
            with self.subTest(line=line):
                self.assert_refused(f"{line}\n", 1, "QA_FAIL_AT")

    def test_indented_assignment(self):
        self.assert_refused("KIT_DIR=x\n  LANES=2\n", 2, "column 1")

    def test_export_assignment(self):
        for line in ("export LANES=2", "export PROFILE=team", "declare -x LANES=2", "\tQA_FAIL_AT=C"):
            with self.subTest(line=line):
                self.assert_refused(f"{line}\n", 1, "column 1")

    def test_append_assignment(self):
        self.assert_refused("LANES+=2\n", 1, "not +=")

    def test_missing_conf(self):
        result = self.run_reader(None)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("settings: agent-kit.conf: not found", result.stderr)


class NoCodeRunsTest(Fixture):
    """C8: the conf is read as text; nothing in it runs."""

    def test_command_substitution_is_refused_and_never_runs(self):
        self.assert_refused('QA_FAIL_AT="$(touch marker)"\n', 1, "QA_FAIL_AT")
        self.assertFalse((self.work / "marker").exists())

    def test_backticks_are_refused_and_never_run(self):
        self.assert_refused('QA_FAIL_AT="`touch marker2`"\n', 1, "QA_FAIL_AT")
        self.assertFalse((self.work / "marker2").exists())

    def test_bare_command_substitution_is_refused_and_never_runs(self):
        self.assert_refused("RECHECK=$(touch marker3)\n", 1, "RECHECK")
        self.assertFalse((self.work / "marker3").exists())

    def test_the_reader_starts_no_process_and_reads_no_environment(self):
        text = SCRIPT.read_text(encoding="utf-8")
        for needle in ("subprocess", "os.system(", "os.popen(", "exec(", "eval(", "os.environ", "getenv",
                       "import os"):
            self.assertFalse(needle in text, needle)


if __name__ == "__main__":
    unittest.main()
