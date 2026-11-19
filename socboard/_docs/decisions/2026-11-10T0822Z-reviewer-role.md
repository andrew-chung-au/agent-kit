# Decision: Add a project-owned, read-only Reviewer role outside the kit

One file per choice that may be revisited. **Status: approved.** The human approved issue #25, whose `## Decision record` section this file copies, by adding the `approved` label on 2026-11-10 (hash `587a86234b4a49aa75def7f364e21afc1e18856bf4eb12d4d9c0a2a6e98ccae0`). Heavy tier: it adds a role and changes how agents are launched. It carries out the role the approved trial decision already allows.

- **Decision:** Add one reviewer role as a project-owned file (`_docs/team/reviewer.md`) outside the kit, with thin per-tool pointers (`.claude/agents/reviewer.md`, `.opencode/agents/reviewer.md` and `.kiro/agents/reviewer.json`, the last added after the first QA check because Kiro's documentation describes project agent files). It is read-only by tool setting where the tool supports it, and by `make assert-clean` plus instruction where it does not. The orchestrator pastes the diff into the launch message, so a tool that gives the reviewer no shell can still review.
- **Reason:** The kit makes the orchestrator the only launcher and has no reviewer; the trial needs independent review without touching kit files. Keeping the role outside `_docs/agent-kit/` keeps the kit pristine for upstream comparison.
- **Alternatives:**
  - *Put the role in `_docs/agent-kit/team/`:* drifts from the kit manifest and is protected.
  - *Let QA do the review:* QA is the control being compared.
  - *Have the Engineer self-review:* the protocol forbids a role scoring its own work.
- **Trade-offs:** In Kiro Web read-only rests on instruction and an after-the-fact check, not a permission block, and it is not confirmed that Kiro Web loads `.kiro/agents/`. The Kiro agent file has not been run in Kiro, and its read tool is not limited to particular paths. A reviewer that wrote something would be caught only by `make assert-clean`, and the human's diff review is the final check. After the second QA check the Claude Code and OpenCode pointers were tightened (the human approved on 2026-11-10) so neither gives the reviewer a shell: the reviewer works from a diff the orchestrator pastes into the launch message and cannot read other commits itself.
- **Evidence:** Issue #25; `_docs/decisions/2026-11-06T0024Z-ponytail-trial.md`; `_docs/planning/ponytail-trial-protocol.md`.
