# Issue #91: Stage 6 plan summary

**Date:** 2026-10-22
**Spec version:** 97893c1

## What changed and why

Roadmap step 13: `_docs/plan-summary.md` now maps all 12 rubric criteria (24
points, 10 to pass) to `_docs/tasks.md` tasks and planning documents, lists nine
top risks with mitigations and owners, and collects 106 open questions,
assumptions and `VERIFY:` items from Stages 1-5. It records seven source
discrepancies instead of silently resolving them, reports the Stage 6 checklist
honestly, and is linked from `README.md`. The deliverable is planned coverage;
`_docs/rubric-evidence.md` remains the only current score record.

QA failed the first hand-over because the completeness table counted the words
"assumption"/"verify" rather than the literal tags, which made the checklist's
completeness PASS false. The Engineer recomputed label-only counts with line
locations and fixed the checklist evidence; QA's re-check passed.

## Files created or modified

- `_docs/plan-summary.md` (new).
- `README.md` (one line in "Planning documents").
- `_docs/roadmap.md` (step 13 done; check-in line).
- `_docs/ai-usage-log.md` and this summary.
- Follow-up `#95` filed (tasks.md Application/task 15 reconciliation).

## Decisions made by the human

- Defer the spec Q2-Q4 status note to the next spec change (protected file).
- File one follow-up (#95) for the tasks.md Application/task 15 discrepancy;
  README `withdrawn` stays with #73.
- Note only the minor checklist recount wording; no third QA pass.

## Mismatches with the spec or design docs

Recorded, not fixed (all out of #91's scope): spec line 3 says "reviewed" while
Q2-Q4 remain open; README's status list omits `withdrawn` (#73); tasks.md's
Application coverage omits task 15 (#95); architecture A1 and api.md A1 share a
tag but are distinct (`file:tag` keys).

## Commands to validate

**Verify:** `make verify BASE=1edc468` (PASS: 62 tests, type check PASS,
whitespace PASS, no weakened tests). **Assert clean:** `make assert-clean`
(PASS, HEAD `882c75d` after QA).

## Proposed AGENTS.md changes

None.

## Temporary changes

None. Read-only `.scratch/` checks (`check_map.py`, `check_links.py`,
`count_labels.py`) were used and removed by `make clean-scratch`.

## Permission review

- Read-only (propose allowing): none.
- Writes to the record (keep asking): `gh issue create` for #91 and #95
  (issue-creation ask rule); `make issue-comment` on #91 (allowed target, four
  comments: PM, Engineer, QA FAIL, QA re-check PASS).
- Risky (propose denying): none.

## Interruptions

None. The first PM launch was aborted before it produced output and was
relaunched unchanged.

## Unrelated problems noticed but not fixed

- `.scratch/check_map.py` hardcodes the rubric points instead of parsing
  `_docs/rubric.md`, so it would not catch a future re-pointing. It is a
  scratch-only helper and is not committed.

## Follow-ups for the next session

- #95: reconcile tasks.md § Coverage summary with task 15 (Application).
- #73: README dashboard status list (`withdrawn`).
- Step 14 (plan review and phase change) still depends on step 12; decide
  whether step 12 is done once the Milestone A backlog is filed, or wait for the
  Milestone B/C filings, before starting step 14.
