# Planning: hand-off to the next orchestrator session (Kiro Web)

**Date:** 2026-11-13T05:20Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

The Kiro Web orchestrator session of 2026-11-12 and 13 ends here because its context is high. Read this file first in the next session, after `AGENTS.md`, `.kiro/steering/*.md` and `_docs/planning/roadmap-1-core.md`. `main` is at `18022f7`.

### Done in this session
- **#11** (Heavy): option B, with database triggers for an append-only audit trail. Merged and closed.
- **#102, #99, #14, #15 and #18:** each issue's session summary is on `main`.
  - #99 was closed by GitHub, because a commit subject began "Fix #99".
  - #18 needed two PRs (#111, then #113 for the NUL check).
- **#16 and #17:** worked by Claude Code in the dev container. Both are closed.
- **The ponytail trial is shelved.**
  - Ponytail itself is in normal use: the Engineer loads `_docs/vendor/ponytail/ponytail.md`, and the Reviewer runs after the last QA PASS. Rules are in `AGENTS.md`, Project settings.
  - Post the Reviewer's report as `Orchestrator: Reviewer report (#N)`. The human labels each finding.
  - Review record: `_docs/records/2026-11-13T0424Z-measure-ponytail-review.md`.
- **Sweeps 4 and 5 ran.** Sweep 5 is `_docs/records/2026-11-13T0424Z-measure-pm-sweep.md`. Its four approved one-line rule edits are on `main`:
  - `pm.md` and `orchestrator-comments.md`: re-check criteria against newer decision records.
  - `AGENTS.md`: `make issue-comment` and `make issue-create` added to Commands.
  - `software-engineer.md`: commit subjects end `(#N)` and never use a closing keyword.
- **Follow-ups filed:** #107 (simplify the audit guard), #110 (simplify the ingest route, which also carries #15's and #18's findings), #112, #114, #115.

### Split proposed for #19 and #20 (the human decides)
Both are Standard and approved, and their hashes match at hand-off (`3928e638…` and `b86eba13…`).
- **#19 (audit trail read API), for the new Kiro Web session.** It depends on #14, #16, #17 and #18, all merged.
- **#20 (closed-cases list for Leads), for Claude Code, in parallel.** This is a second one-time exception to `delivery-pace.md` item 4, and needs the human's approval.
  - #20 depends on #19 for one criterion only: a test that follows a listed case to its audit trail.
  - Build #20's other criteria first. After #19 merges, merge `main` into #20, add that test, then run QA.
  - No body change and no new hash.
- **Shared names, agreed in advance so the merge is clean:**
  - Both routes go in `socboard/cases.py`, which is already on `tests/test_data_audit.py`'s HTTP-layer list, so no new route module is needed.
  - Lead-only access is one dependency named `require_lead` in `socboard/auth.py`, giving 403 `forbidden` (`errors.FORBIDDEN`). #19 adds it. #20 writes the same name, and the second to merge keeps one copy.
  - Each issue's additions sit under a `# Audit trail (#19)` or `# Closed cases (#20)` block.
- **#107 ordering:** the roadmap says #107 comes before #19. That was set so a new route module would not need another file-list ruling. If #19 puts its route in `cases.py`, that reason goes away and #107 can wait until before Deploy. This is the human's call.

### Other work that fits alongside
These are safe in parallel because they share no files with `socboard/` routes or `tests/` route tests:
- **#63:** `make issue-close` ignores reflection-only Engineer comments. Approved. It touches kit scripts, which are protected, so it needs approval of the exact diff. It refused #16's close.
- **#73 + #71 (+ #80):** one `Makefile` sitting, all approved and groomed. Protected, so they need approval of the exact diff. #73 is `make issue-body`, which blind second QA launches need. It also carries sweep 5's proposals 4 and 13.
- **#75, then #31:** frontend lint (`frontend/` and the `Makefile`), before #21. #54, the frontend guardrail scan, also comes before #21.
- **After #19 and #20:**
  - #115 and #112 (contract sync, before #21);
  - #114 (`real_crash_client`; it touches `tests/`);
  - #21 (frontend connected to the API), then #22.
- **Before Deploy:** #107, #110, #103, #104, #100 and #93.

### Rules kept from this session
- **Git:** run git steps one at a time, never in parallel, and never in the same tool batch as a subagent launch. Several results here went stale or arrived out of order because of that.
- **QA:** a QA comment's first line starts `QA: PASS` or `QA: FAIL`.
- **Tools:** use `gh api`, never `gh issue` or `gh pr`.
- **Human approval:** ask the human before any protected-file change, label change or closure the process does not already allow.
- **Blind second QA launches:**
  - search only `socboard/**` and `tests/**`, and read the issue body through a body-only extract (`delivery-pace.md` item 6);
  - a fresh subagent counts as a new session;
  - stopping rule: only a Medium-or-higher finding that needs a change in the issue fails the verdict.
- **Engineer comments:** keep commit hashes out of the Engineer's Reflection comments until #63 lands.
- **Tests can't run in Kiro Web:** `uv` hits a read-only file system, so CI is the test loop. Read results with `.scratch/ci.sh`-style filtering of `gh api .../actions/jobs/<id>/logs`.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

Active time and tool uses: unknown (Kiro Web gives neither). Per-issue counts are in each issue's session summary.

## Files created or modified

This file.

## Decisions made by the human

Recorded in each issue's comments and session summary, in the sweep 4 and 5 records, and in `_docs/decisions/2026-11-12T2300Z-ponytail-adopt.md`.

## Mismatches with the spec or design docs

- `openapi.yaml` lacks the 422 on `getCase` and `claimCase`, the 5,000-character note limit, and the order notes. All of this is #115.

## Commands to validate

- **Verify:** `make verify` (CI on each push; the last green run is on `main` after PR #116).

## Proposed AGENTS.md changes

none.

## Temporary changes

none. `make clean-scratch` ran.

## Interruptions

none. The session ends at a clean point: no role is running, no PR is open, and the working tree is clean.

## Unrelated problems noticed but not fixed

- `LoginRequest` does not go through `_storable`, so a NUL in the login fields may give a 500 on Postgres. This is a candidate for #104.

## Follow-ups for the next session

1. Ask the human:
   - whether #19 (Kiro) and #20 (Claude) run in parallel as above;
   - whether #107 can wait until before Deploy.
2. Start #19. Hash check, Claim (with the new claim-time check against newer decision records), then Engineer with ponytail, then CI, QA, the Reviewer, the decision point, the summary, the merge and the Close.
3. When the human allows it, #63, then the #73 + #71 (+ #80) `Makefile` sitting.
