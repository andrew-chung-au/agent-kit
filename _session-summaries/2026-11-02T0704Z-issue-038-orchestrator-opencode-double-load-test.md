# Issue #38: Test the AGENTS.md double-load fix in OpenCode

**Tier:** Standard (no tier label was set; the PM proposed Light, but the session summary is outside Light's allowed paths). Run without an Engineer: no code or protected file changed, and the only deliverable is this record.
**Date:** 2026-11-02T07:04Z (UTC)
**Spec version:** none

## What changed and why

No kit change. #35 removed the explicit "Read `AGENTS.md`" from the OpenCode role definitions (`agent-kit/opencode/agents/*.md`, commit 664dbff) on the evidence that Claude Code subagents receive `AGENTS.md` automatically. This issue checks the same in OpenCode. The human ran the test and reported the results; the orchestrator checked each quote against `AGENTS.md` with `grep -F`.

**Result: both roles launched quoted a real line, word for word. The fix holds; #35's OpenCode edit stands.**

| Item | Value |
|---|---|
| OpenCode version | 1.19.5, as printed by `opencode --version` in the sandbox terminal (`/workspaces/agent-kit-sandbox`). The repo pins `@opencode-ai/plugin` 1.19.0. I assume the quote tests ran in this same install; the human did not state it separately. |
| Prompt, exactly | `@<role> Before you read any file or run any command, quote one line from AGENTS.md, exactly.` Not told which line. Each role in a new session. |
| `pm` quoted | "Change only the files the task needs. Note an unrelated problem in the session summary instead of fixing it." This is `AGENTS.md` line 44, word for word. |
| `qa-engineer` quoted | "Don't delete files or data you didn't create in this task, including git-ignored files and Docker volumes, without the human's approval." This is the first sentence of `AGENTS.md` line 45, word for word. |
| Tool calls before the answer | none, per the human ("No tools"). Each answer was preceded only by a "Thought" line. |
| Roles launched | two of three (`pm`, `qa-engineer`); the issue requires at least two. `software-engineer` was not tested with this prompt. |

Refused case: neither role read a file first or quoted a line absent from `AGENTS.md`, so the result is "loaded", not "not loaded".

Related smoke checks, run earlier in this session on the human's request (no criteria of #38): the three agents list correctly; `git add .` and a PM edit of `AGENTS.md` were refused by the agents themselves citing `AGENTS.md` and the role file, and the Engineer proposed a `Makefile` edit as a diff and stopped at its process gate. A tool-level permission denial or prompt was never observed, because the agents refused before reaching it. Not verified by automation or by this test: that OpenCode's permission rules fire.

**What I learned:** an agent that has read the kit's rules refuses on its own judgment before a permission rule is reached, so asking an agent to attempt a denied action cannot prove the rule itself.

## Reflection

PM: unknown (role not asked)
Engineer: unknown (role not asked; none launched)
QA: pending, added after the QA check.

## Launch usage

- PM (record hash, short launch): 28.7 s, 10 tool uses
- QA: pending, added after the QA check.

## Files created or modified

- This summary only.

## Decisions made by the human

- Labelled #38 `approved` (the label was added before the hash was recorded; the PM then recorded it).
- Tier: approved the recommendation to run without an Engineer and write the record as the orchestrator's session summary, with QA checking it independently.
- Ran the quote test in OpenCode and reported the results.

## Mismatches with the spec or design docs

- #38's body says "this sandbox cannot run it; see `agent-kit/environments.md`". `environments.md` says no such thing, and OpenCode 1.19.5 runs in the sandbox terminal. The PM noted the correction in its comment; the body was not edited.
- `agent-kit/opencode/START.md` line 3 still says OpenCode "reads `AGENTS.md` directly"; the test now supports that for subagents, so no edit is needed.

## Commands to validate

**Verify:** `make verify`

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- #20's stage 1 gate (confirm the real permission event names) is still open: its Engineer's `opencode run` stalled in the sandbox on an earlier attempt. OpenCode now works, so it can be retried.
- #5, #7 and #15's duplicate targets still need their criteria added before closing (backlog review).
- The #16 and #39 session summaries are still staged and uncommitted.
- `make assert-clean` still fails here because of pre-existing uncommitted work.

## Follow-ups for the next session

- Retry #20's stage 1 gate now that OpenCode runs; the plugin installs under `.opencode/*` need the human's approval.
- #38 body correction (the false `environments.md` claim) is noted only in the PM comment; edit it only if the human wants the text fixed.
