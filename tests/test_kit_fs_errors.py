"""A filesystem error in kit-map, kit-check or kit-compare is an error (exit 2), never drift (issue #114).

Exit 1 means drift, so a crash with a traceback (exit 1) would read as drift. Every
filesystem call in the three scripts goes through kit_map.fs(), which turns an OSError into
a MapError, and each script turns that into a one-line reason and exit 2.

The suite runs as root, where chmod 000 does not stop a read, so each test patches the one
call under test to raise PermissionError (the same error an unsearchable folder gives).
`deny` makes Path.<method> (or os.path.realpath) raise for one path, on the nth call to it.
There is one test per call site, then a guard that reads the three scripts and fails if any
of them calls a filesystem method directly instead of through fs().
"""
from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from kit_repo import new_workdir

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
SCRIPTS = KIT / "scripts"
MAP = "installed-files.txt"


def load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kit_map = load("kit_map_fs", "kit-map.py")
kit_check = load("kit_check_fs", "kit-check.py")
kit_compare = load("kit_compare_fs", "kit-compare.py")


def deny(method: str, target, nth: int = 1):
    """Patch Path.<method> so the nth call on `target` raises PermissionError; others pass through."""
    original = getattr(Path, method)
    seen = {"n": 0}

    def wrapper(self, *args, **kwargs):
        if str(self) == str(target):
            seen["n"] += 1
            if seen["n"] == nth:
                raise PermissionError(13, "Permission denied", str(self))
        return original(self, *args, **kwargs)

    return mock.patch.object(Path, method, wrapper)


def deny_realpath(target, nth: int = 1):
    original = os.path.realpath
    seen = {"n": 0}

    def wrapper(path, *args, **kwargs):
        if str(path) == str(target):
            seen["n"] += 1
            if seen["n"] == nth:
                raise PermissionError(13, "Permission denied", str(path))
        return original(path, *args, **kwargs)

    return mock.patch.object(os.path, "realpath", wrapper)


def write(path: Path, text: str = "a\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class Base(unittest.TestCase):
    def setUp(self):
        self.work = new_workdir(prefix="kit-fs-")
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)

    def run_main(self, main, argv, cwd):
        out, err = io.StringIO(), io.StringIO()
        before = os.getcwd()
        os.chdir(cwd)
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = main(argv)
        finally:
            os.chdir(before)
        return code, out.getvalue(), err.getvalue()

    def assert_error(self, result, prefix):
        code, out, err = result
        self.assertEqual(code, 2, (out, err))
        self.assertEqual(out, "", "nothing may be printed before an error")
        self.assertRegex(err, r"\A%s: [^\n]+\n\Z" % prefix)
        self.assertIn("Permission denied", err)
        self.assertNotIn("Traceback", err)


class KitMapSitesTest(Base):
    """Each filesystem call in kit-map.py: parse_map, _check_repo_install, _read_kit_source, scan_installed."""

    def setUp(self):
        super().setUp()
        self.repo = self.work / "repo"
        self.kit = self.repo / "agent-kit"
        write(self.kit / MAP, "src/a.txt | out/a.txt | repo | none\n")
        write(self.kit / "src" / "a.txt")
        write(self.repo / "out" / "a.txt")

    def run_installed(self):
        return self.run_main(lambda argv: kit_map.main(argv), ["--installed", str(self.kit), str(self.repo)], self.work)

    def assert_exit_two(self, patcher):
        with patcher:
            self.assert_error(self.run_installed(), "kit-map")

    def test_the_baseline_has_no_error(self):
        code, out, err = self.run_installed()
        self.assertEqual((code, out, err), (0, "unchanged out/a.txt\n", ""))

    def test_parse_map_kit_root_is_dir(self):
        self.assert_exit_two(deny("is_dir", self.kit))

    def test_parse_map_kit_root_is_symlink(self):
        self.assert_exit_two(deny("is_symlink", self.kit))

    def test_parse_map_repo_root_is_dir(self):
        self.assert_exit_two(deny("is_dir", self.repo))

    def test_parse_map_map_is_symlink(self):
        self.assert_exit_two(deny("is_symlink", self.kit / MAP))

    def test_parse_map_map_is_file(self):
        self.assert_exit_two(deny("is_file", self.kit / MAP))

    def test_parse_map_map_read(self):
        self.assert_exit_two(deny("read_bytes", self.kit / MAP))

    def test_check_repo_install_realpath_of_the_repo_root(self):
        self.assert_exit_two(deny_realpath(self.repo))

    def test_check_repo_install_symlink_test_of_a_parent(self):
        self.assert_exit_two(deny("is_symlink", self.repo / "out"))

    def test_check_repo_install_symlink_test_of_the_file(self):
        self.assert_exit_two(deny("is_symlink", self.repo / "out" / "a.txt"))

    def test_check_repo_install_realpath_of_the_install_path(self):
        self.assert_exit_two(deny_realpath(self.repo / "out" / "a.txt"))

    def test_read_kit_source_symlink_test_of_a_parent(self):
        self.assert_exit_two(deny("is_symlink", self.kit / "src"))

    def test_read_kit_source_symlink_test_of_the_file(self):
        self.assert_exit_two(deny("is_symlink", self.kit / "src" / "a.txt"))

    def test_read_kit_source_is_file(self):
        self.assert_exit_two(deny("is_file", self.kit / "src" / "a.txt"))

    def test_read_kit_source_read(self):
        self.assert_exit_two(deny("read_bytes", self.kit / "src" / "a.txt"))

    def test_scan_installed_symlink_test_of_a_parent(self):
        # parse_map tests the same path first; the second call is scan_installed's own.
        self.assert_exit_two(deny("is_symlink", self.repo / "out", nth=2))

    def test_scan_installed_symlink_test_of_the_file(self):
        self.assert_exit_two(deny("is_symlink", self.repo / "out" / "a.txt", nth=2))

    def test_scan_installed_is_file(self):
        self.assert_exit_two(deny("is_file", self.repo / "out" / "a.txt"))

    def test_scan_installed_read(self):
        self.assert_exit_two(deny("read_bytes", self.repo / "out" / "a.txt"))

    def test_an_unsearchable_parent_is_an_error_not_missing_and_not_drift(self):
        # The case QA reproduced with chmod 000: the file's test raises, it is not "missing".
        with deny("is_file", self.repo / "out" / "a.txt"):
            code, out, err = self.run_installed()
        self.assertEqual((code, out), (2, ""))
        self.assertNotIn("missing", err.splitlines()[0].split(":", 1)[0])

    def test_scan_installed_raises_map_error_not_oserror(self):
        with deny("is_file", self.repo / "out" / "a.txt"):
            with self.assertRaises(kit_map.MapError):
                kit_map.scan_installed(self.kit, self.repo)

    def test_the_helper_passes_results_and_other_exceptions_through(self):
        self.assertEqual(kit_map.fs(len, "abc"), 3)
        with self.assertRaises(ValueError):
            kit_map.fs(int, "x")
        with self.assertRaises(kit_map.MapError) as raised:
            kit_map.fs(mock.Mock(side_effect=PermissionError(13, "Permission denied")), "p", failed="could not do it")
        self.assertEqual(str(raised.exception), "could not do it (Permission denied)")


class KitCheckSitesTest(Base):
    """Each filesystem call in kit-check.py."""

    def setUp(self):
        super().setUp()
        self.project = self.work / "project"
        self.kit = self.project / "_docs" / "agent-kit"
        write(self.kit / "env" / "dev.json")
        write(self.kit / MAP, "env/dev.json | .devcontainer/dev.json | repo | none\n")
        write(self.project / ".devcontainer" / "dev.json")
        done = subprocess.run([sys.executable, "-B", str(SCRIPTS / "kit-manifest.py"), str(self.kit), "1.0"],
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        write(self.project / "agent-kit.conf", 'KIT_DIR="_docs/agent-kit"\nKIT_VERSION="1.0"\nTEST_CMD="true"\n')

    def run_check(self):
        return self.run_main(kit_check.main, [], self.project)

    def assert_exit_two(self, patcher):
        with patcher:
            self.assert_error(self.run_check(), "kit-check")

    def test_the_baseline_has_no_error(self):
        code, out, err = self.run_check()
        self.assertEqual((code, err), (0, ""), out)

    def test_working_folder(self):
        with mock.patch.object(Path, "cwd", side_effect=PermissionError(13, "Permission denied")):
            self.assert_error(self.run_check(), "kit-check")

    def test_read_conf_read(self):
        self.assert_exit_two(deny("read_bytes", self.project / "agent-kit.conf"))

    def test_read_manifest_is_symlink(self):
        self.assert_exit_two(deny("is_symlink", self.kit / "MANIFEST.sha256"))

    def test_read_manifest_exists(self):
        self.assert_exit_two(deny("exists", self.kit / "MANIFEST.sha256"))

    def test_read_manifest_read(self):
        self.assert_exit_two(deny("read_bytes", self.kit / "MANIFEST.sha256"))

    def test_read_manifest_resolve_of_an_entry(self):
        self.assert_exit_two(deny("resolve", self.kit / "env" / "dev.json"))

    def test_read_manifest_resolve_of_the_kit_folder(self):
        self.assert_exit_two(deny("resolve", self.kit))

    def test_map_exists(self):
        self.assert_exit_two(deny("exists", self.kit / MAP))

    def test_map_is_symlink_when_there_is_no_map(self):
        (self.kit / MAP).unlink()
        done = subprocess.run([sys.executable, "-B", str(SCRIPTS / "kit-manifest.py"), str(self.kit), "1.0"],
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assert_exit_two(deny("is_symlink", self.kit / MAP))

    def test_a_dangling_map_symlink_is_refused_not_skipped(self):
        (self.kit / MAP).unlink()
        (self.kit / MAP).symlink_to("nowhere")
        code, out, err = self.run_check()
        self.assertEqual(code, 2, (out, err))
        self.assertEqual(out, "")

    def test_the_scan_installed_errors_reach_kit_check_as_exit_two(self):
        self.assert_exit_two(deny("is_file", self.project / ".devcontainer" / "dev.json"))
        self.assert_exit_two(deny("read_bytes", self.kit / "env" / "dev.json"))


class KitCompareSitesTest(Base):
    """Each filesystem call in kit-compare.py."""

    def setUp(self):
        super().setUp()
        self.project = self.work / "project"
        self.a = self.project / "kitA"
        self.b = self.project / "kitB"
        for kit in (self.a, self.b):
            write(kit / "x.md")
            write(kit / MAP, "x.md | out/x.md | repo | none\n")

    def run_compare(self):
        return self.run_main(kit_compare.main, ["kitA", "kitB"], self.project)

    def assert_exit_two(self, patcher):
        with patcher:
            self.assert_error(self.run_compare(), "kit-compare")

    def test_the_baseline_has_no_error(self):
        code, out, err = self.run_compare()
        self.assertEqual((code, err), (0, ""), out)

    def test_working_folder(self):
        with mock.patch.object(Path, "cwd", side_effect=PermissionError(13, "Permission denied")):
            self.assert_error(self.run_compare(), "kit-compare")

    def test_kit_root_symlink_test_of_a(self):
        self.assert_exit_two(deny("is_symlink", self.a))

    def test_kit_root_symlink_test_of_b(self):
        self.assert_exit_two(deny("is_symlink", self.b))

    def test_kit_root_is_dir_of_a(self):
        self.assert_exit_two(deny("is_dir", self.a))

    def test_kit_root_is_dir_of_b(self):
        self.assert_exit_two(deny("is_dir", self.b))

    def test_same_folder_resolve_of_a(self):
        self.assert_exit_two(deny("resolve", self.a))

    def test_same_folder_resolve_of_b(self):
        self.assert_exit_two(deny("resolve", self.b))

    def test_read_maps_exists_in_a(self):
        self.assert_exit_two(deny("exists", self.a / MAP))

    def test_read_maps_exists_in_b(self):
        self.assert_exit_two(deny("exists", self.b / MAP))

    def test_read_maps_is_symlink_when_a_root_has_no_map(self):
        (self.a / MAP).unlink()
        self.assert_exit_two(deny("is_symlink", self.a / MAP))

    def test_the_shared_parser_errors_reach_kit_compare_as_exit_two(self):
        self.assert_exit_two(deny("read_bytes", self.a / MAP))
        self.assert_exit_two(deny("is_file", self.b / MAP))


class NoRawFilesystemCallTest(unittest.TestCase):
    """The guard: no script calls a filesystem method itself, so the next read site cannot slip through."""

    METHODS = {"is_file", "is_dir", "is_symlink", "exists", "read_bytes", "read_text", "write_bytes",
               "write_text", "resolve", "stat", "lstat", "iterdir", "glob", "rglob", "open", "samefile",
               "cwd", "readlink", "mkdir", "unlink", "rename", "touch", "chmod"}
    OS_FUNCTIONS = {"realpath", "islink", "isfile", "isdir", "exists", "lexists", "walk", "scandir", "listdir",
                    "stat", "lstat", "readlink", "open", "remove", "unlink", "rename", "mkdir", "makedirs",
                    "samefile"}
    FILES = ("kit-map.py", "kit-check.py", "kit-compare.py")

    def calls(self, name):
        tree = ast.parse((SCRIPTS / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Name) and func.id == "open":
                yield node.lineno, "open"
            elif isinstance(func, ast.Attribute):
                if func.attr in self.METHODS:
                    yield node.lineno, func.attr
                if (isinstance(func.value, ast.Attribute) and func.value.attr == "path"
                        and isinstance(func.value.value, ast.Name) and func.value.value.id == "os"
                        and func.attr in self.OS_FUNCTIONS):
                    yield node.lineno, "os.path." + func.attr
                if isinstance(func.value, ast.Name) and func.value.id == "os" and func.attr in self.OS_FUNCTIONS:
                    yield node.lineno, "os." + func.attr

    def test_no_script_calls_a_filesystem_method_directly(self):
        # Inside fs() the call is `call(*args)`; elsewhere a method is passed to fs() uncalled, so
        # any Call node on one of these names is a direct call.
        for name in self.FILES:
            with self.subTest(script=name):
                self.assertEqual(sorted(self.calls(name)), [], f"{name} calls the filesystem outside fs()")

    def test_the_guard_sees_a_direct_call(self):
        # Prove the check can fail: a snippet with a direct call is flagged.
        tree = ast.parse("def f(p):\n    return p.is_file()\n")
        found = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and n.func.attr in self.METHODS]
        self.assertEqual(len(found), 1)


if __name__ == "__main__":
    unittest.main()
