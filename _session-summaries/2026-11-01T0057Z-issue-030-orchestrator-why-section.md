# Issue #30: Add a required Why section to the issue template

**Date:** 2026-11-01T00:57Z (UTC)
**Spec version:** none

## What changed and why

`agent-kit/templates/task-template.md` now starts with a required `## Why` section before Goal, so every groomed issue states the problem and its evidence in the same place. `agent-kit/team/pm.md` now says "all five sections". `tests/test_task_template.py` pins the heading order (Why, Goal, Acceptance criteria, Out of scope, Constraints). Committed as 4fb8504 with the human's approval; QA PASS at 4fb8504.

Words: template 113 to 148 (+35); `pm.md` 623 unchanged; always-loaded total 4586 unchanged; all kit docs 16113 to 16148.

**What I learned:** a pre-staged unrelated file in the index forced a path-limited commit, and the human's first commit attempt aborted for lack of a message.

## Reflection

### PM

**What slowed you down (evidence):** pm.md's line number had moved (18 to 19) because #27-#29 also edit it, so I re-grepped "four sections" across agent-kit/, tests/, AGENTS.md and .claude/ to be sure of the count.
**What nearly went wrong or was blocked:** the claim "no template test exists" came from a search, and the claims check reads code spans, not headings, so nothing would have caught a dropped Why until I added the pinned-order test.
**One proposed change (file, expected effect, measure):** add to agent-kit/team/pm.md "cite sections by name, not line number" (+8 words); expected effect: fewer stale references in grooming comments; measure by counting wrong line numbers in PM comments over the next five issues.

### Engineer

**What slowed you down (evidence):** a stray pre-staged `.claude/settings.json` already in the index, which I had to spot and exclude before staging explicit paths; the Orchestrator also had to post my results comment because I was told not to comment.
**What nearly went wrong or was blocked:** committing the unrelated staged file with the issue's change; the human's first commit attempt aborted for lack of a message.
**One proposed change (file, expected effect, measure):** in `agent-kit/team/software-engineer.md`, require the approval request to include a ready commit message and `git diff --cached --name-only`, and state that the Engineer posts its results comment unless told otherwise. Expect fewer aborted commits and orchestrator-posted comments; measure by counting both in the next five session summaries.

### QA

**What slowed you down (evidence):** the budget criterion needed a before/after word count at `4fb8504~1` and `4fb8504`, so I wrote `.scratch/qa30-check.sh`; the no-other-issue-touched criterion needed a full `gh issue list --state all` timestamp sweep.
**What nearly went wrong or was blocked:** `make verify` showed uncommitted `.claude/agents/pm.md`, `.claude/settings.json` and `proposals/*`, which I had to separate from the commit's 3-file diff.
**One proposed change (file, expected effect, measure):** add a `make budget-diff REF=<commit>` target (Makefile, `agent-kit/scripts/`) printing always-loaded word counts before and after; expected effect is no hand-written count script per QA check; measure by QA scratch scripts for budget checks, now one per issue, falling to zero.

## Launch usage

- PM (grooming): 34 s, 12 tool uses
- Engineer: 61 s, 19 tool uses
- QA: 47 s, 13 tool uses
- PM (reflection): 20 s, 8 tool uses
- Engineer (reflection): 23 s, 6 tool uses
- QA (reflection): 23 s, 6 tool uses

## Files created or modified

- `agent-kit/templates/task-template.md` (modified)
- `agent-kit/team/pm.md` (modified)
- `tests/test_task_template.py` (new)
- `_session-summaries/2026-11-01T0057Z-issue-030-orchestrator-why-section.md` (this file)

## Decisions made by the human

- Approved the #30 commit (ran the commit command themselves; it aborted for lack of a message, and the orchestrator re-ran it with a message).
- Version bump: the human cuts 1.10 themselves when ready; changelog now covers #22, #24, #23, #27, #28, #25 and #30.
- Sweep: skipped for now; the human doesn't need it yet and wants to understand how "due" works first.
- Not yet answered: whether the PM files the phase issues (1b-a, 1b-b, 2b, 3b), and whether #29, #32 and #33 wait until the human ranks them.

## Mismatches with the spec or design docs

none (no spec yet).

## Commands to validate

**Verify:** `make verify` (PASS: 120 tests, claims check OK, no whitespace errors).

## Proposed AGENTS.md changes

none.

## Temporary changes

none. `make clean-scratch` ran at the end of the issue.

## Interruptions

none. The human's first commit attempt aborted for lack of a message; nothing was left behind.

## Unrelated problems noticed but not fixed

- `make assert-clean` fails on the human's `.claude/agents/pm.md` and staged `.claude/settings.json` changes and two untracked `proposals/` files.
- `.claude/settings.json` was staged before the Engineer started, which forced a path-limited commit.

## Follow-ups for the next session

- The human's decision on the phase issues and on the order of #29, #32 and #33.
- `make sweep-due` says "due: no sweep recorded"; it waits for #32.
- Reflection proposals (suggestions for the human, not applied): cite sections by name in pm.md; commit message and name-only listing in the Engineer's approval request; a `make budget-diff` target.
