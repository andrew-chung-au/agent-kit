# Issue #120: Remove the dead test-only GET /api/cases route from tests/backend_support.py

**Date:** 2026-11-13T12:06Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Claude Code worked it in the local sandbox on `main` from `e5e82c5`. Ponytail was on. The issue was filed in this session as a proposal (found by #20's QA and Engineer), groomed by the PM, labelled by the human, and is the first of the three issues the human ordered before #22 (#120, #114, #104).

- **Round 1 (Engineer):** `tests/backend_support.py` no longer defines the test-only `GET /api/cases` route (`closed_cases`) or the five imports only it used; the module docstring and two comments in `tests/test_backend_order.py` now say the `GET /api/cases` tests hit the real route (`getClosedCases`, `socboard/cases.py`), which `create_app()` registers first. The Engineer's search found exactly the seven `GET /api/cases` tests through the `client` fixture the issue lists (five in `test_backend_order.py`, two in `test_auth_api.py`); none needed new coverage.
- **Mutation proof, with no tracked file edited:** a throwaway `.scratch/` test builds the real app twice, once as is and once with the cases router swapped for one that checks the role inside the handler (after the schema check). The control passes and the mutant fails `test_cases_b` with 422 instead of 403 (`test_cases_d` holds on both, so it does not prove the order). QA re-ran it from its own copy.
- **Round 2 (Reviewer findings 1 and 2, approved):** comment-only edits: the `app` fixture docstring in `tests/conftest.py` no longer says the business routes do not exist, and the `tests/test_auth_api.py` module docstring no longer says the test routes "use the real dependencies" (none does). QA confirmed by an AST comparison with docstrings stripped that no code or test body changed.
- **QA:** PASS at `57b8469` and at `83b274a`; `make assert-clean` passed after each. The Reviewer ran once, on round 1; round 2 (comments only) went to QA without a second Reviewer launch (orchestrator's decision, recorded here).
- **Order of work:** the PM could not edit the issue body (no make target does), so the orchestrator applied the groomed body with `gh api`, with the human approving the command; the PM then recorded the hash.

**What I learned:** a `make verify` ending `PASS WITH WARNINGS` for "test fixtures changed" on a docstring-only edit needs an AST comparison to be proven harmless; QA did that in a script.

## Reflection

### PM

PM: reflection on #120 grooming.

Reflection:
1. Slowed: no make target edits an issue body, so I could not finish grooming in one pass; the comment waited for an orchestrator round trip. Also `make test-one` was the only runnable path for a scratch proof, and the first two mutation attempts failed because routes sit in lazy included routers, which cost two reruns.
2. Blocked: the hash line could not be honest until the body was edited; I stopped rather than quote the old body's hash or run a raw `gh issue edit`.
3. Proposed: add an `issue-edit` target (N, FILE under .scratch/, owner-authored and unlabelled issues only) to Makefile and Makefile.github.mk. Expected effect: the PM edits the body and records its hash in one launch. Measured by counting grooming launches that end with "body edit needed" before and after.

### Engineer

Engineer: final reflection on #120 for my round (the dead-route removal and the mutation proof).

Reflection:
1. Slowed me down: my first docstring and heading rewording left two lines over 100 characters, and I only saw them when reading `git diff --cached`; that cost one extra edit, test run and re-stage before the commit.
2. Nearly went wrong: `make verify` has no line-length check, so it passed with the long lines; only the staged-diff read caught them.
3. Proposed change: add a line-length check (100 characters) on changed lines to `scripts/` verify output, so a long line shows as a warning in `make verify`. Expected effect: no extra edit round for wrapping. Measured by counting rework rounds after a first verify PASS on the next five test-only issues (today: one).

Ponytail: I reused the PM's `.scratch/mutant_order.py` draft and the `make test-one` target instead of writing a new harness, and skipped adding any new test because no test depended on the dead route.

(The round 2 Engineer, a separate launch, posted a one-line Reflection on #120 with its comment; it noted no problem.)

### QA

QA: Reflection

Reflection:
1. Slowed down: `make verify` takes about 2.5 minutes (1508 Python tests plus 208 frontend) and I ran it in both launches for changes that were docstrings only; `make test-one` also refused my first scratch script (0 tests collected), costing one extra round.
2. Nearly went wrong: the verify warning "test fixtures changed: tests/conftest.py" could be misread as a loosened fixture; only an AST comparison with docstrings stripped proved it was a docstring.
3. Proposed change: add a note in `_docs/agent-kit/procedures/verify.md` that for a comment-only re-check QA may run `make test-one` on the touched files plus an AST-equality script, with full `make verify` once at the end. Expected effect: about two minutes saved per comment-only re-check. Measure: QA launch wall time on re-check rounds before and after.

### Ponytail

Engineer: see the `Ponytail:` line above.

## Launch usage

Tool: Claude Code. Figures copied from the completion notifications; a resumed launch's figure may be cumulative or per-resume (unknown).

- PM grooming: 120 s, 29 tool uses; hash-record resume: 22 s, 6 tool uses; reflection resume: 13 s, 3 tool uses.
- Engineer round 1: 521 s, 42 tool uses; final reflection resume: 12 s, 3 tool uses.
- QA round 1 (PASS at `57b8469`): 258 s, 30 tool uses (the notification said the result might be interim).
- Reviewer: 29 s, 11 tool uses.
- Engineer round 2 (comments): 349 s, 18 tool uses.
- QA round 2 (PASS at `83b274a`): 211 s, 15 tool uses; reflection resume: 240 s, 18 tool uses.

## Files created or modified

`tests/backend_support.py`, `tests/test_backend_order.py`, `tests/conftest.py` (a docstring), `tests/test_auth_api.py` (a docstring), the merge of `origin/main` (sweep 6, PR #137: two steering files, the roadmap, the sweep record), this file.

## Decisions made by the human

- File the dead-route follow-up as its own issue before #22 (not folded into #114); run #120, #114 and #22 here, with #104 before #22.
- Approved the groomed text of #120 (labelled it) and approved the `gh api` edit of its body.
- Reviewer findings: apply 1 and 2 (comment-only), skip 3.
- Mutation proof: no tracked file is edited (the groomed body's choice, approved by the label).

## Mismatches with the spec or design docs

none.

## Commands to validate

- **Verify:** `make verify` (`PASS WITH WARNINGS` at `83b274a`: 1508 Python, 208 frontend, whitespace clean, 0 assertion lines added or removed; the one warning is "test fixtures changed: tests/conftest.py", a docstring only).

## Proposed AGENTS.md changes

none. (The Reflection proposals touch `Makefile`, `scripts/` and `_docs/agent-kit/` files; they are for the sweep.)

## Temporary changes

none. No processes started by this session. `make clean-scratch` was not run: `.scratch/` still holds the PM's drafts for #22 (the proposed body and change list, which the human has not yet read) and #104, which the new steering rule (sweep 6, proposal 7) says to copy out first. It runs at the end of the whole session, after those drafts are saved. The two pid files that were in `.scratch/` were not created by this session; the human deleted them.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- The ragged line 4 of the `tests/test_auth_api.py` docstring (cosmetic), and the `/cases` heading at `tests/test_backend_order.py:28` (Reviewer finding 3): left for #114, which edits the same file.
- Sweep 6 (merged during this issue) adds rules this session's earlier launches did not carry: every QA and Engineer launch message names no env file in a comment (rule 12), and a Reviewer launch says "write nothing, not even under `.scratch/`" with the `.scratch/` file names listed before and after (rule 10). They apply from #114 on.
- Roadmap change from sweep 6: #112 is now timed before #22 and #115 is done; #112's groomed drafts in `_human-tasks/groom-handover-2026-11-13/` are not applied.

## Follow-ups for the next session

- #114 next, then #104 (groomed, awaiting the human's label), then #112 (before #22 per the roadmap), then #22 (its proposed body awaits the human's confirmation).
- The PM's proposal for an `issue-edit` make target (one launch to edit a body and record its hash) is for the sweep.
