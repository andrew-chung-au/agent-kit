# Issue #017: enforce "committed alone" for protected changes

**Date:** 2026-10-20
**Spec version:** 9f742d2

## What changed and why

- `_docs/agent-kit/scripts/check-staged.sh` now refuses a commit made with `HUMAN_APPROVED=1` when at least one staged path is `PROTECTED` and at least one is not. It names every non-protected path and says the protected paths must be committed alone. Commits containing only protected paths still pass, so #12's `6541893` precedent (`AGENTS.md` + `CLAUDE.md`) remains valid.
- The existing refusals are unchanged: protected paths without `HUMAN_APPROVED=1`, forbidden files, and whitespace still fail as before.
- No hook file changed, so no `make hooks` re-install is needed; the installed hook calls the script through `KIT_DIR` at run time.
- The unused repo-root `agent-kit/scripts/check-staged.sh` was left untouched; #38 owns its removal.
- QA found two remaining risks outside the criteria. The human chose to file both: #39 (quoted-filename bypass) and #40 (repo-root paths still process-only).

## Files created or modified

- `64308d7` protected change: `_docs/agent-kit/scripts/check-staged.sh` only (+10).
- Approval record on #17: comment 6280810952 (full commit, parent, path, verbatim diff, blob `3712882`).
- QA comments on #17: 6281018092 (first check at `64308d7`) and 6281387668 (re-check at `df72298`).
- New issues: #38 (duplicate folder cleanup), #39 (quoted filenames), #40 (repo-root paths). One `PM:` comment linking them on #17.
- This summary and the usage-log entries. No other repository change.
- `4454518` and `df72298` (#35) were committed by a concurrent orchestration session, not this one.

## Decisions made by the human

- Enforce "committed alone" in `_docs/agent-kit/scripts/check-staged.sh` only; do not change hook files.
- Leave the duplicate `agent-kit/` folder; file cleanup issue #38.
- File follow-ups #39 and #40 for the two QA risks.
- Pause the concurrent #35/#33 orchestration while this session finishes #17/#18 and step 6.

## Mismatches with the spec or design docs

- The spec is unchanged; none.
- Process: the lifecycle assumes one orchestrator per working tree. A concurrent session moved HEAD from `64308d7` to `df72298` during the first QA run. QA was re-run at the stable HEAD; its verdict and the #17 script blob are unchanged. Both sessions paused and coordinated after the human's answer.

## Commands to validate

- **Verify:** `make verify BASE=1d31aac`: PASS at `df72298`; 35 tests passed, whitespace PASS, no weakened tests.
- **QA matrix:** 12/12 in a `.scratch/` throwaway repo: the six required cases, both rename directions, `.env`, whitespace, plus the no-approval and protected-deletion-only variants.
- **Approval record:** `git show --format= --no-renames --patch 64308d7 -- _docs/agent-kit/scripts/check-staged.sh` matches the record; `git rev-parse df72298:_docs/agent-kit/scripts/check-staged.sh` is still `3712882`.
- **Assert clean:** `make assert-clean`: PASS at `df72298`, HEAD unchanged after the re-check.

## Proposed AGENTS.md changes

None.

## Temporary changes

None. No process or server was started, nothing was installed, and no system configuration changed. `make clean-scratch` was not run: the paused concurrent session still has `.scratch/` files this session did not create. Clean up when both sessions are done.

## Permission review

- Read-only (propose allowing): none.
- Writes to the record (keep asking): none; `gh issue create`, `gh issue edit`, `gh issue comment`, `make issue-dump` and `make assert-clean` ran without stopping.
- Risky (propose denying): none.
- Proposed `opencode.json` and `.claude/settings.json` changes: none.

## Interruptions

The first QA run overlapped with the concurrent #35 session, which moved HEAD. The human chose to pause that session; QA re-ran at `df72298` and passed. The Engineer, PM and QA each completed in one run otherwise.

## Unrelated problems noticed but not fixed

- The concurrent #35 session's log entry says its protected diff was "left uncommitted", but it is committed as `4454518` and `df72298`. That session owns the correction; #35 remains open pending its QA.
- The #17 script still requires `HUMAN_APPROVED=1` and, now, a protected-only stage; `git commit --no-verify` and `git cherry-pick` remain process controls. No issue filed because `AGENTS.md` already forbids `--no-verify`.

## Follow-ups for the next session

- Implement #18 (approval-record rule) next, as roadmap step 5 requires it before the six protected spec commits.
- Then implement #3, #6, #4, #5, #7, #8 as separate protected commits in dependency order, after the batched answers already recorded.
- #38, #39 and #40 are filed but not scheduled.
- Resume the other session for #35 QA and #33 after step 5/6 handoff.
