# Issue #043: Stage 2, `_docs/architecture.md`

**Date:** 2026-10-20
**Spec version:** 3ecd54b

## What changed and why

- `_docs/architecture.md` (new) answers the Stage 2 checklist, #9's architecture rows and the step 7 inputs from #41. It covers components and tiers, the workflow, ingestion and matching, the data model (with a table of differences from the mock frontend's types for #23), prioritisation with a worked example, the LLM brief and its guardrail, routing, external sources, the MCP server, security boundaries with a credential table, observability, the responder agent, AWS/CloudFormation deployment, the development environment and rubric enablement. Uncertain facts are tagged `VERIFY:`; judgements are tagged `ASSUMPTION:` (38 of them).
- Two protected spec commits:
  - `faea412`: the status model (re-scan may close a `risk accepted` finding; `withdrawn` needs every merged advisory withdrawn; reinstatement restores the prior status), the `no dependency files` reason, the brief link built by VulnTriage, the KEV values, due dates per lifecycle, and new advisory-text rows.
  - `3ecd54b`: `KEV: not listed` before the first KEV fetch; versionless lockfile entries; stale kept findings.
- The US-14 alert fires once per finding with no repeat (human decision).
- Same session, outside the issue: the roadmap was reprioritised toward product work, and `_docs/cloud-sessions.md` (optional reference) and `_docs/docker-runbook.md` (option A, the human's part) were written.

## Files created or modified

- Spec, protected, each committed alone with `HUMAN_APPROVED=1`: `faea412` (record 6290689973) and `3ecd54b` (record 6291380101).
- `_docs/architecture.md` and `README.md` link: `072c17e`; fixes `631706e`, `974c3f6`, `6e83ce2`, `4180fe3`.
- Usage log: `e15bf29`, `e8ce1be`, `741489a`, `4b90629`, `6dd32e6`, `c2f6279`. Roadmap: `16b445b`, `c2f6279`. Docs outside the issue: `ba1a8cf`, `c9f2a20`.
- Comments on #43:
  - human decisions: 6289876616, 6291276406 and decision point 6301818549;
  - Engineer: 6290123115, 6290358382, 6290918784, 6291326008, 6291539799, 6291652743, 6301770281;
  - QA: 6291494669 (FAIL), 6291613521 (FAIL), 6291706212 (PASS), 6301808583 (PASS).
- Other issues: #23 comment 6301758496; #9 body (five boxes ticked) and comment 6301823825; #31 comment 6301824334.

## Decisions made by the human

- Approved creating #43.
  - D1: Compose dev container.
  - D2: the responder opens PRs only, and the human merges.
  - D3-D8: the PM's recommendations.
- Reinstated `withdrawn` findings restore their earlier status; the optional `risk accepted` row clause was not added.
- KEV option A (reword `not listed`), and a second spec commit before QA (criteria change, 6291276406).
- Approved both exact spec diffs.
- At the decision point:
  - the Engineer's design choices are accepted as assumptions, including that owners accept risk only on their own assets;
  - the alert does not repeat;
  - leftovers go on #23 and in the roadmap, not into new issues.
- Outside the issue: product work first (roadmap priority rule); Docker option A; cloud sessions optional only.

## Mismatches with the spec or design docs

None open. Small spec wording items for the next spec change are noted in `_docs/roadmap.md`: E10's uv workspace entries, and US-2 on the project's own `uv.lock` package.

## Commands to validate

- **Verify:** `make verify BASE=16b445b` PASS in every QA run (35 tests, whitespace PASS, no weakened tests).
- **Diff integrity:** each applied spec diff was `cmp`-identical to its approved patch before staging, and a `.scratch/` script confirmed `git show` matched after each commit. QA confirmed both records byte-identical to `git show` and to the proposals.
- **Assert clean:** PASS after every QA run (`e8ce1be`, `741489a`, `4b90629`, `6dd32e6`).
- **#9 body edit:** a `.scratch/` script confirmed exactly five lines changed before `gh issue edit`.

## Proposed AGENTS.md changes

None in this issue. Later, with #31: the Environment line for the Compose dev container, and a pointer to `_docs/docker-runbook.md`.

## Temporary changes

None. No process was started and nothing was installed. `make clean-scratch` ran; `.scratch/` is empty.

## Permission review

- Read-only (propose allowing): none.
- Writes to the record (keep asking): none stopped. The `gh issue comment`, `gh issue create` and `gh issue edit` calls all ran without stopping.
- Risky (propose denying): none.
- Proposed `opencode.json` and `.claude/settings.json` changes: none.
- Sources: every PM, Engineer and QA comment says "none". The orchestrator had none. Two calls (SendMessage and `gh issue comment 23`) failed twice with a transient permission-check error, not a denial, and succeeded when retried after the human said to continue.

## Interruptions

- The transient permission-check failure above paused the session once; nothing had changed in the meantime.

## Unrelated problems noticed but not fixed

- `make verify` against `origin/main` warns about 7 removed assertions in `frontend/src/test/vulntriage.test.tsx` from earlier unpushed frontend commits; the human needs a reason for each when pushing.

## Follow-ups for the next session

- **Push:** about 30 local commits are waiting for the human's review and push from the clean clone.
- **Roadmap step 8:** #23 (API contract), with inputs in 6301758496 and #41's PM comment.
- **#31 (step 16):** the human sets up the Compose dev container using `_docs/docker-runbook.md` section 1, about 1-1.5 hours.
- **Step 10 inputs** are recorded in the roadmap.
