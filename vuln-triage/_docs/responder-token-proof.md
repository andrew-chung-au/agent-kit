# Responder token and refused-push proof (owner-run)

Runbook for issue [#222](https://github.com/andrew-chung-au/vuln-triage/issues/222)
(task 28e, part of #160). You run every step; an agent cannot, because this
needs your GitHub account and a token that must never enter the sandbox.

**Goal.** Prove two things about the responder's GitHub token:
1. a push to `main` with it is **rejected** by the `protect-main` ruleset (F3), and
2. a push of a `responder/<fingerprint>` branch with it **succeeds** (so the
   real runner, #221, can open its pull request).

**Where to run it.** On a Docker host that is **not** the sandbox and **not**
your clean review clone — a throwaway clone is ideal. The token lives in your
local `.env` only (git-ignored, never committed; agents cannot write `.env`).

Needed before #221 is run live and before the recorded drill (task 39).

---

## 1. Create the fine-grained token

GitHub → Settings → Developer settings → **Fine-grained personal access tokens**
→ Generate new token. Set exactly:

| Setting | Value |
|---|---|
| Resource owner | your account |
| Repository access | **Only select repositories** → `andrew-chung-au/vuln-triage` (this repo only) |
| Repository permissions → **Contents** | **Read and write** |
| Repository permissions → **Pull requests** | **Read and write** |
| Repository permissions → **Administration** | **No access** |
| Everything else | No access |
| Expiration | a short expiry (e.g. 30 days) |

Copy the token once. Keep it out of shell history (see the prompt step below).

> Note: fine-grained tokens cannot be scoped to a single branch, so the refusal
> on `main` is enforced by the `protect-main` ruleset (F3), not by the token
> scope. That is exactly what this proof demonstrates.

## 2. Prepare a throwaway clone

```sh
cd "$(mktemp -d)"
git clone https://github.com/andrew-chung-au/vuln-triage.git
cd vuln-triage
# Do NOT run this from the sandbox folder or your clean review clone.
```

## 3. Create the check script in .scratch/ (not committed)

`.scratch/` is git-ignored and emptied by `make clean-scratch`, so this script
is intentionally **not** committed — you paste it in and run it. Create
`.scratch/responder-push-proof.sh` with the content below:

```sh
#!/usr/bin/env sh
# Responder token refused-push / allowed-push proof (#222). Owner-run.
# Reads the token from RESPONDER_GH_TOKEN; never prints it.
set -eu

: "${RESPONDER_GH_TOKEN:?set RESPONDER_GH_TOKEN (the fine-grained token), do not hard-code it}"
REPO="andrew-chung-au/vuln-triage"
REMOTE="https://x-access-token:${RESPONDER_GH_TOKEN}@github.com/${REPO}.git"
FP="proof-$(date +%s)"
BRANCH="responder/${FP}"

OUT=".scratch/push-proof.out"
redact() { sed "s#${RESPONDER_GH_TOKEN}#***TOKEN***#g"; }
# Run a command with its output redacted, keeping the command's REAL exit code
# in $RC. (Piping straight into redact would report sed's exit code instead.)
run() {
  set +e
  "$@" >"$OUT" 2>&1
  RC=$?
  set -e
  redact <"$OUT"
}

echo "== Baseline: main SHA before =="
run git ls-remote "$REMOTE" refs/heads/main
[ "$RC" -eq 0 ] || { echo "FAIL: cannot read the remote (check the token and repo access)"; exit 1; }
MAIN_BEFORE=$(cut -f1 "$OUT")
[ -n "$MAIN_BEFORE" ] || { echo "FAIL: no main SHA returned"; exit 1; }
echo "main before: ${MAIN_BEFORE}"

echo
echo "== Make a trivial local commit on top of main =="
run git fetch "$REMOTE" main
[ "$RC" -eq 0 ] || { echo "FAIL: fetch failed"; exit 1; }
git checkout -B push-proof FETCH_HEAD
date > PROOF_SCRATCH.txt
git add PROOF_SCRATCH.txt
git -c user.name=proof -c user.email=proof@example.invalid commit -q -m "proof: do not merge"

echo
echo "== Expect REJECTED: push to main =="
run git push "$REMOTE" HEAD:main
PUSH_MAIN_RC=$RC
echo "push-to-main exit code: ${PUSH_MAIN_RC}  (non-zero = rejected, expected)"
if [ "$PUSH_MAIN_RC" -eq 0 ]; then
  echo "FAIL: the push to main was ACCEPTED. The token or the protect-main ruleset is wrong."
  echo "Do not continue: check main now and revert the proof commit through a pull request."
  exit 1
fi

echo
echo "== main unchanged? =="
run git ls-remote "$REMOTE" refs/heads/main
MAIN_AFTER=$(cut -f1 "$OUT")
echo "main after:  ${MAIN_AFTER}"
if [ "$MAIN_BEFORE" = "$MAIN_AFTER" ]; then
  echo "OK: main SHA unchanged"
else
  echo "FAIL: main SHA changed!"
  exit 1
fi

echo
echo "== Expect SUCCESS: push a responder/<fingerprint> branch =="
run git push "$REMOTE" "HEAD:${BRANCH}"
if [ "$RC" -ne 0 ]; then
  echo "FAIL: the responder/<fingerprint> push was rejected (exit ${RC}); the token cannot open the runner's PR branch."
  exit 1
fi
echo "pushed branch: ${BRANCH}"

echo
echo "== Clean up: delete the test branch =="
run git push "$REMOTE" --delete "${BRANCH}"
if [ "$RC" -ne 0 ]; then
  echo "WARNING: could not delete ${BRANCH} (exit ${RC}); delete it by hand on GitHub."
  exit 1
fi
echo "deleted branch: ${BRANCH}"

echo
echo "Done. Expected: push-to-main REJECTED (non-zero, quoting protect-main),"
echo "main SHA unchanged, responder branch push SUCCEEDED then deleted."
```

## 4. Run it

Pass the token through the environment (a leading space keeps it out of shell
history in most shells):

```sh
 RESPONDER_GH_TOKEN='paste-the-token-here' sh .scratch/responder-push-proof.sh | tee .scratch/responder-push-proof.log
```

Expected output, in order:
- a **rejection** of `HEAD:main` whose message quotes the `protect-main` rule
  (pull request required) and a **non-zero** exit code;
- `main` SHA **unchanged** before vs. after;
- a **successful** push of `responder/<fingerprint>`, then its deletion.

## 5. Record the evidence on #160

Post on [#160](https://github.com/andrew-chung-au/vuln-triage/issues/160):
- the commands and the captured output from `.scratch/responder-push-proof.log`,
  with the token **redacted** (the script already masks it; double-check) and
  **no account ids or ARNs**;
- the token scope as text or a screenshot (repo-only, Contents write, Pull
  requests write, no Administration, with an expiry);
- the `protect-main` ruleset basis (F3): bypass list empty, pull request
  required with 0 approvals by design, status checks required.

Then confirm the test branch is gone (the script deletes it) and tick the
acceptance boxes on #222.

## 6. Afterwards

- Keep the token in your local `.env` only (never committed). Delete
  `.scratch/` contents when done (`make clean-scratch`).
- This unblocks #221's live run and the recorded drill (task 39, milestone C7).

## Acceptance criteria (from #222)

- [ ] Token: fine-grained, this repo only, Contents + Pull requests write, no
  Administration, with an expiry.
- [ ] A refused `git push origin HEAD:main` quoting `protect-main`, with `main`
  unchanged (SHA compared before/after).
- [ ] A successful `responder/<test-fingerprint>` push, then branch deleted.
- [ ] Evidence posted on #160 with the token redacted, no account ids/ARNs.
- [ ] F3 ruleset facts recorded as the basis.
