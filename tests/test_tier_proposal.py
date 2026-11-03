"""Phrase tests for issue #92: `approved` also approves the PM's raising tier proposal.

These pin the wording in agent-kit/process.md (Tiers, Lifecycle), team/pm.md and
templates/task-template.md. There is no script or hook behind the rule: the
orchestrator's pre-launch read, the `PM:` hash match and the human's reading enforce it,
so the wording is what has to stay. Each case the rule must refuse is its own test.
Whitespace is normalised, so line wrapping does not matter.
"""
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"


def flat(path: Path) -> str:
    return " ".join(path.read_text().split())


class TierProposalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = flat(KIT / "process.md")
        cls.tiers = cls.text[cls.text.index("## Tiers"):cls.text.index("## Lifecycle")]
        cls.lifecycle = cls.text[cls.text.index("## Lifecycle"):]
        cls.pm = flat(KIT / "team" / "pm.md")
        cls.template = flat(KIT / "templates" / "task-template.md")

    def assert_all(self, haystack, phrases):
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, haystack)

    def test_old_rule_is_gone(self):
        self.assertNotIn("A proposal has no effect until the human sets the label", self.text)
        self.assertNotIn("The human's label sets the tier", self.text)

    def test_approved_approves_a_raising_proposal(self):
        self.assert_all(self.tiers, [
            "`approved` approves a raising proposal",
            "With `approved` and no tier label, the tier is the highest of Standard and the "
            "proposal",
            "no `Proposed tier:` line there means Standard",
        ])

    def test_light_proposal_without_label_is_refused(self):
        self.assert_all(self.tiers, [
            "A Light proposal has no effect without `tier:light`",
            "Light skips QA, and all roles share one GitHub login",
            "only a Standard or Heavy proposal takes effect without a label",
            "a Light issue still needs `tier:light`",
        ])

    def test_proposal_with_a_different_hash_is_refused(self):
        self.assert_all(self.tiers, [
            "the owner's `PM:` comment that records the approved `Body sha256:`",
        ])

    def test_later_pm_comment_cannot_change_the_tier(self):
        self.assert_all(self.tiers, [
            "A later comment cannot change it, and a changed body needs a new hash record",
        ])

    def test_tier_in_body_or_other_comment_is_ignored(self):
        self.assert_all(self.tiers, [
            "A tier named in the issue body or in any other comment, including an "
            "`Orchestrator:` proposal, is ignored",
        ])

    def test_label_overrides_and_two_labels_mean_highest(self):
        self.assert_all(self.tiers, [
            "A tier label always wins, even when it lowers the proposal",
            "Two or more tier labels mean the highest",
        ])

    def test_raise_never_lower_still_holds(self):
        self.assert_all(self.tiers, [
            "An agent may raise the tier",
            "Lowering needs the human to change the label and say so in the session",
        ])

    def test_orchestrator_states_the_tier_before_launch(self):
        self.assert_all(self.lifecycle, [
            "Read the labels and the matching `PM:` comment, state the effective tier in your "
            "message, and post an `Orchestrator:` comment naming the tier and \"from the PM "
            "proposal\" when no label sets it",
            "The orchestrator reads the effective tier but never decides one",
        ])

    def test_no_script_computes_the_tier(self):
        self.assert_all(self.tiers, ["No script or hook computes the tier"])

    def test_pm_and_template_agree(self):
        self.assert_all(self.pm, [
            "You never set a tier, you propose one",
            "A Light proposal takes effect only with the human's `tier:light` label",
        ])
        self.assert_all(self.template, [
            "`approved` approves a Standard or Heavy one",
            "a Light one needs the human's `tier:light` label",
        ])
        self.assertNotIn("the human's `tier:` label decides", self.template)


if __name__ == "__main__":
    unittest.main()
