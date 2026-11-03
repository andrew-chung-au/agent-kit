"""Pins the optional Compose variant of the reference dev container (issue #11).

Text and JSON only: nothing here runs Docker or Compose, and no YAML library is
available (standard library only), so compose_problems(text) reads the
non-comment lines of compose.yaml by indentation. Fixtures are the real file
with one limit broken; each must be flagged.

What the line reader does not catch: YAML anchors and merge keys, flow style
(`ports: ["5432:5432"]` is caught only because the key is on the line, but a
mapping written across a `{ ... }` is not read), keys spelled through aliases,
an `include:` of another file, and anything Compose adds when it merges override
files. The human's review of the diff before the rebuild is the other check.
"""
from __future__ import annotations

import json
import re
import unittest

from kit_repo import KIT
from test_reference_recipe import problems as recipe_problems

LOCAL = KIT / "environments" / "local-sandbox"
COMPOSE_DIR = LOCAL / "compose"
COMPOSE = COMPOSE_DIR / "compose.yaml"
DEVCONTAINER = COMPOSE_DIR / "devcontainer.json"
DOCKERFILE = COMPOSE_DIR / "Dockerfile"
STANDARD = LOCAL / "devcontainer.json"

PLACEHOLDERS = ("<folder>", "<db_name>", "<db_user>", "<db_password>")
DATABASE_URL = "postgresql+psycopg://<db_user>:<db_password>@db:5432/<db_name>"
FORBIDDEN_KEYS = ("privileged", "cap_add", "devices", "driver_opts", "extra_hosts", "security_opt")


def code_lines(text):
    """(indent, content) for each non-blank, non-comment line, trailing comments cut."""
    out = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        line = re.sub(r"\s+#.*$", "", raw.rstrip())
        out.append((len(line) - len(line.lstrip()), line.strip()))
    return out


def service_blocks(lines):
    """{service name: [(indent, content), ...]} for the entries under the top-level services key."""
    blocks, current, in_services = {}, None, False
    for indent, content in lines:
        if indent == 0:
            in_services = content == "services:"
            current = None
        elif in_services and indent == 2 and content.endswith(":"):
            current = content[:-1]
            blocks[current] = []
        elif in_services and current is not None:
            blocks[current].append((indent, content))
    return blocks


def list_items_under(block, key):
    """The `- item` strings under `key:` in a service block (short syntax)."""
    items, active, key_indent = [], False, None
    for indent, content in block:
        if content == key + ":":
            active, key_indent = True, indent
        elif active and indent <= key_indent:
            active = False
        elif active and content.startswith("- "):
            items.append(content[2:].strip())
    return items


def compose_problems(text):
    found = []
    lines = code_lines(text)
    code = "\n".join(c for _, c in lines)
    if "docker.sock" in code:
        found.append("a Docker socket is mentioned (docker.sock)")
    for key in FORBIDDEN_KEYS:
        if re.search(r"(?m)^%s:" % key, code):
            found.append(f"{key} is set")
    if re.search(r"(?m)^network_mode:\s*[\"']?host", code):
        found.append("network_mode: host")
    if re.search(r"(?m)^pid:\s*[\"']?host", code):
        found.append("pid: host")
    if re.search(r"(?m)^type:\s*bind", code):
        found.append("a long-form bind mount")
    if re.search(r"(?m)^(initializeCommand|include):", code):
        found.append("initializeCommand or include is present")

    blocks = service_blocks(lines)
    for name in ("app", "db"):
        if name not in blocks:
            found.append(f"service {name} is missing")
    if "db" in blocks:
        db = blocks["db"]
        if any(c == "ports:" for _, c in db):
            found.append("db has a ports key (published to the host)")
        for item in list_items_under(db, "volumes"):
            source = item.split(":")[0].strip("\"'")
            if source != "pgdata" or not item.endswith(":/var/lib/postgresql/data"):
                found.append(f"db mounts something other than pgdata at the data directory: {item}")
        image = next((c[len("image:"):].strip().strip("\"'") for _, c in db if c.startswith("image:")), "")
        if not re.fullmatch(r"postgres:\d+\.\d+", image):
            found.append(f"db image is not postgres:<major>.<minor> ({image or 'none'})")
        text_db = "\n".join(c for _, c in db)
        if "pg_isready -U" not in text_db or "-d " not in text_db:
            found.append("db has no pg_isready health check with -U and -d")
        for field in ("interval:", "timeout:", "retries:"):
            if field not in text_db:
                found.append(f"db health check has no {field[:-1]}")
    if not any(i == 2 and c == "pgdata:" for i, c in lines):
        found.append("pgdata is not declared under top-level volumes")
    if "app" in blocks:
        app = blocks["app"]
        for item in list_items_under(app, "volumes"):
            if not re.fullmatch(r"\.\.:/workspaces/<folder>", item):
                found.append(f"app mounts something other than the workspace: {item}")
        deps = "\n".join(c for _, c in app)
        if "condition: service_healthy" not in deps or "db:" not in deps:
            found.append("app does not wait for db to be healthy")
    # Any volume entry anywhere that is a host path (leading / . ~ $) other than the app's workspace mount.
    for indent, content in lines:
        if content.startswith("- ") and re.match(r"-\s+[\"']?[/.~$]", content) and ":" in content:
            if content[2:].strip() != "..:/workspaces/<folder>":
                found.append(f"host path mount: {content}")
    return sorted(set(found))


def device_problems(text):
    found = recipe_problems(text)
    data = json.loads(text)
    if data.get("dockerComposeFile") != "compose.yaml":
        found.append("dockerComposeFile is not compose.yaml")
    return found


class FilesTest(unittest.TestCase):
    def test_the_three_files_exist_and_the_json_is_valid(self):
        for p in (COMPOSE, DEVCONTAINER, DOCKERFILE):
            self.assertTrue(p.is_file(), p.name)
        json.loads(DEVCONTAINER.read_text(encoding="utf-8"))

    def test_the_dockerfile_is_one_line_from_the_standard_image(self):
        std = json.loads(STANDARD.read_text(encoding="utf-8"))["image"]
        self.assertEqual(DOCKERFILE.read_text(encoding="utf-8").splitlines(), [f"FROM {std}"])

    def test_the_makefile_json_check_lists_the_variant(self):
        makefile = (KIT.parent / "Makefile").read_text(encoding="utf-8")
        self.assertIn("agent-kit/environments/local-sandbox/compose/devcontainer.json", makefile)


class DevcontainerTest(unittest.TestCase):
    def setUp(self):
        self.text = DEVCONTAINER.read_text(encoding="utf-8")
        self.data = json.loads(self.text)
        self.std = json.loads(STANDARD.read_text(encoding="utf-8"))

    def test_compose_settings(self):
        d = self.data
        self.assertEqual(d["dockerComposeFile"], "compose.yaml")
        self.assertEqual(d["service"], "app")
        self.assertEqual(d["runServices"], ["app", "db"])
        self.assertEqual(d["workspaceFolder"], "/workspaces/<folder>")
        self.assertNotIn("image", d)

    def test_everything_else_equals_the_standard_recipe(self):
        for key in ("features", "remoteEnv", "mounts", "customizations", "postCreateCommand", "name"):
            self.assertEqual(self.data[key], self.std[key], key)
        env = dict(self.data["containerEnv"])
        self.assertEqual(env.pop("DATABASE_URL"), DATABASE_URL)
        self.assertEqual(env, self.std["containerEnv"])

    def test_the_boundary_checks_pass_on_the_reference(self):
        self.assertEqual(device_problems(self.text), [])

    def test_a_drifted_copy_would_differ(self):
        drifted = dict(self.data, features={})
        self.assertNotEqual(drifted["features"], self.std["features"])

    def test_boundary_fixtures_are_flagged(self):
        def variant(**extra):
            return json.dumps(dict(self.data, **extra))
        fixtures = {
            "initializeCommand": variant(initializeCommand="echo hi"),
            "privileged": variant(privileged=True),
            "runArgs": variant(runArgs=["--network=host"]),
            "socket mount": variant(mounts=["source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"]),
            "host path mount": variant(mounts=["source=/home/me,target=/h,type=bind"]),
            "another compose file": variant(dockerComposeFile="other.yaml"),
        }
        for label, text in fixtures.items():
            with self.subTest(label):
                self.assertTrue(device_problems(text), label)


class PlaceholderTest(unittest.TestCase):
    def setUp(self):
        self.compose = COMPOSE.read_text(encoding="utf-8")
        self.device = DEVCONTAINER.read_text(encoding="utf-8")

    def used(self, text):
        return set(re.findall(r"<[a-z_]+>", text))

    def test_the_same_placeholders_appear_in_both_files(self):
        compose_code = "\n".join(c for _, c in code_lines(self.compose))
        for name in PLACEHOLDERS:
            self.assertIn(name, compose_code, name)
            self.assertIn(name, self.device, name)
        self.assertEqual(self.used(compose_code), set(PLACEHOLDERS))
        self.assertEqual(self.used(self.device), set(PLACEHOLDERS))

    def test_database_values_are_placeholders_only(self):
        values = dict(re.findall(r"POSTGRES_(DB|USER|PASSWORD): (\S+)", self.compose))
        self.assertEqual(values, {"DB": "<db_name>", "USER": "<db_user>", "PASSWORD": "<db_password>"})
        self.assertEqual(json.loads(self.device)["containerEnv"]["DATABASE_URL"], DATABASE_URL)

    def test_a_real_looking_value_is_caught(self):
        changed = self.compose.replace("POSTGRES_PASSWORD: <db_password>", "POSTGRES_PASSWORD: hunter2")
        values = dict(re.findall(r"POSTGRES_(DB|USER|PASSWORD): (\S+)", changed))
        self.assertNotEqual(values["PASSWORD"], "<db_password>")

    def test_a_different_folder_placeholder_is_caught(self):
        changed = self.compose.replace("/workspaces/<folder>", "/workspaces/<project>")
        self.assertNotEqual(self.used("\n".join(c for _, c in code_lines(changed))), set(PLACEHOLDERS))

    def test_the_reference_marks_the_postgres_tag_unverified_and_says_how_to_reverse(self):
        self.assertIn("unverified", self.compose)
        self.assertIn("revert these three files and rebuild", self.compose)
        self.assertIn("docker volume rm", self.compose)


class ComposeLimitsTest(unittest.TestCase):
    def setUp(self):
        self.text = COMPOSE.read_text(encoding="utf-8")

    def test_the_reference_has_no_problems(self):
        self.assertEqual(compose_problems(self.text), [])

    def test_the_reference_structure(self):
        blocks = service_blocks(code_lines(self.text))
        self.assertEqual(sorted(blocks), ["app", "db"])
        self.assertEqual(list_items_under(blocks["app"], "volumes"), ["..:/workspaces/<folder>"])
        self.assertEqual(list_items_under(blocks["db"], "volumes"), ["pgdata:/var/lib/postgresql/data"])
        self.assertIn("image: postgres:16.4", self.text)

    def test_comments_that_name_the_forbidden_things_are_not_flagged(self):
        self.assertIn("privileged", self.text)  # the header comment names it
        self.assertNotIn("privileged is set", compose_problems(self.text))

    def add_after(self, anchor, new, indent):
        pad = " " * indent
        return self.text.replace(anchor, anchor + "\n" + pad + new, 1)

    def test_each_refused_fixture_is_flagged(self):
        t = self.text
        fixtures = {
            "docker socket mount": t.replace("      - ..:/workspaces/<folder>\n",
                                             "      - ..:/workspaces/<folder>\n      - /var/run/docker.sock:/var/run/docker.sock\n"),
            "docker.sock anywhere": self.add_after("    command: sleep infinity", "environment:\n      DOCKER_HOST: unix:///var/run/docker.sock", 4),
            "privileged": self.add_after("    command: sleep infinity", "privileged: true", 4),
            "network_mode host": self.add_after("    command: sleep infinity", "network_mode: host", 4),
            "pid host": self.add_after("    command: sleep infinity", "pid: host", 4),
            "cap_add": self.add_after("    command: sleep infinity", "cap_add:\n      - SYS_ADMIN", 4),
            "devices": self.add_after("    command: sleep infinity", "devices:\n      - /dev/fuse", 4),
            "ports under db": self.add_after("    restart: unless-stopped", "ports:\n      - \"5432:5432\"", 4),
            "host path bind in app": t.replace("      - ..:/workspaces/<folder>\n",
                                               "      - ..:/workspaces/<folder>\n      - /home/someone:/data\n"),
            "relative host bind in app": t.replace("      - ..:/workspaces/<folder>\n",
                                                   "      - ..:/workspaces/<folder>\n      - ./data:/data\n"),
            "host path bind in db": t.replace("      - pgdata:/var/lib/postgresql/data\n",
                                              "      - pgdata:/var/lib/postgresql/data\n      - /srv/pg:/backup\n"),
            "workspace mounted elsewhere": t.replace("..:/workspaces/<folder>", "..:/mnt/work"),
            "initializeCommand": t + "initializeCommand: echo hi\n",
            "long-form bind": t.replace("      - ..:/workspaces/<folder>\n", "      - type: bind\n        source: ..\n        target: /w\n"),
            "bare postgres image": t.replace("image: postgres:16.4", "image: postgres"),
            "latest postgres image": t.replace("image: postgres:16.4", "image: postgres:latest"),
            "major-only postgres tag": t.replace("image: postgres:16.4", "image: postgres:16"),
            "no health check": re.sub(r"    healthcheck:\n(?:      .*\n)+", "", t),
            "no wait for health": t.replace("condition: service_healthy", "condition: service_started"),
            "no data volume declared": t.replace("\nvolumes:\n  pgdata:\n", "\n"),
        }
        for label, text in fixtures.items():
            with self.subTest(label):
                self.assertNotEqual(text, t, "the fixture did not change the text")
                self.assertTrue(compose_problems(text), label)


if __name__ == "__main__":
    unittest.main()
