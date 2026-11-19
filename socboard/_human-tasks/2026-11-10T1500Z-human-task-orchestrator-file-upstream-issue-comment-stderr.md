# File an upstream kit issue: issue-comment.sh hides gh's error

## Purpose

Raise one finding with the agent kit's maintainers: when posting a comment fails, the kit's script throws away gh's error output, so the cause is invisible. Decided on 2026-11-10 (`decide-upstream-kit-issues`). Issue: none in this repository.

## Where to run it

In a browser, in the kit's own issue tracker. Not here: this sandbox cannot reach that tracker, and nothing in this repository changes. Do not patch the script locally; the kit's files are protected and a local change would make the kit a derivative.

## Before you start

1. Confirm the line is still the same in this project's kit copy.

```
grep -n 'method POST.*2> /dev/null' _docs/agent-kit/scripts/issue-comment.sh
```

Expected: one line ending in `2> /dev/null < <(printf '%s' "$CONTENT"))` (line 85 when this was written). The first version of this check searched for `comments --method POST`, which matches only the code comment on line 21, because the real line has a quote between `comments` and `--method`.

## Steps

### Step 1: Open a new issue in the kit's tracker with this text

Title: `issue-comment.sh discards gh's stderr, so a failed post shows no cause`

Body (paste as is):

> In `scripts/issue-comment.sh`, the POST that posts the comment runs `gh api "repos/$REPO/issues/$number/comments" --method POST -F body=@- 2> /dev/null`. The two reads before it (`github_api.py head` and `owner`) also send stderr to `/dev/null`. When a post fails, the script reports only its own exit message, and gh's reason (for example HTTP 403 because the token cannot write to that repository) is lost.
>
> Seen in a project on 2026-11-10: a QA agent in the dev container failed to post several times (`make issue-comment` exit 1). A probe against a non-existent issue returned 404, which looked like proof the token could write; it was not, because GitHub returns 404 before it checks permission. The real cause, the token's repository access, showed only when a debug copy of the script kept gh's stderr and printed 403.
>
> Proposal: on a failed POST (and on the two reads), print gh's stderr to the user, after removing anything that looks like a token, instead of discarding it. Expected effect: the cause is visible on the first failure. Measure: rounds of diagnosis before a failed post is understood.

Expected: the issue is filed.

## Record the result

| Step | Pass or fail | Output or note |
|---|---|---|
| Before you start | Pass | Checked by the orchestrator on 2026-11-10: line 85 is still `out=$(gh api "repos/$REPO/issues/$number/comments" --method POST -F body=@- 2> /dev/null < <(printf '%s' "$CONTENT"))`. The check's first pattern was wrong and is corrected above. |
| 1 | Pass | Filed by the human in the kit's tracker on 2026-11-10: https://github.com/andrew-chung-au/agent-kit/issues/187 (open). The body is the finding only, as drafted. |

## Risk

None to this project. The text has no secrets and no private paths.
