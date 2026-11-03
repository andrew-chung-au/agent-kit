# Issue #157 (task 25): telemetry Compose test + `make test-compose` selector

**Date:** 2026-10-24
**Branch:** `feat/157-telemetry-compose-test` (PR #173)
**Environment:** Kiro Web sandbox (no Docker/PyPI/venv; CI route 1 is the only runner for the Docker job)

## What shipped (scope narrowed — human decision, "Option C done right" + review)

- Protected `Makefile` (human-approved commit `825f21c`): `make test-compose` with a validated `JOB=telemetry|alert|responder` selector (empty = all three), dispatching to `ci/test-compose.sh`; `backend-test` gains `-m "not compose"` so the Docker-only cases are **deselected** (never skipped) by `make test`/`make verify`.
- `.github/workflows/verify.yml`: the `telemetry` CI job (contents: read, pinned actions, no secret).
- `T-REFUSE` only (`tests/test_compose_telemetry.py`, `compose`-marked), with helpers `tests/compose_telemetry.py` and driver `tests/compose_driver.py`.
- `tests/test_marker_hygiene.py` (unit): fails if the `compose` marker appears outside the allowlisted compose module — closes the gap that the gate catches a new skip/xfail but not a test newly tagged `compose`.
- `backend/pyproject.toml`: register the `compose` marker.
- Docs: `_docs/testing.md` (telemetry row → `T-REFUSE` shipped, the rest pending #172; narrowing note; US-13 traceability stays `T-JOURNEY-BE`), `_docs/pending-verification.md` #157, `_docs/ai-usage-log.md`, `_docs/roadmap.md`.

The delivery-dependent cases (`T-JOURNEY-BE`, MailHog `I-OWNER-NOAWS`/`I-OWNER-SENDER`, `T-E6`, the delivery-half `T-DELIVER-TRACE`) moved to prerequisite **#172** because each needs the *deployed backend container* to deliver. `alert`/`responder` are tasks 27/#159, 28/#160; the selector exits 3 for them until then.

## What `T-REFUSE` proves (both layers, both pipelines)

The driver emits, in one trace: an app-helper span/log (code allowlist drops excluded attrs before export) AND a **raw OpenTelemetry-API span and raw OTLP log record** that bypass the helper, so the excluded attributes reach the Collector, which must strip them. The test asserts Tempo holds no excluded span-attribute key and Loki holds no excluded value/key (in line or structured metadata), while `vt.scan.id` survives — so a broken *Collector* config fails it, not just the code path. CI: `collected 1 item … 1 passed`.

## Negative-check evidence (task 25 acceptance), recorded on #157

Two throwaway `check/157-refuse-negative-*` branches, each one commit off the PR head, each touching only one allowlist file (not the test):
- Collector allowlist += `owner.email` → `telemetry` RED: `owner.email leaked to Tempo` (the layer's own failing test).
- Code allowlist (A32) += `owner.email` → `unit` RED (task 23's `test_observability.py` guards); `telemetry` stays GREEN, and the driver diagnostic shows `helper path sent excluded keys to Collector: ['owner.email']`, so the green reads as "the Collector stripped it", not "never sent".

Each layer has a test that fails when that layer breaks. Branches to be deleted after the human's review.

## Prerequisite / defect issues filed this session

- **#172** — wire OSV/KEV/EPSS feed clients into `create_app` + `VT_FEEDS=fixtures` mode; carries `T-JOURNEY-BE` and the delivery-dependent cases. Also needed by task 28/#160 (`P-DEMO-BE`).
- **#174** — backend logs were not exported over OTLP (task 23 defect; see below). Fixed on this branch in its own commit.

## ⚠️ Finding: three Compose-only paths had never actually run

The first real Compose run of the telemetry job surfaced three gaps that `make verify` (no Docker) could never have caught:
1. **Feed wiring** — `create_app` injects no OSV/KEV/EPSS clients, so a deployed scan matches nothing (→ #172).
2. **Delivery harness** — delivery must happen in the backend container, not a host process, for `I-OWNER-*` to mean anything (→ #172).
3. **Log export (#174)** — `log_event` wrote JSON to stdout only and **never exported over OTLP**, so no log reached the Collector/Loki. Fixed here: `setup_logging()` installs a `LoggerProvider` + OTLP log exporter (A40 no-op without an endpoint), and `log_event` now also emits an OTLP log record; unit test with an in-memory log exporter asserts an excluded key is dropped and the trace id matches the active span.

**Why task-23 QA missed #174 (record so task 37 and #172 do not repeat it):** task 23's check only *unit-tested the allowlist helper* (`filter_attributes`) — it verified filtering, never that a log record actually leaves the process over OTLP. The helper was correct; the export was absent. Lesson for the verification of any telemetry task: assert the signal **leaves the process/reaches the backend**, not just that the in-code helper filters. PM sweep (below) should apply the same lens to the other Compose-only paths.

## Process

- The whole telemetry job is Docker-only; authored here, verified by CI route 1. `make verify` on the human's host passed PASS WITH WARNINGS (compose case deselected; warnings pre-existing/BASE=HEAD).
- Protected-change approval record for `825f21c` posted on #157.
- No new dependency; `backend/uv.lock` unchanged (OTel SDK + OTLP exporter already locked at 1.45.1; harness helpers use stdlib `urllib`).
- One validated fix per push after an early round of circling (two `PYTHONPATH` guesses) — corrected to read each CI result before the next change.

## Handed to QA

#157's acceptance criteria were narrowed to `T-REFUSE` + the selector (recorded on the issue). Engineer does not close its own issue: QA checks the narrowed criteria and posts PASS/FAIL; then #173 is ready for the human to review and merge.

## Recommendation for #172 (first step, before building)

PM sweep for other Compose-only-never-run paths (the three above were all found by one real run). Make it the first step of #172.
