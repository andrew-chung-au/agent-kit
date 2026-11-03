# Planning: spec review issues #3-#8 (roadmap step 6)

**Date:** 2026-10-20
**Spec version:** fdc7b51

## What changed and why

- The six 2026-10-16 spec review issues were implemented as six separate human-approved protected commits to `_docs/specs.md`, in the order #3, #6, #4, #5, #7, #8, from the batched answers recorded in each issue.
- #3: defines "fixed version for this dependency" and US-10 closing by affected range. #6: one finding-status list (`withdrawn` as `ASSUMPTION:`), brief-unavailable fallback, E7/E8. #4: primary and alias ids, alias lookup, known vs unknown CVE. #5: GitHub-repository ingestion and asset scan status. #7: notifications, due dates and the dedicated tracker repo. #8: MCP output and advisory-derived text rules.
- All six passed QA. One session summary covers the batch because the six were groomed, decided and committed as one step.

## Files created or modified

- `_docs/specs.md` only, in six protected commits: `45f6fa6` (#3), `999fd88` (#6), `e52a07c` (#4), `e0a60ac` (#5), `b03539b` (#7), `fdc7b51` (#8).
- Approval records: #3 6285069644, #6 6285087536, #4 6285106147, #5 6285123424, #7 6285146604, #8 6285163520.
- Engineer comments: #3 6284843229, #6 6284856636, #4 6284857967, #5 6284859024, #7 6284863547, #8 6284865043.
- QA PASS comments: #3 6285218980, #6 6285234570, #4 6286250358, #5 6286739493, #7 6286726338, #8 6286723784.
- Follow-up issue #41 and PM comment 6286808327 on #23 (no tracked file).
- `_docs/roadmap.md`, `_docs/ai-usage-log.md` and this summary.

## Decisions made by the human

- (Earlier in the session) the batched answers for #3-#8, recorded by the PM in each issue, and approval of each exact spec diff before its commit.
- Decision point, QA risks outside the criteria: option 1. The PM files one follow-up issue for the spec contradictions and gaps (#41), lists the Stage 2 details in it as inputs to roadmap step 7, and comments on #23 about the mocked frontend's mismatches with the spec.

## Mismatches with the spec or design docs

- Open in #41: E4's automated `withdrawn` vs #7 Decision 2; the n8n token scope vs closing; missing `VERIFY:` tags on GitHub token claims; asset scan status cases not covered (E3, E10); the spec status line still says "pending the 2026-10-16 review issues".
- The mocked frontend uses scan status, KEV and repository URL values that differ from the spec (comment 6286808327 on #23).

## Commands to validate

- **Verify:** each QA ran `make verify` with the issue's parent as `BASE`: PASS for all six (35 tests, whitespace PASS, no weakened tests). #5 QA also ran plain `make verify`: PASS with 7 assertion warnings, all from `759735a` (#22), each explained in #5's QA comment.
- **Approval records:** each QA confirmed the recorded diff is byte-identical to the stated `git show`, the parent and blob ID match, and the only path is `_docs/specs.md`.
- **Assert clean:** `make assert-clean` PASS at `fdc7b51` after the #5, #7 and #8 QA reruns; HEAD unchanged. The #3, #4 and #6 QA runs each report their own assert-clean PASS at `fdc7b51`.

## Proposed AGENTS.md changes

None.

## Temporary changes

None. No process or server was started, nothing was installed and no system configuration changed. `make clean-scratch` was not run: `.scratch/` still holds the paused #35/#33 session's files, which this session did not create. Run it when that session is done or discarded.

## Permission review

- Read-only (propose allowing): none.
- Writes to the record (keep asking): none.
- Risky (propose denying): none.
- Proposed `opencode.json` and `.claude/settings.json` changes: none.
- Sources: every Engineer, QA and PM comment of this step says "none". The Claude Code close-out (QA reruns, PM follow-up, this summary, closing) had no command stop for approval. The OpenCode orchestrator's own stopped commands for the six commits could not be collected, because that session was interrupted; the human can check its run view.

## Interruptions

- The OpenCode orchestrator (opencode/deepseek-v4.1-flash-free) committed all six spec changes, posted all six approval records and got QA PASS on #3, #6 and #4. It then stopped while the QA runs for #5, #7 and #8 were in progress. The #4 QA run took 1h 7m.
- Checked afterwards: `git status --short` clean; HEAD `fdc7b51`; no QA comment on #5, #7 or #8; no PID files. A partial `.scratch/qa-5/` was treated as unverified and not reused.
- Claude Code (claude-opus-5-5) took over as orchestrator: fresh QA runs for #5, #7 and #8, the decision point, the #41 follow-up, this summary and closing.

## Unrelated problems noticed but not fixed

- The 7 assertion warnings from #22's test rewrite (`759735a`) will appear in the push check until that work is pushed. Each is explained in #5's QA comment.
- Each approval record has no link to an approval comment, because the approvals were given in the orchestrator session. This is the documented limit of the #18 rule.

## Follow-ups for the next session

- #41: the PM asks the human D1-D4, then the spec fix is made as one protected commit.
- Roadmap step 3: #35 still needs QA, from the paused session or a fresh run.
- Roadmap step 7 (Stage 2 architecture) is now unblocked. It needs a new issue that takes #41's Out-of-scope list as input.
- Run `make clean-scratch` once the #35/#33 session is finished or discarded.
