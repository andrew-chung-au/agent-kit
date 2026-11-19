# Deploy evidence timeline: what was checked on the real systems, when, and the result

Steps: _docs/agent-kit/templates/human-task.md

A dated record of every check the maintainer or CI made against AWS, GitHub and the server during the Deploy phase. Each check is recorded once, when it happened (`.kiro/steering/evidence-and-steps.md`, rule 2); a check is repeated only when the thing it checked has changed, and the row says why. Where a human task holds the full result table, this file links it instead of copying it.

- **Who ran the checks:** the maintainer, from their own machine (WSL, Terraform 1.17.2, AWS CLI v2, SSO profile `socboard`), with the planning session writing the steps.
- **What "as reported" means:** the maintainer reported the result; the raw output was not kept.
- **Never in this file:** the AWS account number, any ARN that contains it, role unique IDs, the notification e-mail address, tokens, keys or secret values. The Elastic IP and the hostname are public.

## Timeline

| When (UTC) | What was checked | Result | Record |
|---|---|---|---|
| 2026-11-15 | Terraform 1.17.2 installed as the exact release binary, SHA-256 verified | PASS | #207 row 1 |
| 2026-11-15 | First attempt at `state/` and `iam-and-budgets/` ran in the organisation's main account: the CLI fell back to a `default` IAM-user profile because no step said to sign in | Incident. Both torn down there; the main account holds no socboard resource. Lesson filed in #254 (sign in first, check the account before every apply) | this file |
| 2026-11-15 | During that attempt the local state was deleted before it was moved to the bucket; the 6 resources were re-adopted with `terraform import` | Recovered (`No changes` after import). Lesson in #254 (check the bucket before any delete; rename, never delete) | #207 row 3 |
| 2026-11-15 | `state/`, `iam-and-budgets/`, `ci-access/` applied in the SSO member account | PASS | #207 rows 2 to 4, 8 |
| 2026-11-15 | GitHub settings: `infra` and `deploy` Environments, role ARNs as secrets, `TF_STATE_BUCKET` variable, read back by `gh api` | PASS | #207 row 11 |
| 2026-11-15 | `can_admins_bypass` is the field for "administrators not exempt": set by `PUT`, read back by `GET` (`deploy` changed from true to false) | Verified | this file |
| 2026-11-16 | #156 branch probes: plan role assumed from a pull request; apply and deploy roles refused from throwaway branches | PASS | #156 task file, steps 1 to 5 |
| 2026-11-16 | `server/` applied (at `5cc7352`, with #233's bootstrap): online, bootstrap done, data volume mounted, egress 80/443 only, `ghcr.io` reachable, `https://<hostname>/` answers 502 with a valid certificate | PASS | #207 rows 12 to 22 |
| 2026-11-16 | A second plan in all four folders | `No changes` (as reported) | #207 row 23 |
| 2026-11-16 | Plan role refusals: a dry-run tag write and a secret read | `UnauthorizedOperation`, `AccessDeniedException` | #207 rows 24, 25 |
| 2026-11-16 | Peer address behind host Caddy, measured with a throwaway container on the stack's subnet: Docker 29.1.3 gave the network the gateway `10.231.77.128` (no gateway set), and that was the peer the container saw; a forged `X-Forwarded-For` was replaced by Caddy | Finding: gateway pinned to `10.231.77.1` in `compose.yaml` (#261, CI-checked). Throwaway network removed | #261 |
| 2026-11-16 | The ghcr.io package is public: an anonymous pull token is issued and the tag list returns 200; the newest tag matched the tip of `main` (`20261115-184800-95d2ae3`) | PASS | this file |
| 2026-11-16 | `terraform-plan.yml` run 43747150371 printed the plan role's unique ID (the credentials action's "Authenticated as assumedRoleId" line; `mask-aws-account-id` does not cover it) | Incident. Logs deleted; it was the workflow's only run. `AWS_PLAN_ROLE_ID` and `AWS_DEPLOY_ROLE_ID` stored as secrets so GitHub masks them; a log check is part of #209 | #209 |
| 2026-11-16 | Prod access, the parts that need no new code: secret `socboard/app-prod` created empty; Environment `deploy-prod` with the maintainer as required reviewer, admin bypass off, `main` only, read back | Done | #268 task file |
| 2026-11-16 | D19b: `server/` re-applied with #256's hardened bootstrap. Plan `4 to add, 0 to change, 3 to destroy` (instance, volume attachment and EIP association replaced; the `socboard-deploy` document created); data volume and Elastic IP untouched; new instance online; bootstrap done; owners root 755, uid 999 700 (named `dnsmasq` on the host; nothing runs as uid 999), caddy 700; Docker and Caddy active; 502 with a valid certificate; a re-run of the bootstrap wrote nothing; reboot recovered; second plan `No changes` | PASS. Re-run of the host checks because the bootstrap changed (rule 2) | #236 |
| 2026-11-16 | #266: `server/` applied with the prod site. Plan `3 to add, 0 to change, 3 to destroy` (instance, volume attachment and EIP association replaced); data volume and Elastic IP untouched; new instance online; bootstrap done; `postgres-prod/` 999 and 700 beside `postgres/`; the Caddyfile has two sites and `caddy validate` says `Valid configuration`; dev and prod hostnames both answer 502 with valid certificates (prod's newly issued); a re-run of the bootstrap wrote nothing; second plan `No changes`. Reboot not re-tested (D19b proved it) | PASS (as reported) | #266 |
| 2026-11-16 (pending) | Step 9: the daily snapshot covers the data volume only, with the tag copied | Pending, after 04:00 UTC | #207 rows 28, 30 |
| 2026-11-16 (pending) | #240: the restore rehearsal on a scratch volume, one routine deploy by hand, one rotation, and the teardown read against the README (the runbook `_docs/runbooks/deploy-and-teardown.md`) | NOT CHECKED until the human runs it | `_human-tasks/2026-11-16T0351Z-human-task-240-engineer-restore-rehearsal-and-runs.md` |
| 2026-11-17 | #267: the first prod deploy by hand (prod's secret value, one send with dev's running digest and `environment=prod`, dev unchanged). The first send exited 3 because the instance role could read only dev's secret; a re-apply of `iam-and-budgets` (1 changed) fixed it, and the second send printed `socboard-deploy: deployed.` The repeat and bad-environment sends were not run. | PASS, with four rows NOT CHECKED | `_human-tasks/2026-11-17T0030Z-human-task-267-engineer-first-prod-deploy.md` |
| 2026-11-17 | #269: the first promote to prod from CI, started and approved by the maintainer in `deploy-prod`; `socboard-deploy: deployed.`, health 200, `deploy-record-prod` uploaded | PASS | [run 44001761105](https://github.com/andrew-chung-au/socboard/actions/runs/44001761105); `_human-tasks/2026-11-16T0332Z-human-task-269-engineer-promote-and-rollback.md` |
