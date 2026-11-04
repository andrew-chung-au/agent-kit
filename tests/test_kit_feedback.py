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
kit_map = kit_feedback.kit_map


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

    def real_prefix_entry(self):
        # The real map's own `prefix:` row (setup.sh), so the test follows the shipped rule.
        entries = [e for e in kit_map.parse_map(KIT, REPO) if e.allowed.startswith("prefix:")]
        self.assertEqual(len(entries), 1, "the shipped map has one prefix rule")
        return entries[0]

    def test_lines_named_by_a_prefix_rule_never_reach_the_bundle(self):
        entry = self.real_prefix_entry()
        self.assertEqual(entry.allowed, "prefix:git config --global user.")
        self.project_source(entry.source, "base\n")
        self.reference_source(entry.source, "base\n")
        self.write_map(f"{entry.source} | {entry.install} | repo | {entry.allowed}\n")
        self.installed(entry.install,
                       "base\ngit config --global user.name 'Ada Lovelace'\n"
                       "git config --global user.email ada@example.com\nDRIFT\n")
        done = self.run_script()
        self.assertEqual(done.returncode, 0, done.stderr)
        text = self.bundle_text()
        self.assertNotIn("ada@example.com", text)
        self.assertNotIn("Ada Lovelace", text)
        self.assertNotIn("git config --global user.", text)
        self.assertIn(f"## Changed installed file: {entry.install}", text)
        self.assertIn("DRIFT", text)  # a real drift line is still kept
        self.assertIn("2 line(s) allowed to differ by the map's prefix rule removed", text)

    def test_a_prefix_line_with_crlf_endings_is_stripped_too(self):
        entry = self.real_prefix_entry()
        self.project_source(entry.source, "base\n")
        self.reference_source(entry.source, "base\n")
        self.write_map(f"{entry.source} | {entry.install} | repo | {entry.allowed}\n")
        path = self.project / entry.install
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"base\r\ngit config --global user.email ada@example.com\r\nDRIFT\r\n")
        done = self.run_script()
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertNotIn("ada@example.com", self.bundle_text())

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


class PrivacyTest(Base):
    """Issue #116, QA launch 2: nothing private from the human's machine or the untrusted
    project tree may reach a bundle meant for a public repo."""

    def assert_nothing_left(self):
        """After a refusal: no bundle folder, no file, no temp file anywhere under .scratch/."""
        left = [p for p in (self.run_dir / ".scratch").rglob("*")]
        self.assertEqual(left, [], f"left behind: {left}")

    def one_drifted_entry(self, install=".devcontainer/setup.sh", allowed="none", body="DRIFT\n"):
        self.project_source("env/setup.sh", "base\n")
        self.reference_source("env/setup.sh", "base\n")
        self.write_map(f"env/setup.sh | {install} | repo | {allowed}\n")
        self.installed(install, body)

    # 1. No absolute path in the bundle, nothing forged by a folder name.
    def test_the_bundle_header_prints_labels_not_the_callers_paths(self):
        self.one_drifted_entry()
        done = self.run_script()
        self.assertEqual(done.returncode, 0, done.stderr)
        text = self.bundle_text()
        self.assertIn("# project: <project root>", text)
        self.assertIn("# reference kit: <reference kit root>", text)
        for private in (str(self.project), str(self.reference), str(SCRATCH), str(REPO)):
            self.assertNotIn(private, text)
        self.assertNotIn(str(REPO), done.stdout)  # the success line is relative too

    def test_a_folder_name_with_a_control_character_is_refused(self):
        # A NUL cannot be passed in argv; the others can.
        self.one_drifted_entry()
        for bad in ("proj\n## forged heading", "proj\rx", "proj\ttab", "proj\u2028x"):
            for position in (0, 1):
                with self.subTest(bad=bad, position=position):
                    roots = [str(self.project), str(self.reference)]
                    roots[position] = bad
                    done = subprocess.run(
                        [sys.executable, "-B", str(SCRIPT), *roots],
                        cwd=str(self.run_dir), stdin=subprocess.DEVNULL, capture_output=True,
                        text=True, timeout=60)
                    self.assertEqual(done.returncode, 2, done.stdout)
                    self.assertIn("holds a control character or line break", done.stderr)
                    self.assertNotIn("forged heading", done.stderr)
                    self.assert_nothing_left()

    def test_error_messages_carry_no_absolute_path(self):
        done = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), str(SCRATCH / "nope"), str(self.reference)],
            cwd=str(self.run_dir), stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60)
        self.assertEqual(done.returncode, 2)
        self.assertNotIn(str(SCRATCH), done.stderr)
        self.assertNotIn(str(REPO), done.stderr)
        self.assertIn("the project root is missing", done.stderr)

    # 2. The project's own map must not choose secrets to copy.
    REFUSED_INSTALL_PATHS = (
        ".env", ".env.local", ".env.production", "config/.env", ".envrc", ".ENV",
        ".git/config", ".git/hooks/pre-push", "sub/.git/config",
        "tls/server.pem", "tls/server.key", "keys/SERVER.KEY",
        "id_rsa", "id_rsa.pub", ".ssh/id_rsa_work",
        ".netrc", "home/.netrc", ".npmrc", "web/.npmrc",
        "credentials", "credentials.json", "aws/credentials.bak",
    )

    def test_a_crafted_map_naming_a_secret_file_is_refused_before_any_read(self):
        for install in self.REFUSED_INSTALL_PATHS:
            with self.subTest(install=install):
                shutil.rmtree(self.project, ignore_errors=True)
                shutil.rmtree(self.pkit.parent, ignore_errors=True)
                shutil.rmtree(self.reference, ignore_errors=True)
                self.pkit.mkdir(parents=True)
                self.reference.mkdir(parents=True)
                (self.project / "agent-kit.conf").write_text(
                    'KIT_DIR="_docs/agent-kit"\nTEST_CMD="true"\n', encoding="utf-8")
                self.one_drifted_entry(install=install, body="API_TOKEN=hunter2-SECRET\n")
                done = self.run_script()
                self.assertEqual(done.returncode, 2, done.stdout)
                self.assertIn("nothing written", done.stderr)
                self.assertNotIn("hunter2-SECRET", done.stdout + done.stderr)
                self.assertTrue(
                    "env file" in done.stderr or "under .git/" in done.stderr or "secret file" in done.stderr,
                    done.stderr)
                self.assert_nothing_left()

    def test_ordinary_install_paths_are_still_accepted(self):
        # The rule must not catch look-alikes: environments/, keyboard.md, monkey.txt, a
        # folder merely named env, .gitignore and .github/ (not .git/).
        for install in ("environments/x.sh", "docs/keyboard.md", "docs/monkey.txt",
                        "env/run.sh", ".gitignore", ".github/workflows/ci.yml", "credits.md"):
            with self.subTest(install=install):
                shutil.rmtree(self.pkit.parent, ignore_errors=True)
                shutil.rmtree(self.project / "_docs", ignore_errors=True)
                self.pkit.mkdir(parents=True)
                (self.run_dir / ".scratch").mkdir(exist_ok=True)
                for old in (self.run_dir / ".scratch").glob("kit-feedback-*"):
                    shutil.rmtree(old)
                self.one_drifted_entry(install=install)
                done = self.run_script()
                self.assertEqual(done.returncode, 0, done.stderr)

    def test_a_human_machine_path_under_dot_git_is_not_refused(self):
        # The shipped map names .git/hooks/pre-push as human-machine: only named, never opened.
        self.project_source("env/hook", "h\n")
        self.reference_source("env/hook", "h\n")
        self.write_map("env/hook | .git/hooks/pre-push | human-machine | none\n")
        done = self.run_script()
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn(".git/hooks/pre-push", self.bundle_text())

    # 3. A prefix rule's identity lines, in every spelling, never reach the bundle.
    def test_prefix_variants_are_all_dropped_with_the_real_rule(self):
        entry = [e for e in kit_map.parse_map(KIT, REPO) if e.allowed.startswith("prefix:")][0]
        self.assertEqual(entry.allowed, "prefix:git config --global user.")
        variants = (
            "git config --global user.name 'Ada Lovelace'",              # exact prefix
            "    git config --global user.name 'Ada Lovelace'",          # indented
            "\tgit config --global user.name 'Ada Lovelace'",            # tab-indented
            "git  config   --global  user.email ada@example.com",        # extra spaces
            "sudo git config --global user.email ada@example.com",       # leading command
            "GIT CONFIG --GLOBAL USER.EMAIL ADA@EXAMPLE.COM",            # case
            "echo x && git config --global user.name 'Ada Lovelace'",    # after another command
        )
        self.project_source(entry.source, "base\n")
        self.reference_source(entry.source, "base\n")
        self.write_map(f"{entry.source} | {entry.install} | repo | {entry.allowed}\n")
        self.installed(entry.install, "base\n" + "\n".join(variants) + "\nDRIFT\n")
        done = self.run_script()
        self.assertEqual(done.returncode, 0, done.stderr)
        text = self.bundle_text()
        for private in ("ada@example.com", "Ada Lovelace", "ADA@EXAMPLE.COM", "user.name", "user.email",
                        "USER.EMAIL"):
            self.assertNotIn(private, text)
        self.assertIn("DRIFT", text)
        self.assertIn(f"{len(variants)} line(s) allowed to differ by the map's prefix rule removed", text)

    def test_the_shared_scan_still_matches_only_the_exact_prefix(self):
        # The broader strip is bundle-only: the shared scan's drift rule is unchanged.
        kit_text = "base\n"
        indented = kit_map.scan_text("prefix:git config --global user.", kit_text,
                                     "base\n    git config --global user.name x\n")
        self.assertTrue(any(f.status == "drift" for f in indented))
        exact = kit_map.scan_text("prefix:git config --global user.", kit_text,
                                  "base\ngit config --global user.name x\n")
        self.assertFalse(any(f.status == "drift" for f in exact))

    # 4. A failure leaves nothing behind.
    def test_a_kit_file_with_an_invalid_utf8_name_leaves_nothing_behind(self):
        self.one_drifted_entry()
        bad = os.fsencode(self.pkit) + b"/bad-\xff-name.md"
        try:
            with open(bad, "wb") as handle:
                handle.write(b"x")
        except OSError:
            self.skipTest("this filesystem refuses an invalid UTF-8 file name")
        done = self.run_script()
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertIn("nothing written", done.stderr)
        self.assert_nothing_left()

    def test_every_refusal_leaves_the_scratch_folder_empty(self):
        # A rejected map entry, a secret install path, an unreadable installed file and a
        # control-character root: after each, .scratch/ holds no folder, no file, no temp.
        cases = []

        def rejected_entry():
            self.write_map("env/setup.sh | ../escape | repo | none\n")

        def secret_path():
            self.write_map("env/setup.sh | .env | repo | none\n")
            self.installed(".env", "TOKEN=1\n")

        def unreadable_file():
            self.write_map("env/setup.sh | .devcontainer/setup.sh | repo | none\n")
            self.installed(".devcontainer/setup.sh", "x\n")
            (self.project / ".devcontainer" / "setup.sh").write_bytes(b"\xff\xfe not utf8")

        cases = [("rejected entry", rejected_entry), ("secret path", secret_path),
                 ("non-UTF-8 installed file", unreadable_file)]
        for label, arrange in cases:
            with self.subTest(case=label):
                shutil.rmtree(self.project, ignore_errors=True)
                self.pkit.mkdir(parents=True)
                (self.project / "agent-kit.conf").write_text(
                    'KIT_DIR="_docs/agent-kit"\nTEST_CMD="true"\n', encoding="utf-8")
                self.project_source("env/setup.sh", "base\n")
                self.reference_source("env/setup.sh", "base\n")
                arrange()
                done = self.run_script()
                self.assertEqual(done.returncode, 2, done.stdout)
                self.assertIn("nothing written", done.stderr)
                self.assert_nothing_left()

    def test_the_success_path_leaves_exactly_one_folder_with_one_file_and_no_temp(self):
        self.one_drifted_entry()
        done = self.run_script()
        self.assertEqual(done.returncode, 0, done.stderr)
        found = sorted(p.relative_to(self.run_dir / ".scratch").parts[0] for p in (self.run_dir / ".scratch").rglob("*"))
        self.assertEqual(len(set(found)), 1)
        self.assertTrue(found[0].startswith("kit-feedback-"))
        self.assertEqual(len(found), 2)  # the folder and its bundle.md; no .tmp beside them
        self.assertFalse(list((self.run_dir / ".scratch").glob(".kit-feedback-*")))


class StripPrefixUnitTest(unittest.TestCase):
    def test_lines_containing_the_prefix_are_removed_and_counted(self):
        # Broader than the shared scan's startswith(): a line is dropped if it contains the
        # rule's text anywhere, after collapsing whitespace and lowercasing, so leading
        # indentation, extra inner spaces or a leading `sudo` all still match.
        text = "a\nuser.name=x\n  user.name=y\nuser.email=z\nb\n"
        out, removed = kit_feedback.strip_prefix(text, "user.")
        self.assertEqual(out, "a\nb\n")
        self.assertEqual(removed, 3)

    def test_no_match_returns_the_text_unchanged(self):
        self.assertEqual(kit_feedback.strip_prefix("a\nb\n", "zzz"), ("a\nb\n", 0))

    def test_case_and_whitespace_normalised(self):
        out, removed = kit_feedback.strip_prefix("a\nSUDO   GIT   CONFIG\nb\n", "git config")
        self.assertEqual(out, "a\nb\n")
        self.assertEqual(removed, 1)


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


    def test_a_symlinked_scratch_folder_is_refused_and_nothing_lands_outside(self):
        elsewhere = SCRATCH / "elsewhere"
        elsewhere.mkdir()
        shutil.rmtree(self.run_dir / ".scratch")
        os.symlink(elsewhere, self.run_dir / ".scratch")
        self.project_source("env/x", "a\n")
        self.reference_source("env/x", "a\n")
        self.write_map("env/x | .devcontainer/x | repo | none\n")
        self.installed(".devcontainer/x", "DRIFT\n")
        done = self.run_script()
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertIn(".scratch folder is a symlink", done.stderr)
        self.assertIn("nothing written", done.stderr)
        self.assertEqual(list(elsewhere.iterdir()), [])


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

    def test_absolute_roots_through_make_leave_no_path_in_the_bundle(self):
        self.project_source("env/setup.sh", "a\n")
        self.reference_source("env/setup.sh", "a\n")
        self.write_map("env/setup.sh | .devcontainer/setup.sh | repo | none\n")
        self.installed(".devcontainer/setup.sh", "DRIFT\n")
        self.write_makefile()
        done = self.run_make(f"PROJECT={self.project}", f"KIT={self.reference}")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        text = self.bundle_text()
        for private in (str(self.project), str(self.reference), str(SCRATCH)):
            self.assertNotIn(private, text)
            self.assertNotIn(private, done.stdout)


if __name__ == "__main__":
    unittest.main()
