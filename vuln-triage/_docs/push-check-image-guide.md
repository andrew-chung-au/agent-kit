# Guide: build and try the push-check image (#112)

A step-by-step guide for the human. It covers what to do on your own machine to
build the push-check image from `ci/push-check/Dockerfile`, check it, and make
your pushes pass. Nothing here is run by an agent: the sandbox container has no
Docker.

## Where each step runs

There are three places. Every step below says which one.

| Place | What it is | How you know you are in it |
|---|---|---|
| **Clean clone** | Your own checkout on Ubuntu (WSL), where you review and push. The prompt looks like `andrew@DESKTOP-G6N2NM9:~/projects/vuln-triage$` | `git remote -v` lists a remote named `sandbox` |
| **Sandbox / container** | The dev container where the agent works (`/workspaces/vuln-triage-sandbox`) | Do not use it for this guide |
| **Docker on your machine** | The `docker` command, run from a clean-clone terminal | `docker --version` prints a version |

All commands in this guide are typed in a **terminal in the clean clone**
(`~/projects/vuln-triage`). Open VS Code's Restricted Mode for that folder, as
`_docs/agent-kit/environments.md` says.

**Rule that applies to every step: never run `make` in the clean clone.** That
includes `make verify`, `make test` and `make install`. The Makefile is code an
agent may have changed. The push check runs `make` for you, but inside a
throwaway container. `docker build` and `docker run` are fine: they run the
Dockerfile's steps inside Docker, not on your machine.

## What you will do, in order

1. Check Docker works (2 minutes).
2. Fetch and review the agent's commits (10 to 20 minutes).
3. Merge them locally. Do not push yet.
4. Build the image (5 to 15 minutes, needs the internet).
5. Check the tools in the image.
6. Point the push check at the image and do a dry run.
7. Do a real push.
8. Check the push check blocks a broken install.
9. Report back.

## Step 1. Check Docker works

Run in a clean-clone terminal:

```
docker --version
docker run --rm hello-world
```

Expected: a version line, then a message starting `Hello from Docker!`.

If `docker` is not found, or it says it cannot reach the daemon: start Docker
Desktop on Windows (with its WSL integration turned on for your Ubuntu), or
start the Docker service, then try again. You also need a few gigabytes of free
disk space; `docker system df` shows what Docker uses now.

## Step 2. Fetch and review the agent's commits

Run in the clean clone:

```
git fetch sandbox
git status
git branch -a
```

`git fetch sandbox` copies the agent's commits into your clean clone as
`sandbox/<branch>`; it does not change your files. `git branch -a` lists them.
The agent commits on `main` in the sandbox, so look for `remotes/sandbox/main`.

The commits for this work, from oldest to newest, are (hashes from the sandbox):

| Commit | What |
|---|---|
| `d811e9b` | `Makefile`: new `backend-lock` target (#26) |
| `8ec6313` | #26 implementation (data model, Alembic, tests) |
| `b3e08a7` | `architecture.md`: KEV value marked "derived, not stored" |
| `b6086fa` | `AGENTS.md`: `make backend-lock` line, migrations note |
| `83260c0` | **`ci/push-check/Dockerfile`** (#112) |
| `9902d07` | `AGENTS.md`: push-check gotcha points to the Dockerfile |
| later ones | session summaries, usage log, roadmap, and this guide |

Review them the way `_docs/agent-kit/process.md` ("Commits and pushes") asks:

```
git log --oneline origin/main..sandbox/main
git diff origin/main sandbox/main --stat -- .
```

Then read the full diff, and ask about any changed file that the issue's
Constraints do not allow:

```
git diff origin/main sandbox/main
```

For #112 you must read these two files line by line, because their steps run on
your machine inside Docker with internet access:

```
git show sandbox/main:ci/push-check/Dockerfile
git diff origin/main sandbox/main -- AGENTS.md Makefile
```

What to look for in the Dockerfile:

- every download names an exact version (`npm@11.19.1`, `uv:0.13.1`,
  `python 3.12.15`, `pip-audit==2.10.1`, `terraform 1.17.0` with a SHA-256 check);
- there is no `COPY`, no secret, no `curl ... | sh`, and no Docker socket;
- nothing reads your home folder or credentials.

If anything looks wrong, stop and tell the agent in the sandbox session what to
change. Do not build an image you have not read.

## Step 3. Merge the commits locally (no push yet)

Still in the clean clone. The Dockerfile has to be on your disk to build it, so
merge the reviewed commits into your local branch:

```
git branch --show-current
git merge sandbox/main
```

The first command shows your branch (earlier you were on a `feat/...` branch;
use whichever branch you push from). The merge only changes your local copy.
Nothing reaches GitHub until step 7.

If git reports a conflict, stop and ask the agent session to help. Do not
resolve it by guessing.

Check the file is there:

```
ls ci/push-check
```

Expected: `Dockerfile`.

## Step 4. Build the image

Run in the clean clone (the `.` of `ci/push-check` is the build folder):

```
docker build -t vulntriage-push-check:1 ci/push-check
```

This downloads the Node base image, Debian packages, npm, uv, Python 3.12.15,
`pip-audit`, `openapi-spec-validator` and Terraform. It takes several minutes and
needs the internet. Watch for the last line: `naming to docker.io/library/vulntriage-push-check:1`.

### If the build fails

Copy the **last 30 lines of the output** and send them to the agent session.
Know these likely points before you do:

| Failing step | Message looks like | What it means | What to do |
|---|---|---|---|
| `COPY --from=ghcr.io/astral-sh/uv:0.13.1` | `manifest unknown`, `not found` | That exact tag may not exist on the registry. The most likely failure. | Tell the agent: "use the uv 0.13.1 release tarball with its .sha256 file". The Dockerfile comment names this fallback. |
| `ln -s "$(uv python find 3.12.15)"` | `No interpreter found` | uv put Python somewhere the `find` did not look | Send the output; the Engineer will adjust the link step. |
| Terraform step | `sha256sum: WARNING` or `FAILED` | The download did not match the pinned checksum. Do not work around it. | Send the output. A changed checksum needs a human look. |
| Any `apt-get` or `npm` step | network errors | A temporary download problem | Run the same build command once more. |

Do not edit the Dockerfile yourself on the clean clone. Changes go through the
agent so they are committed in the sandbox and reviewed.

## Step 5. Check the tools in the image

Run each command in the clean clone. Each starts a container, prints one thing
and removes the container (`--rm`). The expected result is next to each.

```
docker run --rm vulntriage-push-check:1 node --version
```
Expected: `v24.22.0`

```
docker run --rm vulntriage-push-check:1 npm --version
```
Expected: `11.19.1`

```
docker run --rm vulntriage-push-check:1 uv --version
```
Expected: `uv 0.13.1` (a build hash may follow in brackets)

```
docker run --rm vulntriage-push-check:1 python3.12 --version
```
Expected: `Python 3.12.15`

```
docker run --rm vulntriage-push-check:1 git --version
docker run --rm vulntriage-push-check:1 make --version
docker run --rm vulntriage-push-check:1 bash --version
```
Expected: a version line each. If one says `executable file not found`, report
it; the base image was assumed to carry them.

```
docker run --rm --network none vulntriage-push-check:1 uvx openapi-spec-validator==0.9.0 --help
```
Expected: a usage text and exit code 0. `--network none` turns the network off,
which proves the tool is cached in the image. If it fails with a network error,
report it: that one check may need the Engineer to change the Dockerfile. It is
not critical for pushing.

```
docker run --rm vulntriage-push-check:1 test -f /usr/include/postgresql/libpq-fe.h
```
Expected: no output. Then check the exit code with `echo $?`: it should print `0`.

```
docker run --rm vulntriage-push-check:1 pip-audit --version
```
Expected: contains `2.10.1`

```
docker run --rm vulntriage-push-check:1 terraform version
```
Expected: `Terraform v1.17.0`

```
docker run --rm vulntriage-push-check:1 sh -c 'cd /tmp && printf "terraform {}\n" > main.tf && terraform fmt -check && terraform init -backend=false && terraform validate'
```
Expected: ends with `Success! The configuration is valid.` The `init` step
needs the internet to fetch Terraform's plugin index, so do not add
`--network none` here.

```
docker run --rm vulntriage-push-check:1 env
```
Expected: the long list contains `UV_PYTHON_DOWNLOADS=never`. Optional.

```
docker image ls vulntriage-push-check:1
```
Expected: one row. Note the **SIZE** column. The target is under about 2 GB. If
it is bigger, report the number; the agent will name the largest layer and you
decide whether to drop a tool.

## Step 6. Point the push check at the image and do a dry run

The push check is the script `.git/hooks/pre-push` in the clean clone (it is
installed from `~/.agent-hooks/pre-push`). It reads the image name from the
environment variable `AGENT_PUSH_CHECK_IMAGE`. Set it in the same terminal:

```
export AGENT_PUSH_CHECK_IMAGE=vulntriage-push-check:1
```

This lasts only for that terminal window. To keep it for every new terminal, add
the same line to the end of your `~/.bashrc` (your own file, not the repo) and
open a new terminal. Check it with `echo "$AGENT_PUSH_CHECK_IMAGE"`.

**Always name the destination in a push: `git push origin HEAD:refs/heads/<name>`.**
A bare `git push` uses the branch's upstream, and a branch created from the
agent's work tracks the `sandbox` remote. Pushing there is wrong: `sandbox` is
the agent's folder, which you only ever fetch from. Check with
`git remote -v` (you want to push to `origin`, the GitHub one) and
`git rev-parse --abbrev-ref @{upstream}` (it may print `sandbox/main`; that is
why a bare push fails or goes to the wrong place).

Pick `<name>` for the branch on GitHub, for example
`feat/26-112-data-model-push-image`. In plan mode the name is only a label.

Now the dry run. Plan mode prints what the push check would run and then
**blocks the push on purpose**, so nothing is sent to GitHub:

```
AGENT_PUSH_CHECK_PLAN=1 git push origin HEAD:refs/heads/<name>
```

Expected output includes:

```
push check plan for <hash> (base <hash>):
  make -C . install verify
push check: plan only; push not sent (unset AGENT_PUSH_CHECK_PLAN to push)
```

and `error: failed to push some refs`. That error is correct: it is plan mode.
The key line is `make -C . install verify`. If you instead see
`WARNING no agent-kit project ... nothing checked`, tell the agent.

## Step 7. Do a real push

Only after steps 4 to 6 look right, and only if you are happy with the diff you
reviewed in step 2:

```
git push origin HEAD:refs/heads/<name>
```

Use the same `<name>` as in step 6. This creates that branch on GitHub; open a
pull request from it, or merge it into `main` your usual way. Do not add
`--set-upstream` or push to `sandbox`.

What happens: the push check bundles your new commits, starts a throwaway
container from the image, checks out your commit, then runs
`make -C . install verify` inside it. That does `npm ci`, `uv sync --locked`, the
frontend tests, the backend tests, the type check and the other checks. It needs
the internet (do not set `AGENT_PUSH_CHECK_NETWORK=none`) and takes a few
minutes.

Expected: the lines `push check: make -C . install verify`, then test output
ending with a verify result of PASS or PASS WITH WARNINGS (warnings are
acceptable; read them), then git's usual push output. Exit code 0.

If it prints `push check: make verify failed ..., push blocked`, copy the last
40 lines of output and send them to the agent session. Common cause: a test that
passes in the sandbox but needs something the image lacks.

## Step 8. Check the push check blocks a broken install

This proves a failing install stops the push instead of being ignored. It uses a
throwaway branch that you delete afterwards.

```
git switch -c throwaway/no-lock
git rm backend/uv.lock
git commit -m "throwaway: remove uv.lock to test the push check"
git push origin HEAD:refs/heads/throwaway/no-lock
```

Expected: the push check runs, `uv sync --locked` fails (an error about a missing
`uv.lock`), it prints `push check: make verify failed ..., push blocked`, and
git refuses the push. **That is the pass.**

If instead the push **succeeds**, that is a problem: tell the agent, then remove
the branch from GitHub with `git push origin --delete throwaway/no-lock`.

Clean up in every case, going back to the branch you were on:

```
git switch <your branch>
git branch -D throwaway/no-lock
```

(`git branch --show-current` earlier told you the name of `<your branch>`.)

## Step 9. Report back

Paste this into the agent session, with your real outputs:

```
#112 image results
- Build: <succeeded / failed + last 30 lines>
- node / npm / uv / python3.12: <the four outputs>
- git / make / bash: <ok / which one was missing>
- offline uvx: <exit 0 / error>
- libpq header: <exit 0 / not found>
- pip-audit / terraform versions: <the two outputs>
- terraform fmt/validate: <Success / error>
- Image size (docker image ls): <size>
- Plan push showed "make -C . install verify": <yes / no>
- Real push: <passed / blocked + last 40 lines>
- Missing uv.lock push: <blocked as expected / unexpectedly passed>
```

Then the agent session closes #112. If something failed, the Engineer fixes the
Dockerfile in the sandbox and QA re-checks only what changed; you fetch,
review, merge and rebuild with `docker build` again (step 2 onwards for the new
commits).

## When the image must be rebuilt

Rebuild (step 4 only, plus step 5 checks) when any pinned version changes:
Node, npm, uv, Python, `openapi-spec-validator`, `pip-audit` or Terraform. The
list is the comment block at the top of the Dockerfile. A change to the pin must
also be made in `.github/workflows/verify.yml` and the dev container, so the
three stay in step.

## If you need to push before the image works

Do not bypass the hook with `--no-verify`. Ask the agent session instead.
Running `make install` and `make verify` in the **sandbox** (not the clean
clone) already shows whether the code passes, and the push check is the gate for
whether it reaches GitHub.
