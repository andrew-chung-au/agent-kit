# Issue #50: Human task files in _human-tasks/

**Tier:** Standard (no tier label was set)
**Date:** 2026-11-02T12:49Z (UTC)
**Spec version:** none

## What changed and why

The first Kiro Web (cloud) session took over from OpenCode and did #50 first, as the handover ordered. By-hand instructions now live in `_human-tasks/` as copy-paste steps with expected output. Commit 9d3c07f (13 files, protected, committed with `HUMAN_APPROVED=1` after the human approved): the template `agent-kit/templates/human-task.md`; the wording test `tests/test_human_task.py`; the `human-task` kind in `procedures/session-summary.md`; the "Human tasks" rule in `process.md`; the pointer in `asking-the-human.md`; rows in `blueprints.md`, `setup.md`, `environments.md` and both docs-index files; one line in `team/software-engineer.md`; two pilot task files (push review from the clean clone; the #47 OpenCode checks, nine recorded steps plus two unrun spot-checks).

QA PASS at 9d3c07f (a fresh subagent; mutations on a copy; no files changed). Not verified: `make verify` end to end, because `tests/test_tier_check.py` hangs in the cloud sandbox (it also hung before this change; 366 other tests and the new tests pass; the claims check passes).

Engineer choices: the test lets a pilot step contain a forbidden command only with both a `Refusal test:` and a `Risk:` line (the template has no exemption); the pilots use the safe variants recorded on #47 (`ls .env`, `gh auth token --help`) instead of the real secret-printing commands; the `human-task` example filename was left out of `session-summary.md` because `tests/test_claims.py` only allows single-word kinds in its examples.

**What I learned:** the repo's docs assume the local sandbox, but a cloud agent can push, has no clean clone and has no kit hooks active. I committed straight to `main`, as AGENTS.md says, which the cloud session's own branch policy forbids; the commit was local only.

## Reflection

### Engineer

1. Slowed down: `make issue-hash` and `gh issue view` fail in the cloud sandbox (GraphQL), so I hashed the body over REST with a `.scratch/` script; `make verify` stalled for 10 minutes on a hanging test before I found it.
2. Nearly went wrong: the first version of `session-summary.md` added an example filename that broke an existing test; I removed it rather than loosen the test.
3. Proposal: `agent-kit/scripts/issue-hash.py` falls back to `gh api` REST when `gh issue view` fails. Effect: the hash check works in cloud sessions. Measure: `make issue-hash` returns a hash in a Kiro Web session (today: `unknown`).

### QA

1. Slowed down: the evidence for the nine OpenCode results sat in one long #47 comment; found by searching the saved output.
2. Nearly went wrong: mutations that changed pilot steps 8 and 9 to `cat .env` and `gh auth token` passed the test (by design, the exemption); QA reported it as a risk and not as a miss.
3. Proposal: require "don't retry another way" in every `If different:` line and add a mutation helper under `tests/`. Effect: fewer bespoke QA scripts, a testable stop rule. Measure: QA sessions that write their own mutation script (here: 1, target 0).

### PM

unknown (role not asked)

## Launch usage

- QA (check #50 at 9d3c07f): about 10 minutes, tool uses not reported by the notification (unknown)

## Files created or modified

- See commit 9d3c07f. This summary only after it.

## Decisions made by the human

- Approved the HUMAN_APPROVED=1 commit of the 13 staged files.
- Said this is a cloud session: it does not push from a clean clone. Asked to focus on the upgrading path and to carry on with the outstanding issues.
- Did not answer the three decision questions (pilot safe variants, pilot steps 10 and 11, stop-rule wording) or the cloud-agent issue question; defaults applied as stated.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify` (cannot finish in the cloud sandbox: `tests/test_tier_check.py` hangs)

## Proposed AGENTS.md changes

none this round. Still pending from the handover: the "token is read-only" line and the Environment setting do not describe cloud sessions.

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- `tests/test_tier_check.py` hangs in the cloud sandbox (first test, probably the unusual file names in `UNUSUAL_NAMES`; not diagnosed).
- No open issue covers cloud agents (Kiro Web); #10 (Codespaces) is the closest.
- `core.hooksPath` is unset in this checkout, so the kit's git hooks did not run on 9d3c07f.
- The commit is on local `main`, one ahead of `origin/main`; not pushed.

## Follow-ups for the next session

- Decide how 9d3c07f reaches GitHub (branch and PR is the cloud policy).
- A cloud-agent profile: new issue or a scope note on #10.
- Then the upgrade path: #9, #31, #2, #7, #8.
