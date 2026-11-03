# Issue #032: Push check install target and dev container corepack/nvm fixes

**Date:** 2026-10-19
**Spec version:** d3a8f11

## What changed and why

- Part A (committed `eb2e64b`, protected, human-approved): `Makefile` adds `install: frontend-install`, adds `install` to `.PHONY`, and guards `frontend-test` when `frontend/node_modules` is missing with `frontend/node_modules is missing: run make install first`. `AGENTS.md` updates the Install and Dependencies lines and adds the push-check gotcha.
- Part B (committed `7207911`, human-approved): `.devcontainer/devcontainer.json` adds `"nvmVersion": "0.40.8"`; `.devcontainer/setup.sh` prepends the pinned node bin path and runs `corepack disable` without `sudo`; `.devcontainer/devcontainer-lock.json` is unchanged. The human reviewed the recipe and rebuilt the container.
- QA PASS at `eb2e64b` after the rebuild: no `yarn`, `yarnpkg`, `pnpm` or `pnpx` shims in a fresh non-interactive `sh`; nvm `0.40.8`; node `v24.22.0`; npm `11.19.1`; uv `0.13.1`; `make install verify` PASS.
- Human push gate on 2026-10-19 from the clean clone: `sandbox/main` and `HEAD` at `eb2e64b`; `node:24.22.0-bookworm` pulled (digest `sha256:14078204b6bb268c107ceff6d3c43f45a888105e5c2b18b14c32b3409d93a1b0`); `command -v bash git make node npm` printed `/usr/bin/bash`, `/usr/bin/git`, `/usr/bin/make`, `/usr/local/bin/node`, `/usr/local/bin/npm`; the gated push ran `make -C . install verify` (npm ci, 518 packages, 10/10 tests, whitespace PASS, weakened tests none), printed `VERIFY: PASS`, and pushed `c1896e4..eb2e64b main -> main`.

## Files created or modified

- `Makefile` (protected): `install` target, `.PHONY` entry and `frontend-test` guard; committed `eb2e64b`.
- `AGENTS.md` (protected): Install line, Dependencies line and Project gotcha; committed `eb2e64b`.
- `.devcontainer/devcontainer.json` and `.devcontainer/setup.sh`; committed `7207911`.
- `.devcontainer/devcontainer-lock.json` unchanged. No dependency or lockfile changes.
- `_docs/ai-usage-log.md` and this summary, updated at close-out.
- `.scratch/` held the guard and audit scripts; `make clean-scratch` removed them.

## Decisions made by the human

- Part B: option (b), `corepack disable` in `.devcontainer/setup.sh`.
- Follow-up #33 for the remaining #15/#20 review findings and hardening B-D.
- Approved the protected `Makefile`/`AGENTS.md` diffs and the `.devcontainer/` commit; rebuilt the container.
- Set `AGENT_PUSH_CHECK_IMAGE=node:24.22.0-bookworm` and ran the real gated push.
- Product-first order after #32: #21, then #22, then #23; #33 deferred.

## Mismatches with the spec or design docs

None. #32 is tooling and process; `_docs/specs.md` does not cover it.

## Commands to validate

- **Install:** `make install` runs `npm --prefix frontend ci`; it is idempotent.
- **Test:** `make test`: 2 files, 10 tests passed.
- **Verify:** `make verify`: PASS, no warnings, after `make install`.
- Guard: `make -C .scratch/issue32-makefile-test frontend-test` with no `frontend/node_modules` printed `frontend/node_modules is missing: run make install first` and exited non-zero.
- Post-rebuild: each of `yarn`, `yarnpkg`, `pnpm`, `pnpx` absent in a fresh `sh`; `nvm --version` `0.40.8`; node `v24.22.0`, npm `11.19.1`, uv `0.13.1`.
- Push check (human, clean clone): `docker run --rm node:24.22.0-bookworm bash -c 'command -v bash git make node npm'` printed five paths; `AGENT_PUSH_CHECK_IMAGE=node:24.22.0-bookworm git push` ran `make -C . install verify`, printed `VERIFY: PASS`, and pushed `c1896e4..eb2e64b`.

## Proposed AGENTS.md changes

Applied in `eb2e64b` with human approval. No pending changes.

## Temporary changes

- The human pulled `node:24.22.0-bookworm` on the host to run the gate; it remains in the host's Docker cache. The human rebuilt the dev container.
- No agent started a process or changed system configuration. `frontend/node_modules` is a git-ignored install, recreated by `make install`.
- The `.devcontainer/` change's undo is to revert `7207911` and rebuild; it was not needed.

## Interruptions

None.

## Unrelated problems noticed but not fixed

- `4895a12` (`opencode.json` read-only `rg` allow rule) is a separate commit, not part of #32.
- The PM's #21 grooming found that #33 hardening D's "exactly one line" `.npmrc` wording needs updating when #33 is next touched; it is recorded on #21, not fixed here.

## Follow-ups for the next session

- #21 is next in the product-first order, then #22, then #23; #33 is deferred.
- The clean clone is at `eb2e64b`; the close-out docs commit is unpushed and will ride with the next gated push.
- No open #32 items.
