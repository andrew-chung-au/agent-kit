Title: Add a consult stage before planning, and give each planned issue grades, Debt, Runs in and criterion-level Needs lines

**What is wrong or missing**

Planning starts from the human's brief and writes the spec straight away; no stage questions the brief, maps the environment or lists everything the finished project will need from the human. In socboard, prerequisites (accounts, servers, secrets, CI access) were found one by one as 45 human tasks. Planned issues carry no grade, so nothing says whether to split one, how to fill lanes or which strength of subagent to launch. Dependencies are on whole issues, so a dependent issue waits for docs it doesn't need. Nothing says where an issue should run (sandbox, CI, the human, cloud), and tech debt an issue creates on purpose isn't tracked.

**What you expected**

Proposal 3.1 and 3.2: a consult stage that writes `_docs/planning/consult.md`, and per-issue planning lines: `Effort:`, `Reasoning:`, `Debt:`, `Runs in:`, `Needs:` (by criterion, with a type) and `Standards:` (added by issue 04b). The grades use the vocabulary already in `customizing.md` (issue 01a).

Plan fields:

- Proposed tier: heavy. Changes the planning procedure and the task template; reasoning variants change which model runs a role.
- Effort: E (split below).
- Reasoning: D. Reasoning variants interact with `STEP_UP` (issue 03a) and the stop rule for a weaker variant (issue 05); criterion-level `Needs:` interacts with branches.
- Impact: M.
- Needs: issue 01a (merged: settings, profiles, the vocabulary and criterion ids); per split below.
- Runs in: sandbox; checking role variants per tool needs the human in OpenCode and Kiro (a human task).
- Debt: none.
- Touches protected `agent-kit/` files: yes.
- Files: `agent-kit/procedures/planning.md` (consult stage, per-issue lines), `agent-kit/process.md` (Planning, Roles: variant per reasoning level), `agent-kit/templates/consult.md` (new), `agent-kit/templates/task-template.md` (`Effort:`, `Reasoning:`, `Debt:`, `Runs in:`, `Needs:` lines), `agent-kit/templates/roadmap.md` (effort per lane), `agent-kit/team/pm.md`, `agent-kit/blueprints.md` (Role definitions: variants), `agent-kit/claude-code/agents/` (an example variant file with a `model:` frontmatter line), `agent-kit/environments.md` (environment map pointer), `agent-kit/installed-files.txt`, `agent-kit/CHANGELOG.md`, `tests/test_planning_gate.py`, `tests/test_task_template.py`, `tests/test_role_definitions.py`.

Acceptance criteria:

- [ ] C1. `procedures/planning.md` has a consult stage before the spec, producing `_docs/planning/consult.md` from a new template with five sections: Questions (each with options and a recommendation), Risks and challenges (with a simpler way where one exists), the Environment map, Prerequisites for the end state (ordered by when each blocks), and Recommended settings (a profile and changes, issue 01a).
  Check: read `agent-kit/procedures/planning.md` and `agent-kit/templates/consult.md`; `tests/test_planning_gate.py` asserts the five headings.
- [ ] C2. The environment map lists what the human has (local sandbox and what it can run, CI, Kiro, cloud sessions, servers, accounts), what each issue type needs, and recommends dev container upgrades where a tool is missing (for example Terraform or Docker).
  Check: read the template's Environment map section.
- [ ] C3. The task template has `Effort: S|R|E`, `Reasoning: B|N|D`, each with a one-line reason, `Debt:` (one line or `none`), `Runs in: sandbox|ci|human|cloud` and `Needs:` lines. `ci` is suggested only when the sandbox lacks a tool and no dev container upgrade is planned.
  Check: `tests/test_task_template.py` asserts each line and its allowed values.
- [ ] C4. `Needs:` names a criterion and a type: `Needs: #12/C3 (built)`, with type `info`, `decision`, `built` (done at a commit on a branch) or `merged` (on `main`). A dependent issue may start when the named criterion shows `done` in the Engineer's checklist (issue 04a) at the right place. Documentation criteria are separate from build criteria.
  Check: read `planning.md` and `process.md`; a test refuses `Needs: #12 (built)` (no criterion) and an unknown type.
- [ ] C5. Planning sums effort per lane into a rough timeline and names which lanes need a deep-reasoning session (roadmap template).
  Check: read `agent-kit/templates/roadmap.md`.
- [ ] C6. Reasoning variants: the model is set in the project's role definitions, not in kit settings. In Claude Code a variant is a role file whose frontmatter names a stronger model; the orchestrator launches the variant matching the agreed `Reasoning:`. Launching a weaker variant than agreed is a stop decision (issue 05); a stronger one is a note. `blueprints.md` says OpenCode and Kiro have no step-up variant (free models; Kiro stays on auto), so there the agreed grade is recorded but doesn't change the launch.
  Check: read `agent-kit/blueprints.md` Role definitions and `process.md` Roles; `tests/test_role_definitions.py` accepts an optional `model:` line.
- [ ] C7. A plan never blocks work because events didn't follow it: running somewhere other than `Runs in:` is a note, not a stop.
  Check: read `process.md`.
- [ ] C8. With variants defined, issue 03a's `STEP_UP=auto` (Claude Code only) switches to the next variant up; this issue ends 03a's "auto acts as ask" fallback where a variant exists, and keeps it where none is defined. The per-tool check is recorded (Claude Code by test of the frontmatter; OpenCode and Kiro as a human task confirming no variant applies).
  Check: read `process.md`; the human task file exists under `_human-tasks/`.

Out of scope: an automatic soft stop from the usage level (issue #191); the cloud-agent profile itself (issue #52).

Split (approved by the human on 2026-11-19; each filed issue renumbers its own criteria from C1):
- 08a: consult stage and environment map (C1, C2). Tier heavy. Effort R, Reasoning N, Impact M. Needs: issue 01a (merged).
- 08b: per-issue planning lines, criterion-level Needs, lane timeline, plans never block (C3 to C5, C7). Tier heavy. Effort R, Reasoning N, Impact M. Needs: issue 04a (merged: the Engineer's checklist that `Needs:` reads).
- 08c: reasoning variants and `STEP_UP=auto` (C6, C8). Tier heavy. Effort R, Reasoning D, Impact M. Needs: issue 03a, issue 05 (the weaker-variant stop point), issue 08b (merged).

Existing issues affected: issue #52 (Kiro Web cloud profile) is the profile that adds the cloud-agent row to the environment map; this issue leaves a `cloud` row placeholder pointing to it.

**Evidence**

- Proposal sections 2.6 (run where it's cheapest), 3.1, 3.2, 3.5 (step up per tool), 9 row 8, 12 (decided: step up Claude Code only).
- Proposal section 1: socboard 45 human tasks in 12 days, prerequisites found one by one; socboard ruling "wait only for a real dependency" (`socboard/.kiro/steering/real-dependencies-only.md`); lanes that own files.
- vuln-triage's `vuln-triage/_docs/planning-process.md` and `cloud-sessions.md` (where the cloud runs were planned by hand).
