# Planning: #68 docs research follow-through, container-track close-out, QA of the first Kiro PR wave, and the closing flow (#119)

**Date:** 2026-11-03T23:10Z (UTC)
**Spec version:** none

## What changed and why

The human's answers to the #68 report's "Needed from the human" were relayed on #68 and the PM filed the build issues #106 to #112 from the recorded P1 to P6 ruling. The compose variant (#11) and push-check image (#96) were QA-passed and, after a stranded merge into the #95 branch, reached `main` through PR #105. The #91 Decision record was drafted, approved by the human (relayed), and the PM filed pieces #113 to #118. The human chose `make issue-close` (#119), which was built by Kiro, failed two QA launches on a command injection through `REASON` and an all-digit short SHA, was fixed, passed two fresh launches, and merged. This session ended by using it.

**What I learned:** a PM comment with `Body sha256:` after `PM:` on the same line records nothing for `issue-hash.py`, and QA correctly refuses to run without a recorded hash.

## Reflection

unknown (roles not asked). The session ran about 40 launches and hit the 5-hour usage limit once; asking each role for a Reflection was not done.

## Launch usage

Roles launched: PM (about 8), QA (about 28, including resumed and redone runs), none other. Figures per launch are in each completion notification of the session and were not copied here: unknown. Five QA runs stopped on the usage limit (reset 21:30Z) and were resumed with their saved work.

## Files created or modified

- `_docs/human-inputs/2026-11-03-rag-file-structure-guide.md`, `_docs/measurements/2026-11-03-vuln-triage-duplication-patterns.md` (committed `ebd164a`).
- `_human-tasks/2026-11-02T1220Z-human-task-047-engineer-opencode-by-hand-checks.md` (the v2.2.5 re-run, the "refused" word, the wording in each step box; `82e9bf7`, `7c27caa`).
- Merge of `origin/main` into the sandbox `main` to get `make issue-close`.
- Issue comments only otherwise; the Engineer (Kiro) and PM changed repository files through PRs.

## Decisions made by the human

- Keep the two kit copies under `vuln-triage/` for now (option 3 in the #91 record, to be compared read-only later).
- Approved the #91 Decision record and the filing of pieces (a) to (f); approved the #119 Decision record; chose `make issue-close` (option 2) over a read-only list.
- Confirmed the `docs-index.md` Plan row edit on #107.
- Authorised the orchestrator to review and close issues with `make issue-close` once merged.
- Not decided: the fourth-field vocabulary of the installed-files map (`none`, `markers`, `prefix:<text>`); which of `AGENTS.md` or `process.md` keeps the closing rule (recommendation given: `process.md` keeps it, `AGENTS.md` a pointer, after #119).

## Mismatches with the spec or design docs

none found.

## Commands to validate

**Verify:** `make verify`. **Test (all):** `make test`.

## Proposed AGENTS.md changes

none. A pointer for the closing rule is proposed for after #119 (see Decisions).

## Temporary changes

None to system configuration. Scratch files under `.scratch/`, plus a QA git worktree `.scratch/qa109` and ref `refs/qa/pr126` left by a QA run: not removed (raw git needs approval; `make clean-scratch` handles the folder).

## Interruptions

Five QA runs (#107, #108, #109, #110, #112) stopped on the usage limit at 21:30Z and were resumed; their saved work was used and each posted its own comment. One resume message went to the wrong, finished agent (a #92 QA run) by my mistake; it only repeated its old report.

## Unrelated problems noticed but not fixed

- `make kit-check` fails in this repo: no `agent-kit/MANIFEST.sha256` (QA on #88).
- `check-tier.sh` header and one message were reworded by #92 without the human's earlier approval (QA: wording only).
- QA on #111 reported that `issue-112-dup-report` may have been force-pushed; not verified.

## Follow-ups for the next session

- Close the issues QA-passed and merged once their close comments are posted; QA the issues that merged without QA (#21, #2, #77, #55, #63, #32, #49, #71, #31, #20 partial).
- Merge the stacked PRs #126 to #129 in order, retargeting each to `main`.
- The human labels `approved` on #114 to #118 and the small follow-ups #72, #85, #86, #87, #93 for Kiro.
