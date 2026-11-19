# Issue #155: CI: format and validate the Terraform on every pull request

**Date:** 2026-11-14T10:05Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

One new workflow, `.github/workflows/terraform-check.yml` ("terraform check"). It runs on pull requests and pushes to `main` that change `terraform/**` or the workflow file, with `contents: read` only and no secret. It reads the Terraform version from `terraform/.terraform-version` (failing with a message that names the file if it is missing or empty), installs it with `hashicorp/setup-terraform`, runs `terraform fmt -check -recursive` once, then `init -backend=false` and `validate` in every folder that holds `*.tf` files, found by search. Both actions are pinned by commit SHA: `actions/checkout` v4.4.0 and `hashicorp/setup-terraform` v4.0.1.

Worked by Session A (Kiro Web). Standard tier. Branch `issue-155-tf-check-ci` (built from #154's branch), PR #172, merge commit `6ef2c4c`, commit `3c9bf0b`. The file is in a protected path, so the human approved the exact content (https://github.com/andrew-chung-au/socboard/issues/155#issuecomment-6874692086) before the Engineer committed it with `HUMAN_APPROVED=1`.

**QA ran after the merge.** I did not launch a QA before the human merged PR #172; the gap was found at close-out and QA ran on the merged state: PASS at `3c9bf0b` (https://github.com/andrew-chung-au/socboard/issues/155#issuecomment-6875639915).

**What I learned:** the first real Terraform check was this workflow's own run on #154's code, and a later run caught a real `validate` failure in #162 (a comma the provider refuses in a policy description).

## Reflection

### Engineer

https://github.com/andrew-chung-au/socboard/issues/155#issuecomment-6874744884: a `gh api ... --jq` read of a job log fails because the log is plain text, so the Engineer proposes that `_docs/agent-kit/procedures/verify.md` say "read job logs without `--jq`".

### QA

unknown (role not asked)

### Orchestrator

The approval request I showed the human wrapped the line `find terraform -name '*.tf' -printf '%h\n'` across two lines in the chat, and the Engineer reported 44 lines where the file has 55. The committed file is correct (`'%h\n'` on one line, checked by QA), but the human approved a rendering with a display glitch. When a protected-file diff is sent for approval, quote it from `git diff` output, not from the Engineer's text, and take the line count from `wc -l`.

## Launch usage

Engineer: 2 launches (wrote the file; committed, pushed, opened the PR and posted the comment). QA: 1 launch, after the merge. Reviewer: none. Active time and tool uses were not given: unknown.

## Files created or modified

- `.github/workflows/terraform-check.yml` (new, protected path, human-approved)
- `_session-summaries/2026-11-14T1005Z-issue-155-orchestrator-terraform-check-ci.md` (this file)

## Decisions made by the human

- Approved the exact workflow content and the `setup-terraform` v4.0.1 pin (its commit was not recorded anywhere before; the approval is the record).
- Merged PR #172 (before a QA existed; see above).

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI run 43577097640: `VERIFY: PASS`).
- **Terraform check:** CI run 43577097715 on the pull request, and push runs 43578593784 and 43583092881 on `main`, all succeeded on Terraform 1.17.2.

## Proposed AGENTS.md changes

none

## Temporary changes

Worktree `.scratch/wt/155` (git-ignored) no longer exists in the sandbox.

## Interruptions

none

## Unrelated problems noticed but not fixed

- With `bash -e`, the first folder that fails `validate` stops the loop, so later folders are not reported in that run (Low; seen in run 43579165424).
- A malformed version value fails inside `setup-terraform`, not with a message naming the file (Low).

## Follow-ups for the next session

- The human's throwaway-branch check: a deliberately misformatted `.tf` fails "Format check"; an undefined variable fails "Init and validate each folder" (steps in the Engineer comment). The invalid-file half was shown by accident in run 43579165424; the bad-format half has not been shown.
