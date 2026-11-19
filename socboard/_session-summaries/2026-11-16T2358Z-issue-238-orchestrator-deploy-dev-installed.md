# Issue #238: Deploy to dev from CI on a green push to main (D22a): installed and first run

**Date:** 2026-11-16T23:58Z (UTC)
**Spec version:** 9cf7ed3

Tier: Standard (no tier label). Session run in Kiro Web, which forbids commits to `main`, so work went on issue branches with pull requests.

## What changed and why

Same session, in order:
- #321 filed and fixed (PR #322, merged). The deploy script's `umask 077` left the fetched `compose/db_init.py` root 0600. `db-init` runs as uid 10001 and could not read the bind mount, so D20's first run exited 5.
- #324 filed and built (PR #327, merged). Exit 5 now prints the failing step's name and its last 20 redacted lines. The orchestrator then filed #328 as a duplicate with stricter criteria; it is open and unlabelled.
- #238 installed (PR #343, merged), after the maintainer asked for DevOps rubric points first. The proposed `deploy-dev.yml` and the publish job's hand-over moved into `.github/workflows/`, with the step that masks `AWS_DEPLOY_ROLE_ID` (#268's hand-over). CI then failed on `tests/test_terraform_plan_workflow.py`, which allowed `id-token: write` only in a `pull_request`-only workflow. The rule now has one named exception: `deploy-dev.yml` triggered only by `workflow_run`, with the grant only in jobs that name an Environment. Fixtures refuse each way out of that shape. This is a deliberate loosening of a #209 security test, flagged to the maintainer for review.
- This branch: the result table of the #238 task file, filled from run 43979237337's logs, job summary and artifacts. README's CI/CD row now reads 2 / 3 with the run linked, and the Deploy to dev status is updated. #349 and #350 are filed and placed in the supporting list.

The first deploy from CI needed four attempts. Attempts 1 and 2: the maintainer had saved `DEPLOY_INSTANCE_ID` and `DEPLOY_URL` as Environment secrets, not variables. Attempt 3: deployed, then the health check used a mistyped `.sslip.ioa`. Attempt 4: "already deployed", health 200, record uploaded.

**What I learned:** a task file that says "Environment variables" still led to secrets, because the GitHub page shows the secrets list first. Steps should name the section and say "not secrets".

## Reflection

unknown (role not asked)

## Launch usage

none

## Files created or modified

- `_human-tasks/2026-11-15T2100Z-human-task-238-engineer-deploy-dev-workflow.md` (result table)
- `README.md` (CI/CD row, Deploy to dev status, the in-progress line)
- `_docs/planning/roadmap-1-core.md` (#349 and #350 in the supporting list)
- this file

## Decisions made by the human

- Work the DevOps rubric points first; install the dev deploy workflow now.
- Approved and merged PRs #322, #327 and #343.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** not run in this sandbox (no project environment). CI on PR #343 passed at e4e9559: verify, postgres, compose and image, push and pull_request. This branch is docs only; CI runs on its pull request.
- **Assert clean:** not run.

## Proposed AGENTS.md changes

none

## Temporary changes

`pyyaml` installed into `.scratch/pylib` to run the workflow tests; deleted.

## Interruptions

none

## Unrelated problems noticed but not fixed

- #349: `find` refuses when a second merge lands before the first commit's publish run (red runs 43978322955 and 43979101310).
- #350: the variable check accepted `https://44-216-250-242.sslip.ioa`.
- `promote-prod.yml` grants `id-token: write` on `workflow_dispatch`, so installing it will need the same kind of named exception in `tests/test_terraform_plan_workflow.py`.

## Follow-ups for the next session

- The orchestrator closes #238 after this branch merges (all rows settled except two marked NOT SETTLED with reasons).
- #328: label it or close it as a duplicate of #324; its docs criteria are not done.
- #267, the last CI/CD point: its Engineer start waits for the maintainer to approve its decision record by name. Then install `promote-prod.yml` (#269).
