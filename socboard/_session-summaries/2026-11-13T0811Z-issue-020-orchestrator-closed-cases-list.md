# Issue #20: Closed-cases list for Leads

**Date:** 2026-11-13T08:11Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Claude Code worked it in the local sandbox on `main` from `18022f7`, in parallel with #19 in Kiro Web (the human's one-time exception to `delivery-pace.md` item 4). Ponytail was on. Body hash `b86eba13…`, unchanged throughout; the claim-time check against decision records approved after grooming found no contradiction.

- **Route:** `socboard/cases.py` adds `GET /api/cases?status=Closed` (`getClosedCases`) under a `# Closed cases (#20)` block. Lead-only through the existing `require_lead` dependency (it came from #13, not #19, so neither issue added it; the hand-off was out of date on that), so 401 comes before 403 before the schema 422. One SELECT joins each closed case to the close time of its latest `status_changed` audit entry, with an explicit NULLs-last rule for a Closed case that has none. No column, no migration, no SQLite-only function, no write on the read.
- **Tests:** `tests/test_closed_cases_api.py` (new, 23 tests): order and id tie-break, open and claimed cases never listed, hostile text as stored, the refusals, read-only, one SELECT, contract match, and one test that closes two cases through the real transition route and follows each listed id to `GET /api/cases/{id}` and `GET /api/cases/{id}/audit` (the half of criterion 5 that waited for #19).
- **Round 1 (Engineer):** all criteria except the audit half of the fifth. **Merge:** after #19 merged (PR #118), `origin/main` was merged into `main` as `0b8538b`; the only conflict was in `socboard/cases.py`, resolved by keeping both route blocks under their headers. **Round 2:** the audit-trail test.
- **QA:** PASS at `0d5e2e5`, then at `590bf92`; `make assert-clean` passed after each.
- **Round 3 (Reviewer findings, approved):** the real-route test closes case 3 before case 1, so it fails if the list stops using the closing entry; the `startswith("Investigating -> Closed (")` condition is deleted (the close time is the latest `status_changed` entry, which holds while no reopen feature exists); the unused `close()` parameter is dropped; the one-SELECT test counts all SELECTs and asserts exactly 2. Finding 5 (paging) skipped.
- **Follow-up filed:** #120 (remove the dead test-only `GET /api/cases` route from `tests/backend_support.py`), placed in the supporting list before #22.
- **Closure and this summary:** the Claude Code session reached its usage limit while writing the documentation. With the human's ruling, the Kiro Web orchestrator closed #20 on 2026-11-13 at 07:39Z without this summary, so that #21 could proceed, and filed #125 to track the summary. The human pushed `main` up to the roadmap commit (`eac622e`; CI and `make verify` passed there). When the session resumed, it had already written this summary (committed after that push), posted its own `Orchestrator: Close` comment on the already-closed issue, and `make issue-close` refused ("the issue is not open"). That Close comment is therefore a duplicate of Kiro's, with the same facts plus the QA PASS and Verify lines; nothing else was closed or changed. This file satisfies #125's purpose; whether to close #125 is the human's call.

**What I learned:** a status check on a shared file is not enough for a parallel pair: the other session's note on #20 (and my own fetch) arrived while a QA launch ran. Do git fetch between launches, and read the other session's issue comment before the merge.

## Reflection

### PM

unknown (role not asked; the PM groomed #20 on 2026-11-09 and filed #120 in this session)

### Engineer

Engineer: final reflection on #20 (this round only; no first-hand record of the earlier rounds). QA has passed.

Reflection:
1. Slowest step was the full `make verify`: about 107 s of Python tests plus 37 s of frontend tests, for a two-file, 18-line change.
2. Nothing was blocked. The near miss: the one-SELECT test count had to be found by running it, since a guessed number could have hidden a per-case query. The first guess of 2 passed, so the assertion is exact.
3. Proposal: in `_docs/agent-kit/procedures/verify.md`, allow `make test-one` for the touched test files plus the frontend step skipped when no `frontend/` file changed. Expected effect: about 37 s saved on backend-only rounds. Measure it by comparing the verify duration on backend-only issues before and after.

Ponytail: reused the existing `close()` helper and `closed()` test helper and deleted code (the detail-text condition, the unused parameter) instead of adding any; no new test helper or dependency.

### QA

Reflection:
1. Slowed down: running mutation checks on a copy needed a pytest wrapper through `make test-one`, whose output hides subprocess results, so I wrote result files and ran it twice (plus a third script for one extra case); in this launch that was three script runs and one rewrite, since my tool set had no edit tool.
2. Nearly went wrong: my first mutation (reverting only the closes order) failed on correct code too, so it proved nothing alone; I added a run with the old order and old assertion to show the real blind spot.
3. Proposed change: add to `_docs/agent-kit/team/qa-engineer.md` one line saying a mutation check needs a clean-code run and a mutated-code run of the same test, and that a mutation script may write results to a `.scratch/` file. Expected effect: fewer reruns and no ambiguous mutation results. Measured by counting QA script runs per issue and mutation claims lacking a clean baseline, over the next five issues.

### Ponytail

Engineer: see the `Ponytail:` line above.

## Launch usage

Tool: Claude Code. Figures copied from the completion notifications; a resumed launch's figure may be cumulative or per-resume (unknown).

- Engineer round 1: 379 s, 46 tool uses.
- Engineer round 2 (audit-trail test, after the merge): 332 s, 21 tool uses.
- QA round 1 (PASS at `0d5e2e5`): 215 s, 18 tool uses.
- Reviewer: 34 s, 8 tool uses.
- Engineer round 3 (Reviewer findings): 356 s, 24 tool uses; final reflection resume: 141 s, 3 tool uses.
- QA round 2 (PASS at `590bf92`): 299 s, 27 tool uses; reflection resume: 327 s, 30 tool uses.
- PM, filing #120: 48 s, 17 tool uses.

## Files created or modified

`socboard/cases.py`, `tests/test_closed_cases_api.py` (new), `_docs/planning/roadmap-1-core.md` (#120 placed), the merge of `origin/main` (#19, PR #118) into `main`, this file. #54's work (`frontend/src/test/guardrails.test.ts`) ran alongside; see its own summary.

## Decisions made by the human

- Run #19 (Kiro) and #20 (Claude Code) in parallel, with the agreed shared names; build every criterion except the audit half first.
- Reviewer findings: applied 1 to 4 (finding 2 by deleting the condition), skipped 5; file the dead-route follow-up as an issue before #22 (not folded into #114); close #54 in parallel.
- Sequence: merge `origin/main` into `main` before closing, and add #20's deferred test then.
- After the usage limit: close #20 from Kiro without the summary so #21 can proceed (the human's ruling, recorded in the Kiro `Orchestrator: Close (#20)` comment and in #125), and push `main` to `eac622e` before the summary was committed.

## Mismatches with the spec or design docs

- The hand-off said `require_lead` would be added by #19; it already existed from #13. No code consequence.
- The generated parameter schema is `const: "Closed"` while the contract says `enum: [Closed]`: the same set, so no contract change is needed (the test accepts either form).

## Commands to validate

- **Verify:** `make verify` (PASS at `590bf92`: 1508 Python, 192 frontend, no weakened tests).

## Proposed AGENTS.md changes

none. (The Reflection proposals touch `_docs/agent-kit/` files; they are for the sweep.)

## Temporary changes

none. No processes started. `make clean-scratch` ran at the end of the session (after the summary text was final, with no process running); it covers the `.scratch/` files of #20 and #54, including the QA and Engineer scripts.

## Interruptions

The Claude Code session stopped at its usage limit after the roadmap commit and before this summary was committed. Left behind: a clean tree on `main` with #20's work and QA evidence committed, the Reflection comments already posted on #20 (the Engineer's and QA's), no running process, and no summary. It was checked on resume with `git status`, `git log` and the issue timeline: nothing was half-edited, and #20 had been closed by the Kiro Web orchestrator in the meantime.

## Unrelated problems noticed but not fixed

- Dead test-only `GET /api/cases` route in `tests/backend_support.py`: filed as #120.
- The list has no paging (out of scope in the issue; recorded as a known limit).
- The close time rests on a Closed case never getting a later `status_changed` entry; a reopen feature must revisit it. Not recorded in a decision record; flagged here.

## Follow-ups for the next session

- #125 (the deferred #20 summary): this file is that summary, committed on `main` after the human's push; the human decides whether to close #125 (it has no label and was not worked).
- #120 needs grooming (its mutation-check step must not leave a `socboard/` change; confirm independence from #114 and #110).
- After #20: #75, then #31, if the human allows them.
- #19's Reviewer and QA follow-ups are in its own summary (merged).
