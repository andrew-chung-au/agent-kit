# Issue #296: O11 Alert on user impact: QueueLatencyOverSLO

**Date:** 2026-11-17T00:10Z (UTC)
**Spec version:** 9cf7ed3

Tier: Standard (from the PM proposal; no tier label). Rubric: Alerting on User Impact, 0 to 1 point (`.kiro/steering/rubric-priority.md`).

## What changed and why

`observability/alerts/queue_latency.yml` defines `QueueLatencyOverSLO` with the contract's section 6 expression (the probe's p95 over 5 minutes above 5 s, at least 20 measurements, `for: 2m`, labels and annotations; `environment` and `version` read from the probe's `target_info`). Promtool cases (a), (b1), (b2), (c) to (g) in `observability/alerts/tests/`; `tests/test_observability_alerts.py` compares the rule with the contract, refuses mutated copies and runs `promtool test rules` and `check rules` in Docker from `prom/prometheus:v3.16.0` pinned by digest; `tests/conftest.py` adds the `docker_only` marker (deselects with a printed count; `make verify` refuses skips). Commits efc6b26, b2ea29e, 1bb8734; PR #346.

The human ruled on three points in this session: annotations from `target_info` (option A); case (b) replaced by (b1) and (b2), because under the spec's 5-minute window a 90-second slow burst fires; and the split, so the `check.sh` call, the load check and the dashboard line moved to #348 (needs #340, #292, #293). The body was confirmed and re-hashed (cbf4bc9).

First QA FAILED with two Medium test gaps (case (f) could not fail without the volume guard; the static test did not compare annotation text). One fix round (1bb8734), then one fresh QA re-check of the changed lines: PASS with Low findings only.

**What I learned:** a promtool case can pass for the wrong reason; QA's simulation with the guard removed found it.

## Reflection

### Engineer

**What slowed you down (evidence):** promtool, Docker and pytest cannot run here, so the promtool semantics were reasoned from docs and confirmed only by CI.
**What nearly went wrong or was blocked:** `pip download` left a stray wheel in the repository root; it was moved to `.scratch/` and deleted.
**One proposed change (file, expected effect, measure):** put the untested promtool behaviours on the CI run's checklist first, and settle the `target_info` label names with #292 before the annotations are final.

### QA

**What slowed you down (evidence):** no promtool locally; the cases were checked with a simulation script.
**What nearly went wrong or was blocked:** the case file read as correct; only removing the guard in the simulation showed case (f) could not fail.
**One proposed change (file, expected effect, measure):** `_docs/agent-kit/team/qa-engineer.md`: for each limit a test case covers, check the case fails with the limit removed (mutation), measured by test gaps found this way. The session's one proposal.

## Launch usage

- Engineer (build, fix round 1): unknown (the tool did not report time or tool uses).
- PM (body rewrite, hash record): unknown.
- QA (first check, re-check): unknown.

## Files created or modified

- `observability/alerts/queue_latency.yml`
- `observability/alerts/tests/queue_latency_test.yml`
- `tests/test_observability_alerts.py`
- `tests/conftest.py`
- `_docs/records/findings/296.json`
- this file

## Decisions made by the human

- Option A for the annotations; accept (b1) and (b2) in place of (b); split the load check, `check.sh` call and dashboard line into #348.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** CI-VERIFIED on 1bb8734: verify run 43983929710 (3325 passed; `docker_only: 2 marked, 0 deselected (Docker answers)`; alert tests 19 passed), image 43983929810, compose 43983929711, postgres 43983929646, all success.
- **Assert clean:** passed after each QA launch (b2ea29e, 1bb8734).

## Proposed AGENTS.md changes

none

## Temporary changes

none (the stray wheel from `pip download` was deleted by the Engineer).

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-296-1: Case (e) does not test exactly 5 s through promtool (Low).
- F-296-2: The README does not list the docker_only count or link the alert's evidence (Low).
- F-296-3: Deselected promtool tests would leave CI green if Docker stopped answering (Low).
- F-296-4: PyYAML is only a transitive dev dependency (Low).
- F-296-5: The case (f) comment misnames which sample leaves the window (Low).
- F-296-6: No mutation changes the label name in the environment or version template (Low).

## Follow-ups for the next session

- After the merge of #346: check the merged head, post the Close comment, run `make issue-close N=296`.
- #348: apply the PM's two body changes (the dashboard criterion duplicates #293; the `target_info` check needs #294) once the human agrees, then record its hash.
- Place #348 in roadmap 4 (after #340, #292, #293 and #294).
