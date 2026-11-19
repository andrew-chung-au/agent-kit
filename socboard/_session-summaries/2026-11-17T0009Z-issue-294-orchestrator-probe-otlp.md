# Issue #294: the synthetic probe, the OTLP histogram

**Date:** 2026-11-17T00:09Z (UTC)
**Spec version:** e3461a7

## What changed and why

The DevOps session built the probe's HTTP side (3a3fe76, draft PR #342) and waited for #338 (the names) and #288 (the packages). Both merged. This session (Terraform lane A, asked by the maintainer on 2026-11-16 to take the next thing) added the rest on `issue-294-probe`, cut from that branch.

- `scripts/observability_probe.py`: `build_recorder(environ, reader=None)` returns the recorder and a shutdown. With `OTEL_EXPORTER_OTLP_ENDPOINT` set it creates a `MeterProvider` with the resource `service.name=socboard-probe` (passed in code, so it wins over `OTEL_SERVICE_NAME`; `OTEL_RESOURCE_ATTRIBUTES` still supplies the two operator-set attributes), the histogram `socboard.probe.time_to_queue` (unit `s`, the contract's bucket bounds through a view), and records each delay inside a sampled span context carrying the cycle's trace id, so the SDK keeps it as the exemplar. `main` flushes it in a `finally`. With the variable unset nothing is imported or created.
- `tests/test_observability_probe.py`: 9 new tests: the histogram value, bounds and exemplar trace id (in-memory reader); the resource against a conflicting environment; a case never seen recorded as 30 in the top bucket; a 429 recording nothing; two cycles; no endpoint means nothing created; shutdown after a failed run; no secret in the metric; and an end-to-end export to a fake OTLP collector on the loopback that decodes the request.
- `README.md`: the probe paragraph describes the histogram instead of "follows with #288 and #338".

**What I learned:** the SDK keeps an exemplar only when the measurement is taken inside a sampled span context; a bare `record(value)` has none.

## Reflection

unknown (role not asked)

## Launch usage

none

## Files created or modified

- `scripts/observability_probe.py`, `tests/test_observability_probe.py`, `README.md`
- `_docs/records/findings/294.json` (new), this file

## Decisions made by the human

- 2026-11-16: "work on the next thing to drive this forward", after #288 merged. #294 was chosen by this session; the claim comment says the maintainer can correct it.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify` (CI). In the sandbox: `pytest tests/test_observability_probe.py --noconftest` with the SDK 1.45.2 installed into `.scratch/` (deleted after): 44 passed on Python 3.11.

## Proposed AGENTS.md changes

none

## Temporary changes

A throwaway `pip install --target .scratch/otel` of the SDK, the exporter and the app's own dependencies, to run the probe's tests. Deleted.

## Interruptions

The DevOps session's claim stopped at the HTTP-side milestone; this session superseded it.

## Unrelated problems noticed but not fixed

- F-294-1: commit d75877e changes `socboard/smoke.py`, outside the issue's Files list.
- F-294-2: the claim comment was posted after the work began.
- F-294-3: the sandbox run was on Python 3.11, not 3.12.

## Follow-ups for the next session

- PR #342 (the old draft) is superseded by the new pull request; the maintainer closes it.
- The probe's use in the overlay and on dev: #301.
