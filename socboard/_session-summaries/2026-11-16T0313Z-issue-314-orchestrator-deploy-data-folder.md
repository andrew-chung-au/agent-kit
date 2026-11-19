# Issue #314: Deploy script: point the database at /srv/socboard-data/postgres, not the volume root

**Date:** 2026-11-16T03:13Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

The deploy script's data folder constant (`terraform/server/socboard-deploy.sh` line 62) is now `/srv/socboard-data/postgres`, the folder the bootstrap creates for Postgres (uid 999, mode 0700), instead of the data volume's mount root, which also holds Caddy's certificates and account. As merged in #237, the Postgres container would have mounted the whole volume and written its data beside `caddy/`; moving it after the first deploy would have started an empty database. Three exact test assertions now pin the new value, and a new test reads the mount root from `main.tf` and the folder from the bootstrap so the two cannot drift apart again. Found as F1 while grooming #267. No data migration: nothing has been deployed. No protected file and no Terraform- or Compose-lane file. #237's approved body still states the old value; by the decision question's recommendation the change is recorded here only.

Branch `issue-314-deploy-data-folder`, draft PR #316. Claim: https://github.com/andrew-chung-au/socboard/issues/314#issuecomment-6905887047. Engineer: https://github.com/andrew-chung-au/socboard/issues/314#issuecomment-6906006358. QA PASS at `3840c46`, Lows only: https://github.com/andrew-chung-au/socboard/issues/314#issuecomment-6906244781. CI on `3840c46`, all success: `socboard verify` 43795218426, `terraform check` 43795218405, postgres 43795218484, image 43795218482, compose 43795218475.

**What I learned:** a fixed value copied from another lane's file goes stale when that file changes; a test that reads both files is cheaper than a later fix after data exists.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

**What slowed you down (evidence):** the label landed on #267 and #240 first, so #314 waited for a second labelling.
**What nearly went wrong or was blocked:** the first dev deploy could have run with the database on the volume root; the grooming of #267 caught it.
**One proposed change (file, expected effect, measure):** when a lane changes a value another lane's script copies (here the bootstrap's folder layout), its PM greps the repository for the old value and lists every hit in the grooming comment (expected: no stale copy reaches a deploy; measure: fixes like this one).

## Launch usage

PM: 1 launch (file and groom). Engineer: 1 launch. QA: 1 launch (PASS). Active time and tool uses: unknown.

## Files created or modified

- `terraform/server/socboard-deploy.sh` (one constant)
- `tests/test_deploy_script.py`
- `_docs/records/findings/314.json`
- `_session-summaries/2026-11-16T0313Z-issue-314-orchestrator-deploy-data-folder.md` (this file)

## Decisions made by the human

- Approved filing #314; labelled it `approved`.
- The decision question (edit #237's approved lines or record the change here) was not answered; its recommendation, record here only, stands.

## Mismatches with the spec or design docs

- #237's approved body states `STACK_PGDATA_DIR=/srv/socboard-data` (F-314-1).

## Commands to validate

- **Verify:** `make verify` (CI run 43795218426).
- **Deploy script tests:** `make test-one FILE=tests/test_deploy_script.py`.

## Proposed AGENTS.md changes

none

## Temporary changes

none (QA's mutations were restored with `git restore`)

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-314-1: Issue 237's approved body still states the volume root as the dev data folder in two places; by the human's default ruling the change is recorded in issue 314 only.
- F-314-2: An earlier dated session summary still names the volume root as the dev data folder; session summaries are records and are not edited.
- F-314-3: The deploy script kept a fixed value that a later bootstrap change made stale, and nothing tied the two together until this issue's test read both files.

## Follow-ups for the next session

- The human's first dev deploy (#237 stage (b)) after this merges.
- #240 (approved) next; #267 (approved, Heavy) after the first dev deploy and its Decision record's approval.
