# Decide: which findings to raise with the kit's maintainers

## Purpose

Decide which of two findings to file upstream. Blocks: nothing. Issue: none.

## Where to decide

In the orchestrator session. Filing happens in the kit's own tracker, which this sandbox cannot reach.

## Options

1. The planning gap. The kit has no planning procedure or spec-readiness gate. A working version exists in `_docs/planning/spec-readiness.md`. The earlier draft was removed from this repo, so it would be redrafted.
2. Attribution and the missing Kiro layer. The local `Assisted-by` deviation is recorded in `_docs/decisions/2026-11-06T0111Z-commit-attribution.md`.
3. Both now.
4. Neither.

## Recommendation

File option 1 now, because its evidence already exists. Hold option 2 until the trial's first sweep shows the rule working in practice.

## Record the result

Write Pass once decided, and name the option in the note.

| Step | Pass or fail | Output or note |
|---|---|---|
| Decide | Pass | Human decided 2026-11-10: file the `issue-comment.sh` stderr finding (from #7: a failed post hides gh's error, so the cause is invisible); the draft is `_human-tasks/2026-11-10T1500Z-human-task-orchestrator-file-upstream-issue-comment-stderr.md`. Option 1 (planning gap) is resolved upstream: kit 1.10 has `procedures/planning.md` with a Definition of ready. Option 2 (attribution and the missing Kiro layer) is held until the first ponytail sweep. |

## Risk

None. Filing is reversible and nothing here depends on it.
