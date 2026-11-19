# Issue #269: Promote to prod: a manual workflow that deploys dev's digest to prod, with rollback

**Date:** 2026-11-16T0544Z (UTC)
**Spec version:** e3461a7

## What changed and why

Terraform lane B groomed #269 from its outline at the human's request, and built it once the human's no-false-waits ruling (`.kiro/steering/real-dependencies-only.md`) applied: nothing is applied by merging, and the code needs only #238's record format, already on `main`. New `scripts/ci_promote.py`:
- **`resolve`:** runs with no cloud role. It picks dev's newest `deploy-record-dev`, or the digest the input names if a dev record from this repository's `main` holds it, and refuses everything else before an approval is asked.
- **`deploy`:** runs in `deploy-prod` after the approval. It sends `socboard-deploy` with `environment=prod`, checks the public health URL, writes a summary naming the approver and uploads `deploy-record-prod`.

`scripts/ci_deploy.py`'s `send` takes an `environment` argument, defaulting to `dev`, so the dev call is unchanged. The workflow is the protected proposal `_human-tasks/269-proposed/promote-prod.yml`. Also added: two test files, the human task file, the decision record `_docs/decisions/2026-11-16T0332Z-promote-to-prod.md` (proposed), one README paragraph and one index row. Merged as PR #320, merge commit `895af49e62d34c8affd8ae70bf2c1143de154e9c`.

**What I learned:** the independent QA's one Medium was in the person's steps, not the code: the refused-run steps did not say "reject the approval if one is asked", which is the step that matters if a refusal fails.

## Reflection

The Engineer and the PM were this session (Terraform lane B). The QA blocks are copied from the reports the launches returned; as on #268, they were not posted as separate comments, so that a comment starting `QA:` is never read as a verdict.

### Engineer

**What slowed you down (evidence):** the project's Python packages are not installed in the sandbox, so every test ran only in CI; one broken-copy test failed in CI because a lambda returned a value that `broken()` took as text (run 43798891177).
**What nearly went wrong or was blocked:** the start condition "once D20 has run": D20 still has not run; the merged steering ruling made it a false wait, and the Claim comment says why.
**One proposed change (file, expected effect, measure):** `_docs/agent-kit/templates/human-task.md`: require an "If different" under every Refusal test block that says what to do if the refusal does not happen; expected to remove findings like this issue's M1; measure: Medium findings on human-task files per issue.

### QA (first launch)

**What slowed you down (evidence):** no test shows an Actions run to prod, so the VERIFY items rest on the human's first run.
**What nearly went wrong or was blocked:** none; the security order holds (every refusal is in a job with no role and no Environment).
**One proposed change (file, expected effect, measure):** none beyond the open VERIFY items.

### QA (independent second launch)

**What slowed you down (evidence):** none recorded.
**What nearly went wrong or was blocked:** the human task's refused-run steps lacked "If different", which is where a failed refusal needs instructions.
**One proposed change (file, expected effect, measure):** check provenance of an artifact with a `head_branch` check; done in fix round 1.

### QA (re-check, fix round 1)

**What slowed you down (evidence):** none.
**What nearly went wrong or was blocked:** reproducing `git status --short` in a scratch repository found a wrong Expected line that reading the diff did not.
**One proposed change (file, expected effect, measure):** run each new Expected line of a fix round once.

### QA (re-check, fix round 2)

**What slowed you down (evidence):** none.
**What nearly went wrong or was blocked:** Python's `True == 1` leaves a small gap on the head-repository side of the filter (F-269-2).
**One proposed change (file, expected effect, measure):** none.

## Launch usage

- QA, first launch: unknown, unknown (the completion notice gave no figures).
- QA, independent second launch: unknown, unknown.
- QA, re-check of fix round 1: unknown, unknown.
- QA, re-check of fix round 2: unknown, unknown.

## Files created or modified

- `scripts/ci_promote.py` (new), `scripts/ci_deploy.py` (`send` gains a defaulted `environment`)
- `tests/test_ci_promote.py`, `tests/test_promote_prod_workflow.py` (new)
- `_human-tasks/269-proposed/promote-prod.yml` (new; protected workflow proposal)
- `_human-tasks/2026-11-16T0332Z-human-task-269-engineer-promote-and-rollback.md` (new; result table not yet filled)
- `_docs/decisions/2026-11-16T0332Z-promote-to-prod.md` (new, proposed), `_docs/index.md` (one row), `README.md` (`### Promote to prod`)
- `_docs/records/findings/269.json`, this summary, and (close-out branch) one sentence in the "Prod access" section of `terraform/README.md`

## Decisions made by the human

- Assigned #269 to this lane ("take and groom #269, then build it once D20 has run") and labelled it `approved` at body hash `0877a2615a879096fc9198b8d474ed26d81510b860844494a1d5b3ec3f491fb5`.
- Merged PR #320 after the "ship or fix?" question at the second fix round; the merge is taken as "ship".
- Not answered: the decision questions 1 (the post-deploy check) and 2 (naming the approver); the build uses option A for both, as the Claim comment and the decision record say. The decision record is still `proposed`; the human has not approved it by name.
- Said "ok complete documentation" after the close-out questions. Done on that word: the body's two wording slips (F-269-6) corrected by a PM edit (new hash `a8e4762e654ac600c50bac9b1ad135c2b2f9c74be7857a8ccee4629a790f0c54`, waiting for the human's confirm), and the `terraform/README.md` "Prod access" masking line now names the promote workflow's mask step. Not done on that word: the decision record's `approved` status and decision questions 1 and 2, which need the human's explicit approval by name (`deploy-coordination.md`, message hygiene).

## Mismatches with the spec or design docs

The body's "three jobs" and `already` (F-269-6), corrected after the merge. No mismatch with the spec.

## Commands to validate

**Verify:** `make verify` (CI: `socboard verify` run 43801682637 on `2bca2e1`, 3188 Python and 237 frontend tests passed). Not run in the sandbox: the Python packages are not installed.

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-269-1: No test feeds the artifact list an entry with a missing or boolean repository id, so the type guards in the main-and-this-repository filter are unexercised.
- F-269-2: The head-repository side of the filter compares by equality, so a boolean true would equal a repository id of 1; GitHub's data cannot produce this.
- F-269-3: A rollback can name only a digest held by one of dev's newest 30 non-expired records; an older one is refused with the never-ran-in-dev message, which misleads but fails safe.
- F-269-4: The previous prod digest is read in the resolve job, before the approval wait, so the summary's line can be stale if another promote finishes during the wait.
- F-269-5: The artifact zip is read fully into memory before its single small file is checked, so a very large artifact slows or fails the resolve job.
- F-269-6: The approved body says three jobs but lists two, and says a dev record's result is already where dev's real record says already deployed; the build follows the two jobs and dev's real value.
- F-269-7: An actor login with a bot suffix is refused, after the role is assumed but before the document is sent, so a bot-started promote fails without deploying.
- F-269-8: No test passes a digest input that starts with a dash; argparse refuses it with exit 2 before any call, which is safe but is not the script's own tested refusal.

## Follow-ups for the next session

- The human installs the workflow and runs the task file's steps once #237's first deploy has run, #238's workflow is live with a `deploy-record-dev`, and #267 is closed; fill the result table from what is pasted back and clear the `VERIFY:` items the runs settle.
- The human approves or changes the decision record, and answers decision questions 1 and 2 if option A is not wanted.
- #268's steps 2, 3 and 6 are still open for the human; fill that table too.
