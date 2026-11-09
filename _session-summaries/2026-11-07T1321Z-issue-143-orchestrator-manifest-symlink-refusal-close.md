# Issue #143: Manifest generator refuses symlinks named like skipped entries

**Date:** 2026-11-07T13:21Z (UTC)
**Spec version:** none

## What changed and why

#143 cleared the two criteria #31's QA failed at `e26c8c9`: `kit_files` tested the skipped names (`*.pyc`, `__pycache__`, the root `MANIFEST.sha256`) before its symlink test, so a symlink with one of those names was neither refused nor hashed. It now refuses them like any other symlink, in the generator and in `kit-check`, `kit-compare` and `kit-feedback`, with a test per caller.

This session did not build it: the Engineer's commit `51cff2c` merged as `4f45cc7` (PR #177) on 2026-11-06 at 11:18Z, and QA passed at `51cff2c`. This session ran the decision point and the close.

**What I learned:** the merge was already on `main`; only the summary and the Close step were missing.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

none

## Files created or modified

- `_session-summaries/2026-11-07T1321Z-issue-143-orchestrator-manifest-symlink-refusal-close.md` (this file)
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
**Close:** `make issue-close N=143`

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- `AGENTS.md` and `process.md` still tell agents to run `gh issue view <N> --json labels` directly, which fails in Kiro Web (#172 QA); by the human's decision this goes into #52.
- No installed kit was searched for the now-refused symlink names. A kit that holds one will fail the generator instead of skipping it, which is the intended refusal.
- The FIFO at the manifest and the directory at `MANIFEST.sha256.tmp` stay on #141.

## Follow-ups for the next session

- `make issue-close N=143` in this session, after this summary.
- #31: the two criteria its QA failed are fixed by #143, but it still needs a QA re-check or a human-approved close, and its cloud-session claim is unreleased.
- #169: its QA FAIL is drafted (`.scratch/qa169-comment.md`) but not posted; that issue is with another agent.
- #171: cut 1.10 and run the first sweep there, by the human's decision.
