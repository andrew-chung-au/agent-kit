"""Phrase tests for issue #156: the planning procedure and the spec definition of ready.

There is no script behind the gate: the PM and orchestrator read the rule and the human reads
the PM's confirmation, so the wording is what has to stay. Whitespace is normalised.
"""
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"


def flat(path: Path) -> str:
    return " ".join(path.read_text().split())


class PlanningGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = flat(KIT / "procedures" / "planning.md")
        cls.process = flat(KIT / "process.md")
        cls.planning = cls.process[cls.process.index("## Planning"):cls.process.index("## Backlog")]
        cls.backlog = cls.process[cls.process.index("## Backlog"):cls.process.index("## Issue comments")]

    def test_the_procedure_has_the_steps_and_the_seven_checks(self):
        for needle in ("Problem", "Users and journeys", "Stories", "MoSCoW", "non-goals", "Risks",
                       "Definition of ready", "problem and core assumption", "Named users",
                       "end-to-end journey", "acceptance criteria", "scope boundary",
                       "non-goals list", "invariants"):
            self.assertIn(needle, self.doc, needle)

    def test_the_procedure_states_the_escape_hatch_the_not_ready_path_and_the_refusal(self):
        for needle in ("not applicable only if the comment says why", "silence is not an exemption",
                       "No script computes it", "create no implementation issues",
                       "no non-goals and no scope boundary", "never issues"):
            self.assertIn(needle, self.doc, needle)

    def test_it_links_instead_of_duplicating_ownership_and_roadmap_rules(self):
        self.assertIn("human-owned", self.doc)
        self.assertIn("Don't give any of them a second home", self.doc)

    def test_the_procedure_is_short(self):
        self.assertLessEqual(len(self.doc.split()), 400)

    def test_process_links_the_procedure_from_planning(self):
        self.assertIn("procedures/planning.md", self.planning)

    def test_backlog_makes_the_pm_confirm_readiness_and_propose_spec_changes_first(self):
        for needle in ("definition of ready", "procedures/planning.md", "proposes the spec changes first",
                       "creates no implementation issues", "Spec notes", "not by a script"):
            self.assertIn(needle, self.backlog, needle)

    def test_the_pm_role_file_and_readme_and_index_know_it(self):
        self.assertIn("definition of ready", flat(KIT / "team" / "pm.md"))
        self.assertIn("planning.md", flat(KIT / "README.md"))
        index = flat(REPO / "_docs" / "index.md")
        self.assertIn("_docs/decisions/156-planning-gate.md", index)
        self.assertTrue((REPO / "_docs" / "decisions" / "156-planning-gate.md").exists())


if __name__ == "__main__":
    unittest.main()
