# Land the on-call drill workflow, give it a model credential, run it once and keep the evidence

## Purpose

Run the drill that proves the On-Call Agent criterion: a planted defect makes `QueueLatencyOverSLO` fire, an agent reads the incident and opens a draft pull request with a fix and a test. Issue: #299. Rubric: On-Call Agent (and Alerting on User Impact). The workflow is in `observability/drill/proposed/oncall-drill.yml`; workflows are protected files, so a person lands it.

The model credential is `CLAUDE_CODE_OAUTH_TOKEN`, made from a Claude subscription with `claude setup-token`, so no Anthropic API key is needed. This file never contains its value, and you never paste it into a comment, a file or a log.

## Where to run it

- In a terminal on your own machine, opened at the repository root of a clean clone of `main`, signed in with `gh auth status` as an owner of the repository. The `{owner}` and `{repo}` in the commands are filled in by `gh` from the clone.
- Steps marked "browser" are pages on github.com.
- Not here: the agent's sandbox. The agent never holds the credential and never changes repository settings.

## Before you start

1. Check that `gh` is signed in and `claude` is installed and signed in.

```
gh auth status
```

Expected: `Logged in to github.com` and no error.
If different: run `gh auth login`, then repeat.

```
claude --version
```

Expected: a version number.
If different: install Claude Code, run `claude` once and sign in with the account you normally use for headless runs.

2. Check that you are on an up-to-date `main`.

```
git switch main && git pull --ff-only
```

Expected: `Already up to date.` or a fast-forward, and no error.
If different: stop and tell the orchestrator what was printed.

## Steps

### Step 1: do the settings of #298 if you have not (`_human-tasks/2026-11-17T0307Z-human-task-298-engineer-oncall-environment-and-ruleset.md`)

Do its steps 1, 3, 4 and 5 (the `oncall` Environment limited to `main`, the ruleset on `main`, Actions may open pull requests, auto-merge off). Skip its step 2: this drill uses a different secret name, set in step 2 below.

Check each one now:

```
gh api repos/{owner}/{repo}/environments/oncall/deployment-branch-policies --jq '.branch_policies[].name'
```

Expected: exactly one line, `main`.
If different: do step 1 of the #298 file.

```
gh api repos/{owner}/{repo}/rulesets --jq '.[] | [.name, .enforcement, (.bypass_actors | length)] | @tsv'
```

Expected: a row `main`, `active`, `0`.
If different: do step 3 of the #298 file.

```
gh api repos/{owner}/{repo}/actions/permissions/workflow --jq '[.default_workflow_permissions, .can_approve_pull_request_reviews] | @tsv'
```

Expected: `read` and `true`.
If different: do step 4 of the #298 file.

### Step 2: make the credential and put it in the `oncall` Environment

Make a long-lived token for the drill. It opens a browser to sign in and then prints a token that starts with `sk-ant-oat`.

```
claude setup-token
```

Expected: a sign-in in the browser, then a token printed once. Copy it; it is not shown again.
If different: stop and tell the orchestrator what was printed, but not the token.

Store it. The next command asks for the value and does not show it. Paste the token, then press Enter. Do not put the value on the command line.

```
gh secret set CLAUDE_CODE_OAUTH_TOKEN --env oncall
```

Expected: `Set Actions secret CLAUDE_CODE_OAUTH_TOKEN for environment oncall`.
If different: stop and tell the orchestrator what was printed (not the token).

```
gh secret list --env oncall
```

Expected: a row for `CLAUDE_CODE_OAUTH_TOKEN`.
If different: no row means it was not saved; repeat the previous command.

Check the repository has no secret of that name outside the Environment, so only the agent job can read it:

```
gh secret list
```

Expected: no row named `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY`.
If different: delete the stray one with `gh secret delete <name>`.

Risk: the token acts as your Claude account, and drill runs count against its usage limits. Undo: `gh secret delete CLAUDE_CODE_OAUTH_TOKEN --env oncall`, and revoke the token in your Claude account settings.

### Step 3: land the workflow and the two workflow changes

The drill's scripts, tests and the proposed workflow are on the branch `claude/299-oncall-workflow`, not yet on `main`. Start a new branch from it, copy the proposed workflow, apply the diff for the other workflows, and check what changed. Use a branch name that does not exist yet (`git branch --list 'land-*'` shows the ones that do).

```
git fetch origin
git switch -c land-299-workflow origin/claude/299-oncall-workflow
cp observability/drill/proposed/oncall-drill.yml .github/workflows/oncall-drill.yml
git apply observability/drill/proposed/workflow-changes.patch
git status --short
```

Expected: `fatal` is absent from the output of the commands above; then `??` for `.github/workflows/oncall-drill.yml` and ` M` for `.github/workflows/compose.yml`, `.github/workflows/observability.yml` and `.github/workflows/verify.yml`.
If different: stop and tell the orchestrator what was printed.

The patch adds `ready_for_review` to the pull request types of `verify.yml` and `compose.yml` (so marking the agent's draft ready starts the normal CI), and raises the observability job's timeout from 20 to 30 minutes (the drift check runs the Python suite, about 6 minutes).

```
make test-one FILE=tests/test_oncall_drill_workflow.py
```

Expected: all tests pass.
If different: stop and tell the orchestrator which test failed.

Commit, push and open the pull request, then merge it in the browser after CI is green. A workflow run from a branch other than `main` cannot read the `oncall` Environment, so the file must be on `main` before step 4.

```
git add .github/workflows
git commit -m "Land the on-call drill workflow and its two workflow changes (#299)"
git push -u origin land-299-workflow
```

Expected: the branch is pushed. Open the pull request into `main` in the browser (browser); it carries the whole drill (scripts, tests, the workflow). Wait for green checks, merge.
If different: if the `socboard observability` run is red, open it: a failing drift check means the planted defect no longer applies or the suite catches it; stop and tell the orchestrator.

### Step 4: run the drill once

Do not run it twice for evidence. Start it from `main`:

```
git switch main && git pull --ff-only
gh workflow run oncall-drill.yml --ref main
```

Expected: `Created workflow_dispatch event for oncall-drill.yml at main`.
If different: a 404 means the workflow is not on `main` yet; finish step 3.

The run has a number, its **run id**. GitHub's tools call the same number `databaseId`, and it is also the last part of the run's web address (`.../actions/runs/<number>`). Print it:

```
gh run list --workflow oncall-drill.yml --limit 1 --json databaseId --jq '.[0].databaseId'
```

Expected: one number, for example `44065861050`. This is the run id. Everywhere below, `<run id>` means this number: type the number itself, without the `<` and `>`, which the shell reads as a redirect.
If different: no output means the run has not started; wait a minute and repeat. Note the number now (the result table has a place for it).

The run takes about 25 to 35 minutes: the first job waits up to 10 minutes for the alert to fire.

The `agent` job waits for approval only if the `oncall` Environment has required reviewers; if it does, approve it in the browser (browser).

```
gh run watch <run id> --exit-status
```

Expected: all five jobs (`drill`, `agent`, `publish`, `check`, `report`) succeed and the command exits 0.
If different: open the run's summary (browser). It says which stage stopped: no alert, hand-off failed, no change, guard refused, or a failed proof. Tell the orchestrator the run id and that line. Do not re-run before it is read.

### Step 5: read the result

```
gh api repos/{owner}/{repo}/pulls --jq '.[] | select(.head.ref | startswith("oncall/")) | [.number, .draft, .base.ref, .html_url] | @tsv'
```

Expected: one row: a pull request number, `true`, `drill/<run id>`, and its link.
If different: no row means no pull request was opened; read the run summary.

Open the pull request (browser), and read its merge box.

Expected: a draft whose base is `drill/<run id>`, and no auto-merge. Do not merge it.
If different: if it can merge into `main` without approval, or auto-merge is on, tell the orchestrator at once and close it.

This also answers the `VERIFY` of step 6 in the #298 file: does the merge box require a review? Write what it says in the table below.

### Step 6: keep the evidence

Download the screenshots of the firing alert and the incident file, then commit them with a record.

```
gh run download <run id> --name drill-evidence --dir _docs/evidence/observability/2026-11-17-oncall-drill
ls _docs/evidence/observability/2026-11-17-oncall-drill
```

Expected: `incident.json` and an `evidence` folder with `alert.png` and `dashboard.png`.
If different: a missing screenshot is not a failed drill; say so in the record.

Write `_docs/evidence/observability/2026-11-17-oncall-drill/README.md` with: the date, the run id and link, the pull request link, what was checked (alert fired at the time in `incident.json`; the agent's pull request; the before and after of the new test from the `check` job's log; the log scan found nothing) and the result. Then commit it on a branch and open a pull request to `main`.

## Record the result

Paste the output or write pass or fail for each step, with the date. Results contain no secrets.

| Step | Pass or fail | Output or note |
|---|---|---|
| Before you start | | |
| 1 | | |
| 2 | | |
| 3 | | |
| 4 (run id) | | |
| 5 (merge box says) | | |
| 6 | | |

## Risk

The run costs about 30 minutes of CI and some of the credential's usage. It pushes two throwaway branches, `drill/<run id>` and `oncall/<run id>`, and opens one draft pull request into the first. Delete both branches after you have kept the evidence (`git push origin --delete drill/<run id> oncall/<run id>`); nothing in `main` changes. The token is readable only by the agent job; a leak is limited by the ruleset on `main` and by revoking it in your Claude account.
