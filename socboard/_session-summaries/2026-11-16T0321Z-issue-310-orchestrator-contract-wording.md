# Issue #310: O0a Observability contract: case id wording, operator-set values, log ids outside a span

**Date:** 2026-11-16T03:21Z (UTC)
**Spec version:** e3461a7

Tier: Standard (from the PM proposal; no tier label).

## What changed and why

`observability/CONTRACT.md` now calls the public case id an opaque string as the API returns it, marks `deployment.environment.name` and `service.version` as operator-set exceptions in section 1, the opening rules and section 9, and says `trace_id` and `span_id` are absent outside a span, matching approved #289. Source: QA's findings F-285-1 and F-285-2 on #285 and the PM's grooming. Commits 0fc63c1 and 16a5344 on `claude/310-contract-wording`, PR #315.

The first QA PASS at 0fc63c1 was voided by the orchestrator: the launch lacked the Medium stopping rule (`.kiro/steering/delivery-pace.md` item 7), and line 7 broke criterion 5 as written. One fix round (16a5344), then one fresh QA re-check of the changed lines: PASS, one Low finding.

This branch also carries this summary, `_docs/records/findings/310.json` and the roadmap 4 rows for #310 and #312 (item 2: one pull request per issue). Criterion 7 ("only `observability/CONTRACT.md`") was checked on the Engineer's commits; these three files are the orchestrator's records.

**What I learned:** the four `.kiro/steering/` files were not in this session's context until the human pointed to them; read them at session start.

## Reflection

### Engineer

**What slowed you down (evidence):** working out that `make verify` without an upstream needs `BASE=eea9398`.
**What nearly went wrong or was blocked:** new prose saying "every value" or `""` would have broken the refused case; grepped after editing. The fix-round comment cites lines 63-64 for the id rows, which are 64-65.
**One proposed change (file, expected effect, measure):** a `make` target that greps a file for a list of forbidden words, so refused-case checks need no raw `grep`.

### QA

**What slowed you down (evidence):** the first check could not tell what to do while CI was still running; it passed on the criteria and flagged the pending run.
**What nearly went wrong or was blocked:** the first check filed a criterion break (line 7) as a wording finding; the re-check read every "every/all/no" sentence in the file, not only the changed lines.
**One proposed change (file, expected effect, measure):** `_docs/agent-kit/team/qa-engineer.md` and `procedures/verify.md`: post PASS only after the stand-in CI run completes; measured by voided verdicts for a pending run (one here). This is the session's one proposal.

## Launch usage

- PM (grooming, two launches): unknown (the tool did not report time or tool uses).
- Engineer (implementation, fix round 1): unknown.
- QA (first check, re-check): unknown.

## Files created or modified

- `observability/CONTRACT.md`
- `_docs/planning/roadmap-4-devops.md` (rows for #310 and #312)
- `_docs/records/findings/310.json`
- this file

## Decisions made by the human

- Approved the PM's body for #310 with the trace_id conflict folded in, and Q1 option A (the character limit is #312).
- Labelled #310 `approved`; asked for `[groomed]` titles (already in `.kiro/steering/backlog-order.md`; #310 retitled).
- Set `LIGHT_ALLOWED` to `_session-summaries/*.md` and `_docs/records/*.md` (eea9398); the contract stays Standard with QA.
- Pointed out that a Medium-or-higher finding fails the verdict (delivery-pace item 7), which voided the first PASS.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify BASE=eea9398` (Tests and Lint cannot run in Kiro Web). CI-VERIFIED on 16a5344: verify run 43796795492, image 43796795485, compose 43796795459, postgres 43796795507, all success.
- **Assert clean:** passed after each QA launch (HEAD 0fc63c1, then 16a5344).

## Proposed AGENTS.md changes

none

## Temporary changes

none (no system change, process or large install).

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-310-1: The opening rule's list of values not derived from a request reads as complete but leaves out service.name, timestamp and logger (Low).
- F-310-2: The data-model decision record's "decimal strings" can mislead next to the contract's opaque case id.
- F-310-3: The QA role file does not say what to do while the stand-in CI run is still in progress.
- F-310-4: The orchestrator launched the first QA without the Medium stopping rule because the steering files were not in context.

## Follow-ups for the next session

- #312: groom after #289 merges; F-310-1 can ride on it, since it edits section 1 of the contract.
- A PM sweep is due (`make sweep-due`); F-310-3 and the QA proposal go to it.
- After the merge of #315: post the Close comment and run `make issue-close N=310`, then `make clean-scratch`.
