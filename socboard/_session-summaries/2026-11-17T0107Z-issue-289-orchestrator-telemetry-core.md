# Issue #289: O4 Telemetry core

**Date:** 2026-11-17T01:07Z (UTC)
**Spec version:** 9cf7ed3

Tier: Standard (from the PM proposal; no tier label). Rubric: Observability, critical path to 2 points (`.kiro/steering/rubric-priority.md`). Track A of roadmap 4 (lane split proposed by Terraform lane A, 2026-11-17).

## What changed and why

`socboard/telemetry.py` (new) sets up traces, metrics and JSON logs from the environment, off unless `OTEL_EXPORTER_OTLP_ENDPOINT` is set: resource attributes per the contract, an always-on sampler, JSON log lines with the contract's fields, OTLP log export on the `socboard` logger tree only through a scrubbing subclass of the SDK's handler (message template only, no arguments or extras, exception type only), providers held in the module (none installed process-wide), and flush and shutdown at the lifespan's end. `socboard/app.py` gains the set-up call and the shutdown call. `tests/test_telemetry.py` uses in-memory exporters. Commits 8070ab4, 4f44f14, 6e7a2fa (a fake exporter lacked `force_flush`, found by CI before QA), 35ded73 (fix round). PR #354.

The body was changed before claiming, after the human confirmed the PM's proposal (logs over OTLP, sampler, flush; hash 3f8e864).

First QA (a relaunch: the first QA launch stopped because it read the relayed lane message as its own prior work) FAILED with one Medium: the unreachable-collector test could not tell a synchronous log export from a batched one. One fix round added a test that fails with `SimpleLogRecordProcessor`; one fresh QA re-check of the changed lines: PASS, Low findings only.

**What I learned:** a human message relayed to every subagent can trip QA's independence check; the launch message now says it is not evidence of the subagent's own work.

## Reflection

### Engineer

**What slowed you down (evidence):** no SDK or test runner in the sandbox; the 1.45.2 wheel was read from `uv.lock` to design the scrubbing.
**What nearly went wrong or was blocked:** the SDK's handler exports extra record fields and exception text, which would have leaked; a test fake missed `force_flush`, caught by CI.
**One proposed change (file, expected effect, measure):** ask earlier whether a test runner is available, so test-first checks are possible.

### QA

**What slowed you down (evidence):** mutants could not run; M1 rests on reading the SDK source and a timing calculation.
**What nearly went wrong or was blocked:** the first launch stopped on the relayed lane message.
**One proposed change (file, expected effect, measure):** `.kiro/steering/delivery-pace.md`: allow QA to install the locked SDK into `.scratch/` so mutants run for real; measured by Medium findings that rest on reasoning alone (one here). The session's one proposal.

## Launch usage

- Engineer (build, CI fix, fix round in two launches): unknown (the tool did not report time or tool uses).
- QA (stopped launch, first check, re-check): unknown.

## Files created or modified

- `socboard/telemetry.py`
- `socboard/app.py`
- `tests/test_telemetry.py`
- `_docs/records/findings/289.json`
- this file

## Decisions made by the human

- Confirmed #289's body change before it was claimed.
- The lane split: this session keeps tracks A and C; lane A takes track B (#340, #292, #293).
- The orchestrator declined the Engineer's request to run `uv` with a Python outside the project folder; CI is the test loop (delivery-pace item 1).

## Mismatches with the spec or design docs

- The contract names two log events; the existing loggers' messages are not those events, so their `event` field carries the message template (F-289-2).

## Commands to validate

- **Verify:** CI-VERIFIED on 35ded73: verify run 43991842170 (`VERIFY: PASS`, 3405 passed; telemetry tests 36 passed), image 43991842239, compose 43991842209, postgres 43991842177, all success.
- **Assert clean:** passed after each QA launch (6e7a2fa, 35ded73).

## Proposed AGENTS.md changes

none (the Engineer proposes a README paragraph naming the two OTEL variables; README is not protected, F-289-5).

## Temporary changes

none (SDK wheels downloaded to `.scratch/` for reading were deleted).

## Interruptions

- The first QA launch stopped before reviewing on a misread independence check; nothing was changed; relaunched fresh.
- One Engineer launch stopped with uncommitted edits, asking for a `uv` workaround; a second launch checked the edits against the QA comment and committed them.

## Unrelated problems noticed but not fixed

- F-289-1: The caller's tracestate is exported with the span (Low).
- F-289-2: The event field of existing loggers is the message template (Low).
- F-289-3: OTLP log records carry fields the contract does not name (Low).
- F-289-4: The test file imports the logs API and uses a hand-written metric exporter (Low).
- F-289-5: The README does not describe the JSON logs or the OTEL variables (Low).
- F-289-6: start_span accepts attributes on the server span (Low).
- F-289-7: No test shows an exemplar is produced (Low).
- F-289-8: Pre-setup warnings stay plain text; a failed dispose skips the flush (Low).
- F-289-9: Two timing tests rely on assumptions about the SDK and the network (Low).

## Follow-ups for the next session

- After the merge of #354: check the merged head, post the Close comment, run `make issue-close N=289`, and tell lane A #289 has merged (the handoff the lane split asks for).
- Next in track A: #290 (needs #289), then #312 and #291.
