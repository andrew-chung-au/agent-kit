"""A make recipe never pastes a command-line variable before it was checked (issue #72).

Issue #57 made the make targets that take a variable safe: a check reads `$(value X)`, which
make does not expand, and a recipe either passes `"$$X"` (the shell variable) or pastes `$(X)`
only after such a check refused everything but an allowed value. The pairing was a convention.
This test enforces it for the three Makefiles, so a new or edited target cannot break it silently.

Definition used here. A command-line variable is any `$(NAME)` or `${NAME}` where NAME matches
`[A-Z][A-Z0-9_]*`, found in a recipe line (a tab-started line under a target; `$$` is a shell
escape and is skipped), except
- make's own names in ALLOWED_MAKE_NAMES (a short list), and
- variables the Makefile itself defines at top level with `=`, `:=`, `::=` or `?=`.

Rule 1: every `$(X)` in a recipe line needs an earlier line of the same target that contains
        `$(value X)` and `$(error` (a check line). A recipe using `"$$X"` has no `$(X)` and
        needs no check line.
Rule 2: a check line (one that contains `$(error`) never contains a bare `$(X)`; only
        `$(value X)` is allowed there. This is the flaw #57 found: `$(N)` expanded in the check.

The rule functions take text, so the mutation tests change strings, not the live files.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MAKEFILES = [
    REPO / "Makefile",
    REPO / "agent-kit" / "templates" / "Makefile.mk",
    REPO / "agent-kit" / "templates" / "Makefile.github.mk",
]
ALLOWED_MAKE_NAMES = {"MAKEFILE_LIST", "MAKE", "CURDIR", "MAKEFLAGS"}

TARGET = re.compile(r"^([A-Za-z0-9_.%/-]+(?:[ ][A-Za-z0-9_.%/-]+)*)[ ]*::?(?!=)")
DEFINITION = re.compile(r"^([A-Za-z0-9_.-]+)[ ]*(?:::=|:=|\?=|=)")
VARIABLE = re.compile(r"\$[({]([A-Z][A-Z0-9_]*)[)}]")


def check_text(text: str, name: str = "Makefile") -> list[str]:
    """Return one message per violation, each naming the file, the target and the variable."""
    defined = {m.group(1) for m in map(DEFINITION.match, text.splitlines()) if m}
    skip = ALLOWED_MAKE_NAMES | defined
    problems: list[str] = []
    target = None
    checked: set[str] = set()  # variables with a `$(value X)` check line earlier in this target
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("\t"):
            if target is None:
                continue
            body = line.replace("$$", "")
            is_check = "$(error" in body
            for var in VARIABLE.findall(body):
                if var in skip:
                    continue
                if is_check:
                    problems.append("%s:%d target %s: $(%s) is expanded in a check line; use $(value %s)"
                                    % (name, number, target, var, var))
                elif var not in checked:
                    problems.append("%s:%d target %s: $(%s) is pasted with no earlier $(value %s) check"
                                    % (name, number, target, var, var))
            if is_check:
                checked.update(re.findall(r"\$\(value ([A-Z][A-Z0-9_]*)\)", body))
            continue
        match = TARGET.match(line)
        if match and not line.startswith("#"):
            target, checked = match.group(1), set()
        elif line.strip() and not line.startswith("#"):
            target = None  # an assignment or directive ends the target
    return problems


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class LiveMakefilesTest(unittest.TestCase):
    def test_every_makefile_follows_the_pairing_rule(self):
        for path in MAKEFILES:
            with self.subTest(file=str(path.relative_to(REPO))):
                self.assertEqual(check_text(read(path), path.name), [])

    def test_the_files_were_actually_scanned(self):
        # Guards against a parser that finds no recipes and so passes everything.
        text = read(REPO / "Makefile")
        for var in ("N", "FILE"):
            self.assertIn("$(%s)" % var, text)
        mutated = text.replace("$(value FILE)", "$(FILE)")
        self.assertNotEqual(check_text(mutated), [])


class MutationTest(unittest.TestCase):
    """The rule reports each of these; the unmutated text and a `"$$X"` recipe pass."""

    @staticmethod
    def drop_line(text: str, needle: str, nth: int = 0) -> str:
        lines = text.splitlines(keepends=True)
        hits = [i for i, line in enumerate(lines) if needle in line]
        del lines[hits[nth]]
        return "".join(lines)

    def test_unmutated_text_passes(self):
        self.assertEqual(check_text(read(REPO / "Makefile")), [])

    def test_a_target_using_shell_variable_passes(self):
        text = "foo: ## x\n\t$(if $(value X),,$(error no))\n\t@bash s.sh \"$$X\"\n"
        self.assertEqual(check_text(text), [])

    def test_a_paired_target_passes(self):
        text = "foo: ## x\n\t$(if $(value X),,$(error no))\n\t@bash s.sh \"$(X)\"\n"
        self.assertEqual(check_text(text), [])

    def test_a_make_name_and_a_defined_variable_pass(self):
        text = "KIT := agent-kit\nfoo:\n\t@awk '{}' $(MAKEFILE_LIST) $(KIT)\n"
        self.assertEqual(check_text(text), [])

    def test_a_recipe_variable_in_a_comment_or_assignment_is_ignored(self):
        text = "# $(N)\nfoo:\n\t@true\nV = $(N)\n"
        self.assertEqual(check_text(text), [])

    def test_a_shell_escape_is_not_a_variable(self):
        text = "foo:\n\t@echo $$(N)\n"
        self.assertEqual(check_text(text), [])

    def test_a_mutation_a_check_line_removed_from_issue_dump(self):
        text = read(REPO / "Makefile")
        mutated = self.drop_line(text, "Usage: make issue-dump N=")
        problems = check_text(mutated, "Makefile")
        self.assertTrue(any("target issue-dump" in p and "$(N)" in p for p in problems), problems)

    def test_b_mutation_check_removed_from_issue_create(self):
        text = read(REPO / "Makefile")
        mutated = self.drop_line(text, "Usage: make issue-create FILE=")
        problems = check_text(mutated, "Makefile")
        self.assertTrue(any("target issue-create" in p and "$(FILE)" in p for p in problems), problems)

    def test_c_mutation_value_dropped_in_issue_hash_check(self):
        text = read(REPO / "Makefile")
        old = "$(if $(call issue-number-ok,$(value N)),,$(error Usage: make issue-hash"
        self.assertIn(old, text)
        mutated = text.replace(old, old.replace("$(value N)", "$(N)"))
        problems = check_text(mutated, "Makefile")
        self.assertTrue(any("target issue-hash" in p and "check line" in p for p in problems), problems)

    def test_d_mutation_new_target_pastes_with_no_check(self):
        mutated = read(REPO / "Makefile") + "\nfoo: ## new\n\t@bash agent-kit/scripts/x.sh $(FOO)\n"
        problems = check_text(mutated, "Makefile")
        self.assertTrue(any("target foo" in p and "$(FOO)" in p for p in problems), problems)

    def test_e_mutation_check_on_a_later_line(self):
        text = ("foo: ## x\n\t@bash s.sh \"$(N)\"\n"
                "\t$(if $(call issue-number-ok,$(value N)),,$(error Usage))\n")
        problems = check_text(text, "Makefile")
        self.assertTrue(any("target foo" in p and "$(N)" in p for p in problems), problems)

    def test_a_check_for_another_target_does_not_count(self):
        text = ("foo:\n\t$(if $(value N),,$(error no))\n"
                "bar:\n\t@bash s.sh \"$(N)\"\n")
        problems = check_text(text, "Makefile")
        self.assertTrue(any("target bar" in p for p in problems), problems)

    def test_a_check_for_another_variable_does_not_count(self):
        text = "foo:\n\t$(if $(value N),,$(error no))\n\t@bash s.sh \"$(FILE)\"\n"
        self.assertTrue(any("$(FILE)" in p for p in check_text(text)))

    def test_brace_form_is_also_checked(self):
        text = "foo:\n\t@bash s.sh \"${FILE}\"\n"
        self.assertTrue(any("FILE" in p for p in check_text(text)))

    def test_the_message_names_file_target_and_variable(self):
        problems = check_text("foo:\n\t@bash s.sh $(FOO)\n", "Makefile.mk")
        self.assertEqual(len(problems), 1)
        for word in ("Makefile.mk", "target foo", "$(FOO)"):
            self.assertIn(word, problems[0])


if __name__ == "__main__":
    unittest.main()
