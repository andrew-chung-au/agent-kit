# Issue #14: Ingest API: POST /api/alerts with an API key

**Date:** 2026-11-13T02:49Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Heavy, from the PM proposal (there is no tier label). This is the one entry point that is not a user, and it takes untrusted input. Kiro Web worked it by the human's ruling; Claude Code waits for #16. Ponytail was on, the third issue in the ponytail group. Draft PR #108.

- **The route:** `POST /api/alerts` (`socboard/ingest.py`) with the `X-API-Key` route dependency, which raises 401 `invalid_api_key` and is in `socboard/auth.py`.
  - Checks run in the contract's order: 401 comes before a schema 422, and a body that isn't JSON gets 422 even with no key.
  - All six fields are validated with the #86 length limits, and the timestamp must be RFC 3339 with an offset.
  - One transaction writes the alert, its `New` case, the #12 score, `ingested_at` and one `append_audit` entry, with a single commit.
  - The key never appears in a response, log line or audit entry.
  - The decision record is `_docs/decisions/<timestamp>-ingest-api-key.md`, with its index row. The README names the key's environment variable and says there is no de-duplication.
- **Rounds:** two Engineer rounds. Round 1 at `cd15b18` had 2 CI failures:
  - The existing #11 test flagged `ApiHTTPException` in `ingest.py`. Without editing the test, the key dependency moved to `auth.py`, which that test already treats as the authentication module.
  - Hour 24 was accepted, because Python 3.12's `fromisoformat` takes it. Timestamp parts now go to `datetime(...)`, which refuses it.
- **Merge:** `main` (with #102 and #99) was merged in at `5453a2c` before QA.
- **CI at `5453a2c`:** pull-request run 43350949551 shows 1230 passed, 157 frontend passed, `Assertion lines: 171 added, 0 removed` and VERIFY: PASS. The push run 43351139057 has one warning, which is #99's comment-only line arriving with the merge.
- **QA:** the first launch passed at `5453a2c`, with an 80-check bypass script and no failures. A fresh second launch (a subagent) also passed at `5453a2c`, with Lows 1 to 4.
- **Reviewer (ponytail):** five lean findings, with an estimate of about 55 code lines and 150 test lines that could go. None was applied; they move to #110.

**What I learned:** `tests/test_data_audit.py`'s list of HTTP-layer file names catches each new route module: `auth.py` (#13), the ingest key (#14) and `cases.py` (#15). The human ruled to add names one at a time for now, and #107 will put the list in one place.

## Reflection

### PM

unknown (role not asked)

### Engineer

From the completion comment, unchanged:

- The riskiest assumptions, which only CI can confirm: the engine `begin`/`commit` event list, pydantic's `Z` output for UTC times, and `httpx` accepting bytes header values.
- I would re-read #102's change to `tests/test_backend_order.py` after the merge, so my order test and its test do not overlap.

### QA

Second launch, unchanged:

Reflection:
- Slowed down: one broad `grep_search` over the whole repo for a settings name returned lines of files I was told to avoid, so I had to write a disclosure instead of a blind review (visible in the search output for `SOCBOARD_TOKEN_SECRET`).
- Nearly went wrong: the independence of this launch; the leak above came from a search, not from a read.
- Proposed change: in `_docs/agent-kit/team/qa-engineer.md` (Code review, Heavy second launch), add "when searching, exclude `.scratch/qa-*`, `.scratch/engineer-*` and `.scratch/issue-*.json`, or limit `includePattern` to `socboard/socboard/**`"; expected effect: a blind second launch stays blind; measure by counting forbidden-file lines in search output across the next five Heavy second launches (target 0).

### Ponytail

Engineer: "Level `full`: I reused the #13 patterns (router, session dependency, `ApiHTTPException`) and added no dependency or abstraction; I skipped per-source keys, rate limits and de-duplication, as the issue says." The Reviewer still found about 55 code lines that could go, mostly the hand-written timestamp parser.

## Launch usage

Active time and tool uses are unknown, because Kiro Web reports neither. Tool: Kiro; model: unknown. Launches: Engineer 2, QA first launch 1 (PASS), QA second launch 1 (PASS), Reviewer 1, PM 1 (filing #110).

## Files created or modified

- `socboard/ingest.py` (new), `socboard/auth.py`, `socboard/schemas.py`, `socboard/errors.py`, `socboard/app.py`
- `tests/test_ingest_api.py` (new), `tests/test_ingest_contract.py` (new)
- `README.md`
- `_docs/decisions/<timestamp>-ingest-api-key.md` (new), `_docs/index.md`
- `_docs/planning/roadmap-1-core.md` (#110 placed, #107 note)
- this file

## Decisions made by the human

- Kiro Web works #14 and #15; Claude Code takes #16 and #17, and waits until #15 merges.
- Reviewer findings: 14-1 useful (smaller; unverified until pydantic's behaviour is proven on every case); 14-2 useful (smaller); 14-3 correct-minor; 14-4 wrong (the 16-character minimum is in the approved decision record and stays); 14-5 correct-minor. QA had raised none of them. None was applied; all go to #110 with QA's Low items.
- `make contract-check` was not run, because CI doesn't run it. Accepted, since `openapi.yaml` is unchanged.
- On #15: `cases.py` was added to the HTTP-layer list in `tests/test_data_audit.py`. `getCase` keeps the contract's 422 as the one named difference.

## Mismatches with the spec or design docs

none.

## Commands to validate

- **Verify:** `make verify` (CI runs 43350949551 and 43351139057 at `5453a2c`).

## Proposed AGENTS.md changes

none.

## Temporary changes

none. `make clean-scratch` is deferred to the end of the session.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- GitHub closed #99 when its PR merged, because a commit subject began "Fix #99". Launch messages now forbid "Fix/Fixes/Closes #N" in commit subjects.
- `README.md` is over the index's 600-word limit; it already was before #14.
- `AGENTS.md` says Python 3.12, while CI ran 3.14.4 (#100).

## Follow-ups for the next session

- #15 is done in CI and needs QA. Then Claude Code takes #16.
- #110 (simplify the ingest route) and #107 (simplify the audit guard, including the HTTP-module list) come before Deploy.
- Sweep 5 evidence: the blind-second-launch search leak, and the commit-keyword auto-close.
