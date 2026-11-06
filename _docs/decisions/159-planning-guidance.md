# Decision: planning guidance with a testable example, a plan-review checklist and one intent per issue

Issue #159 (Heavy). The human approved this record in a comment on #159 (body sha256 `8a98522af7250a5a33bb06d38b1c85044041926e4d08ce259274b53d9e2589c9`), copied here from the issue body.

- **Decision:** In `procedures/planning.md`, add (1) one example requirement in EARS form ("WHEN <trigger> THE SYSTEM SHALL <response>"), saying that one SHALL with a Given/When/Then scenario, or any other testable form, is fine; and (2) a plan-review checklist of at most seven lines (the intent matches what was asked; nothing extra crept into scope; each requirement is observable and testable; each has a case, including an awkward one; the case the human cares most about is covered; what is missing is named; the human would accept exactly this and nothing more). The checklist lives only in `planning.md`; `team/pm.md` links to it. In `team/pm.md`, add to the PM's Definition of done that an issue has one intent that fits in a sentence, and that the PM splits it when it needs "and also". Enforcement is by role-reading at grooming, as for the readiness gate in #156: the human reads the groomed issue, and an issue with two unrelated intents is returned to the PM.
- **Reason:** #156 requires requirements "phrased so acceptance criteria can be derived" but shows no example, and the kit has no check on a plan before code is written, which is the cheapest point to catch a wrong turn. OpenSpec's review pass and Kiro's EARS format both give a short, concrete answer (research in #14).
- **Alternatives:**
  - Make EARS mandatory: rejected, a forced format adds ceremony for small issues.
  - Put the checklist in `pm.md` as well or instead: rejected, `planning.md` is the procedure's home and two copies drift.
  - Say nothing more and trust the PM: rejected, that is the gap.
- **Trade-offs:**
  - `planning.md` grows; its word ceiling in `tests/test_planning_gate.py` stays at 400 and the existing text was trimmed to fit, not the ceiling raised. The checklist items are plain bullets, not checkboxes, to stay under it.
  - A checklist can be ticked without care, as with the readiness gate; the human reading the groomed issue is the control.
  - "One intent" is a judgement, not a script.
- **Evidence:** #159 and #156; `_docs/records/2026-11-06T0330Z-measure-spec-driven-frameworks.md`.
