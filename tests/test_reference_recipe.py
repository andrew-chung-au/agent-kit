"""Pins the reference dev container recipe and its CI template pins (issue #95).

Text and JSON only: nothing here runs Docker, Node or uv. The pins are the
issue's unverified values; this test keeps the copies of each in step, it does
not check that the releases exist.

problems(text) takes the recipe's JSON text and returns the boundary problems
it finds, so the same function runs on the real file (must be empty) and on
fixtures (must not be). Limit: it reads the JSON and the raw text, so it does
not know what a feature or an image does once it runs.
"""
from __future__ import annotations

import json
import re
import unittest

from kit_repo import KIT

LOCAL = KIT / "environments" / "local-sandbox"
RECIPE = LOCAL / "devcontainer.json"
SETUP = LOCAL / "setup.sh"
CI_TEMPLATE = KIT / "templates" / "ci-verify.yml.template"

NODE_FEATURE = "ghcr.io/devcontainers/features/node:2"
GH_FEATURE = "ghcr.io/devcontainers/features/github-cli:1"
NODE_PIN = "24.22.0"
NVM_PIN = "0.40.8"
UV_PIN = "0.13.6"
OPENCODE_PIN = "2.2.5"
PATH_VALUE = "${containerEnv:PATH}:/home/vscode/.local/bin:/home/vscode/.opencode/bin"


def mount_problems(mount):
    """A mount is allowed only if it is a named volume (no host path as its source)."""
    if isinstance(mount, dict):
        kind, source = mount.get("type", ""), str(mount.get("source", mount.get("src", "")))
    else:
        parts = dict(p.split("=", 1) for p in str(mount).split(",") if "=" in p)
        kind, source = parts.get("type", ""), parts.get("source", parts.get("src", ""))
    if kind != "volume" or source.startswith(("/", "~", ".", "${")) or not source:
        return [f"mount {mount!r} is not a named volume (host path or bind mount)"]
    return []


def problems(text):
    found = []
    if "docker.sock" in text:
        found.append("a Docker socket is mentioned (docker.sock)")
    data = json.loads(text)
    for key in ("initializeCommand", "privileged", "runArgs"):
        if key in data:
            found.append(f"{key} is set")
    for mount in data.get("mounts", []):
        found.extend(mount_problems(mount))
    return found


def setup_code():
    return [ln for ln in SETUP.read_text(encoding="utf-8").splitlines() if not ln.lstrip().startswith("#")]


class RecipeTest(unittest.TestCase):
    def setUp(self):
        self.text = RECIPE.read_text(encoding="utf-8")
        self.data = json.loads(self.text)

    def test_the_name_is_the_folder_name(self):
        self.assertEqual(self.data["name"], "${localWorkspaceFolderBasename}")

    def test_the_path_entry(self):
        self.assertEqual(self.data["remoteEnv"]["PATH"], PATH_VALUE)

    def test_the_node_feature_and_the_github_feature(self):
        features = self.data["features"]
        self.assertEqual(features[NODE_FEATURE], {"version": NODE_PIN, "nvmVersion": NVM_PIN, "pnpmVersion": "none"})
        self.assertIn(GH_FEATURE, features)

    def test_the_rest_of_the_recipe_is_unchanged(self):
        d = self.data
        self.assertEqual(d["image"], "mcr.microsoft.com/devcontainers/python:3.12")
        self.assertEqual(d["containerEnv"], {
            "SSH_AUTH_SOCK": "", "GIT_TERMINAL_PROMPT": "0", "CLAUDE_CONFIG_DIR": "/home/vscode/.claude"})
        self.assertEqual(d["mounts"], ["source=claude-config,target=/home/vscode/.claude,type=volume"])
        self.assertEqual(d["postCreateCommand"], "bash .devcontainer/setup.sh")
        self.assertEqual(d["remoteEnv"]["GH_TOKEN"], "${localEnv:AGENT_GH_TOKEN}")
        self.assertEqual(d["remoteEnv"]["OPENCODE_API_KEY"], "${localEnv:OPENCODE_API_KEY}")

    def test_the_reference_has_none_of_the_refused_settings(self):
        self.assertEqual(problems(self.text), [])


class RefusalTest(unittest.TestCase):
    def variant(self, **extra):
        data = json.loads(RECIPE.read_text(encoding="utf-8"))
        data.update(extra)
        return json.dumps(data)

    def test_each_refused_setting_is_flagged(self):
        fixtures = {
            "docker socket mount": self.variant(mounts=["source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"]),
            "docker socket anywhere": self.variant(containerEnv={"DOCKER_HOST": "unix:///var/run/docker.sock"}),
            "initializeCommand": self.variant(initializeCommand="echo hi"),
            "privileged": self.variant(privileged=True),
            "runArgs": self.variant(runArgs=["--network=host"]),
            "host path bind mount": self.variant(mounts=["source=/home/me/data,target=/data,type=bind"]),
            "bind mount of a relative host path": self.variant(mounts=["source=.,target=/data,type=bind"]),
            "mount object with a host source": self.variant(mounts=[{"type": "bind", "source": "/etc", "target": "/e"}]),
            "volume named by a host variable": self.variant(mounts=["source=${localEnv:HOME},target=/h,type=volume"]),
        }
        for label, text in fixtures.items():
            with self.subTest(label):
                self.assertTrue(problems(text), label)

    def test_a_named_volume_is_not_flagged(self):
        self.assertEqual(problems(self.variant(mounts=["source=other,target=/x,type=volume"])), [])


class PinsTest(unittest.TestCase):
    """The Node and uv pins agree across the recipe, setup.sh and the CI template."""

    def test_setup_node_version_equals_the_feature_version(self):
        feature = json.loads(RECIPE.read_text(encoding="utf-8"))["features"][NODE_FEATURE]["version"]
        code = "\n".join(setup_code())
        self.assertEqual(re.findall(r'^node_version="([^"]+)"', code, re.M), [feature])
        self.assertIn('/usr/local/share/nvm/versions/node/v${node_version}/bin', code)

    def test_setup_uv_pin_equals_the_ci_template_pin(self):
        code = "\n".join(setup_code())
        pins = set(re.findall(r"pipx install(?: --force)? uv==(\S+)", code))
        self.assertEqual(pins, {UV_PIN})
        ci = CI_TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(re.findall(r'(?m)^\s*#\s+version: "([^"]+)"', ci), [UV_PIN])

    def test_the_uv_pin_is_not_older_than_the_tls_root_fix(self):
        """uv before 0.13.4 bundles a withdrawn TLS root (GHSA-hq85-5cpj-mr62)."""
        self.assertGreaterEqual(tuple(int(n) for n in UV_PIN.split(".")), (0, 13, 4))

    def test_setup_pins_opencode_2_from_the_v2_installer(self):
        """The recipe installs OpenCode 2 at the pin from the v2 installer, not v1."""
        code = "\n".join(setup_code())
        self.assertEqual(re.findall(r'^opencode_version="([^"]+)"', code, re.M), [OPENCODE_PIN])
        # The major is 2: the v1 installer (/install) refuses 2.x.
        self.assertEqual(OPENCODE_PIN.split(".")[0], "2")
        # It installs from the v2 endpoint and passes the pin as --version.
        self.assertIn("https://opencode.ai/v2/install", code)
        self.assertNotIn("https://opencode.ai/install", code)
        self.assertRegex(code, r'--version\s+"\$opencode_version"')
        # The guard matches on v<version> so it re-runs only when the version differs.
        # Whitespace-tolerant, so a harmless reformat does not break the test.
        self.assertRegex(code, r'\*"v\$\{opencode_version\}"\s*\)\s*;;')

    def test_ci_template_node_pin_equals_the_feature_version(self):
        feature = json.loads(RECIPE.read_text(encoding="utf-8"))["features"][NODE_FEATURE]["version"]
        ci = CI_TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(re.findall(r'node-version: "([^"]+)"', ci), [feature])

    def test_a_drifted_pin_is_detected(self):
        """The comparison itself: two different values do not compare equal."""
        ci = CI_TEMPLATE.read_text(encoding="utf-8").replace('node-version: "24.22.0"', 'node-version: "24.21.0"')
        self.assertNotEqual(re.findall(r'node-version: "([^"]+)"', ci), [NODE_PIN])

    def test_the_ci_template_names_setup_node_and_setup_uv(self):
        ci = CI_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("astral-sh/setup-uv@v6", ci)
        self.assertIn("actions/setup-node@v4", ci)


class NoPersonalValuesTest(unittest.TestCase):
    def test_the_identity_keeps_its_placeholders(self):
        text = SETUP.read_text(encoding="utf-8")
        self.assertIn('git config --global user.name "<Your Name>"', text)
        self.assertIn('git config --global user.email "<id+username@users.noreply.github.com>"', text)
        self.assertEqual(len(re.findall(r"git config --global user\.(name|email)", text)), 2)

    def test_a_real_looking_identity_would_be_caught(self):
        text = SETUP.read_text(encoding="utf-8").replace("<Your Name>", "Jane Doe")
        self.assertNotIn('user.name "<Your Name>"', text)

    def test_no_secret_looking_value_in_the_reference_files(self):
        for path in (RECIPE, SETUP):
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"ghp_[A-Za-z0-9]{20,}|github_pat_", path.name)
            emails = re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", text)
            self.assertEqual([e for e in emails if e != "id+username@users.noreply.github.com"], [], path.name)


if __name__ == "__main__":
    unittest.main()
