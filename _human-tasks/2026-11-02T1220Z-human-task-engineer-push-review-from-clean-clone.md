# Review the sandbox's commits and push them from the clean clone

## Purpose

Fetch the sandbox's commits into the clean clone, read them, merge and push. Issue: none (pilot for #50). The reasons are in `agent-kit/environments.md` (Local sandbox) and `agent-kit/process.md` ("Only the human pushes"); this file holds only the commands.

## Where to run it

A terminal on your own machine, inside the clean clone, `<repo>`. Not here: the sandbox folder or the dev container, and never `make` of any kind in the clean clone (`make hooks`, `make verify` and `make test` would run the agent's Makefile with your login).

## Before you start

1. Check you are on `main`.

```
git branch --show-current
```

Expected: `main`.
If different: stop, and tell the orchestrator what was printed.

2. Check the clean clone has no local changes.

```
git status --short
```

Expected: nothing printed.
If different: stop, and tell the orchestrator what was printed.

3. Check Docker is running, because the push check runs in a throwaway container.

```
docker --version
```

Expected: a version line.
If different: stop, and tell the orchestrator what was printed.

## Steps

### Step 1: Fetch the sandbox's commits into the clean clone

```
git fetch sandbox
```

Expected: git lists the sandbox's updated branches, or prints nothing when there is nothing new.
If different: for an error such as "No such remote", stop, don't retry another way, and tell the orchestrator what was printed.

### Step 2: Confirm the fetched branch is there

```
git branch -r
```

Expected: the list includes `origin/main` and `sandbox/main`.
If different: stop, and tell the orchestrator the list. The later steps assume `sandbox/main`; the branch name comes from the remote name and the Branching setting in `AGENTS.md`.

### Step 3: Read the list of changed files

```
git diff --stat origin/main sandbox/main
```

Expected: only files that the approved issues' Constraints name.
If different: for any other file, especially under `.devcontainer/`, `.github/` or `.githooks/`, stop and ask the orchestrator which issue it belongs to before going on.

### Step 4: Read the full diff

```
git diff origin/main sandbox/main
```

Expected: the changes match the issues and the session summaries. A clean QA report is not proof of a clean diff.
If different: stop, don't merge, and tell the orchestrator which hunk you do not understand.

### Step 5: Merge into your local main

```
git merge sandbox/main
```

Expected: a fast-forward, or a merge commit with no conflicts.
If different: for conflicts, stop and tell the orchestrator. Nothing has been sent anywhere.
Risk: changes your local `main` only. Undo while a merge is unfinished: `git merge --abort`. Otherwise ask the orchestrator before resetting anything.

### Step 6: Push

```
git push
```

Expected: the push check runs your tests in a throwaway container and prints their output, then the push succeeds.
If different: if the push check fails, stop, don't skip it, and send the printed output to the orchestrator; it becomes a new small issue. Do not use `--no-verify`.
Risk: publishes the commits to GitHub. Can't be undone without rewriting history.

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets either.

Note: this was not a dedicated test run. The flow was exercised in normal use (pilot for #50) when the sandbox's commits were reviewed, merged and pushed; the entries below are reconstructed from the history on GitHub, not pasted from a terminal.

| Step | Pass or fail | Output or note |
|---|---|---|
| Before 1 | (confirm) | Not recorded at the time. |
| Before 2 | (confirm) | Not recorded at the time. |
| Before 3 | (confirm) | Not recorded at the time. Docker was needed for the push check, and pushes went through. |
| 1 | (confirm) | Not recorded at the time. |
| 2 | (confirm) | Not recorded at the time. |
| 3 | (confirm) | Not recorded at the time. |
| 4 | (confirm) | Not recorded at the time. |
| 5 | pass (inferred) | Merge commits on `main` authored by the human on 2026-11-02: 8419348 "Merge #50" (13:45Z), f126d39 "Merge #13" (14:13Z), 200dfea "Merge #37" (14:32Z). |
| 6 | pass (inferred) | Those merges are on `origin/main`, so the push succeeded. Whether the push check output was seen is not recorded. |


## Risk

Step 6 publishes. Steps 1 to 5 change nothing outside your clean clone.
