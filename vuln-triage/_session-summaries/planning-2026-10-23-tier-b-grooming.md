# Planning: Tier B (Milestone B) issue grooming

**Date:** 2026-10-23
**Author:** PM grooming pass (Kiro, Vibe session)
**Scope:** Milestone B / phases S2-S3, `_docs/tasks.md` tasks 15-22.
**Status:** FILED 2026-10-23. The human confirmed the open points (file now; the
AWS account + Budgets exist and human AWS steps are done when reached, so no D5
fallback date; security-scan tools and Terraform approved). The 8 issues are
filed: B1=#137 (task 15), B2=#138 (task 16), B3=#139 (task 19), B4=#140 (task 20),
B5=#141 (task 17), B6=#142 (task 21), B7=#143 (task 18), B8=#144 (task 22). #137
and #138 note #31 (T3) as a blocker. No GitHub milestone/label is set, matching
the Milestone A convention.

This is step 12 for Milestone B ("PM proposal approved by the human; each issue
carries its story's acceptance criteria", `_docs/roadmap.md` § Sequence row 12).
Sources: `_docs/tasks.md` (tasks), `_docs/architecture.md` § Deployment /
§ Development environment, `_docs/testing.md` § Integration tests / § Light
security scan / § CI jobs, `_docs/roadmap.md` § Tier B milestones, and the
consolidated [`_docs/tier-b-build.md`](../_docs/tier-b-build.md).

## Decisions and prerequisites that bear on filing

- **Tasks 15 and 17 stay whole** (one issue each); the roadmap B1/B2 and B4/B5
  split is a checkpoint grouping only ("the issue filed from it keeps the task
  whole"). This grooming files 8 issues for 8 tasks, not 6 for the B-table rows.
- **T3 (#31)** — the Compose Postgres recipe and dev-container rebuild — is a
  prerequisite for issues 15 and 16 and is currently **open**. It is on the
  parallel tooling track, owned partly by the human (the rebuild).
- **AWS prerequisites** (account, Budgets alert, `production` environment,
  secrets) gate issues 17, 18, 21, 22 and are the human's (`_docs/aws-setup.md`).
- **No open decision blocks Tier B.** D4 is Tier C; D5 (AWS-unavailable
  fallback) is a named contingency for issue 17, not a blocker.
- **Ordering caveat:** issue 19 depends on 16, and 16 depends on 15 + #31, so
  the pure Tier B order is 15 → 16 → 19 → 20, with 17 able to start right after
  15 (it depends on 15 only). 21 needs 17 + 19; 18 needs 17; 22 needs 17.

---

## Issue B1 — task 15: One-command Compose stack

**Title:** One-command Docker Compose stack (frontend, backend, Postgres)
**Covers:** Containerization
**Depends on:** S1 (task 14 done); T3 (#31, open)

**Goal:** `docker compose up` starts the frontend, backend and Postgres with one
command (through a `make` target), on one origin, with no per-service step.

**Acceptance criteria**
- [ ] Multi-stage Dockerfiles for the backend and the frontend; the frontend container serves the built SPA and proxies the API paths to the backend (one origin, as task 11 assumes); containers run non-root and answer a health check; the backend listens on `0.0.0.0`.
- [ ] A project Compose file with the frontend, backend, Postgres (`db` service, `ASSUMPTION: T-A1`) and the migrations step; named volume for Postgres; health checks and `depends_on: healthy`.
- [ ] One `make` target brings the stack up with `docker compose up --build -d --wait`; the frontend reads the API on the human's host or in CI with no manual per-service step.
- [ ] Data survives a container restart (the B2 "done when").
- [ ] A committed `.env.example` lists setting/secret **names only** (no values): database password, repository read token, `RESPONDER_API_TOKEN`, Grafana admin password, responder LLM key, and the stub switches (`LLM_MODE=stub`, `RESPONDER_MODE=stub`). It does **not** list showcase settings (backend LLM key, `MCP_API_TOKEN`, `N8N_API_TOKEN`, tracker tokens, SMTP).
- [ ] No image is pushed in this task; the Collector, other observability services, MailHog and n8n are NOT added here (tasks 24/33).
- [ ] `make verify` passes.

**Out of scope:** image push/registry (task 17); observability stack (task 24); n8n (showcase task 33).

> **PM → human: confirm before filing**
> 1. **#31 (T3) sequencing.** Issue 15 needs the Compose Postgres recipe and the dev-container rebuild. #31 is open. File 15 now and mark #31 a blocker, or wait until #31 closes?
> 2. **Compose/Makefile naming.** tasks.md leaves the start target name and the `.env.example` stub-switch names to this task ("task 15 chooses the names the documents do not fix"). Any preference, or Engineer's choice?
> 3. **Protected commit.** The new `make` target(s) touch the Makefile (protected) → its own human-approved commit. Confirm that is expected here.

---

## Issue B2 — task 16: Real-Postgres integration tests

**Title:** Real-Postgres integration tests (`make test-integration`)
**Covers:** Testing
**Depends on:** B1 (task 15); T3 (#31). Follow-up #68 runs #26's persistence test on Postgres after.

**Goal:** `make test-integration` runs the integration cases on Postgres in the
test-owned `vt-test` Compose project.

**Acceptance criteria**
- [ ] The `vt-test` Compose project starts the `db` (Postgres) service, runs migrations, and isolates each test (transaction rollback or fresh schema); these cases never use SQLite.
- [ ] Committed fixtures from `_docs/testing.md` § Integration tests are used; no live external call (the network guard still holds).
- [ ] `make test-integration` is green, and `E-GUARD` refuses a database or host that is not the test one.
- [ ] The `postgres-integration` job **target** exists (the job is wired into CI in task 19, not here).
- [ ] `make verify` passes.

**Out of scope:** adding the job to the CI workflow (task 19); #68 (persistence test on Postgres).

> **PM → human: confirm before filing**
> 1. **Runs where.** These cases need Docker, so they run in CI or on the human's host, not the agent sandbox. Confirm the agent writes them and the human (or CI) runs the green check.
> 2. **#68 relationship.** Keep #68 as a separate follow-up after 16 and #31, or fold its single persistence case into this issue?

---

## Issue B3 — task 19: CI test pipeline

**Title:** CI test pipeline — unit, sqlite-integration, frontend, openapi-validation, postgres-integration
**Covers:** CI/CD
**Depends on:** task 14 (done), B2 (task 16). Related: #67 (pass a real `BASE`).

**Goal:** Every pull request runs the test jobs before any deploy.

**Acceptance criteria**
- [ ] The GitHub Actions workflow adds the jobs `unit`, `sqlite-integration`, `frontend`, `openapi-validation` and `postgres-integration`, each using the targets from tasks 13, 14 and 16 and matching `_docs/testing.md` § CI jobs.
- [ ] Every job runs on a pull request and on a review-branch push; a push to `main` re-runs the set before deploy.
- [ ] A PR with a broken test fails the matching job; a clean `main` passes all jobs.
- [ ] No job needs a live feed or a secret.
- [ ] `make verify` passes.

**Out of scope:** the `security-scan` job (task 20); deploy jobs (tasks 17/21); the Compose `telemetry`/`alert`/`responder` jobs (Tier C).

> **PM → human: confirm before filing**
> 1. **#67 (real `BASE`).** testing.md/roadmap put "CI passes a real `BASE`" under #67 (Later). Fold #67 into this issue, or keep it as the separate follow-up it is today?

---

## Issue B4 — task 20: Light security scan in CI

**Title:** Light security scan (`make security-scan` + `security-scan` PR job)
**Covers:** CI/CD, Testing
**Depends on:** B3 (task 19)

**Goal:** `make security-scan` fails on high/critical findings in the app's own
dependencies and reports lower ones.

**Acceptance criteria**
- [ ] `make security-scan` audits the application's own lockfiles/manifests (not a live service) and fails on high and critical findings in production dependencies; lower findings are reported only.
- [ ] The `security-scan` PR job on `ubuntu-latest` runs `make security-scan`.
- [ ] `C-FIXTURE-VULN` (deliberately vulnerable fixture) fails; `C-FIXTURE-CLEAN` (clean fixture) passes.
- [ ] Secret scanning and SAST are out of scope ("light" = dependency auditing only).
- [ ] `make verify` passes.

> **PM → human: confirm before filing**
> 1. **Tool choice (dependency, needs approval).** testing.md suggests `pip-audit` and `npm audit --omit=dev` with a `VERIFY:` on licence/behaviour. Approve these, or prefer others? Note the push-check image (#112) already carries `pip-audit`.

---

## Issue B5 — task 17: AWS infrastructure on one server + the dev environment

**Title:** AWS infra (Terraform) on one server and the dev environment
**Covers:** Deployment
**Depends on:** B1 (task 15); AWS account + Budgets alert (human)

**Goal:** The dev environment is reachable at a public HTTPS `sslip.io` URL on
one AWS server.

**Acceptance criteria**
- [ ] Terraform modules per `_docs/architecture.md` § Deployment: state bucket (versioned/private/encrypted, hand-run bootstrap), GitHub OIDC deploy roles (accepting an **existing** provider rather than failing to create a second — `VERIFY:` one-per-URL-per-account), and one server (Elastic IP, security group 80/443 + SSM access, instance role, EBS volume + daily snapshots, nightly-stop schedule with an on/off Terraform variable on by default, bootstrap installing Docker + Compose).
- [ ] A push-to-`main` build-once job tags images (`YYYYMMDD-HHMMSS-shortsha`, D2) and pushes to GHCR with the workflow `GITHUB_TOKEN`, recording each digest in the deploy log.
- [ ] The `dev` Compose project runs behind the reverse proxy at `dev.<elastic-ip>.sslip.io` with HTTPS (Let's Encrypt; staging-cert / `nip.io` fallback per A36).
- [ ] Division of labour: the agent writes the Terraform + runbook; the **human** creates AWS resources and secrets, approves installing Terraform, and runs the bootstrap, first `terraform apply` and first deploy.
- [ ] Check: the dev URL answers the frontend and the deploy log names one image digest.

**Out of scope:** auto-deploy on merge (task 21); the prod project and promotion (task 18).

> **PM → human: confirm before filing**
> 1. **AWS prerequisites are undone.** The roadmap records "the human has done no AWS step." This issue cannot reach its check until the account, Budgets alert and secrets exist. File now (agent writes Terraform) with the human steps flagged, or hold until the account is ready?
> 2. **D5 fallback.** Name the fallback date/condition now (kind cluster or local-Compose recorded demo) in case AWS is not available in time?
> 3. **`VERIFY:` items to resolve at build time:** SSM Run Command vs. equivalent, S3-native state locking, `t3.medium` sizing, Let's Encrypt rate limits. Confirm these are build-time checks, not pre-filing blockers.
> 4. **Protected/large tool.** Terraform install needs approval (a tool, per architecture). Confirm.

---

## Issue B6 — task 21: Automatic dev deploy

**Title:** Automatic dev deploy on merge to `main`
**Covers:** CI/CD
**Depends on:** B5 (task 17), B3 (task 19)

**Goal:** A merge to `main` deploys the `dev` project automatically when tests
pass.

**Acceptance criteria**
- [ ] After the push-to-`main` build (task 17) and the test jobs (task 19) pass, the workflow assumes the dev deploy role and runs the deploy on the server for the `dev` project only, by image tag, recording tag + digest in the deploy log.
- [ ] A red test leaves the previous version running (no deploy).
- [ ] When the server is stopped (nightly stop), the deploy step reads instance state, does not call the server, and ends with a visible "dev deploy skipped: server stopped" summary (not a pass, not a failed deploy); the human starts the server and re-runs.
- [ ] The production promotion is NOT here (it is part of task 18 per D7).
- [ ] `make verify` passes.

> **PM → human: confirm before filing**
> 1. No new open points beyond B5's AWS prerequisites. Confirm it is filed together with / right after B5.

---

## Issue B7 — task 18: Production Compose project and manual promotion

**Title:** Production Compose project, manual promotion and rollback
**Covers:** Deployment, CI/CD
**Depends on:** B5 (task 17)

**Goal:** Production runs the same image digest as dev on the same server and is
promoted only by a human.

**Acceptance criteria**
- [ ] A second Compose project (`prod`) and hostname `app.<elastic-ip>.sslip.io` on the task-17 server.
- [ ] A manual `workflow_dispatch` in the `production` environment (human as required reviewer) takes an image tag input defaulting to the one running in dev; nothing is rebuilt.
- [ ] The production runbook and the rollback step (re-run the production deploy with the previous tag from the deploy log).
- [ ] Division of labour: the human creates production secrets, approves each production run and runs teardown.
- [ ] Check: the production URL answers; `dev` and `prod` run the same image digest; one rollback to the previous tag is recorded in the deploy log.

> **PM → human: confirm before filing**
> 1. **`production` environment + reviewer.** Needs the GitHub `production` environment with the human as required reviewer (`VERIFY:` available on this repo's plan). Confirm this is set up (aws-setup step 6.1) before the check can run.
> 2. **`P-FLAG-GONE`.** The demo-defect gate runs in this task's production workflow but its step is added in task 29 (Tier C). Confirm the cross-reference is acceptable (no action needed in B7 itself).

---

## Issue B8 — task 22: Pilot seed data

**Title:** Pilot seed data registered through the API
**Covers:** US-1, US-2
**Depends on:** task 4 (done), B5 (task 17)

**Goal:** The pilot assets are registered through `POST /assets` so real findings
appear on dev.

**Acceptance criteria**
- [ ] A pilot seed list (data file, A38) with the human's repositories and OWASP Juice Shop (A41 fallback if Juice Shop lacks a supported lockfile).
- [ ] Each asset is registered through `POST /assets`; the task never writes to the database directly.
- [ ] Repository URLs never enter telemetry (A38).
- [ ] Check: each asset shows a scan status and at least one finding on the dev environment.

> **PM → human: confirm before filing**
> 1. **Repository URLs.** The human supplies the exact pilot repository URLs before the first registration.
> 2. **Juice Shop lockfile.** `VERIFY:` Juice Shop commits a supported `package-lock.json`; otherwise use the A41 fallback repo. Confirm which.

---

## Summary for the human

- **8 issues** proposed (one per task 15-22), tasks 15 and 17 kept whole.
- **Build order:** 15 → 16 → 19 → 20 (S2), with 17 startable after 15; then 21 (needs 17+19), 18 (needs 17), 22 (needs 17) (S3).
- **Hard external dependencies to settle first:** #31 (T3) for 15/16; the AWS account + Budgets + `production` environment for 17/18/21/22.
- **Open points to confirm** are in each issue's "PM → human" block; the recurring ones are #31 sequencing, the AWS-prereq timing + D5 fallback, and the two tool approvals (security-scan tools, Terraform).
- Nothing is filed yet. On confirmation, I will create the issues with these bodies and acceptance criteria, each labelled for Milestone B, and record the filing in the roadmap check-in log.
