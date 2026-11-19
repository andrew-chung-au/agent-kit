# Issue #209: CI read-only Terraform plan (D18b), log-check removal and handover (Heavy tier, not finished)

**Date:** 2026-11-16T01:54Z (UTC)
**Spec version:** 3e02fc4

## What changed and why

Heavy tier. The issue is NOT done: this session ends with a handover to the Terraform B lane (Release comment on #209).

- The in-run `log-check` job (ruling B) could not download the plan job's log in three runs at PR #263 (43777278028, 43780300200, 43784106149). By the human's Decision 1 it was removed from `.github/workflows/terraform-plan.yml` and moved to follow-up issue #307 (filed by the PM, not groomed, no label). Commit 2bd3a05, pushed to `claude/209-terraform-plan`.
- The mask step (ruling A) and its tests stay; masking is proven by 0 `AROA` matches in the plan job's log of all three runs (counted, never printed).
- The tests for the removed job were deleted, the jobs rule is now "plan only", and a re-added second job is refused. Addendum 2 of the decision record records the ruling.
- The plan step still fails: the human found that the plan role lacks `ssm:DescribeDocumentPermission` (needed since main added `terraform/server/deploy_document.tf`). Terraform B fixes it in `terraform/ci-access/plan.tf`.

**What I learned:** a job cannot reliably download another job's log from inside the same run; a check of a finished run's log belongs outside that run.

## Reflection

Copied from the roles' returns to the orchestrator (no issue comment was asked for, as QA has not passed).

### PM

- **What went wrong or was slow:** `gh issue list` does not work in a cloud session (GraphQL is blocked), which cost one failed command. The kit has no make target for listing open issues, so the duplicate check used a raw `gh api` call with the repository name read from `agent-kit.conf`.
- **What I would change:** add a read-only `make issue-list` target (REST, number and title, pull requests excluded) and name it in AGENTS.md Commands, so duplicate checks go through `make`.
- **Unrelated problem noticed, not fixed:** the last line of AGENTS.md Non-negotiables is still the template placeholder.
- **Open risk:** the #209 body's Out of scope does not link #307 (the human chose to leave the body).

### Engineer

- What went well: the change stayed in the three named files, all through the Edit tool.
- What went wrong: one of my Edit calls dropped a trailing space, so the last deletion did not match the first time. I re-read the file and redid it, and no stray text is left.
- Environment findings for the human: the brief's interpreter path and the "node_modules already installed" claim were both false here (this looks like a fresh container). The next launch should check them or drop them.
- Not checked: the workflow has not run on GitHub after this change. Nothing now checks the public log after a run until #307.

### QA

unknown (role not asked; no QA launch in this session)

## Launch usage

- PM (file follow-up #307): 247 s, 13 tool uses.
- Engineer (log-check removal, uncommitted): 1067 s, 37 tool uses.

## Files created or modified

- `.github/workflows/terraform-plan.yml` (protected; the human approved the exact diff)
- `tests/test_terraform_plan_workflow.py`
- `_docs/decisions/2026-11-15T1722Z-terraform-plan-ci.md` (Addendum 2)
- this summary

## Decisions made by the human

- Approved the exact diff removing the `log-check` job; commit and push now.
- #209's body stays unchanged (no link to #307 in the body); Addendum 2 and the workflow header carry the link.
- Both QA launches must review the test deletions by hand against the removed job and say so in their verdicts, because the weakened-test check sees the test file as new and cannot see them.
- The Engineer's `make frontend-install` without asking is accepted this once.
- Stop here; Terraform B takes #209.

## Mismatches with the spec or design docs

- The frozen #209 body still says no masking step is used and describes one job with no follow-up; the decision record's two addenda are the current record.

## Commands to validate

- **Verify:** `make verify BASE=f697e8d942a655bed66134d635baafd4bd408337` passed at 2bd3a05 (2768 Python tests, 237 frontend tests, ESLint 0 errors and 1 warning in `frontend/src/components/ui/button.tsx`, whitespace PASS, weakened tests "27 added, 0 removed"). It needs `make frontend-install` first in a fresh container.
- **Test (one file):** `make test-one FILE=tests/test_terraform_plan_workflow.py` (79 passed).

## Proposed AGENTS.md changes

- From the PM: a read-only `make issue-list` target and its Commands line. Not applied.

## Temporary changes

- `frontend/node_modules`: installed by the Engineer with `make frontend-install` without asking first (the human accepted it afterwards); deleted in this session.
- `.venv/`: created by uv with the system Python 3.12.3 (the handover's `UV_PYTHON` path does not exist in this container); git-ignored, not deleted.
- One verify run was started in the background by the Engineer by mistake and stopped by the Engineer.
- `make clean-scratch` did NOT run: `.scratch/` still holds the PM's issue draft and the commit message. The container is discarded with the session.

## Interruptions

none

## Unrelated problems noticed but not fixed

`_docs/records/findings/209.json` is NOT written yet: it is written once, at close-out, by the lane that finishes #209. Findings to carry into it (not numbered yet):

- QA launch 1, outside the criteria: a duplicate quoted "on" key next to an unquoted one; the test accepts a copy of the plan file, `terraform_wrapper: true` and a quote-split terraform word; a failed show prints two fixed lines; JSON nested about 100k deep gives a traceback; the job summary cannot be read over REST.
- Process: an earlier Engineer launch edited the workflow and test files with scripts instead of the edit tool.
- Process: this session's Engineer ran `make frontend-install` without asking; the orchestrator restored one space the Engineer's edit dropped (`CHDIR = ` in the test file).
- Process: the weakened-test check cannot see tests deleted from a file that is new since BASE.
- Docs: `terraform/README.md` and the #156/#207 task files name only AWS_PLAN_ROLE_ARN, not AWS_PLAN_ROLE_ID.
- Docs: the frozen #209 body does not mention the mask step or #307.
- Kit: `gh issue list` fails in a cloud session and there is no `make issue-list`; AGENTS.md Non-negotiables ends with a template placeholder line.
- The in-run log check could not download the log (now #307).

## Follow-ups for the next session

Terraform B lane, in order:

1. Add the missing read (`ssm:DescribeDocumentPermission`) to the plan role in `terraform/ci-access/plan.tf`; the human applies it.
2. Re-run the plan on PR #263 and get a green run. Check the log by count only.
3. Ruling C, only after the plan passes: a throwaway DRAFT pull request from a branch cut from `claude/209-terraform-plan` that changes only `data_volume_gib` default 10 to 11 in `terraform/server/variables.tf`; expect one resource to change; close it unmerged and leave the branch for the human.
4. Hash check (`make issue-hash N=209`, expected e2561dce7c004f0d07e609b480ee6ce30fe602d3903a5dae723e3f4b78b8e58a), then QA launch 1 again in full, then Assert clean. QA launch 1 failed at f82999e on the unseen "one resource to change" run (the probe) and on the terraform word lookbehind (fixed in 93f5bf1).
5. A fresh QA launch 2, Code review checklist only, then Assert clean. Both launches review the test deletions of 2bd3a05 by hand and say so.
6. Reflection blocks, the findings file, a session summary, `make clean-scratch`, then one decision-point message. After the merge: the Close comment and `make issue-close N=209`.

Open with the human: PR #263 is still marked ready, not draft; it must not merge before both QA launches pass. A follow-up idea, not started: let the plan step print only a denied action's name.
