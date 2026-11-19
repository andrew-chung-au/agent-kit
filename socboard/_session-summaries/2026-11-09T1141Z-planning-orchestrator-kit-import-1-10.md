# Planning: import agent kit 1.10

**Date:** 2026-11-09T11:41Z (UTC)
**Spec version:** 0ef5990

## What changed and why

The live kit (`_docs/agent-kit/`) predated 1.10 and had no `MANIFEST.sha256`, so `make kit-check` and `make kit-compare` did not exist. Imported the v1.10 kit following `procedures/kit-import.md`: unpacked the zip into a new folder under `.scratch/`, found the live kit's baseline with `kit-baseline.py` against a full clone of the kit repo, classified every file, and committed the result as `6211f95` (human-run commit, pushed).

Baseline: `72747a1` (2026-11-04, kit 1.9), matching 79 of 85 live files; the next two candidates matched 78. The repo has one tag, `v1.10`; the baseline manifest was written as version 1.9 from the commit's README.

Outcome by file: 23 taken from v1.10; 3 merged (`blueprints.md`, `process.md`, `team/software-engineer.md`: v1.10 plus the local commit-attribution deviation); 2 kept as local drift (`claude-code/settings.json`, `opencode/opencode.json`); 4 added (`procedures/planning.md`, `scripts/bootstrap-project.sh`, `scripts/github_api.py`, `scripts/kit-baseline.py`); 57 unchanged. `procedures/permission-log.md` was taken from v1.10 and the local hand-check examples dropped, because `opencode/START.md` step 6 now covers the same three checks. Claim: `KIT_VERSION="1.10+socboard.1"`. `make kit-check` confirms the claim; the five `modified` kit files are the three merges and the two kept files.

**What I learned:** A live kit with no manifest can still be imported if the human accepts a baseline; the 1.9 kit's `kit-compare.py` rejects the `optional` rule in the 1.10 `installed-files.txt`, so classify from the two manifests until the new scripts are in place.

## Reflection

### Orchestrator

unknown (role not asked)

## Launch usage

none

## Files created or modified

Committed in `6211f95` (34 files): `AGENTS.md` (two Commands lines), `Makefile` (kit-check, kit-compare, kit-baseline, kit-feedback targets), `agent-kit.conf` (`KIT_VERSION`, `GITHUB_REPO`), and 31 files under `_docs/agent-kit/` as listed above, including the new `MANIFEST.sha256`. `scripts/bootstrap-project.sh` is mode 755, as the manifest records.

This summary is the only other file created. `.scratch/kit-src`, `.scratch/kit-import-1.10` and `.scratch/kit-apply.sh` were created and deleted; `.scratch/agent-kit.zip` is the human's and was left.

## Decisions made by the human

- Accepted `72747a1` as the baseline.
- Approved adding the four kit targets to the Makefile and two lines to `AGENTS.md`.
- Approved the four file decisions: merge three, take v1.10 for `permission-log.md`; keep the two settings files as drift.
- Set `GITHUB_REPO`; the first value was the kit's own repository and was corrected to `andrew-chung-au/socboard` after it was flagged.
- Ran the commit with `HUMAN_APPROVED=1`, copied the installed files from the clean clone (`.opencode/plugins/permission-log.js`, `.claude/skills/sweep/SKILL.md`, the pinned OpenCode block in `.devcontainer/setup.sh`) and pushed.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify` (passed before the commit: 1 test, no whitespace errors, no test files changed).
**Kit check:** `make kit-check` (claim `1.10+socboard.1` correct; exits 1 for the five modified kit files and the `verify.yml` drift, as expected for a derivative).

## Proposed AGENTS.md changes

Already applied in the commit: the `Kit check` and `Kit compare` lines under Commands.

## Temporary changes

- Cloned `https://github.com/andrew-chung-au/agent-kit.git` into `.scratch/kit-src` and checked out `72747a1` there (a clone in `.scratch/`, nothing installed); deleted.
- Unpacked the v1.10 zip into `.scratch/kit-import-1.10`; deleted.
- `chmod 755` on the new `_docs/agent-kit/scripts/bootstrap-project.sh`, because the zip dropped the executable bit.
- No system configuration, packages, services or git config changed. No processes started.

## Interruptions

none

## Unrelated problems noticed but not fixed

- The commit body of `6211f95` holds the placeholder text `<body: ...>` instead of a written body. Left as is because the commit was pushed.
- The first push failed in the push check with exit 127 (`uv` not found): the default `python:3.12` image has no uv. Not caused by the import; the human fixed it with the documented `AGENT_PUSH_CHECK_IMAGE` image.
- `.github/workflows/verify.yml` always shows as `drift`: it is the project's filled-in copy of the CI template and the map marks it `none`.

## Follow-ups for the next session

- Test the issue targets (`make issue-dump N=<number>` and the issue-* wrappers) against the v1.10 scripts and the corrected `GITHUB_REPO`; not yet run.
- The human compares the two `pre-push` copies from the clean clone; `make kit-check` lists them as not checked here, and the kit's `pre-push` did not change in v1.10.
- Commit this summary on its own.
