# Issue #112: Push check image with Node, uv, Python and the tools verify will need

**Date:** 2026-10-23
**Spec version:** 9b04f90

## What changed and why

The push check runs `make install verify` in a throwaway container. Since #74 `make install` also runs `uv sync --locked`, and the container image has no uv, so the push failed with exit 127 before `verify` ran. #32 had deferred the uv image to #24, which was closed as superseded, so nothing covered it. The human asked for an issue (filed as #112) and asked that the image carry everything the roadmaps will need, so it is not rebuilt per phase. The Engineer wrote `ci/push-check/Dockerfile`: `node:24.22.0-bookworm`, npm 11.19.1, uv 0.13.1, Python 3.12.15 installed under `/opt/python`, `openapi-spec-validator` 0.9.0 with a baked uv cache, `libpq-dev`, `pip-audit` 2.10.1 and Terraform 1.17.0 (checksum-verified; `fmt`/`validate` only). The image was NOT built or run in this container (no Docker). The human later built it, ran the plan-mode dry run (it printed `make -C . install verify`), the real push and the broken-install check, and reported that these "all worked fine" (recorded in comment 6359182138). No command output was pasted, so the tool versions, image size and offline `uvx` result are not recorded. #112 was closed on that statement.

## Files created or modified

- `ci/push-check/Dockerfile` (`83260c0`)
- `AGENTS.md` Project gotchas line (`9902d07`, protected; approval record 6356988788)
- `_docs/ai-usage-log.md` (`36ec2b7` Engineer; orchestrator entry in the close-out commit)
- `_docs/roadmap.md` check-in

## Decisions made by the human

- Custom image set through `AGENT_PUSH_CHECK_IMAGE`; Python baked in; Dockerfile in the repo at `ci/push-check/`; scheduled right after #26.
- Include all four extra tools now (`openapi-spec-validator`, `libpq-dev`, `pip-audit`, Terraform fmt/validate); the human approved `pip-audit` and the Terraform install for the image only.
- Approved the `AGENTS.md` gotcha text (committed alone with `HUMAN_APPROVED=1`).
- Keep #112 open until the human builds the image and reports.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (QA: PASS WITH WARNINGS; 62 frontend + 56 backend tests; the "test fixtures changed" warning comes from earlier issues, not #112)
- Human steps (QA comment 6357004988 lists 15 exact commands): `docker build -t vulntriage-push-check:1 ci/push-check`, the `--version` checks, the offline `uvx` run, `docker image ls`, `AGENT_PUSH_CHECK_PLAN=1 git push`, a real push, and the throwaway commit that deletes `backend/uv.lock`.

## Proposed AGENTS.md changes

Applied at the decision point and committed as `9902d07`. None outstanding.

## Temporary changes

none. No Docker or system change was made; `.scratch/` is removed by `make clean-scratch`.

## Permission review

- Read-only (propose allowing): web fetches of version and checksum sources (Engineer, QA; network reads, not prompted). `make issue-dump N=112` (Engineer, QA; ask rule).
- Writes to the record (keep asking): `make issue-comment N=112 ...` (PM, Engineer, QA, orchestrator; posts to the tracker); `gh issue create` for #112 (PM; merits request, filing approved by the human); `HUMAN_APPROVED=1 git commit` for `AGENTS.md` (orchestrator; protected file).
- Risky (propose denying): none.

The Engineer and QA comments state no approvals needed; the PM's filing commands are the orchestrator's account of the PM task.

## Interruptions

none

## Unrelated problems noticed but not fixed

- Build risks recorded by QA, outside the criteria: `COPY --from=ghcr.io/astral-sh/uv:0.13.1` may not exist (fallback: the release tarball with its checksum); the `uv python find 3.12.15` symlink step; the offline `uvx` check may still reach the network; the container runs as root; the 2 GB size budget is untested.

## Follow-ups for the next session

- The human builds the image and runs the checks; if the build fails, the Engineer fixes the Dockerfile, then QA re-checks only what changed. Then close #112.
- Next in S1 per the roadmap: #76 (task 4).
