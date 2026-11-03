# Add Node.js and uv to the dev container, with an optional Compose services variant

## Context

`devcontainer-test` is the base dev container for agent-driven projects. It
currently ships Python 3.12, `github-cli`, `make`, OpenCode and Claude, but no
Node/npm or uv. A Python + React project cannot run `make install` (frontend
`npm ci`, backend `uv sync`) or its tests without them.

A sibling Postgres service is also useful for integration tests, but it should
not give the agent Docker control. The safe pattern is a Compose recipe with an
`app` and `db` service, no Docker socket, where the agent reaches `db` by
hostname and the human controls the stack.

## Proposed changes

1. Pin the Node feature in `.devcontainer/devcontainer.json`:
   `24.22.0`, nvm `0.40.8`, `pnpmVersion: "none"`.
2. In `.devcontainer/setup.sh`:
   - install `uv==0.13.1` with `pipx`;
   - pin the Node bin directory for non-interactive setup;
   - run `corepack disable` so the feature's yarn/pnpm shims do not surprise
     projects.
3. Add the Node feature entry to `.devcontainer/devcontainer-lock.json`.
4. Add `actions/setup-node` and `astral-sh/setup-uv` to
   `.github/workflows/verify.yml`, so `make install` works in CI as well as in
   the container.
5. Optional: add the Compose `app` + `db` variant from the feedback bundle. It
   keeps the same image, adds a pinned `postgres:16.4` sibling, mounts only the
   workspace, and does not mount the Docker socket.

Exact files are in the accompanying feedback bundle. The key diffs:

```diff
--- a/.devcontainer/devcontainer.json
+++ b/.devcontainer/devcontainer.json
@@
-  "features": { "ghcr.io/devcontainers/features/github-cli:1": {} },
+  "features": {
+    "ghcr.io/devcontainers/features/github-cli:1": {},
+    "ghcr.io/devcontainers/features/node:2": {
+      "version": "24.22.0",
+      "nvmVersion": "0.40.8",
+      "pnpmVersion": "none"
+    }
+  },
```

```diff
--- a/.devcontainer/setup.sh
+++ b/.devcontainer/setup.sh
@@
 command -v opencode >/dev/null || curl -fsSL https://opencode.ai/install | bash
 command -v claude >/dev/null || curl -fsSL https://claude.ai/install.sh | bash

+pipx install uv==0.13.1
+export PATH="/usr/local/share/nvm/versions/node/v24.22.0/bin:$PATH"
+corepack disable
+
 git config --global user.name "Andrew Chung"
```

## Acceptance criteria

- [ ] After a rebuild, `node --version` prints `v24.22.0`, `npm --version`
      reports `11.19.1`, and `uv --version` reports `0.13.1`.
- [ ] `make install` succeeds for a project with a frontend and a Python
      backend.
- [ ] `corepack` no longer exposes yarn/pnpm shims (or the project documents
      why it keeps them).
- [ ] `.devcontainer/devcontainer-lock.json` contains the Node feature entry.
- [ ] CI runs `make install` and `make verify` with the same Node/uv pins.
- [ ] Optional Compose variant: `docker compose config` passes, the `db`
      service is healthy, the app reaches it at `db:5432`, and no Docker socket
      is mounted.
- [ ] No project-specific credentials or repository names are in the generic
      files.

## Out of scope

- Docker-in-Docker or mounting the host Docker socket. The agent should not
  control Docker.
- A specific database schema, ORM or migration setup.
- Changing the agent kit's reference recipe; that is a separate change.

## Evidence

- VulnTriage #20 (Node.js and uv), #32 (nvm pin and corepack), #31 (Compose
  dev container).
- Files: `.devcontainer/devcontainer.json`, `.devcontainer/setup.sh`,
  `.devcontainer/devcontainer-lock.json`, `.devcontainer/Dockerfile`,
  `.devcontainer/compose.yaml`, `.github/workflows/verify.yml`.
- `_docs/reviews/2026-10-18-frontend-comparison.md` (F0) and
  `_docs/agent-kit/environments.md` (local sandbox rules).

## Verification

1. Rebuild the dev container.
2. Run `node --version`, `npm --version`, `uv --version`.
3. Run `make install` and `make verify` in a frontend/backend project.
4. For the Compose variant, run `docker compose config` on the host, rebuild,
   and check `pg_isready` from the `app` service.
5. Confirm `docker` is still unavailable to the agent inside the container.

## Rollback

Revert the `.devcontainer/`, `.github/workflows/verify.yml` and lockfile
changes, then rebuild. The optional Compose variant adds a `pgdata` volume; the
human can remove it from the host if a clean slate is wanted.
