# Decision: The proof of the shared trace id and of no leaked data is a separate script run by the observability CI entry point

One file per choice that may be revisited. **Status: approved** (the maintainer approved the Decision record of issue #295 by name; recorded in the claim comment https://github.com/andrew-chung-au/socboard/issues/295#issuecomment-6937755773) (issue #295, O10; copied from the issue's `## Decision record` section).

- **Decision:** the proof of the shared trace id and of no leaked data is a separate script, run by the observability CI entry point (#340) against the layered Compose stack. It chooses the trace id itself, drives one probe cycle and reads back from the three stores. A failure fails the job; nothing is skipped when the stack or a store is missing.
- **Reason:** the claim to prove is about collected and stored signals, so only the stored signals can prove it. Choosing the id removes any dependence on parsing it from output. Reading the stores back covers the exporter, the collector and the storage in one check.
- **Alternatives:** assert only on in-memory exporters (cheap, but cannot show the collector or stores keep the id and the canaries out); a check against the deployed dev server (needs a server big enough and a public Grafana, and the task says no live server); a screenshot only (cannot fail).
- **Trade-offs:** the job needs Docker and adds about 5 minutes; deadlines make it slower on a slow run. The canary search covers the three stores and the collector log, not every place a container might write. Exemplars live in memory only, so the proof is from the run, not from a stored history.
- **Evidence:** `_docs/planning/rubric.md` (Observability); roadmap 4; #287; #340; the senior review of 2026-11-16 (items 2, 3 and 8).
