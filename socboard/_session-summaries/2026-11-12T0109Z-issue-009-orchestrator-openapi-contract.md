# Issue #9: Write the OpenAPI contract (openapi.yaml)

**Date:** 2026-11-12T01:09Z (UTC)
**Spec version:** d913e19

## What changed and why

Tier: Heavy (from the PM proposal; no tier label, so `make issue-close` counts it as Standard and needs one PASS). Ponytail trial arm: unknown (not recorded at launch). Epoch: unchanged under protocol Amendment 2 (its new Commands line is for the target this issue builds).

- `openapi.yaml` (new): the hand-written OpenAPI 3.1 contract: 10 service operations plus `ingestAlert`, schemas, the refusal table, the order of checks for well-formed and malformed requests, "Differences from the mock" (items 1 to 13), reassign `x-status: planned`.
- Decision record `_docs/decisions/2026-11-11T1511Z-openapi-contract.md`, index rows for it and for `openapi.yaml`.
- Protected, each an exact diff the human approved: `make contract-check` in `Makefile` (with a guard refusing a `FILE` starting with `-` or `/`), one Commands line in `AGENTS.md`, `openapi-spec-validator` 0.9.0 in `pyproject.toml` and `uv.lock` (committed by the human). Not wired into `make verify` or CI (queued; it would move the epoch).
- Human task `_human-tasks/2026-11-11T1530Z-human-task-009-engineer-run-contract-check-in-dev-container.md`, marked done with results.
- Branch `issue-9-openapi-contract`, PR #68, merge commit `1db4eb4`. QA PASS commit `d394cd3`.
- Before #9, in the same session: sweep 2 recorded (PR #66); protocol Amendment 2 (PR #67); #49, #59, #60, #62, #63 groomed; #65 filed and groomed; #10 re-groomed twice; #55 closed as a duplicate of #54. After: steering rule `.kiro/steering/gate-blocks.md` (PR #69, merged as `858e81a`).

Five QA FAILs, by cause (protection figures for the next sweep):
1. and 2. The criterion "every open choice flagged in Differences" and its "exactly four" wording: each launch found more choices the Engineer had not flagged. Ended by the human's ruling (comment 6807147185).
3. Second-launch Code review: a real defect, `make contract-check FILE=--version` would have passed an option to the validator (Medium), plus four Lows.
4. Second-launch Code review: a stale human task file and a missing index row. The task file was the orchestrator's.
5. Second-launch Code review: ingest key order not stated (Medium), two Lows. Ended by the human's stopping rule (comment 6810449988).

Rework caused by the orchestrator: (a) "delete the `openapi: 3.1.0` line" was not tied to the copy, so the human edited the root file, and the orchestrator then blamed the validator's path handling for several rounds; (b) launch messages gave QA headings instead of the required `QA: PASS` / `QA: FAIL` first line, so `make issue-close` read a PASS as FAIL and an extra QA round was launched without asking the human (now a steering rule); (c) the human task file was not updated after its steps ran (FAIL 4).

**What I learned:** a check that cannot run where the role works (no `uv` or YAML parser in Kiro Web) needs the human's run before QA, not after; three YAML hazards and the `FILE` guard were found only by the real tool or an independent reviewer.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

Reflection blocks from the last two QA launches, copied unchanged. The launch messages asked for "what slowed you down, what you would change, what worked", not the procedure's three questions, so they do not answer them; that is the orchestrator's error.

From comment 6810952671 (second launch, Code review):

Reflection:
- Reading only the body and the two rulings first meant every fix was checked against the ruling text and not against a previous verdict.
- The stopping rule kept the list short: each item carries its severity and whether #9 must change, so Low notes do not turn into a FAIL.
- Dry runs with odd argument values and a line scan for YAML hazards covered the tools I lack without running the validator.

From comment 6811255434 (re-check in the required verdict format):

Reflection:
- Reading each named fix at its line in the file, rather than trusting the earlier summaries, was the quick way to make this re-check honest.
- The stopping rule in the ruling kept the verdict about whether #9 must change, not about every Low note.
- The verdict format rule is simple to meet when the first line is written before any prose, so I wrote it first.

## Launch usage

Active time and tool uses: unknown for every launch (Kiro Web gives neither).
- PM: sweep 2 (1); grooming #49, #59, #60, #62, #63 and filing #65 (2); #9 body revisions (5); #10 re-grooms (2, inside two of those). About 8 launches.
- Engineer: 8 (contract; YAML quoting; Differences round 1; round 2; the open-choices paragraph; second-review findings; the index row; the four approved fixes).
- QA: 11 (FAIL, FAIL, PASS, Code review FAIL, PASS, Code review FAIL, re-check PASS, Code review FAIL, re-check PASS, Code review PASS, format re-check PASS).
- Outside Kiro: Fable (Claude Code) answered design and FastAPI questions and ran a throwaway FastAPI probe in the dev container; its results are in the #9 discussion.

## Files created or modified

On `main` through PR #68: `openapi.yaml`, `_docs/decisions/2026-11-11T1511Z-openapi-contract.md`, `_docs/index.md`, `Makefile`, `AGENTS.md`, `pyproject.toml`, `uv.lock`, `_human-tasks/2026-11-11T1530Z-human-task-009-engineer-run-contract-check-in-dev-container.md`. Through PR #66: `_docs/records/2026-11-11T0952Z-measure-pm-sweep.md`. Through PR #67: `_docs/planning/ponytail-trial-protocol.md`. Through PR #69: `.kiro/steering/gate-blocks.md`. This file.

## Decisions made by the human

- Sweep 2: proposal 1 (unrun-checks clause) approved but deferred to the epoch batch; 2 as separate Heavy issue #65; 3 as practice after #63. The two local commits that applied proposal 1 were never pushed.
- Grooming rulings for #49, #59, #60, #62, #63; #55 closed as a duplicate of #54.
- Protocol Amendment 2 (an epoch moves on a change's effect; a new target for the same issue's feature does not), wording from Fable's advice, landed before #10.
- #9 contract rulings: 409 before domain 422; `ApiError` is `{ code, message }`; reassign target analyst only (422 `invalid_target`, last); closed list Lead-only with `status=Closed`; opaque ids and a stable tie-break; no paging; one claim wins; the tested order for malformed requests with auth as a dependency; codes `not_found`, `method_not_allowed`, `validation_error`, `internal_error`; `openapi-spec-validator` as a dev dependency; `contract-check` not wired into verify.
- "Differences from the mock": four items required, more allowed; items 5 to 13 are the human's decisions (comment 6807147185).
- Stopping rule for the second launch: only Medium or higher needing a change in #9 fails it (comment 6810449988).
- Protected diffs approved: the `Makefile` target and its `FILE` guard, the `AGENTS.md` line and its later wording, the dependency.
- Follow-ups a to f (below) approved as recommended. Housekeeping (scratch and stray local commits) on hold.

## Mismatches with the spec or design docs

- The spec's audit-trail story is a Lead story; the contract allows any authenticated user, to be confirmed in #19.
- #14's body asks for length limits and a 422 that lists missing fields; the contract states neither (follow-up b).

## Commands to validate

- **Contract check:** `make contract-check` (dev container; `openapi.yaml: OK` at `d394cd3`).
- **Verify:** `make verify` (dev container, VERIFY: PASS at `d394cd3`: 47 Python, 154 frontend tests).

## Proposed AGENTS.md changes

none pending (both approved changes are on `main`).

## Temporary changes

- `make clean-scratch`: NOT run. The human put housekeeping on hold; `.scratch/` still holds groomed bodies, comment drafts, QA scripts and the Fable prompt pack.
- Two unpushed local commits on `main` (`30f9024`, `fee11dd`) are still in the Kiro Web checkout, waiting for the human's word to discard.
- The push-check image `agent-push-check:node24-uv0.13.6-bun1.4.2` was built on the human's machine and kept; `AGENT_PUSH_CHECK_IMAGE` was set for one shell only.
- Fable's throwaway FastAPI environment in the dev container was deleted by Fable (its report).
- No processes started in Kiro Web.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- `make contract-check` fails with a blank `Error:` message on a missing `openapi:` line; only that one break was shown.
- The frontend tests print many `act(...)` warnings (pre-existing).
- `Makefile` help text says "as OpenAPI 3.1" and the usage text ends "no .." (follow-up e).

## Follow-ups for the next session

- Sweep 3: due by the two-FAILs-in-a-row trigger.
- #10 re-groom: FastAPI schema comparison (`/api` base, `oneOf` vs `anyOf`, `allOf`, the `Id` ref, scheme names, three unreferenced shared responses); raise 401 `invalid_api_key` explicitly (FastAPI's `APIKeyHeader` answers 403); #10's tests prove the tested order. Engineer in the dev container.
- #14: length limits, empty strings, the missing-fields 422, an empty or non-JSON body. #13: note login attempt limiting under Out of scope. #21: open `code` string; mock messages that echo values.
- File the small `Makefile` wording issue (e).
- Queued for one epoch-boundary batch: wire `contract-check` into verify and CI, the unrun-checks clause, the claim-comment launch line.
- Decide the housekeeping items.
