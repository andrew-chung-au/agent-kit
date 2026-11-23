# Docs index

No front matter; metadata lives here.

| Detail | Goes in |
|---|---|
| Session narrative and what was learned | a log entry |
| A choice that may be revisited, with reasons and alternatives | a decision record |
| Exact commands, numbers, full tables and caveats | a measurement |
| One headline result plus its limitation | README, linking to the measurement |
| Anything stable and long-lived | a canonical doc |

Write once, link elsewhere: log entries link to stable decisions. README: one headline result and its limitation, no run tables.

## Entry types

By folder: "no doc without an index entry" can't work for hundreds of entries. Names: `agent-kit/procedures/session-summary.md`.

| Type | Folder | Template | Filename pattern |
|---|---|---|---|
| Record: what was measured, found or read, with method and caveats (flat; the filename kind, such as `measure` or `source`, tells them apart; a sweep entry is `measure-pm-sweep`) | `_docs/records/` | `agent-kit/templates/measurement.md` (plus the sections in `agent-kit/procedures/sweep.md` for a sweep), `agent-kit/templates/source.md` | `<timestamp>-<kind>-<slug>.md`; a sweep entry is `<timestamp>-measure-pm-sweep.md` |
| Plan: what we intend to do and in what order, such as the current status (rewritten in place, its Date line says how fresh it is) | `_docs/planning/` | none | `current-status.md`, or `<slug>.md` |
| Decision | `_docs/decisions/` | `agent-kit/templates/adr.md` | `<issue>-<slug>.md` |
| Human task | `_human-tasks/` | `agent-kit/templates/human-task.md` | `<timestamp>-human-task-<id>-<role>-<slug>.md` |

## Canonical docs

By file. Add project manifests here.

| Path | Canonical for | Status |
|---|---|---|
| `_docs/decisions/091-installed-file-map.md` | Decision for an installed-file map in the kit folder, read by one shared parser, with joint import and a feedback bundle, and the two `vuln-triage/` copies kept until the comparison (#91) | Approved 2026-11-03 |
| `_docs/decisions/119-issue-close.md` | Decision to add `make issue-close` (#119) | Approved |
| `_docs/decisions/156-planning-gate.md` | Decision to add `procedures/planning.md` and a spec definition of ready (#156) | Approved |
| `_docs/decisions/159-planning-guidance.md` | Decision to add a testable example, a plan-review checklist and a one-intent rule to the planning guidance (#159) | Approved |
| `_docs/decisions/160-design-section.md` | Decision to add an optional Design section to the issue template (#160) | Approved |
| `_docs/decisions/161-spec-note-layout.md` | Decision to add a fixed layout for spec notes (#161) | Approved |
| `_docs/decisions/169-kit-baseline.md` | Decision to find a no-manifest kit's baseline with `kit-baseline.py` and make its manifest by hand (#169) | Approved |
| `_docs/decisions/182-doc-structure.md` | Decision to split the kit docs by purpose with one home per fact, and test the intended copies (#182) | Approved |
| `_docs/decisions/172-github-repo-source.md` | Decision that the GitHub wrappers take the repository from `GITHUB_REPO` in `agent-kit.conf` and use `gh api` (#172) | Approved |
| `_docs/decisions/196-kit-settings.md` | Decision that kit settings live in `agent-kit.conf`, read as text by one reader in the kit's scripts, with profiles; and that acceptance criteria are numbered `C<n>` with a `Check:` line (#196) | Approved 2026-11-20 |
| `_docs/decisions/197-issue-overrides-and-rulings.md` | Decision that issue overrides and session rulings are two more levels of `read_settings`, read from the issue dump, inside bounds no level can cross, with waivers recorded in the same layout (#197) | Approved 2026-11-20 |
| `_docs/decisions/198-report-formats.md` | Decision that role returns, findings, QA comments and messages to the human are line-based `<Label>: <value>` fields, with finding labels mapped to the findings-log JSON keys, checked for shape by `check-format.py` through `make check-format` (#198) | Approved 2026-11-22 |
| `_docs/decisions/199-qa-routing.md` | Decision that QA's verdict follows from its findings' impact and scope under the settings, checked by `check-format KIND=qa`, and that failing findings are routed by points computed from the issue's QA comments by `route-findings.py` (#199) | Approved 2026-11-22 |
| `_docs/decisions/200-findings-log.md` | Decision that unfixed findings are logged by group in write-once per-issue files, with the sweep's rulings in one append-only file and ages counted in sweep entries, read by `findings.py` (#200) | Approved 2026-11-22 |
| `_docs/decisions/201-criteria-checklist.md` | Decision that the Engineer's issue comment lists every criterion in four fixed forms defined once in `formats.md`, checked by a doc test and by QA's reading, with no script (#201) | Approved 2026-11-22 |
| `_docs/records/findings/` | The findings log: one `<issue>.json` per closed issue, written once at close, in the format of `agent-kit/procedures/formats.md` (Findings log); `make findings` lists the open entries | Written at each close |
| `_docs/records/findings-rulings.jsonl` | The sweep's rulings on findings log entries (`issued`, `dropped`, `kept`, `regroup`), append-only; absent until the first sweep rules | Appended at each sweep |
