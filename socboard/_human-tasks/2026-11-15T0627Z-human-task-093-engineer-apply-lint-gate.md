# Apply the protected lint gate change for #93

## Purpose

Put the frontend lint into the one Lint gate of `make verify` (so CI and the push check run it too): one line in `agent-kit.conf` and one sentence in the `AGENTS.md` Verify line. The agent never edits either file. Issue: #93.

## Where to run it

The clean clone, on the branch `issue-93-frontend-lint-gate`. Not here: the agent's sandbox, which cannot edit protected files.

## Before you start

1. Check that the branch is checked out, the tree is clean, and the proposed diff is in the folder.

```
git switch issue-93-frontend-lint-gate
git pull --ff-only
git status --short
ls _human-tasks/093-proposed
```

Expected: `git status --short` prints nothing, and `ls` prints `lint-gate.diff`.

## Steps

### Step 1: read the diff

```
cat _human-tasks/093-proposed/lint-gate.diff
```

Expected: two changes of one line each. In `AGENTS.md` line 28, the Verify line gains "the OpenAPI contract check, the frontend lint," between "(Python and frontend)," and "whitespace". In `agent-kit.conf` line 25, `LINT_CMD=""` becomes `LINT_CMD="make contract-check && make frontend-lint"`. Nothing else.

### Step 2: apply it

```
git apply --unidiff-zero _human-tasks/093-proposed/lint-gate.diff
git status --short
git diff --stat
```

Expected: `git apply` prints nothing. `git status --short` lists ` M AGENTS.md` and ` M agent-kit.conf`, and the untracked proposal folder. `git diff --stat` shows two files changed, 1 insertion and 1 deletion each.
If different: stop and tell the orchestrator what was printed (the branch may have moved).

### Step 3: check the new line

```
grep -n '^LINT_CMD=' agent-kit.conf
```

Expected, exactly one line: `25:LINT_CMD="make contract-check && make frontend-lint"`

### Step 4: remove the proposal, commit the two files and push

```
git rm -r --quiet _human-tasks/093-proposed
git add AGENTS.md agent-kit.conf
git status --short
HUMAN_APPROVED=1 git commit -m "Run the OpenAPI contract check and the frontend lint in the Lint gate of make verify (#93)" -m "Assisted-by: Kiro"
git push origin issue-93-frontend-lint-gate
```

Expected: `git status --short` lists `M  AGENTS.md`, `M  agent-kit.conf` and `D  _human-tasks/093-proposed/lint-gate.diff`. The commit and the push succeed. Tell the orchestrator once it is pushed. The orchestrator then reads the `socboard verify` run on the new head for the `== Lint (make contract-check && make frontend-lint) ==` section and `PASS: Lint`.
Risk: after this lands on `main`, a red frontend lint or a failing contract check fails `make verify`, the pre-push hook and CI, including for issues that touch only Python. Undo: revert the commit, or set `LINT_CMD=""` again.

### Step 5: the push check (needs Docker)

The pre-push hook runs the push check in a throwaway container. Read its output during the push in step 4.

Expected: it contains `PASS: Lint`. If the hook cannot run (no Docker), say so; CI is the evidence.

## Record the result

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

## Risk

The change widens what `make verify` runs, so a frontend lint failure now blocks every push. #31 made lint pass on `main` first, so the gate starts green.
