# Issue #116: Reverse import writes a feedback bundle from installed copies (#91 piece d)

**Date:** 2026-11-04T11:47Z (UTC)
**Spec version:** none

## What changed and why

#116 adds `agent-kit/scripts/kit-feedback.py` (reverse import): it writes a feedback bundle from a project's installed copies of kit files, using the reference kit's installed-files map as the trusted list. Built by Kiro as the Engineer; this session re-checked it after an earlier QA FAIL.

This session: the Engineer's fixes at `5fc966d` (error scrubbing, atomic write, byte-for-byte line comparison for `prefix:` entries with differing lines withheld, reference map as the trusted list, a wider denylist, hard-link refusal) passed QA launch 1. At the human's approval, one more change was added: a warning line above every whole-copied non-prefix changed `repo` entry (`e3c7293`), because such entries reach the bundle with only marker stripping. QA launch 2 passed at `e3c7293`.

PR #138 was merged into `issue-114-kit-check-installed-map`, a branch PR #136 had already merged to `main`, so #116's code was not on `main`. PR #144 (that branch into `main`) fixed it: merge `0e74efe`, 2026-11-04T11:46Z. I confirmed `e3c7293` is an ancestor of `origin/main`.

**What I learned:** check each PR's base branch against `main` before telling the human a merge order; I had the data and did not check, and the stranded merge cost an extra PR.

## Reflection

unknown (role not asked).

## Launch usage

- QA launch 1 (re-check): about 12 min (725,839 ms), 32 tool uses.
- Engineer (bundle warning): about 8 min (474,987 ms), 19 tool uses.
- QA launch 2: about 7 min (422,192 ms), 22 tool uses.
- PM and other launches for neighbouring issues are not counted here.

## Files created or modified

`agent-kit/scripts/kit-feedback.py`, `tests/test_kit_feedback.py` (and the earlier #116 files in PR #138: `kit-check.py`, `kit-compare.py`, `kit-map.py`, `Makefile`, docs and tests as listed in the PR). This session's own change: the warning line, `e3c7293` (2 files, +17).

## Decisions made by the human

- Approved the bundle warning line, and the commit `e3c7293` (`HUMAN_APPROVED=1`).
- Sent the cosmetic scrub finding to #141.
- Pushed `e3c7293`, merged #138, and opened and merged #144 to bring the stack to `main`.

## Mismatches with the spec or design docs

none known.

## Commands to validate

**Verify:** `make verify BASE=origin/main` passed in QA launch 2: 1312 tests, no failures, no weakened tests. `make assert-clean` passed.

## Proposed AGENTS.md changes

none.

## Temporary changes

none.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- A drifted non-prefix entry is copied whole after marker stripping; personal text outside the markers reaches the bundle until the human reads it. The new warning says so.
- QA, for #141: the temp-file cleanup in `main` calls `exists` and `unlink` directly instead of through `_fs`; a symlink planted at the temp name in `.scratch/` would be followed.
- `kit-import.md` steps 1 to 4 were reworded beyond the one added sentence (harmless).
- The scrub rewrites path-like text after a space in an error message (cosmetic; on #141).

## Follow-ups for the next session

- #143 (symlink-named manifest entries) can start now that #116 is on `main`.
- Retarget PR #137 (#115) to `main`; it still has the stale base.
