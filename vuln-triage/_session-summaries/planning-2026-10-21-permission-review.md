# Planning: permission review records actions, not outcomes

**Date:** 2026-10-21
**Spec version:** 3ecd54b

## What changed and why

- The permission review asked each role to report commands that "stopped for approval". An approved prompt and an auto-allowed command look identical to the agent, so the report defaulted to "none" and the session summaries could not show what the agent actually had to ask about.
- The rule now records every command or change that required approval, whether or not it was granted: every merits-based request and every command matching an `ask` rule. It records the action and its basis, not the decision.
- The template's unenforceable check for commands that "ran without asking although a rule says `ask`" is removed.
- `asking-the-human.md` gains a "Recording requests" section explaining the rule and noting that protected-file approval records are separate.

## Files created or modified

- Protected, approved in this session and committed with `HUMAN_APPROVED=1`: `1b37fd1` (`AGENTS.md`, `_docs/agent-kit/procedures/asking-the-human.md`, `_docs/agent-kit/procedures/session-summary.md`, `_docs/agent-kit/process.md`, `_docs/agent-kit/team/pm.md`, `_docs/agent-kit/team/qa-engineer.md`, `_docs/agent-kit/team/software-engineer.md`, `_docs/agent-kit/templates/session-summary.md`).
- `_docs/ai-usage-log.md` and this summary.

## Decisions made by the human

- The permission review records only the actions that required approval, whether granted or not. The outcome is not relevant to the review.

## Mismatches with the spec or design docs

None.

## Commands to validate

- **Verify:** `make verify` PASS WITH WARNINGS (35/35 frontend tests; whitespace PASS; 7 removed assertions are from the earlier unpushed #22 test rewrite, not this docs-only change).
- `git diff --check`: clean.

## Proposed AGENTS.md changes

None beyond the protected change in `1b37fd1`.

## Temporary changes

None. No process was started and nothing was installed.

## Permission review

Outcomes are not recorded, per the new rule.

- Read-only (propose allowing): none.
- Writes to the record (keep asking):
  - `gh issue edit 23`, by the PM; basis: `gh issue edit*` `ask` rule.
  - Editing the eight protected documentation paths above; basis: the `edit` `ask` rules for `AGENTS.md` and `_docs/agent-kit/**`.
  - `HUMAN_APPROVED=1 git commit` for `1b37fd1`; basis: merits request for a protected commit.
- Risky (propose denying): none.
- Proposed `opencode.json` and `.claude/settings.json` changes: none.
- Sources: the PM's #23 grooming comment reported "none" before the new rule applied; the Engineer's #23 comment reported "none" and ran no `ask`-rule command. The orchestrator's list is above.

## Protected-change approval record

- Issue: none (direct human request on 2026-10-21)
- Commit: `1b37fd11360ad42c8535bc21a763b5d088d01348`
- Parent: `752b36352bb8649267beba0fd0cf4992f7c7df11`
- Paths: `AGENTS.md`, `_docs/agent-kit/procedures/asking-the-human.md`, `_docs/agent-kit/procedures/session-summary.md`, `_docs/agent-kit/process.md`, `_docs/agent-kit/team/pm.md`, `_docs/agent-kit/team/qa-engineer.md`, `_docs/agent-kit/team/software-engineer.md`, `_docs/agent-kit/templates/session-summary.md`
- Approved: human, 2026-10-21, in this session; no issue comment exists
- Diff command: `git show --format= --no-renames --patch 1b37fd1 -- AGENTS.md _docs/agent-kit/procedures/asking-the-human.md _docs/agent-kit/procedures/session-summary.md _docs/agent-kit/process.md _docs/agent-kit/team/pm.md _docs/agent-kit/team/qa-engineer.md _docs/agent-kit/team/software-engineer.md _docs/agent-kit/templates/session-summary.md`
- Diff: the eight-file diff displayed in the approval request in this session; the staged diff was unchanged between that approval and the commit. `git show` with the command above reproduces it.
- Blob IDs:
  - `AGENTS.md`: `f83b0f7928eee7334ce9966f8320b7239d5fc0ab`
  - `_docs/agent-kit/procedures/asking-the-human.md`: `08def803ce8db23348a246a7c8a7a4a4a73b0d90`
  - `_docs/agent-kit/procedures/session-summary.md`: `cead71d7b60ddbeb076e2f8afd2969c409da91c2`
  - `_docs/agent-kit/process.md`: `b7ba18f91b938247ff811fcf18aa6ba912bf583d`
  - `_docs/agent-kit/team/pm.md`: `be7a7a6fa7f66d6b75d89ac6061212cf6a9176a6`
  - `_docs/agent-kit/team/qa-engineer.md`: `2b60f79a3497e580062a2645a23831b3dcf6aa3b`
  - `_docs/agent-kit/team/software-engineer.md`: `c42ecd445dba7a29e41273bbaf4b0684ac76c8e2`
  - `_docs/agent-kit/templates/session-summary.md`: `85fa7d52ad6d143a5fffde5345ac917e596566e5`

## Interruptions

- The `pm`, `software-engineer` and `general` subagents failed several times with "Upstream request failed: Endpoint is unavailable". Short general-subagent runs completed the #23 grooming and contract work. No partial output was reused as verified.

## Unrelated problems noticed but not fixed

- The stale top-level `agent-kit/` copy still has the old permission-review wording. #38 removes the duplicate; it was not edited here.
- The default `make verify` still warns about 7 removed assertions from the earlier unpushed #22 test rewrite.

## Follow-ups for the next session

- **#23 (roadmap step 8):** continue from the Engineer comment 6307457348. The human decisions D1-D5 are recorded in 6305987033. Next: approve the `openapi-validate` Makefile target, run the validator and its broken-`$ref` refusal case, get the human's review of `_docs/openapi.yaml`, then QA.
- **D4 follow-up:** file the `types.ts`/mock/UI alignment issue after #23, before #34/#25.
- **#31 (step 16):** the human sets up the Compose dev container using `_docs/docker-runbook.md` section 1.
