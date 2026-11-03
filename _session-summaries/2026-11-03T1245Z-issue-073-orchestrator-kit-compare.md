# Issue #73: `make kit-compare`, a read-only two-way kit file list

**Date:** 2026-11-03T12:45Z (UTC)
**Spec version:** none

## What changed and why

The kit import procedure (#70) has the agent compare a project's kit with a newer one file by file. #73 adds `agent-kit/scripts/kit-compare.py` and `make kit-compare OTHER=.scratch/<folder>` (in `templates/Makefile.mk`): a read-only list in the `kit-check` vocabulary (`unchanged`, `modified`, `added`, `missing`) and a summary line, so the agent reads a list instead of comparing by hand. It reuses the `kit-manifest.py` scan and `kit-check.py`'s conf reader, writes nothing and decides nothing. The other folder must be a plain relative path under `.scratch/`, checked in make and again in the script. Built by Kiro as PR #82, merged as bbeeae7.

**What I learned:** the PM first proposed heavy tier; the human set `tier:standard`, since the change is one read-only script and one target, the same shape as `kit-check` in #69.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- PM (recorded the #70 decision, filed #73): 92.7 s active, 22 tool uses.
- PM (#77 grooming and the #73 tier comment): 56.5 s, 15 tool uses.
- QA: 678.5 s, 83684 tokens, 32 tool uses.
- Engineer (Kiro, outside this session's launches): unknown.

## Files created or modified

- `agent-kit/scripts/kit-compare.py` (new), `agent-kit/templates/Makefile.mk`, `agent-kit/blueprints.md`, `agent-kit/README.md`, `agent-kit/procedures/kit-import.md`.
- `tests/test_kit_compare.py` (new, 45 tests).

## Decisions made by the human

- Two-way list only; no three-state classification.
- Tier standard (the human added the `tier:standard` label).
- The human merged PR #82.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`. QA ran `make test` on an export of the branch: 786 tests, passed. Mutation checks: 30 mutations of `kit-compare.py` and `Makefile.mk`; 27 caught, 2 survived as equivalent mutants (other checks refuse the same input), 1 not applicable.

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- A file name with U+2028 or a bidi override prints as-is, because the shared scan refuses only ASCII control characters (`kit-check` behaves the same): filed as #87.
- This repo's `Makefile` has no `kit-check` or `kit-compare` target: filed as #88.
- Through make, "differences found" exits 2, the same code as an error; the summary line tells them apart. Not changed.

## Follow-ups for the next session

- #87 and #88 (unlabelled; the human approves them).
- Proposed unreleased changelog line, the human's call with the version: "Added `make kit-compare OTHER=.scratch/<folder>`, a read-only list of how the kit differs from another kit copy."
