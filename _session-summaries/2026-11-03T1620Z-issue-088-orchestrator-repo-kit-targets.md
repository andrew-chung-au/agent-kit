# Issue #88: kit-check and kit-compare targets in this repo's Makefile

**Date:** 2026-11-03T16:20Z (UTC)
**Spec version:** none

## What changed and why

`make kit-check` and `make kit-compare OTHER=.scratch/<folder>` failed here with "No rule to make target", because they existed only in `agent-kit/templates/Makefile.mk`. The repo `Makefile` now carries both, with the template's help text and validators, differing only in the script path (`agent-kit/scripts/`). `kit-compare` checks `$(value OTHER)` before anything runs and passes `"$$OTHER"` to the script. `KitTargetsTest` runs the real Makefile (and the template) against recording stubs with 25 crafted values; a drift test compares the repo and template validators, and one changed character fails it by name. Tier: standard. Built on branch `issue-088-repo-kit-targets`.

**What I learned:** two older tests asserted that the repo Makefile never names `kit-check` or `kit-compare`; they had to be narrowed (no Makefile line outside the two kit targets may name them), which the issue's one-test-file constraint did not foresee.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- Engineer work: orchestrator session (no separate launch).
- QA (fresh subagent): active time and tool uses unknown (not given by the tool).

## Files created or modified

- `Makefile` (protected).
- `tests/test_make_variables.py` (extended; `block()` also matches `name :=`).
- `tests/test_kit_compare.py`, `tests/test_kit_manifest.py` (narrowed assertions; outside the issue's file constraint).

## Decisions made by the human

- Commit the protected files with `HUMAN_APPROVED=1`: approved.
- Narrowing the two older tests beyond the issue's one-test-file constraint: approved (recommended).
- Push the branch and open a pull request that says `Refs #88`: approved.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`. 891 tests passed. QA crafted-value run: 48 command-line values and 3 environment values refused with no marker and no stub run. `make kit-check` exits 2 in this repo ("no manifest") because the kit's own repo ships no `MANIFEST.sha256`; it no longer fails with "No rule".

## Proposed AGENTS.md changes

none

## Temporary changes

Worktrees `.scratch/wt-88`, `.scratch/wt-77`, `.scratch/wt-21` and `.scratch/wt-2` held the four branches' work; they are git-ignored and removed by `make clean-scratch`. One throwaway copy of the Makefile was made in `/tmp` and deleted at once (outside the folder; not needed).

## Interruptions

none. `make issue-hash` could not run (GraphQL-backed `gh` fails in this sandbox); the same hash check was done over the REST API and matched the recorded hash.

## Unrelated problems noticed but not fixed

- `make kit-check` exits 2 here (no manifest); correct, but it may surprise someone following `kit-import.md`.
- The narrowed tests no longer cover a gate recipe separated by a blank line; QA's stronger line-level check was applied after.

## Follow-ups for the next session

- Close #88 after the pull request is merged (orchestrator only).
- #72 (pairing-rule test for every target) is unaffected.
