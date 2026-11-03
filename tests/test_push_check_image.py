"""Pins the reference push-check image (issue #96).

Text only: nothing here runs Docker, Node or uv. image_problems(text) takes the
Dockerfile text and returns what breaks the rules, so the same function runs on
the real file (must be empty) and on fixtures (must not be). The Node, uv and
Python pins must equal the dev container recipe's (issue #95).

Limit: it reads instruction lines. It does not know what a published image
contains, whether a tag exists, or what a RUN line fetches at build time beyond
the patterns below. Every pin stays unverified until the human builds the image.
"""
from __future__ import annotations

import json
import re
import unittest

from kit_repo import KIT

LOCAL = KIT / "environments" / "local-sandbox"
DOCKERFILE = LOCAL / "push-check.Dockerfile"
RECIPE = LOCAL / "devcontainer.json"
SETUP = LOCAL / "setup.sh"
NODE_FEATURE = "ghcr.io/devcontainers/features/node:2"


def instructions(text):
    """Logical Dockerfile instructions: comments dropped, backslash continuations joined."""
    out, buf = [], ""
    for raw in text.splitlines():
        if raw.lstrip().startswith("#"):
            continue
        line = raw.rstrip()
        if not line and not buf:
            continue
        if line.endswith("\\"):
            buf += line[:-1].strip() + " "
            continue
        out.append((buf + line.strip()).strip())
        buf = ""
    if buf:
        out.append(buf.strip())
    return out


def image_tag(ref):
    """The tag of an image reference, or None when it has none."""
    last = ref.rsplit("/", 1)[-1]
    return last.split(":", 1)[1] if ":" in last else None


def image_problems(text):
    found = []
    lines = instructions(text)
    froms = [l.split()[1] for l in lines if l.upper().startswith("FROM ") and len(l.split()) > 1]
    if len(froms) != 1:
        found.append(f"expected one FROM, found {len(froms)}")
    for ref in froms:
        tag = image_tag(ref)
        if tag is None or tag == "latest":
            found.append(f"base image {ref} has no pinned tag")
    for line in lines:
        word = line.split()[0].upper()
        if re.search(r":latest\b|@latest\b", line):
            found.append(f"latest in: {line}")
        if word in ("COPY", "ADD"):
            m = re.search(r"--from=(\S+)", line)
            if word == "ADD" and "--checksum=" not in line:
                found.append(f"ADD without --checksum: {line}")
            elif word == "COPY" and not m:
                found.append(f"COPY from the build context: {line}")
            if m and not m.group(1).isdigit():
                tag = image_tag(m.group(1))
                if tag is None or tag == "latest":
                    found.append(f"copy source image has no pinned tag: {m.group(1)}")
        if word == "RUN":
            if re.search(r"\b(curl|wget)\b[^|]*\|\s*(sudo\s+)?(ba|z|da)?sh\b", line):
                found.append(f"download piped into a shell: {line}")
        if word in ("ENV", "ARG") and re.search(r"(TOKEN|PASSWORD|SECRET|API_KEY|CREDENTIAL)", line, re.I):
            found.append(f"credential-looking {word}: {line}")
        if re.search(r"agent-kit/scripts|\.env\b|gh auth", line):
            found.append(f"kit script, env file or gh login in: {line}")
    return found


def recipe_pins():
    node = json.loads(RECIPE.read_text(encoding="utf-8"))["features"][NODE_FEATURE]["version"]
    setup = "\n".join(l for l in SETUP.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("#"))
    uv = set(re.findall(r"pipx install(?: --force)? uv==(\S+)", setup))
    image = json.loads(RECIPE.read_text(encoding="utf-8"))["image"]
    python = re.search(r"python:(\d+\.\d+)", image).group(1)
    return node, uv, python


def dockerfile_pins(text):
    code = "\n".join(instructions(text))
    node = set(re.findall(r"--from=node:(\d+\.\d+\.\d+)", code))
    uv = set(re.findall(r"--from=ghcr\.io/astral-sh/uv:(\d+\.\d+\.\d+)", code))
    python = set(re.findall(r"(?m)^FROM python:(\d+\.\d+)", code))
    return node, uv, python


class ImageTest(unittest.TestCase):
    def setUp(self):
        self.text = DOCKERFILE.read_text(encoding="utf-8")

    def test_the_reference_has_no_problems(self):
        self.assertEqual(image_problems(self.text), [])

    def test_the_build_checks_every_tool_the_push_check_needs(self):
        run = " ".join(l for l in instructions(self.text) if l.startswith("RUN"))
        for check in ("bash --version", "git --version", "make --version", "python3 --version",
                      "node --version", "npm --version", "uv --version"):
            self.assertIn(check, run)

    def test_every_pin_is_marked_unverified(self):
        self.assertGreaterEqual(self.text.lower().count("unverified"), 3)

    def test_refused_fixtures_are_flagged(self):
        t = self.text
        fixtures = {
            "latest base": t.replace("python:3.12-bookworm", "python:latest"),
            "untagged base": t.replace("python:3.12-bookworm", "python"),
            "two FROM lines": t + "FROM python:3.12-bookworm\n",
            "copy from build context": t + "COPY . /project\n",
            "copy of a kit script": t + "COPY agent-kit/scripts /kit\n",
            "latest uv image": t.replace("uv:0.13.6", "uv:latest"),
            "untagged node image": t.replace("node:24.22.0-bookworm-slim /usr/local/bin/node", "node /usr/local/bin/node"),
            "curl piped to sh": t + "RUN curl -fsSL https://example.invalid/install.sh | sh\n",
            "wget piped to bash": t + "RUN wget -qO- https://example.invalid/i | bash\n",
            "add of a url without checksum": t + "ADD https://example.invalid/x.tar.gz /x\n",
            "token in env": t + "ENV GH_TOKEN=abc\n",
            "env file": t + "COPY --from=python:3.12-bookworm /app/.env /x\n",
        }
        for label, text in fixtures.items():
            with self.subTest(label):
                self.assertNotEqual(text, t, "the fixture did not change the text")
                self.assertTrue(image_problems(text), label)

    def test_a_checksummed_add_is_not_flagged_for_the_checksum(self):
        text = self.text + "ADD --checksum=sha256:" + "0" * 64 + " https://example.invalid/x.tar.gz /x\n"
        self.assertEqual(image_problems(text), [])

    def test_comments_that_mention_the_forbidden_things_are_ignored(self):
        self.assertIn("credentials", self.text)  # the header comment names them
        self.assertEqual(image_problems(self.text), [])


class PinsMatchTheRecipeTest(unittest.TestCase):
    def setUp(self):
        self.text = DOCKERFILE.read_text(encoding="utf-8")

    def test_node_uv_and_python_equal_the_recipe_pins(self):
        node, uv, python = recipe_pins()
        d_node, d_uv, d_python = dockerfile_pins(self.text)
        self.assertEqual(d_node, {node})
        self.assertEqual(d_uv, uv)
        self.assertEqual(len(uv), 1)
        self.assertEqual(d_python, {python})

    def test_a_drifted_dockerfile_is_detected(self):
        node, uv, python = recipe_pins()
        for label, old, new in (("node", f"node:{node}", "node:24.0.0"),
                                ("uv", f"uv:{next(iter(uv))}", "uv:0.1.0"),
                                ("python", "FROM python:3.12", "FROM python:3.11")):
            with self.subTest(label):
                drifted = self.text.replace(old, new)
                self.assertNotEqual(drifted, self.text)
                self.assertNotEqual(dockerfile_pins(drifted), dockerfile_pins(self.text))
                self.assertNotEqual(dockerfile_pins(drifted), ({node}, uv, {python}))


if __name__ == "__main__":
    unittest.main()
