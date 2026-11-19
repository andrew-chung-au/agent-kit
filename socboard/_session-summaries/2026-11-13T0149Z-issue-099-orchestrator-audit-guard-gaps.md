# Issue #99: Harden the audit guard's remaining DDL and id gaps

**Date:** 2026-11-13T01:49Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Heavy (from the PM proposal; no tier label). It closes #11's Low QA findings L1 to L5 in the application guard, a second layer behind #11's database triggers, before #14 writes audit entries in real use. It is the second issue with ponytail on, and the first Heavy one. Draft PR #106.

- `socboard/audit_guard.py` now refuses each of these through SQLAlchemy:
  - an INSERT on `audit_entries` that supplies a non-NULL `id` in any form, including literals, expressions, `from_select`, execute-dict keys and bound parameters under any compiled name;
  - DDL whose rendered text names the table, a trigger or `sqlite_sequence`;
  - `DropIndex` on the table's indexes;
  - the two dangerous pragmas, as words anywhere in the text;
  - `ATTACH` and `DETACH`.
  Its docstring is corrected (L5).
- New tests are in `tests/test_data_audit_guard_gaps.py`. Two existing tests lost only their explicit ids 50 and 51, by the human's ruling, with every assertion kept.
- `_docs/decisions/2026-11-12T0834Z-data-model.md` now states what is refused and what remains open: raw SQL, a custom `@compiles` DDL element, and `CreateIndex` on a lightweight table.
- **Rounds:** four Engineer rounds and two QA FAILs.
  - The first FAIL, at `70ad969`, found an id passed through a named `bindparam`, and a PRAGMA with comments between its words.
  - The second FAIL, at `45eca31`, found an id under a compiled bind name (`id_m1`, `param_1`), and a quoted schema alias in front of a pragma.
  - One CI failure at `ee0ee90` was a wrong expectation in a new test.
  - After the second FAIL the orchestrator told the Engineer to stop listing constructs: ask SQLAlchemy's compiled statement which value goes into `id`, and match the pragma names as words.
- **CI:** at `805b344`, pull-request run 43343969655 and push run 43343965543 both show 1071 passed and 157 frontend tests passed. VERIFY shows PASS WITH WARNINGS; the one warning is a comment-only change to a kept assertion.
- **QA:** first launch PASS at `805b344`. A fresh second launch (a subagent with no shared context) also passed at `805b344`, with Low findings F1 to F6.
- **Reviewer (ponytail):** six lean findings that would cut 60 to 80 guard lines. The human labelled 1 to 3 `useful` and 4 to 6 `correct-minor`. None is applied here; all six go to #107, with QA's Low items.

**What I learned:** on #11 and now #99, an application guard that lists constructs leaks at the edges round after round. Asking SQLAlchemy's compiler, not listing names, ended it. The Reviewer then found the result over-built, which is the case for running the Reviewer on Heavy issues.

## Reflection

### PM

unknown (role not asked)

### Engineer

From `.scratch/engineer-99c.md`, the round 4 comment, unchanged:

Reflection:
- Both rounds failed on spellings of a name; the fix now asks the compiler or matches the name itself, so the next QA round should look for forms where the compile path differs from execution (ORM bulk, custom dialects), not new names.
- The weak point is the hand model of crud names (`id`, `id_m<n>`); a test that compares it with `bind_names` for new forms would be the guard against a SQLAlchemy upgrade.
- Comment false positives on `DDL(...)` are now documented rather than removed.

### QA

Second launch, unchanged:

Reflection:
1. Slowed down: `.scratch/issue-99.json` is one 30000+ character line, so a read of the "body only" returned the first 30000 characters including the start of an Engineer comment; the tool output cut mid-line. Evidence: the read result ended inside an `Engineer:` comment.
2. Nearly went wrong: my first CI filter regex matched every `+ package` install line and `head -60` hid the pass counts; the first output had no counts until I ran a second script (`qa-99d-ci2.sh`).
3. Proposed change: `Makefile`/`issue-dump` (or a new `make issue-body N=99` target that writes `.scratch/issue-99-body.md` with the body only). Expected effect: a launch that must not see comments never loads them. Measure: count launches in which a "no comments" instruction was breached, over the next five Heavy second launches (target 0).

### Ponytail

Engineer, round 1: the skill shaped one helper per refusal. The Reviewer judged the final guard over-built: three extras beyond the criteria, and a compile path for one case.

## Launch usage

Active time and tool uses: unknown (Kiro Web gives neither). Tool: Kiro; model: unknown. Launches: PM 1 (grooming), Engineer 4, QA 3 (two FAIL, one PASS), QA second launch 1 (PASS), Reviewer 1, PM 1 (follow-up #107).

## Files created or modified

`socboard/audit_guard.py`, `tests/test_data_audit_guard_gaps.py` (new), `tests/test_data_audit.py`, `tests/test_data_audit_aliases.py`, `_docs/decisions/2026-11-12T0834Z-data-model.md`, `_docs/planning/roadmap-1-core.md` (#107 placed), this file.

## Decisions made by the human

- The two existing tests lose only their explicit ids (option A, the orchestrator's recommendation, taken when the human did not choose; confirmed by "I accept your recommendations").
- Finding 99-1: useful (smaller). Finding 99-2: useful (smaller). Finding 99-3: useful (smaller). Finding 99-4: correct-minor. Finding 99-5: correct-minor. Finding 99-6: correct-minor. QA had raised none of them. None applied here; all go to #107.
- The second launch's disclosed partial read of an `Engineer:` comment is accepted: it read no QA comment before writing, and its findings come from code, CI and probes.
- `make contract-check` not run (not in CI): accepted, because `openapi.yaml` is unchanged.
- Two QA FAILs in a row: noted as evidence for sweep 5; `make sweep-due` says not due.

## Mismatches with the spec or design docs

none.

## Commands to validate

- **Verify:** `make verify` (CI runs 43343969655 and 43343965543 at `805b344`).

## Proposed AGENTS.md changes

none here (the Reviewer-prefix fix is committed on #102's branch).

## Temporary changes

none. `make clean-scratch`: deferred to the end of the session (#102's and the follow-up's files are still in use).

## Interruptions

none.

## Unrelated problems noticed but not fixed

- `make issue-dump` writes the body and comments on one long line, so a "body only" read can show comments (QA's Reflection, above).
- `make contract-check` is not part of CI's `make verify` (epoch-batch item 6 is still a draft).

## Follow-ups for the next session

- #107 (simplify the guard): groom it when its trigger comes; it carries the bindparam-with-None question for the human.
- #14 next, then #15. #14 must not de-duplicate audit entries with `INSERT OR IGNORE` or `ON CONFLICT DO NOTHING`, must not edit `audit_guard.py`, and writes audit entries only through `append_audit`.
- Sweep 5 evidence: two QA FAILs in a row on a construct-listing guard; the second-launch `issue-body` proposal; the #102 Engineer's dependency-source target proposal.
