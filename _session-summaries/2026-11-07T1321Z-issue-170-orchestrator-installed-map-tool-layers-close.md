# Issue #170: Installed-file map covers the tool-layer files

**Date:** 2026-11-07T13:21Z (UTC)
**Spec version:** none

## What changed and why

#170 added nine `repo` lines to `agent-kit/installed-files.txt` for the OpenCode and Claude Code agents, the sweep skills and the permission-log plugin, a new `optional` rule so an uninstalled plugin reads `not installed (optional)` and exits 0, a test that compares the START files with the map in both directions, and the matching README and import-step text.

This session did not build it: the Engineer's commit `c188ca4` merged as `d1270a1` (PR #178) on 2026-11-06 at 12:05Z, and QA passed at `c188ca4`. This session ran the decision point and the close.

**What I learned:** the merge was already on `main`; only the summary and the Close step were missing.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

none

## Files created or modified

- `_session-summaries/2026-11-07T1321Z-issue-170-orchestrator-installed-map-tool-layers-close.md` (this file)
- `agent-kit/README.md`: the `Unreleased` lines for #143 and #170, committed as `baabd0d` (protected, approved by the human).

## Decisions made by the human

- Sweep: run the first sweep at the 1.10 cut (#171), not in this session.
- Changelog: add the `Unreleased` lines for #143 and #170 now, and commit them.
- Kiro Web leftovers from #172: the PM folds them into #52 at its next grooming.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make test`
**Assert clean:** `make assert-clean`
**Close:** `make issue-close N=170`

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- A directory at an optional file's install path reads `not installed (optional)` and exits 0 (QA's contrived case); a non-optional entry in the same state reads `missing`.
- A project that customises a copied agent file reads `drift` on every check. That is what the map is for, but it is worth knowing before the SOCBoard import.
- Not verified against a real SOCBoard checkout; #169 and #171 will exercise it.
- The PR also edited `procedures/kit-import.md` step 7 and the `kit-check.py` docstring (description only, outside the issue's file list); QA accepted them.
- `AGENTS.md` and `process.md` still tell agents to run `gh issue view <N> --json labels` directly, which fails in Kiro Web (#172 QA); by the human's decision this goes into #52.

## Follow-ups for the next session

- `make issue-close N=170` in this session, after this summary.
- #171: cut 1.10 and run the first sweep there, by the human's decision. The SOCBoard import should show whether `optional` and the drift lines behave on a real project.
- #91: its approved Decision record is still not committed as `_docs/decisions/091-installed-file-map.md`; it needs that and a QA check, or a human-approved close.
