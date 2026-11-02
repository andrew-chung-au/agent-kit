# Planning: handover from the Claude Code orchestrator to OpenCode

**Date:** 2026-11-02T10:48Z (UTC)
**Spec version:** none

Written because the Claude Code usage limit was close. Read this, then `AGENTS.md`, `agent-kit/process.md` and `agent-kit/team/` as usual. Per-issue detail is in the `_session-summaries/*issue-0NN*` files and the issue comments. Nothing is running; the working tree was clean at HEAD 0601022 when this was written (apart from this file).

## What changed and why

Closed this session, each with QA PASS and its own summary: #40, #45, #38, #46, #48; #19 closed as not planned by the human. Commits not yet pushed: about 60, including the evolution plan and review (`proposals/`). The human pushes from the clean clone.

In flight, **#47** (OpenCode permission template refresh): commits A (0ab8586) and B (0601022, this repo's live `opencode.json`) landed after the human approved each exact diff, then QA FAILED at 0601022 (a stale README line plus gaps in the rule list). The human chose option B: the PM revised #47's body (new hash `cd4e6f2f490e90b848b437448e44dc80cf16a38fb53686d3a22c1c04750242a3`, recorded in a `PM:` comment) and filed #49 as the follow-up. **The human has confirmed the new body hash** (an `Orchestrator:` comment on #47 names it, posted after this note's first commit), so the Engineer may be launched on #47 after the usual `make issue-hash N=47` check, which must still show that hash as both body and recorded.

**What the human's by-hand OpenCode test showed (1.19.5, DeepSeek V4.1 Flash Free, recorded on #47):** OpenCode checks each command of a chain separately, so `ls | head`, `ls ; pwd` and `ls && pwd` ran silently, while `$(...)`, redirects, absolute paths, `..` and `git commit --amend` prompted, and `git commit -n`, `.env` and `gh auth token` were denied.

**Important for the next orchestrator:** this repo's `opencode.json` is now the strict, refreshed one (plain `git commit` runs without a prompt; chains of allowed commands run without a prompt). Roles, the permission list and the by-hand findings are in `agent-kit/opencode/START.md` and #47.

## Reflection

unknown (planning session; roles not asked)

## Launch usage

none recorded here; each issue's summary has its own lines. Not recorded for the #13 and #47 PM launches and the #47 Engineer and QA launches (no summary yet, #47 is still open).

## Files created or modified

- This summary only.

## Decisions made by the human

- #47: option B after QA FAIL (fix the README line, `git diff*` matching `git difftool`, the commit abbreviations and the chain wording in #47; the rest in #49).
- #47's earlier four questions: order #47, then #13, then #44; content readers allowed with asks; strict `*.env*` deny with no `.env.example` allow in bash; token scopes as stated (code read, issues read and write, no user permissions, single-repository scope not verified); silent plain commits.
- #46 and #48: the settings-read rule is narrowed and the exported template keeps the strict ban with an opt-in `Readable config` slot, this repo opts in to three paths.
- #2 (root README) is approved with all seven PM decisions (ship after #9, protect the README, no counts, "built with its own process" section, plain tone, no name or contact). #13 is approved with the PM's three defaults (`issue-dump` in core `Makefile.mk`; no issue-data rule in the shared block; #15 stays separate).

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`

## Proposed AGENTS.md changes

none. Possible follow-up: `AGENTS.md` still says "your GitHub token is read-only", which is not accurate now that the token has issues write (stated in #47's docs).

## Temporary changes

none

## Interruptions

The Claude Code usage limit; no role was left half done. The #47 Engineer and QA runs finished and reported; the PM finished its revision of #47 and #49.

## Unrelated problems noticed but not fixed

- `make assert-clean` passes now (the tree was cleaned this session).
- Reflection proposals from #40, #45, #38, #46 and #48 are recorded in the issue summaries for the human; none applied.
- README "Updating the kit" step 4's prompt conflicts with the new `Readable config` note (fails closed).
- The `.opencode/` Readable-config entry covers `node_modules/` (the human's choice).

## Follow-ups for the next session

In this order unless the human says otherwise:
1. **#47:** run `make issue-hash N=47`; launch the Engineer; commits stay split (kit files, then this repo's live config), each with an exact-diff approval request. The inert `;`, `&`, `|` asks are kept (the PM default, recorded in the confirmation comment). Then QA, reflections, summary, close.
2. **#13** (approved): after #47; **#44** (approved): after #13, and it also waits for #20; **#49** (unlabelled): after #47, two open questions with PM defaults (one broad recursive-grep ask; ask patterns for `make -f`, `SHELL=`, `--eval`).
3. **#20** (approved): its stage 1 gate (confirm real permission event names in a live OpenCode session using a throwaway observer) can now be retried, since OpenCode 1.19.5 runs here; it needs the human's approval for the observer and the final plugin (both under `.opencode/*`). **#36** (approved) needs #20.
4. **#2** (approved): the human decided it ships after #9; they have not yet chosen whether to start it now with clone-and-copy install, wait for #9, or have the PM groom #9 first.
5. **#37** (approved): three PM decision questions are unanswered (ADR in the body; a small Light dry-run issue; refresh the body).
6. Backlog review (PM, propose-only) decisions are unanswered: close #14 as not planned; merge #10 and #11; close #5, #7 and #15 only after #12, #6 and a rewritten #13 absorb their criteria; the order for next small issues without OpenCode was #32 (regroom first), #41, #4 with #12, #3, #33.
7. **#42, #43** (unlabelled, groomed; do #42 first, one hook version bump).
8. The first sweep waits for #32 (`make sweep-due`: no sweep recorded). The human decides when to cut version 1.10; the changelog lines proposed in the issue summaries are not applied.
9. **Push:** the human reviews from the clean clone and pushes; the push check needs Docker on their machine.

**Rules that matter when running the process in OpenCode:** the human adds or removes `approved`; the orchestrator never does. Check the hash (`make issue-hash N=<n>`) before launching the Engineer or QA. Protected commits are staged with explicit paths and returned to the human as an approval request with the exact diff; the human commits with `HUMAN_APPROVED=1` and a pathspec. QA never fixes. Ask each role for a `Reflection:` comment after QA PASS. Run `make clean-scratch` only when no role is using `.scratch/`. OpenCode agents tend to refuse commands by judgment before a permission rule is reached, so a refusal is not evidence a rule works; to test a rule, tell the agent explicitly to make the tool call.
