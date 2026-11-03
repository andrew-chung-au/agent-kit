# Issue #105: Task 15: add the .env.example sentence to _docs/tasks.md

**Date:** 2026-10-22
**Spec version:** 4fa7a55

## What changed and why

The documents say a committed `.env.example` lists setting and secret names only (`architecture.md` line ~311, `aws-setup.md` line ~111, roadmap B2), but no task in `tasks.md` created it. The PM found this while grooming #104. At the human's choice (option A), the Engineer appended one sentence to the end of task 15's existing Description line: task 15 creates a committed `.env.example` with names only and no values, which a reviewer copies to a git-ignored `.env`. The file lists only what the whole submission stack needs (the database password, the repository read token, `RESPONDER_API_TOKEN`, the Grafana admin password, the responder's LLM key, and the stub switches `LLM_MODE=stub` and `RESPONDER_MODE=stub`); the backend LLM key, MCP, n8n, tracker tokens and SMTP credentials are not in it. Tasks 24 and 28 use names already listed. No label was added, so the plan-summary tallies and the line numbers it cites (191, 294) are unchanged. `.env.example` itself is not created: no application files are allowed until the plan passes review, and task 15 builds it. QA passed it at 98d0a7e.

## Files created or modified

- `_docs/tasks.md` (98d0a7e, one line); not protected
- `_docs/ai-usage-log.md` and this file (separate commits)

## Decisions made by the human

- 2026-10-22: option A, add the sentence to task 15, rather than leaving it for the build to catch.

## Mismatches with the spec or design docs

- The names for the database password, repository read token, Grafana admin password and the responder's LLM key are not fixed anywhere; task 15 chooses them. Only `RESPONDER_API_TOKEN`, `LLM_MODE`, `RESPONDER_MODE`, `MCP_API_TOKEN` and `N8N_API_TOKEN` are named in the documents.
- The responder's GitHub token (arrives with task 28) and the Grafana Viewer token (task 24) are not in the list or the `architecture.md` secrets table; decide at plan review whether their names go in `.env.example`.
- QA's raw grep finds 7 literal `VERIFY:` strings in `tasks.md`, one more than the plan summary's tally of 6: a backticked mention at line 107, the same in the parent commit, not caused by this issue.

## Commands to validate

**Verify:** `make verify` (QA: PASS, 62 tests passed, type check pass, whitespace pass, no test files changed)
**Assert clean:** `make assert-clean` (PASS)

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Permission review

PM, Engineer and QA comments for #105 say none required on the merits. The PM's issue creation matched an ask rule.

- Read-only (propose allowing): none
- Writes to the record (keep asking): `gh issue create` (PM, ask rule in `opencode.json`); `make issue-close N=105` (orchestrator, matches `make issue-close*`)
- Risky (propose denying): none

## Interruptions

none

## Unrelated problems noticed but not fixed

- The extra literal `VERIFY:` mention at `tasks.md` line 107 (see above).

## Follow-ups for the next session

- Plan review (roadmap step 14).
- Task 15 build: choose the unfixed variable names and create `.env.example`.
