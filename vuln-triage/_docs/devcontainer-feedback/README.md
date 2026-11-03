# Devcontainer feedback bundle

One-off feedback from VulnTriage to `devcontainer-test`, the upstream dev
container project. This is not part of the agent kit and does not change
VulnTriage's own `.devcontainer/`.

## Why

VulnTriage is a Python/FastAPI backend with a React/Vite frontend and a
Postgres-backed Compose stack. The upstream recipe is a single Python 3.12
image with `github-cli`, `make`, OpenCode and Claude. Building VulnTriage in it
needed Node/npm, uv, a reliable non-interactive Node PATH, and a way to reach a
sibling Postgres service. This bundle carries the generic parts of what this
project added, plus the Compose variant as a separate option.

## Source

- #20: pinned Node.js `24.22.0` and uv `0.13.1`.
- #32: pinned nvm `0.40.8` and disabled corepack's yarn/pnpm shims.
- #31: Compose-based dev container with a Postgres sibling (project-specific).
- Files: `.devcontainer/devcontainer.json`, `.devcontainer/setup.sh`,
  `.devcontainer/devcontainer-lock.json`, `.devcontainer/Dockerfile`,
  `.devcontainer/compose.yaml`, `.github/workflows/verify.yml`.

## What is in the bundle

| Path | Apply to | Notes |
|---|---|---|
| `files/devcontainer.json` | `.devcontainer/devcontainer.json` | Base recipe plus pinned Node feature. |
| `files/setup.sh` | `.devcontainer/setup.sh` | Adds uv, the Node PATH pin and `corepack disable`. |
| `files/devcontainer-lock.json` | `.devcontainer/devcontainer-lock.json` | Adds the Node feature entry. |
| `files/verify.yml` | `.github/workflows/verify.yml` | Adds `setup-node` and `setup-uv` so `make install` works in CI. |
| `files/optional-compose/` | optional | Compose `app` + `db` variant; no Docker socket. |

The generic files keep the upstream image, mounts, environment and
`postCreateCommand` unchanged. They add only the Node/uv fixes.

## How to apply

1. Create the issue from `issue.md` in `devcontainer-test`.
2. Review the files in `files/` against the upstream `.devcontainer/`.
3. Copy the three generic files into `devcontainer-test/.devcontainer/` and the
   CI file into `.github/workflows/`.
4. Rebuild the dev container, then run the checks in `issue.md`.
5. If the project needs a sibling service, copy `files/optional-compose/` and
   replace `<repo>`, the database name and the credentials. Use its
   `devcontainer.json` instead of the generic one; the generic `setup.sh` and
   `devcontainer-lock.json` still apply.
6. Delete this bundle, or keep it as the record of the change.

## Generic vs project-specific

- **Generic:** Node feature pins, uv pin, Node PATH pin, corepack disable,
  lockfile entry, CI tool setup.
- **Optional, not generic:** Compose, Postgres, `DATABASE_URL`, workspace folder
  and database credentials. These are examples from VulnTriage, not defaults.

## Verification limits

This bundle was written in VulnTriage's container, which has no Docker CLI and
cannot rebuild `devcontainer-test`. The JSON files were checked with `jq` and
`setup.sh` with `bash -n`; the container checks are for the human after rebuild.
