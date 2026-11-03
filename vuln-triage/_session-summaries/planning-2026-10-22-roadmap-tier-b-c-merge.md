# Planning 2026-10-22: merge the Tier B/C roadmap draft into the roadmap

**Date:** 2026-10-22
**Spec version:** 97893c1

## What changed and why

The human asked to review and merge `_docs/roadmap-tiers-b-c.md` into
`_docs/roadmap.md`, then delete the draft. Step 17 was one row for 8 criteria;
it now points at milestones B1-B6 (Tier B) and C1-C8 (Tier C), with task-number
mapping, human prerequisites, the AWS-slow ordering, and B/C score checkpoints.
Decisions D1-D7 moved into "Open decisions" as rows 5-11. A stray `=======`
conflict marker left at the end of the previous check-in (merge `de0c25d`) was
removed.

The merge follows the draft's own rule: `_docs/tasks.md` wins on task
boundaries, so the draft's splits of tasks 15, 17, 21 and 24 are checkpoint
groupings, not redefinitions; D7 is the proposal to split tasks 21 and 24 when
their issues are filed.

## Files created or modified

- `_docs/roadmap.md`: step 17 row, new "Tier B and Tier C milestones (step 17)"
  section, open decisions 5-11, B/C score checkpoints, one check-in line.
- `_docs/roadmap-tiers-b-c.md`: deleted after the merge (the human's instruction).
- `_docs/ai-usage-log.md`: this session's entry.
- `_session-summaries/planning-2026-10-22-roadmap-tier-b-c-merge.md`: this file.

## Decisions made by the human

- Merge the draft into the roadmap and delete the draft.
- The seven draft decisions D1-D7 were carried over as open; none was answered
  in this session.

## Mismatches with the spec or design docs

None. The draft's sources (`_docs/rubric.md`, `_docs/architecture.md`,
`_docs/testing.md`, `_docs/tasks.md`) were checked; the rubric's 24-point split
backs the checkpoint estimates.

## Commands to validate

**Verify:** `make verify` (PASS WITH WARNINGS: `BASE` equals `HEAD`, docs-only
change; 62 tests pass, type check passes, no whitespace errors, no test files
changed).

## Proposed AGENTS.md changes

None.

## Temporary changes

None.

## Permission review

- Read-only (propose allowing): none.
- Writes to the record (keep asking): none.
- Risky (propose denying): none.

## Interruptions

None.

## Unrelated problems noticed but not fixed

None.

## Follow-ups for the next session

- Answer open decisions 5-11 (D1-D7) at the Milestone B/C briefing, before their
  issues are filed.
- Step 13 (`_docs/plan-summary.md`) is the next product step; it gates step 14
  (plan review and phase change) and the Tier A build.
