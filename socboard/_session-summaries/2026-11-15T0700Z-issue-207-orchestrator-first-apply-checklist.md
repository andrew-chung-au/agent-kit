# Issue #207: First apply, part A: a checklist for the human's apply of the state, IAM, CI-access and server parts, and the record of its VERIFY results

**Date:** 2026-11-15T07:00Z (UTC)
**Spec version:** 5985a83

## What changed and why

D19a, Standard tier from the PM proposal. This session covers stage (a) only: the checklist is written and QA passed, so development is complete and the human's run is next. The issue stays open for stage (b), when the human commits the results and QA re-checks them.

The PM wrote the D19 split and filed #207. The human approved it, and the body changed twice with the human's confirmation:
- the server stays running after the checks, and the issue has two stages;
- after the first QA, the role ARNs moved from repository variables to secrets, because GitHub prints step inputs and variables are not masked.

Branch `claude/207-first-apply-checklist`:
- `_human-tasks/2026-11-15T0055Z-human-task-207-engineer-first-apply-part-a.md`:
  - nine steps (state, iam-and-budgets, ci-access, the GitHub settings, the #156 branch check, server, a second plan, the plan-role refused cases, the next-day snapshot check);
  - 30 result rows, all `NOT CHECKED`;
  - the public-repo rule (no account number, no ARN containing it, no e-mail address, no secrets);
  - cost and teardown.
- `_human-tasks/2026-11-14T0928Z-human-task-156-engineer-ci-access-apply-and-branch-check.md`: secrets instead of variables; the probes print only "assumed" or the error code.
- `.gitignore`: `crash.*.log`, `override.tf`, `*_override.tf`, `.terraformrc`, `terraform.rc`.
- 3cb26e6 merges `origin/main` (c8bb4b9), approved by the human because it carries protected files.
- `_docs/records/findings/207.json`.

QA PASS at df6f4bb against the old body, then PASS at 3cb26e6 against the confirmed body. Assert-clean passed after each.

**What I learned:** an Actions log shows step inputs with values filled in, so any account-identifying value must come from a secret, not a variable, and error text must not be printed.

## Reflection

### PM

Reflection:
1. Slowed: the body was re-hashed three times (dee1607c, 54eb372a, 648e001c), and two of those edits came after approval. GraphQL is blocked and no make target edits issue bodies or titles, so every edit needed a hand-written `gh api -X PATCH` call.
2. Nearly wrong: I copied the #156 task file's "variables, not secrets; a role ARN is not a secret" without asking what reaches a public Actions log. Only QA caught that variables leak the account number. My brief also called 0928Z approved while `main` still said proposed.
3. Proposal: in `_docs/agent-kit/team/pm.md`, for any issue that touches CI or the cloud in a public repository, add a criterion listing each value that reaches an Actions log (variables, step inputs, error text) and whether it identifies the account. Effect: exposure is caught at grooming, not QA. Measure: post-approval body edits made for exposure reasons on D19b, D22a and D22b; target 0.

### Engineer

Reflection:
1. Slowed: two full `make verify` runs of about 5 minutes each for a docs-only change (2272 Python tests on two files under `_human-tasks/`). In the fix round, `BASE=origin/main` also failed, because main had moved and 75 unrelated files showed up as changes. I re-ran it with the merge base, 6fe249d.
2. Nearly wrong: the first probe filter, `grep -m1 -o`, would have printed every parenthesised word of an AWS error line. Only an offline sample test in `.scratch/` caught it. Separately, the first draft let the full role ARNs print in public Actions logs as repository variables; QA and the human changed that to secrets.
3. Proposal: in `_docs/agent-kit/procedures/verify.md`, say to pass `BASE=$(git merge-base HEAD origin/main)` (or its value) when the branch is behind `origin/main`. Effect: no false FAIL and no repeat run. Measure: count verify FAIL reports over the next ten issues whose diff stat lists files the branch never touched (target 0).

### QA

Reflection:
1. Slowed: `make verify` took about 5 minutes (pytest 264 s plus Vitest 35 s, `.scratch/qa-207-verify.log`) for a diff of three markdown and ignore files; I also had to search to find the kit secret scanner (`_docs/agent-kit/scripts/scan-issue-body.sh`) because no make target names it.
2. Nearly wrong: the criterion asks "the kit's secret scan reports nothing", but no Commands entry says which scan that is, so a QA could pass it on the comment wrapper's scan alone; I also nearly missed that `terraform/README.md:75` and `ci-access/outputs.tf:1` went stale, found only by a broad grep.
3. Proposal: add a `make secret-scan FILE=<path>` target and its Commands line in `AGENTS.md`, wrapping `scan-issue-body.sh`. Expected effect: criteria and QA name one command. Measure: in the next five issues with a secret-scan criterion, QA comments quote that target's output.

## Launch usage

- PM (D19 split, filed and groomed #207, #208, #209; later body edits and #218): 27m23s, 43 tool uses on the first run; edits 6m31s/24, 9m24s/12, 4m20s/8, 4m10s/26, 7m51s/23; the earlier resumes were stopped or limited (unknown)
- Engineer (checklist, first run): unknown (stopped by a usage limit)
- Engineer (checklist, resumed): 52s, 5 tool uses
- QA (stage (a), df6f4bb): 14m14s, 36 tool uses
- Engineer (fix round for the confirmed body): 13m42s, 53 tool uses
- QA (re-check, 3cb26e6): 6m56s, 35 tool uses (7m36s, 41 with its reflection)
- Engineer (reflection): 27s, 5 tool uses
- PM (reflection): unknown

## Files created or modified

`_human-tasks/2026-11-15T0055Z-human-task-207-engineer-first-apply-part-a.md` (new), `_human-tasks/2026-11-14T0928Z-human-task-156-engineer-ci-access-apply-and-branch-check.md`, `.gitignore`, `_docs/records/findings/207.json` (new), this summary.

## Decisions made by the human

- They split D19 into D19a (#207, now) and D19b (after D17c).
- The server stays running after the checks.
- #207 is one issue with two stages; stage (a) must say plainly that development is complete and only the run remains.
- Role ARNs are repository secrets, not variables. Probes print only the error code. The #156 task file is updated, and `.gitignore` gains the Terraform entries. They confirmed the new bodies of #207 and #209.
- They approved deleting a private artifact QA published by mistake (deleted).
- They approved committing the merge of `origin/main` with protected files.
- D20 creates the `socboard-deploy` document. #162's decision record is approved, which goes into #208.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify BASE=c8bb4b9`: PASS (2438 Python, 237 frontend).
- The kit's secret scan on both task files exits 0. `git check-ignore` confirms the new ignores, and that `backend.tf` and `.terraform.lock.hcl` stay tracked.

## Proposed AGENTS.md changes

A **Secret scan** line for a `make secret-scan FILE=<path>` target, proposed by the Engineer and by QA; see F-207-6. Not applied.

## Temporary changes

- Terraform 1.17.2 is still in `.scratch/tf/` (124 MB) for offline checks in #208, #209 and #218; `make clean-scratch` removes it when those are done.
- `.scratch/ref-vt` (18 MB read-only clone) is still there, waiting for `make clean-scratch`.
- One private claude.ai artifact published by QA by mistake was deleted with the human's approval.

## Interruptions

- The first Engineer launch hit a usage limit with the checklist staged, not committed. It was resumed and finished. The orchestrator checked the diff and Verify before pushing.
- Container restarts and usage limits interrupted the PM twice. Each time, the issue state on GitHub was checked before resuming. One PM edit to #209 had landed without its hash; the PM re-read the live body and recorded the hash.

## Unrelated problems noticed but not fixed

- F-207-1: The README and the header comment of `ci-access/outputs.tf` still say the role ARNs come from repository variables.
- F-207-2: The next-day snapshot check filters on the project tag, so it cannot show a snapshot of the untagged root volume.
- F-207-3: The secret-read probe cannot tell the explicit deny from a missing allow.
- F-207-4: The checklist names README sections by heading, not by link.
- F-207-5: Three result rows settle provider argument-name VERIFY items without naming them.
- F-207-6: There is no make target for the kit's secret scanner.
- F-207-7: The findings procedure does not say where a two-stage issue's stage (b) findings go.

## Follow-ups for the next session

- The human merges the PR (stage (a)). The orchestrator then posts the "Stage (a) complete: development complete, waiting for the human's run" comment.
- The human runs the checklist and commits the results. QA re-checks the run-record criteria, then the issue closes (stage (b)).
- #208 (labelled) can start, and should pick up F-207-1. Then #209 (approved, Heavy; it can be built before stage (b), but closes after it), then #218 once labelled.
- #199's summary predates sweep 7, so it has no findings file.
