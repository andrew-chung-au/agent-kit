PM: groomed #115 against `main` at 8d2ee9e (the body to apply is `.scratch/groomed-115.md`; the hash below is of those exact bytes).

Proposed tier: standard
Reason: it documents behaviour that already exists, with no new status, code or order; the one code change moves a length check to a field constraint and must answer the same 422 (precedent: #74 and #86 were Standard). Heavy if a response status, body or order changed in the code.
Expected paths: `openapi.yaml`, `socboard/schemas.py`, `tests/test_queue_contract.py`, `tests/test_claim_api.py`, `tests/test_audit_contract.py`, `tests/test_notes_contract.py`. None is on the `PROTECTED` list; `LIGHT_ALLOWED` is empty, so nothing is Light.
Spec-ready confirmation: not required (this grooms an existing issue; no backlog is built).

What changed in the body:
- `main` moved. #19 added a third accepted 422 difference (`getAudit`, `tests/test_audit_contract.py:11-12`, `:71-76`); the criteria now cover `getCase`, `claimCase` and `getAudit`. All line references are refreshed.
- (c) is already met: `openapi.yaml:93-110` says 401 first only "provided the body parses as JSON" and that a body that is not JSON gives 422 even with no token (`tests/test_backend_order.py:78` pins it). The criterion is cut down to adding the reason at `:106`.
- (b) fixed a self-contradiction: the old fallback ("keep the validator, say `maxLength: 5000` in the contract") cannot pass the comparison, because the comparison fails on a keyword in one document only (`tests/test_ingest_contract.py`). The limit moves to `max_length` on the field, so `socboard/schemas.py` is now an expected path, not a maybe.
- "`make verify` shows 0 assertion lines removed" could not hold, because the criteria rewrite the status-set assertions. It now says those lines are listed as rewritten and each gets a reason in the `Engineer:` comment.
- Added the refused cases (5,001 characters, 5,001 emoji, over-limit on a Closed case stays 422), the Refusals-table row, and the order with #112 (merge #115 first).
- The dangling `.scratch/2026-11-13T0424Z-measure-pm-sweep.md` reference now points to `_docs/records/2026-11-13T0424Z-measure-pm-sweep.md` and the committed session summaries.
- Claim-time decision-record check: no record approved since the issue was filed (2026-11-13T04:50Z) contradicts a criterion. `_docs/decisions/2026-11-11T1511Z-openapi-contract.md` rejects a schema `minLength` on `text`, not a `maxLength`.
- Depends on #17: satisfied (closed 2026-11-13). #17 and #20 added no contract differences.

Residual questions: none
Spec notes: none

Body sha256: 6c08ec36942905820365ccd8ea0009ebcf35630992360d67cdc4177aea11ef9c
