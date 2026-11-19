# Issue #339: O0c Contract: a machine-readable copy of the names, with a test

**Date:** 2026-11-17T03:50Z (UTC)
**Spec version:** 9cf7ed3

Tier: Standard (from the PM proposal; no tier label). Kiro Web session (Rubric1).

## What changed and why

One Engineer launch built #339 (be243d7). It merged as PR #368 (`ba79e83`).
- `observability/contract.yaml` copies the names and values of `observability/CONTRACT.md`.
- `tests/test_observability_contract.py` parses both files and fails naming the first difference. It runs 25 mutations, and it also checks the alert rule file against the YAML.
- The canary list stays only in section 8 of `CONTRACT.md`, read by `tests/observability_support.py`.
- PyYAML was already locked, so no dependency was added.

The other lanes' tests can now read names from one file instead of copying them.

**What I learned:** none new.

## Reflection

### Engineer

**What slowed you down (evidence):** `tests/conftest.py` imports sqlalchemy, which the sandbox lacks, so the tests ran with `--noconftest`.
**What nearly went wrong or was blocked:** none.
**One proposed change (file, expected effect, measure):** none recorded.

### QA

**What slowed you down (evidence):** `test_promtool_passes` needs Docker, which the sandbox lacks; CI's observability run covers it.
**What nearly went wrong or was blocked:** none.
**One proposed change (file, expected effect, measure):** check table shape (duplicate headers, indented tables) as well as values (F-339-1, F-339-2).

## Launch usage

- Engineer: unknown (the tool did not report time or tool uses).
- QA: unknown.

## Files created or modified

- `observability/contract.yaml`, `tests/test_observability_contract.py`, `tests/observability_support.py` (PR #368)
- `_docs/records/findings/339.json`
- this file

## Decisions made by the human

- "go" for #339; merged PR #368.

## Mismatches with the spec or design docs

Four ambiguities in `CONTRACT.md`, listed in the Engineer comment on #339 (F-339-5). None blocks the work.

## Commands to validate

- **Verify:** CI-VERIFIED on be243d7: verify 44009537134, compose 44009537078, image 44009537127, observability 44009537024, postgres 44009537028 (pull request); push runs on the same commit also passed.
- **Assert clean:** not run.

## Proposed AGENTS.md changes

none

## Temporary changes

Packages in `.scratch/pylib` for the test runs; deleted.

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-339-1: tables with identical headers in one section keep only the last.
- F-339-2: an indented table is not seen.
- F-339-3: the Implemented-by columns, section 5 and the bullets are not machine-checked.
- F-339-4: the How-to-use test matches by substring.
- F-339-5: four contract ambiguities resolved by reading.

## Follow-ups for the next session

- The lanes can switch their hand-copied names to `observability/contract.yaml` in their own issues.
