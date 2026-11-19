# Issue #258: Make the publish workflow test follow GitHub's trigger rules, so a workflow that cannot run on main is not forced into the gate list

**Date:** 2026-11-15T18:16Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

The two tests that keep the publish workflow's trigger list and the gate's required list in step with the workflow files now decide which workflows run on a push to `main` by GitHub's own trigger rules. Before, they only asked whether the key `push` was present, so a pull-request-only workflow, a workflow written as `on: pull_request`, and a throwaway probe pinned to its own branch each crashed or failed them. The Terraform lane's #209 (a pull-request-only `terraform-plan.yml`) was blocked by it, and the maintainer's probe branches had needed `--no-verify`.

- `tests/workflow_triggers.py` (new): `classify` answers (can run on a push to `main`, runs on every push to `main`) for `on:` as a string, a list or a mapping, with `branches` (the `*`, `**` and `!` rules, later entries winning), `branches-ignore`, `tags` and `paths`. A pattern it does not model counts as the real workflow it might be, so a mistake errs towards listing. `list_problems` and `required_problems` compare the files with `publish.yml`'s list and the gate's required list; the failure for an unfiltered push workflow says to restrict `on.push.branches` or list it.
- `tests/test_workflow_triggers.py` (new, 69 tests): a table of 38 forms, the nine refused and eight accepted cases of the issue, the flip test, the named-or-by-path check.
- `tests/test_publish_workflow.py`: the two list tests use the helper and keep both guards; two tests are added, one pinning today's two lists by name (five and four) and one that every real workflow file parses.
- No protected file changed. The human chose none of the three probe options when labelling; the body's recommendation, (c) model GitHub's rules, was built because the criteria were written for it.

Worked by the Compose and CI lane session, Standard tier, no separate Engineer launch. Branch `issue-258-publish-test-triggers`, PR #260, merge commit `f697e8d`, head before merge `ed9c29a`. Claim: https://github.com/andrew-chung-au/socboard/issues/258#issuecomment-6898671280. QA PASS at `ed9c29a`: https://github.com/andrew-chung-au/socboard/issues/258#issuecomment-6898871038. In a throwaway tree outside git, the real workflows plus a pull-request-only `terraform-plan.yml`, an `on: pull_request` probe and a probe pinned to its own branch passed, and an unfiltered push probe failed both list tests with the hint.

**What I learned:** I broke the helper eleven ways and ran the tests on each before handing over, which is what I did not do on #234. QA tried more of its own and found no way for a workflow that GitHub runs on `main` to come out as "cannot run", apart from one unusual pattern it could not confirm (finding F-258-1). The mutation list took minutes to write and replaced a QA round. It also showed the bug that this issue fixes was mine: the original tests of #235 passed review without ever being run on a workflow of another shape.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

unknown (role not asked)

## Launch usage

PM: none (I groomed in this session). QA: 1 launch (PASS at `ed9c29a`). Active time and tool uses were not given: unknown.

## Files created or modified

- `tests/workflow_triggers.py`, `tests/test_workflow_triggers.py` (new); `tests/test_publish_workflow.py` (edited)
- `_docs/planning/roadmap-1-core.md` (#258 placed in the supporting list earlier, by PR #259; #261 placed in this pull request)
- `_docs/records/findings/258.json`, `_session-summaries/2026-11-15T1816Z-issue-258-orchestrator-publish-test-triggers.md` (this file)

## Decisions made by the human

- Labelled #258 `approved` without choosing among the three probe options; the recommended option (c) was built.
- Merged PR #260.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify`. CI on the pull request (verify run 43743698083) passed; locally the whole Python suite passed on SQLite (2664 passed, 90 deselected).
- **Test (one file):** `make test-one FILE=tests/test_workflow_triggers.py`, `make test-one FILE=tests/test_publish_workflow.py`.

## Proposed AGENTS.md changes

none.

## Temporary changes

- Throwaway trees and a mutation script under `.scratch/` (git-ignored); nothing is running.

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-258-1: a branch pattern with a slash-star-star part might match a bare `main` on GitHub and is treated as not matching.
- F-258-2: a tags-ignore-only push trigger is classified as running on every push to `main`.
- F-258-3: reading workflow files with the yaml extension is unguarded by a test.
- F-258-4: two failure messages do not say what to do.
- F-258-5: an empty branch list is classified as unable to run on `main`.
- F-258-6: the original list tests passed review without being run on a workflow of another shape.

## Follow-ups for the next session

- The Terraform lane's #209 can merge `main` and continue; its `pull_request`-only `terraform-plan.yml` passes the new tests (checked in a throwaway tree, not on its branch).
- Optional, the human's call: apply F-258-1 and F-258-3 (one line and one test).
- #261 (pin the stack network's gateway to `10.231.77.1`, found by the maintainer on the server) is groomed and waiting for the human's label; it goes before #237's first run.
