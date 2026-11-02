# Issue #48: Readable config slot: strict settings-read ban in the template, this repo opts in

**Tier:** Standard (no tier label was set; the PM proposed Heavy, and Heavy has no extra gates until #37 lands)
**Date:** 2026-11-02T09:05Z (UTC)
**Spec version:** none

## What changed and why

#46 put the same permissive settings-read line in this repo's `AGENTS.md` and in the exported template. The human pointed out that this repo (public, committed tool config holds nothing secret) may deliberately differ from what the kit exports: a downstream, possibly private project's committed `.claude/settings.json` or MCP config can carry environment values or tokens, so the exported default should be stricter. The PM filed #48 and the human chose the opt-in slot over a plain strict ban.

Commit d0f6442, a follow-up to bb1d27e (not a rewrite), approved by the human as the exact diff:
- one shared Non-negotiable line, byte-identical in `AGENTS.md` and `agent-kit/templates/AGENTS.md.template`: ban the home folder, the tool's settings and environment variables, except the project config files listed under `Readable config` in Project settings, read as data; the list never includes user-level settings, `.claude/settings.local.json` or `.env` files; stop and tell the human if a value looks like a secret.
- the divergence lives in the slot: the template's `Readable config` defaults to "none"; this repo's lists `opencode.json`, `.opencode/`, `.claude/settings.json` with a public-repo note.
- `agent-kit/setup.md` (new projects get "none"; review mode reports a missing line) and `agent-kit/README.md` (a note that doing nothing keeps the strict ban and opting in needs the human's approval after a secrets check).
- `tests/test_settings_read_rule.py` rewritten around the new shape.

`make verify` passed (333 tests). QA PASS at d0f6442: 24 mutations on copies, all caught; the by-hand injection check passed again (planted instruction read as data and not run; fake token reported, not repeated). Enforcement is text only and the pins are wording tests.

Words (`wc -w`): `AGENTS.md` 1401 to 1429 (+28, expected +20 to +30); template 868 to 905 (+37, slightly over the +25 to +35 estimate, a metric not a gate); `setup.md` 1177 to 1224 (+47); `README.md` 2736 to 2805 (+69).

**What I learned:** a rule's divergence between this repo and the exported template can live in a project-level slot, so the shared block stays identical (no drift) while each project carries its own exception visibly.

## Reflection

### Engineer

(1) Slowed down: the README upgrade prompt (step 4) said to leave the project half unchanged, which conflicts with adding a new project-half slot; I had to read README lines 80-112 and setup.md twice to place the note.
(2) Nearly went wrong: the staged index already held the #16 and #39 session summaries, so a plain commit would have swept them in; I returned a pathspec plan instead of committing.
(3) Proposal: in `agent-kit/team/software-engineer.md`, add one line under Commits: "Before returning an approval request, run `git diff --cached --stat` and name any staged path outside your task." Expected effect: foreign staged files are flagged before approval. Measure: count approval requests that needed a pathspec correction over the next ten issues.

### QA

1. Slowed down: my first mutation run reported 24 of 24 "caught" with empty test names, because `unittest discover -s tests -t .` failed with an ImportError (no `tests/__init__.py`); I only noticed from the baseline line. Cost two extra script rewrites, since I had no edit tool.
2. Nearly went wrong: one mutation showed MISSED because `tell the human.` first matches the Issues section of `AGENTS.md`, not the shared line. I almost reported a test gap that was my own bad mutation.
3. Proposal: in `agent-kit/team/qa-engineer.md`, add "for mutation checks, run the unmutated copy first and require it to pass, and assert each mutation changed the intended line". Expected effect: fewer false CAUGHT/MISSED results. Measure: count QA reports that retract a mutation result, over the next five issues.

### PM

1. Slowed down: finding where the template's shared block is compared with AGENTS.md took four separate greps (tests, scripts, setup.md, README) because no document lists the parity checks; and the hash changed once because the human's decision arrived after I had filed the body.
2. Nearly went wrong: my first wording started with the pinned old string "Don't read the AI tool's settings", which would have tripped or weakened the absence pins in test_settings_read_rule.py; I caught it only by reading the test before drafting.
3. Proposed change: `agent-kit/setup.md` (review-mode drift list) gains one line naming where the shared-block parity is checked (by hand, no test). Expected effect: fewer searches when grooming a shared-block change. Measured by the number of grep calls a PM makes to answer "what compares the template with AGENTS.md" in the next such issue, with QA rounds as the protection metric.

## Launch usage

- PM (groom and file #48, update after the human's decision): 137.7 s, 21 tool uses
- Engineer (implement #48): 178.2 s, 32 tool uses
- QA (check #48 at d0f6442): 177.2 s, 25 tool uses
- PM (reflection, resumed): 17.8 s, 3 tool uses
- QA (reflection, resumed): 221.1 s, 28 tool uses (as the notification reported it; may include the earlier run)
- Engineer (held comment and reflection, resumed): 68.5 s, 6 tool uses

## Files created or modified

- `AGENTS.md`, `agent-kit/templates/AGENTS.md.template`, `agent-kit/setup.md`, `agent-kit/README.md` (edited)
- `tests/test_settings_read_rule.py` (rewritten in part)
- This summary.

## Decisions made by the human

- Asked whether this repo and the exported template could differ; agreed with the orchestrator's argument that the exported default should be stricter, and said yes to the PM filing the issue.
- Chose the opt-in slot (over a plain strict ban with no slot) after asking whether the slot was the divergence itself (it is the mechanism, the divergence is template-strict versus this-repo-open).
- Labelled #48 `approved` with the PM's defaults unchanged (option A: the same shared line in both files; version bump proposed only).
- Approved the exact diff and ran the protected commit (d0f6442).

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`

## Proposed AGENTS.md changes

none (the change itself is this issue)

## Temporary changes

none. `make clean-scratch` ran at the end of this issue.

## Interruptions

none

## Unrelated problems noticed but not fixed

- README "Updating the kit" step 4's upgrade prompt still says to leave the project half unchanged, which conflicts with the new note. A project that follows only the prompt could skip adding a `Readable config` line; that fails closed (the strict ban holds) and review mode reports it. A one-clause fix ("except adding a `Readable config` line") is available; left for the 1.10 upgrade-prompt rewrite.
- `make assert-clean` still fails here only because of pre-existing uncommitted work (`.claude/agents/pm.md`, the staged #16 and #39 summaries, two `proposals/` files); QA compares `git status --short` before and after instead.
- No document lists where the template's shared block is compared with `AGENTS.md` (by hand in setup.md review mode, no test): the PM's proposal to name it in the review-mode drift list.
- QA's first mutation run silently reported nothing caught because `unittest discover -s tests -t .` fails without `tests/__init__.py`; not a repo defect, but the repo's own command is `make test`.
- Proposed, not made: a version bump to 1.10 and a changelog line "Settings-read rule: the template keeps the strict ban and adds a `Readable config` opt-in; projects list config files they allow."

## Follow-ups for the next session

- #47 (OpenCode permission template) and #13 (issue-dump and the make-variable rule) are groomed and unlabelled; the human prefers #47 before #13.
- #2 (root README) is approved but the human decided it ships after #9; still unanswered whether to start now with clone-and-copy install.
- #44, #20, #36 and #37 as before.
- The #16 and #39 summaries are still staged and uncommitted.
