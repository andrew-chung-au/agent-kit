# Verify a change

Done means the gates were run and their results observed, not that the code looks right.

**When:** before the Engineer hands over, when QA checks an issue, and whenever you're about to say work is finished. The pre-push hook runs the same gate again before the human pushes.

1. Run **Verify** (`make verify`). By default it checks everything since the upstream branch, which covers all unpushed work. To check from a specific commit: `make verify BASE=<commit>`.
2. Read the diff yourself (`git diff <base> -- .`), plus any untracked files the output lists.
3. For every WARN, give a one-line reason it's legitimate, such as "assertion rewritten for the renamed field". If you can't, treat it as a FAIL.
4. Report in this form:

   ```
   Verify: PASS | FAIL
   - tests: <passed and failed counts>
   - lint / type check: <result, or "not configured">
   - whitespace: PASS | FAIL
   - weakened tests: none | <what was found, with your reason for each>
   - files changed: <from the diff stat>
   ```

What the gate checks, so you know what a failure means:

- **Tests, lint and type check:** the commands set in `agent-kit.conf`.
- **Whitespace:** `git diff --check` on this folder.
- **Weakened tests:** deleted test files and newly added skip, xfail or focus markers fail the gate. Removed or rewritten assertions and changed fixtures are warnings.

Never edit a test just to make the gate pass, unless the issue's acceptance criteria change that behaviour; if you do, say so in the report. Never skip the gate or the hooks (`--no-verify`).
