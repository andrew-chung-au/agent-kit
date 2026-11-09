# Decision: split the kit docs by purpose, one home per fact

Issue #182 (Heavy, proposed). The human approved the recommendations in `_docs/planning/182-target-structure.md` in the session on 2026-11-09. This record was written from that approval; it was not copied from a hashed issue body, so the Heavy gate in `process.md` (an ADR in the issue body, approved by hash) was not followed to the letter. The human should confirm it.

- **Decision:** Each kit doc has one stated purpose and reader. `README.md` is the overview and a which-file index. `install-and-upgrade.md` is the only home for install and upgrade steps. `releasing.md` holds the release steps. `CHANGELOG.md` holds the per-version notes. `environments.md` keeps the profiles and the sandbox rules; `environments/local-sandbox/README.md` holds the one-time sandbox setup and reference. Intended copies have a named source and a test that fails when they drift (`tests/test_intended_copies.py`).
- **Reason:** The README did eight jobs and `environments.md` four. The same install and upgrade facts lived in three files and drifted. A reader had to cross-read three files to answer one question (see #181).
- **Alternatives:**
  - Keep one big README and add an index only: rejected, the length and the duplicates stay.
  - Put the changelog at the repo root: rejected, it would not travel with the kit.
  - Keep release steps as a situation in the install guide: rejected, it mixes the maintainer with adopters.
  - Check the role-file copies in this repo against their sources: not done, they are tailored copies that differ today.
- **Trade-offs:**
  - `CHANGELOG.md` and `releasing.md` are kit files, so they are hashed in `MANIFEST.sha256` at the next release.
  - Section names and anchors moved. Tests and the root `README.md` links were updated; any outside link to an old anchor breaks.
  - Two new files and a new folder README to maintain.
- **Evidence:** #182; #181 and PR #183; `_docs/records/2026-11-09T1325Z-measure-kit-docs-inventory.md`; `_docs/planning/182-target-structure.md`.
