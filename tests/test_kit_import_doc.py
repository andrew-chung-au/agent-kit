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
        self.assertLessEqual(len(DOC.read_text(encoding="utf-8").split()), 600)

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
        text = flat(KIT / "README.md")
        self.assertIn("the only config files you may read are those listed in the `readable config` slot",
                      text.lower())
        self.assertIn("ask me for anything else", text)

    def test_doc_is_listed_where_the_issue_requires(self):
        self.assertIn("kit-import.md", (KIT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("`procedures/kit-import.md`", (KIT / "blueprints.md").read_text(encoding="utf-8"))
        setup = (KIT / "setup.md").read_text(encoding="utf-8")
        section = setup[setup.index("## 4. Match against the blueprints"):setup.index("**Tool layers.**")]
        self.assertIn("`procedures/kit-import.md`", section)


if __name__ == "__main__":
    unittest.main()
