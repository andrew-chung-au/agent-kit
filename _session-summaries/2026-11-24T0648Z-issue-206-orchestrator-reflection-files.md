# Issue #206: Write reflections to files and have the sweep read them

**Date:** 2026-11-24T06:48Z (UTC)
**Spec version:** none

Tier: heavy (from the PM proposal; no tier label).

## What changed and why

- **Grooming:** the PM groomed #206 together with #239 (Heavy). The human answered D-206-1 with A, A, A.
  - Each role writes a reflection file at the end of every launch.
  - The orchestrator appends it to `_docs/records/reflections/<issue>.md` and commits it.
  - The rule lives in `formats.md`.
- **Order:** the human asked for #206 to be built before #239 and #242.
- **Implementation:** the Engineer built C1 to C7.
  - `4ab57d9`: decision record.
  - `5672028`: tests.
  - `1a618a8`: kit, human-approved, with the blueprints row from D-206-3.
  - `773d143`: ledger answers.
- **Reflections:** the orchestrator appended three reflections under the new rule (`b213e9a`, `78d5a2b`, `e289b8d`).
- **QA:** both QA launches passed at `b213e9a` and `78d5a2b`. PR #243 merged as `3faa409`.
- **Also this session:** the PM filed #244 (the READMEs explain why the kit exists) and #245 (a reproducible headless run, parked). Both are placed in the order.

**What I learned:** the separate post-PASS reflection launch, skipped on #204, is gone. The first real use of the new rule produced three reflections at no extra launch cost.

## Reflection

`_docs/records/reflections/206.md`

## Launch usage

- Engineer, implementation: stopped on the usage limit before changing anything; active time unknown, tool uses unknown.
- Engineer, resumed implementation: 7947061 ms, 86 tool uses.
- Engineer, blueprints row and commits: 655432 ms, 25 tool uses.
- QA, first launch: stopped on the usage limit without posting; discarded; active time unknown, tool uses unknown.
- QA, first launch (fresh): 555787 ms, 70 tool uses.
- QA, Heavy second launch: 572792 ms, 62 tool uses.
- PM, filing #244: 342570 ms, 33 tool uses.
- PM, filing #245: 70956 ms, 6 tool uses.

## Files created or modified

- **Kit (`1a618a8`):**
  - `agent-kit/CHANGELOG.md`, `README.md`, `blueprints.md`
  - `procedures/formats.md`, `procedures/session-summary.md`, `procedures/sweep.md`
  - `process.md`
  - `templates/reflection.md` (new), `templates/session-summary.md`
- **Records:**
  - `_docs/decisions/206-reflection-files.md`, `_docs/index.md`
  - `_docs/records/decisions/206.jsonl`, `_docs/records/reflections/206.md`, `_docs/records/findings/206.json`
  - `_docs/planning/kit-1.11/issues/filed.md`
- **Tests:** `tests/test_reflection.py` (new), `tests/test_session_summary.py`, `tests/test_sweep.py`.

## Decisions made by the human

- D-206-1: A, A, A.
- D-206-2: approved with the stop (append nothing when the heading is already present).
- D-206-3: q1=A (the blueprints row), and the kit commit approved.
- Start #206 before #239. #239 was labelled at 21:25 UTC on 2026-11-23.
- D-244-1: a, a, a. #245 filed as the follow-up; content scanning for secrets left for later.

## Mismatches with the spec or design docs

none (the repo has no `_docs/specs.md`)

## Commands to validate

- **Verify:** `make verify`. It fails only on F-196-1 and F-198-3, which also fail on the base.
- `make decisions N=206` prints `none`.
- `make findings` accepts `_docs/records/findings/206.json`.

## Proposed AGENTS.md changes

none

## Temporary changes

none. `make clean-scratch` ran at the end.

## Interruptions

- **Engineer:** stopped on the usage limit before changing anything. Resumed after checking a clean tree and an unchanged HEAD.
- **First QA launch:** stopped on the usage limit without posting or changing anything. Its work was discarded, and QA was relaunched fresh.

## Unrelated problems noticed but not fixed

- Both READMEs say the pre-commit hook "refuses secrets". It matches file names only. #244's C8 corrects this.

## Follow-ups for the next session

- Next in the order: #239 (labelled), then #242 (unlabelled, not groomed).
- F-206-1 to F-206-5 are in the findings log. F-206-2 touches the same sweep step that #207 edits.
