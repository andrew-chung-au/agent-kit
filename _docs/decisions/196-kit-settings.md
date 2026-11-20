# Decision: kit settings, profiles and numbered acceptance criteria

Issue #196 (Heavy). The human confirmed this record with the groomed body in this session (2026-11-20; body sha256 `1f3b887081468677c3a09ac6a5872f15ea94506fa27a9a3d54307a36aba9fa93`, Orchestrator Confirm comment on #196). Copied here from the issue body's `## Decision record`; it holds two decisions.

## Kit settings live in `agent-kit.conf`, read as text by `scripts/settings.py`, with profiles

- **Decision:** Every kit setting has one kit default (or one per profile for `GROOM_AHEAD`, `LANES`, `DELIVERY_LEAD`, `STATUS_EVERY`) held in one table in `agent-kit/scripts/settings.py`. A project changes a value with one `NAME=value` line in `agent-kit.conf`, and can pick a profile with `PROFILE=solo|team|fleet`. Resolution order: kit default, profile, project line; a written line always beats the profile. The reader parses the conf as text, accepts only the allowed values, refuses unknown names, duplicates and malformed lines with the line number, and ignores the environment. `make settings` shows each value and its source. `customizing.md` documents the settings and the grade vocabulary.
- **Reason:** most of socboard's kit edits changed a value, not a rule (proposal 2.1, section 1); one line in the already-protected conf replaces a fork of the kit's text. Reading as text follows `GITHUB_REPO` (`_docs/decisions/172-github-repo-source.md`): no code runs from the file through this reader, and a typo is refused rather than silently ignored.
- **Alternatives:**
  - Read the values by sourcing the conf in bash (as `scripts/lib.sh` does for the older lines): rejected, it runs whatever the file holds and can't refuse a misspelt name.
  - A separate settings file (JSON or another format): rejected, a second place for project settings next to `agent-kit.conf`, which would also need protecting.
  - Environment variables: rejected, an agent or tool setting can change them unseen and no diff shows it.
  - Keep values in the kit's prose and let projects edit it: the status quo, which is the fork problem.
  - No profiles, only single settings: rejected by the human's 2026-11-19 decision; profiles switch the usage shape at once without losing the project's own lines.
- **Trade-offs:**
  - The conf now has two readers: `lib.sh` still sources it for the older lines, so the setting lines must stay plain tokens that mean the same in `bash`, and a command substitution anywhere in the conf still runs at `make verify` and in the pre-commit hook (the file is protected, so only the human commits it).
  - Unknown names are refused, so a project that put its own variables in `agent-kit.conf` sees `make settings` refuse until they are moved; later scripts that use the reader will refuse too.
  - Sixteen settings are documented before most of them act; `customizing.md` names the issue that wires each, and until then a written value has no effect.
  - Validating `SHIP_RULE`'s grammar now fixes a form #199 will give meaning to; #199 may change it.
- **Evidence:** #196; proposal `_docs/planning/kit-1.11/workflow-review.md` sections 1, 2.1, 2.8, 3.3, 4.0 to 4.3, 4.5 and 12; `_docs/decisions/172-github-repo-source.md`; `agent-kit/scripts/lib.sh` (sources the conf); `agent-kit/scripts/github_api.py` (reads `GITHUB_REPO` as text).

## Acceptance criteria are numbered `C<n>`, each with a `Check:` line

- **Decision:** the task template writes each criterion as `- [ ] C<n>. <statement>` with an indented `Check:` line saying how it is verified (a command, a test name, or a reading of a named file). Ids start at `C1`; after approval a criterion keeps its id. The PM's definition of done requires both; the human's reading before `approved` enforces it.
- **Reason:** findings, the Engineer's checklist and criterion-level `Needs:` (#198, #199, #201, #209) need to name one criterion; a `Check:` line written at grooming turns Engineer-QA disagreements into wording fixes before the build (proposal 3.3).
- **Alternatives:** unnumbered checkboxes (today; nothing can point at one criterion); numbering without `Check:` lines (the disagreement about how to verify stays until QA); a script that checks every issue body (more code; not needed while the PM and the human read each groomed body).
- **Trade-offs:** every groomed issue gets longer by one line per criterion; ids with gaps after edits are allowed, so ids are not always contiguous; nothing mechanical refuses a malformed body.
- **Evidence:** #196; proposal section 3.3; `_docs/planning/kit-1.11/issues/filed.md` (all 21 filed bodies already use the format).
