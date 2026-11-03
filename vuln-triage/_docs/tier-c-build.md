# Tier C build sheet (phase S4)

A single place that answers "what does milestone C_n build, what does it depend
on, which human step or decision unblocks it, and when is it done?" without
reading several documents at once.

Like [`_docs/tier-b-build.md`](tier-b-build.md), this sheet **consolidates and
points to** the authoritative sources; it does not restate design and adds no
new precedence rule. Where this sheet and a source differ, the source wins:

- **Per-task description:** [`_docs/tasks.md`](tasks.md) tasks 23-29, 37, 38, 39 — authoritative on task boundaries and build order.
- **Design:** [`_docs/architecture.md`](architecture.md) § Observability, § Responder agent, § Routing and notifications, § Security boundaries.
- **Order, checkpoints, decisions:** [`_docs/roadmap.md`](roadmap.md) § Tier C milestones (C1-C9), § Open decisions, § Score checkpoints.
- **Test cases and CI jobs:** [`_docs/testing.md`](testing.md) § Telemetry, § Alerting, § Responder, § CI jobs.

Tier C targets the last 5 of 24 points: Observability (2), Alerting on User
Impact (1), On-Call Agent (2). It takes the running total from an estimated 19
(after S3) to 24. **Every Tier C submission milestone runs on the local Compose
stack (H6)** — none waits for AWS (B4-B6), so Tier C can run in parallel with or
ahead of the AWS deployment work (`roadmap.md` § "Ordering if AWS is slow").

## Settled, and NOT settled, before Tier C starts

- **Observability stack is local Compose only (H6).** Deploying Grafana/responder on AWS is **future development** (X3 / milestone C4), not submission.
- **The backend sends the owner notification itself (H7).** n8n routing/reminders/digest are **future development** (X6 / milestone C1). Task 37 (backend delivery) is the submission path and is built inside C3.
- **⚠️ Open decision D4 (blocks C6):** the responder's false-positive rule ("on an alert with no reproducible defect, explain and change nothing") is an addition to US-15 in `specs.md`, which is **protected** — it needs a proposed diff and human approval **before** C6/task 28 is filed. Status: open (`roadmap.md` § Open decisions, row 8).
- **⚠️ Human prerequisites (see the table at the end):** the responder's agent **runtime** must be chosen before task 28 is filed, and `main` **branch protection** that refuses the responder's push must be active before C6. Both are the human's.

## Build-order note (important)

`tasks.md` numbers task 37 (backend delivery) and 38/39 last, but the build
order is **not** the numeric order:

- **Task 37 is built inside C3** — after task 24 (the stack + MailHog) and before task 25 (the telemetry Compose test), because `T-JOURNEY-BE` and the demo defect run through task 37's delivery path. Tasks 25/28 cannot list 37 in `Depends on:` (that line may only name a lower number), so their descriptions say so instead.
- **Task 38 (C9) can be built any time after task 10** — it needs only tasks 8 and 10, not the rest of Tier C.
- **Task 39 is built last** (the recorded drill + README + final re-audit), after the production deploy (task 18) and the responder demo (tasks 28, 29).

## Milestones

Submission milestones only. C1 and C4 are **future development** (built after S5) and are
listed at the end for completeness.

| # | Task(s) | Builds | Depends on | Human step / decision | Criterion | Done when (test) |
|---|---|---|---|---|---|---|
| C2 | 23 | Backend OpenTelemetry: SDK + FastAPI auto-instrumentation; the US-13 spans; `vt_notifications_total`, `vt_notification_delivery_seconds`, `vt_top_tier_notification_overdue`; JSON logs with `trace_id`; the **allowlist helper**; `service.name` / `deployment.environment` / `service.version`. Export is a no-op without a Collector, real span contexts always (A40). | S1 (task 10, 15) | add the OTel SDK deps (ask) | Observability | A unit test drops `owner.email`/`authorization`; a `notification.enqueue` span without a Collector gives a valid non-zero `traceparent` (the `T-JOURNEY-BE` / `T-REFUSE` Compose cases come in C3) |
| C3 | 24 (Compose half), **37**, 25 | The `observability/` local Compose stack (Collector with the allowlist processor, Prometheus, Loki, Tempo, Grafana with provisioned data sources + the "US-13 journey" dashboard, MailHog) **and** the backend delivery worker (task 37: one email per top-tier finding to MailHog, `notification.deliver` as a child of the stored `traceparent`). Then the `telemetry` Compose test (task 25). | C2 | add Grafana/Collector/MailHog images (ask) | Observability, Application | `T-JOURNEY-BE` + `T-REFUSE` pass in `make test-compose JOB=telemetry`; the three signals show side by side in local Grafana; a top-tier owner email reaches MailHog from the backend; auditor marks **Observability 2** |
| C5 | 26, 27 | The US-14 alert as code: the provisioned Grafana rule (`vt_top_tier_notification_overdue`, 30-min window, one instance per finding), notification policy and contact points (human email + responder webhook), annotations (dashboard link, environment, version). Then the `alert` Compose test (task 27). | C3 | — | Alerting on User Impact | `A-FIRE`, `A-HELD`, `A-TIER`, `A-GAP`, `A-RESOLVE` pass in `make test-compose JOB=alert`; auditor marks **Alerting 1** |
| C6 | 28 | The responder in local Compose: the Grafana webhook receiver (bearer secret, repeat-fingerprint guard) that starts one headless agent run per alert in a fresh checkout; the `VT_DEMO_DEFECT=notify_no_fix` path + production refusal; read-only API + Loki tokens; branch `responder/<fingerprint>` + a pull request; every action logged; the **false-positive rule (if D4 approved)**. `RESPONDER_MODE=stub` in CI. | C5; #50 contract (closed) | **D4 approved**; the **responder runtime** chosen; `main` branch protection active | On-Call Agent | `I-RESP-*` + stubbed `P-DEMO-BE` + `P-PROD-REFUSAL` pass in `make test-compose JOB=responder` (stub); a test alert with no incident ends "no change" with an explanation |
| C7 | 28 (live drill), 29, 39 | The end-to-end drill, run locally with the **real** responder runtime: `VT_DEMO_DEFECT=notify_no_fix` → job fails → metric 1 → one alert → responder PR → human merges → local check → delivered to MailHog → alert resolves; recorded (screenshots/short video). Then the cleanup commit removes the flag and `P-FLAG-GONE` passes in the production workflow before any prod promotion. | C6 | the human runs the drill, the merge and the recording; the real responder runtime | On-Call Agent, Alerting, Observability | the recording exists and the README links it; the flag is gone (`P-FLAG-GONE`); auditor marks **On-Call Agent 2** |
| C8 | 2 (evidence note), 39, #19 | Close-out: README sections for deployment, observability and the responder; #19 (AI usage report); the full rubric re-audit; the teardown plan ready for after grading; time reserved for the three peer reviews. | C7, B6 | the human runs teardown and the peer reviews | all | `_docs/rubric-evidence.md` at the final commit shows **all 12 criteria MET** |
| C9 | 38 | The backend scheduler: the daily KEV/EPSS refresh and the scheduled re-scan run inside the backend (replaces the n8n schedule for submission), with the 24-hour catch-up rule. | S1 (tasks 8, 10 only) | a library scheduler would be a dependency (ask); a clock loop needs none | Application | a fake-clock test shows changed signals/ranks after the scheduled run, a re-scan of every asset, and no second notification job on a repeated run (`I-SCHED`) |

## Note: the alert's `owner` annotation (course parity)

The course (Part 4) includes **owner** in the alert payload (service, environment,
version, owner, dashboard URL). Our C5 alert (task 26) carries the dashboard
link, environment and version but **not an owner**, on purpose: the alert's only
identifying label is the opaque finding id (tier is the one other label), so no
owner contact detail enters telemetry (the US-13 no-leak guarantee). For future development
parity a **non-PII** owner/team annotation (e.g. the asset's team name, never an
email) could be added — a deliberate, bounded choice, recorded here so it is not
an accidental omission. Default for submission: keep the alert minimal (no owner
field); revisit as a later enrichment (see X10 in `roadmap-future.md` for
the related host/RPS metrics).

### Future development (built after S5, not submission)

| # | Task(s) | Builds | Why future development |
|---|---|---|---|
| C1 | 33-36 | n8n routing, reminders, digest and workflow export | H7: the backend sends the notification for submission (task 37); n8n is item X6 |
| C4 | — | Deploy observability + responder on AWS, Grafana behind a login | H6: local Compose for submission; AWS is item X3 |

## Dependency chain (submission milestones)

```
S1 ──► C2 (task 23) ──► C3 (24 → 37 → 25) ──► C5 (26, 27) ──► C6 (28) ──► C7 (28 drill, 29, 39) ──► C8 (2, 39, #19)
                                                                                                  ▲
C9 (task 38) ── any time after task 10 ───────────────────────────────────────────────────────── B6 ─┘ (C8 also needs B6)
```

- The Observability/Alert/Responder line (C2→C7) is strictly ordered and all local-Compose, so it needs no AWS.
- **C9** is independent — build it any time after S1.
- **C8** is the only Tier C milestone that needs B6 (the production deploy) done, because it re-audits the whole rubric and writes the deployment README section.

## Open decision and human steps to clear before Tier C

| Item | Needed by | Owner | Notes |
|---|---|---|---|
| **D4** — the responder false-positive rule added to US-15 | C6 (before task 28 is filed) | human | `specs.md` is protected: propose the diff, get approval. Status: **open** (`roadmap.md` § Open decisions) |
| **Responder agent runtime** (Open question 9; the brief's LLM provider is the separate future-development item X4) | C6, and before task 28 is filed | human | A new dependency: ask before adding. CI uses `RESPONDER_MODE=stub`; the recorded C7 drill uses the real runtime |
| **`main` branch protection** that refuses the responder's push | C6 | human | The responder may open PRs, never push to `main`; already required by the architecture |
| OTel SDK, Collector, Grafana, Prometheus, Loki, Tempo, MailHog images | C2, C3 | agent asks, human approves | New dependencies; none exists for submission yet |
| The recorded drill, the merge, teardown and the three peer reviews | C7, C8 | human | Agents write the runbook; the human performs the run and records it |

## How Tier C scores (checkpoints)

From `roadmap.md` § Score checkpoints (estimates; evidenced points come from
`_docs/rubric-evidence.md`):

| After | Points | Adds |
|---|---|---|
| C3 | 21 | Observability 2 |
| C5 | 22 | Alerting 1 |
| C7 (end of S4) | 24 | On-Call Agent 2 |
| C8 (S5) | 24 | full re-audit shows all 12 MET |
