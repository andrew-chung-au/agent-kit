# Issue #240: Deploy and teardown runbook (D23), stage (a)

**Date:** 2026-11-16T04:24Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Stage (a) of D23. The runbook `_docs/runbooks/deploy-and-teardown.md` covers the dev stack after the first deploy. Its sections:
- **Deploys:** a routine deploy. The manual Systems Manager path is written out; the CI path stays `VERIFY:` until `deploy-dev.yml` merges.
- **Failures:** reading a failed run by exit code, and rolling back to the previous digest.
- **Rotation:** rotating the application secret and the Postgres role passwords. Each by-hand step reads the secret into a mode-0600 memory file.
- **Restore:** restoring from a volume snapshot through a scratch volume into `/srv/socboard-data/postgres`. The live folder is renamed aside, not overwritten.
- **Certificates:** a certificate failure on the shared DNS name is handled by diagnosing and waiting.
- **Teardown:** every leftover is its own `Decision:` step with no default delete: the state bucket, the secrets, the snapshots and the image package.

Every command has `Expected:` and `If different:`, and every fact cites its source. 43 facts that only the first dev deploy, #238 or the restore rehearsal can settle are marked `VERIFY:`.

Also added: the stage (b) task file `_human-tasks/2026-11-16T0351Z-human-task-240-engineer-restore-rehearsal-and-runs.md` (all rows `NOT CHECKED`), one `_docs/index.md` row, one `README.md` paragraph and one evidence-timeline line. No code, Terraform, workflow or protected file. Decision questions 1 to 5 stayed at their recommendations: dev now, prod later.

Branch `issue-240-deploy-runbook`, draft PR #326. Claim: https://github.com/andrew-chung-au/socboard/issues/240#issuecomment-6906698710. Engineer: https://github.com/andrew-chung-au/socboard/issues/240#issuecomment-6906914927. QA PASS at `c6462fb`, Lows only, 20 of 21 facts checked OK against their sources: https://github.com/andrew-chung-au/socboard/issues/240#issuecomment-6907266723. CI on `c6462fb`, all success: `socboard verify` 43801714156, postgres 43801714118, image 43801714093, compose 43801714188.

**What I learned:** a runbook copies counts and facts from other lanes' docs, and those go stale quietly (F-240-1); QA's fact table against the live sources is what catches it.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

**What slowed you down (evidence):** the `approved` label was removed and re-added once, so the claim waited a round.
**What nearly went wrong or was blocked:** nothing in this issue; the data-folder fact depended on #314, which merged first.
**One proposed change (file, expected effect, measure):** a runbook's counts that come from Terraform plans are read from the plan's own test files rather than README prose (expected: no stale count; measure: findings like F-240-1).

## Launch usage

PM: 1 launch (grooming). Engineer: 1 launch. QA: 1 launch (PASS). Active time and tool uses: unknown.

## Files created or modified

- `_docs/runbooks/deploy-and-teardown.md` (new)
- `_human-tasks/2026-11-16T0351Z-human-task-240-engineer-restore-rehearsal-and-runs.md` (new)
- `_docs/index.md` (one row), `README.md` (one paragraph), `_docs/records/2026-11-16T0000Z-measure-planning-deploy-evidence-timeline.md` (one line)
- `_docs/records/findings/240.json`
- `_session-summaries/2026-11-16T0424Z-issue-240-orchestrator-deploy-runbook.md` (this file)

## Decisions made by the human

- Labelled #240 `approved` (twice; the label was off in between).
- Decision questions 1 to 5 were not answered; their recommendations stand.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI run 43801714156).
- **Secret scan:** `bash _docs/agent-kit/scripts/scan-issue-body.sh` over the two new files.

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-240-1: The teardown's expected resource count for the server part is copied from a README line written before the deploy document existed, so it says 10 where the plan now shows 11.
- F-240-2: The teardown step that destroys the server part does not say in words that it deletes the data volume holding the live database and the public address.
- F-240-3: The secret rotation's undo refers to an old secret file that the steps have already rewritten and removed, and does not mention restoring the previous secret version from Secrets Manager.
- F-240-4: The restore has no explicit go or no-go step before it stops the app, the exit-10 row states the gateway as settled where the script marks it to be verified, and one check allows the empty lock file.
- F-240-5: The command forms in the runbook were checked from knowledge of the tools, not run or checked against their documentation; the human's runs are the live check.

## Follow-ups for the next session

- Stage (b): after the first dev deploy, the human runs the restore rehearsal and the other rows of the task file; one QA re-check of the filled table; then the Close comment.
- F-240-1 to F-240-3 are cheap wording fixes; the human decides whether they go in this pull request.
