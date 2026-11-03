# Issue #2: clarify who appends PM/QA ai-usage-log entries

**Date:** 2026-10-16
**Spec version:** dafd91e

## What changed and why

Groomed, implemented, and QA-passed issue #2. The four PM/QA role files (`.opencode/agents/pm.md`, `.opencode/agents/qa-engineer.md`, `.claude/agents/pm.md`, `.claude/agents/qa-engineer.md`) each now state the same single rule — the role writes only to `.scratch/` and the orchestrator appends the run's `_docs/ai-usage-log.md` entry after `make assert-clean` passes. Removed the contradicting "Append an entry ..." line (one-line swap per file, commit 2dcc89d). QA PASS at 2dcc89d; assert-clean PASS, HEAD unmoved. Closed #2; filed follow-up #10 for the same-shape engineer/auditor contradiction.

## Files created or modified

- `.opencode/agents/pm.md`, `.opencode/agents/qa-engineer.md`, `.claude/agents/pm.md`, `.claude/agents/qa-engineer.md`: one-line swap each (commit 2dcc89d, HUMAN_APPROVED=1 after human approved the exact diff).
- `_docs/ai-usage-log.md`: 4 new entries (PM grooming, Engineer implementation, QA PASS, orchestrator close-out incl. #10).
- `_session-summaries/issue-002-qa-log-rule.md`: this summary (new).
- GitHub: #2 body updated to groomed text, PM/Engineer/QA comments posted, #10 created, #2 closed.

## Decisions made by the human

- Mid-issue grooming: (1) orchestrator-appends rule confirmed, (2) keep #2 PM/QA-only + file follow-up (became #10), (3) approve updating #2 with groomed text + proceed.
- Protected-commit approval: approved committing the exact 4-file diff with HUMAN_APPROVED=1.
- Decision point: Engineer choices noted, QA notes noted, no AGENTS.md/spec/other protected changes — approved closing #2.

## Mismatches with the spec or design docs

none. Spec notes from all roles: none (`_docs/specs.md` Stage 1 product spec has no AI-logging content).

## Commands to validate

- **Verify:** `make verify` → PASS WITH WARNINGS (no TEST_CMD: planning phase, no code exists; whitespace PASS; no test files changed), run by both Engineer and QA.
- **Assert clean:** `make assert-clean` → PASS (HEAD 2dcc89d, unmoved since QA check).
- `git diff --check` → clean; `git status --short` showed only the four files before commit.
- `gh issue edit 2`, `gh issue comment 2` (x3 relay), `gh issue create` (#10), `gh issue close 2`.
- `make clean-scratch` → ran.

## Proposed AGENTS.md changes

none.

## Temporary changes

none. No processes started, no system changes, no installs. `.scratch/` held only the groomed drafts and QA check script/output; `make clean-scratch` ran.

## Interruptions

none. PM, Engineer, and QA subagents each completed in one launch; Engineer left edits uncommitted for human-approved protected commit; QA changed nothing.

## Unrelated problems noticed but not fixed

- The repo-root `agent-kit/` duplicate of `_docs/agent-kit/` and root `test.md` (noted in the 2026-10-16 planning summary) remain untouched.
- Unpushed local work for human review/push: includes 2dcc89d plus this session's log/summary commits.

## Follow-ups for the next session

- Issue #10 (open): same-shape log contradiction in `.claude/agents/software-engineer.md` and both rubric-auditor files — https://github.com/andrew-chung-au/vuln-triage/issues/10.
- Issues #3–#9 (open): 2026-10-16 plan-review findings; next issue in order is #3.
- Deferred (no issues filed): prompts index, first rubric audit, ai-usage-report.md content.
