# Frontend prototype comparison: Bolt vs Lovable (issue #15)

Date: 2026-10-18. Reviewer: Orchestrator (Claude Code, Opus 5.5).
Inputs: `frontend-bolt/` (commit `fea6fb7`), `frontend-lovable/` (commit `0dd108a`),
both built by the human from the APPROVED `## Prompt` in
`_docs/prompts/lovable-frontend.md`.

**Method: static read only.** Node.js and npm are not installed in the dev
container (`node --version`: command not found), and #15 says to install
nothing in that case. Neither app was installed, built, run or tested. Every
claim below comes from reading the source; anything about runtime behaviour is
marked VERIFY.

## Human decisions (2026-10-18, #15 session)

1. Winner: **Lovable** goes forward as `frontend/`.
2. `frontend-bolt/` is **deleted in its own commit**, linking this review. It
   stays in history at `fea6fb7`.
3. The PM **files F0 to F6 now**. F4 to F6 are blocked until the human changes
   the AGENTS.md "Current phase" line (protected; approved separately).
4. OpenAPI: **hand-written `openapi.yaml` is the contract** (F3), and a
   backend test fails if FastAPI's generated document differs from it (F4).
   `_docs/planning-process.md` Stage 3 wording changes to match, after the
   human approves the exact text.

## Verdict

**Recommended: Lovable**, moved to `frontend/`, after a clean-up issue (F1)
that removes the Lovable-platform coupling and unused code.

Why: steps 3 to 5 depend on the services layer looking like a real API client.
Lovable's already does (async, URL-routed, cached with invalidation). Bolt's
would need a rewrite of the data path of every screen, plus a router, to get
there. Lovable's problems are mostly *extra* code, which can be deleted. Bolt's
problems are *missing* structure, which has to be built.

Close second: Bolt. It is smaller, more conventional and has more tests. A few
of its ideas should be carried over (see "Port from Bolt").

## Side-by-side

| Area | Bolt | Lovable | Better for steps 3-6 |
|---|---|---|---|
| Stack | Vite 5 + React 18 SPA, Tailwind 3 | TanStack Start (SSR, nitro) + React 19, Vite 8, Tailwind 4, shadcn/ui | Bolt (simpler) |
| Dependencies | 3 runtime, 19 dev | ~50 runtime, 23 dev. Only 4 of 46 `components/ui/*` files are used | Bolt |
| Lockfile | `package-lock.json` (npm) | `bun.lock` only. npm can't read it, so `npm install` resolves fresh versions | Bolt |
| Versions | Mature | Bleeding edge: `vite 8.1.5`, `vitest ^4`, `nitro 3.0.260603-beta`, `rolldown` override | Bolt |
| Vendor lock-in | `.bolt/` (2 files, inert) | `@lovable.dev/vite-tanstack-config` hides the Vite plugin list; `lovable-error-reporting.ts`; nested `AGENTS.md` with Lovable sync rules; `twitter:site @Lovable` | Bolt |
| Services shape | **Synchronous**, returns `{ok, error}` objects | **Async (`Promise`)**, throws `Error` | **Lovable** |
| Data fetching | `useMemo(() => services.x())` in each screen | `@tanstack/react-query` with `invalidateQueries` after writes | **Lovable** |
| Routing | None: a `route` value in React state. No deep links; a page refresh signs you out and returns to login | File routes with URLs (`/findings/$id`, `/findings/$id/accept`, `/assets/new`); session kept in `sessionStorage` | **Lovable** (step 5 multi-window test needs URLs) |
| Status values | `'risk accepted'` (a space in the wire value) | `risk_accepted` plus a `STATUS_LABEL` display map | **Lovable** |
| Finding fields | No installed version | `installedVersion` (US-2/US-3 need it) | **Lovable** |
| Brief | A plain string | `{summary, impact, remediation, advisoryReference}` plus `briefStatus` (fits the Stage 2 structured-output guardrail) | **Lovable** |
| Finding + asset | Client joins `assetId` to `listAssets()` | Service returns `FindingWithAsset` | Lovable (fewer calls) |
| Mock packages | Maven/Java (`log4j-core`, `jackson-databind`). Outside the spec's lockfiles (`uv.lock`, `requirements.txt`, `package-lock.json`) | Fictional npm/PyPI-style names, with installed versions | Lovable |
| Audit "who" | The service takes it from the signed-in user | **The client passes `user` into `acceptRisk`**. A real API must take it from the token | **Bolt** |
| Methods | 9: `signIn`, `signOut`, `currentUser`, `listFindings`, `getFinding`, `acceptRisk`, `listAssets`, `getAsset`, `registerAsset` | 6: `login`, `listFindings`, `getFinding`, `acceptRisk`, `listAssets`, `registerAsset`. No `getAsset` and no `signOut` | Bolt |
| Owner contact | `owner` + `ownerEmail` | `owner` is one free-text field (an email in the mock) | Bolt (US-8 notifies the owner) |
| Audit entry id | Yes | No (list index used as the React key) | Bolt |
| Withdrawn in list | Status badge only | Row greyed out, struck-through badge, "left its feed" | Lovable |
| Asset "no findings" | Shows a count of 0 | Explicit "no findings" flag, separate from "not yet scanned" | Lovable |
| Tests | 12 cases in 4 files | 9 cases in 2 files, including a route-tree test | Bolt (more) |
| Network calls outside services | None | `server.ts` (SSR handler `fetch`, not a call) and Google Fonts in `__root.tsx`. #15's grep criterion would flag `server.ts` | Bolt |
| Emails | All `example.com/.org/.net` | All `example.com/.org/.net` | Tie |
| Demo login | `dana.reyes@example.com` / `triage-demo`; `LoginScreen` imports it from `mockServices` | `analyst@example.com` / `triage-demo`; `login.tsx` imports it from `mockData` | Tie (both bypass the services seam) |

Both meet the prompt's screen list (six screens and a layout shell, no extras),
the risk-reason validation, the ranking rule inside the mock, and the mock data
checklist, as far as a read can tell.

## Risks to carry with the Lovable choice

1. **SSR vs SPA.** TanStack Start builds a nitro server. The Lovable config
   comment says nitro's default build target is Cloudflare. VERIFY: whether
   `vite build` outputs a Node server or static files that can run in a
   container on AWS. Decide in F1: keep Start with a Node preset, switch Start
   to SPA mode, or move to plain TanStack Router. Mock data lives in module
   memory, so with SSR the server and the browser each hold their own copy.
   That's harmless today (all queries run in the browser), but it must not
   survive into step 5.
2. **No npm lockfile.** The first `npm install` must create
   `package-lock.json`. That is an install of about 70 packages and needs the
   human's approval (AGENTS.md: dependencies).
3. **Platform hooks.** `lovable-error-reporting.ts` calls `window.__lovableEvents`,
   which is only present inside the Lovable editor. Locally it does nothing,
   but it is dead weight and a telemetry path that isn't ours (US-13 forbids
   unplanned telemetry).
4. **Nested `frontend-lovable/AGENTS.md`.** OpenCode and Claude Code read
   nested AGENTS.md files. Its Lovable sync rules ("push to main syncs to
   Lovable") contradict the root AGENTS.md. Remove it or replace it in F1.
5. **Auth model.** `acceptRisk(id, reason, user)` trusts the client's user. The
   contract (F3) must drop `user` and take "who" from the bearer token.

## Port from Bolt

- `getAsset(id)` and `signOut()` in the services interface.
- `ownerEmail` kept separate from the owner's name (US-8 notifications, E2
  ownerless).
- An `id` on each audit entry.
- "Who" decided by the service, not passed in by the client.
- Bolt's extra test cases: sign-in success, ownerless/scan error/not yet
  scanned, and a whitespace-only reason through the form.

## Other findings (not fixed here)

- `.devcontainer/devcontainer.json` has the `PATH` key twice under
  `remoteEnv`. Unrelated to #15; noted for the human.
- `uv` isn't installed either (step 4 needs it; the brief fixes uv for Python
  dependencies).
- Plan conflicts for steps 3 to 6 (decisions needed, listed in the session
  report to the human):
  - AGENTS.md says "Current phase: PLANNING. No application code until the plan
    in _docs/ has passed review". Steps 4 to 6 are application code, and
    `_docs/architecture.md` (Stage 2) isn't written yet.
  - `_docs/planning-process.md` Stage 3 says "The OpenAPI document is generated
    by FastAPI at build time, not hand-maintained". Step 3 asks for an
    `openapi.yaml` derived from the frontend client. Proposed fix: the
    hand-written `openapi.yaml` is the *contract*, and a backend test checks
    that FastAPI's generated document matches it.
  - #3 (which fixed version applies) and #4 (aliases) are still open. The
    contract keeps the prompt's labelled assumptions until they are resolved.

---

## Draft follow-up issues (not filed)

Written for an implementing agent on OpenCode. The Orchestrator reviews each
one through PM grooming and QA. Each follows
`_docs/agent-kit/templates/task-template.md`. The PM files them only after the
human approves (process.md, Backlog). Numbers are placeholders: F0 to F6.

Dependency chain: F0 → #15 (re-scoped) → F1 → F2 → F3 → F4 → F5 → F6.
F4 to F6 are also gated by the PLANNING-phase decision.

### F0. Dev container: Node.js and uv available to agents

**Goal.** `node`, `npm` and `uv` run inside the dev container, so the frontend
and backend can be installed and tested through make targets.

**Acceptance criteria**
- [ ] `.devcontainer/devcontainer.json` adds the Node feature (LTS, version
      pinned) and installs uv (version pinned). VERIFY: feature ids and the uv
      install method.
- [ ] After a rebuild, `node --version`, `npm --version` and `uv --version`
      succeed inside the container.
- [ ] The duplicate `PATH` key in `remoteEnv` is removed.
- [ ] `_docs/agent-kit/environments.md` lists Node and uv as available in the
      local sandbox.
- [ ] **Refused case:** no global npm packages and no `curl | sh` from an
      unpinned URL.

**Out of scope:** Docker (still a codespace or Compose recipe).
**Constraints:** system configuration. The human approves the exact diff and
rebuilds the container. Files: `.devcontainer/*`,
`_docs/agent-kit/environments.md` (protected: `HUMAN_APPROVED=1`).

### #15 (re-scope, not a new issue)

The PM re-grooms #15 for the comparison outcome: "Frontend v1: choose
Lovable over Bolt and import into `frontend/`". Changes to the current body:
- `git mv frontend-lovable frontend` in its own commit. `git log --follow
  frontend/src/services/index.ts` reaches `0dd108a`.
- `frontend-bolt/` is removed, or kept, as the human decides. If removed: in
  its own commit, with this review linked in the message. It stays in history
  at `fea6fb7`.
- Run record: Lovable after the credit reset (date, follow-ups verbatim,
  credits, or "not recorded"), plus the Bolt run as a compared alternative.
- The existing stage E criteria stay as they are (Node check, scans,
  make targets `frontend-install/start/stop/test`, test-all in `TEST_CMD`,
  `frontend/README.md` listing the services methods). One addition: the
  network grep excludes `src/server.ts` only if F1 still keeps SSR, with the
  reason given.
- Depends on F0.

### F1. Frontend clean-up: remove Lovable coupling and unused code

**Goal.** `frontend/` is a plain, reproducible React app with no app-builder
platform hooks and no unused components, ready to be the long-lived client.

**Acceptance criteria**
- [ ] `frontend/package-lock.json` is committed and `bun.lock` / `bunfig.toml`
      are removed. `make frontend-install` uses `npm ci`.
- [ ] Unused `src/components/ui/*` files are deleted. Today only `button`,
      `input`, `label` and `textarea` are imported. Every dependency left in
      `package.json` is imported somewhere in `src/` or is a build/test tool.
      The Engineer: comment lists each removed dependency.
- [ ] Removed: `src/lib/lovable-error-reporting.ts` and its call,
      `frontend/AGENTS.md`, `.lovable/`, the `twitter:site @Lovable` meta, and
      the Google Fonts links (system fonts or self-hosted).
      `grep -rni lovable frontend --exclude=package-lock.json` has no hits other
      than a provenance line in `frontend/README.md`.
- [ ] `@lovable.dev/vite-tanstack-config` is replaced by an explicit
      `vite.config.ts` that lists its plugins.
- [ ] Render mode decided (decision question to the human, with the
      Engineer's evidence): Start SPA mode, Start with a Node server preset,
      or plain TanStack Router. `make frontend-build` produces output that can
      be served from a container. VERIFY: the TanStack Start SPA-mode option.
- [ ] `frontend/README.md` is rewritten: what the app is, make targets,
      provenance (Lovable project, `0dd108a`, Bolt alternative at `fea6fb7`),
      and the services methods list.
- [ ] `make frontend-test` passes with the same or more test cases. No test is
      deleted or weakened, except tests of removed platform code, each one
      named in the Engineer: comment.
- [ ] **Refused case:** `grep -rnE "fetch\(|axios|XMLHttpRequest|WebSocket|https?://" frontend/src`
      hits only `src/services/` and mock data.

**Out of scope:** services-layer shape changes (F2); visual changes.
**Constraints:** files under `frontend/` only, plus `Makefile` (protected) if
targets change. No new dependency without asking.

### F2. Services layer ready for a real API

**Goal.** The `Services` interface is the final frontend contract: every
method maps to one HTTP call, and nothing in it depends on being a mock.

**Acceptance criteria**
- [ ] `acceptRisk(id, reason)` no longer takes a `user`. The mock takes "who"
      from its own session, as a real API takes it from the token.
      **Refused case:** a test calls `acceptRisk` with no signed-in session and
      expects an "unauthenticated" error and no audit entry.
- [ ] Added: `getAsset(id)`, `logout()`, `currentUser()` (or `me()`).
- [ ] `Asset` has `ownerName: string | null` and `ownerEmail: string | null`
      in place of the single `owner` field. Ownerless means both are null
      (`specs.md` E2).
- [ ] `AuditEntry` has an `id`.
- [ ] Errors are one typed `ServiceError {code, message}` with codes
      `validation`, `not_found`, `conflict`, `unauthenticated`. Screens show
      `message`. These map to 422/404/409/401 in F3.
- [ ] Screens get the demo credentials through the services layer (for
      example `services.demoCredentials()` on the mock only, or a constant in
      `src/services/`), not by importing `mockData`. **Refused case:**
      `grep -rn "services/mock" frontend/src/routes frontend/src/components`
      has no hits.
- [ ] The mock's data and module are imported only through
      `src/services/index.ts` (one switch point for F5).
- [ ] Tests cover each new method and each error code.
- [ ] `frontend/README.md` lists every method: parameters, return type, the
      errors it can throw, and the HTTP call it will become (method + path,
      marked "proposed until F3").

**Out of scope:** the HTTP client itself (F5).
**Constraints:** `frontend/` only. Status wire values stay
`open | risk_accepted | fixed | withdrawn`.

### F3. API contract: `_docs/api.md` and `openapi.yaml` from the services layer (course step 3)

**Goal.** One explicit contract between frontend and backend, derived from
the F2 services layer: endpoints, methods, request and response bodies,
errors and authentication.

**Acceptance criteria**
- [ ] `openapi.yaml` (OpenAPI 3.1, at the repo root or under `api/`; a PM
      grooming choice) has one operation per `Services` method, and no
      operation without a method. The Engineer: comment has a
      method → operation table.
- [ ] Every schema matches the TypeScript types in `src/services/types.ts`:
      field names, nullability, enums (`Tier`, `FindingStatus`, `Criticality`,
      `ScanStatus`). QA compares them field by field.
- [ ] Auth: `POST /auth/login` returns a bearer token. Every other operation
      requires `bearerAuth`, except login. `POST /findings/{id}/risk-acceptance`
      takes only `{reason}`; "who" comes from the token.
- [ ] Errors: one `Error {code, message}` schema; 401, 404, 409, 422 used as
      F2 maps them. An empty or whitespace-only reason → 422. Accepting a
      non-open finding → 409.
- [ ] `listFindings` documents that the order is the ranking and the client
      doesn't re-sort.
- [ ] The file validates. VERIFY: which validator (for example
      `openapi-spec-validator` through `uvx`); ask before adding it.
- [ ] `_docs/api.md` follows `_docs/planning-process.md` Stage 3: an endpoint
      table (method, path, request, response, auth, consumer) for the frontend
      endpoints now, with n8n and MCP rows marked "to add" (not in scope).
- [ ] Labelled ASSUMPTIONs stay for #3 (ranges and fixed versions) and #4
      (aliases), each linked to its issue.
- [ ] The relation to Stage 3's "generated by FastAPI, not hand-maintained"
      rule is settled by the human first (decision in the #15 session), and
      `planning-process.md` is updated to match if needed.

**Out of scope:** backend code (F4); n8n and MCP endpoints.
**Constraints:** no new runtime dependencies. Linked from `README.md`
(planning-process.md: every planning file is linked).

### F4. FastAPI backend with an in-memory store (course step 4)

**Goal.** A FastAPI app in `backend/` implements every F3 operation against an
in-memory store seeded with the same fixtures as the frontend mock.

**Acceptance criteria**
- [ ] `backend/` is a uv project (`pyproject.toml`, `uv.lock`). Its
      dependencies are listed and approved before they are added.
- [ ] Every operation in `openapi.yaml` is implemented. **Contract test:** a
      pytest test loads `openapi.yaml` and FastAPI's `app.openapi()` and fails
      if any path, method, or request/response schema differs. QA breaks one
      field on purpose in a `.scratch/` copy and confirms the test catches it.
- [ ] Storage sits behind a repository interface (for example
      `FindingRepository`, `AssetRepository`), with an in-memory
      implementation. Route handlers never touch the store directly (this is
      what F6 swaps).
- [ ] Seed data matches the frontend mock (same ids, the same coverage list
      from the prompt). One fixture file, or a test that compares the two.
- [ ] Ranking: `GET /findings` returns the mock's order. A test asserts the
      order. VERIFY against `_docs/architecture.md` once Stage 2 exists.
- [ ] Auth: the demo user only, a token from `/auth/login`. "Who" in audit
      entries comes from the token. **Refused cases:** no token → 401;
      whitespace reason → 422 and the status is unchanged; accepting a
      withdrawn finding → 409.
- [ ] Make targets: `backend-install`, `backend-start`/`backend-stop` (PID
      recorded, as for `frontend-*`), `backend-test`. The all-tests target runs
      both frontend and backend tests.
- [ ] No secret in code. The token signing key comes from an env var with a
      `.env.example` entry.

**Out of scope:** the database (F6); n8n/MCP endpoints; real feeds.
**Constraints:** gated by the PLANNING-phase decision. `Makefile`, `AGENTS.md`
and `agent-kit.conf` are protected.

### F5. Connect the frontend to the backend (course step 5)

**Goal.** The frontend talks to the F4 backend through an HTTP implementation
of `Services`, chosen by configuration. The mock stays for tests.

**Acceptance criteria**
- [ ] `src/services/httpServices.ts` implements `Services` with `fetch`
      against `VITE_API_BASE_URL`. `src/services/index.ts` picks http or mock
      from `VITE_SERVICES=http|mock` (default `http` in dev, `mock` in tests).
      Both are in `frontend/.env.example`.
- [ ] The bearer token is kept in `sessionStorage` and sent on every call. A
      401 signs the user out and goes to `/login`.
- [ ] Backend CORS allows only the origins in an env var (default
      `http://localhost:<frontend port>`). **Refused case:** a test request with
      `Origin: http://evil.example.com` gets no `Access-Control-Allow-Origin`.
- [ ] `fetch` appears only in `src/services/httpServices.ts`.
- [ ] Manual check, recorded in the Engineer: comment, with two browser windows
      signed in: (1) accept risk in window A, then refresh window B: the status
      and audit entry show; (2) register an asset in A: it appears in B's asset
      list as "not yet scanned"; (3) restart the backend: the data resets
      (expected until F6).
- [ ] `make dev` (or similar, a name for the PM) starts the backend and the
      frontend together, with one stop target.

**Out of scope:** persistence (F6); deployment.
**Constraints:** `frontend/`, `backend/` (CORS only), `Makefile` (protected).

### F6. Database persistence with SQLAlchemy (course step 6)

**Goal.** The F4 in-memory repository is replaced by SQLAlchemy, SQLite by
default, configured by `DATABASE_URL`, with no SQLite-only code, so Postgres
is a configuration change.

**Acceptance criteria**
- [ ] SQLAlchemy 2.x models for assets, findings, affected ranges, aliases and
      audit entries, matching `_docs/architecture.md`'s data model (or labelled
      ASSUMPTIONs if Stage 2 is still unwritten).
- [ ] `DATABASE_URL` is read from the environment. Default
      `sqlite:///./vulntriage.db`, in `.env.example`. `*.db` stays forbidden by
      `agent-kit.conf`.
- [ ] Database-agnostic: no SQLite-specific SQL or types. **Refused case:**
      `grep -rniE "sqlite" backend/app` hits only the default URL.
- [ ] Schema migrations: Alembic (a dependency question for the human), with a
      `make migrate` target and the AGENTS.md "New migration" command updated
      (protected).
- [ ] `make backend-seed` loads the shared fixtures into an empty database. It
      is idempotent.
- [ ] The F4 contract test and API tests run against a temporary SQLite file
      and pass unchanged.
- [ ] Persistence test: write (accept risk), restart the app, read: the status
      and audit entry are still there.
- [ ] The F5 two-window manual check passes again, and step (3) now shows the
      data kept after a backend restart.

**Out of scope:** Postgres via Docker Compose (needs Docker: a later issue,
`_docs/agent-kit/environments.md`); real feeds and scanning.
**Constraints:** `backend/`, `.env.example`, `Makefile` and `AGENTS.md`
(protected).
