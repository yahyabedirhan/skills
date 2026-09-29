"""Tests for the Cursor adapter and the hook's Cursor reader and writer.

python3 -m unittest discover -s skills/set-up-machine/scripts/tests
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from setupmachine import rules  # noqa: E402
from setupmachine.adapters import cursor  # noqa: E402
from setupmachine.plan import render  # noqa: E402
from test_set_up_machine import MAIL_TOOLS, RM, Home, kinds  # noqa: E402

# Payloads as Cursor 2026.09.18 sends them (captured from `cursor-agent -p` runs), trimmed.
BASE = {"conversation_id": "c1", "generation_id": "g1", "model": "default", "cursor_version": "2026.09.18-9a7762b",
        "workspace_roots": ["/Users/someone/project"], "user_email": None, "transcript_path": None}


def shell(command):
    return {**BASE, "hook_event_name": "beforeShellExecution", "command": command, "cwd": "", "sandbox": False}


def mcp(server, tool):
    return {**BASE, "hook_event_name": "beforeMCPExecution", "tool_name": tool, "tool_input": "{}",
            "mcp_server_name": server, "command": "python3 server.py"}


def read_file(path):
    return {**BASE, "hook_event_name": "beforeReadFile", "file_path": path, "content": "x", "attachments": []}


def pre_tool(tool, **tool_input):
    return {**BASE, "hook_event_name": "preToolUse", "tool_name": tool, "tool_input": tool_input,
            "tool_use_id": "t1", "cwd": ""}


class CursorHookTest(unittest.TestCase):
    """The script as Cursor runs it, IDE or CLI: one event's JSON in, a JSON answer out."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name).resolve()
        self.config = self.dir / "hook.json"
        self.config.write_text(json.dumps({"report_dir": str(self.dir / "reports")}))

    def tearDown(self):
        self._tmp.cleanup()

    def run_hook(self, payload, harness="cursor"):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "pre_tool_hook.py"), "--harness", harness, "--config", str(self.config)],
            input=payload if isinstance(payload, str) else json.dumps(payload),
            capture_output=True, text=True, timeout=30,
        )

    def answer(self, payload):
        proc = self.run_hook(payload)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def assertDenied(self, payload, rule):
        out = self.answer(payload)
        self.assertEqual(out["permission"], "deny", payload)
        self.assertIn(rule, out["user_message"])
        self.assertEqual(out["agent_message"], out["user_message"])

    def test_the_tickets_commands_are_refused(self):
        self.assertDenied(shell("rm -rf x"), "rm-recursive-force")
        self.assertDenied(shell("git push --force origin main"), "git-push-force")
        self.assertDenied(shell("gh repo delete x"), "gh-repo-destructive")
        self.assertDenied(shell("bash -c 'rm -fr x'"), "rm-recursive-force")

    def test_a_mail_send_tool_is_refused_and_a_mail_search_let_through(self):
        self.assertDenied(mcp("gmail", "send_message"), "mail-send")
        self.assertDenied(mcp("claude_ai_Gmail", "trash_thread"), "mail-destructive")
        self.assertEqual(self.answer(mcp("gmail", "search_threads")), {})
        self.assertEqual(self.answer(mcp("linear", "send_message")), {})

    def test_secret_files_are_refused_through_reads_and_writes(self):
        self.assertDenied(read_file("/Users/someone/project/.env"), "env-files-read")
        self.assertDenied(read_file("/Users/someone/.config/app/.env.local"), "env-files-read")
        self.assertDenied(pre_tool("Write", file_path="/Users/someone/project/.env", content="x"), "env-files-write")
        self.assertEqual(self.answer(read_file("/Users/someone/project/.env.example")), {})
        self.assertDenied(pre_tool("Write", file_path="/Users/someone/project/secrets/k", content="x"),
                          "secret-files-write")
        self.assertEqual(self.answer(read_file("/Users/someone/project/notes.txt")), {})
        self.assertEqual(self.answer(pre_tool("Write", file_path="/Users/someone/project/w.txt", content="x")), {})

    def test_an_ordinary_call_gets_an_empty_answer_and_no_report(self):
        self.assertEqual(self.answer(shell("ls -la")), {})
        self.assertFalse((self.dir / "reports").exists())

    def test_a_reported_command_is_logged_once_with_the_conversation(self):
        self.assertEqual(self.answer(shell("gh api repos/me/x")), {})
        [log] = list((self.dir / "reports").iterdir())
        [line] = [json.loads(l) for l in log.read_text().splitlines()]
        self.assertEqual((line["harness"], line["session"], line["rules"]), ("cursor", "c1", ["gh-api-secrets"]))
        self.assertEqual(line["cwd"], "/Users/someone/project")

    def test_claude_codes_hook_under_cursor_refuses_but_leaves_the_report_to_cursors(self):
        # Cursor also runs the hook wired in ~/.claude/settings.json, with its own payload.
        under_cursor = pre_tool("Shell", command="gh api repos/me/x")
        proc = self.run_hook(under_cursor, harness="claude-code")
        self.assertEqual((proc.returncode, proc.stdout), (0, ""), proc.stderr)
        self.assertFalse((self.dir / "reports").exists())
        proc = self.run_hook(pre_tool("Shell", command="rm -rf x"), harness="claude-code")
        self.assertEqual(json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_other_payload_shapes_never_crash(self):
        for payload in ({}, [], "not json", "", {"hook_event_name": "beforeMCPExecution"},
                        {"hook_event_name": "preToolUse", "tool_name": "Write", "tool_input": "x"},
                        {"hook_event_name": "beforeReadFile", "file_path": 3}, pre_tool("MCP:send_message")):
            proc = self.run_hook(payload)
            self.assertIn(proc.returncode, (0, 1), payload)
            self.assertNotIn("Traceback", proc.stderr, payload)
            if proc.returncode == 0:
                self.assertEqual(json.loads(proc.stdout), {}, payload)


class CursorAdapterTest(unittest.TestCase):
    def setUp(self):
        self.home = Home()
        self.table = rules.load()
        self.home.write(".cursor/cli-config.json", json.dumps(
            {"permissions": {"allow": ["Shell(ls)"], "deny": []}, "version": 1, "model": {"modelId": "m"}}, indent=2))

    def tearDown(self):
        self.home.close()

    def cli(self):
        return json.loads(self.home.read(".cursor/cli-config.json"))

    def hooks(self):
        return json.loads(self.home.read(".cursor/hooks.json"))

    def test_without_a_cursor_folder_nothing_is_written(self):
        home = Home()
        try:
            plan = home.apply(self.table, MAIL_TOOLS)
            self.assertIn("Cursor isn't set up here (no ~/.cursor); nothing to set", kinds(plan, "none"))
            self.assertFalse((home.path / ".cursor").exists())
        finally:
            home.close()

    def test_the_full_table_applies_then_a_second_run_has_no_changes(self):
        self.home.apply(self.table, MAIL_TOOLS)
        cli = self.cli()
        deny, allow = cli["permissions"]["deny"], cli["permissions"]["allow"]
        for entry in ("Shell(rm -rf)", "Shell(rm -fr)", "Shell(/bin/rm -rf)", "Shell(git push --force)",
                      "Shell(git push -f)", "Shell(gh repo delete)", "Shell(sudo)", "Shell(bash -c)",
                      "Read(**/.env)", "Read(**/.env.*)", "Write(**/.env.*)",
                      "Write(**/secrets/**)", "Read(~/.ssh/**)", "Shell(printenv)", "Shell(export -p)",
                      "Shell(env:)", "Shell(/usr/bin/env:)", "Shell(set:)",
                      "Mcp(claude_ai_Gmail:send_message)", "Mcp(claude_ai_Gmail:trash_thread)"):
            self.assertIn(entry, deny)
        self.assertNotIn("Mcp(claude_ai_Gmail:untrash_thread)", deny)
        self.assertFalse(any(e.startswith(("Shell(cat", "Shell(source")) for e in deny))  # the hook's
        self.assertEqual(allow[0], "Shell(ls)")
        self.assertIn("Shell(gh api)", allow)
        self.assertFalse(any("force-with-lease" in e for e in deny + allow))  # ask rows have no native list
        self.assertEqual((cli["model"], cli["version"]), ({"modelId": "m"}, 1))
        second = self.home.plan(self.table, MAIL_TOOLS)
        self.assertFalse(second.has_changes, render(second))
        self.assertTrue(render(second).rstrip().endswith("No changes."))

    def test_the_hook_is_wired_on_each_event_and_the_users_hooks_kept(self):
        self.home.write(".cursor/hooks.json", json.dumps({"version": 1, "hooks": {"afterFileEdit": [{"command": "fmt"}]}}))
        self.home.apply(self.table, MAIL_TOOLS)
        hooks = self.hooks()["hooks"]
        self.assertEqual(hooks["afterFileEdit"], [{"command": "fmt"}])
        for event in ("beforeShellExecution", "beforeMCPExecution", "beforeReadFile", "preToolUse"):
            [handler] = hooks[event]
            self.assertIn("pre_tool_hook.py --harness cursor --config", handler["command"])
            self.assertEqual(handler["timeout"], 10)
        self.assertEqual(hooks["preToolUse"][0]["matcher"], "^(Write|Delete|Grep)$")
        self.assertNotIn("matcher", hooks["beforeShellExecution"][0])
        self.assertEqual(self.hooks()["version"], 1)
        self.assertTrue(any("wired" in w for w in kinds(self.home.plan(self.table, MAIL_TOOLS), "wired")))

    def test_a_moved_hook_is_rewired_and_only_its_own_entry_removed(self):
        self.home.apply(self.table, MAIL_TOOLS)
        original = cursor.claude_code.HOOK_SCRIPT
        cursor.claude_code.HOOK_SCRIPT = Path("/moved/pre_tool_hook.py")
        try:
            plan = self.home.apply(self.table, MAIL_TOOLS)
        finally:
            cursor.claude_code.HOOK_SCRIPT = original
        self.assertTrue(any("pre-tool hook" in r for r in kinds(plan, "removed")))
        for handlers in self.hooks()["hooks"].values():
            self.assertEqual(len(handlers), 1)
            self.assertIn("python3 /moved/pre_tool_hook.py --harness cursor", handlers[0]["command"])

    def test_the_shared_file_reaches_cursor_as_an_always_applied_copy(self):
        self.home.apply(self.table, MAIL_TOOLS)
        copy = self.home.read(".cursor/rules/global-instructions.mdc")
        shared = self.home.read(".config/agents/AGENTS.md")
        self.assertTrue(copy.startswith("---\nalwaysApply: true\n---\n"))
        self.assertTrue(copy.endswith(shared))
        # An edit to the shared file shows as a change until the next apply refreshes the copy.
        self.home.write(".config/agents/AGENTS.md", shared + "- A new workflow line.\n")
        plan = self.home.plan(self.table, MAIL_TOOLS)
        self.assertTrue(any(t.startswith("copy of the shared file") for t in kinds(plan, "added")))
        self.home.apply(self.table, MAIL_TOOLS)
        self.assertIn("- A new workflow line.", self.home.read(".cursor/rules/global-instructions.mdc"))
        self.assertFalse(self.home.plan(self.table, MAIL_TOOLS).has_changes)

    def test_other_user_rule_files_are_extra_and_a_foreign_copy_is_left_alone(self):
        self.home.write(".cursor/rules/mine.mdc", "---\nalwaysApply: true\n---\nBe brief.\n")
        self.home.write(".cursor/rules/global-instructions.mdc", "someone else's\n")
        plan = self.home.apply(self.table, MAIL_TOOLS)
        self.assertIn("user rule file mine.mdc", kinds(plan, "extra"))
        self.assertTrue(any("didn't write it" in g for g in kinds(plan, "gap")))
        self.assertEqual(self.home.read(".cursor/rules/global-instructions.mdc"), "someone else's\n")

    def test_the_audit_names_cursors_gaps(self):
        gaps = " | ".join(kinds(self.home.plan(self.table, MAIL_TOOLS), "gap"))
        for words in ("Cursor has no ask level", "cli.json replaces these lists", "IDE doesn't read this file",
                      "working folder is inside the home folder", "account User Rules",
                      "crashes or times out",
                      "`echo $TOKEN`", "Cursor has no semantic guard", "the pre-tool hook alone refuses it",
                      "refuses the exception (`**/.env.example`) too"):
            self.assertIn(words, gaps)

    def test_its_own_entries_go_when_the_table_drops_them_and_others_stay(self):
        self.home.write(".cursor/cli-config.json", json.dumps({"permissions": {"deny": ["Shell(mine)"]}}))
        self.home.apply([RM])
        self.assertIn("Shell(rm -rf)", self.cli()["permissions"]["deny"])
        rows = [r for r in self.table if r.id == "privilege-escalation"]
        plan = self.home.apply(rows)
        deny = self.cli()["permissions"]["deny"]
        self.assertNotIn("Shell(rm -rf)", deny)
        self.assertIn("Shell(rm -rf)", kinds(plan, "removed"))
        self.assertEqual(deny, ["Shell(mine)", "Shell(sudo)", "Shell(/bin/sudo)", "Shell(/usr/bin/sudo)",
                                "Shell(su)", "Shell(/bin/su)", "Shell(/usr/bin/su)"])
        self.assertIn("Shell(mine)", kinds(plan, "extra"))

    def test_a_broader_entry_counts_and_a_deny_of_an_allow_row_is_stricter(self):
        self.home.write(".cursor/cli-config.json", json.dumps({"permissions": {"deny": ["Shell(rm)", "Shell(gh)"]}}))
        plan = self.home.plan(self.table, MAIL_TOOLS)
        self.assertNotIn("Shell(rm -rf)", kinds(plan, "added"))
        self.assertIn("Shell(gh api)", kinds(plan, "stricter"))
        self.assertEqual(kinds(plan, "extra"), [])

    def test_invalid_config_stops_the_plan(self):
        self.home.write(".cursor/hooks.json", "{nope")
        with self.assertRaises(ValueError):
            self.home.plan(self.table, MAIL_TOOLS)

    def test_memory_is_none(self):
        texts = {s.title: s.changes[0] for s in self.home.plan().sections if s.title == "Cursor: memory"}
        self.assertEqual(texts["Cursor: memory"].kind, "none")


class CoversTest(unittest.TestCase):
    def test_a_literal_shell_prefix_covers_at_word_boundaries(self):
        self.assertTrue(cursor.covers("Shell(rm)", "Shell(rm -rf)"))
        self.assertTrue(cursor.covers("Bash(git push)", "Shell(git push --force)"))
        self.assertFalse(cursor.covers("Shell(git push --force)", "Shell(git push --force-with-lease)"))
        self.assertTrue(cursor.covers("Shell(rm*)", "Shell(rm -rf)"))  # `*` matches anything
        self.assertTrue(cursor.covers("Bash(sudo:*)", "Shell(sudo)"))
        self.assertFalse(cursor.covers("Shell(git *--force*)", "Shell(git push --force)"))
        self.assertFalse(cursor.covers("Bash(rm -rf:*)", "Shell(rm -rf)"))  # matches only the bare command
        self.assertTrue(cursor.covers("Shell(env)", "Shell(env:)"))
        self.assertFalse(cursor.covers("Shell(env:)", "Shell(env -u X)"))

    def test_mcp_by_server_or_glob(self):
        self.assertTrue(cursor.covers("Mcp(gmail:*)", "Mcp(gmail:send_message)"))
        self.assertTrue(cursor.covers("Mcp(gmail)", "Mcp(gmail:send_message)"))
        self.assertFalse(cursor.covers("Mcp(linear:*)", "Mcp(gmail:send_message)"))

    def test_entries_for_each_kind(self):
        table = {r.id: r for r in rules.load()}
        self.assertIn("Shell(chmod -R 777)", cursor.entries_for(table["chmod-recursive-777"]))
        self.assertEqual(cursor.entries_for(table["env-files-commands"]), [])
        self.assertIn("Shell(export:)", cursor.entries_for(table["env-dump"]))
        self.assertEqual(cursor.entries_for(table["env-dump-listed"]), [])
        self.assertTrue(any("only flags" in g for g in cursor.gaps_for(table["env-dump-listed"])))
        self.assertEqual(cursor.entries_for(table["home-credentials-read"]), ["Read(~/.ssh/**)", "Read(~/.aws/**)"])
        self.assertEqual(cursor.entries_for(table["mail-send"], ["mcp__gmail__send_message", "mcp__gmail__search"]),
                         ["Mcp(gmail:send_message)"])


if __name__ == "__main__":
    unittest.main()
