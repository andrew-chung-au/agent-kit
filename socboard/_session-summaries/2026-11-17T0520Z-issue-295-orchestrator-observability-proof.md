# Issue #295: O10 CI check: one trace id in the trace, the metric exemplar and the logs, and no canary stored

**Date:** 2026-11-17T05:20Z (UTC)
**Spec version:** 9cf7ed3

Tier: Heavy (from the PM proposal; no tier label). Kiro Web session (Rubric1).

## What changed and why

The maintainer approved the decision record by name, and Rubric1 claimed the issue. One Engineer launch built:
- `scripts/observability_check.py`, which chooses a trace id and drives one probe cycle with it (a new `--trace-id` option on the probe);
- the reads back from Tempo, Loki and Prometheus;
- the canary run, which searches the three stores and the collector log;
- the call in `observability/ci/check.sh`.

The first CI run was green. Two independent QA launches followed. A passed. B failed on three Mediums:
- the canary scans failed open on empty or cut answers;
- exemplars were searched on two metrics only;
- three scans had no test that could fail.

Fix round 1 (a8baaad) fixed all three and five Lows. It also made `check.sh` print the redacted report and a job summary, so no workflow change was needed. One fresh re-check passed, and all 20 of its mutations were caught. The real proof ran in run 44016640671. Its redacted record is committed and linked from the README scorecard. Merged as PR #372 (`2899391`).

**What I learned:** a negative proof ("nothing found") needs a positive guard ("the run's own data was seen"), or an empty store passes.

## Reflection

### Engineer

**What slowed you down (evidence):** "Tempo by id, not a search" conflicts with the contract's separate trace for `queue.first_seen`; a locator search followed by reads by id settles it.
**What nearly went wrong or was blocked:** none recorded.
**One proposed change (file, expected effect, measure):** none recorded.

### QA

**What slowed you down (evidence):** none.
**What nearly went wrong or was blocked:** launch B's mutation runs found four surviving mutants that reading had missed.
**One proposed change (file, expected effect, measure):** one test for `check.sh`'s exit-code logic (F-295-7).

## Launch usage

- Engineer: unknown (the tool did not report time or tool uses).
- QA A: unknown.
- QA B: unknown.
- Engineer, fix round 1: unknown.
- QA re-check: unknown.

## Files created or modified

- `scripts/observability_check.py`, `scripts/observability_probe.py`, `tests/test_observability_check.py`, `tests/test_observability_probe.py`, `observability/ci/check.sh`, `_docs/decisions/2026-11-17T0100Z-observability-proof-in-ci.md`, `_docs/index.md`, `_docs/evidence/observability/2026-11-17-check-run-44016640671.json`, `README.md` (PR #372)
- `_docs/records/findings/295.json`
- this file

## Decisions made by the human

- Approved #295's decision record by name; merged PR #372.

## Mismatches with the spec or design docs

The issue says the trace "holds" `queue.first_seen`, while the contract gives it its own trace linked to the ingest span. The check follows the contract.

## Commands to validate

- **Verify:** CI-VERIFIED on a8baaad: observability 44016640671 (pull request) and 44016632944 (push), verify 44016640318 and 44016632900, postgres 44016640404 and 44016632942, and image and compose, all success.
- **Assert clean:** not run.

## Proposed AGENTS.md changes

none

## Temporary changes

Packages in `.scratch/pylib` for the test runs; deleted.

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-295-1: the canary scans failed open (fixed in a8baaad).
- F-295-2: exemplars were searched on two metrics only (fixed in a8baaad).
- F-295-3: three scans had no failing test (fixed in a8baaad).
- F-295-4: the accepted ingest key and token are not searched for.
- F-295-5: the Tempo scan fails closed at 50 traces.
- F-295-6: the stop trap prints unredacted service logs.
- F-295-7: no test for check.sh's exit code.
- F-295-8: the README probe paragraph lacks `--trace-id`.
- F-295-9: one edit used an inline replace script.

## Follow-ups for the next session

- #300 (the README Observability section) links this run and the record.
- #348 also edits `observability/ci/check.sh`: it merges `main` first.
