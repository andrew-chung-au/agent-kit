# Issue #288: the OpenTelemetry packages

**Date:** 2026-11-16T23:47Z (UTC)
**Spec version:** e3461a7

## What changed and why

#288 adds the three OpenTelemetry packages the app needs for #289. The earlier session wrote the task file and stopped at the human's `uv add` step. The maintainer ran it on 2026-11-16 (`make verify` PASS) and pushed a63c813, then reassigned #288 to this session. The change is `pyproject.toml` (three lines) and `uv.lock` (297 lines added, none removed), both the maintainer's own commit. This session cut `issue-288-otel-deps` from that commit (it did not push to the old `claude/288-otel-deps` branch), filled the task file's result table, and wrote the findings.

**What I learned:** a new exporter release can add dependencies a task file's expected list does not name; the check "no instrumentation package, no moved pin" still holds, so the list should say "and their dependencies".

## Reflection

unknown (role not asked)

## Launch usage

none

## Files created or modified

- `pyproject.toml`, `uv.lock` (the maintainer's commit a63c813)
- `_human-tasks/2026-11-16T0412Z-human-task-288-engineer-add-otel-packages.md` (result table filled)
- `_docs/records/findings/288.json` (new), this file

## Decisions made by the human

- 2026-11-16: the maintainer ran the `uv add` step and reassigned #288 to this session.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify` (CI; the sandbox has no uv cache write). The maintainer's run on their machine: PASS.

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

The earlier session stopped before the human step; the claim was superseded by the maintainer's reassignment.

## Unrelated problems noticed but not fixed

- F-288-1: the task file's package list predates exporter 1.45.2 (two extra 0.66b2 packages).
- F-288-2: the task file's table was filled after the run, from pasted output.

## Follow-ups for the next session

- #289 uses the packages; #294's histogram and OTLP export (PR #342) wait for this merge.
