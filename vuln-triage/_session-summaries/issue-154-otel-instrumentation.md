# Issue #154 (task 23): OpenTelemetry instrumentation and the exclusion helper

**Date:** 2026-10-23
**Branch:** `feat/154-otel-instrumentation`

## What changed and why

Task 23 of Milestone C (S4/C2): the scan-to-notification journey emits one
trace, metric and log with a shared trace id, and the US-13 exclusions are
enforced in code. The codebase was built to anticipate this — `scan.py
new_trace_id()` and `notifications.py _new_traceparent()` both said "task 23
replaces this"; this task swaps those placeholders for real OpenTelemetry span
contexts and adds the SDK, the allowlist helper, the metrics and the JSON
logger.

## Design

New `backend/vulntriage/observability/` package:
- `allowlist.py` — `filter_attributes()` keeps only the A32 keys and drops the rest. The in-code exclusion rule: `owner.email`, `authorization`, `db.statement`, `url.full` etc. never pass. The Collector processor (task 24) repeats the drop as a second line.
- `settings.py` — `os.environ` getters (matching the repo pattern): OTLP endpoint, service name/version, deployment environment.
- `tracing.py` — the TracerProvider (A40: an OTLP exporter only when a Collector endpoint is set; real span contexts always), `span()` (applies the allowlist at start), `set_span_attributes()`, `current_traceparent()` / `current_trace_id_hex()`. `get_tracer()` installs the provider lazily so spans have real non-zero contexts even when the app factory did not run (ingest tests).
- `metrics.py` — the MeterProvider and the three US-13 instruments: `vt_notifications_total{kind,outcome}`, `vt_notification_delivery_seconds`, and the observable gauge `vt_top_tier_notification_overdue` emitting the constant 0 heartbeat series (per-finding values are task 26).
- `logs.py` — `log_event()` writes one JSON line `{event, trace_id, span_id, ...allowlisted}`; extra fields go through the allowlist.

Wiring:
- `main.py create_app`: `setup_tracing()` + `setup_metrics()` before the app; `FastAPIInstrumentor.instrument_app(app)`; `SQLAlchemyInstrumentor().instrument(engine=...)` in the lifespan (human-approved; `db.statement` is off the allowlist so SQL is dropped in code and again at the Collector in task 24).
- `scan.py run_scan`: a `scan.run` root span with children `repository.read`, `osv.query`, `signals.enrich`, `prioritise`; `Scan.trace_id` is set from the root span's trace id.
- `notifications.py create_top_tier_jobs`: runs inside a `notification.enqueue` span; each job stores that span's W3C `traceparent` (replacing the synthetic placeholder).

## Dependencies (human-approved)

Added to `backend/pyproject.toml` (the human runs `make backend-lock`):
`opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-exporter-otlp-proto-grpc`,
`opentelemetry-instrumentation-fastapi`, `opentelemetry-instrumentation-sqlalchemy`.

## Tests

`tests/test_observability.py` (marked `unit`):
- the allowlist drops `owner.email` / `authorization` (and `db.statement`, `url.full`), keeps the A32 keys;
- the allowlist contains only A32 keys;
- opening a span with an excluded attribute does not record it;
- a `notification.enqueue` span without a Collector gives a valid non-zero W3C `traceparent`.

The existing `test_ingest.py` `scan.trace_id` length-32 assertion still holds
(`current_trace_id_hex()` returns 32 hex).

## Course / showcase parity (recorded alongside)

The course Part 4 sets a production-monitoring bar. Our plan matches it tool for
tool (OTel, Collector + Prometheus/Loki/Tempo/Grafana in `observability/`, the
image tag format, dev/prod + manual promotion, the alert, the AI on-call
responder, the demo defect). Two deltas, now recorded:
- Host CPU/mem/RPS metrics — added as showcase item **X10** in `roadmap-showcase.md` (the course's "at minimum" bar; our rubric scores the US-13 journey, so this is a showcase enrichment). FastAPI auto-instrumentation already gives RPS/latency/error HTTP metrics.
- The alert's `owner` annotation — recorded as a deliberate choice in `tier-c-build.md` (we keep the alert minimal / no owner PII; a non-PII team annotation is a possible showcase add).

## Out of scope (unchanged)

The Compose observability stack and the Collector processor (task 24); the
`T-JOURNEY-BE` / `T-REFUSE` Compose cases (task 25); `notification.deliver`
(task 37).

## ⚠️ Verification

The sandbox has no PyPI, so OTel is not installed and `make verify` / the new
tests cannot run here. All changed files byte-compile; the allowlist filter was
validated standalone (keeps exactly the A32 keys). The human runs `make
backend-lock` then `make verify` on the host. `VERIFY:` the exact OTel package
versions resolve on the pinned toolchain.

## Follow-up for task 24 (#155)

Because SQLAlchemy instrumentation emits `db.statement` by default, task 24's
Collector processor must drop it, and a Compose test should assert SQL never
exports (extends the `T-REFUSE` idea to `db.statement`).
