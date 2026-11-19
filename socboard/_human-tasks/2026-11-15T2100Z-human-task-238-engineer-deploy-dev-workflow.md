# Add the dev deploy workflow and the publish job's hand-over, set the two variables, and record the first run

## Purpose

Apply #238's two protected changes, set the two `deploy` Environment variables, and record the first real run. The changes are a new `.github/workflows/deploy-dev.yml` and two steps at the end of the publish job in `.github/workflows/publish.yml`. Issue: #238.

## Where to run it

- Steps 1 to 4: the clean clone, on the branch `issue-238-deploy-dev`.
- Steps 5 and 6: GitHub's settings and the Terraform output, with your own credentials.
- Steps 7 to 9: the Actions list, after the merge.

The agent never edits `.github/` and has no AWS access.

## Before you start

### Step 1: check that the order allows it

Apply and commit steps 2 to 4 at any time; they run nothing until they are on `main`. **Do not merge** the pull request until both of these are true:

- #237's first deploy has run, so the document `socboard-deploy` exists and the server runs the stack.
- Steps 5 and 6 are done.

A merge before that makes every push to `main` fail the deploy job, naming the missing variable. Nothing else changes, but the Actions list turns red.

```
gh api repos/andrew-chung-au/socboard/issues/237 --jq .state
```

Expected: you know whether #237's first deploy has run. The issue may still be open for its stage (b) re-check; what counts is the first run's result row.
If different: do steps 2 to 4 now and stop before the merge.

## Steps

### Step 2: check the branch and the proposal

```
git fetch origin
git checkout issue-238-deploy-dev
git merge origin/main
ls _human-tasks/238-proposed
```

Expected: `deploy-dev.yml` and `publish-workflow.diff`.
If different: stop and tell the orchestrator what was printed.

### Step 3: put the two files in place and read them

```
git mv _human-tasks/238-proposed/deploy-dev.yml .github/workflows/deploy-dev.yml
git apply --unidiff-zero _human-tasks/238-proposed/publish-workflow.diff
git diff -- .github/workflows/publish.yml
```

Expected: `publish.yml` gains two steps at the end of the `publish` job and nothing else.
- "Write the published image for the deploy workflow" writes `published-image.json` with `jq`.
- The pinned `actions/upload-artifact` step uploads it as `published-image`, kept 7 days, overwritten on a re-run.

`deploy-dev.yml` has two jobs:
- `find`: no Environment, `actions: read`.
- `deploy`: Environment `deploy`, `id-token: write`, the role from `secrets.AWS_DEPLOY_ROLE_ARN`. A step before the credentials step masks the role's unique ID from the repository secret `AWS_DEPLOY_ROLE_ID` (set by #268), so the public log does not print it.

If different: stop and tell the orchestrator what was printed.

### Step 4: remove the proposal, check, commit and push

```
git rm --quiet _human-tasks/238-proposed/publish-workflow.diff
git add .github/workflows/deploy-dev.yml .github/workflows/publish.yml
git status --short
make verify
```

Expected: `git status` shows `.github/workflows/deploy-dev.yml` added (renamed from the proposal), `publish.yml` modified and the diff deleted, nothing else. `make verify` passes; `tests/test_deploy_dev_workflow.py` now reads the real files.
If different: send the failing test's name.

```
HUMAN_APPROVED=1 git commit -m "Add the dev deploy workflow and the publish job's hand-over (#238)"
git push origin issue-238-deploy-dev
```

Expected: the commit hook accepts the protected files because of `HUMAN_APPROVED=1`, and the push prints `issue-238-deploy-dev -> issue-238-deploy-dev`.
If different: if the hook refuses, send its message; never use `--no-verify`.

Tell the orchestrator once it is pushed. CI on the pull request checks both files statically; neither workflow runs on a pull request.
Risk: none until the merge. `workflow_run` workflows run only from `main`.

### Step 5: read the instance id and the host name

After #237's first deploy, in your Terraform checkout of `terraform/server/`:

```
terraform output -raw instance_id
```

Expected: `i-` followed by 17 hex digits.

The host name is the one in the public URL that #237's first deploy reached with a valid certificate: its task file's result row for the URL. Use that row, not a value from memory.
If different: if Terraform has no output, run `terraform output` and send the names (not the values) it lists.
Risk: read-only.

### Step 6: set the two Environment variables

On GitHub, go to Settings, then Environments, then `deploy`, then Environment variables. These are variables, not secrets: neither holds a credential or the account number.

- `DEPLOY_INSTANCE_ID`: the value from step 5.
- `DEPLOY_URL`: `https://` followed by the host name, with no path and no trailing slash.

Leave the Environment as it is:
- no required reviewer (dev deploys by itself)
- branch rule `main` only
- the secret `AWS_DEPLOY_ROLE_ARN` unchanged

Expected: the `deploy` Environment lists both variables.
If different: if there is no `deploy` Environment, stop. It comes from #207, and the role refuses a job outside it.
Risk: a wrong value fails the next deploy job before any AWS call, naming the variable.
Undo: delete the variable.

**When the instance is replaced** (a change to the bootstrap or to `acme_ca` replaces it), repeat steps 5 and 6. Until then every deploy fails at the send step with "the instance id in DEPLOY_INSTANCE_ID may be stale".

### Step 7: merge, then watch the first run

Merge the pull request once steps 1, 5 and 6 are done. The merge is a push to `main`. It starts the usual checks, then `socboard publish` runs once per completed workflow, and each of those starts one `socboard deploy dev` run.

Expected:
- Most deploy runs end green at `find` with "this publish run published nothing".
- The run started by the publishing `socboard publish` run goes through `deploy` and prints `socboard-deploy: deployed.`
- The health check prints 200.
- The run has the artifact `deploy-record-dev`.

If different: send the `deploy` job's last lines. A FAIL is fixed through a new issue, never by editing the run.
Risk: this is a real deploy to dev, the same one #237's first run made by hand.

### Step 8: re-run the deploying run once

On that `socboard deploy dev` run, choose "Re-run all jobs".

Expected: the `deploy` job prints `socboard-deploy: already deployed. Nothing was changed.` and uploads a fresh `deploy-record-dev`.
If different: send the job's last lines.
Risk: none. The same digest changes nothing on the server.

### Step 9: show that a pull request does not deploy

Open any pull request, or use the next one. When its checks finish, `socboard publish` runs with the gate skipped, then `socboard deploy dev` runs with `find` skipped.

Expected: no `deploy` job, and no deployment listed on the `deploy` Environment for it.
If different: stop and tell the orchestrator.

## Record the result

Recorded 2026-11-16 by the agent from the run's logs, job summary and artifacts (read through the GitHub API), and from the maintainer's report of the run page. The first deploying run is [43979237337](https://github.com/andrew-chung-au/socboard/actions/runs/43979237337), commit `2ebd8a6` (the merge of PR #344, which landed two minutes after #343's merge). It needed four attempts: attempts 1 and 2 stopped at the variable check because the two values had been saved as Environment secrets, not variables; attempt 3 deployed but its health check used a mistyped `DEPLOY_URL` (`.sslip.ioa`); attempt 4 is the re-run with the corrected value.

| Row | Pass, fail or not settled | Output or note |
|---|---|---|
| The run is `socboard deploy dev`, started by a `socboard publish` run | PASS | Run 43979237337, started by publish run [43979128244](https://github.com/andrew-chung-au/socboard/actions/runs/43979128244) (`RUN_ID` in the `find` log), `HEAD_SHA` `2ebd8a61e896832e2359596b777ac374311d1ddf`. |
| `find` found `published-image` | PASS | `find` green on every attempt; the deploy job got the digest. |
| The role was assumed | PASS | Attempt 3: "Assuming role with OIDC", "Authenticated as assumedRoleId ***:socboard-deploy-dev-43979237337". The role's unique ID printed as `***`, so the mask step works. |
| `send-command` accepted the instance id and the document (first live check of the deploy role's resource split, `VERIFY:` in #156) | PASS | Attempt 3: `sent socboard-deploy for 20261116-231934-2ebd8a6 (command f1625e56-41cb-46f5-903f-16310a6fdcff)`. Settles the #156 `VERIFY:` for the send. |
| The command ended `Success` with the deployed line | PASS | Attempt 3 printed `socboard-deploy: deployed.` |
| The health check passed | PASS (attempt 4) | Attempt 3: 6 of 6 "no answer", because `DEPLOY_URL` was `https://44-216-250-242.sslip.ioa`; the job failed and wrote no record, as designed. Attempt 4, after the fix: `health check 1 of 6: 200`. |
| `deploy-record-dev` exists and holds the digest the publish run printed | PASS | The record (attempt 4) has digest `sha256:49392eb16880a6f51a25ff46e3e9138fd997d437a1a03f5e107f499b070f2773`, tag `20261116-231934-2ebd8a6`, revision `2ebd8a6…`, result `already deployed`, command `38c40a7d-310d-4b6b-875e-7d8d1b8ef918`, the same digest, tag and revision as publish run 43979128244's `published-image`. |
| The re-run shows "already deployed" | PASS | Attempt 4: `socboard-deploy: already deployed. Nothing was changed.` The job summary says the same. Covers step 8. |
| A later push whose publish run was skipped shows `find` green with nothing deployed | PASS | Run [43978394005](https://github.com/andrew-chung-au/socboard/actions/runs/43978394005): `find` green with "this publish run published nothing" (publish run 43978367461), deploy skipped. |
| A pull request's run did not start the deploy job (link) | PASS (by timing) | Run [43983006345](https://github.com/andrew-chung-au/socboard/actions/runs/43983006345): `find` and `deploy` skipped. It follows publish run 43982995261 (skipped), which started 4 s after the pull request `issue-288-otel-deps`'s verify run finished; no push to `main` ran then. The API does not show a run's triggering run, so the link is by timing. No `deploy` job ran between 23:29 and 23:54 UTC across 19 such runs. |
| Time from the push to the URL serving the new digest | NOT SETTLED | Not measurable on this run: the merge was at 23:19:34 UTC and the deploy at 23:51 UTC, delayed by setting the variables. The send-to-deployed part took about 88 s (23:50:00 to 23:51:28, including six health checks). Take it from the next push to `main`. |
| `get-command-invocation` returned `InvocationDoesNotExist` in the first seconds (yes or no) | NOT SETTLED | `scripts/ci_deploy.py` does not print it, so the log cannot show it. |

Found during the run (follow-up issues, not fixed here):
- [#349](https://github.com/andrew-chung-au/socboard/issues/349): runs [43978322955](https://github.com/andrew-chung-au/socboard/actions/runs/43978322955) and [43979101310](https://github.com/andrew-chung-au/socboard/actions/runs/43979101310) failed at `find` with "the published-image artifact's revision is not the publish run's commit". `publish.yml` records the tested commit (`github.event.workflow_run.head_sha` of the CI run); `deploy-dev.yml` compares it with the publish run's own `head_sha`, which is `main`'s head when that run starts. When a second merge lands before the first commit's publish run, the two differ. The refusal is safe (the older commit is not `main`'s head), but it leaves a red run.
- [#350](https://github.com/andrew-chung-au/socboard/issues/350): `ci_deploy.py check` accepted `https://44-216-250-242.sslip.ioa`. It could require the `<four numbers with dashes>.sslip.io` form.

## Risk

The deploy job can send only the one document, with a digest, to the tagged instance, and read its result. The role allows nothing else (#156). A wrong variable fails before any AWS call. A failed deploy leaves the current release serving (#237) and writes no record.
