"""The release note about installed files and shipping the map (issue #118).

Text only: nothing here runs a script. The kit README's release/update text must state that
the zip unpacks only the kit folder, that installed files are not placed by the unzip, and
that the human places them using installed-files.txt; that no agent places an installed
file; and that the human-machine entries are compared as in piece (e). installed-files.txt
must be inside the kit folder, so it ships in the zip and in MANIFEST.sha256.
"""
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
README = KIT / "README.md"
MAP = KIT / "installed-files.txt"


def flat(path):
    return " ".join(path.read_text(encoding="utf-8").split())


class ReleaseInstalledFilesTest(unittest.TestCase):
    def setUp(self):
        self.flat = flat(README)

    def test_the_map_is_inside_the_kit_folder(self):
        # So it is in the release zip and in MANIFEST.sha256 (kit-manifest includes every
        # regular top-level kit file). This is the structural half of the acceptance.
        self.assertTrue(MAP.is_file())
        self.assertEqual(MAP.parent, KIT)

    def test_the_map_would_be_in_the_manifest_source(self):
        # kit-manifest hashes every regular file under the kit except MANIFEST.sha256,
        # __pycache__ and *.pyc. installed-files.txt is a plain top-level file, so it is in.
        import importlib.util
        spec = importlib.util.spec_from_file_location("kit_manifest", KIT / "scripts" / "kit-manifest.py")
        kit_manifest = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(kit_manifest)
        files = kit_manifest.kit_files(KIT)
        self.assertIn("installed-files.txt", files)

    def test_the_zip_unpacks_only_the_kit_folder(self):
        self.assertIn("The release zip unpacks only the kit folder", self.flat)

    def test_installed_files_are_not_placed_by_the_unzip(self):
        self.assertIn("not placed by the unzip", self.flat)

    def test_the_human_places_them_using_the_map(self):
        self.assertIn("the human places them, using `installed-files.txt`", self.flat)
        self.assertIn("ships inside the kit folder", self.flat)
        self.assertIn("`MANIFEST.sha256`", self.flat)

    def test_no_agent_places_an_installed_file(self):
        self.assertIn("No agent places an installed file", self.flat)

    def test_it_points_the_human_machine_entries_at_piece_e(self):
        self.assertIn("`human-machine`", self.flat)
        self.assertIn("Comparing the installed push check", self.flat)
        self.assertIn("`environments.md`", self.flat)


if __name__ == "__main__":
    unittest.main()
