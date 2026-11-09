"""Intended copies must match their named source (issue #182).

Some text is copied on purpose. Each copy has one source; this test fails when they drift.

| Copy | Source | Rule |
|---|---|---|
| `.github/pull_request_template.md` | `agent-kit/templates/github/pull_request_template.md` | byte for byte |
| the shared block of `AGENTS.md` (from `## Non-negotiables` to `SHARED END`) | `agent-kit/templates/AGENTS.md.template` | equal, except the template's placeholder lines (`- <...>`), which a project deletes or fills |

Not checked, on purpose: `.claude/agents/*` and `.opencode/agents/*` in this repo are tailored copies of
`agent-kit/claude-code/agents/*` and `agent-kit/opencode/agents/*` (they differ today); in a project,
`make kit-check` reports their drift from `installed-files.txt`. `_docs/index.md` and `CLAUDE.md` are
tailored from their templates.
"""
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"


def shared_block(path: Path) -> list:
    text = path.read_text(encoding="utf-8")
    start = text.index("## Non-negotiables")
    end = text.index("<!-- SHARED END -->")
    return [line for line in text[start:end].splitlines() if not line.startswith("- <")]


class IntendedCopiesTest(unittest.TestCase):
    def test_the_pull_request_template_matches_its_source(self):
        copy = (REPO / ".github" / "pull_request_template.md").read_bytes()
        source = (KIT / "templates" / "github" / "pull_request_template.md").read_bytes()
        self.assertEqual(copy, source)

    def test_the_agents_md_shared_block_matches_the_template(self):
        self.assertEqual(shared_block(REPO / "AGENTS.md"),
                         shared_block(KIT / "templates" / "AGENTS.md.template"))

    def test_the_placeholder_lines_are_the_only_difference_skipped(self):
        lines = shared_block(KIT / "templates" / "AGENTS.md.template")
        self.assertFalse([line for line in lines if line.startswith("- <")])
        self.assertTrue(any(line.startswith("- Issue titles") for line in lines))


if __name__ == "__main__":
    unittest.main()
