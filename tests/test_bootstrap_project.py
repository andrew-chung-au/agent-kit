"""Behaviour tests for agent-kit/scripts/bootstrap-project.sh (issue #150).

Each test runs in a throwaway folder under .scratch/ with a throwaway HOME and no
inherited git config (via build_env). A bare repo stands in for the GitHub URL, so
`git clone` runs locally. GIT_CEILING_DIRECTORIES stops git looking above the
throwaway folder, so the "plain folder" the script runs from is not inside this
repository's work tree. Nothing here installs a tool or runs Docker.

Layout per test:
  <work>/proj.git                     bare repo the clones come from (the "URL")
  <work>/kitrepo/agent-kit/           a committed copy of the kit: the clean kit clone
  <work>/projects/                    plain folder the script runs from
  <work>/projects/proj, proj-sandbox  the two clones it creates
  <work>/home/.agent-hooks/pre-push   the installed push check
"""
from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

from kit_repo import KIT, build_env, new_workdir

NAME = "proj"
IDENT = ["-c", "user.name=T", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false"]


class BootstrapCase(unittest.TestCase):
    def setUp(self):
        self.work = new_workdir(prefix="bootstrap-")
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.env = build_env(self.work, {"GIT_CEILING_DIRECTORIES": str(self.work)})
        self.home = self.work / "home"
        self.bare = self.work / f"{NAME}.git"
        self.run_cmd(["git", "init", "-q", "--bare", str(self.bare)], cwd=self.work)
        self.projects = self.work / "projects"
        self.projects.mkdir()
        self.url = self.bare.as_uri()
        self.clean = self.projects / NAME
        self.sandbox = self.projects / f"{NAME}-sandbox"
        self.installed_hook = self.home / ".agent-hooks" / "pre-push"
        # The kit under test: the working-tree kit, committed and pushed to a bare
        # "GitHub" remote, then cloned, exactly as a human's clean clone would be.
        seed = self.work / "kitseed"
        shutil.copytree(KIT, seed / "agent-kit", ignore=shutil.ignore_patterns("__pycache__"))
        self.git("init", "-q", "-b", "main", cwd=seed)
        self.git("add", "--all", cwd=seed)
        self.git(*IDENT, "commit", "-q", "-m", "kit", cwd=seed)
        self.kit_origin = self.work / "kit-origin.git"
        self.git("clone", "-q", "--bare", str(seed), str(self.kit_origin), cwd=self.work)
        shutil.rmtree(seed)
        self.kit_repo = self.work / "kitrepo"
        self.git("clone", "-q", str(self.kit_origin), str(self.kit_repo), cwd=self.work)
        self.kit = self.kit_repo / "agent-kit"
        self.script = self.kit / "scripts" / "bootstrap-project.sh"
        self.pre_push = self.kit / "environments" / "local-sandbox" / "pre-push"
        self.recipe = self.kit / "environments" / "local-sandbox"
        self.ci = self.kit / "templates" / "ci-verify.yml.template"

    def run_cmd(self, args, cwd):
        return subprocess.run([str(a) for a in args], cwd=str(cwd), env=self.env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=120)

    def git(self, *args, cwd):
        r = self.run_cmd(["git", *args], cwd=cwd)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r

    def bootstrap(self, *extra, cwd=None, script=None):
        return self.run_cmd(["bash", str(script or self.script), self.url, *extra], cwd=cwd or self.projects)

    def ok(self, *extra, **kw):
        r = self.bootstrap(*extra, **kw)
        self.assertEqual(r.returncode, 0, f"\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}")
        return r

    def refused(self, r):
        self.assertEqual(r.returncode, 1, f"\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}")
        self.assertFalse(self.clean.exists(), "it created files despite refusing")
        self.assertFalse((self.home / ".agent-hooks").exists(), "it wrote ~/.agent-hooks despite refusing")

    def same(self, a, b):
        return Path(a).is_file() and Path(a).read_bytes() == Path(b).read_bytes()

    def make_sandbox_clone(self):
        """A real sandbox: a plain clone with no 'sandbox' remote and no push check."""
        path = self.work / "sandbox-clone"
        self.git("clone", "-q", self.url, str(path), cwd=self.work)
        return path


class FreshRepoTest(BootstrapCase):
    def test_a_fresh_run_creates_both_clones_and_all_installed_files(self):
        r = self.ok()
        self.assertTrue((self.clean / ".git").is_dir())
        self.assertTrue((self.sandbox / ".git").is_dir())
        remote = self.git("remote", "get-url", "sandbox", cwd=self.clean).stdout.strip()
        self.assertEqual(remote, f"file://{self.sandbox}")
        self.assertTrue(self.same(self.installed_hook, self.pre_push))
        self.assertTrue(self.same(self.clean / ".git" / "hooks" / "pre-push", self.pre_push))
        self.assertTrue((self.clean / ".git" / "hooks" / "pre-push").stat().st_mode & 0o111)
        self.assertTrue(self.same(self.clean / ".devcontainer" / "devcontainer.json", self.recipe / "devcontainer.json"))
        self.assertTrue(self.same(self.clean / ".devcontainer" / "setup.sh", self.recipe / "setup.sh"))
        self.assertTrue(self.same(self.clean / ".github" / "workflows" / "verify.yml", self.ci))
        self.assertIn("Next,", r.stdout)

    def test_every_written_path_is_printed_absolute(self):
        r = self.ok()
        wrote = [ln for ln in r.stdout.splitlines() if ln.startswith("  wrote ")]
        self.assertTrue(wrote)
        for ln in wrote:
            self.assertTrue(ln.split()[1].startswith("/"), ln)

    def test_the_kit_lands_at_docs_agent_kit_and_never_beside_it(self):
        self.ok()
        self.assertTrue((self.clean / "_docs" / "agent-kit" / "setup.md").is_file())
        self.assertTrue((self.clean / "_docs" / "agent-kit" / "scripts" / "verify.sh").is_file())
        self.assertFalse((self.clean / "agent-kit").exists())

    def test_a_core_hooks_path_is_unset_so_the_push_check_can_run(self):
        self.git("clone", "-q", self.url, str(self.clean), cwd=self.work)
        self.git("config", "core.hooksPath", ".githooks", cwd=self.clean)
        self.ok()
        r = self.run_cmd(["git", "config", "--local", "--get", "core.hooksPath"], cwd=self.clean)
        self.assertNotEqual(r.returncode, 0, "core.hooksPath is still set")


class ExistingRepoTest(BootstrapCase):
    def snapshot(self):
        out = {}
        for root in (self.projects, self.home):
            for p in sorted(root.rglob("*")):
                rel = p.relative_to(self.work)
                in_git = ".git" in rel.parts
                if p.is_file() and (not in_git or "hooks" in rel.parts):
                    out[str(rel)] = p.read_bytes()
        self.assertTrue(any(k.endswith("verify.yml") for k in out), "snapshot is empty")
        return out

    def test_re_running_changes_nothing(self):
        self.ok()
        before = self.snapshot()
        r = self.ok()
        self.assertEqual(self.snapshot(), before)
        self.assertIn("Nothing changed", r.stdout)
        self.assertNotIn("  wrote ", r.stdout)

    def test_the_identity_filled_into_setup_sh_survives_a_re_run(self):
        self.ok()
        setup = self.clean / ".devcontainer" / "setup.sh"
        edited = setup.read_text(encoding="utf-8").replace("<Your Name>", "Jane Roe")
        setup.write_text(edited, encoding="utf-8")
        r = self.ok()
        self.assertEqual(setup.read_text(encoding="utf-8"), edited, "the human's identity was overwritten")
        self.assertIn("kept", r.stdout)
        self.assertNotIn("wrote " + str(setup), r.stdout)

    def test_edited_ci_workflow_and_devcontainer_survive_a_re_run(self):
        self.ok()
        for rel in (".github/workflows/verify.yml", ".devcontainer/devcontainer.json"):
            p = self.clean / rel
            p.write_text(p.read_text(encoding="utf-8") + "\n# mine\n", encoding="utf-8")
        before = {rel: (self.clean / rel).read_bytes() for rel in (".github/workflows/verify.yml", ".devcontainer/devcontainer.json")}
        self.ok()
        for rel, data in before.items():
            self.assertEqual((self.clean / rel).read_bytes(), data, rel)

    def test_changes_under_the_copied_kit_survive_a_re_run(self):
        self.ok()
        mine = self.clean / "_docs" / "agent-kit" / "MY-NOTES.md"
        mine.write_text("keep\n", encoding="utf-8")
        r = self.ok()
        self.assertTrue(mine.is_file(), "a file under _docs/agent-kit was removed")
        self.assertIn("kept", r.stdout)

    def test_force_replaces_the_files_it_would_keep(self):
        self.ok()
        setup = self.clean / ".devcontainer" / "setup.sh"
        setup.write_text("# edited\n", encoding="utf-8")
        mine = self.clean / "_docs" / "agent-kit" / "MY-NOTES.md"
        mine.write_text("x\n", encoding="utf-8")
        self.ok("--force")
        self.assertTrue(self.same(setup, self.recipe / "setup.sh"))
        self.assertFalse(mine.exists())

    def test_a_stale_push_check_is_brought_back_in_step(self):
        self.ok()
        hook = self.clean / ".git" / "hooks" / "pre-push"
        hook.write_text("#!/bin/sh\n# old\n", encoding="utf-8")
        self.ok()
        self.assertTrue(self.same(hook, self.pre_push))

    def test_an_existing_clone_is_reused_not_recloned(self):
        self.ok()
        marker = self.clean / "LEFT_BY_HUMAN.txt"
        marker.write_text("keep me\n", encoding="utf-8")
        self.ok()
        self.assertTrue(marker.is_file())


class RunLocationTest(BootstrapCase):
    def test_running_inside_a_sandbox_clone_is_refused(self):
        """A real sandbox is a plain clone: no 'sandbox' remote, no push check."""
        sb = self.make_sandbox_clone()
        self.assertNotEqual(self.run_cmd(["git", "remote", "get-url", "sandbox"], cwd=sb).returncode, 0)
        r = self.bootstrap(cwd=sb)
        self.refused(r)
        self.assertIn("git work tree", r.stderr)
        self.assertFalse((sb / NAME).exists(), "a project was created inside the sandbox clone")

    def test_running_inside_a_subfolder_of_a_clone_is_refused(self):
        sb = self.make_sandbox_clone()
        (sb / "sub").mkdir()
        self.refused(self.bootstrap(cwd=sb / "sub"))

    def test_running_inside_a_clean_clone_is_refused_too(self):
        self.ok()
        other = self.work / "other"
        other.mkdir()
        self.git("clone", "-q", self.url, str(other / "x"), cwd=self.work)
        self.git("remote", "add", "sandbox", "file:///nowhere", cwd=other / "x")
        r = self.bootstrap(cwd=other / "x")
        self.assertEqual(r.returncode, 1)
        self.assertIn("git work tree", r.stderr)

    def test_a_plain_folder_is_accepted(self):
        self.ok()

    def test_a_stray_non_git_folder_with_the_repo_name_is_refused_before_cloning(self):
        self.clean.mkdir()
        (self.clean / "notes.txt").write_text("mine\n", encoding="utf-8")
        r = self.bootstrap()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("not a git clone", r.stderr)
        self.assertNotIn("fatal:", r.stderr)
        self.assertFalse(self.sandbox.exists(), "the sandbox was cloned before the refusal")
        self.assertFalse((self.home / ".agent-hooks").exists())
        self.assertEqual(sorted(p.name for p in self.clean.iterdir()), ["notes.txt"])

    def test_a_stray_non_git_folder_with_the_sandbox_name_is_refused_before_cloning(self):
        self.sandbox.mkdir()
        r = self.bootstrap()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertFalse(self.clean.exists(), "the clean clone was created before the refusal")


class KitPathTest(BootstrapCase):
    def test_a_kit_with_a_tracked_edit_is_refused(self):
        (self.kit / "setup.md").write_text("an agent edited this\n", encoding="utf-8")
        r = self.bootstrap()
        self.refused(r)
        self.assertIn("uncommitted", r.stderr)

    def test_a_kit_with_an_untracked_file_is_refused(self):
        (self.kit / "scripts" / "extra.sh").write_text("echo hi\n", encoding="utf-8")
        self.refused(self.bootstrap())

    def test_a_kit_that_is_not_a_git_clone_is_refused(self):
        plain = self.work / "unpacked" / "agent-kit"
        shutil.copytree(KIT, plain, ignore=shutil.ignore_patterns("__pycache__"))
        r = self.bootstrap("--kit", str(plain))
        self.refused(r)
        self.assertIn("not a git clone", r.stderr)

    def test_a_folder_that_is_not_a_kit_is_refused(self):
        empty = self.work / "empty"
        empty.mkdir()
        r = self.bootstrap("--kit", str(empty))
        self.refused(r)
        self.assertIn("not an agent kit", r.stderr)

    def test_the_kit_flag_takes_a_clean_kit_clone(self):
        """--kit points the script at another committed kit; it is the one copied."""
        other = self.work / "other-kit"
        shutil.copytree(self.kit_repo, other)
        (other / "agent-kit" / "marker.txt").write_text("other\n", encoding="utf-8")
        self.git("add", "--all", cwd=other)
        self.git(*IDENT, "commit", "-q", "-m", "m", cwd=other)
        self.git("push", "-q", "origin", "HEAD:refs/heads/other", cwd=other)
        self.ok("--kit", str(other / "agent-kit"))
        self.assertTrue((self.clean / "_docs" / "agent-kit" / "marker.txt").is_file())

    def commit_kit_edit(self):
        """A committed, unpushed edit on top of the cloned HEAD: what an agent leaves in a sandbox."""
        (self.kit / "setup.md").write_text("an agent's committed edit\n", encoding="utf-8")
        self.git("add", "--all", cwd=self.kit_repo)
        self.git(*IDENT, "commit", "-q", "-m", "agent edit", cwd=self.kit_repo)

    def test_a_committed_but_unpushed_kit_edit_is_refused(self):
        self.commit_kit_edit()
        r = self.bootstrap()
        self.refused(r)
        self.assertIn("no reviewed remote branch", r.stderr)
        self.assertIn("fetch", r.stderr, "the message should say how a stale clean clone recovers")

    def test_the_same_edit_is_accepted_once_it_is_on_a_remote_branch(self):
        self.commit_kit_edit()
        self.git("push", "-q", "origin", "HEAD:main", cwd=self.kit_repo)
        self.ok()
        self.assertEqual((self.clean / "_docs" / "agent-kit" / "setup.md").read_text(encoding="utf-8"),
                         "an agent's committed edit\n")

    def kit_sandbox_with_agent_commit(self):
        """A sandbox clone of the kit (a working clone) with an unreviewed agent commit on main."""
        sb = self.work / "kit-sandbox"
        self.git("clone", "-q", str(self.kit_origin), str(sb), cwd=self.work)
        (sb / "agent-kit" / "setup.md").write_text("unreviewed agent edit\n", encoding="utf-8")
        self.git("add", "--all", cwd=sb)
        self.git(*IDENT, "commit", "-q", "-m", "agent edit", cwd=sb)
        return sb

    def fetch_and_check_out(self, remote, url):
        self.git("remote", "add", remote, url, cwd=self.kit_repo)
        self.git("fetch", "-q", remote, cwd=self.kit_repo)
        self.git("checkout", "-q", "--detach", f"{remote}/main", cwd=self.kit_repo)

    def test_a_kit_checked_out_from_the_sandbox_remote_is_refused(self):
        """QA's bypass at a5c7d7a: the normal review flow fetches sandbox/main into the clean clone."""
        sb = self.kit_sandbox_with_agent_commit()
        self.fetch_and_check_out("sandbox", f"file://{sb}")
        r = self.bootstrap()
        self.refused(r)
        self.assertIn("sandbox", r.stderr)
        # The fixture really is QA's case: the agent's edit is what is checked out.
        self.assertEqual((self.kit / "setup.md").read_text(encoding="utf-8"), "unreviewed agent edit\n")

    def test_a_working_clone_remote_under_another_name_is_refused(self):
        """Renaming the sandbox remote doesn't help: a local working clone is never a review gate."""
        sb = self.kit_sandbox_with_agent_commit()
        for name, url in (("agentbox", str(sb)), ("other", f"file://{sb}")):
            with self.subTest(name=name):
                self.fetch_and_check_out(name, url)
                self.refused(self.bootstrap())
                self.git("checkout", "-q", "main", cwd=self.kit_repo)
                self.git("remote", "remove", name, cwd=self.kit_repo)

    def test_a_sandbox_commit_is_accepted_once_it_is_pushed_to_origin(self):
        sb = self.kit_sandbox_with_agent_commit()
        self.fetch_and_check_out("sandbox", f"file://{sb}")
        self.git("push", "-q", "origin", "HEAD:main", cwd=self.kit_repo)
        self.ok()
        self.assertEqual((self.clean / "_docs" / "agent-kit" / "setup.md").read_text(encoding="utf-8"),
                         "unreviewed agent edit\n")

    def test_sandbox_refs_at_the_reviewed_head_do_not_block(self):
        """The usual state: the sandbox remote is fetched and holds the same commit as origin."""
        sb = self.work / "kit-sandbox"
        self.git("clone", "-q", str(self.kit_origin), str(sb), cwd=self.work)
        self.git("remote", "add", "sandbox", f"file://{sb}", cwd=self.kit_repo)
        self.git("fetch", "-q", "sandbox", cwd=self.kit_repo)
        self.ok()

    def test_a_kit_clone_with_no_remote_is_refused(self):
        self.git("remote", "remove", "origin", cwd=self.kit_repo)
        r = self.bootstrap()
        self.refused(r)
        self.assertIn("no reviewed remote branch", r.stderr)

    def test_git_ignored_files_in_the_kit_are_not_copied(self):
        (self.kit / ".gitignore").write_text("ignored.txt\n.env\n", encoding="utf-8")
        self.git("add", "--all", cwd=self.kit_repo)
        self.git(*IDENT, "commit", "-q", "-m", "ignore", cwd=self.kit_repo)
        self.git("push", "-q", "origin", "HEAD:main", cwd=self.kit_repo)
        (self.kit / "ignored.txt").write_text("x\n", encoding="utf-8")
        (self.kit / ".env").write_text("SECRET=placeholder\n", encoding="utf-8")
        self.ok()
        dest = self.clean / "_docs" / "agent-kit"
        self.assertTrue((dest / ".gitignore").is_file())
        self.assertFalse((dest / "ignored.txt").exists(), "an ignored file rode along")
        self.assertFalse((dest / ".env").exists(), "an ignored .env rode along")
        # The ignored files must not make a re-run see the copy as different.
        r = self.ok()
        self.assertIn("matches the kit", r.stdout)
        self.assertIn("Nothing changed", r.stdout)

    def test_executable_bits_survive_the_tracked_copy(self):
        self.ok()
        copied = self.clean / "_docs" / "agent-kit" / "scripts" / "bootstrap-project.sh"
        self.assertTrue(copied.stat().st_mode & 0o111, "the copied script lost its executable bit")

    def test_a_clean_clone_of_the_kit_is_an_accepted_source(self):
        """The human's own clean clone has the 'sandbox' remote and the push check: still fine."""
        self.git("remote", "add", "sandbox", "file:///nowhere", cwd=self.kit_repo)
        hook = self.kit_repo / ".git" / "hooks" / "pre-push"
        hook.write_text("#!/bin/sh\n# agent-kit-push-check v2\nexit 0\n", encoding="utf-8")
        self.ok()


class AgentHooksDirTest(BootstrapCase):
    def test_a_missing_agent_hooks_dir_is_created(self):
        self.assertFalse((self.home / ".agent-hooks").exists())
        self.ok()
        self.assertTrue(self.same(self.installed_hook, self.pre_push))

    def test_an_existing_up_to_date_hook_is_left_alone(self):
        (self.home / ".agent-hooks").mkdir(parents=True)
        shutil.copyfile(self.pre_push, self.installed_hook)
        r = self.ok()
        self.assertIn(f"ok    {self.installed_hook} is up to date", r.stdout)


class CiTemplatePlaceholdersTest(BootstrapCase):
    def test_the_copied_workflow_is_the_template_with_its_standalone_placeholders(self):
        r = self.ok()
        copied = (self.clean / ".github" / "workflows" / "verify.yml").read_text(encoding="utf-8")
        self.assertEqual(copied, self.ci.read_text(encoding="utf-8"))
        for placeholder in ("<project>", "<project folder>", "working-directory: <project folder>"):
            self.assertIn(placeholder, copied)
        self.assertIn("standalone", r.stdout)
        self.assertIn("working-directory", r.stdout)


class UsageTest(BootstrapCase):
    def test_no_url_prints_usage_and_exits_non_zero(self):
        r = self.run_cmd(["bash", str(self.script)], cwd=self.projects)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("usage:", r.stderr)

    def test_it_is_not_a_make_target(self):
        makefile = (KIT.parent / "Makefile").read_text(encoding="utf-8")
        self.assertNotIn("bootstrap-project.sh", makefile)


if __name__ == "__main__":
    unittest.main()
