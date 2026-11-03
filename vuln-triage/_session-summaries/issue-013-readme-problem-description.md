# Issue #013: README problem, functionality and expected behaviour

**Date:** 2026-10-20
**Spec version:** 9f742d2

## What changed and why

- `README.md` now has three self-contained sections ("The problem", "What VulnTriage does", "Expected behaviour") that state the problem, the end-to-end workflow and the user-visible outcomes without relying on links. It keeps the planning-phase warning and both document indexes.
- The functionality prose covers inventory, the three lockfiles, OSV.dev matching, KEV/EPSS enrichment, deterministic ranking, the guarded LLM brief, notification and GitHub issue, daily refresh, re-scan, dashboard and audit trail, the read-only MCP server and the watch-and-respond loop.
- Acronyms OSV.dev, CISA KEV, FIRST EPSS, LLM, MCP and n8n are expanded on first use; the non-goals (no scanning, no automatic patching, no MCP writes) and the undecided values are left as the spec leaves them.
- The roadmap check-in records step 2 as `doing` (implementation QA PASS) until the auditor confirms Problem Description 2 in step 1.

## Files created or modified

- `1a000c2` implementation: `README.md` only (+39/-2).
- `e46fadf` Engineer's `_docs/ai-usage-log.md` entry.
- This summary, the orchestrator's usage-log entry and the roadmap check-in.
- No protected files changed.

## Decisions made by the human

- Do not file a follow-up issue now for README install/run steps, screenshots, badges and a deployment link; scope it in the later backlog review once the app and deployment exist.
- No action on QA's three minor findings outside the criteria: the mandated AI usage-log entry in the cumulative diff, unexpanded CVE/API/JSON/Grafana, and the shorter telemetry-exclusion sentence.

## Mismatches with the spec or design docs

None.

## Commands to validate

- **Test:** `make test`: 2 files, 35 tests passed.
- **Verify:** `make verify BASE=1be4f95`: PASS at `e46fadf`; 35 tests passed, whitespace PASS, no test files changed in the #13 range. Default `make verify`: PASS WITH WARNINGS; the 7 warnings are rewritten assertions from issue #22's unpushed test changes.
- **README link check:** `.scratch/check_readme_13.py` PASS; all 11 relative links resolve and the required headings and fixed names are present.
- **Assert clean:** `make assert-clean`: PASS at `e46fadf`, HEAD unchanged after QA.

## Proposed AGENTS.md changes

None.

## Temporary changes

None. No process or server was started, nothing was installed, and no system configuration changed. `make clean-scratch` ran at close-out.

## Permission review

- Read-only (propose allowing): none.
- Writes to the record (keep asking): none; `gh issue edit`/`gh issue comment`, `make issue-dump` and `make assert-clean` ran without stopping.
- Risky (propose denying): none.
- Proposed `opencode.json` and `.claude/settings.json` changes: none.

## Interruptions

None. PM, Engineer and QA each completed in one run; QA posted PASS (comment 6280140282) at `e46fadf`.

## Unrelated problems noticed but not fixed

- CVE, API, JSON and Grafana are not expanded; the acceptance criterion names only the six required terms, and the human accepted no action.
- The README's telemetry-exclusion sentence is shorter than spec US-13 but does not contradict it; the human accepted no action.
- Roadmap step 1 (refresh rubric evidence) remains `todo`, so #13 was implemented ahead of it at the human's request and step 2 stays `doing` until the audit.

## Follow-ups for the next session

- Roadmap step 1: refresh `_docs/rubric-evidence.md` with the rubric auditor, which should confirm or reject Problem Description 2 after #13 and re-check Testing 1 and CI/CD 1.
- Then follow the roadmap sequence (step 3, #35). #23 is not next: the roadmap places it after the architecture step.
- No new follow-up issues were filed.
