# Issue #77: local-sandbox upgrade steps in environments.md follow kit-import.md (option A)

**Date:** 2026-11-03T16:20Z (UTC)
**Spec version:** none

## What changed and why

The subsection "Upgrading the kit in the local sandbox" still said to unzip the new kit in the clean clone and have the human commit it. It is re-sequenced for option A: the human drops the zip into the container's `.scratch/` through the dev container's VS Code window; the agent unpacks it into a new, empty folder, follows `procedures/kit-import.md`, runs `make kit-check` and `make kit-compare` in the container and commits after approval; the human then runs `git fetch sandbox` in the clean clone, reads the diff, merges and pushes. `git pull` in the container is gone and `make hooks` stays. The three protecting rules are untouched. A wording test (`upgrade_problems` and `LocalSandboxUpgradeStepsTest`) pins the phrases and refuses the old wording. Tier: standard. Branch `issue-077-environments-upgrade-step`.

**What I learned:** a phrase-presence test passes for edits that add a bad instruction next to good ones; QA showed several (for example "Commit the kit from the clean clone."). The test says it checks wording only.

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

- `agent-kit/environments.md` (protected).
- `tests/test_kit_env_and_launch.py`.

## Decisions made by the human

- Commit the protected file with `HUMAN_APPROVED=1`: approved.
- Push and open a pull request that says `Refs #77`: approved.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`. 890 tests passed; claims check OK. QA ran 10 phrase deletions, 9 rule weakenings and the old wording against the checker; each was refused.

## Proposed AGENTS.md changes

none

## Temporary changes

Worktrees `.scratch/wt-88`, `.scratch/wt-77`, `.scratch/wt-21` and `.scratch/wt-2` held the four branches' work; they are git-ignored and removed by `make clean-scratch`. One throwaway copy of the Makefile was made in `/tmp` and deleted at once (outside the folder; not needed).

## Interruptions

none. `make issue-hash` could not run (GraphQL-backed `gh` fails in this sandbox); the same hash check was done over the REST API and matched the recorded hash.

## Unrelated problems noticed but not fixed

- `agent-kit/environments.md` still says the setup guide lives outside the kit (#90).
- The wording test has no negative check for new bad instructions (a possible follow-up).

## Follow-ups for the next session

- Close #77 after the pull request is merged (orchestrator only).
- #90 (merge checklist) and #91 (kit versions) remain.
