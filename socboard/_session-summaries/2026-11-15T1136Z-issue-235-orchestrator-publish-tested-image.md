# Issue #235: CI: push the tested image to the public registry on main, tagged and by digest (D14)

**Date:** 2026-11-15T11:36Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

When every check passes on a push to `main`, CI now pushes that commit's tested image to `ghcr.io/andrew-chung-au/socboard`, tagged `YYYYMMDD-HHMMSS-<7 character sha>`, and records the digest. Before this nothing published the image, and D20 needs an immutable image to deploy by digest. This is D14 of the Deploy phase and the last piece the Compose and CI lane owned before the deploy items.

- `.github/workflows/publish.yml` (new): a `workflow_run` workflow triggered when any workflow that runs on a push to `main` completes. A gate job (`actions: read`, `contents: read`) lists the commit's workflow runs and decides in `scripts/publish_gate.py`; the publishing job is the only one with `packages: write`, runs no repository code, uses only `GITHUB_TOKEN`, and has a non-cancelling concurrency group. Its actions are pinned by commit SHA.
- `.github/workflows/compose.yml`: on a push to `main` the Compose job checks the files of the image it tested, saves it right after the browser test and uploads it as an artifact kept one day. The publishing job loads that artifact, never rebuilds, pushes it, pulls it back by digest and compares ids.
- `scripts/publish_gate.py` and `tests/test_publish_gate.py` (66 tests): ready only for a push to `main` of this repository when the four required workflows have run and every run of the commit on `main` is completed with `success`; the tag from the commit's own UTC time; the lower-case image name. `tests/test_publish_workflow.py` (15 checks) holds the workflow files to the rules: default `contents: read`, `packages: write` on one job, every action pinned by commit, the trigger list equal to the workflows that run on a push.
- `Dockerfile` and `compose.yaml`: the commit and its time become the image's `revision` and `created` labels at build time, because adding a label after the test would change the image id.
- `_docs/decisions/2026-11-15T0915Z-image-publish.md` (approved by the human in the session) and its index row; a README section.

Worked by the Compose and CI lane session, Heavy tier (PM proposal), no separate Engineer launch. Branch `issue-235-publish-tested-image`, PR #247, merge commit `4eedb5a`, head before merge `b2c7463`. Claim: https://github.com/andrew-chung-au/socboard/issues/235#issuecomment-6892165438. Two independent QA passes on `b63af98` (https://github.com/andrew-chung-au/socboard/issues/235#issuecomment-6892492617 and https://github.com/andrew-chung-au/socboard/issues/235#issuecomment-6892493677) and a changed-lines re-check on `0a9325b` (https://github.com/andrew-chung-au/socboard/issues/235#issuecomment-6892495853).

**The first real run, on the merge commit** (it ran from `main`, as it could not before): `socboard publish` ran four times for that commit. The first three gates said `not yet` (compose, postgres and verify were still running) and their publishing jobs were skipped; the fourth, run 43709566765, found everything green and published `ghcr.io/andrew-chung-au/socboard:20261115-112720-4eedb5a` with digest `sha256:8f527caf007b4c958ac1042177bc393eeb83f2c52cf9a640f460325d43d61803`. Its steps all passed: the loaded image id equalled the id the Compose job saved, the labels named this repository and this commit, `Login Succeeded`, the push, and the pull-back by digest with equal ids. The token is shown as `***` in the log and no token pattern is in it. The runner's Docker reported the image id as the manifest digest (the same value as the pushed digest), so the id checks hold. The artifact's one-day retention and the tag from the commit's time (22:27:20+11:00 is 11:27:20 UTC) match.

**What I learned:** a workflow that can run only from `main` has no pre-merge test, so the parts that could be tested without Actions went into a script with unit tests and the rest into a static test of the workflow files. That worked: the first real run passed on the first try. The two independent QA reviewers independently found the same two Lows, and applying them before the human handled the protected files saved a second round of protected-file changes.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

unknown (role not asked)

## Launch usage

PM: none (the issue came groomed). QA: 3 launches (PASS at `b63af98`, an independent second PASS at `b63af98`, PASS at `0a9325b` on the changed lines). Active time and tool uses were not given: unknown.

## Files created or modified

- `scripts/publish_gate.py`, `tests/test_publish_gate.py` (new)
- `Dockerfile`, `compose.yaml`, `tests/test_dockerfile.py` (labels and build arguments)
- `README.md` (a "Published image" section), `_docs/decisions/2026-11-15T0915Z-image-publish.md` (new), `_docs/index.md` (one row)
- `.github/workflows/publish.yml` (new), `.github/workflows/compose.yml`, `tests/test_publish_workflow.py` (new) (protected, applied by the human in `b2c7463`)
- `_human-tasks/2026-11-15T0925Z-human-task-235-engineer-apply-publish-workflow-and-set-package-public.md`
- `_docs/records/findings/235.json`, `_session-summaries/2026-11-15T1136Z-issue-235-orchestrator-publish-tested-image.md` (this file)

## Decisions made by the human

- Labelled #235 `approved`; approved the Decision record and the gate mechanism (a `workflow_run` workflow that reads the commit's other runs): "recommendations approved".
- Applied the protected files on the PR branch (`b2c7463`) and merged PR #247. The human's own steps (the package public and linked, an unlogged `docker pull`) are still open; see the follow-ups.

## Mismatches with the spec or design docs

The issue body says the trigger could be a `workflow_run` on `socboard compose` completing, with a check of the other runs; the design triggers on every workflow that runs on a push, because a trigger on one workflow alone can fire while another is still running. The record says so.

## Commands to validate

- **Verify:** `make verify`. CI on the merge commit (compose run 43709001759, image 43709001812, postgres 43709001801, verify 43709001726) passed; locally the whole Python suite passed on SQLite (2514 passed, 90 deselected) before the hardening round and the gate, Dockerfile, compose and settings tests passed after it (177).
- **Test (one file):** `make test-one FILE=tests/test_publish_gate.py`, `make test-one FILE=tests/test_publish_workflow.py`.
- **Published image:** `docker pull ghcr.io/andrew-chung-au/socboard:20261115-112720-4eedb5a` from a machine that is not logged in to the registry (needs the package public; the human's step).

## Proposed AGENTS.md changes

none (`AGENTS.md` and the `Makefile` are not touched).

## Temporary changes

- `.venv` kept from earlier issues. Throwaway trees under `.scratch/` held copies for checking the proposed workflow test; they are ignored by git. Nothing is running.

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-235-1: a pushed tag stays in the registry if the pull-back comparison fails.
- F-235-2: the issue expected a pushed digest to differ from a local image id; on this runner they are equal (containerd image store), so the id checks would compare different things on a classic-store runner, and would still fail closed.
- F-235-3: a commit dated far in the future gets a tag that sorts above later ones.
- F-235-4: the concurrency group queues by gate finish and keeps one pending run, so quick merges can publish out of order or skip a commit.
- F-235-5: the pattern for "tag absent" also matches "command not found" and "permission denied".
- F-235-6: the static test checks only the workflow-level bash default.
- F-235-7: bad input shows as a red gate job, and the record and docstring do not say so.

## Follow-ups for the next session

- The human sets the package public, links it to the repository, and checks `docker pull` of the tag without a login (task file steps 4 and 5). The server has no registry login, so a private package fails D20.
- The skipped `socboard publish` run for a pull request (the criterion "a pull request never pushes"): the close-out pull request for this issue is the first one opened after `publish.yml` reached `main`; its run is linked in the Close comment.
- D22a (#238, deploy from CI) deploys by the digest this job outputs; it is an outline and was not started. D20 needs the package public.
- The remote branch `scratch-234-broken-lead` is still there (the human deletes it). `_human-tasks/229-proposed/test_stack_make.py` is a leftover copy (F-229-4).
