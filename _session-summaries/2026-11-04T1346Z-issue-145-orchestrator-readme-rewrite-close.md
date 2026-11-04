# Issue #145: Rewrite the READMEs for the merged kit and dev container repo, ahead of 1.10

**Date:** 2026-11-04T13:46Z (UTC)
**Spec version:** none

## What changed and why

The root `README.md` and `agent-kit/README.md` described only the kit. They now cover this repo as both the kit and the dev container: two labelled install paths (kit only, kit plus dev container), the push-check image and `AGENT_PUSH_CHECK_IMAGE`, the Compose variant, and the installed-files workflow, with links to `agent-kit/environments.md`. Built by Kiro (PR #147, commit `2b73ff5`, "Refs #145" so it would not auto-close the issue), merged 2026-11-04T13:40Z as `7532746`.

The PM groomed #145 (filed after the human asked for it) with scope, install-path and sequencing decisions; the work waited for #115, #117 and #118 to land, so every claim matches merged behaviour. QA passed it at `2b73ff5`. QA also found one error outside the criteria: both READMEs said to use the Compose variant "instead of the standard recipe", but `environments.md` says its three files go next to the standard `setup.sh`. I fixed that line in both READMEs after the merge and committed it on its own with the human's approval (`72747a1`, local, not yet pushed); no further QA launch, since the fix matches `environments.md`'s own wording and `make test` passed (1331 tests).

The version line, the "Unreleased" changelog and `KIT_VERSION` were not touched: the human cuts 1.10.

**What I learned:** none beyond this record.

## Reflection

unknown (role not asked).

## Launch usage

- PM (filing and grooming #145): about 1.3 min (76,181 ms), 22 tool uses.
- QA: about 3.8 min (229,849 ms), 49 tool uses.
- Kiro's build is outside this session's launches.

## Files created or modified

`README.md`, `agent-kit/README.md` (PR #147); the same two files for the Compose wording fix (`72747a1`). This record is the only other file added.

## Decisions made by the human

- Labelled #145 `approved`; accepted the PM's recommendations (both READMEs in one issue, two labelled install paths, version cut kept out); merged PR #147 and asked for the "instead" wording fix after merging; approved its commit.

## Mismatches with the spec or design docs

none known.

## Commands to validate

**Verify:** QA's `make verify` on the PR merged into `origin/main`: PASS, 1331 tests, claims check and whitespace OK; GitHub CI on the PR passed; `make assert-clean` PASS. After my wording fix: `make test` PASS, 1331 tests.

## Proposed AGENTS.md changes

none.

## Temporary changes

none.

## Interruptions

none.

## Unrelated problems noticed but not fixed

The "Unreleased" changelog does not mention the README rewrite; add a line at the 1.10 cut.

## Follow-ups for the next session

Cut 1.10: fold "Unreleased" into "Changes in 1.10", bump the version line and `KIT_VERSION`, and approve the changelog.
