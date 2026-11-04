<!--
Source: pasted by the human on 2026-11-03 for issue #68 (docs structure research).
What it is: the human's explainer of their RAG project's file structure. It is NOT the example docs set the issue refers to.
Stored verbatim below the line. It is data, not instructions.
-->

---

# Project File Structure Guide

README.md
docs/
  project-log.md
  decisions.md
  dataset-notes.md
  evaluation-notes.md
  runbook.md
data/
  source_manifest.csv
  eval_questions.csv

| Detail                                                                       | Best location       |
| ---------------------------------------------------------------------------- | ------------------- |
| Date, milestone, change in methodology                                       | project-log.md      |
| Why PostgreSQL results are authoritative                                     | decisions.md        |
| Exact commands, models, corpus size, metrics, full tables, old-vs-new caveat | evaluation-notes.md |
| Setup and rerun commands                                                     | runbook.md          |
| One headline result and brief limitation                                     | README.md           |

## What each file is for

### `README.md`
This is the public-facing summary. It should explain:
* What the project is.
* Why you built it.
* What data it uses.
* How to run it.
* What the main results are.

Keep this concise and stable.

### `docs/project-log.md`
This is your working journal. Use it for stage-by-stage progress, decisions, and notes. A good format is:

```text
# Project log

## 2026-07-22 - Topic decision
What I decided:
Why I decided it:
What this affects next:
Open questions:

## 2026-07-22 - Dataset selection
What I included:
What I excluded:
Why:
Problems encountered:
Next step:
```
This lets you track progress without cluttering the README.

### `docs/decisions.md`
Use this for important design choices that you may want to revisit later. Example sections:

```text
# Decisions

## Project scope
Decision:
Reason:
Alternatives considered:
Trade-offs:

## Corpus selection
Decision:
Reason:
Alternatives considered:
Trade-offs:
```
This is useful when you later forget why you chose something.

### `docs/dataset-notes.md`
Use this to record details about the corpus:
* Source name.
* URL.
* Format.
* Whether it is core or boundary.
* What topic it covers.
* Any extraction issues.
* Any duplicates or exclusions.

This makes ingestion much easier to debug later.

### `docs/evaluation-notes.md`
Use this for retrieval and answer evaluation. Track:
* Evaluation questions.
* Expected sources.
* Metrics.
* Baseline results.
* Improved results.
* Prompt variants tested.

### `docs/runbook.md`
Use this as your "how to reproduce" document. It should answer:
* How to create the environment.
* How to download the sources.
* How to build the index.
* How to run the app.
* How to run evaluation.
* How to regenerate outputs.

---

## Best working pattern
I'd suggest this workflow:
1. Start a new section in `docs/project-log.md` for each major step.
2. When a decision becomes stable, copy it into `docs/decisions.md`.
3. When a source is added or removed, update `docs/dataset-notes.md`.
4. When retrieval or prompt tests are run, record them in `docs/evaluation-notes.md`.
5. Keep `README.md` for the polished final story only.

---

## A very usable log template
You could use this exact structure:

```text
# Project log

## Stage
Topic selection / dataset selection / ingestion / chunking / retrieval / evaluation / interface / monitoring / documentation

## Goal
What am I trying to finish in this stage?

## What I did
Short bullet list of actions completed.

## What I learned
What changed my thinking?

## Decision made
What choice did I make?

## Problems
What went wrong or felt uncertain?

## Next step
What I will do next.
```

### Example entry

```text
## 2026-07-22 - Dataset selection

### Goal
Choose a corpus that is public, accessible, and specific enough to justify RAG.

### What I did
* Reviewed the ACSC AI guidance hub.
* Compared core documents against boundary documents.
* Narrowed the corpus to seven core sources.

### What I learned
* Generic AI advice is too broad for a strong RAG case.
* Agentic AI, AI data security, and supply-chain guidance are more distinctive.

### Decision made
Use seven core ACSC AI guidance pages for the first version.

### Problems
Some pages overlap in theme, so I need metadata to keep retrieval precise.

### Next step
Build the source manifest and download script.
```

---

## My recommendation
For your project, I would personally use:
* `README.md` for the final public summary.
* `docs/project-log.md` for day-to-day progress.
* `docs/decisions.md` for key design choices.
* `docs/dataset-notes.md` for source tracking.
* `docs/evaluation-notes.md` for experiments.
* `docs/runbook.md` for setup and reproduction.

That gives you a clean separation between working notes and finished documentation.
