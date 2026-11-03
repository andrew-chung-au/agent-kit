# Issue #72: Stage 5 task backlog

**Date:** 2026-10-22
**Spec version:** 97893c1

## What changed and why

- `_docs/tasks.md` (new, 36 tasks) is the Stage 5 backlog: tasks 1-29 in the rubric-tier milestones A/B/C, then the Committed scope section for the LLM brief, MCP server and n8n (tasks 30-36). It also has the coverage summary (US-1..US-16, the 12 criteria with points and earliest milestone) and the dependency chain. This is roadmap step 11; step 10 (`_docs/testing.md`, #56) was done.
- `README.md` gains one link line for `_docs/tasks.md` under "Planning documents".
- `ae6b708` aligns the US-15 coverage: tasks 28 and 29 now list `US-15` in `Covers:`, matching the summary row `| US-15 | 10, 28, 29 |`.

## Files created or modified

- `_docs/tasks.md` (new) and `README.md` at `05e3e60`; `_docs/tasks.md` at `ae6b708`.
- Unprotected close-out files: `_docs/roadmap.md` (step 11 row and check-in), `_docs/ai-usage-log.md`, this summary.
- GitHub: #72 created; comments 6331775484 (human D1/D2), 6331821940 (PM grooming), 6332002908 (Engineer), 6332195958 (QA PASS), 6332266585 (Engineer US-15 fix), 6332346303 (QA re-check PASS); #73 and `andrew-chung-au/agent-kit` #19 created.
- No protected file changed and no approval record was needed.

## Decisions made by the human

- Approved filing #72 with the PM's drafted body.
- D1 option 1: three rubric-tier milestones A/B/C for the scoring path, then a `Committed scope` section after C for the LLM brief, MCP server and n8n.
- D2 option 1: one Milestone A task, `planning evidence and tracker hygiene`, covering Problem Description, Product Specification, Agent Team Specification and Context Management.
- Fix the US-15 coverage-summary mismatch now; note the task-sizing risks (tasks 9, 10, 28, 29) and task 17's deploy wording only, for step 12.
- File the three follow-ups: `andrew-chung-au/agent-kit` #19 (task-template naming), and vuln-triage #73 (README `withdrawn` plus the Stage 5 tier-label note). There is no "fast lane" in `AGENTS.md`, so #73 follows the normal process.

## Mismatches with the spec or design docs

- `_docs/agent-kit/templates/task-template.md` is the issue template (Goal, Acceptance criteria, Out of scope, Constraints), not the five-field Stage 5 task format the issue named. The Engineer followed Stage 5 and the issue; the template naming is agent-kit #19.
- `README.md` line 27 omits the `withdrawn` status that `_docs/specs.md` includes; #73 fixes it.
- Stage 5's "Tier A/B/C" collides with the P1-P4 finding priorities and the architecture component tiers; #73 adds the clarifying sentence.

## Commands to validate

- **Verify:** `make verify` PASS at `05e3e60` and `ae6b708` (62 tests, no whitespace errors, no test files changed).
- **Assert clean:** PASS at `05e3e60` and `ae6b708`, HEAD unchanged after each QA run.
- Read-only coverage check (`python3 .scratch/check_tasks.py`): PASS twice (36 tasks, 16 user stories, 12 criteria, lower-numbered acyclic dependencies, dependency chain matches).
- QA PASS (6332195958) and re-check PASS (6332346303).

## Proposed AGENTS.md changes

- none

## Temporary changes

- `.scratch/` scripts and issue-body files; `make clean-scratch` ran at the end of the session.
- No processes started; no system configuration changed; no installs.

## Permission review

- Read-only (propose allowing): none
- Writes to the record (keep asking): `gh issue create` for #72 and #73 (issue-creation allow rule), `gh issue create -R andrew-chung-au/agent-kit` for #19 (same rule, another repo), `gh issue edit 72` (issue-edit ask rule), `make issue-comment` on #72 (allowed target)
- Risky (propose denying): none

## Interruptions

- none

## Unrelated problems noticed but not fixed

- QA risks noted, not filed: tasks 9, 10, 28 and 29 are the broadest and most likely to exceed one session; task 17's description says the image is "deployed" while the agent only writes templates and the human performs the first stack run. Both go to step 12 when tasks become issues.
- `_docs/testing.md` line 11 still says `make test` runs the frontend suite today; that stays true until task 13 and the plan states the growth.

## Follow-ups for the next session

- Groom and file the backlog issues for roadmap step 12 from `_docs/tasks.md` (human approval before creating them), splitting tasks 9, 10, 28 and 29 if needed.
- #73 (documentation housekeeping) and `andrew-chung-au/agent-kit` #19 (template naming) are filed and ungroomed.
- The roadmap step 11 row is marked done; step 12 is next.
