# Issue #11: Assess impact of the final project rubric on the plan

**Date:** 2026-10-16 (Engineer work, OpenCode) and 2026-10-17 (QA, decision point and close-out, Claude Code)
**Spec version:** 16e1ec0
**Status:** closed after QA PASS and the human's decisions. Nothing pushed.

## What changed and why

The final rubric (12 criteria, 24 points, 10 to pass) replaced the draft, and the plan was brought in line with it.

- 2026-10-16 (OpenCode, Space Bunny): PM groomed #11; Engineer replaced `_docs/rubric.md` verbatim (`0604233`) and wrote the impact report (`2cfdf95`). Session paused before QA (see Interruptions).
- 2026-10-17 (Claude Code, claude-opus-5-5, Orchestrator):
  - Posted the Engineer handover (comment 6227197431) with the tool and model history; QA PASS at `c8dea47` (comment 6227226075).
  - OpenCode unavailable: at the human's request an Engineer subagent corrected QA's six report risks and added the source URL and final newline to `_docs/rubric.md` (`ed05530`, comment 6227407227); a fresh QA subagent re-checked those points, PASS (comment 6227431094).
  - Decision point: relayed the human's decisions (comment 6228520087) and applied the approved §7 changes one at a time (see Files).
  - Rubric Evidence Auditor (Claude Code subagent) regenerated `_docs/rubric-evidence.md`: 7 of 24 points evidenced at `a535ff7`.

## Files created or modified

- `_docs/rubric.md`: final criteria, verbatim; line 1 source URL and final newline (`0604233`, `ed05530`).
- `_docs/reviews/2026-10-16-final-rubric-impact.md`: new; QA-risk corrections (`2cfdf95`, `ed05530`).
- `_docs/project-brief.md` (protected): workflow step 8 and CI/CD promotion path (`111b001`); observability stack (`b8792b3`).
- `_docs/specs.md` (protected): US-13 to US-15, E6, open questions 4-5 (`701951d`, `16e1ec0`).
- `AGENTS.md` (protected): Layout and "Where to read more" (`4075318`, committed by the human).
- `_docs/planning-process.md`, `README.md`: §7.3 (`1ebee3b`).
- `_docs/ai-usage-report.md`: §7.5 (`a535ff7`).
- `_docs/rubric-evidence.md`: §7.4 audit (`ad5b27d`).
- `_docs/ai-usage-log.md`: entries for every step above.
- Earlier in #11's first session: `Makefile` `issue-dump` target, `AGENTS.md` command line, `Makefile` added to PROTECTED (`f999cd6`, `fc29661`).
- `test.md`: removed (`0554a9f`, human-approved).
- GitHub: comments on #11, #9 and #10; issues #12 and #13 filed.

## Decisions made by the human

- QA must not run in the tool that built the work; #11 was built in OpenCode, so QA ran in Claude Code. For the follow-up fixes OpenCode was unavailable, so Engineer and QA both ran in Claude Code as separate subagents, recorded in comments and log.
- Model history: the human stated #11 moved from Muse Spark 1.3 to Space Bunny; the record shows Space Bunny for PM and Engineer, and Muse Spark's part as "not recorded".
- Scope: full marks (24/24), built as Tier A (12) → B (19) → C (24) milestones; all no-longer-scored items kept; scoring path first, then LLM brief, MCP server and n8n (committed scope). US-12 unchanged with all three acceptance clauses.
- §7.1 brief: 1a (MCP out of MVP) rejected; 1b accepted; CI/CD sentence and observability stack added.
- §7.2 spec: 2a rejected; US-13/14 accepted with Grafana; US-15 rewritten by the human (PR with fix and test, CI deploys to dev, production manual); E6 with Grafana; open questions 4 (US-14 window) and 5 (responder credential and merge).
- §7.0 AGENTS.md: Orchestrator's revised list with the human's "when to read" wording; `_docs/agent-team.md` left to #12.
- §7.3 planning process: api.md in place of openapi.yaml, CI exports the generated OpenAPI; AWS/CloudFormation, Docker-capable dev environment, cost controls and teardown; deliberate, removable responder defect; milestones.
- §7.4: auditor run now in Claude Code; OpenCode re-audit after Stage 2. §7.5: header and section 2 accepted.
- #9: hosting on AWS with CloudFormation (comment 6229681999).
- Close #11 only after the human's decisions comment, and only once `make assert-clean` passes.

## Mismatches with the spec or design docs

- `.claude/agents/rubric-auditor.md` still says "14 criteria" and tells the auditor to append to the log (same shape as #10).
- The impact report is a dated snapshot: §0 still says "the paste carries no URL"; §1 Totals says Application and Containerization need a "deployed" app (local or Compose is enough); §9 counts are as of 2026-10-17. Not corrected (outside the approved fixes).
- `_docs/rubric.md` line 1 date (2026-10-17) and URL: the human is to check them against the live page.

## Commands to validate

- **Verify:** `make verify` → PASS WITH WARNINGS (no TEST_CMD: planning phase, no code exists).
- **Assert clean:** `make assert-clean` → PASS at `d7f69a9` before close-out.
- `make clean-scratch` → ran at close-out, and again after the last comment files.

## Proposed AGENTS.md changes

- none outstanding (§7.0 applied as `4075318`).

## Temporary changes

- none. No processes started, no system changes, no installs. The human excluded `.local/` via `.git/info/exclude` (their change, local to this clone).

## Interruptions

- 2026-10-16: first Engineer launch interrupted before any commit; checked, relaunched. Session paused before QA while the human's `AGENTS.md`/`opencode.json` edits were uncommitted; the human committed them (`c8dea47`).
- 2026-10-17: none. The human's own `opencode.json` and `.claude/settings.json` edits were left out of every Orchestrator commit; the human committed them (`5feca25`, `d7f69a9`).

## Unrelated problems noticed but not fixed

- Issue #10's body has literal `\n` and no acceptance criteria (filing error from the #2 session); fix still deferred. Human's scope note added (comment 6230949666): fix both rubric-auditor files, 12 criteria, same log-entry rule in both.
- Repo-root `agent-kit/` duplicate of `_docs/agent-kit/` remains.
- Fixed at the human's request during close-out: stray `test.md` removed (`0554a9f`); local `origin/main` refreshed with `git fetch` (`27d4760` → `bd616a5`; no push).

## Follow-ups for the next session

1. Human: review and push the #11 commits (public `main` is at `bd616a5`; criteria 2-4 evidence is local only).
2. Human: check the rubric date and URL against the live page.
3. #12 (`_docs/agent-team.md`): PM grooming; confirm the wording of the same-tool QA exception.
4. #10: fix the body, groom, and include `.claude/agents/rubric-auditor.md`'s "14 criteria" line.
5. #9 and #8 need the changes listed in report §6; #3-#7 remain valid.
6. #13 (README: problem, functionality, expected behaviour): PM grooming, for the missing Problem Description point.
7. OpenCode re-audit of rubric evidence after Stage 2.
