# Issue #312: O4a Limit the two operator-set resource attributes

**Date:** 2026-11-17T03:24Z (UTC)
**Spec version:** 9cf7ed3

Tier: Standard (from the PM proposal; no tier label). Session: Rubric2. Rubric: none directly; it hardens the Observability point's "no customer data" clause.

## What changed and why

`socboard/telemetry.py`: in the resource-attribute set-up only, `deployment.environment.name` and `service.version` from `OTEL_RESOURCE_ATTRIBUTES` are used only when they are 1 to 64 ASCII characters of `A-Z a-z 0-9 . - _ +` (after percent-decoding); a refused value is treated as missing, with #289's once-only warning naming the attribute and never the value. `tests/test_telemetry.py` covers the accepted and refused cases. `observability/CONTRACT.md`: the limit bullet in section 1, and the F-310-1 rewording of the first rule and section 9 (the two operator-set values are examples, not the whole set). Commits 544c5a9, c7b3b94; PR #364.

The maintainer ruled the code scope: resource attributes only, because Rubric1's #291 edits the same file (queue read and its histogram). QA PASS on the first check, Low findings only.

**What I learned:** check every producer of a value (the app, the probe, the emitter), not only the module the issue names (F-312-3).

## Reflection

### Engineer

**What slowed you down (evidence):** no test could run in the sandbox.
**What nearly went wrong or was blocked:** nothing; the existing warning already did the reporting.
**One proposed change (file, expected effect, measure):** check early whether `uv` works in the sandbox and say so at once.

### QA

**What slowed you down (evidence):** the probe and emitter paths could not run.
**What nearly went wrong or was blocked:** nothing.
**One proposed change (file, expected effect, measure):** at the start of a check, list every producer of the value the issue limits; measured by findings like F-312-3. The session's one proposal.

## Launch usage

- Engineer: unknown (the tool did not report time or tool uses).
- QA: unknown.

## Files created or modified

- `socboard/telemetry.py` (resource set-up only)
- `tests/test_telemetry.py`
- `observability/CONTRACT.md`
- `_docs/records/findings/312.json`
- this file

## Decisions made by the human

- Keep #312's code to the resource attributes in `socboard/telemetry.py`; Rubric1 owns the queue read (#291) and #339.
- Earlier: option B for the sentence, one issue, the 1 to 64 ASCII limit.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** CI-VERIFIED on c7b3b94: verify run 44007017959 (`VERIFY: PASS`, 3860 passed), image 44007017999, compose 44007018030, postgres 44007017898, observability 44007017813, all success.
- **Assert clean:** passed after QA.

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-312-1: Surrounding whitespace is stripped before the check, untested (Low).
- F-312-2: Duplicate keys and commas in values are untested (Low).
- F-312-3: The probe and emitter read OTEL_RESOURCE_ATTRIBUTES without the limit (Low).
- F-312-4: The warning does not say whether the value was refused or missing (Low).

## Follow-ups for the next session

- After the merge of #364: check the merged head, post the Close comment, run `make issue-close N=312`. If #291 merges first, merge `main` into this branch before the merge.
