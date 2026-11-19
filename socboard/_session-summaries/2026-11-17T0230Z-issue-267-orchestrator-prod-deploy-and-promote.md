# Issue #267: Prod stack, deploy side: an environment parameter in the deploy script (with #269's install and first promote)

**Date:** 2026-11-17T02:30Z (UTC)
**Spec version:** 9cf7ed3

Tier: Heavy (from the PM proposal; no tier label). Kiro Web session; commits on issue branches with pull requests (the environment forbids commits to `main`).

## What changed and why

- The maintainer approved #267's decision record on 2026-11-16 (comment 6933485386). One Engineer launch built it on `issue-267-deploy-environment` (6ec78bd, 7b8a544, e341c81): the document's `environment` parameter (dev or prod, default dev), the script's whole-value check after the lock, one fixed table of prod's values, the new exit-2 line, and 129 new tests. Two independent QA launches passed at e341c81 with Lows only. Their first launches stopped because the orchestrator's steering note leaked into their context; they were relaunched as fresh subagents (delivery-pace item 6). 5a5af95 fixed QA A's two task-file Lows. Merged as PR #356 (`91c84d2`).
- PR #357 installed `promote-prod.yml` (#269). The id-token rule in `tests/test_terraform_plan_workflow.py` became one entry per deploy workflow, with its trigger and its named Environment; this also closed #238's QA Low 1.
- The maintainer ran the first prod deploy by hand (prod is serving), then the first promote: run 44001761105, approved in `deploy-prod`, `socboard-deploy: deployed.`, health 200. That is the rubric's manual deploy to production.
- This branch: the #267 and #269 result tables, a rewrite of the #267 task file's steps (repository root, shortcuts, one fixed secret path, JSON parameters, the instance-policy check), the README scorecard (CI/CD 3 / 3, 20 of 24 from merged work), the evidence timeline, and this summary. `tests/test_deploy_script.py`'s check of the prod task file now requires recorded results instead of NOT CHECKED, and refuses angle-bracket placeholders in commands.

**What I learned:** a placeholder in angle brackets inside a command block is typed literally and read by the shell as a redirect. Commands a person copies should hold real values or shell variables set and echoed earlier.

## Reflection

### Engineer

**What slowed you down (evidence):** two existing tests pinned `DATA_DIR=` and `10.231.77.` and shaped the table's layout.
**What nearly went wrong or was blocked:** none recorded.
**One proposed change (file, expected effect, measure):** none recorded.

### QA

**What slowed you down (evidence):** no `terraform test` in the sandbox; the HCL assertions rest on reading plus CI run 43988848209.
**What nearly went wrong or was blocked:** the first two launches stopped on a leaked steering note.
**One proposed change (file, expected effect, measure):** add a database-step failure to the never-touch matrix (F-267-3).

## Launch usage

- Engineer: unknown (the tool did not report time or tool uses).
- QA A (first launch, stopped before reviewing): unknown.
- QA B (first launch, stopped before reviewing): unknown.
- QA A: unknown.
- QA B: unknown.

## Files created or modified

- `_human-tasks/2026-11-17T0030Z-human-task-267-engineer-first-prod-deploy.md` (results and the rewritten steps)
- `_human-tasks/2026-11-16T0332Z-human-task-269-engineer-promote-and-rollback.md` (rows 1 to 4)
- `README.md` (CI/CD row, total, the promote section, planned work)
- `_docs/records/2026-11-16T0000Z-measure-planning-deploy-evidence-timeline.md`
- `tests/test_deploy_script.py` (the prod task file's check)
- `_docs/records/findings/267.json`
- this file

## Decisions made by the human

- Approved #267's decision record ("approved"); decision questions taken at the PM's recommendations.
- Merged PRs #356 and #357; ran the first prod deploy and approved the first promote.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** not run in this sandbox. CI on PR #356 at e341c81 passed (terraform check 43988848209, verify 43988848067, postgres 43988848064, compose 43988848105, image 43988848068). Here: `tests/test_deploy_script.py`, `tests/test_promote_prod_workflow.py`, `tests/test_ci_promote.py` and `tests/test_ci_deploy.py`, 528 passed with `--noconftest`.
- **Assert clean:** not run.

## Proposed AGENTS.md changes

none

## Temporary changes

`pyyaml` in `.scratch/pylib` for the workflow tests; deleted.

## Interruptions

The maintainer helped another agent during the prod steps.

## Unrelated problems noticed but not fixed

- F-267-1: wrong step numbers in the task file (fixed in 5a5af95).
- F-267-2: the task file sent by tag (fixed in 5a5af95).
- F-267-3: no database-step failure in the never-touch matrix.
- F-267-4: no check that a fetched compose.yaml reads STACK_PROJECT.
- F-267-5: SECRET_REGION is unused.
- F-267-6: any deploy-role job can send environment=prod.
- F-267-7: no check of the instance role's policy before the first prod send.
- F-267-8: the task file's placeholders and run-folder sentence misled the person.

## Follow-ups for the next session

- After this branch merges: close #267 (the Close comment cites QA PASS e341c81 and merge 91c84d2).
- #267 rows 11 to 14 and #269 rows 5a to 6c (repeat, refusals, rollback, refused runs) are still NOT CHECKED. They add evidence but no rubric point.
- The other task files (#268, #269, #240) use the same `<placeholder>` style; rewrite them as this one was.
