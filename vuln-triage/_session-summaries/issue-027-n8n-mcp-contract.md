# Issue #027: API contract for n8n and the MCP server (Stage 3, part 2)

**Date:** 2026-10-21
**Spec version:** 97893c1

## What changed and why

- Session check: no `_docs/specs.md` commits between the last recorded version (`67a4076`) and the session start, so no backlog review was needed.
- The PM's grooming asked one decision: the human chose option 1, keeping #27 to n8n and MCP; the US-15 responder's read-only API became follow-up #50.
- The Engineer added the nine n8n/MCP operations, the `n8nAuth` and `mcpAuth` bearer service credentials (6 and 4 operations, MCP GET-only), `getAsset` shared with MCP, the job-based delivery schemas and the untrusted-text marks; `_docs/api.md` got the 19-row table, auth, check order, schemas, pagination, Stage 3 checklist (US-15 → #50) and wire decisions.
- The human approved the contract at `7355d8e`. QA PASS. At the decision point the human took all recommendations: mark OSV-sourced ids and ranges untrusted (R2), the architecture and US-12 spec notes, R3-R5 noted on #24, R1/R6/R7 accepted. Two further rounds marked `cveId` and corrected the overview (one QA FAIL on the "inside each dependency" wording, fixed), and the architecture quoting sentence was corrected.

## Files created or modified

- `_docs/openapi.yaml`: `7355d8e`, `6494f28`, `e74b2d1`, `fe55261`.
- `_docs/api.md`: `d89597a`, `9191aea`, `07e6d40`.
- `_docs/architecture.md`: `7855dda` (MCP output, token names, n8n digest, 403, A21), `1f4515a` (quoting sentence).
- `_docs/specs.md`: `97893c1` (protected, US-12 any-status line).
- `_docs/ai-usage-log.md`: `a9557e0`, `9086658` (Engineer) and the orchestrator entry; `_docs/roadmap.md`: step 8 done, #50 note, check-in.
- This summary.
- GitHub: #50 created; #27 body responder bullet links #50; #24 PM comment with R3-R5.
- Approved GitHub records on #27: contract review 6316222176; re-reviews 6316873471 (`6494f28`), 6317003856 (`e74b2d1`), 6317141600 (`fe55261`); protected-change approval record 6316890596 (`_docs/specs.md`, `97893c1`).

## Decisions made by the human

- US-15 scope: option 1, follow-up #50 (approved filing it).
- Contract approved at `7355d8e`; re-reviews of `6494f28`, `e74b2d1` and `fe55261` approved.
- Decision point: all recommendations (architecture notes 1 and 3-8, US-12 spec line, R2 fixed now, R3-R5 to #24, R6 in the usage log, R7 and R1 accepted, #27 body tidy-up).
- `cveId` and overview gaps: fix now (option 1). Last two risks: option 1 (architecture quoting sentence fixed; MCP brief fields left as they are, already marked untrusted).
- Approved the full spec diff used in the approval record (the first request showed an excerpt without the header lines; the human re-approved the verbatim diff before the record was posted).

## Mismatches with the spec or design docs

- None known after `97893c1`, `7855dda` and `1f4515a`. The openapi.yaml overview does not list the MCP brief fields among the marked fields outside `untrustedAdvisoryData`; the human chose to leave it (they are marked and are generated text).

## Commands to validate

- **Verify:** `make verify` PASS on every push (pre-push hook; 35/35 tests, whitespace PASS, no test files changed).
- `make openapi-validate`: exit 0 on `_docs/openapi.yaml`; exit 2 on `.scratch/` copies with a broken response `$ref` (Engineer and QA).
- QA verdicts: PASS 6316386844 (`a9557e0`), PASS 6316919374 (`97893c1`), FAIL 6317030883 (`9086658`), PASS 6317071288 (`fe55261`).
- `make assert-clean`: PASS after each QA run (HEAD `a9557e0`, `97893c1`, `9086658`, `fe55261`).

## Proposed AGENTS.md changes

- None applied. Suggestion for a later session: a `make issue-create` REST target, because `gh issue create` uses GraphQL and the PM could not file #50 in the cloud session (the orchestrator used the GitHub MCP tool).

## Temporary changes

- No processes started; no system configuration changed.
- `make clean-scratch` ran at the end: `.scratch/` is empty.

## Permission review

Role comments: every PM, Engineer and QA comment in this session has the "Commands and changes that required approval" line; all except the PM's #50 record (6315866978) say none. The PM's grooming comment (earlier session) listed `gh issue edit 27` and two `python3 .scratch/` scripts; they are outside this session and not repeated here.

- Read-only (propose allowing): none newly needing a rule. Engineer and QA `python3 .scratch/*.py` checks and `git -C ... status/diff/log` ran without matching an `ask` rule.
- Writes to the record (keep asking):
  - GitHub MCP `issue_write` create for #50; basis: merits request (GitHub write to the record).
  - `gh api -X PATCH repos/andrew-chung-au/vuln-triage/issues/27 -F body=@...` (body tidy-up); basis: merits request (GitHub write to the record).
  - `HUMAN_APPROVED=1 git commit` for `_docs/specs.md`; basis: merits request (protected commit).
  - `git push -u origin claude/compassionate-hamilton-k90q3r` (six pushes); basis: AGENTS.md cloud-session rule; recorded here because it publishes to GitHub.
- Risky (propose denying): none.
- Proposed `opencode.json` and `.claude/settings.json` changes: none.

## Interruptions

- The worker process restarted mid-session. Checked afterwards: the Engineer's R2 commits and comment, and the PM's #24 comment, had landed; the PM's #27 body edit had not, so the orchestrator applied the PM's prepared body file. My uncommitted architecture/spec drafts survived.
- The stop hook twice asked to commit uncommitted changes while they waited for the human's approval or for the Engineer; they were left uncommitted until approved or finished.

## Unrelated problems noticed but not fixed

- `gh issue create` has no REST make target (see Proposed AGENTS.md changes).
- The cloud stop hook (`~/.claude/stop-hook-git-check.sh`) asks to commit and push drafts that are waiting on approval; it conflicts with the protected-file approval flow. Not changed (user-level setting).

## Follow-ups for the next session

- **#45:** D4 alignment, before step 9 (#34).
- **#50:** responder read-only API contract; PM grooms it; the human places it in the roadmap.
- **#24:** its grooming should pick up the R3-R5 notes (PM comment on #24) and implement the #27 operations and refused cases.
