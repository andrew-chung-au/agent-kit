# Planning: critical review of the SOCBoard plans after the kit 1.10 import

**Date:** 2026-11-09T12:26Z (UTC)
**Spec version:** 2394da6

## What changed and why

- Checked the dev container is ready for the next stages: Node 24.22.0, npm, uv 0.13.6 and Python 3.12 are present, so a frontend can be built. Postgres is not available yet: `.devcontainer/` is the single-container recipe, and the kit's Compose variant (`_docs/agent-kit/environments/local-sandbox/compose/`) has not been copied in. Docker is missing in the container, as expected.
- Reviewed the planning done under kit 1.09 (spec, roadmap 1, backlog drafts, local readiness gate) against kit 1.10's `procedures/planning.md` and the course task and rubric.
- The human rejected detailed planning of later stages (rolling-wave planning, which kit 1.10's "not up-front design" supports) and an early Postgres switch (parts slot in behind a stable connection point). Both were accepted; the review was cut down to what Core needs plus an outline of the later phases.
- Spec (`2394da6`): the release is the whole graded project in three phases aiming for full marks. Core is detailed; Deploy and DevOps are outlined and detailed when the phase before is done; Target Enhancements become Could. Core gaps closed: ingest text fields and API key, severity scale and asset-criticality source, two seeded Analysts, a definition of "open", claim sets owner only, single owner under concurrent claims, append-only audit.
- Kit alignment (`2587282`): AGENTS.md and the docs index point at the kit's definition of ready; the local `spec-readiness.md` stopgap is deleted (human approved).
- Follow-ups (`d15ba98`): README states 5 s instead of `[N]`; backlog #6 sort tiebreak and #7 atomic claim with a concurrency test; roadmap 1 stale "pending approval" fixed and the later phases referenced.

**What I learned:** a modular "swap the part later" plan holds as long as the behaviour behind the interface is pinned in a test; the concurrent claim is the one place SQLite and Postgres differ for this app.

## Reflection

### Orchestrator

**What slowed you down (evidence):** the first review proposed detailed operations requirements, roadmaps 3 and 4, and an early Postgres switch; the human rejected these as over-planning and the review had to be cut down.
**What nearly went wrong or was blocked:** nothing blocked. The spec is protected and human-owned, so no spec text was written until the human approved it.
**One proposed change (file, expected effect, measure):** `_docs/agent-kit/procedures/planning.md`: say outright that later phases are an outline (one line each) until the phase before them is done. Expected effect: fewer over-planned proposals. Measure: proposals rejected as over-planning in planning sessions.

### PM

unknown (role not asked)

## Launch usage

none

## Files created or modified

- `_docs/specs.md`
- `README.md`
- `AGENTS.md`
- `_docs/index.md`
- `_docs/planning/core-backlog.md`
- `_docs/planning/roadmap-1-core.md`
- `_docs/planning/spec-readiness.md` (deleted)
- `_session-summaries/2026-11-09T1226Z-planning-orchestrator-spec-review.md`

## Decisions made by the human

- Release scope: the whole graded project, with Deploy and DevOps in the goals to score full marks, but outlined, not detailed, until Core is done.
- Postgres: keep SQLite first and swap later, as the approved stack record says; no new decision record.
- Approved the Core spec fixes, README fix, backlog #6 and #7 criteria, AGENTS.md and index repoint, and deleting `_docs/planning/spec-readiness.md`.

## Mismatches with the spec or design docs

- Backlog drafts #3, #4 and #5 do not yet reflect the revised spec (two Analysts, ingest API key and text fields, asset inventory). Left for the PM's backlog review.
- Backlog #1's first criterion (approve the stack record) is already met.
- No backlog item covers the login UI, wiring the claim, transition and notes UI to the real API, an OpenAPI contract (`02_development.md` step 5), or frontend tests. Raised in the review; for the PM's backlog review.

## Commands to validate

**Verify:** `make verify` (passed before the commits)
**Decisions:** `make decisions`

## Proposed AGENTS.md changes

none (the repoint was made this session, approved)

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- `make kit-check` reports drift on `.github/workflows/verify.yml` and "modified" for `blueprints.md`, `process.md`, `team/software-engineer.md`, `claude-code/settings.json` and `opencode/opencode.json`; not diffed this session.
- AGENTS.md Commands still say Run, E2E and New migration "none"; migrations will need a tool (likely Alembic), which is a dependency needing approval.
- `_human-tasks/2026-11-06T0219Z-human-task-orchestrator-decide-upstream-kit-issues.md` still refers to the deleted `spec-readiness.md`; left as a historical record.

## Follow-ups for the next session

- PM: check the spec against the definition of ready in `_docs/agent-kit/procedures/planning.md`, confirm it item by item in the backlog proposal, update the backlog drafts to the revised spec, propose the Core issues and then archive `core-backlog.md`.
- Before Phase 2: copy the Compose variant into `.devcontainer/` from a clean clone (human), then detail the Deploy phase in the spec.
- Settle these process edits before the first Ponytail baseline issue is groomed (roadmap 2, task 2).
