Title: Ship one short core-rules file that every tool loads into every session

**What is wrong or missing**

The kit's rules are long docs read when a "Read when" trigger fires, and agents don't always follow them. socboard's rulings stuck because Kiro loads `.kiro/steering/` files marked `inclusion: always` into every session. The kit has no equivalent: no short file of the rules that must always apply (the non-negotiables, the formats, the routing rules) loaded by each tool, and no Kiro layer at all. Area rules (such as the human-step standard) are read only if a trigger fires.

**What you expected**

Proposal 7.3: one core-rules file of at most about 500 words, installed where each tool always loads it (Kiro steering with `inclusion: always`, `AGENTS.md` for OpenCode, `CLAUDE.md` for Claude Code), with the long docs kept as references, and area rules loaded only for their paths where the tool supports it.

Plan fields:

- Proposed tier: heavy (decided by the human on 2026-11-19: it changes what every session loads).
- Effort: R.
- Reasoning: D. Which rules make the cut, and keeping it consistent with `AGENTS.md` Non-negotiables without a second copy that drifts.
- Impact: C. A rule dropped from what is always loaded is a rule agents stop following.
- Needs: issue 01a (merged: the vocabulary and settings names it cites), issue 02 (merged: the formats it summarises), issue 03a (merged: routing rules), issue 05 (merged: stop points).

Filed as two issues (split approved by the human on 2026-11-19): 09a, the core-rules file and its Claude Code and OpenCode install (C1, C2 for Claude Code and OpenCode, C3 to C6); 09b, the Kiro layer (C2's Kiro part, and C6 for Kiro). See the end of this section.
- Runs in: sandbox for the files and tests; human for confirming each tool loads it (a human task: Kiro and OpenCode can't be run here).
- Debt: none.
- Touches protected `agent-kit/` files: yes; also this repo's `CLAUDE.md` and `AGENTS.md` if the install changes them.
- Files: `agent-kit/core-rules.md` (new), `agent-kit/claude-code/CLAUDE.md.template` (import it), `agent-kit/templates/AGENTS.md.template` (include or point to it for OpenCode; Non-negotiables de-duplicated against it), `agent-kit/kiro/steering/core-rules.md` (new Kiro layer, `inclusion: always` front matter), `agent-kit/setup.md` and `agent-kit/install-and-upgrade.md` (install steps per tool), `agent-kit/blueprints.md` (path-scoped area rules: Kiro file-match inclusion, nested `CLAUDE.md`), `agent-kit/installed-files.txt`, `agent-kit/CHANGELOG.md`, `tests/test_core_rules.py` (new), `tests/test_intended_copies.py` (if the rules appear in two places on purpose).

Acceptance criteria:

- [ ] C1. `agent-kit/core-rules.md` exists, at most 500 words, holding the non-negotiables, the format first lines (section 5) and the routing rules (impact decides PASS or FAIL; points route; stop points), each pointing to its long doc.
  Check: `tests/test_core_rules.py` counts words (500 or fewer) and asserts each linked doc exists.
- [ ] C2. Installed for each tool where it is always loaded: Claude Code through `CLAUDE.md` (an `@` import in `claude-code/CLAUDE.md.template`), OpenCode through `AGENTS.md`, Kiro as `.kiro/steering/core-rules.md` with `inclusion: always`.
  Check: read the three templates; `tests/test_core_rules.py` asserts the Kiro file's front matter.
- [ ] C3. Each rule has one home: where a rule is in both the core file and `AGENTS.md` Non-negotiables, one is the source and the other points to it, or the duplicate is listed as an intended copy and tested.
  Check: `make dup-report` shows no new unintended repeat; `tests/test_intended_copies.py` passes.
- [ ] C4. Area rules: `blueprints.md` says how to load a rule only for its paths (Kiro file-match inclusion; nested `CLAUDE.md` in Claude Code; in OpenCode, the trigger in `AGENTS.md` Read when, as now).
  Check: read `agent-kit/blueprints.md`.
- [ ] C5. Folded from issue #15: the core rules include (a) fetch web pages with the tool's web fetch, not `curl`; (b) check tool versions with `make tool-versions`, not chained version commands; (c) a `.scratch/` script's command description says whether it only reads or changes anything.
  Check: read `agent-kit/core-rules.md`; `tests/test_core_rules.py` asserts the three rules.
- [ ] C6. Each tool loads the file: confirmed by the human in a fresh session per tool (asking the agent to quote the first core rule without reading any file), recorded in a human task file.
  Check: the task file under `_human-tasks/` with a result per tool.

Out of scope: measuring always-loaded context before and after (issue #33, to run after this issue so it measures the new set); a standards register (issue 04b).

Split (each filed issue renumbers its own criteria from C1):
- 09a: `agent-kit/core-rules.md`, its install for Claude Code (`CLAUDE.md.template`) and OpenCode (`AGENTS.md.template`), one home per rule, area rules, the issue #15 rules, and the human's load check for Claude Code and OpenCode. Tier heavy. Effort R, Reasoning D, Impact C. Needs: as above.
- 09b: the kit's first Kiro layer, `agent-kit/kiro/steering/core-rules.md` with `inclusion: always`, its install steps in `setup.md` and `install-and-upgrade.md`, its row in `installed-files.txt`, and the human's load check in Kiro. Tier heavy. Effort S, Reasoning N, Impact M. Needs: issue 09a (merged).

Existing issues affected:
- Supersedes issue #15 (its three Conventions rules are C5).
- Issue #33 (always-loaded context measurement) should run after this issue; its measurement is the follow-on evidence that the file stays small.

**Evidence**

- Proposal sections 7.3, 9 row 9, 12 (decided: one short core-rules file loaded by every tool).
- socboard's six always-loaded steering files: `socboard/.kiro/steering/backlog-order.md`, `delivery-pace.md`, `evidence-and-steps.md`, `gate-blocks.md`, `real-dependencies-only.md`, `rubric-priority.md` (proposal section 11 keeps them as the model).
- Earlier measurement of always-loaded guidance: `_docs/records/2026-11-02T1447Z-measure-always-loaded-guidance.md`.
