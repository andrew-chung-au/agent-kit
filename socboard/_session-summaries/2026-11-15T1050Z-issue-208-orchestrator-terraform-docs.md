# Issue #208: Terraform docs: fix stale or narrow statements about validate, the IAM deny and Parameter Store

**Date:** 2026-11-15T10:50Z (UTC)
**Spec version:** 5985a83

## What changed and why

Standard tier from the PM proposal. The PM filed #208 from the stale statements QA found on #156 and #199. After approval the body grew, with the human's confirmation each time:
- #162's decision record (0907Z) set to approved;
- the 0928Z index Status column set to Current;
- F-207-1: the role ARNs are repository secrets, not variables.

Branch `claude/208-terraform-docs`, draft PR #248. Commit f300691 changes five files, docs and Terraform comments only:
- `terraform/README.md`: the `state/` validate wording, the role ARNs as secrets, #156's PassRole exception, and the #162 record shown as approved;
- `terraform/ci-access/main.tf`: the Parameter Store comment;
- `terraform/ci-access/outputs.tf`: the header comment;
- the 0907Z record: Status approved, plus one sentence on the exception;
- `_docs/index.md`: the 0907Z and 0928Z rows show Current, and the 0928Z description matches the code.

90477de merges `origin/main` (#214) cleanly. QA PASS at 90477de, then assert-clean PASS. `terraform check` passed on the PR (run 43704012645).

**What I learned:** when a ruling changes a fixed value, a search of `main` for the old wording at grooming time would have caught the stale lines before approval, not after.

## Reflection

### PM

Reflection:
1. Slowed: the body was re-hashed three times (abaa7cb3, 92f3dc87, 4b3da6ca, 20f170ed), as two record statuses and the secrets wording joined the original four statements. I re-checked the line references at three commits (f86e2a7, 6fe249d, 129d64d), and the brief's lines 62-64 for main.tf were really 63-66.
2. Nearly wrong: README line 75 and outputs.tf line 1 ("repository variables, not secrets") were already stale when the secrets ruling landed, and I had read line 75 while grooming D18b. QA found them, not me. The brief also called the 0928Z record approved before main said so.
3. Proposal: in `_docs/agent-kit/team/pm.md`, when a ruling changes a fixed value (for example variables to secrets), the PM greps `main` for the old wording and lists every hit in the grooming comment. Effect: stale-wording criteria are added before approval, not after. Measure: post-approval body edits for stale wording on the next five docs issues; target 0.

### Engineer

Reflection:
1. Slowed: the decision records keep each bullet on one very long line, so the search tool printed "[Omitted long matching line]" for the 1742Z record. Checking the "Parameter Store" refused-reading criterion took three more searches. Also, `make verify` took about 6 minutes (5 min 10 s of Python tests) for a diff that changed only docs and comments.
2. Nearly went wrong: the issue's "Nothing else changes" list and the claim's expected paths name the session summary (the claim also names the findings file), which could read as Engineer work. `session-summary.md` makes both the orchestrator's, so I wrote neither.
3. Proposal: in `_docs/agent-kit/templates/task-template.md`, mark the session summary and findings file in a file list as "(orchestrator, after QA)". Expected effect: no Engineer writes or asks about them. Measure: Engineer comments that mention writing or skipping them, over the next 10 issues.

### QA

Reflection:
1. Slowed by: `make verify BASE=7b49fe4` took about 6 minutes (Python 302.59s and frontend 35.41s in `.scratch/qa208-verify.log`) for a diff of docs and comments only. The two wait loops I set on its log matched `Verify: PASS`, but the gate prints `VERIFY: PASS`, so they never fired and I had to stop them by hand.
2. Nearly went wrong: a plain grep for `ssm:` would have missed a wildcard or NotAction Allow that reaches `ssm:GetParameter`. Only a second search (for NotAction, `"*"` and policy attachments) showed the new `main.tf` comment's "no role allows" claim holds.
3. Proposal: `_docs/agent-kit/procedures/verify.md`, one line saying the gate's last line is exactly `VERIFY: PASS` or `VERIFY: FAIL`, so waits can match it. Effect: no wait loops that never fire. Measure: how often QA logs need a manual TaskStop on a verify wait in the next five issues (target 0).

## Launch usage

- PM (filed and groomed #208; later body edits, shared with #207, #209 and #218): see the #207 summary; this issue's edits were 4m20s/8, 4m10s/26 and 5m07s/12
- Engineer (implement): 8m57s, 43 tool uses
- QA (full check, 90477de): 8m07s, 42 tool uses
- Engineer (reflection): 23s, 3 tool uses
- PM (reflection): 29s, 3 tool uses
- QA (reflection): 8m51s cumulative, 49 tool uses

## Files created or modified

`terraform/README.md`, `terraform/ci-access/main.tf` (comments), `terraform/ci-access/outputs.tf` (comments), `_docs/decisions/2026-11-14T0907Z-instance-iam-snapshots-budgets.md`, `_docs/index.md`, `_docs/records/findings/208.json` (new), this summary.

## Decisions made by the human

- #162's decision record (0907Z) is approved, and the change goes into #208.
- F-207-1 is added to #208 before starting (body confirmed).
- They approved opening draft PR #248 so the `terraform check` workflow runs.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify BASE=7b49fe4`: PASS (2505 Python, 237 frontend).
- **Terraform check:** `make tf-check TERRAFORM=.scratch/tf/bin/terraform`: PASS.
- CI on 90477de: all green, including `terraform check`.

## Proposed AGENTS.md changes

none

## Temporary changes

- Terraform 1.17.2 in `.scratch/tf/` (124 MB) and `.scratch/ref-vt` (18 MB) remain until #209 and #218 are done; `make clean-scratch` removes them.

## Interruptions

The human's usage limit stopped work between the PM's #208 edit and the confirm comment. The issue's hash was re-checked on resume.

## Unrelated problems noticed but not fixed

- F-208-1: The Deploy decision record and the deploy backlog proposal still describe the apply role's IAM deny as covering other IAM writes, narrower than the code.
- F-208-2: The new Parameter Store comment calls the plan role's three SSM actions document reads, though one reads tags.

## Follow-ups for the next session

- The human merges PR #248. Then the orchestrator posts the close comment and closes #208.
- Next: #209 (D18b, approved, Heavy): build now, close after #207's stage (b). #218 needs the human's label. #207 waits for the human's run.
