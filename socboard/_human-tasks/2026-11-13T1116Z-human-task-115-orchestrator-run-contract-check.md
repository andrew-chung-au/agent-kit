# Run make contract-check on the #115 contract changes

## Purpose

Validate the edited `openapi.yaml` against the OpenAPI version it declares. CI runs `make verify`, which does not run `make contract-check`, and the Kiro Web sandbox cannot run `uv`, so this is the one acceptance criterion (the eighth) nobody has run. Issue: #115.

## Where to run it

The dev container terminal (it needs `uv` and the locked packages), in a checkout of branch `issue-115-contract-sync`, or of `main` after the merge. Not here: the Kiro Web sandbox.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue.

## Before you start

1. Confirm the branch and a clean tree.

```
git status --short --branch
```

Expected: the first line names `issue-115-contract-sync` (or `main` after the merge); no other lines.

## Steps

### Step 1: validate the contract

```
make contract-check
```

Expected: `openapi.yaml: OK`, exit 0.
If different: stop, don't retry another way, and tell the orchestrator what was printed (the validator names the path of the bad part).

### Step 2: the new shared response is where the three operations point

```
grep -n "PathParameterValidationError" openapi.yaml
```

Expected: four lines: three `$ref` lines (under `getCase`, `claimCase` and `getAudit`) and one definition under `components/responses`.
If different: stop and tell the orchestrator what was printed.

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets either.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | Pass | `make contract-check` printed `openapi.yaml: OK`, run on `main` in the dev container after PRs #134 and #136 merged (2026-11-13). Run again with `FILE=openapi.yaml` in a separate clone at `5d0ffa6`: also OK. |
| 2 | Not run | The search for `PathParameterValidationError` (three `$ref` lines and one definition) was not reported as run. QA read the same four places in the diff. |

## Risk

None: both commands only read files.
