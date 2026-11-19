# Issue #156: Terraform: GitHub OIDC access for CI, with separate plan, apply and deploy roles

**Date:** 2026-11-14T0928Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Wrote `terraform/ci-access/` (Heavy tier): one GitHub OIDC provider and three roles. The plan role trusts the pull-request subject and is read-only. The apply role trusts the `infra` Environment, reaches only the `server/` state prefix and the server part's EC2 resources, may pass only the instance role, and is denied every other IAM action, reads included (two deny statements); it is also denied the human-applied services (DLM and budgets) and snapshot delete and sharing. The deploy role trusts the `deploy` Environment and may send one custom Systems Manager document (`socboard-deploy`) to instances tagged `project=socboard`. All three deny reading a secret's value. Also added a section in `terraform/README.md`, the decision record `_docs/decisions/2026-11-14T0928Z-ci-oidc-roles.md` (status `proposed`), its row in `_docs/index.md`, and the human task file for the non-`main` branch check (D19's evidence, marked `NOT CHECKED`).

Work ran in one Kiro Web session as Engineer; no PM, QA or Reviewer launch happened. Issue body hash checked before starting: `a825cebe...3eb9`, matches the recorded one.

**What I learned:** the GitHub API (`repos/<owner>/<repo>/actions/oidc/customization/sub`) reports this repository uses the immutable subject, `repo:<owner>@<owner id>/<repo>@<repo id>`. That settles most of the "numeric id" `VERIFY:`: the ids are in the subject, so no customised claim is needed. It was read from the API, not from a real token.

## Reflection

unknown (role not asked)

## Launch usage

none

## Files created or modified

- `terraform/ci-access/main.tf`, `plan.tf`, `apply.tf`, `deploy.tf`, `variables.tf`, `outputs.tf`, `backend.tf.example`, `terraform.tfvars.example` (new)
- `terraform/README.md` (a new section)
- `_docs/decisions/2026-11-14T0928Z-ci-oidc-roles.md` (new, `proposed`), `_docs/index.md` (one row)
- `_human-tasks/2026-11-14T0928Z-human-task-156-engineer-ci-access-apply-and-branch-check.md` (new)

## Decisions made by the human

None this session beyond starting the work. Open for the human: approve the decision record (only the human sets `approved`).

## Mismatches with the spec or design docs

- The issue says the plan role is "read-only, including the state bucket". The native S3 lock needs a write, so the plan job must run with `-lock=false` (D18b). Recorded in the decision record and README.
- The issue says "one custom document (fixed script, one parameter validated by a pattern)". That document is created by the CI-applied server part (D17b or D17c), not here; the roles only name it `socboard-deploy`. D17b's backend key must start with `server/` and its document must use that name.
- The AWS account may already hold a GitHub OIDC provider (AWS allows one per URL). README step 1 has the human check first; if one exists, `reuse_oidc_provider_arn` names it and none is created. A second create would fail.

## Commands to validate

- **Verify:** `make verify`: Python tests could not run here (uv could not write its cache: read-only file system), whitespace passed, no test files changed. Not a result about this change (no Python touched); CI is the evidence.
- `terraform fmt -check` and `validate`: not run locally (Terraform and the provider could not be downloaded: 403 and no package access). They have run only in CI: the `terraform check` workflow ran `fmt -check -recursive` and `validate` on 51aa301 and passed (run 43593591460). `plan` and apply have not run.
- Refused-case searches, run by `grep` over `terraform/ci-access`: no `aws_secretsmanager_secret_version`, no secret-reading `data` block (the only `data` block is `aws_caller_identity`), no access key or user, no AWS-owned document named in an allow, three outputs that are role ARNs. The kit's secret scan reported nothing on every file.
- The apply role cannot create or modify IAM: shown by reading the policy (two denies: `iam:*` with `NotResource` = the instance role, and `NotAction` = `iam:PassRole` on the instance role, so the only IAM action left is passing that one role). No plan or test could run; the human's plan (README step 5) is where it is read.

## Proposed AGENTS.md changes

None. The `terraform/` Layout line is already there.

## Temporary changes

Downloaded and deleted a Terraform binary attempt (403, nothing kept) and a failed `pip` install into `.scratch/` (nothing kept). Both folders removed.

## Interruptions

none

## Unrelated problems noticed but not fixed

- `make verify` cannot run the Python tests in the Kiro Web sandbox: uv fails creating `~/.local/share/uv/python` on a read-only file system.
- #154 is still open although its pull request (#171) is merged; the orchestrator closes it.
- #162's branch and this one both append a section to `terraform/README.md`; expect a trivial merge conflict in that file.

## Follow-ups for the next session

- The human reads and approves (or changes) the decision record.
- D19 (not filed yet): human first apply, the Environments' `main`-only rule, and the refused assume-role check from a throwaway branch (task file above).
- D17b must keep its state key under `server/` and name its document `socboard-deploy`.
- D18b: the plan job uses `-lock=false`.
