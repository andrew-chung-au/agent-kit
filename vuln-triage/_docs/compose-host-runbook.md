# Running the Compose jobs on a Docker host (owner-run)

Step by step for `make test-compose`, for the cases an agent can write but not run
(no Docker daemon in the cloud session). First needed for #233 (`P-DEMO-BE`). The
broader guide is `_docs/verify-locally.md` §7; the script is `ci/test-compose.sh`.

## 1. What the host needs

- **Docker with the Compose plugin and a running daemon.** `docker compose version`
  prints a version and `docker info` prints server details with no error. Docker
  Desktop, a Codespace or a Linux box with Docker all work.
- **git, make, Node and uv.** `make tool-versions` shows which are missing.
- **A separate clone**, not your clean review clone.
- **No `.env` and no secrets.** `ci/test-compose.sh` exports throwaway test values.
- **Free ports.** Nothing else may hold 8000, 3000, 4317, 8025, 9090, 9099 or 9100,
  or the database port. On 2026-10-26 VS Code held 9099 by auto-forwarding it: in
  the Ports panel stop forwarding it, and untick `remote.autoForwardPorts`.

## 2. Check the ports

For each port (change the number each time); it prints nothing and exits 0 when the
port is free:

```sh
docker run --rm -p 127.0.0.1:9099:9099 alpine true
```

"port is already allocated" or "ports are not available" means something else has
it. Free it first.

## 3. Get a clean copy

```sh
git clone https://github.com/andrew-chung-au/vuln-triage.git vuln-triage-compose
cd vuln-triage-compose
git checkout <the branch named in the issue or PR>
```

## 4. Install (one-off)

```sh
make install
```

The script refuses to run without `backend/.venv`.

## 5. Run the job

```sh
time make test-compose JOB=responder
```

- The first run builds images, so allow a few minutes before tests start.
- #233 runs the full loop twice: about 8 to 10 minutes a take, about 20 in all.
  Leave the terminal open.
- `time` gives the duration #233 asks for in the PR description (it sizes
  `timeout-minutes` in #161).
- A green run ends with a pytest line such as `N passed in ...`.

To keep a copy of the output:

```sh
make test-compose JOB=responder 2>&1 | tee compose-run.log
```

## 6. If it fails

- Keep the whole output; the log names the failing step.
- If a service did not start, before cleaning up (the script tears the stack down
  when it exits, so use `-p vt-responder` right after a failure, or rerun):
  `docker compose -p vt-responder ps`, then
  `docker compose -p vt-responder logs <service>`.
- A small fix on the first real run is expected: the external images' behaviour
  carries `VERIFY:` markers until a human has run them.
- Post the failing part on the issue (or paste it to the agent) with the commit
  you ran.

## 7. Clean up

```sh
docker compose -p vt-responder down --volumes --remove-orphans
```

The script already does this on exit; run it if the terminal was killed mid-run,
otherwise the ports stay taken.

## 8. What to record on the issue

- Pass or fail, and the pytest summary line.
- The measured duration from `time`.
- For #233: whether Grafana sent the `resolved` notification (one of its criteria).
- The commit SHA you ran (`git rev-parse --short HEAD`).
