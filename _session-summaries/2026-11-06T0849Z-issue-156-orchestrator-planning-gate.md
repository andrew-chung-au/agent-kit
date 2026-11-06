# Issue #156: Planning phase has no structure or spec-quality gate, so downstream rigor amplifies weak specs

**Date:** 2026-11-06T08:49Z (UTC)
**Spec version:** none

## What changed and why

The kit governed spec to issues to code, but not the spec itself. Added `procedures/planning.md` (five light planning steps and a seven-item definition of ready), linked from `process.md` Planning; `process.md` Backlog gained "Spec ready first" (the PM confirms readiness in its backlog-proposal comment, or proposes spec changes first and creates no implementation issues). `team/pm.md`, `README.md`, the ADR file `_docs/decisions/156-planning-gate.md` and its index row; `tests/test_planning_gate.py`. Commit `f6866f6`, PR #158, merge `5e8900b`.

Heavy: the PM added a `## Decision record` to the issue body (body sha256 `055ae078...109e9`) and the human approved it on the issue before work started. QA PASS at `f6866f6`. Only one QA PASS is recorded on #156; Heavy asks for two. GitHub closed the issue on merge ("Closes #156").

**What I learned:** `make issue-hash` cannot run in Kiro Web, so the PM computed the hash from the REST body; the orchestrator should confirm it with the script.

## Reflection

### Orchestrator

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

none

## Files created or modified

- `agent-kit/procedures/planning.md` (new)
- `agent-kit/process.md`, `agent-kit/team/pm.md`, `agent-kit/README.md`
- `_docs/decisions/156-planning-gate.md` (new), `_docs/index.md`
- `tests/test_planning_gate.py` (new)

## Decisions made by the human

- Approved the issue (label) and the Decision record at the recorded hash.
- Approved the commit and PR.
- After merge, asked for research on OpenSpec and other frameworks (#14).

## Mismatches with the spec or design docs

none

## Commands to validate

**Test (all):** `make test` (1338 tests OK at `f6866f6`)

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- Only one QA PASS on a Heavy issue, and closed by GitHub rather than `make issue-close`, which would have refused it.

## Follow-ups for the next session

- #159, #160, #161 (follow-ups from the #14 research), all merged in this session.
