# Issue #19: Audit trail read API

**Date:** 2026-11-13T05:55Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Kiro Web worked #19 while Claude Code worked #20, a one-time human exception to `delivery-pace.md` item 4. Ponytail was on. PR: #118 (draft). The hand-off (#117) was merged at the start of the session.

- **Claim-time check:** the contract decision (`_docs/decisions/2026-11-11T1511Z-openapi-contract.md`), approved after #19 was groomed, had `getAudit` open to any authenticated user, "to be confirmed in #19". That contradicted the body's Lead-only criterion together with "matches `openapi.yaml`". The human ruled:
  - keep Lead-only;
  - #19 edits `openapi.yaml` for `getAudit`, with no body change;
  - 403 before 404.
  The rulings are recorded in the Claim comment.
- **`require_lead`** was already on `main` (added by #13), so #19 imports it and writes no copy. A note on #20 said so.
- **New route:** `GET /api/cases/{id}/audit` in `socboard/cases.py`, under `# Audit trail (#19)`.
  - It is Lead-only through the `require_lead` route dependency, so the order is 401, 403, 404.
  - Entries are ordered by time, then id. The actor is the user, or `"system"`.
  - There is no write route; the app's 405 answers other methods.
- **Response model:** `AuditEntry` in `socboard/schemas.py`. Its action list is derived from `domain.AUDIT_ACTIONS` (Reviewer 19-2).
- **Contract (`openapi.yaml`):**
  - `getAudit` is Lead-only, with a 403 and the order 401, 403, 404.
  - "Differences from the mock" gains item 14.
  - The stale "any authenticated user" fact is deleted, and the order rule names both case-free role checks (decision point).
- **Tests:** `tests/test_audit_api.py` covers:
  - the five-entry journey;
  - order by time, then id;
  - 401, 403 and 404;
  - 405 on writes;
  - an AST code search, whose exemption is now path-based (Reviewer 19-3);
  - the data-layer refusal;
  - no secrets in any entry.
  `tests/test_audit_contract.py` compares the route with the contract.
- **CI:** green on the first push. QA PASS at `178d324`. After the decision-point changes, CI was green again and the QA re-check passed at `b117d52`.
- **Roadmap:** #107 moved to before Deploy (human ruling). 19-1 was added to #110, and QA's code-search gap was added to #107.

**What I learned:** the claim-time check against newer decision records caught a real contradiction before any code was written. One ruling at the Claim cost less than a QA FAIL would have.

## Reflection

### PM

unknown (role not asked)

### Engineer

From the Engineer's comments on #19, unchanged:

- Went well: `require_lead` and `append_audit` made the route about 20 lines, and the existing 405 handling needed no code.
- Hard: nothing could run, so I read the helpers closely instead of iterating. The least certain parts are the `anyOf` and `const` shape in the generated schema, and the exact `IntegrityError` text for the raw DELETE. If CI fails, look there first.
- Skipped: no new route module, no export or search, and no change to the shared comparison helper.
- (Re-launch) Three small edits, each reached by search and a single replace. The one gap is that the enum output of the derived `Literal` is checked by reading only, so CI is the first real check.

### QA

unknown (role not asked; no Reflection block in QA's comments).

### Ponytail

The route is about 35 lines in an existing module, with one response model and no new helper. The Reviewer's verdict was "Ship", lean -0 lines. It found two real defects worth fixing (19-2, a latent 500 when an action is added; 19-3, a test exemption by base name), both applied, and one security point outside the issue's code (19-1, moved to #110).

## Launch usage

Active time and tool uses are unknown, because Kiro Web reports neither. Tool: Kiro; model: unknown. Launches:
- Engineer 2 (implementation, then the decision-point changes);
- QA 2 (PASS, then PASS on the re-check);
- Reviewer 1.

## Files created or modified

- `socboard/cases.py`, `socboard/schemas.py`, `openapi.yaml`
- `tests/test_audit_api.py` (new), `tests/test_audit_contract.py` (new)
- `_docs/planning/roadmap-1-core.md` (#107 moved; 19-1 added to #110; the code-search gap added to #107)
- this file

## Decisions made by the human

- #19 runs in parallel with #20 (Claude Code), with the agreed shared names.
- #107 waits until before Deploy.
- At the Claim:
  - Lead-only;
  - `openapi.yaml` may change for `getAudit` (the Files constraint is extended, with no body change);
  - 403 before 404.
- At the decision point (all recommendations approved):
  - D1: fix the two stale `openapi.yaml` lines in this PR.
  - Reviewer findings:
    - 19-1 moved to #110;
    - 19-2 applied;
    - 19-3 applied;
    - 19-4 recorded as a known limit (below);
    - 19-5 not applied.
  - D3: the human runs `make contract-check` once from the clean clone before merging. The code-search gaps go to #107.
  - The Engineer's uncovered choices were accepted: the declared 422, the `oneOf` compared as `anyOf` on a copy, 404 for a malformed id, and the imports outside the blocks.
  - D4: tell #20 now that `require_lead` exists. Posted.

## Mismatches with the spec or design docs

- Known limit (19-4): the audit read returns every entry, with no paging. That is fine at SOC-team scale. Revisit it with export and search.
- The frontend mock still lets any user read the trail. This is recorded as contract difference 14, and #21 aligns it.

## Commands to validate

- **Verify:** `make verify` (CI runs 43373179510 at `178d324` and 43374637710 at `b117d52`, both VERIFY: PASS).
- **Contract check:** `make contract-check`, run by the human from the clean clone before merging (it does not run in CI, and `uv` cannot run in Kiro Web).

## Proposed AGENTS.md changes

none.

## Temporary changes

none. `make clean-scratch` runs at the end of this issue, before the Close.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- `make contract-check` is not part of `make verify` or CI, so a contract edit is never machine-validated by CI. This is a candidate for the #73 + #71 `Makefile` sitting (protected).

## Follow-ups for the next session

- After #19 merges: post the notice on #20 so Claude can add #20's last test (a listed case followed to its trail, with a Lead token). Expect an import-line conflict in `socboard/cases.py`.
- Then, if the human allows: #63, then the #73 + #71 (+ #80) `Makefile` sitting.
