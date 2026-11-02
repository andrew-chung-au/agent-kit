"""Checks the human-task template and the task files in _human-tasks/ (issue #50).

check_task takes text and returns a list of problems, so the same function runs
on the real files (must be empty) and on mutated copies (must not be).

Limit: this is a wording test over the template and the files committed in
_human-tasks/. It cannot see what is later written into a copy of the
template, which is why the template says so and QA reads each task file.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
TEMPLATE = KIT / "templates" / "human-task.md"
TASK_DIR = REPO / "_human-tasks"

HEADINGS = ["Purpose", "Where to run it", "Before you start", "Steps", "Record the result", "Risk"]
COMMAND_SECTIONS = ("Before you start", "Steps")
ROLES = ("orchestrator", "pm", "engineer", "qa")

FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
CHAIN = re.compile(r"[;&|]")
SUBSTITUTION = re.compile(r"\$\(|`|\$[A-Za-z_{]")
HEREDOC = re.compile(r"<<")
SECRET = re.compile(
    r"(^|\s)(env|printenv)(\s|$)|\.env\b|gh\s+auth\s+token|/proc/|git\s+credential|--show-token"
)
LEAKS = re.compile(
    r"ghp_[A-Za-z0-9]{20,}|github_pat_|xox[abp]-|AKIA[0-9A-Z]{16}|/home/|/Users/|C:\\"
)
NAME = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{4}Z-human-task-(\d{3}-)?(" + "|".join(ROLES) + r")-"
    r"(?!(" + "|".join(ROLES) + r")-)[a-z][a-z0-9-]*\.md$"
)


def forbidden_in(block: list[str]) -> list[str]:
    hits = []
    for line in block:
        line = line.replace(".env.example", "")
        if CHAIN.search(line):
            hits.append(f"chain operator in {line!r}")
        if SUBSTITUTION.search(line):
            hits.append(f"substitution or variable in {line!r}")
        if HEREDOC.search(line):
            hits.append(f"heredoc in {line!r}")
        if SECRET.search(line):
            hits.append(f"secret-printing command in {line!r}")
    return hits


def parse(text: str):
    """Return (headings, blocks, steps).

    headings: the `## ` titles in order.
    blocks: dicts with section, step (the `### ` title or None), lines, after.
    steps: dicts with title and lines (every line of the step), for `### ` under Steps.
    """
    headings: list[str] = []
    blocks: list[dict] = []
    steps: list[dict] = []
    section = None
    step = None
    fence = None
    current = None
    for line in text.splitlines():
        match = FENCE.match(line)
        if fence:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                fence = None
            else:
                current["lines"].append(line)
            continue
        if match:
            fence = match.group(1)
            current = {"section": section, "step": step, "lines": [], "after": []}
            blocks.append(current)
            if section == "Steps" and steps:
                steps[-1]["blocks"] += 1
            continue
        if line.startswith("## "):
            section = line[3:].strip()
            headings.append(section)
            step = None
            current = None
            continue
        if line.startswith("### "):
            step = line[4:].strip()
            current = None
            if section == "Steps":
                steps.append({"title": step, "lines": [], "blocks": 0})
            continue
        if current is not None:
            current["after"].append(line)
        if section == "Steps" and steps:
            steps[-1]["lines"].append(line)
    return headings, blocks, steps


def has_line(lines: list[str], label: str) -> bool:
    return any(line.startswith(label) for line in lines)


def check_task(text: str, strict: bool) -> list[str]:
    """Problems in a task file. strict: no forbidden command anywhere (the template)."""
    problems: list[str] = []
    headings, blocks, steps = parse(text)
    if headings != HEADINGS:
        problems.append(f"headings are {headings}, expected {HEADINGS}")
    if not steps:
        problems.append("Steps has no `### ` step")
    for block in blocks:
        if block["section"] in COMMAND_SECTIONS and not has_line(block["after"], "Expected:"):
            problems.append(f"{block['step'] or block['section']}: block has no Expected: line")
    for step in steps:
        if step["blocks"] != 1:
            problems.append(f"{step['title']}: {step['blocks']} command blocks, expected 1")
        if not has_line(step["lines"], "If different:"):
            problems.append(f"{step['title']}: no If different: line")
    for block in blocks:
        hits = forbidden_in(block["lines"])
        if not hits:
            continue
        step = next((s for s in steps if s["title"] == block["step"]), None)
        exempt = (
            not strict
            and block["section"] == "Steps"
            and step is not None
            and has_line(step["lines"], "Refusal test:")
            and has_line(step["lines"], "Risk:")
        )
        if not exempt:
            problems += [f"{block['step'] or block['section']}: {hit}" for hit in hits]
    leak = LEAKS.search(text)
    if leak:
        problems.append(f"possible secret or private path: {leak.group(0)!r}")
    return problems


def check_template(text: str) -> list[str]:
    problems = check_task(text, strict=True)
    for phrase in ("reject one prompt at a time", "rejecting ends the agent's turn", "`!`", "Refusal test:"):
        if phrase not in text:
            problems.append(f"missing wording {phrase!r}")
    return problems


STEP = (
    "### Step {n}: Do the thing\n\n```\n{command}\n```\n\n"
    "Expected: it works.\nIf different: stop.\n{extra}\n"
)


def task(command: str = "git status --short", extra: str = "") -> str:
    return (
        "# Title\n\n## Purpose\n\nx. Issue: none.\n\n## Where to run it\n\nhere\n\n"
        "## Before you start\n\n1. Check.\n\n```\ngit log --oneline -1\n```\n\nExpected: a line.\n\n"
        "## Steps\n\n" + STEP.format(n=1, command=command, extra=extra) +
        "## Record the result\n\n| 1 | | |\n\n## Risk\n\nnone\n"
    )


class TemplateTest(unittest.TestCase):
    def setUp(self):
        self.text = TEMPLATE.read_text(encoding="utf-8")

    def test_real_template_passes(self):
        self.assertEqual(check_template(self.text), [])

    def test_removed_heading_fails(self):
        for name in HEADINGS:
            mutated = self.text.replace(f"## {name}\n", "")
            self.assertTrue(check_template(mutated), name)

    def test_reordered_headings_fail(self):
        mutated = self.text.replace("## Steps\n", "## TMP\n").replace("## Risk\n", "## Steps\n")
        mutated = mutated.replace("## TMP\n", "## Risk\n")
        self.assertTrue(check_template(mutated))

    def test_step_without_expected_fails(self):
        head, _, tail = self.text.rpartition("Expected:")
        self.assertTrue(check_template(head + "Result:" + tail))

    def test_step_without_if_different_fails(self):
        self.assertTrue(check_template(self.text.replace("If different:", "Otherwise:")))

    def test_secret_command_in_a_block_fails(self):
        for bad in ("cat .env", "gh auth token", "printenv", "env", "head -n 1 /proc/self/environ"):
            self.assertTrue(check_template(self.text.replace("<one command>", bad, 1)), bad)

    def test_chain_substitution_variable_heredoc_fail(self):
        for bad in ("ls ; pwd", "ls && pwd", "ls | head", "ls $(pwd)", "ls $HOME", "cat <<EOF"):
            self.assertTrue(check_template(self.text.replace("<one command>", bad, 1)), bad)

    def test_dropped_wording_fails(self):
        for phrase in ("reject one prompt at a time", "Refusal test:"):
            self.assertTrue(check_template(self.text.replace(phrase, "x")), phrase)

    def test_template_has_no_exemption(self):
        refusal = "Refusal test: yes, in a session.\nRisk: would print a token."
        mutated = self.text.replace("<one command>", "gh auth token", 1)
        mutated = mutated.replace("Risk: <only", refusal + "\nRisk: <only")
        self.assertTrue(check_template(mutated))


class TaskFileTest(unittest.TestCase):
    def test_a_plain_task_passes(self):
        self.assertEqual(check_task(task(), strict=False), [])

    def test_a_runnable_gh_auth_token_step_is_refused(self):
        self.assertTrue(check_task(task("gh auth token"), strict=False))

    def test_a_refusal_step_needs_both_marker_and_risk(self):
        marker = "Refusal test: yes, in an OpenCode session without the `!` prefix.\n"
        risk = "Risk: would print a token if the rule fails.\n"
        self.assertEqual(check_task(task("gh auth token", marker + risk), strict=False), [])
        self.assertTrue(check_task(task("gh auth token", marker), strict=False))
        self.assertTrue(check_task(task("gh auth token", risk), strict=False))
        self.assertTrue(check_task(task("gh auth token", marker + risk), strict=True))

    def test_an_exempt_step_does_not_cover_another_step(self):
        marker = "Refusal test: yes.\nRisk: x.\n"
        second = STEP.format(n=2, command="cat .env", extra="")
        text = task("ls ; pwd", marker).replace("## Record the result", second + "## Record the result")
        self.assertTrue(check_task(text, strict=False))

    def test_a_before_you_start_block_has_no_exemption(self):
        text = task().replace("git log --oneline -1", "gh auth token")
        self.assertTrue(check_task(text, strict=False))

    def test_two_commands_in_one_step_fail(self):
        extra = "```\ngit status\n```\n"
        self.assertTrue(check_task(task("git log", extra), strict=False))

    def test_a_private_path_or_token_fails(self):
        self.assertTrue(check_task(task() + "\nSee /home/someone/x\n", strict=False))
        self.assertTrue(check_task(task() + "\nghp_" + "a" * 30 + "\n", strict=False))

    def test_committed_task_files_pass(self):
        files = sorted(TASK_DIR.glob("*.md"))
        self.assertTrue(files, "no task files in _human-tasks/")
        for path in files:
            with self.subTest(path.name):
                self.assertRegex(path.name, NAME)
                self.assertEqual(check_task(path.read_text(encoding="utf-8"), strict=False), [])

    def test_file_names_follow_the_convention(self):
        good = "2026-11-02T1200Z-human-task-047-engineer-opencode-by-hand-checks.md"
        self.assertRegex(good, NAME)
        self.assertRegex("2026-11-02T1200Z-human-task-engineer-push-review.md", NAME)
        for bad in (
            "2026-11-02T1200Z-human-task-047-engineer-123.md",
            "2026-11-02T1200Z-human-task-engineer-qa-checks.md",
            "2026-11-02T1200Z-human-task-47-engineer-checks.md",
            "2026-11-02T1200Z-human-task-047-human-checks.md",
        ):
            self.assertNotRegex(bad, NAME)


class DocsTest(unittest.TestCase):
    def read(self, *parts: str) -> str:
        return REPO.joinpath(*parts).read_text(encoding="utf-8")

    def test_session_summary_pins_the_kind_and_folder(self):
        text = self.read("agent-kit", "procedures", "session-summary.md")
        self.assertRegex(text, r"(?m)^\| `human-task` \|.*\| optional.*\|")
        self.assertIn("_human-tasks/", text)
        self.assertIn("`human-task`", text.split("To parse a name", 1)[1])

    def test_indexes_list_the_entry_type(self):
        for path in (("_docs", "index.md"), ("agent-kit", "templates", "docs-index.md")):
            text = self.read(*path)
            self.assertRegex(text, r"(?m)^\| Human task \| `_human-tasks/` \|", path)
            self.assertIn("human-task.md", text)

    def test_process_rule_and_blueprint_row(self):
        process = self.read("agent-kit", "process.md")
        self.assertIn("`_human-tasks/`", process)
        self.assertIn("templates/human-task.md", process)
        blueprints = self.read("agent-kit", "blueprints.md")
        self.assertRegex(blueprints, r"(?m)^\| Human task files \|.*`_human-tasks/`.*`templates/human-task\.md`")


if __name__ == "__main__":
    unittest.main()
