# Issue #21: pull request template (Refs #N, never Closes) and the human task for installing it

**Date:** 2026-11-03T16:20Z (UTC)
**Spec version:** none

## What changed and why

Kiro's pull requests had inconsistent bodies, and one contained a close keyword. The kit now has `agent-kit/templates/github/pull_request_template.md` (54 words): a `Refs #N` line, one sentence forbidding Closes, Fixes and Resolves (because only the orchestrator closes issues, after QA PASS), and four short sections (what changed, what `make verify` ran, protected paths, not verified). `tests/test_pull_request_template.py` pins the wording with mutation cases; a `blueprints.md` row lists it. The `.github/` copy is the human's: `_human-tasks/2026-11-03T1620Z-human-task-021-engineer-merge-prs-and-copy-pr-template.md` gives the step-by-step commands and also covers merging the four pull requests. Tier: standard. Branch `issue-021-pr-template`.

**What I learned:** QA's first run failed the checker: look-alike or zero-width letters in a close keyword and a duplicated forbidding sentence passed. Both are now refused; a fresh QA passed.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- Engineer work: orchestrator session.
- QA (fresh subagent), first run: FAIL on the checker's mutation cases; time and tool uses unknown.
- QA (fresh subagent), re-check: PASS; time and tool uses unknown.

## Files created or modified

- `agent-kit/templates/github/pull_request_template.md` (new, protected path).
- `agent-kit/blueprints.md` (one row).
- `tests/test_pull_request_template.py` (new).
- `_human-tasks/2026-11-03T1620Z-human-task-021-engineer-merge-prs-and-copy-pr-template.md` (new).

## Decisions made by the human

- Commit the protected files with `HUMAN_APPROVED=1`: approved.
- Cloud handover pointer ("read `_docs/agent-kit/templates/github/pull_request_template.md` and follow it; GitHub applies the template only to web-UI pull requests") goes to #52 / the claim comment as a proposal: approved.
- The human copies the template into `.github/` from a clean clone; the steps are in the human task file: approved. Nothing was written under `.github/`.
- Push and open a pull request that says `Refs #21`: approved.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`. 898 tests passed. Always-loaded files (`AGENTS.md`, `process.md`) grew by 0 words. QA ran 103 mutations on the checker; markup that splits a keyword (`Clo<b></b>ses`, entities) is still accepted by `check()`, though the real template is clean.

## Proposed AGENTS.md changes

none

## Temporary changes

Worktrees `.scratch/wt-88`, `.scratch/wt-77`, `.scratch/wt-21` and `.scratch/wt-2` held the four branches' work; they are git-ignored and removed by `make clean-scratch`. One throwaway copy of the Makefile was made in `/tmp` and deleted at once (outside the folder; not needed).

## Interruptions

none. `make issue-hash` could not run (GraphQL-backed `gh` fails in this sandbox); the same hash check was done over the REST API and matched the recorded hash.

## Unrelated problems noticed but not fixed

- `agent-kit/setup.md` has an issue-form paragraph and no matching PR template paragraph (optional).
- Whether the cloud tool applies the template is unverified.

## Follow-ups for the next session

- Post the cloud handover line on #52 or the claim comment.
- After the human installs `.github/pull_request_template.md`, the byte-identical test starts checking it.
- Close #21 after the pull request is merged and the template is installed (orchestrator only).
