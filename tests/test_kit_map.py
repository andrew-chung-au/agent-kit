"""The installed-file map and its shared parser, agent-kit/scripts/kit-map.py (issue #113).

Every test builds a throwaway tree under .scratch/ and runs the real parser. Refusals are
asserted by the error text and, for the command line, the exit code, never by exit code
alone. The real map is checked against the real kit.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
SCRIPT = KIT / "scripts" / "kit-map.py"
SCRATCH = REPO / ".scratch" / "test-kit-map"

spec = importlib.util.spec_from_file_location("kit_map", SCRIPT)
kit_map = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit_map)


class Base(unittest.TestCase):
    def setUp(self):
        shutil.rmtree(SCRATCH, ignore_errors=True)
        self.repo = SCRATCH / "repo"
        self.kit = self.repo / "agent-kit"
        self.kit.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(SCRATCH, ignore_errors=True)

    def write(self, text: str):
        (self.kit / "installed-files.txt").write_text(text, encoding="utf-8")

    def parse(self, text: str):
        self.write(text)
        return kit_map.parse_map(self.kit, self.repo)

    def refused(self, text: str, fragment: str):
        with self.assertRaises(kit_map.MapError) as ctx:
            self.parse(text)
        self.assertIn(fragment, str(ctx.exception))


class ParseTest(Base):
    def test_valid_map(self):
        entries = self.parse(
            "# comment\n\n"
            "a/b.json | .devcontainer/b.json | repo | none\n"
            "a/hook | ~/.agent-hooks/hook | human-machine | markers\n"
            "a/s.sh | .devcontainer/s.sh | repo | prefix:git config --global user.\n")
        self.assertEqual([e.kind for e in entries], ["repo", "human-machine", "repo"])
        self.assertEqual(entries[1].install, "~/.agent-hooks/hook")
        self.assertEqual(entries[2].allowed, "prefix:git config --global user.")
        self.assertEqual(entries[0].line, 3)

    def test_real_map_parses_and_sources_exist(self):
        entries = kit_map.parse_map(KIT, REPO)
        self.assertEqual(
            sorted(e.install for e in entries),
            [".devcontainer/devcontainer.json", ".devcontainer/setup.sh", ".git/hooks/pre-push",
             ".github/workflows/verify.yml", "~/.agent-hooks/pre-push"])
        for entry in entries:
            with self.subTest(source=entry.source):
                self.assertTrue((KIT / entry.source).is_file())
        kinds = {e.install: e.kind for e in entries}
        self.assertEqual(kinds["~/.agent-hooks/pre-push"], "human-machine")
        self.assertEqual(kinds[".github/workflows/verify.yml"], "repo")

    def test_roots_are_required(self):
        with self.assertRaises(kit_map.MapError):
            kit_map.parse_map(None, self.repo)
        with self.assertRaises(kit_map.MapError):
            kit_map.parse_map(self.kit, None)

    def test_empty_roots_are_refused(self):
        # QA on #113: Path("") is the current folder, which would be a silent default.
        self.write("a | x | repo | none\n")
        for kit, repo in (("", self.repo), (self.kit, ""), ("", "")):
            with self.subTest(kit=kit, repo=repo):
                with self.assertRaises(kit_map.MapError) as ctx:
                    kit_map.parse_map(kit, repo)
                self.assertIn("may be empty", str(ctx.exception))

    def test_missing_map(self):
        with self.assertRaises(kit_map.MapError):
            kit_map.parse_map(self.kit, self.repo)


class RefusalTest(Base):
    def line(self, install: str) -> str:
        return f"s.txt | {install} | repo | none\n"

    def test_absolute_install_path(self):
        self.refused(self.line("/etc/passwd"), "plain relative path")

    def test_dotdot_install_path(self):
        self.refused(self.line("a/../../x"), "'..'")

    def test_tilde_install_path(self):
        self.refused(self.line("~/x"), "plain relative path")

    def test_install_path_outside_repo_via_symlink(self):
        outside = SCRATCH / "outside"
        outside.mkdir()
        os.symlink(outside, self.repo / "escape")
        self.refused(self.line("escape/x"), "symlink")

    def test_symlinked_parent(self):
        real = self.repo / "real"
        real.mkdir()
        os.symlink(real, self.repo / "link")
        self.refused(self.line("link/x"), "symlink")

    def test_symlinked_final_component(self):
        (self.repo / "target").write_text("x")
        os.symlink(self.repo / "target", self.repo / "final")
        self.refused(self.line("final"), "symlink")

    def test_rejected_entry_fails_the_whole_read(self):
        self.refused("ok.txt | ok.txt | repo | none\n" + self.line("/abs"), "line 2")

    def test_unknown_kind(self):
        self.refused("s | x | machine | none\n", "unknown kind")

    def test_wrong_field_count(self):
        self.refused("s | x | repo\n", "expected 4 fields, found 3")
        self.refused("s | x | repo | none | extra\n", "expected 4 fields, found 5")

    def test_duplicate_install_path(self):
        self.refused("a | x | repo | none\nb | x | repo | none\n", "duplicate install path")
        self.refused("a | x | repo | none\nb | x | human-machine | none\n", "duplicate install path")

    def test_unknown_allowed_rule(self):
        self.refused("a | x | repo | whatever\n", "allowed-to-differ")
        self.refused("a | x | repo | prefix:\n", "allowed-to-differ")

    def test_bad_source_path(self):
        self.refused("../a | x | repo | none\n", "source path")
        self.refused("/a | x | repo | none\n", "source path")

    def test_control_character(self):
        self.refused("a | x\x01 | repo | none\n", "control character")

    def test_line_break_inside_a_comment_cannot_smuggle_an_entry(self):
        # QA on #113: splitlines() split on these before the control check saw them, so a
        # line that reads as a comment parsed as a real entry. Each is now refused.
        for sep in ("\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\r", "\x85", "\u2028", "\u2029"):
            with self.subTest(sep=repr(sep)):
                self.refused(f"# harmless{sep}s | x | repo | none\n", "control character")

    def test_nul_in_a_comment_is_refused(self):
        self.refused("# a\x00b\nok.txt | ok.txt | repo | none\n", "line 1: control character")

    def test_refusal_names_the_right_line(self):
        self.refused("# one\n# two\n# th\x0bree\n", "line 3:")

    def test_tab_is_still_allowed(self):
        entries = self.parse("a\t| x |\trepo | none\n")
        self.assertEqual((entries[0].source, entries[0].kind), ("a", "repo"))

    def test_map_that_is_a_symlink(self):
        (self.kit / "real.txt").write_text("a | x | repo | none\n")
        os.symlink(self.kit / "real.txt", self.kit / "installed-files.txt")
        with self.assertRaises(kit_map.MapError):
            kit_map.parse_map(self.kit, self.repo)


class HumanMachineIsDataTest(Base):
    def test_install_path_is_never_opened_or_stated(self):
        self.write("hook | /home/someone/.agent-hooks/zzz-unique | human-machine | none\n"
                   "hook | ~/zzz-unique-tilde | human-machine | none\n")
        calls = []
        real = {name: getattr(os, name) for name in ("stat", "lstat", "readlink")}
        real_exists, real_islink = os.path.exists, os.path.islink
        real_real = os.path.realpath

        def spy(name):
            def wrapper(path, *args, **kwargs):
                calls.append(os.fspath(path))
                return real[name](path, *args, **kwargs)
            return wrapper

        def spy_exists(path, *a, **k):
            calls.append(os.fspath(path))
            return real_exists(path, *a, **k)

        def spy_islink(path):
            calls.append(os.fspath(path))
            return real_islink(path)

        def spy_realpath(path, *a, **k):
            calls.append(os.fspath(path))
            return real_real(path, *a, **k)

        with mock.patch("os.stat", spy("stat")), mock.patch("os.lstat", spy("lstat")), \
                mock.patch("os.path.exists", spy_exists), mock.patch("os.path.islink", spy_islink), \
                mock.patch("os.path.realpath", spy_realpath), \
                mock.patch("os.path.expanduser", side_effect=AssertionError("expanded")):
            entries = kit_map.parse_map(self.kit, self.repo)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].install, "/home/someone/.agent-hooks/zzz-unique")
        self.assertFalse([c for c in calls if "zzz-unique" in c])


class ScanTest(unittest.TestCase):
    def test_identical_copies(self):
        self.assertEqual(kit_map.scan_text("none", "a\nb\n", "a\nb\n"), [])

    def test_difference_is_drift(self):
        found = kit_map.scan_text("none", "a\nb\n", "a\nc\n")
        self.assertTrue(found)
        self.assertTrue(all(f.status == "drift" for f in found))
        self.assertEqual({f.where for f in found}, {"kit", "installed"})
        self.assertTrue(all(f.line == 2 for f in found))

    def test_markers_ignore_local_lines(self):
        kit = "a\n# agent-kit: local-begin\nname=<You>\n# agent-kit: local-end\nz\n"
        inst = "a\n# agent-kit: local-begin\nname=Ada\nemail=x\n# agent-kit: local-end\nz\n"
        found = kit_map.scan_text("markers", kit, inst)
        self.assertEqual([f for f in found if f.status == "drift"], [])
        self.assertEqual({f.status for f in found}, {"local, ignored"})

    def test_difference_outside_markers_is_drift(self):
        kit = "a\n# agent-kit: local-begin\nx\n# agent-kit: local-end\nz\n"
        inst = "CHANGED\n# agent-kit: local-begin\ny\n# agent-kit: local-end\nz\n"
        drift = [f for f in kit_map.scan_text("markers", kit, inst) if f.status == "drift"]
        self.assertEqual({f.line for f in drift}, {1})

    def test_missing_marker_pair_is_drift(self):
        kit = "a\n# agent-kit: local-begin\nx\n# agent-kit: local-end\n"
        for kit_text, inst in ((kit, "a\nx\n"), ("a\nx\n", kit)):
            drift = [f for f in kit_map.scan_text("markers", kit_text, inst) if f.status == "drift"]
            self.assertTrue(any("missing" in f.note for f in drift))

    def test_unclosed_local_begin_is_drift(self):
        text = "a\n# agent-kit: local-begin\nx\n"
        drift = [f for f in kit_map.scan_text("markers", text, text) if f.status == "drift"]
        self.assertTrue(any("unclosed" in f.note for f in drift))

    def test_end_without_begin_and_nested_begin_are_drift(self):
        for text, word in (("a\n# agent-kit: local-end\n", "without"),
                           ("# agent-kit: local-begin\n# agent-kit: local-begin\n"
                            "# agent-kit: local-end\n", "inside")):
            drift = [f for f in kit_map.scan_text("markers", text, text) if f.status == "drift"]
            self.assertTrue(any(word in f.note for f in drift), text)

    def test_prefix_rule(self):
        kit = "a\ngit config --global user.name \"<You>\"\nz\n"
        inst = "a\ngit config --global user.name \"Ada\"\ngit config --global user.email e\nz\n"
        found = kit_map.scan_text("prefix:git config --global user.", kit, inst)
        self.assertEqual([f for f in found if f.status == "drift"], [])
        self.assertEqual(len([f for f in found if f.status == "local, ignored"]), 3)
        drift = kit_map.scan_text("prefix:git config --global user.", kit, inst.replace("z", "q"))
        self.assertTrue([f for f in drift if f.status == "drift"])

    def test_findings_never_carry_line_contents(self):
        found = kit_map.scan_text("none", "secret-one\n", "secret-two\n")
        self.assertFalse([f for f in found if "secret" in f.note])


class CommandLineTest(Base):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *args],
                              capture_output=True, text=True)

    def test_prints_entries_and_exits_zero(self):
        self.write("a | x | repo | none\n")
        done = self.run_cli(str(self.kit), str(self.repo))
        self.assertEqual((done.returncode, done.stdout), (0, "repo | a | x | none\n"))

    def test_refusal_is_loud_and_non_zero(self):
        self.write("a | /abs | repo | none\n")
        done = self.run_cli(str(self.kit), str(self.repo))
        self.assertEqual(done.returncode, 2)
        self.assertTrue(done.stderr.startswith("kit-map: line 1:"))
        self.assertEqual(done.stdout, "")

    def test_both_roots_are_required(self):
        done = self.run_cli(str(self.kit))
        self.assertEqual(done.returncode, 2)
        self.assertIn("usage", done.stderr)


class WiringTest(unittest.TestCase):
    def test_blueprints_row_names_map_and_parser(self):
        text = " ".join((KIT / "blueprints.md").read_text().split())
        self.assertIn("`installed-files.txt`", text)
        self.assertIn("`scripts/kit-map.py`", text)

    def test_parser_is_text_only(self):
        source = SCRIPT.read_text()
        for banned in ("subprocess", "exec(", "eval(", "import_module", "os.system"):
            self.assertNotIn(banned, source)


if __name__ == "__main__":
    unittest.main()
