# Issue #292: the observability overlay

**Date:** 2026-11-17T03:40Z (UTC)
**Spec version:** e3461a7

## What changed and why

#292 turns #340's walking skeleton into the stack the app, the checks and the drill use. Terraform lane A (track B) built it on `issue-292-obs-stack`.

- `compose.observability.yaml`: the collector, Tempo, Loki, Prometheus and Alertmanager, each image pinned by tag and index digest (Alertmanager's read on 2026-11-17), on the existing `stack` network, each port on `127.0.0.1` with a `STACK_*_PORT` default, a `mem_limit` each (1344 MiB together, 160 MiB left for Grafana in 1.5 GiB), non-root users, no Docker socket, named volumes capped in size (in-memory file systems owned by each image's user), 24-hour retention in each store. It sets the app's `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_RESOURCE_ATTRIBUTES` and a 5-second metric export interval. `compose.yaml` is unchanged.
- `observability/{otel,tempo,loki,prometheus,alertmanager}/`: the configs, moved from the skeleton and extended. The collector has a `transform/allowlist` processor that keeps only the contract's names on resources, spans, log records and data points and drops scope and span-event attributes. Prometheus loads `observability/alerts/*.yml` and evaluates every 15 seconds; Alertmanager's `group_wait` is 5 seconds and its only receiver is a placeholder for #297.
- `observability/ci/check.sh`: starts the full layered stack (the app and the overlay), waits for readiness, prints `docker stats`, sends one trace with a canary attribute, finds it in the three stores and checks the canary is in none.
- `observability/ci/query.py`: `absent <trace id> <canary>` and Alertmanager in `ready`. `observability/emitter.py`: `--canary`.
- `observability/ci/rendered.py` and its use in `check.sh`: the rendered configuration (`docker compose config --format json`) is checked by a script in the `socboard observability` run (every overlay port on 127.0.0.1 with a host port, the stack network only, the app's exporter, and the base file alone unchanged).
- `tests/test_observability_compose.py` (the overlay's rules with a refused case each, the collector's allow-list against the contract, the configs' timings and limits, and the rendered-config checker on synthetic renderings), and added cases in the query and emitter tests. The body asks for a pytest over the rendered config skipped by a marker where Compose is missing; `make verify`'s weakened-tests check refuses any added skip marker, so the rendered check is a script that `check.sh` runs and its tests always run.
- Two assertions in `tests/test_observability_query.py` were rewritten, not weakened: the `ready` tests now expect Alertmanager in the list (`alertmanager: ready`, and `alertmanager` in the not-ready line).

**What I learned:** a store's disk limit is not a setting Tempo or Loki have; capping the volume is the honest way to get one.

## Reflection

unknown (role not asked)

## Launch usage

none

## Files created or modified

- `compose.observability.yaml` (new); `observability/otel|tempo|loki|prometheus|alertmanager/*` (moved or new); `observability/ci/skeleton/` (removed)
- `observability/ci/check.sh`, `observability/ci/query.py`, `observability/emitter.py`
- `tests/test_observability_compose.py` (new), `tests/test_observability_query.py`, `tests/test_observability_emitter.py`
- `_docs/records/2026-11-17T0233Z-measure-observability-skeleton-first-run.md` (a note on the moved configs), `_docs/records/findings/292.json`, this file

## Decisions made by the human

- 2026-11-17: lane A takes track B (#340, #292, #293).

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify` (CI), and the `socboard observability` run on the pull request (the layered stack, the three found lines and the canary check). In the sandbox: the observability test files with `--noconftest`, with the SDK and PyYAML installed under `.scratch/` (deleted after): 166 passed.

## Proposed AGENTS.md changes

none

## Temporary changes

A throwaway `pip install --target .scratch/otel`, deleted.

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-292-1: the collector transform syntax, Tempo and Loki retention keys and the tmpfs volume options have not run.
- F-292-2: the disk limit is a volume cap in the compose file.
- F-292-3: two additions to #340's files (the emitter's `--canary`, query's `absent`).
- F-292-4: the skeleton's paths exist only in history now.

## Follow-ups for the next session

- #293 adds Grafana to the overlay (160 MiB of the budget) and `make observability-up`.
- #297 replaces Alertmanager's placeholder receiver.
