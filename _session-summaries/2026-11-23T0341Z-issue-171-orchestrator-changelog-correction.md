# Issue #171: Cut kit 1.10: version line, changelog with upgrade notes, manifest and tag

**Date:** 2026-11-23T03:41Z (UTC)
**Spec version:** none

## What changed and why

The QA re-check of #171 failed on one Medium finding (F-171-1): the `v1.10` tag's own `README.md` still says, under "Adding the kit to a project folder", that there is no tagged release yet and that a project gets the kit by cloning, which the tag itself makes false. The tag cannot change, so the human chose QA's recommendation to record the correction in the 1.10 upgrade notes. `agent-kit/CHANGELOG.md` gains a `**Correction (2026-11-23).**` paragraph at the end of `## Changes in 1.10`, saying the tagged paragraph predates the tag and is wrong for 1.10: a project taking 1.10 gets the `agent-kit` folder and its `MANIFEST.sha256` from the tag, as `releasing.md` describes, and the current tree replaces the paragraph with `install-and-upgrade.md`. Commit `51a1e5b`, approved by the human and made with `HUMAN_APPROVED=1`. QA re-checked PASS at `51a1e5b` with `0 fail / 0 log`; F-171-2 to F-171-5 carry over as logged findings.

**What I learned:** the tag's stale paragraph was introduced in `2b73ff5` (2026-11-04) and removed from the current tree in `9a99e6c` (#181), so the correction is a note about the tag, not a current-tree defect.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- Engineer (fix): active time unknown, tool uses unknown
- Engineer (commit): active time unknown, tool uses unknown
- Fix check (fresh subagent): active time unknown, tool uses unknown
- QA (re-check): active time unknown, tool uses unknown

## Files created or modified

- `agent-kit/CHANGELOG.md` (commit `51a1e5b`): the correction paragraph, 2 insertions.
- `_docs/records/findings/171.json` (commit `35263a6`): F-171-2 to F-171-5, the four unfixed findings.
- `_session-summaries/2026-11-23T0341Z-issue-171-orchestrator-changelog-correction.md` (this file).

## Decisions made by the human

- Resolve F-171-1 by adding the approved correction paragraph to the 1.10 notes, not by changing the tag or the current-tree README.
- Approve the protected commit of `agent-kit/CHANGELOG.md` with `HUMAN_APPROVED=1`.

## Mismatches with the spec or design docs

none (the repo has no spec file)

## Commands to validate

- **Verify:** `make verify` at `51a1e5b`: PASS, 1862 tests, 0 failed; claims check OK; whitespace PASS; weakened tests none.
- `make assert-clean` after QA: PASS; HEAD `51a1e5b`.
- `make route-findings N=171`: `F-171-1 points 1 rounds 0 route engineer guard no`.
- `make check-format KIND=qa N=171 FILE=.scratch/171-qa-recheck.md`: `ok`.

## Proposed AGENTS.md changes

none

## Temporary changes

None to the system. `.scratch/` held the issue dump, the Engineer and QA drafts and the fix-check notes; `make clean-scratch` removed them.

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-171-2 (L, in, C1): two 1.10 bullets carry no "Existing projects:" label.
- F-171-3 (M, out): a kit-only project gets `missing` installed-file lines from `make kit-check`.
- F-171-4 (L, in, C2): C2 names `72747a1` as the `AGENTS.md` template's last change; it is `67153ed`.
- F-171-5 (L, in): the tagged README's release-zip wording contradicts step 6.
- `make sweep-due` reports `due: no sweep recorded`.

## Follow-ups for the next session

- The human reviews and pushes the three commits on `main`: `51a1e5b`, `35263a6` and this summary's commit.
- The four logged findings wait for the next sweep; F-171-4 needs a human amend decision if C2 is to name `67153ed`.
