---
inclusion: always
---

# Work the highest-value rubric points first (maintainer's ruling, 2026-11-16)

Applies to every lane in this repository until the maintainer changes it. The rubric is `_docs/planning/rubric.md` (12 criteria, 24 points).

1. **Order by points gained per piece of work.** When choosing the next issue, or what to build first inside one, pick what moves a rubric criterion up a level soonest. Name the criterion and the level in the claim comment.
2. **The points still open are, in rough order of cost:** Alerting on User Impact (1 point: one alert exists), CI/CD (the third point: a manual deploy to production beside the automatic dev deploy), Observability (2 points: one journey with a metric, a trace and structured logs sharing a trace id, no customer data, stored and viewable in a UI), and the On-Call Agent (2 points: an agent wakes on the alert and fixes the issue).
3. **Defer work that adds no point** while those are open: hardening and wording follow-ups, machine-readable copies, diagnostics the alert does not read, and dev showcases of something already proven in CI. Do them when a point-moving issue is blocked, or when one depends on them.
4. **Evidence is part of the point.** A criterion counts only when a reviewer can open the proof (`evidence-and-steps.md`), so the evidence criterion of a point-moving issue is not deferred.
5. **This never lowers a gate.** QA, the stopping rule and the protected-file approvals apply as before; priority changes the order, not the checks.
