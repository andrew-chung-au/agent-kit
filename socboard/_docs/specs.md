# SOCBoard — Product Specification

Human-owned. This is the product description agents build against: the problem, users, journeys, requirements, scope, and invariants. The README is the short public summary; this is the detail behind it. Acceptance criteria for individual pieces of work live on the tracker issues, not here.

Planning context: produced with the process in `_docs/planning/01_planning.md`. Build process starts at `_docs/planning/02_development.md`.

## 1. Problem

Small security teams receive alerts from many sources (failed logins, malware detections, unusual network traffic) with no shared system. Alerts sit in inboxes, chats, and spreadsheets, which causes three failures:

- **No clear ownership** — two analysts work the same alert, or nobody does.
- **No record** — when an alert is closed, there is no trace of who decided what, or why.
- **Inconsistent priority** — each analyst judges severity differently, so urgent alerts wait behind noisy ones.

The core assumption to prove: a shared queue with consistent, rule-based severity and a recorded workflow makes triage ownership and history unambiguous.

## 2. Users

- **Analyst** — works the queue: claims alerts, adds notes, moves cases through the workflow.
- **Lead** — reviews the queue, reassigns cases, and reads the audit trail; can also claim and work a case like an Analyst.
- **Operator** — holds the cloud account and the secrets, approves infrastructure applies, and can tear the deployment down (Deploy phase).
- **Visitor** — opens the public URL and logs in as a seeded user (Deploy phase).

Authentication is minimal: the system is seeded with two Analyst accounts and one Lead account (hashed passwords, bearer token). Two Analysts are needed to show single ownership (a second claim is refused) and reassignment. Source systems are not users: they authenticate ingest with a separate API key set by environment variable, so the public ingest endpoint cannot be filled by anyone. Identity matters because single-ownership, reassignment, and the audit trail ("who decided what") are only meaningful when the system knows who is acting.

## 3. Primary journeys

1. **Ingest → Queue.** An alert arrives via the API, is scored by fixed rules, and appears in the shared queue within the target latency, sorted by severity then age.
2. **Claim → Investigate → Close.** An analyst claims an open alert, adds notes, and moves it `New → Investigating → Closed` with a required closing reason. Every step is recorded in the audit trail.
3. **Deploy → Public URL.** The Operator proposes a change by pull request; CI shows the Terraform plan; the Operator merges; CI passes and CD deploys; a Visitor opens the HTTPS URL and logs in as a seeded user; an alert ingested with the key appears in the queue within N = 5 s.

A Lead variant of journey 2: a Lead reassigns a claimed case to another analyst, and the reassignment is recorded.

## 4. Requirements (user stories)

Each story is a tracker issue; acceptance criteria are written on the issue. Priority uses MoSCoW; the Core Musts are Phase 1 and the Deploy Musts are Phase 2 (Section 6).

**Ingest & scoring**
- (Must) As a source system, I POST an alert (source, type, affected asset, timestamp, title, description) with the ingest API key so it enters the system; a missing or wrong key is refused.
- (Must) As the system, I assign severity on the scale Low, Medium, High, Critical from a fixed, explicit rule table (alert type × asset criticality) so severity is consistent and explainable. Asset criticality comes from a small seeded asset inventory (asset → criticality); an unknown asset counts as Medium criticality, and an unknown alert type gets a documented default severity.
- (Must) As an analyst, alert text is shown escaped and never executed, because alert content is untrusted.
- (Should) As a demoer, I trigger a synthetic alert generator so the board shows live activity.

**Queue**
- (Must) As an analyst, I see open alerts (every case not `Closed`, claimed or not) sorted by severity then age so the most urgent surface first.
- (Must) As an analyst, the queue reflects a new alert within the target latency (polling is acceptable).

**Triage workflow**
- (Must) As an analyst or Lead, I claim an open alert so I own it; an alert has at most one owner at a time. Claiming sets the owner only; moving the status is a separate, explicit step.
- (Must) As an analyst or Lead, I add notes to any open case, owned by me or not, so the team can share context; a note on a `Closed` case is refused.
- (Must) As the case owner (or a Lead), I move a case `New → Investigating → Closed`; closing requires a reason (true positive, false positive, or duplicate). Anyone else's status change is refused.
- (Must) As the system, I reject blocked transitions (e.g. closing a `New` alert) with a clear error — never silently allowed.
- (Should) As a Lead, I reassign a claimed case to another analyst.

**Audit**
- (Must) As a Lead, I read a case's audit trail in order, start to finish: every status change, assignment, and note records who, what, and when.
- (Must) As a Lead, I list closed cases (with their closing reason) separately from the open queue and open any of them, so a closed case's audit trail stays reachable.

**Deploy (Phase 2)**
- (Must) As a visitor, when the single container image runs with a database URL, I get the web app at `/` and the API under `/api` from one origin.
- (Must) As a visitor, a screen route such as `/cases/1` returns the web app's entry page, while a request under `/api` that matches no route returns the JSON 404 `not_found`, never the entry page.
- (Must) As an operator, I choose the database by environment variable: SQLite is the local default, Postgres the deployed one.
- (Must) As an operator, one Docker Compose command starts the app and Postgres, and the app waits for the database and its migrations.
- (Must) As a developer, integration tests run against the Compose stack, and an end-to-end test drives journeys 1 and 2 with two Analysts and a Lead.
- (Must) As an operator, the application is reachable at a public HTTPS URL on infrastructure that Terraform creates and one documented procedure removes.
- (Must) As an operator, on every push to `main` CI runs the tests, builds the image and runs the integration and end-to-end tests; CD deploys only if all pass, with a short-lived scoped credential (GitHub OIDC); pull requests never get a deploy credential.
- (Must) As an operator, infrastructure changes reach the cloud only through Terraform: a pull request shows the plan, and an apply from CI runs only on `main` after I approve it.
- (Must) As an operator, repeated failed logins for one username, or from one client, are slowed or refused for a time, with a fixed 429 or 401 answer that does not say whether the username exists. The limits are set by configuration, with defaults chosen in the issue.
- (Must) As an operator, a source system that exceeds a fixed ingest rate is refused with 429 and the excess alerts are not stored. The rate is set by configuration, with a default chosen in the issue.

**Cross-cutting**

The names below are those of `observability/CONTRACT.md`; a change to a name is made there first.
- (Must, DevOps phase) As an operator, the journey from an accepted `POST /api/alerts` to the first queue read that returns the case is measured by the histogram `socboard.alert.time_to_queue` (unit `s`, bucket bounds include 5), readable as `socboard_alert_time_to_queue_seconds_bucket`, and the counter `socboard.ingest.alerts` counts each ingest by `outcome` (`accepted` or `refused`). The synthetic probe measures the same journey from outside, as a user sees it, in the histogram `socboard.probe.time_to_queue` (unit `s`, the same bucket bounds), readable as `socboard_probe_time_to_queue_seconds_bucket`. The in-app histogram records only while the queue is being watched.
- (Must, DevOps phase) As an operator, one ingest sent with a chosen `traceparent` leaves the same 32-character lower-case hex trace id in the span `ingest.alert`, in the `trace_id` field of the log event `alert.ingested` and in the exemplar of `socboard.alert.time_to_queue`, and the span `queue.first_seen` links to `ingest.alert`.
- (Must, DevOps phase) As an operator, no alert title or description, case note, password, ingest key, token or account number is in any metric, span, log line, exemplar or resource attribute: each canary value of `observability/CONTRACT.md` section 8, planted in a request, is absent from everything Tempo, Loki and Prometheus stored.
- (Must, DevOps phase) As an operator, one make command starts the collector, Tempo (traces), Loki (logs), Prometheus (metrics) and Grafana, and the trace, the log lines and the metric of one ingest can be opened in Grafana.
- (Must, DevOps phase) As an operator, one alert, `QueueLatencyOverSLO` (label `severity` = `page`), fires when the 95th percentile of the probe's `socboard_probe_time_to_queue_seconds_bucket` over 5 minutes is above 5 seconds for 2 minutes and the probe made at least 20 measurements in those 5 minutes, and carries the annotations `summary`, `environment`, `version`, `owner` and `dashboard_url`.
- (Must, DevOps phase) As an operator, when `QueueLatencyOverSLO` is firing, an on-call agent opens one pull request with its fix; it never merges a pull request and never pushes to `main`.

## 5. Expected behavior & invariants

These are the product invariants; agents must keep them (they also appear in `AGENTS.md`):

- A new alert appears in the queue within **5 seconds (N = 5s)** with a severity. The client polls the queue every **3 seconds** (configurable via env var); with ingest + rule scoring taking milliseconds, worst-case visible latency is the poll interval plus processing, comfortably under N. N = 5s is both the product SLO and the threshold the observability alert fires on, so it is chosen with headroom rather than as a best case.
- An alert has **at most one owner** at a time, including under concurrent claims: of two simultaneous claims, exactly one wins, on any supported database (SQLite and Postgres).
- Closing a case **requires a reason**.
- The audit trail for a case can be read **in order**, start to finish, and is **append-only**: entries are never edited or deleted.
- Alert text is **untrusted**: escaped when shown, never treated as instructions.
- **No machine learning in the critical path.** Every severity and every status change is explainable and testable.
- **Secrets come only from the environment**, set from the cloud secret store at deploy time: the ingest key, the seeded passwords and the database password never appear in the repository, the image, the frontend bundle or Terraform state outputs. In deployed mode a missing secret stops the app at start-up.
- **The public deployment holds synthetic data only** (Section 7).
- No long-lived cloud key exists in the repository or in GitHub secrets. CI cannot change its own permissions; the human applies the definitions of CI's roles.

## 6. Scope

This release is the whole graded project, aiming for full marks on every criterion in `_docs/planning/rubric.md`. It is built in three phases. Only the current phase is detailed; each later phase is an outline here and is detailed (spec revision, then backlog review) when the phase before it is done, so its plan fits what was actually built.

**Phase 1: Core (now)** — the Core Must-have stories above: API ingest, rule-based scoring, seeded minimal auth, the sorted queue with polling, the claim/investigate/close workflow with blocked-transition errors, notes, and the audit trail. The end-to-end full-stack application, tested with unit, frontend and integration tests, running locally with one command.

**Phase 2: Deploy (outline)** — following `_docs/planning/03_deployment.md`: one container image, Postgres in place of SQLite, login attempt limiting and ingest rate limiting, the full system including the database started with one Docker Compose command, end-to-end tests, a deployment reachable at a public URL, and CI/CD that runs the tests and deploys. The boundary: one environment, one server and one Postgres, on AWS, created by Terraform. Container start order uses the Postgres health check in Compose, while `GET /api/health` stays database-free (`openapi.yaml`). The backend binds a non-loopback address only when the container image opts in explicitly; `make backend-run` stays loopback-only and refuses any other host.

**Phase 3: DevOps (outline; the observability, alert and on-call stories are detailed in Section 4)** — following `_docs/planning/04_devops.md`: separate dev and prod with automatic deploy to dev and a manual promotion to prod (with a rollback path), one key journey instrumented with metrics, traces and structured logs sharing a trace id and viewable in a self-hosted UI, one alert on real user impact (`QueueLatencyOverSLO`), and an on-call agent that wakes on that alert and opens a pull request with the fix, never merging it.

**Target Enhancements (Could)** — follow-on work after the three phases, never ahead of them (see roadmap for ordering):
- Synthetic alert generator and Lead reassignment (the Should-haves), if not already pulled into Core.
- A LangGraph triage step that *suggests* a severity and a summary for an analyst to confirm — advisory only, never in the critical scoring path.
- n8n for intake and escalation workflows.
- An MCP server for querying cases and checking a vulnerability tracker for known exposures.

## 7. Non-goals (Won't have — this release)

- Real log sources or real customer data (all data is synthetic).
- Automated response actions to security alerts. (The on-call agent of Phase 3 acts on SOCBoard's own latency alert, not on a security alert, and only opens a pull request.)
- Any AI-generated verdict in the critical path (the LangGraph step, when added, is advisory only).
- Multi-tenant orgs, SSO, or a full user-management system.
- Rich RBAC beyond the Analyst/Lead distinction.
- In the Deploy phase: a second environment and promotion, rollback (Phase 3), autoscaling, load balancing, a managed or replicated database, a custom domain, high availability, and SSH access to the server.
- In the DevOps phase: a managed or hosted telemetry service (telemetry is self-hosted), automatic merge of the on-call agent's pull request, and any alert other than `QueueLatencyOverSLO`.

## 8. Documentation approach

Documentation is written for reference — this spec, the roadmap, the agent-team docs, and the tracker — not as a prompt transcript. We do **not** keep an AI-usage or prompt log. Evidence that agents did the work is the normal tracker trail: issues carry acceptance criteria, agents comment on an issue when they start and finish, and commits/PRs reference the issue number.
