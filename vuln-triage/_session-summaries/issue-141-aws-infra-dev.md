# Issue #141 (task 17): AWS infrastructure on one server and the dev environment

**Date:** 2026-10-23
**Branch:** `feat/141-aws-infra-dev`

## What changed and why

Task 17 of Milestone B (S3): the Terraform for the one-server dev+prod
deployment, plus the build-once → GHCR workflow, so the dev environment can be
reached at a public HTTPS `sslip.io` URL. Run in parallel with the other agent's
#140 — **no file overlap**: this adds `terraform/` and `.github/workflows/deploy.yml`
and does not touch `Makefile` or `verify.yml`.

The agent writes the Terraform and the runbook; the **human** installs Terraform,
reviews, and runs every `terraform apply` and the first deploy (the agent holds
no AWS credentials). So this task is authored now and **verified by the human**
against `_docs/terraform-verify.md`.

## Human decisions applied (recorded here per aws-setup.md)

- Region: `ap-southeast-2` (default; `var.aws_region`).
- Reverse proxy: **Caddy** (human-approved; automatic Let's Encrypt).
- Secrets store: Secrets Manager, one JSON secret per environment.
- Instance size: `t3.medium` (`var.instance_type`; `t3.small` fallback noted).
- OIDC provider: `var.create_oidc_provider` (reuse an existing provider by ARN, or create one).
- SES sender: deferred (task 37); `var.ses_sender_identity_arn` empty disables the SES permission for now.

## Files

- `terraform/README.md` — modules, apply order, the `create_oidc_provider` variable, defaults.
- `terraform/bootstrap/` — the S3 state bucket (versioned, private, encrypted), applied with local state then migrated (`README-state.md`). `VERIFY:` S3-native locking.
- `terraform/deploy-roles/` — the GitHub OIDC provider (reuse-or-create) and the `dev`/`prod` roles. Trust policies scoped to this repo, `main` for dev and the `production` environment for prod; no PR/wildcard. The deploy permission is SSM `SendCommand` to `project=vuln-triage` instances only — no IAM/state/secret access.
- `terraform/server/` — one EC2 (Amazon Linux 2023), Elastic IP, security group (80/443 only, **no SSH**), instance role (`AmazonSSMManagedInstanceCore` + read on the named secrets + optional send-only SES), a `gp3` data volume with daily DLM snapshots, the nightly-stop EventBridge schedule (on by default, `var.nightly_stop_enabled`), and `user-data.sh` (Docker + Compose plugin + the `vt-edge` network; Caddy runs from the deploy). `caddy/Caddyfile` routes `dev.<eip>.sslip.io` / `app.<eip>.sslip.io` to each project's frontend.
- `.github/workflows/deploy.yml` (new) — on push to `main`: build the backend and frontend images once, tag `YYYYMMDD-HHMMSS-shortsha` (D2), push to GHCR with `GITHUB_TOKEN`, and record each digest in the job summary (the "deploy log names one image digest" evidence). The dev-deploy-on-merge job is scaffolded as a comment for task 21 (#142).
- `.gitignore` — Terraform state, `.terraform/` and real `*.tfvars` ignored; `*.tfvars.example` tracked.

## Acceptance criteria mapping

- Terraform modules (state bucket, OIDC roles, server with EIP/role/EBS/snapshots/nightly-stop/bootstrap), tagged `project=vuln-triage` ✅ (written; human applies)
- Reuse an existing OIDC provider rather than fail ✅ (`create_oidc_provider` var)
- Build-once → tag → GHCR with `GITHUB_TOKEN`, digest recorded ✅ (`deploy.yml`)
- `dev` behind the reverse proxy at `dev.<eip>.sslip.io` with Let's Encrypt (A36 fallback) ✅ (Caddy; human applies + first deploy)
- Division of labour (agent writes, human applies) ✅
- Check — dev URL answers; deploy log names a digest → **human verifies** (`_docs/terraform-verify.md` §4)

## ⚠️ Verification (the human; no AWS/Terraform in the sandbox)

I cannot run `terraform fmt/validate/plan/apply` here. Checked locally: every
`.tf` file has balanced braces; the `.tfvars.example` files are tracked and real
tfvars/state are git-ignored; the workflow references only `GITHUB_TOKEN` and the
OIDC role (no long-lived AWS key). The human runs, per `_docs/terraform-verify.md`:
§1 `terraform fmt -check` + `init -backend=false` + `validate` in each module
(these also run in the push-check image / CI); §2 the pre-apply security review;
§3 apply in order with the per-module live checks; §4 the dev-URL acceptance.

## Notes / VERIFY (settled at apply time)

OIDC thumbprint (or omit per current AWS guidance), S3-native state locking, the
AL2023 device name for `/dev/sdf`, the Compose-plugin version pin, EventBridge
Scheduler as the stop mechanism, SSM Run Command as the deploy mechanism,
`t3.medium` sizing, Let's Encrypt rate limits for the shared `sslip.io` name, and
the SES action/resource/condition form (task 37). All carry `VERIFY:` in the
files and in `_docs/terraform-verify.md`.

## Out of scope (unchanged)

Auto dev deploy on merge (task 21 / #142), production project + promotion +
rollback (task 18 / #143), pilot seed data (task 22 / #144).
