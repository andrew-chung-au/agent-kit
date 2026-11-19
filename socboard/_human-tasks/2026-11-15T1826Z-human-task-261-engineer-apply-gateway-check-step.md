# Add the gateway check step to the Compose job

## Purpose

Apply the one protected change #261 needs: a step in `.github/workflows/compose.yml` that prints the gateway Docker chose for the stack network and fails unless it is `10.231.77.1`. Issue: #261.

## Where to run it

The clean clone, on the branch `issue-261-pin-stack-gateway`. Not here: the agent's sandbox, which has no Docker. The agent never edits `.github/`.

## Before you start

### Step 1: check the branch and the proposal

```
git fetch origin
git checkout issue-261-pin-stack-gateway
git merge --ff-only origin/issue-261-pin-stack-gateway
ls _human-tasks/261-proposed
```

Expected: `compose-workflow.diff`.
If different: stop and tell the orchestrator what was printed (the branch may have moved).

## Steps

### Step 2: apply the diff and read it

```
git apply --unidiff-zero _human-tasks/261-proposed/compose-workflow.diff
git diff
```

Expected: one new step, "The stack network's gateway is the pinned one (#261)", after "Start the stack". It runs `docker network inspect socboard_stack` with a format that prints only the gateway, echoes it, and fails unless it equals `10.231.77.1`. It reads no secret and changes nothing.
If different: stop and tell the orchestrator what was printed.

### Step 3: remove the proposal, commit the protected file and push

```
git rm -r --quiet _human-tasks/261-proposed
git add .github/workflows/compose.yml
git status --short
```

Expected: `.github/workflows/compose.yml` modified and the diff file deleted, nothing else.

```
HUMAN_APPROVED=1 git commit -m "Check the stack network's gateway in the Compose job (#261)"
git push origin issue-261-pin-stack-gateway
```

Tell the orchestrator once it is pushed. The orchestrator reads the `socboard compose` run: the new step should print `gateway 10.231.77.1`, and everything after it should still pass.
If different: if the step prints another address, Docker on the runner did not take the pin; send the line and the Docker version the job prints in "Set up job".
Risk: the step runs on every push and pull request. It uses no secret and writes nothing.

### Step 4: after the merge, recreate any stack you have running

A stack started before this change has a network with the old settings, which Compose recreates only with its containers stopped.

```
make compose-down
make compose-up
```

Expected: the stack starts again with its data (the volume is kept).
If different: if `make compose-up` says the network exists with a different configuration, run `docker network ls`, find `socboard_stack`, and send what you see.

### Step 5: on the server, remove the network from the gateway measurement

Run this on the server only if the throwaway network you made to measure the gateway is still there. It uses the same subnet, so D20's `docker compose up` would fail with an overlapping address pool.

```
docker network ls
```

Expected: no network with the subnet `10.231.77.0/24` before the first deploy; if one is listed, note its name.
If different: remove it with `docker network rm <name>` after `docker ps -a` shows it has no containers.
Risk: removing a network a container uses fails safely. Undo: not needed, the network was only for the measurement.

## Record the result

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

## Risk

The step only reads Docker's network settings on the runner. A mistake in the diff fails the Compose job, never the stack.
