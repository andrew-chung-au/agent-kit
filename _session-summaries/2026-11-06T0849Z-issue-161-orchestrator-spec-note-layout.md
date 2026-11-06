# Issue #161: Structured format for spec notes (added, changed, removed), with the human still approving

**Date:** 2026-11-06T08:49Z (UTC)
**Spec version:** none

## What changed and why

From the #14 research. `procedures/asking-the-human.md` gained a Spec note layout (Added; Changed with the old text; Removed with a reason; Why), optional for a one-line note; `team/pm.md`, `team/software-engineer.md` and the decision-point step in `process.md` link to it. `process.md` Planning says nothing merges into the spec automatically. ADR file `_docs/decisions/161-spec-note-layout.md` and index row; `tests/test_spec_note_layout.py`. Rebased onto `main` after #160 merged. Commits `e1d4d0c` (after rebase), `e5b198f`. PR #165, merge `0dd54f1`.

QA FAIL at `e1d4d0c`: the new section sat between the Decision question and its two closing paragraphs. Moved it to the end of the file; a test now pins the order. QA PASS at `e5b198f` (two launches). GitHub closed the issue on merge ("Closes #161").

## Reflection

### Orchestrator

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

none

## Files created or modified

- `agent-kit/procedures/asking-the-human.md`, `agent-kit/process.md`, `agent-kit/team/pm.md`, `agent-kit/team/software-engineer.md`
- `_docs/decisions/161-spec-note-layout.md` (new), `_docs/index.md`
- `tests/test_spec_note_layout.py` (new)

## Decisions made by the human

- Approved the issue and the Decision record (`05ccfbe9...`).
- Rebase after #160 merged and force-push (with a lease).

## Mismatches with the spec or design docs

none

## Commands to validate

**Test (all):** `make test` (1387 tests OK at `e5b198f`)

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

none

## Follow-ups for the next session

none
