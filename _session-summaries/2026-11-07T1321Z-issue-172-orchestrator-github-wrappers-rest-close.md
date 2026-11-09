# Issue #172: GitHub wrappers name the repository and use the REST API

**Date:** 2026-11-07T13:21Z (UTC)
**Spec version:** none

## What changed and why

#172 made the kit's GitHub wrappers read the repository from one `GITHUB_REPO="<owner>/<name>"` line in protected `agent-kit.conf` (as text, validated before any `gh` call) and use fixed `gh api` shapes, reading every comment page. They now work where the git remote is not github.com, such as Kiro Web, with every existing check, output and exit code unchanged.

This session did not build it: the Engineer's commits `4ec8e91` and `5dca4c5` (the approved ADR) merged as `f6dd344` (PR #176) on 2026-11-06 at 11:44Z. It is effectively Heavy from the PM proposal, though it carries no tier label; the two Heavy QA launches both passed at `5dca4c5` (the second code-review only). This session ran the decision point and the close.

**What I learned:** these wrappers are live scripts, so this session's own Close comments and closes are their first real POST and PATCH against GitHub.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

none

## Files created or modified

- `_session-summaries/2026-11-07T1321Z-issue-172-orchestrator-github-wrappers-rest-close.md` (this file)
- `_human-tasks/2026-11-07T1321Z-human-task-172-orchestrator-wrapper-write-and-kiro-checks.md`
- `agent-kit/README.md`: the `Unreleased` lines for #143 and #170, committed as `baabd0d` (protected, approved by the human). #172's own line was already there.

## Decisions made by the human

- Sweep: run the first sweep at the 1.10 cut (#171), not in this session.
- Changelog: add the `Unreleased` lines for #143 and #170 now, and commit them.
- Kiro Web leftovers from #172: the PM folds them into #52 at its next grooming, rather than filing a new issue.
- The ADR in the body was approved at `d369ddd8...cfa7`, including the compatibility break for existing projects.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make test`
**Assert clean:** `make assert-clean`
**Close:** `make issue-close N=172`

## Proposed AGENTS.md changes

none; the direct `gh issue view` instructions in `AGENTS.md` and `process.md` go to #52 instead.

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- `AGENTS.md` and `process.md` still tell agents to run `gh issue view <N> --json labels` directly, which fails where the git remote is not github.com; by the human's decision this goes into #52.
- Bot logins now read `kiro-agent[bot]` from the REST API where `gh issue view` gave `app/kiro-agent`; only bot-authored issues are affected.
- `sweep-due`'s `since` is "updated after", so an issue closed in the exact second of a sweep entry's timestamp could be missed; rare, and only delays a sweep.
- Existing projects must add the `GITHUB_REPO` line or every wrapper refuses, and the import procedure does not yet look for it; the ADR and the README say so.
- Not verified against real GitHub by QA: the POST and PATCH write shapes and the Kiro Web check. This session's Close comments and closes exercise the write shapes; the Kiro Web check is in the human task file above.

## Follow-ups for the next session

- `make issue-close N=172` in this session, after this summary.
- Run the human task: confirm the Close comment and close appeared, then `make issue-hash N=172` in Kiro Web.
- #52: the PM folds in the direct `gh issue view` instructions at its next grooming.
- #171: cut 1.10 and run the first sweep there, by the human's decision. Existing projects' upgrade notes must include the `GITHUB_REPO` line.
