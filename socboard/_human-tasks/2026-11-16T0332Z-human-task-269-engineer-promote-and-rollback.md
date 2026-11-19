# Install the promote workflow, then promote to prod, roll back, and show the refused runs

## Purpose

Install `promote-prod.yml`, set its two Environment variables, promote dev's digest to prod, roll prod back to an earlier dev digest and forward again, and show three refused runs. This is the evidence for #269's criteria (rubric: CI/CD, the manual deploy to production; spec Phase 3, the rollback path). The Engineer has **not checked** any of it: no Actions, AWS or server was available. Every `Expected:` line is what the author expects. Issue: #269. Decision: `_docs/decisions/2026-11-16T0332Z-promote-to-prod.md` (proposed).

## What changed in these steps (2026-11-17)

The steps were rewritten for copy and paste after the #267 run (`_human-tasks/2026-11-17T0030Z-human-task-267-engineer-first-prod-deploy.md`, "What changed after the first run"), with no change to what they do. Steps 1 to 4 were run on 2026-11-17 (see the table) and now say "Done on 2026-11-17, skip". Steps 5 and 6 are the ones left. Their placeholders (`sha256:<the 64 digits printed above>`, `<name>`) are now shortcuts read by a command (`D2`, `R6`) and echoed before use.

## Where to run it

- On your own machine, in a terminal opened at the **repository root** (`cd ~/projects/socboard`), on `main` after #269's pull request merged, for `git` and `gh`, with a browser for the Actions tab and the prod URL.
- AWS is needed only for the fallback in step 2. Use your own credentials (SSO is fine). If you use a named profile, add `--profile NAME` to every `aws` command, or run `export AWS_PROFILE=NAME` once in the terminal. Every `terraform` command uses `-chdir=terraform/...`, which only works from the root.
- Not here: the sandbox where the Engineer worked. Never paste a token, an ARN or the account number into this file; the steps print none.

**How to read the commands.** Copy each block exactly. Steps 5 and 6 set shortcuts (`D2`, `R6`) that later blocks use. A shortcut exists only in the terminal where you set it: in a new terminal, run the shortcut steps again. A command with an empty shortcut fails (an `aws ssm send-command` with an empty shortcut fails with `InvalidParameters`), so each shortcut is echoed before it is used.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue.

## Before you start

Each of these must be true; the step that needs it says so if it is not.

1. Dev has been deployed by CI at least once since #238's workflow was installed, so a `deploy-record-dev` artifact exists:

```
gh api "repos/andrew-chung-au/socboard/actions/artifacts?name=deploy-record-dev&per_page=5" --jq '[.artifacts[] | select(.expired == false)] | length'
```

Expected: `1` or more. For the rollback step you need two different dev digests, so ideally `2` or more from two different commits.
If different: `0` means nothing to promote. Merge a change to `main` and wait for the dev deploy, then start again.

2. The prod stack exists: #266 is applied (done 2026-11-16) and #267's first prod deploy by hand has run (its task file), so the server can run the document with `environment=prod`.

```
gh api repos/andrew-chung-au/socboard/issues/267 --jq .state
```

Expected: `closed`.
If different: stop; promote would reach a server without the `environment` parameter, and Systems Manager would refuse the send.

3. You are on a clean `main`.

```
git branch --show-current
```

Expected: `main`.
If different: stop and switch to `main`.

```
git status --short
```

Expected: nothing printed.
If different: stop; leave what is listed alone and tell the orchestrator.

## Steps

### Step 1: Install the workflow (a protected file)

**Done on 2026-11-17, skip.** Installed by PR #357 (merge `91d985f`); the table has the link.

The install is a pull request (branch `issue-269-install-promote`, 2026-11-17). It moves the proposal to `.github/workflows/promote-prod.yml` unchanged and adds the workflow's exception to the id-token rule in `tests/test_terraform_plan_workflow.py`. Approving and merging that pull request is this step. It replaces the earlier copy-and-commit commands.

Check it after the merge:

```
gh api repos/andrew-chung-au/socboard/contents/.github/workflows/promote-prod.yml --jq .path
```

Expected: `.github/workflows/promote-prod.yml`. The Actions tab lists "socboard promote prod" with a "Run workflow" button.
If different: a 404 means the pull request is not merged yet.
Risk: adds a manual workflow. It does nothing until someone starts it and you approve it. Undo: delete the file in a new pull request.

### Step 2: Set the two Environment variables on `deploy-prod`

**Done on 2026-11-17, skip.** The maintainer set `DEPLOY_INSTANCE_ID` and `DEPLOY_URL` on `deploy-prod` (2026-11-16); the table records it as PASS (indirect). The commands are kept for a later re-run.

The instance is the same server as dev, so the suggested value is dev's. Read it into the shortcut `I`:

```
I=$(gh api repos/andrew-chung-au/socboard/environments/deploy/variables/DEPLOY_INSTANCE_ID --jq .value)
```

```
echo "I=[$I]"
```

Expected: `I=[i-` and hex digits `]` (an instance id is not a secret).
If different: an HTTP 404 means `deploy` has no such variable yet (#238's steps set it); read it from Terraform instead, then echo it again:

```
I=$(terraform -chdir=terraform/server output -raw instance_id)
```

Set it on `deploy-prod`:

```
gh variable set DEPLOY_INSTANCE_ID --env deploy-prod --repo andrew-chung-au/socboard --body "$I"
```

Expected: `✓ Created variable DEPLOY_INSTANCE_ID for andrew-chung-au/socboard` (or "Updated").
If different: an error naming the Environment means `deploy-prod` does not exist; it was created on 2026-11-16 (#268), so tell the orchestrator. An empty `I` sets an empty value: run the echo block and set it again.

The URL is prod's hostname (#266's output `prod_hostname`); the suggested value:

```
terraform -chdir=terraform/server output -raw prod_hostname
```

Expected: `prod-44-216-250-242.sslip.io` (recorded at #266's apply, 2026-11-16) or the same form with your Elastic IP.
If different: an error means the server part's state is not reachable from this shell (credentials or `init`); use the `prod_hostname` value recorded in #266's result instead.

```
gh variable set DEPLOY_URL --env deploy-prod --repo andrew-chung-au/socboard --body "https://$(terraform -chdir=terraform/server output -raw prod_hostname)"
```

Expected: `✓ Created variable DEPLOY_URL for andrew-chung-au/socboard`.
If different: an error naming the Environment: as above.

```
gh variable list --env deploy-prod --repo andrew-chung-au/socboard
```

Expected: `DEPLOY_INSTANCE_ID` and `DEPLOY_URL`, and nothing else.
If different: fix the value with the same `gh variable set` command.
Risk: changes where prod deploys go. Undo: `gh variable delete DEPLOY_INSTANCE_ID --env deploy-prod --repo andrew-chung-au/socboard`, and the same with `DEPLOY_URL` in place of `DEPLOY_INSTANCE_ID`.

### Step 3: Promote dev's current digest

**Done on 2026-11-17, skip.** Run 44001761105 promoted `sha256:25446a29…981d57` and was approved by `andrew-chung-au`; the table has the link.

```
gh workflow run promote-prod.yml --repo andrew-chung-au/socboard --ref main
```

Expected: a line saying the workflow was dispatched, or nothing.
If different: read the error and tell the orchestrator.

```
gh run list --repo andrew-chung-au/socboard --workflow promote-prod.yml --limit 1 --json databaseId,url,status
```

Expected: one run. In the Actions tab, its `resolve` job passes and its summary shows "Chosen ... (dev is running it now)" and "Prod runs now". The `promote` job waits for review.
If different: no run listed means GitHub has not started it yet: wait ten seconds and run the block again.

Approve it in the run's page ("Review deployments", tick `deploy-prod`, "Approve and deploy").

Expected: the `promote` job passes. Its log shows `socboard-deploy: deployed.` (or `already deployed`) and `health check 1 of 6: 200`. The summary table "Promote to prod" names the digest, "Started by" and "Approved by" with your login, and the run has an artifact `deploy-record-prod`. `VERIFY:` that "Approved by" shows your login (it reads the approvals endpoint; `not readable from GitHub` means it could not).
If different: a red `promote` job prints the script's fixed line or `ci_promote: ...` naming the problem. Copy that one line into the table and tell the orchestrator; do not re-run with a different digest. A send refused with "the instance id ... may be stale" means `DEPLOY_INSTANCE_ID` is wrong (step 2).

### Step 4: Check what prod serves

**Done on 2026-11-17, skip** (health `200` in run 44001761105; the sign-in page in a browser was not reported, so open it once if you like).

```
curl -sS -o /dev/null -w '%{http_code}\n' https://prod-44-216-250-242.sslip.io/api/health
```

Expected: `200`. Open the prod URL in a browser: the sign-in page loads with a valid certificate.
If different: anything but `200` (or a certificate warning) means prod is not serving: copy the code into the table and tell the orchestrator; prod still runs what the script restored if the swap failed (#237). Do not promote again to "fix" it.

### Step 5: Roll back to an earlier dev digest, then forward again

The suggested digest is the second-newest digest dev ran (the summary of step 3's `resolve` job lists the same ones under "Recent dev digests"). Download dev's second-newest record into the repository's `.scratch/` folder:

```
gh run download --repo andrew-chung-au/socboard --name deploy-record-dev --dir .scratch/dev-record-2 "$(gh api 'repos/andrew-chung-au/socboard/actions/artifacts?name=deploy-record-dev&per_page=2' --jq '.artifacts[1].workflow_run.id')"
```

Expected: no error, and the file `.scratch/dev-record-2/deploy-record-dev.json` exists.
If different: an error from `gh run download` means there is only one dev record: let a second push deploy to dev first, then come back. A message that the folder exists means an earlier try left it: run `rm -r .scratch/dev-record-2` and this block again.

Read the digest into the shortcut `D2`:

```
D2=$(jq -r .digest .scratch/dev-record-2/deploy-record-dev.json)
```

```
echo "D2=[$D2]"
```

Expected: `D2=[sha256:` and 64 hex digits `]`, different from the digest step 3 promoted (`sha256:25446a296fa32d3320c88e862c073729e2de33204ccee8a4946093a346981d57` in the table).
If different: empty brackets mean the download failed (see the block above). The same digest as step 3 means dev's two newest records are the same release; take the next row of the summary's "Recent dev digests" list: copy its digest and set the shortcut by hand, replacing PASTE-DIGEST-HERE with it (`sha256:` and 64 hex digits), then echo again:

```
D2=PASTE-DIGEST-HERE
```

Dispatch the rollback with that digest:

```
gh workflow run promote-prod.yml --repo andrew-chung-au/socboard --ref main -f digest="$D2"
```

Approve it. Expected: the `resolve` summary says "(named by the input)", the `promote` summary shows "Prod ran before" with step 3's digest, and the job passes as in step 3.
If different: `no dev deploy record holds this digest` means `D2` is wrong or empty: echo it and set it again. A red `promote` job: as step 3.

Then forward again, with no input:

```
gh workflow run promote-prod.yml --repo andrew-chung-au/socboard --ref main
```

Approve it. Expected: prod is back on dev's current digest; "Prod ran before" shows the older digest.
If different: as step 3.

Delete the download:

```
rm -r .scratch/dev-record-2
```

Expected: nothing printed.
If different: `No such file or directory` means it is already gone; carry on.

### Step 6: Refused runs

Refusal test: in the Actions tab and the clean clone. Risk: if a refusal does not happen, prod gets a digest dev never ran, or a run from another branch reaches the role. The steps print no secret either way.

**6a. A digest that never ran in dev** (suggested value: 64 zeros):

```
gh workflow run promote-prod.yml --repo andrew-chung-au/socboard --ref main -f digest=sha256:0000000000000000000000000000000000000000000000000000000000000000
```

Expected: the `resolve` job fails with `ci_promote: no dev deploy record holds this digest: only a digest that ran in dev can go to prod`; the `promote` job is skipped and **no approval is asked**.
If different: if GitHub asks you to review a deployment for this run, **reject it** (the refusal test failed: a digest dev never ran reached the approval). Then tell the orchestrator and treat promote as unsafe until it is fixed.

**6b. A dispatch from another branch:**

```
git switch -c promote-probe
```

Expected: `Switched to a new branch 'promote-probe'`.
If different: a refusal that the branch exists means an earlier try left it: use `promote-probe-2` in this and the following 6b commands.

```
git push -u origin promote-probe
```

Expected: the branch is created on `origin` (it holds the same commit as `main`, so the pre-push check has nothing new to verify).
If different: a refused push means the name exists already; pick `promote-probe-2` in this and the following commands.

```
gh workflow run promote-prod.yml --repo andrew-chung-au/socboard --ref promote-probe
```

Expected: both jobs are skipped (their `if` requires `main`); no approval is asked and nothing is deployed. (#268's refused-branch run already shows the role refuses a non-`main` branch in `deploy-prod`.) `VERIFY:` that a dispatch on another branch shows both jobs as skipped rather than failing.
If different: if GitHub asks you to review a deployment, **reject it** and tell the orchestrator: the main-only guard is missing. A `gh workflow run` error saying the workflow is not found on that ref is also a refusal; record it as a pass with that line.

```
git switch main
```

Expected: `Switched to branch 'main'`.

```
git push origin --delete promote-probe
```

Expected: a line ending `[deleted] promote-probe`.

```
git branch -D promote-probe
```

Expected: `Deleted branch promote-probe`.

```
git ls-remote --heads origin promote-probe
```

Expected: nothing printed.
If different: a line means the branch is still on `origin`; run the `git push origin --delete` block again.

**6c. A rejected approval:**

```
gh workflow run promote-prod.yml --repo andrew-chung-au/socboard --ref main
```

Read this run's id into the shortcut `R6` before you reject it (wait ten seconds after the dispatch):

```
R6=$(gh run list --repo andrew-chung-au/socboard --workflow promote-prod.yml --limit 1 --json databaseId --jq '.[0].databaseId')
```

```
echo "R6=[$R6]"
```

Expected: `R6=[` and a number `]`.
If different: empty brackets mean the run is not listed yet: wait ten seconds and run both blocks again.

In the run page, choose "Reject". Expected: the `promote` job does not run, nothing is deployed, and no `deploy-record-prod` is added for this run. `VERIFY:` that a rejected review ends the job without running a step.
If different: if the `promote` job runs after a rejection, tell the orchestrator at once and check prod with step 4.

```
gh api "repos/andrew-chung-au/socboard/actions/artifacts?name=deploy-record-prod&per_page=1" --jq '.artifacts[0].workflow_run.id'
```

Expected: the run id of step 5's second run, a number that is not the `R6` you echoed above.
If different: the same number as `R6` means a record was written after a rejection; tell the orchestrator.

## Record the result

Fill the table once, when you run the steps, with the date, the line you saw, and the run link. Commit this file with the result. No token, ARN or account number.

| Step | Date | Pass or fail | Output or note | Run link |
|---|---|---|---|---|
| 1 install | 2026-11-17 | PASS | Installed by PR #357 (merge `91d985f`), which also gave the workflow its exception in the id-token test. The Actions tab lists "socboard promote prod". | https://github.com/andrew-chung-au/socboard/pull/357 |
| 2 variables | 2026-11-17 | PASS (indirect) | The maintainer set `DEPLOY_INSTANCE_ID` and `DEPLOY_URL` on `deploy-prod` (2026-11-16). The agent cannot read them, but the promote's check step passed and its health check through `prod-44-216-250-242.sslip.io` answered 200, which needs both values to be right. | https://github.com/andrew-chung-au/socboard/actions/runs/44001761105 |
| 3 promote dev's digest (approved; summary names the approver) | 2026-11-17 | PASS | Run #1, started by hand by `andrew-chung-au` on `main` with `digest` empty. `resolve` chose `sha256:25446a296fa32d3320c88e862c073729e2de33204ccee8a4946093a346981d57` (`20261117-020022-4d7abe0`, dev ran it at 02:08:30Z in run 44000643102); "Prod runs now: none". `promote` waited for `deploy-prod` and was approved by `andrew-chung-au` (approvals API). Log: role ID shown as `***`; `sent socboard-deploy for 20261117-020022-4d7abe0 to prod (command 00493ad7-3471-4568-963c-88cdc8bd7728)`; `socboard-deploy: deployed.` `deploy-record-prod`: result `deployed`, `requested_by` and `approved_by` `andrew-chung-au`, deployed at 02:18:56Z. | https://github.com/andrew-chung-au/socboard/actions/runs/44001761105 |
| 4 prod health 200, sign-in page loads | 2026-11-17 | PASS (health) | The run's health check through Caddy: `health check 1 of 6: 200`. The sign-in page in a browser was not reported. | https://github.com/andrew-chung-au/socboard/actions/runs/44001761105 |
| 5a rollback to an earlier digest | | NOT CHECKED | | |
| 5b forward again | | NOT CHECKED | | |
| 6a digest never in dev: refused, no approval asked | | NOT CHECKED | | |
| 6b another branch: skipped | | NOT CHECKED | | |
| 6c approval rejected: nothing deployed | | NOT CHECKED | | |

## Risk

Steps 3 and 5 change what prod runs; a rollback is step 5's second run. The deploy script keeps the previous release and restores it if the new one fails after the swap (#237). Dev and prod share one lock on the server, so a promote during a dev deploy fails with "another run is in progress" and is started again.
