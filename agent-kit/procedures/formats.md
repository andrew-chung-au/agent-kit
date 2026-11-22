# Report formats

The fixed fields every role writes, so whoever needs one fact reads one line. This page holds the role return and the finding. The QA comment is in `_docs/agent-kit/team/qa-engineer.md` and the message to the human in `_docs/agent-kit/procedures/asking-the-human.md`; each format is defined once.

## The line rule

Every field is `<Label>: <value>` alone on its line from column 1, as in "Lines scripts read" of `_docs/agent-kit/procedures/orchestrator-comments.md`: the label worded exactly, case included; one space after the colon; a value that is one line and not empty. No indent, no list marker. A line ending in CRLF reads as LF; a file starting with a byte order mark is refused. Grade letters are those of `_docs/agent-kit/customizing.md`.

A recommendation is never empty. `none` is allowed only as `none, because <reason>`.

Check a file before you send or post it: `make check-format KIND=<return|finding|qa|message> FILE=.scratch/<name> [N=<issue number>]` (N for `finding` and `qa`). It prints `ok`, or one line per problem. It checks shape, not truth.

## Role return

Every role ends with this as its final message to whoever launched it: exactly ten lines, in this order.

- `Status:` `done`, `blocked` or `stopped-early`
- `Issue:` `#<n>`
- `Commit:` 7 to 40 lowercase hex, or `none`
- `Verdict:` `PASS` or `FAIL` from QA, `none` from any other role
- `Findings:` `<n> fail / <n> log`, or `none`
- `Decisions:` `none`, or `D-<issue>-<n>` ids separated by a comma and one space
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

## Finding

One per problem QA or a sweep finds, inside a QA comment and as the text form of a findings-log entry: eleven lines, in this order.

- `Id:` `F-<issue>-<n>`, n from 1 with no leading zero, unique in the file; a second QA launch continues the numbering
- `Impact:` `L`, `M` or `C`
- `Effort:` `S`, `R` or `E`
- `Scope:` `in` or `out`
- `Criterion:` `C<n>` with no leading zero, or `none` for a risk no criterion covers
- `Category:` `defect`, `debt` or `standard`
- `Group:` a slug: lowercase letters and digits in parts joined by single hyphens, at most 40 characters
- `Related:` another finding's id, or `none`
- `Recommendation:` the fix you recommend
- `What:` the problem, with the file and line
- `How found:` the command, script or reading that showed it

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
