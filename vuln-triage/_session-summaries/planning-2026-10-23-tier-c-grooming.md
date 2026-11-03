# Planning: Tier C (Milestone C) issue grooming

**Date:** 2026-10-23
**Author:** PM grooming pass (Kiro, Vibe session)
**Scope:** Milestone C / phase S4, `_docs/tasks.md` tasks 23-29, 37, 38, 39.
**Status:** FILED 2026-10-23. The human confirmed; the 10 issues are filed in
build order: C-23=#154 (task 23), C-24=#155 (task 24), C-37=#156 (task 37),
C-25=#157 (task 25), C-26=#158 (task 26), C-27=#159 (task 27), C-28=#160
(task 28), C-29=#161 (task 29), C-38=#162 (task 38), C-39=#163 (task 39). No
GitHub milestone/label is set, matching the Milestone A/B convention. The
confirm-block items (D4, the responder runtime, `main` branch protection before
task 28/#160; the dependency approvals; the scheduler library-or-loop choice)
are recorded in each issue's Constraints and settled when the issue is picked up.

This is step 12 for Milestone C ("PM proposal approved by the human; each issue
carries its story's acceptance criteria", `_docs/roadmap.md` § Sequence row 12),
done the same way as the Tier B grooming
(`planning-2026-10-23-tier-b-grooming.md`). Sources: `_docs/tasks.md`
(tasks), `_docs/architecture.md` § Observability / § Responder agent /
§ Routing and notifications / § Security boundaries, `_docs/testing.md`
§ Telemetry / § Alerting / § Responder / § CI jobs, `_docs/roadmap.md`
§ Tier C milestones, and [`_docs/tier-c-build.md`](../_docs/tier-c-build.md).

## Decisions and prerequisites that bear on filing

- **Every Tier C submission milestone is local Compose (H6)** — none waits for AWS (B4-B6). So Tier C can be filed and built now, in parallel with the AWS work (#141 etc.).
- **One issue per task** (9 issues for tasks 23-29, 37, 38, 39). The milestone boundaries (C2/C3/C5/C6/C7) group tasks for scoring; they are not re-split. Task 37 is filed as its own issue even though it is "inside" milestone C3.
- **Build order is not numeric** (`tasks.md` Dependency chain): 23 → (24 → **37** → 25) → (26 → 27) → 28 → (28 drill, 29, 39). Task 38 is independent (any time after task 10). Task 39 is last.
- **⚠️ Open decision D4 blocks task 28 (#C6):** the responder false-positive rule is an addition to US-15 in `specs.md` (protected). It needs a proposed diff + human approval **before task 28 is filed**. Status: open.
- **⚠️ Human prerequisites before task 28:** the **responder agent runtime** must be chosen (a dependency; ask), and **`main` branch protection** that refuses the responder's push must be active.
- **New dependencies to approve:** the OpenTelemetry SDK (task 23); the Collector, Prometheus, Loki, Tempo, Grafana and MailHog images (task 24); the AWS SDK / SES client and MailHog (task 37); the responder's agent runtime (task 28). Each is "ask before adding".
- **Several tasks touch the protected `Makefile`** (the `make test-compose JOB=...` selector and its cases): tasks 25, 27, 29. Each is its own human-approved commit.

## Suggested filing order

File in build order so the tracker reads top-to-bottom: **23 → 24 → 37 → 25 → 26
→ 27 → 28 → 29 → 39**, with **38** fileable at any point. Task 28 waits on the
D4 spec change and the two human prerequisites; the rest have no open decision.

---

## Issue C-23 — task 23: OpenTelemetry instrumentation and the exclusion helper

**Covers:** Observability, US-13 · **Depends on:** tasks 10, 15 (done)

**Goal:** The scan-to-notification journey emits one trace, metric and log with a shared trace ID, with exclusions enforced in code.

**Acceptance criteria**
- [ ] The OpenTelemetry SDK and FastAPI auto-instrumentation are wired; `scan.run` and its children and the `notification.enqueue` span (with its stored `traceparent`) are emitted per `_docs/architecture.md` § Observability.
- [ ] Attributes and log bodies are written **only** through the allowlist helper (allowlist A32: `service.name`, `service.version`, `deployment.environment`, `vt.*`, `http.route`, `http.request.method`, `http.response.status_code`, `server.address`).
- [ ] The metrics `vt_notifications_total{kind,outcome}`, `vt_notification_delivery_seconds`, `vt_top_tier_notification_overdue{finding_id,tier}` exist; logs are JSON lines carrying `event`, `trace_id`, `span_id`, ids and outcome codes only.
- [ ] Export is a no-op when no Collector endpoint is set (A40), but the SDK still creates real span contexts, so a stored `traceparent` is a valid non-zero W3C value in `make test`.
- [ ] Checks: a unit test drops `owner.email` and `authorization`; a unit test shows a `notification.enqueue` span without a Collector gives a valid non-zero `traceparent`. (`T-JOURNEY-BE` / `T-REFUSE` Compose cases are task 25.)
- [ ] `make verify` passes.

**Out of scope:** the Compose observability stack (task 24); the Collector processor (task 24); the Compose telemetry test (task 25); `notification.deliver` (task 37).

> **PM → human: confirm before filing**
> 1. **New dependency:** the OpenTelemetry Python SDK + FastAPI instrumentation packages. Approve adding them (names pinned at build time)?

---

## Issue C-24 — task 24: observability stack and the US-13 Grafana dashboard

**Covers:** Observability, US-13 · **Depends on:** task 23

**Goal:** Prometheus, Loki, Tempo, Grafana and the Collector show the US-13 signals side by side.

**Acceptance criteria**
- [ ] An `observability/` local Compose project adds the Collector (with the allowlist processor that drops non-allowlisted attributes and the auto-instrumented URL attributes), Prometheus, Loki, Tempo and Grafana (behind authentication), plus the MailHog mail catcher.
- [ ] Grafana provisions data sources and the "US-13 journey" dashboard with a Prometheus pane, a Tempo pane and a Loki pane, filterable by environment and version; trace-to-logs links where available (`VERIFY:`).
- [ ] For submission the stack runs in local Compose only (running it on AWS is showcase X3).
- [ ] Check: the manual dashboard in Compose shows the three signals side by side and the MailHog service answers. (The `make test-compose` cases are task 25.)
- [ ] `make verify` passes.

**Out of scope:** the backend delivery worker (task 37); the `make test-compose` target and cases (task 25); the alert rule (task 26); the responder (task 28); AWS deployment of the stack (showcase X3).

> **PM → human: confirm before filing**
> 1. **New dependencies (images):** Collector, Prometheus, Loki, Tempo, Grafana, MailHog. Approve adding them to the local Compose observability project?
> 2. **Grafana auth** for local Compose — the `GRAFANA_ADMIN_PASSWORD` from `.env.example` (already listed). Confirm that is the intended source.

---

## Issue C-37 — task 37: backend top-tier owner notification and delivery

**Covers:** Application, US-8, US-13 · **Depends on:** tasks 10, 23, 24 · **Built inside C3, after 24 and before 25**

**Goal:** A new top-priority finding sends exactly one email to its owner from the backend, recorded as `notification.enqueue` and `notification.deliver` with one trace ID.

**Acceptance criteria**
- [ ] The backend delivery worker claims a pending `top tier` job, formats the plain-text labelled-field owner notification (`_docs/architecture.md` § Routing and notifications / § Security boundaries), builds headers from finding id and tier only (CR/LF in a header value is rejected), and defangs any scheme / `www.` / domain-shaped token in advisory text.
- [ ] It sends once per finding lifecycle, records `sent`/`failed` (a failed job retries on the next poll), and holds the job for an ownerless asset (E2).
- [ ] It records `notification.deliver` as a child span of the stored `notification.enqueue` `traceparent`, through task 23's allowlist helper, completing the US-13 journey in the backend.
- [ ] A mail-transport setting selects the MailHog route (dev/tests) or the SES route (AWS, via the instance role + one verified sender); a send from any address other than the verified sender is refused.
- [ ] Checks under `make test` (in-process sink, no Docker/AWS): `I-OWNER-SEND`, `I-OWNER-NOAWS`, `I-OWNER-ONCE`, `I-OWNER-HOLD`, `S-NOTIFY`, `I-OWNER-SENDER`. Under `make test-compose`: `I-OWNER-NOAWS` / `I-OWNER-SENDER` against MailHog. (`T-JOURNEY-BE` is task 25.)
- [ ] `make verify` passes.

**Out of scope:** the SES AWS wiring/first send (that is the human's AWS steps + task 37's `VERIFY:` items at deploy); the telemetry Compose test (task 25); the demo defect (task 28).

> **PM → human: confirm before filing**
> 1. **New dependencies:** MailHog (Compose service — overlaps task 24) and the AWS SDK client for SES. Approve?
> 2. **SES `VERIFY:` items** (sandbox verified-recipient rule, free allowance, `ses:SendEmail` resource/condition form, the SES region) are settled at the human's AWS step; confirm task 37's code can ship with MailHog proven and the SES path `VERIFY:`-marked until then.

---

## Issue C-25 — task 25: telemetry Compose test and CI job

**Covers:** Observability, US-13 · **Depends on:** tasks 19, 24 (and 37, built before)

**Goal:** `make test-compose` proves the shared trace ID and that excluded values never leave the Collector.

**Acceptance criteria**
- [ ] `make test-compose` with a per-job selector (`JOB=telemetry|alert|responder`; no `JOB` runs all three on the human's host) — a protected `Makefile` change, its own human-approved commit.
- [ ] The `telemetry` job runs `T-JOURNEY-BE`, `T-REFUSE`, `T-E6`, and the MailHog form of `I-OWNER-NOAWS` / `I-OWNER-SENDER`, querying Prometheus, Tempo and Loki.
- [ ] Check: `make test-compose JOB=telemetry` green in CI; `T-REFUSE` fails when `owner.email` is added to the allowlist.
- [ ] `make verify` passes.

**Out of scope:** the `alert` and `responder` jobs' cases (tasks 27, 29), though the selector is added here; the `T-JOURNEY` n8n variant (showcase).

> **PM → human: confirm before filing**
> 1. **Protected `Makefile`** change (the `test-compose` target + `JOB` selector) — its own human-approved commit. Confirm.

---

## Issue C-26 — task 26: US-14 alert metric and Grafana rule

**Covers:** Alerting on User Impact, US-14 · **Depends on:** tasks 10, 24

**Goal:** An undelivered top-tier finding fires exactly one alert naming the finding.

**Acceptance criteria**
- [ ] `vt_top_tier_notification_overdue{finding_id,tier}` from stored job state, `tier` from `NotificationJob.tier`; a constant global `0` series so `NoData` means only the backend/metric is down; a `sent` job's series kept 24h; held jobs never set the metric.
- [ ] The provisioned Grafana rule (`_docs/architecture.md` § Observability): 30-minute window, one instance per finding; destinations the responder webhook + human email for a finding alert, human email only for `NoData` (no `finding_id`); annotations carry the dashboard link, environment and version.
- [ ] Check: the rule shows 1 for a failed job and 0 for a sent job; no alert and no responder message on a system with no jobs. (`A-*` Compose cases are task 27.)
- [ ] `make verify` passes.

**Out of scope:** the `alert` Compose test (task 27); the responder that receives the webhook (task 28).

> **PM → human: confirm before filing**
> 1. No new open points. Confirm it is filed after C-24.

---

## Issue C-27 — task 27: alert Compose test and CI job

**Covers:** Alerting on User Impact, US-14 · **Depends on:** tasks 19, 25, 26

**Goal:** The `alert` job proves one firing, no second alert and the held-job exemption.

**Acceptance criteria**
- [ ] The `alert` job (`make test-compose JOB=alert`) adds the `A-*` cases: `A-FIRE`, `A-HELD`, `A-TIER`, `A-GAP` (both parts: an empty system fires nothing; a metric gap sends one email to the human sink and nothing to the responder sink), `A-RESOLVE` (a resolved message is not a second alert), and the backdated job.
- [ ] Check: `make test-compose JOB=alert` green in CI; `A-FIRE` red when the alert rule is removed.
- [ ] `make verify` passes.

> **PM → human: confirm before filing**
> 1. No new open points (the `Makefile` selector landed in C-25). Confirm.

---

## Issue C-28 — task 28: responder agent, webhook and demo defect

**Covers:** On-Call Agent, US-15 · **Depends on:** task 27

**Goal:** The responder wakes on the US-14 alert, reproduces the notification defect, fixes it and opens a pull request.

**Acceptance criteria**
- [ ] A responder container + Grafana webhook receiver in the local Compose observability stack (H6); bearer secret, repeat-fingerprint guard; one headless agent run per alert in a fresh checkout; read-only API + Loki tokens; branch `responder/<fingerprint>` + a pull request; every action logged.
- [ ] The `VT_DEMO_DEFECT=notify_no_fix` path in task 37's formatter and the production refusal (`_docs/architecture.md` § Responder agent).
- [ ] The false-positive rule (**if D4 approved**): on an alert with no reproducible defect, explain and change nothing.
- [ ] CI and `make test-compose` use `RESPONDER_MODE=stub`.
- [ ] Check: `P-DEMO-BE`, `P-PROD-REFUSAL`, `I-RESP-*` pass in `make test-compose JOB=responder` (stub); a test alert with no incident ends "no change" with an explanation.
- [ ] `make verify` passes.

**Out of scope:** the `responder` CI job + `P-FLAG-GONE` + the demo cleanup (task 29); the recorded real-runtime drill (task 39).

> **PM → human: confirm before filing (these GATE this issue)**
> 1. **D4** — approve the responder false-positive rule as a `specs.md` diff first (it is protected). This blocks filing task 28.
> 2. **Responder agent runtime** — choose it (a dependency). CI uses `RESPONDER_MODE=stub`; the real runtime is used only in task 39's recorded drill.
> 3. **`main` branch protection** that refuses the responder's push — confirm it is active.

---

## Issue C-29 — task 29: responder Compose test and demo cleanup

**Covers:** On-Call Agent, US-15 · **Depends on:** tasks 19, 27

**Goal:** The `responder` job proves the undelivered finding reaches its owner in the local demo, and the demo defect is removed.

**Acceptance criteria**
- [ ] The `responder` job (`make test-compose JOB=responder`) with the task 28 cases.
- [ ] `P-FLAG-GONE`: a script that fails the production-promotion workflow if `notify_no_fix` or `VT_DEMO_DEFECT` exists anywhere at the tag being promoted; tested against two fixture trees (one with, one without) under `make test`; its step added to the production workflow (task 18). It is **not** in `make test-compose` or the PR jobs, so the PR gate stays green while the demo defect exists.
- [ ] Check: `make test-compose JOB=responder` green; `P-FLAG-GONE` fails the promotion while the defect path exists and passes after the cleanup commit.
- [ ] `make verify` passes.

> **PM → human: confirm before filing**
> 1. Depends on task 28, so it follows C-28 (and thus the D4 / runtime prerequisites). Confirm filing after C-28.

---

## Issue C-38 — task 38: backend scheduler for the daily refresh and scheduled re-scan

**Covers:** Application, US-7, US-10 · **Depends on:** tasks 8, 10 (done) · **Independent — fileable now**

**Goal:** The backend refreshes KEV and EPSS every day and re-scans every asset after the refresh, with no manual action and no external workflow tool.

**Acceptance criteria**
- [ ] A scheduler inside the backend worker runs the `POST /signals/refresh` + `POST /scans` code once a day at 06:00 UTC, re-scores findings, then scans every asset with trigger `schedule`.
- [ ] A refresh moving a finding into the top tier creates its job via task 10's idempotency key, so a second run the same day makes no second job.
- [ ] Catch-up: at start, if the last completed run is >24h old (or none), run the refresh then the re-scan at once, then follow the 06:00 UTC schedule.
- [ ] Check (`I-SCHED`): a fake-clock + stubbed-feed test shows changed signals/ranks after the run, a re-scan of every asset, no outbound call outside the stubs, and a repeated run making no second notification job; a start 30h stale runs both at once, a start 10h stale runs nothing until 06:00 UTC.
- [ ] `make verify` passes.

> **PM → human: confirm before filing**
> 1. **Dependency:** a library scheduler would be a new dependency (ask); a clock-driven loop needs none. Which — approve a library (name it) or require the no-dependency loop?

---

## Issue C-39 — task 39: close-out (recorded drill, README, final re-audit)

**Covers:** On-Call Agent, Alerting, Observability, Deployment · **Depends on:** tasks 18, 21, 28, 29, 37, 38 · **Built last**

**Goal:** The evidence exists and is linked, the README lets a reviewer reach and run the project, and the whole rubric is re-audited.

**Acceptance criteria**
- [ ] **Recorded drill:** the human runs the local Compose demo (tasks 28, 29) once with the **real** responder runtime and records it; the agents write the drill runbook, the human performs the run, merge and recording. The recording shows: the metric at 1, exactly one alert naming the finding, a PR opened by the real runtime, the human merge, the owner email arriving at MailHog, and the alert resolving.
- [ ] **README close-out:** public URL section (dev/prod `sslip.io`), one-command start (`make dev` + the Compose command), rollback section (previous tag, deploy log, production workflow), a link to the recording, and the deployment/observability/responder sections.
- [ ] **Final re-audit:** the rubric auditor re-audits `main` and updates `_docs/rubric-evidence.md` (the Engineer does not edit that file); it shows all 12 criteria MET. `P-FLAG-GONE` passed before any prod promotion.
- [ ] A reviewer following the one-command start from a clean clone reaches the sign-in page.

> **PM → human: confirm before filing**
> 1. This is the last issue; it needs B6 (prod deploy), tasks 28/29/37/38 done, and the human for the recorded drill, the merge and the peer reviews. Confirm it is filed at the end.

---

## Summary for the human

- **9 issues** proposed (tasks 23-29, 37, 38, 39), one per task.
- **Build/file order:** 23 → 24 → 37 → 25 → 26 → 27 → 28 → 29 → 39; **38** any time.
- **Blocks to clear before task 28 (C-28):** **D4** (responder false-positive rule, a protected `specs.md` diff — still open), the **responder runtime** choice, and **`main` branch protection**.
- **Dependencies to approve:** OTel SDK (23); the observability images (24); MailHog + AWS SES client (37); the responder runtime (28); the scheduler library-or-loop choice (38).
- **Protected `Makefile`** commits: the `test-compose JOB` selector (25) and nothing else new in 27/29 beyond cases.
- Nothing is filed yet. On confirmation I will create the issues with these bodies and acceptance criteria, in build order, labelled for Milestone C, and record the filing in the roadmap check-in log.
