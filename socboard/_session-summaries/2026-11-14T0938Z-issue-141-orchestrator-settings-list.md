# Issue #141: Read all runtime settings from one list and refuse a missing or weak secret in deployed mode

Tier: Standard (from the PM proposal).

**Date:** 2026-11-14T09:38Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

- **Settings list:** `socboard/settings.py` holds one list of every runtime variable, with its name, whether it is a secret, whether deployed mode requires it, and its rule. The README variable table, the example env file and `scripts/run_preflight.py`'s `REQUIRED` tuple are tied to that list by tests.
- **Deployed mode:** `SOCBOARD_MODE=deployed`, exact value only, turns on deployed mode. In deployed mode the app refuses at start-up, with exit 2, a missing, blank, short, edge-whitespace or one-repeated-character ingest key, a repeated-character token secret, or a blank database URL. Messages name the variable, never its value. Outside deployed mode nothing changes.
- **History:** the Engineer built it (`973305f`, summary `5ea6d97`). QA passed it at `5ea6d97`. After the Reviewer pass, the human chose three fixes (`428c582`, summary `ca8f24e`) and one AGENTS.md line, which the orchestrator committed with HUMAN_APPROVED=1 (`90a277c`). QA re-checked and passed at `90a277c`, and Assert clean passed both times.
- **Not closed yet:** `make issue-close` needs a Merge commit line, so the Close comment waits until the human pushes and merges `issue-141-settings-list`.

**What I learned:** "existing tests pass unchanged" and a tightened rule in the same issue can contradict each other. Here the Engineer found it, not grooming.

## Reflection

### PM

Reflection:
1. Slowed: the body was hashed three times (comments 6869964190, 6872418229, 6875041227); the third was an amendment after claim, which needed a human decision, an orchestrator Confirm and a re-record.
2. Nearly wrong: criterion 4 refused a repeated-character token secret "in every mode", while the issue said existing tests pass unchanged; three tests (`tests/test_make_run.py:52`, `tests/test_auth_follow_ups.py:469`, `tests/test_auth_config.py:55`) accept one. The Engineer found it; grooming did not search the tests.
3. Proposal: `_docs/agent-kit/team/pm.md` gains a bullet: when a criterion tightens a validation rule and another says existing tests pass unchanged, search `tests/` for values the new rule refuses and cite the result in the grooming comment. Effect: such conflicts are caught before approval. Measure: count of post-approval criterion amendments caused by test conflicts over the next five groomed issues (baseline: one, #141).

### Engineer

Reflection:
(1) Slowed by checking the criteria against the tests that must not change: a grep for repeated-character values (`"y" * 32`, `"s" * 32`) found three pinned tests that criterion 4 contradicted, so a round trip through the human was needed after grooming.
(2) Nearly went wrong: a refused-case test whose bad value the app accepted would have called `server.main` and started uvicorn, hanging the suite. I checked first that each invalid database URL is refused (`.scratch/check_141_urls.py`).
(3) Proposal: `_docs/agent-kit/procedures/planning.md` (definition of ready) gains a check. When a criterion says "existing tests pass unchanged" and also tightens a rule, the PM greps the tests for values the new rule would refuse. Expected effect: no criterion amendments after the Engineer starts. Measure: count the post-claim criterion amendments per issue.

### QA

Reflection:
1. Slowed: `make verify BASE=0737bb6` took about 2m50s (1886 Python tests in 133s, plus the frontend tests) to re-check a 6-file diff that touched only `settings.py` and its tests.
2. Nearly wrong: `make test-one` takes no pytest flags, so the boundary probe's printed result (zero-width-space key accepted) was nearly lost; I had to pass `PYTEST_ADDOPTS=-s` as a make variable.
3. Proposal: in `_docs/agent-kit/team/qa-engineer.md`, on a re-check, run `make test-one` on the changed test files first, then the full `make verify` once. Effect: failures show up in seconds, not minutes. Measure: time to first failure on re-checks, from the QA comment times.

## Launch usage

Figures as each completion notification gave them; resumed runs are listed separately.

- Engineer (implement): 537231 ms, 59 tool uses
- PM (amend criterion 4): 246791 ms, 16 tool uses
- PM (resumed, record new hash): 299850 ms, 23 tool uses
- QA (first check): 239809 ms, 30 tool uses
- Reviewer: 89181 ms, 17 tool uses
- PM (file follow-up #175): 93489 ms, 20 tool uses
- Engineer (resumed, fixes A to C): 291497 ms, 31 tool uses
- QA (re-check): 291378 ms, 23 tool uses
- Engineer (resumed, reflection): 16671 ms, 3 tool uses
- QA (resumed, reflection): 341155 ms, 27 tool uses
- PM (resumed, reflection): 20986 ms, 4 tool uses

## Files created or modified

- `socboard/settings.py` (new), `socboard/app.py`, `socboard/server.py` (docstring), `scripts/run_preflight.py` (`REQUIRED` line only)
- `tests/test_settings.py` (new), `README.md`, `.env.example` (new, names only)
- `AGENTS.md`: one line, human-approved
- `_session-summaries/2026-11-14T0902Z-issue-141-engineer-settings-list.md` and this file

## Decisions made by the human

- **Criterion 4 conflict:** the human chose deployed-only for the repeated-character token-secret rule. The body was amended (old hash `3b06a708...`, new hash `e8392576...`), with an Orchestrator Confirm comment and a PM re-record.
- **Names:** confirmed `socboard/settings.py` and `SOCBOARD_MODE=deployed`.
- **Review fixes now:** A (edge-whitespace ingest key), B (repeated character with whitespace between) and C (the `deployed` flags drive the check; the README claim made true by a test).
- **Follow-up:** Reviewer finding 2 (preflight in deployed mode) and the Makefile clearing of `SOCBOARD_MODE` go to #175.
- **Protected files:** the AGENTS.md Run line was approved and committed (`90a277c`). The Makefile change is in #175.
- **Sweep:** due (9 closed since 2026-11-13); the human deferred it.

## Mismatches with the spec or design docs

None found. The Deploy decision record's note on D3 matches the shipped behaviour.

## Commands to validate

- **Verify:** `make verify BASE=0737bb6`. It passed at `90a277c` with 1886 Python and 208 frontend tests.
- **Test (one file):** `make test-one FILE=tests/test_settings.py`

## Proposed AGENTS.md changes

The Run line was applied (`90a277c`). Nothing else is proposed.

## Temporary changes

None. No system changes or installs. Roles started no long-running processes. `make clean-scratch` runs after this summary is committed.

## Interruptions

None.

## Unrelated problems noticed but not fixed

None.

## Follow-ups for the next session

- **Push and close:** the human pushes `issue-141-settings-list` and merges it. Then the orchestrator posts the Close comment with `QA PASS commit: 90a277c` and the merge commit, and runs `make issue-close N=141`.
- **#175** (make run and deployed mode) needs grooming and the human's label after #141 merges.
- **QA's risks outside the criteria from the re-check, not filed:** a two-character key such as `"kK" * 8`, or a repeated character with U+200B between, passes the deployed check. Outside deployed mode, an edge-whitespace ingest key is still accepted but can never match (this predates #141). The human may want these as a follow-up.
- **Sweep:** still due.
- **Reflection proposals:** the PM and the Engineer both propose a grooming check for criteria that contradict tests. QA proposes running the changed tests first on a re-check.
