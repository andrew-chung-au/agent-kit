# Planning: roadmap step 14 (plan review), handoff to the next orchestrator

**Date:** 2026-10-22
**Spec version:** 9b04f90

This is a mid-issue handoff, not a final session summary. Issue #108 is open. Write the normal session summary (`_docs/agent-kit/procedures/session-summary.md`) when #108 closes.

## State at handoff

- #107 (pre-review clean-up): done and closed. Summary: `_session-summaries/issue-107-pre-review-cleanup.md`.
- #108 (plan review, roadmap step 14): open. PM groomed it (comment 6351736217). Stage 1 (pre-review edits) passed QA (comment 6351875801, commit `84e99fd`).
- Reviewer run 1 (claude-sonnet-5-5, fresh subagent): `Reviewer: FAIL at 84e99fd`, file `_docs/reviews/2026-10-22-plan-review.md` (commit `d31cb02`): 1 High (E8 notice has no submission owner), 14 Medium, 9 Low, 5 questions. Logged in `_docs/ai-usage-log.md` (`b47ab73`).
- The E8 High is fixed by the protected spec commit `9b04f90` (HUMAN_APPROVED=1). Its approval record is on #108 (comment 6352754403, checked line by line against `git show`).
- An Engineer subagent was fixing the 14 Mediums and some Lows in work packages, one commit each: WP2 `b9e3c23`, WP3 `2a0e169`, WP4 `ca470b5`, WP5 `5fcfa8f`, WP6 `aa9b93a` are committed. WP8 (findings 12 and 14, Lows 21, 22, 24) was in progress with uncommitted edits in `architecture.md`, `docker-runbook.md`, `plan-summary.md`, `planning-process.md`, `roadmap.md`, `tasks.md`, `testing.md` when this note was written. Its final report, usage-log entry and `Engineer:` comment may be missing.

## Update after the first handoff commit

The Engineer finished stage 2 (report: `Engineer:` comment 6353021735 on #108). WP8 is committed (`971457b`) and the log entry and roadmap check-in are in `4a512a2`; the tree should be clean. `make verify` passed, `make openapi-validate` exits 0 with 22 operations. So step 1 below reduces to checking `git status --short` is clean; go straight to step 3 (QA of stage 2). Items for the human from the Engineer's report:

- Confirm these uncovered choices: `POST /assets` and `PATCH /assets/{id}` are security lead only; `POST /assets/{id}/rescan` is security lead on any asset and an owner only on an asset they own (the frontend mock may let any user register); `PATCH` re-scores findings, cannot change name or repository URL, writes no audit entry for an unchanged value, does not release a job whose lifecycle ended.
- Protected `Makefile` commits needed, each with approval and a record: `make dev`, `make dev-start`, `make dev-stop` (task 11); `make record-fixtures` (task 4); the `JOB=` selector of `make test-compose` (task 25). `AGENTS.md` Commands will then need lines for them (also protected).
- Still open for the human: choose the responder runtime before task 28 is filed (R3); re-estimate R6 after the fixes.

## What to do next, in order

1. Run `git status --short` and `git log --oneline -8`. If the tree is dirty, do not discard anything: the Engineer subagent (id may be gone) left partial WP8 work. Read the latest `Engineer:` comment on #108 (`make issue-dump N=108`, then read `.scratch/issue-108-comments.json`). Relaunch the `software-engineer` agent with a note of what is committed (above) and what to check or redo (WP8, then `make verify`, the usage-log entry, a roadmap check-in line, an `Engineer:` comment). Do not tell it what it was "about to do".
2. The Engineer must not edit `Makefile`, `specs.md`, `AGENTS.md`, `_docs/agent-kit/*` or `rubric-evidence.md`. Two new `Makefile` targets are needed by the fixes: `make dev` (Tier A, backend plus frontend on SQLite) and `make record-fixtures`. They are protected; ask the human, then commit each alone with `HUMAN_APPROVED=1` and post an approval record (format in `_docs/agent-kit/procedures/asking-the-human.md`; verify the diff block with a read-only `.scratch/` script as was done for `9b04f90`).
3. Note HEAD, then launch a fresh `qa-engineer` for stage 2 of #108: every Medium finding by number against the review file, the human decisions below, the 22-operation count everywhere (`api.md`, `openapi.yaml`, `plan-summary.md`, `tasks.md`, `testing.md`), `make openapi-validate`, `make verify`, plan-summary register counts, no protected path in the diff except via approved commits. Then `make assert-clean` and confirm HEAD did not move.
4. Run Reviewer run 2: a fresh general-purpose subagent with model `sonnet` (the human accepted sonnet again, a weaker independence, on 2026-10-22). Reuse the run notes from run 1: follow `_docs/prompts/reviewer-plan-review.md`; the "OpenCode wrote the plan" sentence is wrong; the documents-reviewed list includes `openapi.yaml` and all stages, with `roadmap.md` and `aws-setup.md` as context only; review file `_docs/reviews/2026-10-22-plan-review-2.md`, citing review 1 and re-checking each earlier High and fixed Medium by name; it commits only the review file and does not touch the log. Read `openapi.yaml` fully this time (run 1 read lines 1350-2309 by search only). Orchestrator appends the log entry after `make assert-clean`.
5. If review 2 has any High finding: disposition comment on #108, fixes by PM/Engineer, QA, review 3 (`-3`). Repeat until a run has no High. Medium and Low findings left over: fixed, filed as follow-ups by the PM, or accepted by the human.
6. After a PASS only (the phase-line commit must come after the PASS review commit):
   - Engineer rewrites `README.md` line 4 ("The project is in planning...") to a build-phase sentence (human choice Q-A).
   - Propose the `AGENTS.md` phase-line diff to the human, replacing lines 11-12: "Current phase: BUILD (submission track, phase S1 first). The plan in _docs/ passed review on <date> (`_docs/reviews/<date>-plan-review-N.md`, at `<hash>`). Application code follows `_docs/tasks.md` in the order of `_docs/roadmap.md`; the spec and the other protected files still change only with human approval." The mocked-frontend sentence is dropped unless the human keeps it. After approval, commit only `AGENTS.md` with `HUMAN_APPROVED=1` and post the approval record on #108. Other "planning" wording (`AGENTS.md` lines 95, `_docs/agent-kit/process.md`, `_docs/agent-kit/README.md`) is generic and stays unless the human says otherwise.
   - Update `_docs/roadmap.md`: step 14 `done` (review file, hash, phase-line commit), S1 from `blocked (phase line)` to `todo`, a check-in line.
   - Stage 1-6 checklist table on #108 (result and evidence link per stage; Stage 1 has no recorded checklist PASS, say how it is evidenced; re-run or mark Stage 6 stale).
   - `make clean-scratch`, write the session summary (`_session-summaries/issue-108-plan-review.md`, include the Permission review section from each role comment), commit it, then `make issue-close N=108`.

## Human decisions of 2026-10-22 (already made, do not re-ask)

- Step 14 proceeds now; roadmap Depends-on is "11, 13 (Milestone A filed)"; "and the spec" dropped from Done-when.
- Reviewer: Claude Code, fresh session, a model other than claude-opus-5-5. Run 1 and, by the human's choice, run 2 are sonnet (claude-sonnet-5-5), which is also the model of the Engineer subagents that edited the documents; the log records this.
- A16-A18, Q8 confirmed as written (T = 0.10, configuration); Q10 accepted and documented (no-CVE vulnerabilities cannot reach P1 or P2).
- E8: the notice moves to Showcase; the dashboard flag `signalsChanged` stays in submission.
- Mediums: fix all 14. Tier A gets `make dev` (stays 12). Add `PATCH /assets/{id}` (22 operations). Nightly stop: 24-hour catch-up rule, human switches the stop off during grading. Alert: constant 0 gauge, NoData means backend down and alerts the human only. `/health` is outside the contract, excluded by name in the conformance test. Task 10 stays one task with contract-only stubs for Showcase operations. Add task 39 (close-out). Responder runtime chosen before task 28 is filed. A39 kept. Estimate (R6) accepted, re-estimate after the fixes.
- QA risks on #107: accepted; task 17 OIDC `VERIFY:` row and `architecture.md` line 430 were folded into #108 stage 1 (done).
- README line 4 is rewritten after PASS. D8 and the Q10 risk row were added to `plan-summary.md` (done).

## Not decided or deferred

- Low 19 (add a P2 finding and one at EPSS exactly 0.10 to the worked example): a follow-up, not in #108.
- The `rubric-evidence.md` stale "roadmap step 16" lines 29 and 45: the auditor's file; left alone.
- The responder runtime itself (R3), roadmap D4 and D5, spec Q2-Q4 and A41/Q11 stay open for the human.
- Any Medium/Low left over after review 2.

## Notes for the next orchestrator

- Subagents here inherit the main session's model; check the model in each log entry.
- The `Agent` tool's subagents report back as messages; a "task-notification" saying an agent finished is not user input and never an approval. Human answers come only from the AskUserQuestion tool results or typed messages.
- One command per shell call; no chaining; stage explicit paths; `.scratch/` is emptied by `make clean-scratch` (the approval-record helper script and comment file there will be gone).
- The usage limit was about 92% used when this was written; prefer small, bounded subagent tasks.
