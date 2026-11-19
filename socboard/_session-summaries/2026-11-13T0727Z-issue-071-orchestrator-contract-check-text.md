# Issue #71: Fix the make contract-check help and usage text

**Date:** 2026-11-13T07:27Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Kiro Web worked #71 as the second of four issues in one `Makefile` sitting (#73, #71, #80, #75; the human's order). Ponytail was on. PR: #124 (draft). The branch started from `main` at `593edfd`, which already held #73's `Makefile` change, so the `contract-check` lines had moved from 141 and 142 to 146 and 147.

- **Claim-time check:** the five decision records dated after grooming (data model, auth tokens, ponytail adopt, ingest key, close floor) say nothing about `contract-check`. No conflict.
- **Change:** two lines of `Makefile`, the `contract-check:` help line and its `$(error ...)` usage text.
  - Help: "Validate openapi.yaml against the OpenAPI version it declares (3.1); fails on an invalid file: make contract-check [FILE=<path>]", the same wording as the `AGENTS.md` Contract check line.
  - Usage: the PM's option 1, which names each rule in words and ends on "(..)" instead of "no ..".
  - No accepted input behaves differently; `AGENTS.md` and the kit template are unchanged (`contract-check` is project-only).
- **Approval:** the human approved the exact `Makefile` diff in this session; the commit used `HUMAN_APPROVED=1`. The PM's other two questions fell to their defaults: the 3.1 pin stays unfiled, and the Epoch statement (no move) stands.
- **CI:** green on the code commit (runs 43382999298 and 43382986038). QA PASS at `58e8595` with no finding at Medium or higher. The Reviewer said "Ship".
- **Not verified:** the behaviour-unchanged criterion (valid file, `FILE=openapi.yaml`, missing file) needs `uv`, which cannot run in Kiro Web. It is in `_human-tasks/2026-11-13T0700Z-human-task-071-engineer-check-contract-check.md` for the human's dev container.

**What I learned:** committing the Engineer's untracked human-task file before QA keeps `make assert-clean` meaningful, because it counts untracked files.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- Engineer: active time unknown, tool uses unknown (Kiro Web gives neither).
- QA: active time unknown, tool uses unknown.
- Reviewer: active time unknown, tool uses unknown.

## Files created or modified

- `Makefile` (protected; approved diff: 2 insertions, 2 deletions).
- `_human-tasks/2026-11-13T0700Z-human-task-071-engineer-check-contract-check.md`
- This file.

## Decisions made by the human

- Approved the exact `Makefile` diff as shown.
- Decision point: apply neither Reviewer finding. Finding 1 (the sibling targets `kit-compare`, `kit-baseline` and `kit-feedback` keep the old "no .." wording) is parked; finding 2 ("(3.1)" in three places) needs no action.
- `make sweep-due` says due. The human chose to run the sweep after #75, at the end of this sitting.

## Mismatches with the spec or design docs

none.

## Commands to validate

- **Verify:** `make verify` (CI on the branch; green on the code commit).
- **Contract check:** `make contract-check`; the by-hand cases are in the human-task file above.

## Proposed AGENTS.md changes

none.

## Temporary changes

none. `make clean-scratch` ran.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- Reviewer finding 1: three sibling targets keep the old usage wording; a small issue only if the human wants it.

## Follow-ups for the next session

1. After the human merges #71 and the Close is posted, start #80 from the latest `main`, with a hash check first, and write its `_human-tasks/` file for the human's start and stop checks.
2. Run the sweep after #75 (human's choice).
3. The by-hand checks for #71 and #73 are open until the human runs them.
