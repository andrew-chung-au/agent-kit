# Issue #159: Planning guidance: testable requirement wording, a plan review checklist, and one intent per issue

**Date:** 2026-11-06T08:49Z (UTC)
**Spec version:** none

## What changed and why

From the #14 research. `procedures/planning.md` gained one EARS example (other testable forms are fine) and a seven-line Plan review; `team/pm.md` Definition of done gained the one-intent rule, its enforcement (an issue with two unrelated intents is returned to the PM; the human reading the groomed issue enforces it) and a link to the review. ADR file `_docs/decisions/159-planning-guidance.md` and index row; tests. Commits `cb5262e`, `5764864`, `6ec1a40`. PR #163, merge `42f2b2d`.

QA FAIL at `cb5262e`: the committed ADR differed from the approved record by one bullet. The human then edited the Decision record (word ceiling 400 to 500, keep checkboxes and the homes sentence); new body hash `0ba47de3...bd451`, approved on the issue. QA PASS at `6ec1a40` and `42f2b2d` (two launches). GitHub closed the issue on merge ("Closes #159").

**What I learned:** an approval posted on the PR is not seen; it has to be on the issue. Give the issue link with every approval comment asked for.

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

- `agent-kit/procedures/planning.md`, `agent-kit/team/pm.md`
- `_docs/decisions/159-planning-guidance.md` (new), `_docs/index.md`
- `tests/test_planning_gate.py`

## Decisions made by the human

- Approved the issue and its Decision record (twice: `8a98522a...` then, after the human's edit, `0ba47de3...`).
- Raised the `planning.md` word ceiling to 500 and kept the checkboxes and the roadmap, ADR and issue homes sentence.

## Mismatches with the spec or design docs

none

## Commands to validate

**Test (all):** `make test` (1378 tests OK at `6ec1a40`)

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- I used `sed -i` twice on this branch, which `AGENTS.md` forbids; tests checked the results.

## Follow-ups for the next session

none
