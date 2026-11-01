"""Behaviour tests for agent-kit/environments/local-sandbox/pre-push (the push check).

The script is only read and run, never edited. Plan mode (AGENT_PUSH_CHECK_PLAN=1)
prints what would be checked and runs nothing. The part that runs inside the
container is extracted from the file and run with bash against a git bundle, so
no test needs Docker; a stub `docker` fails any test that reaches it.
"""
from __future__ import annotations

import re
import unittest

from kit_repo import KIT, KitTestCase

PUSH_CHECK = KIT / "environments" / "local-sandbox" / "pre-push"
ZERO = "0" * 40
CONF = 'KIT_DIR="agent-kit"\nTEST_CMD="true"\n'


def extract_container_script():
    text = PUSH_CHECK.read_text(encoding="utf-8")
    m = re.search(r"^container_script='\n(.*?)^'$", text, re.S | re.M)
    if m is None:
        raise AssertionError("container_script='...' block not found in %s; "
                             "the push check was renamed or reshaped, update this test" % PUSH_CHECK)
    return m.group(1)


class PushCheckCase(KitTestCase):
    def setUp(self):
        super().setUp()
        self.origin = self.work / "origin.git"
        self.git("init", "-q", "--bare", "-b", "main", str(self.origin), cwd=self.work)
        self.git("remote", "add", "origin", str(self.origin))

    def sha(self, ref="HEAD"):
        return self.git("rev-parse", ref).stdout.strip()

    def push_check(self, *lines, **env):
        env.setdefault("AGENT_PUSH_CHECK_PLAN", "1")
        return self.run_cmd(["bash", str(PUSH_CHECK), "origin"], env=env, stdin="".join(lines))

    def new_branch_line(self, sha=None):
        return "refs/heads/main %s refs/heads/main %s\n" % (sha or self.sha(), ZERO)

    def commit_files(self, *names, message="change"):
        for name in names:
            self.write(name, "x " + message + "\n")
        self.git("add", "--all")
        self.git("commit", "-q", "-m", message)
        return self.sha()


class PlanModeTest(PushCheckCase):
    def test_a_root_project(self):
        self.write("agent-kit.conf", CONF)
        sha = self.commit_files("src.txt")
        r = self.push_check(self.new_branch_line())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("push check plan for %s (base none):" % sha[:8], r.stdout)
        self.assertIn("\n  make -C . [install] verify\n", r.stdout)

    def test_a_project_in_a_subfolder(self):
        self.write("proj/agent-kit.conf", CONF)
        self.commit_files("proj/src.txt", "outside.txt")
        r = self.push_check(self.new_branch_line())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("\n  make -C proj [install] verify\n", r.stdout)
        self.assertNotIn("make -C . ", r.stdout)

    def test_the_nearest_agent_kit_conf_wins(self):
        self.write("agent-kit.conf", CONF)
        self.write("proj/agent-kit.conf", CONF)
        first = self.commit_files(message="both confs")
        second = self.commit_files("proj/src.txt", message="touch proj only")
        r = self.push_check("refs/heads/main %s refs/heads/main %s\n" % (second, first))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("\n  make -C proj [install] verify\n", r.stdout)
        self.assertNotIn("make -C . ", r.stdout)

    def test_two_projects_in_one_push_each_get_a_plan_line(self):
        self.write("a/agent-kit.conf", CONF)
        self.write("b/agent-kit.conf", CONF)
        self.commit_files("a/x.txt", "b/y.txt")
        r = self.push_check(self.new_branch_line())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("\n  make -C a [install] verify\n  make -C b [install] verify\n", r.stdout)

    def test_the_base_is_what_the_remote_had(self):
        self.write("agent-kit.conf", CONF)
        first = self.commit_files("src.txt", message="first")
        second = self.commit_files("src.txt", message="second")
        line = "refs/heads/main %s refs/heads/main %s\n" % (second, first)
        r = self.push_check(line)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("push check plan for %s (base %s):" % (second[:8], first), r.stdout)

    def test_a_push_that_deletes_a_ref_is_skipped(self):
        self.write("agent-kit.conf", CONF)
        self.commit_files("src.txt")
        r = self.push_check("(delete) %s refs/heads/old %s\n" % (ZERO, self.sha()))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(r.stdout.strip(), "")

    def test_a_push_with_no_new_commits_is_skipped(self):
        self.write("agent-kit.conf", CONF)
        sha = self.commit_files("src.txt")
        self.git("update-ref", "refs/remotes/origin/main", sha)
        r = self.push_check(self.new_branch_line(sha))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("has no commits that origin doesn't already have", r.stdout)
        self.assertNotIn("plan for", r.stdout)

    def test_without_agent_kit_conf_a_root_verify_target_is_the_fallback(self):
        self.write("Makefile", "verify:\n\t@true\n")
        self.commit_files("src.txt")
        r = self.push_check(self.new_branch_line())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("\n  make -C . [install] verify\n", r.stdout)

    def test_with_neither_it_warns_and_passes(self):
        self.commit_files("src.txt")
        r = self.push_check(self.new_branch_line())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("WARNING no agent-kit project or root verify target changed", r.stdout)
        self.assertIn("nothing checked", r.stdout)
        self.assertNotIn("plan for", r.stdout)

    def test_unusual_file_names_still_find_their_project(self):
        self.write("proj/agent-kit.conf", CONF)
        self.commit_files('proj/café "q".txt', "proj/back\\slash.txt")
        r = self.push_check(self.new_branch_line())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("\n  make -C proj [install] verify\n", r.stdout)


class RemovedConfTest(PushCheckCase):
    def setUp(self):
        super().setUp()
        self.write("proj/agent-kit.conf", CONF)
        self.first = self.commit_files("proj/src.txt", message="first")
        self.git("rm", "-q", "proj/agent-kit.conf")
        self.git("commit", "-q", "-m", "drop the conf")
        self.line = "refs/heads/main %s refs/heads/main %s\n" % (self.sha(), self.first)

    def test_removing_a_projects_conf_blocks_the_push_and_names_the_project(self):
        r = self.push_check(self.line)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("agent-kit.conf was removed", r.stdout)
        self.assertIn("\n    proj\n", r.stdout)

    def test_allow_removed_lets_the_push_continue(self):
        r = self.push_check(self.line, AGENT_PUSH_CHECK_ALLOW_REMOVED="1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("agent-kit.conf was removed", r.stdout)

    def test_any_other_value_does_not_allow_it(self):
        for value in ("0", "yes", ""):
            with self.subTest(value=value):
                r = self.push_check(self.line, AGENT_PUSH_CHECK_ALLOW_REMOVED=value)
                self.assertEqual(r.returncode, 1)


class ContainerScriptTest(PushCheckCase):
    def run_in_container(self, projects, base=""):
        sha = self.sha()
        bundle = self.work / "push.bundle"
        self.git("branch", "-f", "pushed", sha)
        self.git("bundle", "create", "-q", str(bundle), "pushed")
        workdir = self.work / "container-work"
        return self.run_cmd(
            ["bash", "-c", extract_container_script()],
            env={"BUNDLE": str(bundle), "WORK": str(workdir), "SHA": sha, "BASE": base, "PROJECTS": projects},
        )

    def test_the_script_marker_is_found(self):
        script = extract_container_script()
        self.assertIn("git fetch", script)
        self.assertIn("make -C", script)

    def test_a_passing_verify_exits_0(self):
        self.write("Makefile", "verify:\n\t@echo verify-ran\n")
        self.commit_files("src.txt")
        r = self.run_in_container(".")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("push check: make -C . verify", r.stdout)
        self.assertIn("verify-ran", r.stdout)

    def test_install_runs_first_when_the_project_has_an_install_target(self):
        self.write("Makefile", "install:\n\t@echo install-ran\nverify:\n\t@echo verify-ran\n")
        self.commit_files("src.txt")
        r = self.run_in_container(".")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("push check: make -C . install verify", r.stdout)

    def test_a_failing_verify_exits_non_zero(self):
        self.write("Makefile", "verify:\n\t@exit 3\n")
        self.commit_files("src.txt")
        r = self.run_in_container(".")
        self.assertNotEqual(r.returncode, 0)

    def test_a_failing_second_project_fails_the_run(self):
        self.write("a/Makefile", "verify:\n\t@true\n")
        self.write("b/Makefile", "verify:\n\t@false\n")
        self.commit_files("a/x.txt")
        r = self.run_in_container("a\nb")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("make -C a verify", r.stdout)

    def test_a_reachable_base_is_passed_to_make(self):
        self.write("Makefile", "verify:\n\t@echo base-is-$(BASE)\n")
        first = self.commit_files("src.txt", message="first")
        self.commit_files("src.txt", message="second")
        r = self.run_in_container(".", base=first)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("base-is-" + first, r.stdout)

    def test_an_unreachable_base_is_dropped_not_fatal(self):
        self.write("Makefile", "verify:\n\t@echo base-is-[$(BASE)]\n")
        self.commit_files("src.txt")
        r = self.run_in_container(".", base="1" * 40)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("base-is-[]", r.stdout)


if __name__ == "__main__":
    unittest.main()
