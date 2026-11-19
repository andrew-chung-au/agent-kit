Title: Give role returns, findings, QA comments and messages to the human fixed fields, checked by a script, with a recommendation required

**What is wrong or missing**

Role returns, QA comments and messages to the human are free prose. Scripts and gates that need a fact (a verdict, whether the human is needed) have to read the prose, and that has gone wrong: in socboard the close-floor decision took about 900 words to tell a reflection from a work comment. Long returns also fill the orchestrator's context, and a finding has no fields that a rule could route on. Nothing requires a recommendation, so the human often gets a question without one.

**What you expected**

Four formats with the facts first in fixed fields and the explanation after (proposal section 5.1 to 5.4), a standard-library check script that reports missing or invalid fields, and the role files telling each role to use them. A recommendation is a required field; `none` must give a reason.

Plan fields:

- Proposed tier: heavy. These are interfaces that later scripts (issues 03, 05, 07, 11) and the gates depend on.
- Effort: E. Four formats, one script with tests, and changes to the three role files, the asking-the-human procedure and process.md. (Borderline R; the tie-break says lower for Effort, but the number of files puts it over 30 minutes.)
- Reasoning: D. An interface others depend on; must stay compatible with `agent-kit/scripts/issue-close.sh`, which reads the `QA: PASS` / `QA: FAIL` first line.
- Impact: C. A format change that breaks the first line of a QA comment would break `make issue-close`.
- Needs: issue 01a (merged): the grade vocabulary (impact, effort letters) and the numbered criteria `C<n>` that the finding format refers to.
- Runs in: sandbox.
- Debt: none.
- Touches protected `agent-kit/` files: yes.
- Files: `agent-kit/scripts/check-format.py` (new; a dataclass per format and a function reporting missing or invalid fields, no pydantic, see 5 "Why not pydantic"), `agent-kit/templates/Makefile.mk` and this repo's `Makefile` (a `check-format` target; name is a grooming proposal), `agent-kit/team/qa-engineer.md` (QA comment layout, finding layout), `agent-kit/team/software-engineer.md`, `agent-kit/team/pm.md` (role return), `agent-kit/procedures/asking-the-human.md` (message to the human), `agent-kit/process.md` (Orchestrator: role returns, report by reference), `agent-kit/claude-code/agents/*.md` and `agent-kit/opencode/agents/*.md` only if their one-line prompts need the return format, `agent-kit/installed-files.txt`, `agent-kit/CHANGELOG.md`, `tests/test_check_format.py` (new). `agent-kit/scripts/` runs live.

Acceptance criteria:

- [ ] C1. Role return (5.1): at most ten lines, with `Status:` (`done`, `blocked` or `stopped-early`), `Issue:`, `Commit:`, `Verdict:` (QA only), `Findings:`, `Decisions:`, `Needs the human:`, `Recommendation:`, `Detail:` and `Checkpoint:`. Every role file says to return it.
  Check: `tests/test_check_format.py` validates the 5.1 example as valid and refuses an 11-line return and one without `Recommendation:`; read the three files under `agent-kit/team/`.
- [ ] C2. Finding (5.2): an id `F-<issue>-<n>`, then `impact:` (`L`, `M`, `C`) and `effort:` (`S`, `R`, `E`) in the vocabulary of `customizing.md` (issue 01a), `scope:` (`in`, `out`), `criterion:` (a criterion id `C<n>` from the task template, or `none`), `category:` (`defect`, `debt`, `standard`; the list is a grooming proposal), `group:` (a slug), `related:` (a finding id or `none`), then `Recommendation:`, `What:` and `How found:`.
  Check: `tests/test_check_format.py` accepts the 5.2 example; refuses `impact: medium`, a missing `scope:` and an id not matching `F-<digits>-<digits>`.
- [ ] C3. QA comment (5.3): first line unchanged, `QA: PASS` or `QA: FAIL`, with the commit; then `Findings: <n fail> / <n log>`, the findings in the 5.2 form, the criteria checklist, Verify, then detail. `qa-engineer.md` shows the layout.
  Check: `tests/test_issue_close.py` still passes unchanged (gates read the first line); `tests/test_check_format.py` accepts a full example and refuses one whose `Findings:` counts don't match the findings listed.
- [ ] C4. Message to the human (5.4): first line `Needs you:` with counts, then one line per decision point and per ship-or-fix finding, each with `Recommended:`, then a `Status:` line. `asking-the-human.md` shows it and keeps its existing approval-request and decision-question layouts for the detail.
  Check: read `agent-kit/procedures/asking-the-human.md`; `tests/test_check_format.py` refuses a decision line without `Recommended:`.
- [ ] C5. A recommendation is required in every format; `none` is valid only with a reason (`Recommendation: none, because ...`). Refused: `Recommendation: none` alone, and an empty value.
  Check: `tests/test_check_format.py` refusal cases.
- [ ] C6. `make check-format KIND=<return|finding|qa|message> FILE=.scratch/<name>` prints `ok` or one line per problem, and exits non-zero on a problem. It reads only the file given, as data.
  Check: run it on the 5.1 to 5.4 examples saved under `.scratch/`; each prints `ok`.
- [ ] C7. Standard library only; no new dependency.
  Check: `tests/test_check_format.py` imports the script with `python3 -I`; read its imports.

Out of scope: the status line (5.5, issue 11a), the human-task header (5.6, issue 06), how impact, effort and scope route a finding (issue 03a), decision-point ids and weights (issue 05; this issue only validates the `D-<issue>-<n>` shape).

Split: none.

**Evidence**

- Proposal sections 2.3 (structured first, prose second), 5 (all subsections, and "Why not pydantic"), 8 (no new dependency).
- Proposal section 1, "What didn't work": gates that read comment prose; the socboard close-floor decision took about 900 words to tell a reflection from a work comment.
- socboard's findings kept per issue with a group (`socboard/_docs/records/`), the model for the finding fields.
- Existing gate on the first line: `agent-kit/scripts/issue-close.sh` (reads `QA: PASS` / `QA: FAIL`).
