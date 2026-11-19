# Issue #74: Add the health route to the OpenAPI contract

**Date:** 2026-11-12T03:36Z (UTC)
**Spec version:** d913e19

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Ponytail trial arm: control (no treatment marker). Epoch: unchanged under protocol Amendment 2 (no command a role runs changes; no rule sentence). A supporting issue, not one of the five baseline Core issues.

- `openapi.yaml`: `GET /health` (`getHealth`, `security: []`, tag `health`, one 200 response with `HealthResponse`, `status` as `const: ok`), the top-level `health` tag, the mapping-table row, and the bearer-token sentence corrected to name `login`, `ingestAlert` and `getHealth`.
- `tests/test_backend_health.py`: `test_health_is_in_the_contract` replaces the absence check #10 left (the absence assertion was removed on purpose; `make verify BASE=origin/main` warned about it, and the Engineer comment gives the reason).
- `tests/test_backend_openapi.py`: `test_health_route_equals_the_contract` compares the contract with the app's generated schema; a matching fragment test and four refused ones (status as integer, an extra property, status not required, bearer security).
- Branch `issue-74-health-contract`, PR #82. QA PASS commit `53138d0`, one QA launch, no FAIL.
- Before #74: #11 re-checked against the contract and #10, re-groomed with the human's four rulings (Confirm and PM re-record; still Heavy); #80 filed and placed in the epoch batch (PR #81).

**What I learned:** `make verify` without `BASE=origin/main` again said "No test files changed" on a branch that changed two test files (the trap recorded on #51 and fixed by #65, still in the epoch batch); asking for the `BASE=origin/main` run before QA caught the removed assertion and its reason in time.

## Reflection

### PM

unknown (role not asked)

### Engineer

From comment 6813572759, unchanged:

Reflection:
(1) Slowed down: nothing could run in Kiro Web (no package index), so the contract form and the tests were checked by hand with a line-based YAML audit script, and the real results came only from the human's later run.
(2) Nearly went wrong: the `const: ok` form of the status property was a guess about what `app.openapi()` generates; a wrong guess would have failed the comparison test. It held, and the first draft also named a helper script that no longer existed.
(3) Change: add to `_docs/agent-kit/environments.md` a rule that, where checks cannot run, the Engineer drafts the human-task file for them at the start, listing each unconfirmed guess; measured by counting the hand-over round trips between draft and human results on the next such issue (target: one).

### QA

From comment 6813604141, unchanged:

Reflection:
(1) Slowed down: the tool-search results for the test files came back empty twice because the glob needed the repo folder in front of `tests/`; the same two searches then worked at once, so about two extra round trips.
(2) Nearly went wrong: the bearer-security refused test looks like it guards the contract's `/health`, but it only compares two hand-made operations; I caught it by reading what each argument was built from, not from the test name.
(3) Change: in `_docs/agent-kit/team/qa-engineer.md`, add under Code review one line asking the reviewer to name, for each refused test, the object it builds its inputs from (contract, app or hand-made); expected effect: tests that guard only a helper are labelled as such in the comment; measured by counting QA comments on the next few test-changing issues that state this.

## Launch usage

Active time and tool uses: unknown for every launch (Kiro Web gives neither).
- PM: #74 grooming (2), #11 contract check and re-groom (2), #80 filed (1). 5 launches.
- Engineer: 2 (contract and tests; completion and Reflection comments).
- QA: 1 (PASS).
- Handovers: one dev-container terminal run by the human (`make contract-check`, the broken copy, `make test`, `make verify`), then `make verify BASE=origin/main`.

## Files created or modified

Through PR #82: `openapi.yaml`, `tests/test_backend_health.py`, `tests/test_backend_openapi.py`. Through PR #81: `_docs/planning/roadmap-1-core.md`. This file.

## Decisions made by the human

- #74: `status` in the form `app.openapi()` generates; also update the description sentence, add the `health` tag and the mapping row.
- #11: integer primary keys exposed as decimal strings; two database CHECKs for the closing reason; no assignment table; `SOCBOARD_DATABASE_URL`. #11's Engineer runs in Kiro Web.
- #80 placed in the epoch batch.
- QA's notes outside the criteria for #74 left as they are (the refusal check removed the `openapi:` line rather than `/health`'s responses; accepted).

## Mismatches with the spec or design docs

none.

## Commands to validate

- **Contract check:** `make contract-check` (`openapi.yaml: OK` at `53138d0`).
- **Test (all):** `make test` (121 Python, 154 frontend tests at `53138d0`).
- **Verify:** `make verify BASE=origin/main` (PASS with the stated warning).

## Proposed AGENTS.md changes

none.

## Temporary changes

- `make clean-scratch`: NOT run; housekeeping is on hold at the human's request.
- Two unpushed local commits on `main` in the Kiro Web checkout (`30f9024`, `fee11dd`) still wait for the human's word.
- One process slip: the PM edited its `.scratch/` draft for #11 with a small Python script instead of the edit tool (the "no rewrite scripts" rule); only an untracked draft was affected, and the posted body is what the human approved.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- `make verify` without `BASE=origin/main` reports "No test files changed" on a branch's own upstream (#65, epoch batch).
- `gh issue view` fails in Kiro Web on a host mismatch; long issue dumps are cut off (#73).

## Follow-ups for the next session

- #11 (data model, Heavy): claim, then the Engineer in Kiro Web; its first stop is the dependency list (SQLAlchemy, Alembic) for the human to approve; two QA launches.
- The epoch batch lands after #11 closes: #63, #49, #65, #80 and the queued kit edits (sweep 2 proposal 1, sweep 3 proposals 1 to 4, #42's item 3).
- Sweep 4 evidence: the Engineer and QA Reflections on #10 and #74 both name the environment gap (nothing runs in Kiro Web) and the truncated issue dump.
