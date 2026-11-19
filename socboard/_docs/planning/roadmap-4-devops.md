# Roadmap 4: DevOps (observability, alerting, on-call)

Order and evidence only. Acceptance criteria live on the issues; open or closed is read from the tracker. Scope: `_docs/specs.md` section 4 (cross-cutting story), section 5 (the 5-second invariant) and section 6 (Phase 3). Method: `_docs/planning/04_devops.md`. Dev and prod separation, promotion and rollback belong to the Deploy lanes (#266 to #269) and are not here. Lane and file ownership: the DevOps row of `_docs/planning/deploy-coordination.md`.

- **Status:** filed 2026-11-16 as #285 to #301 (O0 to O16). Revised the same day after a senior review of the plan (relayed by the CI lane; the human approved acting on it): #338 (O0b), #339 (O0c) and #340 (O17) were filed, and #290 to #301 were re-groomed with new body hashes. Open or closed, and labels, are read from the tracker.
- **Goal:** One journey, an alert ingested until it is in the queue within 5 seconds, emits a metric, a trace and structured logs that share one trace id, with no customer data or credential in any signal. The signals are collected, stored and viewable in a UI that starts with one make command. One alert fires on users missing the 5-second promise. An on-call agent wakes on that alert and opens the smallest fix as a pull request. It never merges and never pushes to `main`.

## Decisions (human, 2026-11-16; recorded by #287)

- **Backend:** self-hosted in `compose.observability.yaml`, layered on `compose.yaml` (never edited): OpenTelemetry Collector, Tempo, Loki, Prometheus, Alertmanager and Grafana, each pinned. No account, runs in CI. The all-in-one `grafana/otel-lgtm` image is the fallback, with the human's agreement first.
- **Runner:** `anthropics/claude-code-action` with its key held only in the `oncall` Environment. For the drill the pull request is opened with the workflow's own `GITHUB_TOKEN`, so it gets no automatic CI; an unprivileged job in the drill shows the agent's test failing before and passing after.
- **Alert path:** a script in the drill workflow reads Alertmanager's API and starts the agent when `QueueLatencyOverSLO` is firing. A webhook to `repository_dispatch` is the later dev path and reuses the script's parsing.

## Changes from the senior review (2026-11-16; the human said to act on them)

- **The alert reads the probe** (#338). An in-app first-read measure cannot tell a slow server from an idle board, so the alert reads the synthetic probe's histogram with a minimum of 20 measurements in 5 minutes. The in-app histogram stays as a diagnostic, recorded only while the queue is watched (#291). The spec change is a protected diff in #338.
- **A walking skeleton first** (#340). One path-filtered workflow runs a script in `observability/ci/`, so later checks need no further workflow diff, and a stand-in emitter proves the trace id joins Tempo, Loki and a Prometheus exemplar before the lanes depend on it.
- **The agent runs in its own job** (#298, #299). The job with the model key has a read-only token and hands back a patch; a separate job with no key takes the guard from `main` and opens the draft. A repository ruleset on `main` is the human's step.
- **Smaller fixes on the issues:** logs reach Loki over OTLP (proposed for approved #289, waiting on the human's choice in its comment); the server span comes from a pure ASGI middleware (#290); the exemplar is recorded with the ingest's context (#291); stores publish on loopback for the runner (#292); the probe runs every 5 seconds, waits on a 429 and closes its own cases (#294); the incident file holds checked fields only (#297); the defect is chosen by a spike with a drift check (#299).

## Design in short

- The app exports OTLP to a collector, which routes to Tempo (traces), Loki (logs, with the trace id as structured metadata) and Prometheus (metrics, with exemplars). Spans, metrics and logs are written by hand; there is no SQL or HTTP auto-instrumentation, because those can carry alert text.
- The probe ingests a synthetic alert, polls the queue every second with the same trace id, records the delay in `socboard.probe.time_to_queue`, and closes its case. The app records `socboard.alert.time_to_queue` at the first queue read that returns a case, only while the queue is watched, linked to the ingest trace.
- The alert is a Prometheus rule so `promtool` can test it offline: p95 of the probe's histogram over 5 minutes above 5 s for 2 minutes, with at least 20 measurements.
- The proof of the shared trace id chooses the id itself, sends it as `traceparent`, and reads Tempo, Loki and Prometheus back. A canary test plants fake alert text, a note, a password, a key, a token and an account number and fails if any is stored.
- The drill runs in one workflow of four jobs on an ephemeral stack, with a defect patch applied to a throwaway branch, so `main` never holds the defect.

## Tasks, in order (O-labels), tracks and evidence

Tracks run in parallel after the contract: **A** app telemetry, **B** stack, **C** alert and agent. Each issue's evidence is linked from the README's Observability section by #300, which hands the Planning lane the lines for the reviewer section. "Needs" is what must merge first; each issue's body says what the wait protects and what can be written before it (`.kiro/steering/real-dependencies-only.md`).

| Issue | Track | Needs | Evidence a reviewer can open |
|---|---|---|---|
| #285 O0 Signal contract | Contract | none | merged PR, `observability/CONTRACT.md` |
| #310 O0a Contract wording (QA findings F-285-1, F-285-2) | Contract | #285 | merged PR #315 |
| #338 O0b Contract and spec: alert on the probe | Contract | none | merged PR |
| #339 O0c Machine-readable contract | Contract | #338 | CI run |
| #286 O1 Spec detail (protected diff) | Human | #285 | merged PR |
| #287 O2 Decision record | Human | none | the decision record |
| #288 O3 OpenTelemetry dependencies (protected) | A | the human's `uv add` | PR and CI run |
| #289 O4 Telemetry core | A | #288 | CI run (unit tests) |
| #312 O4a Limit the two operator-set resource attributes | A | #289 | CI run (unit tests) |
| #290 O5 Instrument ingest, server span, canary test | A | #289 | CI run |
| #291 O6 Instrument the queue read (diagnostic) | A | #289, #290, #338 | CI run |
| #340 O17 Walking skeleton and CI entry point (Heavy) | B | #288 (the emitter) | the `socboard observability` run log |
| #292 O7 Collector and storage | B | #340 | `socboard observability` run |
| #293 O8 Grafana and `make observability-up` | B | #292 | committed screenshots and manifest |
| #294 O9 Synthetic probe | C | #338, #288 | CI run |
| #296 O11 Alert and promtool tests | C | #338 | the pull request's CI run (promtool in Docker) |
| #348 O11a The alert in the observability check: `check.sh` call, load check, dashboard line | C | #340, #292, #293 (each part lands as its issue merges) | `socboard observability` run |
| #297 O12 Alert-to-agent hand-off | C | #296 | CI run |
| #298 O13 On-call mandate, guard, two jobs (Heavy) | C | #297 | CI run of the guard tests, mandate file |
| #295 O10 CI check: shared trace id, no canary (Heavy) | Join | #290, #291, #292, #294, #340 | run log and committed query JSON |
| #299 O14 On-call drill (Heavy) | Join | #290, #292, #293, #294, #296, #297, #298 | the drill run log and the agent's pull request |
| #300 O15 README Observability section and link check | Docs | #299 | README, link check |
| #301 O16 Show it on dev | Later | #292, #294 | a dated record, screenshots if dev is used |

Critical path: #288, #340, #292, then #295 and #299 (with #289 and #290 beside it). The contract change #338 goes first because #291, #294 and #296 read it.

## Waves

- **Wave 0 (one sitting with the human):** label #338; approve its spec diff; choose an option on #289's proposed change; run #288's `uv add`; approve the Heavy decision records of #340, #295, #298 and #299 by name when they are labelled.
- **Wave 1 (parallel):** A: #289. B: #340 (its workflow diff and `query.py` first, the emitter once #288 is in). C: #294's HTTP side, #296's rule and promtool tests, #298's guard. Contract: #338, then #339.
- **Wave 2:** A: #290, #312, #291. B: #292, then #293. C: #297, then #298's mandate.
- **Wave 3:** #295, then #299 (its defect spike can run in wave 1), then #300.
- **Dev:** #301 waits only on the server's free memory (the first deploy has run, PR #335). It may end as a record that the stack does not fit.

## Workflow and protected-file diffs

Workflows, the Makefile, `AGENTS.md`, `pyproject.toml`, `uv.lock` and `_docs/specs.md` are protected. The DevOps lane gives exact diffs, so the human can batch them:

- `.github/workflows/observability.yml` (#340), the one workflow the observability checks need; #292, #295 and #296 run through its script.
- `.github/workflows/oncall-drill.yml` and `ready_for_review` on the CI workflows' `pull_request` types (#299).
- The Makefile and `AGENTS.md` lines for `make observability-up` and `observability-down` (#293).
- The spec text of #338. The dependencies of #288 (the human's `uv add`).

## Not in this phase

Dev and prod separation, promotion and rollback (#266 to #269); managed telemetry; automatic merge of the agent's pull request; alerts other than the one on queue latency; a recording (`.kiro/steering/evidence-and-steps.md`, item 4).

## Archive when

The drill's run log and the agent's pull request are linked from the README, the CI run of the shared-trace-id check passes on `main`, and the promtool tests pass on `main`.
