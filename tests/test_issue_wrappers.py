"""Tests for issue-create.sh, issue-comment.sh and the two make targets (issue #44).

No network and no real GitHub. A fake `gh` is first on PATH. It logs every call
as one JSON line, records the standard input it receives, and answers from a
config file, so the refused cases can show that gh was never run and the
successful ones that only the four allowed call shapes were made.

Script tests run in a throwaway project folder under .scratch/ (a copy of the
kit's scripts/, an agent-kit.conf and a .scratch/ folder). Make tests run the
repo's own Makefile in the repo, with their files in a folder under .scratch/.

Exit codes: 1 gh failed, 2 bad argument or file, 3 the scanner refused,
4 the target issue is not allowed.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path

from kit_repo import build_env, new_workdir
from secret_fixtures import MATCH

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
URL = "https://github.com/example/repo/issues/99"
BODY_TOKEN = "UNIQUE-BODY-TOKEN-4711"

FAKE_GH = """\
#!/usr/bin/env python3
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
with open(os.path.join(here, "calls.log"), "a") as log:
    log.write(json.dumps(args) + "\\n")
config = json.load(open(os.path.join(here, "config.json")))
kind = {("issue", "view"): "issue_view", ("repo", "view"): "repo_view",
        ("issue", "create"): "create", ("issue", "comment"): "comment"}.get(tuple(args[:2]), "other")
if kind in ("create", "comment"):
    with open(os.path.join(here, "stdin.bin"), "ab") as out:
        out.write(sys.stdin.buffer.read())
entry = config.get(kind, {})
sys.stdout.write(entry.get("stdout", ""))
sys.exit(entry.get("exit", 0))
"""

SPY_SCANNER = """\
#!/usr/bin/env bash
here=$(dirname "$0")
printf '%s\\n' "$@" > "$here/scanner-args.txt"
cat > "$here/scanned.bin"
if [ -n "${SPY_SWAP:-}" ]; then printf 'QA: SWAPPED AFTER THE SCAN\\n' > "$SPY_SWAP"; fi
exit "${SPY_EXIT:-0}"
"""

APPROVED_ISSUE = json.dumps({"labels": [{"name": "approved"}], "author": {"login": "someone-else"}})
OWNER = json.dumps({"owner": {"login": "the-owner"}})

CREATE_OK = "Title: A fine title\n\nBody line one.\nBody line two.\n"
COMMENT_OK = "QA: PASS\n\nChecked every criterion.\n"


def allowed_shape(argv: list) -> bool:
    """The only four gh calls the wrappers may make."""
    return (
        (len(argv) == 6 and argv[:3] == ["issue", "create", "--title"] and argv[4:] == ["--body-file", "-"]
         and not argv[3].startswith("-"))
        or (len(argv) == 5 and argv[:2] == ["issue", "comment"] and re.fullmatch(r"[1-9][0-9]{0,8}", argv[2])
            and argv[3:] == ["--body-file", "-"])
        or (len(argv) == 5 and argv[:2] == ["issue", "view"] and re.fullmatch(r"[1-9][0-9]{0,8}", argv[2])
            and argv[3:] == ["--json", "labels,author"])
        or argv == ["repo", "view", "--json", "owner"]
    )


class FakeGhMixin:
    """A fake gh in its own folder, a throwaway work area and helpers to read what it saw."""

    def make_gh(self):
        self.work = new_workdir(prefix="wrap-")
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.ghdir = self.work / "gh-bin"
        self.ghdir.mkdir()
        gh = self.ghdir / "gh"
        gh.write_text(FAKE_GH, encoding="utf-8")
        gh.chmod(0o755)
        self.config()
        self.env = build_env(self.work)
        self.env["PATH"] = f"{self.ghdir}{os.pathsep}{self.env['PATH']}"

    def config(self, **overrides):
        config = {"issue_view": {"stdout": APPROVED_ISSUE}, "repo_view": {"stdout": OWNER},
                  "create": {"stdout": URL + "\n"}, "comment": {"stdout": URL + "#issuecomment-1\n"}}
        config.update(overrides)
        (self.ghdir / "config.json").write_text(json.dumps(config), encoding="utf-8")
        self.reset_logs()

    def reset_logs(self):
        for name in ("calls.log", "stdin.bin"):
            (self.ghdir / name).unlink(missing_ok=True)

    def calls(self):
        log = self.ghdir / "calls.log"
        return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []

    def writes(self):
        return [c for c in self.calls() if c[:2] in (["issue", "create"], ["issue", "comment"])]

    def gh_stdin(self):
        path = self.ghdir / "stdin.bin"
        return path.read_bytes() if path.exists() else b""

    def no_gh_path(self):
        """A PATH holding the tools the scripts need and no gh."""
        folder = self.work / "no-gh-bin"
        folder.mkdir(exist_ok=True)
        for tool in ("bash", "head", "base64", "tr", "wc", "python3", "grep", "dirname", "cat", "env"):
            found = shutil.which(tool)
            if found and not (folder / tool).exists():
                (folder / tool).symlink_to(found)
        return str(folder)


class ScriptBase(FakeGhMixin, unittest.TestCase):
    def setUp(self):
        self.make_gh()
        self.project = self.work / "project"
        self.project.mkdir()
        self.scripts = self.project / "agent-kit" / "scripts"
        shutil.copytree(KIT / "scripts", self.scripts, ignore=shutil.ignore_patterns("__pycache__"))
        (self.project / "agent-kit.conf").write_text('KIT_DIR="agent-kit"\n', encoding="utf-8")
        (self.project / ".scratch").mkdir()
        self.marker = self.project / ".scratch" / "marker"

    def put(self, data, name="t.md"):
        path = self.project / ".scratch" / name
        path.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
        return f".scratch/{name}"

    def run_script(self, script, *args, env=None):
        return subprocess.run(["bash", f"agent-kit/scripts/{script}", *args], cwd=str(self.project),
                              env=env or self.env, stdin=subprocess.DEVNULL, capture_output=True)

    def create(self, file, **kw):
        return self.run_script("issue-create.sh", file, **kw)

    def comment(self, number, file, **kw):
        return self.run_script("issue-comment.sh", number, file, **kw)

    @staticmethod
    def shown(done):
        return (done.stdout + done.stderr).decode("utf-8", "replace")

    def assert_refused(self, done, code):
        """Refused before anything reached GitHub: exit code, no stdout, no gh call, no marker."""
        self.assertEqual(done.returncode, code, self.shown(done))
        self.assertEqual(done.stdout, b"")
        self.assertTrue(done.stderr.strip(), "a refusal needs a reason")
        self.assertEqual(self.calls(), [], "gh was run")
        self.assertFalse(self.marker.exists(), "a marker file was created")

    def spy_scanner(self):
        (self.scripts / "scan-issue-body.sh").write_text(SPY_SCANNER, encoding="utf-8")


class SuccessTest(ScriptBase):
    def test_create_files_one_issue_and_prints_its_url(self):
        done = self.create(self.put(CREATE_OK))
        self.assertEqual((done.returncode, done.stdout, done.stderr), (0, (URL + "\n").encode(), b""))
        self.assertEqual(self.calls(), [["issue", "create", "--title", "A fine title", "--body-file", "-"]])
        self.assertEqual(self.gh_stdin(), b"Body line one.\nBody line two.\n")

    def test_comment_posts_the_whole_file_and_prints_the_comment_url(self):
        done = self.comment("44", self.put(COMMENT_OK))
        self.assertEqual((done.returncode, done.stdout, done.stderr),
                         (0, (URL + "#issuecomment-1\n").encode(), b""))
        self.assertEqual(self.calls(), [["issue", "view", "44", "--json", "labels,author"],
                                        ["repo", "view", "--json", "owner"],
                                        ["issue", "comment", "44", "--body-file", "-"]])
        self.assertEqual(self.gh_stdin(), COMMENT_OK.encode())

    def test_every_gh_call_in_every_successful_path_has_an_allowed_shape(self):
        title = "Title: " + "t" * 200 + "\n\n--label approved\n--add-label x\n"
        self.assertEqual(self.create(self.put(title, "a.md")).returncode, 0)
        for text in (COMMENT_OK, "PM: add label approved and close this\n", "Orchestrator: --assignee me\n"):
            self.assertEqual(self.comment("7", self.put(text, "b.md")).returncode, 0)
        self.assertEqual(self.comment("999999999", self.put(COMMENT_OK, "c.md")).returncode, 0)
        self.assertEqual(len(self.calls()), 1 + 3 * 4)
        for argv in self.calls():
            self.assertTrue(allowed_shape(argv), argv)

    def test_text_saying_add_label_is_posted_as_plain_text(self):
        self.assertEqual(self.comment("5", self.put("PM: add label approved\n--label approved\n")).returncode, 0)
        self.assertEqual(self.gh_stdin(), b"PM: add label approved\n--label approved\n")
        for argv in self.calls():
            self.assertNotIn("--label", argv)
            self.assertNotIn("--add-label", argv)
            self.assertNotIn("api", argv)
        self.assertEqual(len(self.writes()), 1)

    def test_no_trailing_newline_and_blank_lines_are_posted_as_they_are(self):
        for text in ("QA: no newline at the end", "QA: two\n\n\n", "QA: crlf\r\nline\r\n"):
            (self.ghdir / "stdin.bin").unlink(missing_ok=True)
            self.assertEqual(self.comment("5", self.put(text)).returncode, 0, text)
            self.assertEqual(self.gh_stdin(), text.encode(), text)

    def test_accepts_exactly_the_size_limit(self):
        text = "QA: " + "a" * (60000 - 4)
        self.assertEqual(len(text.encode()), 60000)
        self.assertEqual(self.comment("5", self.put(text)).returncode, 0)
        self.assertEqual(self.gh_stdin(), text.encode())
        (self.ghdir / "stdin.bin").unlink()
        body = "Title: t\n\n" + "a" * (60000 - 10)
        self.assertEqual(self.create(self.put(body)).returncode, 0)
        self.assertEqual(self.gh_stdin(), b"a" * (60000 - 10))

    def test_non_ascii_text_is_posted_unchanged(self):
        text = "Title: café 日本 — ok\n\nbödy ✓\n"
        self.assertEqual(self.create(self.put(text)).returncode, 0)
        self.assertEqual(self.calls()[0][3], "café 日本 — ok")
        self.assertEqual(self.gh_stdin(), "bödy ✓\n".encode())


class NumberTest(ScriptBase):
    def test_bad_numbers_are_refused_before_gh(self):
        marker = ".scratch/marker"
        bad = ["", "0", "007", "-1", "+1", "1e3", "1.5", " 1", "1 ", "1 2", "1234567890", "--help", "-",
               f"1; touch {marker}", f"$(touch {marker})", f"`touch {marker}`", 'a"b', "1'", "1\n",
               f"1\ntouch {marker}", "０", "١"]
        file = self.put(COMMENT_OK)
        for value in bad:
            with self.subTest(n=value):
                self.assert_refused(self.comment(value, file), 2)

    def test_missing_number_is_a_usage_error(self):
        self.assert_refused(self.run_script("issue-comment.sh", self.put(COMMENT_OK)), 2)
        self.assert_refused(self.run_script("issue-comment.sh"), 2)
        self.assert_refused(self.run_script("issue-comment.sh", "1", "2", "3"), 2)

    def test_nine_digits_is_the_largest_number(self):
        self.assertEqual(self.comment("999999999", self.put(COMMENT_OK)).returncode, 0)
        self.assertEqual(self.comment("1", self.put(COMMENT_OK)).returncode, 0)


class FileArgumentTest(ScriptBase):
    """Every FILE rule, for both scripts."""

    def both(self, file, code=2):
        with self.subTest(script="create", file=file):
            self.assert_refused(self.create(file), code)
        with self.subTest(script="comment", file=file):
            self.assert_refused(self.comment("5", file), code)

    def test_bad_paths(self):
        self.put(COMMENT_OK, "real.md")
        (self.project / ".scratch" / "dir").mkdir()
        (self.project / "outside.md").write_text(COMMENT_OK, encoding="utf-8")
        for file in ["", "--help", "-", "-x", ".scratch/a b", "/etc/hostname", ".scratch/../Makefile",
                     "outside.md", "./outside.md", ".scratchx/a.md", ".scratch", ".scratch/", ".scratch/..",
                     ".scratch/nope.md", ".scratch/dir", ".scratch/dir/", "~/x.md", ".scratch/real.md/",
                     ".scratch/a;touch .scratch/marker", ".scratch/$(touch .scratch/marker)",
                     ".scratch/`touch .scratch/marker`", ".scratch/a\nb", ".scratch/a'b", '.scratch/a"b',
                     ".scratch/a\tb", ".scratch/a*", ".scratch/réal.md", ".scratch/a..b.md/../real.md"]:
            self.both(file)

    def test_missing_file_argument(self):
        self.assert_refused(self.run_script("issue-create.sh"), 2)
        self.assert_refused(self.run_script("issue-create.sh", "a", "b"), 2)
        self.assert_refused(self.run_script("issue-comment.sh", "5"), 2)

    def test_symlinks_are_refused(self):
        self.put(COMMENT_OK, "real.md")
        (self.project / "outside.md").write_text(COMMENT_OK, encoding="utf-8")
        scratch = self.project / ".scratch"
        (scratch / "link.md").symlink_to("real.md")
        (scratch / "outside-link.md").symlink_to(self.project / "outside.md")
        (scratch / "dangling.md").symlink_to("nowhere.md")
        (scratch / "realdir").mkdir()
        (scratch / "realdir" / "x.md").write_text(COMMENT_OK, encoding="utf-8")
        (scratch / "dirlink").symlink_to("realdir")
        for file in (".scratch/link.md", ".scratch/outside-link.md", ".scratch/dangling.md",
                     ".scratch/dirlink/x.md"):
            self.both(file)

    def test_scratch_itself_a_symlink_is_refused(self):
        real = self.project / "elsewhere"
        (self.project / ".scratch").rename(real)
        (real / "x.md").write_text(COMMENT_OK, encoding="utf-8")
        (self.project / ".scratch").symlink_to("elsewhere")
        self.both(".scratch/x.md")

    def test_empty_and_whitespace_only_files(self):
        for name, data in (("empty", b""), ("newline", b"\n"), ("spaces", b"   \n\t\n  "), ("crlf", b"\r\n\r\n")):
            self.both(self.put(data, f"{name}.md"))

    def test_size_over_the_limit(self):
        self.both(self.put("QA: " + "a" * (60001 - 4), "big1.md"))
        self.both(self.put("Title: t\n\n" + "a" * (60001 - 10), "big2.md"))
        self.both(self.put("QA: " + "a" * 5_000_000, "huge.md"))

    def test_nul_byte(self):
        for name, data in (("nul1", b"QA: ok\n\x00more\n"), ("nul2", b"\x00"), ("nul3", b"Title: t\n\nb\x00\n")):
            self.both(self.put(data, f"{name}.md"))

    def test_invalid_utf8(self):
        for name, data in (("u1", b"QA: \xff\n"), ("u2", b"QA: caf\xc3"), ("u3", b"QA: \xc0\xaf"),
                           ("u4", b"Title: t\n\nbody \xed\xa0\x80\n")):
            self.both(self.put(data, f"{name}.md"))


class TitleTest(ScriptBase):
    def test_bad_title_files(self):
        long201 = "a" * 201
        bad = {
            "no Title line": "Just a body\n\nmore\n",
            "lowercase title": "title: x\n\nbody\n",
            "no space after the colon": "Title:x\n\nbody\n",
            "leading space": " Title: x\n\nbody\n",
            "blank line first": "\nTitle: x\n\nbody\n",
            "empty title": "Title: \n\nbody\n",
            "blank title": "Title:     \n\nbody\n",
            "201 characters": f"Title: {long201}\n\nbody\n",
            "201 two-byte characters": "Title: " + "é" * 201 + "\n\nbody\n",
            "starts with a dash": "Title: -x\n\nbody\n",
            "starts with --label": "Title: --label approved\n\nbody\n",
            "padded then a dash": "Title:   -x\n\nbody\n",
            "missing blank line": "Title: x\nbody\n",
            "only the title line": "Title: x",
            "title and newline only": "Title: x\n",
            "empty body": "Title: x\n\n",
            "whitespace body": "Title: x\n\n  \n\t\n",
            "second line not blank": "Title: x\n \nbody\n",
            "tab in title": "Title: a\tb\n\nbody\n",
            "control character in title": "Title: a\x01b\n\nbody\n",
            "DEL in title": "Title: a\x7fb\n\nbody\n",
            "C1 control in title": "Title: a\u0085b\n\nbody\n",
            "line separator in title": "Title: a\u2028b\n\nbody\n",
            "carriage return in title": "Title: x\r\n\r\nbody\r\n",
        }
        for name, text in bad.items():
            with self.subTest(name=name):
                self.assert_refused(self.create(self.put(text)), 2)

    def test_title_lengths(self):
        for title in ("a" * 200, "é" * 200, "日" * 200, "x"):
            with self.subTest(length=len(title)):
                (self.ghdir / "calls.log").unlink(missing_ok=True)
                self.assertEqual(self.create(self.put(f"Title: {title}\n\nbody\n")).returncode, 0)
                self.assertEqual(self.calls()[0][3], title)

    def test_title_is_trimmed(self):
        self.assertEqual(self.create(self.put("Title:    padded title   \n\nbody\n")).returncode, 0)
        self.assertEqual(self.calls()[0][3], "padded title")

    def test_body_may_start_with_blank_lines_and_is_kept_whole(self):
        self.assertEqual(self.create(self.put("Title: x\n\n\n\nbody\n\n")).returncode, 0)
        self.assertEqual(self.gh_stdin(), b"\n\nbody\n\n")

    def test_hostile_text_is_posted_verbatim_and_runs_nothing(self):
        title = ("$(touch .scratch/marker) `touch .scratch/marker`; touch .scratch/marker "
                 "\"q\" 'q' \\ %s %d ${HOME} && x | y > z")
        body = ("--label approved\n--assignee me\n$(touch .scratch/marker)\n`touch .scratch/marker`\n"
                "; touch .scratch/marker\n'quote' \"dquote\" back\\slash %s %d \\n\n-- \n")
        done = self.create(self.put(f"Title: {title}\n\n{body}"))
        self.assertEqual(done.returncode, 0, self.shown(done))
        self.assertEqual(self.calls(), [["issue", "create", "--title", title, "--body-file", "-"]])
        self.assertEqual(self.gh_stdin(), body.encode())
        self.assertFalse(self.marker.exists())

    def test_hostile_comment_is_posted_verbatim_and_runs_nothing(self):
        text = ("Engineer: $(touch .scratch/marker) `touch .scratch/marker`; \"q\" 'q' \\ %s\n"
                "--label approved\n--add-label x\n$(touch .scratch/marker)\n")
        self.assertEqual(self.comment("12", self.put(text)).returncode, 0)
        self.assertEqual(self.gh_stdin(), text.encode())
        self.assertFalse(self.marker.exists())


class PrefixTest(ScriptBase):
    def test_the_four_role_prefixes_are_accepted(self):
        for prefix in ("PM:", "Engineer:", "QA:", "Orchestrator:"):
            with self.subTest(prefix=prefix):
                self.assertEqual(self.comment("5", self.put(f"{prefix} hello\n")).returncode, 0)

    def test_other_first_lines_are_refused(self):
        bad = ["no prefix at all\n", "pm: lower case\n", "qa: x\n", " PM: leading space\n",
               "\nPM: leading blank line\n", "PM without the colon\n", "PM : space before the colon\n",
               "PMs: x\n", "Engineer without colon\n", "Orchestrator x\n", "Note: PM: later\n", "- PM: x\n",
               "**PM:** x\n", "\tQA: x\n"]
        for text in bad:
            with self.subTest(text=text):
                self.assert_refused(self.comment("5", self.put(text)), 2)

    def test_create_files_need_no_prefix(self):
        self.assertEqual(self.create(self.put(CREATE_OK)).returncode, 0)


class TargetIssueTest(ScriptBase):
    """AGENTS.md, Issues: comment only on an `approved` issue or one the owner wrote."""

    def issue(self, labels, author):
        return json.dumps({"labels": [{"name": n} for n in labels], "author": {"login": author}})

    def posts(self, **config):
        self.config(**config)
        return self.comment("5", self.put(COMMENT_OK))

    def assert_not_posted(self, done):
        self.assertEqual(done.returncode, 4, self.shown(done))
        self.assertEqual(done.stdout, b"")
        self.assertEqual(self.writes(), [], "something was posted")
        self.assertTrue(done.stderr.strip())

    def test_approved_label_is_enough(self):
        done = self.posts(issue_view={"stdout": self.issue(["bug", "approved"], "stranger")})
        self.assertEqual(done.returncode, 0, self.shown(done))

    def test_owner_authorship_is_enough(self):
        done = self.posts(issue_view={"stdout": self.issue([], "the-owner")})
        self.assertEqual(done.returncode, 0, self.shown(done))

    def test_both_is_fine(self):
        done = self.posts(issue_view={"stdout": self.issue(["approved"], "the-owner")})
        self.assertEqual(done.returncode, 0, self.shown(done))

    def test_neither_is_refused_with_exit_4(self):
        for labels, author in ((["bug"], "stranger"), ([], "stranger"), (["Approved"], "stranger"),
                               (["approved-ish", "not approved"], "stranger"), ([], "The-Owner"),
                               ([], "the-owner2")):
            with self.subTest(labels=labels, author=author):
                self.assert_not_posted(self.posts(issue_view={"stdout": self.issue(labels, author)}))
        self.assertEqual([c[:2] for c in self.calls()][:2], [["issue", "view"], ["repo", "view"]])

    def test_every_failure_to_find_out_refuses_and_posts_nothing(self):
        good_issue = APPROVED_ISSUE
        cases = {
            "issue view fails": {"issue_view": {"exit": 1, "stdout": good_issue}},
            "issue view prints nothing": {"issue_view": {"stdout": ""}},
            "issue view prints text": {"issue_view": {"stdout": "approved"}},
            "issue view malformed JSON": {"issue_view": {"stdout": '{"labels": ['}},
            "issue view empty object": {"issue_view": {"stdout": "{}"}},
            "issue view a list": {"issue_view": {"stdout": "[]"}},
            "issue view null": {"issue_view": {"stdout": "null"}},
            "labels missing": {"issue_view": {"stdout": '{"author": {"login": "the-owner"}}'}},
            "author missing": {"issue_view": {"stdout": '{"labels": [{"name": "approved"}]}'}},
            "author without login": {"issue_view": {"stdout": '{"labels": [{"name": "approved"}], "author": {}}'}},
            "author login empty": {"issue_view": {"stdout": '{"labels": [], "author": {"login": ""}}'}},
            "labels not a list": {"issue_view": {"stdout": '{"labels": "approved", "author": {"login": "x"}}'}},
            "label name not text": {"issue_view": {"stdout": '{"labels": [{"name": 5}], "author": {"login": "x"}}'}},
            "label without name": {"issue_view": {"stdout": '{"labels": [{}], "author": {"login": "x"}}'}},
            "repo view fails": {"repo_view": {"exit": 1, "stdout": OWNER}},
            "repo view prints nothing": {"repo_view": {"stdout": ""}},
            "repo view malformed JSON": {"repo_view": {"stdout": "{nope"}},
            "repo view empty object": {"repo_view": {"stdout": "{}"}},
            "owner missing login": {"repo_view": {"stdout": '{"owner": {}}'}},
            "owner login empty": {"repo_view": {"stdout": '{"owner": {"login": ""}}'}},
            "owner not an object": {"repo_view": {"stdout": '{"owner": "the-owner"}'}},
        }
        for name, config in cases.items():
            with self.subTest(name=name):
                (self.ghdir / "calls.log").unlink(missing_ok=True)
                self.assert_not_posted(self.posts(**config))

    def test_owner_authored_issue_still_refused_when_the_owner_cannot_be_read(self):
        done = self.posts(issue_view={"stdout": self.issue([], "the-owner")}, repo_view={"stdout": "{}"})
        self.assert_not_posted(done)

    def test_gh_missing_refuses_the_comment(self):
        env = dict(self.env)
        env["PATH"] = self.no_gh_path()
        done = self.comment("5", self.put(COMMENT_OK), env=env)
        self.assertEqual(done.returncode, 4, self.shown(done))
        self.assertEqual(done.stdout, b"")
        self.assertEqual(self.calls(), [])

    def test_the_target_check_runs_after_the_input_checks(self):
        self.config(issue_view={"stdout": self.issue([], "stranger")})
        self.assert_refused(self.comment("5", self.put("no prefix\n")), 2)
        self.assert_refused(self.comment("0", self.put(COMMENT_OK)), 2)


class SameBytesTest(ScriptBase):
    """The bytes scanned are the bytes posted: one read, then the same bytes everywhere."""

    def test_comment_scanned_posted_and_file_bytes_are_equal(self):
        self.spy_scanner()
        data = "QA: bytes\r\nwith CRLF, café, no final newline".encode()
        done = self.comment("5", self.put(data))
        self.assertEqual(done.returncode, 0, self.shown(done))
        self.assertEqual((self.scripts / "scanned.bin").read_bytes(), data)
        self.assertEqual(self.gh_stdin(), data)
        self.assertEqual((self.scripts / "scanner-args.txt").read_text().split(), ["-"])

    def test_create_scanned_bytes_are_the_whole_file_and_posted_bytes_are_its_body(self):
        self.spy_scanner()
        data = "Title: Same bytes\n\nline one\n\nline three, no final newline".encode()
        self.assertEqual(self.create(self.put(data)).returncode, 0)
        self.assertEqual((self.scripts / "scanned.bin").read_bytes(), data)
        self.assertEqual(self.gh_stdin(), b"line one\n\nline three, no final newline")
        self.assertEqual(data.split(b"\n\n", 1)[1], self.gh_stdin())

    def test_a_file_swapped_after_the_scan_changes_nothing(self):
        self.spy_scanner()
        data = b"QA: the scanned text\n"
        path = self.put(data)
        env = dict(self.env)
        env["SPY_SWAP"] = str(self.project / path)
        self.assertEqual(self.comment("5", path, env=env).returncode, 0)
        self.assertEqual((self.project / path).read_bytes(), b"QA: SWAPPED AFTER THE SCAN\n")
        self.assertEqual(self.gh_stdin(), data)
        self.assertEqual((self.scripts / "scanned.bin").read_bytes(), data)

    def test_the_real_scanner_sees_the_same_bytes(self):
        data = "QA: " + MATCH[1][1] + "\n"
        self.assert_refused(self.comment("5", self.put(data)), 3)


class ScannerRefusalTest(ScriptBase):
    def test_every_secret_fixture_is_refused_with_exit_3_in_title_and_body(self):
        for name, text, number, secret in MATCH:
            for script, make_text, line in (
                ("create", lambda t: f"Title: leaked {t}\n\nbody\n", 1),
                ("create", lambda t: f"Title: ok\n\nbody\n{t}\n", 4),
                ("comment", lambda t: f"QA: {t}\n", 1),
                ("comment", lambda t: f"QA: fine\n\n{t}", 3),
            ):
                with self.subTest(name=name, script=script, line=line):
                    path = self.put(make_text(text))
                    done = self.create(path) if script == "create" else self.comment("5", path)
                    self.assert_refused(done, 3)
                    shown = self.shown(done)
                    self.assertIn(f"{path}:{line}: matches pattern {number}", shown)
                    self.assertNotIn(secret, shown)
                    self.assertNotIn(text, shown)

    def test_a_secret_that_starts_the_title_is_refused_too(self):
        for name, text, _, _ in MATCH:
            with self.subTest(name=name):
                done = self.create(self.put(f"Title: {text}\n\nbody\n"))
                self.assertIn(done.returncode, (2, 3))
                self.assertEqual(done.stdout, b"")
                self.assertEqual(self.calls(), [])

    def test_the_text_posted_is_never_a_secret_even_when_hidden_in_a_long_line(self):
        data = "QA: " + "x" * 50000 + " " + MATCH[5][1] + "\n"
        self.assert_refused(self.comment("5", self.put(data)), 3)

    def test_any_non_zero_scanner_exit_is_a_refusal(self):
        self.spy_scanner()
        for code in ("1", "2", "3", "4", "5", "99", "127", "255"):
            with self.subTest(code=code):
                env = dict(self.env)
                env["SPY_EXIT"] = code
                self.assert_refused(self.create(self.put(CREATE_OK), env=env), 3)
                self.assert_refused(self.comment("5", self.put(COMMENT_OK), env=env), 3)

    def test_a_missing_or_broken_scanner_is_a_refusal(self):
        (self.scripts / "scan-issue-body.sh").unlink()
        self.assert_refused(self.create(self.put(CREATE_OK)), 3)
        self.assert_refused(self.comment("5", self.put(COMMENT_OK)), 3)

    def test_a_missing_patterns_file_is_a_refusal(self):
        (self.scripts / "secret-patterns.txt").unlink()
        self.assert_refused(self.create(self.put(CREATE_OK)), 3)
        self.assert_refused(self.comment("5", self.put(COMMENT_OK)), 3)

    def test_a_broken_patterns_file_is_a_refusal(self):
        (self.scripts / "secret-patterns.txt").write_text("[abc\n", encoding="utf-8")
        self.assert_refused(self.comment("5", self.put(COMMENT_OK)), 3)

    def test_clean_text_with_secret_like_words_passes(self):
        text = "QA: git status, make verify, .env.example, config/.env.example, sk-short\n"
        self.assertEqual(self.comment("5", self.put(text)).returncode, 0)


class FailingGhTest(ScriptBase):
    """The underlying command fails: exit 1, one-line reason, no success text, no retry."""

    def assert_failed(self, done, kind):
        self.assertEqual(done.returncode, 1, self.shown(done))
        self.assertEqual(done.stdout, b"", "success text was printed")
        reason = done.stderr.decode().strip()
        self.assertTrue(reason)
        self.assertNotIn("\n", reason, "the reason must be one line")
        self.assertNotIn(BODY_TOKEN, self.shown(done))
        self.assertNotIn("Title", reason)
        self.assertLessEqual(len([c for c in self.calls() if c[1] == kind]), 1, "gh was retried")

    def create_file(self):
        return self.put(f"Title: Failing {BODY_TOKEN}\n\nBody {BODY_TOKEN}\n")

    def comment_file(self):
        return self.put(f"QA: {BODY_TOKEN}\n")

    def test_create_when_gh_is_missing(self):
        env = dict(self.env)
        env["PATH"] = self.no_gh_path()
        done = self.create(self.create_file(), env=env)
        self.assert_failed(done, "create")
        self.assertEqual(self.calls(), [])

    def test_create_when_gh_exits_non_zero(self):
        for code in (1, 2, 4, 127):
            with self.subTest(code=code):
                (self.ghdir / "calls.log").unlink(missing_ok=True)
                self.config(create={"exit": code, "stdout": f"partial {BODY_TOKEN}"})
                self.assert_failed(self.create(self.create_file()), "create")
                self.assertEqual(len(self.calls()), 1)

    def test_create_when_gh_prints_nothing(self):
        for out in ("", "\n", "  \n"):
            with self.subTest(out=out):
                self.config(create={"stdout": out})
                self.assert_failed(self.create(self.create_file()), "create")

    def test_create_when_gh_prints_something_that_is_not_a_url(self):
        for out in (f"created {BODY_TOKEN}\n", "https://a/b https://c/d\n", "https://a/b\nhttps://c/d\n",
                    "http://insecure/x\n"):
            with self.subTest(out=out):
                self.config(create={"stdout": out})
                self.assert_failed(self.create(self.create_file()), "create")

    def test_comment_when_gh_exits_non_zero(self):
        for code in (1, 2, 127):
            with self.subTest(code=code):
                (self.ghdir / "calls.log").unlink(missing_ok=True)
                self.config(comment={"exit": code, "stdout": f"partial {BODY_TOKEN}"})
                self.assert_failed(self.comment("5", self.comment_file()), "comment")
                self.assertEqual(len(self.writes()), 1)

    def test_comment_when_gh_prints_nothing_or_not_a_url(self):
        for out in ("", "\n", f"ok {BODY_TOKEN}\n", "a\nb\n"):
            with self.subTest(out=out):
                self.config(comment={"stdout": out})
                self.assert_failed(self.comment("5", self.comment_file()), "comment")

    def test_the_failure_message_never_holds_the_text(self):
        self.config(create={"exit": 1}, comment={"exit": 1})
        for done in (self.create(self.create_file()), self.comment("5", self.comment_file())):
            self.assertNotIn(BODY_TOKEN, self.shown(done))


class StaticTest(unittest.TestCase):
    SCRIPTS = ("issue-create.sh", "issue-comment.sh", "scan-issue-body.sh", "issue-text-lib.sh")

    def code(self, name):
        text = (KIT / "scripts" / name).read_text(encoding="utf-8")
        return [line for line in text.splitlines() if not line.lstrip().startswith("#")]

    def test_no_eval_no_shell_strings_no_source_of_issue_text(self):
        for name in self.SCRIPTS:
            for line in self.code(name):
                with self.subTest(script=name, line=line):
                    self.assertIsNone(re.search(r"\beval\b", line))
                    self.assertIsNone(re.search(r"\b(bash|sh)\s+-c\b", line))
                    self.assertIsNone(re.search(r"\bxargs\b", line))

    def test_gh_is_only_called_in_the_four_allowed_shapes(self):
        shapes = {
            "issue-create.sh": ['gh issue create --title "$title" --body-file -'],
            "issue-comment.sh": ['gh issue view "$number" --json labels,author', "gh repo view --json owner",
                                 'gh issue comment "$number" --body-file -'],
        }
        for name in self.SCRIPTS:
            found = []
            for line in self.code(name):
                line = re.sub(r'die [0-9] "[^"]*"', "", line)
                for match in re.finditer(r"\bgh (issue|repo|api|label|pr|auth|run)\b[^)>|]*", line):
                    found.append(re.sub(r"\s+2\s*$", "", match.group(0).strip()))
            expected = shapes.get(name, [])
            self.assertEqual(sorted(found), sorted(expected), name)
        for name in self.SCRIPTS:
            text = "\n".join(self.code(name))
            for word in ("--label", "--add-label", "--assignee", "--milestone", "--project", "gh api",
                         "issue edit", "issue close", "issue reopen", "issue delete", "--body "):
                self.assertNotIn(word, text, f"{name}: {word}")

    def test_not_run_by_verify_or_the_hooks(self):
        for path in [KIT / "scripts" / "verify.sh", KIT / "scripts" / "check-staged.sh"]:
            text = path.read_text(encoding="utf-8")
            for word in ("issue-create", "issue-comment", "issue-text-lib"):
                self.assertNotIn(word, text)
        for folder in ("githooks", "claude-code/hooks"):
            for path in (KIT / folder).rglob("*"):
                if path.is_file():
                    text = path.read_text(encoding="utf-8", errors="ignore")
                    self.assertNotIn("issue-create", text)
                    self.assertNotIn("issue-comment", text)


class MakeTargetTest(FakeGhMixin, unittest.TestCase):
    """The make targets validate before any shell runs, then run the script."""

    def setUp(self):
        self.make_gh()
        self.folder = new_workdir(REPO / ".scratch", prefix="make-issue-")
        self.addCleanup(shutil.rmtree, self.folder, ignore_errors=True)
        self.rel = self.folder.relative_to(REPO).as_posix()
        self.marker_rel = f"{self.rel}/marker"
        self.marker = REPO / self.marker_rel

    def put(self, data, name="t.md"):
        (self.folder / name).write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
        return f"{self.rel}/{name}"

    def make(self, *args, env=None):
        self.reset_logs()
        return subprocess.run(["make", "--no-print-directory", *args], cwd=str(REPO), env=env or self.env,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, errors="replace")

    def assert_make_refused(self, done, target):
        self.assertNotEqual(done.returncode, 0)
        self.assertEqual(done.stdout, "")
        self.assertIn(f"Usage: make {target}", done.stderr)
        self.assertEqual(self.calls(), [], "gh was run")
        self.assertFalse(self.marker.exists(), "a marker file was created")

    def test_issue_create_runs_the_script(self):
        done = self.make("issue-create", f"FILE={self.put(CREATE_OK)}")
        self.assertEqual((done.returncode, done.stdout), (0, URL + "\n"), done.stderr)
        self.assertEqual(self.calls(), [["issue", "create", "--title", "A fine title", "--body-file", "-"]])
        self.assertEqual(self.gh_stdin(), b"Body line one.\nBody line two.\n")

    def test_issue_comment_runs_the_script(self):
        done = self.make("issue-comment", "N=44", f"FILE={self.put(COMMENT_OK)}")
        self.assertEqual((done.returncode, done.stdout), (0, URL + "#issuecomment-1\n"), done.stderr)
        self.assertEqual([c[:2] for c in self.calls()], [["issue", "view"], ["repo", "view"], ["issue", "comment"]])
        self.assertEqual(self.gh_stdin(), COMMENT_OK.encode())

    def test_bad_files_are_refused_by_make_before_any_shell_runs(self):
        good = self.put(COMMENT_OK)
        touch = f"touch {self.marker_rel}"
        bad_files = [
            "", "--help", "-", "/etc/hostname", ".scratch/../Makefile", "Makefile", ".scratch/a b", ".scratch",
            f"$(shell {touch})", f".scratch/$(shell {touch})", f".scratch/x.md;{touch}", f".scratch/x.md`{touch}`",
            ".scratch/$(touch)x", ".scratch/x.md ", f".scratch/x.md\n{touch}", ".scratch/a'b", '.scratch/a"b',
            ".scratch/a$b", ".scratch/a\\b", "-x", ".scratchx/a.md", ".scratch/a*", ".scratch/a%b",
        ]
        for file in bad_files:
            with self.subTest(file=file, target="issue-create"):
                self.assert_make_refused(self.make("issue-create", f"FILE={file}"), "issue-create")
            with self.subTest(file=file, target="issue-comment"):
                self.assert_make_refused(self.make("issue-comment", "N=5", f"FILE={file}"), "issue-comment")
        self.assertEqual(self.make("issue-comment", "N=5", f"FILE={good}").returncode, 0)

    def test_missing_variables_are_refused(self):
        file = self.put(COMMENT_OK)
        self.assert_make_refused(self.make("issue-create"), "issue-create")
        self.assert_make_refused(self.make("issue-comment"), "issue-comment")
        self.assert_make_refused(self.make("issue-comment", f"FILE={file}"), "issue-comment")
        self.assert_make_refused(self.make("issue-comment", "N=5"), "issue-comment")
        self.assert_make_refused(self.make("issue-comment", "N=", f"FILE={file}"), "issue-comment")

    def test_bad_numbers_are_refused_by_make_before_any_shell_runs(self):
        file = self.put(COMMENT_OK)
        touch = f"touch {self.marker_rel}"
        # (Not " 1": make strips leading spaces from a command-line value, so that is "1".
        # The script-level NumberTest refuses " 1".)
        for number in ["0", "007", "-1", "1e3", "1.5", "1 ", "1 2", "1234567890", "--help",
                       f"1; {touch}", f"$(shell {touch})", f"$({touch})", f"`{touch}`", 'a"b', "1'",
                       f"1\n{touch}", "1&&echo x", "a1", "1a"]:
            with self.subTest(n=number):
                self.assert_make_refused(self.make("issue-comment", f"N={number}", f"FILE={file}"), "issue-comment")

    def test_the_environment_cannot_smuggle_a_value_either(self):
        file = self.put(COMMENT_OK)
        env = dict(self.env)
        env["N"] = f"$(shell touch {self.marker_rel})"
        self.assert_make_refused(self.make("issue-comment", f"FILE={file}", env=env), "issue-comment")

    def test_secret_in_the_file_is_refused_through_make(self):
        file = self.put("Title: x\n\n" + MATCH[1][1] + "\n")
        done = self.make("issue-create", f"FILE={file}")
        self.assertNotEqual(done.returncode, 0)
        self.assertEqual(done.stdout, "")
        self.assertEqual(self.calls(), [])
        self.assertNotIn(MATCH[1][1], done.stderr)

    def test_template_and_repo_makefile_define_the_same_targets(self):
        template = (KIT / "templates" / "Makefile.github.mk").read_text(encoding="utf-8")
        repo = (REPO / "Makefile").read_text(encoding="utf-8")

        def block(text, root):
            lines, inside = [], False
            for line in text.splitlines():
                if line.startswith(("issue-file-chars", "issue-strip-chars", "issue-file-ok")):
                    lines.append(line)
                    inside = False
                elif re.match(r"issue-(create|comment):", line):
                    lines.append(line)
                    inside = True
                elif inside and line.startswith("\t"):
                    lines.append(line)
                else:
                    inside = False
            return [line.replace(root, "KIT") for line in lines]

        self.assertEqual(block(template, "_docs/agent-kit"), block(repo, "agent-kit"))
        self.assertIn("bash _docs/agent-kit/scripts/issue-create.sh", template)
        self.assertIn("bash _docs/agent-kit/scripts/issue-comment.sh", template)
        self.assertIn("bash agent-kit/scripts/issue-create.sh", repo)
        self.assertIn("bash agent-kit/scripts/issue-comment.sh", repo)
        for text in (template, repo):
            self.assertRegex(text, r"(?m)^issue-create: ## ")
            self.assertRegex(text, r"(?m)^issue-comment: ## ")
            self.assertNotIn("--label", text)

    def test_the_fragment_names_only_two_targets(self):
        template = (KIT / "templates" / "Makefile.github.mk").read_text(encoding="utf-8")
        targets = re.findall(r"(?m)^([a-z][a-z-]*):(?!=)", template)
        self.assertEqual(targets, ["issue-create", "issue-comment"])


if __name__ == "__main__":
    unittest.main()
