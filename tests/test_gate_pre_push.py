"""agent-kit/githooks/pre-push, the repo-wide dispatcher (issue #40).

Run as git runs it: `pre-push <remote> <url>` with the refs on stdin, cwd inside
the repo. Each project's `make verify` is a stub Makefile that appends the
project folder and BASE to a record file. A bare `origin` lives next to the repo.
The git-lfs cases build a PATH holding only the tools the hook needs, so a real
git-lfs can never be found.
"""
from __future__ import annotations

import os
import shutil
import unittest

from kit_repo import KitTestCase, KIT, DEFAULT_CONF

HOOK = KIT / "githooks" / "pre-push"
ZERO = "0" * 40
STUB_MAKEFILE = (
    "verify:\n"
    '\t@echo "$(notdir $(CURDIR)) BASE=$(BASE)" >> "$(RECORD)"\n'
    "\t@test ! -e verify-fails\n"
)
TOOLS = ("git", "make", "bash", "sh", "dirname", "sort", "tail", "cat", "env", "uname",
         "true", "false", "test", "rm", "mkdir", "head", "tr", "sed", "grep", "expr")
LFS_STUB = (
    '#!/bin/sh\n'
    'echo "args: $*" >> "$LFS_RECORD"\n'
    'cat >> "$LFS_RECORD"\n'
    'exit "${LFS_EXIT:-0}"\n'
)


class PrePushTest(KitTestCase):
    def setUp(self):
        super().setUp()
        self.record = self.work / "verify-record"
        self.lfs_record = self.work / "lfs-record"
        self.origin = self.work / "origin.git"
        self.run_cmd(["git", "init", "-q", "--bare", str(self.origin)], cwd=self.work)
        self.git("remote", "add", "origin", str(self.origin))
        for p in ("proj_a", "proj_b"):
            self.project(p)
        self.write("plain/file.txt", "p\n")
        self.write("README.md", "r\n")
        self.base = self.commit_all("base")
        self.slate_ref = self.base
        self.git("push", "-q", "origin", "main")

    def project(self, name):
        self.write(name + "/agent-kit.conf", DEFAULT_CONF)
        self.write(name + "/Makefile", STUB_MAKEFILE)
        self.write(name + "/file.txt", "v1\n")

    def commit_change(self, *rels, message="change"):
        for r in rels:
            self.write(r, "changed %s\n" % message)
        return self.commit_all(message)

    def head(self):
        return self.git("rev-parse", "HEAD").stdout.strip()

    def hook(self, *lines, env=None):
        stdin = "".join(l + "\n" for l in lines)
        e = {"RECORD": str(self.record), "LFS_RECORD": str(self.lfs_record)}
        e.update(env or {})
        return self.run_cmd(["bash", HOOK, "origin", str(self.origin)], env=e, stdin=stdin)

    def update(self, local, remote, ref="refs/heads/main"):
        return "%s %s %s %s" % (ref, local, ref, remote)

    def verified(self):
        if not self.record.exists():
            return []
        return self.record.read_text(encoding="utf-8").splitlines()

    def no_lfs_path(self):
        """A PATH of the stubs folder plus symlinks to the tools the hook needs, and no git-lfs."""
        bindir = self.work / "bin-no-lfs"
        bindir.mkdir(exist_ok=True)
        for t in TOOLS:
            found = shutil.which(t)
            if found and not (bindir / t).exists():
                (bindir / t).symlink_to(found)
        self.assertFalse((bindir / "git-lfs").exists())
        return os.pathsep.join([str(self.work / "stubs"), str(bindir)])

    def lfs_stub_path(self):
        base = self.no_lfs_path()
        lfsdir = self.work / "bin-lfs"
        lfsdir.mkdir(exist_ok=True)
        stub = lfsdir / "git-lfs"
        stub.write_text(LFS_STUB, encoding="utf-8")
        stub.chmod(0o755)
        return str(lfsdir) + os.pathsep + base

    # verify per project

    def test_a_push_touching_one_project_verifies_it_once_with_the_remote_sha_as_base(self):
        new = self.commit_change("proj_a/file.txt")
        r = self.hook(self.update(new, self.base))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.verified(), ["proj_a BASE=" + self.base])

    def test_a_project_with_several_changed_files_is_verified_once(self):
        new = self.commit_change("proj_a/file.txt", "proj_a/sub/other.txt")
        r = self.hook(self.update(new, self.base))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.verified(), ["proj_a BASE=" + self.base])

    def test_two_projects_in_one_push_both_run(self):
        new = self.commit_change("proj_a/file.txt", "proj_b/file.txt")
        r = self.hook(self.update(new, self.base))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(sorted(self.verified()),
                         ["proj_a BASE=" + self.base, "proj_b BASE=" + self.base])

    def test_a_folder_without_agent_kit_conf_runs_nothing_and_exits_0(self):
        new = self.commit_change("plain/file.txt", "README.md")
        r = self.hook(self.update(new, self.base))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.verified(), [])

    def test_a_failing_verify_blocks_the_push(self):
        self.write("proj_a/verify-fails", "x\n")
        new = self.commit_change("proj_a/file.txt")
        r = self.hook(self.update(new, self.base))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("verify failed, push blocked", r.stderr)
        self.assertIn("proj_a", r.stderr)

    def test_the_second_project_still_runs_after_the_first_fails(self):
        self.write("proj_a/verify-fails", "x\n")
        new = self.commit_change("proj_a/file.txt", "proj_b/file.txt")
        r = self.hook(self.update(new, self.base))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(sorted(self.verified()),
                         ["proj_a BASE=" + self.base, "proj_b BASE=" + self.base])

    # refusals before verify

    def test_uncommitted_tracked_changes_in_a_touched_project_block_without_running_verify(self):
        new = self.commit_change("proj_a/file.txt")
        self.write("proj_a/file.txt", "dirty\n")
        r = self.hook(self.update(new, self.base))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("uncommitted changes", r.stderr)
        self.assertEqual(self.verified(), [])

    def test_an_untracked_file_does_not_block(self):
        new = self.commit_change("proj_a/file.txt")
        self.write("proj_a/untracked.txt")
        r = self.hook(self.update(new, self.base))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.verified(), ["proj_a BASE=" + self.base])

    def test_a_pushed_ref_that_is_not_the_checked_out_head_blocks(self):
        self.git("checkout", "-q", "-b", "other")
        other = self.commit_change("proj_a/file.txt", message="on other")
        self.git("checkout", "-q", "main")
        r = self.hook(self.update(other, self.base, ref="refs/heads/other"))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("isn't checked out", r.stderr)
        self.assertEqual(self.verified(), [])

    # skipped pushes

    def test_a_ref_deletion_is_skipped(self):
        r = self.hook("refs/heads/gone %s refs/heads/gone %s" % (ZERO, self.base))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.verified(), [])

    def test_a_push_with_no_new_commits_is_skipped(self):
        r = self.hook(self.update(self.base, self.base))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.verified(), [])

    def test_a_new_branch_at_a_commit_already_on_a_remote_is_skipped(self):
        r = self.hook(self.update(self.base, ZERO, ref="refs/heads/copy"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.verified(), [])

    def test_empty_stdin_exits_0(self):
        r = self.hook()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.verified(), [])

    # BASE

    def test_a_new_branch_takes_base_from_the_parent_of_the_oldest_commit_not_on_a_remote(self):
        self.commit_change("proj_a/file.txt", message="first")
        new = self.commit_change("proj_a/file.txt", message="second")
        r = self.hook(self.update(new, ZERO, ref="refs/heads/feature"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.verified(), ["proj_a BASE=" + self.base])

    def test_a_remote_sha_that_is_not_in_the_repo_is_treated_as_a_new_branch(self):
        new = self.commit_change("proj_a/file.txt")
        r = self.hook(self.update(new, "ab" * 20))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.verified(), ["proj_a BASE=" + self.base])

    def test_a_root_commit_takes_the_empty_tree_as_base(self):
        fresh = self.work / "fresh"
        fresh.mkdir()
        self.git("init", "-q", "-b", "main", cwd=fresh)
        for k, v in (("user.name", "Kit Test"), ("user.email", "kit-test@example.invalid"),
                     ("commit.gpgsign", "false")):
            self.git("config", k, v, cwd=fresh)
        self.write("proj_a/agent-kit.conf", DEFAULT_CONF, base=fresh)
        self.write("proj_a/Makefile", STUB_MAKEFILE, base=fresh)
        self.git("add", "--all", cwd=fresh)
        self.git("commit", "-q", "--no-verify", "-m", "root", cwd=fresh)
        sha = self.git("rev-parse", "HEAD", cwd=fresh).stdout.strip()
        empty_tree = self.git("hash-object", "-t", "tree", "/dev/null", cwd=fresh).stdout.strip()
        r = self.run_cmd(["bash", HOOK, "origin", "none"], cwd=fresh,
                         env={"RECORD": str(self.record)},
                         stdin=self.update(sha, ZERO, ref="refs/heads/main") + "\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.verified(), ["proj_a BASE=" + empty_tree])

    # Git LFS

    def lfs_attributes(self):
        self.write(".gitattributes", "*.bin filter=lfs diff=lfs merge=lfs -text\n")
        return self.commit_all("lfs attributes")

    def test_lfs_in_use_without_git_lfs_installed_exits_1(self):
        new = self.lfs_attributes()
        r = self.hook(self.update(new, self.base), env={"PATH": self.no_lfs_path()})
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("git-lfs isn't installed", r.stderr)

    def test_no_lfs_use_and_no_git_lfs_exits_0(self):
        new = self.commit_change("plain/file.txt")
        r = self.hook(self.update(new, self.base), env={"PATH": self.no_lfs_path()})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("git-lfs", r.stderr)

    def test_git_lfs_gets_the_hook_args_and_the_refs_on_stdin(self):
        new = self.commit_change("plain/file.txt")
        line = self.update(new, self.base)
        r = self.hook(line, env={"PATH": self.lfs_stub_path()})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        recorded = self.lfs_record.read_text(encoding="utf-8")
        self.assertIn("args: pre-push origin %s" % self.origin, recorded)
        self.assertIn(line, recorded)

    def test_git_lfs_failure_is_the_hook_exit(self):
        new = self.commit_change("plain/file.txt")
        r = self.hook(self.update(new, self.base),
                      env={"PATH": self.lfs_stub_path(), "LFS_EXIT": "1"})
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    def test_git_lfs_is_not_called_after_a_verify_failure(self):
        self.write("proj_a/verify-fails", "x\n")
        new = self.commit_change("proj_a/file.txt")
        r = self.hook(self.update(new, self.base), env={"PATH": self.lfs_stub_path()})
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertFalse(self.lfs_record.exists())

    def test_git_lfs_is_not_called_with_empty_stdin(self):
        r = self.hook(env={"PATH": self.lfs_stub_path()})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(self.lfs_record.exists())


if __name__ == "__main__":
    unittest.main()
