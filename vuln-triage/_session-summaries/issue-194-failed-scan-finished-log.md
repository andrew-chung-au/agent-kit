# Issue #194: Emit scan.finished on failed scans, not only successful ones

**Date:** 2026-10-25
**Spec version:** 9b04f90

## What changed and why

A failed scan now emits a `scan.finished` log, so the US-13 journey is visible for failures too. `_fail` in `backend/vulntriage/ingest/scan.py` logs after its commit, inside the `scan.run` span, with `vt.scan.id`, `vt.scan.status` = `scan failed` and `vt.error.code` = the `FailureReason` string as is. The success log and the three early returns (scan missing, already finished, asset missing) are unchanged.

Beyond the log: on the feed-failure path `session.rollback()` reset `Scan.trace_id` to the enqueue placeholder, so the stored id did not match the log's. The Engineer re-sets it from `current_trace_id_hex()` after the re-fetch. QA found no side effects.

## Files created or modified

- `backend/vulntriage/ingest/scan.py`
- `tests/test_scan_finished_log.py` (new: five failure kinds, a success-path guard, three zero-log cases)
- `_docs/ai-usage-log.md`
- `_docs/roadmap.md` (check-in row)

Implementation commit: `c6b37c6`.

## Decisions made by the human

- Q1 (`vt.error.code`): the `FailureReason` string as is (option A).
- Q2 (loose ends): delete the unlinked "showcase telemetry events" out-of-scope line; do not fix the unexpected-exception case here; file a follow-up for it.
- Decision point: QA risks handled as above (follow-up filed as #198).

## Mismatches with the spec or design docs

None. #198 records that a fifth failure reason would conflict with the spec's "exactly these values" list (specs.md lines 324-335, architecture.md line 123); that is for the human to decide there.

## Commands to validate

**Verify:** `make verify` (QA: 87 frontend, 480 backend; PASS)

## Proposed AGENTS.md changes

None.

## Temporary changes

None. No processes started. `make clean-scratch` run at the end.

## Permission review

PM, Engineer and QA comments each reported no command needing approval. The PM could not create the follow-up issue because no make target exists; the orchestrator filed it with `gh issue create` using the PM's drafted text.

- Read-only (propose allowing): none
- Writes to the record (keep asking): `gh issue create --body-file` to file #198 (no make target for issue creation; basis: the human approved filing the follow-up)
- Risky (propose denying): none

## Interruptions

None.

## Unrelated problems noticed but not fixed

- `human-tasklist.md` §C still lists PRs #184 and #183, which no longer show as open.
- There is no `make issue-create` target; PM had to hand the drafted issue back. Worth proposing at the next sweep.

## Follow-ups for the next session

- #198: finish a scan that dies from an unexpected exception (needs the human's decision on the end status; option C would need a protected spec change, a migration and an OpenAPI update).
- Held-job and failed-scan OTLP/Loki legs remain unrun on a Docker host (`_docs/pending-verification.md`).
- QA note only: `log_event` raising after the commit would raise out of `run_scan` with the scan already committed (existing behaviour, now also in `_fail`).
- Next: #181 (T-E6), then #195's static part.
