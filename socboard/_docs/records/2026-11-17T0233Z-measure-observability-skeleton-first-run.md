# Observability skeleton: the first run, and what it settled

> The configs this run used were in `observability/ci/skeleton/`. #292 moved them into `compose.observability.yaml` and `observability/{otel,tempo,loki,prometheus}/` (history: `git log --follow`).

Recorded once, when the run happened (`.kiro/steering/evidence-and-steps.md`, rule 2). Issue #340.

- **The run:** `socboard observability` run 44003479301, on 2026-11-17, branch `install-observability-workflow` at 0b3ad94 (the maintainer's commit that installs the workflow, pull request 361). Result: success, about 50 seconds. Link: https://github.com/andrew-chung-au/socboard/actions/runs/44003479301
- **What it showed:** the log has the trace id and one line per store. The trace id was `4af23ba425ef9de546b5f25e11bfc4dd` (random per run): `tempo: found`, `loki: found` and `prometheus: found`. Readiness of Tempo, Loki, Prometheus and the collector was reached in the 120-second window.
- **Who ran it:** CI (a push to the branch). Nothing was run by hand.

## The versions and settings that worked

| Part | What held | Settled `VERIFY:` |
|---|---|---|
| Images | `otel/opentelemetry-collector-contrib:0.142.0`, `grafana/tempo:3.1.1`, `grafana/loki:3.7.10`, `prom/prometheus:v3.16.0`, each pulled by the index digest read from the registry on 2026-11-16 | The digests exist and pull |
| Collector to Tempo | exporter `otlphttp/tempo`, `http://tempo:4318`, no TLS | The path under that endpoint (`/v1/traces`): the trace arrived |
| Collector to Loki | exporter `otlphttp/loki`, `http://loki:3100/otlp` (the exporter adds `/v1/logs`) | Loki's native OTLP path on 3.7.10 |
| Collector to Prometheus | exporter `prometheusremotewrite`, `http://prometheus:9090/api/v1/write` | Exemplars arrive with the histogram |
| Prometheus flags | `--web.enable-remote-write-receiver` and `--enable-feature=exemplar-storage` | Both were enough; no other flag was needed |
| The histogram's Prometheus name | `socboard_alert_time_to_queue_seconds_bucket` (the query by that name found the exemplar) | The name the contract gives |
| Tempo | `-target=all` with the config in `observability/ci/skeleton/tempo.yaml`, no Kafka; `GET /api/traces/<id>` with `Accept: application/json` found the span `ingest.alert` | Tempo 3.1.1 runs as one process |
| Loki | schema v13 on tsdb, `allow_structured_metadata: true`; with `X-Loki-Response-Encoding-Flags: categorize-labels` the trace id came back as structured metadata and not as a stream label | The query and the label split |
| Loki's readiness | `/ready` answered within the deadline | The wait is long enough |

No fallback was needed: neither the collector's `filelog` receiver for logs nor Prometheus's own OTLP receiver for metrics. The open `VERIFY:` notes in the skeleton are marked settled by this run.

## Seen in the log, not a failure

- Tempo warned once, `unowned file entry ignored during wal replay` (file `blocks`), at start-up on the empty volume.
- Tempo logged one warning and one error line for the same event, `error calling scheduler ... no jobs found` (its backend worker finding no work), about 15 seconds after Tempo started (about 35 seconds into the run). The checks passed with it.

Neither changes a result; if a later run fails near them, start there.

## What this does not show

- The run is a push to a branch. The same workflow on a pull request, on `main` and nightly has not run yet.
- The stack is the skeleton (no Alertmanager, no Grafana, no allow-list processor, no retention). The full overlay is #292; the real app's signals are #289 to #291.
- The emitter stands in for the app, so what is proved is the path, not the app.
