# Issue #160: Optional design section in the issue template for Standard issues with design choices

**Date:** 2026-11-06T08:49Z (UTC)
**Spec version:** none

## What changed and why

From the #14 research. `templates/task-template.md` gained an optional `## Design` section between Out of scope and Constraints ("none" is normal; Light issues leave it out; a Heavy choice still needs a Decision record). `team/pm.md` says when to fill it and links to the Heavy rule in Tiers instead of restating it. Section-order tests updated; ADR file `_docs/decisions/160-design-section.md` and index row. Rebased onto `main` after #159 merged (index-row conflict, both rows kept). Commits `760ca6c`, `299beb9`, `960b0c8` (after rebase). PR #164, merge `70387c8`.

QA FAIL at `26cb110` (the ADR file differed from the approved record by one bullet; pm.md paraphrased the Tiers row). QA PASS at `1794787`, `960b0c8` and `70387c8`. GitHub closed the issue on merge ("Closes #160").

**What I learned:** an ADR file "copied from the issue body" must be copied byte for byte; generate it from the body rather than retyping it.

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

- `agent-kit/templates/task-template.md`, `agent-kit/team/pm.md`
- `_docs/decisions/160-design-section.md` (new), `_docs/index.md`
- `tests/test_task_template.py`, `tests/test_issue_intake_form.py`

## Decisions made by the human

- Approved the issue and the Decision record (`7d881f7b...`).
- Restore the ADR bullet exactly; cut the pm.md paragraph to a link; rebase after #159 merged and force-push (with a lease).

## Mismatches with the spec or design docs

none

## Commands to validate

**Test (all):** `make test` (1380 tests OK at `960b0c8`)

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
