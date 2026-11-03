# Issue #67: orchestrator comment layouts

**Date:** 2026-11-03T12:45Z (UTC)
**Spec version:** none

## What changed and why

The orchestrator wrote the same four issue comments (claim, release, confirm, close) from memory, and the wording drifted. #67 adds `agent-kit/procedures/orchestrator-comments.md` (fixed lines and per-issue facts for each layout, the `Orchestrator:` prefix and `make issue-comment` rules, do-not cases), one Read-when line in `AGENTS.md` and in `agent-kit/templates/AGENTS.md.template`, a `blueprints.md` row, and `tests/test_orchestrator_comments.py`. Built by Kiro as PR #83, merged as 36e6171.

After the merge, the claim layout's line "the REST fallback" was reworded to "REST fallback for reads; writes still use `make issue-comment`" (commit 264b8a9, with a pin and two mutation cases), because the fallback line contradicted the rule against raw `gh` writes. The human's reword instruction reached Kiro too late; the PR was merged first, so the orchestrator made the edit on `main`.

**What I learned:** a fix requested after QA must also be passed to the role that owns the PR before the human merges, or it becomes a second commit on `main`.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- QA: 343.4 s, 63381 tokens, 39 tool uses.
- Engineer (Kiro, outside this session's launches): unknown. No PM launch this session.

## Files created or modified

- `agent-kit/procedures/orchestrator-comments.md` (new, 227 words after the reword, cap 300).
- `AGENTS.md`, `agent-kit/templates/AGENTS.md.template` (one Read-when line each, +22 words each: AGENTS.md 1473 to 1495), `agent-kit/blueprints.md`.
- `tests/test_orchestrator_comments.py` (new).

## Decisions made by the human

- The `_docs/agent-kit/` path in both Read-when lines is accepted (it matches the neighbouring lines and the project gotcha; the criterion's "`agent-kit/` here" looked mistaken).
- Reword the REST fallback line; approved with `HUMAN_APPROVED=1` and committed as 264b8a9.
- The human merged PR #83.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`. QA ran `make test` on an export of the branch: 749 tests, passed. Mutation checks on `tests/test_orchestrator_comments.py`: 18 of 18 caught. After the reword, `make test` on `main`: 804 tests, passed.

## Proposed AGENTS.md changes

none (the Read-when line is already in).

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- QA did not compare the layouts' field lists with the scratch drafts or the sweep evidence; neither did the Engineer.

## Follow-ups for the next session

- Version bump and changelog lines, the human's call.
