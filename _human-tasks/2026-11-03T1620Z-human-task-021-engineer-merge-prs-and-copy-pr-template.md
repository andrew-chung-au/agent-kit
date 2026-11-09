# Review and merge the four pull requests, then install the pull request template

## Purpose

Merge the pull requests for #88, #77, #21 and #2, then copy the kit's pull request template into `.github/` so GitHub offers it in the web UI. Issues: #88, #77, #21, #2. The copy into `.github/` is the human's, because `.github/` is protected and agents never write it.

## Where to run it

The clean clone on your machine (not the sandbox folder, not the dev container), and the GitHub web UI for the merges. Not here: `make` in the clean clone, any target, ever.

## Before you start

1. Check that the clean clone has no local changes.

```
git status --short
```

Expected: no output.
If different: stop and tell the orchestrator what was printed.

2. Fetch the four branches.

```
git fetch origin
```

Expected: the four branches `issue-088-repo-kit-targets`, `issue-077-environments-upgrade-step`, `issue-021-pr-template` and `issue-002-root-readme` appear, or are already up to date.

## Steps

### Step 1: Read the changed files for #88.

```
git diff origin/main...origin/issue-088-repo-kit-targets --stat
```

Expected: `Makefile` and three files under `tests/`, plus the session summary. Ask about any other path.
If different: stop and tell the orchestrator what was printed.

### Step 2: Read the full diff for #88.

```
git diff origin/main...origin/issue-088-repo-kit-targets
```

Expected: two new make targets, `kit-check` and `kit-compare`, with the check on `$(value OTHER)` before the script runs; two narrowed assertions in `tests/test_kit_manifest.py` and `tests/test_kit_compare.py`.
If different: stop and tell the orchestrator what was printed.

### Step 3: Read the changed files for #77.

```
git diff origin/main...origin/issue-077-environments-upgrade-step --stat
```

Expected: `agent-kit/environments.md`, `tests/test_kit_env_and_launch.py` and the session summary.
If different: stop and tell the orchestrator what was printed.

### Step 4: Read the `environments.md` diff for #77.

```
git diff origin/main...origin/issue-077-environments-upgrade-step -- agent-kit/environments.md
```

Expected: only the "Upgrading the kit in the local sandbox" subsection changes; the rules about `make` in a clean clone, touching the sandbox folder from Ubuntu and copying files only from a clean clone are untouched.
If different: stop and tell the orchestrator what was printed.

### Step 5: Read the changed files for #21.

```
git diff origin/main...origin/issue-021-pr-template --stat
```

Expected: the new template, `tests/test_pull_request_template.py`, one row in `agent-kit/blueprints.md`, this task file and the session summary. Nothing under `.github/`.
If different: stop and tell the orchestrator what was printed.

### Step 6: Read the template for #21.

```
git diff origin/main...origin/issue-021-pr-template -- agent-kit/templates/github/pull_request_template.md
```

Expected: a template of at most 70 words that says `Refs #N` and forbids Closes, Fixes and Resolves in one sentence.
If different: stop and tell the orchestrator what was printed.

### Step 7: Read the changed files for #2.

```
git diff origin/main...origin/issue-002-root-readme --stat
```

Expected: `README.md`, `tests/test_root_readme.py`, `agent-kit.conf` (one line) and the session summary.
If different: stop and tell the orchestrator what was printed.

### Step 8: Read the `agent-kit.conf` diff for #2.

```
git diff origin/main...origin/issue-002-root-readme -- agent-kit.conf
```

Expected: one line, with `'README.md'` added to `PROTECTED`. Then read `README.md` on the branch as a visitor would, and the three session summaries it links; the test checks links, paths and make targets, not sentences. Decide whether to merge #2 now or wait for #9.
If different: stop and tell the orchestrator what was printed.

### Step 9: Merge the four pull requests in the GitHub web UI, in this order: #88, #77, #21, then #2 (or leave #2 open until #9 ships).

```
git ls-remote --heads origin
```

Expected: the four branches are listed. In the web UI each pull request shows green CI before you merge and "merged" after. Each pull request body says `Refs #N`, so merging does not close the issue.
If different: a red check means do not merge; tell the orchestrator which one.
Risk: a merge to `main` can't be undone without a revert commit.

### Step 10: Switch the clean clone to main.

```
git checkout main
```

Expected: `Switched to branch 'main'` or `Already on 'main'`.
If different: stop and tell the orchestrator what was printed.

### Step 11: Bring in the merged commits.

```
git pull --ff-only
```

Expected: the merged commits arrive without a merge prompt.
If different: stop and tell the orchestrator what was printed.

### Step 12: Create the `.github` folder if it is missing.

```
mkdir -p .github
```

Expected: no output.
If different: stop and tell the orchestrator what was printed.

### Step 13: Copy the template.

```
cp agent-kit/templates/github/pull_request_template.md .github/pull_request_template.md
```

Expected: no output.
If different: `No such file` means the #21 pull request is not merged yet; go back to the merge step.

### Step 14: Check the copy is byte-identical.

```
cmp agent-kit/templates/github/pull_request_template.md .github/pull_request_template.md
```

Expected: no output.
If different: stop and tell the orchestrator what was printed.

### Step 15: Stage the copy.

```
git add .github/pull_request_template.md
```

Expected: no output.
If different: stop and tell the orchestrator what was printed.

### Step 16: Commit the copy.

```
git commit -m "Install the pull request template in .github (#21)"
```

Expected: one new file in the commit. The kit's own hooks do not run in the clean clone; your push check and CI do that job.
If different: stop and tell the orchestrator what was printed.
Risk: undo before pushing with `git reset --hard origin/main`.

### Step 17: Push.

```
git push
```

Expected: the push check passes and the push succeeds.
If different: stop and tell the orchestrator what was printed.
Risk: a push to `main` can't be undone without a revert commit.

When all steps pass, tell the orchestrator. It closes #88, #77 and #21 (and #2 when you merge it); a merge alone never closes an issue.

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets either.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | (confirm) | Local check, not visible from GitHub. |
| 2 | (confirm) | Local diff read, not visible from GitHub. |
| 3 | (confirm) | Local diff read, not visible from GitHub. |
| 4 | (confirm) | Local diff read, not visible from GitHub. |
| 5 | (confirm) | Local diff read, not visible from GitHub. |
| 6 | (confirm) | Local diff read, not visible from GitHub. |
| 7 | (confirm) | Local diff read, not visible from GitHub. |
| 8 | (confirm) | Local diff read, not visible from GitHub. Decision: #2 was merged now, not held for #9. |
| 9 | pass | All four PRs merged 2026-11-03 (UTC): #2 as PR #100 at 15:30:44, #88 as PR #97 at 15:31:03, #77 as PR #98 at 15:31:34, #21 as PR #99 at 15:32:03. Merge order differed from the task: #2 went first. Issues #88, #77, #21 and #2 are closed. |
| 10 | pass (inferred) | Commit a3c43d3 sits on `main`, so the clone was on `main`. |
| 11 | pass (inferred) | The template was present on `main` to copy from, and the commit has a single parent, so history is linear (fast-forward). |
| 12 | pass (inferred) | `.github/` exists with the new file. |
| 13 | pass | `.github/pull_request_template.md` exists on `main`. |
| 14 | pass | Blob SHA of both files on `main` is `eb07fe060f2632c1abb1207845b581519245b98e`, so they are byte-identical. |
| 15 | pass (inferred) | The file is in the commit. |
| 16 | pass | Commit `a3c43d3` "Install the pull request template in .github (#21)", 2026-11-04T03:54Z, one file changed. |
| 17 | pass | Commit `a3c43d3` is on `origin/main`, and `main` has since moved ahead. |


## Risk

Merging and pushing change `main`. Nothing here prints a secret. Never run `make` in the clean clone.
