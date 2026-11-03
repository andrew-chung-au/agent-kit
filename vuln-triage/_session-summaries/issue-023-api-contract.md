# Issue #023: API contract (`_docs/openapi.yaml` and `_docs/api.md`)

**Date:** 2026-10-21
**Spec version:** 67a4076

## What changed and why

- #23's contract was completed against the PM-groomed body and the senior review's items A-N: 403 on `registerAsset`/`reScan`, the `401 -> 403 CSRF -> 404 -> 403 owner -> 422 -> 409` check order, strict request bodies, `AuditEntry.actorDisplayName`, case-insensitive owner match, the tighter GitHub URL pattern, parameter `$ref`s, `epss` bounds, `format: email`, and the unpaginated pilot-scale `GET /findings` note.
- The protected `make openapi-validate` target was added and run; the contract was reviewed and approved by the human at `3cb40af`.
- At the decision point the human approved three doc changes: the `AGENTS.md` Commands line, three spec sentences (US-6 brief pending, US-11 owner restriction, US-10 manual re-scan) and the architecture A30 case-insensitive owner-match note.
- The human scheduled #44 (cloud sessions) after #23 and before #27, and approved filing #45 (D4 alignment) and #46 (QA risks).

## Files created or modified

- `_docs/openapi.yaml`: `7d6fe6e`, `3cb40af` (A-N).
- `_docs/api.md`: `3bdc565`, `d9817f9`.
- `_docs/planning-process.md`: `dc94837` (approved Stage 3 text, alone).
- `README.md`: `49a296f` (links only).
- `Makefile`: `aa066fc` (protected, `openapi-validate`).
- `AGENTS.md`: `5b35ece` (protected, Commands line).
- `_docs/specs.md`: `67a4076` (protected, three sentences).
- `_docs/architecture.md`: `525284b` (A30 note).
- `_docs/ai-usage-log.md`: `752b363`, `2486d7a`, `052f53a`, `1f5a21b`, and the orchestrator entry.
- `_docs/roadmap.md`: `13b0ee9` (#44 scheduling) and the check-in.
- This summary.
- Approved GitHub records: contract review 6308766939; approval records 6308646350 (`Makefile`), 6309239012 (`AGENTS.md`), 6309240051 (`_docs/specs.md`).

## Decisions made by the human

- Contract review at commit `3cb40af`: approved, no changes requested.
- Approve the revised `openapi-validate` target and its validator runs.
- Apply the `AGENTS.md` Commands line; apply all three spec-note sentences; add the A30 note.
- QA risks outside the criteria: one follow-up issue (#46).
- File the D4 alignment issue now (#45).
- Schedule #44 after #23, before #27 (the issue's option B).

## Mismatches with the spec or design docs

- None after the spec commits. The three grooming notes were applied to `_docs/specs.md`, and A30 now records the case-insensitive owner match.

## Commands to validate

- **Verify:** `make verify` PASS WITH WARNINGS (35/35 tests; whitespace PASS). The 7 weakened-test warnings are from the earlier unpushed #22 commit `759735a`; #23 changes no test files.
- `make openapi-validate`: exit 0 on `_docs/openapi.yaml`; exit 2 on a `.scratch/` copy with a broken response `$ref`; exit 2 on `OPENAPI=../x.yaml` before the validator runs.
- `make assert-clean`: PASS at `13b0ee9`.

## Proposed AGENTS.md changes

- Applied in `5b35ece` with the human's approval and approval record 6309239012.

## Temporary changes

- `uvx` installed `openapi-spec-validator==0.9.0` into uv's tool cache for the validator runs; it is a cache entry, not a project dependency, and was left in place.
- No processes were started; no system configuration changed.
- `make clean-scratch` ran after QA: `.scratch/` is empty.

## Permission review

- Read-only (propose allowing):
  - QA's `.scratch/` check scripts (`node`, `python3`), `sed -n` reads, `ls ... > .scratch/...` and one `gh issue view ... | grep`; basis: the `*` and `* > *` `ask` rules (the piped command also matched the chained-command rule).
  - The PM's `python3` scratch checks for the body edit; basis: the `*` `ask` rule.
- Writes to the record (keep asking):
  - `gh issue edit 23` (PM body edit, A-K); basis: `gh issue edit*` `ask` rule.
  - `gh issue comment 23` (contract approval record, follow-ups) and `gh issue comment 44` (scheduling); basis: GitHub write to the record.
  - `gh issue create` for #45 and #46 by the PM; basis: GitHub write to the record. The PM's follow-up-filing return did not include a separate approval line; recorded from its reported actions.
  - Editing the protected `Makefile`, `AGENTS.md` and `_docs/specs.md`; basis: merits requests for protected files.
  - `HUMAN_APPROVED=1 git commit` for `aa066fc`, `5b35ece` and `67a4076`; basis: merits requests for protected commits.
  - `make openapi-validate` on the real file and a `.scratch/` copy; basis: merits request (validator download/run).
- Risky (propose denying): none.
- Proposed `opencode.json` and `.claude/settings.json` changes: none.

## Interruptions

- None. One QA re-check returned FAIL because the orchestrator had left `_docs/roadmap.md` uncommitted and an unrelated #44 usage-log commit (`be4c100`) had landed; the roadmap was committed as `13b0ee9` and the re-check passed.

## Unrelated problems noticed but not fixed

- `openapi-spec-validator 0.9.0` does not catch a broken `$ref` in a request-body schema; the `openapi-validate` path guard also lets a path containing a space through; and the "`format` is an annotation by default" sentence is untagged. Filed as #46.
- The Engineer appended a usage-log entry with a shell heredoc, against the "never edit files from the shell" convention; the content is correct and committed.
- The default `make verify` still warns about 7 removed assertions from the unpushed #22 test rewrite.

## Follow-ups for the next session

- **#44 (scheduled):** PM grooms it first (the issue is still ungroomed); work starts after #23, before #27, and needs the human's GitHub setup in `_docs/cloud-sessions.md` § 4.
- **#45:** D4 `types.ts`/mock/screens/35-test alignment; starts after #23 and before step 9 (#34). #34/#25 wait for it.
- **#46:** validator/guard/`VERIFY:` risks; under "Later".
- **#27:** Stage 3 part 2, after #44; step 8 closes when #27 closes.
- **#31:** the human sets up the Compose dev container using `_docs/docker-runbook.md` section 1.
