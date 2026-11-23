## Why

The problem in one or two sentences, with evidence: where it showed up and what it cost. Not the mechanism or the solution; Goal says what should be true when this is done.

## Goal

One or two sentences on what should be true when this is done.

## Acceptance criteria

Number each criterion `C1`, `C2`, ... up by one, and give it an indented `Check:` line saying how it is verified. Once the issue is approved, a criterion keeps its id: a removed criterion leaves a gap, and a new one takes the next unused number.

- [ ] C1. A statement you can check by looking at the result
  Check: how it is verified: a command, a test name, or a reading of a named file
- [ ] C2. One line per case, including the awkward ones
  Check: the test that covers each case
- [ ] C3. For each limit on what something may do: how it's enforced, and a case that must be refused
  Check: the test or command that shows the refusal

## Out of scope
- Something that does not belong in this task, moved to #TASK-NUMBER

## Design

Optional. Fill this in only when the issue makes a real design choice: the choice and one line of reason, linking to an ADR if one exists instead of copying it. "None" is the normal answer, and a Light issue or a typo fix leaves the section out. A Heavy issue's choice also needs a `## Decision record`; this section alone does not satisfy that gate.

## Constraints
- Files this should stay inside
- Libraries to use
- Guidelines to follow
- Fixed text or values, and where each comes from (the spec, outside material, or a grooming decision)
- Proposed tier: light, standard or heavy, with a one-line reason and the paths the change is expected to touch (a proposal; `approved` approves a Standard or Heavy one, a Light one needs the human's `tier:light` label, and a `tier:` label overrides)

Standards: the file names in `_docs/standards/` of the standards that apply (for example `human-steps.md, commit-style.md`), or `none`
