"""The read-only duplicate report, agent-kit/scripts/dup-report.py and `make dup-report` (#112).

Fixtures are throwaway trees under .scratch/. Assertions are the exact report lines, the exit
code, and a before-and-after snapshot of the tree, so a write shows up. The last tests check
that the report is never a gate: verify, test and the hooks do not call it.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
SCRIPT = KIT / "scripts" / "dup-report.py"
SCRATCH = REPO / ".scratch"

SHARED = "Every role reads the project instructions first and then follows its own role file exactly."


def snapshot(root: Path) -> dict:
    out = {}
    for folder, dirs, files in os.walk(root):
        for name in dirs + files:
            path = Path(folder) / name
            info = os.lstat(path)
            out[str(path.relative_to(root))] = (path.read_bytes() if path.is_file() and not path.is_symlink()
                                                else None, info.st_mode, info.st_mtime_ns)
    return out


class Base(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix="dup-report-", dir=SCRATCH))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def put(self, name: str, text: str):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def run_report(self, *args):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *args], cwd=str(self.root),
                              capture_output=True, text=True, stdin=subprocess.DEVNULL)


class ReportTest(Base):
    def fixture(self):
        # A heading needs its own full stop, or (as in dup68.py) it joins the next sentence.
        self.put("a.md", f"# A.\n\n{SHARED} Short one.\n\nD3 is open for now.\n")
        self.put("docs/b.md", f"Intro.\n\n**{SHARED.upper()}**\n\nD3 was decided on Monday.\n")
        self.put("c.md.template", "Nothing shared here at all.\n\nQ7 is open.\n")
        self.put("d.md", "Q7 is open as well.\n")

    def test_one_repeated_sentence_and_one_key_with_differing_status(self):
        self.fixture()
        done = self.run_report(".")
        self.assertEqual(done.returncode, 0, done.stderr)
        sentence = SHARED.lower()
        self.assertEqual(done.stdout.splitlines(), [
            "dup-report: read-only report, never a gate. Files scanned: 4.",
            "Repeated sentences (12+ words, in 2+ files): 1",
            f"- a.md | docs/b.md :: {sentence[:80]}...",
            "Decision keys in 2+ files: 2",
            "- D3: a.md, docs/b.md",
            "- Q7: c.md.template, d.md",
            "- D3: status differs: open in a.md; decided in docs/b.md",
        ])
        self.assertEqual(done.stderr, "")

    def test_same_status_is_not_flagged(self):
        self.fixture()
        self.assertNotIn("Q7: status differs", self.run_report(".").stdout)

    def test_short_sentences_and_code_fences_are_not_counted(self):
        fence = f"```\n{SHARED}\n```\n"
        self.put("a.md", fence + "Too short to count here.\n")
        self.put("b.md", fence + "Too short to count here.\n")
        self.assertIn("Repeated sentences (12+ words, in 2+ files): 0", self.run_report(".").stdout)

    def test_exclusions_and_suffixes(self):
        self.fixture()
        self.put("skip/e.md", SHARED + "\n")
        self.put("notes.txt", SHARED + "\n")
        done = self.run_report("--exclude", "docs/", "--exclude", "skip/", ".")
        self.assertIn("Files scanned: 3.", done.stdout)
        self.assertIn("Repeated sentences (12+ words, in 2+ files): 0", done.stdout)
        self.assertNotIn("docs/b.md", done.stdout)

    def test_git_folder_and_symlinks_are_never_read(self):
        self.put("a.md", SHARED + "\n")
        self.put(".git/b.md", SHARED + "\n")
        outside = Path(tempfile.mkdtemp(prefix="dup-outside-", dir=SCRATCH))
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)
        (outside / "c.md").write_text(SHARED + "\n", encoding="utf-8")
        os.symlink(outside, self.root / "linked")
        os.symlink(outside / "c.md", self.root / "c.md")
        done = self.run_report(".")
        self.assertIn("Files scanned: 1.", done.stdout)
        self.assertIn("Repeated sentences (12+ words, in 2+ files): 0", done.stdout)

    def test_exit_0_with_duplicates_and_nothing_written(self):
        self.fixture()
        before = snapshot(self.root)
        done = self.run_report(".")
        self.assertEqual(done.returncode, 0)
        self.assertEqual(snapshot(self.root), before)

    def test_unreadable_file_is_listed_not_fatal(self):
        if os.geteuid() == 0:
            self.skipTest("root can read any file")
        self.fixture()
        (self.root / "d.md").chmod(0)
        self.addCleanup((self.root / "d.md").chmod, 0o644)
        done = self.run_report(".")
        self.assertEqual(done.returncode, 0)
        self.assertIn("unreadable (skipped): d.md", done.stdout)

    def test_bad_usage_exits_2(self):
        for args in ((), ("missing-folder",), ("--bogus", ".")):
            with self.subTest(args=args):
                done = self.run_report(*args)
                self.assertEqual(done.returncode, 2)
                self.assertEqual(done.stdout, "")


class StaticTest(unittest.TestCase):
    def test_script_has_no_write_subprocess_or_network(self):
        text = SCRIPT.read_text(encoding="utf-8")
        imports = [line for line in text.splitlines() if line.startswith(("import ", "from "))]
        for name in ("subprocess", "socket", "urllib", "http", "shutil", "tempfile"):
            with self.subTest(module=name):
                self.assertFalse([line for line in imports if name in line])
        code = text.split('"""', 2)[2]  # everything after the module docstring
        for word in ("subprocess.", "socket.", "os.system", "os.remove",
                     "unlink", "rmtree", "write_text", "write_bytes", '"w"', "'w'", '"a"', "'a'",
                     "eval(", "exec("):
            with self.subTest(word=word):
                self.assertNotIn(word, code)
        self.assertIn('open(name, "rb")', code)

    def test_never_a_gate(self):
        for path in (KIT / "scripts" / "verify.sh", KIT / "scripts" / "check-staged.sh"):
            self.assertNotIn("dup-report", path.read_text(encoding="utf-8"))
        for folder in ("githooks", "claude-code/hooks"):
            for path in (KIT / folder).rglob("*"):
                if path.is_file():
                    self.assertNotIn("dup-report", path.read_text(encoding="utf-8", errors="ignore"))
        for makefile in (REPO / "Makefile", KIT / "templates" / "Makefile.mk"):
            text = makefile.read_text(encoding="utf-8")
            for line in text.splitlines():
                if line.startswith(("verify:", "test:", "assert-clean:", "hooks:")):
                    with self.subTest(makefile=makefile.name, line=line):
                        self.assertNotIn("dup-report", line)
                if "dup-report" in line and line.startswith("\t"):
                    with self.subTest(makefile=makefile.name, line=line):
                        self.assertIn("dup-report.py", line)

    def test_targets_and_catalog(self):
        template = (KIT / "templates" / "Makefile.mk").read_text(encoding="utf-8")
        self.assertIn("dup-report: ## Report repeated sentences", template)
        self.assertIn("read-only; never a gate", template)
        self.assertIn("dup-report:", (REPO / "Makefile").read_text(encoding="utf-8"))
        blueprints = " ".join((KIT / "blueprints.md").read_text(encoding="utf-8").split())
        self.assertIn("Duplicate report: `dup-report` target | The human asks for it", blueprints)
        self.assertIn("never part of `make verify`", blueprints)


class MakeTargetTest(unittest.TestCase):
    def test_runs_on_this_repo_with_duplicates_and_exits_0(self):
        done = subprocess.run(["make", "--no-print-directory", "dup-report"], cwd=str(REPO),
                              capture_output=True, text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertTrue(done.stdout.startswith("dup-report: read-only report, never a gate."))
        self.assertRegex(done.stdout, r"Repeated sentences \(12\+ words, in 2\+ files\): [1-9]")

    def test_listed_in_help(self):
        done = subprocess.run(["make", "--no-print-directory", "help"], cwd=str(REPO),
                              capture_output=True, text=True, stdin=subprocess.DEVNULL)
        self.assertIn("dup-report", done.stdout)


if __name__ == "__main__":
    unittest.main()
