"""The reverse-import feedback bundle, agent-kit/scripts/kit-feedback.py (issue #116).

Every test builds throwaway trees under .scratch/ and runs the real script as a subprocess
(and the real template Makefile.mk for the target). The bundle is written under .scratch/;
the project and reference trees are snapshotted before and after to prove the tool is
read-only. Refusals are asserted by the error text and the exit code, never by exit code
alone.
"""
from __future__ import annotations

import contextlib
import errno
import importlib.util
import io
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

    def test_lines_that_differ_from_the_kit_copy_are_withheld_for_a_prefix_rule(self):
        entry = self.real_prefix_entry()
        self.assertEqual(entry.allowed, "prefix:git config --global user.")
        self.project_source(entry.source, "base\n")
        self.reference_source(entry.source, "base\nsecond\n")
        self.write_map(f"{entry.source} | {entry.install} | repo | {entry.allowed}\n")
        self.installed(entry.install,
                       "base\ngit config --global user.name 'Ada Lovelace'\n"
                       "git config --global user.email ada@example.com\nsecond\nDRIFT\n")
        done = self.run_script()
        self.assertEqual(done.returncode, 0, done.stderr)
        text = self.bundle_text()
        for private in ("ada@example.com", "Ada Lovelace", "git config --global user.", "DRIFT"):
            self.assertNotIn(private, text)
        self.assertIn(f"## Changed installed file: {entry.install}", text)
        # The lines that match the kit stay; every other line is only numbered.
        body = text.split("```")[1].splitlines()[1:]
        self.assertEqual(body, ["base", "line 2 differs (text withheld)", "line 3 differs (text withheld)",
                                "second", "line 5 differs (text withheld)"])
        self.assertIn("3 line(s) differing from the reference kit's copy withheld", text)

    def test_a_prefix_file_with_crlf_endings_is_withheld_too(self):
        entry = self.real_prefix_entry()
        self.project_source(entry.source, "base\n")
        self.reference_source(entry.source, "base\n")
        self.write_map(f"{entry.source} | {entry.install} | repo | {entry.allowed}\n")
        path = self.project / entry.install
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"base\r\ngit config --global user.email ada@example.com\r\nDRIFT\r\n")
        done = self.run_script()
        self.assertEqual(done.returncode, 0, done.stderr)
        text = self.bundle_text()
        self.assertNotIn("ada@example.com", text)
        # `base\r\n` is not byte-identical to the kit's `base\n`: withheld, never guessed equal.
        self.assertIn("line 1 differs (text withheld)", text)

    def test_the_rule_comes_from_the_reference_map_not_the_project_map(self):
        # A project map that says `none` for the setup.sh row would copy the body whole. The
        # rule is read from the trusted reference map, so the body is still withheld.
        entry = self.real_prefix_entry()
        self.project_source(entry.source, "base\n")
        self.reference_source(entry.source, "base\n")
        (self.pkit / "installed-files.txt").write_text(
            f"{entry.source} | {entry.install} | repo | none\n", encoding="utf-8")
        (self.reference / "installed-files.txt").write_text(
            f"{entry.source} | {entry.install} | repo | {entry.allowed}\n", encoding="utf-8")
        self.installed(entry.install, "base\ngit config --global user.email ada@example.com\n")
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
        # Misses QA found in launch 1: a case-insensitive .git, a trailing dot, more key and
        # token names, and a name that only starts like .netrc.
        ".GIT/config", ".Git/hooks/x", "sub/.GIT/config", ".git./config",
        "tls/x.pem.", "tls/x.pem..", "tls/x.PEM.", "notes.pem.txt", "api.key.bak",
        "keys/id_ed25519", "id_ed25519.pub", "id_ecdsa", "id_dsa",
        "token.json", "tokens.yaml", "secrets.txt", "secret-key", "config/Secrets.json",
        ".netrc.bak", ".npmrc.old", ".NETRC.bak",
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

    # 4. The reference kit's map is the trusted list of files this tool may read.
    def test_a_project_map_entry_that_the_reference_map_lacks_is_refused(self):
        self.project_source("env/x", "a\n")
        self.reference_source("env/x", "a\n")
        (self.reference / "installed-files.txt").write_text(
            "env/x | .devcontainer/x | repo | none\n", encoding="utf-8")
        (self.pkit / "installed-files.txt").write_text(
            "env/x | .devcontainer/x | repo | none\nenv/x | notes/private.txt | repo | none\n", encoding="utf-8")
        self.installed(".devcontainer/x", "same\n")
        self.installed("notes/private.txt", "PRIVATE-NOTE-hunter2\n")
        done = self.run_script()
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertIn("not in the reference kit's installed-files.txt", done.stderr)
        self.assertIn("nothing written", done.stderr)
        self.assertNotIn("PRIVATE-NOTE-hunter2", done.stdout + done.stderr)
        self.assert_nothing_left()

    def test_the_same_path_with_a_different_kind_is_refused(self):
        self.project_source("env/hook", "h\n")
        self.reference_source("env/hook", "h\n")
        (self.reference / "installed-files.txt").write_text(
            "env/hook | .git/hooks/pre-push | human-machine | none\n", encoding="utf-8")
        (self.pkit / "installed-files.txt").write_text(
            "env/hook | .git/hooks/pre-push | repo | none\n", encoding="utf-8")
        done = self.run_script()
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertIn("different kind", done.stderr)
        self.assert_nothing_left()

    def test_a_missing_reference_map_is_refused(self):
        self.project_source("env/x", "a\n")
        self.reference_source("env/x", "a\n")
        (self.pkit / "installed-files.txt").write_text("env/x | .devcontainer/x | repo | none\n", encoding="utf-8")
        self.installed(".devcontainer/x", "x\n")
        done = self.run_script()
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertIn("installed-files.txt is missing", done.stderr)
        self.assert_nothing_left()

    def test_a_project_map_with_fewer_entries_than_the_reference_is_fine(self):
        self.project_source("env/x", "a\n")
        self.reference_source("env/x", "a\n")
        (self.reference / "installed-files.txt").write_text(
            "env/x | .devcontainer/x | repo | none\nenv/x | .github/y | repo | none\n", encoding="utf-8")
        (self.pkit / "installed-files.txt").write_text("env/x | .devcontainer/x | repo | none\n", encoding="utf-8")
        self.installed(".devcontainer/x", "DRIFT\n")
        done = self.run_script()
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("drift .devcontainer/x", self.bundle_text())

    # 6. A hard link under an ordinary name to a secret file.
    def test_an_installed_file_with_two_hard_links_is_refused(self):
        secret = SCRATCH / "secret-elsewhere"
        secret.write_text("API_TOKEN=hunter2-SECRET\n", encoding="utf-8")
        self.project_source("env/x", "base\n")
        self.reference_source("env/x", "base\n")
        self.write_map("env/x | notes/ordinary.txt | repo | none\n")
        (self.project / "notes").mkdir()
        os.link(secret, self.project / "notes" / "ordinary.txt")
        self.assertEqual(os.stat(secret).st_nlink, 2)
        done = self.run_script()
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertIn("more than one hard link", done.stderr)
        self.assertNotIn("hunter2-SECRET", done.stdout + done.stderr)
        self.assert_nothing_left()

    def test_a_single_link_installed_file_and_a_missing_one_are_not_refused(self):
        self.project_source("env/x", "base\n")
        self.reference_source("env/x", "base\n")
        self.write_map("env/x | notes/one.txt | repo | none\nenv/x | notes/gone.txt | repo | none\n")
        self.installed("notes/one.txt", "DRIFT\n")
        done = self.run_script()
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("missing", self.bundle_text())

    def test_ordinary_install_paths_are_still_accepted(self):
        # The rule must not catch look-alikes: environments/, keyboard.md, monkey.txt, a
        # folder merely named env, .gitignore and .github/ (not .git/).
        for install in ("environments/x.sh", "docs/keyboard.md", "docs/monkey.txt",
                        "env/run.sh", ".gitignore", ".github/workflows/ci.yml", "credits.md",
                        "tokenizer.py", "docs/secretary.md", "identity.md", "pemmican.md",
                        "docs/monkeys.txt", "keys.md", "git/config", "gitlab-ci.yml"):
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
    PREFIX_BYPASSES = (
        "git config --global user.name 'Ada Lovelace'",              # exact prefix
        "    git config --global user.name 'Ada Lovelace'",          # indented
        "\tgit config --global user.name 'Ada Lovelace'",            # tab-indented
        "git  config   --global  user.email ada@example.com",        # extra spaces
        "sudo git config --global user.email ada@example.com",       # leading command
        "GIT CONFIG --GLOBAL USER.EMAIL ADA@EXAMPLE.COM",            # case
        "echo x && git config --global user.name 'Ada Lovelace'",    # after another command
        # The three that beat the text filter (QA launch 1):
        "git config \\\n--global user.name 'Ada Lovelace'",          # backslash continuation
        "git -c x=y config --global user.name 'Ada Lovelace'",       # an option between words
        "git config --global 'user.name' 'Ada Lovelace'",            # a quoted key
    )

    def test_every_prefix_bypass_is_withheld_and_nothing_private_is_in_the_bundle_folder(self):
        entry = [e for e in kit_map.parse_map(KIT, REPO) if e.allowed.startswith("prefix:")][0]
        self.project_source(entry.source, "base\n")
        self.reference_source(entry.source, "base\n")
        self.write_map(f"{entry.source} | {entry.install} | repo | {entry.allowed}\n")
        self.installed(entry.install, "base\n" + "\n".join(self.PREFIX_BYPASSES) + "\nDRIFT\n")
        done = self.run_script()
        self.assertEqual(done.returncode, 0, done.stderr)
        # The name and the email appear nowhere in the whole bundle folder, nor in the output.
        everything = done.stdout + done.stderr
        for path in (self.run_dir / ".scratch").rglob("*"):
            if path.is_file():
                everything += path.read_text(encoding="utf-8")
        for private in ("ada@example.com", "Ada Lovelace", "ADA@EXAMPLE.COM", "user.name", "user.email",
                        "USER.EMAIL", "USER.NAME", "DRIFT", "git config", "GIT CONFIG", "--global"):
            self.assertNotIn(private, everything)
        # Only `base` survives, and every other line (one more for the continuation) is numbered.
        body = self.bundle_text().split("```")[1].splitlines()[1:]
        self.assertEqual(body[0], "base")
        self.assertTrue(all(line.startswith("line ") and line.endswith(" differs (text withheld)") for line in body[1:]))
        installed_lines = len(("base\n" + "\n".join(self.PREFIX_BYPASSES) + "\nDRIFT\n").splitlines())
        self.assertEqual(len(body), installed_lines)
        self.assertIn(f"{installed_lines - 1} line(s) differing from the reference kit's copy withheld",
                      self.bundle_text())

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


class AtomicWriteTest(Base):
    """Issue #116: the bundle is built in memory and written through a temp file and a rename,
    so a failure at the write, the mkdir or the rename leaves no folder, no file and no temp
    file under .scratch/. Each failure is injected in-process (a patch on the Path call)."""

    def setUp(self):
        super().setUp()
        self.project_source("env/setup.sh", "a\n")
        self.reference_source("env/setup.sh", "a\n")
        self.write_map("env/setup.sh | .devcontainer/setup.sh | repo | none\n")
        self.installed(".devcontainer/setup.sh", "DRIFT\n")
        before = os.getcwd()
        os.chdir(self.run_dir)
        self.addCleanup(os.chdir, before)

    def run_main(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = kit_feedback.main([str(self.project), str(self.reference)])
        return code, out.getvalue(), err.getvalue()

    def assert_nothing_left(self):
        left = list((self.run_dir / ".scratch").rglob("*"))
        self.assertEqual(left, [], f"left behind: {left}")

    def assert_refused_cleanly(self, code, out, err):
        self.assertEqual(code, 2, out)
        self.assertIn("nothing written", err)
        self.assertNotIn("wrote", out)
        self.assert_nothing_left()

    def test_the_unpatched_run_writes_one_folder_with_one_file(self):
        code, out, err = self.run_main()
        self.assertEqual(code, 0, err)
        found = sorted(p.name for p in (self.run_dir / ".scratch").rglob("*"))
        self.assertEqual(len(found), 2)
        self.assertEqual(found[0], "bundle.md")
        self.assertTrue(found[1].startswith("kit-feedback-"))

    def test_a_write_failure_after_some_bytes_leaves_nothing(self):
        real = Path.write_bytes

        def partial(self_path, data):
            real(self_path, data[:7])  # some bytes land, then the disk is full
            raise OSError(errno.ENOSPC, "injected: no space left")

        with mock.patch.object(Path, "write_bytes", partial):
            self.assert_refused_cleanly(*self.run_main())

    def test_a_mkdir_failure_after_the_temp_file_is_written_leaves_nothing(self):
        real = Path.mkdir

        def fail_bundle_folder(self_path, *args, **kwargs):
            if self_path.name.startswith("kit-feedback-"):
                raise OSError(errno.EACCES, "injected: permission denied")
            return real(self_path, *args, **kwargs)

        with mock.patch.object(Path, "mkdir", fail_bundle_folder):
            self.assert_refused_cleanly(*self.run_main())

    def test_a_rename_failure_removes_the_folder_and_the_temp_file(self):
        def fail(self_path, target):
            raise OSError(errno.EIO, "injected: i/o error")

        with mock.patch.object(Path, "rename", fail):
            self.assert_refused_cleanly(*self.run_main())

    def test_the_folder_is_not_made_before_the_temp_file_is_written(self):
        # Order: temp file first. If the write fails, no bundle folder was ever created, which
        # is what makes the cleanup above unnecessary for that failure.
        seen = []
        real_mkdir = Path.mkdir

        def record(self_path, *args, **kwargs):
            if self_path.name.startswith("kit-feedback-"):
                seen.append(sorted(p.name for p in self_path.parent.iterdir()))
            return real_mkdir(self_path, *args, **kwargs)

        with mock.patch.object(Path, "mkdir", record):
            code, _out, err = self.run_main()
        self.assertEqual(code, 0, err)
        self.assertEqual(len(seen), 1)
        self.assertTrue(any(name.endswith(".tmp") for name in seen[0]), seen)


class ScrubUnitTest(unittest.TestCase):
    def test_the_named_roots_become_labels_in_any_spelling(self):
        out = kit_feedback._scrub("x /home/ada/work/proj/_docs/agent-kit y /home/ada/kit z",
                                  ["/home/ada/work/proj", "/home/ada/kit"])
        self.assertEqual(out, "x <project root>/_docs/agent-kit y <reference kit root> z")

    def test_a_relative_root_does_not_rewrite_a_word(self):
        self.assertEqual(kit_feedback._scrub("the project root is missing", ["proj", "ref"]),
                         "the project root is missing")
        self.assertEqual(kit_feedback._scrub("in proj/_docs/agent-kit and ref", ["proj", "ref"]),
                         "in <project root>/_docs/agent-kit and <reference kit root>")

    def test_the_working_and_home_folders_are_hidden(self):
        message = f"cannot read '{Path.cwd() / 'x'}' and '{Path.home() / 'y'}'"
        out = kit_feedback._scrub(message, ["a", "b"])
        self.assertNotIn(str(Path.cwd()), out)
        self.assertNotIn(str(Path.home()) + "/", out)

    def test_any_other_absolute_path_becomes_a_placeholder(self):
        self.assertEqual(kit_feedback._scrub("cannot read '/etc/passwd': denied", ["a", "b"]),
                         "cannot read '<path>': denied")

    def test_a_relative_install_path_is_left_alone(self):
        message = "install path is under .git/: 'sub/.git/config'"
        self.assertEqual(kit_feedback._scrub(message, ["proj", "ref"]), message)


class WithholdDifferingUnitTest(unittest.TestCase):
    def test_only_byte_identical_lines_are_kept(self):
        out, withheld = kit_feedback.withhold_differing("a\nuser.name=x\n  a\nb\n", "a\nb\n")
        self.assertEqual(out, ["a", "line 2 differs (text withheld)", "line 3 differs (text withheld)", "b"])
        self.assertEqual(withheld, 2)

    def test_nothing_of_a_withheld_line_is_in_the_output(self):
        out, _ = kit_feedback.withhold_differing("secret-value\n", "other\n")
        self.assertEqual(out, ["line 1 differs (text withheld)"])

    def test_a_missing_kit_copy_withholds_every_line(self):
        out, withheld = kit_feedback.withhold_differing("a\nb\n", "")
        self.assertEqual(withheld, 2)
        self.assertNotIn("a", [line for line in out if not line.startswith("line ")])

    def test_marker_blocks_are_dropped_without_renumbering(self):
        text = "a\n# agent-kit: local-begin\nsecret\n# agent-kit: local-end\nb\nextra\n"
        out, withheld = kit_feedback.withhold_differing(text, "a\nb\n")
        self.assertEqual(out, ["a", "b", "line 6 differs (text withheld)"])
        self.assertEqual(withheld, 1)

    def test_a_line_ending_difference_counts_as_different(self):
        out, withheld = kit_feedback.withhold_differing("a\r\n", "a\n")
        self.assertEqual((out, withheld), (["line 1 differs (text withheld)"], 1))


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

    def test_the_missing_map_error_carries_no_absolute_path(self):
        # The parser's own message quotes the kit root in full; _scrub must still catch it.
        self.project_source("env/x", "a\n")
        self.reference_source("env/x", "a\n")
        (self.pkit / "installed-files.txt").unlink(missing_ok=True)
        done = self.run_script()
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertIn("installed-files.txt is missing", done.stderr)
        self.assertIn("<project root>", done.stderr)
        self.assertNotIn(str(self.project), done.stderr)
        self.assertNotIn(str(SCRATCH), done.stderr)

    def test_an_unreadable_installed_file_error_carries_no_absolute_path(self):
        self.project_source("env/setup.sh", "base\n")
        self.reference_source("env/setup.sh", "base\n")
        self.write_map("env/setup.sh | .devcontainer/setup.sh | repo | none\n")
        path = self.project / ".devcontainer" / "setup.sh"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\xff\xfe not utf8")
        done = self.run_script()
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertIn("cannot be read as UTF-8", done.stderr)
        self.assertNotIn(str(self.project), done.stderr)

    def test_a_secret_path_refusal_message_carries_no_absolute_path(self):
        self.project_source("env/x", "a\n")
        self.reference_source("env/x", "a\n")
        self.write_map("env/x | .env | repo | none\n")
        self.installed(".env", "TOKEN=1\n")
        done = self.run_script()
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertIn("looks like an env file", done.stderr)
        self.assertNotIn(str(self.project), done.stderr)

    def test_an_invalid_utf8_name_error_carries_no_absolute_path(self):
        self.project_source("env/setup.sh", "a\n")
        self.reference_source("env/setup.sh", "a\n")
        self.write_map("env/setup.sh | .devcontainer/setup.sh | repo | none\n")
        self.installed(".devcontainer/setup.sh", "DRIFT\n")
        bad = os.fsencode(self.pkit) + b"/bad-\xff-name.md"
        try:
            with open(bad, "wb") as handle:
                handle.write(b"x")
        except OSError:
            self.skipTest("this filesystem refuses an invalid UTF-8 file name")
        done = self.run_script()
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertNotIn(str(self.project), done.stdout + done.stderr)

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
