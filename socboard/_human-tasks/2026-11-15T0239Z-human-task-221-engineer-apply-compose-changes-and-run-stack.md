# Apply the protected Compose changes and run the stack once

## Purpose

Apply the three protected-file changes that #221 needs, and run `make compose-up` once where Docker exists. Issue: #221.

## Where to run it

The clean clone, on the branch `issue-221-compose-stack` (steps 1 and 2), and a machine with Docker and a browser (step 3). Not here: the agent's sandbox, which has no Docker. The agent never edits `Makefile`, `AGENTS.md` or `.github/`.

## Before you start

1. Check that the branch is checked out and the three proposed files are in the folder.

```
ls _human-tasks/221-proposed
```

Expected: `agents.diff`, `compose.yml` and `makefile.diff`.

## Steps

### Step 1: apply the `Makefile` and `AGENTS.md` diffs

Read both diffs first. The `Makefile` diff adds the targets `compose-up` and `compose-down` at the end; the `AGENTS.md` diff adds the two Commands lines and names `compose.yaml` and `compose/` in the Layout line.

```
git apply --unidiff-zero _human-tasks/221-proposed/makefile.diff _human-tasks/221-proposed/agents.diff
```

Expected: no output; `git status --short` shows `Makefile` and `AGENTS.md` modified.
If different: stop and tell the orchestrator what was printed (the branch may have moved).

### Step 2: add the workflow and remove the proposals

```
git mv _human-tasks/221-proposed/compose.yml .github/workflows/compose.yml
git rm -r --quiet _human-tasks/221-proposed
```

Commit the four paths with `HUMAN_APPROVED=1` (they are protected) and push. The orchestrator then reads the `socboard compose` run on the pull request's head commit.

Expected: the job passes. It checks the health route through the proxy (port 8080) and on the app's own port (8000), that the application role is neither a superuser nor the owner of `audit_entries`, that it is refused `ALTER TABLE audit_entries DISABLE TRIGGER ALL`, that the four audit triggers are enabled, that the app has no superuser password, that a second start succeeds with the three seeded users unchanged, and that `make compose-down` keeps the data volume.
If different: send the failing step's name and log lines to the orchestrator.

### Step 3: one run on a machine with Docker

```
make compose-up
```

Expected: the images build, the one-shot steps exit 0, the command returns once the app is healthy, and it printed names but no value. Open http://127.0.0.1:8080/ in a browser: the entry page loads and the Lead can sign in. The password is the value of `SOCBOARD_SEED_PASSWORD_LEAD` in `compose.secrets`: open that file yourself, and never paste it anywhere. Then:

```
make compose-down
```

Expected: containers and network removed. The data volume `socboard_socboard-pgdata` is still listed by `docker volume ls`.
If different: send the last lines of `docker compose logs` (they hold no secret) to the orchestrator.
Risk: none to anything outside the project's own containers and volume. Starting over means `docker volume rm socboard_socboard-pgdata` and deleting `compose.secrets`, and that deletes the stack's data; do it only when you mean to.

### Step 4 (after D17c): the bind-mount case

With `STACK_PGDATA_DIR` set to an absolute path owned by uid 999 and holding a `lost+found` folder, `make compose-up` starts and Postgres writes `pgdata` under it. D17c does this on the real volume; nothing here can.

## Record the result

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |

## Risk

Step 2 adds a workflow that runs on every push and pull request; it uses `contents: read` and no repository secret, and it creates throwaway secrets inside the runner.
