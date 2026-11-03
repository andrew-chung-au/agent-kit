# Issue #044: cloud sessions (REST issue targets, push guard, session hook)

**Date:** 2026-10-21
**Spec version:** 67a4076

## What changed and why

- A Claude Code cloud session can now read issues through REST, post a comment, install the repo's git hooks, and push only its own `claude/*` branch; the local sandbox keeps today's behaviour (local pushes still refused, no extra session output).
- The protected commit `8eeaf53` adds the REST-only `issue-dump` (two flat JSON files), `issue-comment` and `issue-close` Make targets; the `gh api` allow and the `make issue-close` ask rules; the four `git push` deny rules; the `guard_git.py` cloud push exception; the new `cloud_session_start.sh` SessionStart hook; and the `AGENTS.md` cloud profile.
- The human scheduled #44 after #23 and before #27 (option B); its own criteria had the orchestrator close it with the new target.

## Files created or modified

- `Makefile`, `.claude/settings.json`, `opencode.json`, `_docs/agent-kit/claude-code/hooks/guard_git.py`, new `_docs/agent-kit/claude-code/hooks/cloud_session_start.sh` (100755), `AGENTS.md`: all six in `8eeaf53` (protected; approval record 6313318576).
- `_docs/roadmap.md` (check-in), `_docs/ai-usage-log.md`, this summary.
- GitHub: grooming comment 6310709588; live `make issue-comment` test 6311435040; Engineer evidence 6314178652; QA FAIL 6314003194 and PASS 6314208500; follow-up #47.

## Decisions made by the human

- Groom then implement #44 (option B: after #23, before #27).
- Approve the exact six-file protected diff as one commit.
- File one low-priority follow-up for the four outside-criteria guard/`FILE` risks (#47).
- Defer the PM's six `_docs/cloud-sessions.md` notes to the § 5 trial follow-up.

## Mismatches with the spec or design docs

- The groomed issue's `gh api --paginate --slurp ... --jq 'add'` is not accepted by the local `gh` (`--slurp` is rejected together with `--jq`), so the target uses the permitted equivalent `gh api --paginate --slurp ... | jq 'add'` under `bash -o pipefail`. This matches an outside image detail left for the § 5 trial (`jq` must exist in the cloud image).

## Commands to validate

- **Verify:** `make verify` PASS WITH WARNINGS (35/35 tests; whitespace PASS; the 7 weakened-test warnings are the earlier unpushed #22 rewrite, not #44).
- `make assert-clean`: PASS at `8eeaf53`.
- `make issue-dump N=44`: wrote `.scratch/issue-44.json` and `.scratch/issue-44-comments.json`.
- Guard matrix 30/30; SessionStart checks 7/7; settings checks 14/14; issue-target refusals 16/16.

## Proposed AGENTS.md changes

- Applied in `8eeaf53` with the human's approval and approval record 6313318576.

## Temporary changes

- No system configuration changed and no long-running process started.
- `chmod 755` on the new hook; a `py_compile` bytecode directory was created and removed.
- `make clean-scratch` ran after QA: `.scratch/` is empty.

## Permission review

- Read-only (propose allowing):
  - The Engineer's and QA's `.scratch/` check scripts (`python3`, `bash`), `sed -n` reads and `git`/`gh` reads; basis: the `*` and `* > *` `ask` rules.
  - The PM's `python3 .scratch/pm44_extract.py` and `.scratch/pm_show_body.py`; basis: the `*` `ask` rule.
- Writes to the record (keep asking):
  - Editing the six protected paths (`Makefile`, `.claude/settings.json`, `opencode.json`, `guard_git.py`, the new `cloud_session_start.sh`, `AGENTS.md`); basis: the `Edit(...)` `ask` rules and merits requests for protected files.
  - `HUMAN_APPROVED=1 git commit` for `8eeaf53`; basis: merits request for a protected commit.
  - `make issue-comment` on #44 (the live test and the evidence comment); basis: GitHub write to the record (ran under the `make *` allow rule).
  - `gh issue create` for #47; basis: GitHub write to the record.
  - `gh issue comment`/`gh issue edit` used in grooming; basis: `gh issue edit*`/GitHub write to the record.
- Risky (propose denying): none.
- Proposed `opencode.json` and `.claude/settings.json` changes: none.

## Interruptions

- The first Engineer subagent run failed with "Upstream request failed: Endpoint is unavailable" before making any change. The orchestrator checked `git status`, `git log` and `.scratch/`, found nothing left behind, and relaunched fresh.
- QA FAILed #44 once: two record-keeping criteria (the guard matrix and the live-comment URL) were not in an issue comment; the Engineer posted comment 6314178652 and the re-check passed.

## Unrelated problems noticed but not fixed

- Guard bypasses (`git -c alias.p=push`, `git -C <other checkout> push`) and `make issue-comment` `FILE` gaps (a `.scratch/` symlink that escapes, and shell metacharacters): filed as #47.
- The `_docs/cloud-sessions.md` § 3 text is now stale versus the implemented targets and settings; deferred to the § 5 trial follow-up.
- The default `make verify` still warns about 7 removed assertions from the unpushed #22 test rewrite.

## Follow-ups for the next session

- **§ 5 trial (human):** after this is pushed and the `Protect Main Branch` ruleset is Active, run a cloud-session trial and check every remaining `VERIFY:` (branch prefix, `CLAUDE_CODE_REMOTE`, banner, Node 22 `npm ci` + 35 tests, Docker/Postgres, REST reads and comments, `jq` present, the ruleset Active). File its follow-up issue then, together with the `_docs/cloud-sessions.md` notes.
- **#45:** D4 `types.ts`/mock/UI alignment, after #23 and before step 9 (#34); #34/#25 wait for it.
- **#27:** Stage 3 part 2; step 8 closes when #27 closes.
- **#47:** the guard/`FILE` risks; under "Later".
- **#31:** the human sets up the Compose dev container using `_docs/docker-runbook.md` section 1.
