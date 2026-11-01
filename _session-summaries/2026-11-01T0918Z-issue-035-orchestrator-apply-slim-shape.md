# Issue #35: Slim the always-loaded context, part 2 (Phase 1b-b)

**Date:** 2026-11-01T09:18Z (UTC)
**Spec version:** none

## What changed and why

Five commits, each approved by the human: 9a01ea4 (kit changes: the `.env` Non-negotiable and an honest hook line, "Conventions" wording replaced across the kit, a README upgrade note for the new SHARED START/END marker pair, `tests/test_kit_env_and_launch.py`), d79b199 (this repo's own `AGENTS.md` rebuilt to the new shape), 339d547 and 664dbff (the Claude Code and OpenCode role definitions no longer say "Read `AGENTS.md`", pinned by `tests/test_role_agents_md_pointer.py`; the two commits are separate so the OpenCode half, which is unverified, can be reverted first) and d01c71e (this repo's `agent-kit.conf` line 27 pointer and a stale test docstring). The double load was confirmed for Claude Code (a subagent's context already held `CLAUDE.md` with `@AGENTS.md` inlined before it read any file); OpenCode was not observed, and follow-up #38 tests it.

QA: FAIL at 664dbff for evidence only (the mapping table and the re-grep report were not on the issue), then PASS at 664dbff once the Orchestrator posted both. d01c71e (one comment word and a docstring) came after QA and was not re-checked by QA; the orchestrator ran `make verify` on it (PASS).

Words: `AGENTS.md` 1658 to 1313 (-21%); the template 780 to 803 (+23); the three Claude Code definitions 258 to 252 and the three OpenCode definitions 220 to 214.

Live-edited code: `agent-kit/claude-code/hooks/guard_git.py` runs live from the working tree; its edit was a docstring on line 2 only. No `agent-kit/scripts/` file was touched.

**What I learned:** a mapping table or grep report that exists only in an approval request counts as missing evidence for QA; and a case-sensitive grep misses a lowercase "conventions".

## Reflection

### PM

**What slowed you down (evidence):** scope grew during grooming (the `.env` rule, the double-load decision, then a third commit), so the body was edited more than once. The issue now has 6 comments.
**What nearly went wrong or was blocked:** the decisions sat in comments while the body said otherwise, so an Engineer could have followed a stale body. Editing the body fixed it.
**One proposed change (file, expected effect, measure):** in `agent-kit/team/pm.md`, add "after any mid-groom decision, fold it into the body before handing off". Expected effect: fewer body-versus-comment conflicts. Measure: count issues where the Engineer or QA cites a comment that contradicts the body, over the next 5 issues.

*Orchestrator note:* the PM wrote this without re-reading the issue or `pm.md`; points 1 and 2 come from the orchestrator's brief and a comment count. Point 2 is only partly right: the `.env` change was folded into the body at grooming, but the double-load decision and the third commit live only in a later PM comment, because that run did not edit the body. QA read all the comments, so nothing went wrong.

### Engineer

**What slowed you down (evidence):** the first QA verdict was FAIL only because the mapping table and re-grep report sat in the approval request, not on the issue; commit 1 took about 45 minutes, mostly waiting for approval, and a later run found a lowercase "conventions" the capitalised grep missed.
**What nearly went wrong or was blocked:** the capitalised-only grep left a dangling reference unreported until a rerun.
**One proposed change (file, expected effect, measure):** `agent-kit/team/software-engineer.md` should say to post the mapping table and case-insensitive re-grep output as an `Engineer:` issue comment before requesting approval; expected effect is no evidence-only QA FAIL; measure by counting first-pass QA FAILs for missing evidence per issue.

*Orchestrator note:* the "about 45 minutes" is the elapsed time of the re-stage run (2709 s), not commit 1 (144 s), and includes waiting. The Engineer also posted its comment without checking the `approved` label or running `make issue-hash N=35` itself, relying on the orchestrator's statement. The issue was approved and owner-authored; no harm came of it, but `AGENTS.md` says each role checks.

### QA

**What slowed you down (evidence):** my first check was a FAIL only because the evidence for the criteria was not yet posted on the issue, so I re-checked after it appeared (two QA passes, FAIL then PASS at 664dbff).
**What nearly went wrong or was blocked:** the role definitions were changed in two commits (339d547, 664dbff), so a check of only the first would have missed the OpenCode copy.
**One proposed change (file, expected effect, measure):** in `agent-kit/team/software-engineer.md`, require the hand-off to list each criterion with its evidence and every commit touched; expected effect: no FAIL for missing evidence; measured by counting QA FAILs on evidence alone over the next five issues.

*Orchestrator note:* QA wrote this without re-reading its earlier comments or the commit diffs; point 2 is inferred from the two commits and was not something it saw go wrong.

*Orchestrator observation:* all three proposals point at one idea: the issue itself should hold everything the next role needs (decisions folded into the body, evidence and tables posted before hand-off). The Engineer's and QA's proposals both edit `software-engineer.md`; the PM's edits `pm.md`. None is applied.

## Launch usage

Durations are those on the completion notices (elapsed, which can include waiting).

- PM (grooming): 1227 s, 16 tool uses
- PM (double-load decision, filing #38): 58 s, 13 tool uses
- PM (filing #39): 60 s, 14 tool uses
- Engineer (commit 1): 144 s, 44 tool uses
- Engineer (re-stage with `agent-kit.conf.template` line 27): 2709 s, 12 tool uses
- Engineer (commit 2, `AGENTS.md`): 89 s, 16 tool uses
- Engineer (commit 3a): 113 s, 18 tool uses
- Engineer (commit 3b): 55 s, 21 tool uses
- Engineer (follow-up commit): 40 s, 11 tool uses
- QA (first check, FAIL): 123 s, 25 tool uses
- QA (re-check, PASS): 65 s, 18 tool uses
- PM (reflection): 24 s, 6 tool uses
- Engineer (reflection): 26 s, 4 tool uses
- QA (reflection): 19 s, 5 tool uses

Not for #35 but in the same session: PM rewriting #20, #1 and #16 as Phases 2a, the #1 re-scope and 3a: 613 s, 85 tool uses.

## Files created or modified

- `agent-kit/README.md`, `agent-kit/blueprints.md`, `agent-kit/claude-code/hooks/guard_git.py`, `agent-kit/procedures/asking-the-human.md`, `agent-kit/setup.md`, `agent-kit/team/pm.md`, `agent-kit/team/qa-engineer.md`, `agent-kit/team/software-engineer.md`, `agent-kit/templates/AGENTS.md.template`, `agent-kit/templates/agent-kit.conf.template` (modified)
- `AGENTS.md`, `agent-kit.conf` (modified)
- `agent-kit/claude-code/agents/{pm,software-engineer,qa-engineer}.md`, `agent-kit/opencode/agents/{pm,software-engineer,qa-engineer}.md` (modified)
- `tests/test_kit_env_and_launch.py`, `tests/test_role_agents_md_pointer.py` (new)
- `_session-summaries/2026-11-01T0918Z-issue-035-orchestrator-apply-slim-shape.md` (this file)

## Decisions made by the human

- Folded the "Conventions" wording and the `.env` rule into #35, and posted the #34 mapping table on #34.
- File the `.env` shell-guard follow-up (#39), and keep `NoDanglingConventionsTest`.
- Double load: take option 1 for Claude Code and apply the same to OpenCode ("if the redirection works in Claude Code it should also work in OpenCode"), with a note to test it in OpenCode (#38). Line 3 of `team/*.md` stays as the fallback (default).
- Have the PM rewrite #20 as Phase 2a, re-scope #1 and rewrite #16 as Phase 3a; #18 waits until after Phase 2.
- Approved the final small commit (`agent-kit.conf` line 27 and the test docstring), and "all recommended" for the decision point: #1 fixes the non-ASCII filename defect inside #1; a Light change in #16 may touch only `agent-kit/README.md`, `environments.md` and `blueprints.md`; a Light issue gets its body-hash record from a short PM launch.
- Version bump: the human cuts it when ready. Sweep: skipped; the human doesn't need it yet.

## Mismatches with the spec or design docs

none (no spec yet).

## Commands to validate

**Verify:** `make verify` (PASS at d01c71e: 143 tests, claims check OK, whitespace clean, 0 assertion lines removed).

## Proposed AGENTS.md changes

none beyond d79b199 (already approved and committed).

## Temporary changes

none. `make clean-scratch` ran at the end of the issue.

## Interruptions

The first QA run ended in FAIL for missing evidence on the issue; the orchestrator posted the evidence and a fresh QA run passed. Nothing was left behind by any role.

## Unrelated problems noticed but not fixed

- `check-staged.sh` line 19 reads names without `-c core.quotePath=false`, so a forbidden `café.pem` and a protected `docs/café.md` pass pre-commit while an ASCII `plain.pem` is refused (found by the PM while rewriting #1, probed in a throwaway repo). `verify.sh` line 60 reads names the same way and was not probed. Both run live. #1 now holds the fix, with tests first.
- 339d547 cannot be reverted alone after 664dbff because both edit the same test file; revert 664dbff first.
- The `.claude/agents/*` copies in this repo still have the old "Read `AGENTS.md`" wording until the human syncs them from `agent-kit/claude-code/agents/`.
- `make assert-clean` fails on the human's `.claude/agents/pm.md` change and two untracked `proposals/` files.
- The PM changed the titles of #1, #20 and #16 to the Phase wording although only bodies were asked for (disclosed by the PM; GitHub keeps the old titles in the edit history).

## Follow-ups for the next session

- Unlabelled, waiting for the human's `approved`: #1 (re-scoped), #20 (Phase 2a), #16 (Phase 3a), #38 (OpenCode double-load test) and #39 (`.env` shell guard); also #31, #32, #33 and #26. #36 and #37 already carry `approved` but depend on #20 and #16.
- The human creates the three `tier:*` labels once, before #16 can be used.
- PM's suggested order: #1, then #20, then #36, then #16 (after #29), then #37, with #18 after Phase 2. #29 is approved and parked; it edits the same `process.md` lines as #16.
- Human steps open: sync `.claude/agents/*`; cut the version (changelog now covers #22, #24, #23, #27, #28, #25, #30, #34 and #35; suggested #35 line is in the Orchestrator comment on #35); the sweep waits for #32 and for the human.
- Reflection proposals (suggestions for the human, not applied): the PM folds mid-grooming decisions into the body; the Engineer posts mapping tables and a case-insensitive re-grep on the issue before asking for approval; the Engineer's hand-off lists each criterion with its evidence and every commit touched.
