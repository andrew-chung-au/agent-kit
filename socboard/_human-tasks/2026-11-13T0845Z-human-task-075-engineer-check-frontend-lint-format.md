# Check make frontend-lint and make frontend-format

> Drafted from `_docs/agent-kit/templates/human-task.md`. No step prints a secret or the environment.

## Purpose

Check by hand the criteria of #75 that need `frontend/node_modules` and the npm registry: the refused case, the pass-through of bun's result, the format run, the missing-tool message in a clone, and that `make verify` is unchanged. Issue: #75.

## Where to run it

The dev container, in a checkout of `main` (it has the #75 targets since PR #130 merged), after `make frontend-install` (except Step 6, which needs a clone without `frontend/node_modules`). Not here: `main` itself, for any step that writes (Step 5 uses a throwaway branch). `make frontend-format` rewrites files, so never run it on `main`.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue.

## Before you start

1. Confirm you are on an up-to-date `main` with a clean tree.

```
git status --short --branch
```

Expected: the first line names `main`; no other lines.

## Steps

### Step 1: Create the untracked probe file with single quotes

Create `frontend/src/lint-probe.ts` containing exactly this one line (single quotes):

```
export const probe = 'x';
```

Expected: `git status --short` shows `?? frontend/src/lint-probe.ts` and nothing else.
If different: stop and tell the orchestrator what was printed.
Risk: creates one untracked file; Step 3 deletes it.

### Step 2: The lint target refuses the probe and takes no arguments

```
make frontend-lint
```

Expected: a `prettier/prettier` error for `frontend/src/lint-probe.ts` (among the other errors current `main` has until #31), and a non-zero exit.

```
make frontend-lint ARGS=--fix
```

Expected: the same error for the probe file, a non-zero exit, and `frontend/src/lint-probe.ts` unchanged (still single quotes; the target ignores `ARGS`).
If different (the file was rewritten or `--fix` took effect): fail; tell the orchestrator what was printed.
Risk: if the rule fails, `--fix` would rewrite only the untracked probe file; nothing tracked is touched.

### Step 3: Delete the probe and check the tree is clean

Delete `frontend/src/lint-probe.ts` (the file is this task's own).

```
git status --short
```

Expected: nothing printed.

### Step 4: Pass-through comparison for lint

```
make frontend-lint
```

```
cd frontend && bun run lint
```

Expected: the same rules, counts and files in both, and the same non-zero exit on current `main` (it has lint errors until #31). The counts differ from older numbers because #21's frontend changes landed after the issue was groomed; compare the two runs with each other, not with old figures. The `make` run adds only the `make: *** ... Error` line.
If different: fail; paste both outputs to the orchestrator.

### Step 5: The format run, on a throwaway branch only

Do not run this on `main`. Create the throwaway branch from it:

```
git switch -c throwaway-75-format
```

```
make frontend-format
```

```
git status --short
```

Expected: changed files listed under `frontend/` (the target rewrites files). Write down whether the list includes `frontend/package.json` (a protected file) or any file under `frontend/src/test/` or any `*.test.*` file (the weakened-test guard watches those); tell the orchestrator either way. Then discard them and leave the branch:

```
git restore frontend
```

```
git status --short
```

Expected: nothing printed.

```
git switch main
```

```
git branch -d throwaway-75-format
```

Expected: you are back on `main` and the throwaway branch is gone.
If different: do not retry another way; tell the orchestrator what was printed.
Risk: `make frontend-format` rewrites tracked files under `frontend/` (markdown, CSS, JSON, HTML and sources not in `frontend/.prettierignore`). Undo: `git restore frontend`. Files Prettier creates, if any, show as `??` in `git status --short`; remove only those you recognise as its output.

### Step 6: The missing-tool message in a clone without node_modules

In a fresh clone of the branch (no `frontend/node_modules`; do not run `make frontend-install` there):

```
make frontend-lint
```

Expected: `frontend-lint: frontend/node_modules/.bin/eslint is missing; run make frontend-install first`, a non-zero exit, and no bun output.

```
make frontend-format
```

Expected: `frontend-format: frontend/node_modules/.bin/prettier is missing; run make frontend-install first`, a non-zero exit, and no bun output.

### Step 7: make verify is unchanged

On `main` (after `make frontend-install`), and, to compare, on a checkout from before PR #130 (for example the commit before its merge):

```
make verify
```

Expected: the same list of steps and the same kind of output on both. Neither lint nor format appears among the steps.
If different: fail; paste the two step lists to the orchestrator.

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets either.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | Pass | Run 2026-11-13 in a separate clone at `main` `5d0ffa6`. The probe file showed as `?? frontend/src/lint-probe.ts` and nothing else. |
| 2 | Pass | `make frontend-lint` reported `1:22 error Replace 'x' with "x" prettier/prettier` for the probe file; the same with `ARGS=--fix`, and the file stayed single-quoted (`ARGS` ignored). |
| 3 | Pass | After deleting the probe, `git status --short` printed nothing. |
| 4 | Pass | `make frontend-lint` and `cd frontend && bun run lint` both ended `395 problems (394 errors, 1 warning)` and `script "lint" exited with code 1`; `make` added only its own `Error 1` line. |
| 5 | Pass | `make frontend-format` on a throwaway branch rewrote 18 files: 7 test files under `frontend/src/test/` (`contract-paths`, `error-page-router`, `guardrails`, `http-service`, `mock-service`, `real-client`, `screen-behaviour`), `frontend/AGENTS.md`, `frontend/README.md`, `frontend/src/routes/README.md` and 8 source files. It did NOT change `frontend/package.json`. `git restore frontend` left a clean tree and the branch was deleted. This answers Reviewer finding 1 (the warning on the `AGENTS.md` line): the target does rewrite files the weakened-test guard watches. #31's Engineer will meet the same churn. |
| 6 | Pass | In a clean clone, `make frontend-lint` and `make frontend-format` printed the two exact missing-tool messages, each followed by `Error 1` and exit 2; bun did not start. |
| 7 | Pass | `make verify` ended `PASS: Tests`, `PASS: no whitespace errors`, `No test files changed.`, `VERIFY: PASS`. Neither lint nor format is among its steps. |

## Risk

Step 1 creates one untracked file (removed in Step 3). Step 5 rewrites tracked files under `frontend/` on a throwaway branch; `git restore frontend` undoes it. `make frontend-format` rewrites files, so it must not be run on `main`. Nothing else changes live behaviour.
