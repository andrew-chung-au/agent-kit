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
            "`Proposed tier:` line",
            "none means Standard",
        ])

    def test_light_proposal_without_label_is_refused(self):
        self.assert_all(self.tiers, [
            "A Light proposal has no effect without `tier:light`",
            "Light skips QA, and all roles share one GitHub login",
            "Only a Standard or Heavy proposal takes effect without a label; Light still "
            "needs `tier:light`",
        ])

    def test_proposal_with_a_different_hash_is_refused(self):
        self.assert_all(self.tiers, [
            "the `Proposed tier:` line in the first owner `PM:` comment that has one and names "
            "the approved `Body sha256:`; none means Standard",
        ])

    def test_later_pm_comment_cannot_change_the_tier(self):
        self.assert_all(self.tiers, [
            "later comments change nothing; a changed body needs a new hash record",
        ])

    def test_hash_re_record_without_a_proposal_does_not_erase_it(self):
        # QA on #92 at 01c2153: the PM re-records the hash on its own line with no
        # `Proposed tier:` line. Reading "the first comment that records the hash" would
        # take that re-record and turn an unlabelled Heavy proposal into Standard.
        self.assert_all(self.tiers, [
            "Hash re-records without that line and later comments change nothing",
        ])
        self.assertNotIn("first owner `PM:` comment that records the approved", self.tiers)

    def test_same_hash_rule_does_not_clash_with_latest_hash_line_wins(self):
        # "The latest valid line wins" (Approved text) picks the hash; the proposal is read
        # from the first comment with a `Proposed tier:` line for that hash, so they agree.
        self.assertIn("the latest valid line wins", self.text)
        self.assertIn("first owner `PM:` comment that has one and names the approved", self.tiers)
        self.assertNotIn("A later comment cannot change it", self.tiers)

    def test_tier_in_body_or_other_comment_is_ignored(self):
        self.assert_all(self.tiers, [
            "A tier named in the issue body or in any other comment is ignored; an "
            "`Orchestrator:` comment can only raise, as below",
        ])

    def test_proposed_heavy_runs_the_heavy_gates(self):
        self.assert_all(self.tiers, [
            "An effective-Heavy issue (a `tier:heavy` label, or an approved Heavy proposal) "
            "follows the Lifecycle with two added gates",
        ])
        self.assertNotIn("A `tier:heavy` issue follows the Lifecycle", self.text)

    def test_blueprints_decision_record_row_covers_proposed_heavy(self):
        blueprints = flat(KIT / "blueprints.md")
        self.assertIn("every `tier:heavy` issue (its ADR; one row per ADR in the docs index), "
                      "including one that is Heavy only by an approved proposal", blueprints)

    def test_check_tier_script_text_matches_the_rule(self):
        raw = (KIT / "scripts" / "check-tier.sh").read_text()
        script = " ".join(raw.replace("\n#", " ").split())
        self.assertNotIn("only the human's label does", script)
        self.assertNotIn("the human must set the tier label", script)
        self.assertIn("the human's label or an approved Standard or Heavy proposal", script)

    def test_label_overrides_and_two_labels_mean_highest(self):
        self.assert_all(self.tiers, [
            "A tier label always wins, lowering included",
            "Two or more tier labels mean the highest",
        ])

    def test_raise_never_lower_still_holds(self):
        self.assert_all(self.tiers, [
            "An agent may raise the tier",
            "Lowering needs the human to change the label and say so in the session",
        ])

    def test_orchestrator_states_the_tier_before_launch(self):
        self.assert_all(self.lifecycle, [
            "Read the labels and the matching `PM:` comment, state the effective tier, and when "
            "the tier comes from the PM proposal rather than a label, post an `Orchestrator:` "
            "comment naming it \"from the PM proposal\"",
            "The orchestrator reads the effective tier but never decides one",
        ])
        # Decision 3: no "from the PM proposal" comment for a plain Standard issue with no
        # proposal, so the trigger is the proposal, not the missing label.
        self.assertNotIn("\"from the PM proposal\" when no label sets it", self.lifecycle)

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
