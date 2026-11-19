# Issue #54: Close the cheap gaps in the frontend source guardrail scan

**Date:** 2026-11-13T06:22Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Claude Code worked it in the local sandbox on `main` while #20 waited for #19 (the human's one-time exception to `delivery-pace.md` item 4: one small supporting issue alongside a main issue). Ponytail was on.

- **Scan widened** (`frontend/src/test/guardrails.test.ts`, the only file): the `fetch(` and `.sort(`/`.toSorted(` rules also refuse a space or line break before the bracket, bracket access (`a["sort"]`, `window["fetch"]`) and `window`/`globalThis`/`self` `.fetch`, under their old names. New rules: `HTML sink` (`insertAdjacentHTML`, `outerHTML`, `document.write`, `createContextualFragment`, then `setHTMLUnsafe` and `parseHTMLUnsafe`), `XMLHttpRequest or sendBeacon`, and `HTML-parsing package import`. Two new `src/test/` checks: no non-test file imports from it, and only `*.test.ts(x)` and `setup.ts` may sit in it.
- **Known limits** are written as a comment at the top of the file: computed property names, aliased functions, run-time strings, `srcDoc`, `sanitize-html` and `htmlparser2`, a comment between name and bracket, `document?.write`, an import path that reaches `src/test/` by another segment first, and one-element bracket arrays; they wait for lint rules (#31).
- **Round 2 (Reviewer findings, approved):** a `window?.fetch` refusal row, the two `*HTMLUnsafe` sinks, the markdown rule written through the shared `importOf` helper, and the extra known limits. Vitest went from 157 to 189 to 192; no assertion removed.
- **QA:** PASS at `7091057` and `f32d2bd`; `make assert-clean` passed after each.
- **Stale base:** QA's `make verify` at `f32d2bd` failed its weakened-test check ("test files deleted: tests/test_audit_api.py, tests/test_audit_contract.py") only because the orchestrator ran `git fetch` during QA and `origin/main` (#19's merge) moved ahead of local `main`. After merging `origin/main` into `main` (`0b8538b`), `make verify` passed (1508 Python, 192 frontend, 0 assertion lines removed), so the Close line cites that run.
- **Slip:** round 2 dropped a space after a comma in the existing `globalThis.fetch` row, against the instruction to change no other line. No behaviour changed; QA and the Engineer both recorded it. Left as is.

**What I learned:** `git fetch` is not read-only for the checks: `make verify` compares with `origin/main`, so a fetch while QA runs can fail its weakened-test check. Fetch between launches, not during one.

## Reflection

### PM

Reflection:
1. Slowed by a wrong premise in the launch brief: it said the scan was a script under `scripts/` in `make frontend-build`; the PM read the Makefile, `scripts/` and the test folder before finding it was `guardrails.test.ts`, which `make frontend-test` runs.
2. Nearly wrong: it might have proposed a protected-file tier (Heavy) on that premise; reading `agent-kit.conf` showed the test file is in `TEST_FILES` but not `PROTECTED`, so Standard with no approval of the diff.
3. Proposed change: `_docs/agent-kit/procedures/planning.md`, add "name the gate by the command that runs it, not by file type" to the launch-brief checklist. Expected effect: fewer wrong path or tier premises. Measure: count grooming sessions where the PM report corrects the brief, over the next five issues.

### Engineer

Ponytail: reused the existing `importOf` helper for the markdown rule and left `importsFromTestFolder` alone, because its regex has a capture group and the `g` flag, so sharing the prefix would have changed behaviour.

Reflection:
1. What slowed me down: the 35-second Vitest run, done twice (once in `make frontend-test`, again inside `make verify`), plus the 93-second Python suite that `make verify` runs for a test-only change.
2. What went wrong: in round 2 my edit to add the `window?.fetch` row dropped the space after the comma in the existing `globalThis.fetch` row, which I was asked not to touch. The tests still passed and `git diff --check` does not flag it, so I committed it. Cosmetic only.
3. Proposed change: in `_docs/agent-kit/team/software-engineer.md`, under Commits, add "read `git diff --cached` and confirm that no line outside the task's list changed before committing". Expected effect: an accidental edit to an untouched line is caught before commit. Measure: count of QA findings of the kind "changed a line the task did not name" per issue.

(Round 2's Engineer had no memory of round 1; its comment says the round-1 part came from the issue history.)

### QA

Reflection:
1. Slowed down: `make verify` reported FAIL ("test files deleted: ...") only because local main was behind `origin/main`; it cost an extra investigation and a judgement call against the "Verify FAIL means FAIL" rule.
2. Nearly went wrong: the stale-base failure could have forced a FAIL verdict the Engineer cannot fix, or been waved through without proof; the base is outside the issue's files.
3. Proposed change: the verify script's weakened-tests section and `_docs/agent-kit/procedures/verify.md`: when HEAD is behind `origin/main`, print "base is N commits behind origin/main" and list deleted files only against the merge-base. Effect: no false "deleted" reports. Measure: count of QA comments that explain a stale-base verify FAIL, expected to drop to zero.

### Ponytail

Engineer: see the `Ponytail:` line above.

## Launch usage

Tool: Claude Code. Figures copied from the completion notifications; a resumed launch's figure may be cumulative or per-resume (unknown).

- PM grooming: 219 s, 32 tool uses; reflection resume: 13 s, 3 tool uses.
- Engineer round 1: 429 s, 22 tool uses.
- QA round 1 (PASS at `7091057`): 202 s, 11 tool uses.
- Reviewer: 49 s, 6 tool uses.
- Engineer round 2: 352 s, 16 tool uses; final reflection resume: 171 s, 7 tool uses.
- QA round 2 (PASS at `f32d2bd`): 216 s, 16 tool uses; reflection resume: 14 s, 3 tool uses.

## Files created or modified

`frontend/src/test/guardrails.test.ts`, this file. The merge of `origin/main` (#19) into `main` is recorded in #20's summary.

## Decisions made by the human

- Approved the groomed body, which includes the strings beyond #8's list (`insertAdjacentHTML`, `outerHTML`, `document.write`, `createContextualFragment`, `XMLHttpRequest`, `sendBeacon`, `window`/`globalThis`/`self` `.fetch`, and the four packages including `dompurify`) and the pointer to lint rules without a new issue.
- Reviewer findings: applied 1 (the `window?.fetch` row), 2 (the two `*HTMLUnsafe` sinks, `srcDoc` as a known limit), 3 (the shared `importOf`), 4 and 5 and QA's two risks as lines in the known-limits comment; skipped 6.
- Close #54 in parallel with #20's second round.

## Mismatches with the spec or design docs

none. (The launch brief wrongly called the scan a build script; the groomed body names the real file.)

## Commands to validate

- **Verify:** `make verify` (PASS on the merged tree: 1508 Python, 192 frontend, no weakened tests).

## Proposed AGENTS.md changes

none. (The Reflection proposals touch `_docs/agent-kit/` files; they are for the sweep.)

## Temporary changes

none. No processes started. The orchestrator runs `make clean-scratch` at the end of the session, after #20's Close.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- A dead test-only `GET /api/cases` route in `tests/backend_support.py`: filed as #120 and placed in the supporting list before #22.
- QA's residual limits (not refused by the text scan: `fetch/**/(u)`, `a.sort/**/(c)`, `document?.write(t)`, `@/components/../test/x`, `setHTML` without `Unsafe`) are written in the known-limits comment or left to the lint rules (#31).

## Follow-ups for the next session

- #31 (lint) should read the known-limits comment at the top of `guardrails.test.ts` when it is groomed.
- #75, then #31, if the human allows them after #20.
