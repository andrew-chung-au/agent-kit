# Decision: an optional Design section in the issue template

Issue #160 (Heavy). The human approved this record in a comment on #160 (body sha256 `7d881f7b3b4316364655c0dd4711db370b46383224e85e626bb611bf791eb8e2`), copied here from the issue body.

- **Decision:** Add an optional `## Design` section to `templates/task-template.md`, between Out of scope and Constraints. It holds the design choice and one line of reason, or "none", which is the normal answer. It links to an ADR when one exists instead of copying it. A Light issue, or any issue with no design choice, omits it, and the template says so. The five required sections stay required. `team/pm.md` says when to fill it and links to the Tiers rule for when a choice needs a Heavy ADR instead. A Heavy issue whose choice sits only in `## Design` with no `## Decision record` is not approved; this is enforced by the existing Heavy ADR gate and the orchestrator's hash check in `process.md`, which this issue does not change.
- **Reason:** A Standard issue that makes a real design choice has no agreed place to say so, so the reasoning ends up in an Engineer comment or is lost. OpenSpec's per-change `design.md` shows the need; a section in the issue body meets it without a new file per issue (research in #14).
- **Alternatives:**
  - A separate design file per issue: rejected, a second home next to the issue and extra cost for small issues.
  - An ADR for every Standard issue: rejected, ADRs are for revisitable choices and are heavier.
  - Do nothing: rejected, the reasoning is lost.
- **Trade-offs:**
  - A PM may fill the section by habit; "none is normal" in the template limits that.
  - A choice can be recorded in two places (Design and an ADR); the rule is to link, not copy.
  - The section is in the issue body, so it is covered by the body hash and a later edit needs re-approval.
  - Tests that count template sections needed updating (`tests/test_task_template.py`, `tests/test_issue_intake_form.py`).
- **Evidence:** #160; `_docs/records/2026-11-06T0330Z-measure-spec-driven-frameworks.md`; `process.md` Tiers.
