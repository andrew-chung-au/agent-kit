# Issue #86: Add the ingest field limits to the OpenAPI contract

**Date:** 2026-11-12T06:13Z (UTC)
**Spec version:** e68c39e

## What changed and why

Tier: Standard (from the PM proposal; no tier label). A supporting issue that must land before #14. Ponytail trial: not a control issue. Epoch: no move under Amendment 2.

- `openapi.yaml`, `IngestRequest` only: `maxLength` 200 on `source`, `type`, `asset` and `title`, 10000 on `description`; `minLength: 1` on all six required fields. 11 lines.
- CI was the test loop (run 43163674050: VERIFY: PASS, 121 Python and 154 frontend tests). The human ran `make contract-check` once in the dev container (`openapi.yaml: OK`), because contract-check is not in verify yet (queued in the epoch batch, item 6).
- The Engineer's and QA's own check scripts each pass on the real file and fail on copies with a limit removed or out of range (written under `.scratch/`, never by editing `openapi.yaml`).
- Branch `issue-86-ingest-limits`; this summary is on it (one PR for the issue). QA PASS commit `c024c82`, one QA launch.

**What I learned:** two of my steps ran out of order because I issued them in one parallel batch: the claim comment went up just after the Engineer launch, and QA launched alongside the Engineer's comment step instead of after it. Neither changed the result (QA checked the pushed commit and its comment landed after the Engineer's), but launches that depend on each other must be sequential.

## Reflection

### PM

unknown (role not asked)

### Engineer

From comment 6816199392, unchanged:

Reflection:
(1) Slowed down: no package index here, so no YAML parser or validator; I wrote a line-based check script plus two mutated copies in `.scratch/` (the script is the only proof I could run myself), and the draft needed four separate edits once CI and human results arrived.
(2) Nearly wrong: the draft said verify and the contract check were "not checked", which went stale once the CI run and the dev-container run came back; posting it unedited would have understated the evidence. The contract check is also outside verify, so CI alone would never have covered it.
(3) Change: `Makefile` (verify target) to run `make contract-check`; expected effect is that CI catches an invalid `openapi.yaml` without a human run; measure by checking, on the next issue that touches `openapi.yaml`, that the CI log shows the contract check line and that no human-run task is needed for it.

### QA

From comment 6816216614, unchanged:

Reflection:
(1) Slowed down by `gh issue view` failing on a blocked GraphQL call, and by the CI job log being too large for one tool result (it was saved to a file outside the workspace that I could not search); I fell back to the issue JSON and a small script that filters the log.
(2) Blocked: my search of the saved log file returned nothing because it sits outside the workspace, so the first CI-VERIFIED attempt gave no `VERIFY:` line until I re-fetched the log through a `.scratch/` script.
(3) Proposed change: `_docs/agent-kit/team/qa-engineer.md` should say "read CI logs with a `.scratch/` script that prints only the `VERIFY:` and pass-count lines, and read the issue from `.scratch/issue-<n>.json`, not `gh issue view`"; expected effect is no failed or oversized call in the CI-VERIFIED step; measure by counting failed or truncated tool calls in the QA launch.

## Launch usage

Active time and tool uses: unknown (Kiro Web gives neither). Engineer 2. QA 1 (PASS). Handovers: one human run (`make contract-check`).

## Files created or modified

`openapi.yaml`. This file.

## Decisions made by the human

- #60 does not move the epoch.
- #86 approved (labelled).

## Mismatches with the spec or design docs

none.

## Commands to validate

- **Contract check:** `make contract-check` (`openapi.yaml: OK` at `c024c82`, human-run).
- **Verify:** `make verify` (CI run 43163674050: VERIFY: PASS).

## Proposed AGENTS.md changes

none.

## Temporary changes

- `make clean-scratch`: NOT run; housekeeping is on hold.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- Nothing automated guards the six `minLength: 1` lines until #14's direct tests exist (`tests/openapi_compare.py` drops `minLength`).

## Follow-ups for the next session

- #11, then #12 to #14 (all approved and checked ahead). #14 now has its contract limits.
- The Engineer's Reflection (wire contract-check into verify) is already epoch-batch item 6.
- QA's Reflection (a `.scratch/` CI-log filter, and the issue JSON instead of `gh issue view`): sweep 4 evidence.
