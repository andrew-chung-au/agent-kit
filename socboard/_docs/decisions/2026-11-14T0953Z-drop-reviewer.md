# Decision: Drop the Reviewer; QA is the only review step

One file per choice that may be revisited. **Status: approved** by the human on 2026-11-14 in the orchestrator session ("just drop the reviewer"). Supersedes the Reviewer part of `_docs/decisions/2026-11-12T2300Z-ponytail-adopt.md` and the launch rule of `_docs/decisions/2026-11-10T0822Z-reviewer-role.md`.

- **Decision:** The orchestrator no longer launches the Reviewer, and no Reviewer report is posted. QA is the review step: a Medium-or-higher finding fails the verdict and goes back to the Engineer; Low findings go in the report (`.kiro/steering/delivery-pace.md` item 7). The Engineer keeps reading `_docs/vendor/ponytail/ponytail.md` at level `full`; that part of the adopt record is unchanged. The Reviewer files stay in place and unchanged, so a one-off review can be asked for by the human.
- **Reason:** A Reviewer that finds something proves little, because any extra review round finds something; the cost is speed. On #154 and #162 the Reviewer ran after a QA PASS and each time led to a fix round and a QA re-check (#162 took six launches against a minimum of two). The measurement record `_docs/records/2026-11-13T0424Z-measure-ponytail-review.md` could not show a benefit in defects: "defects found after PASS" is unknown for every issue, and its comparison is directional only.
- **Alternatives:**
  - *Keep it on every issue:* the cost above, with no measured gain.
  - *Run it on Heavy issues only:* less cost, but the same missing evidence, and a rule to maintain.
  - *Run it when QA passes but the human is unsure:* possible later, as the human's one-off request.
- **Trade-offs:** The independent look that found #154's teardown problem after a QA PASS is gone, so a gap QA misses reaches the human at the decision point and in the human's own diff review. The human's finding labels (`Finding <issue>-<n>: <label>`) stop; the review measurement of the adopt record loses its Reviewer half. If defects after merge show that QA misses things the Reviewer would have caught, revisit.
- **Not changed here (protected, needs the human's approval of the exact diff):** the Ponytail line of `AGENTS.md`, which still says the orchestrator launches the Reviewer after the last QA PASS; the pointers `.claude/agents/reviewer.md` and `.opencode/agents/reviewer.md`.
- **Evidence:** `_docs/records/2026-11-13T0424Z-measure-ponytail-review.md`; Reviewer reports on #154 and #162; the human's ruling of 2026-11-14.
