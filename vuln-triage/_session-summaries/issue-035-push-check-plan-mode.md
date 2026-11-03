# Issue #035: push check plan mode completes the push without checking

**Date:** 2026-10-20
**Spec version:** fdc7b51

## What changed and why

- With `AGENT_PUSH_CHECK_PLAN=1`, the local-sandbox `pre-push` hook used to print a plan and then let the push through unchecked. Plan mode now blocks every push, including paths that print no plan line, with `push check: plan only; push not sent (unset AGENT_PUSH_CHECK_PLAN to push)` and exit 1.
- Each plan line now names the real targets: `make -C <project> install verify` when the pushed commit's Makefile has an `install:` target, otherwise `make -C <project> verify`, detected from the pushed commit, not the working tree.
- The `pre-push` row in `_docs/agent-kit/environments.md` now describes the real gate. Non-plan behaviour is unchanged.

## Files created or modified

- `df72298` protected commit, two paths only: `_docs/agent-kit/environments/local-sandbox/pre-push`, `_docs/agent-kit/environments.md` (+15/-3).
- `4454518`: usage-log entry for the implementation.
- Comments on #35: Engineer 6280974785; QA FAIL 6281291470; free-form approval note 6281324989; approval record 6287006555; correction 6287127239 (the free-form note's diff does not match the commit; 6287006555 is authoritative); QA PASS 6287037242.
- Follow-up issue #42. `_docs/roadmap.md`, `_docs/ai-usage-log.md` and this summary.

## Decisions made by the human

- At grooming: fix only `_docs/agent-kit`; the top-level `agent-kit/` duplicate stays with #36.
- Approved the exact two-file diff before `df72298`.
- Decision point, QA risks outside the criteria: option 1. The PM files one low-priority follow-up (#42) for the hook header wording, the unquoted plan path, the symlinked-Makefile limit and the unnumbered step in `environments.md`. The Orchestrator posts a correction about the free-form note's diff.

## Mismatches with the spec or design docs

None. The product spec is unchanged.

## Commands to validate

- **Verify:** `make verify BASE=4454518` PASS at `df72298` (first QA) and at HEAD `48cbb9d` (re-check): 35 tests, whitespace PASS, no weakened tests.
- **Behaviour:** the Engineer's 10-case harness and QA's independent 83-check harness (`.scratch/qa-push-check-plan.sh`) both passed, covering every plan path, the detection cases, the root fallback and unchanged non-plan behaviour against the pre-#35 hook.
- **Approval record:** a `.scratch/` script confirmed the approval-request diff is byte-identical to `git show`; QA's re-check ran 34 field checks with 0 failures.
- **Assert clean:** `make assert-clean` PASS at `48cbb9d` after the re-check. The first QA run did not report it, and HEAD did not move during that run.

## Proposed AGENTS.md changes

None.

## Temporary changes

None. No process was started and nothing was installed. The harnesses wrote only throwaway repositories under `.scratch/`. `make clean-scratch` ran after both OpenCode sessions had stopped; `.scratch/` is empty, which also covers the step 6 files noted in `planning-2026-10-20-spec-review-3-8.md`.

## Permission review

- Read-only (propose allowing): none.
- Writes to the record (keep asking): none.
- Risky (propose denying): none. `git push` is denied in the sandbox by design; no role attempted it.
- Proposed `opencode.json` and `.claude/settings.json` changes: none.
- Sources: the Engineer, both QA and the PM comments all say "none". The Claude Code close-out had none. The OpenCode orchestrator's own stopped commands for `df72298` could not be collected, because that session was interrupted.

## Interruptions

- The OpenCode session implemented, committed and QA'd #35 while a second OpenCode session committed #17 in the same working tree. Each session's commits moved HEAD during the other's QA. The two sessions paused to coordinate, and the #35 session then stopped. Claude Code (claude-opus-5-5) took over as the only orchestrator, so the coordination question no longer applies.
- Checked afterwards: clean tree, no #35 file changed since `df72298`, and only criterion 10 failing.

## Unrelated problems noticed but not fixed

- The hook source is stored as non-executable (`100644`); this predates #35 and is noted in #42.
- The exit trap's `update-ref -d` is a no-op in plan mode; the PM left it out of #42.

## Follow-ups for the next session

- Human, after pushing: confirm `AGENT_PUSH_CHECK_PLAN=1 git push` aborts with the remote ref unchanged, reinstall the hook (make sure the installed copy is executable), and run the `cmp` confirmation from the Engineer's comment.
- #42 (low priority), #36 (duplicate `agent-kit/`).
- Roadmap step 4 (#33) is next, followed by step 7.
