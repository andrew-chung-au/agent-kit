# Decision: find a kit's baseline with a read-only search, and make its manifest by hand

Issue #169 (Heavy). The human approved this record in a comment on #169 (body sha256 `0927eee4d789767240fa0ad1ac4d8eb48ac0f9f7a19fb3ca5efc7613f705b503`), copied here from the issue body.

- **Decision:** When a live kit has no manifest, the import finds its baseline with a read-only script, `scripts/kit-baseline.py` (run as `make kit-baseline KIT=<live kit folder> SOURCE=<clone of the kit repository>`), and produces the baseline manifest by hand. The script compares each live kit file's path and content with the `agent-kit/` history of a clone of this repository and lists up to three candidate commits with match counts and the differing files. It names a baseline only when one commit matches at least three quarters of the live files and no different tree ties; otherwise the human decides from the candidates. The human approves the chosen commit before step 4 uses it. The manifest is then made from a `git archive` export of that commit with the existing `scripts/kit-manifest.py`, written under `.scratch/`, never into the live kit folder, and step 4 classifies with `make kit-compare` against that export. The script writes nothing and never prints a commit message.
- **Reason:** Step 2 of `kit-import.md` stops when the live kit has no manifest and says nothing about how to find a baseline. Every project that took the kit before 1.10 is in that state, and without a baseline step 4 cannot tell a deliberate local change from an old file, so a guess could overwrite a local change. A match by content against history is checkable: the human sees the count and the differing files before approving.
- **Alternatives:**
  - Manual commands only, no script: rejected, a search over hundreds of commits by hand is slow and each person would pick differently.
  - A script that also exports the commit and writes the manifest: rejected, it adds a writing script to the import path; the existing generator and `git archive` already do it.
  - The human names the commit: rejected as the only path, the human may not know it, but it stays possible when the script finds no clear best.
  - Match on the README version line or dates: rejected, the SOCBoard kit says 1.9 but is a later snapshot.
  - Pick the best match silently: rejected, a wrong baseline can overwrite a deliberate local change.
- **Trade-offs:**
  - It needs a clone of the kit's repository in the project's `.scratch/`; the human makes it.
  - The three-quarters threshold is a judgment call; below it, or on a tie, the human decides.
  - File modes are ignored in the match, because a copy or unzip may drop them.
  - It looks at the last 2000 commits that changed `agent-kit/`.
  - New make target and script to ship; `kit-import.md` grows by about 185 words, so its word limit in two tests rises from 713 to 900.
- **Evidence:** #169; PR #179; SOCBoard case in this issue's Why section (79 of 85 files identical to `72747a1`); `agent-kit/procedures/kit-import.md`.
