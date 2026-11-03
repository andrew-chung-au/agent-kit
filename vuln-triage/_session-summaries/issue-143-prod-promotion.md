# Issue #143 (task 18): Production Compose project, manual promotion and rollback

**Date:** 2026-10-24
**Branch:** `feat/143-prod-promotion`

## What changed and why

Task 18 of Milestone B: production runs the same image digest as dev on the one
server (A36) and is promoted **only by a human**. Builds on task 17's server and
roles and task 21's dev deploy; **no file overlap** with #159 (the alert Compose
job) — this touches `.github/workflows/deploy.yml`, a shared
`terraform/server/deploy-env.sh`, and three docs.

### One server, two projects, one Caddy

The key design point: dev (`dev.<eip>.sslip.io`) and prod (`app.<eip>.sslip.io`)
run on the same host as two Compose projects, but only one container can bind
:80/:443. So the task-21 dev script (which ran its own `dev-caddy`) is refactored
into one shared `deploy-env.sh` that runs a **single shared Caddy** (`vt-caddy`,
project `vt-edge`) whose Caddyfile is rebuilt from a per-env site snippet on each
deploy. Deploying prod leaves dev serving and vice-versa. `deploy-dev.sh` is
deleted; both the dev and prod workflow jobs run `deploy-env.sh` with
`DEPLOY_ENV=dev|prod`.

### Workflow (`.github/workflows/deploy.yml`)

- New `workflow_dispatch` trigger with an `image_tag` input (blank = the tag
  currently running in dev). `build-and-push` and `deploy-dev` are gated to
  `github.event_name == 'push'`; the new `deploy-prod` to `workflow_dispatch`.
  Concurrency groups are split so a prod promotion never cancels a dev deploy.
- `deploy-prod` runs in the `production` environment (human = required reviewer,
  so the run pauses for approval and the prod OIDC credential is only issued
  there). It reads instance state (skip-and-report if stopped), resolves the tag
  (input or dev's current tag, read from `/opt/vuln-triage/dev/.env` via SSM),
  resolves the GHCR digests for the deploy log, deploys the `prod` project via
  SSM, and records the promoted tag + digests in the run summary. **Nothing is
  rebuilt.** Rollback = re-run with the previous tag from the log.

### Secrets model (architecture-correct)

The prod deploy carries **no secret**. `deploy-env.sh` reads `vuln-triage/prod`
from Secrets Manager using the **instance role** (the deploy OIDC role has no
secrets access; `architecture.md` Security boundaries). Prod requires at least
`POSTGRES_PASSWORD` in that secret (hard fail otherwise); dev falls back to a
throwaway value if its secret is absent. `.env` is written with `umask 077`.
`DEPLOYMENT_ENVIRONMENT=prod` is set so the backend's `VT_FEEDS=fixtures` /
`VT_DEMO_DEFECT` refusals fail closed (A42/A35).

## No Terraform resource change

The prod deploy role and the instance-role Secrets Manager read already exist
from task 17, and the prod role shares the dev role's deploy policy (including
the `ec2:DescribeInstances` added in #142). So **task 18 adds no Terraform** and
needs no re-apply — only the `production` environment, `AWS_PROD_ROLE_ARN`, and
the `vuln-triage/prod` secret, which are human setup steps.

## Documentation

- `_docs/aws-setup.md` — new "Production promotion and rollback (task 18)"
  section (prerequisites, the Run-workflow promotion steps, rollback).
- `_docs/terraform-verify.md` — new §7 (prod promotion verification; notes no
  Terraform change); title scope extended to #143.
- `_docs/human-tasklist.md` — added A12 (add the prod secret + promote to
  production → closes #143); removed #143 from §E "Later".

## Acceptance criteria mapping

- Second `prod` Compose project + `app.<eip>.sslip.io` ✅ (`deploy-env.sh` prod
  branch + the shared Caddy's `app.` site)
- Manual `workflow_dispatch` in `production` (human reviewer), tag input
  defaulting to dev's tag, nothing rebuilt ✅ (`deploy-prod` job)
- Production runbook + rollback (re-run with the previous tag from the deploy
  log) ✅ (`aws-setup.md`; the log records tag + digests)
- Division of labour (human creates prod secrets, approves each run, runs
  teardown) ✅ (production environment reviewer; Secrets Manager; teardown
  unchanged in §11)
- Check: prod URL answers; dev and prod same digest; rollback recorded →
  **human verifies** (`terraform-verify.md` §7)
- `make verify` ✅ (only workflow / shell / docs changed; no test, backend or
  frontend code. Could not run the backend suite in this sandbox — no PyPI
  network — but whitespace and weakened-test gates pass, no test file changed,
  the 11 embedded workflow shell blocks pass `bash -n`, and `deploy-env.sh` was
  exercised end-to-end against stub `aws`/`docker` for dev, prod, the prod
  missing-secret failure, the bad-env failure, and the shared two-site Caddyfile.)

## VERIFY (on the running stack, by the human)

- The prod `workflow_dispatch` pauses on the `production` environment for
  approval and the prod OIDC role assumes cleanly.
- Reading dev's tag via SSM (`/opt/vuln-triage/dev/.env`) returns the running
  tag; the GHCR digest resolution (`docker buildx imagetools inspect`) returns a
  digest (best-effort; falls back to `unknown`, never failing the deploy).
- The single shared Caddy serves both `dev.` and `app.` hostnames after each
  deploys, and bringing one up does not drop the other.
- `vuln-triage/prod` in Secrets Manager is read by the instance role on the
  server (not by the workflow).
