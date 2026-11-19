Title: Groom criteria as the Engineer's and QA's shared checklist, name the standards that apply, and groom ahead with a [groomed] title prefix

**What is wrong or missing**

The Engineer and QA work from different readings of the same criteria, so disagreements surface as QA FAILs instead of wording fixes at grooming. Issue 01a gives criteria ids and `Check:` lines, but nothing yet makes the Engineer report against that list or limits QA to it. There is no register of project standards (such as the human-step format), so QA fails work on rules the issue never named. And `process.md` (Lifecycle step 2) allows grooming only the next issue, so the human labels one issue at a time and waits; socboard's human ruled for grooming two to three ahead, marked `[groomed]`, with every filed issue placed in the order.

**What you expected**

Grooming per proposal 3.3 and 3.4, using the numbered-criteria format from issue 01a (`C<n>` with a `Check:` line): the PM writes each criterion as QA's check, the Engineer fills the same checklist, QA checks that list and the listed standards; a `Standards:` line and a standards register under `_docs/standards/`; grooming up to `GROOM_AHEAD` issues ahead.

Filed as three issues (split approved by the human on 2026-11-19): 04a, 04b, 04c below.

Plan fields for the whole:

- Proposed tier: heavy. It changes the lifecycle (grooming order) and the task template every issue uses.
- Effort: E across the three.
- Reasoning: N, with 04c at D (it interacts with the approval hash and label rules).
- Impact: M. A wrong template makes grooming slower or criteria unclear, but the human's label still gates the work.
- Runs in: sandbox.
- Debt: none.
- Touches protected `agent-kit/` files: yes.

### 04a: criteria as the shared checklist

Grades: Effort R, Reasoning N, Impact M. Needs: issue 01a (merged: the criteria format). Tier: heavy.

Files: `agent-kit/team/pm.md` (write each `Check:` so QA can run it; plan review step), `agent-kit/team/software-engineer.md` (fill the checklist), `agent-kit/team/qa-engineer.md` (check the same list), `agent-kit/procedures/planning.md` (plan review checklist), `agent-kit/CHANGELOG.md`, `tests/test_role_definitions.py` or a new doc test if the wording is asserted.

- [ ] C1. `pm.md` says each criterion's `Check:` line must be something QA can run or read without asking (a command, a test name, a named file), and the plan review in `procedures/planning.md` checks it before the label is asked for.
  Check: read `agent-kit/team/pm.md` and `agent-kit/procedures/planning.md`.
- [ ] C2. The Engineer's comment lists every criterion as `C<n>: done (<evidence>)`, `C<n>: not done` or `C<n>: not checked (<reason>)`.
  Check: read `agent-kit/team/software-engineer.md`; a doc test asserts the three forms are named.
- [ ] C3. QA checks the same list and nothing that wasn't asked for; anything else goes in its risks section, as today.
  Check: read `agent-kit/team/qa-engineer.md`.

### 04b: standards register and the Standards: line

Grades: Effort R, Reasoning B, Impact L. Needs: issue 04a (merged). Tier: heavy.

Files: `agent-kit/templates/task-template.md` (`Standards:` line), `agent-kit/templates/standard.md` (new), `agent-kit/templates/docs-index.md` (standards row), `agent-kit/team/pm.md`, `agent-kit/installed-files.txt`, `agent-kit/CHANGELOG.md`, `tests/test_task_template.py`.

- [ ] C1. The template has a `Standards:` line listing the standards files that apply, or `none`. A standard is a short file under `_docs/standards/` from the new template, with a check script when the rule is mechanical.
  Check: `tests/test_task_template.py` asserts the line; read `agent-kit/templates/standard.md`.
- [ ] C2. A standard added mid-project applies to issues groomed after it, plus one audit issue for files already written. `pm.md` says so.
  Check: read `agent-kit/team/pm.md`.

### 04c: groom ahead with [groomed], every issue placed in the order

Grades: Effort R, Reasoning D, Impact M. Needs: issue 01a (merged: `GROOM_AHEAD`). Tier: heavy.

Files: `agent-kit/process.md` (Lifecycle step 2, Backlog, Approved text), `agent-kit/team/pm.md`, `agent-kit/CHANGELOG.md`.

- [ ] C1. The PM may groom up to `GROOM_AHEAD` unlabelled issues ahead of the one in progress (replacing "Groom only the next issue" in Lifecycle step 2), adds the `[groomed]` prefix to each title, and records each body hash as now. The human labels them in one sitting.
  Check: read `agent-kit/process.md` Lifecycle step 2; `tests/test_approval_freeze.py` still passes (the hash rule is unchanged).
- [ ] C2. Refused: grooming beyond `GROOM_AHEAD`, and grooming an issue that is not placed in the agreed order. The orchestrator enforces it by reading the order and counting `[groomed]` unlabelled issues before launching the PM; no script does (`process.md` says so).
  Check: read `process.md`; the rule names its enforcement.
- [ ] C3. Every filed issue, follow-ups included, is placed in the order (a position in the backlog list) when it is filed.
  Check: read `process.md` Backlog and `pm.md`.
- [ ] C4. A title change for `[groomed]` does not invalidate the approval (the hash covers the body only; a title change is a note, as today).
  Check: read `process.md` Approved text.

Out of scope (all three): the criteria format itself (issue 01a); per-issue planning lines (grades, `Runs in:`, `Needs:`, `Debt:`; issue 08b); the human-step standard (issue 06); the findings log (issue 03b).

**Evidence**

- Proposal sections 2.5 (the Engineer and QA work from one list), 3.3, 3.4 (Standards), 9 row 4.
- Proposal section 1, socboard rulings: grooming 2 to 3 ahead with a `[groomed]` title prefix; every filed issue placed in the order; gates on mechanics.
- `socboard/.kiro/steering/backlog-order.md` and `real-dependencies-only.md` (the order rulings).
- Current rule to replace: `agent-kit/process.md` Lifecycle step 2, "Groom only the next issue in the agreed order, not a second unlabelled issue while the first waits for the label".
