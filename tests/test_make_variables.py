"""A crafted make variable runs nothing (issue #57).

`make *` is allowed without approval, so any make target that takes a variable is an entry
point for an attacker-chosen string. Two ways a value can run a command:
- make expands it. `$(N)` in a check expands the value, and GNU Make also expands every
  command-line variable when it exports it to a recipe, so a value holding `$(shell ...)`
  runs even if the recipe never uses it (found while building #57, GNU Make 4.3);
- make pastes it into the shell line (`script.sh $(BASE)` runs `; touch m`).
The fix has two parts: the FIRST recipe line checks `$(value X)` and refuses a value holding `$`
(make aborts before it builds the recipe's environment), and the recipe passes the value as
`"$$X"`, the shell variable, so the shell never parses it.

Every test runs the real Makefile (or the template) in a throwaway folder under .scratch/ whose
scripts are stubs that record the arguments they received as JSON. A crafted value must leave no
MARKER file and must either be refused before any script runs or reach the script as exactly one
argument. Assertions are side effects, never only exit codes.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path

from kit_repo import new_workdir

REPO = Path(__file__).resolve().parent.parent
REPO_MAKEFILE = REPO / "Makefile"
TEMPLATE = REPO / "agent-kit" / "templates" / "Makefile.mk"
GITHUB_FRAGMENT = REPO / "agent-kit" / "templates" / "Makefile.github.mk"

RECORDER = (
    "#!/usr/bin/env bash\n"
    "python3 -B -c 'import json, sys; open(\"args.log\", \"a\").write(json.dumps(sys.argv[1:]) + \"\\n\")' \"$@\"\n"
)
RECORDER_PY = (
    "import json, sys\n"
    "open('args.log', 'a').write(json.dumps(sys.argv[1:]) + '\\n')\n"
)

# Values holding `$`: make would expand them (run $(shell ...), write files with $(file ...)).
# A target refuses these before anything runs.
WITH_DOLLAR = [
    "$(shell touch MARKER)",
    "$(touch MARKER)",
    "$(file >MARKER,x)",
    "$(eval X:=$(shell touch MARKER))",
    "$(shell touch MARKER) x",
    "x $(shell touch MARKER)",
    "x$$(touch MARKER)",
    "x$(shell touch MARKER)",
    "${HOME}",
    "$HOME",
    "a$b",
    "$$",
]
# Values holding only characters the shell would act on. They are not make syntax, so they are
# allowed, and they must reach the script as exactly one argument.
SHELL_META = [
    "x; touch MARKER",
    '"; touch MARKER; "',
    "'; touch MARKER; '",
    "x && touch MARKER",
    "x | touch MARKER",
    "x\ntouch MARKER",
    "`touch MARKER`",
    "-- touch MARKER",
    "a b",
    "it's",
    "50% done",
    "x > MARKER",
    "x < MARKER",
    "*",
]


class MakeCase(unittest.TestCase):
    """Builds a throwaway project from the repo Makefile or the template."""

    def setUp(self):
        self.work = new_workdir(prefix="make-vars-")
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)

    def project(self, kind: str, makefile: str | None = None) -> Path:
        """kind 'repo' (kit at agent-kit/) or 'template' (kit at _docs/agent-kit/)."""
        folder = self.work / kind
        folder.mkdir(exist_ok=True)
        kit = "agent-kit" if kind == "repo" else "_docs/agent-kit"
        source = makefile if makefile is not None else (REPO_MAKEFILE if kind == "repo" else TEMPLATE).read_text(encoding="utf-8")
        (folder / "Makefile").write_text(source, encoding="utf-8")
        scripts = folder / kit / "scripts"
        scripts.mkdir(parents=True, exist_ok=True)
        for name in ("verify.sh", "check-tier.sh"):
            (scripts / name).write_text(RECORDER, encoding="utf-8")
        (scripts / "issue-hash.py").write_text(RECORDER_PY, encoding="utf-8")
        return folder

    def make(self, folder: Path, *args: str):
        env = {k: v for k, v in os.environ.items() if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "BASE", "TIER", "N", "FILE", "MSG")}
        return subprocess.run(["make", "--no-print-directory", *args], cwd=str(folder), env=env,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, errors="replace")

    @staticmethod
    def received(folder: Path) -> list:
        log = folder / "args.log"
        return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []

    def assert_nothing_ran(self, folder: Path, done):
        self.assertFalse((folder / "MARKER").exists(), "a crafted value ran a command and created MARKER")
        self.assertEqual(self.received(folder), [], "a script ran")
        self.assertNotEqual(done.returncode, 0)


class TargetCase(MakeCase):
    kinds = ("repo", "template")

    def each_kind(self):
        for kind in self.kinds:
            with self.subTest(kind=kind):
                yield kind, self.project(kind)


class VerifyBaseTest(TargetCase):
    def test_shell_characters_in_base_run_nothing_and_arrive_as_one_argument(self):
        for kind, folder in self.each_kind():
            for value in SHELL_META:
                with self.subTest(kind=kind, base=value):
                    (folder / "args.log").unlink(missing_ok=True)
                    done = self.make(folder, "verify", "BASE=" + value)
                    self.assertFalse((folder / "MARKER").exists(), "BASE created MARKER")
                    self.assertEqual(done.returncode, 0, done.stderr)
                    self.assertEqual(self.received(folder), [[value]])

    def test_a_base_holding_a_dollar_is_refused_before_anything_runs(self):
        for kind, folder in self.each_kind():
            for value in WITH_DOLLAR:
                with self.subTest(kind=kind, base=value):
                    done = self.make(folder, "verify", "BASE=" + value)
                    self.assert_nothing_ran(folder, done)
                    self.assertIn("Usage: make verify", done.stderr)

    def test_a_valid_base_is_passed_through(self):
        for kind, folder in self.each_kind():
            for value in ("HEAD", "origin/main", "HEAD~3", "v1.0^{commit}", "a" * 40):
                with self.subTest(kind=kind, base=value):
                    (folder / "args.log").unlink(missing_ok=True)
                    done = self.make(folder, "verify", "BASE=" + value)
                    self.assertEqual(done.returncode, 0, done.stderr)
                    self.assertEqual(self.received(folder), [[value]])

    def test_no_base_still_runs_the_script(self):
        for kind, folder in self.each_kind():
            done = self.make(folder, "verify")
            self.assertEqual(done.returncode, 0, done.stderr)
            # The script treats no argument and an empty one alike (BASE="${1:-}").
            self.assertIn(self.received(folder), ([[]], [[""]]))

    def test_a_base_from_the_environment_is_also_checked(self):
        for kind, folder in self.each_kind():
            env = {k: v for k, v in os.environ.items() if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL")}
            env["BASE"] = "$(shell touch MARKER)"
            done = subprocess.run(["make", "--no-print-directory", "verify"], cwd=str(folder), env=env,
                                  stdin=subprocess.DEVNULL, capture_output=True, text=True)
            self.assert_nothing_ran(folder, done)


class TierCheckTest(TargetCase):
    def test_shell_characters_in_base_run_nothing_and_arrive_as_one_argument(self):
        for kind, folder in self.each_kind():
            for value in SHELL_META:
                with self.subTest(kind=kind, base=value):
                    (folder / "args.log").unlink(missing_ok=True)
                    done = self.make(folder, "tier-check", "TIER=light", "BASE=" + value)
                    self.assertFalse((folder / "MARKER").exists(), "BASE created MARKER")
                    self.assertEqual(done.returncode, 0, done.stderr)
                    self.assertEqual(self.received(folder), [["light", value]])

    def test_a_base_holding_a_dollar_is_refused_before_anything_runs(self):
        for kind, folder in self.each_kind():
            for value in WITH_DOLLAR:
                with self.subTest(kind=kind, base=value):
                    done = self.make(folder, "tier-check", "TIER=light", "BASE=" + value)
                    self.assert_nothing_ran(folder, done)
                    self.assertIn("Usage: make tier-check", done.stderr)

    def test_a_crafted_tier_is_refused_before_any_script_runs(self):
        bad = WITH_DOLLAR + ["`touch MARKER`", "light; touch MARKER", "light $(shell touch MARKER)",
                             "light heavy", "", "LIGHT", "light\ntouch MARKER", "lights", "-light",
                             "light'; touch MARKER; '"]
        for kind, folder in self.each_kind():
            for value in bad:
                with self.subTest(kind=kind, tier=value):
                    done = self.make(folder, "tier-check", "TIER=" + value)
                    self.assert_nothing_ran(folder, done)
                    self.assertIn("Usage: make tier-check", done.stderr)

    def test_a_missing_tier_is_refused(self):
        for kind, folder in self.each_kind():
            self.assert_nothing_ran(folder, self.make(folder, "tier-check"))

    def test_each_valid_tier_reaches_the_script_with_the_base(self):
        for kind, folder in self.each_kind():
            for tier in ("light", "standard", "heavy"):
                (folder / "args.log").unlink(missing_ok=True)
                done = self.make(folder, "tier-check", "TIER=" + tier, "BASE=HEAD")
                self.assertEqual(done.returncode, 0, done.stderr)
                self.assertEqual(self.received(folder), [[tier, "HEAD"]])

    def test_a_valid_tier_without_a_base_still_runs_the_script(self):
        for kind, folder in self.each_kind():
            done = self.make(folder, "tier-check", "TIER=standard")
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual(self.received(folder), [["standard", ""]])


class IssueHashNumberTest(TargetCase):
    def test_a_crafted_number_is_refused_before_anything_runs(self):
        bad = ["$(shell touch MARKER)", "$(touch MARKER)", "`touch MARKER`", "1; touch MARKER",
               "1 $(shell touch MARKER)", "$(file >MARKER,x)", "$(shell touch MARKER) 1", "1$(shell touch MARKER)",
               '1"; touch MARKER; "', "1\ntouch MARKER", "$(eval X:=$(shell touch MARKER))"]
        for kind, folder in self.each_kind():
            for value in bad:
                with self.subTest(kind=kind, n=value):
                    done = self.make(folder, "issue-hash", "N=" + value)
                    self.assert_nothing_ran(folder, done)
                    self.assertIn("Usage: make issue-hash N=<issue number>", done.stderr)

    def test_the_other_refused_numbers_run_nothing(self):
        # " 1" is not here: make strips the leading space of a command-line value, so it is "1".
        bad = ["", "0", "007", "-1", "1e3", "1.5", "1 ", "1 2", "1234567890", "--help", "a1", "1a", "+1"]
        for kind, folder in self.each_kind():
            for value in bad:
                with self.subTest(kind=kind, n=value):
                    done = self.make(folder, "issue-hash", "N=" + value)
                    self.assert_nothing_ran(folder, done)

    def test_a_missing_number_is_refused(self):
        for kind, folder in self.each_kind():
            done = self.make(folder, "issue-hash")
            self.assert_nothing_ran(folder, done)
            self.assertIn("Usage: make issue-hash N=<issue number>", done.stderr)

    def test_valid_numbers_reach_the_script_unchanged(self):
        for kind, folder in self.each_kind():
            for value in ("1", "13", "57", "999999999", "100"):
                with self.subTest(kind=kind, n=value):
                    (folder / "args.log").unlink(missing_ok=True)
                    done = self.make(folder, "issue-hash", "N=" + value)
                    self.assertEqual(done.returncode, 0, done.stderr)
                    self.assertEqual(self.received(folder), [[value]])

    def test_a_number_from_the_environment_is_also_safe(self):
        for kind, folder in self.each_kind():
            env = {k: v for k, v in os.environ.items() if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL")}
            env["N"] = "$(shell touch MARKER)"
            done = subprocess.run(["make", "--no-print-directory", "issue-hash"], cwd=str(folder), env=env,
                                  stdin=subprocess.DEVNULL, capture_output=True, text=True)
            self.assert_nothing_ran(folder, done)


class IssueDumpAndGithubTargetsTest(TargetCase):
    """The targets that were already safe stay safe (the audit found no flaw in them)."""

    def test_issue_dump_refuses_a_crafted_number(self):
        for kind, folder in self.each_kind():
            for value in ("$(shell touch MARKER)", "$(file >MARKER,x)", "1; touch MARKER", "`touch MARKER`"):
                with self.subTest(kind=kind, n=value):
                    done = self.make(folder, "issue-dump", "N=" + value)
                    self.assert_nothing_ran(folder, done)
                    self.assertIn("Usage: make issue-dump", done.stderr)

    def test_the_github_fragment_refuses_crafted_values(self):
        for kind in self.kinds:
            fragment = GITHUB_FRAGMENT.read_text(encoding="utf-8")
            root = "agent-kit" if kind == "repo" else "_docs/agent-kit"
            base = (REPO_MAKEFILE if kind == "repo" else TEMPLATE).read_text(encoding="utf-8")
            folder = self.project(kind, makefile=base if kind == "repo" else base + "\n" + fragment)
            (folder / root / "scripts" / "issue-create.sh").write_text(RECORDER, encoding="utf-8")
            (folder / root / "scripts" / "issue-comment.sh").write_text(RECORDER, encoding="utf-8")
            for value in ("$(shell touch MARKER)", "$(file >MARKER,x)", "`touch MARKER`", ".scratch/x;touch MARKER"):
                with self.subTest(kind=kind, value=value):
                    done = self.make(folder, "issue-create", "FILE=" + value)
                    self.assert_nothing_ran(folder, done)
                    done = self.make(folder, "issue-comment", "N=" + value, "FILE=.scratch/x.md")
                    self.assert_nothing_ran(folder, done)
                    done = self.make(folder, "issue-comment", "N=5", "FILE=" + value)
                    self.assert_nothing_ran(folder, done)


class TemplateOnlyTargetsTest(MakeCase):
    """test-one and migration are project placeholders; their recipes must use "$$VAR"."""

    def instantiate(self, target: str, placeholder: str) -> Path:
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn(placeholder, text)
        folder = self.work / ("template-" + target)
        folder.mkdir()
        (folder / "record.sh").write_text(RECORDER, encoding="utf-8")
        (folder / "record.sh").chmod(0o755)
        (folder / "Makefile").write_text(text.replace(placeholder, "bash ./record.sh"), encoding="utf-8")
        return folder

    def test_test_one_passes_the_file_as_one_argument_and_runs_nothing_else(self):
        folder = self.instantiate("test-one", "<the project's single-file test command>")
        for value in SHELL_META + ["tests/test_a.py", "a b"]:
            with self.subTest(file=value):
                (folder / "args.log").unlink(missing_ok=True)
                done = self.make(folder, "test-one", "FILE=" + value)
                self.assertFalse((folder / "MARKER").exists(), "FILE created MARKER")
                self.assertEqual(done.returncode, 0, done.stderr)
                self.assertEqual(self.received(folder), [[value]])

    def test_test_one_refuses_a_file_holding_a_dollar(self):
        folder = self.instantiate("test-one", "<the project's single-file test command>")
        for value in WITH_DOLLAR:
            with self.subTest(file=value):
                done = self.make(folder, "test-one", "FILE=" + value)
                self.assert_nothing_ran(folder, done)
                self.assertIn("Usage: make test-one", done.stderr)

    def test_test_one_without_a_file_prints_usage_and_runs_nothing(self):
        folder = self.instantiate("test-one", "<the project's single-file test command>")
        done = self.make(folder, "test-one")
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("Usage: make test-one FILE=", done.stdout + done.stderr)
        self.assertEqual(self.received(folder), [])

    def test_migration_passes_the_message_as_one_argument_and_runs_nothing_else(self):
        folder = self.instantiate("migration", "<the project's migration command>")
        for value in SHELL_META + ["add users table", 'it\'s "quoted"']:
            with self.subTest(msg=value):
                (folder / "args.log").unlink(missing_ok=True)
                done = self.make(folder, "migration", "MSG=" + value)
                self.assertFalse((folder / "MARKER").exists(), "MSG created MARKER")
                self.assertEqual(done.returncode, 0, done.stderr)
                self.assertEqual(self.received(folder), [[value]])

    def test_migration_refuses_a_message_holding_a_dollar(self):
        folder = self.instantiate("migration", "<the project's migration command>")
        for value in WITH_DOLLAR:
            with self.subTest(msg=value):
                done = self.make(folder, "migration", "MSG=" + value)
                self.assert_nothing_ran(folder, done)
                self.assertIn("Usage: make migration", done.stderr)

    def test_migration_without_a_message_prints_usage_and_runs_nothing(self):
        folder = self.instantiate("migration", "<the project's migration command>")
        done = self.make(folder, "migration")
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("Usage: make migration MSG=", done.stdout + done.stderr)
        self.assertEqual(self.received(folder), [])


def block(text: str, name: str) -> list:
    """The lines of one make target (header and recipe) or definition, up to the blank line."""
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(name + ":") or line.startswith(name + " ="))
    out = []
    for line in lines[start:]:
        if not line.strip():
            break
        out.append(line)
    return out


class SameInBothFilesTest(unittest.TestCase):
    def normalized(self, path: Path, kit: str) -> str:
        return path.read_text(encoding="utf-8").replace(kit, "KIT")

    def test_issue_hash_issue_number_ok_verify_and_tier_check_are_the_same_in_the_repo_and_the_template(self):
        repo = self.normalized(REPO_MAKEFILE, "agent-kit/scripts")
        template = self.normalized(TEMPLATE, "_docs/agent-kit/scripts")
        for name in ("issue-hash", "issue-number-ok", "issue-dump", "verify", "tier-check"):
            with self.subTest(name=name):
                self.assertEqual(block(repo, name), block(template, name))

    def test_no_make_variable_is_expanded_in_a_check_or_pasted_into_a_recipe_line(self):
        """Read every target that takes a variable: checks use $(value X), recipes use "$$X"."""
        for path in (REPO_MAKEFILE, TEMPLATE):
            text = path.read_text(encoding="utf-8")
            for name, variables in (("issue-hash", "N"), ("verify", "BASE"), ("tier-check", "TIER|BASE"),
                                    ("test-one", "FILE"), ("migration", "MSG")):
                if name in ("test-one", "migration") and path == REPO_MAKEFILE:
                    continue
                body = "\n".join(block(text, name))
                with self.subTest(file=path.name, target=name):
                    self.assertIsNone(re.search(r"\$\((%s)\)" % variables, body),
                                      "a variable is expanded with $(X):\n" + body)

    def test_the_rule_comment_names_the_two_safe_forms(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        comment = text[text.index("# Rule for every target"):text.index("issue-hash:")]
        self.assertIn("$(value X)", comment)
        self.assertIn('"$$X"', comment)
        self.assertIn("issue-dump", comment)
        self.assertIn("worked example", comment)


if __name__ == "__main__":
    unittest.main()
