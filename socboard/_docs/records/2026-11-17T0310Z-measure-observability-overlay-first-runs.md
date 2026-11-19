# Observability overlay: the first runs

Recorded once, when the runs happened (`.kiro/steering/evidence-and-steps.md`, rule 2). Issue #292.

## The run on the pull request

- `socboard observability` run 44007243871, on 2026-11-17, pull request 365 (branch `issue-292-obs-stack` at 8d88232). Result: success, about 100 seconds, including building the app image. Link: https://github.com/andrew-chung-au/socboard/actions/runs/44007243871
- (After this run, `verify` failed on a rule of the repository, not on a test: the added `skipif` marker. The rendered-configuration check moved from a skipped pytest to `observability/ci/rendered.py`, which `check.sh` runs; the run recorded here predates it.)
- The log shows the layered stack (`compose.yaml` and `compose.observability.yaml`) started with `--wait`, all five stores and the collector ready (`tempo`, `loki`, `prometheus`, `alertmanager`, `collector`), then trace id `e8ebfe38926674ec6d24d922b9d6b6f6` sent with a canary attribute, `tempo: found`, `loki: found`, `prometheus: found`, and then `tempo: no canary`, `loki: no canary`, `prometheus: no canary`.
- Memory used by each container at that point (`docker stats`, the six services of the budget being the five below and Grafana later): collector 30.6 MiB of 256, Prometheus 32.7 of 256, Alertmanager 12.5 of 64, Loki 36.7 of 384, Tempo 19.3 of 384. The app, proxy and database are outside the budget (app 64.6 MiB, database 38 MiB, proxy 10 MiB).

## The negative control

The canary check passes only if the collector's allow-list works, so the check was tried with the allow-list removed: `socboard observability` run 44007556277 on the branch `control-292-no-allowlist` (not to be merged; it removes `transform/allowlist` from the three pipelines). Result: failure, as intended. The trace was found in the three stores, and then `tempo: canary found (the trace holds the canary)`, `loki: canary found (the log lines hold the canary)`, `prometheus: canary found (the exemplars hold the canary)`, `the canary reached: tempo, loki, prometheus`. So the check catches a leak in each store, and the passing run above is not a check that cannot fail.

## What the first run settled

| Setting | Result |
|---|---|
| `transform/allowlist` (the structured-statements form with `context:`) | Accepted by collector 0.142.0 and it works: the canary on the resource, span, log record and data point did not reach a store. The collector logs an info line that paths were "modified to include their context prefix, please rewrite them accordingly": the flat form (`keep_keys(span.attributes, ...)`) is the current one, and rewriting to it is a later, small change |
| Tempo `overrides.defaults.compaction.block_retention: 24h` | Accepted by Tempo 3.1.1 (it started, and logged `retention provider started`) |
| Loki `compactor` retention block and `limits_config.retention_period: 24h` | Accepted by Loki 3.7.10 (it started and was ready) |
| Prometheus `--storage.tsdb.retention.time=24h` and `--storage.tsdb.retention.size=128MB` | Applied: `TSDB retention updated duration=1d size=128MiB` |
| tmpfs named volumes with `size=` and `uid`/`gid` | All three stores started and wrote to them; no permission error |
| The app's `OTEL_*` variables | The app started healthy with them (the layered stack came up with `--wait`) |

## What these runs do not show

- That the 24-hour deletion happens: nothing ran for a day. The settings are accepted; the effect is not watched.
- That the app's own signals reach the stores: the emitter stands in for the app here. That is #295's check.
- Alertmanager's route to the agent (#297) and the alert firing (#299): the placeholder receiver has no destination.
- Grafana (#293).
