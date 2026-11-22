"""Behaviour tests for agent-kit/environments/local-sandbox/setup.sh (issue #95).

Run in a throwaway repo with a throwaway HOME and GIT_CONFIG_GLOBAL under
.scratch/. Stubs for sudo, apt-get, curl, pipx, corepack, uv, opencode and claude
sit first on PATH: in the refusal cases any call fails the test; in the allowed
case they succeed without installing anything. Nothing here installs a tool,
reaches the network or runs Docker.
"""
from __future__ import annotations

import re
import unittest

from kit_repo import KIT, KitTestCase

SETUP = KIT / "environments" / "local-sandbox" / "setup.sh"
STUBBED = ("sudo", "apt-get", "curl", "pipx", "corepack", "uv", "opencode", "claude")
# What a stub prints when setup.sh asks for a version. The defaults take the install
# branches: a uv version other than the pin, and opencode's pinned version. Tests set
# these per case, including "" to print nothing and fail the command.
VERSIONS = {"uv": "uv 0.0.0", "opencode": "opencode v2.2.5"}
PINNED_UV = "pipx install --force uv==0.13.6"
NAME_LINE = 'git config --global user.name "<Your Name>"'


def code_lines():
    return [ln for ln in SETUP.read_text(encoding="utf-8").splitlines() if not ln.lstrip().startswith("#")]


class SetupCase(KitTestCase):
    def setUp(self):
        super().setUp()
        self.add_project()
        self.write("README.md")
        self.commit_all()
        self.called = self.work / "stub-called"

    def stub_commands(self, succeed, versions=None, failing=()):
        """Write the stubs first on PATH.

        `succeed` sets every stub's exit status; `versions` overrides, per command,
        the line it prints ("" prints nothing); `failing` names commands that exit
        non-zero even when the rest succeed.
        """
        printed = dict(VERSIONS)
        printed.update(versions or {})
        failing = set(failing)
        stubs = self.work / "stubs"
        for name in STUBBED:
            body = '#!/bin/sh\necho "%s $*" >> "%s"\n' % (name, self.called)
            if printed.get(name):
                body += 'echo "%s"\n' % printed[name]
            body += "exit %d\n" % (0 if succeed and name not in failing else 97)
            p = stubs / name
            p.write_text(body, encoding="utf-8")
            p.chmod(0o755)

    def run_setup(self):
        return self.run_cmd(["bash", str(SETUP)])

    def calls(self):
        return self.called.read_text(encoding="utf-8").splitlines() if self.called.exists() else []

    def pinned_uv_installs(self):
        return [c for c in self.calls() if c == PINNED_UV]

    def global_config(self):
        return (self.work / "empty.gitconfig").read_text(encoding="utf-8")


class RefusedTest(SetupCase):
    def assert_refused(self, r):
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("clean clone", r.stderr)
        self.assertIn("-sandbox", r.stderr)
        self.assertIn("environments.md", r.stderr)
        self.assertEqual(self.calls(), [], "a stubbed command ran before the refusal")
        self.assertEqual(self.global_config(), "", "git config --global ran before the refusal")
        self.assertNotIn("Setup complete", r.stdout)

    def test_a_sandbox_remote_is_refused(self):
        self.stub_commands(succeed=False)
        self.git("remote", "add", "sandbox", "../sandbox-repo")
        self.assert_refused(self.run_setup())

    def test_the_clean_clone_push_check_is_refused(self):
        self.stub_commands(succeed=False)
        hook = self.repo / ".git" / "hooks" / "pre-push"
        hook.write_text("#!/bin/sh\n# agent-kit-push-check v2\nexit 0\n", encoding="utf-8")
        hook.chmod(0o755)
        self.assert_refused(self.run_setup())

    def test_both_signals_together_are_refused(self):
        self.stub_commands(succeed=False)
        self.git("remote", "add", "sandbox", "../sandbox-repo")
        hook = self.repo / ".git" / "hooks" / "pre-push"
        hook.write_text("#!/bin/sh\n# agent-kit-push-check v2\n", encoding="utf-8")
        self.assert_refused(self.run_setup())


class AllowedTest(SetupCase):
    def test_a_plain_sandbox_repo_passes_the_check_and_runs_to_the_end(self):
        self.stub_commands(succeed=True)
        r = self.run_setup()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Setup complete", r.stdout)
        # uv is installed with the pinned version, then corepack is disabled, in that order.
        calls = self.calls()
        pipx = [i for i, c in enumerate(calls) if c.startswith("pipx install") and "uv==0.13.6" in c]
        corepack = [i for i, c in enumerate(calls) if c == "corepack disable"]
        self.assertEqual(len(pipx), 1, calls)
        self.assertEqual(len(corepack), 1, calls)
        self.assertLess(pipx[0], corepack[0])
        # Global git config was written, only inside the throwaway.
        config = self.global_config()
        self.assertIn("<Your Name>", config)
        self.assertIn("<id+username@users.noreply.github.com>", config)
        self.assertFalse((self.work / "home" / ".gitconfig").exists())

    def test_running_it_twice_still_succeeds(self):
        self.stub_commands(succeed=True)
        self.assertEqual(self.run_setup().returncode, 0)
        # A rebuilt container starts with a fresh global git config; the earlier run's
        # credential lines are not what this test is about (setup.sh adds them with --add).
        (self.work / "empty.gitconfig").write_text("", encoding="utf-8")
        self.assertEqual(self.run_setup().returncode, 0)

    def test_a_folder_that_is_not_a_git_repo_is_not_refused_by_the_check(self):
        """The check looks only at git signals: no repo means neither signal is present."""
        self.stub_commands(succeed=True)
        bare = self.work / "not-a-repo"
        bare.mkdir()
        r = self.run_cmd(["bash", str(SETUP)], cwd=bare)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class UvTest(SetupCase):
    """Both branches of setup.sh's uv version check, and its failure edges."""

    def assert_setup_complete(self, r):
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Setup complete", r.stdout)

    def test_a_different_uv_version_installs_the_pin_once(self):
        self.stub_commands(succeed=True, versions={"uv": "uv 0.0.0"})
        r = self.run_setup()
        self.assert_setup_complete(r)
        calls = self.calls()
        self.assertIn("uv --version", calls)
        self.assertEqual(self.pinned_uv_installs(), [PINNED_UV], calls)
        self.assertLess(calls.index("uv --version"), calls.index(PINNED_UV))
        self.assertLess(calls.index(PINNED_UV), calls.index("corepack disable"))
        # opencode and claude are stubbed at their pins here, so neither installer is fetched.
        self.assertIn("opencode --version", calls)
        self.assertEqual([c for c in calls if c.startswith("curl")], [], calls)

    def test_the_pinned_uv_version_does_not_install_again(self):
        self.stub_commands(succeed=True, versions={"uv": "uv 0.13.6"})
        r = self.run_setup()
        self.assert_setup_complete(r)
        calls = self.calls()
        self.assertIn("uv --version", calls)
        self.assertEqual([c for c in calls if c.startswith("pipx")], [], calls)
        self.assertIn("corepack disable", calls)
        self.assertLess(calls.index("uv --version"), calls.index("corepack disable"))

    def test_an_unreadable_uv_version_still_installs_the_pin(self):
        self.stub_commands(succeed=True, versions={"uv": ""}, failing=("uv",))
        r = self.run_setup()
        self.assert_setup_complete(r)
        self.assertEqual(self.pinned_uv_installs(), [PINNED_UV], self.calls())

    def test_a_failed_uv_install_is_not_masked(self):
        self.stub_commands(succeed=True, versions={"uv": "uv 0.0.0"}, failing=("pipx",))
        r = self.run_setup()
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("Setup complete", r.stdout)
        self.assertEqual(self.pinned_uv_installs(), [PINNED_UV], self.calls())


class OrderTest(unittest.TestCase):
    """Static order in setup.sh (comments ignored)."""

    def first(self, pattern):
        for i, line in enumerate(code_lines()):
            if re.search(pattern, line):
                return i
        self.fail("no line matches %r" % pattern)

    def test_the_check_comes_before_anything_that_installs_or_configures(self):
        check = self.first(r"git remote get-url sandbox")
        for pattern in (r"\bsudo\b", r"\bapt-get\b", r"\bcurl\b", r"\bpipx\b", r"\bcorepack\b", r"git config"):
            self.assertLess(check, self.first(pattern), pattern)

    def test_the_check_comes_after_the_path_export(self):
        self.assertLess(self.first(r'^export PATH="\$HOME/\.local/bin'), self.first(r"git remote get-url sandbox"))

    def test_uv_then_node_path_then_corepack_then_identity(self):
        order = [self.first(p) for p in (r"pipx install", r"^export PATH=.*nvm/versions/node", r"^corepack disable", NAME_LINE)]
        self.assertEqual(order, sorted(order))
        self.assertEqual(len(set(order)), 4)

    def test_the_check_uses_the_same_two_signals_as_install_hooks(self):
        hooks = (KIT / "scripts" / "install-hooks.sh").read_text(encoding="utf-8")
        setup = "\n".join(code_lines())
        for signal in ("git remote get-url sandbox", "grep -qs '^# agent-kit-push-check'"):
            self.assertIn(signal, hooks)
            self.assertIn(signal, setup)


if __name__ == "__main__":
    unittest.main()
