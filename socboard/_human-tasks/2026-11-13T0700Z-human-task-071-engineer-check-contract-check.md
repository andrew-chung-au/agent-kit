# Check that make contract-check behaves the same after the #71 text change

## Purpose

Confirm the valid, explicit and missing-file runs of `make contract-check` are unchanged by the text-only edit. Issue: #71.

## Where to run it

The dev container (needs `uv` and the locked packages), in a clean clone or this folder, on branch `issue-71-contract-check-text`. Not here: the Kiro Web sandbox, where `uv` cannot run (read-only file system).

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue.

## Before you start

1. Check you are on the branch with the `Makefile` change applied (committed or in the working tree).

```
git status --short
```

Expected: shows the branch's `Makefile` change if uncommitted, or nothing if committed.

## Steps

For the "before" side, run each step once on `main` (593edfd) and once on the branch, and compare.

### Step 1: valid default file

```
make contract-check
```

Expected: prints `openapi.yaml: OK`, exit 0.
If different: stop and tell the orchestrator what was printed.

### Step 2: valid explicit file

```
make contract-check FILE=openapi.yaml
```

Expected: prints `openapi.yaml: OK`, exit 0.
If different: stop and tell the orchestrator what was printed.

### Step 3: missing file

```
make contract-check FILE=nope.yaml
```

Expected: the same validator error on `main` and on the branch, and a non-zero exit.
If different: stop and tell the orchestrator what was printed.

## Record the result

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | Pass | `make contract-check` printed `openapi.yaml: OK` (run on `main` in the dev container, 2026-11-13). |
| 2 | Pass | `make contract-check FILE=openapi.yaml` printed `openapi.yaml: OK`, in a separate clone at `main` `5d0ffa6`. |
| 3 | Pass | `make contract-check FILE=nope.yaml` printed `No such file: nope.yaml`, then `Error 1`, exit 2: the validator's own error, not a usage line. Extra check: `FILE=--version` printed the new usage text at `Makefile:147`, exit 2. |

## Risk

None: read-only commands.
