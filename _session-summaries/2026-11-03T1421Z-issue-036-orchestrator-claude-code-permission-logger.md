# Issue #36: Claude Code permission logger, combined report and log retention

**Date:** 2026-11-03T14:21Z (UTC)
**Spec version:** none

## What changed and why

Phase 2b of the permission log. #36 adds the Claude Code observe-only `PermissionRequest` hook (`agent-kit/claude-code/hooks/log_permission.py`), shared redaction (`agent-kit/scripts/permission_log_lib.py`), `make permission-report [SINCE=YYYY-MM-DD]` over both tools' logs, and `make permission-logs-prune DAYS=<n>` for retention, with the same cap and marker rule as the OpenCode plugin (#20, #71). Built by Kiro as PR #81, merged as 5d54856.

The hook event carries a session, a tool name and a tool input but no outcome and no id to pair an ask with its result, so asks are logged and outcomes are not; the report prints `-` (unknown, not zero) for the reply columns.

QA found that the repo's `Bash(make *)` allow let `make permission-logs-prune` (a delete) run with no prompt. The fix, requested by the human, is an ask rule in four places: the kit's Claude settings, this repo's `.claude/settings.json` (commit 911b009), the kit's OpenCode config and this repo's `opencode.json`. This repo's `PermissionRequest` registration was added in aa5f7c4 and takes effect after Claude Code reloads its settings.

**What I learned:** a delete target needs its own ask rule the moment a broad `make *` allow exists; a text note that "the human runs it" is not a control. Also, rebasing a PR branch that the human is about to push breaks their fetch: the rebase rewrote unpushed commits the human had already fetched.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- QA (full check at af57111): 958.8 s active, 115873 tokens, 58 tool uses.
- QA (delta re-check at acdc14d): 389.0 s, 65241 tokens, 25 tool uses.
- PM (filed follow-ups #85 to #88): 172.3 s, 37 tool uses.
- Engineer (Kiro, outside this session's launches): unknown.

## Files created or modified

- New: `agent-kit/claude-code/hooks/log_permission.py`, `agent-kit/scripts/permission_log_lib.py`, `permission-report.py`, `permission-logs-prune.py`, `tests/test_permission_log_claude.py`, `tests/test_permission_report.py`.
- Changed: `Makefile`, `agent-kit/templates/Makefile.mk` (conflict with #82's `kit-compare` resolved in the rebase), `agent-kit/claude-code/settings.json`, `agent-kit/claude-code/START.md`, `agent-kit/opencode/opencode.json`, `opencode.json`, `agent-kit/procedures/permission-log.md`, `agent-kit/README.md`, `agent-kit/blueprints.md`, `agent-kit/setup.md`, `tests/test_permissions.py`.
- This repo's `.claude/settings.json`: ask rule (911b009) and hook registration (aa5f7c4), committed by the orchestrator with the human's approval.

## Decisions made by the human

- Outcomes are not logged (option 1 in the Engineer's hook check).
- Add the prune ask rule to #81 before merge, not as a follow-up.
- The `.claude/settings.json` ask rule and the `PermissionRequest` registration, each approved as a diff before its `HUMAN_APPROVED=1` commit.
- Kiro rebases #81 and force-pushes only that branch with `--force-with-lease`; it stages protected paths and waits for approval from then on.
- The human merged PR #81.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`. QA ran `make test` and `make verify` on exports: 813 tests (first check), 883 tests (after the rebase). Mutation checks: 30 of the new tests in the first pass, 2 survived (cap boundary and file mode); Kiro added those two tests and QA's delta pass caught every mutation.

## Proposed AGENTS.md changes

none

## Temporary changes

none. This repo's `.claude/settings.json` now registers a hook that writes the git-ignored permission log in `.agent-kit/logs/permissions/`.

## Interruptions

none. Kiro committed and pushed protected files (d3f724d) before the human's per-diff approval, reading an earlier "ok" as the go-ahead; the human's merge was the control, and Kiro agreed to stage only from then on.

## Unrelated problems noticed but not fixed

- The logger writes through a symlinked log folder: filed as #85.
- A path to a production-variant env file leaves a visible tail after redaction: filed as #86.
- Not verified in a real session: one allowed and one denied prompt with the prompt unchanged; whether a hook that exits 0 with no output leaves the prompt untouched in the human's version; whether subagent prompts get their own `session_id`.

## Follow-ups for the next session

- The human's real-session check of the hook (the human task for #20 and #36 checks).
- #85 and #86 (unlabelled).
