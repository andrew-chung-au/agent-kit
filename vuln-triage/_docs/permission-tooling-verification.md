# Permission tooling verification (#271)

**Date:** 2026-10-29
**Scope:** the permission-tooling change tracked by issue #271: safe read-only allows, guarded issue writes, the five-group permission review, the optional cloud-session push module, and the top-level `agent-kit/` mirror.
**Commits:** `e174151` (settings and guarded Make targets), `8778092` (docs, guard and kit copy), `5f9cd61` (the unprotected mirror, this file and the session summary), and the post-QA fixes `5a0f256` (file-at SSH key names), `4a27b30` (`AGENTS.md` kit version), `b50207f` (Claude cloud-push ask rule) and `d9986ef` (all standard SSH key names).

## What was checked

- `make check-scripts`: PASS. Bash syntax for the kit scripts, hooks and `pre-push`; Python parse for the hooks and scripts; `jq empty` for `.claude/settings.json` and `opencode.json`.
- `make verify BASE=51bcf57`: PASS. 89 frontend tests, 563 backend tests (14 deselected), 1638 responder tests; frontend type check PASS; whitespace PASS; no test files changed.
- `.scratch/check-guard.sh`: the mirrored `guard_git.py` allowed `git push -u origin claude/test` only with `AGENT_KIT_CLOUD_PUSH=1`, `CLAUDE_CODE_REMOTE=true` and the checked-out `claude/test` branch. The other three cases exited 2: no module, module outside a cloud session, and a push form other than `-u origin <current branch>`.
- `make permission-report SINCE=9eb4071` and `SINCE=51bcf57`: ran read-only during the change; the five groups and the older three-group summaries were read, and the prompt log was read when present. No settings change was proposed from the counts.
- `make branches`, `make ci LIMIT=3`, `make file-at`, and the `make issue-comment` path: validated wrappers ran; `DRY_RUN=1` posted nothing; the secret scan refused a test body with a match; invalid `CONTAINS`, `LIMIT`, `REF`, `FILE`, dash-led and single-quote values were refused. Details and the comment links are in the approval records on #271.
- QA at `5f9cd61` (comment 6495904527): PASS on the issue's scope and decisions, with the same Verify result. It also ran the four guard cases, the guarded wrappers, the read-only helpers and `make permission-report`.

## Post-QA fixes

- `5a0f256`: the `file-at` secret-name filter now refuses bare `id_rsa`/`id_ed25519` and `keys/id_rsa` as well as the `.pem` and `.key` names. Three `make file-at` calls stopped at `Makefile:163`.
- `d9986ef`: the filter now refuses `id_dsa`/`id_ecdsa`, nested names and embedded names such as `my_id_rsa_backup`; it uses `findstring` because the old `%id_rsa%` pattern does not match under GNU make. Ordinary paths such as `.gitignore` and `README.md` still print. The check is case-sensitive, so non-standard `ID_RSA`/`id-rsa` names are a residual, low risk.
- `4a27b30`: `AGENTS.md` now says the kit is version 1.10, matching both READMEs.
- `b50207f`: the project `.claude/settings.json` now has `Bash(git push -u origin *)` in `ask`, the missing piece of the cloud-session fragment. Correction to the QA note: the project settings already used specific `main`, force and delete denies; the blanket `Bash(git push *)` deny QA saw is in the generic kit copy `_docs/agent-kit/claude-code/settings.json`, which stays no-push.
- `make verify BASE=5f9cd61`: PASS at `b50207f` (89 frontend, 563 backend with 14 deselected, 1638 responder; type check and whitespace PASS; no test files changed). Re-QA at `b50207f` (comment 6497370140) and at `d9986ef` (comment 6498104690): PASS.

## QA risks outside the scope

- `make file-at`'s secret-name filter missed a bare `id_rsa`/`id_ed25519` and `keys/id_rsa`; fixed in `5a0f256`. The same check now covers `id_dsa`/`id_ecdsa` and embedded names in `d9986ef`.
- `AGENTS.md` said the kit was version 1.9 while both READMEs say 1.10; fixed in `4a27b30`.
- The project `.claude/settings.json` set `AGENT_KIT_CLOUD_PUSH=1` without the fragment's push ask rule; fixed in `b50207f`.
- The Claude `make issue-close` ask rule depends on ask-over-allow precedence and was not verified live (#66).
- `make file-at REF=... FILE=.env` is blocked by the tool's `*.env*` deny rule before `make` runs; this is the tool rule, not the Makefile filter.
- The `file-at` key-name check is case-sensitive, so `ID_RSA` or `id-rsa` would still reach `git show`; non-standard names only.

## What is not checked

- A real `git push` from a Claude Code cloud session. The guard's four decision paths are checked against a scratch repository; no push, remote or cloud session was used.
- The live OpenCode prompt behaviour. OpenCode loads permission rules at session start, so the rules changed in `opencode.json` are not active in the session that wrote them. The human must restart OpenCode and check the rules in its permissions view.
- The top-level `agent-kit/` mirror is for comparison, not a second executable kit. It carries the permission docs, the guard, the settings, the cloud-session module and `scan-issue-body.sh`, but not `permission-report.py` or the earlier project-only differences in `check-staged.sh`, `verify.sh`, `pre-push`, `asking-the-human.md` and `verify.md`. It also keeps a generic `cloud_session_start.sh` (the project copy installs dependencies and hooks) and the older `environments.md` pre-push line. The project copy in `_docs/agent-kit/` is the one `make` targets run. The duplication remains tracked by #36 and #38.

## Human steps

1. Restart OpenCode so the new `opencode.json` rules load.
2. Read the settings and Makefile diff, then merge and push from the clean clone.
3. The next permission sweep runs `make permission-report SINCE=9eb4071` (sweep 1's baseline) and decides the recorded approvals; this issue's approvals are in its session summary.
