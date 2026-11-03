# VulnTriage task backlog (Stage 5)

Numbered, dependency-ordered tasks for the build. Task 1 is the empty project with one passing test. The submission scope is Milestones A-C plus tasks 37, 38 and 39 (the backend's own owner notification, its scheduler, and the close-out); it follows the submission track of decisions H2-H7 (Terraform, one server for dev and prod, images in GHCR, `sslip.io` hostnames, observability and the responder in local Compose, the backend delivering the top-tier notification and running the schedule). Tasks 30-36 (LLM brief, MCP server, n8n) are in the final "Future development (after submission)" section and are built after submission. Numbers are never reused or renumbered: 37, 38 and 39 are numbered after 36 and build earlier than the future-development tasks. No submission task depends on a future-development task. The dependency chain is the final section.

# Milestone A — Tier A (12 points)

## 1. Empty project with one passing test
Goal: A runnable skeleton with one passing test and no product behaviour.
Description: Creates the `backend/` FastAPI package with `pyproject.toml` and `uv.lock`, the `tests/` directory and the `Makefile` test target (the Makefile is a protected file, so that change is its own human-approved commit), and keeps the existing `frontend/`; there is no endpoint, model, UI flow or business logic. It also creates the test harness that every later task reuses: the network guard behind `U-NET` and `I-NET` (any outbound HTTP call fails the test; the stub settings `LLM_MODE=stub` and `RESPONDER_MODE=stub` are the only accepted modes), an in-memory SQLite test fixture, and an empty `tests/fixtures/` directory with `fixtures/MANIFEST.md`. The first fixtures are recorded in task 4. The new tests are `tests/test_smoke.py` and the guard's own tests `U-NET` and `I-NET`, and the exact command that runs them is `make test`; the existing frontend suite stays under `make frontend-test` and is not part of this task's pass condition. Reviewers confirm `make test` passes, a test that makes a live outbound call fails under the guard, and the commit contains no route, table or screen.
Depends on: none
Covers: Application (scaffold), Testing (test harness)

## 2. planning evidence and tracker hygiene
Goal: The four documentation criteria are evidenced without changing the record.
Description: Checks the README problem statement, the public issue tracker and the `_docs/agent-team.md` plus `AGENTS.md` links to `_docs/agent-kit/` using `_docs/project-brief.md`, `_docs/specs.md` and `_docs/agent-team.md`. It records a short evidence note under this task in `_docs/tasks.md` with the `Covers:` line; it creates, edits or closes no issue, posts no comment and rewrites no document, and a needed fix is a follow-up note. The check is that the note names one public URL or file path for each of Problem Description, Product Specification, Agent Team Specification and Context Management.
Depends on: none
Covers: Problem Description, Product Specification, Agent Team Specification, Context Management

Evidence note (2026-10-23): the four documentation criteria are each evidenced by one file path in this repository.

| Criterion | Evidence (one path per criterion) | What it shows |
|---|---|---|
| Problem Description | `README.md` | States the problem, the system functionality and the expected behaviour (the "The problem", "What VulnTriage does" and "Expected behaviour" sections). |
| Product Specification | `_docs/specs.md` | The product spec: user stories US-1..US-15, each with an "Acceptance" line, and the edge cases. The public task tracker is the repository's GitHub Issues (e.g. the Milestone A build issues #74-#88), where the issues carry acceptance criteria and role-labelled PM/Engineer/QA/Orchestrator comments show the agents used the tracker. |
| Agent Team Specification | `_docs/agent-team.md` | Defines the six agent roles plus the human, what each may write, the tool and model per role, QA independence, and the issue lifecycle and hand-over between roles. |
| Context Management | `AGENTS.md` | Exists and points to the modular docs under "Where to read more": `_docs/project-brief.md`, `_docs/specs.md`, `_docs/rubric.md`, `_docs/roadmap.md`, `_docs/agent-kit/process.md`, `_docs/agent-kit/team/`, `_docs/agent-kit/procedures/`, `_docs/agent-team.md` and `_docs/ai-usage-log.md`. `CLAUDE.md` imports `AGENTS.md`. |

No follow-up fix was needed: each of the four source files exists and names the required content. This note is the only change to `_docs/tasks.md`; no other task entry, document, issue or comment was changed by this task.

## 3. Backend data model and SQLite persistence
Goal: Assets, dependencies, findings, lifecycles, jobs and audit entries persist in SQLite.
Description: Implements the Data model and enums from `_docs/architecture.md` in SQLAlchemy over SQLite, including the `Asset`, `Dependency`, `Finding`, `Lifecycle`, `NotificationJob` (with its `tier` field, the tier when the job was created) and `AuditEntry` tables and their constraints. It adds no API endpoint and seeds no data. The check is the backend unit suite in `make test` showing the migration creates the schema and an audit entry records who, when and the previous value.
Depends on: 1
Covers: Application

## 4. Asset registration and repository ingestion
Goal: `POST /assets` registers an asset and the first scan reads its dependency files.
Description: Implements the `POST /assets` route and the GitHub contents read with the read-only token, then the `uv.lock`, `requirements.txt` and `package-lock.json` parsers for US-1 and US-2 from `_docs/architecture.md` § Ingestion and matching. It also builds the background worker and the job table (A4) that run the first scan after `POST /assets` returns; tasks 8, 37 and 38 reuse them. It records the first fixtures, the GitHub contents responses for the three lockfile formats under `tests/fixtures/github/contents/`, and adds the `make record-fixtures` target (a Makefile change, protected, its own human-approved commit; the human runs it because it calls the live API with their token; testing T-A2), with one `MANIFEST.md` row per capture. The human provides the read-only token; the session and CSRF guard is added in task 9. The check is the `U-UV`, `U-REQ`, `U-NPM` and `I-ASSET` cases in `make test`, plus a forced `repository unavailable` scan and a registration whose first scan is still pending when the `201` returns.
Depends on: 3
Covers: Application, US-1, US-2

## 5. OSV matching and fixed version
Goal: Findings record the primary id, all aliases and the fixed version for this dependency.
Description: Calls OSV only through the reviewed endpoints in `_docs/architecture.md` § External data sources and derives the fixed version from every merged range, creating one finding per (asset, package, vulnerability identity) for US-3 and E9. The harness of task 1 stubs OSV and fails on any outbound call; this task records the OSV fixtures under `tests/fixtures/osv/` with `make record-fixtures` (the human runs it) and a `MANIFEST.md` row for each. The check is `U-FIXED`, `U-ALIAS`, `U-WITHDRAW` and `I-FINDINGS` in `make test`.
Depends on: 4
Covers: Application, US-3

## 6. KEV and EPSS enrichment
Goal: Every finding shows exactly one KEV value, an EPSS score or `n/a`, and stale markers.
Description: Implements the KEV and EPSS fetches, the `Signal` rows and the `KEV: listed`, `KEV: not listed` and `KEV: n/a (no CVE)` values with `kev_stale` and `epss_stale` for US-4, E3 and E11, following `_docs/architecture.md` § External data sources and § Data model. It uses the reviewed source URLs and stubbed feed fixtures, recorded under `tests/fixtures/kev/` and `tests/fixtures/epss/` with `make record-fixtures` (the human runs it) and a `MANIFEST.md` row for each. The check is `U-KEV`, `U-EPSS`, `U-FEED` and `I-FINDINGS` in `make test`.
Depends on: 5
Covers: Application, US-4

## 7. Deterministic ranking and rank reason
Goal: Findings get a deterministic tier, a total order and a rank reason.
Description: Implements the `P1`-`P4` rules, the EPSS then criticality then age then id tie-breaks and the worked example from `_docs/architecture.md` § Prioritisation for US-5, with no AI. The check is `U-TIER`, `U-TIE` and `I-RANK` in `make test` reproducing the example order `fnd-0001`, `fnd-0002`, `fnd-0004`, `fnd-0005`, `fnd-0003`, `fnd-0006`. No threshold or enum is added beyond that section.
Depends on: 6
Covers: Application, US-5

## 8. Finding status lifecycle, re-scan and audit trail
Goal: Re-scans set `fixed`, `withdrawn` or reopen findings, and every change is audited.
Description: Implements the status transitions in `_docs/specs.md` E4, E7 and E8 and the audit entries with who, when and previous value for US-10 and US-11, including the manual re-scan. The check is `U-WITHDRAW`, `I-RESCAN` and the audit part of `I-RISK` in `make test`.
Depends on: 7
Covers: Application, US-10, US-11

## 9. Session authentication and the frontend API
Goal: The frontend operations work with the session cookie, CSRF header and owner-match rule.
Description: Implements `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`, `GET /findings`, `GET /findings/{id}`, `GET /assets`, `GET /assets/{id}`, `POST /assets`, `PATCH /assets/{id}`, `POST /assets/{id}/rescan` and `POST /findings/{id}/risk-acceptance` from `_docs/api.md`, adding the session guard to task 4's route and the role rules of `_docs/api.md` § Authorization (registration and update for a `security lead` only; re-scan for a `security lead` or the matching `asset owner`). `PATCH /assets/{id}` changes the owner name, owner email, criticality or internet-facing flag, writes one stored audit entry per changed field, re-scores the asset's findings, and releases the asset's jobs held as `held: ownerless` or `held: owner email missing` when an owner email is set (the delivery of task 37 then sends them). It also builds the operator command that creates a dashboard user (username, display name, email, role and a password read from a prompt, never from the command line; there is no sign-up), which the dev, prod and local demo environments need. The check is `I-AUTH-SESSION` (including the role refusals: an `asset owner` registering or updating an asset gets `403`), `I-ASSET-UPDATE` and `I-RISK` in `make test`, plus a user created by the command signing in while the stored password value is an Argon2id hash and not the password.
Depends on: 8
Covers: Application, US-1, US-11

## 10. Service API and notification jobs
Goal: The submission service operations work, the contract's future-development operations exist as stubs, and the backend creates `top tier` notification jobs.
Description: Implements `POST /signals/refresh` and `POST /scans` (the code the backend scheduler of task 38 also calls in-process, behind the n8n bearer allowlist) and the two `/responder/` operations from `_docs/api.md`, with the bearer allowlists. It also creates `top tier` NotificationJobs with the lifecycle idempotency key from `_docs/architecture.md` § Routing and notifications and a `traceparent` from the `notification.enqueue` span; it creates no `signals changed` job (the E8 notice is future development, human decision 2026-10-22). The future-development operations (the three `/notification-jobs` operations, `GET /reports/weekly-digest` and the three `/mcp/` operations) are contract-only stubs: each is registered with its documented security, parameters and response statuses so the conformance test of task 14 can compare all operations, and returns the documented responses (`401` and `403` from the allowlist, `404` and `422` where documented, an empty list or an empty documented shape on `200`), with no claim, report, digest or MCP logic; their behaviour belongs to future-development tasks 32-35. It ships no n8n workflow. The check is `I-RESP-*` and `I-SIGNALS` in `make test`, plus the job-creation assertion of `I-OWNER-ONCE` (a second refresh creates no second `top tier` job; its email part is checked in task 37).
Depends on: 9
Covers: Application, US-8, US-15

## 11. Frontend dashboard read views
Goal: The dashboard talks to the real backend, shows assets and ranked findings with status, rank reason and brief marker, and starts with one local command.
Description: The screens and the mock service already exist (roadmap steps 9, #34, #45), so this task connects them to the backend. It implements the real `Services` over `fetch` in `frontend/src/services/` for US-1, US-4, US-5 and US-6: requests send the session cookie, every non-GET request sends `X-Requested-With: XMLHttpRequest`, and an `Error` body is mapped to the five service error codes. It removes the mock from the production wiring (the mock stays only as a vitest fixture) and fixes how the SPA reaches the API: one origin everywhere, so the backend needs no CORS. In development the Vite dev server proxies the API paths to the backend; in Compose the frontend container's web server proxies them (task 15) and on AWS the reverse proxy does (task 17). The screens show owner or ownerless, criticality, internet-facing, KEV and EPSS, dependencies, rank reason and `brief` or `briefStatus`; no API field is added beyond `_docs/api.md`. It also adds `make dev`, the Application criterion's single local command: it starts the backend on SQLite and the frontend dev server together, with no Docker (a Makefile change, protected, its own human-approved commit; because AGENTS.md wants long-running processes behind `<name>-start` and `<name>-stop` targets, the same commit adds `make dev-start` and `make dev-stop`, which record and stop only their own process IDs). The check is the `F-ASSET` and `F-STATUS` vitest cases under `make frontend-test` and `make frontend-typecheck`, a vitest case showing the real service sends the cookie and the CSRF header and maps a `403` to `forbidden`, and `make dev` serving a sign-in page whose login reaches `POST /auth/login` on the backend.
Depends on: 9
Covers: Application, US-1, US-4, US-5, US-6

## 12. Risk acceptance, audit trail, manual re-scan and asset edit in the dashboard
Goal: A signed-in human can accept risk with a reason, see the audit trail, request a re-scan, and a security lead can correct an asset's owner and attributes.
Description: Implements the dashboard write path for `POST /findings/{id}/risk-acceptance`, `POST /assets/{id}/rescan` and `PATCH /assets/{id}` from `_docs/api.md` for US-1, US-10 and US-11, rejecting an empty or whitespace-only reason and showing who, when and the previous value. It adds `updateAsset(assetId, input): Promise<Asset>` to the `Services` interface, the mock and the real service, an edit form for the owner name, owner email, criticality and internet-facing flag shown to a `security lead` only, and hides the register and edit controls from an `asset owner`. The check is `F-STATUS` and `F-ASSET` (edit form, owner role hidden) plus `I-RISK` in `make test` and `make frontend-typecheck`.
Depends on: 11
Covers: Application, US-1, US-10, US-11

## 13. Backend test layers and stored fixtures
Goal: `make test` is confirmed as the single command that runs every backend unit and SQLite integration case, and the fixture set is complete.
Description: This is the CI-facing consolidation; the harness, the network guard and the first fixtures already exist (tasks 1, 4, 5 and 6, which each add their own `U-*` and `I-*` cases to `make test`). It checks that `make test` runs the backend unit and SQLite integration layers together with `make frontend-test` for `make verify`, adds the project-authored `tests/fixtures/malicious/advisory.json` for `S-FIXTURE`, and completes `fixtures/MANIFEST.md` so every fixture in the `_docs/testing.md` inventory has a row. The `unit` and `sqlite-integration` PR jobs are added in task 19. The check is `make test` with `U-NET` and `I-NET` still failing on any outbound HTTP call, and a yes/no read of the `_docs/testing.md` fixture inventory against `fixtures/MANIFEST.md` finding no fixture without a row.
Depends on: 10
Covers: Testing

## 14. OpenAPI conformance and validation
Goal: A backend test fails when FastAPI's contract differs from `_docs/openapi.yaml`.
Description: Adds the conformance test over every path, method, parameter, request and response schema and security requirement (all 22 operations, future-development stubs included), and keeps `make openapi-validate` as the contract check; the `openapi-validation` PR job is added in task 19. It also adds `GET /health`, the infrastructure endpoint outside the contract that task 15's health checks use, and the conformance test excludes it by name (`I-CONTRACT`). The check is a deliberate contract mismatch failing the test while `make openapi-validate` exits 0 on the reviewed file, and `I-CONTRACT` showing that `/health` is excluded by name while an extra path that is not in the contract still fails the test.
Depends on: 10
Covers: Application, Testing

# Milestone B — Tier B (19 points)

## 15. One-command Compose stack
Goal: Docker Compose starts the frontend, backend and Postgres with one command.
Description: Adds the Dockerfiles and the project Compose file for the frontend, backend, Postgres and migrations (the frontend container serves the built SPA and proxies the API paths to the backend, one origin, as task 11 assumes), with the `db` service and the service names fixed by `_docs/testing.md` (`ASSUMPTION: T-A1`); the Collector, the other observability services and the MailHog mail catcher arrive in task 24, and n8n is a future-development task (33). The check is `docker compose up` starting the stack with no manual per-service step and the frontend reading the API on the human's host or in CI. No image is pushed. This task also creates a committed `.env.example` that lists setting and secret names only, with no values, which a reviewer copies to a git-ignored `.env` before starting the stack; it lists only what the submission needs, as a whole (tasks 24 and 28 use the names already listed): the database password, the repository read token, `RESPONDER_API_TOKEN`, the Grafana admin password, the responder's LLM key, and the stub-mode switches such as `LLM_MODE=stub` and `RESPONDER_MODE=stub` (task 15 chooses the names that the documents do not fix); the future-development settings are not in it: the backend's LLM key, MCP (`MCP_API_TOKEN`), n8n (`N8N_API_TOKEN`) and tracker tokens, and SMTP credentials, which do not exist for submission.
Depends on: 14
Covers: Containerization

## 16. Real-Postgres integration tests
Goal: `make test-integration` runs the integration cases on Postgres in the test-owned Compose project.
Description: Adds the `vt-test` setup, migrations, transaction isolation and committed fixtures from `_docs/testing.md` § Integration tests, and the `postgres-integration` job target. The job is added to the pipeline in task 19; it runs in CI or on the human's Docker host. The check is `make test-integration` green and `E-GUARD` refusing a database or host that is not the test one.
Depends on: 15
Covers: Testing

## 17. AWS infrastructure on one server and the dev environment
Goal: The dev environment is reachable at a public HTTPS `sslip.io` URL on one AWS server.
Description: Writes the Terraform modules (state bucket bootstrap, GitHub OIDC deploy roles, and the one server with its Elastic IP, instance role, EBS volume and bootstrap) from `_docs/architecture.md` § Deployment, adds the push-to-`main` build-once job that tags the images and pushes them to GHCR with the workflow's `GITHUB_TOKEN`, and runs the `dev` Compose project behind the reverse proxy at `dev.<elastic-ip>.sslip.io`. The deploy-role Terraform accepts an already-existing GitHub OIDC provider in the account instead of failing to create a second one (one provider per URL per account; `VERIFY:`). The nightly stop schedule has an on/off switch (a Terraform variable, on by default) that the human turns off while graders may visit. It deploys the same image that Compose uses; the automatic deploy on merge is task 21. Terraform is a tool the human approves before it is installed. The human creates the AWS account resources and the secrets, runs the bootstrap and the first `terraform apply`, and performs the first deploy; the agent only writes the Terraform and the runbook. The check is the dev URL answering the frontend and the deploy log naming one image digest.
Depends on: 15
Covers: Deployment

## 18. Production Compose project and manual promotion
Goal: The production environment runs the same image digest as dev on the same server and is promoted only by a human.
Description: Adds a second Compose project (`prod`) and the hostname `app.<elastic-ip>.sslip.io` on the server from task 17, the manual production workflow (`workflow_dispatch` in the `production` environment, the human as the required reviewer, an image tag input that defaults to the one running in dev, nothing rebuilt) from `_docs/architecture.md` § Deployment, the production runbook and the rollback step. The human creates the production secrets, approves each production run and runs teardown. The check is the production URL, the same image digest in `dev` and `prod`, and a rollback to the previous tag recorded in the deploy log.
Depends on: 17
Covers: Deployment, CI/CD

## 19. CI test pipeline
Goal: Every pull request runs the test jobs before any deploy.
Description: Adds the `unit`, `sqlite-integration`, `frontend`, `openapi-validation` and `postgres-integration` jobs to the GitHub Actions workflow from `_docs/testing.md` § CI jobs, using the targets from tasks 13, 14 and 16. The check is a pull request that fails on a broken test in each job and passes on `main`; no job needs a live feed or a secret.
Depends on: 14, 16
Covers: CI/CD

## 20. Light security scan
Goal: `make security-scan` fails on high or critical findings in the app's own dependencies.
Description: Adds the dependency audit target and the `security-scan` PR job from `_docs/testing.md` § Light security scan; the tools are a dependency and the human approves adding them. The check is `C-FIXTURE-VULN` failing and `C-FIXTURE-CLEAN` passing, with lower findings reported only.
Depends on: 19
Covers: CI/CD, Testing

## 21. Automatic dev deploy
Goal: A merge to `main` deploys the `dev` project automatically when the tests pass.
Description: Adds the deploy step that runs after the push-to-`main` build in task 17 and the test jobs in task 19: the workflow assumes the dev deploy role and runs the deploy on the server for the `dev` Compose project only, by image tag, from `_docs/architecture.md` § Deployment, and records the tag and digest in the deploy log. The manual production promotion is part of task 18 (split per roadmap D7), so this task does not wait for the production project. The deploy step first reads the server's state: when the server is stopped (the nightly stop) it does not call the server and the workflow ends with a visible "dev deploy skipped: server stopped" summary that the human acts on by starting the server and re-running the workflow; the human turns the nightly stop off while graders may visit (`_docs/aws-setup.md` step 10). The check is a merge updating `dev` without a rebuild, a red test leaving the previous version running, and a merge while the server is stopped ending in the skipped-and-reported summary (not a pass and not a failed deploy).
Depends on: 17, 19
Covers: CI/CD

## 22. Pilot seed data
Goal: The pilot assets are registered through the API so real findings appear.
Description: Adds the pilot seed list from `_docs/architecture.md` A38/A41 with the human's repositories and OWASP Juice Shop, using the A41 fallback if Juice Shop lacks a supported lockfile. The human supplies the exact repository URLs; the task registers each asset through `POST /assets` and never writes to the database. The check is each asset showing a scan status and at least one finding on the dev environment.
Depends on: 4, 17
Covers: US-1, US-2

# Milestone C — Tier C (24 points)

## 23. OpenTelemetry instrumentation and the exclusion helper
Goal: The scan-to-notification journey emits one trace, metric and log with a shared trace ID, with exclusions enforced in code.
Description: Instruments `scan.run` and its children and the `notification.enqueue` span with its stored `traceparent` from `_docs/architecture.md` § Observability (the backend's own delivery in task 37 records `notification.deliver` as the child span), writing attributes and log bodies only through the allowlist helper. Only export is a no-op when no Collector endpoint is configured, per A40: the SDK still creates real span contexts, so the stored `traceparent` of a job is valid in `make test`. The check is a unit test dropping `owner.email` and `authorization`, and a unit test showing a `notification.enqueue` span without a Collector endpoint gives a valid non-zero `traceparent`; the `T-JOURNEY-BE` and `T-REFUSE` Compose cases are added in task 25. Gap found later (task 25): this task instrumented the allowlist helper and stored the traceparent, but left `log_event` writing stdout only (no OTLP log export — fixed in #174) and `create_app` wiring no feed clients (a deployed scan matched nothing — fixed in task 40/#172). The task-23 check unit-tested the helper, not that signals leave the process; the lesson for later telemetry checks is to assert the signal reaches the backend, not only that the in-code helper behaves.
Depends on: 10, 15
Covers: Observability, US-13

## 24. Observability stack and the US-13 Grafana dashboard
Goal: Prometheus, Loki, Tempo, Grafana and the Collector show the US-13 signals side by side.
Description: Adds the Collector processors and the Compose observability services (Prometheus, Loki, Tempo, Grafana and the Collector) from `_docs/architecture.md` § Observability, with Grafana behind authentication, and the MailHog mail catcher as a Compose service (a dependency, ask before adding) that task 37 and the Grafana email contact point send to in development and tests. For submission the stack runs in local Compose only; running it on AWS is a future-development item (X3 in `_docs/roadmap-future.md`). It provisions the "US-13 journey" dashboard with a Prometheus pane, a Tempo pane and a Loki pane. The check is the manual dashboard in Compose showing the three signals side by side and the MailHog service answering; the `make test-compose` cases are added in task 25.
Depends on: 23
Covers: Observability, US-13

## 25. Telemetry Compose test and CI job
Goal: `make test-compose` proves the shared trace ID and that excluded values never leave the Collector.
Description: Creates the `make test-compose` target with a per-job case selector (`make test-compose JOB=telemetry`, `JOB=alert` or `JOB=responder`; with no `JOB` it runs all three on the human's host; a Makefile change, protected, its own human-approved commit) so each CI job runs only its own cases, and adds the `telemetry` job and the `T-JOURNEY-BE`, `T-REFUSE` and `T-E6` cases from `_docs/testing.md` § Telemetry, querying Prometheus, Tempo and Loki (`T-JOURNEY`, the n8n version, is future development), plus the MailHog form of `I-OWNER-NOAWS` and `I-OWNER-SENDER`. `T-JOURNEY-BE` needs the delivery path of task 37, which is built before this task (see Build order under Dependency chain). The check is `make test-compose JOB=telemetry` green in CI and `T-REFUSE` failing when `owner.email` is added to the allowlist. Build note (2026-10-24): task 25 ships the selector and `T-REFUSE` only; the containerized-backend-delivers cases (`T-JOURNEY-BE`, `T-E6`, the MailHog `I-OWNER-*` forms) move to task 40 (#172), which wires the feed clients and the `VT_FEEDS` fixture mode they need (a host-process delivery would make `I-OWNER-NOAWS`/`I-OWNER-SENDER` hollow). The negative check is recorded against both allowlists: the Collector allowlist (telemetry job red) and the code allowlist (the task-23 unit test red).
Depends on: 19, 24
Covers: Observability, US-13

## 26. US-14 alert metric and Grafana rule
Goal: An undelivered top-tier finding fires exactly one alert naming the finding.
Description: Implements `vt_top_tier_notification_overdue{finding_id,tier}` from stored job state, with the `tier` label taken from `NotificationJob.tier` (the tier when the job was created), a constant global `0` series so that `NoData` means only that the backend or metric is down, and a `sent` job's series kept for 24 hours; and the Grafana rule from `_docs/architecture.md` § Observability, with the 30-minute window, one instance per finding, the responder webhook plus human email destinations for a finding alert, and the human email only for the `NoData` alert (no `finding_id`). Held jobs never set the metric. The check is the provisioned rule showing 1 for a failed job and 0 for a sent job, and no alert and no responder message on a system with no jobs; the `A-*` Compose cases are added in task 27.
Depends on: 10, 24
Covers: Alerting on User Impact, US-14

## 27. Alert Compose test and CI job
Goal: The `alert` job proves one firing, no second alert and the held-job exemption.
Description: Adds the `alert` job and the `A-*` cases from `_docs/testing.md` § Alerting to `make test-compose`, including the backdated job, the rule that a resolved message is not a second alert, `A-TIER` (the job's recorded tier) and both parts of `A-GAP` (an empty system fires nothing; a metric gap sends one email to the human sink and nothing to the responder sink). The check is `make test-compose JOB=alert` green in CI and `A-FIRE` red when the alert rule is removed.
Depends on: 19, 25, 26
Covers: Alerting on User Impact, US-14

## 28. Responder agent, webhook and demo defect
Goal: The responder wakes on the US-14 alert, reproduces the notification defect, fixes it and opens a pull request.
Description: Adds the responder container and Grafana webhook receiver to the local Compose observability stack (decision H6; running it on AWS is future-development item X3), the `VT_DEMO_DEFECT=notify_no_fix` path in the notification formatter of task 37 and the production refusal from `_docs/architecture.md` § Responder agent, using the responder's read-only API and Loki tokens. Task 37 is built before this task (see Build order under Dependency chain). It writes the failing test, the fix and the pull request; the human merges and production promotion stays manual. The responder's agent runtime is chosen with the human before this task is filed (`_docs/architecture.md` § Responder agent, A34: still open); CI and `make test-compose` use `RESPONDER_MODE=stub`, which proves the wiring and not an agent fixing anything, and the recorded run of task 39 uses the real runtime. The check is `P-DEMO-BE`, `P-PROD-REFUSAL` and `I-RESP-*` in `make test-compose JOB=responder` with `RESPONDER_MODE=stub` (`P-DEMO`, the n8n version, is future development). Task 28 owns the `responder` branch of `ci/test-compose.sh`, `compose.responder.yaml` and the cases in `tests/test_compose_responder.py` (built as 28a to 28d: #218, #219, #220 for the Compose wiring and wiring cases, #233 for `P-DEMO-BE`, #221 for the real runner); task 29 owns the `verify.yml` `responder` job and `P-FLAG-GONE`.
Depends on: 27
Covers: On-Call Agent, US-15

## 29. Responder Compose test and demo cleanup
Goal: The `responder` job proves, in the local Compose demo, that the undelivered finding reaches its owner, and the demo defect is removed.
Description: Adds the `responder` job to `verify.yml` (the `make test-compose JOB=responder` branch of `ci/test-compose.sh` and its cases are built in task 28) and the `P-FLAG-GONE` check from `_docs/testing.md` § Responder, then removes the demo defect before production promotion; the `P-DEMO-BE` and refused responder cases come from task 28. `P-FLAG-GONE` is one yes/no check that runs only in the production-promotion workflow of task 18 (it is not part of `make test-compose` or the pull-request jobs, so the pull-request gate stays green while the demo defect exists): before it deploys, the workflow fails if the `notify_no_fix` path or `VT_DEMO_DEFECT` exists anywhere in the code at the tag being promoted. The same check also covers the `VT_FEEDS=fixtures` rule added by task 40 (delivered here in #161 with the `VT_DEMO_DEFECT`/`notify_no_fix` rule, not by #172); `feeds.py` ships in every image by design, so it targets the fixtures flag/value and its refusal gate, not the module's existence (`VERIFY:` this wording choice with the owner). This task writes that check as a script, tests it against two small fixture trees (one with the path, one without) under `make test`, and adds its step to the production workflow (in the order where AWS work is late, the step is added when task 18 is built). The demo is a local run of the Compose stack with the responder, MailHog receiving the delivered notification, and in the local run the human restarts the stack on the merged code (pull-request workflows hold no AWS role, so there is no dev deploy in the drill); the deployed observability and responder on AWS are future-development item X3. The human performs the merge and the manual promotion. The check is `make test-compose JOB=responder` green, and `P-FLAG-GONE` failing the promotion while the defect path exists and passing after the cleanup commit.
Depends on: 19, 27
Covers: On-Call Agent, US-15

# Submission additions (backend notification, scheduler and close-out)

Tasks 37, 38 and 39 are submission tasks numbered after the future-development tasks so that tasks 1-36 keep their numbers (human decision on #93, 2026-10-22; task 39 added in #108 stage 2). Tasks 37 and 38 are built inside Milestone C, as the Dependency chain's Build order says; task 39 is built last.

## 37. Backend top-tier owner notification and delivery
Goal: A new top-priority finding sends exactly one email to its owner from the backend, recorded as `notification.enqueue` and `notification.deliver` with one trace ID.
Description: Adds the backend delivery worker for the notification jobs that task 10 creates: it claims a pending `top tier` job, formats the plain-text labelled-field owner notification from `_docs/architecture.md` § Routing and notifications and § Security boundaries, builds the headers from the finding id and tier only (a CR or LF in a header value is rejected), defangs any scheme, `www.` or domain-shaped token in advisory text (`S-NOTIFY`, `S-FIXTURE`), sends it once per finding lifecycle, records `sent` or `failed` (a failed job is retried on the next poll) and holds the job for an ownerless asset (E2). It records `notification.deliver` as a child span of the stored `notification.enqueue` `traceparent`, through the allowlist helper of task 23, so the scan-to-notification journey of US-13 is complete in the backend. Email route (human decision, 2026-10-22): the backend sends through the Amazon SES API using the server's instance role, with one verified sender address, because `sslip.io` hostnames cannot carry SES domain DKIM records; in development and tests it sends to the MailHog container that is part of the Compose stack (task 24 lists it). A mail-transport setting (name a build detail) selects the MailHog route or the SES route, and the sender address must be the configured verified sender. MailHog and the AWS SDK client are dependencies, ask before adding. `VERIFY:` the SES sandbox allows only verified recipient addresses, so the demo recipient must be verified too. `VERIFY:` the current SES free allowance and sending limits. `VERIFY:` the instance-role permission, the `ses:SendEmail` action and the resource form (the verified identity ARN). `VERIFY:` the SES region that holds the verified identity. The route is the human's decision of 2026-10-22 (the SES API through the instance role, one verified sender, MailHog for development and tests), recorded in `_docs/architecture.md` § Routing and notifications. The check is two runs of the same delivery cases. Under `make test` (no Docker), the delivery worker sends through an injected mail transport that records messages in process, with no AWS credentials in the environment: the notification is delivered once to the recorded sink (`I-OWNER-SEND`, `I-OWNER-NOAWS`), a retry produces no second email (`I-OWNER-ONCE`), a held job sends nothing (`I-OWNER-HOLD`), the defanging and header rules hold on the malicious advisory fixture (`S-NOTIFY`), and a send from an address other than the verified sender is refused with nothing delivered (`I-OWNER-SENDER`, the case that must be refused). Under `make test-compose` (Docker, CI or the human's host) the same `I-OWNER-NOAWS` and `I-OWNER-SENDER` cases deliver to or are refused by the MailHog container; the journey case `T-JOURNEY-BE` is added in task 25.
Depends on: 10, 23, 24
Covers: Application, US-8, US-13

## 38. Backend scheduler for the daily refresh and the scheduled re-scan
Goal: The backend refreshes KEV and EPSS every day and re-scans every asset after the refresh, with no manual action and no external workflow tool.
Description: Adds a scheduler inside the backend's background worker (A4, built in task 4) that runs the same code as `POST /signals/refresh` and `POST /scans` once a day at 06:00 UTC (A25, as carried over from the n8n schedule), re-scores the findings and then starts a scan of every asset with trigger `schedule`. A refresh that moves a finding into the top tier creates its `top tier` job through task 10's lifecycle idempotency key, so a second run the same day makes no second job (US-8). A catch-up rule covers the nightly stop of the server: at backend start, if the last completed refresh and re-scan finished more than 24 hours ago (or none has run), the scheduler runs the refresh and then the re-scan at once, then follows the 06:00 UTC schedule; the human turns the nightly stop off while graders may visit. A library scheduler would be a dependency, ask before adding; a clock-driven loop needs none. It covers spec US-7 (the daily refresh and re-score, lines 103-107, and both acceptance lines, 108-112) and the scheduled re-scan clause of US-10 (line 149). The check is a test with a fake clock and stubbed feeds showing changed signals and ranks after the scheduled run, a re-scan of every asset, no outbound call outside the stubs, and a repeated run creating no second notification job; plus the catch-up case: a start with the last run 30 hours old runs the refresh and re-scan at once, and a start with the last run 10 hours old runs nothing until 06:00 UTC.
Depends on: 8, 10
Covers: Application, US-7, US-10

## 39. Close-out: recorded drill, README sections and final rubric re-audit
Goal: The evidence for the highest-value criteria exists and is linked, the README lets a reviewer reach and run the project, and the whole rubric is re-audited.
Description: Three pieces of work, each with yes/no checks. (1) The recorded drill. The human runs the local Compose demo of tasks 28 and 29 once with the real responder runtime (chosen with the human before task 28 is filed; `_docs/architecture.md` § Responder agent, A34), not `RESPONDER_MODE=stub`, and records it (screenshots or a short video) as review evidence, because a stub run does not show an agent fixing anything. The agents write the drill runbook; the human performs the run, the merge and the recording. (2) The README close-out. The README gets a public URL section (the dev and prod `sslip.io` URLs), a one-command start section (`make dev` and the Compose command), a rollback section (the previous image tag, the deploy log and the production workflow) and a link to the recording, plus the deployment, observability and responder sections that roadmap C8 names. (3) The final rubric re-audit. The rubric auditor re-audits `main` against `_docs/rubric.md` and updates `_docs/rubric-evidence.md` (the Engineer does not edit that file). The checks, each yes or no: the recording exists and the README links it; the recording shows the metric at 1, exactly one alert naming the finding, a pull request opened by the real responder runtime, the human merge, the owner notification arriving at MailHog and the alert resolving (five answers); the demo defect is gone from the code before any production promotion (`P-FLAG-GONE` passed in the production workflow); the README names the public URL, the one-command start and the rollback steps, and a reviewer following the one-command start section from a clean clone reaches the sign-in page; `_docs/rubric-evidence.md` at the final commit shows all 12 criteria MET.
Depends on: 18, 21, 28, 29, 37, 38
Covers: On-Call Agent, Alerting on User Impact, Observability, Deployment

# Future development (after submission)

Tasks 30-36 are built after submission (spec § Future development; items X4-X6 in `_docs/roadmap-future.md`). They keep their numbers and nothing in the submission scope depends on them. Task 35 gained the E8 notice, the security-lead contact's check and a dependency on task 34 (human decision, 2026-10-22).

## 30. LLM brief with the fix-version guardrail
Goal: An open finding gets a matching brief or the structured finding with "brief unavailable".
Description: Implements the structured prompt, pinned model configuration and `LLM_MODE=stub` from `_docs/architecture.md` § LLM brief, plus the ordered guardrail and the rejected-brief path in `_docs/testing.md` § Rejected-brief path. The brief is cached per lifecycle, fixed version, prompt version and model; advisory text stays in the labelled untrusted field. The check is `U-GUARD`, `R1` and `I-BRIEF` in `make test`, with a stub returning `1.2.6` against `1.2.5` rejected and the notification still carrying the structured finding.
Depends on: 10
Covers: US-6

## 31. LLM brief evaluation with a human scorer
Goal: `make test-brief-eval` records a human-scored sample with the pinned model.
Description: Adds the `make test-brief-eval` target, the nine `L1`-`L9` cases and the scored results under `tests/eval/briefs/` from `_docs/testing.md` § LLM brief evaluation. The human is the scorer and runs it manually or on a schedule, because it is not a PR CI job. The check is a committed scored result for the pinned model, and a model or prompt change re-runs it.
Depends on: 30
Covers: US-6, Testing

## 32. MCP server with four read-only tools
Goal: `list_top_exposures`, `which_assets_affected`, `get_finding` and `get_asset` answer exposure questions with a GET-only token.
Description: Implements the Python stdio MCP server from `_docs/architecture.md` § MCP server against the `/mcp/` and `GET /assets/{id}` operations, marking advisory text as `untrusted_advisory_data` and using `MCP_API_TOKEN`. The human provisions the token and the MCP client runs on the developer's machine. The check is `I-MCP`, `I-AUTH-MCP` and `S-MCP` in `make test`, including a write attempt refused with 403 and no state change.
Depends on: 10
Covers: US-12

## 33. n8n service, daily refresh and scheduled re-scan
Goal: n8n runs `daily-signal-refresh` and `scheduled-rescan` from committed JSON.
Description: Adds the n8n Compose service, its credentials and the two workflows under `n8n/workflows/` from `_docs/architecture.md` § Routing and notifications, calling `POST /signals/refresh` and `POST /scans` with the n8n token. This is the n8n variant of the schedule that the backend runs for submission in task 38 (spec US-7, lines 103-112, and US-10, line 149); a setting turns the backend scheduler off while n8n drives the refresh and the re-scan, so the two never run together. The human provisions the SMTP and tracker secrets. The check is a Compose run showing changed signals and a re-scan, and both exported files parsing as JSON; `make test-workflows` is added in task 36.
Depends on: 10, 15
Covers: US-7 (n8n variant), US-16

## 34. n8n top-tier notification and tracker issue
Goal: A new top-priority finding opens one GitHub tracker issue through n8n (the "US-8 GitHub tracker issue" in the spec's Future development section).
Description: Adds `notify-top-tier` and `close-tracker-issue` under `n8n/workflows/` using the job list, claim and report operations, the `vt-lifecycle:<id>` search guard and the dedicated `vuln-triage-findings` token from `_docs/architecture.md` § Routing and notifications. The owner notification itself is sent by the backend in task 37; the workflow's email step is the original route and is used only if future development moves delivery back to n8n, which is decided when future development starts. The check is the `make test-e2e` `E-DELIVER` journey in the `e2e` job, proving one issue and no duplicate on a retry, with one notification, plus `S-ISSUE`. The human provides the tracker repository and token.
Depends on: 19, 33
Covers: US-8 (GitHub tracker issue), US-16

## 35. n8n reminders, escalation, weekly digest and the E8 notice
Goal: Overdue findings produce reminders and escalation, the security lead gets one weekly digest, and a `risk accepted` finding whose signals escalate notifies its owner and the security lead once.
Description: Adds `overdue-reminders` and `weekly-digest` under `n8n/workflows/` using the job and `GET /reports/weekly-digest` operations and the missing security-lead contact behaviour (`SECURITY_LEAD_NAME`, `SECURITY_LEAD_EMAIL`, A28) from `_docs/architecture.md` § Routing and notifications. It also adds the E8 "signals changed" notice (human decision, 2026-10-22: the notice and the security-lead contact are future development): in the future-development build the backend creates the `signals changed` job when a `risk accepted` finding's signals escalate, and the `notify-top-tier` workflow of task 34 sends it to the owner and to the security lead, once per lifecycle. The submission build only sets the `signalsChanged` flag. The human sets the security-lead contact. The check is `I-REMIND`, `I-CONFIG`, `I-DIGEST`, `I-SIGNALS-NOTICE` and `S-SIGNALS` in `make test` plus a manual Compose run showing one weekly digest.
Depends on: 33, 34
Covers: US-9, US-16, E8 (notice)

## 36. n8n workflow export check
Goal: `make test-workflows` proves every exported workflow is the one Compose runs.
Description: Adds `make test-workflows`, the `W-EXPORT` check and the `workflow-export` PR job from `_docs/testing.md`, parsing every `n8n/workflows/*.json`, matching the file name to the workflow name and comparing it with the workflow Compose imports. The check is `make test-workflows` green and a renamed export failing the job.
Depends on: 19, 34, 35
Covers: US-16, Testing

## Coverage summary

Every submission story and every criterion in `_docs/rubric.md` appears in at least one submission task (tasks 1-29, 37, 38 and 39). The stories and clauses that the spec moved to its Future development section are covered by future-development tasks (30-36) and are listed separately; they are future-development coverage, not gaps.

Submission stories:

| User story | Covering task(s) |
|---|---|
| US-1 | 4, 9, 11, 12, 22 |
| US-2 | 4, 22 |
| US-3 | 5 |
| US-4 | 6, 11 |
| US-5 | 7, 11 |
| US-7 | 38 |
| US-8 | 10, 37 |
| US-10 | 8, 12, 38 |
| US-11 | 8, 9, 12 |
| US-13 | 23, 24, 25, 37 |
| US-14 | 26, 27 |
| US-15 | 10, 28, 29 |

Future-development coverage (after submission; the story or clause is in the spec's Future development section):

| User story or clause | Covering future-development task(s) | Submission support |
|---|---|---|
| US-6 plain-language fix brief | 30, 31 | 11 shows the `brief` marker |
| US-7 n8n variant of the schedule | 33 | 38 runs the schedule in the backend |
| US-8 GitHub tracker issue | 34 | 37 delivers the owner notification |
| US-9 reminders, escalation, weekly digest | 35 | 10 creates the jobs and serves the digest |
| E8 "signals changed" notice and the security-lead contact | 35 | 8 sets the `signalsChanged` flag; no notice in submission |
| US-12 read-only assistant | 32 | 10 serves the `/mcp/` operations |
| US-16 n8n workflows exported | 33, 34, 35, 36 | none |

| Criterion | Points | Covering task(s) | Earliest milestone |
|---|---|---|---|
| Problem Description | 2 | 2 | A |
| Product Specification | 2 | 2 | A |
| Agent Team Specification | 2 | 2 | A |
| Context Management | 2 | 2 | A |
| Application | 2 | 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 37, 38 | A |
| Testing | 2 | 1, 13, 14, 16, 20 | A |
| Containerization | 2 | 15 | B |
| Deployment | 2 | 17, 18, 39 | B |
| CI/CD | 3 | 18, 19, 20, 21 | B |
| Observability | 2 | 23, 24, 25, 39 | C |
| Alerting on User Impact | 1 | 26, 27, 39 | C |
| On-Call Agent | 2 | 28, 29, 39 | C |

`ASSUMPTION:` task 15's Compose file and service names follow `_docs/testing.md` T-A1; task 17's Terraform resource names and the AWS region follow `_docs/architecture.md` § Deployment and carry the same `VERIFY:` tags as that document. `VERIFY:` the exact Juice Shop lockfile in task 22 is confirmed by the human before the first registration. The future-development tasks 31 and 36 add Testing evidence (the brief evaluation and the workflow export check) after submission; the Testing criterion does not depend on them.

Note: the Application row above lists the tasks for the end-to-end application. Application's "runs locally with a single command" clause is supplied in Tier A by `make dev` (task 11: backend on SQLite and the frontend together, no Docker); task 15's one-command Compose stack is the container variant of the same clause (`_docs/roadmap.md` B2), and its own `Covers:` line names only Containerization.

## Dependency chain

Every `Depends on:` resolves to a lower-numbered task; no task depends on itself or a later task. No submission task (1-29, 37, 38, 39) depends on a future-development task (30-36); the future-development tasks depend only on submission tasks and on each other.

Build order: tasks 37, 38 and 39 are numbered last, and 37 and 38 build earlier; task 39 builds last, after the production deploy (task 18) and the responder demo (tasks 28 and 29). Build 37 after 24 and before 25, because the `T-JOURNEY-BE` case of task 25 and the demo defect of task 28 run through task 37's delivery path; build 38 any time after 10. Tasks 25 and 28 do not list 37 in `Depends on:` because that line may only name a lower number (human decision, no renumbering); their descriptions say so.

| Task | Depends on |
|---|---|
| 1 | none |
| 2 | none |
| 3 | 1 |
| 4 | 3 |
| 5 | 4 |
| 6 | 5 |
| 7 | 6 |
| 8 | 7 |
| 9 | 8 |
| 10 | 9 |
| 11 | 9 |
| 12 | 11 |
| 13 | 10 |
| 14 | 10 |
| 15 | 14 |
| 16 | 15 |
| 17 | 15 |
| 18 | 17 |
| 19 | 14, 16 |
| 20 | 19 |
| 21 | 17, 19 |
| 22 | 4, 17 |
| 23 | 10, 15 |
| 24 | 23 |
| 25 | 19, 24 |
| 26 | 10, 24 |
| 27 | 19, 25, 26 |
| 28 | 27 |
| 29 | 19, 27 |
| 30 | 10 |
| 31 | 30 |
| 32 | 10 |
| 33 | 10, 15 |
| 34 | 19, 33 |
| 35 | 33, 34 |
| 36 | 19, 34, 35 |
| 37 | 10, 23, 24 |
| 38 | 8, 10 |
| 39 | 18, 21, 28, 29, 37, 38 |

## 40. Backend feed-client wiring and the VT_FEEDS fixture mode
Goal: A deployed/Compose scan matches, enriches, ranks and notifies with no live feed, so the US-13/US-14 Compose journeys can run.
Description: Wires the OSV client into the scan worker and the KEV/EPSS clients into `app.state` in `create_app` (today none are wired, so a deployed scan reads dependencies but matches nothing, ranks nothing and notifies no one — found during task 25). Adds the `VT_FEEDS` setting (`live` default; `fixtures` injects an httpx replay transport over `tests/fixtures/{osv,kev,epss,github}` into the same clients, so no second code path runs; an unknown value stops start-up with an error, never a silent fall-back to `live`). Fixture mode is refused unless `DEPLOYMENT_ENVIRONMENT` is explicitly `dev` or `test`, read from the raw environment so it fails closed (unset, `prod` or unknown refuses; not the telemetry getter, which defaults to `dev`); this is the same test `VT_DEMO_DEFECT` uses, settling Open question T-A8 on the name `DEPLOYMENT_ENVIRONMENT` (A35, A42). Then implements `T-JOURNEY-BE` as written in `_docs/testing.md` § Telemetry (the backend span list `scan.run`, `repository.read`, `osv.query`, `signals.enrich`, `prioritise`, `notification.enqueue`, `notification.deliver`; `brief.generate` is future development), green in `make test-compose JOB=telemetry`, asserting one trace ID across the Prometheus metric, the Tempo trace and the Loki JSON log, the traceparent round-trip and the `T-REFUSE` exclusions. `P-FLAG-GONE` gains the `VT_FEEDS=fixtures` rule, but that rule is delivered by task 29 / #161 with the `VT_DEMO_DEFECT` rule, not by this task or #172 (`feeds.py` ships in every image by design; the check targets the flag/value and its refusal gate, not the module; `VERIFY:` this wording with the owner). The `T-JOURNEY-BE` metric is also asserted to carry the journey trace id as a Prometheus exemplar (`T-A4`), which needs the Collector's `enable_open_metrics` and Prometheus's `exemplar-storage`. Build order: task 40 builds before task 25's remaining Compose cases (`T-JOURNEY-BE`, `T-E6`, the MailHog `I-OWNER-*` forms) and before task 28 (`P-DEMO-BE` needs the fixture mode); the prod deploy must set `DEPLOYMENT_ENVIRONMENT=prod` (task 18/#143). The check is unit tests under `make test` (no Docker) for the wiring, the fixture-mode selection, the unknown-value start-up error and the refusal including the unset-environment case (a `fixtures`-mode scan yields a KEV-listed P1 finding and exactly one `top tier` job through the replay transport), and `T-JOURNEY-BE` green in the telemetry CI job.
Depends on: 10, 15
Covers: Observability, US-13, US-14, Application
