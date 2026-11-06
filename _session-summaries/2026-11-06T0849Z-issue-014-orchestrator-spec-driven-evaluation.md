# Issue #14: Evaluate OpenSpec for spec-driven changes in the agent kit workflow

**Date:** 2026-11-06T08:49Z (UTC)
**Spec version:** none

## What changed and why

Research only, no kit file changed, nothing installed. One record, `_docs/records/2026-11-06T0330Z-measure-spec-driven-frameworks.md`: verified OpenSpec facts with links (licence, install, what `openspec init` writes, delta specs, archive, review), Spec Kit, lower-confidence notes on Kiro, BMAD and Tessl; an overlap map; conflicts with kit rules (including who writes which artifact); feasibility; three options; trade-offs. Recommendation: don't adopt OpenSpec; borrow ideas. Commits `6d31ec0`, `2ac3044`. PR #162, merge `2ce20d1`.

QA FAIL at `6d31ec0`: the issue said to propose follow-ups, not file them, and #159, #160 and #161 had been filed at the human's request; the roles item was half answered; the trial undo missed the binary's schemas folder. Section 8 reworded to propose titles with one-line goals and to say the human later chose to file three; roles and undo fixed. QA PASS at `2ac3044`. The PR said "Refs #14", so the issue is still open for `make issue-close`.

**What I learned:** several sites returned 403; the GitHub API was the reliable way to read OpenSpec's and Spec Kit's own docs.

## Reflection

### Orchestrator

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

none

## Files created or modified

- `_docs/records/2026-11-06T0330Z-measure-spec-driven-frameworks.md` (new)

## Decisions made by the human

- Asked for wider research (OpenSpec and other popular frameworks), recorded in #14.
- Filed the follow-ups as #159, #160 and #161 (items 1 to 3, 4 and 5), each its own issue.
- Section 8: reword (not a waiver).

## Mismatches with the spec or design docs

none

## Commands to validate

**Test (all):** `make test` (1331 tests OK at `2ac3044`)

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- Not re-checked by QA: the change-folder, archive and `/opsx:verify` rows of the overlap map.

## Follow-ups for the next session

- Close #14: post the `Orchestrator:` Close comment, then `make issue-close N=14` from the local sandbox.
