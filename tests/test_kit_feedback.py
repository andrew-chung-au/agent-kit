"""The reverse-import feedback bundle, agent-kit/scripts/kit-feedback.py (issue #116).

Every test builds throwaway trees under .scratch/ and runs the real script as a subprocess
(and the real template Makefile.mk for the target). The bundle is written under .scratch/;
the project and reference trees are snapshotted before and after to prove the tool is
read-only. Refusals are asserted by the error text and the exit code, never by exit code
alone.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import stat
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
SCRIPT = KIT / "scripts" / "kit-feedback.py"
TEMPLATE = KIT / "templates" / "Makefile.mk"
SCRATCH = REPO / ".scratch" / "test-kit-feedback"

spec = importlib.util.spec_from_file_location("kit_feedback", SCRIPT)
kit_feedback = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit_feedback)


def snapshot(root: Path) -> dict:
    out = {}
    for folder, dirs, files in os.walk(root):
        for name in dirs + files:
            path = Path(folder) / name
            info = os.lstat(path)
            key = os.fsencode(path.relative_to(root))
            if stat.S_ISREG(info.st_mode):
                out[key] = ("file", path.read_bytes(), info.st_mode)
            else:
                out[key] = ("other", os.readlink(path) if path.is_symlink() else None, info.st_mode)
    return out


class Base(unittest.TestCase):
    def setUp(self):
        shutil.rmtree(SCRATCH, ignore_errors=True)
        self.run_dir = SCRATCH / "run"
        self.project = SCRATCH / "proj"
        self.reference = SCRATCH / "ref"
        self.pkit = self.project / "_docs" / "agent-kit"
        for d in (self.run_dir / ".scratch", self.pkit, self.reference):
            d.mkdir(parents=True)
        (self.project / "agent-kit.conf").write_text(
            'KIT_DIR="_docs/agent-kit"\nTEST_CMD="true"\n', encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(SCRATCH, ignore_errors=True)

    def kit_source(self, base: Path, rel: str, text: str):
        path = base / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def project_source(self, rel, text):
        self.kit_source(self.pkit, rel, text)

    def reference_source(self, rel, text):
        self.kit_source(self.reference, rel, text)

    def write_map(self, text: str):
        (self.pkit / "installed-files.txt").write_text(text, encoding="utf-8")
        (self.reference / "installed-files.txt").write_text(text, encoding="utf-8")

    def installed(self, rel: str, text: str):
        path = self.project / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def run_script(self):
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), str(self.project), str(self.reference)],
            cwd=str(self.run_dir), stdin=subprocess.DEVNULL,
            capture_output=True, text=True, timeout=60)

    def bundle_text(self):
        folders = sorted((self.run_dir / ".scratch").glob("kit-feedback-*"))
        self.assertEqual(len(folders), 1, "exactly one bundle folder")
        return (folders[0] / "bundle.md").read_text(encoding="utf-8")


class BundleTest(Base):
    def test_lists_changed_installed_and_kit_files(self):
        self.project_source("env/setup.sh", "a\n")
        self.reference_source("env/setup.sh", "a\n")
        self.project_source("extra.md", "project only\n")  # a changed kit file (added)
        self.write_map("env/setup.sh | .devcontainer/setup.sh | repo | none\n")
        self.installed(".devcontainer/setup.sh", "DRIFTED\n")
        done = self.run_script()
        self.assertEqual(done.returncode, 0, done.stderr)
        text = self.bundle_text()
        self.assertIn("drift .devcontainer/setup.sh", text)
        self.assertIn("added extra.md", text)

    def test_a_personal_value_between_markers_is_stripped(self):
        self.project_source("env/setup.sh", "base\n")
        self.reference_source("env/setup.sh", "base\n")
        self.write_map("env/setup.sh | .devcontainer/setup.sh | repo | none\n")
        self.installed(".devcontainer/setup.sh",
                       "line\n# agent-kit: local-begin\nemail=ada@example.com\n# agent-kit: local-end\nDRIFT\n")
        done = self.run_script()
        self.assertEqual(done.returncode, 0, done.stderr)
        text = self.bundle_text()
        self.assertNotIn("ada@example.com", text)
        self.assertIn("## Changed installed file: .devcontainer/setup.sh", text)
        self.assertIn("DRIFT", text)  # the drift line itself is kept

    def test_human_machine_entries_are_named_and_never_opened(self):
        self.project_source("env/hook", "h\n")
        self.reference_source("env/hook", "h\n")
        # The install path is one that would fail if opened; it must be only named.
        self.write_map("env/hook | ~/.agent-hooks/zzz-unique-feedback | human-machine | none\n")
        done = self.run_script()
        self.assertEqual(done.returncode, 0, done.stderr)
        text = self.bundle_text()
        self.assertIn("the human supplies these from the clean clone", text.lower())
        self.assertIn("~/.agent-hooks/zzz-unique-feedback", text)

    def test_unclosed_markers_are_reported_as_drift_not_stripped_silently(self):
        self.project_source("env/setup.sh", "base\n")
        self.reference_source("env/setup.sh", "base\n")
        self.write_map("env/setup.sh | .devcontainer/setup.sh | repo | none\n")
        self.installed(".devcontainer/setup.sh",
                       "x\n# agent-kit: local-begin\nemail=ada@example.com\nNO END MARKER\n")
        done = self.run_script()
        self.assertEqual(done.returncode, 0, done.stderr)
        text = self.bundle_text()
        self.assertIn("drift .devcontainer/setup.sh", text)
        self.assertIn("markers unbalanced", text)
        # Body not written, so the value inside the unclosed block never leaks.
        self.assertNotIn("ada@example.com", text)


class StripLocalUnitTest(unittest.TestCase):
    def test_balanced_markers_strip_the_block(self):
        text = "a\n# agent-kit: local-begin\nsecret\n# agent-kit: local-end\nb\n"
        out, ok = kit_feedback.strip_local(text)
        self.assertTrue(ok)
        self.assertEqual(out, "a\nb\n")
        self.assertNotIn("secret", out)

    def test_unclosed_begin_is_not_ok_and_returns_the_body_unchanged(self):
        text = "a\n# agent-kit: local-begin\nsecret\n"
        out, ok = kit_feedback.strip_local(text)
        self.assertFalse(ok)
        self.assertEqual(out, text)

    def test_end_without_begin_is_not_ok(self):
        _out, ok = kit_feedback.strip_local("a\n# agent-kit: local-end\n")
        self.assertFalse(ok)


class RefusalTest(Base):
    def test_a_rejected_map_entry_writes_no_bundle(self):
        self.project_source("env/x", "a\n")
        self.reference_source("env/x", "a\n")
        self.write_map("env/x | ../escape | repo | none\n")
        before = snapshot(SCRATCH)
        done = self.run_script()
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertIn("line 1", done.stderr)
        self.assertIn("nothing written", done.stderr)
        self.assertFalse(sorted((self.run_dir / ".scratch").glob("kit-feedback-*")))
        self.assertEqual(snapshot(SCRATCH), before)

    def test_a_missing_project_root_is_refused(self):
        done = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), str(SCRATCH / "nope"), str(self.reference)],
            cwd=str(self.run_dir), stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60)
        self.assertEqual(done.returncode, 2)
        self.assertIn("nothing written", done.stderr)


class ReadOnlyTest(Base):
    def test_neither_tree_changes(self):
        self.project_source("env/setup.sh", "a\n")
        self.reference_source("env/setup.sh", "b\n")  # a kit-file difference
        self.write_map("env/setup.sh | .devcontainer/setup.sh | repo | none\n"
                       "env/setup.sh | ~/.agent-hooks/pre-push | human-machine | none\n")
        self.installed(".devcontainer/setup.sh", "DRIFT\n")
        before_project = snapshot(self.project)
        before_reference = snapshot(self.reference)
        done = self.run_script()
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(snapshot(self.project), before_project)
        self.assertEqual(snapshot(self.reference), before_reference)


class MakeTargetTest(Base):
    def env(self):
        return {k: v for k, v in os.environ.items() if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL")}

    def write_makefile(self):
        shutil.copytree(KIT / "scripts", self.run_dir / "_docs" / "agent-kit" / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        (self.run_dir / "Makefile").write_text(TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")

    def run_make(self, *args):
        return subprocess.run(["make", "-s", "kit-feedback", *args], cwd=str(self.run_dir),
                              env=self.env(), stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60)

    def test_the_guard_refuses_a_dotdot_or_dollar_value(self):
        self.write_makefile()
        for bad in ("PROJECT=../escape", "PROJECT=a b", 'PROJECT=$(HOME)'):
            with self.subTest(bad=bad):
                done = self.run_make(bad, "KIT=ref")
                self.assertNotEqual(done.returncode, 0)
                self.assertIn("Usage: make kit-feedback", done.stderr)

    def test_the_target_runs_the_script_with_both_roots(self):
        self.project_source("env/setup.sh", "a\n")
        self.reference_source("env/setup.sh", "a\n")
        self.write_map("env/setup.sh | .devcontainer/setup.sh | repo | none\n")
        self.installed(".devcontainer/setup.sh", "DRIFT\n")
        self.write_makefile()
        done = self.run_make(f"PROJECT={self.project}", f"KIT={self.reference}")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("kit-feedback: wrote", done.stdout)


if __name__ == "__main__":
    unittest.main()
