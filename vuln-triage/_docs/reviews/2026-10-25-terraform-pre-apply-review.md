# Terraform pre-apply review (CC10) and static check (CC9)

- Date: 2026-10-25. Reviewer: orchestrator, Claude Code cloud session (no AWS credentials).
- Scope: `terraform/bootstrap`, `terraform/deploy-roles`, `terraform/server` at `fb24904`, against the checklist in `_docs/terraform-verify.md` §2 and the deploy workflow `.github/workflows/deploy.yml`.
- Method: read every `.tf` file and `user-data.sh` (630 lines). **Nothing was planned or applied.** `terraform validate` and `plan` did not run (see "Static check"), so findings about AWS behaviour are from reading and my knowledge of AWS and GitHub, and are marked `VERIFY:` where I am not certain.
- Fixes are proposals. No `.tf` file was changed.

## Summary

Two findings will stop the first apply or the first dev deploy, so fix them before A6. Three more are likely defects or design limits. The checklist items for the security group, Elastic IP, tagging, secrets-in-code and unused resources pass.

| # | Severity | Finding | Blocks |
|---|---|---|---|
| F1 | High | The dev role's trust policy can never match the dev deploy job | A9 (first dev deploy) |
| F2 | High | The server module needs both secrets to exist at plan time, but the tasklist creates them after the apply | A6 (server apply) |
| F3 | Medium | `ssm:SendCommand` is conditioned on a tag that the document resource does not have | A9 (probably) |
| F4 | Medium | `user-data.sh` may format the data volume before it is attached | A9 (server bootstrap) |
| F5 | Medium | Both roles share one policy that can run arbitrary root commands on the server holding both environments | design, not blocking |
| F6 | Low | Smaller items, listed below | none |
| F7 | Medium | Security group egress description had an apostrophe, which AWS rejects (found by `validate`) | A6 (server apply); **fixed** |

## Findings

### F1 (High): dev trust policy expects the wrong `sub` claim

`deploy-roles/main.tf:47` requires `repo:andrew-chung-au/vuln-triage:ref:refs/heads/main`. The `deploy-dev` job declares `environment: dev` (`deploy.yml:105`). When a job references a GitHub environment, GitHub issues the OIDC `sub` claim as `repo:<owner>/<repo>:environment:<name>`, not the `ref` form. So `sts:AssumeRoleWithWebIdentity` is refused ("Not authorized") and every dev deploy fails at the "Assume the dev deploy role" step. The repo does not customize the claim (searched for `include_claim_keys`, `use_default`). The prod role already uses the environment form (`main.tf:70`), which is correct for `deploy-prod`.

Proposed fix (Terraform, not a protected file): change the dev condition to `${local.repo_sub_prefix}:environment:dev` via a `dev_environment` variable, mirroring `production_environment`. Restrict deployment branches to `main` in the `dev` environment's GitHub settings (A3) so the branch limit is not lost. Alternative: remove `environment: dev` from the workflow (protected `.github/`, needs approval), but then the `dev` environment settings and variables are unused. Update `terraform-verify.md` §2 line 58 and `aws-setup.md` line 106, which both say `ref:refs/heads/main`. `VERIFY:` the claim format against the run's token once, for example by reading the failed-assume error or the `sub` in a debug step.

### F2 (High): secrets must exist before the server apply

`server/iam.tf:30` uses `data "aws_secretsmanager_secret" "env"` over `var.secret_names` (default `vuln-triage/dev` and `vuln-triage/prod`). A data source for a secret that does not exist fails at plan time. The human tasklist applies the server at A6 and adds the dev secrets at A7 and the prod secret at A12, after the apply. `aws-setup.md` step 8 says "before the first dev deploy", which is consistent with the data source only if both secrets exist before A6.

Proposed fix, either: (a) build the ARNs without a lookup, `arn:aws:secretsmanager:<region>:<account>:secret:vuln-triage/dev-*` (needs the account id from `data.aws_caller_identity`, so nothing is hard-coded); or (b) add a step before A6 that creates both secrets (even with placeholder values) and update A7 and A12. Option (a) removes the ordering trap and keeps the role limited to exactly those two names.

### F3 (Medium, `VERIFY:`): `SendCommand` condition on the document resource

`deploy-roles/main.tf:84-95` has one statement with two resources, the `AWS-RunShellScript` document and `instance/*`, and a single condition `ssm:resourceTag/project = vuln-triage`. A document has no `project` resource tag, so the condition is false for that resource and `SendCommand` is likely denied. AWS's documented pattern uses two statements: the instance statement carries the tag condition, the document statement carries none. Fix by splitting the statement. `VERIFY:` against the IAM policy simulator or a real deploy after F1 is fixed.

### F4 (Medium): data volume attached after first boot

`server/compute.tf:41` attaches the volume with a separate `aws_volume_attachment`, created after the instance. `user-data.sh:23-29` runs at first boot, resolves `/dev/sdf` and formats it if `blkid` finds nothing. If the volume is not attached yet, `readlink -f` still returns a path, `blkid` fails, and `mkfs` fails on a missing device. With `set -e` the script stops before `docker network create vt-edge` and never writes `bootstrap.done`. Fix by waiting for the device (a bounded loop on `lsblk`/`test -b`), and by looking the device up by size or serial rather than by `/dev/sdf` (Nitro instances present `/dev/nvme1n1`). `VERIFY:` on the real instance type.

### F5 (Medium, design): roles are not limited to their environment

Both roles use the same policy (`main.tf:125-135`). `AWS-RunShellScript` runs any shell command as root on the one server, which hosts dev and prod and holds the instance role that reads `vuln-triage/prod`. The checklist line "Dev role can run only the dev deploy; prod role only the production deploy" (`terraform-verify.md:59`) cannot be met with IAM alone on a shared server. This is a consequence of decision H3 (one server for both). Mitigations that are available: keep `main` branch protection on, restrict the `dev` environment to `main`, require reviewers on `production` (A3), and use a custom SSM document that runs only the deploy script instead of `AWS-RunShellScript`. Record it as an accepted risk or change the checklist wording; do not leave it unticked silently.

**Decision (human, 2026-10-25): accepted for submission.** The protection is process, not IAM: only merged `main` can assume the dev role (with the `dev` environment limited to `main`, human tasklist A3), `production` needs the human's approval, and `main` is protected. The custom-document fix is parked as showcase item X10 (`roadmap-showcase.md`). The checklist line is therefore recorded as an accepted risk, not a pass.

### F6 (Low)

- `user-data.sh:17` downloads the Compose plugin from `releases/latest` with no checksum (it has a `VERIFY:` to pin).
- `bootstrap/versions.tf` and the others require Terraform `>= 1.6.0`, but S3-native state locking (`use_lockfile`) needs a newer release (`VERIFY:` 1.10). The project pins 1.17.0 elsewhere; raise the floor.
- `server/iam.tf:53-60` SES policy comment says the grant is conditioned on the From address, but there is no `ses:FromAddress` condition. The policy is off by default (`ses_sender_identity_arn = ""`); add the condition before supplying an identity.
- State bucket: no `prevent_destroy`, no policy refusing non-TLS requests.
- `deploy-roles/main.tf:19` thumbprint `ffff…` is a placeholder, used only if `create_oidc_provider = true` (default `false`).
- `aws_instance` does not set `metadata_options { http_tokens = "required" }`; Amazon Linux 2023 defaults to IMDSv2 only, so this is a hardening note, not a defect.

## Checklist result (`terraform-verify.md` §2)

| Item | Result |
|---|---|
| OIDC provider reused when it exists (`create_oidc_provider` default `false`) | Pass |
| Trust audience is `sts.amazonaws.com` | Pass |
| Subject limited to this repo; no wildcard over repos or pull requests | Pass for prod. **Fail for dev (F1)**: wrong claim form |
| Dev role runs only the dev deploy; prod only the prod deploy | **Not met (F5)** |
| Neither role can change IAM, state, or read secrets; no mutating EC2 action | Pass (only `ssm:SendCommand`, read of command results, `ec2:DescribeInstances`) |
| Security group opens 80 and 443 only; no SSH, no key pair | Pass |
| One Elastic IP kept across the stop | Pass |
| EBS data volume with daily snapshots | Pass (DLM, 7 retained); `VERIFY:` the tag target |
| Nightly stop present, on by default | Pass; stop is limited to `project=vuln-triage` instances |
| SES permission send-only, scoped to one identity | Pass while disabled; condition missing (F6) |
| Every resource tagged `project=vuln-triage` | Pass: all three modules set it in `default_tags` |
| No secret, account id or key in any `.tf` | Pass (searched) |
| No unused resource type (load balancer, NAT, RDS, ECS/EKS, CloudFront, registry) | Pass |

## Static check (CC9)

Run in a cloud session with Docker, image `hashicorp/terraform:1.17.0` (the version pinned in `ci/push-check/Dockerfile`), on a copy of `terraform/` under `.scratch/` so the repo stays clean.

- `terraform fmt -check -recursive`: **pass**, all three modules, no diff.
- `terraform init -backend=false` and `terraform validate`: **first attempt blocked**, then run after the human added `registry.terraform.io` and `releases.hashicorp.com` to the cloud environment's allowed domains (B6). Provider `hashicorp/aws v5.100.0` installed for all three modules. `bootstrap` and `deploy-roles` are valid.
- **`server` failed validation (F7, Medium, fixed):** `network.tf` egress description `All outbound (image pulls, Let's Encrypt, SES, SSM)` contains an apostrophe, which AWS security group descriptions do not allow (`"egress.0.description" doesn't comply with restrictions`). It would have failed the first `terraform apply`. Fixed in this branch by rewording to `TLS certificates`. After the fix `server` validates and `fmt -check` is clean on all modules. `validate` checks syntax and provider schema only; it does not run `plan`, so IAM policy behaviour (F1, F3) is still unproven until a real apply and deploy.
- Provider lock files (`.terraform.lock.hcl`) are not committed. `init` resolved `~> 5.0` to 5.100.0. Committing them would pin the provider; if the human applies from a different OS, generate hashes for both platforms with `terraform providers lock` first (F6, Low).
- Container networking: a container cannot reach the session proxy by default. Use `--network host`, pass `HTTPS_PROXY` and mount `/root/.ccr/ca-bundle.crt` as `SSL_CERT_FILE`. Docker Hub pulls by the daemon work.
