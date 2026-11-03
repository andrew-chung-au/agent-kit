# Issue #12: Write _docs/agent-team.md for the Agent Team Specification criterion

**Date:** 2026-10-18 (session started 2026-10-17)
**Spec version:** 16e1ec0

## What changed and why

- The session started on #15, but the human's commit fea6fb7 had added a Bolt-built frontend in `frontend-bolt/`. The PM re-groomed #15 (comments 6234073282 and 6234079369). The human then parked #15 until the Lovable credits reset, so the two frontends can be compared (Orchestrator comment 6234114564), and asked for an unrelated issue.
- #12: the PM groomed it (6234146060) and the human answered both decisions (6234208915), after which the body was replaced. The Engineer wrote `_docs/agent-team.md` and its README link (ede47bf). The Orchestrator committed the approved AGENTS.md link line (948e332). QA PASS at 948e332 (6243727864).
- At the decision point, the human approved a settings-reading rule and moved the scratchpad line from CLAUDE.md into AGENTS.md (6541893). The Engineer fixed the doc (32ed2a3), and QA re-checked only the changes: PASS at 92d9926 (6243839013).
- All roles ran as Claude Code subagents (claude-opus-5-5). QA used the same-tool exception, because OpenCode is unavailable and the human chose it (6243691600).

## Files created or modified

- `_docs/agent-team.md` (new: ede47bf, 32ed2a3)
- `README.md` (link line: ede47bf)
- `AGENTS.md` (protected: 948e332, 6541893)
- `CLAUDE.md` (protected: 6541893)
- `_docs/ai-usage-log.md` (ccd13b6, 45f7717, ca0dcf8, 92d9926, a5c214d)
- GitHub: #12 body replaced; comments on #12 and #15

## Decisions made by the human

- #15: Bolt was used because Lovable hit a credit limit. The approved prompt was pasted verbatim, with no follow-ups. Keep `.bolt/` for now. The prompt file name, folder and dependency approval are deferred.
- #12 grooming: the PM's wording for the QA same-tool exception; intent plus record for tool and model.
- The human ran the body edit as a `!` command. It did not apply (the body was unchanged), so the Orchestrator ran the same command once.
- QA tool: a fresh Claude Code subagent. AGENTS.md link line: approved as written.
- Decision point:
  - Rows with no recorded role say "not recorded".
  - The CLAUDE.md scratchpad line moves into AGENTS.md.
  - The #12 runs are added as Claude Code runs.
  - Tracked project settings files may be read: the human's wording, with the exact diff approved.
  - The Engineer's other choices are accepted.
  - No follow-up issues were selected.

## Mismatches with the spec or design docs

- `CLAUDE.md`, and the second `AGENTS.md` change, are outside #12's file-scope list. Both are the human-approved 6541893, noted by QA.

## Commands to validate

- **Verify:** `make verify BASE=ccd13b6` → PASS WITH WARNINGS (no TEST_CMD: no code exists), last run by QA at 92d9926.
- **Assert clean:** `make assert-clean` → PASS after both QA runs (948e332, 92d9926).
- `make clean-scratch` → ran at close-out.

## Proposed AGENTS.md changes

- none outstanding (948e332 and 6541893 applied).

## Temporary changes

- none. No processes started, no system changes, no installs.

## Interruptions

- The human's weekly usage limit ran out after the #12 QA-tool and AGENTS.md answers. On resume, `git status` was clean and HEAD was 45f7717, as expected; nothing was half-done.
- Blocked actions:
  - The tool blocked the PM's `gh issue edit 12`; the human then ran it (see Decisions).
  - The guard hook blocked QA's `git config core.hooksPath`; QA re-ran it read-only with `--get`. Nothing was changed.

## Unrelated problems noticed but not fixed

- QA risks not taken up:
  - The `agent-team.md` history table has no rule for keeping it current. It still lacks the Orchestrator's #12 commits, 32ed2a3 and the re-check.
  - `check-staged.sh` accepts `HUMAN_APPROVED=1` when AGENTS.md is staged with other files.
  - Approvals are recorded in comments as descriptions, not literal diffs.
- `_docs/ai-usage-report.md` §2 still has a TODO pointing at #12.
- Carried over: #10 is open; the repo-root `agent-kit/` duplicate remains.

## Follow-ups for the next session

1. Human: review and push `ccd13b6..HEAD`, plus the earlier `fea6fb7`/merge commits if not yet pushed.
2. #15: the human supplies the Lovable build (repo URL and SHA). Then decide the prompt file name, the folder (`frontend/`, or one folder per builder for comparison), dependency approval, and how #15's scope changes to compare the two frontends. The PM re-grooms.
3. #13 and #10 remain.
