# Issue #71: Permission-log plugin follow-ups from #20 QA (closing record)

**Date:** 2026-11-04T11:19Z (UTC)
**Spec version:** none

## What changed and why

This is a closing record written after the fact, from #71's issue comments only. The orchestrator who ran #71 did not write a summary, and this session did not build it. The work was built by Kiro (Engineer comment: commit `2b01562`, PR #79, merge `725f1ff`) and QA-passed at `e26c8c9`.

#71 fixed gaps found in #20's QA of the OpenCode permission-log plugin: no record after the `truncated` marker (one marker per day file, later records dropped, also after a restart), source-check gaps in the observe-only checker, and a test for the 200-character pattern cut. `agent-kit/procedures/permission-log.md` states the cap rule in one sentence.

**What I learned:** QA noted two mutation shapes that survive the tests (removing the restart check from the marker condition, and a cut line left only in a comment). They are not criterion failures and were not filed here.

## Reflection

unknown (role not asked). This is a closing record only.

## Launch usage

none (this session launched nothing for #71).

## Files created or modified

Per `git show 2b01562 --stat` (as QA recorded): 3 files, 155 insertions and 5 deletions: `agent-kit/opencode/plugins/permission-log.js`, `agent-kit/procedures/permission-log.md`, `tests/test_permission_log.py`. This record is the only file added now.

## Decisions made by the human

- 2026-11-03: #71 lands before #36, which reuses its cap rule (PM comment on #71).
- 2026-11-04: asked to close #71; chose to have this closing record written from the issue record (option a).

## Mismatches with the spec or design docs

none known.

## Commands to validate

**Verify:** `make verify` (QA: PASS at `09c3021`, 1175 tests; `BASE=2b01562^` at `e26c8c9`, 1147 tests, PASS with warnings that belong to later issues).

## Proposed AGENTS.md changes

none.

## Temporary changes

none.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- The by-hand OpenCode check of the cap and restart behaviour is unverified; it is on #20's real-session list. Node is not installed in the sandbox, so QA ran a Python model and text checks only.
- `procedures/permission-log.md` is now 325 words (limit raised to 330 by #85) because later issues grew it, not #71.

## Follow-ups for the next session

Close #20 once its real-session list is done.
