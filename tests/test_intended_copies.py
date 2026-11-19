"""Intended copies must match their named source (issue #182).

The copies and their rules are listed in `agent-kit/README.md`, "Intended copies";
this test is the check that `make test` runs for each one. It compares the AGENTS.md
shared block, the pull request template, `CLAUDE.md`, the docs index and the sweep
skill. The role copies differ by design in this repo, so it compares them after the
two named rewrites.
"""
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
ROLE_LAYERS = ((".claude", "claude-code"), (".opencode", "opencode"))
ROLES = ("pm", "qa-engineer", "software-engineer")


def shared_block(path: Path) -> list:
    text = path.read_text(encoding="utf-8")
    start = text.index("## Non-negotiables")
    end = text.index("<!-- SHARED END -->")
    return [line for line in text[start:end].splitlines() if not line.startswith("- <")]


def repo_role(text: str) -> str:
    """Undo the two rewrites this repo makes to a copied role file.

    A copy may name the kit folder `agent-kit/` or `_docs/agent-kit/`, and every copy
    tells the role to read `AGENTS.md` first. The source says neither.
    """
    text = text.replace("_docs/agent-kit/", "agent-kit/")
    text = text.replace("Read `AGENTS.md`, then `", "Read `")
    return text.replace("`, and follow both.", "` and follow it.")


def headings(text: str) -> list:
    return [line for line in text.splitlines() if line.startswith("#")]


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

    def test_the_role_file_copies_match_their_sources(self):
        for folder, layer in ROLE_LAYERS:
            for role in ROLES:
                with self.subTest(copy=f"{folder}/agents/{role}.md"):
                    copy = (REPO / folder / "agents" / f"{role}.md").read_text(encoding="utf-8")
                    source = (KIT / layer / "agents" / f"{role}.md").read_text(encoding="utf-8")
                    self.assertIn(f"Read `_docs/agent-kit/team/{role}.md` and follow it.", source)
                    self.assertIn(f"Read `AGENTS.md`, then `agent-kit/team/{role}.md`, and follow both.",
                                  copy.replace("_docs/agent-kit/", "agent-kit/"))
                    self.assertEqual(repo_role(copy), repo_role(source))

    def test_claude_md_matches_its_template(self):
        self.assertEqual((REPO / "CLAUDE.md").read_bytes(),
                         (KIT / "claude-code" / "CLAUDE.md.template").read_bytes())

    def test_the_claude_sweep_skill_matches_the_opencode_skill(self):
        claude = (KIT / "claude-code" / "skills" / "sweep" / "SKILL.md").read_text(encoding="utf-8")
        opencode = (KIT / "opencode" / "skills" / "sweep" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("disable-model-invocation: true\n", claude)
        self.assertNotIn("disable-model-invocation", opencode)
        self.assertEqual(claude.replace("disable-model-invocation: true\n", ""), opencode)

    def test_the_docs_index_keeps_the_headings_of_its_template(self):
        copy = headings((REPO / "_docs" / "index.md").read_text(encoding="utf-8"))
        source = headings((KIT / "templates" / "docs-index.md").read_text(encoding="utf-8"))
        self.assertEqual(copy, source)


if __name__ == "__main__":
    unittest.main()
