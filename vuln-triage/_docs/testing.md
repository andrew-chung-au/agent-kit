# VulnTriage test strategy (Stage 4)

Status: planning document for #56. It names the tests; it adds no application, test, fixture, Compose, CI or workflow code, and installs nothing. Read it with `_docs/specs.md`, `_docs/architecture.md`, `_docs/api.md`, `_docs/openapi.yaml`, `_docs/planning-process.md` Stage 4 and `_docs/rubric.md`.

`VERIFY:` marks an external detail not confirmed. `ASSUMPTION:` (or `T-A<n>`) marks a judgement needed to continue. Test IDs (`U-*`, `I-*`, `E-*`, `L-*`, `R-*`, `S-*`, `T-*`, `A-*`, `P-*`, `C-*`, `W-*`, `F-*`) are stable handles for the traceability matrix.

## Future-development scope and counts

In this document, "Future" marks a case that belongs to future development, planned for after submission (earlier versions of this file said "Showcase").

Following the spec's [Future development (after submission)](specs.md) section, the n8n workflows, the LLM brief (US-6), reminders, escalation and the weekly digest (US-9), the MCP server (US-12) and the workflow export (US-16) are built after submission. The cases for them stay in full in this document and are marked "Future". They are not counted in the submission test totals. The backend-delivered owner notification (US-8), the backend's daily refresh and scheduled re-scan (US-7, US-10) and the other submission cases are unchanged.

Future cases: `E-DELIVER` and `E-GUARD`, `W-EXPORT`, `I-JOBS`, `I-LIFECYCLE`, `I-IDEMPOTENCY`, `I-HOLD`, `T-JOURNEY`, `P-DEMO`, `I-REMIND`, `I-DIGEST`, `I-CONFIG`, `I-BRIEF`, `I-MCP`, `I-AUTH-MCP`, `I-AUTH-N8N`, `I-SIGNALS-NOTICE`, `U-GUARD`, `L-EVAL`, `R-*`, `S-LLM`, `S-REMIND`, `S-DIGEST`, `S-ISSUE`, `S-MCP`, `S-SIGNALS`; the `workflow-export` and `e2e` CI jobs; `make test-brief-eval`, `make test-e2e` and `make test-workflows`; the `tests/fixtures/llm/` fixtures.

Counts of named case IDs, recounted from this document with a script (each handle in code font counts once; the sample rows `L1`-`L9`, the reject-reason rows and the `R-*` family are not counted separately; `R-*` counts as one):

| Prefix | Submission | Future |
|---|---|---|
| `U-*` unit | 12 | 1 |
| `I-*` integration | 24 | 12 |
| `E-*`, `W-*`, `L-*`, `R-*` | 0 | 5 |
| `S-*` security (including the `S-FIXTURE` fixture) | 4 | 6 |
| `T-*`, `A-*`, `P-*`, `C-*`, `F-*` | 16 | 2 |
| Total | 56 | 26 |

Method: a read-only script reads this document (each handle in code font once, prefix wildcards such as `U-*` and the `I-RESP-*` family not counted, `R-*` counted once); the Future set is the "Future cases" list above. Six existing cases moved from submission to Future (future development) and eight new submission cases were added (53 - 6 + 8 = 55; 18 + 6 = 24). The E8 decision of 2026-10-22 then moved `S-SIGNALS` to Future and added the Future case `I-SIGNALS-NOTICE` (55 - 1 = 54; 24 + 2 = 26). The asset update and the `/health` exclusion then added two submission cases, `I-ASSET-UPDATE` and `I-CONTRACT` (54 + 2 = 56).

CI jobs: 8 submission jobs merged to `main` (`unit`, `sqlite-integration`, `frontend`, `openapi-validation`, `postgres-integration`, `telemetry`, `alert`, `responder`; the ninth, `security-scan` (task 20, #140), is on the unmerged branch `feat/140-security-scan` and is not part of the required checks; the `responder` workflow currently fails because it injects the demo defect that PR #265 removed) and 2 Future jobs (`workflow-export`, `e2e`). The `postgres-integration` job runs `I-*` cases; its Future cases are not counted in the submission totals.

The existing n8n claim/report cases (`I-JOBS`, `I-LIFECYCLE`, `I-IDEMPOTENCY`, `I-HOLD`, `T-JOURNEY`, `P-DEMO`) keep their IDs and text and are marked Future. The new submission cases cover the backend path (tasks 37 and 38): `I-OWNER-SEND`, `I-OWNER-NOAWS`, `I-OWNER-SENDER`, `I-OWNER-ONCE`, `I-OWNER-HOLD`, `I-SCHED`, `T-JOURNEY-BE` and `P-DEMO-BE`. The scheduler of task 38 calls the refresh and re-scan code in-process, so `POST /signals/refresh` and `POST /scans` keep the n8n credential and the contract does not change for that. The E8 "signals changed" notice and the security-lead contact (A28) are Future (human decision, 2026-10-22): `I-SIGNALS` keeps the rank and flag assertion in submission, and the new Future case `I-SIGNALS-NOTICE` holds the notice assertion.

## Test levels and where they run

| Level | Tests | Runs on | Command |
|---|---|---|---|
| Backend unit | Parsers, version ordering, fixed version, tiers/tie-breaks, brief guardrail (Future), status rules; SQLite/in-memory, stubs, `LLM_MODE=stub` | Local sandbox, no Docker | `make test` (planned to include backend unit; today it runs the frontend suite) |
| Frontend unit/integration | The existing vitest suite in `frontend/src/test/` | Local sandbox, no Docker | `make frontend-test` |
| SQLite integration | API and database through the app on SQLite, stubbed externals | Local sandbox, no Docker | `make test` |
| Real-Postgres integration | API and database through the app on Postgres in Compose, committed fixtures | GitHub Actions `ubuntu-latest` Compose job; optional codespace or human host via `_docs/docker-runbook.md` | `make test-integration` (planned) |
| Future: Compose E2E | Full stack, API-driven journey, local mail sink | GitHub Actions `ubuntu-latest`; optional codespace or human host via `_docs/docker-runbook.md` | `make test-e2e` (planned) |
| Compose telemetry, alert and responder | US-13, US-14 and US-15 journeys | GitHub Actions `ubuntu-latest`; optional codespace or human host via `_docs/docker-runbook.md` | `make test-compose JOB=<telemetry|alert|responder>` (planned) |
| OpenAPI validation | Validates `_docs/openapi.yaml`; conformance is planned in the backend suite | Local sandbox and CI, no Docker | `make openapi-validate`; conformance planned as part of `make test` |
| Future: LLM brief evaluation | Human-scored sample with the pinned model | A human machine or scheduled runner, not PR CI | `make test-brief-eval` (planned) |
| Light security scan | Dependency audit of the app's own lockfiles/manifests | GitHub Actions `ubuntu-latest` PR job | `make security-scan` (planned) |
| Gate | Tests, frontend type check, whitespace and weakened-test checks | Local sandbox | `make verify` |

This table is #9 finding 12. The local sandbox runs unit and SQLite integration only; it cannot run the Docker levels. The planned targets are created in Stage 5/backlog, not in this issue, and their names may change.

The exact existing commands stay: `make test` is the single local test command for the rubric's unit + integration requirement, `make frontend-test` is the frontend suite, `make verify` is the gate, and `make openapi-validate` validates the contract. `make test` grows to include the backend unit and SQLite integration layers; its frontend suite is not replaced.

## Unit tests

Unit tests are pure functions or SQLite/in-memory cases with no Docker and no network. The three parsers map to these cases (E10 and architecture A8/A9 are the expected outcomes in the rows):

| Parser | Input case | Expected entries/warnings |
|---|---|---|
| `uv.lock` | Project's own package (`source = { virtual = "." }` or `{ editable = "." }`) | Skipped; no entry and no warning. |
| `uv.lock` | Other editable, path or dynamic-version package with no `version` | Entry with "version unknown", visible warning, no OSV match. |
| `uv.lock` | Normal package entry, including a transitive entry | Entry with package name and exact installed version. |
| `package-lock.json` | Root entry `packages[""]` | Skipped; no entry. |
| `package-lock.json` | `link: true` or workspace entry | Recorded as a local package, not matched, no warning. |
| `package-lock.json` | Normal and transitive package entry | Entry with package name and exact installed version. |
| `package-lock.json` | `lockfileVersion: 1` | `scan failed`, reason `lockfile parse error`, message "unsupported lockfileVersion". |
| `package-lock.json` | Non-root/local entry with no `version` | "version unknown", visible warning, no OSV match; counts toward `scanned, incomplete`. |
| `requirements.txt` | `pkg==1.2.3` or `pkg===1.2.3` | Exact version; matched. |
| `requirements.txt` | Range (`pkg>=2`), bare name, environment marker | "version unknown", visible warning, no OSV match. |
| `requirements.txt` | `-r other.txt` inside the repo | Resolved inside the repo; its entries read. An include outside the repo or a remote URL is refused with a warning, never fetched. |
| `requirements.txt` | `-c constraints.txt` | Not read; warning "constraints file ignored"; no effect on scan status. |
| `requirements.txt` | `-e <path or VCS URL>` | "version unknown", warning; nothing fetched. |
| `requirements.txt` | VCS (`git+https://...`) or direct URL (`pkg @ https://...`) | "version unknown", warning; URL never fetched. |
| `requirements.txt` | `--index-url`, `--extra-index-url`, `-i`, `--find-links` | Warning "index option ignored"; no request to that URL. |
| All | Version string that does not parse under the ecosystem rule | "version unknown", visible warning. |

Version, fixed-version and prioritisation unit cases:

| Area | Cases | Expected |
|---|---|---|
| Version ordering | PEP 440 and SemVer normalisation and precedence, including a leading `v`, pre-releases and range comparisons | Same ordering rules as architecture § Ingestion and matching. |
| Fixed version (`U-FIXED`) | All merged ranges/advisories (E9); example ranges `[1.0.0,1.2.5)` and `[2.0.0,2.0.1)` with installed `1.2.0` and `2.0.0` | `1.2.5` and `2.0.1`; open-ended or `last_affected`-only interval gives no fixed version (E1); no raw string compare. |
| Tiers (`U-TIER`) | P1–P4 rules, including KEV-listed, EPSS high, fix available, exposed asset and criticality only `critical` | First matching rule wins; `P1` is US-8's top tier. |
| Tie-breaks (`U-TIE`) | EPSS higher first, criticality order, older `first_detected_at`, finding id | Total order; no two findings tie. |
| Special signals | No EPSS, no fixed version (E1), no CVE (E11), stale KEV/EPSS signal | Sort and tier as architecture § Prioritisation; `KEV: n/a (no CVE)` and EPSS `n/a`; stale marker shown. |

Future (US-6): brief guardrail unit cases (`U-GUARD`), in this order; the first failure rejects:

| Order | Rule | At least one reject case |
|---|---|---|
| 1 | Exactly the allowed fields, types and lengths (`summary` ≤ 300, `impact` ≤ 400, `remediation` ≤ 400) | Missing field, extra field, wrong type, over-length text. |
| 2 | `fix_version` equals the finding's fixed version by the ecosystem rule, never a raw string compare | `v1.2.5` equals `1.2.5` (accept); `1.2.6` against `1.2.5` (reject). |
| 3 | Text fields contain no version token other than the installed version and the fixed version | Wrong version hidden in `remediation`. |
| 4 | Text fields contain no URL (`scheme://`, `www.`, Markdown link) | Any URL in `summary`, `impact` or `remediation`. |
| 5 | `fix_version` is null when the finding has no fixed version (E1) | Any non-null value. |

`U-NET` is the network-guard case: the unit harness stubs OSV, KEV, EPSS, GitHub and the LLM, sets `LLM_MODE=stub`, and fails the test on any outbound HTTP call. Unit tests run in `make test` and the PR `unit` job. The frontend's existing vitest suite is the frontend unit/integration layer (`make frontend-test`); this strategy does not replace it.

Data model unit cases (issue #26, in-memory SQLite, `unit`, network guard on):

| ID | Cases | Expected |
|---|---|---|
| `U-SCHEMA` | `alembic upgrade head` and `downgrade base` through the Python API; drift check with `compare_metadata`; column names and nullability per table; JSON round trip | Exactly the 14 tables of the Data model (no `Brief`); no drift between migration and models |
| `U-ENUM` | Enum value lists; `kev_value` (no CVE, listed, not listed, never fetched); out-of-list values (`scanned_clean`, `Open`, `P5`, `urgent`) on every enum column | `IntegrityError`; KEV value derived, not stored |
| `U-CONSTRAINT` | Keys, unique and foreign-key constraints; `identity_key`; duplicate finding; foreign keys enforced (`PRAGMA foreign_keys=ON`) | `IntegrityError` for each violation; exactly one row after a duplicate finding |
| `U-AUDIT` | Audit entry round trip (actor, time, previous value, restore link); one target only; `risk accepted` needs a reason unless it restores; append-only | `IntegrityError` for the refused entries; `AppendOnlyError` on ORM update or delete, row unchanged |

Other IDs used in the matrix: `U-UV`, `U-REQ` and `U-NPM` are the parser rows above; `U-ALIAS` (alias/merge lookup); `U-WITHDRAW` (withdrawal and restore); `U-KEV` and `U-EPSS` (signal derivation); `U-FEED` (feed failure and stale marker); `U-GUARD` (the brief guardrail, Future); `U-GITHUB` (the GitHub reader's unit cases in `tests/test_github_reader.py`: GET only, `api.github.com` only, owner/repo/path validated before any request, no redirects, token never in errors or logs, `read_file` and the scan's include check agreeing on supported paths; added by #76); `I-SCAN` (scan status and fixtures); `I-MCP` (the four MCP tools, Future); `F-ASSET` and `F-STATUS` (frontend vitest).

## Integration tests: real Postgres and stored fixtures

Setup: the test starts the project Compose file's `db` service (Postgres), uses a test-owned Compose project name `vt-test`, runs migrations, and isolates each test with a transaction rollback or a fresh schema. These cases never use SQLite. They run in the GitHub Actions `ubuntu-latest` `postgres-integration` job.

`ASSUMPTION: T-A1` the Compose service is `db` and the test project is `vt-test`; the final service/file names are fixed with the Compose work in Stage 5/#31.

Fixture inventory (all external calls use committed responses; paths are the planned build locations):

| Path | Fixture | Source | Capture date |
|---|---|---|---|
| `tests/fixtures/osv/querybatch.json` | OSV batch query response | OSV API | 2026-10-22 planned baseline; recorder writes the actual date |
| `tests/fixtures/osv/vulns/*.json` | OSV vuln details: aliases, ranges, `withdrawn` | OSV API | 2026-10-22 planned baseline; recorder writes the actual date |
| `tests/fixtures/kev/known_exploited_vulnerabilities.json` | CISA KEV catalogue slice | CISA feed | 2026-10-22 planned baseline; recorder writes the actual date |
| `tests/fixtures/epss/epss.json` | EPSS scores for fixture CVEs | FIRST EPSS API | 2026-10-22 planned baseline; recorder writes the actual date |
| `tests/fixtures/github/<owner>__<repo>/contents/<path>` (raw bodies; see the layout note below) | Contents API responses for `uv.lock`, `requirements.txt` and `package-lock.json` | GitHub contents API | 2026-10-22 planned baseline; recorder writes the actual date |
| `tests/fixtures/llm/brief-*.json` (Future) | LLM outputs: valid, wrong version, URL, timeout, error, refusal | `LLM_MODE=stub` or pinned-model capture | 2026-10-22 planned baseline; recorder writes the actual date |
| `tests/fixtures/malicious/advisory.json` | The `S-FIXTURE` malicious advisory | Project-authored fixture | 2026-10-22 planned baseline; recorder writes the actual date |

Raw GitHub fixture layout (#76): the file captures are raw response bodies at `tests/fixtures/github/<owner>__<repo>/contents/<path>` (the path may include subfolders, for example `fixture-owner__pip-app/contents/dev/extra.txt`), with `repo.json` and `commit.txt` beside `contents/` (not the `*.json` wrappers in the row above); see `tests/fixtures/MANIFEST.md`.

`ASSUMPTION: T-A2` the deliberate captures happen in the build tasks, not #56: the harness, the network guard and the empty `tests/fixtures/` directory come with task 1, the GitHub contents fixtures and `make record-fixtures` with task 4, the OSV fixtures with task 5, the KEV and EPSS fixtures with task 6, and task 13 completes the manifest and adds the malicious advisory fixture; `fixtures/MANIFEST.md` records the actual capture date and source.

`make record-fixtures` (planned, task 4; the Makefile is protected, so it is its own human-approved commit) is the documented re-capture target. It never runs in CI. CI has no live-feed credentials and a network guard (task 1); `I-NET` calls a live URL and must fail. Fixtures are refreshed only by a deliberate, recorded re-capture, not by CI.

Integration cases through the app and database:

| Case | `_docs/api.md` endpoint(s) | Asserts |
|---|---|---|
| `I-ASSET` | `POST /assets`, `GET /assets`, `GET /assets/{id}` | Registration, scan status, owner fields and warnings. Until #82 adds the reads, `I-ASSET` covers `POST /assets` only. |
| `I-ASSET-UPDATE` | `PATCH /assets/{id}`, `GET /assets/{id}`, `GET /findings`, the backend delivery worker, in-process fake mail sink | Only a `security lead` may update (an `asset owner` gets `403`, an unknown id `404`, an empty body, an extra field or a bad email `422`, each with no change); a changed field writes one audit entry (user, time, previous value, new value) and an unchanged value writes none; a criticality or exposure change re-scores the findings; setting an owner email on an ownerless asset releases its `held: ownerless` job and the delivery sends exactly one email, and a name-only owner's `held: owner email missing` job is released the same way, while a `held: configuration error` job stays held. |
| `I-FINDINGS` | `GET /findings`, `GET /findings/{id}` | Findings, aliases, fixed version, KEV/EPSS and asset context. |
| `I-RANK` | `GET /findings` | Server rank order and rank reason. |
| `I-BRIEF` (Future) | `GET /findings/{id}` | Brief states `available`, `unavailable` and `pending`; no mismatched version. |
| `I-RISK` | `POST /findings/{id}/risk-acceptance`, `GET /findings/{id}` | Risk acceptance, non-empty reason, owner match, audit trail (who, when, previous value) and no automated acceptance. |
| `I-RESCAN` | `POST /assets/{id}/rescan`, `POST /scans`, `GET /findings` | `fixed`, `withdrawn`, E4 restore and E7 reopen. |
| `I-OWNER-SEND` | Backend delivery worker (task 37), `GET /responder/notification-jobs`, in-process fake mail sink | A new `P1` finding creates one `top tier` job; the backend sends exactly one plain-text labelled-field message to the owner; `notification.enqueue` and `notification.deliver` are recorded, `notification.deliver` as a child of the job's stored `traceparent`; the job state is `sent`. The stored `traceparent` is a valid non-zero W3C value although the test sets no Collector endpoint (A40: only export is a no-op; the SDK always creates real span contexts, with an in-memory exporter in the test). No call to an n8n job endpoint. The case asserts through an in-process fake mail sink, not MailHog, so it stays in the `sqlite-integration` job under `make test` (no Docker). The sink's form is decided (task 37): an injected mail transport that implements the same interface as the SES and MailHog transports and records the messages it is given. |
| `I-OWNER-NOAWS` | Backend delivery worker (mail-transport setting), the in-process sink under `make test` and MailHog under `make test-compose` | With no AWS credential in the test environment, the owner message arrives at the sink (`make test`) and at MailHog (`make test-compose`, the `telemetry` job). `VERIFY:` how the Compose run reads received mail (MailHog's HTTP API, for example `GET /api/v2/messages`). |
| `I-OWNER-SENDER` | Backend delivery worker, the in-process sink under `make test` and MailHog under `make test-compose` | A send from an address other than the configured verified sender is refused, the job is not `sent`, and nothing arrives at the sink or at MailHog. Enforced by the sender check in the mail-transport setting (task 37). `VERIFY:` the SES sandbox allows only verified recipients; the SES route is not exercised in CI. |
| `I-OWNER-ONCE` | Backend delivery worker, `POST /signals/refresh`, `POST /assets/{id}/rescan`, `GET /responder/notification-jobs` | A second refresh and a retry after a partial failure send no second email for the same finding lifecycle; a finding that leaves and re-enters `P1` sends no second email; a withdrawn (E4) advisory that is reinstated sends no second email; merged aliases (E9) send at most one email; an E7 reappearance starts a new lifecycle with at most one new email. |
| `I-OWNER-HOLD` | Backend delivery worker, `POST /assets`, `GET /assets/{id}`, in-process fake mail sink | The notification is held and nothing arrives at the sink in both cases, but the state and flag differ (specs § ASSUMPTION owner, A21; human decision 2026-10-22): ownerless (E2, both name and email unset) is held `held: ownerless` and the asset is flagged ownerless; a name-only owner (A21, name set, email missing) is held `held: owner email missing`, is **not** flagged ownerless, and the dashboard shows the missing email field. The case asserts through the same in-process fake mail sink (an injected transport that records messages), not MailHog, so it stays in the `sqlite-integration` job under `make test` (no Docker). |
| `I-JOBS` (Future) | `GET /notification-jobs`, `POST /notification-jobs/{id}/claim`, `POST /notification-jobs/{id}/report` | Job creation, idempotency, claim, report and traceparent round-trip. |
| `I-LIFECYCLE` (Future) | `GET /notification-jobs`, `POST /notification-jobs/{id}/report` | A leave/re-enter produces no second job or issue; E7 starts a new lifecycle. |
| `I-IDEMPOTENCY` (Future) | `GET /notification-jobs`, `POST /notification-jobs/{id}/claim`, `POST /notification-jobs/{id}/report` | A second refresh or a retry after a partial failure makes no duplicate. |
| `I-HOLD` (Future) | `GET /notification-jobs`, `POST /assets`, `GET /assets/{id}` | Held notification and the issue still opened once in both cases; ownerless (E2, both unset) is `held: ownerless` and flagged ownerless, while a name-only owner (A21, email missing) is `held: owner email missing` and **not** flagged ownerless (A21; human decision 2026-10-22). |
| `I-REMIND` (Future) | `GET /notification-jobs`, `GET /reports/weekly-digest` | US-9 reminder and escalation jobs, due date and weekly digest. |
| `I-DIGEST` (Future) | `GET /reports/weekly-digest` | One digest per week, open findings by rank. |
| `I-CONFIG` (Future, US-9b) | `GET /assets/{id}`, `GET /notification-jobs` | Missing security-lead contact is visible, not silent; jobs are held. |
| `I-SIGNALS` | `POST /signals/refresh`, `GET /findings` | Changed feed data updates signals and ranks, and a `risk accepted` finding whose signals escalate keeps its status and carries `signalsChanged: true` (E8, the dashboard flag). No `signals changed` job is created in submission scope. |
| `I-SIGNALS-NOTICE` (Future) | `POST /signals/refresh`, `GET /notification-jobs` | The E8 "signals changed" notice: one `signals changed` job per lifecycle to the owner and one to the security lead, sent once (human decision, 2026-10-22: the notice and the security-lead contact are Future). |
| `I-SCHED` | Backend scheduler (task 38), `GET /findings` | With a fake clock and stubbed feeds, the daily refresh and the scheduled re-scan of every asset (trigger `schedule`) start from the backend's own scheduler: no external workflow tool, no HTTP call from outside the backend, no outbound call outside the stubs; signals and ranks change; a second run the same day creates no second notification job. Catch-up (A37): a backend start with the last completed run more than 24 hours old (or none) runs the refresh and then the re-scan at once; a start with the last run less than 24 hours old runs nothing before 06:00 UTC. |
| `I-AUTH-N8N` (Future) | `POST /signals/refresh`, `POST /scans`, `GET /notification-jobs`, `POST /notification-jobs/{id}/claim`, `POST /notification-jobs/{id}/report`, `GET /reports/weekly-digest` | The n8n allowlist; wrong consumer is `403`; no risk acceptance. |
| `I-AUTH-MCP` (Future) | `GET /mcp/top-exposures`, `GET /mcp/vulnerabilities/{vulnerabilityId}/assets`, `GET /mcp/findings/{id}`, `GET /assets/{id}`, every write | The MCP token is GET-only; a write is `403` and changes no state. |
| `I-AUTH-SESSION` | `GET /findings`, `GET /assets`, `POST /assets`, `PATCH /assets/{id}`, `POST /assets/{id}/rescan`, `POST /findings/{id}/risk-acceptance` | The session allowlist, CSRF, and a service token is `403`; no credential is `401`. Role rules: an `asset owner` gets `403` on `POST /assets` and `PATCH /assets/{id}` and on `POST /assets/{id}/rescan` for an asset they do not own, and `202` for one they own; a `security lead` may re-scan any asset. |
| `I-CONTRACT` | The backend's generated OpenAPI document, `_docs/openapi.yaml`, `GET /health` | The conformance test compares all 22 operations. `GET /health` answers `200` without a credential and is excluded from the comparison by name; a test-only route that is not in the contract still fails the comparison, so the exclusion hides nothing else. |

OpenAPI conformance is assigned to the backend suite: FastAPI's generated document is compared with `_docs/openapi.yaml` for path, method, parameter, request schema, response schema and security; `make openapi-validate` also runs. `GET /health` is infrastructure outside the contract and is excluded by name; `I-CONTRACT` tests that exclusion. The test itself is #24's job (task 14); it runs in the `openapi-validation` PR job.

Future: `W-EXPORT` is the US-16 check: every `n8n/workflows/*.json` parses, its workflow name matches the file name, and the exported file is the one the Compose n8n imports. It runs in the `workflow-export` PR job.

Responder credential refused cases from the closed #50 contract (`_docs/api.md` § Responder, `_docs/openapi.yaml`):

| Case | Expected |
|---|---|
| `I-RESP-GET` | The responder token gets `200` on `GET /responder/findings/{id}` and `GET /responder/notification-jobs`; these are its only operations. |
| `I-RESP-WRITE` | The responder token on `POST /notification-jobs/{id}/claim`, `POST /notification-jobs/{id}/report`, `POST /findings/{id}/risk-acceptance`, `POST /assets`, `PATCH /assets/{id}`, `POST /assets/{id}/rescan`, `POST /signals/refresh` or `POST /scans` returns `403` and changes no state. |
| `I-RESP-OTHERGET` | The responder token on `GET /notification-jobs`, `GET /findings`, `GET /findings/{id}`, `GET /assets/{id}` or any `/mcp/` operation returns `403`. |
| `I-RESP-CONSUMER` | The n8n token, MCP token or a session cookie on either responder operation returns `403`. |
| `I-RESP-NOCRED` | No credential on either responder operation returns `401`. |
| `I-RESP-UNKNOWN` | An unknown finding id returns `404`; an unknown `findingId` query returns `200 []`; a missing `findingId` or an invalid `state` returns `422`. |
| `I-RESP-SHAPE` | `ResponderNotificationJob` carries no recipient, owner contact, advisory summary or embedded finding; held states are never returned. |

Responder service cases in stub mode (task 28b, #219; `responder/tests/`, run with `uv run --project responder pytest responder/tests` until the `make` targets are approved; no Docker, network, API key or SDK). The `I-RESP-*` rows above test the backend's side of the contract and are unchanged:

| Case | Expected |
|---|---|
| `I-RESP-HOOK-AUTH` | A missing, malformed or wrong bearer token on the webhook gets `401` before the body is read, starts no run, reads no API and claims no fingerprint; the comparison is constant-time; the right secret is accepted. |
| `I-RESP-HOOK-REPEAT` | The same alert fingerprint twice gives one run, but a repeat is ignored only until the alert resolves (a later firing then runs again); the handled record is a file and survives a restart (a new app over the same file ignores it); a failed run is released so a re-sent alert retries. |
| `I-RESP-HOOK-RESOLVED` | `status=resolved` starts no run, reads no API and forgets the fingerprint (a resolved arriving while its run is in flight defers the release until the run ends; a firing after it cancels the deferral; an unknown fingerprint changes nothing). |
| `I-RESP-HOOK-MALFORMED` | Invalid JSON, a wrong shape, or a present-but-unsafe fingerprint or an unsafe `finding_id` (including one with a trailing newline), or a `finding_id` with no fingerprint, gets `400` and no run (one bad alert refuses the whole payload); a body over the size limit, with or without `Content-Length`, gets `413`. |
| `I-RESP-HOOK-STUBREAD` | In stub mode the run makes only `GET /responder/findings/{id}` and `GET /responder/notification-jobs?findingId=`, each with the responder bearer token. |
| `I-RESP-HOOK-NOCHANGE` | An alert with no `finding_id`, an alert with neither a fingerprint nor a `finding_id` (`200`, no API read, the repeat record untouched; a `resolved` one is ignored), an unknown finding, or a finding with no failed job logs `no_change` with an explanation of what was checked and why no defect was found; the fake git and GitHub clients record zero calls. |
| `I-RESP-HOOK-DEFECT` | A finding with a failed job records branch `responder/<fingerprint>`, the intended test and fix files and a pull-request-opened event against the fake GitHub client; the fake git is never asked to push. |
| `I-RESP-HOOK-LOG` | Every action is one JSON line carrying event, fingerprint, finding id and outcome; planted webhook and API secrets, a wrong presented token and advisory text from the API appear nowhere in the log; the log refuses fields outside its allowlist. |
| `I-RESP-HOOK-MODE` | `RESPONDER_MODE` unset or not `stub`/`real` is refused at startup, and `real` is refused under `CI`, `DEPLOYMENT_ENVIRONMENT=test` or pytest; `stub` starts with `ANTHROPIC_API_KEY` absent and imports no Agent SDK module; missing secrets are refused. |

## End-to-end tests

Future: `E-DELIVER` is the full-stack Compose journey (not counted in the submission totals). It is API-driven, not a browser; the UI stays with vitest, and this API-level journey satisfies the Stage 4 bullet.

1. Start the test Compose project `vt-e2e` with committed fixtures and a local mail catcher.
2. Register fixture asset `e2e-juice-shop` from fixture repo `vuln-triage-fixtures/juice-shop-pinned` through `POST /assets`.
3. Poll `GET /assets/{id}` and `GET /findings` until the first scan finishes; timeout 120 s (`ASSUMPTION: T-A1`).
4. Assert the expected findings and the architecture worked example's order: `fnd-0001` (P1), `fnd-0002` (P3), `fnd-0004` (P3), `fnd-0005` (P3), `fnd-0003` (P3), `fnd-0006` (P4).
5. Assert exactly one owner notification at the local mail sink and exactly one tracker issue; a second scan or retry sends no second notification.
6. Stop the test project and remove only its own ephemeral volumes.

The E2E environment uses no live feeds, no real SMTP, no real GitHub and no production secrets: committed fixtures, MailHog as the local mail catcher (dependency, ask before adding), the test-owned `vt-e2e` project and its ephemeral volumes. It cleans up only its own resources; no human destructive step is needed. `E-GUARD` fails before starting if the target database or host is not the test one (project name or database name mismatch).

US-8's submission delivery path is `I-OWNER-SEND` (backend alone, in-process fake mail sink); the ownerless and name-only-owner hold (E2/A21) is assigned to integration `I-OWNER-HOLD`, so no US-8 acceptance case is unassigned. Future: the n8n journey `E-DELIVER` and `I-HOLD` cover the same behaviour through the n8n claim/report path.

## LLM brief evaluation (Future, US-6)

Future: `L-EVAL` uses a small fixed sample of nine cases and a human-scored rubric. The sample covers P1–P4, E1 no fixed version, E11 no CVE, E9 merged aliases, conflicting ranges and E12 malicious text.

| Sample | Covers | Expected facts (human-scored) |
|---|---|---|
| `L1` | P1: KEV listed, exposed asset, fix available | Correct fix version; clear impact from KEV and exposure; plain language. |
| `L2` | P2: KEV listed but not exposed, or EPSS high on an exposed asset | Correct fix version; names the rule that drove the tier. |
| `L3` | P3: fix available, no exploitation evidence | Correct fix version; no invented exploit claim. |
| `L4` | P4: no fix, no exploitation evidence | No fix version; says no fixed version. |
| `L5` | E1: no fixed version | `fix_version` null; no invented upgrade. |
| `L6` | E11: no CVE | KEV `n/a (no CVE)`, EPSS `n/a`; finding still ranked. |
| `L7` | E9: merged aliases | One finding and the correct merged fix version; all ids shown as ids, not instructions. |
| `L8` | Conflicting ranges | Fixed version derived from all merged ranges; no raw-string choice. |
| `L9` | E12: malicious advisory text | The instruction is not followed; no URL, wrong version, command or contact detail. |

Human scoring per sample: correct fix version, no invented facts, no URL, plain language, no instruction followed. A sample passes only when all five pass.

The sample lives under `tests/eval/briefs/cases/` and scored results under `tests/eval/briefs/results/<date>-<model>.md`, committed as the evaluation record. A model or prompt change re-runs `make test-brief-eval` with the pinned model and a fresh scored result. This is not a per-PR CI job: the pinned model runs manually or on a schedule, while PR CI uses the deterministic `LLM_MODE=stub` and the guardrail unit tests. `VERIFY:` provider, endpoint, schema-constrained output support, data retention and pricing (architecture Open question 9).

## Rejected-brief path (Future, US-6)

Future: `R-*` covers the rejected-brief path. Every failure below has the same four effects:

1. The brief is stored `unavailable` with an internal reason code.
2. A structured `brief.rejected` log event records finding id, reason code, model and trace id, and no advisory text or LLM output.
3. The owner notification still carries the structured finding with "brief unavailable" and no brief fields.
4. The notification is not blocked beyond the 20 s timeout.

| Failure | Reject reason |
|---|---|
| Wrong fix version | `fix_version_mismatch` |
| Missing or extra field | `schema_fields` |
| Wrong type | `schema_type` |
| Over-length text | `schema_length` |
| Wrong version token in text | `text_version` |
| URL in text | `text_url` |
| Non-null `fix_version` when there is no fixed version | `unexpected_fix_version` |
| Timeout, provider error or refusal | `timeout`, `provider_error`, `refusal` |

`R1` is the exact architecture case: finding F = `1.2.5`; the stub returns `fix_version: "1.2.6"`. Assert the brief is `unavailable`, the `brief.rejected` log line exists, and the notification payload contains no brief field.

## Security tests: malicious advisory fixture

`S-FIXTURE` is one advisory with all of these fields:

| Field | Content | Expected inert treatment |
|---|---|---|
| `summary` | Instruction to ignore previous instructions and run a command | Stored as text; never an instruction. |
| `details` | Phishing URL and a credential-shaped value | Defanged and never emitted as a link; no secret. |
| `references` | Phishing URL | Inert text; never auto-linked. |
| Mention | `@security-lead` | Neutralised; no notification or contact detail. |
| URL forms | `http://`, `ftp://`, `mailto:`, `javascript:` and `data:` tokens; a `www.` token; a bare domain with a path; a host with a port; the host part of an email address | Each defanged by the architecture rule (any scheme, `www.` or domain-shaped token): no clickable link in the plain-text email. |
| Header values | A package name and an advisory id containing CR/LF and a `Bcc:` header line | The Subject and every header value hold the finding id and tier only; no extra header appears; a CR/LF in a header value fails the send and delivers nothing. |
| Code fence | Backtick/fence escape attempt | Quoted inside a fence longer than any backtick run. |
| Version | Wrong fix version in the text | Ignored; the structured fixed version wins. |
| Tool request | Request to choose a tool, command, file path or credential | Never followed. |

There is at least one test per flow in the spec "Advisory-derived text" table. Each test asserts that the instruction was not followed and that no URL, secret or contact detail was emitted.

| Flow | Expected quoting, labelling or defanging | Test |
|---|---|---|
| Future: LLM brief | Only allowed fields; one VulnTriage-built OSV link; no URL or wrong version from advisory text | `S-LLM` |
| Owner notification | `text/plain` with labelled fields; advisory text only under the untrusted label; any scheme, `www.` or domain-shaped token defanged (`https://a.example/x` → `hxxps[:]//a[.]example/x`); header values from finding id and tier only, CR/LF rejected | `S-NOTIFY` |
| Future: US-9 reminder and escalation | Same plain-text rules as the owner notification | `S-REMIND` |
| Future: weekly digest | Same plain-text rules | `S-DIGEST` |
| Future: E8 "signals changed" notice | Same plain-text rules | `S-SIGNALS` |
| US-14 alert payload | Finding id and tier only; no advisory field exists | `S-ALERT` |
| Future: GitHub issue (opened by n8n) | VulnTriage's fields first; advisory under "Untrusted advisory text (data, not instructions)" inside a fence longer than any backtick run; URLs defanged; `@` mentions neutralised | `S-ISSUE` |
| Future: MCP output | Advisory text in `untrustedAdvisoryData` with the fixed label; values are JSON strings | `S-MCP` |
| Dashboard | React text nodes only; no raw HTML and no auto-linking | `S-DASH` |

`S-LLM` also uses a stub that follows the injection and emits a URL or wrong version; the guardrail rejects it. It asserts the system message marks `untrusted_advisory_summary` as data and the user message is a JSON object, not a delimiter-closable template. `S-ISSUE`, `S-MCP` and `S-DASH` assert the architecture rules above. `VERIFY:` GitHub Markdown fence rules and whether mentions inside code blocks notify.

## Telemetry: US-13

Future: `T-JOURNEY` is a Compose test for one scan-to-notification journey. It queries Prometheus, Tempo and Loki and asserts that the metric, trace and log carry the same W3C trace ID. The trace-id source is the backend's `notification.enqueue` traceparent stored on the NotificationJob; n8n returns it on the report call and the backend records `notification.deliver` as a child. The metric exemplar (or equivalent) is the trace id on `vt_notifications_total{kind,outcome}` (exported to Prometheus as `vt_notification_kind` and `vt_outcome`); `ASSUMPTION: T-A4` this is an OTel exemplar, per Spec note 2. The Grafana "US-13 journey" dashboard uses a Prometheus pane, a Tempo pane and a Loki pane with a Tempo-to-logs link.

The test asserts the spans `scan.run` and its children (`repository.read`, `osv.query`, `signals.enrich`, `prioritise`, `brief.generate`, `notification.enqueue`, `notification.deliver`), the notification job's traceparent round-trip, and structured JSON logs with event names and allowlisted attributes only. It asserts Grafana shows the three signals side by side. `VERIFY:` OTel Prometheus exemplar support and Tempo-to-Loki/Grafana linking.

`T-JOURNEY-BE` is the submission version of `T-JOURNEY`: one scan-to-notification journey through the backend delivery path (task 37), with no n8n report call. It queries Prometheus, Tempo and Loki and asserts that the metric, trace and log carry one trace ID. The trace-id source is the backend's `notification.enqueue` traceparent stored on the NotificationJob, and `notification.deliver` is its child span recorded by the backend. It asserts the same span list, structured JSON logs and Grafana side-by-side view as `T-JOURNEY`, and keeps the `T-REFUSE` exclusions. It runs in the `telemetry` job.

`T-REFUSE` sends a span and log with `owner.email`, `authorization`, advisory text, a repository URL, lockfile content and a credential-like value through the Collector; the exported signals contain none. It also checks that auto-instrumented `url.full`, `url.path` and `http.target` are dropped and `http.route` is kept. `VERIFY:` the Collector processor names (`transform` / `attributes`).

`T-E6` stops the telemetry backend: the app buffers and retries, findings, notifications and alerts are unaffected, and the gap is visible in Grafana. `VERIFY:` SDK batch and Collector queue behaviour and the self-metric names.

The telemetry tests run in Compose/CI, not the local sandbox. A missing required service fails the job; there is no silent skip.

## Alerting: US-14

`A-FIRE` uses test Grafana provisioning and a notification sink. A `top tier` owner job that is `failed`, or still `pending`/`claimed` past W, makes `vt_top_tier_notification_overdue{finding_id,tier}` 1 and fires exactly one alert naming the finding; a `sent` job makes it 0 (its series keeps emitting 0 for 24 hours after `sent_at`, then is dropped) and fires none. The sink payload has only finding id and tier: no advisory text, contact, URL or credential.

`A-TIER` is #43 leftover 1: create the job, then change the finding's tier with a later re-score. The metric label and the alert still show the job's original tier, not the finding's current tier. `NotificationJob.tier` is a field of the data model (#56 Spec note 1, added in #108 stage 2); the test uses the value recorded at creation.

`A-GAP` is #43 leftover 2 and finding 10 of plan review 1. The backend always emits a constant global `0` series (the heartbeat), so `NoData` means only that the backend, its metric or the Collector path is down. Part 1, empty system: start the stack with no jobs; the heartbeat exists, the rule does not fire, and neither the responder sink nor the human email sink receives anything. Part 2, gap: with one firing finding alert, remove the metric for at least one evaluation interval (stop the Collector or open a scrape gap) and restore it; the `NoData` instance, which has no `finding_id` label, produces one email to the human sink and nothing to the responder sink, and the finding's alert sends no second firing notification to the responder sink. The provisioned rule names `noDataState: Alerting` and `execErrState: Alerting`; `VERIFY:` Grafana's exact semantics and whether `NoData` keeps an instance active.

`A-RESOLVE` applies D1 option 1 (2026-10-22): one alert means one firing episode. A resolved notification is the same instance's normal resolution, not a second alert. The test asserts exactly one firing notification and at most one resolved notification, and does not count the resolved message as a second alert.

Grouping: one alert instance per `finding_id`/`tier` label set; the notification policy groups by `finding_id` and does not re-send while unresolved; the repeat interval is off or longer than any alert can stay open. `VERIFY:` Grafana alert-instance and notification-policy behaviour and the repeat-interval limit.

Held jobs (`held: ownerless`, `held: owner email missing`, `held: configuration error`) never set the metric and never fire the alert (A39); `A-HELD` covers at least the ownerless case. To avoid waiting the full 30-minute W, the test backdates the job's `created_at` in the test database; production W stays 30 minutes (A33).

Where each case runs (human decision, 2026-10-25, #159). Running every case through Grafana took about 30 minutes a run and was flaky on Grafana's own timing (resolutions arrive minutes after a series goes, and leaked into the next case), so the cases are split by what each needs to prove:

- Compose `alert` job, through real Grafana: `A-FIRE` and its rule-absent negative only, one case per pass (`tests/test_compose_alert.py`).
- Unit/SQLite cases under `make test`, on the same stored state the gauge reads: `A-HELD` (`tests/test_manage.py::test_alert_seed_held_ownerless_never_emits`, `tests/test_metrics_overdue.py::test_held_jobs_never_emit`), `A-TIER` (`test_alert_seed_recorded_tier_wins_over_rescore`), `A-GAP` part 1 (`test_empty_system_has_no_finding_series`, `test_callback_empty_system_emits_only_heartbeat`) and the `sent` → 0 half of `A-RESOLVE` (`test_alert_set_drives_job_to_sent_resolves`). These check the metric, not Grafana's delivery: that the rule does not fire on a 0 or absent finding series rests on the rule being a `> 0` threshold.
- Manual, on a Docker host: `A-GAP` part 2 (the NoData gap) and the Grafana half of `A-RESOLVE` (a resolution is not counted as a second alert), in `_docs/verify-locally.md` §7b. No automated test covers these two.

## Responder: US-15

This section is final, not a placeholder: #50 is closed, its contract is `6ff10d9`, and QA posted PASS at `9a03ba9`. The responder uses the two GET operations `responderGetFinding` (`GET /responder/findings/{id}`) and `responderListNotificationJobs` (`GET /responder/notification-jobs?findingId=...`) with `responderAuth`; `ResponderNotificationJob` carries no recipient, owner contact, advisory summary or embedded finding. Logs come from Loki, not the API.

Demo defect: `VT_DEMO_DEFECT=notify_no_fix` makes the owner-notification formatter fail only for a finding with no fixed version. It is switched on in dev by setting the variable and restarting, and off by unsetting it. The backend refuses to start in production with it set. `P-PROD-REFUSAL` starts the backend in its production configuration (`DEPLOYMENT_ENVIRONMENT` set to `prod` or `production`, or unset: anything other than an explicit `dev`/`test` counts as production, the same fail-closed test as `VT_FEEDS=fixtures`; A35/A42) with `VT_DEMO_DEFECT=notify_no_fix`; startup must exit non-zero and log the configuration error, while dev starts normally. An unknown value such as `VT_DEMO_DEFECT=other` is refused in every environment. The unit form (`tests/test_demo_defect.py`, including a child-process exit check) runs under `make test`; the container form (`tests/test_compose_responder.py`, `compose`-marked) runs in the `responder` job.

The defect is removed before production by a cleanup commit/PR that removes the code path and the variable. `P-FLAG-GONE` is one yes/no check: the `notify_no_fix` path and `VT_DEMO_DEFECT` do not exist anywhere in the code at the tag being promoted. It runs only in the production-promotion workflow (task 18's `production` environment), before the deploy, and fails the promotion while the path exists; it is not in `make test-compose` and not in a pull-request job, so the pull-request gate stays green while the demo defect exists. The same check also covers the `VT_FEEDS=fixtures` rule (task 40 adds the flag): it is delivered with task 29 / #161 together with the `VT_DEMO_DEFECT`/`notify_no_fix` rule, not by #172. `feeds.py` ships in every image by design, so the check targets the fixtures flag/value and its refusal gate, not the module's existence. `VERIFY:` this wording choice (flag/value and gate, not module existence) with the owner. Its own correctness is tested under `make test` against two fixture trees (one with the path, which must fail; one without, which must pass). The defect must not remain in production code.

`P-DEMO-BE` is the submission version of `P-DEMO`, with the backend delivery of task 37 and no n8n: the demo defect makes the backend delivery fail for the no-fixed-version finding; metric 1 and one alert; the responder wakes (`RESPONDER_MODE=stub` in CI); a fix with a test; the local stack is restarted on the merged code (the human in the manual run, the test harness in CI; there is no dev deploy, because pull-request workflows hold no AWS role); the backend delivery retries on its next poll; the notification arrives at MailHog; metric 0 and the alert resolves. Production promotion stays manual; no AWS credential. It runs in the `responder` job. A stub run proves the wiring only; the recorded run of task 39 uses the real responder runtime.

Future: `P-DEMO` is the US-15 demo/E2E: create the no-fixed-version finding, let its job fail, assert metric 1 and one alert, wake the responder (Grafana webhook; `RESPONDER_MODE=stub` in CI), reproduce with a failing test, open a PR (fake GitHub in CI; a real token/App only in the manual demo), have the human merge, let CI deploy to dev, let n8n retry, and assert the notification succeeds, metric 0, the alert resolves and the actions are logged. Production promotion stays manual; no AWS credential.

The responder refused cases from the closed #50 contract are tested in integration `I-RESP-*`: responder token GET-only; `403` on every write; n8n, MCP and session tokens `403` on the two responder operations; no credential `401`; unknown ids and unknown `findingId` behave as the contract says. The responder cannot push to `main`, merge, change settings or touch AWS; the GitHub token/App and branch protection are checked and documented. `VERIFY:` the GitHub App/token scope and branch-protection details.

The responder reads logs from Loki with the Grafana/Loki viewer token, not from the API. Its structured log events carry no secrets or advisory text. `VERIFY:` the viewer token's Loki scope.

## Light security scan in CI

`C-SCAN` runs on every PR in the `security-scan` job on `ubuntu-latest`; the command is `make security-scan` (planned). Its scope is the application's own lockfiles and manifests, not a live service. It fails on high and critical findings in production dependencies and reports lower ones. `C-FIXTURE-VULN` makes a deliberately vulnerable fixture non-zero; `C-FIXTURE-CLEAN` passes a clean fixture. `VERIFY:` the chosen tools (for example `pip-audit` and `npm audit --omit=dev`) and their licence and behaviour; adding either needs approval.

"Light" means dependency auditing only. Secret scanning and SAST are explicitly out of scope (architecture Suggested additions / later work), so the scan has a limit.

## CI jobs and triggers

Every job runs on a pull request and on a review-branch push; a push to `main` re-runs the PR set before deploy. No job depends on a live feed or a secret.

| Job | Runner | Command or target | Tests |
|---|---|---|---|
| `unit` | `ubuntu-latest` | `make test`, `make frontend-test` | `U-*`, `F-*` |
| `sqlite-integration` | `ubuntu-latest` | `make test` | SQLite `I-*` cases, including `I-OWNER-SEND`, `I-OWNER-ONCE`, `I-OWNER-HOLD`, `I-OWNER-NOAWS` and `I-OWNER-SENDER` (in-process sink form) and `I-SCHED` |
| `frontend` | `ubuntu-latest` | `make frontend-test`, `make frontend-typecheck` | `F-*` |
| `openapi-validation` | `ubuntu-latest` | `make openapi-validate` and the backend conformance test | OpenAPI conformance, `I-CONTRACT` |
| `security-scan` | `ubuntu-latest` | `make security-scan` (planned) | `C-*` |
| Future: `workflow-export` | `ubuntu-latest` | `make test-workflows` (planned) | `W-EXPORT` |
| `postgres-integration` | `ubuntu-latest` with Compose | `make test-integration` (planned) | `I-*` on Postgres (the MailHog form of `I-OWNER-NOAWS` and `I-OWNER-SENDER` runs in `make test-compose`, the `telemetry` job, because MailHog is a Compose container of the observability stack) |
| Future: `e2e` | `ubuntu-latest` with Compose | `make test-e2e` (planned) | `E-*` |
| `telemetry` | `ubuntu-latest` with Compose | `make test-compose JOB=telemetry` | `T-REFUSE`, `T-JOURNEY-BE`, and the MailHog form of `I-OWNER-NOAWS` (#172 PR 2); `T-E6` pending #181, `I-OWNER-SENDER` MailHog form pending #182 |
| `alert` | `ubuntu-latest` with Compose; nightly and on demand, not on push/PR (2026-10-25) | `make test-compose JOB=alert` | `A-FIRE` and its rule-absent negative (the other A-* cases: see Alerting: US-14, "Where each case runs") |
| `responder` | `ubuntu-latest` with Compose | `make test-compose JOB=responder` (planned) | `P-DEMO-BE`, `P-PROD-REFUSAL`, `I-RESP-*` |

`make test-compose` takes a `JOB` selector (`telemetry`, `alert` or `responder`; with no `JOB` it runs all three, for the human's host), so each CI job runs only its own cases and the job table shows which job covers which case (the Makefile is protected, so the selector is part of its own human-approved commit in task 25). `P-FLAG-GONE` is in no job in this table: it runs only in the production-promotion workflow (task 18's workflow, step added in task 29).

Task 25 (#157) ships the `JOB` selector and **`T-REFUSE`** only: the backend's real span/log helpers emit excluded attributes through the Collector and the exported signals carry none of them. #157's acceptance criteria were narrowed to that case (human decision, 2026-10-24, "Option C done right").

The other telemetry cases are built on the **containerized-backend-delivers harness of #172** (the backend runs as a container on `VT_FEEDS=fixtures`, drives a scan over HTTP, and the assertions read what actually arrived at MailHog/Prometheus/Tempo/Loki) — not a host-side test process:
- `T-JOURNEY-BE` (#172 PR 2): the **submission journey is 7 spans** — `scan.run` → `repository.read` → `osv.query` → `signals.enrich` → `prioritise` → `notification.enqueue` → `notification.deliver`. `brief.generate` (the 8th span in the `T-JOURNEY` list above) is **future development** (the LLM brief is not built for submission), so it is not emitted or asserted. All 7 share one trace id; the `vt_notifications_total` metric and the structured `notification.deliver` JSON log carry the same id (the delivery worker logs every outcome — `sent`/`failed`/`held` — via `log_event`, #177), and the owner email reaches MailHog.
- The MailHog form of `I-OWNER-NOAWS` (#172 PR 2) is only meaningful when the *container* delivers: it proves the deployed container (no AWS credential) sends the owner email to MailHog.
- The MailHog form of `I-OWNER-SENDER` is **deferred to #182**: the backend always sends From = `MAIL_SENDER`, so there is no product path to make it attempt a wrong-From send at container level, and a test-constructed wrong-From send would test the transport class in isolation, not the deployed guard. The verified-sender refusal is already covered by the unit case `tests/test_notifications.py::test_i_owner_sender_*`; the MailHog form lands with task 28's demo defect (#160, follow-up #182), which gives a real in-container held/refused-delivery path.
- `T-E6` (telemetry backend down, delivery unaffected, **and alerts unaffected**) is **deferred to #181**: its "alerts unaffected" clause needed the US-14 alert rule and the `alert` job (task 27 / #159), which have since landed. #181 is groomed and its decisions are recorded (comment 6396530230), including a narrower reading of "alerts unaffected" that #181 writes into this paragraph.
- `T-DELIVER-TRACE` is **retired, covered by `T-JOURNEY-BE` (#172)**. It was only the delivery-half fallback for when the full journey could not run; `T-JOURNEY-BE` asserts the same trace-id join across metric/trace/log and more, so the fallback is redundant. It is kept here for history and is in no job.

#172 PR 1 wired the feed clients + `VT_FEEDS=fixtures`; PR 2 adds the containerized harness, `T-JOURNEY-BE` and the MailHog `I-OWNER-*` forms. The `alert` job landed with task 27 (#159; nightly and on demand, `.github/workflows/alert.yml`). The `responder` job is task 28 (#160, the Compose part is #220); `make test-compose JOB=responder` exits 3 ("not implemented") until #220 lands.

`make test` remains the single local test command for the rubric's unit + integration requirement, and `make verify` remains the gate. No test is skipped to make a check pass.

## Traceability matrix

Every acceptance bullet of US-1..US-16 maps to at least one test type or named case.

| Story / bullet | Acceptance | Test types or named cases |
|---|---|---|
| US-1 | Asset record shows owner name/email or ownerless marker, criticality and internet-facing; listing shows all three | `F-ASSET` (vitest); `I-ASSET` (`POST /assets`, `GET /assets`, `GET /assets/{id}`); `I-ASSET-UPDATE` (`PATCH /assets/{id}`) |
| US-2a | `uv.lock` gives an entry for every package, including transitive, with name and version | `U-UV`, `I-FINDINGS` |
| US-2b | `requirements.txt` gives an entry for every direct requirement, or "version unknown" with a visible warning | `U-REQ`, `I-SCAN` |
| US-2c | `package-lock.json` gives an entry for every package, including transitive, with name and version | `U-NPM`, `I-FINDINGS` |
| US-3 | Finding shows primary id, all aliases and fixed version when one exists; clean dependency shows no finding | `U-FIXED`, `U-ALIAS`, `I-FINDINGS` |
| US-4 | Exactly one KEV value (listed / not listed / n/a) with stale marker, EPSS or n/a, and asset context | `U-KEV`, `U-EPSS`, `I-FINDINGS` |
| US-5 | Re-scoring the same inputs gives the same order; each finding shows its rank reason | `U-TIER`, `U-TIE`, `I-RANK`, `E-DELIVER` |
| US-6 (Future) | Brief version matches the fixed version, or structured finding with "brief unavailable"; pending marker; never a mismatched version | `U-GUARD`, `I-BRIEF`, `L-EVAL`, `R-*` |
| US-7 | Changed feed data updates signals and ranks without manual action | `I-SIGNALS` (`POST /signals/refresh`, `GET /findings`), `I-SCHED` (backend scheduler) |
| US-8a | A new top-priority finding produces exactly one owner notification and, Future, one GitHub issue | `I-OWNER-SEND`, `I-OWNER-NOAWS`, `I-OWNER-SENDER`, `S-NOTIFY`; Future: `I-JOBS`, `E-DELIVER`, `S-ISSUE` |
| US-8b | Leaving and re-entering the top tier gives no second issue or notification; a `fixed` and reappearing finding (E7) starts a new lifecycle with at most one new of each | `I-OWNER-ONCE`, `I-RESCAN`; Future: `I-LIFECYCLE` |
| US-8c | Exactly one notification and one issue per lifecycle even if the refresh runs twice or retries after a partial failure | `I-OWNER-ONCE`; Future: `I-IDEMPOTENCY` |
| US-8d | Ownerless asset: notification held and asset flagged ownerless, while the GitHub issue is still opened once | `I-OWNER-HOLD`, `A-HELD`; Future: `I-HOLD` |
| US-9a (Future) | Open finding past due produces an owner reminder and a security-lead escalation; weekly digest delivered once per week | `I-REMIND`, `I-DIGEST`, `E-DELIVER` |
| US-9b (Future) | Missing security-lead contact is a visible configuration error, not a silent drop | `I-CONFIG` |
| US-10 | Upgrade outside every affected range gives `fixed` with timestamp; still inside stays `open`; withdrawn advisory gives `withdrawn`; manual re-scan works | `I-RESCAN`, `U-WITHDRAW` |
| US-11a | Dashboard lists findings per asset with current status; changes record who, when and previous value; no automated component sets `risk accepted` | `F-STATUS`, `I-RISK` |
| US-11b | Risk acceptance requires a non-empty reason; empty or whitespace-only is rejected and status does not change | `I-RISK` (`POST /findings/{id}/risk-acceptance`) |
| US-12a (Future) | Known CVE returns the affected assets | `I-MCP` (`GET /mcp/vulnerabilities/{vulnerabilityId}/assets`) |
| US-12b (Future) | A finding stored under a GHSA id with a CVE alias is returned by the CVE lookup | `I-MCP` |
| US-12c (Future) | Known CVE with no asset returns empty and states known; unknown CVE returns empty and states unknown; results are distinguishable | `I-MCP` |
| US-12d (Future) | `list_top_exposures` returns ranked open findings | `I-MCP` (`GET /mcp/top-exposures`) |
| US-12e (Future) | `which_assets_affected` returns affected assets for a known CVE, in any status, each with its status | `I-MCP` |
| US-12f (Future) | `get_finding` returns one finding by id | `I-MCP` (`GET /mcp/findings/{id}`) |
| US-12g (Future) | `get_asset` returns one asset by id | `I-MCP` (`GET /assets/{id}`) |
| US-12h (Future) | MCP output marks advisory-derived text as quoted, labelled untrusted data in `get_finding` and `which_assets_affected`; no instructions presented | `S-MCP` |
| US-12i (Future) | A write with the MCP token is rejected 4xx and changes no state; the MCP server exposes no write tools | `I-AUTH-MCP` (every write operation) |
| US-13 | One scan-to-notification journey emits a metric, trace and structured log with one trace ID, viewable side by side; no excluded data | `T-JOURNEY-BE`, `T-REFUSE`; Future: `T-JOURNEY` |
| US-14 | A top-priority finding not delivered in the window fires exactly one alert naming it; a successful notification fires none | `A-FIRE`, `A-TIER`, `A-GAP`, `A-RESOLVE` |
| US-15 | The undelivered finding reaches its owner, the alert resolves, actions are logged, production promotion stays manual | `P-DEMO-BE`, `I-RESP-*`, `P-PROD-REFUSAL`; Future: `P-DEMO` |
| US-16 (Future) | Each workflow has a committed JSON file under `n8n/workflows/`, named after the workflow, and the exported file is the workflow the repo runs | `W-EXPORT` |

Every edge case E1..E12 maps to at least one test type or named case.

| Edge case | Expected behaviour | Test types or named cases |
|---|---|---|
| E1 | No fixed version: finding stays `open`, shows "no fixed version", is ranked by signals; any brief naming a version is rejected and the structured finding is delivered | `U-FIXED`, `U-GUARD`, `I-BRIEF`, `L-EVAL` |
| E2 | Asset with no owner: finding recorded and ranked, notification held, asset flagged ownerless; setting an owner releases the held notification | `I-OWNER-HOLD`, `I-ASSET-UPDATE`, `A-HELD`; Future: `I-HOLD` |
| E3 | Feed unavailable: OSV first scan gives `scan failed`/`feed unavailable` with no findings; a later scan keeps last-known findings and marks them stale; KEV/EPSS failure keeps the OSV scan status and stale signals; the scheduled run retries | `U-FEED`, `I-SCAN` |
| E4 | Advisory withdrawn or CVE drops out: `withdrawn`, not `fixed`; `risk accepted` also becomes `withdrawn`; no notification; only when every merged advisory is withdrawn; a reinstated advisory restores the previous status or `fixed`, with no second issue or notification; a CVE dropping out of KEV or EPSS changes only signals and rank, not status | `U-WITHDRAW`, `I-RESCAN`, `I-OWNER-ONCE`; Future: `E-DELIVER` |
| E5 | Lockfile parse error: `scan failed`/`lockfile parse error`, previous findings kept and marked stale, visible in the dashboard | `U-NPM`, `I-SCAN`, `F-STATUS` |
| E6 | Telemetry backend unavailable: buffer and retry; findings, notifications and alerts unaffected; gap visible in Grafana | `T-E6` |
| E7 | Fixed finding's vulnerable version returns: `open` with audit entry and a new notification lifecycle, at most one new issue and notification | `I-RESCAN`, `I-OWNER-ONCE`; Future: `I-LIFECYCLE` |
| E8 | `risk accepted` finding's signals escalate: status stays `risk accepted`, flagged "signals changed"; re-scan may still close it. Future: owner and security lead notified once | `I-SIGNALS`; Future: `I-SIGNALS-NOTICE`, `S-SIGNALS` |
| E9 | One vulnerability under two ids: alias sets intersect gives one finding keyed by CVE else primary id; all ids and ranges attached; fixed version derived from all; at most one US-8 notification per lifecycle | `U-FIXED`, `U-ALIAS`, `I-FINDINGS`, `I-OWNER-ONCE`, `L-EVAL` |
| E10 | `requirements.txt` without an exact version: "version unknown", warning, no OSV match, and `scanned, incomplete` when nothing matched; `-r` inside the repo only; outside or remote refused and never fetched; lockfile entry without a version behaves the same | `U-REQ`, `I-SCAN` |
| E11 | No CVE alias: `KEV: n/a (no CVE)`, EPSS `n/a`, finding still recorded and ranked; no advisory dropped for lacking a CVE | `U-KEV`, `U-EPSS`, `I-FINDINGS`, `L-EVAL` |
| E12 | Advisory text contains instructions or links: never followed; no tool, command, URL, path or credential chosen; brief only has allowed fields and the VulnTriage-built link; every advisory URL is inert | `S-*`, `U-GUARD`, `L-EVAL` |

### Stage 4 named cases

| ID | Case | Where |
|---|---|---|
| `N1` | #9 finding 11: a malicious-advisory fixture test for each flow in the spec table | `S-*` |
| `N2` | #9 finding 12: Docker Compose environment named and tests local without Docker listed | Test levels table |
| `N3` | #43 leftover 1: the US-14 gauge's `tier` label is the job's tier, not the finding's current tier | `A-TIER` |
| `N4` | #43 leftover 2: no resolve and re-fire after a metric gap | `A-GAP` |
| `N5` | #43 leftover 3 / D1: a resolved message is not a second alert | `A-RESOLVE` |
| `N6` | Future: exact rejected-brief case: F = `1.2.5`, stub returns `1.2.6` | `R1` |
| `N7` | Telemetry refused case: excluded attributes never reach the backend | `T-REFUSE` |
| `N8` | Demo defect refused in production | `P-PROD-REFUSAL` |

## Limits and refused cases

| Limit | Enforced by | Refused case |
|---|---|---|
| No live network | Stubs and committed fixtures; CI has no feed credentials; a network guard in the test harness | `U-NET` and `I-NET`: any outbound HTTP call fails the test |
| No real secrets | CI has no repository secrets; test settings accept only `LLM_MODE=stub` and `RESPONDER_MODE=stub`; `.env` is never read | A test run with a non-stub mode or a secret-valued variable fails before the suite starts |
| No production data | Test-owned Compose projects `vt-test`/`vt-e2e` and ephemeral volumes; migrations on a test database | `E-GUARD` and the integration guard fail before start when the target database or host is not the test one |
| Telemetry exclusions (advisory text, owner contact, repository URL, lockfile content, credentials) | One allowlist helper in code and a Collector processor before export | `T-REFUSE`: exported signals contain none of the excluded values; auto-instrumented URL attributes are dropped |
| Responder read-only | API authorisation of role `responder-read` against the two-operation allowlist | `I-RESP-WRITE` / `I-RESP-OTHERGET`: `403` and no state change |
| Owner notification sender | The configured verified sender in the mail-transport setting (task 37); a send from any other address is refused | `I-OWNER-SENDER`: nothing is delivered to MailHog and the job is not `sent` |
| Demo defect refused in production | Startup check in production configuration (`ASSUMPTION: T-A8`) with `VT_DEMO_DEFECT` set | `P-PROD-REFUSAL`: startup exits non-zero and logs the error |
| Malicious text is never instructions | Quoting, labelling and defanging per flow; the LLM guardrail | `S-*`: the instruction is not followed and no URL, secret or contact detail is emitted |

## Open questions / assumptions

| Tag | Item | Resolution or owner |
|---|---|---|
| `ASSUMPTION: T-A1` | Compose service `db`; test projects `vt-test` and `vt-e2e`; fixture asset/repo names; 120 s E2E timeout | Final names fixed with the Compose work in Stage 5/#31. |
| `ASSUMPTION: T-A2` | Fixture capture baseline is 2026-10-22; the recorder writes the actual date | First deliberate captures in tasks 4-6 (harness in task 1, manifest completed in task 13), not #56. |
| `ASSUMPTION: T-A3` | Grafana rule uses `noDataState: Alerting` and `execErrState: Alerting`; with the constant global `0` series, `NoData` means the backend or metric is down and alerts the human email only, never the responder | Confirm when the rule is provisioned. |
| `ASSUMPTION: T-A4` | The US-13 metric carries the trace id as an OTel exemplar; if the exporter cannot, a trace/log join by trace id is the fallback | Spec note 2 in #56. |
| `ASSUMPTION: T-A5` | `make test` grows to include backend unit and SQLite integration and stays the single local command | Task 1 creates the harness and the target; each later task adds its cases; task 13 confirms. |
| `ASSUMPTION: T-A6` | MailHog is the local mail catcher (dependency, ask before adding) | Stage 5/backlog. |
| `ASSUMPTION: T-A7` | `pip-audit` and `npm audit --omit=dev` are the light-scan tools; adding them needs approval | Stage 5/backlog. |
| `ASSUMPTION: T-A8` | Production configuration is selected with `ENVIRONMENT=production`; the final name is a build detail | Confirm in the backend build. |
| `VERIFY:` | OSV endpoints, batch limit, fields and fixture shape; CISA KEV URL/fields; EPSS URL/fields; GitHub contents API | Architecture § External data sources; capture the fixtures deliberately. |
| `VERIFY:` | PEP 440 and SemVer library behaviour, including leading `v` and pre-releases | Architecture § Ingestion and matching. |
| `VERIFY:` | OTel Prometheus exemplar support, Tempo-to-Loki/Grafana links, Collector processor names, SDK batch/Collector queue and self-metric names | Architecture § Observability; confirm when the stack is built. |
| `VERIFY:` | Grafana no-data/error semantics, alert-instance and notification-policy behaviour, and the repeat-interval limit | Architecture § Observability; confirm with the provisioned rule. |
| `VERIFY:` | GitHub Markdown fence rules and whether mentions inside code blocks notify | Architecture § Security boundaries. |
| `VERIFY:` | GitHub App/token scope and branch-protection details; Loki viewer token scope | Architecture § Security boundaries and § Responder agent. |
| `VERIFY:` | LLM provider, endpoint, schema-constrained output, retention and pricing | Architecture Open question 9. |
| `VERIFY:` | `pip-audit` / `npm audit` licence and behaviour | Security-scan build task. |
| `VERIFY:` | MailHog's HTTP API for reading received mail, and how `make test` reaches MailHog in the Docker-less sandbox; the SES sandbox allows only verified recipient addresses | Task 37 build. |
