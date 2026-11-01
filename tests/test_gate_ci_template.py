"""Pins the properties of agent-kit/templates/ci-verify.yml.template (issue #1).

The template is the kit's pattern for a CI backstop that runs the weakened-test
check against a real base. This test covers the template, not the repo's own
workflow (only the human changes that). Comments are ignored, because the
template's comments mention secrets in order to forbid them.
"""
from __future__ import annotations

import re
import unittest

from kit_repo import KIT

TEMPLATE = KIT / "templates" / "ci-verify.yml.template"
BASE_RUN = ("make verify BASE=\"${{ github.event_name == 'pull_request' && "
            "format('origin/{0}', github.base_ref) || github.event.before }}\"")


def code_lines(text):
    return [re.sub(r"\s+#.*$", "", ln) for ln in text.splitlines() if not ln.lstrip().startswith("#")]


def problems(text):
    code = "\n".join(code_lines(text))
    found = []
    if not re.search(r"^\s+fetch-depth: 0\s*$", code, re.M):
        found.append("checkout has no fetch-depth: 0")
    if BASE_RUN not in code:
        found.append("verify step does not pass the template's BASE expression")
    if not re.search(r"^permissions:\n  contents: read\s*$", code, re.M):
        found.append("permissions is not exactly contents: read")
    if re.search(r"(:\s*write\b|write-all)", code):
        found.append("a write permission is present")
    if "secrets." in code:
        found.append("a secrets. reference is present")
    return found


class CiTemplateTest(unittest.TestCase):
    def setUp(self):
        self.text = TEMPLATE.read_text(encoding="utf-8")

    def test_the_template_keeps_its_properties(self):
        self.assertEqual(problems(self.text), [])

    def test_the_template_triggers_on_push_and_pull_request(self):
        code = "\n".join(code_lines(self.text))
        self.assertRegex(code, r"(?m)^on:\n  push:")
        self.assertRegex(code, r"(?m)^  pull_request:")

    def test_a_missing_fetch_depth_is_refused(self):
        self.assertIn("checkout has no fetch-depth: 0", problems(self.text.replace("fetch-depth: 0", "fetch-depth: 1")))

    def test_a_missing_base_is_refused(self):
        self.assertTrue(problems(self.text.replace("BASE=", "NOBASE=")))

    def test_a_wider_permission_is_refused(self):
        wider = self.text.replace("contents: read", "contents: write")
        found = problems(wider)
        self.assertIn("permissions is not exactly contents: read", found)
        self.assertIn("a write permission is present", found)

    def test_a_secrets_reference_is_refused(self):
        bad = self.text + "      - run: echo ${{ secrets.TOKEN }}\n"
        self.assertIn("a secrets. reference is present", problems(bad))

    def test_a_secrets_mention_in_a_comment_is_not_a_reference(self):
        self.assertIn("secrets.", self.text)  # the template's own comment
        self.assertNotIn("a secrets. reference is present", problems(self.text))


if __name__ == "__main__":
    unittest.main()
