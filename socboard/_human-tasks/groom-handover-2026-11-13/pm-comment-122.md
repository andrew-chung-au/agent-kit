PM: re-read #122 against `main` at 8d2ee9e. I kept the drafted body and changed only what was wrong or open (the body to apply is `.scratch/groomed-122.md`; the hash below is of those exact bytes). The body keeps its `## Decision record` section; the Engineer does not start until the human has approved it, and `approved` should name that section.

Proposed tier: heavy
Reason: it changes the rule that gates every issue's closure (the process itself).
Expected paths: `_docs/agent-kit/scripts/issue-close.sh`, `_docs/agent-kit/procedures/session-summary.md` (both protected by `_docs/agent-kit/*`; the human approves each exact diff and commits with `HUMAN_APPROVED=1`), `_docs/decisions/<new record>.md` and the old record's status line, `_docs/index.md`, and the regression test file once the human approves its place in `tests/`. `LIGHT_ALLOWED` is empty, so nothing is Light.
Spec-ready confirmation: not required (this grooms an existing issue; no backlog is built).

Checked and still true on `main`: the script's rule is where the body says (`issue-close.sh` header and `is_reflection`); the Light path, the not-planned path and the `QA PASS commit` line exist as described; the old record and its `_docs/index.md` row exist; `session-summary.md` Reflection says what the body quotes; every comment id the body cites exists on the issue it names (#63 Reviewer report 6846010929, QA 6845523068 and 6845882757, #51, #16, #99, #17, #18, #14, #13, #46) and #99 and #14 each have their own `Reflection:` block. No decision record approved after the issue was filed (2026-11-13T06:42Z) contradicts a criterion. The body has no dangling reference to a `.scratch/` file (the two mentions describe checks, not files).

What I changed in the body:
- Resolved your question 3 by looking: the kit keeps no single list of local deviations. A deviation is a `<!-- local deviation: <record> -->` pointer in the changed kit file (`process.md:133`, `blueprints.md:149`, `issue-close.sh`) plus its decision record in `_docs/index.md`; `make kit-check` shows the drift. The criterion now says that. The body's "possibly `MANIFEST.sha256` and `KIT_VERSION`" is replaced: the manifest is not edited (a derivative keeps the upstream one, `kit-import.md`), and `KIT_VERSION` stays `1.10+socboard.1` as #63 left it unless the human asks for a bump (`README.md` says the `<n>` rises with each local change; #63 did not).
- Question 1 and question 2 are left as marked questions in the body (`OPEN QUESTION 1`, `OPEN QUESTION 2`), plus two "(open question 1)" pointers.

Decision needed: question 1, the extra limit on the Reflection block (criterion 4).
- Context: the limit (three lines, 150 words, "small margin") contradicts the Accepted cases. The real #51 reflection (6792494473) has 10 non-empty lines and 293 words; the real #16 reflection (6843134115) has 7 and 222. A three-line, 150-word rule refuses both. Length does not separate them from work either: the real work comments #17 and #18 are 1,133 and 1,560 characters, the reflections 1,870 and 1,492.
- Options:
  1. Drop the limit. The shape test is then: at most one short line before `Reflection:`, no commit named there. Remaining gap: work written after a `Reflection:` line is read as a reflection. Add it to the record's trade-offs.
  2. Keep a limit sized from the real reflections (for example 400 words): it still blocks nothing in the real work comments, so it is cosmetic.
  3. Require the block to have the three numbered items that `session-summary.md` asks for: closer to a shape test, but I have not checked it against the real reflections and it would refuse any that do not number them.
- Recommendation: 1, because no length can separate the two groups on the evidence, and the deliberate-evasion case is out of reach of a script that reads text.
- If you don't answer: the issue is not ready to approve; the Engineer must not implement criterion 4.

Decision needed: question 2, if no `tests/` file is approved, is the `.scratch/` check acceptable (last Regression test criterion)?
- Context: `tests/` is a separate approval, and the human has said not to touch it for now. Without a committed test, a kit import can silently reopen the hole (finding 7).
- Options: 1. Accept the `.scratch/` run as the proof and mark the criterion not met. 2. Hold the issue until a `tests/` place is approved (the likely place is a new file by the `tests/test_ponytail_metrics.py` precedent). 3. Approve the `tests/` place now, in the same sitting as this issue.
- Recommendation: 3. It is one new file and no `Makefile` change.
- If you don't answer: the issue is not ready to approve.

Residual questions: the two above. Spec notes: none.

Body sha256: 78dec8119b48d15ca9fbf97a261fd42f93fc23fe7b4213e5f0dccdb70d31b782
