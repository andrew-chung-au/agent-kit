#!/usr/bin/env python3
"""Route the failing findings of an issue's latest QA comment by points (issue #199).

Run from the project folder as `make route-findings N=<issue number>`: the target first
writes .scratch/issue-<n>.json as `make settings N=<n>` does, then runs
    python3 -B <kit>/scripts/route-findings.py <n>
It is read-only: it reads agent-kit.conf and the dump as data, writes nothing and starts no
process. The rules are in customizing.md (points) and process.md (Lifecycle, step 6).

What it reads, all through check-format.py (loaded by path from this folder), so there is
one parser: the settings, with read_settings at the issue level (load_issue_settings); every
owner `QA:` comment of the dump, oldest first (owner_qa_comments), each parsed with the `qa`
row of check-format (read_qa); and whether a finding fails (finding_fails).

Terms:
- A finding's chain is the finding plus every finding linked to it by `Related:`, in either
  direction and through any number of links, across all owner QA: comments.
- A chain's failures are the owner QA: comments in which at least one finding of the chain
  fails (each comment counted once); its rounds are its failures minus 1.
- Points are the finding's effort as last posted (S=1, R=2, E=3: the grade table in
  customizing.md) plus its chain's rounds. Fix checks add none.
- Route, in this order: `Category: criterion` -> human; a matching SHIP_RULE -> ship; points
  at or above ASK_AT -> human; otherwise engineer. A ship rule matches when every key it
  names holds: impact at or below `impact:`, effort at or above `effort:`, rounds at or
  above `rounds:`. SHIP_RULE=none never matches.
- guard is `yes` when the chain has two or more failures (the patchwork guard).

Output: one line per failing finding of the latest owner QA: comment, in its order,
    <id> points <p> rounds <r> route <engineer|human|ship> guard <yes|no>
or `none` when that comment is `QA: PASS` or there is no owner QA: comment; exit 0.
A refusal prints one line on standard error, `route-findings: <place>: <reason>`, and exits
1: a missing or unreadable dump, a settings refusal, or a latest QA: comment that
`make check-format KIND=qa` would refuse (its first problem). Earlier QA: comments are read
as far as they parse; a block whose impact, effort or scope is not allowed is passed over.
A usage error exits 2. Standard library only.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

_CHECK_FORMAT_PATH = Path(__file__).resolve().parent / "check-format.py"
_spec = importlib.util.spec_from_file_location("kit_check_format_for_route_findings", _CHECK_FORMAT_PATH)
check_format = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_format)

PROG = "route-findings"
USAGE = "Usage: make route-findings N=<issue number>"
IMPACTS = check_format.LMC[1]
EFFORTS = check_format.SRE[1]
# The grade table's points (customizing.md, Grades): S=1, R=2, E=3, in the Effort order.
EFFORT_POINTS = {effort: position + 1 for position, effort in enumerate(EFFORTS)}


def chains_of(comments: list) -> dict:
    """finding id -> the set of ids in its chain, over the findings of every comment."""
    links = {}
    for findings in comments:
        for finding in findings:
            links.setdefault(finding["id"], set())
            related = finding.get("related", "none")
            if related != "none":
                links[finding["id"]].add(related)
                links.setdefault(related, set()).add(finding["id"])
    chains = {}
    for start in links:
        if start in chains:
            continue
        seen, todo = {start}, [start]
        while todo:
            for other in links[todo.pop()]:
                if other not in seen:
                    seen.add(other)
                    todo.append(other)
        for member in seen:
            chains[member] = seen
    return chains


def ship_rule_matches(rule: str, finding: dict, rounds: int) -> bool:
    """SHIP_RULE (already checked by read_settings) against one finding and its rounds."""
    if rule == "none":
        return False
    keys = dict(pair.split(":", 1) for pair in rule.split(","))
    if "impact" in keys and IMPACTS.index(finding["impact"]) > IMPACTS.index(keys["impact"]):
        return False
    if "effort" in keys and EFFORTS.index(finding["effort"]) < EFFORTS.index(keys["effort"]):
        return False
    if "rounds" in keys and rounds < int(keys["rounds"]):
        return False
    return True


def route(number: int, values: dict, bodies: list) -> list:
    """The output lines for issue `number`, or raise CheckError for a refused latest comment."""
    if not bodies:
        return ["none"]
    earlier = bodies[:-1]
    known = check_format.finding_ids(earlier, number)
    problems, verdict, latest = check_format.read_qa(bodies[-1], number, values, known)
    if problems:
        line, reason = problems[0]
        raise check_format.CheckError(f"issue #{number} latest QA: comment line {line}", reason)
    if verdict == "PASS":
        return ["none"]
    comments = []
    for body in earlier:
        findings = check_format.read_qa(body, number)[2]
        comments.append([f for f in findings if "id" in f and check_format.gradable(f)])
    comments.append(latest)
    chains = chains_of(comments)
    ask_at = int(check_format.setting(values, "ASK_AT"))
    rule = check_format.setting(values, "SHIP_RULE")
    out = []
    for finding in latest:
        if not check_format.finding_fails(finding, values):
            continue
        chain = chains[finding["id"]]
        failures = sum(1 for findings in comments
                       if any(f["id"] in chain and check_format.finding_fails(f, values) for f in findings))
        rounds = failures - 1
        points = EFFORT_POINTS[finding["effort"]] + rounds
        if finding["category"] == "criterion":
            where = "human"
        elif ship_rule_matches(rule, finding, rounds):
            where = "ship"
        elif points >= ask_at:
            where = "human"
        else:
            where = "engineer"
        guard = "yes" if failures >= 2 else "no"
        out.append(f"{finding['id']} points {points} rounds {rounds} route {where} guard {guard}")
    return out


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1 or not re.fullmatch(check_format.ISSUE, args[0]):
        print(USAGE, file=sys.stderr)
        return 2
    number = int(args[0])
    try:
        values, issue = check_format.load_issue_settings(number)
        lines = route(number, values, check_format.owner_qa_comments(issue))
    except check_format.CheckError as error:
        print(f"{PROG}: {error.place}: {error.reason}", file=sys.stderr)
        return 1
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
