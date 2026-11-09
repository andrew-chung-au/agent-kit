# Issue #31: Kit evolution in using repos: hash manifest, derivative versioning and import review (Part 1)

**Date:** 2026-11-09T16:14Z (UTC)
**Spec version:** none

## What changed and why

This session closed out #31 Part 1. The implementation was merged earlier: commit `91ae241`, merged as `4007dad` (PR #69). It adds the hash manifest generator, `make kit-check` and `KIT_VERSION` derivative claims. The only QA verdict on the issue was a FAIL of 2026-11-04 (at `e26c8c9`), on three criteria: a symlink named `*.pyc`, `__pycache__` or `MANIFEST.sha256` was skipped instead of refused; no test covered that; `make verify` did not pass.

Later issues fixed those (#143 for the symlink refusal and its tests; the `make verify` hang was reported fixed on #168). No code was changed here. A fresh QA launch re-checked every criterion on `origin/main` at `7c53c54` and posted `QA: PASS` (comment https://github.com/andrew-chung-au/agent-kit/issues/31#issuecomment-6742422621). This summary is the `Summary:` file for the Close comment.

**What I learned:** a QA FAIL on a merged issue can sit for days with its fixes landing under other issue numbers, so a close needs a fresh QA at the current commit, not a reading of the old verdict.

## Reflection

### QA

unknown (role not asked)

### Engineer

unknown (role not asked)

### PM

unknown (role not asked)

## Launch usage

- QA (#31, sub-agent): active time unknown, tool uses unknown (the completion notification did not give figures)

## Files created or modified

- `_session-summaries/2026-11-09T1614Z-issue-031-orchestrator-kit-manifest-close.md` (this file)
- QA wrote only under `.scratch/` (verdict text, an exported copy of `origin/main`, throwaway trees and attack scripts). `make assert-clean` passed afterwards (HEAD `023d6f2`, no changes).

## Decisions made by the human

- The human asked for the QA runs and for session summaries and QA comments to be written where needed to close issues. Whether to close #31 by hand or with `make issue-close` is still open.

## Mismatches with the spec or design docs

none (the repo has no spec file)

## Commands to validate

QA could not run `make verify`: the exported tree has no git history. It ran **Verify** as `make test` plus `python3 -B agent-kit/scripts/check-claims.py` on the export of `origin/main`.
- `make test`: 1482 run, 0 failed, 1 skipped (`tests/test_dup_report.py:117`, "root can read any file", environmental, from another issue)
- `check-claims.py`: OK (38 docs, 130 make targets, 289 kit paths, 17 installable paths covered)
- whitespace and weakened-test checks: not run on the export; the QA read #31's diff (583 test lines added, none deleted) instead

## Proposed AGENTS.md changes

none

## Temporary changes

QA created folders and scripts under `.scratch/`; they are not cleared yet (`make clean-scratch` has not been run, because other `.scratch/` files here are still in use). Nothing was started that is still running.

## Interruptions

none. One QA `make test` was started in the background and its output could not be read, so it was re-run in the foreground; nothing was left running.

## Unrelated problems noticed but not fixed

- `kit-manifest.py` has no `OSError` guard around the manifest write; a failed write might leave a `MANIFEST.sha256.tmp`. Not tested (the sandbox runs as root, so unwritable and unreadable cases cannot be reproduced). Low risk: it is a release step.
- A sub-agent's `pgrep` printed a process line containing an access token. It was not copied, but it is in that transcript; consider rotating the token if transcripts are kept.
- #91 got `QA: FAIL` in the same session: the approved Decision record was never committed (no `_docs/decisions/091-installed-file-map.md`, no index row). It is not closed.
- #171 has `Recorded sha256: none`: no PM hash was ever recorded, so no role was launched on it.

## Follow-ups for the next session

- Human decision: close #31 by hand, or post the Close comment (`QA PASS commit: 7c53c54`, `Merge commit: 4007dad`, `Verify:`, `Summary:` this file) and run `make issue-close N=31`.
- #91: commit the approved Decision record with its index row, then re-run QA, then the second Heavy QA launch (code review).
- #171: record a hash (a `PM:` comment) before any QA.
