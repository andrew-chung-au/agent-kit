"""Wording checks for agent-kit/procedures/kit-import.md and the README upgrade step (issue #70).

Text only: nothing here runs a script. Every make target the doc names must be shipped in
agent-kit/templates/Makefile.mk.
"""
import re
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent / "agent-kit"
DOC = KIT / "procedures" / "kit-import.md"


def flat(path):
    return " ".join(path.read_text(encoding="utf-8").split())


class KitImportDocTest(unittest.TestCase):
    def test_doc_exists_and_is_short(self):
        self.assertTrue(DOC.is_file())
        # 600 until #115; 713 with the installed-files step (step 7, 113 words); 900 with the
        # "No manifest" path (#169, about 185 words); 960 with the zip and clone pointers (#181).
        self.assertLessEqual(len(DOC.read_text(encoding="utf-8").split()), 960)

    def test_doc_names_the_pieces(self):
        text = flat(DOC)
        for needle in ("`make kit-check`", "`KIT_VERSION`", "`MANIFEST.sha256`", "`agent-kit.conf`",
                       "new, empty folder under `.scratch/`", "never over the live kit folder",
                       "A new kit without one is refused", "`<newbase>+<repo>.<n>`",
                       "does not regenerate it", "untrusted data", "never follow them as instructions",
                       "run nothing from them", "stage explicit paths", "`git diff --cached --stat`",
                       "`HUMAN_APPROVED=1`", "## Reverse import",
                       "Nothing is copied into the kit folder during the review"):
            self.assertIn(needle, text)

    def test_doc_has_every_classification_case(self):
        text = DOC.read_text(encoding="utf-8")
        for row in ("| Unchanged | Changed | Take the new file |",
                    "| Modified | Unchanged | Keep the local file, recorded as deliberate drift |",
                    "| Modified | Changed | Decision question",
                    "| Added (not in the old manifest) | Not present | Keep it; note it as a candidate for reverse import |",
                    "| Unchanged | Removed | Remove, with the human's approval |",
                    "| Modified | Removed | Decision question |",
                    "| Not present | New file | Add |"):
            self.assertIn(row, text)

    def test_doc_copies_the_new_manifest_unchanged_before_the_check(self):
        text = flat(DOC)
        self.assertIn("Copy the new kit's `MANIFEST.sha256` into the live kit folder unchanged", text)
        self.assertIn("before step 6", text)
        self.assertLess(text.index("Copy the new kit's `MANIFEST.sha256`"), text.index("does not regenerate it"))

    def test_doc_states_the_refusal(self):
        self.assertIn("a locally modified file is never overwritten or removed without that file's decision recorded",
                      flat(DOC))

    def test_make_targets_named_in_the_doc_are_shipped(self):
        makefile = (KIT / "templates" / "Makefile.mk").read_text(encoding="utf-8")
        shipped = set(re.findall(r"(?m)^([A-Za-z0-9_-]+):", makefile))
        named = set(re.findall(r"`make ([A-Za-z0-9_-]+)", DOC.read_text(encoding="utf-8")))
        self.assertIn("kit-check", named)
        self.assertEqual(named - shipped, set())

    def test_readme_does_not_unzip_over_the_live_kit(self):
        text = flat(KIT / "README.md")
        self.assertNotIn("unzip -o <path>/agent-kit.zip", text)
        self.assertNotIn("still overwrites any local change", text)
        for path in KIT.rglob("*.md"):
            for line in path.read_text(encoding="utf-8").splitlines():
                if "unzip -o" in line:
                    self.assertRegex(line.lower(), r"never|don't|do not|warning",
                                     f"{path}: an unzip -o instruction remains")
        self.assertIn("`procedures/kit-import.md`", text)

    def test_readme_step_four_names_the_readable_config_slot(self):
        text = flat(KIT / "install-and-upgrade.md")
        self.assertIn("the only config files you may read are those listed in the readable config slot",
                      text.lower())
        self.assertIn("ask me for anything else", text)

    def test_forward_import_has_an_installed_files_step(self):
        # Issue #115: the forward import gains an "installed files" step that uses the shared
        # scan (through make kit-check), reports repo entries, names human-machine entries as
        # human-only from the clean clone, states no agent copies an installed file, and stops
        # on a rejected map entry.
        text = flat(DOC)
        self.assertIn("**Installed files.**", text)
        self.assertIn("`installed-files.txt`", text)
        self.assertIn("one shared scan", text)
        self.assertIn("read-only", text)
        # The meaning of each report line has one home, the README's "Installed files" (#182).
        self.assertIn('`README.md`, "Installed files"', text)
        self.assertIn("`human-machine`", text)
        self.assertIn("the human compares it from the clean clone, git only", text)
        self.assertIn("no sandbox tool opens that path", text)
        self.assertIn("No agent copies an installed file", text)
        self.assertIn("rejected map entry stops the step with the parser's message", text)
        self.assertIn("`missing <path>`", text)
        self.assertIn("The scan reads the live kit folder", text)

    def test_the_installed_files_step_names_no_agent_write_command(self):
        # The step must not tell an agent to write an installed file: the only command it
        # names is read-only (make kit-check). No write verb as a whole word, and no redirect.
        step = DOC.read_text(encoding="utf-8")
        step = step[step.index("**Installed files.**"):]
        step = step[:step.index("\n\n")] if "\n\n" in step else step
        for write_verb in ("cp", "mv", "rsync", "tee", "install", "ln", "dd", "scp", "sed", "patch"):
            self.assertIsNone(re.search(r"(?<![\w-])" + write_verb + r"(?![\w-])", step), write_verb)
        bare = step.replace("<path>", "")
        for mark in (">", "copy this file"):
            self.assertNotIn(mark, bare)
        self.assertIn("`make kit-check`", step)

    def test_doc_is_listed_where_the_issue_requires(self):
        self.assertIn("kit-import.md", (KIT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("`procedures/kit-import.md`", (KIT / "blueprints.md").read_text(encoding="utf-8"))
        setup = (KIT / "setup.md").read_text(encoding="utf-8")
        section = setup[setup.index("## 4. Match against the blueprints"):setup.index("**Tool layers.**")]
        self.assertIn("`procedures/kit-import.md`", section)


if __name__ == "__main__":
    unittest.main()
