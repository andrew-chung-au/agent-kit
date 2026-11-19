# Issue #63: issue-close ignores reflection-only Engineer comments

**Date:** 2026-11-13T06:43Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Heavy (from the PM proposal; the only label was `approved`). Kiro Web worked #63 on branch `issue-63-close-floor-reflection` (PR #119) while other sessions worked #19, #20 and the Makefile issues, a one-time human exception to `delivery-pace.md` item 4. Ponytail was on for the Engineer.

- **The bug:** `make issue-close` took as its floor any owner `Engineer:` comment that said "commit" and held a hex string. A post-PASS reflection that named a commit moved the floor past the QA PASS, so the close was refused (#51, then #16).
- **The change (`_docs/agent-kit/scripts/issue-close.sh`, protected):** a new `is_reflection` function. An owner `Engineer:` comment does not set the floor when it has a `Reflection:` line and has neither a line starting with Verify or Verification nor a numbered criterion line saying done or not checked. Owner-only handling, the two-PASS rule for Heavy, the `QA PASS commit` check, the Light path and the not-planned path are unchanged.
- **Record:** `_docs/decisions/2026-11-13T0537Z-close-floor-reflection.md` (a local deviation from the kit, with an upstream note) and its row in `_docs/index.md`.
- **Commits:** 28a3c8d (record and index row), 54be201 (script, round 1), a67da41 (record), c869592 (script, round 2), 72107f2 (record), 8fbb56b (script, round 3). Each protected script commit was made with `HUMAN_APPROVED=1` after the human approved the exact diff.
- **QA took four runs.**
  - The first run failed: the work test needed both markers (`verify and criteria`), and the issue's Design said either one. Real comments from #99, #17 and #18 slipped through with a Reflection appended.
  - The second run failed: the Verify pattern allowed only 20 characters between the word and the colon, so real comment 6839188081 on #13 slipped through.
  - The third run passed at 8fbb56b.
  - The Heavy second launch was a fresh subagent that read only the three changed files and a body-only extract, and it passed at 8fbb56b.
- **CI at 8fbb56b:** run 43377785253 (pull request) and 43377778599 (push) succeeded. 1485 Python tests and 157 frontend tests passed, with `VERIFY: PASS`.
- **Reviewer:** seven findings, posted as `Orchestrator: Reviewer report (#63)`. The human chose to apply none and defer them to one follow-up, #122. The core finding is that the marker list fails open on any work layout it does not know.
- **`main` moved** from 0a55fe1 to eac622e during the review. None of #63's three files changed there, and a dry-run merge was clean.

**What I learned:** a rule that decides "reflection" by the absence of known work markers fails open, and each QA run found another layout it missed. Testing the comment's shape (almost nothing before the Reflection block) fails closed. That is now #122.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Ponytail

The Engineer kept the script change to one function and one filter line. The Reviewer found about 10 lines of duplicated rule text (finding 5) and one design-level problem, the fail-open marker list (findings 1 to 3). The human deferred both to #122.

## Launch usage

Active time and tool uses: unknown, because Kiro Web reports neither. Launches: PM 1 (the follow-up draft); Engineer 3 (implementation, then two QA fixes); QA 4 (FAIL, FAIL, PASS, then the second Heavy launch PASS); Reviewer 1.

## Files created or modified

- `_docs/agent-kit/scripts/issue-close.sh` (protected)
- `_docs/decisions/2026-11-13T0537Z-close-floor-reflection.md` (new)
- `_docs/index.md` (one row)
- this file

No `Makefile`, `AGENTS.md`, `socboard/` or `tests/` file was touched. `procedures/session-summary.md` did not need a change.

## Decisions made by the human

- Approved the exact diff of `issue-close.sh` three times (rounds 1, 2 and 3), each before its `HUMAN_APPROVED=1` commit.
- At the decision point: apply none of the seven Reviewer findings in #63; file one follow-up (#122) for findings 1 to 4, 6 and 7, with finding 5 folded in; merge #119 as it stands.
- Kept the widened Reflection pattern (bold, quote, heading, any case) when offered the chance to narrow it.

## Mismatches with the spec or design docs

None.

## Commands to validate

- **Verify:** `make verify` (CI on PR #119: pass at 8fbb56b).
- **Kit check:** `make kit-check` reports the kit as a derivative; QA noted drift in other files that predates this branch.

## Proposed AGENTS.md changes

none.

## Temporary changes

none. `make clean-scratch` ran.

## Interruptions

none. Two QA runs failed on substance, not by stopping early.

## Unrelated problems noticed but not fixed

- The Engineer's report counted 44 check cases; the script prints 41 `ok` cases and 8 timing lines. Not material.
- `make issue-body` (#73) has not landed, so the blind second QA launch read the body through a `gh api` extract.
- The search tool does not index `_docs/`; roles had to use `grep` through the shell there.
- `.kiro/agents/reviewer.json` is not a listed sub-agent in Kiro Web, so the Reviewer ran as a general task held read-only by its launch message.

## Follow-ups for the next session

1. **#122** (filed, not groomed): make the close floor test the shape of a reflection. It needs grooming, the human's approval of its `## Decision record` and a PM hash record before the Engineer starts. It adds a criterion beyond the Reviewer's findings (a Reflection block longer than three lines or 150 words counts as work), and the human should confirm it.
2. **Roadmap placement:** #122 is not yet in `_docs/planning/roadmap-1-core.md`, because the human limited this session's files. Proposed supporting-list line: "#122 Make the close floor test the shape of a reflection, not a marker list (follow-up to #63). After #63 merges and before the next Standard or Heavy closure that has an Engineer reflection; same protected-file sitting as #73 and #71 if they are still open. The regression test waits for the separate approval of a place in `tests/`."
3. After #63 merges: the Close comment, then `make issue-close N=63`. Once #63 is on `main`, Reflection comments may carry commit hashes again.
