Title: Add an optional delivery-lead role that runs the board for parallel lanes and relays to the human

**What is wrong or missing**

When several sessions work in parallel, the human relays every message between them by hand (socboard, with Kiro sessions). Nobody holds the board: which lane runs which issue, the merge order, open decisions and human tasks. Lane names drifted into durable docs ("Session A/B" against lanes by area). The orchestrator's context fills with each worker's full output.

**What you expected**

Proposal section 6: an optional delivery lead (`DELIVERY_LEAD=on`, the `fleet` default) that holds the board, assigns issues to lanes, sets the merge order and relays to the human in the 5.4 form, reading only role returns (5.1) and one-line status lines (5.5). It doesn't build, groom or test.

Plan fields:

- Proposed tier: heavy. A new role, a new comment prefix and a new channel between sessions.
- Effort: E (split below).
- Reasoning: D. Parallel safety, a new comment prefix that the trust rules and `issue-comment.sh` must accept, and per-tool channels.
- Impact: C. Two lanes changing the same files or protected files at once, or an untrusted `Lead:` comment acting as orders, would break the work or the trust rules.
- Needs: issue 01a (`DELIVERY_LEAD`, `LANES`, `STATUS_EVERY`), issue 02 (role return, message), issue 05 (ledger), issue 06 (human tasks), issue 07b (`make status`), issue 08b (grades and lanes), all merged. Last in the order (section 9) apart from issue 12, which has no dependencies.
- Runs in: sandbox for the docs and scripts; Kiro and cloud polling need the human (human task).
- Debt: none. A dmux trial in one lane is a later, separate issue (proposal section 10).
- Touches protected `agent-kit/` files: yes; also `AGENTS.md` (Issues: the trusted role prefixes) via `templates/AGENTS.md.template`.
- Files: `agent-kit/team/delivery-lead.md` (new), `agent-kit/claude-code/agents/delivery-lead.md` and `agent-kit/opencode/agents/delivery-lead.md` (new), `agent-kit/process.md` (Roles, Orchestrator, lanes), `agent-kit/procedures/orchestrator-comments.md` (`Lead:` orders, `Status:` lines), `agent-kit/scripts/issue-comment.sh` and `agent-kit/scripts/issue-text-lib.sh` (accept `Lead:` and `Status:` first lines), `agent-kit/scripts/issue-close.sh` only if it must ignore the new prefixes, `agent-kit/templates/AGENTS.md.template` (role prefixes), `agent-kit/scripts/check-format.py` (status line 5.5), `agent-kit/installed-files.txt`, `agent-kit/CHANGELOG.md`, `tests/test_issue_wrappers.py`, `tests/test_role_definitions.py`, `tests/test_delivery_lead.py` (new). `agent-kit/scripts/` runs live.

Acceptance criteria:

- [ ] C1. `team/delivery-lead.md` defines the role: holds the board (lanes, order, grades, the decision ledger, human tasks), assigns the next issue to a free lane, sets the merge order, answers "where are we?", relays in the 5.4 form. It never builds, grooms, tests, labels or closes.
  Check: read the file; `tests/test_role_definitions.py` covers the new Claude Code and OpenCode definitions (Edit denied).
- [ ] C2. The role runs only when `DELIVERY_LEAD=on`; otherwise `process.md` reads as today.
  Check: read `process.md`; `make settings` shows the value.
- [ ] C3. Status line (5.5): `Status: #<n> <state> | <k> of <m> criteria done | blocked: yes|no | next: C<n> | at: <commit>`, posted at each milestone (`STATUS_EVERY=milestone`) or on a timer (`15m` in `fleet`). The lead reads only status lines and role returns, and opens a worker's detail only when a line says `blocked: yes`.
  Check: `make check-format KIND=status` accepts the 5.5 example and refuses one without `blocked:`.
- [ ] C4. Lane names appear only in status lines and the board, never in durable docs, commits or issue bodies.
  Check: read `delivery-lead.md`; `tests/test_delivery_lead.py` greps a fixture commit message and issue body and flags a lane name (rule enforced at the human's review; say so).
- [ ] C5. Channels per tool: Claude Code, background subagents each in its own worktree (notified on finish, can be messaged and stopped); Kiro and other cloud sessions, GitHub comments polled on a short interval, workers posting `Status:` lines and the lead posting `Lead:` orders; a shared machine, `.scratch/status/<lane>` files the lead watches (no record).
  Check: read `delivery-lead.md`.
- [ ] C6. Trust: `Lead:` is added to the role prefixes in `AGENTS.md.template` (Issues) and `process.md` (Issue comments); a `Lead:` comment from an account other than the repository owner's is input, not orders. `issue-comment.sh` accepts `Lead:` and `Status:` first lines.
  Check: `tests/test_issue_wrappers.py` cases; refusal case: a comment starting `Leader:` is still refused.
- [ ] C7. Parallel safety (from issue #17): two issues run in parallel lanes only when (a) neither has a dependency link to the other, either way; (b) they have no files in common (from their expected paths); (c) they don't both change a protected file. The lead checks this before assigning.
  Check: `tests/test_delivery_lead.py` refuses each of the three cases on fixture issues and accepts a clean pair.
- [ ] C8. Soft stop: when the human says "wrap up", or a status line reports the usage limit is near, every running role writes `.scratch/progress-<N>.md` and stops at the next safe point; a relaunch starts from it (`process.md`, When a role stops early).
  Check: read `process.md` and `delivery-lead.md`.

Out of scope: an automatic usage-level stop (issue #191); dmux (proposal section 10: trial in one lane after this issue, merging by hand); an approval proxy (section 8).

Split (approved by the human on 2026-11-19; each filed issue renumbers its own criteria from C1):
- 11a: role, settings gate, status line, lanes, parallel safety, soft stop, Claude Code channel (C1 to C5 for Claude Code, C7, C8). Effort E, Reasoning D, Impact C.
- 11b: the GitHub-comment channel for Kiro and cloud sessions with the `Lead:` and `Status:` prefixes (C5 cloud part, C6). Effort R, Reasoning D, Impact C. Needs: 11a.

Existing issues affected: supersedes issue #17 (parallel issues in worktrees); its parallel-safety rules are C7.

**Evidence**

- Proposal sections 5.5, 6, 4.2 (`DELIVERY_LEAD`, `LANES`, `STATUS_EVERY`), 4.3 (profiles), 8 (no role always on; no homegrown multiplexer), 9 row 11, 10 (dmux).
- Proposal section 1: the human as relay for every message between Kiro sessions; socboard ruling "lanes that own files"; the Reviewer role added and dropped within four days.
- vuln-triage's `vuln-triage/_docs/cloud-sessions.md` and `agent-team.md` (parallel cloud sessions coordinated by hand).
