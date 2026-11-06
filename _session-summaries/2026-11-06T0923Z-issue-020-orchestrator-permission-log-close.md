# Issue #20: Permission logging, part 1: OpenCode observe-only plugin and log record format (Phase 2a)

**Date:** 2026-11-06T09:23Z (UTC)
**Spec version:** none

## What changed and why

No new code in this session: a close review. #20's plugin and record format were built on 2026-11-03 (commit `0f14f6c`, PR #64, merge `873c221`) and QA passed every criterion it could check at `7e290f8`, leaving three real-session criteria unverified: the allowed, rejected and key-shaped records; subagent prompts; and fail-closed, the 200-character cut and the 1 MiB cap by hand. Since then the V1 plugin it built was replaced by the V2 port (#155, PR #157), because OpenCode 2.2.5 no longer loads V1, and #71 and #166 changed the cap and stream handling. The open criteria are now checked against V2 in #168, which the PM broadened on the human's approval: one current human task for every open real-session check of both loggers (OpenCode 2.2.5 and Claude Code), replacing the two task files that disagreed. #20 closes with those criteria recorded as moved and unverified.

**What I learned:** a real-session check written against one plugin API version goes stale when the tool upgrades; keep it with the current plugin's issue, not the original one.

## Reflection

### Orchestrator

unknown (role not asked)

## Launch usage

none

## Files created or modified

none. Issue edits: #168 (title and body, new hash `0584c4e7...91484`).

## Decisions made by the human

- Broaden #168 to cover every open real-session check (OpenCode 2.2.5, Claude Code, subagents, the optional cap check) and to replace both human task files, instead of filing a new issue.
- Close #20 with its real-session criteria moved to #168 and recorded as unverified.

## Mismatches with the spec or design docs

none

## Commands to validate

**Test (all):** `make test` (639 tests OK at `7e290f8`, QA)

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- #36 closed with its real-session checks never run; #168 now carries them.
- #56's dry-run candidates (#94, #77) are both closed; #56 needs new ones.

## Follow-ups for the next session

- `make issue-close N=20` from the local sandbox, after this summary is on `main`.
- #168: the human labels it; the agent writes the new task file; QA checks it; the human runs it.
