# Plan a spec

A light guideline for taking an idea to an approved `_docs/specs.md`, and the gate the spec must pass before the PM builds a backlog from it. Not up-front design: a few lines per step are enough. The spec stays human-owned and the human approves its text (`process.md`, Planning); the docs-index entry types and the roadmap and ADR split apply as written. Order and status go in a roadmap, revisitable choices in decision records, acceptance criteria on issues. Don't give any of them a second home here.

**When:** drafting or revising the spec, and before the PM proposes issues from it.

1. **Problem:** what is wrong now, for whom, and the one core assumption the spec rests on.
2. **Users and journeys:** name the users, then write at least one end-to-end journey concrete enough to derive tests from.
3. **Stories:** requirements phrased so acceptance criteria can be written against them, such as "WHEN a user submits an empty form THE SYSTEM SHALL show which fields are missing." One SHALL with a Given/When/Then case, or any testable form, is fine.
4. **Scope:** rank with MoSCoW (must, should, could, won't), state the scope boundary, and list the non-goals.
5. **Risks:** a short pass: what could make this wrong or expensive, and the invariants that must always hold.

## Definition of ready

The minimum before a backlog is built from the spec:

- [ ] A stated problem and core assumption.
- [ ] Named users.
- [ ] At least one end-to-end journey.
- [ ] Requirements that acceptance criteria can be derived from.
- [ ] An explicit scope boundary.
- [ ] An explicit non-goals list (a heading with nothing under it fails).
- [ ] Listed invariants.

**The PM confirms it** in the backlog-proposal comment, item by item, before proposing issues. One item may be marked not applicable only if the comment says why; silence is not an exemption. The human reads that confirmation before approving. No script computes it.

**Not ready:** name each failed item, propose the spec change that satisfies it (the human approves it), and create no implementation issues until the spec passes. Example that must be refused: a spec with no non-goals and no scope boundary gets spec changes proposed first, never issues.

## Plan review

Before the human approves a groomed plan:

- [ ] The intent matches what was asked.
- [ ] Nothing extra crept into scope.
- [ ] Each requirement is observable and testable.
- [ ] Each has a case, including an awkward one.
- [ ] The case the human cares about most is covered.
- [ ] What is missing is named.
- [ ] The human would accept exactly this and nothing more.
