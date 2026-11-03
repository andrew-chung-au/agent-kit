# Issue #180: PM sweep — observability / US-13 / US-15 helper real-path callers | Planning: observability helper sweep

**Date:** 2026-10-25
**Spec version:** 9b04f90
**Covers:** #180 (helper real-path sweep); confirms the four known defects #172, #174, #176, #177; cross-checks US-13/US-14/US-15 (#160, #161, #179, #181, #182); extends the Compose-path sweep in `planning-2026-10-24-compose-path-sweep.md`. Filed #193, #194 and #195; #177 folded into #193; the exemplar assertion (D) added to #172's `T-JOURNEY-BE` criteria.

## What changed and why

Analysis only — no product code changed. This sweep answers one question for every observability / US-13 / US-15 helper: **is it called by code that runs on the real path?** It is the detection half of #179; the prevention half stays with QA.

The four known "helper built, never called on the real path" defects are confirmed fixed on current `main` (`9eb4071`):

| Defect | Helper that existed | Real-path caller now | Status |
|---|---|---|---|
| Feed wiring #172 | OSV/KEV/EPSS clients | `main.py:98` → `app.state` clients (`99-100`) → `ScanWorker` (`105-111`); `require_feeds_allowed()` at `main.py:158` | reached |
| #174 | `log_event`'s OTLP export | `main.py:151` `setup_logging()`; lazy setup `logs.py:111`; exporter `logs.py:69-78` | reached |
| #176 | `hash_password` + `User` model | `manage.py:455-461` parser → `_cmd_create_user` (`146-158`) → `create_user` (`112-143`); used by `ci/test-compose.sh:94`, documented `README.md:117` | reached; #176 closed |
| #177 | `log_event` | `scan.py:308` (`scan.finished`), `delivery.py:100` (`notification.deliver`) | reached, but not every branch (below) |

The sweep also found four branch/consumer gaps that no existing issue covered. Three were filed on 2026-10-25 as #193, #194 and #195; the fourth (the metric-exemplar assertion) was added to #172's `T-JOURNEY-BE` criteria.

## Method

- **Real path** means code that executes in the running app/container, a worker loop, an HTTP route, or the operator CLI — not only a unit test. The container starts `uvicorn vulntriage.main:app` (`backend/Dockerfile:53`), so module-level `create_app()`, its lifespan, the scan worker, the delivery worker, the scheduler, and registered routes all count.
- `reached` means a caller executes on one of those paths. A branch-specific hole is a **separate row** marked `FLAG`, so each helper still has exactly one of the two verdicts the issue asks for.
- Line references were checked by `.scratch/sweep_helpers.py` (read-only), not copied from memory. Re-run it with `python3 .scratch/sweep_helpers.py`.
- Partial branch coverage is treated as a FLAG: "the helper is called somewhere" is not enough when the issue asks whether each intended signal is emitted on the real path.

## Inventory — named helpers

### Tracing (`observability/tracing.py`)

| Helper (definition) | Real-path caller | Where it runs | Verdict |
|---|---|---|---|
| `setup_tracing` (:41) | `main.py:149` | app construction, before lifespan | reached |
| `span` (:77) | `scan.py:221,232,272,284,288`; `notifications.py:73` | scan worker, refresh scan, request-path enqueue | reached |
| `span_from_traceparent` (:89) | `delivery.py:192` | delivery worker | reached |
| `set_span_attributes` (:121) | `delivery.py:208,234,248,258,277` | delivery worker | reached |
| `current_traceparent` (:127) | `notifications.py:74` | scan worker and refresh | reached |
| `current_trace_id_hex` (:139) | `scan.py:230` | scan worker | reached |
| `build_resource` (:30) | `tracing.py:52`, `metrics.py:175`, `logs.py:67` | traces, metrics and logs providers | reached |
| `get_tracer` (:67) | `tracing.py:84,115` | used by `span` / `span_from_traceparent` | reached (internal) |

### Metrics (`observability/metrics.py`)

| Helper / instrument (definition) | Real-path caller | Where it runs | Verdict |
|---|---|---|---|
| `setup_metrics` (:160) | `main.py:150`; `delivery.py:123` | app construction; delivery worker `__init__` | reached |
| `set_overdue_source` (:77) | `main.py:91` (lifespan start), `main.py:135` (shutdown) | app lifespan | reached |
| `compute_overdue_series` (:93) | `metrics.py:218` (gauge callback) | Prometheus scrape | reached |
| `_observe_overdue` (:199) | registered as callback `metrics.py:191` | Prometheus scrape | reached |
| `vt_notifications_total` (:179) | recorded `delivery.py:238` (sender-not-verified), `261` (failed), `278` (sent) | delivery worker | reached on those outcomes; **FLAG** for the other held branches (row below) |
| `vt_notification_delivery_seconds` (:183) | recorded `delivery.py:281` | delivery worker | reached (sent only, by design: it times delivery) |
| `vt_top_tier_notification_overdue` (:189) | observed by callback `metrics.py:199`; data `compute_overdue_series` (:93); source `main.py:91` | Prometheus scrape | reached |

### Logs (`observability/logs.py`)

| Helper / event (definition) | Real-path caller | Where it runs | Verdict |
|---|---|---|---|
| `setup_logging` (:50) | `main.py:151`; lazy `logs.py:111` | app construction; first `log_event` if not installed | reached |
| `log_event` (:87) | `scan.py:308`; `delivery.py:100` | scan worker; delivery worker | reached |
| `scan.finished` (`scan.py:308`) | success path only | scan worker | reached on success; **FLAG** on failed scans (row below) |
| `notification.deliver` (`delivery.py:100`) | `_send_and_record` only | delivery worker | reached on send-path outcomes; **FLAG** on pre-send holds (row below) |
| `brief.rejected` | none | — | **FLAG: no real-path caller** — Showcase task 30 is unfiled/not built |

### Allowlist (`observability/allowlist.py`)

| Helper (definition) | Real-path caller | Where it runs | Verdict |
|---|---|---|---|
| `filter_attributes` (:40) | `tracing.py:83` (span start), `tracing.py:112` (span_from_traceparent), `tracing.py:123` (set_span_attributes); `logs.py:96` | every span and every log record | reached on both paths |
| `is_allowed` (:50) | none | — | no caller; not a signal emitter; minor dead helper (not a US-13 gap) |

### Feeds (`ingest/feeds.py`, `ingest/settings.py`)

| Helper (definition) | Real-path caller | Where it runs | Verdict |
|---|---|---|---|
| `build_feed_clients` (`feeds.py:214`) | `main.py:98` | app lifespan | reached |
| `require_feeds_allowed` (`settings.py:78`) | `main.py:158` | app construction (`create_app`) | reached |
| `get_feeds_mode` (`settings.py:41`) | `main.py:98` | app lifespan | reached |
| `fixtures_root` (`feeds.py:52`) | `feeds.py:242` from `build_feed_clients` | app lifespan when `VT_FEEDS=fixtures` | reached conditionally (fixtures/demo mode only, by design) |

## Inventory — delivery worker outcome signals

The delivery worker is started at `main.py:125-126` (`DeliveryWorker.start()`), stopped at `main.py:137`. The span is opened once at `delivery.py:192`; the log helper is `_log_delivery_outcome` (`delivery.py:79-100`); the counter adds are at `238`, `261`, `278`; the histogram records at `281`.

| Outcome branch | Span `notification.deliver` | `notification.deliver` log | `vt_notifications_total` | Histogram | Evidence |
|---|---|---|---|---|---|
| sent | yes | yes | yes | yes | `delivery.py:271-286` (span 192, counter 278, histogram 281, log 284) |
| transport failed (retries) | yes | yes | yes | no (not a completed delivery) | `delivery.py:254-267` (counter 261, log 264) |
| held: sender_not_verified | yes | yes | yes | no | `delivery.py:228-243` (counter 238, log 241) |
| held: header_injection | yes | yes | **no** | no | `delivery.py:244-253` (span/log only) |
| held: mail_config | yes | yes | **no** | no | `delivery.py:203-214` (span/log only) |
| held: ownerless | **no** | **no** | **no** | no | `delivery.py:168-175` returns before `_send_and_record` (192) |
| held: owner email missing | **no** | **no** | **no** | no | `delivery.py:168-175` |
| held: no_target | **no** | **no** | **no** | no | `delivery.py:158-166` returns before `_send_and_record` (192) |

The last three are the gap. A held job is a real deliverable outcome (it is what the responder and the operator see), but it emits no `notification.deliver` span, no `notification.deliver` log and no counter value. #177 covers only the **log** half; it does not cover the span or counter, and it predates the `mail_config` / `header_injection` counter gap.

## Inventory — US-15 responder (task 28 / #160)

The responder **receiver** is not built. What exists in the tree is the API surface it will call, plus the Grafana destination:

| Piece | Real-path caller | Verdict |
|---|---|---|
| `GET /api/findings/{id}` and `GET /api/jobs` (`api/service.py:146,163`; `require_responder` `api/service_auth.py:82`; router registered `main.py:178`) | HTTP request to the running API | reached route; there is no responder client to call it yet |
| Grafana `finding-responder-webhook` contact point (`observability/grafana/provisioning/alerting/us14-overdue.yaml:162-168`) | Grafana alert notification | destination provisioned; receiver is task 28 (#160) |
| Responder Loki read | none | **FLAG: no real-path caller** — no responder package in the tree |
| `VT_DEMO_DEFECT` demo-defect path | none | **FLAG: no real-path caller** — `VT_DEMO_DEFECT` appears only in a comment (`ingest/settings.py:23`); no reader exists |
| Production refusal | none | **FLAG: no real-path caller** — `is_non_production_environment` (`settings.py:62`) exists, but nothing checks it against `VT_DEMO_DEFECT` |
| Responder action log | none | **FLAG: no real-path caller** — no responder code emits it (`_docs/architecture.md:389`) |

This is expected: task 28 (#160) is not built, and task 29 (#161) owns the Compose `responder` job and `P-FLAG-GONE`. The sweep confirms there is nothing to audit yet, rather than inventing a caller.

## Cross-check against the architecture and testing docs

- **Submission span list** (`_docs/architecture.md` § Observability): `scan.run`, `repository.read`, `osv.query`, `signals.enrich`, `prioritise`, `notification.enqueue`, `notification.deliver` all have emitters on the real path (rows above). `brief.generate` has none — Showcase (task 30), not a submission span.
- **Log event list** (`_docs/testing.md` US-13/US-15): `scan.finished` and `notification.deliver` exist; `brief.rejected` does not. The latter is the Showcase US-6 case (task 30, unfiled), not a submission blocker.
- **T-A4 / exemplar** (`_docs/testing.md:267,344`): the test says the metric, trace and log share the trace id, but `tests/test_compose_telemetry.py:211-212` only asserts `wait_for_metric('vt_notifications_total{vt_outcome="sent"}')` exists. It never asserts the metric exemplar carries `journey_trace_id`. The instrumentation records the counter inside the `notification.deliver` span (`delivery.py:277-281`), so an exemplar is expected; the test does not prove it. This is an evidence gap, not a missing emitter.
- **US-13 dashboard** (`observability/grafana/dashboards/us13-journey.json:43`): the pane groups `sum by (kind, outcome)`, but the counter is emitted with `vt.notification.kind` / `vt.outcome` (`delivery.py:278`), and `tests/test_compose_telemetry.py:212` uses the Prometheus-normalised `vt_outcome` (`observability/otel-collector.yaml:51` lists the dotted `vt.outcome` in its `keep_keys`). `_docs/testing.md:267` also uses `{kind,outcome}` and should be updated with the panel if the live check confirms the mismatch. This is a consumer bug, not a helper gap.
- **US-14 alert**: `vt_notifications_total` is the alert input; the held-branch counter gap means a burst that ends in `held` has no series for an alert/dashboard to count. `vt_top_tier_notification_overdue` is reached.
- **CI jobs**: `#181` (`T-E6`, telemetry backend down) and `#182` (`I-OWNER-SENDER`, MailHog) are test cases, not signal emitters; they remain open and are not re-scoped here. `#185` (T-JOURNEY-BE flake) is closed; the 02:20 comment on #180 that describes it as unbuilt predates the fix commit `7ceef0d` (02:26), which adds `_normalize_trace_id` at `tests/compose_telemetry.py:142`.

## Findings / actions

1. **FLAG — held delivery branches lack the `notification.deliver` span and counter.** `delivery.py:168-175` (ownerless, owner email missing) and `158-166` (no_target) return before `_send_and_record` (192). `mail_config` (203-214) and `header_injection` (244-253) have the span and log but no counter. Existing #177 covers the log half only. **Filed as #193; #177 is folded into #193** (closed 2026-10-25).
2. **FLAG — failed scans emit no `scan.finished`.** `_fail` (`scan.py:312-320`) is called on repository, lockfile and feed failures (`234-242`, `274-281`) but never calls `log_event`; only the success path does (`scan.py:308`). **Filed as #194.**
3. **FLAG — `brief.rejected` has no emitter.** No definition, no caller. Showcase task 30 (unfiled). No submission action; not filed.
4. **FLAG — US-15 responder helpers do not exist.** Loki read, demo-defect path, production refusal and action log are all absent; task 28 (#160) is not built. Task 29 (#161) owns the responder test and `P-FLAG-GONE`. No new issue; the existing tasks cover it.
5. **Cross-check finding — dashboard label mismatch.** `us13-journey.json:43` groups by `kind, outcome`; the series have `vt_notification_kind, vt_outcome`. **Filed as #195, with the live check as its first step; close as a no-op if the labels already match.**
6. **Cross-check finding — exemplar assertion missing.** T-JOURNEY-BE checks the counter exists, not that its exemplar carries the journey trace id. **Not filed separately: added to #172's `T-JOURNEY-BE` acceptance criteria** (human decision, 2026-10-25).
7. **Minor — `allowlist.is_allowed` is unused.** No caller; not a signal emitter. Note only.
8. **Record correction — #180's 02:20 comment is stale on #185.** #185 is closed and the padding fix is on `main` (`7ceef0d`, `tests/compose_telemetry.py:142`).

## Filed issues (approved 2026-10-25)

One deliverable each; evidence is in the rows above.

1. **#193 — Delivery worker: emit the outcome span/log/counter on every held branch (folds #177)**
   - Goal: a held job (ownerless, owner email missing, no_target, mail_config, header_injection) produces the same `notification.deliver` span, structured log and `vt_notifications_total` value as sent/failed, so the responder and dashboard see it.
   - Evidence: `delivery.py:158-175` returns before the span at 192; `delivery.py:203-214` and `244-253` skip the counter. #177 covered the log half only; it is folded in and closed.
2. **#194 — Emit `scan.finished` on failed scans, not only successful ones**
   - Goal: every terminal scan outcome logs `scan.finished` with its status/failure reason inside `scan.run`, so a failed scan is visible in Loki and the journey trace.
   - Evidence: `_fail` (`scan.py:312-320`) is called at `234-242` and `274-281`; only the success path calls `log_event` at `308`.
3. **#195 — US-13 dashboard: verify `vt_notifications_total` label grouping live, fix if mismatched**
   - Goal: check the panel against the live series first; if the labels really differ (`vt_notification_kind`, `vt_outcome` vs `kind`, `outcome`), make the one-line query fix; if they match, close as a no-op with evidence.
   - Evidence: `us13-journey.json:43` vs `delivery.py:278`, `tests/test_compose_telemetry.py:212`, `observability/otel-collector.yaml:51`.
4. **D was not filed.** The metric-exemplar assertion is added to #172's `T-JOURNEY-BE` acceptance criteria instead.

## Decisions made by the human

- **A** — file it, and fold #177 into it (one issue, not two overlapping ones). Filed as #193; #177 closed as superseded.
- **B** — file it. Filed as #194.
- **C** — file it, with the live panel check as the first step; if the labels match, close it. Filed as #195.
- **D** — do not file as its own issue; add it to the `T-JOURNEY-BE` criteria. Added to #172.
- **Not filed:** `brief.rejected`, the `brief.generate` span, the US-15 responder gaps and `is_allowed`; they belong to Showcase/unbuilt tasks.

## Mismatches with the spec or design docs

- `_docs/testing.md` T-A4 claims the metric exemplar shares the journey trace id; the test does not assert it. (Evidence gap, not a product defect.)
- `observability/grafana/dashboards/us13-journey.json` queries labels the counter does not emit.
- `_docs/architecture.md` / `_docs/testing.md` describe `brief.rejected` (Showcase US-6) and the US-15 responder helpers; neither is built. Both are already scoped to task 30 and task 28 (#160), so this is a known phase gap, not a new mismatch.

## Commands to validate

- **Verify:** `make verify` — run after this summary was written; result recorded in the session log / final message.
- **Check:** `python3 .scratch/sweep_helpers.py` — re-runs the definition/caller assertions, read-only. The script is git-ignored and `make clean-scratch` removes it, so after this issue closes the line references can only be re-checked by hand.
- **OpenAPI:** none (no API change).

## Proposed AGENTS.md changes

None.

## Temporary changes

None. No processes started, no system changes, no installs. The `.scratch/` scripts and fetched issue JSON are git-ignored and are removed by `make clean-scratch` at the end of the issue.

## Process corrections (human, 2026-10-25)

- `python3 .scratch/*` must **never** be proposed for allow, whether it only reads or writes under `.scratch/`: the sweep rules say scratch scripts are not a permission candidate. The right answer is a make target. No settings change is proposed here.
- The two modified docs (`_docs/ai-usage-log.md`, `_docs/permission-sweeps.md`) were the human's #65 work, not this session's, and are now committed as `0e9af39`. The interim report calling them "not mine" was wrong; checked here before any commit.

## Permission review

- No settings changes proposed.
- Read-only, not a permission candidate:
  - `python3 .scratch/show_issue.py`, `.scratch/show_other_issues.py`, `.scratch/show_161_185.py`, `.scratch/sweep_helpers.py` — read-only issue/code inspection; matched the catch-all `bash: "*": "ask"` rule in `opencode.json`. Per the sweep rules these scripts are never proposed for allow; the right fix is a make target.
  - `sed -n ...` reads of source and docs — read-only; matched the same catch-all `ask` rule.
- Scratch-only write, not a permission candidate:
  - `python3 .scratch/add_172_exemplar.py` — writes only `.scratch/issue-172-body.md`; no repository file changes. Same `ask` rule; no settings change proposed.
- Writes to the record (keep asking):
  - `make issue-comment N=180 FILE=.scratch/issue-180-pm-comment.md` — posts the PM comment, which #180 explicitly asks for; `make *` is allow, so no approval was requested.
  - `gh issue create` for #193, #194, #195 — human-approved at the decision point.
  - `gh issue edit 172 --body-file ...` — adds the D criterion, human-approved.
  - `make issue-comment N=177 ...` and `make issue-close N=177` — fold #177 into #193, human-approved.
- Risky (propose denying):
  - None.

## Interruptions

None.

## Unrelated problems noticed but not fixed

- `allowlist.is_allowed` (`allowlist.py:50`) has no caller; harmless but dead.
- The 02:20 comment on #180 is stale about #185; #185 is closed and the padding fix is on `main`.
- `#181` and `#182` remain open test cases; not re-scoped by this sweep.

## Follow-ups for the next session

1. Build #193 (held-delivery signals) and #194 (failed-scan log); both are submission observability.
2. #195 needs the live panel check on a Docker host/CI; close as a no-op if the labels already match.
3. #177 is closed and folded into #193; do not duplicate its log half.
4. The exemplar assertion is part of #172's `T-JOURNEY-BE`; do not file a separate issue.
5. US-15 remains task 28 (#160) and task 29 (#161); re-run this sweep when the responder lands.
