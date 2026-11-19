# Issue #162: Terraform: the instance's IAM role and the budgets, applied by the human

**Date:** 2026-11-14T10:05Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

`terraform/iam-and-budgets/` defines, as a part only the human applies: the instance role (trusts only `ec2.amazonaws.com`; the AWS-managed Systems Manager core policy plus one inline statement allowing only `secretsmanager:GetSecretValue` on one secret ARN given as a variable) and its instance profile (output by name or ARN); a daily Data Lifecycle Manager snapshot schedule selecting volumes by tag `project=socboard`, 7 kept, with its own execution role; and budget notifications at 50, 80 and 100 percent of a human-set monthly amount, to a human-set address. State goes to the #154 bucket under its own key. A new README section gives the human's steps and teardown, and the decision record `_docs/decisions/2026-11-14T0907Z-instance-iam-snapshots-budgets.md` is `approved`.

Worked by Session A (Kiro Web). Heavy tier. Branch `issue-162-tf-iam-budgets`, PR #174, merge commit `e4eca0a`. QA passed at `1f14fba` (https://github.com/andrew-chung-au/socboard/issues/162#issuecomment-6875111217). The one Reviewer pass found five items, all applied in one fix round (`2ca5115`); its QA re-check (https://github.com/andrew-chung-au/socboard/issues/162#issuecomment-6875326313) and the independent second QA launch in a new session (https://github.com/andrew-chung-au/socboard/issues/162#issuecomment-6875396358) both passed at `2ca5115`. A later commit, `c065d86`, set the record's Status to `approved` and its index row to Current; it changes no Terraform.

**What I learned:** the Reviewer's findings after a QA PASS were README and wording gaps plus one tag risk. Only one (a role comment that said "tag-scoped" about an account-wide managed policy) could have misled the human at the first apply. Recommending all five was my call and created the round; four could have been follow-ups.

## Reflection

### Engineer

Build (https://github.com/andrew-chung-au/socboard/issues/162#issuecomment-6875058635) and fix round (https://github.com/andrew-chung-au/socboard/issues/162#issuecomment-6875276658): the Engineer comments carry their own Reflection blocks. The first push failed `terraform validate` because the provider refuses a comma in the snapshot policy description; it was fixed in one round with no Terraform available locally.

### QA

unknown (role not asked)

### Orchestrator

I started this issue after "ok do #162" in answer to a message that also asked whether the human had read the new text; I recorded that in the claim. Six launches (Engineer, QA, Reviewer, fix Engineer, QA re-check, second QA) against a minimum of two prompted the human to drop the Reviewer (PR #176).

## Launch usage

Engineer: 2 launches (build with one CI fix inside; fix round). QA: 3 launches (PASS at `1f14fba`; PASS at `2ca5115` as the narrow re-check; PASS at `2ca5115` as the independent second launch, new session). Reviewer: 1 launch (`1f14fba`). Active time and tool uses were not given: unknown.

## Files created or modified

- `terraform/iam-and-budgets/{main.tf,variables.tf,outputs.tf,backend.tf.example,terraform.tfvars.example}` (new)
- `terraform/README.md` (new section)
- `_docs/decisions/2026-11-14T0907Z-instance-iam-snapshots-budgets.md` (new), `_docs/index.md` (one row)
- `_session-summaries/2026-11-14T1005Z-issue-162-orchestrator-instance-iam-budgets.md` (this file)

## Decisions made by the human

- Option A for the snapshot schedule (it lives in this part), approved on #139's second Reviewer report.
- "ok do #162" as the go to start the Engineer.
- Reviewer findings 1 to 5: "recommendations approved". For finding 2 the orchestrator picked the option that keeps the issue's tag selection and writes a rule for D17b (its root volume must not carry `project=socboard`); the human did not choose between the options.
- "ok but it seems like a lot of rounds": narrow QA re-check, then the independent second QA launch.
- "decision approved": the record's Status set to `approved` (commit `c065d86`, set by the orchestrator in the human's name).
- Dropped the Reviewer role (decision record `2026-11-14T0953Z-drop-reviewer.md`, PR #176), with the `AGENTS.md` Ponytail line approved.
- Merged PR #174 after marking it ready.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI runs 43580747723 and 43580744457 on `2ca5115`: `VERIFY: PASS`, 208 frontend tests).
- **Terraform check:** run 43580747659 on `2ca5115`: Terraform 1.17.2, `fmt` passed, `init -backend=false` and `validate` passed for `terraform/iam-and-budgets` and `terraform/state`.

## Proposed AGENTS.md changes

none

## Temporary changes

Worktree `.scratch/wt/162` (git-ignored); not deleted.

## Interruptions

none

## Unrelated problems noticed but not fixed

QA's Low risks, all open: customer-managed key on the secret needs `kms:Decrypt`; the 100 percent budget notification fires on actual spend above the limit; "7 kept" in the policy description can go stale; no source-account condition in the two trust policies; the secret ARN check accepts any suffix; `terraform/README.md` has two top-level headings; the session summary named in the PM's expected paths is this file.

## Follow-ups for the next session

- The human's first apply and the `VERIFY:` items: the managed Systems Manager policy name and its width; whether DLM needs `execution_role_arn`, its trust principal and managed policy; DLM argument names, the `03:00` UTC time and tag selection before the volume exists; the budgets API from `us-east-1` and the confirmation mail; the provider `region` argument; that snapshots taken survive a `destroy`.
- D17b's issue must carry the criterion that its root volume does not carry `project=socboard`, or the human accepts the extra snapshots.
- #156's deny on CI's apply role must cover `iam:*` (including `socboard-instance` and `socboard-snapshot`), `dlm:*`, `budgets:*` and `ec2:DeleteSnapshot` if CI holds EC2 rights.
