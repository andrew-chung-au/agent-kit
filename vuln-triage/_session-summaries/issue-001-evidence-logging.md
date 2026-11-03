# Issue #1: Set up evidence logging and rubric evidence auditor

**Date:** 2026-10-13
**Spec version:** dafd91e

## What changed and why

Implemented issue #1 (groomed): every agent records work in `_docs/ai-usage-log.md`, key prompts indexed under `_docs/prompts/`, new Rubric Evidence Auditor role (`.opencode/agents/rubric-auditor.md`) plus `update-rubric-evidence` skill, `_docs/rubric-evidence.md` (14 criteria, all MISSING), `_docs/ai-usage-report.md` skeleton, backfilled log from git history, README links. QA: full check FAIL only on uncommitted protected paths (human-deferred), then PASS on targeted C12 re-check after the approved protected commit.

## Files created or modified

- Committed 8e637d6: `_docs/ai-usage-log.md`, `_docs/rubric-evidence.md`, `_docs/ai-usage-report.md`, `_docs/prompts/README.md` (skeleton: no prompts recorded yet), `README.md` (4 links), `.agents/skills/update-rubric-evidence/SKILL.md`.
- Committed 0b2a18f (HUMAN_APPROVED=1, approved in-session): `AGENTS.md` (2 log rules), `.opencode/agents/pm.md`, `software-engineer.md`, `qa-engineer.md` (DoD log line each), `.opencode/agents/rubric-auditor.md` (new).
- Uncommitted, untouched: `M opencode.json` (human's own pre-existing allow-rule change, out of scope).

## Decisions made by the human

- Mid-issue Q1 (`_docs/prompts/` missing): "Skeleton README, index later" — engineer wrote zero-entry README; indexing is a follow-up.
- Mid-issue Q2 (out-of-scope follow-ups): may become follow-ups; creating/editing issues needs approval.
- Post-QA approval: initially "Defer commit" of protected paths (caused expected QA FAIL on C12), then at decision point "Approve and commit" (committed as 0b2a18f), "You paste" for the PM/Engineer/QA issue comments, "Draft follow-ups" (PM drafts, nothing created).

## Mismatches with the spec or design docs

none. Spec notes from PM, Engineer, QA: none.

## Commands to validate

- **Verify:** `make verify` → PASS WITH WARNINGS (no TEST_CMD: planning phase, no code exists; whitespace PASS; no test files changed).
- QA re-check at 0b2a18f: C1–C11 carry over PASS, C12 PASS. No E2E (AGENTS.md: none; docs-only change).

## Proposed AGENTS.md changes

none beyond the criterion-2 two-rule diff already committed as 0b2a18f.

## Temporary changes

none. No processes started, no system changes, no installs. `.scratch/` held only check scripts and grooming text; `make clean-scratch` ran.

## Interruptions

Two `software-engineer` subagent launches failed before doing work (one invalid-params error, one aborted); third launch succeeded. Nothing was left behind; verified via `git status --short` before proceeding.

## Unrelated problems noticed but not fixed

- `M opencode.json` (human's allow-rule additions) remains uncommitted; needs separate human review/commit.
- No GitHub comments posted yet (PM, Engineer, QA texts await human paste — commenting needs approval). Issue #1 still OPEN; ready to close after comments are pasted.
- PM/QA roles could not append their own `_docs/ai-usage-log.md` entries (read-only roles); only the Engineer entry was appended. Grooming and QA work is evidenced by `.scratch/` transcripts (removed by clean-scratch) and this summary.

## Follow-ups for the next session

PM drafts (approval needed before creating): (1) index human-added prompt files in `_docs/prompts/README.md` (blocked on human adding files); (2) run first rubric audit in fresh session via skill; (3) write report content (last; needs index + audit). Order: 1/2 either order, 3 last.
