# Apply the publish workflow, then make the first package public

## Purpose

Apply the protected changes that #235 needs (the new `publish.yml`, the tested-image steps in `compose.yml`, and the test of both), merge, and after the first push to `main` make the registry package public and check that it can be pulled without a login. Issue: #235.

## Where to run it

The clean clone on the branch `issue-235-publish-tested-image` (steps 1 and 2), GitHub (steps 3 to 5), and a machine that is not logged in to ghcr.io (step 5). Not here: the agent's sandbox, which has no Docker and no Actions. The agent never edits `.github/`.

## Before you start

1. Check that the branch is checked out and the proposals are in the folder.

```
git fetch origin
git checkout issue-235-publish-tested-image
git merge --ff-only origin/issue-235-publish-tested-image
ls _human-tasks/235-proposed
```

Expected: `compose-workflow.diff`, `publish-workflow-check.txt` and `publish.yml`.

## Steps

### Step 1: apply the compose diff, add the workflow and its test

Read them first. `compose-workflow.diff` adds the commit and its time to the Compose job's environment (they become the image's labels) and, on a push to `main` only, three steps at the end of the job: check the tested image's files, save the image with `docker save`, upload it as the artifact `tested-image` for one day. `publish.yml` is the new workflow: a gate job that reads the commit's other workflow runs, and the one publishing job that holds `packages: write`. `publish-workflow-check.txt` is a test of both files; it is a text file here so that moving it is not read as deleting a test file, and it can only pass once the workflow exists.

```
git apply --unidiff-zero _human-tasks/235-proposed/compose-workflow.diff
git mv _human-tasks/235-proposed/publish.yml .github/workflows/publish.yml
git mv _human-tasks/235-proposed/publish-workflow-check.txt tests/test_publish_workflow.py
git rm -r --quiet _human-tasks/235-proposed
git add .github/workflows/compose.yml .github/workflows/publish.yml tests/test_publish_workflow.py
git status --short
```

Expected: `compose.yml` modified, `publish.yml` and `tests/test_publish_workflow.py` added, and the three proposal files shown as moved or deleted.
If different: stop and tell the orchestrator what was printed (the branch may have moved).

### Step 2: commit and push

```
HUMAN_APPROVED=1 git commit -m "Add the publish workflow and the tested-image steps of the Compose job (#235)"
git push origin issue-235-publish-tested-image
```

Tell the orchestrator once it is pushed. The Compose job on the pull request will still pass: the new steps run on a push to `main` only. `publish.yml` cannot run on a pull request (a `workflow_run` workflow runs from `main`), so the first real run is after the merge.

### Step 3: merge, then watch the first run on `main`

After you merge, the pushes to `main` start `socboard verify`, `postgres`, `image` and `compose`. When the last one completes, `socboard publish` runs: the gate job says `ready=true`, the publishing job pushes the image. Send the orchestrator the link to the `socboard publish` run. If it fails, nothing deploys from it yet (D20 and D22a do not exist), and the orchestrator fixes it in a new pull request.

Expected: a run named `socboard publish` with `gate` and `publish` both green, and a job summary showing the image, the tag and the digest. Read the log of the push and login steps once: no token, only `Login Succeeded` and the layer lines.
If the push fails with a denied or unauthorized message on this first run, send the lines (the first run is also the check of how GHCR answers for a package that does not exist yet).
Note: runs of `socboard publish` for the other, earlier-finishing workflows end with `ready=false` and a `publish` job that is skipped. That is the design.

### Step 4: make the package public and link it to the repository

GitHub creates the package on the first push, often as private. The server has no registry login, so a private package fails the deploy.

1. On GitHub: your profile or organisation, Packages, `socboard`, Package settings.
2. If the package is not connected to the repository, connect it (the image's `org.opencontainers.image.source` label names the repository, which normally links it).
3. Under "Manage Actions access", make sure this repository is listed with the Write role (a package created by a workflow is usually linked at once; if it is not, the second push gets a 403).
4. Under Danger Zone, change the visibility to Public.

Risk: anyone can then pull the image. It holds no secret (the image check of #190 runs on it) and the repository is public. Making a package private again is possible; deleting a published version is not undone.

### Step 5: check the pull from a machine that is not logged in

```
docker pull ghcr.io/<owner>/socboard:<the tag in the job summary>
```

Expected: the image downloads with no login. Compare the digest it prints with the one in the job summary.
If different: the package is still private or not found; send what was printed.

### Step 6: show that a pull request never pushes

Open or update any pull request after step 3. In the Actions list, `socboard publish` appears for the pull request's head with the `gate` job skipped (and `publish` skipped). Send the orchestrator the link.

## Record the result

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| 6 | | |

## Risk

`publish.yml` holds the only registry write permission CI has. It runs on every completion of the five workflows, ends at a skipped job unless the run is a push to `main` of this repository, and runs no code from the repository in the job that holds the token. The first push makes a package that is private until you change it. A mistake in the publishing job is fixed forward; nothing deploys from the image yet.
