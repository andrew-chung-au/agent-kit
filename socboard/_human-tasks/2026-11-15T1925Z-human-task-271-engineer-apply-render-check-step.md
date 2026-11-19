# Add the render check to the Compose job and make the gateway check cover every pool entry

## Purpose

Apply the one protected change #271 needs in `.github/workflows/compose.yml`: replace #261's gateway step with one that also requires exactly one pool entry, and add a step that renders `compose.yaml` three times (no variable, an example second stack, the server's trusted address) and fails unless the project name, the five addresses and the trusted address come out as expected. Issue: #271.

## Where to run it

The clean clone, on the branch `issue-271-stack-variables`. Not here: the agent's sandbox, which has no Docker. The agent never edits `.github/`.

## Before you start

### Step 1: check that #261's CI step is on `main`

PR #273 carries it (PR #264 was merged before it was pushed). The diff below is written against the file as #273 leaves it.

```
git fetch origin
git merge-base --is-ancestor e42efce origin/main && echo on-main
```

Expected: `on-main`.
If different: merge PR #273 first, or tell the orchestrator; the diff will not apply without that step.

### Step 2: check the branch and the proposal

```
git checkout issue-271-stack-variables
git merge origin/main
ls _human-tasks/271-proposed
```

Expected: `compose-workflow.diff`.
If different: stop and tell the orchestrator what was printed.

## Steps

### Step 3: apply the diff and read it

```
git apply --unidiff-zero _human-tasks/271-proposed/compose-workflow.diff
git diff
```

Expected: the step "The stack network's gateway is the pinned one (#261)" is replaced by "The stack network has one pool entry, with the pinned gateway (#261, #271)" (it prints the number of entries and the gateway and fails unless they are `1 10.231.77.1`), and one new step, "The project name, the network and the trusted proxy follow their variables (#271)", follows it. The new step runs `docker compose --env-file compose.secrets config --format json` three times and pipes each result to a small Python check. It starts nothing, reads no secret value into the log and prints only names and addresses.
If different: stop and tell the orchestrator what was printed.

### Step 4: remove the proposal, commit the protected file and push

```
git rm -r --quiet _human-tasks/271-proposed
git add .github/workflows/compose.yml
git status --short
```

Expected: `.github/workflows/compose.yml` modified and the diff file deleted, nothing else.

```
HUMAN_APPROVED=1 git commit -m "Render check and pool-entry check in the Compose job (#271)"
git push origin issue-271-stack-variables
```

Tell the orchestrator once it is pushed. The orchestrator reads the `socboard compose` run: the first new step should print `pool entries and gateway: 1 10.231.77.1`, and the second three JSON lines (one per render) with the matching names and addresses.
If different: the render step names what did not match. If Docker Compose's JSON uses other key names than the check expects (`ip_range`, `ipv4_address`), send the printed line and the Compose version the job prints; that is a `VERIFY:` point of the issue and the orchestrator fixes the check.
Risk: the steps run on every push and pull request. They use no secret value and write only a file in the runner's temporary folder.

## Record the result

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |

## Risk

The steps only read Docker's network settings and render the file on the runner. A mistake in the diff fails the Compose job, never the server.
