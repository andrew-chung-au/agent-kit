"""Wording checks for agent-kit/procedures/orchestrator-comments.md and its Read-when lines (issue #67).

Limit: this checks the wording of the procedure and the two trigger lines, not what the
orchestrator actually writes on an issue.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KIT = ROOT / "agent-kit"
DOC = KIT / "procedures" / "orchestrator-comments.md"
AGENTS = ROOT / "AGENTS.md"
TEMPLATE = KIT / "templates" / "AGENTS.md.template"

HEADINGS = ("## Claim", "## Release", "## Confirm", "## Close")
PREFIX_RULE = "start with `Orchestrator:`"
POST_RULE = "`make issue-comment N=<n> FILE=.scratch/<name>.md`, never a raw `gh` write"
REST_RULE = "REST fallback for reads; writes still use `make issue-comment`"
READ_WHEN = re.compile(r"(?m)^- Before writing a claim, release, confirm or close comment on an issue -> "
                       r"`(?:_docs/)?agent-kit/procedures/orchestrator-comments\.md`.*$")


def words(text):
    return len(text.split())


def sections(text):
    """Map each layout heading to its body."""
    parts = re.split(r"(?m)^(## .*)$", text)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def check_doc(text):
    """Return a list of problems with the procedure text (empty when it is fine)."""
    problems = []
    if not 1 <= words(text) <= 300:
        problems.append("word cap")
    found = sections(text)
    for heading in HEADINGS:
        if heading not in found:
            problems.append("missing " + heading)
        elif "**Fact:**" not in found[heading] and heading in ("## Claim", "## Release", "## Confirm", "## Close"):
            problems.append("no per-issue facts in " + heading)
    flat = " ".join(text.split())
    if PREFIX_RULE not in flat:
        problems.append("prefix rule")
    if POST_RULE not in flat:
        problems.append("post rule")
    close = " ".join(found.get("## Close", "").split())
    if "Never close without QA PASS" not in close or "approved that closure" not in close:
        problems.append("close do-not")
    claim = " ".join(found.get("## Claim", "").split())
    if "Never name an env file" not in claim:
        problems.append("claim env do-not")
    if REST_RULE not in claim:
        problems.append("claim rest rule")
    return problems


def read_when_line(path):
    match = READ_WHEN.search(path.read_text(encoding="utf-8"))
    return match.group(0) if match else None


class OrchestratorCommentsTest(unittest.TestCase):
    def test_doc_passes_its_own_checks(self):
        self.assertEqual(check_doc(DOC.read_text(encoding="utf-8")), [])

    def test_doc_word_cap(self):
        self.assertLessEqual(words(DOC.read_text(encoding="utf-8")), 300)

    def test_every_layout_lists_fixed_and_fact_fields(self):
        found = sections(DOC.read_text(encoding="utf-8"))
        for heading in HEADINGS:
            self.assertIn("Fixed:", found[heading])
            self.assertIn("**Fact:**", found[heading])

    def test_read_when_lines_exist_with_cap_and_match(self):
        lines = []
        for path in (AGENTS, TEMPLATE):
            line = read_when_line(path)
            self.assertIsNotNone(line, path)
            self.assertLessEqual(words(line), 30, path)
            lines.append(line)
        self.assertEqual(lines[0], lines[1])

    def test_read_when_lines_sit_in_the_read_when_list(self):
        for path in (AGENTS, TEMPLATE):
            text = path.read_text(encoding="utf-8")
            self.assertLess(text.index("## Read when"), text.index("Before writing a claim, release"))

    def test_mutation_missing_layout_fails(self):
        text = DOC.read_text(encoding="utf-8")
        for heading in HEADINGS:
            self.assertTrue(check_doc(text.replace(heading, "## Other")), heading)

    def test_mutation_missing_rules_fail(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertTrue(check_doc(text.replace(PREFIX_RULE, "begin however you like")))
        self.assertTrue(check_doc(text.replace("`make issue-comment", "`gh issue comment")))
        self.assertTrue(check_doc(text.replace("Never close without QA PASS.", "")))
        self.assertTrue(check_doc(text.replace("Never name an env file in a claim.", "")))
        self.assertTrue(check_doc(text.replace(REST_RULE, "the REST fallback")))
        self.assertTrue(check_doc(text.replace("writes still use", "writes may also use")))
        self.assertTrue(check_doc(text + " word" * 300))

    def test_mutation_missing_read_when_line_fails(self):
        for path in (AGENTS, TEMPLATE):
            text = path.read_text(encoding="utf-8")
            line = read_when_line(path)
            self.assertIsNone(READ_WHEN.search(text.replace(line, "")))


if __name__ == "__main__":
    unittest.main()
