# Issue #142 (task 21): Automatic dev deploy on merge to main

**Date:** 2026-10-24
**Branch:** `feat/142-auto-dev-deploy`

## What changed and why

Task 21 of Milestone B: a merge to `main` now deploys the `dev` Compose project
automatically after the build and tests pass. This fills in the `deploy-dev`
job that task 17 (#141) left scaffolded as a comment in `.github/workflows/deploy.yml`.

Chosen to run in parallel with the other agent's #159 (the alert Compose job) —
**no file overlap**: #159 touches `verify.yml`, `ci/test-compose.sh`, the alert
Compose override and new `tests/test_compose_alert*`; this task touches
`deploy.yml`, a new `terraform/server/deploy-dev.sh`, and the dev deploy role in
`terraform/deploy-roles/main.tf`.

The agent authors the workflow and the server-side script; the **human** applies
the one-line Terraform IAM change and verifies the deploy on the running server
(the agent holds no AWS credentials).

## How it works

`.github/workflows/deploy.yml` on push to `main`:

1. `build-and-push` (task 17, unchanged logic) builds + pushes the backend and
   frontend images tagged `YYYYMMDD-HHMMSS-shortsha`, and now also **outputs**
   the two image digests so the deploy job can record them.
2. `deploy-dev` (new) `needs: build-and-push`. The push-to-`main` event is
   already gated by branch protection (the `verify.yml` test jobs must be green
   to merge), so **a red test leaves the previous version running** — there is
   no deploy on a failed PR. The job:
   - assumes the dev OIDC role (`vars.AWS_DEV_ROLE_ARN`, `vars.AWS_REGION`);
   - **reads the instance state first** via `ec2:DescribeInstances`
     (`tag:project=vuln-triage`, `Name=vuln-triage-server`);
   - **stopped server (nightly stop):** writes the exact summary
     `dev deploy skipped: server stopped`, does **not** call the server, and the
     job ends neither as a deploy nor as a failure (the human starts the server
     and re-runs) — architecture.md Cost controls (2), aws-setup.md step 10;
   - **running server:** base64-encodes `terraform/server/deploy-dev.sh` and the
     committed `compose.yaml` and sends one `AWS-RunShellScript` SSM command that
     runs the script, then waits and fails on a non-`Success` final status;
   - records the deployed tag, both digests, the SSM command id and the instance
     id in the job summary (the "tag and digest in the deploy log" evidence).

`terraform/server/deploy-dev.sh` (new, runs on the server via SSM): decodes the
committed `compose.yaml`, writes the dev project `.env` (the image tag, dev-only
stub modes, `DEPLOYMENT_ENVIRONMENT=dev`), an **image-pinned override**
(`compose.deploy.yaml`: runs the published GHCR images by tag with `!reset` on
`build`/`ports`, names the frontend `dev-frontend` on the shared `vt-edge`
network), the dev `Caddyfile` (filled with the EIP and ACME email), then
`docker compose pull` + `up -d --wait` for the `dev` project and brings Caddy up.
A failed pull leaves the running containers in place (architecture.md Rollback).
GHCR images are public, so the server pulls with no registry credential.

## Human action required (Terraform re-apply)

`terraform/deploy-roles/main.tf` — the dev deploy role gained a **read-only**
`ec2:DescribeInstances` statement so the workflow can "first read the instance
state" before deciding to deploy or skip. The role still cannot start/stop or
modify the instance, touch IAM/state/secrets, and its SSM `SendCommand` stays
scoped to `project=vuln-triage`. **The human must `terraform apply` the
`deploy-roles` module** for the new permission to take effect (aws-setup.md
step 7); the ARN in `AWS_DEV_ROLE_ARN` is unchanged.

## Acceptance criteria mapping

- Deploy the `dev` project only, by image tag, via the dev role; record tag +
  digest in the deploy log ✅ (`deploy-dev` job + `deploy-dev.sh`; human verifies on the server)
- A red test leaves the previous version running (no deploy) ✅ (branch
  protection gates the merge; the deploy job only runs on push to `main`)
- Stopped server → reads state first, does not call the server, ends with the
  visible `dev deploy skipped: server stopped` summary (not a pass, not a
  failed deploy) ✅ (`state` + skip-and-report steps)
- Production promotion is not here (task 18/#143) ✅ (only the `dev` project)
- `make verify` ✅ (only workflow/Terraform/shell changed; no test, backend or
  frontend code touched. The backend suite could not be run in this sandbox —
  no PyPI network — but the whitespace and weakened-test gates pass and no test
  file changed. The embedded workflow shell and `deploy-dev.sh` pass `bash -n`,
  and `deploy-dev.sh` was exercised end-to-end against a stub `docker`.)

## Documentation

- `_docs/terraform-verify.md` — new §6 "Re-apply for the automatic dev deploy
  (task 21 / #142)" records the deploy-roles re-apply step and the end-to-end
  deploy / red-test / stopped-server checks; the §2 dev-role checklist item and
  the deploy-mechanism VERIFY note now include the read-only
  `ec2:DescribeInstances` grant.

## Unrelated flake found (filed)

- #185 — `T-JOURNEY-BE` (`tests/test_compose_telemetry.py`, task 40 / #172) is
  flaky: Tempo's search API returns `traceID` without leading-zero padding, so
  `assert len(trace_id) == 32` fails ~1 in 16 runs. Hit once on this PR's first
  `verify` run; passed on the push run and on re-run. Not caused by this task
  (no telemetry/test code touched). Fix: zero-pad the id to 32 hex chars in the
  harness helper.

## VERIFY (on the running stack, by the human)

- SSM Run Command reaches the instance and `deploy-dev.sh` runs under the
  AL2023 shell (the dev role grants `ssm:SendCommand` + the new
  `ec2:DescribeInstances`).
- Docker Compose on the server supports `!reset` (needs Compose v2.24+; the
  latest plugin from user-data.sh does).
- `dev.<eip>.sslip.io` answers after the deploy and Caddy obtains a certificate
  (A36 Let's Encrypt fallback if the shared sslip.io name is rate-limited).
