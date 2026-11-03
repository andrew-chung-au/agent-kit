# Issue #041: spec fixes from the #3-#8 QA risks

**Date:** 2026-10-20
**Spec version:** 1445ca5

## What changed and why

- `withdrawn` is now set by a re-scan when OSV withdraws the advisory, never by the scheduled refresh, so the rule from #7 Decision 2 (status changes only by re-scan or a person) holds without exceptions. A withdrawn advisory gives `withdrawn`, not `fixed`. A KEV or EPSS change moves signals and rank only.
- US-8: the n8n token may create, comment on and close issues in `vuln-triage-findings` only. The GitHub permission claims carry `VERIFY:`.
- Asset scan status: five values (`not yet scanned`, `scan failed`, `scanned, findings`, `scanned, incomplete`, `scanned, clean`), with a precedence order. There are three failure reasons (`feed unavailable` meaning OSV only, `lockfile parse error`, `repository unavailable`), and each of eight cases maps to exactly one value. A KEV or EPSS outage no longer fails a scan. E3, E4 and E10 were brought in line.
- The status line now marks the 2026-10-16 review as resolved.
- This was the first issue worked under the roadmap's 2026-10-20 priority rule (product work first); it opens step 7.

## Files created or modified

- `1445ca5` protected commit, `_docs/specs.md` only (+47/-14), committed alone with `HUMAN_APPROVED=1`.
- `6a33ba0`: usage-log entries for the draft and the commit. Earlier the same day: `86ccb39`, `0308252`, `d6cdc2e`, `c77a437` (roadmap check-in, reprioritisation, decisions, D4 note).
- Comments on #41: decisions 6287579005 (D1-D3) and 6287964999 (D4); PM grooming 6288008663; Engineer diff 6288084947; approval record 6288541138; QA PASS 6288587511; decision point 6289212246. On #31: 6287579525 (dependency on #26 dropped).
- `_docs/roadmap.md`, `_docs/ai-usage-log.md` and this summary.

## Decisions made by the human

- The roadmap was reprioritised toward product work: step 4 (#33) deferred, and decision 4 (promoting #38 and #39) withdrawn.
- #41: D1, D2, D3 and D4 option 1 in each case; D5 option 1 (`repository unavailable`), chosen when the diff was approved.
- Roadmap decision 2: #31 no longer waits on #26; it starts once step 7 names the environment.
- Approved the exact diff before `1445ca5`.
- Decision point: QA's status-model risks 1-3 become inputs to the step 7 issue; risks 4 and 5 need no action.

## Mismatches with the spec or design docs

- US-10 and US-11 predate the `withdrawn` rule and don't refer to it (QA risk 3). This is a step 7 input, recorded in 6289212246.

## Commands to validate

- **Verify:** `make verify BASE=c77a437` PASS (QA): 35 tests, whitespace PASS, no test files changed.
- **Diff integrity:** the applied diff was `cmp`-identical to the approved patch before staging. After the commit, a `.scratch/` script confirmed a single parent, only `_docs/specs.md` changed, and `git show` matched the patch. QA independently confirmed that the record, `git show` and the proposal are byte-identical, and that the blob ID matches.
- **Criteria:** the Engineer's 61/61 checks; QA's own script passed 81/82, and the one miss was a gap in the script's prefix list, confirmed by a separate check that nothing outside the allowed regions changed.
- **Assert clean:** `make assert-clean` PASS at `6a33ba0` after QA; HEAD unchanged.

## Proposed AGENTS.md changes

None.

## Temporary changes

None. No process was started and nothing was installed. `make clean-scratch` ran; `.scratch/` is empty.

## Permission review

- Read-only (propose allowing): none.
- Writes to the record (keep asking): none.
- Risky (propose denying): none.
- Proposed `opencode.json` and `.claude/settings.json` changes: none.
- Sources: the PM, Engineer and QA comments all say "none"; the orchestrator had none (the `HUMAN_APPROVED=1` commit ran after the human's approval of the diff).

## Interruptions

None.

## Unrelated problems noticed but not fixed

- `make verify` warns about 7 removed assertions in `frontend/src/test/vulntriage.test.tsx` from earlier unpushed commits since `origin/main`. The human needs a reason for each when pushing.

## Follow-ups for the next session

- Roadmap step 7: the PM proposes the Stage 2 architecture issue, taking its inputs from #41 (out-of-scope list, 6288008663, 6289212246) and #9. Creating the issue needs the human's approval.
- #31 can start once step 7 names the Docker-capable environment.
