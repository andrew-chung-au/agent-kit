"""Tests for agent-kit/scripts/check-claims.py.

Unit tests cover how a make target is read; the other tests build small kits
under .scratch/ and run the checker on them. The last test runs it on the
real kit, which must pass.
"""
from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CHECKER = REPO / "agent-kit" / "scripts" / "check-claims.py"
SCRATCH = REPO / ".scratch"

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("check_claims", CHECKER)
claims = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(claims)

MAKEFILE_MK = """\
help: ## List targets
\t@echo help

verify: ## Verify: make verify [BASE=<commit>]
\t@echo verify

install: ## Install
\t<the project's install command(s)>

test-one: ## One file: make test-one FILE=path
\t@echo one

<name>-start: ## Start <name>
\t@echo start
"""
BLUEPRINTS = """\
# Blueprints

| Blueprint | Source |
|---|---|
| Templates | `templates/Makefile.mk` |
| Scripts | `scripts/` |
| Roles and procedures | `team/`, `procedures/` |
| Claude Code layer | `claude-code/START.md`, with `claude-code/agents/` and `claude-code/hooks/` |
"""


class MakeTargetTest(unittest.TestCase):
    def targets(self, code):
        return list(claims.make_claims(code))

    def test_skips_options_values_and_assignments(self):
        self.assertEqual(self.targets("make -C <project> install verify"), ["install"])
        self.assertEqual(self.targets("make test-one FILE=path"), ["test-one"])
        self.assertEqual(self.targets("make verify BASE=<commit>"), ["verify"])
        self.assertEqual(self.targets("make -f other.mk --directory=x -s lint"), ["lint"])
        self.assertEqual(self.targets("make --file x.mk VAR=1 e2e"), ["e2e"])
        for opt in ("-I", "-o", "-W", "--include", "--old-file", "--assume-old", "--directory"):
            self.assertEqual(self.targets(f"make {opt} value hooks"), ["hooks"], opt)

    def test_skips_placeholders_and_bare_make(self):
        self.assertEqual(self.targets("make <name>-start"), [])
        self.assertEqual(self.targets("make <target>"), [])
        self.assertEqual(self.targets("make"), [])
        self.assertEqual(self.targets("make -C dir VAR=1"), [])
        self.assertEqual(self.targets("Bash(make *)"), [])

    def test_finds_make_after_operators_and_prefixes(self):
        self.assertEqual(self.targets("VAR=x make run"), ["run"])
        self.assertEqual(self.targets("make install && make verify"), ["install", "verify"])


class KitCase(unittest.TestCase):
    """Builds a minimal passing kit under .scratch/ for each test."""

    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix="claims-", dir=SCRATCH))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.kit = self.root / "agent-kit"
        self.write("templates/Makefile.mk", MAKEFILE_MK)
        self.write("templates/task-template.md", "# Task\n")
        self.write("scripts/verify.sh", "#!/bin/sh\n")
        self.write("blueprints.md", BLUEPRINTS)
        self.write("claude-code/START.md", "Start.\n")
        self.write("claude-code/agents/pm.md", "PM.\n")
        self.write("claude-code/hooks/guard_git.py", "\n")
        self.write("team/pm.md", "PM role.\n")
        self.write("procedures/verify.md", "Verify.\n")

    def write(self, rel, text):
        path = self.kit / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def check(self):
        result = subprocess.run([sys.executable, "-B", str(CHECKER), "--kit", str(self.kit)],
                                cwd=self.root, capture_output=True, text=True, timeout=60)
        return result.returncode, result.stdout + result.stderr

    def assert_passes(self):
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn("claims: OK", out)
        return out

    def assert_fails(self, *expected):
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("claims: FAIL", out)
        for text in expected:
            self.assertIn(text, out)
        return out


class MakeClaimsTest(KitCase):
    def test_minimal_kit_passes(self):
        self.assert_passes()

    def test_prose_is_not_a_claim(self):
        self.write("team/qa.md", "Make the change, then make sure it works. Run make nope.\n")
        self.assert_passes()

    def test_unknown_target_in_inline_code_fails_with_doc_line_and_claim(self):
        self.write("team/qa.md", "Intro.\n\nRun `make run`, then `make stop`.\n")
        out = self.assert_fails("agent-kit/team/qa.md:3:", "`run`", "`stop`")
        self.assertIn("make run", out)

    def test_unknown_target_in_fenced_block_fails(self):
        self.write("procedures/x.md", "Text\n\n```\n- `make probe URL=...` wrapper\nmake verify\n```\n")
        self.assert_fails("agent-kit/procedures/x.md:4:", "`probe`")

    def test_fenced_block_text_after_fence_is_prose(self):
        self.write("procedures/x.md", "```\nmake verify\n```\nmake nope outside code\n")
        self.assert_passes()

    def test_known_and_skipped_forms_pass(self):
        self.write("team/qa.md", "`make -C <project> install verify`, `make test-one FILE=path`, "
                                 "`make verify BASE=<commit>`, `make <name>-start`, `make <target>`, `make`.\n")
        self.assert_passes()

    def test_option_value_is_not_the_target(self):
        self.write("team/qa.md", "`make -C nope missing-target`\n")
        self.assert_fails("`missing-target`")

    def test_root_makefile_is_not_a_source(self):
        (self.root / "Makefile").write_text("only-root:\n\t@echo root\n", encoding="utf-8")
        self.write("team/qa.md", "Run `make only-root`.\n")
        self.assert_fails("agent-kit/team/qa.md:1:", "`only-root`")

    def test_named_mk_fragment_adds_targets(self):
        self.write("templates/extra.mk", "extra: ## Extra\n\t@echo extra\n")
        self.write("team/qa.md", "Merge `templates/extra.mk`, then run `make extra`.\n")
        self.assert_passes()

    def test_fragment_targets_are_only_for_the_doc_naming_it(self):
        self.write("templates/extra.mk", "extra: ## Extra\n\t@echo extra\n")
        self.write("team/qa.md", "Merge `templates/extra.mk`.\n")
        self.write("team/pm.md", "Run `make extra`.\n")
        self.assert_fails("agent-kit/team/pm.md:1:", "`extra`")

    def test_missing_mk_fragment_fails_path_check(self):
        self.write("team/qa.md", "Merge `templates/missing.mk`, then run `make extra`.\n")
        self.assert_fails("kit path `templates/missing.mk` does not exist", "`extra`")


class PathClaimsTest(KitCase):
    def test_doc_relative_path_resolves(self):
        self.write("claude-code/START.md", "Copy `agents/pm.md` into place.\n")
        self.assert_passes()

    def test_kit_root_path_resolves(self):
        self.write("team/pm.md", "Use `templates/task-template.md`.\n")
        self.assert_passes()

    def test_kit_prefixed_paths_resolve_to_kit_root(self):
        self.write("team/pm.md", "See `_docs/agent-kit/team/pm.md` and `agent-kit/scripts/verify.sh`.\n")
        self.assert_passes()

    def test_missing_path_fails_with_doc_line_and_span(self):
        self.write("team/pm.md", "Line one.\nRun `scripts/nope.sh`.\n")
        self.assert_fails("agent-kit/team/pm.md:2: kit path `scripts/nope.sh` does not exist")

    def test_missing_kit_prefixed_path_fails(self):
        self.write("team/pm.md", "See `_docs/agent-kit/team/nope.md`.\n")
        self.assert_fails("`_docs/agent-kit/team/nope.md`")

    def test_trailing_slash_must_be_a_directory(self):
        self.write("team/pm.md", "See `templates/` and `claude-code/hooks/`.\n")
        self.assert_passes()
        self.write("team/pm.md", "See `scripts/verify.sh/`.\n")
        self.assert_fails("kit directory `scripts/verify.sh/` does not exist")

    def test_placeholders_globs_anchors_and_bare_names_are_skipped(self):
        spans = ["templates/<name>.md", "scripts/*.sh", "scripts/$NAME", "team/~x",
                 "templates/...", "scripts/x.sh FOO=1", "templates/a=b", "team/pm.md#",
                 "templates/two words.md", "agent-kit/https://x", "nope.md", "settings.json",
                 "src/app/nope.py", ".claude/agents/nope.md"]
        self.write("team/pm.md", "".join(f"`{s}`\n" for s in spans))
        self.assert_passes()

    def test_paths_in_prose_are_not_checked(self):
        self.write("team/pm.md", "Read scripts/nope.sh in prose.\n")
        self.assert_passes()


class CoverageTest(KitCase):
    def test_new_top_level_module_without_row_fails(self):
        self.write("newmodule/run.sh", "#!/bin/sh\n")
        self.assert_fails("no row or path names installable `newmodule/`")

    def test_new_first_level_directory_without_row_fails(self):
        self.write("claude-code/newdir/file.py", "\n")
        self.assert_fails("no row or path names installable `claude-code/newdir/`")

    def test_new_file_in_documented_directory_passes(self):
        self.write("claude-code/hooks/new_hook.py", "\n")
        self.write("claude-code/hooks/nested/deeper.py", "\n")
        self.assert_passes()

    def test_row_naming_new_module_passes(self):
        self.write("newmodule/run.sh", "#!/bin/sh\n")
        self.write("blueprints.md", BLUEPRINTS + "| New module | `newmodule/` |\n")
        self.assert_passes()

    def test_kit_docs_are_not_installable(self):
        for name in ("README.md", "environments.md", "CHANGELOG.md", "releasing.md", "setup.md", "process.md"):
            self.write(name, "Doc.\n")
        self.assert_passes()

    def test_new_top_level_file_without_row_fails(self):
        self.write("newtool.sh", "#!/bin/sh\n")
        self.assert_fails("installable `newtool.sh`")


class TemplateFilesTest(KitCase):
    def test_missing_new_template_path_fails_with_doc_line_and_span(self):
        self.write("team/pm.md", "Line one.\nCopy `templates/source.md`.\n")
        self.assert_fails("agent-kit/team/pm.md:2: kit path `templates/source.md` does not exist")

    def test_filename_pattern_and_example_names_are_not_flagged(self):
        procedure = (REPO / "agent-kit" / "procedures" / "session-summary.md").read_text(encoding="utf-8")
        lines = procedure.splitlines()
        start = lines.index("Examples:") + 1
        examples = []
        for line in lines[start:]:
            if not line.strip():
                break
            examples += re.findall(r"`([^`]+\.md)`", line)
        self.assertGreaterEqual(len(examples), 3)
        kinds = re.findall(r"^\| `([a-z]+)` \|", procedure, re.MULTILINE)
        self.assertIn("issue", kinds)
        convention = re.compile(
            r"^\d{4}-\d{2}-\d{2}T\d{4}Z-(?P<kind>[a-z]+)-(?:\d{3}-)?"
            r"(?:(?:orchestrator|pm|engineer|qa)-)?[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
        for name in examples:
            match = convention.match(name)
            self.assertIsNotNone(match, name)
            self.assertIn(match.group("kind"), kinds, name)
        # A name with a colon in the timestamp breaks the convention.
        self.assertIsNone(convention.match("2026-10-31T06:42Z-issue-022-engineer-x.md"))

        # A kit whose procedure holds the pattern and those names passes.
        self.write("procedures/verify.md",
                   "Name it `<timestamp>-<kind>-<id>-<role>-<slug>.md`.\n"
                   "Pattern `templates/<timestamp>-<kind>-x.md` is a placeholder.\n"
                   + "".join(f"- `{name}`\n" for name in examples))
        self.assert_passes()

        # Negative control: the same names under templates/ are read as kit paths and fail.
        self.write("procedures/verify.md", "".join(f"- `templates/{name}`\n" for name in examples))
        out = self.assert_fails()
        for name in examples:
            self.assertIn(f"templates/{name}", out)


class RealKitTest(unittest.TestCase):
    def test_every_loose_template_has_a_blueprints_row(self):
        kit = REPO / "agent-kit"
        blueprints = (kit / "blueprints.md").read_text(encoding="utf-8")
        missing = [f"templates/{p.name}" for p in sorted((kit / "templates").iterdir())
                   if p.is_file() and f"templates/{p.name}" not in blueprints]
        self.assertEqual(missing, [], "templates with no blueprints.md row")

    def test_todays_kit_passes(self):
        result = subprocess.run([sys.executable, "-B", str(CHECKER)], cwd=REPO,
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("claims: OK", result.stdout)


class ScopeTest(KitCase):
    def test_docs_outside_the_kit_are_not_read(self):
        other = self.root / "vuln-triage" / "agent-kit" / "team"
        other.mkdir(parents=True)
        (other / "pm.md").write_text("Run `make nope` and read `scripts/nope.sh`.\n", encoding="utf-8")
        (self.root / "README.md").write_text("Run `make nope`.\n", encoding="utf-8")
        self.assert_passes()


if __name__ == "__main__":
    unittest.main()
