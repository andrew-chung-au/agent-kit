# Issue #102: A request body that cannot be parsed gets 500 instead of 422

**Date:** 2026-11-13T01:49Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Standard (from the PM proposal; no tier label). This was a #13 follow-up, done before #14, which takes JSON from outside. It is the first issue run with ponytail on. Draft PR #105.

- **The fix:** `socboard/errors.py`, in `http_exception_handler`. FastAPI's own body-parse failure is `HTTPException(400, "There was an error parsing the body")`, raised for invalid UTF-8, very deep nesting, or a number over Python's digit limit. It now answers 422 `validation_error` with the contract's fixed message. Every route inherits it. Other 400s and the existing 418 case still give 500.
- **Tests:** 13 login bodies in `tests/test_auth_api.py`, plus a non-login route and a direct handler check in `tests/test_backend_errors.py`. No existing test was edited.
- **CI at `ee78288`:** pull-request run 43337507125 and push run 43337485180 both report `811 passed`, frontend `157 passed`, `Assertion lines: 11 added, 0 removed` and `VERIFY: PASS`.
- **QA:** PASS at `ee78288`. QA confirmed in FastAPI 0.162.5 (`routing.py:495-498`) which cases raise the 400 and which already raised 422.
- **Reviewer (ponytail):** verdict "Ship", with four nice-to-have findings. The human labelled all four `correct-minor`, and none was applied.
- **Also on this branch:** a one-line `AGENTS.md` fix (commit `5fedf79`, human-approved). The Reviewer's report now starts `Orchestrator: Reviewer report`, because `make issue-comment` refuses `Reviewer:`.

**What I learned:** the Reviewer step needs a comment prefix the posting script accepts. It was found on the first issue that used it, and fixed by changing one line.

## Reflection

### PM

unknown (role not asked)

### Engineer

From comment 6840115815, unchanged:

Reflection:
1. Slowed down: FastAPI is not installed here and `uv` cannot run; I fetched `routing.py` at the locked tag through `gh api` (the output exceeded the tool limit and needed a second grep on the saved file).
2. Nearly wrong: I ran `git add` and `git diff --check` in parallel against the one-at-a-time instruction (no harm, both read-only or index-only); and the new tests were never executed, so a wrong assumption (for example `caplog` capture in the TestClient thread) would show only in CI.
3. Proposal: add the make target `make src-of PKG=fastapi FILE=routing.py` (Makefile, protected) to read a locked dependency's source; expected effect: no web fetch needed when `uv` cannot run; measured by the number of commands used to read dependency source in an issue.

### QA

unknown (QA's comment has no Reflection block).

### Ponytail

Engineer: "one `if` in the shared handler and table-driven tests; I cut a custom request class, a new test route and a handler docstring rewrite."

## Launch usage

- Active time and tool uses: unknown, because Kiro Web reports neither.
- Tool: Kiro. Model: unknown.
- Launches: PM 1 (grooming), Engineer 1, QA 1 (PASS), Reviewer 1.

## Files created or modified

`socboard/errors.py`, `tests/test_auth_api.py`, `tests/test_backend_errors.py`, `AGENTS.md` (the one-line prefix fix), this file.

## Decisions made by the human

- #14's "Depends on" line is left unchanged, because #102 runs first anyway (the orchestrator's recommendation, accepted).
- Finding 102-1: correct-minor. Finding 102-2: correct-minor. Finding 102-3: correct-minor. Finding 102-4: correct-minor. QA had raised none of them, and none is applied.
- The Reviewer report is posted as `Orchestrator: Reviewer report (#N)`, with the matching `AGENTS.md` wording.
- The Engineer's `make src-of` proposal is kept as evidence for the next sweep; no action now.

## Mismatches with the spec or design docs

none.

## Commands to validate

- **Verify:** `make verify` (CI runs 43337507125 and 43337485180 at `ee78288`).

## Proposed AGENTS.md changes

The prefix fix above is approved and committed.

## Temporary changes

- No temporary system changes.
- The orchestrator ran `make assert-clean` twice in the same batch as the QA and Reviewer launches, so those runs don't count. Each was re-run after the launch finished, and both passed.
- `make clean-scratch` is deferred to the end of the session.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- `make ponytail-metrics` gives git figures only after the Close comment exists, because it reads the `QA PASS commit:` line from it.

## Follow-ups for the next session

- #14, then #15. #14 keeps its own order test for a non-JSON body with no key; the shared mapping is done here.
