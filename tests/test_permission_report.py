"""`make permission-report`, `make permission-logs-prune` and the log folder's retention (issue #36).

Report and prune run as real processes (and through the real Makefile and template) in throwaway
folders under .scratch/, on fixture log files. No live tool is used. Prune is only ever run on
those fixture folders.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from kit_repo import KitTestCase, new_workdir
from secret_fixtures import MATCH

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
REPORT = KIT / "scripts" / "permission-report.py"
PRUNE = KIT / "scripts" / "permission-logs-prune.py"
REPO_MAKEFILE = REPO / "Makefile"
TEMPLATE = KIT / "templates" / "Makefile.mk"
LOGS = Path(".agent-kit") / "logs" / "permissions"
GOOD_DATES = ["2026-11-03", "2026-01-01", "2026-12-31", "2028-02-29"]
GOOD_TIMES = ["2026-11-03T00:00Z", "2026-11-03T10:30Z", "2026-11-03T23:59Z", "2028-02-29T12:00Z"]
BAD_SINCE = ["2026-13-40", "2026-02-30", "2027-02-29", "$(x)", "$(shell touch MARKER)", "../x", "/etc/passwd",
             ".scratch/x", "0123456789abcdef0123456789abcdef01234567", "a1b2c3d", "deadbeef", "HEAD", "origin/main",
             "2026-1-3", "20261103", "2026/11/03", "2026-11-03x", "x2026-11-03", "2026-11-03\n", " 2026-11-03 ",
             "2026-11-03 10:00", "2026-11-03T00:00:00Z", "\u0662\u0660\u0662\u0666-\u0660\u0661-\u0660\u0663", "0000-00-00",
             "`touch MARKER`", "2026-11-03; touch MARKER", "-1", "--help", "1.5",
             # #93: a UTC minute is accepted only in the one exact form.
             "2026-11-03T25:00Z", "2026-11-03T24:00Z", "2026-11-03T10:60Z", "2026-02-30T10:00Z", "2027-02-29T10:00Z",
             "2026-13-01T10:00Z", "2026-11-03T10:00+10:00", "2026-11-03T10:00+0000", "2026-11-03T10:00",
             "2026-11-03T10:00z", "2026-11-03T10:00:00Z", "2026-11-03T10:00:00.000Z", "2026-11-03 10:00Z",
             "2026-11-03T1:00Z", "2026-11-03T10:0Z", "\u0662\u0660\u0662\u0666-11-03T10:00Z",
             "2026-11-03T\u0661\u0660:00Z", "2026-11-03T10:00Z\n", " 2026-11-03T10:00Z", "2026-11-03T10:00Z ",
             "\n2026-11-03T10:00Z", "2026-11-03T10:00ZZ", "2026-11-03T10:00Z; touch MARKER", "$(shell touch MARKER)T10:00Z"]
BAD_DAYS = ["0", "-1", "1.5", "", "3651", "10000", "99999", "007", "01", "1e3", "1 2", "+5", " ", "../x", "/tmp", "1/2",
            "x", "$(shell touch MARKER)", "$(file >MARKER,x)", "$$", "`touch MARKER`", "1; touch MARKER", "5\ntouch MARKER",
            "\u0663", "0x10", "--help", "30 days"]


def ask(tool, session, kind, pattern, time, ident=None, **extra):
    record = {"event": "ask", "tool": tool, "time": time, "sessionID": session, "type": kind, "pattern": pattern}
    if ident:
        record["id"] = ident
    record.update(extra)
    return json.dumps(record)


def reply(tool, session, ident, response, time):
    return json.dumps({"event": "reply", "tool": tool, "time": time, "sessionID": session, "id": ident, "response": response})


class Fixture(unittest.TestCase):
    def setUp(self):
        self.work = new_workdir(prefix="perm-report-")
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.project = self.work / "project"
        self.project.mkdir()

    def log(self, name, lines, raw=False):
        path = self.project / LOGS / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def script(self, script, *args, cwd=None):
        return subprocess.run([sys.executable, "-B", str(script), *args], cwd=str(cwd or self.project),
                              capture_output=True, text=True, errors="replace", timeout=60, stdin=subprocess.DEVNULL)

    def report(self, *args):
        return self.script(REPORT, *args)


class ReportTest(Fixture):
    def two_tools(self):
        self.log("2026-11-02.jsonl", [
            ask("opencode", "ses_1", "bash", "git push *", "2026-11-02T09:00:00.100Z", "per_1", source="permission.asked"),
            reply("opencode", "ses_1", "per_1", "once", "2026-11-02T09:00:05.000Z"),
            ask("opencode", "ses_1", "bash", "git push *", "2026-11-02T09:10:00.000Z", "per_2"),
            reply("opencode", "ses_1", "per_2", "reject", "2026-11-02T09:10:03.000Z"),
            ask("claude-code", "cc-1", "bash", "git push origin main", "2026-11-02T10:00:00.000Z", source="PermissionRequest"),
        ])
        self.log("2026-11-03.jsonl", [
            ask("opencode", "ses_2", "bash", "git push *", "2026-11-03T08:00:00.000Z", "per_3"),
            reply("opencode", "ses_2", "per_3", "always", "2026-11-03T08:00:02.000Z"),
            ask("claude-code", "cc-1", "bash", "git push origin main", "2026-11-03T11:00:00.000Z"),
            ask("claude-code", "cc-2", "bash", "git push origin main", "2026-11-03T12:00:00.000Z"),
            ask("claude-code", "cc-2", "edit", "/a/b.py", "2026-11-03T12:30:00.000Z"),
        ])

    def rows(self, out):
        lines = [l for l in out.splitlines() if l.split() and l.split()[0] in ("opencode", "claude-code")]
        return {(l.split()[0], l.split()[1], " ".join(l.split()[9:])): l.split()[2:9] for l in lines}

    def test_two_tools_one_pattern_in_two_sessions_counts_sessions_not_lines(self):
        self.two_tools()
        done = self.report()
        self.assertEqual(done.returncode, 0, done.stderr)
        rows = self.rows(done.stdout)
        # asked allowed always denied sessions first last
        self.assertEqual(rows[("opencode", "bash", "git push *")][:5], ["3", "1", "1", "1", "2"])
        claude = rows[("claude-code", "bash", "git push origin main")]
        self.assertEqual(claude[:5], ["3", "-", "-", "-", "2"])  # three asks, two sessions, outcome unknown
        self.assertEqual(rows[("claude-code", "edit", "/a/b.py")][:5], ["1", "-", "-", "-", "1"])

    def test_first_and_last_occurrence_are_shown(self):
        self.two_tools()
        out = self.report().stdout
        line = next(l for l in out.splitlines() if l.startswith("opencode") and "git push *" in l)
        self.assertIn("2026-11-02T09:00:00Z", line)
        self.assertIn("2026-11-03T08:00:00Z", line)

    def test_a_tool_with_no_replies_is_marked_as_unknown_not_zero(self):
        self.two_tools()
        out = self.report().stdout
        self.assertIn("Outcomes not recorded for: claude-code", out)
        self.assertNotIn("Outcomes not recorded for: opencode", out)

    def test_header_names_the_files_and_range(self):
        self.two_tools()
        self.assertIn("2 log files, 2026-11-02 to 2026-11-03", self.report().stdout)

    def test_unknown_truncated_and_non_json_lines_are_reported_not_hidden(self):
        self.log("2026-11-03.jsonl", [
            ask("opencode", "ses_1", "bash", "ls", "2026-11-03T08:00:00.000Z", "p1"),
            json.dumps({"event": "unknown", "tool": "opencode", "time": "2026-11-03T08:01:00.000Z", "source": "permission.v2.asked"}),
            json.dumps({"event": "unknown", "tool": "claude-code", "time": "2026-11-03T08:02:00.000Z", "source": "unparsed"}),
            json.dumps({"event": "truncated", "tool": "claude-code", "time": "2026-11-03T23:59:00.000Z"}),
            "not json at all", "{broken", "[1,2]", "null", '"text"', "42", "",
            json.dumps({"event": "mystery", "tool": "opencode", "time": "2026-11-03T08:03:00.000Z"}),
        ])
        done = self.report()
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("Skipped lines (not JSON objects): 6", done.stdout)
        self.assertIn("Unknown or unrecognised records: 3", done.stdout)
        self.assertIn("Size cap reached (later records that day were dropped): claude-code 2026-11-03", done.stdout)
        self.assertRegex(done.stdout, r"opencode\s+bash\s+1\s")

    def test_an_empty_folder_prints_a_short_line_and_exits_zero(self):
        (self.project / LOGS).mkdir(parents=True)
        done = self.report()
        self.assertEqual(done.returncode, 0)
        self.assertIn("No permission logs found", done.stdout)
        self.assertEqual(len(done.stdout.splitlines()), 1)

    def test_a_missing_folder_prints_the_same_line(self):
        done = self.report()
        self.assertEqual((done.returncode, len(done.stdout.splitlines())), (0, 1))
        self.assertIn("No permission logs found", done.stdout)

    def test_other_files_in_the_folder_are_not_read(self):
        self.two_tools()
        (self.project / LOGS / "notes.txt").write_text(ask("opencode", "x", "bash", "NOTES-FILE", "2026-11-03T08:00:00.000Z"))
        (self.project / LOGS / "2026-11-03.jsonl.bak").write_text(ask("opencode", "x", "bash", "BAK-FILE", "2026-11-03T08:00:00.000Z"))
        outside = self.work / "outside.jsonl"
        outside.write_text(ask("opencode", "x", "bash", "OUTSIDE-FILE", "2026-11-03T08:00:00.000Z"))
        (self.project / LOGS / "2026-11-04.jsonl").symlink_to(outside)
        (self.project / LOGS / "2026-11-05.jsonl").mkdir()
        out = self.report().stdout
        for name in ("NOTES-FILE", "BAK-FILE", "OUTSIDE-FILE"):
            self.assertNotIn(name, out)

    def test_a_secret_planted_in_a_log_is_not_printed(self):
        planted = [m for m in MATCH if m[0] in ("ghp_ token", "Authorization Bearer header", "cat .env")]
        self.log("2026-11-03.jsonl", [
            ask("claude-code", "s", "bash", "echo " + text, "2026-11-03T08:00:00.000Z") for _, text, _, _ in planted])
        out = self.report().stdout
        self.assertIn("[redacted]", out)
        for _, text, _, secret in planted:
            self.assertNotIn(secret, out)
            self.assertNotIn(text, out)

    def test_control_characters_and_long_fields_in_a_log_are_neutralised(self):
        self.log("2026-11-03.jsonl", [
            ask("claude-code", "s", "bash", "echo \x1b[31mred\x1b[0m\x07\nFAKE LINE\r", "2026-11-03T08:00:00.000Z"),
            ask("claude-code", "s", "bash", "x" * 900, "2026-11-03T08:00:01.000Z"),
            ask("claude-code\x1b[1m", "s", "t" * 300, "p", "2026-11-03T08:00:02.000Z")])
        out = self.report().stdout
        self.assertNotRegex(out, r"[\x00-\x09\x0b-\x1f\x7f]")
        self.assertTrue(all(len(l) < 400 for l in out.splitlines()), max(len(l) for l in out.splitlines()))
        self.assertNotIn("\nFAKE LINE", out)

    def test_nothing_in_a_log_is_executed(self):
        self.log("2026-11-03.jsonl", [ask("opencode", "s", "bash", "$(touch MARKER) `touch MARKER` ; touch MARKER",
                                         "2026-11-03T08:00:00.000Z")])
        out = self.report().stdout
        self.assertIn("$(touch MARKER)", out)
        self.assertFalse((self.project / "MARKER").exists())

    def test_unreadable_patterns_show_the_marker_not_the_log_text(self):
        kit = self.work / "kit"
        shutil.copytree(KIT / "scripts", kit / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        (kit / "scripts" / "secret-patterns.txt").write_text("a*\n", encoding="utf-8")
        self.log("2026-11-03.jsonl", [ask("opencode", "s", "bash", "PLAIN-TEXT", "2026-11-03T08:00:00.000Z")])
        out = self.script(kit / "scripts" / "permission-report.py").stdout
        self.assertIn("[redacted: no patterns]", out)
        self.assertNotIn("PLAIN-TEXT", out)

    def test_a_reply_is_counted_once_and_a_reply_without_an_ask_is_reported(self):
        self.log("2026-11-03.jsonl", [
            ask("opencode", "s", "bash", "ls", "2026-11-03T08:00:00.000Z", "p1"),
            reply("opencode", "s", "p1", "once", "2026-11-03T08:00:01.000Z"),
            reply("opencode", "s", "p1", "reject", "2026-11-03T08:00:02.000Z"),
            reply("opencode", "s", "gone", "once", "2026-11-03T08:00:03.000Z"),
            ask("opencode", "s", "bash", "pwd", "2026-11-03T08:00:04.000Z", "p2"),
            reply("opencode", "s", "p2", "maybe", "2026-11-03T08:00:05.000Z")])
        out = self.report().stdout
        self.assertRegex(out, r"opencode\s+bash\s+1\s+1\s+0\s+0\s+1\s.*\sls\n")
        self.assertIn("Replies with no matching ask in range: 1", out)
        self.assertIn("Unknown or unrecognised records: 1", out)

    def test_times_with_other_fraction_lengths_order_correctly(self):
        self.log("2026-11-03.jsonl", [
            ask("opencode", "s", "bash", "ls", "2026-11-03T08:00:02Z"),
            ask("opencode", "s", "bash", "ls", "2026-11-03T08:00:02.114Z"),
            ask("opencode", "s", "bash", "ls", "2026-11-03T08:00:01.999999999Z")])
        line = next(l for l in self.report().stdout.splitlines() if l.startswith("opencode"))
        self.assertIn("2026-11-03T08:00:01Z  2026-11-03T08:00:02Z", line)


class SinceTest(Fixture):
    def setUp(self):
        super().setUp()
        self.log("2026-11-01.jsonl", [ask("opencode", "a", "bash", "OLD-PATTERN", "2026-11-01T23:59:59.000Z")])
        self.log("2026-11-02.jsonl", [ask("opencode", "b", "bash", "MID-PATTERN", "2026-11-02T00:00:00.000Z")])
        self.log("2026-11-03.jsonl", [ask("opencode", "c", "bash", "NEW-PATTERN", "2026-11-03T00:00:00.000Z"),
                                      ask("opencode", "c", "bash", "BAD-TIME", "yesterday")])

    def test_since_limits_the_report_by_record_time(self):
        out = self.report("2026-11-02").stdout
        self.assertNotIn("OLD-PATTERN", out)
        self.assertIn("MID-PATTERN", out)
        self.assertIn("NEW-PATTERN", out)
        self.assertIn("from 2026-11-02 (3 log files", out)
        out = self.report("2026-11-03").stdout
        self.assertNotIn("MID-PATTERN", out)
        self.assertIn("NEW-PATTERN", out)

    def test_the_start_minute_is_inclusive_and_the_millisecond_before_it_is_not(self):
        self.log("2026-11-03.jsonl", [
            ask("opencode", "t", "bash", "BEFORE-PATTERN", "2026-11-03T10:29:59.999Z"),
            ask("opencode", "t", "bash", "AT-PATTERN", "2026-11-03T10:30:00.000Z"),
            ask("opencode", "t", "bash", "AFTER-PATTERN", "2026-11-03T10:30:00.001Z")])
        done = self.report("2026-11-03T10:30Z")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertNotIn("BEFORE-PATTERN", done.stdout)
        self.assertIn("AT-PATTERN", done.stdout)
        self.assertIn("AFTER-PATTERN", done.stdout)

    def test_a_date_and_that_days_midnight_timestamp_give_the_same_report(self):
        for day in ("2026-11-02", "2026-11-03"):
            with self.subTest(day=day):
                by_date = self.report(day).stdout.replace("from " + day + " ", "from X ")
                by_time = self.report(day + "T00:00Z").stdout.replace("from " + day + "T00:00Z ", "from X ")
                self.assertEqual(by_date, by_time)

    def test_the_header_shows_the_value_as_given(self):
        self.assertIn("Permission report from 2026-11-03T10:30Z (3 log files", self.report("2026-11-03T10:30Z").stdout)
        self.assertIn("Permission report from 2026-11-02 (3 log files", self.report("2026-11-02").stdout)
        self.assertIn("Permission report (3 log files", self.report("").stdout)

    def test_a_utc_minute_cuts_within_one_day(self):
        self.log("2026-11-02.jsonl", [
            ask("opencode", "m", "bash", "EARLY-MINUTE", "2026-11-02T09:59:59.999Z"),
            ask("opencode", "m", "bash", "LATE-MINUTE", "2026-11-02T10:00:00.000Z")])
        out = self.report("2026-11-02T10:00Z").stdout
        self.assertNotIn("EARLY-MINUTE", out)
        self.assertIn("LATE-MINUTE", out)
        self.assertIn("NEW-PATTERN", out)

    def test_records_are_judged_by_their_own_time_not_by_the_file_name(self):
        self.log("2026-11-01.jsonl", [ask("opencode", "a", "bash", "LATE-IN-OLD-FILE", "2026-11-04T00:00:00.000Z"),
                                      ask("opencode", "a", "bash", "EARLY-IN-OLD-FILE", "2026-10-01T00:00:00.000Z")])
        out = self.report("2026-11-02").stdout
        self.assertIn("LATE-IN-OLD-FILE", out)
        self.assertNotIn("EARLY-IN-OLD-FILE", out)

    def test_no_since_and_an_empty_since_both_mean_no_limit(self):
        for args in ((), ("",)):
            self.assertIn("OLD-PATTERN", self.report(*args).stdout)

    def test_a_since_after_every_record_gives_a_short_report(self):
        done = self.report("2027-01-01")
        self.assertEqual(done.returncode, 0)
        self.assertIn("No permission requests in this range.", done.stdout)

    def test_valid_dates_and_utc_minutes_are_accepted(self):
        for value in GOOD_DATES + GOOD_TIMES:
            with self.subTest(since=value):
                self.assertEqual(self.report(value).returncode, 0)

    def test_every_refused_value_is_refused_with_a_message_and_a_non_zero_exit_before_any_file_is_read(self):
        for value in BAD_SINCE:
            with self.subTest(since=value):
                done = self.report(value)
                self.assertNotEqual(done.returncode, 0)
                self.assertEqual(done.stdout, "")
                self.assertIn("SINCE must be a real date written YYYY-MM-DD or a UTC minute written YYYY-MM-DDTHH:MMZ", done.stderr)
                self.assertFalse((self.project / "MARKER").exists())
        # "Before any file is read": a refused value is refused even when there is no folder at all,
        # while a good value in the same place only says there are no logs.
        empty = self.work / "empty"
        empty.mkdir()
        self.assertNotEqual(self.script(REPORT, "2026-13-40", cwd=empty).returncode, 0)
        self.assertEqual(self.script(REPORT, "2026-11-03", cwd=empty).returncode, 0)

    def test_more_than_one_argument_is_refused(self):
        self.assertNotEqual(self.report("2026-11-03", "2026-11-04").returncode, 0)


class MakeCase(Fixture):
    kinds = {"repo": (REPO_MAKEFILE, "agent-kit"), "template": (TEMPLATE, "_docs/agent-kit")}

    def make_project(self, kind):
        makefile, kit = self.kinds[kind]
        folder = self.work / ("make-" + kind)
        folder.mkdir()
        (folder / "Makefile").write_text(makefile.read_text(encoding="utf-8"), encoding="utf-8")
        shutil.copytree(KIT / "scripts", folder / kit / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        return folder

    def make(self, folder, *args, env=None):
        e = {k: v for k, v in os.environ.items() if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "SINCE", "DAYS")}
        e.update(env or {})
        return subprocess.run(["make", "--no-print-directory", *args], cwd=str(folder), env=e, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, errors="replace", timeout=60)

    def each(self):
        for kind in self.kinds:
            with self.subTest(kind=kind):
                yield kind, self.make_project(kind)

    def put(self, folder, name, text="{}\n"):
        path = folder / LOGS / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path


class ReportTargetTest(MakeCase):
    def test_the_target_runs_the_report(self):
        for kind, folder in self.each():
            self.put(folder, "2026-11-03.jsonl", ask("opencode", "s", "bash", "make verify", "2026-11-03T08:00:00.000Z") + "\n")
            done = self.make(folder, "permission-report", "SINCE=2026-11-01")
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertIn("make verify", done.stdout)
            done = self.make(folder, "permission-report")
            self.assertEqual(done.returncode, 0, done.stderr)

    def test_a_dollar_in_since_is_refused_by_make_before_anything_runs(self):
        for kind, folder in self.each():
            for value in ("$(shell touch MARKER)", "$(x)", "${HOME}", "$$", "a$b"):
                done = self.make(folder, "permission-report", "SINCE=" + value)
                self.assertNotEqual(done.returncode, 0)
                self.assertIn("Usage: make permission-report", done.stderr)
                self.assertFalse((folder / "MARKER").exists())

    def test_every_refused_since_fails_through_make_too(self):
        for kind, folder in self.each():
            for value in BAD_SINCE:
                if value.endswith("\n") or value.startswith(("\n", " ")) or value.endswith(" "):
                    continue  # make trims blanks and newlines from a command-line value
                with self.subTest(kind=kind, since=value):
                    done = self.make(folder, "permission-report", "SINCE=" + value)
                    self.assertNotEqual(done.returncode, 0)
                    self.assertFalse((folder / "MARKER").exists())

    def test_since_from_the_environment_is_also_checked(self):
        for kind, folder in self.each():
            done = self.make(folder, "permission-report", env={"SINCE": "$(shell touch MARKER)"})
            self.assertNotEqual(done.returncode, 0)
            self.assertFalse((folder / "MARKER").exists())

    def test_the_target_is_documented_in_make_help(self):
        for kind, folder in self.each():
            helped = self.make(folder, "help").stdout
            self.assertRegex(helped, r"permission-report\s+Summarise")
            self.assertRegex(helped, r"permission-logs-prune\s+Delete")


class PruneTest(MakeCase):
    def day(self, ago):
        return (datetime.now(timezone.utc).date() - timedelta(days=ago)).isoformat()

    def build(self, folder):
        """Fixture folder: logs of several ages and things that must never be deleted."""
        logs = folder / LOGS
        made = {}
        for ago in (0, 1, 29, 30, 31, 45, 400):
            made[ago] = self.put(folder, self.day(ago) + ".jsonl", "keep or delete\n")
        made["note"] = self.put(folder, "notes.txt")
        made["bak"] = self.put(folder, "2020-01-01.jsonl.bak")
        made["bad name"] = self.put(folder, "old.jsonl")
        made["bad date"] = self.put(folder, "2020-13-45.jsonl")
        made["upper"] = self.put(folder, "2020-01-01.JSONL")
        (logs / "2020-02-02.jsonl").mkdir()
        outside = folder / "outside" / "2020-01-01.jsonl"
        outside.parent.mkdir()
        outside.write_text("outside\n", encoding="utf-8")
        made["outside"] = outside
        made["parent"] = self.put(folder, "../2020-01-01.jsonl")
        made["scratch"] = folder / ".scratch" / "2020-01-01.jsonl"
        made["scratch"].parent.mkdir()
        made["scratch"].write_text("scratch\n", encoding="utf-8")
        (logs / "2020-03-03.jsonl").symlink_to(outside)
        return made

    def test_it_deletes_only_dated_jsonl_files_older_than_the_limit(self):
        for kind, folder in self.each():
            made = self.build(folder)
            done = self.make(folder, "permission-logs-prune", "DAYS=30")
            self.assertEqual(done.returncode, 0, done.stderr)
            for ago in (31, 45, 400):
                self.assertFalse(made[ago].exists(), (kind, ago))
            for ago in (0, 1, 29, 30):
                self.assertTrue(made[ago].exists(), (kind, ago))
            for name in ("note", "bak", "bad name", "bad date", "upper", "outside", "parent", "scratch"):
                self.assertTrue(made[name].exists(), (kind, name))
            self.assertTrue((folder / LOGS / "2020-02-02.jsonl").is_dir())
            self.assertTrue((folder / LOGS / "2020-03-03.jsonl").is_symlink())
            self.assertEqual(made["outside"].read_text(encoding="utf-8"), "outside\n")
            self.assertIn("Deleted 3 log files older than 30 days", done.stdout)

    def test_the_boundary_day_is_kept(self):
        for kind, folder in self.each():
            made = self.build(folder)
            self.make(folder, "permission-logs-prune", "DAYS=31")
            self.assertTrue(made[31].exists())
            self.assertFalse(made[45].exists())

    def test_every_refused_days_value_deletes_nothing(self):
        for kind, folder in self.each():
            made = self.build(folder)
            before = sorted(p.name for p in (folder / LOGS).iterdir())
            for value in BAD_DAYS:
                with self.subTest(kind=kind, days=value):
                    done = self.make(folder, "permission-logs-prune", "DAYS=" + value)
                    self.assertNotEqual(done.returncode, 0)
                    self.assertFalse((folder / "MARKER").exists())
                    self.assertEqual(sorted(p.name for p in (folder / LOGS).iterdir()), before)
            done = self.make(folder, "permission-logs-prune")
            self.assertNotEqual(done.returncode, 0)
            self.assertEqual(sorted(p.name for p in (folder / LOGS).iterdir()), before)

    def test_the_script_refuses_the_same_values_when_run_directly(self):
        for kind, folder in self.each():
            made = self.build(folder)
            before = sorted(p.name for p in (folder / LOGS).iterdir())
            script = folder / self.kinds[kind][1] / "scripts" / "permission-logs-prune.py"
            for value in BAD_DAYS + ["3651"]:
                with self.subTest(days=value):
                    done = self.script(script, value, cwd=folder)
                    self.assertNotEqual(done.returncode, 0)
                    self.assertEqual(sorted(p.name for p in (folder / LOGS).iterdir()), before)
            self.assertNotEqual(self.script(script, cwd=folder).returncode, 0)
            self.assertNotEqual(self.script(script, "5", "6", cwd=folder).returncode, 0)

    def test_the_limits_are_accepted(self):
        for kind, folder in self.each():
            self.put(folder, self.day(10) + ".jsonl")
            for value in ("1", "9", "30", "365", "3650"):
                with self.subTest(days=value):
                    self.assertEqual(self.make(folder, "permission-logs-prune", "DAYS=" + value).returncode, 0)

    def test_it_never_follows_a_symlinked_log_folder(self):
        for kind, folder in self.each():
            target = folder / "elsewhere"
            target.mkdir()
            victim = target / "2020-01-01.jsonl"
            victim.write_text("do not delete\n", encoding="utf-8")
            (folder / ".agent-kit" / "logs").mkdir(parents=True)
            (folder / LOGS).symlink_to(target)
            done = self.make(folder, "permission-logs-prune", "DAYS=30")
            self.assertNotEqual(done.returncode, 0)
            self.assertTrue(victim.exists())

    def test_no_folder_is_not_an_error(self):
        for kind, folder in self.each():
            done = self.make(folder, "permission-logs-prune", "DAYS=30")
            self.assertEqual(done.returncode, 0)
            self.assertIn("nothing to prune", done.stdout)

    def test_days_from_the_environment_is_also_checked(self):
        for kind, folder in self.each():
            made = self.build(folder)
            done = self.make(folder, "permission-logs-prune", env={"DAYS": "$(shell touch MARKER)"})
            self.assertNotEqual(done.returncode, 0)
            self.assertFalse((folder / "MARKER").exists())
            self.assertTrue(made[400].exists())


class MakefileShapeTest(unittest.TestCase):
    def block(self, text, name):
        lines = text.splitlines()
        start = next(i for i, l in enumerate(lines) if l.startswith(name + ":") or l.startswith(name + " ="))
        out = []
        for line in lines[start:]:
            if not line.strip():
                break
            out.append(line)
        return out

    def test_the_repo_and_the_template_define_the_targets_the_same_way(self):
        repo = REPO_MAKEFILE.read_text(encoding="utf-8").replace("agent-kit/scripts", "KIT")
        template = TEMPLATE.read_text(encoding="utf-8").replace("_docs/agent-kit/scripts", "KIT")
        for name in ("permission-days-ok", "permission-report", "permission-logs-prune"):
            with self.subTest(name=name):
                self.assertEqual(self.block(repo, name), self.block(template, name))

    def test_variables_are_checked_with_value_and_passed_as_shell_variables(self):
        for path in (REPO_MAKEFILE, TEMPLATE):
            text = path.read_text(encoding="utf-8")
            for name, variable in (("permission-report", "SINCE"), ("permission-logs-prune", "DAYS")):
                body = "\n".join(self.block(text, name))
                with self.subTest(file=path.name, target=name):
                    self.assertNotIn("$(%s)" % variable, body)
                    self.assertIn("$(value %s)" % variable, body)
                    self.assertIn('"$$%s"' % variable, body)


class RetentionTest(KitTestCase):
    """The log folder survives `make clean-scratch` and stays out of git status and assert-clean."""

    def test_clean_scratch_leaves_the_log_folder_alone(self):
        shutil.copyfile(REPO_MAKEFILE, self.repo / "Makefile")
        log = self.write(".agent-kit/logs/permissions/2026-11-03.jsonl", '{"event":"ask"}\n')
        junk = self.write(".scratch/junk.txt", "x\n")
        done = self.run_cmd(["make", "--no-print-directory", "clean-scratch"], env={"MAKEFLAGS": "", "MAKELEVEL": ""})
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertFalse(junk.exists())
        self.assertEqual(log.read_text(encoding="utf-8"), '{"event":"ask"}\n')

    def test_a_log_file_is_not_seen_by_git_status_or_assert_clean(self):
        project = self.add_project()
        self.write(".gitignore", (REPO / ".gitignore").read_text(encoding="utf-8"))
        self.write("tracked.txt", "one\n")
        self.commit_all("base")
        self.write(".agent-kit/logs/permissions/2026-11-03.jsonl", '{"event":"ask"}\n')
        status = self.git("status", "--short", "--untracked-files=all").stdout
        self.assertNotIn(".agent-kit", status)
        done = self.run_cmd(["bash", "agent-kit/scripts/assert-clean.sh"], cwd=project)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("ASSERT-CLEAN: PASS", done.stdout)


if __name__ == "__main__":
    unittest.main()
