# Planning and trial plumbing: backlog filed, frontend re-scoped, ponytail plumbing #23 to #25

**Date:** 2026-11-10T09:24Z (UTC)
**Spec version:** d913e19

## What changed and why

- Backlog (2026-11-09): the PM pass found the spec ready (definition of ready, item by item) and filed 19 issues, #7 to #25, groomed with recorded body hashes. The human approved the order after questioning the old draft: scoring before ingest, the audit writer built early, tests inside each issue, and an OpenAPI contract before any backend issue.
- Frontend: the Lovable import (`fab3dd3`, committed directly by the human) turned out to be a TanStack Start project with server-side rendering, because Lovable's default template changed on 13 May 2026. A second generator (Bolt) was tried and did not work out. The human approved the recommendation: keep the stack record's static single-page app and fix the output. #7 was re-scoped to review and record the import, and new issue #27 makes the build static and removes the Lovable coupling. Order is now #7, #27, #8, #9. Guidance, stack record note, roadmaps and `core-backlog.md` are updated on branch `docs-frontend-realignment`.
- Ponytail plumbing: #23 (pinned `ponytail-review` file and licence, path `_docs/vendor/ponytail/` as the human decided) is done and passed QA at 72e35df. #24 (metrics script, tests, `ponytail-metrics` target) passed QA at 8330f05 and the human merged it (4b04b84). #25 (read-only Reviewer role) passed re-check and the Heavy second QA launch at 4f33407. The role file is `_docs/team/reviewer.md`; pointers exist for Claude Code, OpenCode and Kiro.
- QA found real problems that were fixed: a missing Kiro agent file and answer (#25), shell allow-patterns on the OpenCode pointer and an open shell on the Claude Code pointer (#25, tightened), a missing generated-commit constant for the Lovable import (#24), and a date in the source record (#23, found by the trial reviewer run).

**What I learned:** a generator's default stack can change under a plan; the plan should check the template that came back, not assume it. Also, the first thing a Heavy issue needs is its decision record committed as a file, which I missed until QA time.

## Reflection

### Orchestrator

**What slowed you down (evidence):** `make issue-dump` failed in Kiro Web (it used `gh issue view`), which blocked the first QA launch on #25; the human replaced the recipe with the kit template's version in 7f5411e.
**What nearly went wrong or was blocked:** I parallelised dependent tool calls twice, so an index edit missed its commit and a hash was read before an edit landed; both were caught and redone.
**One proposed change (file, expected effect, measure):** `_docs/agent-kit/process.md` Lifecycle step 3: say the Engineer commits a Heavy issue's decision record file before the first QA launch. Expected effect: fewer Heavy QA FAILs for a missing file. Measure: QA FAILs on Heavy issues citing the decision record.

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- QA, #23: active time unknown, tool uses unknown
- QA, #25 first launch (blocked: issue dump failed): unknown, unknown
- QA, #25 first launch relaunched (FAIL, Kiro criterion): unknown, unknown
- QA, #25 re-check at 5fc032c (PASS): unknown, unknown
- QA, #25 second launch at 5fc032c (FAIL): unknown, unknown
- QA, #25 re-check at 4f33407 (PASS): unknown, unknown
- QA, #25 second launch at 4f33407 (PASS): unknown, unknown
- QA, #24 first launch at 7f5411e (FAIL, generated definition): unknown, unknown
- QA, #24 re-check at 8330f05 (PASS): unknown, unknown
- Reviewer trial run on 3f73bb0 (one finding, "fix it" declined, assert-clean PASS): unknown, unknown
- Tool and model for all launches: Kiro Web, model `auto` (as shown in the session); the QA and reviewer launches used the general-purpose sub-agent, not the project's role files.

## Files created or modified

- `_docs/vendor/ponytail/ponytail-review.md`, `_docs/vendor/ponytail/LICENSE`, `_docs/records/2026-11-06T0024Z-source-ponytail.md` (#23)
- `_docs/team/reviewer.md`, `.claude/agents/reviewer.md`, `.opencode/agents/reviewer.md`, `.kiro/agents/reviewer.json`, `_docs/decisions/2026-11-10T0822Z-reviewer-role.md`, `_docs/index.md` (#25)
- `scripts/ponytail_metrics.py`, `tests/test_ponytail_metrics.py`, `Makefile`, `AGENTS.md` (#24; the last two by the human)
- On `docs-frontend-realignment`: `_docs/planning/lovable-guidance.md`, `_docs/planning/core-backlog.md`, `_docs/planning/roadmap-1-core.md`, `_docs/planning/roadmap-2-ponytail-trial.md`, `_docs/decisions/20261105T133030Z-stack-choice.md`
- This file.

## Decisions made by the human

- Backlog order: contract first, with scoring before ingest and tests inside each issue (option a).
- Pinned file path: `_docs/vendor/ponytail/` (the better name, already decided in the human task).
- Frontend: keep Lovable, drop Bolt; fix the output to a static single-page app (spike on TanStack Start's single-page mode, then plain Vite); #7 re-scoped, #27 created.
- Protected files: approved the two Reviewer pointer files, then their tightening (no shell in either); the human added the `Makefile` target, the `AGENTS.md` bullet and the `issue-dump` fix to `main` themselves.
- #25: amend the Files list to include the Kiro agent file (option A), with a new hash.

## Mismatches with the spec or design docs

- Spec notes raised on #15 (the spec does not define "age" in the queue order) and #19 (the spec says only a Lead reads the audit trail); neither is decided.
- The old backlog drafts said `backend/`; the repo uses `socboard/` (decided in #10's grooming). `core-backlog.md` is marked superseded on the docs branch.

## Commands to validate

**Verify:** `make verify` (blocked here: `uv` cannot create its Python directory in the sandbox; the human's clean-clone runs passed: 1 test at 3d459e2 for #23/#25, 21 tests on the #24 branch).
**Decisions:** `make decisions`
**Trial metrics:** `make ponytail-metrics N=<issue>` (read-only).

## Proposed AGENTS.md changes

- Layout line to mention `frontend/` (from #7, not yet worked).

## Temporary changes

none. Scratch files under `.scratch/` are git-ignored and are removed with `make clean-scratch`.

## Interruptions

- The first QA launch on #25 stopped with no verdict because `make issue-dump` failed; nothing was left behind, and it was relaunched with the issue dumped by the kit's REST reader.
- The trial Reviewer run and every QA launch used a general sub-agent with no tool-level read-only setting; each was followed by `make assert-clean` (PASS).

## Unrelated problems noticed but not fixed

- `make kit-check` reports drift on several kit files and `.github/workflows/verify.yml` (also noted in the 2026-11-09T1226Z summary).
- Pull request #26 was opened on the #23 branch before the human asked for no PRs; it is still open.
- The OpenCode and Claude Code read checks of the vendored file are recorded "not tested" on #23.
- Decision record question: if the human wants a decision record file for each Heavy issue to be created at grooming, the PM role file should say so.

## Follow-ups for the next session

- Merge `issue-23-pinned-ponytail-review` (it is behind `main` by the #24 merge; no file overlaps), then post the Close comments for #23 and #25, and for #24 (merge commit 4b04b84), and run `make issue-close`.
- Merge `docs-frontend-realignment`.
- Work #7, then #27 (spike first), then #8; approve #9 onward one at a time as each predecessor nears done.
- Ponytail: settle process edits before the first baseline issue (decide-claude-code-layer and check-agent-commit-lines human tasks), record the epoch start, and run the shadow review after each baseline issue's QA PASS.
