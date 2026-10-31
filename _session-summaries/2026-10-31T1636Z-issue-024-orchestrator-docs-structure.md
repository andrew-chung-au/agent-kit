# Issue #24: Docs structure: docs index with routing table, entry types and one filename convention (Part A)

**Date:** 2026-10-31T1636Z (UTC)
**Spec version:** none

## What changed and why

The kit now has a docs index template with a routing table (where each kind of detail goes), five entry-type templates (decision record, measurement, source, runbook, plus the existing session summary) and one filename convention for log-style entries: `<timestamp>-<kind>-<id>-<role>-<slug>.md`, UTC, no colons, timestamp first so `ls` sorts chronologically. One file per entry means parallel agents never share a file. Old `issue-NNN-...` summaries keep their names. The idea came from the human's RAG projects, generalised: dataset notes became sources and inputs, evaluation notes became measurements.

**What I learned:** loose files directly under `templates/` weren't covered by the claims check, so the Engineer added a test and two blueprints rows.

This session also filed #23 (scorecard and reflection prompts, self-learning loop part 1) and #24, and agreed the order #24 Part A, then #23, then #18 re-groomed after Phase 2.

## Files created or modified

Commit 4eba51d (13 files): `AGENTS.md`, `agent-kit/README.md`, `agent-kit/blueprints.md`, `agent-kit/procedures/session-summary.md`, `agent-kit/process.md`, `agent-kit/templates/AGENTS.md.template`, `agent-kit/templates/session-summary.md`, `agent-kit/templates/adr.md` (new), `agent-kit/templates/docs-index.md` (new), `agent-kit/templates/measurement.md` (new), `agent-kit/templates/runbook.md` (new), `agent-kit/templates/source.md` (new), `tests/test_claims.py`.
Live code: `tests/test_claims.py` runs live in `make test` and `make verify` (three new tests). Nothing under `agent-kit/scripts/` or `agent-kit/claude-code/hooks/` changed.
Doc budget: always-loaded 4,422 to 4,420 words (no file grew); core Markdown 14,297 to 15,020 (+723, +5.06%, about a third of the 15% cap).

## Decisions made by the human

- Order of the three session-summary issues: #24 Part A, then #23, then #18 re-groomed after Phase 2. #18's hand-kept prompt record is dropped, because the Phase 2 permission log replaces it ("has not worked before").
- #24 is Part A only: naming first, `docs-check` filed later as a separate target not wired into `make test` or `make verify`.
- Ran the approved commit 4eba51d themselves.
- At the decision point: accept the header-only Entry types table; one version bump after #23 lands (covering #22, #24 and #23); fold QA's small follow-ups into #23's grooming and file Part B later, after the index has been used in a real project.

## Mismatches with the spec or design docs

None (there is no `_docs/specs.md`). One conflict between two criteria: "one row per entry type" in the Entry types table can't hold within the 150-word limit, because `wc -w` counts table pipes. QA passed it with a caveat and the human accepted it.

## Commands to validate

- **Verify:** `make verify` (passes at 4eba51d: claims OK, 60 tests, 0 failed)
- **Test (all):** `make test`

## Proposed AGENTS.md changes

Applied in 4eba51d with the human's approval: the **Session summaries** line no longer lists the filename patterns and points to the procedure.

## Temporary changes

None. `make clean-scratch` ran at the end of the issue. Nothing was started that needs stopping.

## Interruptions

None. `make assert-clean` fails only on the known baseline: ` M .claude/settings.json` (the human's change) and the two untracked `proposals/` files. HEAD did not move during QA.

## Unrelated problems noticed but not fixed

- The PM that filed #24 appended text to its scratch file with a shell heredoc, which the rules forbid. It was git-ignored scratch and nothing tracked was touched.
- `.claude/settings.json` is still modified and uncommitted, and the two `proposals/` files are untracked.

## Follow-ups for the next session

- Ask the human to add `approved` to #23, so it is groomed against the files as #24 left them. Pass these notes to its PM, since #23 edits the same procedure and template: give the exact `git log -1 -- _session-summaries/` command in `process.md` step 2; add a line on how to read old `issue-NNN-...` names; cover the `-3` collision case; strengthen the example-filenames part of the third new test (bare filenames are never flagged); and report #23's own word delta, because the total budget headroom is shrinking.
- Still open from #22: the human's live checks with the kit's settings installed in Claude Code and OpenCode (including `gh run view 1 --log` being refused), and the stale `agent-kit/opencode/START.md` wording (small follow-up, not filed).
- Version bump: one minor bump after #23 lands, with the combined changelog for #22, #24 and #23.
- Part B (`docs-check`, index-based, `FIX=1`): file after the index has been used in a real project.
- #18 waits for the Phase 2 permission logging work and is then re-groomed without the hand-kept prompt record.
