# Issue #291: O6 Instrument the queue read: time from ingest to first appearance in the queue

**Date:** 2026-11-17T03:50Z (UTC)
**Spec version:** 9cf7ed3

Tier: Standard (from the PM proposal; no tier label). Kiro Web session (Rubric1).

## What changed and why

The maintainer split the open work across three agents. Rubric1 claimed #291 and #339, Rubric2 has the on-call chain and #312, and Rubric3 has the stack. One Engineer launch built #291 (ae6381d), and it merged as PR #366 (`07932e5`). The first queue read that returns a case now:
- starts the span `queue.first_seen`, linked to the ingest span;
- logs `alert.first_in_queue` with the ingest trace id;
- records `socboard.alert.time_to_queue`, only while the queue is watched, with the ingest context as the exemplar's context.

The data comes from a bounded in-process map. It is the in-app diagnostic. The alert reads the probe (#338). #295, the shared-trace-id check, needs this measure.

**What I learned:** a concurrency test should be checked against a mutation that removes the lock, not only one that splits the operation.

## Reflection

### Engineer

**What slowed you down (evidence):** no project environment; packages were installed into `.scratch/pylib` on Python 3.11.
**What nearly went wrong or was blocked:** the first edit used a rewrite script (F-291-5).
**One proposed change (file, expected effect, measure):** none recorded.

### QA

**What slowed you down (evidence):** the first mutation run imported the real package, because the working directory beats PYTHONPATH; `python3 -P` fixed it.
**What nearly went wrong or was blocked:** none.
**One proposed change (file, expected effect, measure):** a race test on the last-read time (F-291-1).

## Launch usage

- Engineer: unknown (the tool did not report time or tool uses).
- QA: unknown.

## Files created or modified

- `socboard/telemetry.py`, `socboard/cases.py`, `socboard/ingest.py`, `tests/test_telemetry_queue.py`, `README.md` (PR #366)
- `_docs/records/findings/291.json`
- this file

## Decisions made by the human

- The lane split, and "go" for #291 and #339; merged PR #366.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** CI-VERIFIED on ae6381d: verify 44007836545, postgres 44007836549, compose 44007836562, image 44007836640, observability 44007836531 (pull request); push runs on the same commit also passed.
- **Assert clean:** not run.

## Proposed AGENTS.md changes

none

## Temporary changes

Packages in `.scratch/pylib` for the Engineer's and QA's runs; deleted.

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-291-1: the race test passes with the lock removed.
- F-291-2: telemetry errors in the queue read are not isolated.
- F-291-3: the ingest time is taken after the commit.
- F-291-4: the watched state is process-wide.
- F-291-5: one edit used a rewrite script.

## Follow-ups for the next session

- #312 (Rubric2) also edits `socboard/telemetry.py`: it merges `main` first.
- #295 can start once #292 merges.
