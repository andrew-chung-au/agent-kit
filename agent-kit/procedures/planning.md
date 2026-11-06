# Plan a spec

A light guideline for taking an idea to an approved `_docs/specs.md`, and the gate the spec must pass before the PM builds a backlog from it. Not up-front design: a few lines per step. The spec stays human-owned and the human approves its text (`process.md`, Planning); the docs-index entry types and the roadmap and ADR split apply as written. Don't give any of them a second home.

**When:** drafting or revising the spec, and before the PM proposes issues from it.

1. **Problem:** what is wrong now, for whom, and the one core assumption.
2. **Users and journeys:** name the users; write at least one end-to-end journey concrete enough to derive tests from.
3. **Stories:** requirements that acceptance criteria can be written against, such as "WHEN a user submits an empty form THE SYSTEM SHALL show which fields are missing." One SHALL with a Given/When/Then case, or any testable form, is fine.
4. **Scope:** rank with MoSCoW (must, should, could, won't), state the scope boundary, list the non-goals.
5. **Risks:** what could make this wrong or expensive, and the invariants that must hold.

## Definition of ready

The minimum before a backlog is built from the spec:

- A stated problem and core assumption.
- Named users.
- At least one end-to-end journey.
- Requirements that acceptance criteria can be derived from.
- An explicit scope boundary.
- An explicit non-goals list (an empty heading fails).
- Listed invariants.

**The PM confirms it** in the backlog-proposal comment, item by item, before proposing issues. One item may be marked not applicable only if the comment says why; silence is not an exemption. The human reads that confirmation before approving. No script computes it.

**Not ready:** name each failed item, propose the spec change that satisfies it (the human approves it), and create no implementation issues until the spec passes. Example that must be refused: a spec with no non-goals and no scope boundary gets spec changes proposed first, never issues.

## Plan review

Before the human approves a groomed plan:

- The intent matches what was asked.
- Nothing extra crept into scope.
- Each requirement is observable and testable.
- Each has a case, including an awkward one.
- The case the human cares about most is covered.
- What is missing is named.
- The human would accept exactly this and nothing more.
