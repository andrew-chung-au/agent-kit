# Check make issue-body where gh is missing and where the remote is not github.com

## Purpose

Check the two #73 cases that the Kiro Web sandbox could not test: `make issue-body` with `gh` unavailable, and in a clone whose git remote is not github.com. Neither blocks the merge. Issue: #73.

## Where to run it

The dev container or a clean clone with `make`, `python3` and (for step 2) `gh` installed. Not here: the Kiro Web sandbox, where `gh` is always present and the remote is a gateway.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue.

## Before you start

1. Check that the branch with #73 is checked out (or `main` after the merge) and that `make help` lists `issue-body`.

```
make help
```

Expected: a line starting `issue-body` among the targets.

## Steps

### Step 1: run it where `gh` is not installed

Use a shell or container that has `make` and `python3` but not `gh`. First confirm `gh` is absent.

```
command -v gh
```

Expected: prints nothing and exits non-zero. If it prints a path, find another place; do not uninstall anything.

```
make issue-body N=999999
```

Expected: one line on stderr starting `issue-body:`, then make's own error line; a non-zero exit; and no `.scratch/issue-999999-body.json` and no `.scratch/issue-999999-body.json.tmp`.
If different: stop, don't retry another way, and tell the orchestrator what was printed.

### Step 2: run it in a clone whose remote is not github.com

In a clone with a non-github.com remote and `gh` logged in:

```
make issue-body N=73
```

Expected: prints `.scratch/issue-73-body.json`. The file has `title`, `labels` and `body`, and no `comments` key.
If different: stop and tell the orchestrator what was printed.

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets either.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | Not run (optional) | Skipped by the human. QA ran the failed-read case (`N=999999`) with `gh` present; it fails the same way, one `issue-body:` line and no file. |
| 2 | Pass | Run 2026-11-13 in a separate clone at `main` `5d0ffa6`, with a clone whose remote is a local path. `make issue-body N=73` printed `.scratch/issue-73-body.json`; its keys are `author`, `body`, `labels`, `number`, `state`, `title`, and no `comments`. `make help` lists `issue-body`. |

## Risk

None. Both steps only read from GitHub and write under `.scratch/`.
