# Issue #271: Make the stack's project name, network prefix and trusted proxy variables in compose.yaml, with the defaults unchanged, so a second stack can reuse it

**Date:** 2026-11-15T21:30Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Dev and prod will run as two Compose stacks on one server (`_docs/decisions/2026-11-15T1840Z-dev-prod-one-server.md`). `compose.yaml` held the project name and five network addresses as literals, so a second stack could not reuse it. The maintainer asked for three variables, each defaulting to today's value so that dev changes nothing.

- `compose.yaml`:
  - `name: ${STACK_PROJECT:-socboard}`.
  - One `STACK_NET` prefix (default `10.231.77`) for the subnet, the pool, the gateway, the proxy address and the default trusted address. The layout inside the `/24` stays fixed.
  - `SOCBOARD_TRUSTED_PROXIES: ${STACK_TRUSTED_PROXIES:-${STACK_NET:-10.231.77}.10}`.
  - The header comment lists all three.
- `tests/test_compose.py`:
  - An expander for Compose's default rules, tested on its own.
  - Every rule now runs with no variables set and with an example second stack (`socboard-prod`, `10.231.78`). The expected values come from the file's own defaults, so `GATEWAY` is gone.
  - Every `ipam.config` entry is checked (QA's Low on #261).
  - A second stack that shares dev's prefix or project name is refused.
- `.github/workflows/compose.yml` (protected, the human's commit `13c576f`):
  - The gateway step now requires exactly one pool entry.
  - A new step renders the file three times: with the defaults, with the second stack, and with the server's trusted address.
- `README.md`: the three variables, and what a second stack needs.

Worked by the Compose and CI lane session, Standard tier, no separate Engineer launch.
- **Branch and PR:** `issue-271-stack-variables`, PR #274, merge commit `fe0aa0b`.
- **QA:** the first pass failed at `0f7f6be` on one Medium. The overlap refusal was only a helper assertion, not a rule. The re-check passed at `2a3c06e`: https://github.com/andrew-chung-au/socboard/issues/271#issuecomment-6900160827
- **CI evidence:** the Compose job on `13c576f` printed `pool entries and gateway: 1 10.231.77.1` and three renders with the expected names and addresses. That settles the issue's two `VERIFY:` points: Compose interpolates the top-level `name`, and it accepts the nested default.

**What I learned:** my own mutation list (12 changes to the file, all refused) missed the gap QA found. Every refusal I had tried changed the file. The overlap rule was about the variable's value, and no mutation of the file can reach that. A mutation list needs the inputs as well as the code under test.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

unknown (role not asked)

## Launch usage

PM: none (I groomed in this session). QA: 2 launches (FAIL at `0f7f6be`, PASS at `2a3c06e`). Active time and tool uses were not given: unknown.

## Files created or modified

- `compose.yaml`, `tests/test_compose.py`, `README.md`, `_docs/planning/roadmap-1-core.md` (#271 placed in the supporting list) (PR #274)
- `.github/workflows/compose.yml` (the human's commit `13c576f`)
- `_human-tasks/2026-11-15T1925Z-human-task-271-engineer-apply-render-check-step.md` (PR #274; the proposal folder was removed by `13c576f`)
- `_docs/records/findings/271.json`, `_session-summaries/2026-11-15T2130Z-issue-271-orchestrator-stack-variables.md` (this file)

## Decisions made by the human

- Asked for the follow-up and its variable names, and labelled #271 `approved`.
- Merged PR #273 first (the #261 step this issue's diff replaced), applied the CI diff, and merged PR #274.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify`. CI on the merge commit `fe0aa0b` passed (verify 43762080525, compose 43762080524, image 43762080508, postgres 43762080646). Locally, 2716 passed and 90 deselected on SQLite at the first head.
- **Test (one file):** `make test-one FILE=tests/test_compose.py`.

## Proposed AGENTS.md changes

none.

## Temporary changes

- Mutation scripts and worktrees under `.scratch/` (git-ignored). Nothing is running.

## Interruptions

- The diff for `compose.yml` was written against #261's step. It could apply only after PR #273 carried that step to `main`.

## Unrelated problems noticed but not fixed

- F-271-1: the render check compares six values, not the whole render with `main`'s.
- F-271-2: a project name with a trailing space or capitals is not refused by the test.
- F-271-3: no test pins the other stack variables' defaults.
- F-271-4: nothing stops a fixed `name:` on the stack network.

## Follow-ups for the next session

- The prod outlines #266, #267 and #269 can now set `STACK_PROJECT`, `STACK_NET` and `STACK_TRUSTED_PROXIES` instead of changing `compose.yaml`.
- #238 (deploy to dev) has passed QA. PR #277 can merge as is; the workflow is applied after #237's first deploy.
