# Permission sweeps

One line per sweep: date, the commit the sweep counted up to, outcome. The next sweep starts from the last commit listed here (`make permission-report SINCE=<commit>`). Procedure: `_docs/agent-kit/procedures/permission-sweep.md`.

- 2026-10-25, counted up to `9eb4071` (sweep 1, #65): 68 summaries read, no settings changes (`make *` already allowed in both tools; the rest are writes that stay on ask or below the 3-session threshold). 29 summaries had no Permission review section, mostly Kiro Web and cloud sessions. Added `.opencode/plugins/permission-log.js` (`4fa0674`) to log OpenCode prompts; the log now lives at `.agent-logs/permission-prompts.jsonl` (git-ignored, outside `.scratch/` so `make clean-scratch` keeps it), and the next sweep copies a reviewed snapshot to `_docs/permission-sweeps/<date>.jsonl`. Next sweep starts from `9eb4071`.

Cloud sessions run file edits without asking in every mode, so the `Edit` ask rules only protect local sessions (see the live check on #60, comment 6330923566). The agent cannot see permission prompts: a live check needs the human to record what appeared on screen.

- 2026-10-29, #271 (tooling change, not a sweep): the report and the review template now use five groups, routine issue writes are already allowed and are not candidates, and cloud push is an opt-in module rather than a sweep item. `make permission-report SINCE=9eb4071` ran read-only; no settings change was proposed. The next sweep still starts from `9eb4071` (sweep 1) unless the human chooses a later baseline. Verification: `_docs/permission-tooling-verification.md`.
