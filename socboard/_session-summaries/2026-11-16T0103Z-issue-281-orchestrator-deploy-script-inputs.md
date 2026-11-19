# Issue #281: Deploy script: ignore an inherited STACK_IMAGE and check the current-release link

**Date:** 2026-11-16T01:03Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Follow-up to #237 (D20), before the human's first deploy. In `terraform/server/socboard-deploy.sh`:
- **No test hooks:** the run folder, the release folder and the two waits are literal constants. `tests/test_deploy_script.py` runs a copy with exactly five lines replaced (those four and the fixed search path), and a test pins that set.
- **Unset names:** the ten names the script writes into its variable file are unset at start.
- **Current link:** a failed update of the `current` link takes the existing restore path (exit 7 or 9) instead of printing the success line.
- **Clean start:** the script begins with a POSIX sh line. It hands over once to `/bin/bash --norc --noprofile` under `env -i` with a fixed `PATH`, and a strict bash-only check follows. Shell options, start-up files and inherited variables never reach the real run.
- **Why POSIX sh:** Systems Manager starts the script with `sh`, dash on Ubuntu. That fact was found during this issue, and the human added it to the body's criteria.
- **Decision record:** the approved record is committed as `_docs/decisions/2026-11-15T2301Z-deploy-script-ambient-inputs.md`, with two Trade-offs sentences added on the human's approval: the outer `BASH_ENV` limit and the sh start-up block.
- **Not changed:** no protected file, `deploy_document.tf` or fixed text.

Branch `issue-281-deploy-script-inputs`, draft PR #283. Claim: https://github.com/andrew-chung-au/socboard/issues/281#issuecomment-6902753030. Final body hash `1053688706055be2b65a3ca3728aad7b2792c9dd0125f3973a8325e5d43dc2d0` (Confirm https://github.com/andrew-chung-au/socboard/issues/281#issuecomment-6903905826). CI on `6d38b84`, all success: `socboard verify` 43781073164 (the sh test ran under the Ubuntu runner's dash), `terraform check` 43781073219, postgres 43781073270, image 43781073127, compose 43781073133.

QA record (Heavy):
- QA 1 at `b811ce1`: FAIL, one Medium (`BASH_ENV` and `SHELLOPTS=xtrace` still changed the run; tracing printed every secret): https://github.com/andrew-chung-au/socboard/issues/281#issuecomment-6903074839.
- Fix round 1 (`41bbe67`, the human's option A; then `6d38b84` after the human added the sh criterion), re-check PASS: https://github.com/andrew-chung-au/socboard/issues/281#issuecomment-6904235782.
- Independent second QA at `6d38b84` (fresh subagent, issue body and diff only): PASS, Lows only: https://github.com/andrew-chung-au/socboard/issues/281#issuecomment-6904443525.

**What I learned:** `aws:runShellScript` runs the script with `sh`, so a `#!/bin/bash` line on a document's script means nothing; only reading how the agent runs the file showed it, and #237's tests could not.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

**What slowed you down (evidence):** two body edits mid-fix-round (the sh criterion, then the record sentence and Out of scope line), each needing the human's confirm.
**What nearly went wrong or was blocked:** the first clean-start block was bash-only and would have failed under Systems Manager's `sh`; caught by reading the fix before the re-check.
**One proposed change (file, expected effect, measure):** in Engineer launches for scripts a remote agent runs, name the interpreter that will run them and require a test under that interpreter (expected: no shell mismatch reaches QA; measure: fix rounds caused by the interpreter).

## Launch usage

PM: 4 launches (grooming, the sh criterion, the record sentence and Out of scope). Engineer: 3 launches (implementation, fix round 1, the POSIX block). QA: 3 launches (QA 1, re-check, independent second QA). Active time and tool uses: unknown.

## Files created or modified

- `terraform/server/socboard-deploy.sh`
- `tests/test_deploy_script.py`
- `_docs/decisions/2026-11-15T2301Z-deploy-script-ambient-inputs.md` (new), `_docs/index.md` (one row)
- `_docs/records/findings/281.json`
- `_session-summaries/2026-11-16T0103Z-issue-281-orchestrator-deploy-script-inputs.md` (this file)

## Decisions made by the human

- Approved filing and grooming #281; labelled it; approved its Decision record by name; decision questions 1 to 3 at option 1.
- Option A for QA 1's Medium (restart under an empty environment), with the outer `BASH_ENV` limit recorded.
- Option A for the sh finding: a POSIX start-up block, added to #281's criteria; confirmed the body, the record sentence and the narrowed Out of scope line.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI run 43781073164).
- **Deploy script tests:** `make test-one FILE=tests/test_deploy_script.py`.

## Proposed AGENTS.md changes

none

## Temporary changes

none (every rule removal by the Engineer and QA was restored with `git restore`)

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-281-1: A start-up file named in the starting shell's environment and the shell's trace option still reached the run, and tracing printed every secret; fixed by restarting under an empty environment in 41bbe67 and 6d38b84.
- F-281-2: An exported variable with the same name as the script's own secret array makes the run fail closed with exit 3, changing nothing.
- F-281-3: Systems Manager runs the script with sh, which is dash on Ubuntu, so the bash-only script would have stopped at its first bash-only line; fixed by a POSIX start-up block that hands over to bash in 6d38b84.
- F-281-4: A stray directory with the temporary link's name in the release root makes the link update land inside it, and the success line prints while the current-release name is a folder, not a link.
- F-281-5: When bash starts the script, exported functions named like commands the start-up block uses can skip the hand-over and keep a dirty variable; Systems Manager starts it with sh, which imports no functions, and the limit is recorded in the script header.
- F-281-6: The CI log does not name the shell the sh test ran under, so dash is inferred from the test count, and the unset line has only a static test because the hand-over already empties the environment.
- F-281-7: The restart under an empty environment also removes the home folder variable, and whether Docker and the secret client cope with that is shown only by the human's first deploy.

## Follow-ups for the next session

- Process slip: one test-file edit in `41bbe67` was made with a heredoc instead of the file tools; the content was checked by QA.
- Roadmap: #281's supporting-list line is not yet in `_docs/planning/roadmap-1-core.md` (a docs pull request, with the other tidy-ups).
- The human's first deploy (#237 stage (b)) checks F-281-7 and the dash start live.
