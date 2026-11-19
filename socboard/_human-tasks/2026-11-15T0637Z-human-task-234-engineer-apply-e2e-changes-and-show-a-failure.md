# Apply the protected changes for the browser test, then show that a failure leaves an artifact

## Purpose

Apply the three protected-file changes that #234 needs (the `make e2e-install` and `make e2e` targets, the `AGENTS.md` lines, and the browser steps of the Compose workflow), so CI runs the browser test; then show once that a failing run uploads a screenshot and a redacted trace. Issue: #234.

## Where to run it

The clean clone, on the branch `issue-234-e2e-browser-test` (steps 1 and 2; it is the pull request's branch, so CI runs the browser test on it), and the GitHub Actions page (step 3). Not here: the agent's sandbox, which has no Docker and no browser. The agent never edits `Makefile`, `AGENTS.md` or `.github/`.

## Before you start

1. Check that the branch is checked out and the proposals are in the folder.

```
git fetch origin
git checkout issue-234-e2e-browser-test
git merge --ff-only origin/issue-234-e2e-browser-test
ls _human-tasks/234-proposed
```

Expected: `agents.diff`, `compose-workflow.diff`, `e2e-make-check.txt` and `makefile.diff`.

## Steps

### Step 1: apply the three diffs and move the make-target test

Read the diffs first. `makefile.diff` adds `.PHONY: e2e` (the folder `e2e/` has the same name as the target, so without it make says "up to date" and runs nothing) and the targets `e2e-install` and `e2e`; `agents.diff` replaces the line `E2E: none` and adds `e2e/` to the Layout line; `compose-workflow.diff` adds Node and bun setup, the Chromium install, the browser test, a redaction step and the artifact upload to `.github/workflows/compose.yml`, after the stack tests step and before "Start again". `e2e-make-check.txt` is a test of the make target; it is a text file here so that moving it is not read as deleting a test file, and it can only pass once the target exists.

```
git apply --unidiff-zero _human-tasks/234-proposed/makefile.diff _human-tasks/234-proposed/agents.diff _human-tasks/234-proposed/compose-workflow.diff
git mv _human-tasks/234-proposed/e2e-make-check.txt tests/test_e2e_make.py
git rm -r --quiet _human-tasks/234-proposed
git add Makefile AGENTS.md .github/workflows/compose.yml tests/test_e2e_make.py
git status --short
```

Expected: `git status --short` lists `Makefile`, `AGENTS.md` and `.github/workflows/compose.yml` modified, `tests/test_e2e_make.py` added, and the three diffs deleted (the `.txt` shows as moved).
If different: stop and tell the orchestrator what was printed (the branch may have moved).

### Step 2: commit and push

```
HUMAN_APPROVED=1 git commit -m "Add make e2e-install and make e2e, their AGENTS.md lines and the browser steps of the Compose job (#234)"
git push origin issue-234-e2e-browser-test
```

Tell the orchestrator once it is pushed. The orchestrator reads the `socboard compose` run. The browser test has never run in a browser (the sandbox has none), so expect to go round this loop: a failed step, a fix in `e2e/`, a push by the orchestrator, a new run. Only changes to the three protected files need you.

Expected: the job passes, with `3 passed` for the journey, hostile-text and wrong-password tests and the 25 address tests in the Playwright output.

### Step 3: show a failure (once the job has passed)

The orchestrator pushes a scratch branch `scratch-234-broken-lead` whose only change is a wrong password for the Lead in `e2e/tests/journey.spec.ts`. Its `socboard compose` run should fail at "Browser test against the stack", run the redaction step, and upload the artifact `e2e-test-results`.

1. Open the run on GitHub (the orchestrator sends the link), check the artifact exists and expires in 7 days, download it and open `trace.zip` with `bunx playwright show-trace` or the online trace viewer.
2. Check by eye that the sign-in step shows `[redacted]` where the password was typed, and that no `Authorization` header shows a token.
3. Delete the scratch branch: `git push origin --delete scratch-234-broken-lead`.

Expected: the failed run, the artifact with a screenshot and a trace, and no secret value visible in either.
Risk: the trace of a failing run is public to anyone who can read the repository's Actions artifacts. The values in it are throwaway (generated on the runner), and the redaction step runs first and fails the job's upload if a value is left. The branch deletion cannot be undone, and the branch holds one commit that exists nowhere else.

## Record the result

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |

## Risk

The workflow steps run on every push and pull request. They read only the secrets file the job generated, mask its values, and drive a stack that exists only inside the runner. The browser download (about 150 MB) comes from the Playwright CDN on each run.
