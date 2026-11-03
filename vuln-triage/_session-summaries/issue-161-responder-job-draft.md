# Issue #161: the `responder` CI job and `P-FLAG-GONE`, drafted as a proposal (task 29)

**Date:** 2026-10-26
**Spec version:** 76c73f7

## What changed and why

The orchestrator asked for a draft, not an application, of the protected `.github/` changes for #161, as was done for `make demo`. Branch `claude/161-responder-job-draft`, created from `origin/main`. Nothing protected was edited.

- **Proposal:** `_docs/161-responder-job-proposal.md`. It holds the exact diffs for a new `.github/workflows/responder.yml` (nightly plus `workflow_dispatch`, `timeout-minutes: 45`, a log upload on failure), a pointer comment in `verify.yml`, an every-PR alternative for `verify.yml`, and the `deploy.yml` change that puts `P-FLAG-GONE` into the `deploy-prod` job (a full-history checkout, one step after the tag is resolved and before the deploy, one reworded comment). It also holds an optional `ci/test-compose.sh` log hunk, an optional `Makefile` target, the protected-path list, the order to apply them, what to do if the first CI run is red, and nine open questions with a recommendation each.
- **`ci/check_flag_gone.py` and `tests/test_flag_gone.py` (not protected, committed):** the `P-FLAG-GONE` script and 19 `unit` cases that run it as a child process against fixture trees built per test (one that must fail, one that must pass). They run in `make test`.
- **Findings recorded in the proposal:** `.github/` is not in `agent-kit.conf` `PROTECTED`; a nightly job cannot live in `verify.yml` (workflow-level `on:`); the alert job has no teardown or log upload and the script's `EXIT` trap removes the logs; the 8 #220 cases already passed on the owner's host (103 s) so only #233's loop is unrun; the `VT_FEEDS=fixtures` rule cannot be "string absent"; the script run on `main` gives 78 findings in 13 files, including the container-form tests of the `responder` job itself.

## Files created or modified

- `ci/check_flag_gone.py` (new), `tests/test_flag_gone.py` (new), `_docs/161-responder-job-proposal.md` (new), `_docs/ai-usage-log.md` (entry), this summary.
- GitHub, outside the diff: one `Orchestrator:` comment on #161 pointing at the proposal and listing the open questions. The issue was not edited or closed.
- Protected: none changed.

## Decisions made by the human

none in this session. Pending: the nine questions in the proposal, and the `P-FLAG-GONE` wording box in #229.

## Mismatches with the spec or design docs

- `_docs/testing.md` § CI jobs and triggers lists the `responder` row with no cadence (the `alert` row says nightly and on demand) and says `make test-compose JOB=responder` is "(planned)" and exits 3 until #220 lands; #220 has landed. Not edited here (the proposal says what the row should become).
- `ci/test-compose.sh` header comment says "#161 adds the verify.yml job"; with the recommended option the job is in `responder.yml`.

## Commands to validate

- **Verify:** `make verify` (result in the final report of the session).
- **Test (backend):** `make backend-test` (551 passed, 13 deselected, with the 19 new cases).
- **The check on the current tree (expected to FAIL while the demo defect exists):** `python3 ci/check_flag_gone.py .` (78 findings, 13 files).
- **Proposal validation (parse only):** `python3 -I .scratch/validate_proposal.py`, which parses the proposed YAML with PyYAML, runs `bash -n` on the run blocks and the proposed script, and runs the `P-FLAG-GONE` step's shell text locally against this repository. It does not run GitHub Actions, Docker or the Compose job.

## Proposed AGENTS.md changes

none (an optional `Makefile` target and its `AGENTS.md` line are in the proposal, section 2.4, recommended against for now).

## Temporary changes

- `make install` ran in this worktree (the venvs and `frontend/node_modules` were missing); it installs from the lockfiles into git-ignored directories. Left in place.
- `.scratch/proposal/`, `.scratch/validate_proposal.py` and `.scratch/probe_yaml.py` are git-ignored scratch files. No processes were started and no system configuration was changed.

## Permission review

- Read-only (propose allowing): `python3 -I ci/check_flag_gone.py .` (read-only; no `ask` rule recorded as matched); the PyYAML probe and the `validate_proposal.py` run (read the repo, write only under `.scratch/`); `git diff --no-index --output=.scratch/...` to produce the diffs (writes under `.scratch/` only); `cp` of workflow files into `.scratch/proposal/` (three calls).
- Writes to the record (keep asking): `make issue-comment N=161` (the `Orchestrator:` comment); `git commit` of the non-protected files; `make install` (network, installs into git-ignored directories; no `ask` rule recorded as matched).
- Risky (propose denying): none. No push, no protected commit, no command outside this folder.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- The `Makefile` comment above `COMPOSE_JOBS` says `T-JOURNEY-BE` "needs the backend feed-fixture wiring of prerequisite #172", which has landed (protected file; not touched).

## Follow-ups for the next session

- The owner answers the nine questions in the proposal (the first: whether to apply `responder.yml` before #233's host run; the recommendation is no need to wait).
- After approval: commit A (`deploy.yml`) and commit B (`responder.yml`, `verify.yml`) as separate `HUMAN_APPROVED=1` commits with records on #161.
- After #233 merges: the `ci/test-compose.sh` log hunk; after the first CI run: re-size `timeout-minutes`.
- After the recorded drill (#163): the cleanup commit (proposal section 2.5) and the `responder.yml` change that goes with it.
