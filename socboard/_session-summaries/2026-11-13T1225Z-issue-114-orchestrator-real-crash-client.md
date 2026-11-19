# Issue #114: Add a real_crash_client test fixture

**Date:** 2026-11-13T12:25Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Claude Code worked it in the local sandbox on `main` from `cb29f37` (which holds #120 and sweep 6). Ponytail was on. Second of the three issues the human ordered before #22 (#120, #114, #104). Its text was regroomed against `origin/main` (the PM recounted 10 uses of `raise_server_exceptions`, not 7), the human labelled it, and the orchestrator applied the groomed body with `gh api` with the human's approval of the command.

- **Fixture:** `tests/conftest.py` adds `real_crash_client(real_app)`, a `TestClient` over the real app with `raise_server_exceptions=False`, beside the unchanged `crash_client(app)` (the app plus the test-only routes, which two other test files need for `/api/boom`).
- **Reuse:** the `safe_client` fixture in `tests/test_auth_api.py` is removed and its four test functions take `real_crash_client`; the inline clients in the route-walk (auth), claim and notes tests use it; the transition test uses `crash_client`, built on the same `app` it used before. The unused `TestClient` import in `tests/test_notes_api.py` is gone.
- **Stay:** four sites keep their own clients, each now with a one-line comment (the ingest key is read when the app is built, so `real_app` does not fit): `build_client`, `ingest_client` and an inline client in `tests/test_ingest_api.py`, and `journey` in `tests/test_audit_api.py`. `git grep -n raise_server_exceptions -- tests` ends at exactly 6 lines (was 10). Tests: 1508 before and after.
- **Docstring:** the ragged module docstring paragraph left by #120 in `tests/test_auth_api.py` is rewrapped (human-approved, docstring only).
- **QA:** PASS at `5e71dc6`, one launch; `make assert-clean` passed after it and after the Reviewer.
- **Reviewer:** no Must or Should fix. One nice-to-have (a redundant `client = real_crash_client` alias in the route-walk test) skipped by the human.

**What I learned:** a criterion worded "assertion lines: 0 removed" cannot be met by any rename, because the weakened-test check counts a rename as a removal plus an addition (and a docstring containing the word "assert").

## Reflection

### PM

PM: Reflection on #114 grooming.

Reflection:
1. Slowed down: the body edit needed the human, so the hash-bearing comment took two rounds (hash 42cc4395 for the old body, 06c8ff6d for the new one) instead of one.
2. Nearly wrong: criterion 5 said "0 removed", but renaming `safe_client` uses and swapping fixture parameters changes assertion-bearing lines in the diff, so a literal "0 removed" can fail the weakened-test check on a pure rename. Word such criteria as: "every removed assertion line has an identical line added in the same test (a rename or fixture swap only), and the weakened-test check passes".
3. Proposal: in `_docs/agent-kit/procedures/planning.md`, add that a criterion on assertion lines must allow renames and say how to confirm them. Effect: no QA or Engineer rework over rename counts. Measure: count FAIL or clarification comments about assertion counts on refactor-only issues over the next five such issues (target 0).

### Engineer

Engineer: Final reflection on #114.

Reflection:
1. Slowed down: the baseline `make test` took over 120 s and was moved to the background (1508 tests, 125 s), so I made the edits while it ran, then `make verify` ran the suite again (133 s).
2. Nearly went wrong: criterion 5 says "0 removed", but the weakened-test check printed "2 added, 3 removed" for a pure rename plus a deleted fixture docstring that contains the word "assert"; I had to explain each line as a warning.
3. Proposed change: in the criteria template under `_docs/agent-kit/`, word a no-assertion-change criterion as "no assertion removed or weakened; renamed lines and docstrings the check counts are explained in the comment". Effect: no criterion that a rename cannot meet. Measure: count of issues whose verify result has "assertions removed" warnings against a criterion that says "0 removed".

Ponytail: reused `crash_client` for the transition test and added one 3-line fixture instead of a helper or rename; skipped changing the four ingest-key sites, as the issue said.

### QA

QA: Reflection

Reflection:
1. Slowed down: the old-commit test count needed two tries. The first collect-only run on an archive of tests alone gave 1462 plus a collection error, because `tests/test_ponytail_metrics.py` reads `scripts/ponytail_metrics.py`; archiving `scripts` too gave 1508. `make verify` also ran past the 180s foreground limit and moved to the background.
2. Nearly went wrong: I first wrote the criterion about the commit message as PASS from the Engineer's report alone; reading the message showed it says `safe_client` had "five tests" when four test functions used it. My Edit tool was also unavailable, so I fixed the draft with a script.
3. Proposed change: in `_docs/agent-kit/procedures/verify.md`, add that a pure rename gives "N added, M removed" and a docstring containing "assert" counts, so QA compares each removed line with its added line and the PM words the criterion that way. Effect: no wording-versus-count debate. Measured by counting QA comments that need a "removed assertions" explanation.

### Ponytail

Engineer: see the `Ponytail:` line above.

## Launch usage

Tool: Claude Code. Figures copied from the completion notifications; a resumed launch's figure may be cumulative or per-resume (unknown).

- PM grooming: 90 s, 22 tool uses; hash-record resume: 17 s, 4 tool uses; reflection resume: 14 s, 3 tool uses.
- Engineer: 565 s, 44 tool uses; final reflection resume: 12 s, 3 tool uses.
- QA (PASS at `5e71dc6`): 264 s, 23 tool uses; reflection resume: 14 s, 3 tool uses.
- Reviewer: 27 s, 14 tool uses.

## Files created or modified

`tests/conftest.py`, `tests/test_audit_api.py` (a comment), `tests/test_auth_api.py`, `tests/test_claim_api.py`, `tests/test_ingest_api.py` (comments), `tests/test_notes_api.py`, `tests/test_transition_api.py`, this file.

## Decisions made by the human

- Accepted #114 as met in intent although `make verify` prints `Assertion lines: 2 added, 3 removed` (two renamed assertion lines and a docstring containing "assert"; QA and the orchestrator checked each line). Criterion 5's wording is not edited (the body is approved text); the follow-up is the Reflection proposals above, for the sweep.
- Reviewer finding (the redundant alias): skip. The two Low QA findings (the commit message says "five tests", there are four; the criterion wording): let go.
- Approved the `gh api` edit of the groomed body, and the order #120, #114, #104, #22.

## Mismatches with the spec or design docs

none. (Criterion 5 of the issue says "0 removed" and the weakened-test check counts a rename as a removal; recorded above.)

## Commands to validate

- **Verify:** `make verify` (`PASS WITH WARNINGS` at `5e71dc6`: 1508 Python, 208 frontend, whitespace clean; warnings: `Assertion lines: 2 added, 3 removed` for the renames above, and "test fixtures changed: tests/conftest.py" for the added fixture).

## Proposed AGENTS.md changes

none. (The Reflection proposals touch `_docs/agent-kit/` files; they are for the sweep.)

## Temporary changes

none. No processes started. `make clean-scratch` was not run: `.scratch/` still holds the PM's #22 change list and drafts and #104's drafts, and #22 and #104 are not done. It runs at the end of the session. (The #22 and #104 bodies are already on their issues, so the drafts are copies; nothing exists only in `.scratch/` except the unposted "Changes since the first draft" list in `.scratch/issue-22-changes.md`.)

## Interruptions

none.

## Unrelated problems noticed but not fixed

- Two lines over 100 characters in `tests/test_transition_api.py` (near lines 395 and 437), older code, not in this change; `make verify` has no line-length check (the Engineer's #120 Reflection proposes one).
- The commit message of the #114 commit says `safe_client` had "five tests"; four test functions used it (QA's Low note). History is not rewritten.

## Follow-ups for the next session

- #104 next (approved; Claim, Engineer, and the human's approval of the `Makefile` and `AGENTS.md` diff at commit), then #112 (before #22), then #22.
- Sweep proposals from the Reflections: reword criteria on assertion lines so a rename passes (the PM, Engineer and QA each proposed a place), and an `issue-edit` make target (from #120).
