# Issue #340: the observability walking skeleton and its CI entry point

**Date:** 2026-11-17T00:34Z (UTC)
**Spec version:** e3461a7

## What changed and why

#340 is the first issue of track B in roadmap 4: one CI entry point for the observability checks, and a first proof that one trace id joins a trace, a log line and a metric exemplar across a collector and three stores. Terraform lane A took track B on 2026-11-17 (the maintainer's split with the DevOps session, which keeps tracks A and C).

- `observability/emitter.py`: sends one span `ingest.alert`, one log record (`event` = `alert.ingested`) and one value of `socboard.alert.time_to_queue` with an exemplar, under a chosen trace id, to a collector on the loopback. Names come from `observability/CONTRACT.md`; the span has only the two contract attributes, the log record only `event`.
- `observability/ci/query.py`: `ready` polls the collector and the three stores; `find <trace id>` asks Tempo by id, Loki for the id as structured metadata (and refuses it as a stream label), and Prometheus's exemplar API, polling each for 60 seconds, printing one line per store and naming each that lacks the id.
- `observability/ci/skeleton/`: a Compose file and four configs for the collector, Tempo 3.1.1, Loki 3.7.10 and Prometheus v3.16.0, images pinned by index digest read from the registry on 2026-11-16, all ports on the loopback.
- `observability/ci/check.sh`: starts the stack, waits, emits with a random trace id, queries, always stops the stack.
- `observability/ci/proposed/observability.yml`: the workflow, as a file for the CI lane or the maintainer to land (protected path). Its static test also shows how its triggers read in `tests/workflow_triggers.py` and `scripts/publish_gate.py`.
- Tests: query (22, fake stores), emitter (17, a fake OTLP collector, including a collector that refuses a signal: exit 1), workflow (17): 56 in three files. Decision record `_docs/decisions/2026-11-17T0034Z-observability-ci-entry-point.md` and its index row.

QA's first run (PASS, Lows only) found four small things, fixed before the second QA: the path check used a proper-subset test, one workflow test failed once publish.yml was edited, the emitter exited 0 when the collector refused a signal, and this summary said a scratch install was deleted when it was not yet.

**What I learned:** a path-filtered workflow that can run on a push to `main` has to be in publish.yml's trigger list (a test enforces it), so landing this workflow is three edits for the CI lane, not one.

## Reflection

unknown (role not asked)

## Launch usage

none

## Files created or modified

- `observability/emitter.py`, `observability/ci/check.sh`, `observability/ci/query.py`, `observability/ci/skeleton/*`, `observability/ci/proposed/observability.yml`
- `tests/test_observability_query.py`, `tests/test_observability_workflow.py`, `tests/test_observability_emitter.py` (the last beyond the issue's list)
- `_docs/decisions/2026-11-17T0034Z-observability-ci-entry-point.md`, `_docs/index.md` (one row), `_docs/records/findings/340.json`, this file

## Decisions made by the human

- 2026-11-17: lane A takes track B (#340, #292, #293); the DevOps session keeps #289, #290, #291 and track C.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify` (CI). In the sandbox: `pytest` on the three new observability test files, the probe's and the publish tests with `--noconftest` and the SDK installed under `.scratch/`: all passed on Python 3.11. The stack itself needs Docker and the workflow, so it has not run.

## Proposed AGENTS.md changes

none

## Temporary changes

A throwaway `pip install --target .scratch/otel` (SDK, exporter, the app's dependencies and PyYAML) to run the tests. Deleted.

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-340-1: landing the workflow also needs publish.yml's trigger list and `TRIGGER_LIST` in `tests/test_publish_workflow.py`.
- F-340-2: the stack settings come from the projects' own examples and docs, not a run.
- F-340-3: the check against the real stores waits for the workflow to land.
- F-340-4: one test file beyond the issue's list, and the workflow filter names its own file.

## Follow-ups for the next session

- The CI lane or the maintainer lands `.github/workflows/observability.yml`, `publish.yml`'s list entry and `TRIGGER_LIST`; the first `socboard observability` run then settles the VERIFY notes, and the pull request records the versions that worked.
- #292 builds the overlay from these configs.
