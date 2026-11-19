# Kit docs: proposed target structure (issue #182, step 2)

**Date:** 2026-11-09. **Status:** proposal for the human to review. No text has been moved. Evidence: `_docs/records/2026-11-09T1325Z-measure-kit-docs-inventory.md`.

## Principles

1. One purpose per file, stated in its first two lines, with its reader (human, agent or script).
2. One home per fact. Other files link to it with a section anchor. They do not restate it.
3. An intended copy names its source and has a check that fails when they differ.
4. Move text in small steps, one intent each, with `make test` green after each.

## Proposed files

| File | Purpose | Reader | Change |
|---|---|---|---|
| `README.md` | What the kit is, how the controls work, and a "which file answers which question" index. Target about 1,500 words. | H | Shrinks from 5,826. Loses install, upgrade, release and changelog sections, keeping a signpost to each. |
| `install-and-upgrade.md` | The walkthroughs: install, upgrade, dev container upgrade, per situation, with prompts and expected output. | H | Already exists (#181). Becomes the only home. README "Adding the kit" and "Upgrading a project" and `environments.md` "Upgrading the kit in the local sandbox" go; links point here. |
| `releasing.md` (new) | Cutting a release: tag, archive, manifest, zip. Versions, `MANIFEST.sha256`, installed files in a release. Human only. | H (maintainer) | Takes situation 9 of the walkthrough and README "Cutting a release", "Versions in a project" and "Installed files in a release". The walkthrough keeps one line linking to it. |
| `CHANGELOG.md` (new) | What changed per version, and what an existing project must do. | H | Takes README "Changes in 1.6" to "1.10" (about 2,700 words), unchanged in wording at first. |
| `environments.md` | The three profiles and why the local sandbox rules exist. | H | Shrinks from 3,348. Keeps the profile table and "Rules for the local sandbox". Loses the upgrade steps. |
| `environments/local-sandbox/README.md` (new) | One-time sandbox setup reference: the bootstrap script, the recipe files and pins, the token, the push-check image, the Compose variant, the WSL 2 mount fix, comparing the installed push check. | H | Takes those sections from `environments.md`. Sits beside the files it describes. |
| `process.md`, `setup.md`, `blueprints.md`, `procedures/*`, `team/*`, tool layers | Unchanged purposes. | A | No move. Add a two-line purpose and reader at the top where one is missing. |

## The index (goes in `README.md`)

A table of "I want to ... | open | reader", for example: install the kit -> `install-and-upgrade.md`; upgrade the kit -> `install-and-upgrade.md`; see what changed -> `CHANGELOG.md`; cut a release -> `releasing.md`; understand where agents run -> `environments.md`; set up the sandbox by hand -> `environments/local-sandbox/README.md`; set up a project (agent) -> `setup.md`; how work flows (agent) -> `process.md`; review a newer kit (agent) -> `procedures/kit-import.md`.

## One home per fact

The facts table in the inventory lists eleven facts with more than one home. The target homes are in that table. In short: walkthroughs in `install-and-upgrade.md`, release steps in `releasing.md`, per-version notes in `CHANGELOG.md`, classification and version-claim rules in `procedures/kit-import.md`, the "who closes issues" rule in `process.md`.

## Intended copies: source and check

| Copy | Source | Proposed check |
|---|---|---|
| `AGENTS.md` shared block | `templates/AGENTS.md.template` | A test that the text between `SHARED START` and `SHARED END` equals the template's. Needs a decision on what the "from" line says, since it differs. |
| `.claude/agents/*`, `.opencode/agents/*` in this repo | `claude-code/agents/*`, `opencode/agents/*` | `make kit-check` already does this in a project; add a test for this repo, or accept the difference with a named reason. |
| `.github/pull_request_template.md`, `_docs/index.md`, `CLAUDE.md` | Their templates | A byte-for-byte test for the PR template; the other two are tailored, so name the source in a comment only. |

## Order of changes (each its own commit and test run)

0. **Decide the order with #181.** Recommend: merge #181 first (PR 183), then do this. It already adds `install-and-upgrade.md`, so no walkthrough is written twice.
1. Add `CHANGELOG.md` with the 1.6 to 1.10 text moved from the README; README links to it. Update `tests` that read the README changelog.
2. Add `releasing.md`; remove the release text from the README and the walkthrough; update links.
3. Remove README "Adding the kit" and "Upgrading a project" in favour of links to `install-and-upgrade.md`; remove the sandbox upgrade steps from `environments.md`.
4. Move the one-time setup sections of `environments.md` to `environments/local-sandbox/README.md`.
5. Add the index to the README and the two-line purpose headers.
6. Add the drift checks for the intended copies.

Each step touches protected paths, so each needs your approval to commit. Steps 1 to 4 each change which test files read which doc; the inventory counts about 30 test files that read these docs, so expect test edits in every step.

## Decisions for the human

1. **Order with #181.** Merge #181 first (recommended), or stack this on it.
2. **Where the changelog goes:** `agent-kit/CHANGELOG.md` inside the kit (recommended; it travels with the kit but is then hashed in `MANIFEST.sha256`), or the repo root.
3. **Split `environments.md`:** the new `environments/local-sandbox/README.md` (recommended), or keep one file and only remove the upgrade steps.
4. **Separate `releasing.md`**, or keep release steps in `install-and-upgrade.md` as situation 9 (simpler, but mixes maintainers with adopters).
5. **Tier.** By `make tier-check` this is many protected paths. I propose Heavy for the moves in steps 1 to 4 (an ADR first, per `process.md`), and Standard for steps 5 and 6.
6. **Version bump.** The moves change `README.md`, so a README version bump and changelog line are a human decision at cut time.

## Not decided here

The wording of any moved text. Steps 1 to 4 move text as is.
