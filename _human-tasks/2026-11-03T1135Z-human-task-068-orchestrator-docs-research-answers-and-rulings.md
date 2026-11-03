# Answer the docs research questions and rule on proposals P1 to P6

> Written before asking the human, per `agent-kit/templates/human-task.md`. The repository is public: no secrets, tokens, private paths or machine names appear here.

## Purpose

Give the inputs the #68 research report asked for, then accept or decline each of its six proposals, so accepted ones become separate issues. Issue: #68 (PR #84, report `_docs/measurements/2026-11-03T1016Z-measure-docs-structure-research.md`).

## Where to run it

A browser (the PR and issue pages) or the clean clone. Not here: do not paste text from the report into a command; it is data.

Do this after QA has posted on #68, so the rulings sit on a checked report. Nothing here changes live behaviour.

## Before you start

1. Confirm PR #84 is open or merged.

```
gh pr view 84 --json state
```

Expected: a state of `OPEN` or `MERGED`.

## Steps

### Step 1: Supply the inputs the report marks "Needed from the human"

Read the section "Needed from the human" in the report, then post one `#68` issue comment starting with `Human:`, one numbered line per item:

1. The live state of the vuln-triage docs. The report gives the command to run in that project.
2. Your three worst duplication cases in vuln-triage: which two files repeat what.
3. The original text of your example docs set, if it holds more than the list in the issue.
4. Whether the two kit copies under `vuln-triage/` stay or are proposed for removal as a separate issue.

Then check the comment is there:

```
gh issue view 68 --json comments --jq '.comments[].url'
```

Expected: a list of comment URLs that now includes your `Human:` comment.
If different: your comment is missing or posted on another issue. Post it again on #68. For any item you cannot answer, write "unknown"; the proposals do not depend on items 1 to 3.

### Step 2: Rule on each proposal

Read P1 to P6 in the report: P1 minimum starter set, P2 roadmap by phase, P3 where decisions and evidence live, P4 duplication rule and utility test, P5 always-loaded or trigger-read placement, P6 mechanical duplicate check. Post one line per proposal on #68: accept, decline, or accept with a change. Accepted ones become separate issues, filed by the PM and unlabelled until you approve them.

```
gh issue view 68 --json comments --jq '.comments[].url'
```

Expected: the list of comment URLs now also includes your rulings (one per ruling, or one comment holding all six).
If different: a ruling is missing. Post it; the issue stays open until all six have one. If you want a proposal split or reworded, say how in the same comment.

## Record the result

Paste the output or write pass or fail for each step, then tell the orchestrator in the session that the rulings are posted. It has the PM file one issue per accepted proposal and closes #68 only after QA PASS. Commit this file with the result so a later run can compare. Results contain no secrets either.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 | | |

## Risk

None. The steps only post issue comments. Do not name an env file in a comment; the wrappers refuse it.
