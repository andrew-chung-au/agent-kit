# Issue #221: Compose stack: the app, Postgres with two roles, a local proxy, and one-shot migrate and seed, started by make compose-up (D11)

**Date:** 2026-11-15T03:49Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

`make compose-up` now starts Postgres 16, creates two database roles, migrates and seeds, then starts the app behind a local Caddy proxy; `make compose-down` stops it and keeps the data. This is D11 of the Deploy phase and the stack D12, D13, D14 and D17c build on.

- `compose.yaml` runs `db`, `db-init`, `migrate`, `seed`, `app` and `proxy` in that order. `migrate` connects as the owner role; `seed` and `app` as the application role, which cannot disable the audit triggers (decision 8 of the Deploy record). Only `db` and `db-init` hold the superuser's password. `app` and `proxy` are published on `127.0.0.1` only; the proxy has a fixed address (`10.231.77.10`) that the app trusts for `X-Forwarded-For`.
- `compose/db_init.py` makes the roles with a SCRAM verifier made by libpq, so no role password reaches a statement or a command line. The first version was a shell script that sent them as text (QA Medium, fixed).
- `scripts/compose_secrets.py` writes `compose.secrets` (git-ignored, mode 0600) with random values for the eight required names, never prints a value and never rewrites a line. Compose requires each name with `${NAME:?}`, so a missing one stops `docker compose` naming it.
- `STACK_PGDATA_DIR` (named volume when unset, a host path when set; `PGDATA` is a subdirectory) is the interface D17c mounts its volume on. The `STACK_*` names avoid the `SOCBOARD_` prefix because `tests/test_settings.py` fails on any other `SOCBOARD_` name in the README.
- Protected, applied by the human: the `Makefile` targets, two `AGENTS.md` Commands lines and the Layout line, and `.github/workflows/compose.yml`.

Worked by the Compose lane session, Standard tier, no separate Engineer launch. Branch `issue-221-compose-stack`, PR #223, merge commit `61e2d76`, head before merge `76f91f9`. Claim: https://github.com/andrew-chung-au/socboard/issues/221#issuecomment-6888028184. QA PASS at `56cbacb`: https://github.com/andrew-chung-au/socboard/issues/221#issuecomment-6888320638. CI on `76f91f9`: Compose job run 43672989206 (PR) and 43672985550 (push) passed, including the role refusal, the second start with three users unchanged and the volume kept after `compose-down`.

**What I learned:** the first QA found in an hour what the criterion's "or" had let through: "a psql variable the log never records" is not a way to keep a password out of statement text. I wrote that alternative myself while grooming; a criterion that lists two ways should be checked for whether each one meets the sentence before it.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

unknown (role not asked)

## Launch usage

PM: none (I groomed in this session). QA: 2 launches (FAIL at `c2383be`, PASS at `56cbacb` on the changed lines only). Active time and tool uses were not given: unknown.

## Files created or modified

- `compose.yaml`, `compose/Caddyfile`, `compose/db_init.py`, `scripts/compose_secrets.py` (new)
- `tests/test_compose.py`, `tests/test_compose_secrets.py` (new)
- `README.md` (a "Compose stack" section, one sentence in the Postgres paragraph), `.gitignore`, `.dockerignore` (one line each)
- `Makefile`, `AGENTS.md`, `.github/workflows/compose.yml` (protected, applied by the human)
- `_human-tasks/2026-11-15T0239Z-human-task-221-engineer-apply-compose-changes-and-run-stack.md`
- `_docs/records/findings/221.json`, `_session-summaries/2026-11-15T0349Z-issue-221-orchestrator-compose-stack.md` (this file)

## Decisions made by the human

- Labelled #221 `approved`; gave #205 to another agent.
- Applied the three protected changes and pushed.
- Merged PR #223.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify`. CI run 43672989100 on `76f91f9` passed; locally the Python tests passed (2340 before the fix round, 87 in the Compose, secrets and settings files after it). The frontend tests did not run here.
- **Compose stack:** `make compose-up`, then `make compose-down` (needs Docker; never run in the agent's sandbox). CI's Compose job is the evidence; step 3 of the human task (a browser sign-in on port 8080) was not recorded.
- **Test (one file):** `make test-one FILE=tests/test_compose.py`, `make test-one FILE=tests/test_compose_secrets.py`.

## Proposed AGENTS.md changes

none (the approved Commands and Layout changes are committed).

## Temporary changes

- Python environment in `.venv` (created by `uv sync` from the system Python 3.12), left for the next issue.
- Nothing is running.

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-221-1: the secrets script reads only plain `NAME=value` lines.
- F-221-2: the static Compose test does not check every use of a required name, the proxy's address range or the app's health check.
- F-221-3: a bare name in the data-directory variable makes Compose fail on an undefined volume; the README does not say so.
- F-221-4: the generated secrets file is not on the pre-commit hook's forbidden list.
- F-221-5: the README's image-variable bullet omits the role set-up service.
- F-221-6: the role set-up test's fake connection ignores parameters and the password argument.
- F-221-7: any connection error in the role set-up prints the deleted-secrets-file explanation.
- F-221-8: the bind-mounted role set-up script needs a world-readable checkout.
- F-221-9: the journeys do not read a base URL, so D12 needs a fixture change that no issue states.

## Follow-ups for the next session

- D12 (integration tests against the stack): groom it with the journeys fixture change in its body; needs #221 merged (done). `SOCBOARD_BASE_URL` appears nowhere in the code today.
- Not verified in CI yet: Caddy's `X-Forwarded-For` handling (D12), the bind mount with `lost+found` (D17c), the browser sign-in (human task step 3).
- #205 (second database URL for `make migrate`) is with another agent and must land before D20.
