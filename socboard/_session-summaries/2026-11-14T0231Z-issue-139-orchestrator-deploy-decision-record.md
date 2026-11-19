# Issue #139: Record the Deploy decisions (Terraform on AWS, Postgres audit rule, rate limits)

**Date:** 2026-11-14T02:31Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

A new decision record, `_docs/decisions/2026-11-13T2156Z-deploy.md` (status `proposed`; only the human sets `approved`), and one `_docs/index.md` row. The record holds the seven Deploy decisions of 2026-11-12 (from the roadmap), the three new decisions in the issue's approved Decision record section (Postgres audit triggers with an application role that does not own the table; in-process limits with one worker; the amendment that moves every IAM resource and the budgets to the human-applied part), the region (`us-east-1`, the human's own account), accepted risks, the Postgres 16 pin, a never-hold table that separates what is enforced today from what is only planned, and a list of who settles each `VERIFY:` item. Later Deploy issues (#154, #155, #156, #162 so far) cite it.

Worked by Session A (Kiro Web) in a git worktree, draft PR #151, branch `issue-139-deploy-decision-record`. Heavy tier: eight Engineer rounds; both QA launches passed at the end at `94df972` (https://github.com/andrew-chung-au/socboard/issues/139#issuecomment-6872930459 and https://github.com/andrew-chung-au/socboard/issues/139#issuecomment-6872936711). PR #151 merged on 2026-11-14 (merge commit `b598a5d`). The rounds were: 1 (write the record), 2 to 4 (QA findings, mostly the never-hold table claiming checks that do not exist), 5 (restructure the table into enforced-today and planned columns), 6 (the first Reviewer report's six findings), 7 (restore the issue body's wording on the state-bucket region, which round 6 had overridden), 8 (option A: the snapshot schedule and its role move to the human-applied part, #162, so decision 10 stays as approved; three wording fixes).

**What I learned:** a table that pairs every rule with "the check that enforces it" invites overclaiming when most checks are future work; splitting "enforced today" from "planned" ended a run of QA failures.

## Reflection

### Engineer

Rounds 1 to 5: unknown (role not asked). Round 6 (comment https://github.com/andrew-chung-au/socboard/issues/139#issuecomment-6870075023):

Reflection:
- Slowed me down: the search tool does not index `_docs/`, so I checked issue bodies and the record with the shell.
- Nearly went wrong: the "not filed yet" wording was in four places besides the header, so a single replace would have left contradictions.
- Proposed change: a `make` target that lists issue numbers by D-number title so the record's numbers can be checked in one command.

Round 7 (comment https://github.com/andrew-chung-au/socboard/issues/139#issuecomment-6870213412):

Reflection:
1. Slowed: `gh run view --log` returned Forbidden here, so I used the jobs REST endpoint and grepped a saved log; CI took about 5 minutes to start and finish.
2. Nearly wrong: none blocked; the risk was a second rewrite adding procedure again, so I kept the edit to the one bullet.
3. Proposed change: `_docs/agent-kit/procedures/verify.md` could name the REST jobs-log route for sandboxes where `gh run view` fails, so engineers skip the trial and error; measured by the count of failed `gh` calls per round.

### QA

unknown (role not asked)

### Orchestrator

The orchestrator applied a Reviewer finding (4) that overrode approved issue text; the second QA launch caught it. A Reviewer finding applied on a recommendation must be checked against the approved body first.

## Launch usage

Engineer: 8 launches. QA first launch: 7 launches (FAIL at `5aa3272`; PASS at `1ae2345`, `6baa1ab`, `7a4e2e6`, `270e69b`, `c2f53c7` and `94df972`; each after the first was a fresh re-check). QA second launch: 6 launches including one that declined by mistake and was relaunched (FAIL at `1ae2345`, FAIL at `6baa1ab`, PASS at `7a4e2e6`, FAIL at `270e69b`, PASS at `c2f53c7`, PASS at `94df972`). Reviewer: 3 launches (`7a4e2e6`, the delta to `c2f53c7`, the delta to `94df972`). All were subagents; active time and tool uses were not recorded.

## Files created or modified

- `_docs/decisions/2026-11-13T2156Z-deploy.md` (new)
- `_docs/index.md` (one row)
- `_session-summaries/2026-11-14T0231Z-issue-139-orchestrator-deploy-decision-record.md` (this file)

## Decisions made by the human

- Approved the issue's Decision record section as written, including Postgres 16 (Orchestrator comment https://github.com/andrew-chung-au/socboard/issues/139#issuecomment-6865879093).
- Region: `us-east-1`, the human's own account (home region `ap-southeast-2`), no organisation-policy check (in the session, recorded in `_docs/planning/deploy-backlog-proposal.md`).
- After two second-launch FAILs, option 1 (restructure the never-hold table), and the stopping rule that a Medium-or-higher finding fails the Heavy second launch while Lows are reported (https://github.com/andrew-chung-au/socboard/issues/139#issuecomment-6869773094; the steering sentence is PR #161). An earlier comment that recorded this decision from a message meant for the other session was corrected (https://github.com/andrew-chung-au/socboard/issues/139#issuecomment-6867105416).
- Applying the first Reviewer report's six findings, under the human's blanket approval of the orchestrator's recommendations (https://github.com/andrew-chung-au/socboard/issues/139#issuecomment-6869999175), with finding 4 later corrected back to the body's wording.
- Second Reviewer report, finding 1: **option A** (2026-11-14): the snapshot schedule and its role move to #162; decision 10 unchanged. #156 and #162 were updated to match (Confirm comments on each). Findings 2 and 3 and the smaller point applied as wording.
- Third Reviewer report (https://github.com/andrew-chung-au/socboard/issues/139#issuecomment-6872964663): **option Y**, ship the record as it is; finding 1 fixed in the planning docs (PR #168); the data-volume tag and its contract (findings 3 and 4) go to #162 and the D17b draft; findings 2 and 5 left as wording.
- The human set the record's status to `approved` by merging the close-out pull request (#170).
- After this issue, the human ruled to limit review rounds (PR #169, `delivery-pace.md` item 13).

## Mismatches with the spec or design docs

- Spec section 5's secrets list omits the token signing secret (spec note A, pending the human); the record marks it as added.
- The issue body's region criterion says "account and organisation" in `ap-southeast-2`; the record follows the human's later clarification (own account).

## Commands to validate

- **Decisions:** `make decisions` (the record is listed as `proposed`)
- **Verify:** `make verify`

## Proposed AGENTS.md changes

none

## Temporary changes

A git worktree at `.scratch/wt/139` (git-ignored); removed when the issue is closed. No system changes, no processes, no installs.

## Interruptions

- One second-launch QA subagent declined, reading other agents' notes in its context as its own prior work; nothing ran, and it was relaunched with a clarifying line.
- One second-launch QA comment (at `c2f53c7`) says `make assert-clean` confirmed the clean tree; that QA did not run it. The orchestrator checked: the worktree was clean at `c2f53c7` and `make assert-clean` passed in the main checkout.

## Unrelated problems noticed but not fixed

- `make issue-close` checks only that a Close comment names a merge commit, not that it exists on `origin` (recorded in PR #157).
- `qa-engineer.md` says any problem fails the Heavy second launch; this repository's ruling differs (PR #161).

## Follow-ups for the next session

- #162: add a tag that only the data volume carries, for the snapshot schedule to select (third Reviewer report, finding 3); its body changes, so the human reads it before the Engineer starts.
