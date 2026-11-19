# Issue #140: Serve the built frontend from the FastAPI app

**Date:** 2026-11-13T22:03Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

The app now serves `frontend/dist`: `socboard/spa.py` adds one GET/HEAD fallback route after every API router. It never matches `/api` or a path under it, returns a file only if its real path is inside the folder, returns `index.html` for extension-less paths and a 404 for a missing path with an extension. The folder comes from `SOCBOARD_STATIC_DIR` (default `frontend/dist` in the repository root); a missing folder or `index.html` adds nothing. Cache headers: `no-cache` for the entry page and unhashed files, one-year `immutable` for `assets/`. Decision record committed as `proposed`.

**What I learned:** a catch-all route that accepts all methods would turn an unknown `/api` POST from 404 into 405 or a wrong-method answer into 404, so the route class refuses `/api` in `matches()` and takes GET only.

## Reflection

### Engineer

unknown (role not asked). The Engineer's comments on the issue carry no Reflection block; the launches were separate and cannot be resumed.

### QA

unknown (role not asked)

### Orchestrator

unknown (role not asked). Close-out by the Hardening session on 2026-11-14: PR #150 merged as `efbf67c` (on `origin/main`); the closing QA PASS is the second Heavy launch at `35cad54` (https://github.com/andrew-chung-au/socboard/issues/140#issuecomment-6872787764), after the re-check PASS at `2d030c5` (https://github.com/andrew-chung-au/socboard/issues/140#issuecomment-6869889192). The follow-up issue 160 holds the Reviewer findings and the QA Lows left unfixed by the human's decision.

## Launch usage

none

## Files created or modified

`socboard/spa.py` (new), `socboard/app.py`, `tests/test_spa_serving.py` (new), `README.md` (one paragraph), `_docs/decisions/2026-11-13T2156Z-serve-built-frontend.md` (new, proposed), `_docs/index.md` (one row), this summary.

## Decisions made by the human

The Decision record in the issue body was approved with the issue. I deviated in one detail: no separate `assets` mount, because one route has one containment check (recorded in the decision file).

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify` (CI run on the branch).

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- Existing tests (for example `test_unknown_route_outside_the_api_prefix_is_404_not_found`, `/health`) would get the entry page on a machine where `frontend/dist` exists, because the default folder is read when no setting is given. CI has no `dist`. Fixed in the QA fix round (QA finding M1, human-approved): an autouse fixture in `tests/conftest.py` sets `SOCBOARD_STATIC_DIR` to a missing folder.
- This sandbox could not run the Python tests; CI was the test loop.

## Follow-ups for the next session

Response security headers (a content security policy) remain out of scope; the human decides at the decision point.
