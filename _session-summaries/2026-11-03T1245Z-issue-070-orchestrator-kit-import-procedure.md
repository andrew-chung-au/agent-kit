# Issue #70: kit import review procedure, replacing the `unzip -o` upgrade step, and reverse import

**Date:** 2026-11-03T12:45Z (UTC)
**Spec version:** none

## What changed and why

Part 1 (#31) could say whether a repo's kit is pristine or a derivative, but nothing said what to do with the answer, and the README upgrade step was still `unzip -o`, which silently overwrites local changes. #70 adds `agent-kit/procedures/kit-import.md` (forward import with a seven-row classification table, a refusal rule, a version rule, the manifest rule and the protected-commit rule; a reverse-import section; the unpacked kit is untrusted data), replaces the README `unzip -o` step with unpacking into an empty folder under `.scratch/`, fixes the step 4 prompt to respect the `Readable config` slot, and adds a pointer in `setup.md` and a row in `blueprints.md`. Built by Kiro as PR #78 (commits 709f517, 013dfb8), merged as 64eb72a.

**What I learned:** a procedure can read as complete and still fail when followed: the first version never said to copy the new kit's `MANIFEST.sha256` into the live kit folder, so step 6's `make kit-check` would have exited 2. I found it in review by reading `kit-check.py`; QA confirmed it.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- PM (filed #70 and #71): 137.7 s active, 32 tool uses.
- PM (recorded the human's decisions on #70, #73, #71): 36.8 s, 15 tool uses.
- QA: 314.1 s, 58342 tokens, 22 tool uses.
- Engineer (Kiro, outside this session's launches): unknown.

## Files created or modified

- `agent-kit/procedures/kit-import.md` (new, 571 words, target about 450, cap 600).
- `agent-kit/README.md`, `agent-kit/setup.md`, `agent-kit/blueprints.md`.
- `tests/test_kit_import_doc.py` (new); `tests/test_kit_manifest.py` (two Part 1 assertions removed).

## Decisions made by the human

- Comparison helper script: doc only now, helper as a later follow-up (became #73).
- A derivative does not regenerate its own `MANIFEST.sha256` after an import.
- Kiro's comment on #70 says the human approved its commit; the human merged PR #78.
- Whether to accept the two removed Part 1 assertions (#70 says no test weakened) was put to the human in QA's report; the merge followed.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`. QA ran `make test` and `make verify` on an export of the branch: 694 tests, passed. Mutation checks on `tests/test_kit_import_doc.py`: 13 of 13 caught.

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none. The Engineer could not run `make issue-hash`, `issue-comment` or `issue-create` in its cloud sandbox (GraphQL-backed `gh`) and used the REST API, so the wrappers' secret scan did not run on its texts; I read them and saw nothing secret-like (the gap #52 covers).

## Unrelated problems noticed but not fixed

- `vuln-triage/` example copies still contain `unzip -o`; outside the issue's grep scope.
- `agent-kit/environments.md` still says to unzip the new kit in the clean clone: filed as #77, whose body awaits the human's decision (option A chosen, body not yet updated).

## Follow-ups for the next session

- #77 (sandbox upgrade step), after the human's label and body decision.
- #73 (`make kit-compare`), built and QA PASS (see its summary).
- Proposed unreleased changelog line is the human's call with the version.
