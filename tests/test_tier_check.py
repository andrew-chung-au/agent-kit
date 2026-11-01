"""check-tier.sh, the escalation check for the tiers (issue #16).

TIER=light passes only when every changed path is in LIGHT_ALLOWED, none is on the
fixed escalation list, and the changed lines stay within LIGHT_MAX_LINES. Standard
and heavy have no path limit. Any other TIER value exits 2 before git runs.
"""
from __future__ import annotations

import unittest

from kit_repo import KitTestCase, DEFAULT_CONF, UNUSUAL_NAMES

ALLOW = DEFAULT_CONF + "LIGHT_ALLOWED=( 'agent-kit/README.md' 'agent-kit/environments.md' 'docs/*.md' )\n"
# An allowance that matches everything: the fixed list must still win.
ALLOW_ALL = DEFAULT_CONF + "LIGHT_ALLOWED=( '*' )\n"
SCRIPT = "agent-kit/scripts/check-tier.sh"


class TierCheckBase(KitTestCase):
    conf = ALLOW

    def setUp(self):
        super().setUp()
        self.add_project(conf=self.conf)
        self.write("agent-kit/README.md", "intro\n")
        self.write("agent-kit/environments.md", "envs\n")
        self.write("agent-kit/claude-code/hooks/guard_git.py", "x = 1\n")
        self.write("agent-kit/claude-code/settings.json", "{}\n")
        self.write("docs/a.md", "".join("line %d\n" % i for i in range(60)))
        self.write("docs/outside.txt", "t\n")
        self.write("notes/other.md", "o\n")
        self.write("tests/notes.md", "n\n")
        self.write("Makefile", "a:\n")
        self.write(".github/workflows/x.yml", "a: 1\n")
        self.write(".claude/settings.json", "{}\n")
        for label, base in UNUSUAL_NAMES.items():
            self.write("docs/" + base + ".md", "one\n")
        self.base = self.commit_all("base")
        self.slate_ref = self.base

    def tier(self, tier="light", base=None):
        return self.run_cmd(["bash", SCRIPT, tier, base or self.base])

    def append(self, rel, n):
        p = self.repo / rel
        p.write_text(p.read_text(encoding="utf-8") + "".join("more %d\n" % i for i in range(n)), encoding="utf-8")

    def refused(self, r, *names, absent=()):
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("needs at least Standard", r.stdout)
        for n in names:
            self.assertIn("  " + n + "\n", r.stdout)
        for n in absent:
            self.assertNotIn(n, r.stdout)


class TierCheckTest(TierCheckBase):
    def test_a_typo_in_an_allowed_markdown_path_passes(self):
        self.write("agent-kit/README.md", "intr0\n")
        r = self.tier()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("PASS for light", r.stdout)

    def test_a_committed_change_since_base_counts(self):
        self.write("agent-kit/README.md", "intr0\n")
        self.git("add", "--all")
        self.git("commit", "-q", "--no-verify", "-m", "typo")
        self.assertEqual(self.tier().returncode, 0)
        self.write("agent-kit/claude-code/hooks/guard_git.py", "x = 2\n")
        self.git("add", "--all")
        self.git("commit", "-q", "--no-verify", "-m", "hook")
        self.refused(self.tier(), "agent-kit/claude-code/hooks/guard_git.py")

    def test_escalating_paths_are_refused(self):
        cases = [
            "agent-kit/claude-code/hooks/guard_git.py",
            "agent-kit/scripts/verify.sh",
            "agent-kit.conf",
            "Makefile",
            ".github/workflows/x.yml",
            ".claude/settings.json",
            "agent-kit/claude-code/settings.json",
        ]
        for path in cases:
            with self.subTest(path=path):
                self.append(path, 1)
                self.refused(self.tier(), path)

    def test_a_markdown_test_file_is_refused(self):
        self.append("tests/notes.md", 1)
        self.refused(self.tier(), "tests/notes.md")

    def test_a_markdown_path_outside_the_allowance_is_refused(self):
        self.append("notes/other.md", 1)
        r = self.tier()
        self.refused(r, "notes/other.md")
        self.assertIn("not in LIGHT_ALLOWED", r.stdout)

    def test_a_mixed_diff_names_only_the_escalating_path(self):
        self.append("docs/a.md", 1)
        self.append("agent-kit/scripts/verify.sh", 1)
        r = self.tier()
        self.refused(r, "agent-kit/scripts/verify.sh", absent=("docs/a.md",))

    def test_twenty_lines_pass_and_twenty_one_are_refused(self):
        self.append("docs/a.md", 20)
        self.assertEqual(self.tier().returncode, 0)
        self.git("reset", "-q", "--hard", self.base)
        self.append("docs/a.md", 21)
        r = self.tier()
        self.refused(r)
        self.assertIn("21 changed lines", r.stdout)

    def test_deleted_lines_count(self):
        self.write("docs/a.md", "")
        r = self.tier()
        self.refused(r)
        self.assertIn("60 changed lines", r.stdout)

    def test_a_new_untracked_file_is_counted(self):
        self.write("docs/new.md", "".join("n %d\n" % i for i in range(21)))
        r = self.tier()
        self.refused(r)
        self.assertIn("21 changed lines", r.stdout)
        self.write("docs/new.md", "".join("n %d\n" % i for i in range(20)))
        self.assertEqual(self.tier().returncode, 0)

    def test_tracked_and_untracked_lines_add_up(self):
        self.append("docs/a.md", 15)
        self.write("docs/new.md", "".join("n %d\n" % i for i in range(6)))
        self.refused(self.tier())

    def test_a_new_untracked_escalating_file_is_refused(self):
        self.write("agent-kit/claude-code/hooks/new_hook.py", "x = 1\n")
        self.refused(self.tier(), "agent-kit/claude-code/hooks/new_hook.py")

    def test_unusual_file_names_are_handled_like_ascii_names(self):
        for label, base in UNUSUAL_NAMES.items():
            with self.subTest(name=label):
                self.write("docs/" + base + ".md", "two\n")
                r = self.tier()
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertIn("PASS for light (2 changed lines", r.stdout)
        self.write("docs/ünï.md", "new\n")
        self.assertEqual(self.tier().returncode, 0)

    def test_an_unusual_escalating_name_is_refused_by_its_real_name(self):
        self.write("agent-kit/scripts/café.sh", "x\n")
        self.refused(self.tier(), "agent-kit/scripts/café.sh")

    def test_standard_and_heavy_have_no_path_limit(self):
        self.append("agent-kit/scripts/verify.sh", 50)
        for tier in ("standard", "heavy"):
            with self.subTest(tier=tier):
                r = self.tier(tier)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertIn("no path limit", r.stdout)


class TierCheckBaseTest(TierCheckBase):
    """A bad BASE, or a failing git command, must never end in PASS."""

    def assertNoPass(self, r, code):
        self.assertEqual(r.returncode, code, r.stdout + r.stderr)
        self.assertNotIn("PASS", r.stdout)

    def test_a_nonexistent_base_exits_2(self):
        r = self.tier(base="nosuchrev")
        self.assertNoPass(r, 2)
        self.assertIn("not a commit", r.stderr)

    def test_a_base_that_is_not_a_commit_exits_2(self):
        r = self.tier(base="HEAD:docs/a.md")
        self.assertNoPass(r, 2)

    def test_a_base_with_a_leading_dash_is_not_an_option(self):
        for base in ("--output=injected.txt", "-p", "--stat"):
            with self.subTest(base=base):
                r = self.tier(base=base)
                self.assertNoPass(r, 2)
                self.assertIn("must not start with '-'", r.stderr)
                self.assertFalse((self.repo / "injected.txt").exists(), "BASE reached git as an option")

    def test_a_valid_base_by_name_and_by_hash_still_passes(self):
        self.append("docs/a.md", 1)
        self.assertEqual(self.tier(base="HEAD").returncode, 0)
        self.assertEqual(self.tier(base=self.base).returncode, 0)

    def _failing_git(self, fail_on):
        import shutil
        real = shutil.which("git", path=self.env["PATH"])
        stubs = self.work / "failgit"
        stubs.mkdir(exist_ok=True)
        stub = stubs / "git"
        stub.write_text(
            '#!/bin/sh\nfor a in "$@"; do [ "$a" = "%s" ] && { echo "fatal: forced failure" >&2; exit 128; }; done\n'
            'exec "%s" "$@"\n' % (fail_on, real), encoding="utf-8")
        stub.chmod(0o755)
        return {"PATH": str(stubs) + ":" + self.env["PATH"]}

    def test_a_failing_git_diff_is_a_failure_not_a_pass(self):
        r = self.run_cmd(["bash", SCRIPT, "light", self.base], env=self._failing_git("diff"))
        self.assertNoPass(r, 1)
        self.assertIn("could not list the changes", r.stderr)

    def test_a_failing_git_ls_files_is_a_failure_not_a_pass(self):
        r = self.run_cmd(["bash", SCRIPT, "light", self.base], env=self._failing_git("ls-files"))
        self.assertNoPass(r, 1)
        self.assertIn("could not list the changes", r.stderr)


class TierCheckNoAllowanceTest(TierCheckBase):
    conf = DEFAULT_CONF  # LIGHT_ALLOWED unset

    def test_unset_light_allowed_refuses_everything(self):
        self.append("docs/a.md", 1)
        r = self.tier()
        self.refused(r, "docs/a.md")
        self.assertIn("not in LIGHT_ALLOWED", r.stdout)


class TierCheckAllowanceOnFixedListTest(TierCheckBase):
    conf = ALLOW_ALL

    def test_an_allowance_entry_on_the_fixed_list_is_ignored(self):
        self.append("docs/a.md", 1)
        self.assertEqual(self.tier().returncode, 0)
        for path in ("agent-kit/scripts/verify.sh", "agent-kit/claude-code/hooks/guard_git.py",
                     "agent-kit.conf", "Makefile", ".github/workflows/x.yml", ".claude/settings.json",
                     "tests/notes.md"):
            with self.subTest(path=path):
                self.append(path, 1)
                self.refused(self.tier(), path)


class TierCheckMaxLinesTest(TierCheckBase):
    conf = ALLOW + "LIGHT_MAX_LINES=5\n"

    def test_light_max_lines_is_overridable(self):
        self.append("docs/a.md", 5)
        self.assertEqual(self.tier().returncode, 0)
        self.append("docs/a.md", 1)
        r = self.tier()
        self.refused(r)
        self.assertIn("at most 5", r.stdout)


class TierCheckUsageTest(KitTestCase):
    def test_any_other_tier_value_exits_2_before_git_runs(self):
        stubs = self.work / "gitstub"
        stubs.mkdir()
        git = stubs / "git"
        git.write_text('#!/bin/sh\necho called >> "%s"\nexit 99\n' % (self.work / "git-called"), encoding="utf-8")
        git.chmod(0o755)
        self.add_project()
        self.slate_ref = self.commit_all("base")  # subTest resets to a clean slate
        script = self.repo / SCRIPT
        env = {"PATH": str(stubs) + ":" + self.env["PATH"]}
        for value in ("", "Light", "light;ls", "$(x)", "light heavy", "LIGHT", "lights"):
            with self.subTest(value=value):
                r = self.run_cmd(["bash", script, value], env=env)
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn("Usage: make tier-check", r.stderr)
        r = self.run_cmd(["bash", script], env=env)
        self.assertEqual(r.returncode, 2)
        self.assertFalse((self.work / "git-called").exists(), "git ran before the usage check")


if __name__ == "__main__":
    unittest.main()
