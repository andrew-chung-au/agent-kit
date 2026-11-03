# Issue #233: P-DEMO-BE, the full stub loop in Compose, run twice (task 28c-C of #160)

**Date:** 2026-10-26
**Spec version:** 76c73f7

## What changed and why

The Engineer wrote the `P-DEMO-BE` case on the existing containerized harness. The session has the Docker CLI but no Docker daemon, so the case is WRITTEN AND STATICALLY CHECKED ONLY. No [D] criterion has been observed passing.

- **VERIFY 1 (fixture).** No committed fixture produced a top-tier finding with no fixed version: every OSV advisory has a `fixed` event, so pygoat's urllib3 finding has fixed version 1.26.17 and the demo defect (which needs `fixed_version is None`) never fires. The Engineer stopped and returned the question. The owner chose option (a): one project-authored advisory (`GHSA-fixture-nofix-0001`, invented alias `CVE-2099-0001`, open-ended range, flask), one `querybatch.json` entry (`PyPI|flask|2.3.3`, a version `fixture-owner/pip-app` already pins) and one invented KEV row. An exposed `pip-app` asset ranks P1 with no fixed version. MANIFEST rows added (project-authored, not recordings). `make backend-test` before and after: the 532 existing cases are unchanged; `make demo` registers four other repositories and the pygoat journey asserts nothing about flask, and a new test shows the pygoat scan is unchanged.
- **VERIFY 2 (seam).** `seed_overdue_job` (`alert-seed`) always creates a NEW finding, so it cannot re-seed an existing finding id. `alert-set` (`set_alert_job`) flips every top-tier job of an existing finding to a state, so take 2 uses it through a new wrapper `compose_alert.set_job_state`. `DeliveryWorker.deliver_pending` selects `pending` and `failed` jobs and never reads `owner_notified_at`, so a re-failed job on a lifecycle that was already notified is retried and (with the defect on) fails again.
- **VERIFY 3 (resolved).** `us14-overdue.yaml` sets no `disableResolveMessage` on the webhook receiver, so Grafana's default (send resolved) should apply. That is read from the provisioning only; the case asserts the `alert_ignored`/`resolved` line at the responder, prints the VERIFY result, and on a timeout fails with a message pointing to the #220 comment 6410222531 fallback.
- **The case.** `tests/test_compose_demo_be.py` (compose-marked, deselected by `make test`) runs take 1 step by step from real sinks, the refused case (duplicate firing, right bearer, ignored as `repeat`), the harness fix (recreate the backend with `VT_DEMO_DEFECT` unset), the owner mail, metric 0 and the `resolved` notification, then take 2 on the same finding id with the guard record read from the container between takes. Each step is a bounded `_poll` with a named timeout. The docstring states the stub proves wiring only and the harness applies the fix.
- **Harness.** `compose_responder.recreate_backend` (up -d --force-recreate --no-deps --wait backend with the variable removed from or set in the subprocess environment), `backend_demo_defect`, `message_subject`; `ci/test-compose.sh` `run_responder` seeds the security-lead user and runs both test files in one pytest call. No second harness, no new image, no `.github/` change.

## Files created or modified

- Fixtures: `tests/fixtures/osv/vulns/GHSA-fixture-nofix-0001.json`, `tests/fixtures/osv/querybatch.json`, `tests/fixtures/kev/known_exploited_vulnerabilities.json`, `tests/fixtures/MANIFEST.md`.
- Tests and harness: `tests/test_fixture_nofix_finding.py`, `tests/test_compose_demo_be.py`, `tests/test_compose_demo_be_static.py`, `tests/compose_alert.py`, `tests/compose_responder.py`, `tests/test_marker_hygiene.py` (one allowlist entry, as that guard's message prescribes), `ci/test-compose.sh`.
- Docs: `_docs/roadmap.md`, `_docs/ai-usage-log.md`, this summary.
- Commits: `48c79a8` (fixture), `901a37f` (case and harness), and the docs commit.

## Decisions made by the human

- Question 1 (no fixture gave a no-fixed-version top-tier finding): the owner chose (a), a project-authored fixture, with these limits: smallest possible, MANIFEST row, existing tests unchanged, take 2 through `alert-set`.

## Mismatches with the spec or design docs

none.

## Commands to validate

- **Verify:** `make verify` (PASS WITH WARNINGS: fixtures changed, nothing loosened; frontend 89, backend 542, responder 85).
- **Compose responder job (owner's Docker host, NOT run by the agent):** `make test-compose JOB=responder`. Record the result and the measured duration of the whole job (about 8 to 10 minutes per take expected) in the PR description, for #161's `timeout-minutes`. The agent cannot measure it.

## Proposed AGENTS.md changes

none.

## Temporary changes

- `.scratch/collect_compose.sh` (read-only collection script) and `.scratch/issue-*.json` dumps; git-ignored. No processes started; no system configuration changed.

## Permission review

- Read-only (propose allowing): `bash .scratch/collect_compose.sh` (a `pytest --collect-only` of the compose-marked cases; starts no container, writes pycache only; no matched `ask` rule recorded).
- Writes to the record (keep asking): `make issue-comment N=233` (the Engineer comment); `git commit` of the three commits on the session branch.
- Risky (propose denying): none.

## Interruptions

- The Engineer stopped at VERIFY 1 and handed a question back; the owner answered (a) and the work resumed. Nothing was left half-done.

## Unrelated problems noticed but not fixed

Unverified risks in the written case (found while writing it; none can be checked without Docker):
- Recreating the backend makes the metric briefly absent; the Prometheus exporter keeps the last value for the collector's default expiry, and the rule's `noDataState: Alerting` could send a NoData human email to the human address. The case counts only FIRING-subject emails to the human address, but a NoData FIRING email would break "exactly one". Watch the first run.
- Grafana's default email subject is assumed to contain `FIRING`/`RESOLVED`.
- After a resolved notification the Alertmanager group must notify the next firing of the same finding inside `group_interval` (1 minute); the case allows 300 s for take 2's firing and 480 s for `resolved`.
- `docker compose up --wait` with `--no-deps` on a recreated backend is assumed to republish port 8000 and keep the responder's DNS name `backend` valid.

## Follow-ups for the next session

- The owner runs `make test-compose JOB=responder`, records the pass and the measured duration in the PR, and closes #233 only on a green recorded run; QA review of the written case is still due.
