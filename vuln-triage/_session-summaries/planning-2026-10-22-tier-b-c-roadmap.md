# Planning 2026-10-22: temporary Tier B/C roadmap

Tool: Claude Code (cloud session), branch `claude/kind-einstein-i39rmh`.

## What was asked

The human asked for a temporary secondary roadmap for Tiers B and C, without interrupting the session working roadmap step 11, to be merged into `_docs/roadmap.md` later. Inputs: the final-project criteria and the course's Module 2-4 notes and Module 3/4 homework, pasted by the human.

## What was done

- Added `_docs/roadmap-tiers-b-c.md`: Tier B milestones B1-B6 and Tier C milestones C1-C8 with dependencies, "done when", criteria, relative size and score checkpoints (19 after B6, 24 after C7); human prerequisites; a local-first order if AWS is slow; a course-vs-plan comparison; decisions D1-D6; merge steps.
- `_docs/roadmap.md` was not changed, so it does not conflict with the step 11 session.
- Appended an entry to `_docs/ai-usage-log.md`.

## Verification

`make verify` (after `make install`): PASS WITH WARNINGS. The one warning is `BASE` equal to `HEAD` (uncommitted, docs-only change); no test files changed.

No QA or rubric-auditor review; the file is a draft for the human.

## Open decisions (in the new file)

D1 close architecture Open question 6 with the Module 4 pattern; D2 course image tag and `service.version` in the allowlist; D3 domain and TLS; D4 responder false-positive rule (protected spec change); D5 AWS fallback; D6 move n8n tasks 33 and 34 ahead of task 25; D7 split tasks 21 and 24 when filing.

## Follow-up after step 11

PR #89 (step 11, `_docs/tasks.md`) was still open when this file's PR was written. The draft now maps each milestone to its `tasks.md` task numbers. Found in PR #89, not changed (not this session's branch): `_docs/roadmap.md` line 137 is a leftover `=======` conflict marker. Both PRs append to `_docs/ai-usage-log.md`; whichever merges second keeps both entries.

## Process notes

- The usage-log entry was appended with a shell heredoc and the install and verify commands were chained, against the `AGENTS.md` conventions (edit with the editing tool; one command per call). The resulting diff is ordinary and visible in the commit.

## Permission review

No approval requests in this session.
