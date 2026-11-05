"""Behaviour tests for agent-kit/scripts/bootstrap-project.sh (issue #150).

Each test runs in a throwaway folder under .scratch/ with a throwaway HOME and
no inherited git config (via build_env). A bare repo stands in for the GitHub
URL, so `git clone` runs locally and nothing touches the network. The script
copies out of the real kit (KIT), never a sandbox. Nothing here installs a tool
or runs Docker (the docker stub from build_env fails any test that reaches it).

Layout per test:
  <work>/origin.git            bare repo the clones come from (the "GitHub URL")
  <work>/projects/             the folder the human runs the script from (= PWD)
  <work>/projects/<name>       the clean clone the script creates
  <work>/projects/<name>-sandbox   the sandbox clone
  <work>/home/.agent-hooks/pre-push   the installed push check
"""
from __future__ import annotations

import os
import shutil
import subprocess
import unittest
from pathlib import Path

from kit_repo import KIT, build_env, new_workdir

SCRIPT = KIT / "scripts" / "bootstrap-project.sh"
PRE_PUSH = KIT / "environments" / "local-sandbox" / "pre-push"
RECIPE = KIT / "environments" / "local-sandbox"
CI_TEMPLATE = KIT / "templates" / "ci-verify.yml.template"
NAME = "proj"


class BootstrapCase(unittest.TestCase):
    def setUp(self):
        self.work = new_workdir(prefix="bootstrap-")
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.env = build_env(self.work)
        self.home = self.work / "home"
        # A bare repo plays the role of the remote the URL points at. Its name
        # sets the derived project name, so call it <NAME>.git.
        self.bare = self.work / f"{NAME}.git"
        self.run_cmd(["git", "init", "-q", "--bare", str(self.bare)], cwd=self.work)
        # The human runs the script from here; it is not a git repo.
        self.projects = self.work / "projects"
        self.projects.mkdir()
        self.url = self.bare.as_uri()
        self.clean = self.projects / NAME
        self.sandbox = self.projects / f"{NAME}-sandbox"
        self.installed_hook = self.home / ".agent-hooks" / "pre-push"

    def run_cmd(self, args, cwd, env_extra=None, stdin=None):
        e = dict(self.env)
        e.update(env_extra or {})
        kw = {"input": stdin} if stdin is not None else {"stdin": subprocess.DEVNULL}
        return subprocess.run([str(a) for a in args], cwd=str(cwd), env=e,
                              capture_output=True, text=True, timeout=120, **kw)

    def bootstrap(self, *extra, cwd=None, url=None):
        return self.run_cmd(["bash", str(SCRIPT), url or self.url, *extra], cwd=cwd or self.projects)

    def git(self, *args, cwd):
        return self.run_cmd(["git", *args], cwd=cwd)

    def ok(self, r):
        self.assertEqual(r.returncode, 0, f"\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}")
        return r


class FreshRepoTest(BootstrapCase):
    def test_a_fresh_run_creates_both_clones_and_all_installed_files(self):
        r = self.ok(self.bootstrap())
        # Two clones side by side.
        self.assertTrue((self.clean / ".git").is_dir(), "clean clone missing")
        self.assertTrue((self.sandbox / ".git").is_dir(), "sandbox clone missing")
        # The 'sandbox' remote on the clean clone points at the sandbox clone as file://.
        remote = self.git("remote", "get-url", "sandbox", cwd=self.clean).stdout.strip()
        self.assertEqual(remote, f"file://{self.sandbox}")
        # The push check is installed in both places, byte for byte from the kit.
        self.assertTrue(self._same(self.installed_hook, PRE_PUSH), "~/.agent-hooks/pre-push differs")
        self.assertTrue(self._same(self.clean / ".git" / "hooks" / "pre-push", PRE_PUSH),
                        "clean clone hook differs")
        self.assertTrue(os.access(self.installed_hook, os.X_OK), "installed hook is not executable")
        # The recipe and CI land at the right paths.
        self.assertTrue(self._same(self.clean / ".devcontainer" / "devcontainer.json",
                                   RECIPE / "devcontainer.json"))
        self.assertTrue(self._same(self.clean / ".devcontainer" / "setup.sh", RECIPE / "setup.sh"))
        self.assertTrue(self._same(self.clean / ".github" / "workflows" / "verify.yml", CI_TEMPLATE))
        # It names each file it wrote and the next step, and pushed nothing.
        self.assertIn("Next,", r.stdout)
        self.assertNotIn("git push", r.stdout.replace("push from this clean clone", ""))

    def test_the_kit_lands_at_docs_agent_kit_and_never_beside_it(self):
        self.ok(self.bootstrap())
        self.assertTrue((self.clean / "_docs" / "agent-kit" / "setup.md").is_file(),
                        "kit not at _docs/agent-kit/")
        self.assertFalse((self.clean / "agent-kit").exists(), "kit landed beside _docs, not inside it")
        # A spot check that it is the whole kit, not a stub.
        self.assertTrue((self.clean / "_docs" / "agent-kit" / "scripts" / "verify.sh").is_file())

    def _same(self, a: Path, b: Path) -> bool:
        return a.is_file() and a.read_bytes() == Path(b).read_bytes()


class ExistingRepoTest(BootstrapCase):
    def test_re_running_changes_nothing(self):
        self.ok(self.bootstrap())
        before = self._snapshot()
        r = self.ok(self.bootstrap())
        self.assertEqual(self._snapshot(), before, "a second run changed files")
        self.assertIn("Nothing changed", r.stdout)
        self.assertNotIn("wrote ", r.stdout)

    def test_an_existing_clone_is_reused_not_recloned(self):
        self.ok(self.bootstrap())
        marker = self.clean / "_docs" / "LEFT_BY_HUMAN.txt"
        marker.write_text("keep me\n", encoding="utf-8")
        self.ok(self.bootstrap())
        # The clone is reused (the marker survives) and the kit copy still refreshes beside it.
        self.assertTrue(marker.is_file(), "an existing clean clone was wiped")
        self.assertTrue((self.clean / "_docs" / "agent-kit" / "setup.md").is_file())

    def _snapshot(self):
        out = {}
        for root in (self.clean, self.sandbox, self.home / ".agent-hooks"):
            if not root.exists():
                continue
            for p in sorted(root.rglob("*")):
                if p.is_file() and ".git/" not in str(p.relative_to(root)) + "/":
                    out[str(p.relative_to(self.work))] = p.read_bytes()
        return out


class SandboxDetectionTest(BootstrapCase):
    def test_running_from_inside_a_sandbox_is_refused(self):
        """A folder with a 'sandbox' remote is a clean clone / agent tree: refuse to run there."""
        here = self.work / "someclone"
        here.mkdir()
        self.git("init", "-q", cwd=here)
        self.git("remote", "add", "sandbox", "file:///nowhere", cwd=here)
        r = self.bootstrap(cwd=here)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("sandbox", r.stderr)
        self.assertFalse(self.clean.exists(), "it created files despite refusing")

    def test_running_where_the_push_check_is_installed_is_refused(self):
        here = self.work / "someclone"
        here.mkdir()
        self.git("init", "-q", cwd=here)
        hook = here / ".git" / "hooks" / "pre-push"
        hook.write_text("#!/bin/sh\n# agent-kit-push-check v2\nexit 0\n", encoding="utf-8")
        r = self.bootstrap(cwd=here)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("sandbox", r.stderr)

    def test_a_kit_path_that_is_a_sandbox_is_refused(self):
        """It must never copy the kit out of a sandbox; --kit to one is refused."""
        kit_clone = self.work / "kit-sandbox"
        shutil.copytree(KIT, kit_clone)
        self.git("init", "-q", cwd=kit_clone)
        self.git("remote", "add", "sandbox", "file:///nowhere", cwd=kit_clone)
        r = self.bootstrap("--kit", str(kit_clone))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("sandbox", r.stderr)
        self.assertFalse(self.clean.exists())

    def test_a_kit_path_without_the_recipe_is_refused(self):
        not_a_kit = self.work / "empty"
        not_a_kit.mkdir()
        r = self.bootstrap("--kit", str(not_a_kit))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("not an agent kit", r.stderr)


class AgentHooksDirTest(BootstrapCase):
    def test_a_missing_agent_hooks_dir_is_created(self):
        self.assertFalse((self.home / ".agent-hooks").exists())
        self.ok(self.bootstrap())
        self.assertTrue(self._same(self.installed_hook, PRE_PUSH),
                        "push check not installed into a fresh ~/.agent-hooks")

    def test_an_existing_up_to_date_hook_is_left_alone(self):
        (self.home / ".agent-hooks").mkdir(parents=True)
        shutil.copyfile(PRE_PUSH, self.installed_hook)
        self.installed_hook.chmod(0o755)
        r = self.ok(self.bootstrap())
        self.assertIn("is up to date", r.stdout)

    def _same(self, a: Path, b: Path) -> bool:
        return a.is_file() and a.read_bytes() == Path(b).read_bytes()


class CiTemplatePlaceholdersTest(BootstrapCase):
    """The CI template is copied verbatim, keeping its standalone placeholders."""

    def test_the_copied_workflow_is_the_template_with_its_placeholders(self):
        self.ok(self.bootstrap())
        copied = (self.clean / ".github" / "workflows" / "verify.yml").read_text(encoding="utf-8")
        self.assertEqual(copied, CI_TEMPLATE.read_text(encoding="utf-8"))
        # The placeholders a standalone repo must resolve are still present.
        self.assertIn("<project>", copied)
        self.assertIn("<project folder>", copied)
        self.assertIn('working-directory: <project folder>', copied)
        # The script tells the human what to do with them.
        r = self.bootstrap()  # second run just for the printed guidance
        self.assertIn("standalone", r.stdout.lower())
        self.assertRegex(r.stdout, r"working-directory")


class UsageTest(BootstrapCase):
    def test_no_url_prints_usage_and_exits_non_zero(self):
        r = self.run_cmd(["bash", str(SCRIPT)], cwd=self.projects)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("usage:", r.stderr)

    def test_it_is_not_wired_as_a_make_target(self):
        """Bootstrap runs before any Makefile exists, so it is never a make target."""
        makefile = (KIT.parent / "Makefile").read_text(encoding="utf-8")
        self.assertNotIn("bootstrap-project.sh", makefile)


if __name__ == "__main__":
    unittest.main()
