# Issue #73: Add make issue-body

**Date:** 2026-11-13T06:48Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Kiro Web worked #73 as the first of four issues in one `Makefile` sitting (#73, #71, #80, #75; the human's order). Ponytail was on. PR: #121 (draft). Other sessions ran at the same time by the human's one-time exception to `delivery-pace.md` item 4: #20 (Claude Code) and #63 (Kiro, kit scripts); both merged while #73 waited.

- **Claim-time check:** the four decision records dated after grooming (data model, auth tokens, ponytail adopt, ingest key) say nothing about the issue targets or files. No conflict.
- **New target `make issue-body N=<n>`** in `Makefile` and in the kit template `_docs/agent-kit/templates/Makefile.mk` (same five lines in both), after `issue-dump`. It takes the repository from `github_api.py repo`, reads the issue with `github_api.py head` (no comments), checks the JSON with `json.tool` and moves it into `.scratch/issue-<n>-body.json` only on success.
- **`AGENTS.md`:** one Commands line, **Fetch an issue's body**, after **Fetch an issue**.
- **Approval:** the human approved the exact diff of the three protected files in this session, and the commit used `HUMAN_APPROVED=1`.
- **CI:** green on the first push (runs 43377955473 and 43377942002). QA PASS at `1b712cc`, all nine criteria, no finding at Medium or higher. The Reviewer said "Ship" with no must-fix finding.
- **Kit:** the `Makefile.mk` edit makes `make kit-check` report a derivative of its manifest. For the human's `KIT_VERSION` bump (epoch-batch item 7): `_docs/agent-kit/templates/Makefile.mk` changed; the manifest entry and `_docs/agent-kit/README.md` line 161 (which does not name the target) are not updated here.

**What I learned:** the Engineer's own copy of its diff was garbled at the end of the template hunk; reading `git diff` myself before showing it to the human caught that.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- Engineer: active time unknown, tool uses unknown (Kiro Web gives neither).
- QA: active time unknown, tool uses unknown.
- Reviewer: active time unknown, tool uses unknown.

## Files created or modified

- `Makefile`, `_docs/agent-kit/templates/Makefile.mk`, `AGENTS.md` (protected; approved diff).
- `_human-tasks/2026-11-13T0648Z-human-task-073-orchestrator-check-issue-body.md`
- This file.

## Decisions made by the human

- Approved the exact diff of the three protected files, as shown.
- Decision point: apply none of the Reviewer's findings to #73. Findings 1 (the error text blames `gh` when `repo` fails), 3 (the long help text) and 4 (no test of `issue-number-ok`) are parked as follow-up candidates; finding 2 (manifest) belongs to epoch-batch item 7.
- Option A: the two by-hand checks go in a `_human-tasks/` file and do not block the merge.

## Mismatches with the spec or design docs

none.

## Commands to validate

- **Verify:** `make verify` (CI on the branch; green on `1b712cc`).
- **Fetch an issue's body:** `make issue-body N=<n>`; the by-hand cases are in the human-task file above.

## Proposed AGENTS.md changes

none (the one Commands line was approved and committed).

## Temporary changes

none. `make clean-scratch` ran.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- Reviewer 1, 3 and 4 above (wording and a missing test for `issue-number-ok`); the PM can file one small follow-up if the human wants it.

## Follow-ups for the next session

1. After the human merges #73 and the Close is posted, start #71 from the latest `main`, with a hash check first.
2. The by-hand checks in the human-task file are open until the human runs them.
