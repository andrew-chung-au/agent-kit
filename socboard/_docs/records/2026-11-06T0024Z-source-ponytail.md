# Source: ponytail (agent skill)

One file per external input: a dataset, third-party API, vendor doc, standard or tool version.

- **Location:** https://github.com/DietrichGebert/ponytail (canonical repo; npm package `@dietrichgebert/ponytail`).
- **Version or date retrieved:** 5.3.3 (`package.json`), `main` at commit `96608e078b2d5ea607c5c3b8b5a54d1c1fba6846` (committed 2026-10-29). Retrieved 2026-11-06 through the GitHub API.
- **Why included or excluded:** Included as the subject of the trial in `_docs/decisions/2026-11-06T0024Z-ponytail-trial.md`. Only its skill files are to be vendored, at this pin. Its plugins are excluded.
- **Known quirks:**
  - *Read directly:* README, INSTALL.md, `docs/agent-portability.md`, `skills/ponytail/SKILL.md`, `.kiro/steering/ponytail.md`, `hooks/claude-codex-hooks.json`.
  - *Not read:* the `-audit`, `-debt`, `-gain` and `-help` skill files, the OpenCode plugin code, the Node hook scripts, and the benchmark method files.
  - *`ponytail-review`:* its description and opening sections were read, and its folder was checked: one self-contained file with no references to other files. Its description matches requests such as "code review", so, like the core skill, it must not sit in a folder tools discover while control issues run.
  - *Benchmark figures* (roughly half the code, more risky logic tested) are the vendor's own, from Claude Code on one model family. They are unverified here and not assumed to transfer.
  - *Auto-trigger:* the core skill's description invites loading on any coding task. We vendor it verbatim, so scoping relies on our own rule, not on editing the file.
  - *Kiro:* upstream ships an always-on steering file with no commands or levels. We use a skill, or manual-inclusion steering as a fallback.
  - *Plugins:* the Claude Code and Codex forms run Node lifecycle hooks, including one that injects into subagents. The OpenCode form injects its rules every turn. The Claude Code "band" keeps data under the user's home config. None is used.
  - *Lookalikes:* several forks and copies exist with different claims. The README says to install only from the canonical repo or npm package.
- **Licence:** MIT.
- **Vendored copy (issue #23, 2026-11-10):** `skills/ponytail-review/SKILL.md` at the pinned commit is held verbatim as `_docs/vendor/ponytail/ponytail-review.md` (git blob `a50e3ac6ded6fccc9edae34ce37877bbce11e3fa`, 5143 bytes, sha256 `33fe4ebe22a460924e5d4a261e223df22e409cc94ab76182bee9fb91a3ef022e`). The upstream licence at the same commit is `_docs/vendor/ponytail/LICENSE` (git blob `715d483338cea4365f0d91a27799cf61226d6bcf`, 1071 bytes, sha256 `fb1bc6909ac3ef82d5c22106e32ef682b0cff66788fa915fb9b53b15c9d2f3ab`). Both were fetched with `gh api` raw content at the pin; recompute the blob hash with `git hash-object <file>` to check. The folder holds `SKILL.md` alone, so nothing else is vendored. The file was read in full and refers to no other file.
- **Vendored copy (2026-11-12, `_docs/decisions/2026-11-12T2300Z-ponytail-adopt.md`):** `skills/ponytail/SKILL.md` at the same pinned commit is held verbatim as `_docs/vendor/ponytail/ponytail.md` (git blob `d64edd32265ba21cbf5270158f04e97d96925f27`, 3496 bytes, sha256 `9badd22a32e19cb884e46dfa8d3aae82bb81dfa5484105b8b4f0262df823a509`). It was fetched with `gh api` at the pin, and its blob id matched the upstream folder listing. The folder holds `SKILL.md` alone. The file was read in full: it is guidance text, runs nothing and refers to no other file. It is loaded by path by the Engineer, never from a folder a tool discovers.
