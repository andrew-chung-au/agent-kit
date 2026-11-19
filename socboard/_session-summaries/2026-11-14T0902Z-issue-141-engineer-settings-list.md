# Issue #141: Read all runtime settings from one list and refuse a missing or weak secret in deployed mode

**Date:** 2026-11-14T09:02Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

`socboard/settings.py` lists every runtime variable (`SETTINGS`): name, secret, required in deployed mode, required by `make run`, and the rule. The names come from the modules that already read them, so none is written twice. `SOCBOARD_MODE` set to exactly `deployed` turns on deployed mode. Then `create_app` refuses a missing, blank, short or one-repeated-character ingest key, a missing or blank database URL, and a token secret of one repeated character, by raising `ConfigError`, so `python -m socboard.server` exits 2 and names only the variable. `scripts/run_preflight.py` takes `REQUIRED` from the list's `make_run` entries. The README has a variable table and a build-arguments line, and the example env file at the root lists names and rules. #140 had merged, so `SOCBOARD_STATIC_DIR` is in the list.

**What I learned:** three existing tests that must pass unchanged accept a one-repeated-character token secret outside deployed mode, so the "every mode" part of criterion 4 could not be done as written.

## Reflection

### Engineer

Not asked yet (the orchestrator asks after QA PASS).

## Launch usage

none

## Files created or modified

`socboard/settings.py` (new), `socboard/app.py`, `socboard/server.py` (docstring only), `scripts/run_preflight.py` (REQUIRED only), `tests/test_settings.py` (new), `README.md` (one section), the example env file (new), this summary.

## Decisions made by the human

- Names confirmed: `socboard/settings.py`, `SOCBOARD_MODE`, exact value `deployed`.
- Criterion 4 amended to deployed-only for the token secret's repeated-character rule, as proposed (new body hash `e83925...ef715`).
- After QA PASS and the Reviewer report, three fixes applied on this branch: (A) in deployed mode an ingest key with leading or trailing whitespace is refused (HTTP strips header whitespace, so it could never match); (B) the repeated-character check ignores all whitespace, so `"k " * 9` and `"s " * 17` are refused in deployed mode; (C) `check_deployed` walks the list's `deployed` flags (`DEPLOYED_CHECKS`, with a test that its keys match), and a test now checks the README table's Secret and Required columns, so the README claim holds. README and the example env file state the new rules.
- Not now: Reviewer finding 2 (the preflight in deployed mode) and clearing `SOCBOARD_MODE` in the Makefile go to a follow-up issue the PM is filing. The orchestrator commits the AGENTS.md line.

## Mismatches with the spec or design docs

Criterion 4 conflicted with the unchanged-tests rule (`tests/test_make_run.py`, `tests/test_auth_follow_ups.py`, `tests/test_auth_config.py` accept `"s" * 32` or `"y" * 32`). Resolved: the human amended the criterion to deployed-only.

## Commands to validate

**Verify:** `make verify BASE=0737bb6` (local): PASS, 1876 Python and 208 frontend tests; after the review fixes, PASS again, 1886 Python and 208 frontend tests.

## Proposed AGENTS.md changes

Under Commands, Run: add "`SOCBOARD_MODE=deployed` turns on deployed mode (see README, Runtime variables); no make target sets it." Makefile, for a later sitting: `make run` and `make backend-run` could clear `SOCBOARD_MODE`, so a value inherited from the shell cannot switch a development run into deployed mode.

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

none

## Follow-ups for the next session

The PM's follow-up issue: the preflight in deployed mode, and clearing `SOCBOARD_MODE` in `make run` and `make backend-run`.
