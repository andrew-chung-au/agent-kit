# Issue #285: O0 Observability: write the signal contract

**Date:** 2026-11-16T01:34Z (UTC)
**Spec version:** e3461a7

Tier: Standard (from the PM proposal; no tier label).

## What changed and why

Added `observability/CONTRACT.md`, which fixes every name the Phase 3 lanes share: resource attributes, the two metrics with their Prometheus names and buckets, the three spans and their two allowed attributes, the JSON log fields and events, the trace id format, the `QueueLatencyOverSLO` alert, the Alertmanager fields the hand-off reads, and the canary strings. Added its row to `_docs/index.md`. Work was on `claude/o0-observability-contract` (commit 5669b21), merged by the human as PR #306 (merge commit 7a05650).

The session's main agent did the Engineer work itself instead of launching an Engineer subagent; QA was a separate launch.

**What I learned:** roadmap 4 was only on `origin/devops-roadmap-4` when work started; it reached `main` with PR #302 before #306 merged.

## Reflection

### Engineer

**What slowed you down (evidence):** the issue cited `_docs/planning/roadmap-4-devops.md`, which was not on `main` (read from `origin/devops-roadmap-4` instead), and the local verify could not run Tests and Lint (uv on a read-only home folder), so CI had to be awaited.
**What nearly went wrong or was blocked:** I first wrote HTTP attributes on the ingest server span, which the criterion forbids; caught on re-reading before the commit. I also first said the issue lacked approval, because the label was added after my check.
**One proposed change (file, expected effect, measure):** see the QA proposal below; one proposal per session.

### QA

**What slowed you down (evidence):** Verify could not run locally, so the verdict relied on the CI result for the same commit, as stated in the comment.
**What nearly went wrong or was blocked:** nothing; the document is short enough to check every row against the criteria, the openapi enum, the spec line and the roadmap table.
**One proposed change (file, expected effect, measure):** `_docs/agent-kit/procedures/orchestrator-comments.md`, Claim: name the CI runs that stand in for the Verify steps the environment cannot run, so QA does not have to ask; measured by QA comments that ask about it (one here).

## Launch usage

- QA: active time unknown, tool uses unknown (the tool did not report them).

## Files created or modified

- `observability/CONTRACT.md` (new, PR #306)
- `_docs/index.md` (one row, PR #306)
- `_docs/records/findings/285.json` (new, this commit)
- `_session-summaries/2026-11-16T0134Z-issue-285-orchestrator-signal-contract.md` (this file)

## Decisions made by the human

- Added the `approved` label to #285 during the session.
- Approved the push of `claude/o0-observability-contract` and asked for the pull request; merged #306.
- PM decision questions: no explicit answer; the contract uses the proposals (`for: 2m`, buckets 0.5 to 30 s). The human merged it with those values.
- QA findings and the sweep: not ruled on; carried as follow-ups.

## Mismatches with the spec or design docs

none (the spec's Phase 3 detail is #286).

## Commands to validate

- **Verify:** `make verify` (Tests and Lint cannot run in Kiro Web; CI passed verify, image, compose and postgres on 5669b21).
- **Assert clean:** `make assert-clean` passed after QA at 5669b21.

## Proposed AGENTS.md changes

none

## Temporary changes

none (no system change, process or large install). `make clean-scratch` ran after the issue was closed.

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-285-1: The contract says the public case id is decimal digits only, while openapi.yaml calls ids opaque.
- F-285-2: The environment name and service version from OTEL_RESOURCE_ATTRIBUTES have no character limit, so section 9's "every value is fixed" is slightly too strong.
- F-285-3: The ingest server span has no attributes in the contract, so #290 must not add HTTP attributes without a contract change.
- F-285-4: In Kiro Web the Tests and Lint steps of make verify cannot run, so CI stood in for them.
- F-285-5: Nothing checks yet that the canary block parses as kind=value lines.

## Follow-ups for the next session

- Rule on F-285-1 and F-285-2 (proposed: a one-line contract wording change, and a character limit on the two resource attributes in #289).
- Note F-285-3 on #290 and F-285-5 on #290 or #295.
- A PM sweep is due (`make sweep-due`: 23 closed since 2026-11-14).
- Next in order: #286 (spec detail, protected), #287, #288.
