# Issue #293: Grafana and one command

**Date:** 2026-11-17T04:55Z (UTC)
**Spec version:** e3461a7

## What changed and why

#293 makes the stored signals viewable: Grafana, provisioned from files, and one command to start the stack with it. Terraform lane A (track B) built it on `issue-293-grafana`.

- `compose.observability.yaml`: a `grafana` service (image pinned by digest, 384 MiB, user 472, `127.0.0.1:${STACK_GRAFANA_PORT:-3000}` only, anonymous access and sign-up off, a health check, an admin password that is a required variable with no default). The six services add up to 1344 MiB: Grafana was killed (exit 137) while starting at the 160 MiB the first plan set aside, so it has 384 and the five older services' limits came down (they used a few tens of MiB each in the runs), and the volume caps came down with them.
- `observability/grafana/`: datasources for Prometheus, Tempo and Loki with no credential (an exemplar opens its trace, a trace opens its log lines by `trace_id`, a log line's `trace_id` opens its trace) and the dashboard "SOCBoard: alert to queue" (the probe's and the app's p50, p95 and p99 with a 5-second line, ingest outcomes per minute, the `alert.ingested` and `alert.first_in_queue` log lines, filters by environment and version). `observability/otel/collector.yaml` makes the kept resource attributes series labels for those filters.
- `scripts/observability_secrets.py`: Grafana's password into `observability.secrets` (git-ignored, mode 0600, never printed, never rewritten). `scripts/observability_up.py`: what `make observability-up` and `-down` run, with the refused case (no Docker, or a missing secrets script: one named reason, nothing started).
- `observability/screenshots/`: `capture.mjs` (Playwright from `e2e/`, kiosk mode, a fixed viewport and dark theme, an absolute window, three screenshots and the redacted answers of the three stores) and `manifest.py` (the manifest and its check). `observability/ci/check.sh` runs the real probe and the capture when `SCREENSHOT_DIR` is set.
- Tests: the overlay's rules now include Grafana, the datasources and the dashboard, the secrets script, the up script, the evidence manifest, and the workflow's new steps.
- README: an "Observability" section in the step format.
- Protected, given to the maintainer as exact diffs: the Makefile targets, the two `AGENTS.md` Commands lines, and the workflow's screenshot steps.

**What I learned:** the repo's guard against added skip markers pushed the refused-case logic into a script that tests can call before the Makefile changes.

## Reflection

unknown (role not asked)

## Launch usage

none

## Files created or modified

- `compose.observability.yaml`, `.gitignore`, `.dockerignore`, `README.md`
- `observability/grafana/*`, `observability/screenshots/*`, `observability/otel/collector.yaml`, `observability/ci/check.sh`, `observability/ci/rendered.py`, `observability/ci/proposed/observability.yml`
- `scripts/observability_secrets.py`, `scripts/observability_up.py`
- `tests/test_observability_compose.py`, `tests/test_observability_workflow.py`, `tests/test_observability_secrets.py`, `tests/test_observability_up.py`, `tests/test_observability_evidence.py`
- `_docs/records/findings/293.json`, this file

## Decisions made by the human

- 2026-11-17: lane A takes track B (#340, #292, #293).

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify` (CI), and the `socboard observability` run. In the sandbox: the observability and script test files with `--noconftest`.

## Proposed AGENTS.md changes

The two Commands lines for `make observability-up` and `make observability-down` (protected; an exact diff for the maintainer).

## Temporary changes

A throwaway `pip install --target .scratch/otel`, deleted.

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-293-1 to F-293-4 (see the findings file).

## Follow-ups for the next session

- Done: the maintainer applied the workflow and `AGENTS.md` diffs (commit 08e775d); run 44027949931 produced the artifact; it is committed once under `_docs/evidence/observability/2026-11-17/` with its manifest. Not applied: the Makefile diff (F-293-8), so `make observability-up` does not exist on the branch yet.
- The proof of #295 failed once on the pull request run and passed on the re-run of the same commit (F-293-9): worth a look by the DevOps lane.
