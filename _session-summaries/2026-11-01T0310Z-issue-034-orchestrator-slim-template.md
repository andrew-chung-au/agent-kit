# Issue #34: Slim the always-loaded context, part 1 (Phase 1b-a)

**Date:** 2026-11-01T03:10Z (UTC)
**Spec version:** none

## What changed and why

`agent-kit/templates/AGENTS.md.template` is restructured to: project paragraph, Commands, Project settings, Non-negotiables, one "Enforced by hooks" line, a 10-line "Read when" trigger index, then Project gotchas, with one SHARED START / SHARED END marker pair around Non-negotiables through Read when. Step-specific rules moved to `software-engineer.md` (`## Commits`), `process.md` (Issue comments, Planning, Lifecycle QA step, Definition of done) and the new `procedures/processes.md`. `check-claims.py` now verifies heading anchors in kit-path spans, with tests in `tests/test_claims_anchors.py` and one expectation changed in `tests/test_claims.py` (`team/pm.md#commits` to `team/pm.md#`, not a weakened test). Committed as 76b6090 with the human's approval; QA PASS at 76b6090. The 26-bullet mapping table is on the issue as an Orchestrator comment.

Words: template 1107 to 780 (-327); `software-engineer.md` 292 to 411; `process.md` 1508 to 1616; `processes.md` 0 to 87. The four files total 2907 before and 2894 after.

Live-edited code: `agent-kit/scripts/check-claims.py` runs from the working tree, so this change altered `make test` and `make verify` for itself.

**What I learned:** the issue body's figures were wrong in three places (27 bullets vs 26, `_docs/README.md` vs `_docs/index.md`, a test expectation); the PM caught them by counting at HEAD.

## Reflection

### PM

**What slowed you down (evidence):** unverified figures in the issue body: "27 bullets" was this repo's AGENTS.md count (the template has 26), and `_docs/README.md` should have been `_docs/index.md`; I fixed three body errors by counting and grepping at HEAD.
**What nearly went wrong or was blocked:** `tests/test_claims.py` had a case treating `team/pm.md#commits` as skipped, which the change had to alter, so it could have read as a weakened test; I added a criterion saying it is not.
**One proposed change (file, expected effect, measure):** `agent-kit/team/pm.md` grooming steps gain "recount every number, path and anchor the issue cites at HEAD before commenting". Expected effect: fewer body corrections. Measure: body corrections per groomed issue in `PM:` comments, over the next five issues.

### Engineer

**What slowed you down (evidence):** about 67 minutes elapsed: nine staged paths, a long approval request, then the human's first commit attempts failed on a `--` typo; the mapping table lived only in the approval request, so the Orchestrator had to post it on the issue later.
**What nearly went wrong or was blocked:** dangling "Conventions" references remained outside my closed file list; found only after the work, so a grep for renamed headings was missing.
**One proposed change (file, expected effect, measure):** in `agent-kit/team/software-engineer.md`, require the approval request to give the commit command as a ready-to-paste block and to post any mapping table as an issue comment first, plus a grep for renamed headings across the repo before staging. Expected effect: no retyped commands or later table reposts, no dangling references. Measure: failed commit attempts and post-QA fix-ups per protected-file issue, from session summaries.

*Orchestrator note:* the Engineer gave no commit command; the `--` typo was in a command typed by the human, and the orchestrator's approval request had the correct form. The "about 67 minutes" is the completion notice's duration and includes waiting, not active work time.

### QA

**What slowed you down (evidence):** the criterion asking for the 26-bullet mapping table in the Engineer's issue comment had no table on the issue, so I rebuilt the mapping myself against `76b6090~1` (see my PASS comment, criterion 5).
**What nearly went wrong or was blocked:** `check-claims.py` was live-edited by the commit under test, so `make verify` used the new anchor logic; I had to read its tests to trust the run. The `.env` shell read is unenforced.
**One proposed change (file, expected effect, measure):** `agent-kit/team/software-engineer.md` should require the Engineer to paste any table the issue asks for into its issue comment before QA starts. Expected effect: QA skips the rebuild. Measure: QA tool uses spent on mapping across the next three issues with such a criterion.

## Launch usage

Durations are those on the completion notices (elapsed, which can include waiting).

- PM (grooming): 77 s, 21 tool uses
- Engineer: 4033 s elapsed, 46 tool uses
- QA: 76 s, 21 tool uses
- PM (reflection): 18 s, 5 tool uses
- Engineer (reflection): 22 s, 5 tool uses
- QA (reflection): 25 s, 8 tool uses

Not for #34 but in the same session: PM filing phases 1b-b, 2b, 3b and 1b-a as #34 to #37: 205 s, 43 tool uses.

## Files created or modified

- `agent-kit/README.md`, `agent-kit/blueprints.md`, `agent-kit/process.md`, `agent-kit/scripts/check-claims.py`, `agent-kit/team/software-engineer.md`, `agent-kit/templates/AGENTS.md.template`, `tests/test_claims.py` (modified)
- `agent-kit/procedures/processes.md`, `tests/test_claims_anchors.py` (new)
- `_session-summaries/2026-11-01T0310Z-issue-034-orchestrator-slim-template.md` (this file)

## Decisions made by the human

- Approved the #34 commit as it stood. Two of the human's own commit attempts failed on a `--` typo; the orchestrator committed with a corrected command, and the human's later attempts found nothing to commit.
- Agreed to the orchestrator's recommendations: fold the "Conventions" wording and the `.env` rule into #35 for the PM to handle when it grooms, and post the mapping table on #34.
- Chose to file the phase issues (1b-a, 1b-b, 2b, 3b), now #34 to #37, ahead of the side issues.
- Sweep: skipped; the human doesn't need it yet. Version bump: the human cuts it when ready.

## Mismatches with the spec or design docs

none (no spec yet).

## Commands to validate

**Verify:** `make verify` (PASS: 130 tests, claims check OK, whitespace clean, 0 assertion lines removed).

## Proposed AGENTS.md changes

none. (#35 applies the new shape to this repo's `AGENTS.md`.)

## Temporary changes

none. `make clean-scratch` ran at the end of the issue.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- "Conventions" wording remains in `team/pm.md`, `team/qa-engineer.md`, `team/software-engineer.md` line 3, `procedures/asking-the-human.md` line 12, `setup.md` (lines 39, 45, 87), `README.md` (lines 76 and 95, where line 95 tells projects to update a block that no longer exists) and the `guard_git.py` docstring. Planned for #35.
- A shell `cat .env` is blocked only by the Read/Edit deny rules, not by a hook, and "use `.env.example`" no longer appears in the template. Planned for #35.
- The anchor check looks only at the first resolved file when a span resolves in both the doc's folder and the kit root, and it ignores setext headings. No current doc is affected.
- `make assert-clean` fails on the human's `.claude/agents/pm.md` change and two untracked `proposals/` files.

## Follow-ups for the next session

- #35 (approved): groom with the Conventions and `.env` points added to its scope.
- `make sweep-due` says "due: no sweep recorded"; the sweep waits for #32 and the human.
- Reflection proposals (suggestions for the human, not applied): PM recounts every cited number, path and anchor at HEAD; Engineer approval requests give a ready commit command, post tables on the issue first and grep for renamed headings; QA gets any required table before it starts.
