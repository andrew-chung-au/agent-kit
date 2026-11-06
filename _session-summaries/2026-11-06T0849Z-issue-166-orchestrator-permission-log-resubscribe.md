# Issue #166: OpenCode permission log stops silently if its event stream ends; resubscribe

**Date:** 2026-11-06T08:49Z (UTC)
**Spec version:** none

## What changed and why

Follow-up from #155's QA. The plugin now subscribes again when OpenCode's event stream ends: one attempt per wait, 1 s doubling to a 5 min cap while streams bring nothing, reset after a stream that delivered events; it stops on unload. Doc limit replaced; text checks and a Python model of the waits.

Commit `e3e189d`, PR #167, QA PASS at `e3e189d`. PR #167's base was the #155 branch, and it merged 11 seconds after PR #157 had already merged that branch into `main`, so `main` never got the fix. Cherry-picked onto a branch from `main` as `6bedf52`, plus `ab111ea`: QA's note that each wait left an `abort` listener behind, now removed whichever comes first (a test pins it and fails against the old code). PR #173, open, waiting for QA's re-check (the new commit voids the PASS at `e3e189d`). The PR says "Refs #166".

**What I learned:** a PR based on another feature branch must be retargeted or merged first; otherwise its fix can land on a branch that is already merged.

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

- `agent-kit/opencode/plugins/permission-log.js` (148 lines)
- `agent-kit/procedures/permission-log.md`
- `tests/test_permission_log.py`

## Decisions made by the human

- Labelled the issue (Standard; the PM recorded body hash `eaa02bd4...e302f`, unchanged since filing).
- Fix QA's listener note in this change (option 1).
- Continue #166 in this session rather than a new one.

## Mismatches with the spec or design docs

none

## Commands to validate

**Test (all):** `make test` (1391 tests OK at `ab111ea`)

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

The work was briefly handed over for a new session (comment on #166), then continued here at the human's request; the handover comment's steps are superseded by PR #173.

## Unrelated problems noticed but not fixed

none

## Follow-ups for the next session

- QA re-check of PR #173 at `ab111ea`, merge, then the `Orchestrator:` Close comment and `make issue-close N=166`.
- Not verified live: no Node or OpenCode here; the hand check (#168) covers normal logging only.
