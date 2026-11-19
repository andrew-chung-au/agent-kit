# Issue #261: Pin the stack network's gateway to 10.231.77.1 in compose.yaml, because Docker chose 10.231.77.128

**Date:** 2026-11-15T20:21Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

On the server the maintainer measured that Docker gave the stack's network the gateway `10.231.77.128`, the first address of its `ip_range`, because `compose.yaml` named no gateway. The app sees the gateway as the address of every request through host Caddy, and the deploy script (#237) and `terraform/README.md` assume `10.231.77.1`. So the trusted proxy address would have been wrong on the first deploy.

- `compose.yaml`: `gateway: 10.231.77.1` in the stack network's one `ipam.config` entry, with a comment giving the measured reason.
- `tests/test_compose.py`: gateway rules. The gateway must be set, be the documented address, be inside the subnet and outside the pool, and not be the network, broadcast or proxy address. The proxy must be outside the pool. There are 12 refused cases, plus a cross-check that `terraform/README.md`'s "The forwarded address" paragraph names the same address.
- `README.md`: one sentence on the pinned gateway.
- `.github/workflows/compose.yml` (protected, the human's commit `e42efce`): a step that prints the running network's gateway and fails unless it is `10.231.77.1`.

Worked by the Compose and CI lane session, Standard tier, no separate Engineer launch.
- **Code:** branch `issue-261-pin-stack-gateway`, PR #264, merged as `95d2ae3` at head `361cf32`.
- **CI step:** PR #264 was merged before the human pushed the step, so it reached `main` through PR #273 (merge commit `6441838`).
- **QA:** PASS at `361cf32`: https://github.com/andrew-chung-au/socboard/issues/261#issuecomment-6899355026
- **Evidence on `main`:** at `6441838` the Compose job printed `gateway 10.231.77.1` (run 43755370681), and verify, postgres and image passed.

**What I learned:** the merge and the human's protected commit are two separate steps, and nothing checked their order. I read only "PR merged" and "CI step applied" and nearly closed the issue on a `main` that did not run the check. Checking `git merge-base --is-ancestor` on the protected commit found it (F-261-5).

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

unknown (role not asked)

## Launch usage

PM: none (groomed in this session). QA: 1 launch (PASS at `361cf32`). Active time and tool uses were not given: unknown.

## Files created or modified

- `compose.yaml`, `tests/test_compose.py`, `README.md` (PR #264)
- `.github/workflows/compose.yml` (the human's commit `e42efce`, PR #273)
- `_human-tasks/2026-11-15T1826Z-human-task-261-engineer-apply-gateway-check-step.md` (PR #264; the proposal folder was removed by `e42efce`)
- `_docs/records/findings/261.json`, `_session-summaries/2026-11-15T2021Z-issue-261-orchestrator-pin-stack-gateway.md` (this file)

## Decisions made by the human

- Labelled #261 `approved`.
- Applied the CI step (`e42efce`), merged PR #264 and then PR #273.
- Removed the throwaway measuring network `peerprobe` from the server before #237's first run.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify`. CI on the merge commit `6441838` passed (verify 43755370642, compose 43755370681, image 43755370650, postgres 43755370657).
- **Test (one file):** `make test-one FILE=tests/test_compose.py`.

## Proposed AGENTS.md changes

none.

## Temporary changes

- Mutation scripts and worktrees under `.scratch/` (git-ignored). Nothing is running.

## Interruptions

- PR #264 merged without the CI step. I opened PR #273 to carry it, and the human merged it.

## Unrelated problems noticed but not fixed

- F-261-1: only the first `ipam.config` entry was checked. Taken into #271.
- F-261-2: the README cross-check gives the same message for a reworded paragraph as for a wrong address.
- F-261-3: the README sentence is one long parenthetical.
- F-261-4: a second stack needed its own literals. Filed as #271.
- F-261-5: PR #264 merged before the protected commit was on its branch.

## Follow-ups for the next session

- #271 (variables for the project name, network prefix and trusted proxy) has passed QA and the human's CI step. PR #274 waits for the human's merge.
- #238 (deploy to dev from CI) is claimed and being built.
