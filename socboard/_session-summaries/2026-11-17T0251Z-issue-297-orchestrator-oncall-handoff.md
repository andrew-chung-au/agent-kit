# Issue #297: O12 Alert-to-agent hand-off

**Date:** 2026-11-17T02:51Z (UTC)
**Spec version:** 9cf7ed3

Tier: Standard (from the PM proposal; no tier label). Rubric: On-Call Agent, first step of 2 points ("wakes up on an alert"; `.kiro/steering/rubric-priority.md`). Track C of the lane split.

## What changed and why

`observability/oncall/handoff.py` (standard library only) polls Alertmanager's `GET /api/v2/alerts` every 5 s up to a timeout, acts only on an active `QueueLatencyOverSLO`, and writes `incident.json` atomically from checked fields only: `alertname`, `startsAt` in one fixed UTC form, `environment` and `version` only when they equal the caller's `--environment` and `--version`, `dashboard_url` equal to the Grafana base plus the rule's path, the rule's fixed `summary` and `owner`, and a fixed query; refused fields are listed by name. One parsing function serves the API and the webhook shapes. Exit codes 0, 2 and 3. `tests/test_oncall_handoff.py` runs against a fake Alertmanager. Commits 112052c, 7b5675c, a425ee1, c6877cc, a8bd60b; PR #359.

Before QA, CI caught a real leak: a canary planted in `environment` passed #312's character rule, so the script now requires the expected values as arguments (a425ee1). CI then caught a self-recursive test helper (c6877cc). The first QA FAILED with one Medium: valid RFC 3339 times at the year limits crashed or were written in two forms. One fix round (a8bd60b), then one fresh QA re-check of the changed lines (224 boundary values): PASS, Low findings only.

**What I learned:** the canary test caught a leak no criterion foresaw; a format rule alone does not keep chosen text out.

## Reflection

### Engineer

**What slowed you down (evidence):** no test could run in the sandbox; three CI rounds were needed before QA.
**What nearly went wrong or was blocked:** the first dashboard check accepted payload text in the URL path; a canary passed the environment format rule.
**One proposed change (file, expected effect, measure):** run the canary test mentally against every accepted field before writing the checks.

### QA

**What slowed you down (evidence):** none; the script is standard library only, so a 261-attempt and a 224-value script ran here.
**What nearly went wrong or was blocked:** the time-parsing crash was found only by the attack script, not by the unit tests or CI.
**One proposed change (file, expected effect, measure):** for standard-library scripts, QA runs a boundary-value sweep on every parsed field; measured by Medium findings found this way (one here). The session's one proposal.

## Launch usage

- Engineer (build, two CI fixes, fix round): unknown (the tool did not report time or tool uses).
- QA (first check, re-check): unknown.

## Files created or modified

- `observability/oncall/handoff.py`
- `tests/test_oncall_handoff.py`
- `_docs/records/findings/297.json`
- this file

## Decisions made by the human

- none in this issue.

## Mismatches with the spec or design docs

- #312's character rule cannot keep a canary out of `environment` and `version`; the script also requires the expected values (F-297-1). #312's body and this issue's text should say the caller supplies them.

## Commands to validate

- **Verify:** CI-VERIFIED on a8bd60b: verify run 44004674216 (`VERIFY: PASS`, 3817 passed), image 44004674189, compose 44004674192, postgres 44004674149, all success.
- **Assert clean:** passed after each QA launch (c6877cc, a8bd60b).

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-297-1: The character rule alone accepts canaries; the caller supplies the expected values (Low).
- F-297-2: Extra labels and annotations are refused under fixed words, not names (Low).
- F-297-3: One failed poll exits with no retry; no fsync on write (Low).
- F-297-4: Some out-of-range startsAt offsets are handled but not pinned by tests (Low).

## Follow-ups for the next session

- After the merge of #359: check the merged head, post the Close comment, run `make issue-close N=297`.
- #298 (on-call mandate, guard and two jobs, Heavy): its decision record needs the human's approval by name before the Engineer starts. #299 (the drill) passes `--environment` and `--version` to the hand-off.
