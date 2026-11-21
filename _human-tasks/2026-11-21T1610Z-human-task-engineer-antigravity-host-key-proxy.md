# Put a key-injecting proxy beside the container for the Antigravity checks

## Purpose

**Status (2026-11-21): done, all four steps passed.** Give the dev container a way to reach Gemini without the key ever being inside it: a Caddy container joins the dev container's network namespace and adds the `x-goog-api-key` header in flight, so the container is told only a dummy key and `127.0.0.1:8787`. This was the setup step for the API-key path in `2026-11-21T1524Z-human-task-engineer-antigravity-live-checks.md`; it turned out not to be needed, because the CLI runs on the Antigravity starter quota with no credential at all. It stays as the recorded answer for anyone who does use an API key. Issue: none.

The proxy has to be a container here. This dev container runs under Docker Desktop, so it sits in the Docker Desktop VM (`172.17.0.2`, gateway `172.17.0.1`) and `host.docker.internal` points at Windows (`192.168.65.254`), not at the WSL distro; a process in WSL is in a third network namespace that nothing in the VM can route to. A sibling container is the only place the dev container can reach that does not put the key inside it.

## Where to run it

One command in the dev container for pre-check 1, a WSL shell where `docker` reaches Docker Desktop for pre-check 2 and steps 1 to 3, and the dev container's own terminal again for step 4. Press Ctrl-C first in the terminal that is still running `caddy run` from the earlier attempt: that process is replaced by the container, and the `~/bin/caddy` binary is no longer used.

Not here: a CodeBuddy or Claude Code session, in either place. The key is typed into a WSL shell once, and an agent must never be the thing that types it.

## Before you start

1. In the dev container, read its container id, which pre-check 2 matches against.

```
hostname
```

Expected: twelve hex characters. Write them down. If different: if it is a word rather than hex, this is not the container the recipe built; stop.

2. In the WSL shell, find that container's name, which step 2 needs.

```
docker ps --format '{{.Names}} {{.ID}}'
```

Expected: one line per running container, and one of them carries the id from pre-check 1; the name on that line is the one step 2 uses. Write it down. If different: if no line carries that id, this `docker` is talking to a different engine than the one running the dev container; stop and report that.

3. Confirm the config from the earlier attempt is still there.

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
docker run -d --name gemini-proxy --network container:devcontainer -e GEMINI_KEY -v ~/gemini-proxy.Caddyfile:/etc/caddy/Caddyfile:ro caddy
```

Expected: one long container id, and on the first run a short `Unable to find image ... locally` followed by the pull. Replace `devcontainer` with the name from pre-check 2, as a plain word: an angle bracket in that position is read by the shell as a redirect, which is why it must not be used. The `container:` form puts the proxy in the dev container's network namespace, so it listens on `127.0.0.1:8787` there and nowhere else.
If different: `No such container: devcontainer` means the name was not replaced, or that container stopped; `invalid reference format` means the `-v` path was mangled; a mount error mentioning the file means Docker cannot read it from WSL, and that is worth recording before trying another way.

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

**Status (2026-11-21): run, all four steps passed.** Run by the repository owner in the WSL shell and this dev container. Results contain no secrets: the status code, not the response body.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | pass | no output; the variable was still exported from the earlier attempt |
| 2 | pass | pulled `caddy:latest` (`sha256:4851e54a…`), started `551cdc1e9762…` on `--network container:happy_cori` |
| 3 | pass | last line `serving initial configuration`, `addr: ":8787"` |
| 4 | pass | `200` from `http://127.0.0.1:8787/v1beta/models` |

The pre-checks also passed: `hostname` printed the id that `docker ps` matched to `happy_cori`, and `~/gemini-proxy.Caddyfile` was present from the earlier attempt. Two failures came first and are worth keeping: `--network container:<name>` was read by bash as a redirect, which is why the step now uses a plain word, and the earlier host-side Caddy in WSL was unreachable from this container at both `host.docker.internal` and `172.17.0.1`, which is why the proxy is a container.

## Risk

The real key sits in this shell's environment and in the proxy container's environment; it is never written to a file, never printed, and never enters the dev container. The two containers share a network namespace but not a process namespace, so the agent can send requests through the proxy and cannot read the proxy's environment; the dev container has no Docker socket, so it cannot inspect the proxy container either. Reaching the proxy is still a capability: anything in the dev container can spend quota through it, which is the point. Undo: `docker rm -f gemini-proxy` stops and removes the proxy; the `~/bin/caddy` binary and `~/gemini-proxy.Caddyfile` from the earlier attempt are then unused and can be deleted. No file in this repository changes.
