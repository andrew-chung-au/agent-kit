# Issue #93: Merge the submission track draft into the main roadmap; pre-merge clean-ups

**Date:** 2026-10-22
**Spec version:** 4fa7a55

## What changed and why

#93 began as one large issue (roadmap merge plus documents the H2-H7 decisions required). It was split by the PM into #93 (roadmap merge, milestones), #97 (architecture and AWS setup), #98 (spec Showcase section), #99 (tasks and plan summary) and #100 (showcase marking), and later gained #101-#103 and the folded-in items from #92. The Engineer implemented #93 in two commits. Commit 1b14412: the submission draft is folded into `_docs/roadmap.md` as phases S1-S5 with estimates 12, 14, 19 and 24 and Observability 2 at C3; H1-H7 are recorded as resolved; D1, D2, D3, D6 and D7 are resolved and D4 and D5 stay open; `_docs/roadmap-submission-draft.md` is deleted; the README links `roadmap-showcase.md` and `aws-setup.md`; three check-in lines were added (#73 done, `aws-setup.md` added at 25960f5, and the merge, which describes commit 2 in words with no hash); the "AWS account with an AWS Budgets alert" prerequisite points at `_docs/aws-setup.md` and is not marked done. Commit e6ceb22: `I-OWNER-SEND` and `I-OWNER-HOLD` in `_docs/testing.md` use an in-process fake mail sink and stay in `make test` (no case ID or count changed); `_docs/tasks.md` task 17 accepts an already-existing GitHub OIDC provider and task 37 cites the decision instead of "option (b)"; `_docs/architecture.md` marks the LLM-keys secrets row, the MCP server section and the "second claim" line as showcase; `_docs/plan-summary.md` A37 says the one server stops nightly. The two GitHub milestones "Submission" (#1) and "Showcase" (#2) were created by the orchestrator after the human approved. QA passed everything at e6ceb22 after the milestone recheck. #92's items 1, 2 and 4 are covered here; item 3 was already done; item 5 is obsolete except the OIDC sentence; items 6 and 7 stay noted only.

## Files created or modified

- `README.md`, `_docs/roadmap.md`, deleted `_docs/roadmap-submission-draft.md` (1b14412)
- `_docs/architecture.md`, `_docs/plan-summary.md`, `_docs/tasks.md`, `_docs/testing.md` (e6ceb22); none protected
- GitHub milestones "Submission" and "Showcase" (tracker, not files)
- `_docs/ai-usage-log.md` and this file (separate commits)

## Decisions made by the human

- 2026-10-22: approved the #93 split and the recommendations on it; approved folding #92's items 1, 2 and 4, the task 17 OIDC sentence, the in-process mail sink and the architecture and plan-summary marks into #93.
- 2026-10-22: approved creating the two GitHub milestones ("ok that is fine", after an explanation of what they are).
- Not approved, not done: three one-line fixes (see Unrelated problems).

## Mismatches with the spec or design docs

- Roadmap C2 says it depends on S1 while task 23 depends on task 15 (S2); the phase order is still right (QA, left for plan review).
- D2 is recorded as "kept but half applied": `service.version` is not in the `architecture.md` allowlist (A32), so that edit is still open work.
- Engineer judgement calls accepted by QA: a new milestone C9 for task 38 (the backend scheduler), and the Docker-capable-environment step folded into S2's dependency on T3.

## Commands to validate

**Verify:** `make verify` (QA: PASS, 62 tests passed, type check pass, whitespace pass, no test files changed)
**Assert clean:** `make assert-clean` (PASS after each QA run)

## Proposed AGENTS.md changes

none

## Temporary changes

The two GitHub milestones are new tracker state, kept on purpose. Undo: delete them in the GitHub UI or `gh api -X DELETE repos/{owner}/{repo}/milestones/<number>`. Nothing else.

## Permission review

PM, Engineer and QA comments for #93 say none required on the merits, with the PM's tracker writes matching ask rules. The milestone creation was a merits-based approval request (tracker write, no make target).

- Read-only (propose allowing): none
- Writes to the record (keep asking): `gh issue edit 93` (PM, several times, ask rule in `opencode.json`); `gh api repos/{owner}/{repo}/milestones` x2 (orchestrator, merits request, no make target); `make issue-close N=93` and `N=92` (orchestrator, matches `make issue-close*`)
- Risky (propose denying): none

## Interruptions

The session ran across an opencode rate limit (before this Claude session picked it up) and a Claude usage-limit reset. No role left partial output; each hand-back was checked against `git status` and `git log` before the next step.

## Unrelated problems noticed but not fixed

- `architecture.md` credentials-table LLM-keys row (~line 325) is unmarked and disagrees with the secrets-table row.
- `testing.md` line 175 prose still names MailHog for `I-OWNER-SEND`.
- `roadmap-showcase.md` line 3 names the deleted draft in backticked prose (a note, not a link).
- The case-count script lives in git-ignored `.scratch/`, so the counts cannot be rerun from a clean clone.
- Spec Open question 3 and A26 still say "SES by email"; naming MailHog there would be a protected change.

## Follow-ups for the next session

- Plan review (roadmap step 14), then Tier A build. The three one-line fixes above can be done before it with the human's go-ahead.
- Settle at plan review which backend the local responder reads, and the `service.version` allowlist edit.
- The human reads `git show 4fa7a55` (protected spec change, approved after the commit) and `git diff origin/main --stat -- .` before pushing.
