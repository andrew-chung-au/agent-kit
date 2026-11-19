# Roadmap 2: Ponytail trial

Order and status only. Method and criteria: `_docs/planning/ponytail-trial-protocol.md`. Decision (approved): `_docs/decisions/2026-11-06T0024Z-ponytail-trial.md`.

- **Status:** shelved, 2026-11-12. This is a measurement exercise to quantify ponytail's benefit. It was considered and its plumbing built (tasks 3 to 5), but it was not fully implemented: no shadow review ran (protocol Amendment 3). It is kept for review.
  - **In its place:** ponytail is used in normal work, and a light before-and-after measurement (issues #8 to #12 without it; issues claimed after it is switched on, with it; #13 in neither) gives the human figures to review. The decision record holds the method: `_docs/decisions/2026-11-12T2300Z-ponytail-adopt.md`, "Measurement for review".
  - **This plan** is kept as it was, so the full controlled measurement can be picked up again if that review is promising.
- **To resume:** the human decides to resume. Then:
  1. Take the ponytail skill out of normal Engineer use, so control issues are unprimed again (`AGENTS.md`, Project settings).
  2. Write a new epoch-start record from the current commit, as in `_docs/records/2026-11-10T1506Z-measure-ponytail-epoch-1-start.md`.
  3. Restart at task 6 (Phase 1). The protocol, metrics script (`make ponytail-metrics`), reviewer role and vendored files are all still in place.
  4. Land, or deliberately hold, the process edits in `_docs/planning/epoch-batch-1/` first, so they do not split the new epoch.
- **Goal:** Learn whether, and for which function, ponytail improves how this project's agents work, measured against our own baseline.
- **Tasks, in order** (file as issues when groomed; numbers added then):
  1. Human habit, starting now: record tool and model on every `Launch usage` line. The `Assisted-by` commit line is already required.
  2. Settle every process edit before the first baseline issue is groomed: a later change that could alter a control issue starts a new epoch.
  3. (#23) Phase 1 plumbing: hold the pinned `ponytail-review` file verbatim at a path no tool auto-discovers (not `.claude/skills/`, `.opencode/skills/`, `.kiro/skills/` or `.agents/skills/`; OpenCode reads the first and last too), for the reviewer role to load by path. Confirm each tool you use can read it. Keep the core `ponytail` skill out of the repo for now. Both skills' descriptions can trigger on ordinary work, which would contaminate control issues.
  4. (#24) Metrics script and make target, computing every figure from git and GitHub only.
  5. (#25) Reviewer role: one role file, thin pointers in each tool, read-only; `make assert-clean` after each run.
  6. Phase 1: baseline plus shadow review on at least 5 qualifying issues; gate review at the sweep.
  7. Phase 2, after the gate: install the core `ponytail` skill where tools discover it, only in tools that passed, and add the `ponytail: on` rule to AGENTS.md (protected). Then Phase 3 as the protocol says.
- **Not in this phase:** installing any ponytail plugin; scope, debt-ledger and audit functions (each needs its own trial after the first two are decided).
- **Archive when:** the Phase 3 gate decision record exists.
