Title: Weight decision points, keep a ledger of the ones the agent continued past, and answer them per point

**What is wrong or missing**

Every question waits for the decision point at the end of the issue, or stops the work mid-issue. There is no way for the agent to take its recommended option on a small choice and keep going, with a record the human can reverse later. The human answers one long message with yes or no, cannot amend one question in it, and has no list of what is still open or what depends on it.

**What you expected**

Decision points as in proposal 3.6: an id and a weight, stop points versus continue points, a ledger of continued points with their rollback, a weighted budget, per-point answers, and `make decisions`.

Plan fields:

- Proposed tier: heavy. It changes when work stops for the human, and what may merge.
- Effort: E. A ledger format, a script with tests, process and asking-the-human changes.
- Reasoning: D. Stop points include security limits and irreversible actions; the merge rule interacts with branching.
- Impact: C. A wrong stop/continue rule lets an agent continue past a security, money or irreversible decision.
- Needs: issue 01a and 01b (merged): `DECISION_BUDGET`, and session rulings (a ruling such as "decision budget 8" lasts for that issue only). Issue 02 (merged): the message-to-the-human format (5.4).
- Runs in: sandbox.
- Debt: none.
- Touches protected `agent-kit/` files: yes.
- Files: `agent-kit/process.md` (Orchestrator, Lifecycle step 7), `agent-kit/procedures/asking-the-human.md` (decision point layout, per-point answers), `agent-kit/team/*.md` (who opens a point), `agent-kit/scripts/decisions.py` (new), `agent-kit/templates/decisions-pending.md` (new ledger template), `agent-kit/templates/Makefile.mk` and this repo's `Makefile` (`decisions` target), `agent-kit/installed-files.txt`, `agent-kit/CHANGELOG.md`, `tests/test_decisions.py` (new).

Acceptance criteria:

- [ ] C1. A decision point has an id `D-<issue>-<n>`, a weight 1 to 3 by blast radius (1: a choice inside one file; 2: an interface or doc structure others use; 3: something many issues build on) and a recommendation per question.
  Check: read `asking-the-human.md`; `tests/test_decisions.py` refuses an entry with weight 0 or 4 or without a recommendation.
- [ ] C2. Stop points always wait for the human: the spec, security limits, money, irreversible or outside-the-repo actions, launching a weaker variant than the agreed reasoning level, a change of approach from the patchwork guard, shipping a failing finding.
  Check: read `process.md`; the list matches 3.6.
- [ ] C3. Continue points: the agent takes its recommended options, logs the point in `_docs/planning/decisions-pending.md` with its rollback and what depends on it, and keeps working. New work stops starting when the open weight reaches `DECISION_BUDGET` (default 3; 0 means every point stops).
  Check: `tests/test_decisions.py`: open weight 3 with budget 3 reports "budget reached"; open weight 2 with budget 3 reports "within budget"; with budget 0 a new continue point is refused and reported as a stop.
- [ ] C4. Refused: logging a stop-point kind as a continue point. The ledger has a `kind:` field and `make decisions` exits non-zero on a stop kind in the continue list.
  Check: `tests/test_decisions.py` refusal case with `kind: security`.
- [ ] C5. Per-point answers: `D-12-1 approve` (all recommendations), `D-12-2 q2=B` (another option for one question), `D-12-3 reject`. Each answer closes the point and lowers the open weight; an amended or rejected point adds a rework item for the owning Engineer, listed in the ledger.
  Check: read `asking-the-human.md`; `tests/test_decisions.py` applies the three answer forms to a fixture ledger.
- [ ] C6. The rollback is the branch. In a project that works on branches, nothing that depends on an open point is merged to `main`. In a project that commits directly to `main` (as this repo does), a commit that depends on an open point is not pushed until the point is closed, and the human's push review lists the open points. (Wording approved by the human on 2026-11-19.)
  Check: read `process.md` Commits and pushes; both cases are named, keyed to the **Branching** project setting in `AGENTS.md`.
- [ ] C7. `make decisions` lists open points with weight, age and dependents, and the total open weight against the budget.
  Check: run `make decisions` on a fixture ledger in `tests/test_decisions.py`; on no ledger it prints `none`.

Out of scope: the delivery lead relaying points (issue 11a); an approval proxy for weight-1 points (proposal section 8, later).

Proposed split: none.

**Evidence**

- Proposal sections 3.6, 4.2 (`DECISION_BUDGET`), 5.4, 8 (no approval proxy yet).
- Proposal section 1: the human as relay between sessions; socboard's "wait only for a real dependency" ruling (`socboard/.kiro/steering/real-dependencies-only.md`).
- Current rule: `agent-kit/process.md` Orchestrator ("asks the human mid-issue only when the work can't continue") and Lifecycle step 7.
