# Issue #237: Deploy script and the first deploy to the public URL (D20), stage (a)

**Date:** 2026-11-15T21:28Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Stage (a), the repository work, of D20. `terraform/server/socboard-deploy.sh` is one root script and the whole content of the Systems Manager document `socboard-deploy` (`terraform/server/deploy_document.tf`, with a `terraform test` run). It takes one parameter, an image digest checked twice. It takes the lock, pulls the app image by digest and checks its labels, and fetches `compose.yaml` and `compose/db_init.py` at the image's revision. It pulls the pinned Postgres image with placeholder values (the secret is not read yet), then reads the one secret with the instance role into a memory-backed 0600 variable file. It runs `db-init`, `migrate` (as the owner role) and `seed` as Compose one-shots, then proves a candidate on `127.0.0.1:8001`. Only then does it swap the app, check health, the smoke check and host Caddy, and restore the previous release on failure. Fixed texts and exit codes; no secret in output, arguments or logs (canary tests; the 20 log lines after exits 6, 7 and 9 are redacted). The trusted proxy address and the restart policy come from an override file the script writes; a run-time gateway check (exit 10) guards the address. `tests/test_deploy_script.py` (112 tests) runs the script against stub programs. The first-deploy task file has every row `NOT CHECKED`; the decision record and its index row are added. No protected file and no Compose-lane file changed. The Compose project name and the app's ports are single settings, so a later prod stack can reuse the script.

Branch `issue-237-deploy-script`, draft PR #270. Claim: https://github.com/andrew-chung-au/socboard/issues/237#issuecomment-6898956834. The body went through confirmed edits: the Compose lane's review folded in, the start gate, the maintainer's facts of 2026-11-16, and option A for the database image. The final body hash is `a9508b1e0efdb2198190835dff70174eaa649407b325701e98eae5152cfb4bd3` (Confirm https://github.com/andrew-chung-au/socboard/issues/237#issuecomment-6900909439). CI on `ec00ee8`, all success: `socboard verify` 43762997505, `terraform check` 43762997529, postgres 43762997498, image 43762997523, compose 43762997492.

QA record (Heavy):
- QA 1 at `fd9cc36`: FAIL, two Mediums (the lock loser removed the holder's variable file; already deployed ignored a stopped app): https://github.com/andrew-chung-au/socboard/issues/237#issuecomment-6900048087.
- Fix round 1 (`292121f`), re-check PASS: https://github.com/andrew-chung-au/socboard/issues/237#issuecomment-6900313726.
- Independent second QA at `292121f` (fresh subagent, issue body and diff only): FAIL, one Medium (the Postgres image never pulled): https://github.com/andrew-chung-au/socboard/issues/237#issuecomment-6900590216.
- Fix round 2 (`b398821`, the human's option A after a body edit), re-check FAIL, one Medium (real Compose refuses the pull before the variable file exists): https://github.com/andrew-chung-au/socboard/issues/237#issuecomment-6901188582.
- Fix round 3 (`ec00ee8`, the human chose "try recommended" at the ship-or-fix question), re-check PASS, Lows only: https://github.com/andrew-chung-au/socboard/issues/237#issuecomment-6901641476.

**What I learned:** stub-based tests of a deploy script prove ordering and secrecy but not the real tool's rules; the two Mediums found after the first QA were both behaviours of real Docker Compose that a permissive stub hid.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

**What slowed you down (evidence):** a grooming collision (another session's body overwritten, F-237-13) and three fix rounds, two of them for real-Compose behaviour the stubs could not show.
**What nearly went wrong or was blocked:** launching the PM without re-reading the issue's comments overwrote another lane's grooming.
**One proposed change (file, expected effect, measure):** in the PM launch for any issue another session may touch, re-read the issue's comments and confirm the live hash immediately before the edit (expected: no overwrite; measure: grooming collisions).

## Launch usage

PM: 6 launches (grooming, the Compose-review edit after an interrupted run, start gate, header, maintainer's facts, option A). Engineer: 4 launches (stage (a), three fix rounds). QA: 5 launches (QA 1, three re-checks, independent second QA). Active time and tool uses: unknown.

## Files created or modified

- `terraform/server/socboard-deploy.sh`, `terraform/server/deploy_document.tf` (new), `terraform/server/tests/server.tftest.hcl`, `terraform/server/main.tf` (a comment), `terraform/README.md`
- `tests/test_deploy_script.py` (new)
- `_human-tasks/2026-11-15T1822Z-human-task-237-engineer-first-deploy.md` (new)
- `_docs/decisions/2026-11-15T1822Z-deploy-script.md` (new), `_docs/index.md` (one row)
- `_docs/records/findings/237.json`
- `_session-summaries/2026-11-15T2128Z-issue-237-orchestrator-deploy-script.md` (this file)

## Decisions made by the human

- #237 assigned to this lane, then briefly to another session, then back ("you own it now").
- Approved the Decision record by name and the recommended option of decision questions 1 to 7: #205 closed as not planned; the script as a Terraform document in `terraform/server/`; `python3-boto3`; files fetched from GitHub at the image's revision; candidate then a short-outage swap; no migration undone, a check filed before the first schema change after the first deploy; the override file.
- Confirmed four body edits; chose option A for the database image; chose "try recommended" (fix round 3) at the ship-or-fix question; chose no other Lows to fix.
- Dev and prod: this stack is dev; prod comes later by new issues.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI run 43762997505).
- **Deploy script tests:** `make test-one FILE=tests/test_deploy_script.py`.
- **Terraform:** CI's `terraform check` (run 43762997529); `make tf-check` where Terraform is installed.

## Proposed AGENTS.md changes

none

## Temporary changes

none (every rule removal by the Engineer and QA was restored with `git restore`)

## Interruptions

- A stray "stop" interrupted one PM launch before it applied anything.

## Unrelated problems noticed but not fixed

- F-237-1: A second deploy run that lost the lock removed the running deploy's variable file because the exit trap was set before the lock; fixed in 292121f.
- F-237-2: The already-deployed check did not require the app container to be running, so a stopped app could be reported as deployed; fixed in 292121f.
- F-237-3: Redaction of the log lines printed after a failure leaves a tail when two secret values overlap without one containing the other, and misses a value split across two lines.
- F-237-4: Sending the same digest again cannot repair an unhealthy release, because the swap changes nothing when the configuration is unchanged, so the run ends in exit 9.
- F-237-5: The database image pinned in the Compose file was never brought to the server, so the first deploy could not start the database; fixed in b398821 and ec00ee8.
- F-237-6: An image variable exported in the root shell's environment would override the digest the script writes, and the test-only path and timing hooks are also read from that environment.
- F-237-7: A failed creation of the run folder prints the lock-held text, and a run ended by a signal prints no line from the failure table.
- F-237-8: Release folders are never pruned, and a failed swap of the current-release link is not checked, so the success line could print after it.
- F-237-9: Whether Systems Manager runs the script with bash, and whether an older bash would put the secret through a temporary file, are settled only on the server.
- F-237-10: The database image pull ran before the variable file existed and with the required Compose variables unset, which real Compose refuses; fixed in ec00ee8 with an empty env file and placeholders for that call only.
- F-237-11: The script is tested only against stub programs, so real Docker Compose behaviour, including the placeholder pull, is proven only by the human's first deploy.
- F-237-12: The static scan for the variables the Compose file requires uses patterns that would miss a variable reached through a YAML anchor or an extends entry.
- F-237-13: Two sessions groomed the issue minutes apart and the second overwrote the first body, because the second orchestrator did not re-read the issue's comments before launching its PM.

## Follow-ups for the next session

- Stage (b): the human's first deploy, after #236 stage (b) and #261's gateway pin (PR #264) merge; then one QA re-check of the filled result table, including the comparison with #236's peer-address row; then the Close comment.
- The migration-compatibility check (decision question 6) is filed before the first schema change after the first deploy and placed in the roadmap's supporting list.
- Lows F-237-6 and F-237-8 (the `STACK_IMAGE` unset and the unchecked current-link swap) were recommended as one-line fixes; the human did not choose them for this pull request.
