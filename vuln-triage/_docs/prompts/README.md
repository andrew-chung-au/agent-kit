# Prompts

Key prompts that define a role, stage, or task are saved verbatim in this
folder and indexed below.

| file | purpose (what it got the agent to plan or build) | where executed |
|---|---|---|
| [reviewer-plan-review.md](reviewer-plan-review.md) | Defines the independent Reviewer role: review the planning documents that exist against the brief and rubric, write `_docs/reviews/<date>-plan-review.md` with a PASS/FAIL verdict | Claude Code (claude-opus-5-5), 2026-10-16; produced `_docs/reviews/2026-10-16-plan-review.md` (commit ba39c5c) |
| [lovable-frontend.md](lovable-frontend.md) | Defines the Lovable build task for issue #14: generate a mocked React frontend (six screens) with every backend call in one services layer plus a mock implementation, so it runs without a backend; that services layer becomes the input to `_docs/api.md` | Lovable, run by the human, build completed 2026-10-18 (chosen); also run in Bolt, 2026-10-17 (compared); approved by the human 2026-10-17 |
