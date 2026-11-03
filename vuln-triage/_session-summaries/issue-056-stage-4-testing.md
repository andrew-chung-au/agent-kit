# Issue #56: Stage 4 test strategy (`_docs/testing.md`)

**Date:** 2026-10-22
**Spec version:** 97893c1

## What changed and why

- Added `_docs/testing.md` (385 lines): the Stage 4 test strategy for unit, real-Postgres Compose integration with stored fixtures, API-driven Compose E2E, LLM brief evaluation, the rejected-brief path, malicious-advisory security tests, US-13 telemetry, US-14 alerting, US-15 responder and the light CI security scan. It includes a US-1..US-16 / E1..E12 traceability matrix, a limits/refused-cases table, and the three #43 leftovers (`A-TIER`, `A-GAP`, `A-RESOLVE`).
- Linked the document from the README planning-documents list and ticked only the two Stage 4 rows in issue #9.
- The issue was worked on branch `claude/issue-056-stage-4-testing`, rebased onto the merged #50/#58 work before close-out. It was not committed to `main`.
- Deferred four spec notes to #63 rather than editing protected docs during the active parallel sessions.

## Files created or modified

- Engineer `8d9db69`, `2430912`: `_docs/testing.md` (new), `README.md`.
- Close-out: `_docs/roadmap.md` (step 10 row, #43 leftover line, one check-in line), `_docs/ai-usage-log.md` (one entry), this summary.
- GitHub: #56 comments 6329411066 (PM grooming), 6329460170 (PM body-edit note), 6329735908 (Engineer), 6329945929 (QA PASS), 6330289999 (QA re-check PASS at `ae0d55d`); #9 body (two Stage 4 rows); #63 created.
- No application, test, fixture, Compose, CI, Makefile, OpenAPI, `api.md`, spec or architecture file changed. No protected commit.

## Decisions made by the human

- D1 (from grooming): option 1, count firing episodes only. One firing notification = one alert; a Grafana "resolved" message is the same instance's resolution, not a second alert. The test asserts exactly one firing and at most one resolved notification.
- Move the work to its own branch, rebase on the merged #50/#58 sessions, and check for conflicts; push only that branch.
- Defer the four spec notes to one follow-up issue (filed as #63) instead of protected edits now.
- QA's two outside-criteria risks are note only: the `make verify` BASE gap on a branch with no upstream, and the scan tools' live advisory-data source.

## Mismatches with the spec or design docs

- `NotificationJob` has no `tier` field, although the US-14 gauge's `tier` label is the creation tier. The test is written (`A-TIER`) but the model gap is #63 note 1.
- The US-13 metric has no trace-id carrier; `testing.md` uses an OTel exemplar as `ASSUMPTION: T-A4` (`VERIFY:`), and #63 note 2 proposes the wording.
- US-14 lacks the "one firing episode" sentence that matches D1; #63 note 3 proposes it.
- Architecture A35 does not say how the demo defect is removed; #63 note 4 proposes the wording.
- The merged #58 work added the "traceparent is always set" rule; `testing.md` is consistent with it (`T-JOURNEY`, `I-JOBS`).

## Commands to validate

- **Test:** `make test`: 62 passed, 0 failed (3 vitest files; the planned backend layers do not exist yet).
- **Verify:** `make verify`: PASS; also `make verify BASE=origin/main` on the branch (no upstream).
- **Assert clean:** `make assert-clean`: PASS at `2430912` after the first QA and at `ae0d55d` after the re-check.
- **OpenAPI:** `make openapi-validate`: not needed; the contract was not edited.
- **Document checks:** `make issue-dump N=9` plus the Engineer's read-only `.scratch/verify_issue9.py`; `grep -n "VERIFY:" _docs/testing.md`.

## Proposed AGENTS.md changes

- none.

## Temporary changes

- None to the system or installed packages. No processes were started.
- Local `main` was moved back to `origin/main` (`9a03ba9`) after the Engineer's commits; the commits were kept on `claude/issue-056-stage-4-testing`. No work was lost.
- `make clean-scratch` was not run: `.scratch/` is shared with the paused #50/#58 sessions and contains files this session did not create. Only the branch's own commits and `.scratch/` files for #56 were touched.
- The branch is local only: the requested `git push -u origin claude/issue-056-stage-4-testing` was denied by the project's `git push*` rule, so the human pushes it from the clean clone.

## Permission review

PM, Engineer and QA each listed their approvals and ask-rule commands in their #56 comments; the orchestrator's own actions are included below.

- Read-only (propose allowing): PM's read-only `gh api` loop for issue titles (matched `gh api*` ask rule); `make issue-dump N=9/50/56` reads; the Engineer's and QA's git/log/diff reads and `.scratch/` doc checks; the orchestrator's `git fetch`, `git log`, `git rebase`, `make assert-clean`.
- Writes to the record (keep asking): PM `gh api -X PATCH` on the #56 body (ask rule; orchestrator-requested); Engineer `gh api -X PATCH` on the #9 body (ask rule); PM `gh issue create` for #63 (issue-creation rule); `make issue-comment`/`make issue-dump` issue writes (allowed targets).
- Risky (propose denying): `git push -u origin claude/issue-056-stage-4-testing` (matched the `git push*` deny rule; the agent did not pursue another way and left the push to the human).
- Proposed `opencode.json` and `.claude/settings.json` changes: none.

## Interruptions

- none.

## Unrelated problems noticed but not fixed

- Plain `make verify` on a branch with no upstream defaults to `HEAD` as its base, so the weakened-test check misses committed changes; `make verify BASE=origin/main` passed. This is the verify-gate gap already tracked by #53 (note only, per the human).
- `C-SCAN` does not say where `pip-audit`/`npm audit` get advisory data; those tools normally use live services, which needs settling with the no-live-feed rule when the scan is built (Stage 5). Noted only.
- #9 has no issue-body history API; the "only two rows changed" check relied on the Engineer's pre-edit `.scratch/` snapshot and a byte-for-byte comparison of the live body.
- The planned targets and tools (`test-integration`, `test-compose`, `test-e2e`, `test-brief-eval`, `security-scan`, Mailpit, `pip-audit`/`npm audit`) do not exist yet; they are Stage 5/backlog work and need dependency approval when built.
- `A-GAP` and `T-JOURNEY` depend on Grafana/OTel behaviour marked `VERIFY:`; if the semantics differ, those test designs need revision.
- The four deferred spec notes are #63.
- The #50 and #58 sessions were merged before this close-out; the branch rebased cleanly, with no overlap in `README.md` or `_docs/testing.md`.

## Follow-ups for the next session

- Step 11 (Stage 5 `_docs/tasks.md`) is unblocked once #56 is closed.
- #63 (four Stage 4 spec notes) needs the human's scheduling and, for each, a protected-doc decision.
- Push, review and merge the local `claude/issue-056-stage-4-testing` branch (the agent's `git push` is denied by the permission rule); the diff is `README.md`, `_docs/testing.md`, `_docs/roadmap.md`, `_docs/ai-usage-log.md` and this summary.
