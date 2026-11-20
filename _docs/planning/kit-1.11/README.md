# Kit 1.11 planning

**Date:** 2026-11-19. Everything a session needs to carry on the 1.11 kit upgrade, in the repo so a cloud session can read it.

| File | What it is |
|---|---|
| `workflow-review.md` | The 1.11 proposal: evidence from socboard, vuln-triage and the kit, the workflow, settings and profiles, formats, and the 1.11 scope (section 9). Every decision is recorded in section 12; none is open. |
| `issues/00-index.md` | The 21 draft issues in filing order (01a to 12), with tier, grades, needs, the existing issues each one affects, and the gaps still open. |
| `issues/filed.md` | The filed issue number for each draft id (issue #196 to issue #216), how they were filed, and notes from the split. |
| `issues/01-...md` to `issues/12-...md` | One draft per issue. A file holding a split (01, 03, 04, 07, 08, 09, 11) has each part as its own section. |
| `backlog-review-2026-11-19.md` | Review of the 26 open issues against main and the proposal: what was closed, what 1.11 supersedes, what folds into which draft. |

## Where things stand

- **All 21 issues are filed** (2026-11-20), as issue #196 to issue #216, unlabelled. `issues/filed.md` maps each draft id to its number. Next: the human adds `approved` to 01a (issue #196); the PM grooms it first. Settled by the human on 2026-11-19: 04c is heavy; 07a waits for 05 and 06.
- **Grooming is one issue at a time** until 04c (groom ahead) lands, because `process.md` still forbids grooming a second unlabelled issue.
- **Closures that wait for the human's approval** (as not planned): issue #142 and issue #26 (when 7b is approved), issue #17 (into 11a), issue #15 (into 09a), issue #9 (superseded by `agent-kit/releasing.md`, or narrowed). See the backlog review, sections C and D.
- **Related open issues, unlabelled:** issue #188 (push-check uv stub; until fixed, `unset AGENT_PUSH_CHECK_IMAGE` before pushing the kit), issue #191 (usage visibility; later), issue #192 (install-guide wording), issue #193 (tests that share `.scratch/`; all four files, approved scope).
- **Tool economics** shape the design: Claude Code has a five-hour window and is the only tool with a model step-up (`STEP_UP`); OpenCode runs free models; Kiro has month credits and its auto model is cheaper than a named one.
