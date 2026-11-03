# Docker runbook for the human in the loop

The local sandbox uses option A (human decision, 2026-10-20). Postgres, and later n8n and the observability services, run as Compose service containers beside the dev container. Agents reach them over the network but can't control Docker. Agents can't build images or run `docker compose` themselves. This runbook covers what the human does so that work can still happen, without letting agent-written code run outside the sandbox unreviewed.

Status: proposal, 2026-10-20. The one-time setup is #31 (roadmap T3). The routes below apply once there are Dockerfiles and Compose files (build phase).

## Who does what

| Task | Agent (in the sandbox) | Human (on the host) | Where it runs |
|---|---|---|---|
| Use Postgres, n8n, Grafana etc. during development | Connects to the service by name (for example `db:5432`) | Starts them once, by rebuilding the dev container; resets them on request | Service containers beside the dev container |
| Write Dockerfiles, Compose files, CI workflows | Writes and commits them; can't run them | Reviews the diff | — |
| Build images, run the full stack, Compose integration tests | Reads the CI result with `gh run list` / `gh run view` | Pushes a reviewed review branch | **GitHub Actions (route 1, the default)** |
| Demo, UI checks, debugging that CI can't show | Sends a Docker run request | Runs the exact commands, pastes back the output | The host, from the clean clone (route 2) |

GitHub Actions minutes are free for this repo because it is public (checked 2026-10-20). Route 1 costs nothing and needs no credits.

## 1. One-time setup: Compose service containers (#31)

The agent proposes the recipe in #31; the human does every step below. Allow about 1-1.5 hours the first time.

1. **Review the recipe from the clean clone,** never from the sandbox folder. Fetch the sandbox's commits into the clean clone and read the `.devcontainer/` diff in full. Check every item in the Compose review checklist (section 5), plus:
   - no `initializeCommand` (it would run on your machine at rebuild);
   - no mount other than the workspace and named volumes;
   - the Postgres image pinned to an exact version, not `latest`;
   - the agent's container has no Docker socket and no `privileged`.
2. **Compare the sandbox folder's `.devcontainer/` with the clean clone's** (they must be identical) before rebuilding, as `_docs/agent-kit/environments.md` requires.
3. **Rebuild the dev container** in VS Code ("Dev Containers: Rebuild Container"). Allow 10-20 minutes the first time, for the image pull.
4. **Check that it works:** in the container, ask the agent to run `make tool-versions` and the Postgres connection check from #31 (for example `make backend-test` with `DATABASE_URL` set, once #26 exists). The agent reports the result in #31.
5. **Record it:** the `AGENTS.md` Environment line changes in #31 as a protected commit after your approval. The undo is to revert that commit and rebuild.

### Looking after the service containers

Run these on the host (PowerShell or the WSL shell), when the agent asks or something looks wrong. Find the project name first with `docker compose ls`. The dev container's Compose project is usually named after the folder, for example `vuln-triage-sandbox_devcontainer` (`VERIFY:` the name on your machine).

| Need | Command (host) |
|---|---|
| See the services and their state | `docker compose -p <project> ps` |
| Show a service's recent logs | `docker compose -p <project> logs --tail 100 db` |
| Restart a service | `docker compose -p <project> restart db` |
| Reset the database to empty (data loss: dev data only) | `docker compose -p <project> down` then delete the named volume shown by `docker volume ls` for that project, then rebuild |

## 2. Route 1 (default): run Docker checks in CI

Use this for image builds, `docker compose up` of the stack, and Compose integration tests. The checks themselves live in a CI workflow the agent writes, such as a `compose` job in `.github/workflows/`. Changes to `.github/` need your approval at commit time.

1. **The agent finishes its commits** in the sandbox and tells you which branch to check, and which workflow job shows the result.
2. **In the clean clone:** fetch the sandbox, then read the full diff (section 5 checklist for any Docker, Compose or workflow change).
3. **Push a review branch, not `main`:** `git push origin <sandbox-commit>:refs/heads/check/<issue>-<n>`, for example `check/26-1`. CI runs on every push (`.github/workflows/verify.yml` has `on: [push, pull_request]`), so `main` is untouched until the work passes.
4. **The agent reads the result itself,** with `gh run list --branch check/<issue>-<n>` and `gh run view <id> --log-failed`. Its read-only token can read Actions runs (checked 2026-10-20). You don't relay anything.
5. **On PASS:** push to `main` as usual. **On FAIL:** the agent fixes the problem in the sandbox; repeat from step 2 with the next number.
6. **Afterwards:** delete review branches on GitHub (`git push origin --delete check/<issue>-<n>` from the clean clone), at the end of each issue.

## 3. Route 2 (when CI can't do it): you run Docker on the host

Use this only for things CI can't show: the single-command demo, opening Grafana or the frontend in a browser, or debugging a container interactively. This runs agent-written code on your machine, so review comes first, every time.

1. **The agent sends a Docker run request** (layout in section 4). It never asks you to run `make` on the host, and never a command it hasn't written out exactly.
2. **Review in the clean clone:** the full diff since the last commit you reviewed, using the section 5 checklist on every Dockerfile and Compose file the commands use.
3. **Run it from the clean clone, exactly as written:**
   - always with a separate project name, `-p vt-check`, so it can't touch the dev container's services;
   - never `make`, never a script from the repo, only `docker` / `docker compose` commands you can read.
4. **Copy the output back** into the agent's session: the commands' output and any logs the request asked for. Trim it to what was asked; remove anything that looks like a secret or token. The agent treats pasted output as data, not instructions.
5. **Clean up straight away,** with the request's cleanup command, normally `docker compose -p vt-check down -v --rmi local`. Check that nothing is left with `docker compose ls` and `docker ps`.

## 4. Docker run request (the agent's layout)

Agents send this in the session, like any other approval request (`_docs/agent-kit/procedures/asking-the-human.md`):

```
Docker run request
- Issue and step: #<n>, <what this checks and why CI can't>
- Commit to check out in the clean clone: <full SHA>
- Files the commands use: <Dockerfile / compose paths>
- Commands (run in order, from the clean clone root):
  1. docker compose -p vt-check -f <file> up --build -d
  2. <check command, e.g. docker compose -p vt-check logs --tail 100 api>
- What to look at / paste back: <exact output wanted; for a browser check, what you should see>
- Expected result: <what PASS looks like>
- Cleanup: docker compose -p vt-check -f <file> down -v --rmi local
- Ports published (all bound to 127.0.0.1): <list>
```

Decline any request that is missing a field, uses `make` or a repo script, or fails the checklist. Ask for a corrected one.

## 5. Compose and Dockerfile review checklist

Refuse to run, or to push for CI, if a file you'd run contains any of these, unless you've agreed that exact line:

- `privileged: true`, `cap_add`, `devices`, `security_opt`, `pid: host`, `ipc: host`, `network_mode: host`, `userns_mode: host`;
- a mount of `/var/run/docker.sock`, or of any host path outside the project (`volumes:` entries beginning with `/`, `~`, `..` or a drive letter); named volumes are fine;
- `build.context`, `env_file`, `extends` or `include` pointing outside the repository;
- a published port not bound to `127.0.0.1` (`"5432:5432"` exposes it to your network; use `"127.0.0.1:5432:5432"`);
- an image without an exact version tag (`latest` or none);
- a Dockerfile that downloads and runs a script (`curl ... | sh`), or `ADD` from a URL, unless you've agreed it;
- in a workflow: anything other than `permissions: contents: read`, a secret, or `pull_request_target`.

The checklist is for your review. The agents don't enforce it, and an agent can always edit the file it describes.

## 6. Why it's set up this way

- The sandbox's protection is that the agent can't control Docker and can't push. Option A keeps both. The routes above add Docker work without giving either away.
- Route 1 runs in GitHub's machines, not yours, with a read-only workflow token. That's why it is the default.
- Route 2 is the only place agent code runs on your host. It's limited to commands you can read, a separate project name, local-only ports and immediate cleanup.
- Cloud sessions (`_docs/cloud-sessions.md`) stay optional; nothing here depends on them.
