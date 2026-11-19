# Issue #287: O2 Decision record: telemetry backend, on-call runner and alert path

**Date:** 2026-11-16T04:11Z (UTC)
**Spec version:** e3461a7

Tier: Standard (from the PM proposal; no tier label).

## What changed and why

Added `_docs/decisions/2026-11-16T0400Z-observability-backend-agent-alert.md` (Status: approved) recording the human's 2026-11-16 decisions from roadmap 4: the self-hosted backend in `compose.observability.yaml`, `anthropics/claude-code-action` in the `oncall` Environment, and the drill workflow's Alertmanager poll, each with alternatives and trade-offs. Added its row to `_docs/index.md`. Commit 7038356 on `claude/287-observability-decision`, PR #325.

**What I learned:** check the merged head of a pull request before closing (#310's merge missed its fix; see the correction on #310).

## Reflection

### Engineer

**What slowed you down (evidence):** `make verify` cannot pass in Kiro Web, so the result reads FAIL for an environment reason and needs explaining.
**What nearly went wrong or was blocked:** there is no transcript of the 2026-11-16 ruling; the Evidence line links where it is recorded (roadmap 4's Decisions, PR #302, the PM grooming comment) rather than an invented link.
**One proposed change (file, expected effect, measure):** see QA.

### QA

**What slowed you down (evidence):** none beyond relying on CI for Tests and Lint; the head SHA of all four runs was checked against 7038356.
**What nearly went wrong or was blocked:** the five-versus-six count comes from the issue text itself, so it was graded Low and left to the human.
**One proposed change (file, expected effect, measure):** `_docs/agent-kit/procedures/verify.md`: report a read-only uv home as "not run" instead of FAIL, so docs-only issues in Kiro Web show a clean result; measured by Engineer comments explaining an environmental FAIL (one per issue so far). The session's one proposal (from the Engineer).

## Launch usage

- Engineer: unknown (the tool did not report time or tool uses).
- QA: unknown.

## Files created or modified

- `_docs/decisions/2026-11-16T0400Z-observability-backend-agent-alert.md`
- `_docs/index.md`
- `_docs/records/findings/287.json`
- this file

## Decisions made by the human

- Start #287 and #286 as recommended (this session).

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** CI-VERIFIED on 7038356: verify run 43801548403, image 43801548462, compose 43801548314, postgres 43801548324, all success. Local Tests and Lint cannot run in Kiro Web.
- **Assert clean:** passed after QA at 7038356.

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-287-1: The server-size trade-off says five more containers while the record lists six services (Low).

## Follow-ups for the next session

- After the merge of #325: check the merged head is this branch's last commit, post the Close comment, run `make issue-close N=287`.
