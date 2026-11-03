# Issue #144 (task 22): Pilot seed data registered through the API

**Date:** 2026-10-25
**Branch:** `feat/144-pilot-seed`

## What changed and why

Task 22 of Milestone B: register the pilot assets so real findings appear on the
dev environment. They are registered **through `POST /assets`** (US-1), never by
writing to the database — so the dashboard, scan worker and audit trail all run
the real path. No overlap with #159 (the alert Compose job): this adds only a
seed data file and a client script plus docs, and changes **no** registration or
scan code (out of scope per the issue).

## Files

- `deploy/pilot-seed.json` — the committed seed list (A38 "lives in the repo as
  a data file"). Entries are `NewAssetInput` bodies. Ships `REPLACE_ME`
  placeholders for the human's own repositories (the human supplies the exact
  URLs), an OWASP Juice Shop entry, and a NodeGoat **A41 fallback** entry carrying
  `_use_only_if_juice_shop_has_no_package_lock` (the script skips it until the
  flag is removed). A leading `_comment` explains the VERIFY and the fill-in.
- `deploy/seed-pilot.py` — a stdlib-only (urllib) client that logs in
  (`POST /auth/login`), then `POST /assets` for each entry with the session
  cookie and the `X-Requested-With` CSRF header, mirroring the proven pattern in
  `tests/compose_telemetry.py`. It:
  - reads the password from `VT_SEED_PASSWORD` or a prompt — **never** a CLI arg
    (same rule as the operator create-user command);
  - supports `--base-url`, `--username`, `--seed-file`, `--insecure`;
  - refuses a `REPLACE_ME` repositoryUrl and reports a `403` as "not a security
    lead"; skips flagged fallback entries;
  - never writes to the database and emits no telemetry (A38: repository URLs
    stay out of telemetry — it is a plain API client).

## Documentation

- `_docs/aws-setup.md` — new "Pilot seed data (task 22)" section: fill the seed
  list, the Juice Shop VERIFY / A41 fallback, run the script against the dev URL
  as a `security lead`, and the acceptance check (scan status + ≥1 finding).
- `_docs/human-tasklist.md` — added A13 (register the pilot seed → closes #144);
  removed #144 from §E "Later".

## Acceptance criteria mapping

- Seed list data file with the human's repos + Juice Shop (A41 fallback) ✅
  (`deploy/pilot-seed.json`)
- Registered through `POST /assets`, never the database ✅ (`seed-pilot.py` is an
  API client only)
- Repository URLs never enter telemetry (A38) ✅ (plain client, no OTEL)
- Out of scope: no registration/scan code change ✅ (none touched)
- Check: each asset shows a scan status and ≥1 finding on dev → **human
  verifies** after running the script against the dev environment
  (`aws-setup.md` "Pilot seed data").
- `make verify` ✅ (only a JSON data file, a standalone script and docs; no
  test, backend or frontend code. The backend suite could not run in this
  sandbox — no PyPI network — but whitespace and weakened-test gates pass, no
  test file changed; `pilot-seed.json` parses, `seed-pilot.py` compiles, and it
  was exercised end-to-end against a stub backend: 2 registered + 1 fallback
  skipped on the happy path, 401 on a wrong password, and the REPLACE_ME guard
  firing.)

## VERIFY (by the human, before/at the run)

- **Juice Shop lockfile (A41):** confirm `juice-shop/juice-shop` commits a
  supported `package-lock.json`; if not, use the NodeGoat fallback entry.
- Sign in as a real `security lead` (needs the operator create-user command,
  #176, which creates dashboard users).
- The exact pilot repository URLs are the human's to provide (issue constraint).
