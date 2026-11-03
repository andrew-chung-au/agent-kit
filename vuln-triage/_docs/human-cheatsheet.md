# Human cheatsheet: reviewing, pushing and merging agent work

For the human only. The agent kit's original method was "fetch the sandbox's `main`, read the diff, push `main`". The repo has moved on: `main` is protected, most work arrives as `claude/*` branches through pull requests, and several sessions can run at once. This sheet describes the method as the repo now works, from `AGENTS.md`, `_docs/cloud-sessions.md`, the roadmap and the recent history. Where it disagrees with those, they win; fix this file. Items marked `VERIFY:` are inferred from the record, not confirmed.

## 0. The one-minute picture

- **`main` only changes by merged pull request** (merge commit; no squash, no rebase). Ruleset: PR required, `verify` check required, no force-push, no delete. Your bypass is "for pull requests only", so you cannot push to `main` directly either.
- **Work lands on a branch**, `claude/<name>` or `claude/issue-NNN-<name>`, from one of two places:
  - **Cloud session:** the session pushes its own branch (the only push an agent may make). You open and merge the PR.
  - **Local sandbox:** the agent commits on a branch in the sandbox and **cannot push** (`git push*` is denied, token is read-only). You fetch it into the clean clone, push the branch, and open the PR. `VERIFY:` that sandbox `main` is kept equal to `origin/main`, as the #56 session did.
- **Issues, comments and closing** go through `make issue-dump`, `make issue-comment`, `make issue-close` (REST), not `gh issue ...` (blocked in the cloud).
- **Protected files** (`AGENTS.md`, spec, `agent-kit.conf`, `.claude/`, `Makefile` parts, etc.) change only on your approval, in their own commit with `HUMAN_APPROVED=1`, followed by an approval record on the issue. Merge commits keep those SHAs valid, which is why squash and rebase are off.

| | Sandbox (dev container) | Clean clone (Ubuntu) | Cloud session |
|---|---|---|---|
| Who works there | Agent | You | Agent |
| Can push? | No | Yes (your login) | Own `claude/*` branch only |
| `make` | Yes | **Never** | Yes |

## 1. Rules that never change

- **Never run `make` in the clean clone** (including `make hooks`, `make verify`). Agent-written Makefile, your login.
- **Touch the sandbox folder only with `git fetch sandbox`**, run from the clean clone. Don't open or rebuild the dev container without comparing `.devcontainer/` against the clean clone's copy first.
- **Read the full diff before every merge or push.** A QA PASS or green CI is not proof of a clean diff. Ask about every file outside the issue's Constraints.
- **Check these files first:** `Makefile`, `.claude/`, `.githooks/`, `.github/`, `.devcontainer/`, `.vscode/`, `.envrc`, `mise.toml`, `.gitmodules`, `agent-kit.conf`, `AGENTS.md`, `_docs/specs.md`, `package.json`/lockfiles (new dependencies need your approval), and any test that shrank.
- **Start cloud sessions only from `main` or a branch you have reviewed.** The branch's own hooks and `.claude/settings.json` run in the session.
- **One issue, one environment, one branch at a time.**

Examples use issue #56 and branch `claude/issue-056-stage-4-testing`; swap in your own. Run each command on its own line. `$` lines are commands; `#` lines are notes.

## 2. Flow A: a cloud session's branch

1. **Before launching:** answer the issue's decision questions; push anything local first (the session clones GitHub, not the sandbox).
2. **Launch** (normal permission mode, not auto/bypass; answer approvals promptly, idle sessions pause):

   ```
   $ claude --cloud "Work issue #56 following _docs/agent-kit/process.md, as the orchestrator. Ask me at the decision point."
   ```

3. **At the decision point** the session asks once; approve or reject protected diffs there. Approved protected commits are made in the session with `HUMAN_APPROVED=1`.
4. **When it finishes, review the branch** (clean clone, read-only commands):

   ```
   $ git fetch origin
   $ git log --oneline origin/main..origin/claude/issue-056-stage-4-testing
   $ git diff origin/main...origin/claude/issue-056-stage-4-testing --stat
   $ git diff origin/main...origin/claude/issue-056-stage-4-testing
   ```

   Then open the PR on GitHub (the branch page offers "Compare & pull request"), or with `gh`:

   ```
   $ gh pr create --base main --head claude/issue-056-stage-4-testing --title "Issue #56: Stage 4 test strategy" --body "Closes nothing; orchestrator closes #56."
   ```

   `VERIFY:` `gh pr create` uses GraphQL; it works on your machine but not in a cloud session. Use the web page if it fails.
5. **Check the PR:** `verify` is green; each protected commit has an approval record on the issue whose SHA matches. Merge with a **merge commit** (web button "Create a merge commit", or `gh pr merge 70 --merge`). Merged head branches are deleted automatically.
6. **Sync** (clean clone, then container):

   ```
   $ git switch main
   $ git fetch origin
   $ git merge --ff-only origin/main
   ```

   ```
   # in the dev container
   $ git pull
   ```

## 3. Flow B: a branch the local sandbox agent committed

Run in the clean clone, one command at a time. (This replaces the old "fetch `main`, push `main`".)

1. **Check the clone is clean and current:**

   ```
   $ git status --short
   $ git fetch origin
   ```

   `git status --short` should print nothing.
2. **Bring in the sandbox's work and list what is new:**

   ```
   $ git fetch sandbox
   $ git branch -r
   $ git log --oneline origin/main..sandbox/claude/issue-056-stage-4-testing
   ```

3. **Review** (stat first, then everything; use the section 1 list):

   ```
   $ git diff origin/main...sandbox/claude/issue-056-stage-4-testing --stat
   $ git diff origin/main...sandbox/claude/issue-056-stage-4-testing
   ```

   Look at one file or one commit when the diff is large:

   ```
   $ git diff origin/main...sandbox/claude/issue-056-stage-4-testing -- Makefile .claude .githooks
   $ git show 8d9db69 --stat
   ```

4. **Make a local branch of the same name:**

   ```
   $ git switch -c claude/issue-056-stage-4-testing sandbox/claude/issue-056-stage-4-testing
   ```

5. **Dry-run the push check** (prints which projects it would verify, sends nothing; the "push blocked" message at the end is expected):

   ```
   $ AGENT_PUSH_CHECK_PLAN=1 git push -u origin claude/issue-056-stage-4-testing
   ```

6. **Push the branch, not `main`.** The push check runs `make install verify` in a throwaway Docker container and blocks the push if it fails. The image must have Node; the default `python:3.12` does not (#32):

   ```
   $ AGENT_PUSH_CHECK_IMAGE=node:24.22.0-bookworm git push -u origin claude/issue-056-stage-4-testing
   ```

   Success ends with `VERIFY: PASS` and a `* [new branch]` line.
7. **Open the PR and merge** as in Flow A steps 4-5 (web page, or `gh pr create` / `gh pr merge N --merge`).
8. **Sync.** Clean clone as in Flow A step 6. In the container, make sure the agent isn't still on the old branch:

   ```
   # in the dev container
   $ git switch main
   $ git pull
   $ git branch -d claude/issue-056-stage-4-testing
   ```

   `git branch -d` refuses if the branch isn't merged, which is the check you want. Clean up the clone's copies:

   ```
   $ git branch -d claude/issue-056-stage-4-testing
   $ git fetch origin --prune
   ```

## 4. Several sessions at once

Parallel branches are normal now (for example #56 beside #60/#37/#61). Habits that keep it safe:

- Run in parallel only issues that touch different files. The roadmap's "Parallel tooling track" lists which ones share files (T2 then T3, never together).
- Expect conflicts in `_docs/roadmap.md` and `_docs/ai-usage-log.md` (every session appends). Resolution rule: **keep both entries**. Do it by having the branch's session merge `main` into the branch (`Merge remote-tracking branch 'origin/main' into claude/...`), then re-review.
- Merge the PRs in dependency order, and after each merge tell the other sessions to merge `main` in. In the container, on the branch:

  ```
  $ git fetch origin
  $ git merge origin/main
  # conflict in roadmap.md or ai-usage-log.md: edit the file, keep both sides' entries, then
  $ git add _docs/ai-usage-log.md
  $ git commit
  ```

  (Agents do this themselves when asked; the commands are here so you can read what they did: `git log --merges --oneline -5`.)
- `.scratch/` is shared in the sandbox; a session may skip `make clean-scratch` while another is active. Run it yourself when all are done.

## 5. Between issues: housekeeping that is now part of the process

- **Session summary** (`_session-summaries/`), **usage log** entry (`_docs/ai-usage-log.md`) and **roadmap check-in** (`_docs/roadmap.md`) arrive with every issue's branch. Check they are present and say the same thing as the diff. The summary's Permission review section lists every approval the agents needed.
- **Priority rule:** product steps first; tooling (kit, hooks, dev container) goes under "Later" unless it blocks the next product step or you schedule it. Don't let a PR smuggle in tooling work.
- **Permission sweep** (`_docs/agent-kit/procedures/permission-sweep.md`): periodically run `make permission-report SINCE=<commit>` in the container and approve or reject the proposed settings changes. First sweep is #65.
- **Spec and protected changes** are never silent: each has your approval in chat or on the issue and an approval record comment. #63 has four deferred spec notes waiting.
- **Rebuilding the dev container** (for example #31) is a human step, not mid-issue.

## 5b. Handy commands

Clean clone (read-only, safe):

```
$ git log --oneline --graph -15 origin/main        # recent history, with merged PRs
$ git log origin/main..main                        # commits only in your local main (should be empty)
$ git diff origin/main...<branch> --stat           # files a branch changes
$ git show <sha> --stat                            # one commit's files
$ git cat-file -p <sha>                            # a commit's parents and message
$ git rev-parse <sha>:AGENTS.md                    # blob ID, to compare with an approval record
$ git show --format= --no-renames --patch <sha> -- AGENTS.md   # the diff an approval record should contain
```

Issues from the container (agents use these; you can too):

```
$ make issue-dump N=56          # writes .scratch/issue-56.json and issue-56-comments.json
$ make issue-comment N=56 FILE=.scratch/comment.md
$ make issue-close N=56         # orchestrator only, after QA PASS and a committed session summary
```

Container, between issues:

```
$ make verify                   # tests, whitespace, weakened-test check
$ make verify BASE=origin/main  # same, with a real base on a branch with no upstream (#53)
$ make assert-clean             # nothing changed (used after QA)
$ make clean-scratch            # empty .scratch/ (when no session is still using it)
$ make permission-report SINCE=<commit>   # approvals recorded since a commit (for the sweep)
$ make tool-versions            # node, npm, uv, python3, docker
```

Approving a protected change (container; only after you approved the exact diff in chat):

```
$ git add AGENTS.md
$ git status --short
$ git diff --check
$ HUMAN_APPROVED=1 git commit -m "Describe what changed and why"
```

Then the agent posts the approval record on the issue (format: `_docs/agent-kit/procedures/asking-the-human.md`).

## 6. When something goes wrong

| Symptom | What to do |
|---|---|
| Push check: `make verify failed` | Read the container output; ask the agent to fix on the branch; re-fetch and re-review. Don't edit in the clean clone. |
| Push check fails on Node/npm | Set `AGENT_PUSH_CHECK_IMAGE=node:24.22.0-bookworm` (see Flow B step 5). |
| Push check: "nothing checked" | The new commits touch no project with `agent-kit.conf`; fine for docs-only, but confirm the diff really is. |
| Push check: `agent-kit.conf was removed` | Stop and find out why. Only if intended: `AGENT_PUSH_CHECK_ALLOW_REMOVED=1`. |
| GitHub rejects a push to `main` | Expected. Push a branch and open a PR. |
| PR blocked: `verify` not passing | Open the Actions run; the same `make verify` runs there. A branch with no upstream can hide a weakened test locally (#53): use `make verify BASE=origin/main` in the container. |
| Branch behind `main` after another PR merged | Have the session merge `main` into the branch (keep both log entries), then re-review the new diff. |
| `git merge --ff-only origin/main` refuses in the clean clone | Your local `main` has a commit that isn't on GitHub. Don't force; find the commit with `git log origin/main..main` and ask. |
| A session stopped early | Don't trust partial output. Check `git status --short`, `git log --oneline -5`, the issue's latest comments, and any running process before relaunching (`process.md`, "When a role stops early"). |
| Agent action blocked as risky | The agent stops and reports. Look at each blocked command and what it tried; decide to resume or restart fresh (QA: usually fresh). |
| `git fetch sandbox` acts strangely | The agent can edit `.git/config` in the shared folder. Read `<sandbox>/.git/config` as text; don't run git inside that folder. Keep your git updated. |

## 7. Checklist before you click merge

- [ ] I read the whole diff, including any file outside the issue's Constraints.
- [ ] `verify` is green on the PR (or the push check passed).
- [ ] QA PASS is on the issue and refers to the commit I'm merging.
- [ ] Protected commits are alone, each with an approval record whose SHA and diff match.
- [ ] No new dependency I haven't approved; no weakened or deleted tests.
- [ ] Session summary, usage log and roadmap lines are present.
- [ ] Merge type is **merge commit**.
- [ ] After merging: clean clone and container are on the new `main`; other sessions know.
