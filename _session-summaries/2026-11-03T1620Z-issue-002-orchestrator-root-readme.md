# Issue #2: public root README, refreshed onto main

**Date:** 2026-11-03T16:20Z (UTC)
**Spec version:** none

## What changed and why

Kiro's earlier branch (commit fd3a441, based on f4621a4, QA PASS, no pull request) was re-applied onto current main and its claims re-checked. Changes since: the OpenCode bullet in "Not verified by automation" now says the permission-logging plugin exists, the human checked most permission rules by hand on OpenCode 1.19.5 (the `--no-verify` rule by tests only), and #20 is still open (#38 is closed, so it is no longer named); a tier note in "How it works"; CI worded as "where the project has it"; "Where things live" gains `_human-tasks/`, `_docs/`, `.devcontainer/` and the tool config. Install steps are still clone-and-copy because #9 (releases) is open and there are no tags. `tests/test_root_readme.py` now accepts `_human-tasks/` paths; `agent-kit.conf` protects the root `README.md`. Tier: standard. Branch `issue-002-root-readme`.

**What I learned:** the recovered commit was reachable on GitHub by SHA even though no branch or pull request pointed at it.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- Engineer work: orchestrator session.
- QA (fresh subagent): active time and tool uses unknown (not given by the tool).

## Files created or modified

- `README.md` (new; protected once `agent-kit.conf` lands).
- `tests/test_root_readme.py` (new).
- `agent-kit.conf` (protected: `'README.md'` added to PROTECTED).

## Decisions made by the human

- Commit the protected files with `HUMAN_APPROVED=1`: approved.
- Push and open a pull request that says `Refs #2`: approved. The README ships after #9 per the earlier decision; the human decides when to merge (the human task file lists this as a choice).

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`. 902 tests passed. QA re-verified every claim and every issue number named (#9, #10, #20 open; #38 closed) against main, and ran the test's must-be-refused cases.

## Proposed AGENTS.md changes

none

## Temporary changes

Worktrees `.scratch/wt-88`, `.scratch/wt-77`, `.scratch/wt-21` and `.scratch/wt-2` held the four branches' work; they are git-ignored and removed by `make clean-scratch`. One throwaway copy of the Makefile was made in `/tmp` and deleted at once (outside the folder; not needed).

## Interruptions

none. `make issue-hash` could not run (GraphQL-backed `gh` fails in this sandbox); the same hash check was done over the REST API and matched the recorded hash.

## Unrelated problems noticed but not fixed

- The README names a date-stamped `_human-tasks` file; renaming it needs a README edit (the test catches it).
- "CI" and "Light skips grooming" wording was loosened after QA's note.

## Follow-ups for the next session

- The human reads the prose and the three linked summaries before merging.
- Close #2 only after the merge (orchestrator only).
