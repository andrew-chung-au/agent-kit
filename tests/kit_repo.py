"""Shared throwaway-repo helper for the kit's gate behaviour tests.

Not named test*.py, so `unittest discover` does not collect it. Test modules
import it with `from kit_repo import KitTestCase`.

Each test gets its own folder under .scratch/ (created if missing) holding a
git repo with the kit's scripts/ and githooks/ copied in, a fixed identity, no
signing, and no inherited git config: GIT_CONFIG_GLOBAL and GIT_CONFIG_SYSTEM
point at an empty file. TMPDIR is a folder under the same .scratch/ folder, and
a stub `docker` is first on PATH: it records a marker and exits 99, so any test
that reaches Docker fails in tearDown.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
SCRATCH = REPO / ".scratch"

DEFAULT_CONF = """KIT_DIR="agent-kit"
TEST_CMD="true"
LINT_CMD=""
TYPECHECK_CMD=""
TEST_FILES=( 'tests/*' )
FORBIDDEN=( '.env' '*/.env' '.env.*' '*/.env.*' '*.db' '*.pem' )
ALLOWED=( '.env.example' '*/.env.example' )
PROTECTED=( 'AGENTS.md' 'agent-kit.conf' 'docs/*' 'protected/*' )
"""

# Names that git quotes in plain output (or that need care in a shell script).
# "plain" is the control: it works with or without the fix.
UNUSUAL_NAMES = {
    "plain": "plain",
    "space": "a b",
    "non-ascii": "café",
    "double quote": 'a"b',
    "backslash": "a\\b",
}


def new_workdir(scratch: Path = SCRATCH, prefix: str = "kit-gate-") -> Path:
    scratch.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=scratch))


def build_env(work: Path, extra: dict | None = None) -> dict:
    """Environment for every subprocess: nothing inherited from the machine."""
    env = {
        k: v for k, v in os.environ.items()
        if not k.startswith(("GIT_", "AGENT_PUSH_CHECK_", "AGENT_KIT_"))
        and k not in ("HUMAN_APPROVED", "FORCE", "BASE", "BUNDLE", "WORK", "SHA", "PROJECTS",
                     "MAKEFLAGS", "MFLAGS", "MAKELEVEL")
    }
    home = work / "home"
    tmp = work / "tmp"
    stubs = work / "stubs"
    for d in (home, tmp, stubs):
        d.mkdir(exist_ok=True)
    empty = work / "empty.gitconfig"
    empty.write_text("", encoding="utf-8")
    docker = stubs / "docker"
    if not docker.exists():
        docker.write_text(
            '#!/bin/sh\necho "docker stub called" >> "%s"\necho DOCKER-STUB-CALLED >&2\nexit 99\n'
            % (work / "docker-called"),
            encoding="utf-8",
        )
        docker.chmod(0o755)
    env.update({
        "HOME": str(home),
        "TMPDIR": str(tmp),
        "GIT_CONFIG_GLOBAL": str(empty),
        "GIT_CONFIG_SYSTEM": str(empty),
        "GIT_CONFIG_NOSYSTEM": "1",
        "PATH": str(stubs) + os.pathsep + env.get("PATH", ""),
    })
    env.update(extra or {})
    return env


class KitTestCase(unittest.TestCase):
    """A throwaway repo per test, at self.repo."""

    def setUp(self):
        self.work = new_workdir()
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.env = build_env(self.work)
        self.repo = self.work / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Kit Test")
        self.git("config", "user.email", "kit-test@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.docker_expected = False
        self.slate_ref = "HEAD"  # what each sub-case resets to

    def tearDown(self):
        if not self.docker_expected:
            self.assertFalse((self.work / "docker-called").exists(), "a test reached Docker")

    # running things

    # Seconds any helper command may run before the test fails (#59). The whole suite takes
    # about 20 seconds, so a command that needs a minute is hung, not slow.
    CMD_TIMEOUT = 60

    def run_cmd(self, args, cwd=None, env=None, stdin=None, timeout=None):
        """Run a command in the throwaway repo.

        Standard input is /dev/null unless `stdin` text is given, so a command that reads
        stdin ends instead of waiting on the caller's terminal or socket. A command that runs
        longer than `timeout` (default CMD_TIMEOUT) fails the test with the command line and
        whatever it printed, never an unhandled TimeoutExpired. The environment is not shown.
        """
        e = dict(self.env)
        e.update(env or {})
        argv = [str(a) for a in args]
        stdin_args = {"stdin": subprocess.DEVNULL} if stdin is None else {"input": stdin}
        try:
            return subprocess.run(
                argv, cwd=str(cwd or self.repo), env=e, **stdin_args,
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=self.CMD_TIMEOUT if timeout is None else timeout,
            )
        except subprocess.TimeoutExpired as expired:
            def shown(data):
                if isinstance(data, bytes):
                    data = data.decode("utf-8", "replace")
                return (data or "")[-2000:]
            self.fail("command timed out after %s s: %s\nstdout: %s\nstderr: %s" % (
                expired.timeout, " ".join(argv), shown(expired.stdout), shown(expired.stderr)))

    def git(self, *args, cwd=None, env=None, check=True):
        r = self.run_cmd(["git", *args], cwd=cwd, env=env)
        if check and r.returncode != 0:
            raise AssertionError("git %s failed (%d): %s" % (" ".join(args), r.returncode, r.stderr))
        return r

    def clear_docker_marker(self):
        (self.work / "docker-called").unlink()

    # building the repo

    def write(self, rel, content="placeholder\n", base=None):
        p = Path(base or self.repo, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    def add_project(self, subdir=".", conf=DEFAULT_CONF, with_scripts=True):
        """Copy the kit's scripts/ and githooks/ in and write agent-kit.conf."""
        folder = Path(self.repo, subdir)
        folder.mkdir(parents=True, exist_ok=True)
        if with_scripts:
            kit = folder / "agent-kit"
            shutil.copytree(KIT / "scripts", kit / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copytree(KIT / "githooks", kit / "githooks")
        (folder / "agent-kit.conf").write_text(conf, encoding="utf-8")
        return folder

    def stage(self, *paths):
        self.git("--literal-pathspecs", "add", "--", *paths)

    def commit_all(self, message="setup"):
        self.git("add", "--all")
        # Setup commits are not under test, so they skip the hook (this is a throwaway repo).
        self.git("commit", "-q", "--no-verify", "-m", message)
        return self.git("rev-parse", "HEAD").stdout.strip()

    def install_precommit(self, src=None):
        hook = self.repo / ".git" / "hooks" / "pre-commit"
        shutil.copyfile(src or KIT / "githooks" / "pre-commit", hook)
        hook.chmod(0o755)

    def try_commit(self, approved=None, message="change"):
        """git commit, running the installed hook. approved=None leaves HUMAN_APPROVED unset."""
        env = {} if approved is None else {"HUMAN_APPROVED": approved}
        return self.git("commit", "-q", "-m", message, env=env, check=False)

    def subTest(self, *args, **params):
        """Every sub-case starts from a clean slate, so one failure cannot cascade into the next."""
        self.git("reset", "-q", "--hard", self.slate_ref, check=False)
        self.git("clean", "-q", "-f", "-d", check=False)
        return super().subTest(*args, **params)

    def unstage_all(self):
        self.git("reset", "-q")
        self.git("clean", "-q", "-f", "-d")
