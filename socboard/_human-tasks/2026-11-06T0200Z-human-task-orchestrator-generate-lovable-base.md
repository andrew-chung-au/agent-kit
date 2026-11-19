# Generate the Lovable frontend base

## Purpose

Produce the frontend base that the scaffold task imports, following the Lovable guidance. Issue: the scaffold task (number added when it is filed).

## Where to run it

In a browser for Lovable, then on your machine for the clone. Not here: don't connect Lovable to this repository. Its sync commits straight to the default branch of whatever repository it is connected to.

## Before you start

1. Confirm the scaffold issue is groomed and approved, so the import belongs to it.

```
gh issue list --state open --label approved
```

Expected: the scaffold issue is listed.

2. Find the starting prompt and the guardrails.

```
grep -n '^## ' _docs/planning/lovable-guidance.md
```

Expected: headings including "Guardrails" and "Starting prompt".

## Steps

### Step 1: Prompt Lovable

In Lovable, paste the starting prompt from the guidance together with the relevant parts of `_docs/specs.md`. Iterate until the queue, the case detail and the audit trail screens look right.

Expected: a working app that runs on mock data, with no real backend.
If different: keep iterating in Lovable. Don't edit the code by hand yet.

### Step 2: Let Lovable create its own repository

Connect Lovable to GitHub so that it creates a new repository of its own.

Expected: a new repository under your GitHub account, separate from this one.
Risk: Lovable then syncs to that repository's default branch. That is expected.

### Step 3: Clone it to a scratch folder outside this repository

```
git clone <lovable-repo-url> <scratch-folder>
```

Read the repository address from the new repository's page on GitHub.

Expected: the clone completes.

### Step 4: Check the guardrails

```
grep -rn -E "dangerouslySetInnerHTML|supabase" <scratch-folder>/src
```

Expected: no matches. Also check by eye that every backend call goes through one service layer with a mock implementation, and that severity is only displayed, never computed.
If different: ask Lovable to fix it. Don't continue to Step 5.

### Step 5: Copy it into this repository without its git history

```
rsync -a --exclude='.git' <scratch-folder>/ frontend/
```

Expected: `frontend/` holds the app, and `git status --short` shows it as untracked. Leave it uncommitted: the scaffold issue's Engineer commits it as a normal reviewed commit.
Risk: none. Deleting `frontend/` undoes it.

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets either.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 to 5 | Done, differently | Recorded 2026-11-10. The human generated the base in Lovable and committed it directly as fab3dd3, not through the scaffold issue's Engineer. Step 4's guardrail search would have found `dangerouslySetInnerHTML` in `src/components/ui/chart.tsx`. The import was then reviewed in #7 and fixed in #27 (the chart file is removed). Source record: `_docs/records/2026-11-10T0946Z-source-lovable-frontend.md`. |

## Risk

Connecting Lovable to this repository by mistake would let it commit straight to main. If that happens, disconnect it in Lovable's GitHub settings and tell the orchestrator.
