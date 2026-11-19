# Issue #154: Terraform: the state bucket

**Date:** 2026-11-14T10:05Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

`terraform/state/` defines one private S3 bucket for Terraform state in `us-east-1`: public access blocked, versioned, encrypted, a bucket policy that refuses non-TLS access, a lifecycle rule that expires noncurrent versions after 90 days, `force_destroy = false`, tagged `project=socboard`. The bucket name is a variable the human sets; the backend ships as `backend.tf.example` (native S3 lock file) because a live backend would point the first apply at a bucket that does not exist yet. `terraform/.terraform-version` holds Terraform 1.17.2, `terraform/README.md` has the human's numbered steps and teardown, and `.gitignore` ignores state, plans, `.terraform/`, crash logs and real variable files.

Worked by Session A (Kiro Web, infrastructure lane) in a git worktree. Standard tier. Branch `issue-154-tf-state-bucket`, PR #171, merge commit `b095061`. QA passed at `f7cfdf0` (https://github.com/andrew-chung-au/socboard/issues/154#issuecomment-6873965785); the Reviewer ran once and found five items; the human marked four must-fix; the fix round ended at `dd52e25` and its QA re-check passed (https://github.com/andrew-chung-au/socboard/issues/154#issuecomment-6874892252).

**What I learned:** the Reviewer's best finding (teardown emptied the bucket before `destroy` could read its state) was a README ordering error that QA had passed, because QA read each step and not the sequence as a whole.

## Reflection

### Engineer

Build (https://github.com/andrew-chung-au/socboard/issues/154#issuecomment-6873926428) and fix round (https://github.com/andrew-chung-au/socboard/issues/154#issuecomment-6874760246): the Engineer comments carry their own Reflection blocks; the fix-round one reports that the kit secret scan refuses a whole `.gitignore` because of two lines that already existed (they name an env file), so it scanned only the added lines, and proposes that the scan script document a diff-only mode.

### QA

unknown (role not asked)

### Orchestrator

The first QA re-check launch stopped at once because the worktree no longer existed in the sandbox (the sandbox had been reset). I recreated it and relaunched. Worktrees under `.scratch/wt/` do not survive between sessions.

## Launch usage

Engineer: 2 launches (build; fix round). QA: 2 launches (PASS at `f7cfdf0`; PASS at `dd52e25`, after one launch that stopped on the missing worktree). Reviewer: 1 launch (`f7cfdf0`). Active time and tool uses were not given in the notifications: unknown.

## Files created or modified

- `terraform/.terraform-version`, `terraform/README.md`, `terraform/state/{main.tf,variables.tf,backend.tf.example,terraform.tfvars.example}` (new)
- `.gitignore` (Terraform block)
- `AGENTS.md` (Layout line gains `terraform/`, committed alone with the human's approval)
- `_session-summaries/2026-11-14T1005Z-issue-154-orchestrator-state-bucket.md` (this file)

## Decisions made by the human

- Approved the Terraform tool and the top-level `terraform/` folder (2026-11-13, recorded on the issue).
- Reviewer findings 1 to 4 must-fix, finding 5 dropped (https://github.com/andrew-chung-au/socboard/issues/154#issuecomment-6874691045), and the exact `AGENTS.md` Layout line.
- Merged PR #171 after marking it ready.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI run 43577162016 on `dd52e25`: `VERIFY: PASS`, 1837 Python and 208 frontend tests).
- **Terraform:** `terraform check` (#155) runs `fmt -check`, `init -backend=false` and `validate` on `terraform/state` on every Terraform change.

## Proposed AGENTS.md changes

none (the Layout line was applied)

## Temporary changes

Worktree `.scratch/wt/154` (git-ignored), recreated once; not deleted.

## Interruptions

One QA launch stopped before checking (missing worktree); nothing was left behind.

## Unrelated problems noticed but not fixed

- The kit secret scan exits 1 on the whole `.gitignore` (lines 1 and 2 name an env file).
- `terraform/state/backend.tf.example` line 1 says "Step 5 of terraform/README.md", which is ambiguous now that a second README section numbers its steps (Low).

## Follow-ups for the next session

- The human's first apply (README steps, then the `VERIFY:` items in `terraform/state/main.tf`), then commit `.terraform.lock.hcl` made with `terraform providers lock` for `linux_amd64` and the human's platform.
- Re-check that 1.17.2 is still the newest stable at the first `init`.
- Lifecycle `filter {}` and abort-incomplete-multipart (Low, open).
