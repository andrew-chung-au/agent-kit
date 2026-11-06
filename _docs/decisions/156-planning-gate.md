# Decision: add a planning procedure and a spec definition of ready

Issue #156 (Heavy). The human approved this record in a comment on #156 (body sha256 `055ae078cc69029cf332782d90fcd6e7407a66fcc4e3b05631010026822109e9`), copied here from the issue body.

- **Decision:** Add `procedures/planning.md`, linked from `process.md` Planning the way `verify.md` is linked from the Lifecycle. It holds a short planning flow (problem framing, users and journeys, stories with acceptance criteria, MoSCoW scope with explicit non-goals, a brief risk pass) and a definition of ready for the spec: problem and core assumption, named users, at least one end-to-end journey, requirements that acceptance criteria can be derived from, an explicit scope boundary, an explicit non-goals list, and listed invariants. `process.md` Backlog says the PM confirms the definition of ready in its backlog-proposal comment before proposing issues. If an item fails, the PM names it, proposes the spec change (the spec stays human-owned, the human approves) and creates no implementation issues until the spec passes. One item may be marked not applicable only if the PM states why in that comment; silence is not an exemption. The docs index and README list the new procedure. Enforcement is by role-reading (the orchestrator and PM read the process rule), not a script or hook.
- **Reason:** The kit governs how a spec becomes issues and code but not the spec itself, so a weak spec is built precisely. The reactive per-issue "Spec notes" path in `pm.md` catches spec defects late and one at a time; this adds the proactive check once, before the backlog exists.
- **Alternatives:**
  - Rely on the reactive "Spec notes" path only: late, one defect at a time, expensive rework. Rejected.
  - A script or hook that checks the spec: it cannot judge spec quality, and the kit enforces other non-scripted rules by role-reading. Rejected.
  - A hash-freeze for the spec, like the issue body hash: out of scope here; propose separately if wanted.
  - Keep the gate as a project-local extension (as in SOCBoard): works, but every project repeats it and drifts. Rejected as the kit's answer.
- **Trade-offs:**
  - The gate relies on the PM stating the check honestly and on the human reading it before approving; it can be ticked without care. The not-applicable rule (reason required) limits this.
  - One more procedure doc to keep short and in step with `process.md`. It links to the spec-ownership rules, the docs-index entry types and the roadmap/ADR split instead of copying them.
  - The seventh check (invariants) comes from the SOCBoard gate and is beyond the issue's minimum list; it is kept because the reference project found it useful.
  - SOCBoard lessons carried upstream: role-reading enforcement, the not-applicable escape hatch, and wiring through the existing reserved points (the "Read when" trigger for the spec already points at `process.md#planning`; the docs index entry). The project-specific one-line gotcha is not carried, as it is project-owned.
- **Evidence:** Issue #156 and its reference implementation section; `process.md` Backlog, Tiers and Approved text; `team/pm.md` Spec notes.
