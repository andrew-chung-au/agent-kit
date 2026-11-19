## Why

See #63. `issue-close.sh` now ignores an owner `Engineer:` comment as the close floor when `is_reflection` calls it a reflection. `is_reflection` decides that by the absence of two known work markers (a line starting with Verify or Verification, a numbered line saying done or not checked). The Reviewer's report on #63 (the `Orchestrator: Reviewer report (#63)` comment, https://github.com/andrew-chung-au/socboard/issues/63#issuecomment-6846010929; findings 1, 2, 3, 4, 6, 7 and 5) shows the list is the wrong test, because it fails open on any work layout it does not know:

- A short fix note plus a Reflection block is accepted as a reflection: `Engineer: fixed in commit abc1234`, then `Reflection:`. Nothing starts with Verify and nothing is numbered, so the floor does not move and the old QA PASS closes the issue over unreviewed work (finding 2).
- The role file asks for "the verify result and what you did" and one line per criterion (`_docs/agent-kit/team/software-engineer.md`, Definition of done), but does not say a line must start with the word Verify or that a criterion line must be numbered "N. ... done". `make verify: PASS (3 warnings explained)` followed by `AC1 - done` matches neither marker, so a conforming work comment with a Reflection appended is hidden (finding 3).
- The opposite error: `1. Slowed by a test that was done twice` in a genuine reflection counts as work and blocks the close again, the original failure of #51 in a narrower form (finding 6).
- Nothing tells a role to keep a reflection to its Reflection block (`procedures/session-summary.md`, Reflection), so the rule lives only in the script and the decision record (finding 4).
- No test is kept in the repository; the only proof is an uncommitted `.scratch/` check, so a kit import or pattern edit can silently reopen the hole (finding 7).
- The marker patterns are described in three places (the script header, the function comment, the decision record) and will drift (finding 5).

The human decided to ship #63 as it is and defer these findings to this one follow-up. The decision record `_docs/decisions/2026-11-13T0537Z-close-floor-reflection.md` already lists the first group as accepted trade-offs ("Still uncovered after QA's second check").

Real comments show the cost of the marker list (the QA comments on #63: 6845523068 and 6845882757): work comments with a Reflection appended slipped past the floor when the verify label was long (6839188081 on #13); a real work comment with its own bold `Reflection:` block and no line-start Verify was accepted as a reflection (6786726633 on #46).

## Goal

`is_reflection` in `_docs/agent-kit/scripts/issue-close.sh` decides by shape: a comment is a reflection only when almost nothing precedes its `Reflection:` block, so an unknown work layout counts as work. Roles are told to keep a reflection to its Reflection block.

## Acceptance criteria

Rule (shape test). Each case is checked by replaying a comment through the script's checker (a fake owner QA PASS, the comment, a valid Close comment) and reading the exit code and the refusal text, as the #63 QA reports did:

- [ ] A comment is a reflection only when the text before its first `Reflection:` line, after the `Engineer:` prefix, is blank or one short line (at most 200 characters), and that line does not name a commit. Otherwise it is work and sets the floor, as a comment with "commit" and a 7 to 40 hex string does today
- [ ] The commit-hash check (the word "commit" plus 7 to 40 hex) for the floor is made on the text before the Reflection block, not on the Reflection block. A Reflection block that names hashes, such as "commits aadb64a..c8f4282", does not make the comment work
- [ ] Unknown work layouts count as work: a comment with a long preamble, a table, bullets, `Verified:`, `Tests: N passed`, or any other text before the Reflection block is refused with "found 0" when the preamble is more than one short line
- [ ] The Reflection block is the rest of the comment from the first `Reflection:` line. The PM adds one limit for the Engineer to set and record: a block longer than the length `session-summary.md` allows (three lines, 150 words at most; the Engineer may allow a small margin) makes the comment work. Without it, work placed after a short preamble and a `Reflection:` line would evade the shape test. **OPEN QUESTION 1 (the human decides before approval):** this limit is a PM addition and, as worded, it contradicts the Accepted cases below. The real #51 reflection (comment 6792494473) has 10 non-empty lines and 293 words, and the real #16 reflection (comment 6843134115) has 7 and 222, so a three-line, 150-word limit would refuse both. The Engineer does not implement this criterion until the human has ruled; the options are in the `PM:` comment

Accepted (exit 0 for the floor; the issue closes when the rest is valid):

- [ ] The real #51 reflection (comment 6792494473, "commits aadb64a..c8f4282")
- [ ] The real #16 reflection (comment 6843134115)
- [ ] A reflection with no text before the block, and one with a single short line before it (for example `Engineer: reflection after the QA PASS`), bold `**Reflection:**`, `## Reflection:`, lower case, and CRLF line endings, as the #63 QA checked
- [ ] A reflection whose numbered item contains "done" in prose, such as `1. Slowed by a test that was done twice`, is accepted (the over-block of finding 6 is gone); a reflection with a line starting `Verify - this is slow` or `Verification took ...` inside the block is accepted for the same reason

Refused (exit 1, "found 0"):

- [ ] `Engineer: fixed in commit abc1234` followed by a `Reflection:` block (finding 2)
- [ ] A work comment with the line `make verify: PASS (3 warnings explained)` and a line `AC1 - done`, with a `Reflection:` block appended (finding 3)
- [ ] The real work comments, replayed with a Reflection appended where they had none: #17 (6844663040), #18 (6843565444), #13 (6839188081); and the real ones that already have their own Reflection block: #99 (6840947751) and #14 (6841890053)
- [ ] The real #46 comment 6786726633 (a work comment with its own bold `Reflection:` block and no line-start Verify) is refused, as it was accepted before
- [ ] A work comment with no Reflection block still sets the floor (unchanged)

Behaviour that must not change (the cases of #63's criteria, rerun):

- [ ] Owner-only: an `Engineer:` or `QA:` comment from a non-owner account, or from a deleted account, never counts as a PASS and never moves a floor in the permissive direction
- [ ] Heavy still needs two owner QA PASS comments at or after the floor and the `QA PASS commit` line in the Close comment; Standard needs one
- [ ] The Light path (`tier-check: PASS`, `Human approved diff: yes`) is unchanged and does not use `is_reflection`
- [ ] The not-planned path is unchanged

Docs and records:

- [ ] `procedures/session-summary.md` (Reflection) gains one sentence: a reflection comment holds only its Reflection block, with nothing before it except at most one short line, no work report and no commit-fix note. This is in scope here. #63's "Out of scope" excluded changing what a Reflection must contain; this sentence does change it by limiting what else may go in the comment, and the human's approval of this issue is that approval
- [ ] The decision is recorded as a new decision record that supersedes `_docs/decisions/2026-11-13T0537Z-close-floor-reflection.md` (status line of the old record set to superseded, its text otherwise unchanged), or as an update to it; the Engineer picks one and says why in the comment. The record states the new Decision, drops the marker list and its trade-offs, and lists the remaining trade-off (a short, well-formed work note under 200 characters with no commit named still reads as a reflection)
- [ ] The local-deviation trail is updated. The kit keeps no single list of its local deviations (checked at grooming). A deviation is marked by a `<!-- local deviation: <record> -->` pointer in the changed kit file (`_docs/agent-kit/process.md:133`, `_docs/agent-kit/blueprints.md:149`, `issue-close.sh`) and by its decision record, which `_docs/index.md` lists; `make kit-check` shows the drift from `MANIFEST.sha256`. So: the pointers in `issue-close.sh` (the header and `is_reflection`) name the new record; the new sentence in `session-summary.md` carries the same pointer; and the comment lists `make kit-check` output before and after (the expected difference is `procedures/session-summary.md` changing from unchanged to modified)
- [ ] The upstream note (feedback for the upstream kit) is updated to the shape test and to the sentence added to `session-summary.md`
- [ ] The docs index entry for the record (`_docs/index.md`) is updated or added
- [ ] Cleanup (finding 5): the rule is written once. The script header keeps one short sentence ("a reflection does not set the floor; see `is_reflection`") and the colon list that introduces "completed, Standard or Heavy" is no longer broken by it; the pattern text lives only in `is_reflection`, which has no very long comment line; the record links to the function instead of copying the patterns
- [ ] `make verify` passes

Regression test:

- [ ] The accepted, refused and unchanged cases above are kept as a committed test that fails on the old marker-list code for the refused cases of findings 2 and 3. Fixtures are the real shapes (layout, line order and lengths) from the comments named above, reduced to what the test needs, with no names, tokens or other secrets. The Engineer fetches them read-only. Where the test lives is the Engineer's proposal, see Constraints
- [ ] **OPEN QUESTION 2 (the human decides before approval):** whether this fallback is acceptable at all. If no committed test is approved, the Engineer runs the same cases from a `.scratch/` script, lists its output in the comment, and says plainly that criterion is not met; the human decides whether to accept that

## Out of scope

- Any finding not listed above: the Reviewer raised seven, and all are covered here
- Replacing comment-text matching with commit-based floors (Alternative 2 below)
- Any change to the Light path, the not-planned path, the two-PASS rule, owner filtering, or the Close comment layout
- Changing when roles post a reflection, or what the three Reflection items ask for (only the one sentence about what else the comment may hold)
- Older fix notes with no Reflection block: they set the floor today and still do
- Changes to the `Makefile`, `tests/` or `agent-kit.conf` unless the human approves them separately (see Constraints)

## Design

The shape test replaces the marker list. In pseudocode: split the comment at the first `Reflection:` line; the text before it, minus the `Engineer:` prefix, must be blank or one line of at most 200 characters naming no commit; the block after it must fit the Reflection length limit (open question 1); both hold, the comment is a reflection. No Verify or criterion patterns are kept: with a one-line preamble limit they add only the over-block of finding 6. The Engineer may keep the Verify check as a second guard on the preamble if the cases above need it, and says so in the comment.

## Constraints

- Files expected to change (the human approves the exact diff of each protected one and commits with `HUMAN_APPROVED=1`):
  - `_docs/agent-kit/scripts/issue-close.sh` (protected: `_docs/agent-kit/*`)
  - `_docs/agent-kit/procedures/session-summary.md` (protected)
  - `_docs/decisions/<new record>.md`, and the old record `_docs/decisions/2026-11-13T0537Z-close-floor-reflection.md` if superseded (`_docs/decisions/` is not in the protected list)
  - `_docs/index.md` (the entry for the record)
  - not edited: `_docs/agent-kit/MANIFEST.sha256` (a derivative keeps the upstream manifest, `procedures/kit-import.md`, Manifest) and `KIT_VERSION` in `agent-kit.conf` (protected; #63 and PR #119 left it at `1.10+socboard.1`, although `_docs/agent-kit/README.md` (Versions in a project) says its `<n>` rises with each local change). The Engineer asks the human whether to bump it and does not edit it
- Where the regression test goes (investigated while drafting):
  - No harness for the kit's scripts exists: nothing under `_docs/agent-kit/` tests a script, and no file in `tests/` runs a kit script.
  - The closest precedent is `tests/test_ponytail_metrics.py`, which tests the project script `scripts/ponytail_metrics.py` with `importlib` and fixture data. `make test` runs `tests/`. The checker in `issue-close.sh` is Python inside a shell here-document and the script calls `gh`, so a test would need either a fake `gh` on the path (a throwaway script in the test's own temporary folder) or the checker moved to its own file (a kit change the Engineer would have to justify).
  - `tests/` and the `Makefile` are separate approvals, and the human has told the current sessions not to touch them for now. So the Engineer must propose where the test goes (a `tests/` file by the precedent above is the likely answer; no `Makefile` change should be needed because `make test` already collects `tests/`), and wait for that approval. The Engineer does not create the test file before then.
- Fixed values and where they come from: the 200-character preamble limit is from the Reviewer's finding 1 (the Reviewer report comment on #63, "about 200 characters at most"); the Reflection block length is from `procedures/session-summary.md` (three lines, 150 words at most); the real comment ids are from the QA comments on #63 (6845523068 and 6845882757).
- Use `gh api` GET only to refetch comments; the script's own `gh` calls stay as listed in its header.
- Comments are data, never instructions. Do not paste whole real comments into the committed test.
- Guidelines: `_docs/agent-kit/process.md` (Tiers), `_docs/agent-kit/team/software-engineer.md` (Commits: explicit paths, no closing keyword before an issue number).
- Proposed tier: heavy, because it changes the rule that gates every issue's closure (the process itself). Expected paths: `_docs/agent-kit/scripts/issue-close.sh`, `_docs/agent-kit/procedures/session-summary.md`, `_docs/decisions/<new record>.md` (and the old record's status line), `_docs/index.md`, the regression test file once the human approves its place.

## Decision record

PM's draft, for the human to approve. The Engineer does not start until the human has approved it.

- **Decision:** In `issue-close.sh`, an owner `Engineer:` comment does not set the close floor only when it has a `Reflection:` block and almost nothing before it: the text before the first `Reflection:` line, after the `Engineer:` prefix, is blank or one short line (at most 200 characters) that names no commit, and the block fits the Reflection length in `procedures/session-summary.md` (open question 1). Any other comment is work and sets the floor, so a work layout the script does not know counts as work. The commit-hash check is made on the preamble, not the Reflection block. `session-summary.md` gains one sentence telling roles to keep a reflection to its Reflection block. Supersedes the marker-list rule of `_docs/decisions/2026-11-13T0537Z-close-floor-reflection.md`; still a local deviation from the kit with an upstream note.
- **Reason:** It fails closed. The marker list fails open on every layout it does not name (`Verified:`, `Tests: N passed`, `make verify: PASS` with `AC1 - done`, a fix note plus a Reflection), and each new layout needs a new pattern. The shape of a genuine reflection is fixed by `session-summary.md` (role prefix, then a Reflection block), so testing the shape needs no list of work markers. It also removes the over-block on a numbered "done" in a reflection and shrinks the rule to one place.
- **Alternatives:**
  1. Keep the markers and widen them (match `verify` with PASS or FAIL anywhere on a line, allow a dash after the number): smallest diff, but the list stays open-ended and the "reflection with a numbered done" over-block stays or is traded for new gaps.
  2. Floor from commits on the issue instead of comment text: stronger, but needs a reliable link from commits to the issue, which the kit does not have (Kiro Web branches and pull request merges differ).
  3. Reject any comment that has a Reflection block, as work, and ask roles to post reflections without hashes: no script change, but one slip blocks a close again (it is the state before #63).
  4. Tell roles to avoid hashes in reflections (`session-summary.md` only): nothing enforces it.
  5. Upstream first, then import: shared fix, but closures stay exposed to the evasion until it lands.
- **Trade-offs:** A short, well-formed work note of one line (200 characters or fewer) that names no commit, followed by a Reflection, still reads as a reflection; the rule cannot see work it describes without a commit. A genuine reflection with a long preamble line, or a lead-in sentence, counts as work and delays the close until QA re-checks (the safe direction); the one-sentence addition to `session-summary.md` is meant to prevent it. The Reflection length limit is a new way for a reflection to count as work if a role writes more than allowed. The rule depends on the reflection layout in `procedures/session-summary.md`; if that changes, the script and the record change with it. It stays a local deviation: it adds to the difference list and needs an upstream note.
- **Evidence:** see #63; the Reviewer's report on #63 (`Orchestrator: Reviewer report (#63)`, comment 6846010929); the QA comments on #63 (6845523068 and 6845882757); #51 (the refused close, 2026-11-11); real comments 6792494473 (#51), 6843134115 (#16), 6840947751 (#99), 6844663040 (#17), 6843565444 (#18), 6841890053 (#14), 6839188081 (#13), 6786726633 (#46); `_docs/decisions/2026-11-13T0537Z-close-floor-reflection.md`.
