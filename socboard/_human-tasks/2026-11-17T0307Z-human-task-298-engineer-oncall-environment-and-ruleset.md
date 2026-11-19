# Set up the `oncall` Environment, protect `main`, and allow Actions to open pull requests

## Purpose

Give the on-call agent's workflow the one secret it needs in a locked Environment, and make sure the publish job's `contents: write` cannot reach `main`. Issue: #298. Rubric: On-Call Agent. The agent's drill workflow (#299) is not built yet, so nothing here can run the agent; these are the settings it will rely on.

The secret is `ANTHROPIC_API_KEY`. This file never contains its value, and you never paste it into a comment, a file or a log.

## Where to run it

- In a terminal on your own machine, opened at the repository root of a clean clone, signed in with `gh auth status` as an owner of the repository. The `{owner}` and `{repo}` in the commands are filled in by `gh` from the clone.
- Steps marked "browser" are settings pages on github.com.
- Not here: the agent's sandbox. The agent never holds this key and never changes repository settings.

## Before you start

1. Check that `gh` is signed in.

```
gh auth status
```

Expected: `Logged in to github.com` and no error.
If different: run `gh auth login`, then repeat. If it still fails, stop and tell the orchestrator what was printed.

## Steps

### Step 1: create the `oncall` Environment, limited to the `main` branch

```
gh api -X PUT repos/{owner}/{repo}/environments/oncall -F 'deployment_branch_policy[protected_branches]=false' -F 'deployment_branch_policy[custom_branch_policies]=true' --jq '.name'
```

Expected: `oncall`.
If different: a 403 or 404 means your sign-in lacks admin rights on the repository. Stop and tell the orchestrator the status code.
Risk: creates an Environment with no secret and no rule yet. Undo: `gh api -X DELETE repos/{owner}/{repo}/environments/oncall`.

```
gh api -X POST repos/{owner}/{repo}/environments/oncall/deployment-branch-policies -f name=main -f type=branch --jq '.name'
```

Expected: `main`.
If different: a 422 saying the name already exists means it is already set; go on. Anything else: stop and tell the orchestrator what was printed.

```
gh api repos/{owner}/{repo}/environments/oncall/deployment-branch-policies --jq '.branch_policies[].name'
```

Expected: exactly one line, `main`.
If different: an extra line means another branch is allowed. Delete it in the browser (Settings, Environments, `oncall`, Deployment branches and tags) and repeat.

### Step 2: add the secret to the Environment

The next command asks for the value and does not show it. Paste the key when asked, then press Enter. Do not put the value on the command line.

```
gh secret set ANTHROPIC_API_KEY --env oncall
```

Expected: a prompt for the value, then `Set Actions secret ANTHROPIC_API_KEY for environment oncall`.
If different: stop and tell the orchestrator what was printed (not the key).

```
gh secret list --env oncall
```

Expected: one row, the name `ANTHROPIC_API_KEY` and an updated time. GitHub never shows the value.
If different: no row means the secret was not saved; repeat the previous command.

Also check that the repository has no secret of that name outside the Environment, so only the agent job's Environment can read it:

```
gh secret list
```

Expected: no row named `ANTHROPIC_API_KEY`.
If different: delete it with `gh secret delete ANTHROPIC_API_KEY` and keep the Environment's one.

### Step 3: add the ruleset on `main` (browser)

Open Settings, Rules, Rulesets, New ruleset, New branch ruleset.

- Ruleset name: `main`.
- Enforcement status: `Active`.
- Bypass list: leave it empty. In particular, do not add GitHub Actions or any app.
- Target branches: Add target, Include default branch.
- Rules, tick: Restrict deletions; Require a pull request before merging, with Required approvals set to `1`; Block force pushes. Leave Restrict creations and Restrict updates unticked (Require a pull request already stops a direct push).

Click Create.

Expected: the new ruleset appears in the list with status Active.
If different: stop and tell the orchestrator which rule was missing.

```
gh api repos/{owner}/{repo}/rules/branches/main --jq '.[].type'
```

Expected: the lines `deletion`, `non_fast_forward` and `pull_request` (any order).
If different: a missing line means that rule is not on `main`; open the ruleset and tick it.

```
gh api repos/{owner}/{repo}/rules/branches/main --jq '.[] | select(.type == "pull_request") | .parameters.required_approving_review_count'
```

Expected: `1`.
If different: `0` means no approval is required; open the ruleset and set Required approvals to 1.

```
gh api repos/{owner}/{repo}/rulesets --jq '.[] | [.name, .enforcement, (.bypass_actors | length)] | @tsv'
```

Expected: a row `main`, `active`, `0`.
If different: a number above 0 means someone is on the bypass list; remove them.

### Step 4: allow GitHub Actions to create pull requests (browser)

Open Settings, Actions, General, Workflow permissions. Leave "Read repository contents and packages permissions" selected. Tick "Allow GitHub Actions to create and approve pull requests", then Save. GitHub has one box for creating and approving; there is no creating-only box.

```
gh api repos/{owner}/{repo}/actions/permissions/workflow --jq '[.default_workflow_permissions, .can_approve_pull_request_reviews] | @tsv'
```

Expected: `read` and `true`.
If different: `write` means the default token is not read-only; select the read option and Save. `false` means the box is not ticked.

### Step 5: check that auto-merge is off for the repository

```
gh api repos/{owner}/{repo} --jq '.allow_auto_merge'
```

Expected: `false`.
If different: `true` means auto-merge is allowed. Untick "Allow auto-merge" under Settings, General, Pull Requests, then repeat.

### Step 6: `VERIFY:` whether an approval by `github-actions` counts toward the required review

The question: with the ruleset from step 3, does an approving review posted by `github-actions` (the workflow's token) satisfy "1 required approval"? The publish job never approves, and the ruleset's review rule is the backstop, so the answer decides how much the backstop is worth. A community answer says such an approval does not count ([discussion 181487](https://github.com/orgs/community/discussions/181487)); that is not GitHub's documentation, so it is not taken as fact.

First check that no workflow approves (this should hold now and after #299 lands):

```
grep -rnE "gh pr review|--approve|/reviews" .github/workflows
```

Expected: no output.
If different: tell the orchestrator the file and line. A workflow that approves is a finding for #299.

Then answer the question once, when the first draft pull request from the agent exists (#299), by opening it and reading its merge box. Record what it says in the table below.

Expected: the merge box says a review is required and the pull request is blocked until you approve.
If different: if it says the pull request can merge with no approval, tell the orchestrator at once and do not merge it.

## Record the result

Paste the output or write pass or fail for each step, with the date. Commit this file with the result so a later run can compare. Results contain no secrets either.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| 6 (VERIFY, answered when #299's first pull request exists) | | |

## Risk

Step 4 lets workflows approve pull requests as well as open them. The ruleset in step 3 and the fixed code of the publish job are what keep that harmless, so do step 3 before step 4. Nothing here can be undone silently: each setting can be switched off on the same page.
