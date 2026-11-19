# Issue #209: CI: a read-only Terraform plan of the server part on pull requests (D18b)

**Date:** 2026-11-16T05:46Z (UTC)
**Spec version:** e3461a7

Tier: Heavy. Lanes: Terraform, then CI (a Kiro session) up to 2988b71; a Claude session from 2bd3a05 to f50d5d0 (its summary: `_session-summaries/2026-11-16T0154Z-issue-209-orchestrator-log-check-removal-handover.md`); then the Terraform B lane (this Kiro session) to close-out. Branch `claude/209-terraform-plan`, PR #263.

## What changed and why

- 93f5bf1: the workflow test treats a path ending in `terraform` (for example `/usr/bin/terraform`) as the terraform command (QA FAIL 2 at f82999e).
- 531dd72 (human-approved): ruling A, a step before the credentials step masks the plan role's unique ID from the secret `AWS_PLAN_ROLE_ID`; ruling B, a `log-check` job. 342bb88 and 2988b71 (human-approved) added retries and an HTTP-status line to `log-check`. It never downloaded the log in a live run, so the human removed it (2bd3a05, Claude session) and moved it to follow-up #307.
- 450fbd5: addendum to the decision record for rulings A and B.
- PR #309 (merged as 0d4e1a9): the plan role gets `ssm:DescribeDocumentPermission` on the deploy document, with a terraform test, and the #268 task file's ci-access re-apply covers it. The human applied it, then applied `server/` to clear drift left by #281.
- ad977a1, 978470e: the setup docs name `AWS_PLAN_ROLE_ID` (README Outputs, notes in the #156 and #207 task files, docs index row); a stale sentence in the decision record is fixed. 7db13b0 merges main (one conflict in the #207 task file, main's version kept and the note re-added).
- Seen working: "No changes." on PR #263 (run 43789387489, attempt 4; also run 43801395705 at 978470e); "1 to change" on probe PR #313 (run 43793878102, closed unmerged). Zero role unique IDs in every plan log checked since the mask.

**What I learned:** a role's unique ID is printed by the credentials action and is masked only when the job references it as a secret.

## Reflection

### PM

Reflection:
(1) Grooming fixed facts the first run disproved: "no masking step is needed" (the credentials action printed the plan role's unique ID, so the human ruled a mask step and deleted the logs), a fixed "five workflows" replay count that went stale, and a role read list that missed ssm:DescribeDocumentPermission after main added the SSM document.
(2) The unique ID nearly stayed in public logs; #281 changed server code with no re-apply, so main drifted from AWS, and the new AWS_PLAN_ROLE_ID secret was absent from setup docs until QA launch 2.
(3) Change `_docs/agent-kit/team/pm.md`: a criterion claiming a log holds no sensitive value or listing a role's reads must be tagged VERIFY with a first-run check, and replay counts read "QA states the count at its commit"; measure by body-change rulings after approval on the next five Heavy issues (this one had three).

### Engineer

Reflection:
(1) Three live rounds on the log-check job (531dd72, 342bb88, 2988b71) each failed on the same in-run log download, until the human removed the job (2bd3a05, follow-up #307).
(2) The first test for PR #309 compared a Terraform list with a tuple and would always have failed; the orchestrator caught it before push. One Engineer launch also edited files with Python heredocs, against AGENTS.md.
(3) In `_docs/agent-kit/team/software-engineer.md`, add: when a step depends on something only a live run shows, probe it once on its own, and after one failed retry stop and ask. Expected: fewer fix rounds. Measure: fix commits per such step in `git log`, target at most one.

### QA

Reflection:
(1) Three launch-2 docs FAILs, each needing a fix and a fresh launch: missing secret in docs (https://github.com/andrew-chung-au/socboard/issues/209#issuecomment-6906221660), main-merge conflict (https://github.com/andrew-chung-au/socboard/issues/209#issuecomment-6906624488), stale lines (https://github.com/andrew-chung-au/socboard/issues/209#issuecomment-6906875917).
(2) Launch 1 passed while the new required secret was undocumented, and main moved under the branch twice, so a PASS nearly went stale.
(3) Proposal: in `_docs/agent-kit/team/qa-engineer.md`, make launch 1 also grep the docs for each new secret or variable and check `git merge-tree` against current origin/main; expected effect is fewer launch-2 docs FAILs, measured as launch-2 FAIL count per Heavy issue (here 3).

## Launch usage

The tool does not report active time or tool uses, so each reads unknown.
- Engineer (TERRAFORM_WORD fix, mask step, log-check job): unknown, unknown
- Engineer (log-check retry): unknown, unknown
- Engineer (log-check HTTP status): unknown, unknown
- Engineer (plan-role SSM read, PR #309): unknown, unknown
- Engineer (docs for AWS_PLAN_ROLE_ID): cancelled by the human part-way; unknown, unknown
- QA launch 1 at f50d5d0: PASS; unknown, unknown
- QA launch 2 at f50d5d0: FAIL (docs); unknown, unknown
- QA launch 2 at ad977a1: FAIL (merge conflict with main); unknown, unknown
- QA launch 2 at 7db13b0: FAIL (two stale docs lines); unknown, unknown
- QA launch 2 at 978470e: PASS; unknown, unknown
- PM, Engineer, QA Reflection launches: unknown, unknown

## Files created or modified

- `.github/workflows/terraform-plan.yml`, `tests/test_terraform_plan_workflow.py`
- `_docs/decisions/2026-11-15T1722Z-terraform-plan-ci.md`, `_docs/index.md`
- `terraform/README.md`, `_human-tasks/2026-11-14T0928Z-human-task-156-engineer-ci-access-apply-and-branch-check.md`, `_human-tasks/2026-11-15T0055Z-human-task-207-engineer-first-apply-part-a.md`
- `_docs/records/findings/209.json`, this summary
- PR #309 (merged): `terraform/ci-access/plan.tf`, `terraform/ci-access/tests/trust.tftest.hcl`, `_human-tasks/2026-11-15T2328Z-human-task-268-engineer-prod-access-apply.md`
- Probe PR #313 (closed unmerged): `terraform/server/variables.tf` on `claude/209-plan-probe`

## Decisions made by the human

- Rulings A (mask the role unique ID) and B (log-check job); then retry and HTTP-status rounds approved; then removal of log-check to follow-up #307 after the HTTP-status round failed.
- Each protected workflow diff approved before its `HUMAN_APPROVED=1` commit.
- Frontend install in the sandbox and the `UV_PYTHON` path outside the folder: allowed.
- Rulings A and B recorded in the decision record; the approved body is not edited.
- The plan role's missing read goes through PR #309 in `terraform/ci-access/`, applied by the human; `server/` re-applied to clear the #281 drift.
- Docs fix for `AWS_PLAN_ROLE_ID` on this branch (option 1).
- QA launch 1's PASS at f50d5d0 carries over to 978470e, since only docs changed after it.

## Mismatches with the spec or design docs

The approved #209 body says no masking step is used and names a five-workflow replay count; both are superseded (F-209-10, F-209-11). The decision record's addenda record the change.

## Commands to validate

**Verify:** `make verify BASE=518106504e2de0dc6db7ae3da2bfd88a023f9aaf` (PASS at 978470e). **Assert clean:** `make assert-clean` (PASS after every QA launch). **Terraform check:** CI only (no Terraform in the sandbox); passed at 978470e.

## Proposed AGENTS.md changes

none

## Temporary changes

- `frontend/node_modules` installed with `make frontend-install` for `make verify`: deleted at close-out.
- `UV_PYTHON=/root/.pyenv/versions/3.12.13/bin/python` passed as a make variable; it created a git-ignored `.venv`, kept.
- No processes started. `make clean-scratch` run at close-out.

## Interruptions

The human stopped the docs Engineer launch part-way; its four uncommitted edits were shown, checked against main and committed as ad977a1. The Claude session held #209 between 2988b71 and f50d5d0 and released it (issuecomment-6905214191).

## Unrelated problems noticed but not fixed

- F-209-1: A quoted and an unquoted on key read as two keys, so the trigger rule can miss one.
- F-209-2: The workflow test accepts a copy of the plan file.
- F-209-3: The workflow test accepts terraform_wrapper set to true.
- F-209-4: A quote-split terraform spelling is not recognised as the command.
- F-209-5: A failed show prints two fixed lines.
- F-209-6: Deeply nested plan JSON gives a traceback that reaches the log.
- F-209-7: The job summary is not readable over REST.
- F-209-8: A failure in the credentials action prints its own error text.
- F-209-9: Nothing checks the public plan log for a role ID until #307.
- F-209-10: The approved body still says no masking step is used.
- F-209-11: The replay criterion's fixed count of five went stale.
- F-209-12: The weakened-test check cannot see deletions in a file new since the base.
- F-209-13: add-mask masks only the first line of a value.
- F-209-14: The state bucket variable is expanded into script text.
- F-209-15: Checkout persists the read token while branch code runs.
- F-209-16: Decision record addendum 1 says one job no longer holds; addendum 2 restores it.
- F-209-17: The earlier dated summary lists a docs gap that is now fixed.
- F-209-18: The check script refuses a plan with no resources.
- F-209-19: #281 changed server Terraform with no re-apply step, so main drifted from the account.
- F-209-20: The plan step could print only a denied action's name.
- F-209-21: An Engineer launch used heredoc rewrite scripts against the command-shape rule.
- F-209-22: PR #263 was marked ready by someone outside the lane before QA passed.

## Follow-ups for the next session

- After PR #263 merges: Close comment and `make issue-close N=209`.
- Delete branches `claude/209-plan-probe` and `claude/209-plan-role-ssm-read` (the human's step).
- #307: the in-run log check for a role unique ID.
- Sweep is due (`make sweep-due`: 31 closed since 2026-11-14).
- Compose lane: mask `AWS_DEPLOY_ROLE_ID` in `_human-tasks/238-proposed/deploy-dev.yml` and #269, following this workflow's mask step.
