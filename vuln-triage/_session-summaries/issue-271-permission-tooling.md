# Issue #271: permission tooling

**Date:** 2026-10-29
**Spec version:** 0158517

## What changed and why

- `opencode.json` and `.claude/settings.json` now allow safe read-only commands, guard issue comments and creation through `make`, keep issue edits and closes on ask, deny `.env` edits, and match each other on the guarded paths.
- The `Makefile` has guarded `issue-comment` and `issue-create` targets, read-only `branches`, `ci`, `ci-run` and `file-at` helpers, and `check-scripts`; the issue-body path checks size, secrets and symlinks.
- The permission review uses five groups; routine issue writes are already allowed and are not sweep candidates. Approval records are posted after each protected commit.
- The optional `claude-code/cloud-session/` module lets a cloud session push only its current `claude/*` branch when `AGENT_KIT_CLOUD_PUSH=1` and `CLAUDE_CODE_REMOTE=true`; the core kit remains no-push.
- The top-level `agent-kit/` mirror carries the permission docs, guard, settings, cloud module and `scan-issue-body.sh`; `_docs/permission-tooling-verification.md` records what was and was not checked.
- QA PASS at `5f9cd61` (comment 6495904527) for the issue's scope and decisions; it re-ran Verify and listed six risks outside the scope.
- The human then chose to fix the actionable QA risks: `5a0f256` adds bare and nested SSH private-key names to the `file-at` filter, `4a27b30` updates `AGENTS.md` to kit 1.10, and `b50207f` adds the cloud-push ask rule to the project Claude settings. `make verify BASE=5f9cd61` PASS at `b50207f`; re-QA PASS at `b50207f` (comment 6497370140).
- Re-QA found the filter still missed `id_dsa`, `id_ecdsa` and embedded names; the human chose to extend it. `d9986ef` replaces the ineffective `%id_rsa%` patterns with a `findstring` check for all four standard names. Re-QA PASS at `d9986ef` (comment 6498104690), with only the non-standard case-sensitive names (`ID_RSA`, `id-rsa`) left as a residual.

## Files created or modified

Protected, committed with `HUMAN_APPROVED=1`:

- `e174151`: `opencode.json`, `.claude/settings.json`, `Makefile`, `_docs/agent-kit/scripts/scan-issue-body.sh` (new).
- `8778092`: `AGENTS.md`, `_docs/agent-kit/README.md`, `process.md`, `team/*.md`, `procedures/permission-sweep.md`, `procedures/session-summary.md`, `templates/AGENTS.md.template`, `templates/Makefile.mk`, `templates/session-summary.md`, `claude-code/START.md`, `claude-code/settings.json`, `claude-code/hooks/guard_git.py`, `claude-code/cloud-session/README.md` (new), `claude-code/cloud-session/settings.fragment.json` (new), `environments.md`, `opencode/opencode.json`, `scripts/permission-report.py`.
- `5a0f256`: `Makefile` (the `file-at` secret-name filter).
- `4a27b30`: `AGENTS.md` (kit version 1.10).
- `b50207f`: `.claude/settings.json` (cloud-push ask rule).
- `d9986ef`: `Makefile` (all standard SSH key names and embedded names).

Unprotected, in the mirror commit:

- `agent-kit/**` (mirror of the permission changes), `_docs/permission-tooling-verification.md` (new), `_docs/permission-sweeps.md`, `_docs/pending-verification.md`, `_docs/ai-usage-log.md`, `_docs/roadmap.md`, this summary.

## Decisions made by the human

- Approved the plan and each protected diff ("Approve and commit").
- Issue comments and creation are routine; editing and closing stay on ask.
- Cloud push is an opt-in module, not a core permission; the project enables it for cloud sessions through the guard.
- The top-level kit mirror is for comparison, not a resolution of #36/#38.
- Post-QA: fix the `file-at` SSH-key filter, bump `AGENTS.md` to 1.10, enable the cloud-push ask rule fully, and close after the fixes and re-QA.
- After re-QA found `id_dsa`/`id_ecdsa` and embedded names: extend the filter now rather than accept the residual.

## Mismatches with the spec or design docs

None.

## Commands to validate

**Verify:** `make verify BASE=51bcf57`, then `make verify BASE=5f9cd61` for the post-QA fixes
**Check scripts:** `make check-scripts`
**Guard check:** `bash .scratch/check-guard.sh`
**Permission report:** `make permission-report SINCE=9eb4071`
**File-at filter:** `make file-at` refused `id_rsa`, `keys/id_rsa`, `id_ed25519`, `id_dsa`, `keys/id_ecdsa`, `my_id_rsa_backup`, `my_id_ed25519_backup`, `server.pem` and `server.key`; `.gitignore` and `README.md` printed
**QA:** PASS at `5f9cd61` (6495904527), re-QA PASS at `b50207f` (6497370140) and at `d9986ef` (6498104690)

## Proposed AGENTS.md changes

None; the approved changes are in `8778092`.

## Temporary changes

- `make install` installed the locked frontend and responder dependencies; no system change outside the repo.
- `.scratch/guard-repo` was created by the guard check; `make clean-scratch` ran before QA, and again after QA's fixtures. `.scratch/` is empty.
- The parse check's `__pycache__` in `agent-kit/claude-code/hooks/` was removed.

## Permission review

- Read-only (propose allowing): `git status`, `git diff`, `git log`, `git ls-files`, `bash -n`, `python3 -m py_compile`, `make check-scripts`, `make verify`, `make permission-report`, `make branches`, `make ci`, `make file-at`, and `bash .scratch/check-guard.sh` (scratch repo only).
- Routine issue writes (already allowed; list only if a role recorded one): none.
- Protected record writes (keep asking): `HUMAN_APPROVED=1 git commit` for `e174151`, `8778092`, `5a0f256`, `4a27b30`, `b50207f` and `d9986ef`, after the human approved each diff; approval records are on #271 (6470535173; 6472423911 and the following part; 6496389807; 6496400857; 6496418162; 6497413564). QA's `make issue-close N=abc` validation matched the `make issue-close*` ask rule and did not close anything.
- System and external changes (keep asking): `make install` (locked dependencies), `chmod +x agent-kit/claude-code/hooks/cloud_session_start.sh`, removal of the parse check's `__pycache__`, and QA's `.scratch/` fixtures (`bash .scratch/check-guard-271.sh`, `python3 .scratch/extract-271.py`, `ln -s`, `truncate`), which matched the default `*` ask rule; `.scratch/` scripts are never allowed.
- Risky (propose denying): none.

## Interruptions

None.

## Unrelated problems noticed but not fixed

- The top-level `agent-kit/` mirror still lacks `permission-report.py` and the earlier project-only differences in `check-staged.sh`, `verify.sh`, `pre-push`, `asking-the-human.md` and `verify.md`; it also keeps a generic `cloud_session_start.sh` and the older `environments.md` pre-push line. #36/#38 track the duplication.
- OpenCode loads permission rules only at session start; the new `opencode.json` rules are not active until the human restarts.
- QA risks outside the scope: the first three are fixed in `5a0f256`, `4a27b30` and `b50207f`, and the SSH-key gap is closed in `d9986ef`; the Claude `make issue-close` ask precedence is still not verified live (#66), and the `.env` block is the tool rule rather than the Makefile filter. `id_rsa`/`id-rsa` case variants are not caught by the case-sensitive check; non-standard names only.

## Follow-ups for the next session

- The human restarts OpenCode, reads the settings diff, and pushes.
- The human runs the Claude `make issue-close` live check (#66).
- The next permission sweep starts from `9eb4071` and decides the approvals recorded here.
