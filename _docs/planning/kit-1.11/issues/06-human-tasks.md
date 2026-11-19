Title: Give human tasks a header, a make human-tasks list, rendered steps and an archive for done one-off tasks

**What is wrong or missing**

socboard raised 45 human tasks in 12 days, mostly applies and deploys, and found their prerequisites one by one. A task file doesn't say what it blocks, how urgent it is, whether it recurs or how long it takes, so the human can't tell which to do first. Steps are hand-formatted, and QA failed work on step formatting. Done tasks stay in `_human-tasks/` next to open ones (this repo has six there now), so the folder doesn't show what is still to do.

**What you expected**

Human tasks as in proposal 7.1 and 5.6: a one-line header, a list command, steps written as data and rendered by a script, and an archive for done one-off tasks.

Plan fields:

- Proposed tier: standard. A template, a script and the docs that point at them; no change to gates.
- Effort: E. Two make targets (`human-tasks`, `human-task-render`), a step data format, template and doc changes, tests.
- Reasoning: N. Known options; the safety wording in the template (no secrets, refusal tests) must survive the change.
- Impact: M. A wrong list order or render wastes the human's time; a lost safety line in the template would be C, covered by C6.
- Needs: none (proposal section 9: runs in a parallel lane). If issue 02 has merged, the header check may reuse `check-format.py`; it doesn't wait for it.
- Runs in: sandbox.
- Debt: socboard's `_human-tasks/` trim waits for this issue (proposal section 11, "Later" row).
- Touches protected `agent-kit/` files: yes.
- Files: `agent-kit/templates/human-task.md` (header, steps as data), `agent-kit/scripts/human-tasks.py` (new: list and render), `agent-kit/templates/Makefile.mk` and this repo's `Makefile` (`human-tasks`, `human-task-render`), `agent-kit/process.md` (Orchestrator, Human tasks), `agent-kit/procedures/session-summary.md` (the naming rules for the archive path; issue 07b later moves them to `templates/docs-index.md`), `agent-kit/templates/docs-index.md` (archive row), `agent-kit/installed-files.txt`, `agent-kit/CHANGELOG.md`, `tests/test_human_task.py`, `tests/test_human_tasks_list.py` (new).

Acceptance criteria:

- [ ] C1. Each task file starts with the 5.6 header: `Blocks: <issues or none> | Priority: <1-3> | Kind: one-off|recurring | Time: <n> min | Status: open|done`, and a recurring task has a `Recurs:` line (`after each dev container rebuild`, `monthly`) and a last-done date.
  Check: read `agent-kit/templates/human-task.md`; `tests/test_human_tasks_list.py` refuses a header missing `Kind:` and a recurring task without `Recurs:`.
- [ ] C2. Steps are written as data: each step has `command`, `expected` and `if_different` (the data format, JSON in a fenced block or a sidecar `.json`, is a grooming choice for the human; JSON keeps it standard-library). `make human-task-render FILE=_human-tasks/<name>` writes the rendered steps into the file's Steps section and refuses a step missing a field.
  Check: `tests/test_human_tasks_list.py` renders a fixture and compares with expected text; refusal case for a step without `expected`.
- [ ] C3. `make human-tasks` lists open tasks, blockers first, ordered by how close the work they unlock is (the issue order), then recurring tasks that are due from their last-done date.
  Check: `tests/test_human_tasks_list.py` with three fixtures (a blocker, a non-blocker, a due recurring task) asserts the order.
- [ ] C4. A done one-off task moves to `_docs/records/human-tasks/` with its result table filled; `_human-tasks/` holds only open tasks and recurring ones, which record each run.
  Check: read `agent-kit/process.md` and the index template; `make human-tasks` warns on a `Status: done` one-off still in `_human-tasks/`.
- [ ] C5. A task goes to the human only for what the sandbox, CI and the agent can't do, and the file says why (a `Why the human:` line).
  Check: read the template; `tests/test_human_task.py` asserts the line is present.
- [ ] C6. The template keeps its existing safety rules unchanged in meaning: no secrets or environment printing in examples, the `Refusal test:` and `Risk:` lines.
  Check: `tests/test_human_task.py` (existing wording checks) still passes.
- [ ] C7. The script reads task files as data and never runs a step's `command`.
  Check: read `agent-kit/scripts/human-tasks.py`; a test with a fixture whose command is `touch .scratch/should-not-exist` asserts the file is not created.

Out of scope: planning's prerequisites list that batches tasks early (issue 08a); moving this repo's existing `_human-tasks/` files (the human decides, after this lands).

Proposed split: none.

**Evidence**

- Proposal sections 5.6, 7.1, 9 row 6, 11 ("Later" row for `socboard/_human-tasks/`).
- Proposal section 1: socboard human tasks, 45 in 12 days, mostly applies and deploys; prerequisites found one by one. socboard ruling: the step format for human instructions (`socboard/.kiro/steering/evidence-and-steps.md`).
- vuln-triage kept a single `vuln-triage/_docs/human-tasklist.md` and `cloud-tasklist.md`, the list view this issue adds.
