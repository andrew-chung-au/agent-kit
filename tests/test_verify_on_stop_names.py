"""agent-kit/claude-code/hooks/verify_on_stop.py reads changed names NUL-delimited (issue #42).

Run as the Stop hook runs it: JSON on stdin, CLAUDE_PROJECT_DIR set, cwd elsewhere.
The project's `verify` target is a stub that appends a line to a record file kept
outside the repo, so each test counts real runs.
"""
from __future__ import annotations

import json
import shutil
import sys
import unittest

from kit_repo import KitTestCase, KIT, UNUSUAL_NAMES

HOOK = KIT / "claude-code" / "hooks" / "verify_on_stop.py"
MAKEFILE = 'verify:\n\t@echo run >> "$(RECORD)"\n'


class VerifyOnStopNamesTest(KitTestCase):
    def setUp(self):
        super().setUp()
        self.record = self.work / "verify-record"
        self.write(".gitignore", ".scratch/\n")
        self.write("Makefile", MAKEFILE)
        for n in ("café", 'a"b', "plain", "a b", "a\\b"):
            self.write(n + ".md", "tracked\n")
        self.slate_ref = self.commit_all("base")

    def reset_state(self):
        self.record.unlink(missing_ok=True)
        shutil.rmtree(self.repo / ".scratch", ignore_errors=True)

    def stop(self):
        return self.run_cmd(
            [sys.executable, HOOK], cwd=self.work,
            env={"CLAUDE_PROJECT_DIR": str(self.repo), "RECORD": str(self.record)},
            stdin=json.dumps({"session_id": "s1"}))

    def runs(self):
        if not self.record.exists():
            return 0
        return len(self.record.read_text(encoding="utf-8").splitlines())

    def test_an_untracked_markdown_file_skips_verify(self):
        for label, name in UNUSUAL_NAMES.items():
            with self.subTest(label):
                self.reset_state()
                self.write("new-%s.md" % name, "x\n")
                r = self.stop()
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(self.runs(), 0)

    def test_a_modified_markdown_file_skips_verify(self):
        for label, name in UNUSUAL_NAMES.items():
            with self.subTest(label):
                self.reset_state()
                self.write("%s.md" % name, "edited\n")
                r = self.stop()
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(self.runs(), 0)

    def test_an_unusual_named_non_markdown_file_runs_verify(self):
        for label, name in UNUSUAL_NAMES.items():
            with self.subTest(label):
                self.reset_state()
                self.write("new-%s.txt" % name, "x\n")
                r = self.stop()
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(self.runs(), 1)

    def test_editing_an_untracked_unusual_named_file_after_a_pass_runs_verify_again(self):
        for label, name in UNUSUAL_NAMES.items():
            with self.subTest(label):
                self.reset_state()
                path = "new-%s.txt" % name
                self.write(path, "one\n")
                self.assertEqual(self.stop().returncode, 0)
                self.assertEqual(self.runs(), 1)
                self.write(path, "two\n")
                self.assertEqual(self.stop().returncode, 0)
                self.assertEqual(self.runs(), 2)

    def test_an_unchanged_tree_after_a_pass_does_not_run_verify_again(self):
        self.write("new-café.txt", "one\n")
        self.assertEqual(self.stop().returncode, 0)
        self.assertEqual(self.stop().returncode, 0)
        self.assertEqual(self.runs(), 1)


if __name__ == "__main__":
    unittest.main()
