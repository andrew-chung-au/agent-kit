"""Kit settings, profiles and the grade vocabulary (issue #196).

The reader (agent-kit/scripts/settings.py) runs on fixture confs in throwaway folders
under .scratch/, never on this repo's own agent-kit.conf. The expected table below is
written from the issue's Design table, not read from the reader.
"""
from __future__ import annotations

import importlib.util
import json
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

BOM = chr(0xFEFF)  # written as a code point, not as the invisible character
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
    # Issue #197 C13.
    ("WAIVABLE_GATES", "heavy-second-qa,qa-recheck", ("subset", ("heavy-second-qa", "qa-recheck"))),
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
    "WAIVABLE_GATES": ("`none`, or one or more of `heavy-second-qa`, `qa-recheck`, comma-separated, no spaces, "
                       "each at most once"),
}
TAKES_EFFECT = {
    "PROFILE": "#196", "GROOM_AHEAD": "#203", "LANES": "#214", "DELIVERY_LEAD": "#214",
    "STATUS_EVERY": "#214, #215", "DECISION_BUDGET": "#204", "QA_FAIL_AT": "#199",
    "QA_SCOPE_STRICT": "#199", "RECHECK": "#199", "FIX_CHECK_LOOPS": "#199", "ASK_AT": "#199",
    "SHIP_RULE": "#199", "STEP_UP": "#199; `auto` acts as `ask` until #210", "FINDINGS_TO_ISSUE_AT": "#200",
    "FINDINGS_GROUP_AT": "#200", "FINDINGS_KEEP_SWEEPS": "#200",
    "HEAVY_SECOND_QA": "no 1.11 issue wires `off` yet; `on` is what the kit does today",
    "WAIVABLE_GATES": "#197 checks `Waiver:` lines against it, #218 lets `make issue-close` accept them",
}
NAMES = [row[0] for row in EXPECTED]
PROFILE_NAMES = ["GROOM_AHEAD", "LANES", "DELIVERY_LEAD", "STATUS_EVERY"]
LINE = re.compile(r"([A-Z_]+)=(\S*) \((kit default|profile (?:solo|team|fleet)|agent-kit\.conf line [1-9][0-9]*"
                  r"|issue #[1-9][0-9]* body line [1-9][0-9]*|issue #[1-9][0-9]* ruling \S+ line [1-9][0-9]*)\)")
USAGE = "Usage: make settings [N=<issue number>]"


OWNER = "owner-account"
STAMP = "2026-11-20T10:00:00Z"


def ruling(*lines, stamp=STAMP, author=OWNER, first="Orchestrator: Ruling", ruled="Human ruled: 2026-11-20"):
    """A comment in the dump's shape; by default an owner ruling comment whose line 3 is lines[0]."""
    body = "\n".join([first] + ([ruled] if ruled else []) + list(lines))
    return {"author": None if author is None else {"login": author}, "body": body, "createdAt": stamp}


def dump(number=5, body="", labels=(), comments=(), owner=OWNER) -> dict:
    """An issue as `make issue-dump` writes it (#197 C2)."""
    return {"number": number, "title": "T", "body": body, "state": "OPEN",
            "labels": [{"name": name} for name in labels], "author": {"login": owner},
            "comments": list(comments), "repositoryOwner": {"login": owner}}


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

    def run_reader(self, conf: str | None, env_extra: dict | None = None, args=()):
        if conf is not None:
            (self.work / "agent-kit.conf").write_text(conf, encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if k not in NAMES}
        env.update(env_extra or {})
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *args], cwd=self.work, env=env,
                              capture_output=True, text=True, timeout=60)

    def values(self, conf: str, env_extra: dict | None = None, args=()) -> dict:
        result = self.run_reader(conf, env_extra, args)
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
            # Issue #197 C13.
            "WAIVABLE_GATES": (["none", "qa-recheck", "heavy-second-qa", "qa-recheck,heavy-second-qa",
                                "heavy-second-qa,qa-recheck"],
                               ["", "none,qa-recheck", "qa-recheck,qa-recheck", "qa-recheck, heavy-second-qa",
                                "qa-recheck,", ",qa-recheck", "QA-RECHECK", "None", "qa", "push", "approved"]),
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

    def test_levels_table_has_six_rows_without_markers(self):
        rows = table_after(self.text, "## Levels")
        self.assertEqual([r[0] for r in rows], [
            "Kit default", "Profile", "Project setting", "Path rule", "Issue override", "Session ruling"])
        self.assertNotIn("(added by #197)", self.text)
        self.assertIn("`make settings` and `scripts/settings.py` resolve five levels", self.flat)
        self.assertIn("The path rule level stays with `scripts/check-tier.sh`", self.flat)

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
            "When a setting is added, its default keeps what the kit did before, unless the human decides otherwise",
            "Every default the human decides differently is listed under \"Defaults that differ from what the kit "
            "does today\" above, and the issue that wires it announces the change in its changelog entry",
            "The reader doesn't parse bash, so it is conservative",
            "`HEAVY_SECOND_QA=off` has no effect yet",
        ):
            self.assertIn(needle, self.flat, needle)

    def test_profile_guide(self):
        rows = table_after(self.text, "## Profiles follow your usage")
        self.assertEqual([bare(r[0]) for r in rows], ["solo", "team", "fleet"])
        self.assertTrue(all(r[1] and r[2] for r in rows))

    def test_points_routing_and_bounds_are_left_to_later_issues(self):
        self.assertNotIn("Points at the first FAIL", self.text)
        # Issue #197 C10 and C11: the bounds are documented now.
        self.assertIn("## Bounds no level can cross", self.text)

    def test_issue_levels_and_bounds_rule_are_documented(self):
        """#197 C10, C11."""
        for needle in (
            "`Overrides: NAME=value, NAME=value`", "`overrides` label", "`Orchestrator: Ruling`",
            "`Human ruled: <YYYY-MM-DD>`", "`Ruling: NAME=value`", "`Waiver: <gate> - <reason>`",
            "`settings: issue #<n> body line <l>: <reason>`",
            "`settings: issue #<n> ruling <createdAt> line <l>: <reason>`",
            "`HEAVY_SECOND_QA=off` is refused there on every issue",
            "A new setting that could drop QA, lower a tier or loosen the label, protected-file or push rules "
            "adds its `BOUNDS` row in the same issue, or its `PROJECT_ONLY` entry when no issue may change it at all",
        ):
            self.assertIn(needle, self.flat, needle)

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
        # Issue #197 C1: with an issue file.
        conf.write_text("PROFILE=team\nLANES=3\n", encoding="utf-8")
        path = self.work / "issue-5.json"
        path.write_text(json.dumps(dump(body="Overrides: LANES=4", labels=("overrides",),
                                        comments=[ruling("Ruling: ASK_AT=2")])), encoding="utf-8")
        result = settings.read_settings(conf, path)
        self.assertEqual(list(result), NAMES)
        self.assertEqual(result["LANES"], ("4", "issue #5 body line 1"))
        self.assertEqual(result["ASK_AT"], ("2", f"issue #5 ruling {STAMP} line 3"))
        self.assertEqual(result["GROOM_AHEAD"], ("4", "profile team"))
        self.assertEqual(settings.read_settings(conf, None), settings.read_settings(conf))
        path.write_text(json.dumps(dump(body="Overrides: LANES=0", labels=("overrides",))), encoding="utf-8")
        with self.assertRaisesRegex(settings.SettingsError, r"^issue #5 body line 1: "):
            settings.read_settings(conf, path)


class OutputTest(Fixture):
    """C6: make settings and its output."""

    def test_line_format_order_and_the_three_source_forms(self):
        result = self.run_reader("PROFILE=team\nASK_AT=3\n")
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 18)
        self.assertEqual(lines[-1], "WAIVABLE_GATES=heavy-second-qa,qa-recheck (kit default)")
        self.assertEqual([line.split("=")[0] for line in lines], NAMES)
        self.assertIn("PROFILE=team (agent-kit.conf line 1)", lines)
        self.assertIn("ASK_AT=3 (agent-kit.conf line 2)", lines)
        self.assertIn("LANES=2 (profile team)", lines)
        self.assertIn("QA_FAIL_AT=M (kit default)", lines)

    def test_extra_arguments_are_refused(self):
        """#197 C3: one argument that is an issue number is accepted; anything else exits 2."""
        (self.work / "agent-kit.conf").write_text("\n", encoding="utf-8")
        for args in (["other.conf"], ["abc"], ["0"], ["012"], ["5", "6"], ["-5"], ["5 "], [""],
                     ["1234567890"]):
            with self.subTest(args=args):
                result = subprocess.run([sys.executable, "-B", str(SCRIPT), *args], cwd=self.work,
                                        capture_output=True, text=True, timeout=60)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn(USAGE, result.stderr)
        (self.work / ".scratch").mkdir()
        (self.work / ".scratch" / "issue-5.json").write_text(json.dumps(dump()), encoding="utf-8")
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "5"], cwd=self.work,
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(result.stdout.splitlines()), 18)

    def test_both_makefiles_have_the_target(self):
        """#197 C3: N checked as issue-hash does, the dump written as issue-dump does, then the reader."""
        for path, kit in ((REPO / "Makefile", "agent-kit"), (KIT / "templates" / "Makefile.mk", "_docs/agent-kit")):
            lines = path.read_text(encoding="utf-8").splitlines()
            index = next(i for i, line in enumerate(lines) if line.startswith("settings:"))
            dump_index = next(i for i, line in enumerate(lines) if line.startswith("issue-dump:"))
            dump_line = lines[dump_index + 3]
            self.assertTrue(dump_line.startswith("\t@if python3 -B"), path)
            same_dump = (dump_line[1:].replace(' && echo ".scratch/issue-$(N).json"', "")
                         .replace("issue-dump: gh could not", "settings: gh could not"))
            self.assertEqual(lines[index + 1:index + 6], [
                "\t$(if $(value N),$(if $(call issue-number-ok,$(value N)),,"
                "$(error Usage: make settings [N=<issue number>])))",
                "\t$(if $(value N),@mkdir -p .scratch)",
                f"\t$(if $(value N),{same_dump})",
                f'\t@python3 -B {kit}/scripts/settings.py $(if $(value N),"$(N)")',
                "",
            ], path)


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

    # Fix round (QA finding): lines bash would apply as a setting are refused, never passed over.
    def test_setting_after_a_known_assignment(self):
        self.assert_refused("KIT_DIR=x LANES=5\n", 1, "LANES must be on a line of its own")

    def test_setting_after_a_semicolon(self):
        self.assert_refused("# conf\nKIT_DIR=x; LANES=5\n", 2, "LANES must be on a line of its own")

    def test_setting_after_another_export_name(self):
        self.assert_refused("export X=1 LANES=2\n", 1, "LANES must be on a line of its own")

    def test_setting_inside_if(self):
        self.assert_refused("if true; then LANES=5; fi\n", 1, "LANES must be on a line of its own")

    def test_profile_after_a_byte_order_mark(self):
        self.assert_refused(BOM + "PROFILE=team\n", 1, "byte order mark")

    def test_byte_order_mark_before_a_known_line(self):
        self.assert_refused(BOM + 'KIT_DIR="agent-kit"\n', 1, "byte order mark")

    def test_setting_inside_an_array_is_refused_conservatively(self):
        self.assert_refused("PROTECTED=( 'a'\n            LANES=2 )\n", 2, "LANES must be on a line of its own")

    def test_a_setting_named_in_a_comment_is_passed_over(self):
        found = self.values("# LANES=5\n  # export QA_FAIL_AT=C\nKIT_DIR=x\n")
        self.assertEqual(found["LANES"], ("1", "kit default"))
        self.assertEqual(found["QA_FAIL_AT"], ("M", "kit default"))

    def test_known_lines_without_a_setting_are_still_passed_over(self):
        found = self.values('KIT_DIR=x OTHER=1\nTEST_CMD="make test" ; true\nexport X=1 Y=2\n')
        self.assertTrue(all(source == "kit default" for _, source in found.values()))

    def test_append_assignment(self):
        self.assert_refused("LANES+=2\n", 1, "not +=")

    # Fix round 3: very long digit strings get the normal refusal, never a traceback.
    def test_a_very_long_whole_number(self):
        result = self.assert_refused("LANES=" + "9" * 4301 + "\n", 1, "LANES has")
        self.assertNotIn("Traceback", result.stderr)

    def test_a_very_long_minutes_value(self):
        result = self.assert_refused("STATUS_EVERY=" + "1" * 5000 + "m\n", 1, "STATUS_EVERY has")
        self.assertNotIn("Traceback", result.stderr)

    def test_a_very_long_ship_rule_rounds(self):
        result = self.assert_refused("SHIP_RULE=rounds:" + "1" * 5000 + "\n", 1, "SHIP_RULE has")
        self.assertNotIn("Traceback", result.stderr)

    def test_a_long_value_is_shortened_in_the_reason(self):
        for line, name in (("LANES=" + "1" * 5000, "LANES has '"), ("PROFILE=" + "x" * 5000, "unknown profile '"),
                           ("STATUS_EVERY=" + "1" * 5000 + "m", "STATUS_EVERY has '")):
            with self.subTest(name=name):
                result = self.assert_refused(f"# c\n{line}\n", 2, name)
                self.assertLess(len(result.stderr), 200, result.stderr)
                self.assertIn("... (", result.stderr)
                self.assertIn(" characters)", result.stderr)

    def test_a_long_unknown_name_is_shortened_in_the_reason(self):
        result = self.assert_refused("A" * 5000 + "=1\n", 1, "unknown setting AAAA")
        self.assertLess(len(result.stderr), 200, result.stderr)
        self.assertIn("... (5000 characters)", result.stderr)

    def test_a_short_value_is_echoed_whole(self):
        self.assert_refused("QA_FAIL_AT=X\n", 1, "QA_FAIL_AT has 'X'; allowed:")

    def test_a_conf_that_cannot_be_opened(self):
        (self.work / "agent-kit.conf").mkdir()
        result = self.run_reader(None)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("settings: agent-kit.conf: cannot be opened (", result.stderr)
        self.assertNotIn("UTF-8", result.stderr)

    def test_a_conf_that_is_not_utf8(self):
        (self.work / "agent-kit.conf").write_bytes(b"LANES=\xff\n")
        result = self.run_reader(None)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("settings: agent-kit.conf: cannot be read as UTF-8 text", result.stderr)

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


class IssueFixture(Fixture):
    """Issue #197: a fixture dump at .scratch/issue-<n>.json in the throwaway folder, read with `<n>`."""

    def write_dump(self, data, number=5, raw: str | None = None):
        folder = self.work / ".scratch"
        folder.mkdir(exist_ok=True)
        text = raw if raw is not None else json.dumps(data)
        (folder / f"issue-{number}.json").write_text(text, encoding="utf-8")

    def issue_values(self, data, conf: str = "\n", number=5) -> dict:
        if data is not None:
            self.write_dump(data, number)
        return self.values(conf, args=[str(number)])

    def assert_issue_refused(self, data, place: str, reason: str = "", conf: str = "\n", number=5, raw=None):
        if data is not None or raw is not None:
            self.write_dump(data, number, raw)
        result = self.run_reader(conf, args=[str(number)])
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr.startswith(f"settings: {place}: "), result.stderr)
        self.assertEqual(len(result.stderr.strip().splitlines()), 1, result.stderr)
        self.assertIn(reason, result.stderr)
        return result

    def assert_all_defaults(self, found: dict):
        self.assertEqual(list(found), NAMES)
        for name in NAMES:
            self.assertEqual(found[name], (kit_default(name), "kit default"), name)


class IssueLevelsTest(IssueFixture):
    """C1, C4, C6, C7: the five levels and their source forms."""

    def test_the_five_source_forms(self):
        data = dump(body="Intro\n\nOverrides: QA_FAIL_AT=C\n", labels=("overrides",),
                    comments=[ruling("Ruling: RECHECK=full")])
        found = self.issue_values(data, "PROFILE=team\nASK_AT=3\n")
        self.assertEqual(found["DECISION_BUDGET"], ("3", "kit default"))
        self.assertEqual(found["LANES"], ("2", "profile team"))
        self.assertEqual(found["ASK_AT"], ("3", "agent-kit.conf line 2"))
        self.assertEqual(found["QA_FAIL_AT"], ("C", "issue #5 body line 3"))
        self.assertEqual(found["RECHECK"], ("full", f"issue #5 ruling {STAMP} line 3"))
        self.assertEqual(len(found), 18)

    def test_an_issue_without_overrides_or_rulings_gives_the_project_values(self):
        self.assert_all_defaults(self.issue_values(dump(body="Nothing here", labels=("approved",))))

    def test_override_with_two_items_and_trailing_space(self):
        data = dump(body="Overrides: QA_FAIL_AT=C, SHIP_RULE=impact:M,effort:E \t", labels=("overrides",))
        found = self.issue_values(data)
        self.assertEqual(found["QA_FAIL_AT"], ("C", "issue #5 body line 1"))
        self.assertEqual(found["SHIP_RULE"], ("impact:M,effort:E", "issue #5 body line 1"))

    def test_a_crlf_body_gives_the_same_result(self):
        data = dump(body="Intro\r\nOverrides: QA_FAIL_AT=C, RECHECK=full\r\nMore\r\n", labels=("overrides",))
        found = self.issue_values(data)
        self.assertEqual(found["QA_FAIL_AT"], ("C", "issue #5 body line 2"))
        self.assertEqual(found["RECHECK"], ("full", "issue #5 body line 2"))

    def test_the_label_without_a_line_changes_nothing(self):
        self.assert_all_defaults(self.issue_values(dump(body="Text", labels=("overrides",))))

    def test_an_override_beats_a_project_line(self):
        found = self.issue_values(dump(body="Overrides: LANES=4", labels=("overrides",)), "LANES=2\n")
        self.assertEqual(found["LANES"], ("4", "issue #5 body line 1"))

    def test_a_mention_inside_a_sentence_is_passed_over(self):
        body = "The PM writes `Overrides: X=1` in the body.\nSee `Overrides: QA_FAIL_AT=C, RECHECK=full`.\n"
        self.assert_all_defaults(self.issue_values(dump(body=body)))

    def test_a_ruling_applies_to_its_own_issue_only(self):
        self.write_dump(dump(number=6, body="Other issue"), number=6)
        found = self.issue_values(dump(comments=[ruling("Ruling: DECISION_BUDGET=8")]))
        self.assertEqual(found["DECISION_BUDGET"], ("8", f"issue #5 ruling {STAMP} line 3"))
        self.assert_all_defaults(self.values("\n", args=["6"]))

    def test_a_later_ruling_wins(self):
        early, late = "2026-11-20T09:00:00Z", "2026-11-20T11:00:00Z"
        comments = [ruling("Ruling: DECISION_BUDGET=9", stamp=late), ruling("Ruling: DECISION_BUDGET=8", stamp=early)]
        found = self.issue_values(dump(comments=comments))
        self.assertEqual(found["DECISION_BUDGET"], ("9", f"issue #5 ruling {late} line 3"))

    def test_a_tie_goes_to_the_later_comment_in_the_list(self):
        comments = [ruling("Ruling: DECISION_BUDGET=8"), ruling("", "Ruling: DECISION_BUDGET=9")]
        found = self.issue_values(dump(comments=comments))
        self.assertEqual(found["DECISION_BUDGET"], ("9", f"issue #5 ruling {STAMP} line 4"))

    def test_a_ruling_beats_an_override(self):
        data = dump(body="Overrides: QA_FAIL_AT=C", labels=("overrides",), comments=[ruling("Ruling: QA_FAIL_AT=L")])
        self.assertEqual(self.issue_values(data)["QA_FAIL_AT"], ("L", f"issue #5 ruling {STAMP} line 3"))

    def test_rulings_outside_owner_ruling_comments_change_nothing(self):
        comments = [
            ruling("Ruling: DECISION_BUDGET=8", author="someone-else"),
            ruling("Ruling: DECISION_BUDGET=8", author=None),
            ruling("Ruling: DECISION_BUDGET=8", first="PM: groomed"),
            ruling("Ruling: DECISION_BUDGET=8", first="QA: PASS"),
            ruling("Ruling: DECISION_BUDGET=8", first="Orchestrator: Claim"),
            ruling("Ruling: PROFILE=x", "Waiver: push - x", "- Ruling: X=1", first="PM: quoting", ruled=None),
        ]
        body = "Ruling: DECISION_BUDGET=8\nWaiver: push - x\n"
        self.assert_all_defaults(self.issue_values(dump(body=body, comments=comments)))

    def test_a_process_ruling_is_passed_over(self):
        """C7."""
        data = dump(comments=[ruling("Ruling: C9's Check accepts the README mention", "Ruling: DECISION_BUDGET=8")])
        found = self.issue_values(data)
        self.assertEqual(found["DECISION_BUDGET"], ("8", f"issue #5 ruling {STAMP} line 4"))
        self.assertEqual(sum(1 for _, source in found.values() if source != "kit default"), 1)

    def test_a_valid_waiver_changes_no_value(self):
        """C8."""
        alone = self.issue_values(dump(comments=[ruling("Ruling: DECISION_BUDGET=8")]))
        both = self.issue_values(dump(comments=[ruling(
            "Ruling: DECISION_BUDGET=8", "Ruling: C9's Check accepts the README mention",
            "Waiver: heavy-second-qa - the human judged QA done enough after three launches")]))
        self.assertEqual(list(both), list(alone))
        self.assertEqual({n: v for n, (v, _) in both.items()}, {n: v for n, (v, _) in alone.items()})
        self.assertEqual(both["WAIVABLE_GATES"], ("heavy-second-qa,qa-recheck", "kit default"))

    def test_a_waiver_allowed_by_a_narrowed_project_line(self):
        found = self.issue_values(dump(comments=[ruling("Waiver: qa-recheck - ok")]), "WAIVABLE_GATES=qa-recheck\n")
        self.assertEqual(found["WAIVABLE_GATES"], ("qa-recheck", "agent-kit.conf line 1"))

    def test_a_null_author_comment_is_skipped(self):
        """C2: a null-author comment is skipped, even a malformed ruling."""
        data = dump(comments=[ruling("- Ruling: X=1", author=None, ruled=None)])
        self.assert_all_defaults(self.issue_values(data))


class IssueDumpRefusalTest(IssueFixture):
    """C2: the dump is checked; the reader never falls back to ignoring the issue levels."""

    PLACE = ".scratch/issue-5.json"

    def test_a_missing_dump(self):
        self.assert_issue_refused(None, self.PLACE, "not found")

    def test_a_dump_that_cannot_be_opened(self):
        (self.work / ".scratch" / "issue-5.json").mkdir(parents=True)
        self.assert_issue_refused(None, self.PLACE, "cannot be opened")

    def test_text_that_is_not_json(self):
        for raw in ("{not json", "", "\xff"):
            with self.subTest(raw=raw):
                self.assert_issue_refused(None, self.PLACE, "is not JSON", raw=raw)

    def test_a_dump_that_is_not_an_object(self):
        self.assert_issue_refused(None, self.PLACE, "is not a JSON object", raw="[]")

    def test_missing_or_wrongly_typed_fields(self):
        cases = {
            "number": (None, "5", True, 0, 5.0),
            "labels": (None, "overrides", [1], [{"name": 1}], {}),
            "body": (None, 1, ["x"]),
            "comments": (None, {}, "x"),
            "repositoryOwner": (None, "owner-account", {}, {"login": ""}, {"login": None}, []),
        }
        for field, bad_values in cases.items():
            for bad in bad_values:
                with self.subTest(field=field, value=bad):
                    data = dump()
                    if bad is None:
                        del data[field]
                    else:
                        data[field] = bad
                    self.assert_issue_refused(data, self.PLACE, field)

    def test_a_malformed_comment(self):
        for comment in ("text", {"body": "x", "createdAt": STAMP}, {"author": "me", "body": "x", "createdAt": STAMP},
                        {"author": {"login": OWNER}, "createdAt": STAMP}, {"author": {"login": OWNER}, "body": "x"}):
            with self.subTest(comment=comment):
                self.assert_issue_refused(dump(comments=[comment]), "issue #5 comment 1", "")

    def test_a_dump_for_another_issue(self):
        self.write_dump(dump(number=5, comments=[ruling("Ruling: DECISION_BUDGET=8")]), number=6)
        self.assert_issue_refused(None, ".scratch/issue-6.json", "holds issue #5, not #6", number=6)


class OverrideRefusalTest(IssueFixture):
    """C5 and C10: each refusal names the issue and body line."""

    def refused(self, line: str, reason: str = "", labels=("overrides",), at: int = 2):
        return self.assert_issue_refused(dump(body=f"Intro\n{line}\nEnd\n", labels=labels),
                                         f"issue #5 body line {at}", reason)

    def test_the_line_without_the_label(self):
        self.refused("Overrides: QA_FAIL_AT=C", "`overrides` label", labels=("approved", "tier:heavy"))

    def test_two_lines(self):
        self.assert_issue_refused(dump(body="Overrides: QA_FAIL_AT=C\nOverrides: RECHECK=full", labels=("overrides",)),
                                  "issue #5 body line 2", "a second Overrides: line")

    def test_an_empty_list(self):
        for line in ("Overrides:", "Overrides: ", "Overrides:  \t"):
            with self.subTest(line=line):
                self.refused(line, "lists no setting")

    def test_items_that_are_not_name_value(self):
        for line in ("Overrides: QA_FAIL_AT=C,", "Overrides: QA_FAIL_AT=C, ", "Overrides: QA_FAIL_AT",
                     "Overrides: QA_FAIL_AT=C,  RECHECK=full", "Overrides:  QA_FAIL_AT=C", "Overrides:QA_FAIL_AT=C",
                     "Overrides: QA_FAIL_AT=C, , RECHECK=full", "Overrides: =C"):
            with self.subTest(line=line):
                self.refused(line)

    def test_names_that_are_not_settings(self):
        for name in ("QA_FAIL", "lanes", "PROTECTED", "LIGHT_ALLOWED", "LIGHT_MAX_LINES", "GITHUB_REPO", "KIT_DIR",
                     "KIT_VERSION", "TEST_CMD"):
            with self.subTest(name=name):
                self.refused(f"Overrides: {name}=x", f"unknown setting {name}")
        self.refused("Overrides: PROTECTED=x", "unknown setting PROTECTED")
        self.refused("Overrides: LIGHT_MAX_LINES=999", "unknown setting LIGHT_MAX_LINES")

    def test_project_only_names(self):
        for item in ("PROFILE=team", "WAIVABLE_GATES=none", "WAIVABLE_GATES=qa-recheck"):
            with self.subTest(item=item):
                self.refused(f"Overrides: {item}", "only by a project line")

    def test_the_same_name_twice(self):
        self.refused("Overrides: QA_FAIL_AT=C, QA_FAIL_AT=L", "QA_FAIL_AT is listed twice")

    def test_values_outside_the_allowed_values(self):
        for item, shown in (("QA_FAIL_AT=", "an empty value"), ('QA_FAIL_AT="C"', "'\"C\"'"), ("QA_FAIL_AT=c", "'c'"),
                            ("LANES=0", "'0'"), ("SHIP_RULE=impact:X", "'impact:X'")):
            with self.subTest(item=item):
                self.refused(f"Overrides: {item}", shown)

    def test_bullet_and_indented_lines(self):
        for line in ("- Overrides: QA_FAIL_AT=C", "* Overrides: QA_FAIL_AT=C", "+ Overrides: QA_FAIL_AT=C",
                     "1. Overrides: QA_FAIL_AT=C", "  Overrides: QA_FAIL_AT=C", "\tOverrides: QA_FAIL_AT=C",
                     "    Overrides: QA_FAIL_AT=C", "  - Overrides: QA_FAIL_AT=C"):
            with self.subTest(line=line):
                self.refused(line, "column 1")
                self.refused(line, "column 1", labels=())

    def test_a_long_value_and_name_are_shortened(self):
        for line in ("Overrides: LANES=" + "1" * 5000, "Overrides: " + "A" * 5000 + "=1"):
            with self.subTest(line=line[:30]):
                result = self.refused(line, "... (5000 characters)")
                self.assertLess(len(result.stderr), 200, result.stderr)

    def test_heavy_second_qa_off_crosses_a_bound(self):
        """C10: refused on a Heavy issue and on one with no tier label."""
        for labels in (("overrides", "tier:heavy"), ("overrides",), ("overrides", "tier:light")):
            with self.subTest(labels=labels):
                self.refused("Overrides: HEAVY_SECOND_QA=off", "bound", labels=labels)
        self.assertEqual(self.issue_values(dump(body="Overrides: HEAVY_SECOND_QA=on", labels=("overrides",)))
                         ["HEAVY_SECOND_QA"], ("on", "issue #5 body line 1"))


class RulingRefusalTest(IssueFixture):
    """C6, C7, C8, C10, C13: each refusal names the ruling comment and line."""

    def refused(self, *lines, reason: str = "", at: int = 3, conf: str = "\n", **kwargs):
        return self.assert_issue_refused(dump(comments=[ruling(*lines, **kwargs)]),
                                         f"issue #5 ruling {STAMP} line {at}", reason, conf=conf)

    def test_unknown_names(self):
        for line in ("Ruling: QA_FAIL=M", "Ruling: lanes=2", "Ruling: PROTECTED=x", "Ruling: LIGHT_MAX_LINES=999"):
            with self.subTest(line=line):
                self.refused(line, reason="unknown setting")

    def test_project_only_names(self):
        for line in ("Ruling: PROFILE=team", "Ruling: WAIVABLE_GATES=qa-recheck", "Ruling: WAIVABLE_GATES=none"):
            with self.subTest(line=line):
                self.refused(line, reason="only by a project line")

    def test_bad_values(self):
        for line in ("Ruling: DECISION_BUDGET=", "Ruling: DECISION_BUDGET=08", "Ruling: QA_FAIL_AT=m",
                     "Ruling: SHIP_RULE=impact:M, effort:E", "Ruling: DECISION_BUDGET = 8"):
            with self.subTest(line=line):
                self.refused(line, reason="DECISION_BUDGET" if "BUDGET" in line else "")

    def test_the_same_name_twice_in_one_comment(self):
        self.refused("Ruling: DECISION_BUDGET=8", "Ruling: DECISION_BUDGET=8", reason="ruled twice", at=4)

    def test_bullet_and_indented_lines(self):
        for line in ("- Ruling: DECISION_BUDGET=8", "  Ruling: DECISION_BUDGET=8", "1. Ruling: free text",
                     "* Waiver: qa-recheck - x", "    Waiver: qa-recheck - x", "\tWaiver: qa-recheck - x"):
            with self.subTest(line=line):
                self.refused(line, reason="column 1")

    def test_a_ruling_comment_without_the_human_ruled_line(self):
        for ruled in (None, "Human ruled: today", "Human ruled 2026-11-20", " Human ruled: 2026-11-20"):
            with self.subTest(ruled=ruled):
                self.refused("Ruling: DECISION_BUDGET=8", ruled=ruled, at=1, reason="Human ruled:")

    def test_heavy_second_qa_off_crosses_a_bound(self):
        """C10."""
        self.refused("Ruling: HEAVY_SECOND_QA=off", reason="bound")

    def test_gates_the_project_leaves_out(self):
        """C8 and C13: the reason names WAIVABLE_GATES and its value."""
        self.refused("Waiver: qa-recheck - x", reason="WAIVABLE_GATES (heavy-second-qa)",
                     conf="WAIVABLE_GATES=heavy-second-qa\n")
        for gate in ("qa-recheck", "heavy-second-qa"):
            with self.subTest(gate=gate):
                self.refused(f"Waiver: {gate} - x", reason="WAIVABLE_GATES (none)", conf="WAIVABLE_GATES=none\n")

    def test_gates_that_can_never_be_waived(self):
        for gate in ("approved", "push", "protected-files", "qa", "qa-rechek", "tier", "hash", "QA-RECHECK"):
            with self.subTest(gate=gate):
                self.refused(f"Waiver: {gate} - x", reason=f"{gate!r} is not a gate that can be waived")
        result = self.refused("Waiver: " + "g" * 5000 + " - x", reason="... (5000 characters)")
        self.assertLess(len(result.stderr), 250, result.stderr)

    def test_malformed_waivers(self):
        for line in ("Waiver: qa-recheck", "Waiver: qa-recheck x", "Waiver: qa-recheck -x", "Waiver:qa-recheck - x",
                     "Waiver: qa-recheck - ", "Waiver: qa-recheck - \t "):
            with self.subTest(line=line):
                self.refused(line)

    def test_the_same_gate_twice(self):
        self.refused("Waiver: qa-recheck - a", "Waiver: qa-recheck - b", reason="waived twice", at=4)


class ReadRulingsTest(unittest.TestCase):
    """C9: read_rulings on parsed JSON in both shapes; no file, no process."""

    def test_order_and_contents_in_both_shapes(self):
        late, early = "2026-11-20T12:00:00Z", "2026-11-20T08:00:00Z"
        comments = [
            ruling("Ruling: DECISION_BUDGET=8", "Waiver: qa-recheck - fine", stamp=late),
            {"author": {"login": OWNER}, "body": "PM: Ruling: DECISION_BUDGET=1", "createdAt": STAMP},
            ruling("Ruling: free text", "Ruling: QA_FAIL_AT=C", stamp=early),
            ruling("Ruling: DECISION_BUDGET=2", author=None),
        ]
        dumped = dump(comments=comments)
        issue_shape = {k: v for k, v in dumped.items() if k != "repositoryOwner"}
        for shape in (dumped, issue_shape):
            with self.subTest(owner_field="repositoryOwner" in shape):
                found = settings.read_rulings(shape, OWNER, ("heavy-second-qa", "qa-recheck"))
                self.assertEqual(found, [
                    {"createdAt": early, "index": 2, "rulings": [("QA_FAIL_AT", "C", 4)], "waivers": []},
                    {"createdAt": late, "index": 0, "rulings": [("DECISION_BUDGET", "8", 3)],
                     "waivers": [("qa-recheck", "fine", 4)]},
                ])

    def test_a_refusal(self):
        with self.assertRaisesRegex(settings.SettingsError, rf"^issue #5 ruling {STAMP} line 3: unknown setting"):
            settings.read_rulings(dump(comments=[ruling("Ruling: QA_FAIL=M")]), OWNER, ())

    def test_a_null_author_comment_is_skipped(self):
        self.assertEqual(settings.read_rulings(dump(comments=[ruling("- Ruling: x", author=None)]), OWNER, ()), [])

    def test_the_waivable_gates_decide(self):
        data = dump(comments=[ruling("Waiver: qa-recheck - x")])
        self.assertEqual(settings.read_rulings(data, OWNER, ("qa-recheck",))[0]["waivers"], [("qa-recheck", "x", 3)])
        with self.assertRaisesRegex(settings.SettingsError, "WAIVABLE_GATES"):
            settings.read_rulings(data, OWNER, ())

    def test_another_owner_counts_nothing(self):
        data = dump(comments=[ruling("Ruling: DECISION_BUDGET=8")])
        self.assertEqual(settings.read_rulings(data, "someone-else", ()), [])


class BoundsTest(Fixture):
    """C10 and C13: the bounds table, PROJECT_ONLY and the waivable gates."""

    def test_the_bounds_table(self):
        self.assertEqual([row[:2] for row in settings.BOUNDS], [("HEAVY_SECOND_QA", "off")])
        self.assertTrue(all("bound" in row[2] or "drop" in row[2] for row in settings.BOUNDS))
        self.assertEqual(settings.PROJECT_ONLY, frozenset(("PROFILE", "WAIVABLE_GATES")))

    def test_heavy_second_qa_off_stays_allowed_as_a_project_line(self):
        found = self.values("# c\nHEAVY_SECOND_QA=off\n")
        self.assertEqual(found["HEAVY_SECOND_QA"], ("off", "agent-kit.conf line 2"))

    def test_no_setting_names_a_tier_label_protection_push_or_approval_outside_project_only(self):
        names = set(settings.NAMES) | {row[0] for row in settings.BOUNDS}
        for name in names:
            if any(word in name for word in ("TIER", "LABEL", "PROTECT", "PUSH", "APPROVE")):
                self.assertIn(name, settings.PROJECT_ONLY, name)

    def test_the_waivable_gates_list(self):
        kind = settings.TABLE["WAIVABLE_GATES"][2]
        self.assertEqual(kind, ("subset", ("heavy-second-qa", "qa-recheck")))
        for gate in kind[1]:
            for word in ("approve", "label", "tier", "hash", "protect", "push"):
                self.assertNotIn(word, gate)
        self.assertFalse(hasattr(settings, "WAIVABLE"))

    def test_waivable_gates_none_as_a_project_line(self):
        found = self.values("WAIVABLE_GATES=none\n")
        self.assertEqual(found["WAIVABLE_GATES"], ("none", "agent-kit.conf line 1"))


class MakeTargetTest(unittest.TestCase):
    """C3: `make settings [N=<n>]` through both Makefiles, with a fake gh (never a live issue)."""

    def setUp(self):
        from fake_gh_rest import FAKE_GH, rest_config
        SCRATCH.mkdir(parents=True, exist_ok=True)
        self.work = Path(tempfile.mkdtemp(prefix="settings-make-", dir=SCRATCH))
        self.addCleanup(shutil.rmtree, self.work, True)
        self.bin = self.work / "bin"
        self.bin.mkdir()
        (self.bin / "gh").write_text(FAKE_GH)
        (self.bin / "gh").chmod(0o755)
        view = {"number": 5, "title": "T", "body": "Overrides: QA_FAIL_AT=C", "state": "OPEN",
                "labels": [{"name": "overrides"}], "author": {"login": OWNER},
                "comments": [ruling("Ruling: DECISION_BUDGET=8")]}
        config = rest_config(json.dumps(view))
        config["repo_view"] = {"stdout": json.dumps({"owner": {"login": OWNER}})}
        (self.bin / "config.json").write_text(json.dumps(config))

    def run_make(self, makefile: Path, kit: str, *args):
        run = self.work / ("run-" + kit.replace("/", "-"))
        if not run.exists():
            (run / kit / "scripts").mkdir(parents=True)
            for name in ("settings.py", "github_api.py"):
                shutil.copy(KIT / "scripts" / name, run / kit / "scripts" / name)
            (run / "agent-kit.conf").write_text('GITHUB_REPO="example-org/example-repo"\nASK_AT=3\n')
        env = {k: v for k, v in os.environ.items() if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "N")}
        env["PATH"] = f"{self.bin}{os.pathsep}{env['PATH']}"
        done = subprocess.run(["make", "--no-print-directory", "-f", str(makefile), "settings", *args], cwd=run,
                              env=env, capture_output=True, text=True, timeout=120)
        return done, run

    def calls(self):
        log = self.bin / "calls.log"
        return log.read_text().splitlines() if log.exists() else []

    def each_makefile(self):
        for makefile, kit in ((REPO / "Makefile", "agent-kit"), (KIT / "templates" / "Makefile.mk", "_docs/agent-kit")):
            with self.subTest(makefile=makefile.name):
                (self.bin / "calls.log").unlink(missing_ok=True)
                yield makefile, kit

    def test_with_n_the_dump_is_written_and_read(self):
        for makefile, kit in self.each_makefile():
            done, run = self.run_make(makefile, kit, "N=5")
            self.assertEqual(done.returncode, 0, done.stderr)
            lines = done.stdout.splitlines()
            self.assertEqual(len(lines), 18, done.stdout)
            self.assertIn("ASK_AT=3 (agent-kit.conf line 2)", lines)
            self.assertIn("QA_FAIL_AT=C (issue #5 body line 1)", lines)
            self.assertIn(f"DECISION_BUDGET=8 (issue #5 ruling {STAMP} line 3)", lines)
            self.assertTrue((run / ".scratch" / "issue-5.json").exists())
            self.assertEqual(len(self.calls()), 3)

    def test_without_n_nothing_is_fetched(self):
        for makefile, kit in self.each_makefile():
            done, run = self.run_make(makefile, kit)
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual(len(done.stdout.splitlines()), 18)
            self.assertEqual(self.calls(), [])

    def test_a_bad_n_stops_with_the_usage_line_before_anything_runs(self):
        for makefile, kit in self.each_makefile():
            for value in ("abc", "0", "012", "1 2", "5; touch marker", "$(touch marker)", "-1"):
                with self.subTest(value=value):
                    done, run = self.run_make(makefile, kit, f"N={value}")
                    self.assertNotEqual(done.returncode, 0)
                    self.assertIn(USAGE, done.stderr)
                    self.assertEqual(done.stdout, "")
                    self.assertEqual(self.calls(), [])
                    self.assertFalse((run / ".scratch").exists())
                    self.assertFalse((run / "marker").exists())

    def test_a_failed_dump_stops_before_the_reader(self):
        config = json.loads((self.bin / "config.json").read_text())
        config["issue_view"] = {"exit": 1}
        (self.bin / "config.json").write_text(json.dumps(config))
        for makefile, kit in self.each_makefile():
            done, run = self.run_make(makefile, kit, "N=5")
            self.assertNotEqual(done.returncode, 0)
            self.assertEqual(done.stdout, "")
            self.assertIn("settings: gh could not return valid JSON for issue 5", done.stderr)


if __name__ == "__main__":
    unittest.main()
