# Proposal: move the API under `/api` (Option B) to resolve the single-origin SPA/API collision

**Date:** 2026-10-23
**Context:** #137 (task 15, the Compose stack). On one origin the SPA and the API
both claim `/findings` and `/assets`. The human prefers Option B (a `/api`
prefix) over Option A (Accept-header routing). This document analyses the impact
and proposes the exact changes **before** any edit.

**Status:** APPROVED and IMPLEMENTED (2026-10-23). The human approved Option B,
D1 (`root_path="/api"`) and D2 (`/api/health`). Implemented on the
`feat/137-compose-stack` branch as part of #137; see the rollout plan below and
the #137 session summary. `architecture.md`/`testing.md` needed no change
(their `/health` references are the backend path, which did not move).

**Correction (D1), after `make verify`:** `root_path="/api"` is deprecated in the
pinned FastAPI (0.161.1) and emits a `FastAPIDeprecationWarning`. Since D1 was
optional and cosmetic (the proxy strips `/api` regardless), `root_path` was
**dropped** — the app sets no `root_path`. The `/api` base lives in the proxy and
`openapi.yaml`'s `servers.url`. `make verify` also caught a stale task-4 test
that pinned `.env.example` to the single `GITHUB_READ_TOKEN=` line; it was
updated to assert the task-15 contract (required names present, showcase names
absent, no committed values).

## The problem (recap)

- The SPA's client-side router has pages at `/`, `/login`, `/assets`, `/findings`, `/findings/:id`.
- The backend API serves `GET /findings`, `GET /assets`, etc. at the same root.
- On one origin a request for `/findings` is ambiguous: SPA page (HTML) or API (JSON)? A browser hard-refresh on `/findings` would get API JSON instead of the app. The same ambiguity is latent in the #133 Vite dev proxy.

## The mechanism (how `/api` resolves it)

Three moving parts, each small:

1. **Frontend** sends every API call to `/api/...` instead of `/...`.
2. **The reverse proxy** (nginx in Compose; Vite in dev) routes `/api/*` to the backend and **strips the `/api` prefix**, so the backend receives `/findings` exactly as today. Everything else (`/`, `/findings`, `/assets`, ...) is served by the SPA.
3. **The backend is unchanged in routing**: it still mounts `/findings`, `/assets`, etc. Optionally `root_path="/api"` is set so the generated OpenAPI docs advertise the prefix, but it is not required for correctness because the proxy strips the prefix.

Key consequence: because the proxy strips `/api`, the backend's routes, the 58 `TestClient` endpoint tests, and the conformance test's path sets **do not change**. The move is almost entirely frontend + proxy + docs.

## Impact map

### Must change (not protected — no `HUMAN_APPROVED` needed)

| # | File | Change | Why |
|---|---|---|---|
| 1 | `frontend/src/services/httpService.ts` | Add `const API_BASE = "/api"` and build every request as `` `${API_BASE}${path}` `` (one place in `request()`), keeping the per-call paths as they are. | The browser must call `/api/...`. |
| 2 | `frontend/src/test/http-service.test.ts` | Update the two exact-URL assertions to expect `/api/assets` and `/api/findings/f1/risk-acceptance`. | They assert literal URLs. |
| 3 | `frontend/nginx.conf` (new in #137) | Replace the per-path proxy blocks with a single `location /api/ { proxy_pass http://backend:8000/; }` (trailing slash on `proxy_pass` strips `/api`). The SPA `location /` fallback then cleanly owns `/`, `/findings`, `/assets`. Backend `/health` is reached at `/api/health` (D2). | Resolves the collision; this is the whole point. |
| 4 | `frontend/vite.config.ts` | Replace the `apiPaths` list with a single `/api` proxy whose `rewrite` strips `/api` (so dev behaves like Compose). | Dev parity; the SPA owns `/findings`/`/assets` in dev too. |
| 5 | `_docs/openapi.yaml` | `servers: - url: /` → `url: /api`. Paths stay relative. | Contract records the base. The conformance test ignores `servers`, so this is safe. |
| 6 | `_docs/api.md` | Update the base-path statement and the `/health` note (D2); the endpoint table paths stay relative to the server. | Doc accuracy. |

### Must change only if we set a backend `root_path` (D1)

| # | File | Change | Why |
|---|---|---|---|
| 7 | `backend/vulntriage/main.py` | `FastAPI(lifespan=lifespan, root_path="/api")` (one line). | Makes `GET /openapi.json` / Swagger advertise `/api`. **Optional** — see D1. |

With `root_path`, routing is still at `/findings` (Starlette does not match on `root_path`), so **no test changes** and **no router/decorator changes**. We will NOT use router `prefix="/api"` — that would force ~58 test edits and ~8 conformance-test edits for no benefit, since the proxy strips the prefix anyway.

### Must verify (likely no change)

| File | Check |
|---|---|
| `backend/Dockerfile`, `compose.yaml` (new in #137) | The backend health check calls the backend **directly** at `http://localhost:8000/health` (no proxy in the path), so it stays `/health` regardless of D2. ✅ already written that way. |
| `_docs/architecture.md`, `_docs/testing.md` | `/health` prose and endpoint references drift only if D2 moves health; update for accuracy. Not executable. |
| `Makefile` (protected), `_docs/specs.md` (protected) | Grep confirmed neither references literal API paths today. Expected: **no change**, so no protected commit for this part. |

### No change needed

- The 58 `TestClient` endpoint tests (`tests/test_api_*.py`) — the proxy strips `/api`; the app still routes at `/findings`.
- `tests/test_openapi_conformance.py` — it compares `app.openapi()` path keys against the contract `paths:` keys; neither changes (it never reads `servers`).
- Wire schemas / `types.ts`, auth/CSRF/cookie logic, README.

## Decisions needed from the human

**D1 — set `root_path="/api"` on the backend?**
- **Recommend: yes.** One line; makes the backend's own `/docs` and `/openapi.json` correct behind the proxy, and matches the contract's `servers.url: /api`. Costs nothing (no test/route changes).
- Alternative: omit it. The app still works (proxy strips the prefix), but the backend's self-served OpenAPI would advertise `/` while the contract says `/api` — a cosmetic mismatch.

**D2 — where does the backend health endpoint live from the browser/proxy side?**
- **Recommend: `/api/health`.** The frontend/proxy reach the backend only under `/api`, so health goes through the same single `location /api/` rule — one proxy rule, no special-case. The Compose/Dockerfile container health check already hits the backend **directly** at `:8000/health` (not via the proxy), so it is unaffected either way. We'd update the `/health` note in `api.md` (and the conformance test's `EXCLUDED_PATHS` stays `{"/health"}` because that is the backend's own path, which does not change).
- Alternative: keep a special proxy rule for `/health` outside `/api`. More config for no gain.

## Rollout plan (once D1/D2 approved)

1. Frontend: `httpService.ts` (API_BASE), its 2 test assertions, `vite.config.ts` (single `/api` proxy with rewrite).
2. Proxy: `frontend/nginx.conf` → single `/api/` location.
3. Backend: `root_path="/api"` (if D1 yes).
4. Contract/docs: `openapi.yaml` `servers.url`, `api.md` base + health note; accuracy fixes in `architecture.md`/`testing.md`.
5. Finish the rest of #137 (Dockerfiles/compose already written; adjust the frontend health/proxy only).
6. Hand off: human runs `make verify` (frontend suite + conformance test must stay green — expected, since backend/tests are untouched) and `make compose-up`, then a hard-refresh on `/findings` to confirm the SPA loads (the acceptance of the whole change).

## Why not Option A (Accept-header routing)

A works with zero contract change but relies on a subtle nginx `map` on `Accept`, is harder to reason about, and leaves the API and SPA permanently entangled at the same paths (fragile for future routes). B is a one-time, explicit separation. The human chose B; this analysis confirms B is cheap because the proxy-strip keeps the backend and all its tests unchanged.

## Risk / notes

- `VERIFY:` nginx `proxy_pass http://backend:8000/;` (trailing slash) strips the matched `location /api/` prefix — standard behaviour; confirmed at `make compose-up`.
- `VERIFY:` Vite `server.proxy` `rewrite: (p) => p.replace(/^\/api/, "")` for dev parity.
- This change is contained in #137's branch; it does not alter the wire contract (schemas, auth), only the path prefix and the `servers` base. It is not a protected-file change (no Makefile/specs edits expected).
