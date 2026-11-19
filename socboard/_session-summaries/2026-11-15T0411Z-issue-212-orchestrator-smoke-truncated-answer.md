# Issue #212: Smoke check: a truncated answer is a failed step, and a non-ASCII URL exits 2 (follow-up to #191)

**Date:** 2026-11-15T04:11Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

The smoke check no longer calls a half answer whole, and refuses a URL it cannot send before it does anything with it. Both came from the third QA of #191 (findings F-191-1 and F-191-2).

- `socboard/smoke.py`: a body that ends before a valid `Content-Length` has arrived, or a chunked body that ends before its last chunk, fails the step with `the answer was cut short`, for any HTTP status (so a cut 401 or 429 prints no code from the partial body). A timeout and the size cap still win; a cut step 4 poll fails at once and is not polled again. A URL with any character above ASCII is refused with exit 2 and one fixed line, `the URL must hold ASCII characters only`, before it is split, so no host is converted or looked up and nothing of the URL is echoed.
- `tests/test_smoke.py`: 50 new cases, among them a raw stub that sends a length it does not deliver for each of the five steps, three chunked cuts, whole answers that still pass, time-wins cases, and the non-ASCII rule with a check that no name lookup or request happens.
- `README.md`: one sentence in the smoke paragraph. No protected file was changed.

Worked by the Hardening session, Standard tier, no Engineer launch. Branch `issue-212-smoke-truncated-answer`, PR #230, head `5496291` (plus this summary and the findings file on the same branch). Claim: https://github.com/andrew-chung-au/socboard/issues/212#issuecomment-6888792195. QA PASS at `5496291`: https://github.com/andrew-chung-au/socboard/issues/212#issuecomment-6888986912.

**What I learned:** the clock check at the top of the read loop already turns a slow body into `timed out`, so the order of the cut-short test after the loop only matters for a chunked cut; a mutation of that branch is what showed the chunked time-wins test was real, and a mutation of the post-loop order did not.

## Reflection

### Engineer

(1) The first mutation check passed unexpectedly: swapping the cut-short test before the `expired` test did not fail a test, because the loop-top clock check already ends a slow body as `timed out`. (2) Nothing blocked; the chunked branch carries the ordering and a second mutation proved its test. (3) None.

### QA

(1) Slowed: `make verify` cannot finish in this sandbox, so the verify criterion needed a manual split. Evidence: it stopped at `frontend-test` (bun not installed, `vitest is missing`) and printed `VERIFY: FAIL`, so I ran the Python tests and read CI separately. Time lost: unknown. (2) Blocked: the frontend step was not run here; CI success on `5496291` was the only evidence for it. Nearly wrong: unknown. (3) Proposal: `Makefile` (the `verify` target): when bun is missing, print `frontend: not run (bun missing)` and end `VERIFY: PARTIAL`, not FAIL. Effect: a QA comment needs no explanation for the FAIL line. Measure: count QA comments whose Verify section explains a bun-caused FAIL, before and after; unknown today.

### PM

(1) Slowed by http.client's undocumented short-body behaviour: I wrote a raw-socket experiment (`.scratch/exp212.py`) per case. The project pins Python 3.12 but only 3.11.15 was installed, so 3.12 behaviour was not run. Time spent: unknown. (2) Nearly went wrong: a cut check placed before the `expired` test would have broken the timeout tests (`tests/test_smoke.py` lines 567-604). I fixed the order in the criteria. (3) Proposal: add a line to `_docs/agent-kit/procedures/planning.md` telling the PM to record, for stdlib-dependent criteria, the interpreter versions run against the pinned one. Expected effect: fewer unverified-version caveats reaching the Engineer. Measure: count of such caveats in grooming comments per ten issues. Baseline: unknown.

## Launch usage

PM: 2 launches (grooming, comment 6888701776; reflection, comment 6888994030). QA: 2 launches (PASS at `5496291`; reflection, comment 6888992269). Active time and tool uses were not given: unknown.

## Files created or modified

- `socboard/smoke.py`, `tests/test_smoke.py`, `README.md`
- `_docs/records/findings/212.json` (new)
- `_session-summaries/2026-11-15T0411Z-issue-212-orchestrator-smoke-truncated-answer.md` (this file)

## Decisions made by the human

- Labelled `approved` before and after grooming; approved the PM's four recommendations and the replacement body (Confirm comment 6888759343, hash 258b0adc...); approved installing the Python environment under `.scratch/`.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI runs 43674632823 (push) and 43674637692 (pull_request) on `5496291`, plus image, compose and postgres; local Python tests 2389 passed; the frontend tests did not run locally, bun is not installed in this sandbox).
- **Test (one file):** `make test-one FILE=tests/test_smoke.py`.

## Proposed AGENTS.md changes

none

## Temporary changes

- Python environment in `.scratch/venv` and `.scratch/uv-cache` (about 94 MB, approved) and the `.venv` symlink: deleted with `make clean-scratch` and `rm .venv` after this summary was committed (see below).
- Nothing is running.

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-212-1: an answer cut inside its headers is read as a 200 with an empty body, so step 1 passes.
- F-212-2: a chunked answer cut after its final zero-size line, or inside its trailers, passes step 1.
- F-212-3: a Content-Length written as two equal numbers is read as no length, so a short body passes.
- F-212-4: ASCII URLs that carry look-alikes of a real host are accepted.
- F-212-5: a connection reset in the middle of a body fails with the generic text, not the cut-short text.
- F-212-6: no test covers a cut step 4 poll while the queue window is the limit, or a cut in the headers or trailers.
- F-212-7: in the smoke tests the URL-rules section header now sits above the two new sections.

Full record: `_docs/records/findings/212.json`.

## Follow-ups for the next session

- The sweep gives F-212-1 to F-212-7 their groups and rulings in `_docs/records/findings-index.jsonl`; F-212-1, F-212-2 and F-212-3 belong with the `checker-looser-than-intent` group, which then has six open findings.
- The QA proposal to print `PARTIAL` when bun is missing touches the protected `Makefile`; the PM proposal touches `procedures/planning.md`. Both are for the human to rule on at the next sweep.
