# Issue #188: The setup.sh test fails in the push-check image that has uv, because it does not stub uv

**Date:** 2026-11-21T08:40Z (UTC)
**Spec version:** none

## What changed and why

`tests/test_gate_setup_sh.py` now stubs `uv`, `opencode` and `claude` beside the other installers, and `stub_commands` takes per-command versions and failures, so the module no longer depends on what the machine has on PATH. Four new `UvTest` cases cover the install branch, the skip branch, an unreadable version and a failed install that must not be masked. The implementation was already on `opencode/issue-188` as `168351c`; this session verified it, merged `main` into the branch (`3e14ad5`) at the human's request, and the human pushed that merge to `main`.

**What I learned:** the pre-fix module can be re-run from `git show <base>:tests/test_gate_setup_sh.py` with a fake `uv 0.13.6` first on PATH, which reproduces the push-check image's relevant difference without Docker.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

none (the PM, Engineer and QA roles ran in sequence in this session; no subagents)

## Files created or modified

- `tests/test_gate_setup_sh.py` (commit `168351c`, merged to `main` as `3e14ad5`)
- `_session-summaries/2026-11-21T0840Z-issue-188-orchestrator-setup-sh-uv-stub.md` (this file)
- `.scratch/` evidence: the QA worktree `.scratch/188-qa` and its `qa188` logs; not committed

## Decisions made by the human

- Merge `main` into `opencode/issue-188` so the branch does not diverge.
- Merge and push the branch to `main`.

## Mismatches with the spec or design docs

none (the repo has no spec file)

## Commands to validate

- **Verify:** `make verify BASE=main` on the merged branch at `3e14ad5`: PASS, 1632 tests, 0 failed (273.710 s); whitespace PASS; weakened tests none (20 assertion lines added, 0 removed).
- QA evidence, `.scratch/188-qa/.scratch/188-qa.sh`: the pre-fix module fails `0 != 1` with a fake `uv 0.13.6`; the fixed module passes 14/14 in five environments; six mutants each fail.

## Proposed AGENTS.md changes

none

## Temporary changes

None to the system. `.scratch/` was not cleaned because it holds other sessions' files and worktrees; the QA worktree `.scratch/188-qa` is left for review. Nothing was left running.

## Interruptions

none

## Unrelated problems noticed but not fixed

- `tests/kit_repo.py` passes the machine's PATH through, so other test modules can still see host tools (out of scope in the issue body).
- `setup.sh`'s `"uv 0.13.6"*` prefix match also accepts e.g. `uv 0.13.60` (out of scope in the issue body).
- `make sweep-due` reports `due: no sweep recorded`.

## Follow-ups for the next session

- Merge this summary commit (branch `opencode/issue-188`, one commit ahead of `main`) if it is to live on `main`.
- Start issue #187 next on this track; it needs `approved`.
