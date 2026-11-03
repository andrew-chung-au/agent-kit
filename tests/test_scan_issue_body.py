"""Tests for agent-kit/scripts/scan-issue-body.sh (issue #44).

Each test runs the script in a throwaway project folder under .scratch/ that has
its own copy of the kit's scripts/, an agent-kit.conf and (by default) the real
secret-patterns.txt. A few tests run it in the repo itself. No network.

Exit codes: 0 clean, 1 a pattern matched, 2 anything that stopped the scan.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import unittest
from pathlib import Path

from kit_repo import build_env, new_workdir
from secret_fixtures import MATCH, NON_MATCH

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
SCRIPT_TEXT = (KIT / "scripts" / "scan-issue-body.sh").read_text(encoding="utf-8")
CONF = 'KIT_DIR="agent-kit"\n'


class ScanBase(unittest.TestCase):
    def setUp(self):
        self.work = new_workdir(prefix="scan-")
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.env = build_env(self.work)
        self.project = self.work / "project"
        self.project.mkdir()
        shutil.copytree(KIT / "scripts", self.project / "agent-kit" / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        (self.project / "agent-kit.conf").write_text(CONF, encoding="utf-8")
        (self.project / ".scratch").mkdir()
        self.patterns = self.project / "agent-kit" / "scripts" / "secret-patterns.txt"

    def put(self, data, name="body.md"):
        path = self.project / ".scratch" / name
        path.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
        return f".scratch/{name}"

    def scan(self, *args, stdin=None, cwd=None):
        return subprocess.run(["bash", "agent-kit/scripts/scan-issue-body.sh", *args],
                              cwd=str(cwd or self.project), env=self.env, input=stdin,
                              capture_output=True)

    def scan_text(self, text, name="body.md"):
        return self.scan(self.put(text, name))

    @staticmethod
    def shown(done):
        return (done.stdout + done.stderr).decode("utf-8", "replace")


class FixtureTest(ScanBase):
    def test_every_secret_fixture_is_refused_with_its_pattern_number(self):
        for name, text, number, _ in MATCH:
            with self.subTest(name=name):
                done = self.scan_text(text + "\n")
                self.assertEqual(done.returncode, 1, self.shown(done))
                self.assertEqual(done.stdout.decode(), f".scratch/body.md:1: matches pattern {number}\n")

    def test_every_non_secret_fixture_passes_silently(self):
        for name, text in NON_MATCH:
            with self.subTest(name=name):
                done = self.scan_text(text + "\n")
                self.assertEqual((done.returncode, done.stdout, done.stderr), (0, b"", b""))

    def positions(self, text):
        """The same text in each place a secret can hide: (label, file bytes, expected line)."""
        return [
            ("title line", f"Title: {text}\n\nbody\n".encode(), 1),
            ("last line, no trailing newline", f"first\nsecond\n{text}".encode(), 3),
            ("CRLF file", f"first\r\n{text}\r\nlast\r\n".encode(), 2),
            ("100000-character line", ("x" * 100000 + " " + text + "\n").encode(), 1),
            ("start of a 100000-character line", (text + " " + "x" * 100000 + "\n").encode(), 1),
        ]

    def test_every_secret_is_refused_wherever_it_sits(self):
        for name, text, number, _ in MATCH:
            for place, data, line in self.positions(text):
                with self.subTest(name=name, place=place):
                    done = self.scan(self.put(data))
                    self.assertEqual(done.returncode, 1, self.shown(done))
                    self.assertEqual(done.stdout.decode(),
                                     f".scratch/body.md:{line}: matches pattern {number}\n")

    def test_non_secrets_pass_wherever_they_sit(self):
        for name, text in NON_MATCH:
            for place, data, _ in self.positions(text):
                with self.subTest(name=name, place=place):
                    done = self.scan(self.put(data))
                    self.assertEqual((done.returncode, done.stdout), (0, b""), self.shown(done))

    def test_output_never_holds_the_matching_text(self):
        for name, text, _, secret in MATCH:
            for place, data, _ in self.positions(text):
                with self.subTest(name=name, place=place):
                    shown = self.shown(self.scan(self.put(data)))
                    self.assertNotIn(secret, shown)
                    self.assertNotIn(text, shown)

    def test_an_env_file_refusal_carries_the_hint_and_never_the_name(self):
        # #63 B: the hint says to describe env files in words, and holds nothing pattern 8 refuses.
        hint = b"describe it in words instead"
        for name, text, number, secret in MATCH:
            with self.subTest(name=name):
                done = self.scan_text(f"QA: {text}\n")
                self.assertEqual(done.returncode, 1)
                if number == 8:
                    self.assertIn(hint, done.stderr)
                    self.assertNotIn(secret.encode(), done.stdout + done.stderr)
                    self.assertEqual(done.stderr.count(b"\n"), 1, "one hint line")
                else:
                    self.assertNotIn(hint, done.stderr)

    def test_the_hint_itself_passes_the_scan(self):
        self.patterns.write_text(self.patterns.read_text(encoding="utf-8"), encoding="utf-8")
        done = self.scan_text("QA: " + MATCH[7][1] + "\n")
        hint_line = done.stderr.decode().strip()
        self.assertTrue(hint_line)
        again = self.scan_text(hint_line + "\n", name="hint.md")
        self.assertEqual((again.returncode, again.stdout), (0, b""), again.stderr)

    def test_one_line_per_hit_in_line_order(self):
        ghp, akia = MATCH[1][1], MATCH[3][1]
        data = f"ok\n{ghp}\nok\n{akia} {ghp}\n"
        done = self.scan(self.put(data))
        self.assertEqual(done.returncode, 1)
        self.assertEqual(done.stdout.decode().splitlines(), [
            ".scratch/body.md:2: matches pattern 2",
            ".scratch/body.md:4: matches pattern 2",
            ".scratch/body.md:4: matches pattern 4",
        ])

    def test_a_clean_long_line_and_empty_text_pass(self):
        for data in ("a" * 100000 + "\n", "plain\n", "\n", "no newline at all"):
            with self.subTest(length=len(data)):
                done = self.scan(self.put(data))
                self.assertEqual((done.returncode, done.stdout, done.stderr), (0, b"", b""))

    def test_standard_input_is_scanned_like_a_file(self):
        secret = MATCH[5][1]
        done = self.scan("-", stdin=f"x\n{secret}\n".encode())
        self.assertEqual((done.returncode, done.stdout.decode()), (1, "-:2: matches pattern 6\n"))
        self.assertEqual(self.scan("-", stdin=b"git status\n").returncode, 0)
        self.assertEqual(self.scan("-", stdin=b"").returncode, 0)

    def test_the_real_repo_patterns_are_found_from_agent_kit_conf(self):
        folder = new_workdir(REPO / ".scratch", prefix="scan-real-")
        self.addCleanup(shutil.rmtree, folder, ignore_errors=True)
        (folder / "x.md").write_text(MATCH[1][1] + "\n", encoding="utf-8")
        (folder / "y.md").write_text("git status\n", encoding="utf-8")
        env = build_env(self.work)
        rel = folder.relative_to(REPO)
        hit = subprocess.run(["bash", "agent-kit/scripts/scan-issue-body.sh", f"{rel}/x.md"],
                             cwd=str(REPO), env=env, capture_output=True, text=True)
        miss = subprocess.run(["bash", "agent-kit/scripts/scan-issue-body.sh", f"{rel}/y.md"],
                              cwd=str(REPO), env=env, capture_output=True, text=True)
        self.assertEqual((hit.returncode, hit.stdout), (1, f"{rel}/x.md:1: matches pattern 2\n"))
        self.assertEqual((miss.returncode, miss.stdout), (0, ""))


class FailClosedTest(ScanBase):
    """Anything that stops the scan from finishing is exit 2, never 0."""

    def assert_exit_2(self, done, reason=None):
        self.assertEqual(done.returncode, 2, self.shown(done))
        self.assertEqual(done.stdout, b"")
        self.assertTrue(done.stderr.strip())
        if reason:
            self.assertIn(reason, done.stderr.decode())

    def test_usage_errors(self):
        self.assert_exit_2(self.scan())
        self.assert_exit_2(self.scan("a", "b"))
        self.assert_exit_2(self.scan(""))
        self.assert_exit_2(self.scan("--help"))

    def test_missing_directory_and_unreadable_file(self):
        self.assert_exit_2(self.scan(".scratch/nope.md"))
        (self.project / ".scratch" / "dir").mkdir()
        self.assert_exit_2(self.scan(".scratch/dir"))
        # A symlink that points at itself cannot be opened, even by root (a chmod 0 file can).
        (self.project / ".scratch" / "loop.md").symlink_to("loop.md")
        self.assert_exit_2(self.scan(".scratch/loop.md"))

    def test_nul_byte_is_refused_not_skipped_as_binary(self):
        secret = MATCH[1][1]
        cases = {
            "clean text with a NUL": b"clean\x00text\n",
            "secret then a NUL": f"{secret}\n".encode() + b"\x00\n",
            "a NUL then a secret": b"\x00\n" + f"{secret}\n".encode(),
            "only a NUL": b"\x00",
        }
        for name, data in cases.items():
            with self.subTest(name=name):
                self.assert_exit_2(self.scan(self.put(data)), "NUL")

    def test_invalid_utf8_is_refused(self):
        secret = MATCH[1][1].encode()
        cases = {
            "lone 0xff": b"\xff\xfe\n",
            "truncated sequence": b"caf\xc3",
            "overlong slash": b"\xc0\xaf\n",
            "surrogate": b"\xed\xa0\x80\n",
            "secret beside a bad byte": secret + b"\n\xff\n",
        }
        for name, data in cases.items():
            with self.subTest(name=name):
                self.assert_exit_2(self.scan(self.put(data)), "UTF-8")

    def test_valid_non_ascii_text_is_scanned(self):
        done = self.scan(self.put("café 日本 — ok\n"))
        self.assertEqual(done.returncode, 0, self.shown(done))
        done = self.scan(self.put("café " + MATCH[3][1] + "\n"))
        self.assertEqual(done.returncode, 1)

    def test_size_limit(self):
        self.assertEqual(self.scan(self.put(b"a\n" * 524288)).returncode, 0)
        self.assert_exit_2(self.scan(self.put(b"a\n" * 524288 + b"b")), "larger")

    def test_missing_conf(self):
        (self.project / "agent-kit.conf").unlink()
        self.assert_exit_2(self.scan(self.put("x\n")))

    def test_patterns_file_missing(self):
        self.patterns.unlink()
        self.assert_exit_2(self.scan(self.put("x\n")), "missing")

    def test_patterns_file_empty(self):
        self.patterns.write_text("", encoding="utf-8")
        self.assert_exit_2(self.scan(self.put("x\n")), "empty")

    def test_patterns_file_unreadable(self):
        # A symlink that points at itself cannot be opened, even by root (a chmod 0 file can).
        self.patterns.unlink()
        self.patterns.symlink_to(self.patterns.name)
        self.assert_exit_2(self.scan(self.put("x\n")), "unreadable")

    def test_patterns_file_is_a_directory(self):
        self.patterns.unlink()
        self.patterns.mkdir()
        self.assert_exit_2(self.scan(self.put("x\n")))

    def test_a_line_grep_cannot_read(self):
        text = self.put("nothing here\n")
        for bad in ("[abc", "(unclosed", "a{2,1}", "trailing\\", "ok\n[abc"):
            with self.subTest(bad=bad):
                self.patterns.write_text("ghp_[A-Za-z0-9]{36}\n" + bad + "\n", encoding="utf-8")
                self.assert_exit_2(self.scan(text), "grep cannot read")

    def test_a_pattern_that_matches_an_empty_line(self):
        text = self.put("nothing here\n")
        for bad in ("a*", "^", "$", "x?", "(a|)"):
            with self.subTest(bad=bad):
                self.patterns.write_text("ghp_[A-Za-z0-9]{36}\n" + bad + "\n", encoding="utf-8")
                self.assert_exit_2(self.scan(text), "empty line")
        self.patterns.write_text("ghp_[A-Za-z0-9]{36}\n\n", encoding="utf-8")
        self.assert_exit_2(self.scan(text), "empty line")

    def test_a_failed_scan_never_reports_a_secret_as_clean(self):
        secret_file = self.put(MATCH[1][1] + "\n")
        self.patterns.write_text("[abc\n", encoding="utf-8")
        self.assertEqual(self.scan(secret_file).returncode, 2)
        self.patterns.unlink()
        self.assertEqual(self.scan(secret_file).returncode, 2)

    def test_kit_dir_comes_from_agent_kit_conf(self):
        elsewhere = self.project / "tools" / "kit" / "scripts"
        elsewhere.mkdir(parents=True)
        shutil.copy(self.patterns, elsewhere / "secret-patterns.txt")
        self.patterns.unlink()
        secret_file = self.put(MATCH[1][1] + "\n")
        self.assert_exit_2(self.scan(secret_file), "missing")
        (self.project / "agent-kit.conf").write_text('KIT_DIR="tools/kit"\n', encoding="utf-8")
        self.assertEqual(self.scan(secret_file).returncode, 1)

    def test_default_kit_dir_when_conf_has_no_kit_dir_line(self):
        (self.project / "agent-kit.conf").write_text('TEST_CMD="true"\n', encoding="utf-8")
        secret_file = self.put(MATCH[1][1] + "\n")
        self.assert_exit_2(self.scan(secret_file), "_docs/agent-kit")
        folder = self.project / "_docs" / "agent-kit" / "scripts"
        folder.mkdir(parents=True)
        shutil.copy(self.patterns, folder / "secret-patterns.txt")
        self.assertEqual(self.scan(secret_file).returncode, 1)

    def test_empty_kit_dir(self):
        (self.project / "agent-kit.conf").write_text('KIT_DIR=""\n', encoding="utf-8")
        self.assert_exit_2(self.scan(self.put("x\n")), "KIT_DIR")


class ScriptTextTest(unittest.TestCase):
    def test_no_second_copy_of_the_patterns(self):
        for needle in ("ghp_", "github_pat_", "AKIA", "PRIVATE KEY", "xox[", "sk-", "Bearer", r"\.env"):
            self.assertNotIn(needle, SCRIPT_TEXT, needle)

    def test_reads_the_pattern_file_through_grep_e_f(self):
        self.assertIn("secret-patterns.txt", SCRIPT_TEXT)
        self.assertRegex(SCRIPT_TEXT, r"grep [^\n]*-E -f")

    def test_never_uses_grep_I_or_binary_skipping(self):
        for line in SCRIPT_TEXT.splitlines():
            if line.lstrip().startswith("#") or "grep" not in line:
                continue
            self.assertIsNone(re.search(r"grep\b[^|]*?\s-[A-Za-z]*I", line), line)
            self.assertNotIn("--binary-files", line)
            self.assertNotIn("--exclude", line)

    def test_is_not_run_by_verify_or_the_hooks(self):
        for path in [KIT / "scripts" / "verify.sh", KIT / "scripts" / "check-staged.sh"]:
            self.assertNotIn("scan-issue-body", path.read_text(encoding="utf-8"))
        for folder in ("githooks", "claude-code/hooks"):
            for path in (KIT / folder).rglob("*"):
                if path.is_file():
                    self.assertNotIn("scan-issue-body", path.read_text(encoding="utf-8", errors="ignore"))


if __name__ == "__main__":
    unittest.main()
