# Report formats

The fixed fields every role writes, so whoever needs one fact reads one line. This page holds the role return, the reflection, the Engineer's criteria list, the finding, the findings log and the decision ledger. The QA comment is in `_docs/agent-kit/team/qa-engineer.md` and the message to the human in `_docs/agent-kit/procedures/asking-the-human.md`; each format is defined once.

## The line rule

Every field is `<Label>: <value>` alone on its line from column 1, as in "Lines scripts read" of `_docs/agent-kit/procedures/orchestrator-comments.md`: the label worded exactly, case included; one space after the colon; a value that is one line and not empty. No indent, no list marker. A line ending in CRLF reads as LF; a file starting with a byte order mark is refused. Grade letters are those of `_docs/agent-kit/customizing.md`.

A recommendation is never empty. `none` is allowed only as `none, because <reason>`.

Check a file before you send or post it: `make check-format KIND=<return|finding|qa|message> FILE=.scratch/<name> [N=<issue number>]` (N for `finding` and `qa`). It prints `ok`, or one line per problem. It checks shape, not truth. For `qa` it also reads the issue's settings (`agent-kit.conf` and the dump `.scratch/issue-<n>.json`), so run `make settings N=<n>` first; it then checks that the verdict and the `Findings:` counts follow from the findings (`team/qa-engineer.md`).

## Role return

Every role ends with this as its final message to whoever launched it: exactly ten lines, in this order. Before that message, every role (PM, Engineer, QA) writes its reflection for the launch to `.scratch/reflection-<issue>-<role>.md` from the template (Reflection, below); the ten lines don't change. A launch that stops early may leave none.

- `Status:` `done`, `blocked` or `stopped-early`
- `Issue:` `#<n>`
- `Commit:` 7 to 40 lowercase hex, or `none`
- `Verdict:` `PASS` or `FAIL` from QA, `none` from any other role
- `Findings:` `<n> fail / <n> log`, or `none`
- `Decisions:` `none`, or the ids of the decision points the role opened (`D-<issue>-<n>`), separated by a comma and one space
- `Needs the human:` `none` or `yes`
- `Recommendation:` what you recommend next
- `Detail:` an `https://` link, or a relative path inside the project with no `..`
- `Checkpoint:` a relative path, or `none`

With `Needs the human: none`, nothing follows. With `yes`, one blank line follows, then one or more requests in the approval-request or decision-question layout of `asking-the-human.md`, each starting `Approval needed:` or `Decision needed:`, kept in full (`process.md`, Report by reference).

```
Status: done
Issue: #198
Commit: 1a2b3c4
Verdict: none
Findings: none
Decisions: none
Needs the human: yes
Recommendation: Approve the staged commit, then launch QA.
Detail: .scratch/engineer-198.md
Checkpoint: none

Approval needed: commit the staged kit files for #198 with HUMAN_APPROVED=1.
- Why: #198, every criterion; agent-kit/ is protected.
- Seen before: no
- What will run or change: HUMAN_APPROVED=1 git commit; diff in .scratch/diff-198.patch
- Checked just now: git diff --cached --stat lists 4 files.
- Risk and undo: a local commit only; undo with git reset --soft HEAD~1.
- Alternatives: you commit it yourself; or I change the diff first.
- Recommendation: approve; make verify printed PASS.
```

## Reflection

What a role learned in one launch, for the sweep. Every PM, Engineer and QA launch ends by writing one from `_docs/agent-kit/templates/reflection.md` to `.scratch/reflection-<issue>-<role>.md`, `<role>` being `pm`, `engineer` or `qa`, replacing any file a previous launch left there. It costs no launch of its own.

- A heading `### <role>, <UTC time YYYY-MM-DDTHH:MMZ>`: the role and the time of writing.
- `Slowed:` what slowed you, with evidence.
- `Nearly:` what nearly went wrong or was blocked.
- `Change:` one proposed change: the file it touches, the expected effect, how it would be measured.

The three lines follow the line rule. A role with nothing to report writes the single line `Nothing to report.` under the heading instead. A proposal is a suggestion for the human; nobody applies it.

```
### qa, 2026-11-24T10:15Z

Slowed: make verify ran twice because the first run hit a stale .scratch fixture (QA comment on #206).
Nearly: the HEAD check nearly ran before Assert clean.
Change: process.md step 5, name the order; fewer QA re-runs, measured by QA rounds per issue.
```

The orchestrator appends each file unchanged to `_docs/records/reflections/<issue>.md`, one section per launch, and commits it (`process.md`, Reading a return). It appends nothing when the launch left no file, or when the file's heading is already in the issue's file. The file is append-only, as the decision ledger is: an earlier section is never edited or removed, and the orchestrator writes no reflection text of its own; the human's diff review reads that it was only appended to. Refused:

- A reflection posted as an issue comment. It lives only in the file; the orchestrator's and the human's reading enforce this.
- QA writing to `_docs/records/reflections/` itself: **Assert clean** fails on the changed or untracked file, and QA's verdict is discarded (`process.md`, Lifecycle step 5).

The sweep reads these files (`procedures/sweep.md`, step 2).

## Criteria list

The Engineer's issue comment holds a `Criteria` list: one line for every criterion of the issue, in its order, in one of four forms. Evidence names a test, a command and its result, or a file.

- `C<n>: done (<evidence>)`
- `C<n>: not done`
- `C<n>: not checked (<reason>)`
- `C<n>: challenged (<reason>)`: the criterion was raised before building as one that can't be met as written (`team/software-engineer.md`)

```
Criteria
C1: done (tests/test_x.py passes)
C2: challenged (the Check: names a script that does not exist)
```

QA reads the list first and names any disagreement on its own `Criteria` line (`team/qa-engineer.md`). No script reads the list; `make check-format` has no kind for it.

## Finding

One per problem QA or a sweep finds, inside a QA comment and as the text form of a findings-log entry: eleven lines, in this order.

- `Id:` `F-<issue>-<n>`, n from 1 with no leading zero, unique in the file; a second QA launch continues the numbering
- `Impact:` `L`, `M` or `C`
- `Effort:` `S`, `R` or `E`
- `Scope:` `in` or `out` (below)
- `Criterion:` `C<n>` with no leading zero, or `none` for a risk no criterion covers
- `Category:` `defect`, `debt`, `standard` or `criterion` (a criterion stricter than the issue's goal needs; it still fails or logs by its impact and scope)
- `Group:` a slug: lowercase letters and digits in parts joined by single hyphens, at most 40 characters
- `Related:` another finding's id, or `none` (below)
- `Recommendation:` the fix you recommend
- `What:` the problem, with the file and line
- `How found:` the command, script or reading that showed it

**Scope.** `in` is what the issue asks for (a criterion, a standard on its `Standards:` line) or what its own change caused, the Code review items of `team/qa-engineer.md` included. `out` is everything else: a failure the change didn't cause (such as a **Verify** failure a clean copy of the base also shows), a risk outside the issue, and a finding moved out of scope by a ship (`process.md`, Lifecycle step 6). Whether a finding fails follows from its impact and scope under the settings `QA_FAIL_AT` and `QA_SCOPE_STRICT` (`_docs/agent-kit/customizing.md`).

**Related.** Set it when the finding stems from an earlier finding's fix, or has the same cause. A finding that still fails at a re-check is repeated with its own id; a new problem takes the next id. The value is `none` or an id `F-<issue>-<n>` other than the finding's own. In a QA comment, an id of this issue must be in a finding of the same comment or of an earlier owner `QA:` comment on the issue; an id of another issue is checked for shape only. `make route-findings` follows these links to count a finding's rounds.

Each label maps to the findings-log JSON key of the same field: lower-case it and replace the space with `_` (`How found` is `how_found`). `scripts/check-format.py` holds the keys in order as `FINDING_FIELDS`, and checks the text form and the JSON form with the same function.

```
Id: F-198-1
Impact: L
Effort: S
Scope: in
Criterion: C8
Category: defect
Group: check-format-usage
Related: none
Recommendation: Name the allowed kinds in the usage line.
What: make check-format KIND=bogus prints a usage line that does not list the kinds (Makefile line 40).
How found: .scratch/qa-198-probe.py, case 3.
```

## Findings log

Where an unfixed finding goes (`process.md`, Lifecycle step 9): at or above `FINDINGS_TO_ISSUE_AT` (default `C`), an unlabelled draft issue; below it, one entry in `_docs/records/findings/<issue>.json`. A finding the human shipped gets its follow-up issue and is not logged; a fixed finding is not logged. Debt is a finding with `Category: debt`. `Group:` names one problem: QA runs `make findings` first and reuses a listed slug that fits.

The orchestrator writes the file once, at close, after the last QA PASS, from the QA comments' finding blocks, and never edits it. The `group` is QA's, copied unchanged.

```
{"issue": 199, "logged": "2026-11-22T21:40Z", "findings": [{"id": "F-199-2", "impact": "L", ... "how_found": "First QA launch."}]}
```

Each entry has the eleven keys of `FINDING_FIELDS`, in order, as the finding above. `logged` is a UTC time. A file's name is `<issue>.json` and matches `issue`.

The sweep's rulings go in `_docs/records/findings-rulings.jsonl`, append-only, one line each, `at` being a sweep entry's name time (`YYYY-MM-DDTHHMMZ`):

```
{"id": "F-199-1", "ruling": "issued", "at": "2026-12-01T0900Z", "issue": 230}
{"id": "F-199-3", "ruling": "dropped", "at": "2026-12-01T0900Z"}
{"id": "F-199-4", "ruling": "kept", "at": "2026-12-01T0900Z"}
{"id": "F-199-2", "ruling": "regroup", "at": "2026-12-01T0900Z", "group": "route-findings-docs"}
```

`issued` and `dropped` close an entry; `kept` restarts its age at `at`; `regroup` replaces its group. An entry's age is the number of sweep entries named later than its `logged` time (or its last `kept`).

`make findings` lists the open entries by group, largest first, with age in sweeps and debt counts. It flags a group of `FINDINGS_GROUP_AT` open entries `draft one issue` and an entry of `FINDINGS_KEEP_SWEEPS` sweeps `keep or drop`, prints `none` when nothing is open, and refuses a bad file or line by name (`scripts/findings.py`, which uses `check_finding`).

## Decision ledger

Where decision points live while the work runs (`process.md`, Decision points): one file per issue, `_docs/records/decisions/<issue>.jsonl`, append-only, one JSON object per line. A line is never edited or deleted; the role that writes a line commits it with its work. The ledger is a process record, as the findings log is, so writing it is never `scope` work. Three events:

- `open`: a role met a decision point. Keys: `event`, `id` (`D-<issue>-<n>`, of the issue the file names), `at` (UTC, `YYYY-MM-DDTHH:MMZ`), `kind` (a stop kind or `choice`), `mode` (`stop` or `continue`; `continue` only for `choice`), `impact` (`L`, `M`, `C`), `effort` (`S`, `R`, `E`: the rework if the answer changes), `questions` (`q1`, `q2`, ... in order, each with `text`, lettered `options` from `A` and a `recommended` option it offers), `dependents` (paths, commits or issue ids; may be empty), and for `continue` only `rollback` (what to undo, and where). No `points` key: points come from `effort`.
- `answer`: the orchestrator records the human's answer. Keys: `event`, `id`, `at`, `answer` (`approve`, `reject`, or `q<n>=<option>` pairs separated by a comma). One per point; it closes the point.
- `reworked`: the Engineer finished a rework item. Keys: `event`, `id`, `at`, `commit` (7 to 40 lowercase hex).

```
{"event": "open", "id": "D-12-3", "at": "2026-11-23T10:15Z", "kind": "choice", "mode": "continue", "impact": "L", "effort": "R", "questions": [{"q": "q1", "text": "Where do the signup fixtures live?", "options": {"A": "tests/fixtures/signup/", "B": "tests/signup/"}, "recommended": "A"}], "dependents": ["tests/test_signup.py", "5e6f7a8"], "rollback": "move tests/fixtures/signup/ back to tests/signup/"}
{"event": "answer", "id": "D-12-3", "at": "2026-11-24T09:00Z", "answer": "q1=B"}
{"event": "reworked", "id": "D-12-3", "at": "2026-11-24T11:30Z", "commit": "9a8b7c6"}
```

A continue point answered `reject`, or with an option other than the one taken, is a rework item until a `reworked` entry names the commit. `make decisions [N=<n>]` (read-only) lists each open point with its id, impact, effort, points, mode, age in whole days and dependents, then each rework item, then `open points <p>, budget <b>:` and `within budget`, `budget reached` or `over budget` (exit 1); with N, the issue's points against the open points of every issue, with the issue's `DECISION_BUDGET` (read as `make settings N=<n>` reads it). It prints `none` when nothing is open, and refuses a bad file or line by name (`scripts/decisions.py`).
