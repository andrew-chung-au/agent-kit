# Issue #16: Tiers, part 1: tier definitions, human-set tier label and escalation check (Phase 3a)

**Date:** 2026-11-01T11:46Z (UTC)
**Spec version:** none

## What changed and why

Added the three change tiers (Light, Standard, Heavy) to the process: a `## Tiers` section in `process.md`, tier-aware lifecycle steps and Definition of done, and the PM, task template, conf template, blueprints and setup rows that go with it. Added `agent-kit/scripts/check-tier.sh` and `make tier-check TIER=<light|standard|heavy> [BASE=<commit>]`, which fails a Light change that touches the fixed escalation list, a path outside `LIGHT_ALLOWED`, or more than `LIGHT_MAX_LINES` (default 20) changed lines. The tier label is set only by the human.

QA failed the first version: a bad `BASE` made the check print PASS (the `git diff` error was swallowed), and a `BASE` starting with `-` reached `git diff` as an option. Fixed in a third commit: `BASE` is validated and resolved to a hash, and any git failure while collecting changes fails the check. QA re-checked and passed.

Commits: d4d7574 (kit), 3b9012b (`Makefile` target and `agent-kit.conf` `LIGHT_ALLOWED`), f8dde3a (fail-closed fix). QA: FAIL at 3b9012b, PASS at f8dde3a. Issue closed by the orchestrator.

**What I learned:** new scripts that take a revision or path from the caller need bad-input tests from the start; the first version's tests only used valid values.

## Reflection

### Engineer

Reflection:
1. Slowed by: process.md pinned wording in `tests/test_approval_freeze.py` (steps 4 and 9), so my first tier-aware text failed two tests and cost a verify rerun; and `make verify` dumped a 6000-line diff against a far-behind origin/main each run.
2. Nearly went wrong: `check-tier.sh` passed on a bad BASE (git errors swallowed by process substitution) and let a leading-dash BASE reach `git diff` as an option; QA caught it, my tests had only valid BASEs. Also `make verify BASE=HEAD` leaks BASE into a test's sub-make and fails one test.
3. Proposed change: add to `agent-kit/team/software-engineer.md` "for any script taking a git revision or path from the caller, test a nonexistent value, a leading-dash value and a failing git call". Expected effect: fewer QA FAILs on input handling. Measure: count of QA FAILs on argument handling over the next ten issues.

### QA

Reflection:
1. Slowed down: the issue body plus 7 comments was 52 KB (`gh issue view 16 --comments` was truncated to a file), so I had to grep it for the Engineer comment; and testing the new tests against the old script needed a patched copy of `tests/kit_repo.py` (its `REPO` path comes from `__file__`) built by a 30-line `.scratch/` script.
2. Nearly went wrong: `BASE=--output=injected.txt` really wrote a file in this repo's `.scratch/` when I ran it against the live repo instead of a throwaway one, and the Engineer's tests had no bad-BASE case, so the fail-open (`BASE=nosuchrev` printed PASS) was only found by my own probing.
3. Proposed change: `agent-kit/team/software-engineer.md`, add "for every script argument or env value a user can set, add a test with a nonexistent, option-like (leading `-`) and empty value, and one where the underlying command fails". Expected effect: fail-open and option-injection bugs in new scripts are caught before QA, so fewer QA FAIL loops. Measure: count QA FAILs whose cause is bad-input handling in a new script over the next ten issues (this one: 1 of 1 FAILs).

### PM

unknown (role not asked)

## Launch usage

- Engineer, implement #16: 6m10s active, 59 tool uses.
- QA, first check (FAIL): 1m52s active, 24 tool uses.
- Engineer, resumed to post its comment: 37s active, 4 tool uses.
- Engineer, resumed to fix `BASE` handling: 2m24s active, 11 tool uses.
- Engineer, resumed to post the fix comment: 3m02s active, 15 tool uses.
- QA, re-check (PASS): 1m05s active, 14 tool uses.
- Engineer, resumed for its reflection: 13s active, 4 tool uses.
- QA, resumed for its reflection: 1m39s active, 17 tool uses.

## Files created or modified

- Created: `agent-kit/scripts/check-tier.sh`, `tests/test_tier_check.py`.
- Modified (kit commit): `agent-kit/blueprints.md`, `agent-kit/process.md`, `agent-kit/setup.md`, `agent-kit/team/pm.md`, `agent-kit/templates/Makefile.mk`, `agent-kit/templates/agent-kit.conf.template`, `agent-kit/templates/task-template.md`.
- Modified (second commit): `Makefile`, `agent-kit.conf`.
- Modified (fix commit): `agent-kit/scripts/check-tier.sh`, `tests/test_tier_check.py`.
- Word counts, before to after: `process.md` 1941 to 2706 (+765, expected about +280), `pm.md` 623 to 734, `task-template.md` 148 to 175, `blueprints.md` 2356 to 2440.

## Decisions made by the human

- Approved the kit commit as staged, and asked for the commit command; the `process.md` trim is left to the next sweep.
- Approved the second commit (`Makefile`, `agent-kit.conf`) and the fix commit; ran all three commits themselves with `HUMAN_APPROVED=1`.
- Earlier, in the issue: `LIGHT_ALLOWED` lists three kit docs (decision 1, option 2); the body was confirmed by hash.

## Mismatches with the spec or design docs

none (no spec yet).

## Commands to validate

**Verify:** `make verify` (278 tests, 0 failures, claims check OK, whitespace clean at f8dde3a).
**Tier check:** `make tier-check TIER=light BASE=<commit>`. Pass `BASE=` explicitly; the default is far behind in this repo.

## Proposed AGENTS.md changes

none.

## Temporary changes

none. QA and the Engineer left only `.scratch/` files; QA deleted its throwaway repos.

## Interruptions

none stopped early. QA's first check failed the issue; the Engineer was resumed to fix it and QA re-checked.

## Unrelated problems noticed but not fixed

- `make verify BASE=HEAD` fails one `tests/test_gate_push_check.py` test because `BASE` leaks into the test's sub-make. Plain `make verify` passes.
- The default `BASE` (`origin/main`) is far behind here, so `make verify` prints a very large diff each run.
- `.claude/agents/pm.md` is modified and the two `proposals/` files are untracked, so `make assert-clean` fails on them.
- `tests/test_approval_freeze.py` pins wording in `process.md` steps 4 and 9, which constrains tier-aware edits.

## Follow-ups for the next session

- Sweep: trim `process.md`; consider the one proposal above (a bad-input testing line in `agent-kit/team/software-engineer.md`), which both roles made independently. It is a suggestion for the human; nobody applies it.
- #20: the event-name gate is still open and needs the human to run the observer `opencode run`; #36 waits behind it.
- #37 (Phase 3b) follows #16 and does the Light-tier dry runs; #39 is groomed and ready; #40 has no PM grooming yet.
- Proposed version bump and changelog lines for the human to decide: tiers (#16) join the unreleased 1.10 changelog.
