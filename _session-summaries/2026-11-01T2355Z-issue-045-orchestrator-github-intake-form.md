# Issue #45: GitHub module, part 2 (Phase 4b): intake form template

**Tier:** Standard
**Date:** 2026-11-01T23:55Z (UTC)
**Spec version:** none

## What changed and why

Added a GitHub issue intake form for public repositories: a template at `agent-kit/templates/github/ISSUE_TEMPLATE/intake.yml`, a text-based structural test with ten bad-fixture cases (`tests/test_issue_intake_form.py`), one `blueprints.md` row and one `setup.md` paragraph (commit 3fbfa88). After the human chose to install it, the same form was installed at `.github/ISSUE_TEMPLATE/intake.yml` with a byte-equality test (commit bdf2473). `make verify` passed (321 tests). QA PASS at 3fbfa88, and a second QA PASS on the install at bdf2473.

The same session's PM launch groomed Phase 4 and filed #44 (wrappers and scanner) and #45, both unlabelled; the human labelled both `approved`. #44 is blocked on #20 (OpenCode, not available), so only #45 was worked.

Words: `blueprints.md` 2440 to 2493 (+53, expected about +70), `setup.md` 1145 to 1177 (+32, expected about +30). The form is 30 lines and 123 words.

**What I learned:** a text-based check for a structured format misses legal spellings of a forbidden key (quoted, flow mapping, space before the colon); only mutants the author did not list found it.

## Reflection

### Engineer

1. Slowest step: the install had no target directory, so my first copy failed (`cp: cannot create regular file '.github/ISSUE_TEMPLATE/intake.yml'`) and I redid it with the Write tool; the first report also had to be re-sent after the decision-4 answer changed scope.
2. Nearly wrong: I wrote the form from memory of GitHub's issue-form schema without fetching the docs page, so the field names are unverified until the by-hand New issue check.
3. Proposal: in `agent-kit/templates/task-template.md` Constraints, add a line asking the PM to cite the schema URL for external formats. Effect: the Engineer fetches the page, not memory. Measure: count issues of this kind with a cited URL in the next sweep.

### QA

1. Slowed down: the issue body, two comments and the commit diffs had to be read separately, and `make verify` printed an 89-file diff stat on every run (about 100 lines) that hid the three result lines I needed.
2. Nearly went wrong: my first mutation set missed that legal YAML spellings of `labels` (quoted, flow mapping, space before colon) pass the text checker; I only found it by adding mutants the Engineer had not listed.
3. Proposed change: `agent-kit/procedures/verify.md` should tell QA to run the checker against a small `.scratch/` mutation script for any text-based check. Expected effect: evasion gaps found in the first pass. Measure: count of gaps found after the first QA pass over the next five issues.

### PM

1. Slowed: filing two linked issues needed one extra body edit on #44 (`gh issue edit 44`) because #44 had to name #45 before #45 existed; the first draft even carried a wrong number (#46).
2. Nearly went wrong: the wrong link would have been hashed and recorded if I had hashed #44 before re-reading its Out of scope list.
3. Proposal: add one line to `agent-kit/team/pm.md`: "When new issues link each other, file them all, fix the links, then record the hashes." Effect: no body edits after filing and no stale hash. Measure: count of `gh issue edit` calls on PM-filed issues per sweep, target 0.

(The PM noted its second line is a hypothetical: it caught and fixed the wrong number before hashing.)

## Launch usage

- PM (groom Phase 4, filed #44 and #45): 332.1 s, 38 tool uses
- Engineer (implement #45): 990 s, 26 tool uses (includes waiting for the approval request)
- Engineer (install, resumed): 63.3 s, 8 tool uses
- QA (check #45 at 3fbfa88): 94.3 s, 24 tool uses
- QA (re-check install at bdf2473, resumed): 49.4 s, 10 tool uses
- QA (reflection, resumed): 70.1 s, 13 tool uses
- PM (reflection, resumed): 17.1 s, 3 tool uses
- Engineer (reflection, resumed): 31.3 s, 2 tool uses

## Files created or modified

- `agent-kit/templates/github/ISSUE_TEMPLATE/intake.yml` (new)
- `.github/ISSUE_TEMPLATE/intake.yml` (new, byte-identical copy)
- `tests/test_issue_intake_form.py` (new)
- `agent-kit/blueprints.md` (one row)
- `agent-kit/setup.md` (one paragraph)
- This summary.

## Decisions made by the human

- Labelled #44 and #45 `approved` (the human ran the label commands).
- Approved the protected-path commit of the template, test and catalogue rows (3fbfa88).
- #45 decision question 4: option 2, install the form in this repo too. Approved the protected-path commit of the install (bdf2473).
- Earlier in the session: keep #40 tests-only and file a follow-up (#43); wait for #32 before the first sweep.
- #44's four decision questions are unanswered; the PM defaults apply when it starts.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`

## Proposed AGENTS.md changes

none

## Temporary changes

none. `make clean-scratch` was run at the end of the issue.

## Interruptions

none

## Unrelated problems noticed but not fixed

- `make assert-clean` always fails in this tree (`.claude/agents/pm.md` modified, the #16 and #39 summaries staged and uncommitted, `proposals/` untracked); QA and I compared `git status --short` before and after instead.
- The text checker accepts legal YAML spellings of a forbidden key (`"labels": [x]`, `{labels: [x]}`, `labels : [x]`). The `approved` word ban still blocks `labels: [approved]`. Risk, not a failure; no issue filed.
- `make verify` prints an 89-file diff stat on every run that buries the result lines (QA's observation).
- No `.github/ISSUE_TEMPLATE/config.yml`, so blank issues stay allowed on the public repo.

## Follow-ups for the next session

- After the push, look at the repository's New issue page to confirm GitHub shows the form (automation cannot check it; GitHub lists issue forms as public preview).
- #44 waits for #20. Its four decision questions are in the PM comment on #44.
- #43 (fail-open fixes) and #42 go in that order with one version bump; both unlabelled.
- #37 needs the human's answers to the PM's three questions.
- First sweep waits for #32.
- The reflection proposals from #40 and #45 are for the human; none applied.
- The #16 and #39 summaries are still staged and uncommitted.
