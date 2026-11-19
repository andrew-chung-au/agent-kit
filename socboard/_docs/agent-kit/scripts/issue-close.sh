#!/usr/bin/env bash
# Close one GitHub issue, only when the issue's recorded history shows the process was
# followed. Run through the make target, from the project folder:
#     make issue-close N=<issue number> [REASON=completed|not-planned]
# or directly: bash _docs/agent-kit/scripts/issue-close.sh <number> [completed|not-planned]
#
# Only the orchestrator closes issues (process.md, Lifecycle step 9). This is the one
# sanctioned way; it does nothing else to an issue: no edit, label, reopen, delete or
# comment. It prints one line on success.
#
# What it reads (all from the comments of the REPOSITORY OWNER's account; a comment from
# any other account, or from a deleted account (null author), is ignored for every check).
# A QA verdict is the first line: FAIL if it says FAIL anywhere, PASS only if it starts
# `QA: PASS` (team/qa-engineer.md). An Engineer comment reports a commit when it says
# "commit" and holds any 7 to 40 hex characters, all-digit short hashes included, unless it
# is a reflection: it has a `Reflection:` line and has neither a Verify line (a line starting
# with Verify or Verification) nor a numbered
# criterion line saying done or not checked (local deviation, see _docs/decisions/):
#   completed, Standard or Heavy: the issue is open and has `approved`; the latest `QA:`
#     verdict is PASS; at least one `QA:` PASS (two for `tier:heavy`) was posted at or
#     after the last `Engineer:` comment that reports a commit; an `Orchestrator:` Close
#     comment at or after the latest PASS has the lines
#         QA PASS commit: <7 to 40 hex>   (this value must appear in the latest PASS)
#         Merge commit: <7 to 40 hex>
#         Verify: <text>
#         Summary: <path>
#   completed, Light (`tier:light`): `approved`; an `Engineer:` comment with a
#     `tier-check: PASS` line; an `Orchestrator:` Close comment at or after it with the
#     Merge commit, Verify and Summary lines and `Human approved diff: yes`. No QA.
#   not-planned: an `Orchestrator: Close as not planned` comment with the lines
#         Human approved closure: <YYYY-MM-DD>
#         Backlog review: <path or comment URL>
#     No `approved` label and no QA verdict are needed.
# The tier is the highest tier label (heavy over standard over light); none is Standard.
# Comments are ordered by createdAt, ties by their order in the list; "at or after"
# compares createdAt only, so a PASS posted at the same time counts as after.
# The script checks the recorded lines, not the facts: it cannot see that a commit
# exists or that the human approved a diff. All roles share the owner's account, so
# the checks stop mistakes and shortcuts, not a role set on bypassing the process.
#
# The repository is the GITHUB_REPO line of agent-kit.conf (github_api.py validates it);
# the REST API is used because `gh issue` cannot find the repository from the git remote
# everywhere (Kiro Web). The only gh calls it makes are these shapes, fixed here, never
# built from issue text (the first three are made by github_api.py, every page of the
# comments is read):
#     gh api repos/<repo>/issues/<N>
#     gh api "repos/<repo>/issues/<N>/comments?per_page=100&page=<P>"
#     gh api repos/<repo>
#     gh api repos/<repo>/issues/<N> --method PATCH -f state=closed -f state_reason=completed
#                                            (or -f state_reason=not_planned)
# (the last is the only write). It fails closed: if gh is missing, fails, prints nothing
# or malformed JSON, or a field is missing, it refuses and closes nothing.
#
# Exit codes: 0 closed; 1 gh failed on the close (no retry); 2 bad N or REASON (no gh
# command ran); 4 refused, or could not check.
set -u
set -o pipefail
export LC_ALL=C

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd) || exit 2
die() {
  echo "issue-close: $2" >&2
  exit "$1"
}
# shellcheck source=issue-text-lib.sh
. "$here/issue-text-lib.sh"

{ [ "$#" -eq 1 ] || [ "$#" -eq 2 ]; } || die 2 "Usage: issue-close.sh N [completed|not-planned] (N is one issue number)"
number="$1"
reason="completed"
[ "$#" -eq 2 ] && reason="$2"
check_number "$number"
case "$reason" in
  completed | not-planned) ;;
  *) die 2 "REASON must be absent, completed or not-planned" ;;
esac

command -v gh > /dev/null 2>&1 || die 4 "cannot check issue $number: gh was not found; nothing was closed"
github_repo || die 4 "cannot check issue $number: no valid GITHUB_REPO=\"<owner>/<name>\" line in agent-kit.conf; nothing was closed"
issue_json=$(python3 -B "$here/github_api.py" issue "$REPO" "$number" 2> /dev/null) || die 4 "cannot read issue $number with gh; nothing was closed"
repo_json=$(python3 -B "$here/github_api.py" owner "$REPO" 2> /dev/null) || die 4 "cannot read the repository owner with gh; nothing was closed"

# The checker reads the issue JSON on standard input, not as an argument, so a long
# comment history cannot hit the argument-length limit and make the issue unclosable.
# `read -d ''` returns 1 at the end of the here-document; that is expected.
read -r -d '' checker << 'PY' || true
import json, re, sys

# Exit 0: allowed to close. 1: refused (the reason is printed). 2: could not tell.
def refuse(why):
    print(why)
    sys.exit(1)

try:
    issue = json.loads(sys.stdin.read())
    repo = json.loads(sys.argv[1])
    reason = sys.argv[2]
    state = issue["state"]
    names = [label["name"] for label in issue["labels"]]
    issue_author = issue["author"]  # must be present (fail closed); null means a deleted account
    if issue_author is not None and not isinstance(issue_author["login"], str):
        sys.exit(2)
    owner = repo["owner"]["login"]
    raw = issue["comments"]
    if not (isinstance(state, str) and isinstance(raw, list) and all(isinstance(n, str) for n in names)
            and isinstance(owner, str) and owner):
        sys.exit(2)
    comments = []
    for index, item in enumerate(raw):
        body, author, stamp = item["body"], item["author"], item["createdAt"]
        # A deleted account's comment has a null author: it is not the owner's, so it is
        # skipped like any other non-owner comment instead of blocking the whole issue.
        if author is None:
            continue
        login = author["login"]
        if not (isinstance(body, str) and isinstance(login, str) and isinstance(stamp, str) and stamp):
            sys.exit(2)
        if login == owner:
            comments.append((stamp, index, body))
except Exception:
    sys.exit(2)

comments.sort(key=lambda c: (c[0], c[1]))
if state != "OPEN":
    refuse("the issue is not open")

HEX = r"[0-9a-f]{7,40}"

def line_value(body, label, pattern=r".+"):
    match = re.search(r"^" + re.escape(label) + r": (" + pattern + r")[ \t]*$", body, re.M)
    return match.group(1) if match else None

def prefixed(prefix):
    return [c for c in comments if c[2].startswith(prefix)]

def verdict_of(body):
    # team/qa-engineer.md: the comment starts with `QA: PASS` or `QA: FAIL`. A first line
    # that says FAIL anywhere is FAIL; PASS only when the line starts `QA: PASS`, so
    # "QA: NOT PASS" or "QA: did not PASS" is no verdict.
    first = body.split("\n", 1)[0]
    if re.search(r"\bFAIL\b", first):
        return "FAIL"
    return "PASS" if re.match(r"QA: PASS\b", first) else None

if reason == "not-planned":
    for stamp, _, body in prefixed("Orchestrator: Close as not planned"):
        date = line_value(body, "Human approved closure", r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
        review = line_value(body, "Backlog review")
        if date and review:
            sys.exit(0)
    refuse("no owner Orchestrator comment starting 'Orchestrator: Close as not planned' with "
           "'Human approved closure: <YYYY-MM-DD>' and 'Backlog review: <path or URL>' lines")

if "approved" not in names:
    refuse("the issue does not carry the approved label")
tier = "heavy" if "tier:heavy" in names else "light" if (
    "tier:light" in names and "tier:standard" not in names) else "standard"

def close_comment(after_stamp, need_commit):
    """The latest owner Close-layout comment at or after after_stamp, or None."""
    best = None
    for stamp, index, body in prefixed("Orchestrator:"):
        if stamp < after_stamp:
            continue
        if (line_value(body, "Merge commit", HEX) and line_value(body, "Verify")
                and line_value(body, "Summary")
                and (not need_commit or line_value(body, "QA PASS commit", HEX))
                and (need_commit or line_value(body, "Human approved diff", r"yes"))):
            best = (stamp, index, body)
    return best

if tier == "light":
    tier_check = [c for c in prefixed("Engineer:")
                  if re.search(r"^tier-check: PASS", c[2], re.M)]
    if not tier_check:
        refuse("no owner Engineer comment with a 'tier-check: PASS' line (Light)")
    if close_comment(tier_check[-1][0], False) is None:
        refuse("no owner Orchestrator Close comment at or after the tier-check comment with "
               "Merge commit, Verify, Summary and 'Human approved diff: yes' lines (Light)")
    sys.exit(0)

verdicts = [(c, verdict_of(c[2])) for c in prefixed("QA:")]
verdicts = [(c, v) for c, v in verdicts if v]
if not verdicts:
    refuse("no owner QA comment with a PASS verdict")
if verdicts[-1][1] == "FAIL":
    refuse("the latest owner QA verdict is FAIL")
def is_reflection(body):
    # Local deviation (_docs/decisions/2026-11-13T0537Z-close-floor-reflection.md): a comment with a
    # `Reflection:` block and neither work marker is the post-PASS reflection, not new work. Work
    # markers (team/software-engineer.md), either one is enough: a Verify line (any line that starts,
    # after `>`, `*`, `_`, `#`, `-` and spaces, with the word Verify or Verification, however long the
    # label: `Verify:`, `**Verify** (make verify BASE=x): PASS`, `Verify - PASS`, `## Verify`),
    # or a numbered criterion line (`1.`, `1)`, `1:`, `Criterion 1:`, `AC1:`) that says
    # done or not checked. A work comment with a reflection appended has a marker, so it still counts. When in doubt it counts as work: QA re-checks.
    verify = re.search(r"(?im)^[ \t>*_#-]*verif(?:y|ication)\b", body)
    criteria = re.search(r"(?im)^[ \t]*(?:[-*][ \t]+)?(?:(?:criterion|ac)[ \t]*)?\d+[.):].*\b(?:done|not checked)\b", body)
    reflection = re.search(r"(?im)^[ \t>*_#]*reflection[ \t*_]*:", body)
    return bool(reflection) and not (verify or criteria)

engineer = [c for c in prefixed("Engineer:")
            if re.search(r"(?i)\bcommit", c[2])
            and re.search(r"\b" + HEX + r"\b", c[2])  # any 7 to 40 hex, all-digit included
            and not is_reflection(c[2])]
floor = engineer[-1][0] if engineer else ""
passes = [c for c, v in verdicts if v == "PASS" and c[0] >= floor]
needed = 2 if tier == "heavy" else 1
if len(passes) < needed:
    refuse(f"needs {needed} owner QA PASS comment(s) at or after the last Engineer commit comment; found {len(passes)}")
latest = passes[-1]
close = close_comment(latest[0], True)
if close is None:
    refuse("no owner Orchestrator Close comment at or after the latest QA PASS with QA PASS commit, "
           "Merge commit, Verify and Summary lines")
named = line_value(close[2], "QA PASS commit", HEX)
if named not in latest[2]:
    refuse("the QA PASS commit named in the Close comment does not appear in the latest owner QA PASS comment")
sys.exit(0)
PY
verdict=$(printf '%s' "$issue_json" | python3 -B -c "$checker" "$repo_json" "$reason")
code=$?
case "$code" in
  0) ;;
  1) die 4 "refused: $verdict; nothing was closed" ;;
  *) die 4 "cannot tell whether issue $number may be closed; nothing was closed" ;;
esac

if [ "$reason" = "not-planned" ]; then
  gh api "repos/$REPO/issues/$number" --method PATCH -f state=closed -f state_reason=not_planned > /dev/null 2>&1
else
  gh api "repos/$REPO/issues/$number" --method PATCH -f state=closed -f state_reason=completed > /dev/null 2>&1
fi
code=$?
[ "$code" -eq 0 ] || die 1 "gh issue close failed (exit $code); nothing was retried, so check GitHub before closing again"
echo "issue-close: closed issue $number ($reason)"
