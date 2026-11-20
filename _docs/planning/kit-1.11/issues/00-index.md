# Kit 1.11 issue drafts: index

Source: `_docs/planning/kit-1.11/workflow-review.md`, section 9 order, revised with the human's decisions of 2026-11-19 (vocabulary and numbered criteria move into issue 01; issues 07 and 09 are heavy; issue 07 is filed after 05 and 06; all proposed splits accepted). Drafts only; nothing filed.

Grades use the proposal's vocabulary (4.0): Effort S/R/E, Reasoning B/N/D, Impact L/M/C. Impact is a findings grade in the proposal; for an issue the PM reads it as "how bad if this change is wrong".

## Filing order

Each split is filed as its own issue. Its draft lives in the parent's file, as a `###` section or a split list.

| Order | Issue | Title | Tier | Effort | Reasoning | Impact | Needs (merged) | Draft file |
|---|---|---|---|---|---|---|---|---|
| 1 | 01a | Add kit settings, profiles, the grade vocabulary and numbered criteria, documented in customizing.md | heavy | E | N | M | none | `01-settings-profiles-overrides.md` |
| 2 | 01b | Add per-issue overrides with the overrides label, the bounds no level can cross, and session rulings | heavy | R | D | C | 01a | `01-settings-profiles-overrides.md` |
| 3 | 02 | Give role returns, findings, QA comments and messages to the human fixed fields, checked by a script, with a recommendation required | heavy | E | D | C | 01a | `02-formats.md` |
| 4 | 03a | Route failing QA findings by impact and points, with a fix check, a patchwork guard, RECHECK and STEP_UP | heavy | E | D | C | 01a, 01b, 02 | `03-qa-loop.md` |
| 5 | 03b | Log unfixed findings by group, list them with make findings, and sweep them | heavy | R | N | M | 03a | `03-qa-loop.md` |
| 6 | 04a | Make the numbered criteria the Engineer's and QA's shared checklist | heavy | R | N | M | 01a | `04-grooming-and-standards.md` |
| 7 | 04b | Add a standards register and a Standards: line to issues | heavy | R | B | L | 04a | `04-grooming-and-standards.md` |
| 8 | 04c | Groom up to GROOM_AHEAD issues ahead with a [groomed] prefix, each placed in the order | heavy | R | D | M | 01a | `04-grooming-and-standards.md` |
| 9 | 05 | Weight decision points, keep a ledger of the ones the agent continued past, and answer them per point | heavy | E | D | C | 01a, 01b, 02 | `05-decision-points.md` |
| 10 | 06 | Give human tasks a header, a make human-tasks list, rendered steps and an archive for done one-off tasks | standard | E | N | M | none | `06-human-tasks.md` |
| 11 | 07a | Write reflections to files and have the sweep read them | heavy | R | N | M | 05, 06 (filing order) | `07-make-status-and-reflections.md` |
| 12 | 07b | Replace the session summary with make status (including the spec version) and the Close comment | heavy | E | N | M | 07a, 05, 06 | `07-make-status-and-reflections.md` |
| 13 | 08a | Add a consult stage and environment map before planning | heavy | R | N | M | 01a | `08-planning-consult-grades.md` |
| 14 | 08b | Give each planned issue grades, Debt, Runs in and criterion-level Needs lines | heavy | R | N | M | 04a | `08-planning-consult-grades.md` |
| 15 | 08c | Add reasoning variants of role files and let STEP_UP=auto use them (Claude Code only) | heavy | R | D | M | 03a, 05, 08b | `08-planning-consult-grades.md` |
| 16 | 09a | Ship one short core-rules file loaded by Claude Code and OpenCode in every session | heavy | R | D | C | 01a, 02, 03a, 05 | `09-core-rules-file.md` |
| 17 | 09b | Add the kit's Kiro layer: the core rules as always-loaded steering | heavy | S | N | M | 09a | `09-core-rules-file.md` |
| 18 | 10 | Make Verify quiet by default, printing the test output only on failure or with V=1 | standard | S | N | C | none | `10-quiet-verify.md` |
| 19 | 11a | Add an optional delivery-lead role for parallel lanes, with the Claude Code channel | heavy | E | D | C | 01a, 02, 05, 06, 07b, 08b | `11-delivery-lead.md` |
| 20 | 11b | Let the delivery lead and workers talk through Lead: and Status: issue comments (Kiro and cloud) | heavy | R | D | C | 11a | `11-delivery-lead.md` |
| 21 | 12 | Move this repo's docs into one _docs/ tree following socboard's layout, with an index row for each file | standard | R | B | M | none | `12-repo-docs-structure.md` |

Titles for splits are working titles; the draft file's main `Title:` line covers the whole. Before filing, the PM writes one file per split with its own `Title:` line, and criteria renumbered from C1.

Parallel lane (no dependencies): 06, 10, 12 can be filed and worked at any point. 07a waits for 05 and 06 only because of the filing order the human set; it has no technical dependency on them.

Protected files: every issue except 12 touches protected `agent-kit/` files; 12 touches the protected `Makefile`. 01a, 01b, 02, 03a, 03b, 05, 06, 07b, 10, 11a and 11b change `agent-kit/scripts/`, which runs live; 10 may touch `agent-kit/claude-code/hooks/verify_on_stop.py`. `STEP_UP` is Claude Code only (01a, 03a, 08c).

## Existing issues affected (proposed; closures need the human)

- issue #15: superseded by 09a (its three Conventions rules are a criterion there).
- issue #17: superseded by 11a (its parallel-safety rules are a criterion there).
- issue #142: made obsolete by 07b; its start-time need for `make permission-report SINCE=` moves to issue #18.
- issue #26: made obsolete by 07b; the launch-usage line is dropped, and the question about the token figure joins issue #191.
- issue #141: 03a's patchwork guard answers its "fix the class, not the spot" question; issue #141 keeps only its audit.
- issue #52: named in 08a as the profile that adds the cloud-agent row to the environment map.
- issue #33: runs after 09a and 09b, as follow-on evidence of the always-loaded set.
- issue #6 and issue #3: 12 must decide where `proposals/helpers.sh` and `proposals/pre-push-v3` go (12's question 2).

## Gaps and conflicts

Resolved by the human on 2026-11-19:

1. **Resolved.** Order against dependencies: the vocabulary (4.0) and the numbered-criteria format (C1.. with `Check:`) are in 01a. The workarounds in 02, 03, 04 and 08 are removed.
2. **Resolved.** Criterion ids come late: now in 01a; 04a uses the format rather than introducing it.
3. **Resolved.** `STEP_UP=auto` acts as `ask` until 08c lands (03a C7, 08c).
4. **Resolved.** "Size" against "Effort": Effort throughout.
5. **Resolved.** The `Debt:` line is in 08b; the debt finding category is in 03b.
6. **Resolved.** `TIER_DEFAULT` is dropped everywhere; only `LIGHT_ALLOWED` (and `LIGHT_MAX_LINES`) exists.
7. **Resolved.** A session ruling lasts for that issue only (01b C3).
8. **Resolved.** Merge rule: "not pushed until the point is closed" for projects that commit to `main`; "not merged" for branch projects (05 C6).
9. **Resolved.** Issue 07 needs 05 and 06 and is filed after them. `make status` prints the spec version. Launch-usage lines are dropped (issue #191). The file-naming rules move to `templates/docs-index.md` (07b C3).
10. **Resolved.** Issues 07 and 09 are heavy.
11. **Resolved.** The Kiro layer is its own issue, 09b.

Still open (for the human or for grooming):

12. **New comment prefixes.** 11b adds `Lead:` and `Status:` as GitHub comment first lines; `issue-comment.sh` accepts only `PM:`, `Engineer:`, `QA:` and `Orchestrator:`, and `AGENTS.md` Issues lists the trusted prefixes. The `AGENTS.md` change needs the human's approval when 11b is groomed.
13. **Groom ahead against the current rule.** `process.md` Lifecycle step 2 forbids grooming a second unlabelled issue; 04c reverses it. Until 04c lands, the 1.11 issues themselves are groomed one at a time.
14. **Quiet Verify has no proposal section.** Only section 9 row 10 mentions it. Draft 10's criteria are the PM's reading; on failure it recommends the full output over a tail plus a log file.
15. **Issue 12 layout.** socboard's `_docs/` has no `reference/` folder. `proposals/` holds two scripts under review (issue #6, issue #3), not only plans. The 1.11 proposal is now committed (8f903dc), so that part is settled. Draft 12 asks four questions.
16. **Make targets the proposal doesn't name:** `make settings` (01a) and `make check-format` (02) are grooming proposals. The proposal does name `make findings`, `make decisions`, `make human-tasks`, `make human-task-render` and `make status`.
17. **The `overrides` label** must be created by the human (`AGENTS.md`: agents never create labels). 01b adds a human task for it.
18. **Data format for human-task steps** (06 C2): JSON in a fenced block or in a sidecar file. JSON keeps it standard-library; the human picks the placement.
19. **`make status` DAYS default** (07b C1): 7 is a grooming proposal.
