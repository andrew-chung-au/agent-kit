# Issue #286: O1 Spec: detail the Phase 3 observability story

**Date:** 2026-11-16T05:53Z (UTC)
**Spec version:** 1b619a1

Tier: Standard (from the PM proposal; no tier label).

## What changed and why

`_docs/specs.md` section 4 replaces "Detailed when that phase starts" with six one-line DevOps-phase stories that use the names of `observability/CONTRACT.md`: time to queue, one shared trace id, no forbidden data in any signal, the one-command stack, `QueueLatencyOverSLO`, and the on-call agent that opens a pull request and never merges. Section 6's Phase 3 outline and section 7's non-goals changed only where they conflicted. The PM drafted the exact diff; the human approved it as drafted; the orchestrator checked `main`'s spec was unchanged since the draft, applied it byte-identical and committed it with HUMAN_APPROVED=1 (1b619a1, PR #332).

The same session also closed #287 (PR #325, merged head checked) and opened PR #329 to land #310's fix, which the #315 merge missed.

**What I learned:** check a pull request's merged head against the QA PASS commit before closing.

## Reflection

### PM

**What slowed you down (evidence):** none; the contract and roadmap gave every name.
**What nearly went wrong or was blocked:** the shared-trace-id story relies on `queue.first_seen` being its own linked trace; a reader could expect `alert.first_in_queue` to carry the ingest trace id.
**One proposed change (file, expected effect, measure):** add a hunk-count assertion to the diff check script so a spec diff cannot touch lines outside its intended hunks.

### QA

**What slowed you down (evidence):** none; CI head SHA checked for all four runs.
**What nearly went wrong or was blocked:** the unnamed make target could have been read as a criterion failure; graded Low since the human kept it generic.
**One proposed change (file, expected effect, measure):** none beyond leaving non-findings out of the comment.

## Launch usage

- PM (diff draft): unknown (the tool did not report time or tool uses).
- QA: unknown.

## Files created or modified

- `_docs/specs.md` (protected, human-approved)
- `_docs/records/findings/286.json`
- this file

## Decisions made by the human

- Approved the PM's spec diff as drafted, with the recommended answers to its four questions (narrow the automated-response non-goal; keep "one make command" generic; keep the Phase 3 label; leave the off switch, resource attributes and Alertmanager payload in the contract only).

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** CI-VERIFIED on 1b619a1: verify run 43812207250, image 43812207368, compose 43812207386, postgres 43812207194, all success.
- **Assert clean:** passed after QA at 1b619a1.

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-286-1: The one-command story does not name the make target (Low).
- F-286-2: The one-command story leaves out Alertmanager (Low).
- F-286-3: The journey story states 5 s only as a bucket bound (Low).

## Follow-ups for the next session

- After the merge of #332: check the merged head is this branch's last commit, post the Close comment, run `make issue-close N=286`.
- #329 (land #310's fix), then #312's body (option C), then #288's human step.
