PM: groomed #112 against `main` at 8d2ee9e (the body to apply is `.scratch/groomed-112.md`; the hash below is of those exact bytes). The body has a `## Decision record` section; the Engineer does not start until the human has approved it, and `approved` should name that section.

Proposed tier: heavy
Reason: it adds a status and an error code to the contract that #21 depends on, and a handler to `socboard/errors.py` that changes how every route fails (an interface other code depends on; the #74 note called this the Heavy line).
Expected paths: `openapi.yaml`, `socboard/errors.py`, `socboard/cases.py`, `socboard/ingest.py`, `tests/test_claim_api.py`, `tests/test_transition_api.py`, `tests/test_notes_api.py`, `tests/test_notes_contract.py`, `tests/test_ingest_api.py`, `tests/test_ingest_contract.py`, `tests/test_backend_errors.py`, `_docs/decisions/<new record>.md`, `_docs/index.md`. None is on the `PROTECTED` list of `agent-kit.conf`, so no `HUMAN_APPROVED=1` commit, no `AGENTS.md` change and no `agent-kit.conf` change; `LIGHT_ALLOWED` is empty, so nothing is Light.
Spec-ready confirmation: not required (this grooms an existing issue; no backlog is built).

What I added:
- The write routes on `main`: `claimCase`, `transitionCase`, `addNote` and `ingestAlert` (`login` and the reads write nothing; `reassignCase` is planned). The draft named only #17 and #18.
- Checkable criteria with a fast test technique (lower `BUSY_TIMEOUT_SECONDS` in the test, hold the row lock as `tests/test_claim_api.py:183-209` does), a retry-succeeds case, refused cases (an error with the lock text but another code, and an `IntegrityError`, stay 500), a log check, and the contract text to change (components, Refusals table, order note, "Differences from the mock").
- Order with #115: merge #115 first. Both edit `openapi.yaml` (`claimCase`, `addNote`) and the claim and notes status-set assertions, so there is a textual conflict if both are open at once, and no code conflict (#115 touches `socboard/schemas.py`; #112 touches `errors.py`, `cases.py`, `ingest.py`).
- Claim-time decision-record check: nothing approved since the issue was filed (2026-11-13T03:36Z) contradicts a criterion. The data-model record left the lock-timeout answer to #16, and #16 left it here.

Decision needed: which routes does the 503 handler cover?
- Context: #112, Design. The lock error can also surface in a dependency (the user lookup) or at commit.
- Options:
  1. App-wide handler, documented once for any route and listed on the four writes: one place, no per-route code, a future write route is covered. A read can answer 503 in a rare window.
  2. Only the four writes (a `try` block in each, or a router-level wrapper): matches the draft's wording, but four copies, and a forgotten route brings the gap back.
- Recommendation: 1.
- If you don't answer: the body as written (option 1) is what I recorded the hash for.

Decision needed: the code name and the retry hint.
- Context: #112, Design. The draft left the code, `Retry-After` and the message open.
- Options: 1. 503 `service_busy`, `Retry-After: 1`, message "The service is busy. Please try again." 2. A different name (for example `database_busy`) or a longer hint (5 seconds, the length of the wait that already happened).
- Recommendation: 1. The name does not tie the contract to a database, and 1 second is a hint that is cheap to follow.
- If you don't answer: option 1.

Decision needed: file a follow-up issue for the Postgres lock-timeout mapping (Deploy)?
- Context: the draft puts it out of scope; the template wants every moved item to link to an issue. I did not create one.
- Options: 1. File it now (the PM drafts it; you approve; it is placed in `_docs/planning/roadmap-1-core.md` or the Deploy roadmap per `.kiro/steering/backlog-order.md`). 2. Leave it to Deploy planning and keep the out-of-scope line as written.
- Recommendation: 1, small and low priority.
- If you don't answer: the out-of-scope line stays with no link.

Residual questions: the three above.
Spec notes: none (`_docs/specs.md` says nothing on lock timeouts; the code name, message and `Retry-After` value are grooming decisions recorded in the body).

Body sha256: 5cedf334368eabec5832721c855bdd85d65b2388fdf0678a6b7ad0422492e749
