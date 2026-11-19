# Decide: install the kit's Claude Code layer

## Purpose

Decide whether to install the kit's Claude Code layer. It adds role definitions, a git guard, a verify-on-stop hook, permission rules and commit attribution. It must be settled before the baseline, because hooks and permissions change agent behaviour and a later change starts a new epoch. Issue: none.

## Where to decide

In the orchestrator session. If you choose to install, the steps are in `_docs/agent-kit/claude-code/START.md`, and you install the protected files from a clean clone.

## Options

1. Install now, before the first baseline issue.
2. Skip it and use Claude Code without the kit's guards. Roles then rely on the launch message that points to their role file.
3. Install later. That starts a new epoch for the trial.

## Recommendation

Option 1. Claude Code is your orchestrator, so its guards and permissions should be in place before measurement starts. The kit has no layer for Kiro, and that gap stays.

## Record the result

Write Pass once decided, and name the option in the note.

| Step | Pass or fail | Output or note |
|---|---|---|
| Decide | Pass | Option 1: installed, in 9b69b14 ("install Claude Code layer"). `.claude/settings.json` has the git guard and permission-log hooks and `Assisted-by: Claude Code` attribution; `.claude/agents/software-engineer.md` has the verify-on-stop hook. It differs from the kit's reference `settings.json` only by extra ask rules (`Makefile`, `pyproject.toml`, `opencode.json`, `.opencode/`, `.github/`, `.devcontainer/`). Recorded 2026-11-10 by the orchestrator from the repo, confirmed by the human, before the ponytail epoch start. |

## Risk

The layer adds protected files, so each needs your approval to commit.
