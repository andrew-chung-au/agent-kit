# Apply the protected changes for the stack tests and run them once

## Purpose

Apply the three protected-file changes that #229 needs (the `make test-stack` target, its Commands line, and the added steps of the Compose workflow), and run the stack tests once where Docker exists. Issue: #229.

## Where to run it

The clean clone, on the branch `issue-229-stack-integration-tests` (steps 1 and 2), and a machine with Docker (step 3). Not here: the agent's sandbox, which has no Docker. The agent never edits `Makefile`, `AGENTS.md` or `.github/`.

## Before you start

1. Check that the branch is checked out and the three proposed files are in the folder.

```
ls _human-tasks/229-proposed
```

Expected: `agents.diff`, `compose-workflow.diff`, `makefile.diff` and `test_stack_make.py` (a test that runs `make test-stack` with no address and expects it to refuse; it can only pass once the Makefile has the target, so it goes into `tests/` in the same commit).

## Steps

### Step 1: apply the three diffs

Read them first. `makefile.diff` adds the target `test-stack` after `test-one`; `agents.diff` adds one Commands line after "Test (one file)"; `compose-workflow.diff` adds three steps to `.github/workflows/compose.yml` before its "Start again" step: mask the generated values, fetch the built image's schema out of the `app` container, and run `make test-stack` with the proxy's address.

```
git apply --unidiff-zero _human-tasks/229-proposed/makefile.diff _human-tasks/229-proposed/agents.diff _human-tasks/229-proposed/compose-workflow.diff
```

Expected: no output; `git status --short` shows `Makefile`, `AGENTS.md` and `.github/workflows/compose.yml` modified.
If different: stop and tell the orchestrator what was printed (the branch may have moved).

### Step 2: remove the proposals, commit the protected paths and push

```
git mv _human-tasks/229-proposed/test_stack_make.py tests/test_stack_make.py
git rm -r --quiet _human-tasks/229-proposed
git add Makefile AGENTS.md .github/workflows/compose.yml tests/test_stack_make.py
git status --short
HUMAN_APPROVED=1 git commit -m "Add make test-stack, its AGENTS.md line and the stack test steps of the Compose job (#229)"
git push origin issue-229-stack-integration-tests
```

`git status --short` should list the three modified protected paths, the new `tests/test_stack_make.py`, and the three deleted diff files. Tell the orchestrator once it is pushed. The orchestrator then reads the `socboard compose` run on the new head. If the stack tests fail there, the job fails at "Integration tests against the stack"; send the step's log lines.

Expected: the job passes, with `stack_only: 4 marked, 0 deselected (live stack)` in the log.

### Step 3: one run on a machine with Docker

```
make compose-up
set -a; . ./compose.secrets; set +a
SOCBOARD_BASE_URL=http://127.0.0.1:8080 STACK_APP_URL=http://127.0.0.1:8000 STACK_SCHEMA_FILE=<a file you made with the command in the README, "Tests against the stack"> make test-stack
```

Expected: all tests pass. The shell now holds the stack's secrets: close it afterwards. Do not paste any value anywhere.
If different: send the failing test names and the last lines of `docker compose logs` (they hold no secret).
Risk: the run adds cases to the stack's database and uses the ingest key's allowance for a minute. Starting over means deleting the data volume, which you do on purpose (README, "Compose stack").

## Record the result

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |

## Risk

The workflow steps run on every push and pull request. They read only the secrets file the job itself generated, mask its values, and write cases to a stack that exists only inside the runner.
