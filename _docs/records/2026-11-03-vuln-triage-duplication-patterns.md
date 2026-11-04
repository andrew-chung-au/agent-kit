# vuln-triage duplication patterns (input to #68)

Source: the tracked copy under `vuln-triage/_docs/` (project docs only, kit copies excluded: 55 files, 222,536 words). The human confirmed on 2026-11-03 that the copy is the latest but lacks the project README. The human did not name cases; these are patterns found by reading headings and overlapping sections. Read-only analysis, one pass, not exhaustive. Quoted figures are `wc -w` counts.

## Patterns

### 1. One decision is restated in four or five places, each with its own status

Example, decision D4 (the US-15 false-positive rule):
- `roadmap.md` Open decisions row 8: status `open`.
- `human-tasklist.md` section F, row F1: `Decided 2026-10-26, option 1`, with the commit hash.
- `plan-summary.md` Open questions table: a third status column.
- `specs.md` Open questions: a fourth place, still worded as open (answers are a pointer).
- `tasks.md` and `cloud-tasklist.md` also cite it as a gate.

Effect: the status is stale in at least `roadmap.md` (row 8 reads `open`, the decision was made 2026-10-26). A reader of the roadmap gets the wrong answer. This is the "roadmaps change a bit" symptom: the same fact has no single home, so each copy drifts.

Same shape for decisions H1 to H7 (`roadmap.md` rows 12 to 18, `roadmap-future.md` header, `tasks.md` Future-development intro) and for the `D`-numbering clash with `aws-setup.md`, which `roadmap.md` has to explain in a note.

### 2. Plan, status and evidence share files

`roadmap.md` (15,945 words) holds the sequence (plan), the Open decisions table (decisions), Score checkpoints and a Check-in log (status snapshots). Its own header says the status column "is a snapshot taken at each check-in, not live state", and names the tracker and `rubric-evidence.md` as the source of truth. So the file mixes a stable plan with dated state that goes stale on the next check-in.

`human-tasklist.md` (7,506), `cloud-tasklist.md` (4,186) and `pending-verification.md` (1,713) are three more status lists, with a "Moved to the cloud list" section and a "Keeping this current" section in each tasklist. Items migrate between them by hand.

### 3. Full text kept in two places "so nothing is lost"

`specs.md` section "Future development (after submission)" keeps the story text in full; the old location holds a pointer. `tasks.md` "Future development" repeats tasks 30 to 36 in full, and `roadmap-future.md` lists them again as X-items with design notes. Three files carry the same scope, in three granularities. `specs.md` Open questions 1 to 5 and the `plan-summary.md` table repeat each other nearly word for word.

### 4. Dated and issue-numbered files accumulate beside living ones

`161-owner-apply-commits.md`, `161-responder-job-proposal.md`, `63-spec-notes-proposal.md`, `make-demo-proposal.md`, `plan-review-2026-10-12-superseded.md`, `s1-build-plan.md`, `tier-b-build.md`, `tier-c-build.md`, `reviews/*` (7 files) and `roadmap-showcase.md` (23 words, a pointer kept for old links). None says in its name whether it is current, proposal, record or retired, so the reader has to open each. The `-superseded` file is the only one that says so.

### 5. Evidence and logs dominate the word count

`ai-usage-log.md` is 61,215 words (27% of the set) and `ai-usage-report.md` is 200. Other large files: `architecture.md` 13,482, `testing.md` 10,449, `tasks.md` 8,431, `api.md` 7,864, `plan-summary.md` 7,824. Roughly a third of the set is an append-only record; the rest mixes reference (architecture, api, testing) with plans. No file states "read this for X" in the way the human's file-structure guide does with its table of detail types and best locations.

### 6. Runbooks split by command vs. explanation

`drill-runbook.md` (1,238) and `drill-runbook-commands.md` (40), `docker-runbook.md`, `compose-host-runbook.md`, `verify-locally.md`, `terraform-verify.md`, `push-check-image-guide.md`: the same how-to topics appear in more than one file, with no single runbook that the README points at (the README is the missing file the human noted).

## How this compares with the human's own structure

The human's guide (`_docs/human-inputs/2026-11-03-rag-file-structure-guide.md`) assigns each kind of detail one file: log for dates and milestones, decisions for why, evaluation notes for evidence, runbook for commands, README for one headline. vuln-triage has the equivalents (`ai-usage-log`, `roadmap` Open decisions, `rubric-evidence`, the runbooks) but each kind of detail lives in several files, and the status of an item lives in all of them.

## What would be tested next (not done)

A mechanical check for pattern 1: list every `D<n>`, `H<n>`, `F<n>`, `Q<n>` and `A<n>` key and the files that mention it, then flag keys whose status wording differs. That is proposal P6's territory. Not run here.

## Limits

One read of headings and of five overlapping sections; no claim about the other files. The project README is absent from the copy. No file was edited.
