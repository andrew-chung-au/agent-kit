# Add the contract-check target and validator, and run them in the dev container

> Human task for #9. Written by the orchestrator; the Engineer could not run `uv` in Kiro Web.

> **Status: done (2026-11-11).** Every step below has been run once; the results are in "Record the result". Do not run steps 1, 3 or 7 again: the dependency is already committed (`2e009c9`) and the branch is pushed. To re-check the contract on a later commit, run only steps 4, 5 and 6 in the dev container after `git pull --rebase origin issue-9-openapi-contract`; they change nothing in the repository.

## Purpose

Land the protected changes for #9 (the `contract-check` target, its Commands line and the validator dependency), then prove the check passes on `openapi.yaml` and fails on a broken copy. Issue: #9.

## Where to run it

The dev container, in a clean checkout of branch `issue-9-openapi-contract` (pushed to GitHub). Not here: Kiro Web, where `uv` cannot create its Python directory.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue.

## Before you start

1. You have read the three protected diffs in the orchestrator's message and approved them (the `Makefile` target, the `AGENTS.md` Commands line, and the dev dependency).

```
git switch issue-9-openapi-contract
```

Expected: you are on the branch, and `git log --oneline -3` shows `Add the OpenAPI contract openapi.yaml (#9)` at the top.

## Steps

### Step 1: add the validator as a dev dependency

```
uv add --dev openapi-spec-validator
```

Expected: `pyproject.toml` and `uv.lock` change; `uv.lock` names a version that supports OpenAPI 3.1 (`openapi-spec-validator` 0.7 or later). Write the version in the results table.
If different: stop and tell the orchestrator what was printed.

### Step 2: check the target and Commands line already on the branch

The orchestrator committed the approved `Makefile` target and the AGENTS.md Commands line in `2ab7135` (with `HUMAN_APPROVED=1`, after you approved the exact diffs). Check them:

```
git show --stat 2ab7135
```

Expected: only `Makefile` (6 lines added) and `AGENTS.md` (1 line added).

### Step 3: commit the dependency files

```
HUMAN_APPROVED=1 git commit -m "Add openapi-spec-validator as a dev dependency (#9)" pyproject.toml uv.lock
```

Expected: the commit succeeds with `pyproject.toml` and `uv.lock` only; end the message with the tool line the repository requires if an agent helped.

### Step 4: the check passes on the contract

```
make contract-check
```

Expected: exits 0 and says the file is valid.
If different: copy the full error to the orchestrator; do not edit `openapi.yaml` yourself.

### Step 5: the check refuses a broken copy

Do not edit `openapi.yaml` by hand in this step. This command writes the broken copy for you, with the `openapi: 3.1.0` line left out, and leaves `openapi.yaml` unchanged:

```
grep -v '^openapi: 3.1.0$' openapi.yaml > .scratch/broken-openapi.yaml
```

Then run the check on the copy, then on the root file again, then confirm nothing in the repository changed:

```
make contract-check FILE=.scratch/broken-openapi.yaml
make contract-check
git status --short
```

Refusal test: run it in this dev container window, not in an agent session.
Risk: none; the copy is in `.scratch/` and nothing is printed except the validator's error. If `openapi.yaml` itself was edited by mistake, `git restore openapi.yaml` puts it back.
Expected: the copy fails with a non-zero exit (the validator prints a blank `Error: `); the root file still prints `openapi.yaml: OK`; `git status --short` prints nothing. Then delete `.scratch/broken-openapi.yaml`.

Also check that the target refuses an option or an absolute path as `FILE`, without running the validator:

```
make contract-check FILE=--version
```

Expected: the usage error from `Makefile` line 142; no `uv run` line is printed. The same for `FILE=/etc/hosts`.

### Step 6: verify is unchanged

```
make verify
```

Expected: the same steps as before; its output lists no contract check. If it fails for a reason unrelated to #9, copy the output.

### Step 7: push from the clean clone

The dev container cannot push (GitHub returns 403; by design, see `AGENTS.md`, Project settings). Push from the clean clone on your machine instead, after fetching the dev container's branch into it:

```
git push origin sandbox/issue-9-openapi-contract:refs/heads/issue-9-openapi-contract
```

Expected: the push check runs `make install verify` in the push-check image and the branch updates on GitHub. If the image is missing, build it first (`_human-tasks/2026-11-11T0327Z-human-task-engineer-rebuild-push-check-image.md`). Never use `--no-verify` or `--force`. Tell the orchestrator, who then launches QA.

## Record the result

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 (validator version) | pass | `openapi-spec-validator` 0.9.0 (21 packages resolved; also pydantic 2.14.3, pydantic-core 2.50.4). Hardlink warning only. |
| 2 | pass | The branch was behind at first (`No rule to make target 'contract-check'`); after `git pull --rebase` the target and Commands line from `2ab7135` were present. |
| 3 | pass | Committed `pyproject.toml` and `uv.lock` only (532 insertions, 2 deletions); on GitHub as `2e009c9`. |
| 4 | pass | First run failed on three unquoted YAML scalars (lines 257, 592, 597), fixed in `114624c`; then `openapi.yaml: OK`, and again `openapi.yaml: OK` after the Differences change in `8ad8874`. |
| 5 | pass | Final run at `7e4de44`: `openapi.yaml: OK`; a copy written with `grep -v` (no `openapi: 3.1.0` line) failed with a blank `Error: ` and make exit status 2; the root file again `openapi.yaml: OK`; `git status --short` empty. `FILE=--version` and `FILE=/etc/hosts` were refused with the usage error and the validator did not run. Earlier runs were confused because the root file had been edited by hand (the old wording of this step was ambiguous) and copies of it failed; `git restore openapi.yaml` fixed it. The failure message is blank, a known limitation; only one kind of break was shown. |
| 6 | pass | `VERIFY: PASS` at `7e4de44`: 47 Python tests, 154 frontend tests, no whitespace errors, "No test files changed", nothing changed since the pushed branch. Its output lists no contract check. |
| 7 | pass | The dev container cannot push (403 by design). Pushed from the clean clone after building `agent-push-check:node24-uv0.13.6-bun1.4.2` (bun 1.4.2) and setting `AGENT_PUSH_CHECK_IMAGE`; the push check passed. Also covers the rebuild-the-image task from #46. |

Filled in by the orchestrator from the output the human pasted in this session; the human confirmed the steps ("I think I did the steps can you fill it in for me").

## Risk

The dependency commit changes protected files (`pyproject.toml`, `uv.lock`); it was committed only with your approval of the exact change. Steps 4 to 6 change nothing. The branch is pushed, so there is no local undo: a wrong commit is fixed by a new commit, never by rewriting the pushed history. If `openapi.yaml` is edited by mistake in step 5, `git restore openapi.yaml` puts it back.
