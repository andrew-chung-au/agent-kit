# Verifying the Terraform (task 17 / #141; task 21 / #142; task 18 / #143)

How to check the `terraform/` modules before and after applying them. The agent
writes the Terraform; **the human runs every `terraform apply`** and performs the
checks in §3-§6 (the agent holds no AWS credentials and never applies —
`_docs/architecture.md` § Security boundaries, `_docs/aws-setup.md`).

Task 21 (#142, the automatic dev deploy) adds **one** read-only permission to the
deploy-roles module; §6 is its own re-apply-and-verify section. A later task that
changes any `terraform/` file must add the same kind of note: say which module to
re-apply and what to check.

This runbook is the single place that says what "the Terraform is verified"
means. It complements, and does not replace:
- `_docs/aws-setup.md` — the ordered human AWS/GitHub runbook (account, region, budget, bootstrap, secrets).
- `_docs/architecture.md` § Deployment — the design the modules implement (modules table, A36, the pipeline, cost controls, teardown).

Modules (see `terraform/README.md` for the layout):

| Module | Path | Applied | State |
|---|---|---|---|
| Bootstrap (state bucket) | `terraform/bootstrap/` | once, by hand | local, then moved into the bucket |
| Deploy roles (OIDC + dev/prod roles) | `terraform/deploy-roles/` | once, by hand | the state bucket |
| Server (EC2, EIP, SG, instance role, schedule) | `terraform/server/` | by hand; CI only deploys images onto it | the state bucket |

## 1. Static checks (no AWS; the agent, CI or the human can run these)

These need only Terraform (or OpenTofu) and no credentials. They catch syntax,
formatting and internal-reference errors. The push-check image already ships
Terraform (`_docs/push-check-image-guide.md`), so these can run there; they do
**not** contact AWS.

Run in each module directory (`terraform/bootstrap`, `terraform/deploy-roles`,
`terraform/server`):

```sh
terraform fmt -check -recursive      # formatting is canonical (fails if not)
terraform init -backend=false        # download providers, no remote state
terraform validate                   # types, references and required args resolve
```

- `terraform fmt -check` must exit 0 (run `terraform fmt -recursive` to fix).
- `terraform validate` must report "Success" in every module.
- `-backend=false` means `init`/`validate` never touch the real state bucket, so
  this is safe to run anywhere, including CI on a pull request.

A green run here proves the files are well-formed and self-consistent. It does
**not** prove the plan is correct against a live account — that is §3.

## 2. Pre-apply review checklist (the human, reading the diff)

Before the first `terraform apply`, read the module and confirm each item. These
are the security-critical properties the design fixes; a miss here is a defect,
not a preference.

Deploy-roles module:
- [ ] OIDC provider: reused when it already exists (the `create_oidc_provider` variable is `false`), created only when absent — one provider per URL per account (`VERIFY:` the account; `_docs/aws-setup.md` step 7.3).
- [ ] Trust policy audience is `sts.amazonaws.com`; subject is limited to **this** repository, `environment:dev` for the dev role (the `deploy-dev` job declares that environment, so its token has no `ref:` form; the branch limit is the `dev` environment's deployment-branch setting, `main` only) and `environment:production` for the prod role. No wildcard over other repositories or over pull requests (the `sub` claim carries GitHub's immutable ids, `repo:<owner>@<owner id>/<repo>@<repo id>:environment:<name>`, confirmed from a CloudTrail record on 2026-10-25; the variables `github_owner_id` and `github_repo_id` in `deploy-roles/` hold them, and a recreated repository needs new values).
- [ ] Dev role can run only the dev deploy on the server; prod role only the production deploy. **Accepted risk for submission (2026-10-25):** both roles use `AWS-RunShellScript` on the one shared server, so IAM cannot enforce this; the control is process (merged `main` only, the `dev` environment limited to `main`, `production` approval). Fix parked as future-development item X11 (`roadmap-future.md`). Neither can change IAM, Terraform state or the server configuration, or read secrets.
- [ ] Dev role's deploy policy (task 21 / #142): `ssm:SendCommand` scoped to `project=vuln-triage` instances + the `AWS-RunShellScript` document, `ssm:GetCommandInvocation`/`ssm:ListCommandInvocations`, and a **read-only** `ec2:DescribeInstances` (no resource scoping is possible, so it is on `*`). Confirm there is **no** `ec2:StartInstances`/`StopInstances`/`RunInstances`/`TerminateInstances` or any other mutating action — the role only reads state and sends the deploy command (`_docs/architecture.md` Cost controls (2): the deploy "first reads the instance state").

Server module:
- [ ] Security group opens **80 and 443 only**; **no SSH (port 22)** and **no key pair**. Access is AWS SSM Session Manager (the instance role has `AmazonSSMManagedInstanceCore`).
- [ ] One Elastic IP, kept across the nightly stop.
- [ ] EBS data volume with daily snapshots.
- [ ] Nightly-stop schedule present, with an on/off variable **on by default**.
- [ ] Instance role SES permission (for task 37) is send-only and scoped to the one verified sender identity; it is not broader. (May be absent until task 37; note which.)

All modules:
- [ ] Every resource is tagged `project=vuln-triage`.
- [ ] No secret value, AWS account id, access key or password appears in any `.tf` file. Secrets are **names only** (Secrets Manager); the account id lives only in the GitHub repository variables (`_docs/aws-setup.md` step 6.2).
- [ ] No resource the plan says is "not used on purpose" (load balancer, NAT gateway, RDS, ECS/EKS, CloudFront, an AWS container registry) is created.

## 3. Apply and per-module verification (the human, with AWS)

Apply in order (`_docs/aws-setup.md` step 7). After each `terraform apply`, run
`terraform plan` again — a clean apply shows **"No changes"** on the second plan
(idempotence). Then the per-module live check:

1. **Bootstrap (state bucket):** `aws s3api get-bucket-versioning` shows versioning enabled; the bucket is private and encrypted (`VERIFY:` the console/CLI path). Then move the state into the bucket as `terraform/README.md` instructs and confirm a later `terraform init` finds it.
2. **Deploy roles:** the two role ARNs appear in `terraform output`. Copy them into the GitHub variables `AWS_DEV_ROLE_ARN` / `AWS_PROD_ROLE_ARN` (`_docs/aws-setup.md` step 6.2). Confirm the trust policy in the console matches §2 (repo, branch/environment conditions).
3. **Server:** `terraform output` names the Elastic IP; the instance is `running`; a Session Manager session connects (no SSH); the `project=vuln-triage` tag is on the instance, volume and EIP. Record the two hostnames `dev.<eip>.sslip.io` and `app.<eip>.sslip.io` in the #141 issue.

## 4. Acceptance for #141 (the dev environment answers)

Task 17's acceptance is end-to-end, so it needs the first deploy (the human runs
it, `_docs/aws-setup.md` steps 6-8). Confirm all of:

- [ ] A push to `main` ran the build-once job: an image tagged `YYYYMMDD-HHMMSS-shortsha` is in GHCR, and the **deploy log names the image digest**.
- [ ] The `dev` Compose project is up on the server behind the reverse proxy.
- [ ] **`https://dev.<elastic-ip>.sslip.io` answers the frontend** (the sign-in page) over HTTPS. If Let's Encrypt refuses the shared `sslip.io` name, the A36 fallback is in effect (staging cert, then `nip.io`); note which was used.
- [ ] `sslip.io` resolves the hostname to the Elastic IP (`VERIFY:` the exact name form).

Record the dev URL, the image tag and its digest in the #141 issue; that is the
evidence the task is done.

## 5. Teardown verification (the human, at end of life)

Follow `_docs/aws-setup.md` step 11 / `_docs/architecture.md` Teardown. After
`terraform destroy` (server, then deploy roles, then empty+delete the state
bucket), confirm **no resource tagged `project=vuln-triage` remains** (Tag Editor
or Resource Groups; `VERIFY:`), the Elastic IP is released, and the next bill
shows no running charges.

## 6. Re-apply for the automatic dev deploy (task 21 / #142)

Task 21 adds the `deploy-dev` job to `.github/workflows/deploy.yml` (deploy the
`dev` Compose project on merge to `main`, and skip-and-report when the server is
stopped). For the job to "first read the instance state" before it calls the
server, the **dev deploy role gains a read-only `ec2:DescribeInstances`
statement** in `terraform/deploy-roles/main.tf`. This is the only Terraform
change for #142.

Re-apply (the human, with AWS):

- [ ] **Re-apply the deploy-roles module** (`terraform apply` in `terraform/deploy-roles/`). The role ARN is unchanged, so the GitHub variable `AWS_DEV_ROLE_ARN` does **not** change. Confirm the second `terraform plan` shows **"No changes"** (idempotence).
- [ ] The dev role now has the §2 permissions, including `ec2:DescribeInstances` and **no** mutating EC2 action (re-check the §2 dev-role item).

Then the end-to-end check for #142 (needs a push to `main`):

- [ ] **Server running:** a merge to `main` with the tests green runs `deploy-dev`, which deploys the `dev` project by image tag and records the tag and both image digests in the job summary (the deploy log). `https://dev.<elastic-ip>.sslip.io` answers the new build (no rebuild on the server — it pulls the tag).
- [ ] **A red test leaves the previous version running:** a merge whose tests fail does not deploy (the push-to-`main` build/deploy is gated by the required test jobs); the running `dev` build is unchanged.
- [ ] **Server stopped (the nightly stop):** a merge while the instance is `stopped` ends with the visible summary **`dev deploy skipped: server stopped`** — the job does **not** call the server, is **not** a pass-as-deployed and **not** a failed deploy. After starting the server (EC2 → Instances → Start) and re-running the workflow, the deploy completes (`_docs/aws-setup.md` step 10, `_docs/architecture.md` Cost controls (2)).

Note: the `deploy-dev` job runs only on push to `main`; pull requests never
receive an AWS role (confirmed by the `deploy` workflow not running on PRs).

## 7. Production promotion and rollback (task 18 / #143)

Task 18 adds the manual `deploy-prod` job to the same `.github/workflows/deploy.yml`
(a `workflow_dispatch` in the `production` environment) and refactors the
server-side logic into one shared `terraform/server/deploy-env.sh` that both the
dev and prod deploys run. **No Terraform change is needed** — the prod deploy
role and the instance role (Secrets Manager read) already exist from task 17,
and the prod role shares the same deploy policy as the dev role (including the
`ec2:DescribeInstances` added in §6). The prod deploy carries **no secret**: the
server reads `vuln-triage/prod` from Secrets Manager with the instance role.

Prerequisites (the human):

- [ ] The `production` GitHub environment exists with the human as the **required reviewer** (`aws-setup.md` step 6.1), and the repo variable `AWS_PROD_ROLE_ARN` is set (§3 / `aws-setup.md` step 7).
- [ ] The Secrets Manager secret `vuln-triage/prod` exists with at least `POSTGRES_PASSWORD` (`aws-setup.md` step 8). The instance role reads it; the deploy role cannot.

End-to-end checks (needs a `workflow_dispatch` run):

- [ ] **Promotion gates on approval:** Actions → deploy → Run workflow pauses on the `production` environment until the human approves; the prod OIDC credential is only issued for the `production` environment (not `main`, not PRs).
- [ ] **Default tag = dev's current tag:** running with a blank `image_tag` promotes the tag currently running in dev (read from `/opt/vuln-triage/dev/.env` on the server); an explicit tag overrides it. Nothing is rebuilt.
- [ ] **Prod answers and shares dev's digest:** `https://app.<elastic-ip>.sslip.io` answers the frontend; when the promoted tag is dev's current tag, `dev` and `prod` run the **same image digest** (the deploy log names it). Both hostnames are served by the one shared Caddy (`vt-caddy`), so bringing up `prod` leaves `dev` serving.
- [ ] **Rollback:** re-running the workflow with the **previous** tag from an earlier "prod promotion" deploy-log entry rolls production back; a failed pull leaves the running containers in place (`_docs/architecture.md` Rollback). The rollback is recorded as a new deploy-log entry.
- [ ] **Stopped server:** a promotion while the instance is stopped ends with a visible "prod promotion skipped: server stopped" summary and does not call the server.
- [ ] `DEPLOYMENT_ENVIRONMENT=prod` is set on the prod backend (so `VT_FEEDS=fixtures` / `VT_DEMO_DEFECT` fail closed; `architecture.md` Environment signal). Confirm the prod `.env` on the server carries it.

Note: the demo-defect gate `P-FLAG-GONE` runs in this production workflow but its
step is added by task 29 (#161), not task 18.

## Notes / VERIFY (settled at apply time)

These carry `VERIFY:` in `_docs/architecture.md` / `_docs/aws-setup.md` and are
confirmed against the AWS/Terraform docs when the human applies:

- SSM Run Command (or an equivalent) as the deploy mechanism. Task 21 (#142) implements it as `ssm:SendCommand` on the `AWS-RunShellScript` document, with the dev role reading state via `ec2:DescribeInstances`; confirm on the running stack that the instance is an SSM-managed target and the command runs under the AL2023 shell.
- S3-native state locking (no DynamoDB lock table) in the Terraform version used; if absent, a lock table is added to the bootstrap module.
- `t3.medium` sizing (fallback `t3.small`).
- Let's Encrypt rate limits for the shared `sslip.io` name; the staging-cert / `nip.io` fallback.
- The Terraform version the AWS provider needs, and Terraform's current licence (OpenTofu runs the same files).
