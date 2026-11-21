# Kit 1.11 planning

**Date:** 2026-11-19. Everything a session needs to carry on the 1.11 kit upgrade, in the repo so a cloud session can read it.

| File | What it is |
|---|---|
| `workflow-review.md` | The 1.11 proposal: evidence from socboard, vuln-triage and the kit, the workflow, settings and profiles, formats, and the 1.11 scope (section 9). Every decision is recorded in section 12; none is open. |
| `issues/00-index.md` | The 21 draft issues in filing order (01a to 12), with tier, grades, needs, the existing issues each one affects, and the gaps still open. |
| `issues/filed.md` | The filed issue number for each draft id (issue #196 to issue #216), how they were filed, and notes from the split. |
| `issues/01-...md` to `issues/12-...md` | One draft per issue. A file holding a split (01, 03, 04, 07, 08, 09, 11) has each part as its own section. |
| `backlog-review-2026-11-19.md` | Review of the 26 open issues against main and the proposal: what was closed, what 1.11 supersedes, what folds into which draft. |

## Where things stand

- **All 21 issues are filed** (2026-11-20), as issue #196 to issue #216, unlabelled. `issues/filed.md` maps each draft id to its number. Next: the human adds `approved` to 01a (issue #196); the PM grooms it first. Settled by the human on 2026-11-19: 04c is heavy; 07a waits for 05 and 06.
- **Grooming is one issue at a time** until 04c (groom ahead) lands, because `process.md` still forbids grooming a second unlabelled issue.
- **Closures that wait for the human's approval** (as not planned): issue #142 and issue #26 (when 7b is approved), issue #17 (into 11a), issue #15 (into 09a), issue #9 (superseded by `agent-kit/releasing.md`, or narrowed). See the backlog review, sections C and D.
- **Related open issues, unlabelled:** issue #188 (push-check uv stub; until fixed, `unset AGENT_PUSH_CHECK_IMAGE` before pushing the kit), issue #191 (usage visibility; later), issue #192 (install-guide wording), issue #193 (tests that share `.scratch/`; all four files, approved scope).
- **Tool economics** shape the design: Claude Code has a five-hour window and is the only tool with a model step-up (`STEP_UP`); OpenCode runs free models; Kiro has month credits and its auto model is cheaper than a named one.

## CodeBuddy

Decided on 2026-11-21; the live spike ran the same day on CodeBuddy 2.185.0, and the layer was written from those results the same day.

- `AGENTS.md` is the single always-loaded core-rules home. CodeBuddy loads a folder's `AGENTS.md` when that folder has no `CODEBUDDY.md`, and a parent `CODEBUDDY.md` does not shadow a child `AGENTS.md`; the kit adds no `CODEBUDDY.md`. Project rules, if used, live at `.codebuddy/rules/<name>/RULE.mdc`; use Agent Requested (`alwaysApply: false` plus a description) rather than the undocumented `paths` key.
- No model swapping in CodeBuddy, as in OpenCode and Kiro: `STEP_UP` stays Claude-only, and a step-up attempt notes that no escalated model is configured (3.5).
- The status-line script is optional and fail-silent (context percentage and spend only, no quota), and the soft stop stays manual. Issue #191 stays decoupled.
- `memory.parentDiscovery: false` is the monorepo setting: the spike confirmed the key is accepted without a warning and loads only the child `AGENTS.md`.
- The guard hardening in `agent-kit/claude-code/hooks/guard_git.py` applies to every tool that runs the hook. The spike confirmed `PreToolUse` exit 2 blocks Bash and a failing hook is still blocked through the `|| exit 2` wrapper, so CodeBuddy uses the same script and wrapper; no JSON `permissionDecision` adapter is needed.

Live spike results (2026-11-21, CodeBuddy 2.185.0; steps and observations in `_human-tasks/2026-11-21T1056Z-human-task-engineer-codebuddy-live-checks.md`):

- **Permission rules:** both `Bash(echo allow-space *)` and `Bash(echo allow-colon:*)` are honored, for allow and deny; deny rules are hard stops. Use the documented colon form in the template; the space form works in this build but is not documented.
- **Hooks:** `PreToolUse` exit 2 blocks Bash, fires for `Bash`, `Read`, `Agent` and `Grep` with a `*` matcher, and a hook that exits 1 is blocked through `|| exit 2`.
- **Payloads:** `PermissionRequest` fires for an ask and carries `tool_use_id`/`call_id`; `PermissionDenied` fires for a deny rule with the same `call_id` and a `reason`. A human-rejected ask produced no `PermissionDenied`, so the log can record asks and hard denials but not the human's decision on an ask.
- **Subagents:** a subagent frontmatter `Stop` hook did not run without `allowUntrustedFrontmatterHooks`; `SubagentStop` fires globally with `agent_id` and `agent_type`. Do not enable the trust flag; use a global `SubagentStop` hook to identify the agent, and rely on git hooks and QA.
- **Parent discovery:** with the default, a parent `CODEBUDDY.md` and the child `AGENTS.md` both load, plus a grandparent `AGENTS.md`; in the parent folder itself, `CODEBUDDY.md` shadows the parent's `AGENTS.md`. `memory.parentDiscovery: false` loads only the child `AGENTS.md`.
- **Not covered:** model selection and the status line.

The layer is written from these results: `codebuddy/START.md`, `codebuddy/settings.json`, the three agent files and the sweep skill. Keep `AGENTS.md` as the single core-rules home and add no `CODEBUDDY.md`; use the colon permission form, the guard with `|| exit 2`, and `memory.parentDiscovery: false` for monorepos. Do not enable `allowUntrustedFrontmatterHooks` globally. `memory.parentDiscovery` ships commented out, because the default suits every project that is not a monorepo and the setting only narrows what loads.
