# Planning: backlog review, and readiness to cut kit 1.10 and import it into SOCBoard

**Date:** 2026-11-06T08:49Z (UTC)
**Spec version:** none

## What changed and why

The human asked whether to bump the kit and import it into SOCBoard, which ships, and which issues are stale. Findings:
- The README still says 1.9 and "Unreleased" lists three items, though about 70 issues changed the kit since; everything since 1.9 becomes 1.10 (the human's decision).
- SOCBoard (public repo) carries a kit labelled 1.9 that is really this repo at `72747a1`: 79 of 85 kit files identical, 6 edited locally (an `Assisted-by:` commit trailer in five files, hand-check notes in one), no manifest, `KIT_VERSION` unset, the V1 permission plugin that OpenCode 2.2.5 rejects, 0 issues. Its agents work in Kiro Web (all five PRs) although its `AGENTS.md` says local sandbox and commits to `main`.
- Import gaps: no manifest to import (#171); no baseline path when the live kit has none (#169); the installed-file map skips the tool-layer copies (#170); the #166 fix was not on `main` (PR #173).
- The GitHub wrappers fail in Kiro Web (#172).

Backlog: 27 open issues reviewed against `main`; a dry run of `issue-close.sh` with a non-closing stand-in for `gh` showed only #7 closable today.

## Reflection

### Orchestrator

unknown (role not asked)

## Launch usage

none

## Files created or modified

none in the repo. Issues filed: #169, #170, #171, #172 (unlabelled). Issue edits: #6 (folded #7 in), #8 (narrowed, deferred). Comments: #6, #7 (Close as not planned), #8, #52, #166, #172.

## Decisions made by the human

- Next version is 1.10, covering everything since 1.9; the import into an existing kit repo must work.
- File the 1.10 blockers: #169, #170, #171 (with #143 and #166).
- SOCBoard's `Assisted-by:` trailer stays a SOCBoard change.
- GitHub wrappers: option (a), name the repository and use REST (#172).
- #7: fold into #6 and close as not planned (approved 2026-11-06).
- #8: narrow to review mode for existing repos and defer.
- #166: continue in this session (PR #173).

## Mismatches with the spec or design docs

- SOCBoard's `AGENTS.md` (local sandbox, commit to `main`) does not match how its work arrives (Kiro Web branches and PRs): #52.

## Commands to validate

**Fetch an issue:** `make issue-dump N=<number>` (local sandbox only until #172).

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- #91's approved Decision record was never committed as `_docs/decisions/091-installed-file-map.md`.
- `_human-tasks/2026-11-03T1435Z-human-task-orchestrator-permission-logs-real-session-checks.md` still says to copy the plugin, which today installs the V1 plugin.
- #20's open real-session criteria (subagent prompts in the log; #71's cap after a restart) are not in #168.
- Several PRs this session said "Closes #N", so GitHub closed #155, #156, #159, #160 and #161 without `make issue-close`.

## Follow-ups for the next session

- `make issue-close N=7 REASON=not-planned` (local sandbox).
- Close #14 once this summary is on `main` (Close comment posted).
- The human labels #169 to #172; #172 needs a Decision record first.
- #20: extend #168 or file a separate issue for its open real-session checks, then decide the close.
- Close #91 after committing its Decision record and a QA check, or by hand; #31 after #143; #90 after the `devcontainer-test` check.
