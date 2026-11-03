# Issue #018: protected-change approval record

**Date:** 2026-10-20
**Spec version:** 9f742d2

## What changed and why

- A protected-file commit now gets a new issue comment recording the exact approved text: issue, full commit and parent SHAs, paths, approval date, the exact `git show` command, the verbatim diff, and a blob ID per path.
- `AGENTS.md` and `_docs/agent-kit/templates/AGENTS.md.template` carry the same post-commit, pre-close sentence and point to the format, so the shared source and the project copy stay in sync.
- `_docs/agent-kit/procedures/asking-the-human.md` has the new `## Approval record` section with the human-approved format (2026-10-20), field rules, refused cases and the documentation-only limit.
- `_docs/agent-kit/process.md` step 7 says to post the record after each approved protected commit; step 8 says the session summary names each record comment.
- The commit `efae1ea` is the first live test: its own record on #18 (comment 6282041221) passed every check.

## Files created or modified

- `efae1ea` protected commit, four paths only: `AGENTS.md`, `_docs/agent-kit/procedures/asking-the-human.md`, `_docs/agent-kit/process.md`, `_docs/agent-kit/templates/AGENTS.md.template` (+36/-3).
- Approval record on #18: comment 6282041221. QA comment: 6282208055.
- `_docs/roadmap.md`: step 5 `done`, step 6 `doing` with answers recorded, decisions 1 and 3 resolved, step 3 marked `doing` (implementation `df72298`, QA pending), new check-in line.
- This summary and the usage-log entries. No other repository change.

## Decisions made by the human

- Include `_docs/agent-kit/templates/AGENTS.md.template` in the same protected commit, rather than filing a follow-up.
- Approve the exact four-file diff for commit `efae1ea`.
- (Earlier in this session) script-only enforcement for #17; leave the duplicate folder to #38; file #39 and #40; pause the concurrent #35/#33 session.

## Mismatches with the spec or design docs

None. The product spec is unchanged.

## Commands to validate

- **Verify:** `make verify BASE=ea257c9`: PASS at `efae1ea`; 35 tests passed, whitespace PASS, no weakened tests.
- **Approval record:** posted diff and the stated `Diff command` output both 8394 bytes, `cmp` exit 0; `Paths` equals `git show --name-only`; all four blob IDs match `git rev-parse <commit>:<path>`.
- **Refused cases:** missing field, abbreviated SHA, path outside `PROTECTED`, mismatched diff and mismatched blob ID were rejected by the written rule in a `.scratch/` reading check; merge commit rejected by rule (no merge exists).
- **Assert clean:** `make assert-clean`: PASS at `efae1ea`, HEAD unchanged after QA.

## Proposed AGENTS.md changes

None beyond this issue's own approved change.

## Temporary changes

None. No process or server was started, nothing was installed, and no system configuration changed. `make clean-scratch` was not run: the paused concurrent session still has `.scratch/` files this session did not create. Clean up when both sessions are done.

## Permission review

- Read-only (propose allowing): none.
- Writes to the record (keep asking): none; `gh issue create`, `gh issue edit`, `gh issue comment`, `make issue-dump` and `make assert-clean` ran without stopping.
- Risky (propose denying): none.
- Proposed `opencode.json` and `.claude/settings.json` changes: none.

## Interruptions

None in #18. #17's first QA run overlapped with the concurrent #35 session; the human paused that session and QA re-ran at a stable HEAD.

## Unrelated problems noticed but not fixed

- The approval event for `efae1ea` happened in the orchestrator session, not in an issue comment, so the record attests it rather than independently proving it. This is the documented limit of the approved rule, not a defect.
- The posted record diff includes `index` lines that the engineer's earlier draft snippets omitted; it matches the stated `git show` command, so no action.
- #35 remains open awaiting QA in the paused session; its log entry still says the protected diff was uncommitted, which the other session owns.

## Follow-ups for the next session

- Implement the six spec-review issues as separate protected commits, in order: #3, #6, #4, #5, #7, #8. The batched answers are recorded in the issues.
- #38, #39 and #40 are filed but not scheduled.
- Resume the other session for #35 QA and #33 after step 6, or as the human prefers.
