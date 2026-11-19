# Issue #338: O0b Contract and spec: alert on the synthetic probe's measurement

**Date:** 2026-11-16T23:12Z (UTC)
**Spec version:** 9cf7ed3

Tier: Standard (from the PM proposal; no tier label).

## What changed and why

`observability/CONTRACT.md` adds the probe's resource (`socboard-probe`) and histogram `socboard.probe.time_to_queue`, marks the in-app histogram as a diagnostic recorded only while the queue is watched (6 s), states the always-on sampler, logs over OTLP with the trace id as Loki structured metadata, and moves `QueueLatencyOverSLO` onto the probe's histogram with at least 20 measurements in 5 minutes (b14fd9a). `_docs/specs.md` changes the two section 4 lines the issue fixes (9cf7ed3, HUMAN_APPROVED=1 after the human approved the exact diff). Source: the senior review of 2026-11-16, decision 1. PR #344. Done first because #294, #296 and #291 read it, and #296 is the shortest path to the Alerting rubric point (`.kiro/steering/rubric-priority.md`, PR #345).

In the same session the human confirmed #289's body change; the orchestrator applied the PM's body, posted the Confirm comment and the PM recorded hash 3f8e864.

**What I learned:** none new.

## Reflection

### Engineer

**What slowed you down (evidence):** none.
**What nearly went wrong or was blocked:** the contract edit was made with an inline shell script instead of the edit tool (F-338-1).
**One proposed change (file, expected effect, measure):** use the edit tool for every edit and keep scripts for checks only.

### QA

**What slowed you down (evidence):** none; CI head SHA checked for all four runs.
**What nearly went wrong or was blocked:** ruling out stale contract text needed the whole file read, not only the diff.
**One proposed change (file, expected effect, measure):** none; the session's one proposal is the Engineer's.

## Launch usage

- Engineer: unknown (the tool did not report time or tool uses).
- QA: unknown.

## Files created or modified

- `observability/CONTRACT.md`
- `_docs/specs.md` (protected, human-approved)
- `_docs/records/findings/338.json`
- this file

## Decisions made by the human

- Approved the exact spec diff and confirmed 20 measurements and the 6-second watch window.
- Confirmed #289's body change (Option 1 of the PM's proposal).
- Work the highest-value rubric points first (recorded as `.kiro/steering/rubric-priority.md`, PR #345).

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** CI-VERIFIED on 9cf7ed3: verify run 43975527047, image 43975527043, compose 43975527080, postgres 43975527034, all success.
- **Assert clean:** passed after QA at 9cf7ed3.

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-338-1: The contract edit was made with an inline shell script instead of the edit tool (Low).
- F-338-2: Section 2's sentence about what the histogram measures does not say which of the two histograms it means (Low).

## Follow-ups for the next session

- After the merge of #344: check the merged head is this branch's last commit, post the Close comment, run `make issue-close N=338`.
- #296 (the alert) needs its label; it is the last step to the Alerting point. F-338-2 can ride on #312.
