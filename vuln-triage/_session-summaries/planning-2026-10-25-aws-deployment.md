# Session summary: first AWS deployment, dev and production (2026-10-25)

Same Claude Code cloud session as `planning-2026-10-25-cloud-tasklist.md` (branch `claude/quirky-brahmagupta-uisrck`). The human ran every AWS and GitHub settings step from their own clean clone and browser; the agent held no AWS credentials, ran no `terraform apply`, and guided step by step.

## What was done

- **Terraform applied by the human** (Kiro / IAM Identity Center account, `us-east-1`, state in S3): bootstrap (4 resources), deploy-roles (5, GitHub OIDC provider created), server (15; nightly stop off). Server `i-090e482680338eb75`, Elastic IP `52.206.221.145`, hostnames `dev.52-206-221-145.sslip.io` and `app.52-206-221-145.sslip.io`.
- **Code fixes found while deploying** (on `main` through PRs 204, 205 and 206): the Elastic IP and security group were left to Terraform; the deploy-roles trust policy now matches the real OIDC `sub` claim, which carries immutable owner and repo ids (found through the CloudTrail `userName`); the Caddy deploy no longer sends a placeholder ACME contact email (Let's Encrypt refused it, ZeroSSL issued the certificate); the secret read policy and the data-volume mount wait were tightened.
- **Dev live** over HTTPS at `https://dev.52-206-221-145.sslip.io`. A public shared reviewer login was created (human decision) and four public repositories were registered from `deploy/demo-seed.json`; scans produced findings. The README's "Try it as a reviewer" section carries the login.
- **Production promoted** (run #31, tag `20261025-160125-215ea78`). The first run was not gated: the `production` environment had no Required reviewers rule. The human added it and unticked administrator bypass.
- **Rollback rehearsed** as a gated run (#32): `deploy-prod` waited 58 s for approval, then deployed the explicit earlier tag `20261025-152518-37baad0` (SSM command `be22c253-99b9-4d99-b119-ce97019ad49a`).
- **Forward run** (#33, commit `215ea78`, tag left blank): success in 6m 56s. The human confirmed `https://app.52-206-221-145.sslip.io` loads. Run #34 was a queued duplicate behind #33.
- README and `_docs/human-tasklist.md` (A6, A9, A12-A14) updated to match.

## Approvals asked for (permission review)

| Action | Basis | Group | Outcome |
|---|---|---|---|
| `git push -u origin claude/quirky-brahmagupta-uisrck` (several times) | Pushes to an external service; the pre-push `make verify` ran each time | writes to the record (keep asking) | Pushed |
| `mcp__github__create_pull_request` (PRs 204, 205, 206, and the PR for this branch) | Posts to GitHub; opened only after the user said to | writes to the record (keep asking) | Opened |
| Write to `.env` | Not attempted this part of the session | n/a | n/a |

All AWS and GitHub settings actions were done by the human, not the agent.

## Findings and risks for the human

- **Not verified by an agent:** that the live URLs load (the human reported it), the digests of run #33, and the `production` environment settings beyond the gated run's behaviour (reviewers on, administrator bypass off).
- `GITHUB_READ_TOKEN` in `vuln-triage/dev` is not confirmed; scans worked without it.
- Caddy logs were not re-read after the #206 deploy to confirm no `invalidContact` errors.
- CC33: Postgres `pgdata` lives on the root disk, not the snapshotted `/data` volume.
- B6 (`ghcr.io`, `pkg-containers.githubusercontent.com`) and B7 (`.env`) still block Docker runs in cloud sessions.
- The nightly stop is off. Leave it off until after grading, or the demo URL goes down at 04:00 UTC if it is turned on.
- The rubric re-audit has not been run since the deployment; the recorded score is still 17 (2026-10-25 audit at `fb24904`).

## Next

Rubric re-audit with the deployment evidence; the responder decisions F1-F3; closing #141, #143 and #144 (the human's call); peer reviews; submission.
