"""Tests for the heading-anchor check in agent-kit/scripts/check-claims.py (issue #34).

A kit path span like `team/pm.md#commits` must name an existing file and a
heading whose GitHub-style slug is the anchor. Other spans with `#` are skipped.
"""
from __future__ import annotations

import unittest

from test_claims import KitCase, claims


class SlugTest(unittest.TestCase):
    def slugs(self, text):
        return claims.heading_slugs(text)

    def test_slug_is_lowercase_hyphenated_without_punctuation(self):
        self.assertEqual(self.slugs("## Commits and pushes\n"), {"commits-and-pushes"})
        self.assertEqual(self.slugs("### What's `make` for? (A-B)\n"), {"whats-make-for-a-b"})

    def test_duplicates_get_a_numbered_suffix(self):
        self.assertEqual(self.slugs("## Notes\n## Notes\n"), {"notes", "notes-1"})

    def test_headings_in_fenced_code_are_ignored(self):
        self.assertEqual(self.slugs("```\n# not a heading\n```\n# Real\n"), {"real"})


class AnchorClaimsTest(KitCase):
    def setUp(self):
        super().setUp()
        self.write("team/engineer.md", "# Engineer\n\n## Commits\n\nText.\n\n## Commits and pushes\n")

    def test_valid_anchor_passes(self):
        self.write("team/pm.md", "See `team/engineer.md#commits` and `_docs/agent-kit/team/engineer.md#commits-and-pushes`.\n")
        self.assert_passes()

    def test_anchor_in_another_file_passes(self):
        self.write("team/pm.md", "See `team/engineer.md#commits` and `procedures/verify.md#verify`.\n")
        self.write("procedures/verify.md", "# Verify\n")
        self.assert_passes()

    def test_missing_file_fails_with_doc_line_and_claim(self):
        self.write("team/pm.md", "One.\nSee `team/nope.md#commits`.\n")
        self.assert_fails("agent-kit/team/pm.md:2: kit path `team/nope.md#commits` does not exist")

    def test_missing_heading_fails_with_doc_line_and_claim(self):
        self.write("team/pm.md", "One.\nTwo.\nSee `team/engineer.md#nope`.\n")
        self.assert_fails("agent-kit/team/pm.md:3: kit path `team/engineer.md#nope` has no heading with anchor `#nope`")

    def test_link_without_anchor_behaves_as_before(self):
        self.write("team/pm.md", "See `team/engineer.md` and `team/missing.md`.\n")
        self.assert_fails("kit path `team/missing.md` does not exist")
        self.write("team/pm.md", "See `team/engineer.md`.\n")
        self.assert_passes()

    def test_hash_in_urls_placeholders_and_other_spans_is_skipped(self):
        spans = ["agent-kit/https://x.md#nope", "team/<role>.md#nope", "team/*.md#nope",
                 "team/engineer.md#", "scripts/verify.sh#nope", "team/a=b.md#nope",
                 "team/two words.md#nope", "team/engineer.md#a#b", "team/engineer.md#...",
                 "nope.md#commits", "team/$X.md#nope"]
        self.write("team/pm.md", "".join(f"`{s}`\n" for s in spans))
        self.assert_passes()

    def test_anchor_in_prose_is_not_checked(self):
        self.write("team/pm.md", "See team/engineer.md#nope in prose.\n")
        self.assert_passes()


if __name__ == "__main__":
    unittest.main()
