# Issue #155 (task 24): observability stack and the US-13 Grafana dashboard

**Date:** 2026-10-24
**Branch:** `feat/155-observability-stack`

## What changed and why

Task 24 of Milestone C (C3): a local-Compose observability stack that shows the
US-13 signals (the metric, the trace and the logs the backend emits from task
23) side by side in Grafana, with the Collector enforcing the A32 allowlist as a
second line of defence. Depends on task 23 (#154, merged). For submission the
stack is local Compose only; AWS deployment is showcase item X3.

## Files (all new, under `observability/`)

- `compose.yaml` — a separate Compose project: `otel-collector`, `prometheus`, `tempo`, `loki`, `grafana` (behind auth via `GRAFANA_ADMIN_PASSWORD`), `mailhog`.
- `otel-collector.yaml` — OTLP receiver; the `transform/allowlist` processor keeps only the A32 keys on traces, logs and metrics and drops the rest (owner contact, advisory text, `url.*`, **`db.statement`** from the SQLAlchemy instrumentation, credentials); exports to Prometheus / Tempo / Loki.
- `prometheus.yml`, `tempo.yaml`, `loki-config.yaml` — single-binary local stores.
- `grafana/provisioning/datasources/datasources.yaml` — Prometheus, Loki, Tempo, with a Tempo→Loki trace-to-logs link.
- `grafana/provisioning/dashboards/dashboards.yaml` + `grafana/dashboards/us13-journey.json` — the "US-13 journey" dashboard: a Prometheus metric pane, a Tempo trace pane and a Loki logs pane, filterable by `environment` and `version`.
- `README.md` — how to run it, how to point the backend at the Collector (`OTEL_EXPORTER_OTLP_ENDPOINT`), the allowlist guarantee, and the VERIFY list.

No backend code and no Makefile change (the `make test-compose` target is task
25), so `make verify` is unaffected.

## The task-24 follow-up from #154 (db.statement)

Handled: the Collector's `keep_keys` drops every non-allowlisted attribute, so
`db.statement` (emitted by the SQLAlchemy instrumentation) is dropped before
export. The in-code allowlist test (`test_observability.py`, #154) already
asserts `db.statement` is excluded; the Compose-side assertion is task 25's
`T-REFUSE`.

## Acceptance criteria mapping

- `observability/` Compose project with the Collector (allowlist processor, drops `url.*`), Prometheus, Loki, Tempo, Grafana (auth), MailHog ✅
- Grafana data sources + the US-13 dashboard with three panes, env/version filter, trace-to-logs ✅
- Local Compose only (AWS is X3) ✅
- Check — the dashboard shows the three signals side by side, MailHog answers → **human verifies in a cloud/Docker session** (`_docs/pending-verification.md`)
- `make verify` passes ✅ (no code/Makefile change)

## ⚠️ Verification

Docker is required, so the stack can't run in the agent sandbox. Steps are in
`observability/README.md` and centralised in `_docs/pending-verification.md`
(#155 section): bring the stack up, run the backend with
`OTEL_EXPORTER_OTLP_ENDPOINT` set, trigger a scan, and confirm the three signals
in Grafana + MailHog answering. All config files are offline-validated (the
dashboard JSON parses; the YAML is hand-checked). `VERIFY:` the pinned image
tags and the `keep_keys` / OTLP ingest / trace-to-logs behaviour on those
versions (README VERIFY list).

## Out of scope (unchanged)

The backend delivery worker (task 37/#156); the `make test-compose` target and
cases (task 25/#157); the alert rule (task 26/#158); the responder (task
28/#160); AWS deployment (showcase X3).
