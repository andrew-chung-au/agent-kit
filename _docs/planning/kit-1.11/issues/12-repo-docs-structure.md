Title: Move this repo's docs into one _docs/ tree following socboard's layout, with an index row for each file

**What is wrong or missing**

This repo keeps docs in several top-level places: `proposals/` (plans, plus `helpers.sh` and `pre-push-v3`), `_docs/human-inputs/`, and the two project copies `socboard/` and `vuln-triage/` at the root. `_docs/index.md` lists only decisions. socboard's `_docs/` (decisions, records, planning, runbooks, one index) proved easier to navigate, and 1.11 adds more records (findings, reflections, human-task archive) that need fixed homes.

**What you expected**

One `_docs/` with `decisions/`, `records/`, `planning/`, `runbooks/` and `reference/`, and an index row for each file in it (proposal section 9 row 12).

Plan fields:

- Proposed tier: standard (section 9).
- Effort: R. Mostly `git mv` and index rows; the reference checks make it more than S.
- Reasoning: B. The moves follow from the issue text; the open points are listed under Questions.
- Impact: M. A broken link or a dup-report exclusion pointing at an old path is confusing but recoverable.
- Needs: none (section 9: parallel lane).
- Runs in: sandbox.
- Debt: none.
- Touches protected `agent-kit/` files: no. Touches this repo's `Makefile` (protected: the `dup-report` target excludes `vuln-triage/` and `proposals/`) and possibly `README.md` and `AGENTS.md` (protected) if they name the moved paths.
- Files: `proposals/*` to `_docs/planning/`, `_docs/human-inputs/*` to `_docs/records/`, `socboard/` and `vuln-triage/` to `_docs/reference/socboard/` and `_docs/reference/vuln-triage/`, `_docs/index.md` (a row per file), `_docs/decisions/091-installed-file-map.md` (a dated note on the new `vuln-triage` paths, not a rewrite), `Makefile` (`dup-report` excludes), and any file `grep` finds naming an old path.

Acceptance criteria:

- [ ] C1. `_docs/` has `decisions/`, `records/`, `planning/`, `runbooks/` and `reference/`; `proposals/` and `_docs/human-inputs/` no longer exist; the project copies are under `_docs/reference/`.
  Check: `ls _docs proposals _docs/human-inputs` (the last two report missing); `git log --follow` on one moved file shows its history.
- [ ] C2. Every file under `_docs/` outside `reference/` has a row in `_docs/index.md`; `reference/` has one row per project copy (not per file).
  Check: a `.scratch/` script lists `_docs/` files and compares with the index rows; it prints no missing row.
- [ ] C3. No live reference points at an old path: a search of tracked files outside `_docs/reference/` for `proposals/`, `human-inputs`, and root-level `socboard/` and `vuln-triage/` finds only historical text (session summaries, records), and each remaining hit is listed in the Engineer's comment with why it stays.
  Check: a `.scratch/` script runs the search; compare its hits with the Engineer's list.
- [ ] C4. `make dup-report` excludes the new paths of the moved project copies and planning files as it excluded the old ones.
  Check: run `make dup-report`; read the `Makefile` target.
- [ ] C5. Decision 091 gets a dated note naming the new `vuln-triage` kit paths; its decision text is not changed.
  Check: read `_docs/decisions/091-installed-file-map.md`.
- [ ] C6. `make verify` passes; no test depends on the old paths.
  Check: run `make verify`.

Questions for the human (decision questions, with recommendations):
1. socboard's `_docs/` has no `reference/` (it has `decisions`, `evidence`, `planning`, `records`, `runbooks`, `team`, `vendor`). Keep `reference/` as section 9 says? Recommended: yes; it is the clearest name for read-only project copies.
2. `proposals/helpers.sh` and `proposals/pre-push-v3` are scripts under review in issue #6 and issue #3, not plans. Options: A move them to `_docs/reference/proposed-scripts/`; B leave them in `proposals/` until those issues close. Recommended: A, with a note on issue #6 and issue #3 (posted by the orchestrator only if those issues allow comments).
3. `_docs/planning/kit-1.11/workflow-review.md` (the proposal) was committed into `_docs/planning/kit-1.11/` on 2026-11-19, so it no longer needs moving; only the older files in `proposals/` do.
4. `_session-summaries/` and `_human-tasks/` stay at the root (the kit names those paths). Recommended: yes, until issues 06 and 07 settle them.

Out of scope: the kit's own folder layout (`agent-kit/`, decided in issue #182); trimming the project copies further (proposal section 11 "Later" rows).

Proposed split: none.

**Evidence**

- Proposal section 9 row 12, section 11 (the trimmed copies, commits `c68bfe7` and `5fcddf7`).
- socboard's layout: `socboard/_docs/` with `decisions/`, `records/`, `planning/`, `runbooks/` and `index.md`.
- Current paths: `proposals/`, `_docs/human-inputs/2026-11-03-rag-file-structure-guide.md`, `Makefile` line 88 (`dup-report --exclude vuln-triage/ --exclude proposals/`), `_docs/decisions/091-installed-file-map.md` (names `vuln-triage/agent-kit/` and `vuln-triage/_docs/agent-kit/`), `_docs/decisions/182-doc-structure.md`.
