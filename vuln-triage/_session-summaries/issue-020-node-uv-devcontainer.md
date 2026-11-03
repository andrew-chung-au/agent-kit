# Issue #020: Dev container: Node.js and uv available to agents (blocks #15 part E2)

**Date:** 2026-10-18
**Spec version:** d3a8f11

## What changed and why

- Session check: no `_docs/specs.md` commits since the last summary's version (`d3a8f11`), so no backlog review was needed.
- PM groomed #20 (its first grooming) and pinned the previously-open values. It found the filer's example feature id `node:1` was stale (current major is `node:2`), that Node 20 is EOL so it can't be the "LTS line" criterion 1 wants, and that the lockfile behaviour was open.
- The human answered four grooming decisions in-session; the PM applied the approved body edits to #20 and filed the Docker/Compose follow-up #31, linked from #20's out-of-scope.
- The Engineer implemented the recipe and stopped before the `.devcontainer/` commit: the pre-commit hook gates `.devcontainer/` behind `HUMAN_APPROVED=1`. The change is staged in the working tree, uncommitted.
- The Engineer could not regenerate `.devcontainer/devcontainer-lock.json`: this container has no devcontainer CLI (nor node/npx/docker). Raised as a decision question instead of committing a stale digest.
- Mid-session, on a direct human instruction (no issue), the Orchestrator added a `make tool-versions` target (node, npm, uv, python3, docker, or `<tool>: missing`) and a "Tool versions" line in AGENTS.md's Commands section. Committed in its own protected commit, which also carried the human's pre-existing AGENTS.md Project-rules edits.
- Post-rebuild (continuation, same issue): the human ran the `.devcontainer/` commit (`4eb0485`) and rebuilt. `make tool-versions` then printed node `v24.22.0`, npm `11.19.1`, uv `0.13.1`, python3 `3.12.15`, docker `missing`.
- The regenerated `.devcontainer/devcontainer-lock.json` was inspected against the agreed check (only the `node:2` entry added, `github-cli` unchanged) and committed as `f3ed87d` after the human approved.
- The Engineer ran the post-rebuild runtime checks, posted its #20 comment (6249655264) and logged it (`abaed5d`). QA checked every criterion and posted PASS (6249711806) at `abaed5d`.
- Decision point: the human approved the AGENTS.md Environment line, committed as `a90d182` with `HUMAN_APPROVED=1`, and confirmed the `opencode.json` change bundled into `4eb0485` was intended (no action). The issue was closed.

## Files created or modified

- `.devcontainer/devcontainer.json` (uncommitted, working tree): adds `"ghcr.io/devcontainers/features/node:2": { "version": "24.22.0", "pnpmVersion": "none" }`; removes the duplicate `remoteEnv.PATH`, keeping `${containerEnv:PATH}:/home/vscode/.local/bin:/home/vscode/.opencode/bin`.
- `.devcontainer/setup.sh` (uncommitted, working tree): adds `pipx install uv==0.13.1`.
- `AGENTS.md` (protected): proposed Environment-line change, not edited, not committed (below).
- GitHub: #20 body edited to the groomed text; PM comment 6247960494 (grooming) and 6248923707 (decisions applied); new issue #31.
- `.scratch/` (git-ignored): `issue-20-check.py`, `issue-20-tooling.sh`, `issue-20-pipx-writable.py`, and the PM's drafts. Kept for the post-rebuild work.
- `Makefile` (protected): new `tool-versions` target. `AGENTS.md` (protected): Commands "Tool versions" line; committed with the human's pre-existing Project-rules edits.
- Post-rebuild commits: `.devcontainer/devcontainer.json` + `.devcontainer/setup.sh` (`4eb0485`, the human); `.devcontainer/devcontainer-lock.json` (`f3ed87d`, HUMAN_APPROVED); `_docs/ai-usage-log.md` (`abaed5d`, Engineer; `20c0944`, QA); `AGENTS.md` Environment line (`a90d182`, HUMAN_APPROVED). Note: `4eb0485` also carried an intended `opencode.json` permission change (outside #20's Constraints; human confirmed at the decision point; it drops the file's trailing newline).
- This summary.

## Decisions made by the human

- Node pin `24.22.0` (Active LTS; option 1 of 3).
- uv installed with `pipx install uv==0.13.1` in `setup.sh` (option 1; no third-party feature).
- File the Docker/Compose follow-up now: #31.
- Apply the PM's proposed body edits to #20 as drafted.
- The human runs the `.devcontainer/` commit commands themselves (keeps `HUMAN_APPROVED=1` with the human), then rebuilds.
- Approved committing the `tool-versions` change (`Makefile` + `AGENTS.md`) with `HUMAN_APPROVED=1`, including the pre-existing AGENTS.md Project-rules edits.
- Lockfile (criterion 4): option 1 with checks — after the rebuild, show the `devcontainer-lock.json` diff before committing; it must add only the new feature entries with their versions and digests and leave `github-cli` unchanged. If the rebuild did not update it, stop and tell the human, who will regenerate it with the devcontainer CLI on their machine (option 2).
- Post-rebuild decision point: approved committing the lockfile (`f3ed87d`) after seeing the diff; approved applying the AGENTS.md Environment line with `HUMAN_APPROVED=1` (`a90d182`); confirmed the `opencode.json` permission change bundled into `4eb0485` was intended (kept as committed).

## Mismatches with the spec or design docs

- None. `_docs/specs.md` does not cover toolchain versions; this is infrastructure that makes the lockfiles named in US-2 producible.

## Commands to validate

- **Verify:** `make verify BASE=dc843de` and `make verify` — PASS WITH WARNINGS, the only warning being the no-`TEST_CMD` one (project still in planning, no code).
- Static check: `python3 .scratch/issue-20-check.py` — all criteria PASS on the working-tree diff, including the refused-case patterns.
- Runtime (after the rebuild, run by the Engineer and re-run by QA): `node --version` → `v24.22.0`, `npm --version` → `11.19.1`, `uv --version` → `uv 0.13.1 (x86_64-unknown-linux-gnu)`; all three resolve in a non-interactive `sh -c` and via `make tool-versions`. QA PASS at `abaed5d` (comment 6249711806).

## Proposed AGENTS.md changes

One line, protected, approved and applied at the decision point (`a90d182`, `HUMAN_APPROVED=1`):

```
- **Environment:** local sandbox (dev container; no Docker). The recipe installs Node.js `24.22.0` and uv `0.13.1`. GitHub token: read-only code (you can't push); read and write issues (you can post comments and close issues). See `_docs/agent-kit/environments.md`.
```

## Temporary changes

None by the agent. The Engineer installed nothing and started nothing. The `.devcontainer/` change is a system change the human applies: they run the commit and then rebuild the container. Undo: revert the commit and rebuild.

## Interruptions

None. The Engineer stopped on purpose before the gated commit and returned an approval request plus the lockfile decision question (relayed to the human).

## Unrelated problems noticed but not fixed

- The issue's own example feature id `node:1` was stale (current `node:2`); corrected in the applied body.
- #31 was filed without a priority/blocked label because the repo has no such labels; its status lives in the title and body.

## Follow-ups for the next session

- All #20 tasks are done and the issue is closed; nothing left here.
- Next: #15 part E2 (install, run, test). Start with `node --version` / `npm --version`, then `npm install --before=2026-10-18` in `frontend/`, add the `frontend-install`/`frontend-start`/`frontend-stop`/`frontend-test` targets, point `TEST_CMD` and the AGENTS.md Install/Run/Test lines at the all-tests target (protected, `HUMAN_APPROVED=1` at the decision point), run the tests, and re-run the secrets scan after `package-lock.json`.
- `make clean-scratch` was **not** run: #15 is still open and its `.scratch/` E1 scan and fixture scripts are reused by E2 QA. Run it when #15 closes.
