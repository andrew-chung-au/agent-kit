# Issue #18: Case notes

**Date:** 2026-11-13T04:10Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Kiro Web worked #18 alongside Claude Code's #16, a one-time human exception to `delivery-pace.md` item 4. #18 depends only on #15, #13 and #11. Ponytail was on (fifth Kiro issue in the ponytail group). PRs: #111 (merged) and #113 (the follow-up).

- **New route:** `POST /api/cases/{id}/notes` in `socboard/cases.py`, under a `# Notes (#18)` block.
  - Checks run in the contract's order: 401, schema 422, 404, 409 `case_closed`, then 422 `empty_note`. Whitespace-only text is empty; text over 5,000 characters gets 422 from a validator, because the contract has no `maxLength`.
  - Text is stored raw.
  - One `note_added` audit entry is written through `append_audit`. It names the note id, never the text. A refused note writes nothing. Everything happens in one transaction.
- **Supporting code:** `NoteRequest` in `socboard/schemas.py`; `CASE_CLOSED` and `EMPTY_NOTE` in `socboard/errors.py`.
- **Tests:** `tests/test_notes_api.py` and `tests/test_notes_contract.py`.
- **CI and QA at `7709890`:** CI 1380 passed, VERIFY: PASS, and QA PASS.
- **Merge with #16:** #16 merged first. The Engineer resolved the `cases.py` conflict (`4f0b878`): imports merged, the duplicate `CASE_CLOSED` removed, and #18's message renamed to `NOTE_CASE_CLOSED_MESSAGE` so #16's 409 text is unchanged. CI 1398 passed.
- **Early merge:** the human merged PR #111 at `4f0b878` before its QA re-check. The approved finding 18-2 therefore went into a second PR, #113 (`7433303`): `_storable` now refuses a NUL character as 422, which covers note text and all ingest text, because Postgres rejects NUL. CI 1400 passed.
- **QA re-check:** PASS at `7433303`, covering both the merge and 18-2.
  - The claim route is structurally identical to #16's (AST compare).
  - Only U+0000 changed outcome, across all 1,114,112 code points.

**What I learned:** two Core issues on the same files in parallel cost one conflict round. Keeping each issue's code in a labelled block, and telling the other session the shared constant name in advance, kept the conflict small.

## Reflection

### PM

unknown (role not asked)

### Engineer

From the completion comment, unchanged:

- The 5,000 limit has no home in the contract; a validator kept the comparison green, but the contract should state it.
- FastAPI's body-before-dependency order means "401 first" is only true for valid JSON; worth a line in the contract's order notes.
- Nothing ran, so the tests are unproven until CI.

### QA

unknown (no Reflection block in QA's comments).

### Ponytail

Engineer: "One route in the existing `cases.py`, one request model, two error codes; no helper, no new module, no migration." The Reviewer still found about 30 lines that could go, and one real defect: the NUL 500 (18-2), which was applied.

## Launch usage

Active time and tool uses are unknown, because Kiro Web reports neither. Tool: Kiro; model: unknown. Launches: Engineer 3 (implementation, merge resolution, 18-2); QA 2 (PASS, then PASS on re-check); Reviewer 2 (the first answered an unrelated message mid-run and was discarded).

## Files created or modified

- `socboard/cases.py`, `socboard/schemas.py`, `socboard/errors.py`
- `tests/test_notes_api.py` (new), `tests/test_notes_contract.py` (new), `tests/test_ingest_api.py` (one new test)
- `_docs/planning/roadmap-1-core.md` (#18's findings on #110)
- this file

## Decisions made by the human

- #18 runs in parallel with #16, as a one-time exception to delivery-pace item 4.
- Reviewer findings:
  - Finding 18-1: correct-minor, moved to #110.
  - Finding 18-2: useful, applied in PR #113.
  - Finding 18-3: useful. QA also raised it. Recorded for #17's close transition; the notice is on #17.
  - Finding 18-4: correct-minor, moved to #110.
  - Finding 18-5: useful, moved to #110.
  - Finding 18-6: correct-minor, not applied.
  - Finding 18-7: correct-minor, moved to #110.
- QA risks accepted:
  - A note made only of a zero-width space is accepted, because `str.strip()` keeps it.
  - Over-limit text gets the generic `validation_error`.
- PR #111 was merged before the re-check (by accident). The re-check then covered the merged code together with #113.

## Mismatches with the spec or design docs

- The 5,000-character note limit is not in `openapi.yaml` (`NoteRequest.text` has no `maxLength`). A later contract issue should add it.

## Commands to validate

- **Verify:** `make verify` (CI runs 43358635955 at `7709890`, 43361820732 at `4f0b878`, and 43363017767 at `7433303`).

## Proposed AGENTS.md changes

none.

## Temporary changes

none. `make clean-scratch` runs at the end of this session.

## Interruptions

- The first Reviewer launch answered a mid-run message about #16 instead of reviewing #18. It was discarded and the Reviewer relaunched.

## Unrelated problems noticed but not fixed

- `LoginRequest` does not go through `_storable`, so a NUL in a username or password may give a 500 on Postgres instead of 401. QA reasoned this; it was not run. Candidate for #104 or #110.

## Follow-ups for the next session

- #17 (Claude Code): merge `main` again after #113. Lock the case row on close, or record the note race (18-3).
- #110 now carries findings from #14, #15 and #18.
- Sweep 5 and the ponytail comparison are due (Claude's #16 decision point).
