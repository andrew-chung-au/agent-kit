# Decision: split the kit docs by purpose, one home per fact

Issue #182 (Heavy). The human approved the recommendations in `_docs/planning/182-target-structure.md` in the session on 2026-11-09 and confirmed this record in that session. It was not copied from a hashed issue body, so the Heavy gate in `process.md` (an ADR in the issue body, approved by hash) was met by the human's confirmation in chat, not by hash.

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

## Amendment after QA (2026-11-10)

QA found five of the eleven multi-home facts still stated in more than one doc, stale pointers to deleted README sections, and install steps in three places. The resulting changes, and the homes they settle:

- **Install:** `install-and-upgrade.md` only. The root `README.md` "Install and quick start" now links to it (the Path 1 and Path 2 steps are gone); the by-hand setup moved from `environments/local-sandbox/README.md` into situation 1 there.
- **Bootstrap script:** the script header says what it does, `install-and-upgrade.md` says how to run it. The sandbox README no longer repeats the command or the description.
- **Installed-file report lines:** `README.md` "Installed files" explains them; `procedures/kit-import.md` step 7, `setup.md` and the root README point there. Step 7 keeps the agent rules (no agent copies an installed file; a rejected map entry stops the step).
- **Version scheme:** `README.md` "Updating the kit" owns the `<base>+<repo>.<n>` numbering. This differs from the first plan, which named `procedures/kit-import.md`; the README is pinned by `tests/test_kit_manifest.py` and `kit-import.md` has a word budget. `kit-import.md` keeps only how to set the claim at an import.
- **Who closes issues:** unchanged. `AGENTS.md` keeps the sentence as an intended copy of `process.md` step 9, and `tests/test_approval_freeze.py` fails if the two differ.
- **Stale pointers:** `CHANGELOG.md` and `blueprints.md` no longer name the deleted README upgrade section.
- **Defects found alongside:** `_docs/agent-kit/...` paths in the sandbox README commands; `AGENT_PUSH_CHECK_PLAN=1` was called a dry run but lets the push through unchecked, so the docs now use `git push --dry-run` with it; the stale "89 files for 1.10" count.
