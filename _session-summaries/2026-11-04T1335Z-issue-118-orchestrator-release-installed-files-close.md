# Issue #118: Release procedure notes installed files and ships the map (#91 piece f)

**Date:** 2026-11-04T13:35Z (UTC)
**Spec version:** none

## What changed and why

#118 makes the release procedure note installed files and ship the installed-files map. Its first QA (03:12) failed because the README pointed at a section that existed only in PR #139 (#117). After #139 merged, QA rechecked PR #140 at head `8b9b3c6`, found the pointer target ("Comparing the installed push check (human only)") on `main`, and passed it. PR #140 merged at 2026-11-04T12:17Z as `f6d6a75`; GitHub closed the issue itself two seconds later, so this is a closing record written afterwards from the issue's comments.

**What I learned:** a PR body that closes the issue on merge skips the Close comment and its recorded lines; the new PR template says "Refs #N" for that reason.

## Reflection

unknown (role not asked).

## Launch usage

- QA recheck: about 3.5 min (201,352 ms), 17 tool uses.
- The earlier QA launch and the Engineer's work on #118 are not counted here.

## Files created or modified

Per QA: the merged tree added `tests/test_release_installed_files.py` and README and release-procedure text (PR #140). This record is the only file added now.

## Decisions made by the human

- Merged PR #139 first, then PR #140. The tier label was left off, so the close gate treats #118 as Standard.

## Mismatches with the spec or design docs

none known.

## Commands to validate

**Verify:** QA's `make verify` on the merged tree: PASS, 1329 tests; the claims check OK; `make assert-clean` PASS (run before and after posting).

## Proposed AGENTS.md changes

none.

## Temporary changes

none.

## Interruptions

none.

## Unrelated problems noticed but not fixed

QA's optional follow-up: the README test checks only that the phrase appears, not that the target heading exists.

## Follow-ups for the next session

none.
