# Issue #117: Human-only read-only comparison of the push check from the clean clone (#91 piece e)

**Date:** 2026-11-04T12:02Z (UTC)
**Spec version:** none

## What changed and why

#117 documents a human-only, read-only way to compare the push check in the clean clone with the kit's reference copy, so the human can see drift without agents touching `agent-kit/environments/local-sandbox/pre-push`. The change is documentation and a test: `agent-kit/environments.md` and `tests/test_push_check_doc.py`. No script was added and `pre-push` was not edited.

This is a closing record written from the issue's comments. The issue's QA history: PASS 03:12, FAIL 06:18, PASS 08:07, and a final PASS at `3185893` (this session, PR #139's head). PR #139 merged into `main` at 2026-11-04T12:01Z as `335625b`; I confirmed `3185893` is an ancestor of `origin/main`.

**What I learned:** none beyond the closing record.

## Reflection

unknown (role not asked).

## Launch usage

- QA final launch: about 6 min (356,798 ms), 20 tool uses.
- Earlier QA launches and the Engineer's work on #117 are not counted here (not part of this session's notifications).

## Files created or modified

`agent-kit/environments.md`, `tests/test_push_check_doc.py` (PR #139). This record is the only file added now.

## Decisions made by the human

- 2026-11-04: merged PR #139 after QA PASS. The tier label was left to the human; #117 carries only `approved`, so the close gate treats it as Standard.

## Mismatches with the spec or design docs

none known.

## Commands to validate

**Verify:** QA's `make verify` against the merge-base `0769975`: PASS, 1268 tests, 29 assertions added, 0 removed. Against `origin/main` it failed only because the branch lacked #138 and #144 at the time (a test file shown as deleted); `make assert-clean` PASS.

## Proposed AGENTS.md changes

none.

## Temporary changes

none.

## Interruptions

none.

## Unrelated problems noticed but not fixed

QA's minor notes on #117: a missing file, a symlink or a non-regular file exits 0, and only a mismatch exits 1; the test reads only the first fenced block in the section. The version bump is the human's call.

## Follow-ups for the next session

#118 (PR #140) waits on this merge for a recheck; its QA launch is running.
