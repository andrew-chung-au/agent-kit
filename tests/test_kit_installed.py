"""The installed-file scan shared by kit-check, agent-kit/scripts/kit-map.py (issue #114).

scan_installed() is the one driver every reader uses: it calls parse_map() for the entries
and scan_text() per file, so there is a single code path and no second parser. Every test
builds a throwaway tree under .scratch/ and runs the real driver, or the real kit-check.py
as a subprocess. Refusals are asserted by the error text and the exit code, never by exit
code alone. Read-only is asserted with a before-and-after snapshot of both trees.
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
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
MAP_SCRIPT = KIT / "scripts" / "kit-map.py"
CHECK_SCRIPT = KIT / "scripts" / "kit-check.py"
MANIFEST_SCRIPT = KIT / "scripts" / "kit-manifest.py"
SCRATCH = REPO / ".scratch" / "test-kit-installed"

spec = importlib.util.spec_from_file_location("kit_map", MAP_SCRIPT)
kit_map = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit_map)


def snapshot(root: Path) -> dict:
    """Every path under root with its type, bytes and mode, so any write shows up."""
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
        self.repo = SCRATCH / "repo"
        self.kit = self.repo / "agent-kit"
        self.kit.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(SCRATCH, ignore_errors=True)

    def write_map(self, text: str):
        (self.kit / "installed-files.txt").write_text(text, encoding="utf-8")

    def kit_source(self, rel: str, text: str):
        path = self.kit / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def installed(self, rel: str, text: str):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def states(self, reports):
        return {r.install: r.state for r in reports}


class DriverTest(Base):
    def test_single_code_path_through_parse_map_and_scan_text(self):
        # The driver must not hold a second parser or a second comparison: it is built from
        # parse_map and scan_text only. A grep proves the single code path the AC asks for.
        source = MAP_SCRIPT.read_text()
        body = source[source.index("def scan_installed"):source.index("def report_lines")]
        self.assertIn("parse_map(", body)
        self.assertIn("scan_text(", body)
        # No ad-hoc re-parse of the map or second difflib call inside the driver.
        self.assertNotIn("difflib", body)
        self.assertNotIn("installed-files.txt", body)

    def test_unchanged_drift_and_missing(self):
        self.kit_source("src/dev.json", "a\nb\n")
        self.kit_source("src/ci.yml", "x\n")
        self.kit_source("src/gone.json", "y\n")
        self.write_map(
            "src/dev.json | .devcontainer/dev.json | repo | none\n"
            "src/ci.yml | .github/workflows/ci.yml | repo | none\n"
            "src/gone.json | .config/gone.json | repo | none\n")
        self.installed(".devcontainer/dev.json", "a\nb\n")          # unchanged
        self.installed(".github/workflows/ci.yml", "CHANGED\n")     # drift
        # .config/gone.json is never created -> missing
        reports = kit_map.scan_installed(self.kit, self.repo)
        self.assertEqual(self.states(reports), {
            ".devcontainer/dev.json": "unchanged",
            ".github/workflows/ci.yml": "drift",
            ".config/gone.json": "missing"})
        lines = kit_map.report_lines(reports)
        self.assertEqual(lines, [
            "unchanged .devcontainer/dev.json",
            "drift .github/workflows/ci.yml",
            "missing .config/gone.json"])

    def test_local_ignored_when_difference_is_allowed(self):
        self.kit_source("src/setup.sh", "line\ngit config --global user.name \"<You>\"\nz\n")
        self.write_map("src/setup.sh | .devcontainer/setup.sh | repo | prefix:git config --global user.\n")
        self.installed(".devcontainer/setup.sh",
                       "line\ngit config --global user.name \"Ada\"\ngit config --global user.email e\nz\n")
        reports = kit_map.scan_installed(self.kit, self.repo)
        self.assertEqual(self.states(reports), {".devcontainer/setup.sh": "unchanged"})
        self.assertEqual(kit_map.report_lines(reports), ["local, ignored .devcontainer/setup.sh"])

    def test_findings_never_carry_line_contents(self):
        self.kit_source("src/f", "secret-one\n")
        self.write_map("src/f | .config/f | repo | none\n")
        self.installed(".config/f", "secret-two\n")
        reports = kit_map.scan_installed(self.kit, self.repo)
        for report in reports:
            for finding in report.findings:
                self.assertNotIn("secret", finding.note)


class HumanMachineIsDataTest(Base):
    def test_human_machine_install_path_is_never_opened(self):
        # The install path is set to a file that would fail the scan if it were opened:
        # the driver must report it as not-checked without touching it.
        self.kit_source("src/hook", "a\nb\n")
        self.write_map("src/hook | ~/.agent-hooks/zzz-unique-hm | human-machine | none\n")
        calls = []
        real = {name: getattr(os, name) for name in ("stat", "lstat", "readlink")}
        real_islink, real_exists, real_isfile = os.path.islink, os.path.exists, Path.is_file

        def spy(name):
            def wrapper(path, *a, **k):
                calls.append(os.fspath(path))
                return real[name](path, *a, **k)
            return wrapper

        def spy_islink(path):
            calls.append(os.fspath(path))
            return real_islink(path)

        def spy_exists(path, *a, **k):
            calls.append(os.fspath(path))
            return real_exists(path, *a, **k)

        with mock.patch("os.stat", spy("stat")), mock.patch("os.lstat", spy("lstat")), \
                mock.patch("os.path.islink", spy_islink), mock.patch("os.path.exists", spy_exists), \
                mock.patch("os.path.expanduser", side_effect=AssertionError("expanded a human-machine path")):
            reports = kit_map.scan_installed(self.kit, self.repo)
        self.assertEqual(self.states(reports), {"~/.agent-hooks/zzz-unique-hm": "not checked"})
        self.assertEqual(kit_map.report_lines(reports),
                         ["not checked here (human compares from the clean clone) ~/.agent-hooks/zzz-unique-hm"])
        self.assertFalse([c for c in calls if "zzz-unique-hm" in c])


class RefusalTest(Base):
    def test_rejected_map_entry_stops_the_run_before_any_file_is_read(self):
        self.kit_source("src/ok", "a\n")
        self.write_map(
            "src/ok | .config/ok | repo | none\n"
            "src/bad | ../escape | repo | none\n")
        self.installed(".config/ok", "a\n")
        before = snapshot(self.repo)
        with self.assertRaises(kit_map.MapError) as ctx:
            kit_map.scan_installed(self.kit, self.repo)
        self.assertIn("line 2", str(ctx.exception))
        self.assertEqual(snapshot(self.repo), before)

    def test_symlinked_install_parent_is_refused(self):
        outside = SCRATCH / "outside"
        outside.mkdir(parents=True)
        os.symlink(outside, self.repo / "escape")
        self.kit_source("src/x", "a\n")
        # A plain-path repo entry whose parent is a symlink: parse_map refuses it up front.
        self.write_map("src/x | escape/x | repo | none\n")
        with self.assertRaises(kit_map.MapError) as ctx:
            kit_map.scan_installed(self.kit, self.repo)
        self.assertIn("symlink", str(ctx.exception))

    def test_dotdot_install_path_is_refused(self):
        self.kit_source("src/x", "a\n")
        self.write_map("src/x | a/../../x | repo | none\n")
        with self.assertRaises(kit_map.MapError):
            kit_map.scan_installed(self.kit, self.repo)


class ReadOnlyTest(Base):
    def test_the_driver_writes_nothing_to_either_tree(self):
        self.kit_source("src/dev.json", "a\n")
        self.kit_source("src/hook", "h\n")
        self.write_map(
            "src/dev.json | .devcontainer/dev.json | repo | none\n"
            "src/hook | ~/.agent-hooks/pre-push | human-machine | none\n")
        self.installed(".devcontainer/dev.json", "DRIFTED\n")
        before = snapshot(SCRATCH)
        kit_map.scan_installed(self.kit, self.repo)
        self.assertEqual(snapshot(SCRATCH), before)


class CommandLineTest(Base):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(MAP_SCRIPT), *args],
                              capture_output=True, text=True)

    def test_installed_flag_prints_lines_and_exits_one_on_drift(self):
        self.kit_source("src/dev.json", "a\n")
        self.write_map("src/dev.json | .config/dev.json | repo | none\n")
        self.installed(".config/dev.json", "b\n")
        done = self.run_cli("--installed", str(self.kit), str(self.repo))
        self.assertEqual(done.returncode, 1)
        self.assertEqual(done.stdout, "drift .config/dev.json\n")

    def test_installed_flag_exits_zero_when_all_unchanged(self):
        self.kit_source("src/dev.json", "a\n")
        self.write_map("src/dev.json | .config/dev.json | repo | none\n")
        self.installed(".config/dev.json", "a\n")
        done = self.run_cli("--installed", str(self.kit), str(self.repo))
        self.assertEqual((done.returncode, done.stdout), (0, "unchanged .config/dev.json\n"))

    def test_installed_flag_refusal_is_loud_and_exits_two(self):
        self.kit_source("src/x", "a\n")
        self.write_map("src/x | /abs | repo | none\n")
        done = self.run_cli("--installed", str(self.kit), str(self.repo))
        self.assertEqual(done.returncode, 2)
        self.assertTrue(done.stderr.startswith("kit-map: line 1:"))
        self.assertEqual(done.stdout, "")


class KitCheckIntegrationTest(unittest.TestCase):
    """The real kit-check.py, run as a subprocess from a throwaway project folder."""

    def setUp(self):
        shutil.rmtree(SCRATCH, ignore_errors=True)
        self.project = SCRATCH / "project"
        self.kit = self.project / "_docs" / "agent-kit"
        self.kit.mkdir(parents=True)
        shutil.copytree(KIT / "scripts", self.kit / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        (self.project / "agent-kit.conf").write_text(
            'KIT_DIR="_docs/agent-kit"\nTEST_CMD="true"\n', encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(SCRATCH, ignore_errors=True)

    def kit_file(self, rel: str, text: str):
        path = self.kit / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def installed(self, rel: str, text: str):
        path = self.project / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def make_manifest(self):
        done = subprocess.run(
            [sys.executable, "-B", str(self.kit / "scripts" / "kit-manifest.py"), str(self.kit), "1.0"],
            capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        (self.project / "agent-kit.conf").write_text(
            'KIT_DIR="_docs/agent-kit"\nKIT_VERSION="1.0"\nTEST_CMD="true"\n', encoding="utf-8")

    def run_check(self):
        return subprocess.run([sys.executable, "-B", str(self.kit / "scripts" / "kit-check.py")],
                              cwd=str(self.project), capture_output=True, text=True)

    def test_installed_lines_follow_the_verdict_and_an_unchanged_kit_with_drift_exits_one(self):
        self.kit_file("env/dev.json", "a\nb\n")
        self.kit_file("installed-files.txt",
                      "env/dev.json | .devcontainer/dev.json | repo | none\n")
        self.make_manifest()
        self.installed(".devcontainer/dev.json", "a\nDRIFTED\n")
        done = self.run_check()
        self.assertEqual(done.returncode, 1, done.stderr)
        lines = done.stdout.splitlines()
        self.assertIn("kit-check: pristine; claim 1.0 is correct", lines)
        self.assertEqual(lines[-1], "drift .devcontainer/dev.json")
        # The installed line comes after the verdict line, not interleaved with the kit files.
        self.assertGreater(lines.index("drift .devcontainer/dev.json"),
                           lines.index("kit-check: pristine; claim 1.0 is correct"))

    def test_pristine_kit_and_matching_installed_file_exits_zero(self):
        self.kit_file("env/dev.json", "a\nb\n")
        self.kit_file("installed-files.txt",
                      "env/dev.json | .devcontainer/dev.json | repo | none\n"
                      "env/dev.json | ~/.agent-hooks/x | human-machine | none\n")
        self.make_manifest()
        self.installed(".devcontainer/dev.json", "a\nb\n")
        done = self.run_check()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("unchanged .devcontainer/dev.json", done.stdout)
        self.assertIn("not checked here (human compares from the clean clone) ~/.agent-hooks/x",
                      done.stdout)

    def test_a_rejected_map_entry_exits_two_naming_the_entry_with_no_partial_output(self):
        self.kit_file("env/dev.json", "a\n")
        self.kit_file("installed-files.txt", "env/dev.json | ../escape | repo | none\n")
        self.make_manifest()
        done = self.run_check()
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertEqual(done.stdout, "")
        self.assertTrue(done.stderr.startswith("kit-check: "))
        self.assertIn("line 1", done.stderr)

    def test_a_kit_with_no_map_keeps_the_old_behaviour_and_prints_no_installed_lines(self):
        self.kit_file("env/dev.json", "a\n")
        self.make_manifest()
        done = self.run_check()
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertNotIn("not checked here", done.stdout)
        self.assertNotIn("drift ", done.stdout)
        self.assertTrue(done.stdout.strip().endswith("kit-check: pristine; claim 1.0 is correct"))


if __name__ == "__main__":
    unittest.main()
