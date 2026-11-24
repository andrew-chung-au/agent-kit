# Issue #204: Weight decision points, keep a ledger of the ones the agent continued past, and answer them per point

**Date:** 2026-11-23T20:43Z (UTC)
**Spec version:** none

Tier: heavy (from the PM proposal; no tier label).

## What changed and why

- **Took over:** picked up the previous session's records commit `7fd4ae4` (issued rulings) on `claude/funny-turing-6jki2a`.
- **Grooming:** the PM regroomed #204 against the kit as it stood after #196 to #203.
  - The human changed the design at grooming: decision points carry the existing `Impact:` and `Effort:` grades (points 1 to 3 from Effort), not a new weight. A continued point gets a `Rollback:` line and there is no `Point:` line.
  - D-204-1: the ledger is `_docs/records/decisions/<issue>.jsonl`.
  - D-204-3: a cloud session may push its own branch while points are open (C13).
  - The PR trial from #200 was split out as #239.
- **Implementation:** the Engineer built it at `f6ae9b1` (kit, human-approved), with `c35e4f6` (Decision record) and `80c7f61` (ledger, D-204-4).
  - The human then ruled that the questions met at one stop are one decision point, and the Engineer added that rule.
- **QA:** both QA launches passed at `80c7f61`. At the decision point the human chose to fix F-204-7 (who logs a stop point), committed at `cfa80b9` with corrected changelog counts. QA's re-check passed at `cfa80b9`.
- **Merge:** PR #240 merged as `272479e`.
- **Also filed:** #238 (V2 idea: evaluate adapting T3 Code), parked outside the order. #239 is placed after #204 in `_docs/planning/kit-1.11/issues/filed.md` (`4ffbf18`).

**What I learned:** the new rules caught this session's own slips. Three choices were first logged as three points, and my step-7 questions were three points and were asked before being logged. Both were fixed by rulings that went into the kit text.

## Reflection

Roles were not asked for reflection blocks this session: the PM, Engineer and QA launches hit the 5-hour usage limit three times, and a further launch was not spent on them.

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- PM, first launch: stopped on the usage limit before doing anything; active time unknown, tool uses unknown.
- PM, regroom: 612474 ms, 80 tool uses.
- PM, Effort/Rollback revision: 115696 ms, 39 tool uses.
- PM, grooming comment post: 59337 ms, 13 tool uses.
- web-fetch, T3 Code docs: 27664 ms, 3 tool uses.
- Engineer, implementation: 3006102 ms, 112 tool uses.
- Engineer, grouping rule: 1205980 ms, 24 tool uses.
- Engineer, kit and ledger commits: 50436 ms, 20 tool uses.
- Engineer, F-204-7 fix staging: 401696 ms, 16 tool uses.
- Engineer, CHANGELOG deltas question: 36316 ms, 11 tool uses.
- Engineer, F-204-7 commit: stopped on the usage limit after committing; active time unknown, tool uses unknown.
- QA, first launch: 506637 ms, 63 tool uses.
- QA, Heavy second launch: 844425 ms, 44 tool uses.
- QA, re-check after fix round 1: 772466 ms, 34 tool uses.

## Files created or modified

- Kit (`f6ae9b1`, `cfa80b9`, human-approved): `agent-kit/process.md`, `agent-kit/procedures/asking-the-human.md`, `agent-kit/procedures/formats.md`, `agent-kit/procedures/orchestrator-comments.md`, `agent-kit/team/software-engineer.md`, `agent-kit/scripts/decisions.py` (new), `agent-kit/scripts/check-format.py`, `agent-kit/templates/Makefile.mk`, `agent-kit/customizing.md`, `agent-kit/README.md`, `agent-kit/CHANGELOG.md`.
- Other files: `Makefile`, `tests/test_decisions.py` (new), `tests/test_check_format.py`, `_docs/decisions/204-decision-points.md` (new), `_docs/index.md`, `_docs/records/decisions/204.jsonl` (new), `_docs/records/findings/204.json` (new), `_docs/planning/kit-1.11/issues/filed.md`.

## Decisions made by the human

- **Grooming:**
  - Weight is replaced by `Impact:` and `Effort:` points, plus `Rollback:` on continued points.
  - D-204-1: ledger under `_docs/records/decisions/`.
  - D-204-2: decision block option 1, then revised to Effort plus Rollback.
  - D-204-3: yes, C13 kept.
  - Approved the body edit, and placed #239 after #204.
- **Mid-issue:**
  - The grouping ruling: one point per stop, counted once.
  - D-204-4: approve, all recommendations (budget 0 with nothing open is within budget; `make decisions` fetches the issue itself; strict entry checks).
  - The kit commit approved as staged.
- **Decision point:** D-204-5 approve (fix F-204-7 now, sweep after the 1.11 cut, open the PR); D-204-6 A (correct the changelog counts), including the two difference figures.
- **Outside #204:** file #238 as a long-term V2 idea; open PR #240; merge it.

## Mismatches with the spec or design docs

none (the repo has no `_docs/specs.md`)

## Commands to validate

- **Verify:** `make verify`. It fails only on F-198-3 and F-196-1, which a clean copy of base `4ffbf18` also shows.
- **Decision points:** `make decisions N=204` prints `none`.
- **Findings log:** `make findings` accepts `_docs/records/findings/204.json`.

## Proposed AGENTS.md changes

none

## Temporary changes

none. No system changes and no processes started; `make clean-scratch` ran at the end.

## Interruptions

- **PM first launch:** stopped on the usage limit. I checked the tree, the issue body and the comments: nothing changed. I relaunched it fresh.
- **Engineer, final launch:** stopped on the usage limit after making commit `cfa80b9`. I checked that the commit holds exactly the approved files and figures, and that its fix-round draft was complete, then posted it.
- **Worker restarts:** the session's worker restarted several times. Each time I checked the state before continuing.

## Unrelated problems noticed but not fixed

- No roadmap file exists yet. The 1.11 filing list carries the agreed order, and #235 carries the same gap (F-203-6).
- Edits to a body or title go through raw `gh api` PATCH, because no make target edits an issue (the PM's grooming and the `[groomed]` prefix).

## Follow-ups for the next session

- Next in the 1.11 order: #239 (trigger: #204 merged), then #205.
- F-204-8 (are approval gates logged in the ledger?) is in the findings log; settle it at the sweep.
- A sweep is due (none recorded). The human chose to run it after the 1.11 cut.
- The findings log and this summary land in a follow-up PR from `claude/funny-turing-6jki2a`, because #240 is already merged.
