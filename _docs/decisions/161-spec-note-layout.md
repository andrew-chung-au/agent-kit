# Decision: a fixed layout for spec notes

Issue #161 (Heavy). The human approved this record in a comment on #161 (body sha256 `05ccfbe9f379f4e0ec7ea67c7b6187184ecb425ec5e97d27fd4e68799b6ac30f`), copied here from the issue body.

- **Decision:** Define one "Spec note" layout in `procedures/asking-the-human.md`, the file that holds the kit's other ask layouts: a line each for Added (the requirement), Changed (the new text, with "was:" and the old text) and Removed (the requirement, with a reason), plus a one-line Why. It is optional for a one-line note. `team/pm.md`, `team/software-engineer.md` and the decision-point step in `process.md` link to it instead of restating it. `process.md` Planning states that nothing is merged into `_docs/specs.md` automatically: the human approves, then the change is committed on its own, as it is today. The approval flow and spec ownership do not change. A spec note that edits `_docs/specs.md` directly is refused by the protected-file rule and the commit approval that already cover that file.
- **Reason:** Spec notes are free text, so a reviewer cannot see at a glance what is new, changed or removed. OpenSpec's delta specs show a better layout; only the layout is worth borrowing, because its automatic merge on archive conflicts with the human-owned spec (research in #14).
- **Alternatives:**
  - Copy OpenSpec's archive and merge step: rejected, it would change spec ownership.
  - Put the layout in each role file: rejected, it would drift.
  - Leave spec notes as free text: rejected, that is the gap.
- **Trade-offs:**
  - A little more writing for the role that raises the note; the layout is optional for small notes.
  - An optional layout may be ignored; the human can ask for it.
  - `asking-the-human.md` grows a little.
- **Evidence:** #161; `_docs/records/2026-11-06T0330Z-measure-spec-driven-frameworks.md`; `process.md` Planning.
