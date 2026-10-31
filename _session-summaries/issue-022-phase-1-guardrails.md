# Issue #22: Phase 1: guardrails — claims check, .env edit deny, read-only allows, behaviour tests

**Date:** 2026-10-31
**Spec version:** none

## What changed and why

`make test` now fails when the kit's docs promise something the kit doesn't ship. A stdlib claims check covers make targets, kit paths and blueprints coverage, and a stdlib `unittest` suite covers it. Both tool layers now deny editing `.env` files and keep `.env.example` editable. Precise read-only allows were added for `git remote`, `git cat-file`, `gh issue`, `gh run` and `sha256sum`, with mutating and `--log` denies. `guard_git.py` has behaviour tests. A doc-budget baseline was recorded: always-loaded 4,414 words; core Markdown 14,297 (+6 against the 14,291 baseline, all in `blueprints.md`). Real doc failures were fixed: a `run` target in `Makefile.mk`, `make stop` changed to `make <name>-stop`, the `make probe` example turned into a placeholder, and blueprints rows for `claude-code/agents/`, `claude-code/hooks/` and `opencode/agents/`.

The opencode session ran out of usage after grooming. The orchestrator resumed from the PM's comment and the issue text.

## Files created or modified

Commit da33bd7 (11 files): `Makefile`, `agent-kit/blueprints.md`, `agent-kit/claude-code/settings.json`, `agent-kit/opencode/opencode.json`, `agent-kit/procedures/asking-the-human.md`, `agent-kit/scripts/check-claims.py` (new), `agent-kit/team/qa-engineer.md`, `agent-kit/templates/Makefile.mk`, `tests/test_claims.py` (new), `tests/test_guard_git.py` (new), `tests/test_permissions.py` (new).
Commit 46a6724: `AGENTS.md` (Test (all) wording).
Live code: `agent-kit/scripts/check-claims.py` runs live from the working tree inside `make test`, `make verify` and the git hooks, including for its own commit. Nothing under `claude-code/hooks/` changed.

## Decisions made by the human

- Cloud-session push allow path stays out of Phase 1; the tests lock in the core denial (Phase 6 adds the allow path).
- Keep `Bash(sha256sum *)` as a read-only allow.
- Approved and ran the Engineer's commit (da33bd7) with `HUMAN_APPROVED=1`.
- `.claude/settings.json` changed during QA and was the human's own change (or an approval they gave), so QA's PASS stands.
- Approved only the `AGENTS.md` Test (all) change (46a6724). Not chosen: the version bump, the PM follow-up for the stale `opencode/START.md`, and a follow-up for the live checks.

## Mismatches with the spec or design docs

None (there is no `_docs/specs.md`). One acceptance criterion couldn't hold literally: "no allow pattern matches `gh run view --log`", because the required `gh run view *` allows match it. The tests instead prove that `--log` and `--log-failed` end up refused through deny-wins (Claude Code) and last-match-wins (OpenCode). QA accepted this.

## Commands to validate

- **Verify:** `make verify` (passes at da33bd7: claims OK, 57 tests, 0 failed)
- **Test (all):** `make test`

## Proposed AGENTS.md changes

Applied (46a6724): Test (all) now mentions the claims check and the unittest suite.

## Temporary changes

None. `make clean-scratch` ran at the end of the issue and emptied `.scratch/`. Nothing was started that needs stopping.

## Interruptions

The opencode agent ran out of usage after the PM groomed the issue; the PM's comment was complete and nothing was left half-done. `make assert-clean` failed after QA because of ` M .claude/settings.json` plus the two untracked `proposals/` files. The `proposals/` files were untracked before the session started. The human confirmed the `.claude/settings.json` change was theirs, so QA's verdict was kept.

## Unrelated problems noticed but not fixed

- `.claude/settings.json` is still modified and uncommitted (the human's change).
- The two `proposals/` files are untracked, so `make assert-clean` fails until they're committed or moved.

## Follow-ups for the next session

- The human runs the live checks QA couldn't do, in Claude Code with the kit's `settings.json` installed and in OpenCode: `gh run view 1 --log` is refused; `Edit(.env)`, `Edit(.env.local)` and a nested `config/.env` are denied; `.env.example` is editable; `gh issue list` with no arguments matches the allow. At QA's run, `gh run view 1 --log` was not refused (likely the installed settings lack the new deny, unconfirmed). If it is still not refused with the kit settings, the PM files a follow-up.
- `agent-kit/opencode/START.md` still says `opencode.json` blocks only reading `.env` files, not editing (small follow-up, not filed).
- Version bump (proposed: minor, with a changelog line in the Engineer's comment) was not approved yet. The human decides when to cut a version.
- `check-claims.py` treats a directory as covered if `blueprints.md` names any path inside it. This is generous; revisit if the coverage check misses real gaps.
