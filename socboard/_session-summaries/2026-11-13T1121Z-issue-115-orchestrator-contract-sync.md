# Issue #115: Bring openapi.yaml in line with the code

**Date:** 2026-11-13T11:21Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Kiro Web worked #115. Ponytail was on. PR: #134 (merged by the human at head `33e0502`), then a small follow-up PR for the by-hand check and this summary.

- **How it became ready:** the issue was unlabelled and ungroomed when the human asked for it. A PM launch drafted a grooming, and the same hour another Kiro session had committed an independent draft (PR #133, `_human-tasks/groom-handover-2026-11-13/groomed-115.md`). The human approved applying the committed draft with two text fixes (the trigger became "before #22 and Deploy"; the sentence that #21 "will read" the contract was dropped). The orchestrator applied the body, posted the PM comment with the new hash `8ff99f50…674b` and the `[groomed]` prefix, and the human added the `approved` label. The discarded PM draft differed only on item (c): it added a pointer to three `Order:` lines; the committed draft adds the reason in one place.
- **Claim-time check:** no decision record is newer than the grooming. The contract record (`2026-11-11T1511Z-openapi-contract.md`) rejected a schema `minLength` on `text`, not a `maxLength`. None of the six files the issue lists changed between the draft's baseline `8d2ee9e` and `main` at `d37a8f8`.
- **Change (one Engineer commit):**
  - `openapi.yaml`: a `422` with an `ApiError` body on `getCase`, `claimCase` and `getAudit`, through one new shared response `PathParameterValidationError` (it says the server does not return it today); `maxLength: 5000` on `NoteRequest.text` with a description of the code-point count and the order; a Refusals-table mention of a note over 5,000 characters; and the reason for the non-JSON order (FastAPI reads the body before the token dependency).
  - `socboard/schemas.py`: the note limit moved from a validator to `StringConstraints(max_length=NOTE_MAX_LENGTH)` ahead of `AfterValidator(_storable)`; `_note_text` removed (no other caller).
  - Four contract tests: the status-set assertions are now equalities, and `test_notes_contract.py` asserts `maxLength` is 5000 in both documents. Seven assertion lines were rewritten (CI: "7 added, 7 removed"), each listed with its replacement in the Engineer comment.
  - No behaviour changed.
- **CI:** green on the first push (runs 43414477189 and 43414453328): 1508 Python tests, 208 frontend tests, `VERIFY: PASS WITH WARNINGS` (the rewritten assertions). The Engineer could not run any test here and reasoned that the generated `NoteRequest` would equal the contract's; CI confirmed it.
- **QA:** PASS at `33e0502`, all nine criteria, nothing at Medium or higher. **Reviewer:** Ship, two Nice-to-have findings.
- **Not verified:** `make contract-check` has not been run by anyone (CI runs `make verify`, which does not call it; `uv` cannot run in Kiro Web). It is the human's, in `_human-tasks/2026-11-13T1116Z-human-task-115-orchestrator-run-contract-check.md`.

**What I learned:** my launch message to QA quoted criterion wording ("not by reusing `ValidationError`") from the discarded PM draft, not from the body that was applied. QA read the real body and said so. Copy criterion text from the applied body, never from a draft.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- PM (grooming draft, discarded in favour of PR #133's draft): active time unknown, tool uses unknown (Kiro Web gives neither).
- Engineer: active time unknown, tool uses unknown.
- QA: active time unknown, tool uses unknown.
- Reviewer: active time unknown, tool uses unknown.

## Files created or modified

- `openapi.yaml`, `socboard/schemas.py`, `tests/test_queue_contract.py`, `tests/test_claim_api.py`, `tests/test_audit_contract.py`, `tests/test_notes_contract.py` (PR #134; none protected).
- `_human-tasks/2026-11-13T1116Z-human-task-115-orchestrator-run-contract-check.md`
- This file.

## Decisions made by the human

- Approved applying the committed grooming draft with two text fixes; recorded #112 as separate and merging after #115, kept item (c) as a one-place reason, and left the closed-cases list order as a separate follow-up (not filed).
- Added the `approved` label.
- Merged PR #134 without answering the decision point. The orchestrator took the recommendations as the default and says so here: Reviewer finding 1 (a duplicate assertion) not applied; finding 2 (no test for an over-limit note on an unknown case id) parked; the shared `PathParameterValidationError` component accepted (QA Low). No follow-up issue was filed for finding 2.

## Mismatches with the spec or design docs

none.

## Commands to validate

- **Verify:** `make verify` (CI; green on `33e0502`).
- **Contract check:** `make contract-check` (not yet run; see the human-task file above).

## Proposed AGENTS.md changes

none.

## Temporary changes

none. No server was started. `make clean-scratch` ran.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- No test posts an over-limit note to an unknown case id to pin "limit before the 404" (QA Low; Reviewer 2). It belongs in `tests/test_notes_api.py`, outside this issue's Files list. Unfiled.
- Reviewer 1: `tests/test_notes_contract.py` repeats a `maxLength` assertion that the line after it already proves.

## Follow-ups for the next session

1. Run `make contract-check` (the human-task file).
2. Groom #112 after this merge: it adds `"503"` to the same status sets, so it must merge after #115. Its draft is in `_human-tasks/groom-handover-2026-11-13/`.
3. Decide whether the PM files the follow-up for the unknown-id note test.
