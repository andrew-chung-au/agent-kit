# Issue #190: Build one container image of the app and the built frontend, and build and check it in CI

**Date:** 2026-11-14T19:24Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

One container image now serves the API and the built frontend from one origin, and CI builds it on every push and pull request and checks what is in it.

- `Dockerfile`: stage 1 builds the frontend with Node and bun (`VITE_USE_MOCK` set with `ENV`, the two build arguments, `VITE_API_BASE_URL` unset); stage 2 is `python:3.12-slim-bookworm`, installs the locked runtime dependencies only (`uv sync --locked --no-dev`, so the Postgres driver is included), copies `socboard/` and the built `dist`, and runs as the numeric user 10001. The start command is `python -m socboard.server --allow-non-loopback-host` in exec form: one worker, no `FORWARDED_ALLOW_IPS`, no `SOCBOARD_TRUSTED_PROXIES`, no secret setting in the file. Base images are pinned by digest.
- `.dockerignore`: keeps the git folder, scratch, node modules, env files (the example one excepted), databases and journals, tests, docs, summaries, human tasks, terraform and CI files out of the build context.
- `scripts/check_image_files.py` (standard library only): checks an export of the image's files and refuses env-file names, `.git`, `tests`, test files, node modules, database files, a demo credential, a Google fonts host, any line matching the secret list, and server or worker output in the build. It never prints a matched value.
- `tests/test_dockerfile.py` (60 cases) and `tests/test_check_image_files.py` (33 cases) run in `make verify` without Docker.
- `.github/workflows/image.yml` (protected, committed with `HUMAN_APPROVED=1` after the human approved the exact diff): build, compare the image's Python minor version with `.python-version`, export and check the app files, expect exit 2 from deployed mode with no settings, then run with throwaway settings, migrate and seed with `docker exec`, and expect `/api/health` and the entry page.
- README "Container image" section; the `AGENTS.md` Layout line (protected, approved); a human task file for the one local build.

Worked by the Hardening session, Standard tier, no Engineer launch. Branch `issue-190-container-image`, PR #198, merge commit `f86e2a7`, head `2533047`. Claim: https://github.com/andrew-chung-au/socboard/issues/190#issuecomment-6881298429. QA PASS at `2533047`: https://github.com/andrew-chung-au/socboard/issues/190#issuecomment-6881808013.

**What I learned:** the first CI build of the image passed every step. The Deploy draft's run step was wrong in three ways the PM caught (all three seed passwords, a database URL, a writable SQLite path), and my draft passed the checker `app/` where it takes the folder holding `app/`.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

unknown (role not asked)

## Launch usage

PM: 1 launch (grooming, comment 6878026896); active time and tool uses were not given: unknown. QA: 1 launch (PASS at `2533047`); unknown.

## Files created or modified

- `Dockerfile`, `.dockerignore`, `scripts/check_image_files.py` (new)
- `tests/test_dockerfile.py`, `tests/test_check_image_files.py` (new)
- `README.md`, `_human-tasks/2026-11-14T1719Z-human-task-190-orchestrator-build-image-locally.md`
- `.github/workflows/image.yml` (new), `AGENTS.md` (Layout line): protected, approved
- `_session-summaries/2026-11-14T1924Z-issue-190-orchestrator-container-image.md` (this file)

## Decisions made by the human

- Confirmed the two corrections to the CI run step and the checker (the Confirm comment 6878187592 on the issue).
- Labelled `approved`; approved the exact diffs of `image.yml` and the `AGENTS.md` Layout line; merged PR #198.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI runs 43622822443 and 43622827932 on `2533047`, plus the image job 43622822455 and 43622827923; local Python tests 2158 passed; the frontend tests did not run locally, bun is not installed in this sandbox).
- **Test (one file):** `make test-one FILE=tests/test_dockerfile.py` (60 passed), `make test-one FILE=tests/test_check_image_files.py` (33 passed).

## Proposed AGENTS.md changes

none (the approved Layout line is committed).

## Temporary changes

- Python environment in `.scratch/venv` and `.scratch/uv-cache` (about 94 MB, approved), linked as `.venv`; still in place for #191; to be deleted when the Hardening work ends.
- Nothing is running.

## Interruptions

none

## Unrelated problems noticed but not fixed

QA listed gaps outside the criteria, none a failure, left as they are unless the human asks:
- The static test accepts `USER 00`, `USER 0000` and `USER +0` (root to Docker), and the "named paths only" check misses `COPY ./. ./`, `COPY .* ./` and `COPY ** ./`; the real Dockerfile has neither.
- The checker compares names case-sensitively and scans line by line, so an upper-case env-file name or a credential split over two lines is missed.
- `.dockerignore` has no `*.sqlite*` pattern (the checker would refuse such a file).
- The human task file says the build has a "dependency install" stage the Dockerfile does not have, and step 4 says "Risk: none" where the template wants what would print if the rule fails.
- No CI run shows the wrong-Python-minor refusal; only the static test does.

## Follow-ups for the next session

- The human builds the image once locally and records the result in the human task file (base image digests, whether `bun run build` needs Node as well as bun).
- D11 (Compose) needs D5a, D6a and this image; D12 must test the forwarded address through the proxy.
