Title: Add kit settings with defaults, profiles and per-issue overrides, the grade vocabulary and numbered criteria, documented in a new customizing.md

**What is wrong or missing**

Every value the process uses (how far ahead to groom, when QA fails, how many re-checks before the human is asked) is fixed in the kit's prose. A project that needs a different value has to edit the kit's text and carry a fork. socboard did this: 18 kit files changed, six steering rulings and 11 queued patches in two weeks, mostly changing a value rather than a rule. There is no way to set a value per project, per usage plan (profile) or for one issue, and no document that tells a project what it can adjust.

The later 1.11 issues also share two foundations that don't exist yet: one grade vocabulary (Effort, Reasoning, Impact), so "medium" can't mean two things, and numbered acceptance criteria with a `Check:` line, so a finding, a checklist or a dependency can point at one criterion.

**What you expected**

A settings layer with documented defaults, so a project changes a value in one line of `agent-kit.conf` without editing the kit, and a new kit doc, `agent-kit/customizing.md`, that explains it (proposal section 4), including the vocabulary and grading guide (4.0). The task template numbers criteria `C1`, `C2`, ... each with a `Check:` line (proposal 3.3). Issues 02 to 11 build on both.

Filed as two issues (split approved by the human on 2026-11-19), 01a and 01b below.

Plan fields for the whole (grades are proposals for the human to agree with the label):

- Proposed tier: heavy. It changes the process itself and adds an override path next to the approval hash.
- Effort: E. A new reader script with tests, a new kit doc, the conf and task templates and process changes; more than one session, hence the split.
- Reasoning: D. Override precedence interacts with the approval hash, the label rules and the tier rules; the bounds no level can cross are security limits.
- Impact: C. A wrong precedence or a missing bound could let an issue lower QA or a tier without the human.
- Needs: none (first in the order).
- Runs in: sandbox.
- Debt: none expected. Later issues (02 to 11) each wire the behaviour behind their own settings; this issue adds the full 4.2 table with defaults and the reader only.
- Touches protected `agent-kit/` files: yes (`HUMAN_APPROVED=1` commit after approval). `agent-kit/scripts/` runs live, so the new reader is live as soon as it is in the working tree.

### 01a: settings, profiles, vocabulary, numbered criteria, customizing.md

Grades: Effort E, Reasoning N, Impact M. Needs: none. Tier: heavy.

Files: `agent-kit/customizing.md` (new), `agent-kit/scripts/settings.py` (new, standard library only), `agent-kit/templates/agent-kit.conf.template`, `agent-kit/templates/Makefile.mk` and this repo's `Makefile` (a `settings` target), `agent-kit/templates/task-template.md` (numbered criteria with `Check:` lines), `agent-kit/team/pm.md` (definition of done), `agent-kit/installed-files.txt`, `agent-kit/README.md` (a pointer to customizing.md), `agent-kit/CHANGELOG.md`, `tests/test_settings.py` (new), `tests/test_task_template.py`.

Acceptance criteria:

- [ ] C1. `agent-kit/customizing.md` exists with the levels table (4.1), the profile settings table and the standalone settings table (4.2) with every setting, default and meaning listed there, the profile guide (4.3), and the rule for adding a setting (4.5). It says `STEP_UP` applies in Claude Code only and is ignored in OpenCode and Kiro. Of the settings that already exist, only `LIGHT_ALLOWED` (and `LIGHT_MAX_LINES`) is listed as unchanged. Points routing (4.4) is added by issue 03a, which owns that behaviour.
  Check: read `agent-kit/customizing.md`; `tests/test_settings.py` asserts every setting name in the reader's defaults appears in the doc's tables and vice versa.
- [ ] C2. `customizing.md` has the vocabulary and grading guide (4.0): three grades, Reasoning B/N/D, Effort S/R/E and Impact L/M/C, sharing no word or letter; each level with a test and an example as in the 4.0 table; Effort at under 10, 10 to 30 and over 30 minutes; the tie-break rule (when unsure, the higher level for Impact and Reasoning, the lower for Effort); and "each grade comes with one line of reason".
  Check: read the section; `tests/test_settings.py` asserts the nine letters are distinct and each level has a test and an example row.
- [ ] C3. The task template numbers acceptance criteria `C1`, `C2`, ... and each has a `Check:` line naming how it is verified (a command, a test name, or a reading of a named file). `pm.md`'s definition of done requires both. Refused: a criterion without an id or without a `Check:` line.
  Check: `tests/test_task_template.py` asserts the format on the template and fails on a fixture criterion missing `Check:`.
- [ ] C4. `agent-kit/scripts/settings.py` resolves each setting in the order kit default, then profile (`PROFILE=solo|team|fleet`), then a project line in `agent-kit.conf`. A setting written in `agent-kit.conf` wins over the profile; switching `PROFILE` changes only settings not written.
  Check: `tests/test_settings.py` cases: no conf lines gives the kit defaults; `PROFILE=fleet` gives `GROOM_AHEAD=6`, `LANES=3`, `DELIVERY_LEAD=on`, `STATUS_EVERY=15m`; `PROFILE=fleet` plus `LANES=2` gives `LANES=2` and the other fleet values.
- [ ] C5. `make settings` prints each effective setting and where its value came from (kit default, profile, project; issue override and session ruling once 01b lands). (The target name is a grooming proposal; the proposal names no target.)
  Check: run `make settings` in this repo; every setting in 4.2 appears once with a source.
- [ ] C6. Defaults equal what the kit does today (4.5): an upgraded project with no new lines behaves as before. `PROFILE` unset means `solo`.
  Check: `tests/test_settings.py` asserts the defaults table; `agent-kit/CHANGELOG.md` says no action is needed to keep current behaviour.
- [ ] C7. Refused: an unknown setting name, an unknown profile, or a value outside a setting's allowed set (for example `QA_FAIL_AT=X`, `RECHECK=some`) makes the reader exit non-zero and name the line. It never falls back silently.
  Check: `tests/test_settings.py` refusal cases, one per kind.
- [ ] C8. `agent-kit.conf` is read as text, never sourced, as the `GITHUB_REPO` line already is.
  Check: `tests/test_settings.py` case with `$(touch .scratch/x)` as a value: the file is not created and the line is refused.

### 01b: issue overrides, bounds and session rulings

Grades: Effort R, Reasoning D, Impact C. Needs: issue 01a (merged). Tier: heavy.

Files: `agent-kit/scripts/settings.py`, `agent-kit/process.md` (Lifecycle steps 3 and 4, Approved text: overrides and session rulings), `agent-kit/procedures/orchestrator-comments.md` (session-ruling comment layout), `agent-kit/customizing.md`, `agent-kit/CHANGELOG.md`, `tests/test_settings.py`, `tests/test_orchestrator_comments.py`, a human task file under `_human-tasks/`.

Acceptance criteria:

- [ ] C1. The reader takes an issue's `Overrides:` body line (for example `Overrides: QA_FAIL_AT=C, RECHECK=full`) only when the issue carries the `overrides` label; with the line and no label it refuses and names the issue. The orchestrator runs this check before launching the Engineer and QA, next to the hash check (`process.md`, Lifecycle steps 3 and 4). The line is covered by the approved body hash.
  Check: `tests/test_settings.py` with a fake issue JSON (as `tests/test_issue_hash.py` uses): line plus label applies; line without label refuses; label without line changes nothing; read `agent-kit/process.md` Lifecycle step 3.
- [ ] C2. Bounds no level can cross (4.1), enforced by the reader: no override or session ruling can drop QA (`HEAVY_SECOND_QA=off` is refused on a `tier:heavy` issue or one whose paths hit the escalation list in `agent-kit/scripts/check-tier.sh`), lower a tier, or remove the label, protected-file or push rules.
  Check: `tests/test_settings.py` refusal case: `Overrides: HEAVY_SECOND_QA=off` on a heavy issue exits non-zero.
- [ ] C3. Session rulings (4.1): a ruling the human gives in a session ("decision budget 8 for this issue") is recorded by the orchestrator in an `Orchestrator:` comment on the issue, with its layout in `procedures/orchestrator-comments.md`. It lasts for that issue only, and becomes a project setting only at a sweep. (Decided by the human on 2026-11-19: the 4.1 table wins over the text that said "until the session ends".)
  Check: read `process.md` and `orchestrator-comments.md`; `tests/test_orchestrator_comments.py` gains a case for the ruling layout; `tests/test_settings.py` applies a ruling to its issue and not to another issue.
- [ ] C4. The `overrides` label is created by the human, not an agent (`AGENTS.md`, Issues). The issue's human task file says how.
  Check: a task file under `_human-tasks/` from `agent-kit/templates/human-task.md` exists for creating the label.

Out of scope (both): the behaviour behind each setting (issues 02 to 11 wire their own); points routing (issue 03a).

**Evidence**

- Proposal sections 2.1 (adjustable without editing the kit), 2.8 (one vocabulary), 3.3 (`Check:` lines; Overrides), 4.0 to 4.3 and 4.5, 12 (vocabulary, thresholds, tie-break and profile defaults decided 2026-11-19).
- Proposal section 1: socboard (kit `1.10+socboard.2`) changed 18 kit files, holds six steering rulings in `socboard/.kiro/steering/` and 11 approved but unlanded patches in `socboard/_docs/planning/epoch-batch-1/`, most of them value changes.
- Existing settings reading pattern: `GITHUB_REPO` in `agent-kit.conf` is read as text by `agent-kit/scripts/github_api.py` (decision `_docs/decisions/172-github-repo-source.md`).
