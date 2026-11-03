# Reference image for the push check (see environments.md, "The push-check image").
# The push check runs `make install verify` in a throwaway container. The default
# image, python:3.12, has git and make but no Node and no uv, so a Node plus uv
# project's `make install` fails there with exit 127. This image adds both, at the
# same pins as the dev container recipe (devcontainer.json and setup.sh).
#
# You build it on your own machine, from a copy taken from a clean clone, never
# from a sandbox, and point the push check at it:
#   docker build -t agent-push-check:node24-uv0.13.6 - < push-check.Dockerfile
#   export AGENT_PUSH_CHECK_IMAGE=agent-push-check:node24-uv0.13.6
# Building from standard input gives docker no build context, so nothing from a
# folder can be copied in. Nothing here is built or published by this repo.
#
# Holds no credentials, tokens, kit scripts or project files. The only COPY
# sources are published images, pinned by tag. A project adds its own extras
# (Terraform, pip-audit, libpq-dev) to its own copy of this file.
#
# All pins are UNVERIFIED until you have built the image and read the output of
# the version checks below. Node and uv must equal the recipe's pins; a test
# fails when they differ. npm is the one that ships with that Node.

# Base: the python:3.12 line the default image uses, pinned to one Debian release
# so the Node image below matches it. Unverified tag.
FROM python:3.12-bookworm

# Node, from the official Node image at the recipe's version (unverified tag).
# Copying the binary and its modules, not the whole /usr/local, so Python's files
# are untouched. npm and npx are links, as in the Node image.
COPY --from=node:24.22.0-bookworm-slim /usr/local/bin/node /usr/local/bin/node
COPY --from=node:24.22.0-bookworm-slim /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

# uv, from Astral's published image at the recipe's version (unverified tag).
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /uvx /usr/local/bin/

# The build fails if a tool the push check needs is missing.
RUN bash --version | head -n 1 && git --version && make --version | head -n 1 \
 && python3 --version && node --version && npm --version && uv --version
