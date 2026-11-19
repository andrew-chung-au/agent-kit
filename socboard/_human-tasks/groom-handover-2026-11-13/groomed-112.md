Follow-up from #16, approved by the human at #16's decision point (`_docs/agent-kit/process.md`, Lifecycle step 7).

## Why

On #16 (`POST /api/cases/{id}/claim`), a write that waits longer than SQLite's busy timeout (`BUSY_TIMEOUT_SECONDS = 5`, `socboard/database.py:32`) for another writer's lock gets the generic 500 `internal_error`, with nothing committed, because `openapi.yaml` has no code for it. The client cannot tell a transient lock wait from a server fault, so it does not know that retrying is safe. Source: QA's risk 2 ("Lock timeout answers 500 `internal_error`") in its #16 PASS comment, and the #16 session summary (`_session-summaries/2026-11-13T0343Z-issue-016-orchestrator-claim-single-owner.md`, "Lock timeout: keep the 500 `internal_error` for Core; the PM filed #112"). The data-model decision record (`_docs/decisions/2026-11-12T0834Z-data-model.md`) left the choice to #16; the human chose to keep the 500 for Core and handle it here. The module docstring of `socboard/cases.py` (lines 7-9) says the timeout is not mapped.

The same gap exists on every write route that exists on `main` (listed at grooming, 2026-11-13): `claimCase` (`socboard/cases.py`, #16), `transitionCase` (#17), `addNote` (#18) and `ingestAlert` (`socboard/ingest.py`, #14). `login` and the reads write nothing. `reassignCase` is planned and not built.

## Goal

A request that fails only because it timed out waiting for the database write lock gets a documented, retryable answer (503 `service_busy` with a `Retry-After` header) that is in `openapi.yaml`; nothing is committed, so the client can retry safely.

## Acceptance criteria
- [ ] `openapi.yaml` has a shared response (in `components/responses`) for status 503, code `service_busy`, body `ApiError`, with a `Retry-After` header documented as integer seconds, value `1`. `claimCase`, `transitionCase`, `addNote` and `ingestAlert` each list `"503"` with it. The Refusals table gets a row (`Database lock timeout | 503 | service_busy (new)`), and the "outside any operation" table says any route can answer it (see Design). The "Order of checks" text says it can replace the answer of the first statement that needs the write lock, after the 401 and the schema 422. "Differences from the mock" lists it as new (the mock has no such code) and the sentence "Codes the mock lacks are new:" names `service_busy`. `make contract-check` passes.
- [ ] A claim that times out on the lock gets 503, body exactly `{"code": "service_busy", "message": "<fixed text>"}`, and a `Retry-After: 1` header, not 500. The case's owner is unchanged and no audit entry is written. The test holds the case row's write lock from a second connection (as `tests/test_claim_api.py:183-209` does) past a busy timeout the test lowers to 0.5 s or less (monkeypatching `socboard.database.BUSY_TIMEOUT_SECONDS` before the first request), so it does not wait 5 s.
- [ ] The same test exists for `transitionCase`, `addNote` and `ingestAlert`: 503, same body and header, and nothing stored (status, owner, note, alert, case and audit rows all unchanged).
- [ ] Retrying is safe: after the lock is released, the same claim request succeeds (200) and writes exactly one `claimed` audit entry.
- [ ] The answer is chosen by the driver's error code for SQLite busy or locked, not by the message text. Refused case: an `OperationalError` whose text says "database is locked" but whose code is another one (for example an I/O error), and an `IntegrityError`, still get the generic 500 `internal_error` with no `Retry-After` header and no detail in the body.
- [ ] The response body and the log do not include the SQL statement, the parameters or the driver message. A `caplog` test over the 503 path finds no log record, at any level, containing the statement text or "database is locked", and the handler logs one fixed-text line without a traceback.
- [ ] A lock timeout on a read route also answers 503 (the handler is app-wide), tested once with a simulated driver error; the 500 handler is unchanged for everything else (`tests/test_backend_errors.py` unchanged).
- [ ] The generated OpenAPI of the four write routes lists `"503"` with an `ApiError` body and the `Retry-After` header, and the contract tests of those routes assert the status sets equal (adding `"503"` to both sides), so nothing is exempted.
- [ ] No existing response status, body or order changes in the code, and no assertion is weakened: the only assertion lines changed are the contract status-set lines that gain `"503"` (`make verify` lists them as rewritten, and the `Engineer:` comment gives the reason). The busy timeout stays 5 s (`tests/test_data_engine.py:88` unchanged).
- [ ] The decision record is committed as a file in `_docs/decisions/` with its row in `_docs/index.md`; the comment in `socboard/errors.py` that says to add no code without a contract change is satisfied by this issue's `openapi.yaml` change.
- [ ] `make contract-check` and `make verify` pass.

## Out of scope
- Changing the busy timeout value or the SQLite transaction mode (`_docs/decisions/2026-11-12T0834Z-data-model.md`).
- Postgres lock-timeout and deadlock behaviour and its error mapping (Deploy phase, `_docs/planning/roadmap-3-deploy.md`). Only SQLite busy and locked are recognised here, in one function whose docstring says so. No follow-up issue exists yet; the PM proposes one in the grooming comment for the human to approve.
- What the frontend does with a 503 (retry, message): #21 reads the contract; the mock and `frontend/` are unchanged here.
- Documenting the 503 on `reassignCase`: it is planned and not built; it gets the same response when it is.
- The 422s and the note limit missing from the contract: #115, which merges first.

## Design

The choices below are made in this body and recorded in the decision record that follows; approving the body approves them.

- Status 503, code `service_busy`, fixed message "The service is busy. Please try again." and `Retry-After: 1`. 503 is the status for a temporary inability to serve; 409 would collide with `already_claimed`, 429 means a rate limit, 504 means a gateway.
- One handler in `socboard/errors.py` for the SQLAlchemy `OperationalError` whose wrapped driver error is SQLite BUSY (5) or LOCKED (6), matched on the error code (`sqlite_errorcode` with the low byte masked, Python 3.12). It is registered in `register_error_handlers`. The write routes need no new `try` block; each declares `503` in its `responses` so the generated document matches the contract. The Engineer may propose a different way to recognise the code, with a reason.
- The handler is app-wide, so the contract states it once as a refusal that can happen on any route (like 404, 405 and 500) and lists it on the four write operations. A lock timeout in a read, such as the user lookup, is retryable too.

## Constraints
- Files: `openapi.yaml`, `socboard/errors.py`, `socboard/cases.py` and `socboard/ingest.py` (the `responses` declarations and the stale docstring in `cases.py:7-9`), `tests/test_claim_api.py`, `tests/test_transition_api.py`, `tests/test_notes_api.py`, `tests/test_notes_contract.py`, `tests/test_ingest_api.py`, `tests/test_ingest_contract.py`, `tests/test_backend_errors.py` (new tests), `_docs/decisions/<new record>.md`, `_docs/index.md`.
- Protected files (`PROTECTED` in `agent-kit.conf`): none of the paths above is on it, so no commit needs `HUMAN_APPROVED=1`, no `AGENTS.md` change is needed and `agent-kit.conf` stays as it is. `openapi.yaml` and `socboard/errors.py` are not protected, but they are the interface #21 builds to, which is why this is Heavy. Under `LIGHT_ALLOWED` (empty) nothing is Light.
- Order with #115: merge #115 first. Both edit `openapi.yaml` (the `claimCase` and `addNote` responses) and the status-set assertions of the claim and notes contract tests; #115 makes those sets equal, then this issue adds `"503"` to both sides. No code overlap (#115 touches `socboard/schemas.py`).
- No new dependency. The `Retry-After` value, the code name and the message are grooming decisions recorded here, not from the spec (`_docs/specs.md` says nothing on lock timeouts).
- Decision records approved after this issue was filed (2026-11-13T03:36Z): `_docs/decisions/2026-11-13T0537Z-close-floor-reflection.md` only, which does not touch this. The data-model record left the answer to #16 and #16 left it here, so no criterion is contradicted.
- Proposed tier: heavy. It adds a status and an error code to the contract that #21 depends on, and a handler to `socboard/errors.py` that changes how every route fails. Expected paths: `openapi.yaml`, `socboard/errors.py`, `socboard/cases.py`, `socboard/ingest.py`, the test files above, `_docs/decisions/<new record>.md`, `_docs/index.md`.

## Decision record

PM's draft, for the human to approve. The Engineer does not start until the human has approved it.

- **Decision:** A request that fails because SQLite timed out waiting for the write lock (BUSY or LOCKED, recognised by the driver's error code) answers 503 with code `service_busy`, the fixed message "The service is busy. Please try again." and `Retry-After: 1`. One app-wide handler in `socboard/errors.py` does it; the contract documents it once for every route and on the four write operations. Nothing is committed when it happens, so the request can be retried. The log gets one fixed-text line and the response never carries the statement or the driver message. Other database errors stay 500 `internal_error`.
- **Reason:** The client cannot retry what it cannot tell apart from a server fault. The claim, transition, note and ingest writes are each one transaction that is rolled back when the session closes, so nothing is stored on a timeout and a retry cannot duplicate. One handler covers all four write routes and any later one with no per-route code, and it also sees an error raised in a dependency, such as the user lookup, which a `try` block in a route body would not. The error code avoids depending on SQLite's message wording.
- **Alternatives:**
  1. Keep the 500 (the #16 state): no work, but retryable and fatal errors look alike and the log gets a traceback with the statement.
  2. A `try` block in each write route: explicit, but four copies, and a new write route that forgets it brings the gap back.
  3. A different status: 409 collides with `already_claimed`, 429 means a rate limit, 504 means a gateway.
  4. Raise the busy timeout or use `BEGIN IMMEDIATE`: fewer timeouts but not none, and the data-model record ruled it out.
  5. Retry inside the server: hides the contention and holds a worker for longer.
- **Trade-offs:** The frontend gets a new status and code to handle (#21). `Retry-After: 1` is a hint, not a promise that the lock is free. A read route can also answer 503 in the rare window when a writer commits. Only SQLite is recognised; Postgres has no lock timeout set today and its mapping is left to Deploy. The recognition relies on `sqlite_errorcode` (Python 3.11 and later; the project pins 3.12). A client that gives up on its own timeout before the 503 can still retry an ingest that did commit; that risk exists today and no idempotency key is added here.
- **Evidence:** #16 (QA risk 2 in its PASS comment; `_session-summaries/2026-11-13T0343Z-issue-016-orchestrator-claim-single-owner.md`); `_docs/decisions/2026-11-12T0834Z-data-model.md` (busy timeout, lock timeout left to #16); `socboard/cases.py` module docstring; `socboard/errors.py`; `tests/test_claim_api.py:183-209` (the held-lock technique).
