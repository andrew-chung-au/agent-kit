# Put a key-injecting proxy beside the container for the Antigravity checks

## Purpose

**Status (2026-11-21): not run.** Give the dev container a way to reach Gemini without the key ever being inside it: a Caddy container joins the dev container's network namespace and adds the `x-goog-api-key` header in flight, so the container is told only a dummy key and `127.0.0.1:8787`. This is the setup step for `2026-11-21T1524Z-human-task-engineer-antigravity-live-checks.md`; run this one first, or that task stops at its step 3. Issue: none.

The proxy has to be a container here. This dev container runs under Docker Desktop, so it sits in the Docker Desktop VM (`172.17.0.2`, gateway `172.17.0.1`) and `host.docker.internal` points at Windows (`192.168.65.254`), not at the WSL distro; a process in WSL is in a third network namespace that nothing in the VM can route to. A sibling container is the only place the dev container can reach that does not put the key inside it.

## Where to run it

A WSL shell where `docker` reaches Docker Desktop, for steps 1 to 3; the dev container's own terminal for step 4. Press Ctrl-C first in the terminal that is still running `caddy run` from the earlier attempt: that process is replaced by the container, and the `~/bin/caddy` binary is no longer used.

Not here: a CodeBuddy or Claude Code session, in either place. The key is typed into a WSL shell once, and an agent must never be the thing that types it.

## Before you start

1. Find the dev container's name, which step 2 needs.

```
docker ps --format '{{.Names}}'
```

Expected: one name per running container, one of them for this workspace. Write that name down. If different: if the list is empty, the dev container is not running; start it and repeat.

2. Confirm the config from the earlier attempt is still there.

```
ls ~/gemini-proxy.Caddyfile
```

Expected: the path, printed back. If different: if it is missing, write it again with the `printf` line from that attempt and check it with `~/bin/caddy validate`; the file must exist before step 2.

## Steps

### Step 1: Put the key in this shell

```
export GEMINI_KEY=<your key>
```

Expected: no output. Replace `<your key>` with the real key; it stays in this shell's environment, and step 2 passes it to the proxy container only.
If different: if the shell rejects the line, the key holds a character the shell treats specially; wrap the value in single quotes and run it again.

### Step 2: Start the proxy beside the dev container

```
docker run -d --name gemini-proxy --network container:<name> -e GEMINI_KEY -v ~/gemini-proxy.Caddyfile:/etc/caddy/Caddyfile:ro caddy
```

Expected: one long container id, and on the first run a short `Unable to find image ... locally` followed by the pull. Replace `<name>` with the name from the pre-check; the `container:` form puts the proxy in the dev container's network namespace, so it listens on `127.0.0.1:8787` there and nowhere else.
If different: `No such container` means the name in `container:` is wrong or that container stopped; `invalid reference format` means the `-v` path was mangled; a mount error mentioning the file means Docker cannot read it from WSL, and that is worth recording before trying another way.

### Step 3: Confirm the proxy is serving

```
docker logs gemini-proxy
```

Expected: a few JSON log lines ending with `serving initial configuration`.
If different: if the last line is a `run:` error naming `GEMINI_KEY` or the config, step 1 or the config file is wrong; record the last three lines and stop.

### Step 4: One request through it from the dev container

Run this in the dev container's terminal.

```
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8787/v1beta/models
```

Expected: `200`, which means the dev container reached the proxy, the proxy reached Google, and the key was accepted; write the number in the record.
If different: `401` or `403` means the proxy is up but the key is missing or wrong; stop and tell the orchestrator, and never paste the key. `connection refused` means the proxy container is not in this network namespace; repeat the pre-check and step 2. `command not found` means `curl` is absent from the container; record that and stop.

## Record the result

**Status (2026-11-21): not run.** Fill the table and commit this file with the result. Results contain no secrets either: the status code, not the response body.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |

## Risk

The real key sits in this shell's environment and in the proxy container's environment; it is never written to a file, never printed, and never enters the dev container. The two containers share a network namespace but not a process namespace, so the agent can send requests through the proxy and cannot read the proxy's environment; the dev container has no Docker socket, so it cannot inspect the proxy container either. Reaching the proxy is still a capability: anything in the dev container can spend quota through it, which is the point. Undo: `docker rm -f gemini-proxy` stops and removes the proxy; the `~/bin/caddy` binary and `~/gemini-proxy.Caddyfile` from the earlier attempt are then unused and can be deleted. No file in this repository changes.
