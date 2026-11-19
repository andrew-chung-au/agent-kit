# Issue #12: Rule-based severity scoring and seeded asset inventory

**Date:** 2026-11-12T21:28Z (UTC)
**Spec version:** see `git log -1 --format=%h -- _docs/specs.md` (not changed by this issue)

## What changed and why

Standard tier. The Engineer added `socboard/scoring.py` (a pure `score()` over the approved 12-row table, exact rule strings, Medium defaults), `socboard/inventory.py` (`criticality_for_asset`, exact match), `socboard/seed.py` (10 synthetic assets, inserts only missing names, exit 2 on a bad URL, exit 1 with fixed text on an unmigrated database), tests for each, and the README "Severity rules" section. The `Makefile` `seed` target and the `AGENTS.md` "Seed" line are staged and wait for the human's approval (protected files).

**What I learned:** `make seed` and `make migrate` run in parallel on the same new file race; run them in order.

## Reflection

### Engineer

**What slowed you down (evidence):** unknown (role not asked)
**What nearly went wrong or was blocked:** unknown (role not asked)
**One proposed change (file, expected effect, measure):** unknown (role not asked)

## Launch usage

Engineer: unknown (figures not available to this launch)

## Files created or modified

`socboard/scoring.py`, `socboard/inventory.py`, `socboard/seed.py`, `tests/test_scoring.py`, `tests/test_inventory.py`, `README.md`; staged, not committed: `Makefile`, `AGENTS.md`.

## Decisions made by the human

none during this launch (the table and exact matching were approved with the issue).

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (PASS)
- **Contract check:** `make contract-check` (OK)
- **Seed:** `make seed SOCBOARD_DATABASE_URL=<temporary url>` after `make migrate`, twice

## Proposed AGENTS.md changes

The "Seed" line in Commands and the `seed` Makefile target (staged; see the issue comment).

## Temporary changes

Scratch database `.scratch/i12.db` and `.scratch/issue-12*` files; remove with `make clean-scratch`. No process started, no system change.

## Interruptions

none

## Unrelated problems noticed but not fixed

`make verify` lists unrelated unpushed changes since origin/main (the #59 commits), which are not part of this issue.

## Follow-ups for the next session

Commit the staged `Makefile` and `AGENTS.md` after approval. #14 calls `criticality_for_asset`, then `score`.
