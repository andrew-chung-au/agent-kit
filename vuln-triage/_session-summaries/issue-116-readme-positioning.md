# Issue #116: README audience and outcome positioning

**Date:** 2026-10-23
**Spec version:** 9b04f90

Tool: Claude Code (local sandbox), on `main`. No push.

## What changed and why

The human worried that VulnTriage overlaps with the platform's own dependency alerts and asked for a clearer niche without changing earlier work. After a chat brainstorm they chose a narrower profile: a tool for the security function of an organisation with many teams. The README now says that as problem and outcome, with no other product named (human rule).

- **PM** (6362512286) filed and groomed #116: 12 acceptance criteria, three decision questions.
- **Human decisions** (orchestrator comment 6362524465): D1 option 1 (audience line), D2 option 1 (submission-build claims only), D3 option 1 (extend "The problem"; no new section, no rewrite).
- **Engineer** `47e8ffe`: one audience paragraph and five outcome bullets in "The problem" (`README.md` lines 10-16); the usage-log entry. Comment 6362551983. It dropped the draft sentence "severity scores rate almost everything as urgent" because the plan does not support it.
- **QA: PASS** at `47e8ffe` (6362566732), all 12 criteria; criterion 10 ("one path changed") judged compliant because the commit also holds the required usage-log entry.
- Issue closed with `make issue-close N=116`.

## Files created or modified

- `README.md` (Engineer, `47e8ffe`)
- `_docs/ai-usage-log.md` (Engineer, `47e8ffe`)
- `_docs/roadmap.md` (check-in line, this session)
- `_session-summaries/issue-116-readme-positioning.md` (this file)
- `tests/fixtures/github/repositories.txt` (orchestrator, outside #116: the three confirmed repositories `astral-sh/uv-docker-example`, `heroku/python-getting-started`, `heroku/nodejs-getting-started` replace the empty list; not committed by this issue)

## Decisions made by the human

- Which niche: the security function over many teams; do not name or compare to Dependabot or GitHub's alerts.
- File the README change as an issue (not a direct edit).
- D1-D3 on #116: all as recommended.
- The three fixture repositories in `repositories.txt` (confirmed by "yes please" after the list was shown). The GitHub features of other tools were not researched; no claim about them is in the README.

## Mismatches with the spec or design docs

None found. The README risk wording matches spec US-11 (an owner may accept risk on their own assets; the security lead on any).

## Commands to validate

**Verify:** `make verify` (PASS WITH WARNINGS at `47e8ffe`: 62 frontend and 246 backend tests; the one warning is the uncommitted `repositories.txt`).

## Proposed AGENTS.md changes

None.

## Temporary changes

none. (`make record-fixtures SOURCE=github` has not been run by this session; it is the human's step. `.scratch/` still holds this issue's files until `make clean-scratch`.)

## Permission review

PM, Engineer and QA reported no approvals beyond the normal targets. Orchestrator actions:

- Read-only (propose allowing): `make issue-dump N=76`; `grep` over `.scratch/issue-76-comments.json`; `git log -1 --format=%h -- _docs/specs.md`; `grep` over `agent-kit.conf`.
- Writes to the record (keep asking): `make issue-comment N=116` (decisions comment); `make issue-close N=116` (ask rule); `gh issue create` and `make issue-comment` by the PM at the human's request; a web fetch through a subagent to check three public repositories.
- Risky (propose denying): none.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- `make record-fixtures SOURCE=osv|kev|epss` print "implemented in task 5/6" and exit 2; they are built with #77 onward.
- The proposed `requirements.txt` fixture repository (`heroku/python-getting-started`) has version ranges only, no `==` pins and no `-r` includes, so it exercises the parser weakly.
- The Engineer for #76 proposed `heroku/node-js-getting-started`; GitHub now redirects it to `heroku/nodejs-getting-started`.
- #116's issue body says "routing and delivery stories"; the PM comment clarifies this as US-8, US-11 and US-14.

## Follow-ups for the next session

- The human runs `make install` (if needed) and `make record-fixtures SOURCE=github`, checks the files for tokens and private data, pastes the MANIFEST rows, and commits `repositories.txt` with the captures.
- Next product step: #77 (task 5, OSV matching).
- Optional: put the audience line in `_docs/specs.md` (Roles) or `_docs/project-brief.md`: both protected, needs a separate approved diff.
