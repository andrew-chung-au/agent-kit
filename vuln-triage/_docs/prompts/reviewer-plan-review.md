You're an independent reviewer for this project. Another agent (OpenCode)
wrote the plan; you did not. Your job is to find problems, not fix them.

Setup check first: confirm you have read CLAUDE.md and, through it, AGENTS.md.
If CLAUDE.md is missing, stop and tell me.

Then run `git rev-parse --short HEAD` and review the repo at that commit.

Read these, in order: `_docs/project-brief.md`, `_docs/rubric.md`,
`_docs/planning-process.md`, then every planning document that exists so far
(e.g. `_docs/specs.md`, `_docs/architecture.md`, `_docs/openapi.yaml`,
`_docs/testing.md`, `_docs/tasks.md`, `_docs/plan-summary.md`). Review only
what exists; list stages not written yet under "Not yet written" and don't
count them as failures.

Look critically for:
1. Errors: steps that are wrong, contradict each other, or contradict the brief
2. Gaps: steps or decisions that aren't fully thought through, explained or
   justified, and edge cases that aren't handled
3. Scope: anything in the plan that isn't in the brief, or brief items missing
   from the plan
4. Checkability: acceptance criteria that can't be checked with a yes or no
5. Invented details: external API facts (OSV.dev, CISA KEV, FIRST EPSS)
   stated as fact without a VERIFY: tag
6. Feasibility: anything unrealistic for one developer, or blocked by the
   environment (e.g. no Docker in this container)
7. Security: places where the design could let untrusted data (advisory text,
   issue comments) steer an agent or the LLM

Rules:
- Do not edit any existing file. Write only your review file and your log entry.
- For each finding, quote or point to the exact section, so it can be found.
- If you're unsure whether something is a problem, include it as a question,
  not a finding.

Write the review to `_docs/reviews/<today's date>-plan-review.md` in this format:

  Reviewer: <PASS | FAIL> at <commit hash>
  Documents reviewed: <list>
  Not yet written: <list>

  ## Findings
  1. [High | Medium | Low] <file> § <section>: <what's wrong>
     Why it matters: <one line>
     Suggested fix: <one line>

  ## Questions for the human
  - <anything you couldn't decide>

The verdict is FAIL if there is any High finding. Then append an entry to
`_docs/ai-usage-log.md` (role: Reviewer, with your model name), commit only
those two files, show me the commit, and STOP.
