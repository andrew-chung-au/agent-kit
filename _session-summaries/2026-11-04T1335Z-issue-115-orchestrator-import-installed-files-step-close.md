# Issue #115: Add an installed-files step to the forward kit import (#91 piece c)

**Date:** 2026-11-04T13:35Z (UTC)
**Spec version:** none

## What changed and why

#115 adds step 7, "Installed files", to `agent-kit/procedures/kit-import.md`: `make kit-check` reads `installed-files.txt` through the shared scan (read-only), reports each `repo` file as `unchanged`, `local, ignored`, `drift` or `missing <path>`, only names `human-machine` entries (the human compares them from the clean clone), and no agent copies an installed file. Tests in `tests/test_kit_import_doc.py` pin the step's wording and check that it names no write command.

Built by Kiro as the Engineer. An earlier head (`49f0999`) failed QA because it trimmed unrelated lines of `kit-import.md` to stay under the 600-word cap. Kiro restored the original text, added the step and raised the cap from 600 to 713 in `tests/test_kit_import_doc.py` and in `tests/test_kit_compare.py`, which caps the same doc (713 equals the doc's actual word count, so the next edit to it needs another raise). Head `ecd499b`, one commit, was force-pushed after a rebase. The old PR #137 sat on a stale base and was closed unmerged; PR #146 (same branch, base `main`) merged at 2026-11-04T13:20Z as `109dc22`. I confirmed `ecd499b` is an ancestor of `origin/main`.

**What I learned:** a closed-then-reopened PR against `main` was the clean way out of a stale stacked base; I had warned about the base early but only after #138 had stranded.

## Reflection

unknown (role not asked).

## Launch usage

- QA launch 1: about 6.5 min (389,670 ms), 19 tool uses; asked again to post its comment: about 7 min (427,079 ms), 22 tool uses.
- QA launch 2: about 4 min (240,397 ms), 29 tool uses.
- Earlier launches for #115 and Kiro's work are not counted here.

## Files created or modified

`agent-kit/procedures/kit-import.md` (+1 line), `tests/test_kit_import_doc.py`, `tests/test_kit_compare.py` (PR #146). This record is the only file added now.

## Decisions made by the human

- Ruled on the cap raise (Kiro: 600 to 713, nothing trimmed), per my recommendation; approved Kiro's protected-path commit in the Kiro session (recorded there, not in this session).
- Replaced PR #137 with #146 against `main`, and merged it.
- Left the tier label off #115, so the close gate treated it as Standard; two fresh QA launches passed anyway.

## Mismatches with the spec or design docs

none known.

## Commands to validate

**Verify:** QA's `make verify` on the merged tree passed in both launches: 1331 tests, no weakened tests; `make assert-clean` PASS. `make kit-check` could not be run for real because this repo ships no `MANIFEST.sha256`; QA checked step 7's claims against `kit-check.py` and the existing tests.

## Proposed AGENTS.md changes

none.

## Temporary changes

none.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- The write-verb test is a blacklist: it would not catch `CP` in uppercase, `python3 -c ...write`, `git apply`, `curl -o`, `rm`, `touch`, `truncate` or `chmod`. QA ruled the criteria do not require closing these (the step names only the read-only `make kit-check`).
- The test comment says step 7 is 113 words; QA counts 112. Cosmetic.
- QA used `sed -i` once on its own `.scratch` script, against the no-shell-edit rule; nothing outside `.scratch/` was touched.
- No make target builds a throwaway kit with a manifest, so QA cannot run `make kit-check` end to end here.

## Follow-ups for the next session

None for #115. #145 (README rewrite, PR #147) is in QA and may state claims that depend on this step.
