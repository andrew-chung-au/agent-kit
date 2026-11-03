# Planning: install Claude Code layer alongside OpenCode

**Date:** 2026-10-16
**Spec version:** 3f6a919 (HEAD at start; spec unchanged)

## What changed and why

The human uses OpenCode to do the work and Claude Code to supervise and review it. The kit's Claude Code layer (`_docs/agent-kit/claude-code/START.md`) had not been installed: there was no `CLAUDE.md` and no `.claude/`. This session installed steps 2-5 and made sure the two tools don't overwrite each other's configuration:

- Each tool's config is protected from the other. Claude Code asks before editing `opencode.json` and `.opencode/**`. OpenCode asks before editing `CLAUDE.md` and `.claude/*`. Without the second rule, OpenCode (`edit "*": allow`) could have rewritten the reviewer's settings and hooks.
- Both tools read the same instructions: `CLAUDE.md` only imports `AGENTS.md`, so there's one source of truth.
- Role parity: the Claude Code role files carry the same project DoD line as the OpenCode ones, and `rubric-auditor` was ported so both tools have the same four roles.
- Claude Code's hooks (`guard_git.py`, `verify_on_stop.py`) and permission rules apply only inside Claude Code; they don't change how OpenCode runs.

## Files created or modified

- `CLAUDE.md` (new, from `claude-code/CLAUDE.md.template`)
- `.claude/agents/pm.md`, `software-engineer.md`, `qa-engineer.md` (new, from the kit plus the ai-usage-log line from the `.opencode` versions)
- `.claude/agents/rubric-auditor.md` (new, same body as `.opencode/agents/rubric-auditor.md`)
- `.claude/settings.json` (new, from the kit's settings, with these differences: the ask list matches PROTECTED, plus `Makefile` to mirror `opencode.json`; `gh issue view`/`list` are allowed for reviewing; `gh issue delete` is denied to mirror `opencode.json`)
- `agent-kit.conf`: PROTECTED adds `'CLAUDE.md' '.claude/*'`
- `opencode.json`: edit `ask` for `CLAUDE.md` and `.claude/*`. Also includes the human's earlier uncommitted `"gh issue create*": "ask"` → `"allow"` change
- `_docs/ai-usage-log.md`: new entry

## Decisions made by the human

- Approved the protected edits to both `agent-kit.conf` and `opencode.json` (cross-protection).
- Chose to include the pending `gh issue create*` change in the same commit.

## Mismatches with the spec or design docs

None.

## Commands to validate

- **Verify:** `make verify` (PASS WITH WARNINGS; the only warning is no TEST_CMD, because no code exists yet)
- START.md step 6, after restarting Claude Code and accepting workspace trust: `/agents` lists the four roles, `/hooks` lists the git guard, `/permissions` shows the rules. Asking Claude to run `git add .` should be blocked with "Stage explicit paths only".

## Proposed AGENTS.md changes

- Layout line: mention `CLAUDE.md` and `.claude/` (Claude Code layer) next to `opencode.json` and `.opencode/agents/`.
- If Claude Code posts review comments on issues, it needs a role label. The Conventions list only `PM:`, `Engineer:`, `QA:` and `Orchestrator:`. Consider adding `Reviewer:`.

## Temporary changes

None.

## Interruptions

None.

## Unrelated problems noticed but not fixed

- The repo root has a tracked `agent-kit/` folder, an exact duplicate of `_docs/agent-kit/` (`git diff --no-index` shows no differences). It's not referenced by `KIT_DIR`. Decide whether to delete it.
- The repo root has a tracked `test.md`, purpose unknown.
- PM and QA role files (both tools) say "write only to `.scratch/`", but also "append to `_docs/ai-usage-log.md`". QA editing the log will also make `make assert-clean` after QA fail. The rule needs a carve-out, or the orchestrator should write the log entry for those roles.
- `.agents/skills/update-rubric-evidence/SKILL.md` points to `.opencode/agents/rubric-auditor.md`. Claude Code doesn't load skills from `.agents/` (VERIFY: it reads `.claude/skills/`), so in Claude Code, launch the `rubric-auditor` subagent directly.
- `AGENTS.md` requires key role prompts to be saved verbatim in `_docs/prompts/`. Neither tool's role definitions are there yet, and the index is empty.
- VERIFY: whether `*` in OpenCode permission globs crosses `/`. If it doesn't, `".claude/*"` (like the existing `".opencode/*"` and `"_docs/agent-kit/*"`) wouldn't cover `.claude/agents/*.md`.

## Follow-ups for the next session

- Restart Claude Code, accept workspace trust, and run the START.md step 6 checks.
- Run `make hooks` if the git hooks need reinstalling (START.md, existing-setup step 5).
- Don't run OpenCode and Claude Code against the same working tree at the same time. Review OpenCode's work after it has committed.
