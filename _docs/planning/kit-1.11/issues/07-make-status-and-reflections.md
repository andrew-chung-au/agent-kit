Title: Replace the session summary with make status, the Close comment and reflection files

**What is wrong or missing**

The session summary costs about 890 words per issue and mostly repeats what the issue thread, the PR and CI already hold. Parallel sessions write conflicting summaries. Reflections live in issue comments, where gates that read comments have to tell them apart from work comments (socboard's close-floor decision took about 900 words to do that). The human still has no one command that shows where things stand.

**What you expected**

Proposal 7.2 and 3.8: `make status` gives the current state from GitHub and the repo, including the spec version the start-of-session check needs; the Close comment keeps what only the session knows; each role's reflection is a file under `_docs/records/reflections/`; the session summary is retired, with every job it does today moved somewhere named or dropped on purpose.

Filed as two issues (split approved by the human on 2026-11-19), 07a then 07b, after issues 05 and 06.

Plan fields for the whole:

- Proposed tier: heavy (decided by the human on 2026-11-19: it removes a Definition of done item and changes the sweep's input and the start-of-session spec check).
- Effort: E across the two.
- Reasoning: N.
- Impact: M. A missed job of the summary would be lost silently; 07b's C3 lists each one.
- Needs: issue 05 (merged: `make decisions`) and issue 06 (merged: `make human-tasks`), which `make status` prints. Filed after both.
- Runs in: sandbox (GitHub reads through `agent-kit/scripts/github_api.py`; the read-only token is enough).
- Debt: none.
- Touches protected `agent-kit/` files: yes; also `AGENTS.md` (Project settings, the Session summaries line) and this repo's `Makefile`.

### 07a: reflections become files; the sweep reads them

Grades: Effort R, Reasoning N, Impact M. Needs: issue 05, issue 06 (merged; filing order). Tier: heavy.

Files: `agent-kit/templates/reflection.md` (new), `agent-kit/procedures/session-summary.md` (Reflection section points to the files), `agent-kit/procedures/sweep.md` and both `skills/sweep/SKILL.md` copies, `agent-kit/process.md`, `agent-kit/CHANGELOG.md`, `tests/test_session_summary.py`, `tests/test_sweep.py`.

- [ ] C1. Each role that worked on the issue writes `_docs/records/reflections/<issue>-<role>.md` from the new template: what slowed it, what nearly went wrong, one proposed change (file, expected effect, how measured). A role with nothing to report writes one line saying so. Reflections are never posted as issue comments.
  Check: read `agent-kit/templates/reflection.md` and `process.md`; a template test asserts the three questions.
- [ ] C2. The sweep reads the reflection files added since the last sweep instead of the summaries' Reflection blocks.
  Check: read `agent-kit/procedures/sweep.md`; `tests/test_sweep.py`.

### 07b: make status, the Close comment, retire the session summary

Grades: Effort E, Reasoning N, Impact M. Needs: issue 07a (merged). Tier: heavy.

Files: `agent-kit/scripts/status.py` (new), `agent-kit/templates/Makefile.mk` and this repo's `Makefile` (`status` target with `DAYS=`), `agent-kit/process.md` (Start of every session step 2, Lifecycle step 8, Definition of done), `agent-kit/procedures/session-summary.md` (retired), `agent-kit/templates/session-summary.md` (retired), `agent-kit/templates/docs-index.md` (takes the file-naming rules), every doc that says "named as in `procedures/session-summary.md`" (`agent-kit/templates/human-task.md`, `agent-kit/procedures/sweep.md`, `_docs/index.md` and others the Engineer finds), `agent-kit/procedures/orchestrator-comments.md` (Close comment fields), `agent-kit/templates/AGENTS.md.template` (Session summaries setting), `agent-kit/installed-files.txt`, `agent-kit/CHANGELOG.md`, `tests/test_status.py` (new), `tests/test_session_summary.py`, `tests/test_orchestrator_comments.py`, `tests/test_issue_close.py`.

- [ ] C1. `make status` prints open issues by state (grooming, approved, building, in QA, waiting), what merged or was committed in the last `DAYS` days (default 7; a grooming proposal), open decision points (from issue 05), open human tasks (from issue 06), and failing CI. It is read-only and refuses a `DAYS` that isn't a positive integer.
  Check: `tests/test_status.py` with the fake GitHub API (`tests/fake_gh_rest.py`); refusal case `DAYS=abc`.
- [ ] C2. `make status` prints the spec version: the last commit that changed `_docs/specs.md`, or `none`. `process.md` Start of every session step 2 compares it with the `Spec version:` line of the latest Close comment instead of reading the last summary.
  Check: `tests/test_status.py` in a fixture repo with and without a spec; read `process.md` Start of every session.
- [ ] C3. Every job the summary does today has a stated outcome:
  - Spec version: printed by `make status` (C2) and recorded in the Close comment.
  - `make clean-scratch` record: a line in the Close comment.
  - Launch usage lines: dropped. What a per-launch usage figure means, and where it could come from, is issue #191.
  - Reflections: files (07a).
  - File-naming rules (`<timestamp>-<kind>-<slug>.md` and the kinds) that other docs cite as "named as in `procedures/session-summary.md`": moved to `templates/docs-index.md` (Entry types), and every citing doc points there.
  Check: a `.scratch/` script searches `agent-kit/` and `_docs/` for `session-summary` and lists each hit; none is a live instruction to write a summary or a naming pointer to the retired file.
- [ ] C4. The Close comment keeps the merge or HEAD commit, the QA verdicts, the decisions, the findings ids, the spec version and the clean-scratch line, and `make issue-close` still accepts it.
  Check: `tests/test_issue_close.py` and `tests/test_orchestrator_comments.py` pass with the new fields.
- [ ] C5. Definition of done no longer requires a session summary; `AGENTS.md.template` drops the Session summaries setting.
  Check: read `process.md` Definition of done and the template.
- [ ] C6. Upgrade note: `CHANGELOG.md` says existing `_session-summaries/` folders stay as history; nothing deletes them (deleting is the human's call).
  Check: read `agent-kit/CHANGELOG.md`.

Out of scope: a usage figure per launch (issue #191); trimming socboard and vuln-triage `_session-summaries/` to a sample of five (proposal section 11, after this lands, by the human).

Existing issues affected:
- Makes issue #142 (session-summary Date line) obsolete; its one live need, a start time for `make permission-report SINCE=`, moves to issue #18.
- Makes issue #26 (token figure in the launch-usage line) obsolete; the launch-usage line is dropped and the question about the figure joins issue #191.

**Evidence**

- Proposal sections 3.8, 7.2, 9 row 7, 12 (decided: `make status` replaces the session summary; reflections stay, as files), 11 ("Later" row for `_session-summaries/`).
- Proposal section 1: session summaries about 890 words each, duplicated by issues and PRs; 113 session summaries in socboard (`socboard/_session-summaries/`); gates that read comment prose.
- Current dependents: `agent-kit/process.md` Start of every session step 2 reads `**Spec version:**` from the last summary; `agent-kit/procedures/sweep.md` step 2 reads summaries' Reflection and Launch usage blocks; `_docs/index.md` and `agent-kit/templates/human-task.md` cite the naming rules in `procedures/session-summary.md`.
