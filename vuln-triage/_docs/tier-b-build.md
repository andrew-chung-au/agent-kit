# Tier B build sheet (phases S2-S3)

A single place that answers "what does milestone B_n build, what does it depend
on, which human step unblocks it, and when is it done?" without reading four
documents at once.

This sheet **consolidates and points to** the authoritative sources; it does not
restate design and it adds no new precedence rule. Where this sheet and an
authoritative source differ, the source wins and the difference is a defect here:

- **Per-task description:** [`_docs/tasks.md`](tasks.md) Milestone B (tasks 15-22) — authoritative on task boundaries.
- **Design (infra, pipeline, cost):** [`_docs/architecture.md`](architecture.md) § Deployment, § Development environment, § Rubric enablement.
- **Order, checkpoints, decisions:** [`_docs/roadmap.md`](roadmap.md) § Sequence (S2/S3), § Tier B milestones (B1-B6), § Open decisions (H1-H7, D1-D7).
- **Test cases and CI jobs:** [`_docs/testing.md`](testing.md) § Integration tests, § Light security scan, § CI jobs.
- **Human AWS/GitHub runbook:** [`_docs/aws-setup.md`](aws-setup.md).

Tier B targets 19 of 24 points: Containerization (2), Deployment (2) and the
first two rungs of CI/CD (to 2, then 3 at B6). S2 ends at an estimated 14, S3 at
19 ([`roadmap.md`](roadmap.md) § Score checkpoints).

## Settled before Tier B starts

- **Decisions H1-H7, D1-D3, D6, D7: resolved** (roadmap § Open decisions). Terraform (H2), one server for dev+prod (H3), GHCR (H4), `sslip.io` + Let's Encrypt (H5), image tag `YYYYMMDD-HHMMSS-shortsha` + `service.version` in the allowlist (D2), dev/prod deploy split (D7).
- **No open decision blocks the S2/S3 build start.** D4 (responder false-positive rule) is Tier C only. **D5** (fallback if AWS is unavailable) is a named contingency for B4, not a blocker — the plan keeps AWS as the default and names the fallback date at B4.
- **`VERIFY:` markers remain on infra mechanisms** (SSM Run Command vs. equivalent, S3-native state locking, Let's Encrypt rate limits, `t3.medium` sizing, GitHub environment protection on this repo's plan). These are checked against vendor docs at build time; they are not planning gaps.

## Milestones

Dependency note: tasks 15 and 17 each **stay whole** (one issue each). The
roadmap's B1/B2 and B4/B5 split is a checkpoint grouping only — "the issue filed
from it keeps the task whole" ([`roadmap.md`](roadmap.md) § Tier B milestones).
So this sheet lists milestones by task, not by the B-table's finer rows.

| # | Task(s) | Builds | Depends on | Human prerequisite | Criterion | Done when (test) |
|---|---|---|---|---|---|---|
| S2.1 | 15 | Dockerfiles + project Compose file (frontend, backend, Postgres `db`, migrations) and the committed `.env.example` (names only); one-command start; no image pushed | S1; **T3 (#31)** Compose Postgres recipe | #31 dev-container rebuild (human) | Containerization | `docker compose up` (via a `make` target) starts the stack with no per-service step; the frontend reads the API on one origin; data survives a restart (B2) |
| S2.2 | 16 | `make test-integration`: the `vt-test` Compose project, migrations, transaction isolation, committed fixtures; the `postgres-integration` job target | S2.1; **T3 (#31)**; (#68 runs #26's persistence test on Postgres after) | Docker host or CI | Testing | `make test-integration` green; `E-GUARD` refuses a non-test database/host |
| S2.3 | 19 | CI pipeline: `unit`, `sqlite-integration`, `frontend`, `openapi-validation`, `postgres-integration` jobs on every PR; (#67 passes a real `BASE`) | S2.1, S2.2 (needs 14, 16) | — | CI/CD | A PR fails on a broken test in each job and passes on `main`; no job needs a live feed or secret |
| S2.4 | 20 | `make security-scan` + the `security-scan` PR job (dependency audit; high/critical fail, lower reported) | S2.3 | approve the scan tools (e.g. `pip-audit`, `npm audit`) | CI/CD, Testing | `C-FIXTURE-VULN` fails, `C-FIXTURE-CLEAN` passes |
| S3.1 | 17 | Terraform modules (state bucket, OIDC deploy roles, one server + Elastic IP, instance role, EBS, bootstrap); push-to-`main` build-once → tag → GHCR; the `dev` Compose project behind the reverse proxy at `dev.<eip>.sslip.io` | S2.1 | **AWS account + Budgets alert** (aws-setup steps 1,3); approve installing Terraform; human runs bootstrap + first `apply` + first deploy | Deployment | The dev URL answers the frontend; the deploy log names one image digest |
| S3.2 | 21 | Auto dev deploy on merge to `main` (assume dev role, deploy by tag, record tag+digest; skip-and-report when the server is stopped) | S3.1, S2.3 (needs 17, 19) | nightly-stop off while graders visit (aws-setup step 10) | CI/CD | A merge updates `dev` with no rebuild; a red test leaves the old version; a merge to a stopped server ends in the skipped-and-reported summary |
| S3.3 | 18 | The `prod` Compose project + `app.<eip>.sslip.io` on the same server; manual `workflow_dispatch` in the `production` environment (human reviewer, tag defaults to dev's, nothing rebuilt); runbook + rollback | S3.1 | **GitHub `production` environment** with the human as required reviewer; production secrets (aws-setup step 6) | Deployment, CI/CD | Prod runs the same digest as dev; one rollback to the previous tag recorded in the deploy log |
| S3.4 | 22 | Pilot seed data registered through `POST /assets` (human repos + OWASP Juice Shop, A41 fallback) | task 4 (done), S3.1 | supply the exact repository URLs | US-1, US-2 | Each asset shows a scan status and at least one finding on dev |

## Ordering if AWS is slow

If the AWS prerequisites hold up S3.1-S3.3, S2.1 → S2.2 → S2.3 → S2.4 still bank
Containerization, Testing and the first CI/CD rung, and the Tier C local-Compose
work (C2, C3, C5, C6, C7) can run before S3 ([`roadmap.md`](roadmap.md)
§ "Ordering if AWS is slow"). The demo-defect switch is removed (`P-FLAG-GONE`)
before the first production deploy.

## The human's parallel prerequisites (start any time)

From [`_docs/aws-setup.md`](aws-setup.md); none waits for S1:

1. AWS account hygiene + region (steps 1-2).
2. AWS Budgets alert before any stack exists (step 3) — gates S3.1.
3. Hostnames/TLS: `sslip.io` from the Elastic IP, HTTPS from Let's Encrypt (step 4) — closed by H5.
4. GitHub `production` environment with the human as required reviewer (step 6.1) — gates S3.3.
5. `main` branch protection that refuses the responder's push (step 6.4) — needed by Tier C, not Tier B.
6. Existing OIDC provider check, deploy-role secrets, SES sender (steps 7-9).
7. **T3 (#31)**: the Compose Postgres recipe and dev-container rebuild — gates S2.1 and S2.2 (parallel tooling track, roadmap).
