"""Tests for the opencode adapter and the hook's opencode reader and writer, against throwaway homes.

python3 -m unittest discover -s skills/set-up-machine/scripts/tests
"""
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from setupmachine import hook, reconcile, rules, shared  # noqa: E402
from setupmachine.adapters import opencode  # noqa: E402
from setupmachine.plan import render  # noqa: E402

TABLE = rules.load()
BY_ID = {r.id: r for r in TABLE}
RM, LEASE, FORCE, GH_API = (BY_ID[i] for i in ("rm-recursive-force", "git-push-force-with-lease", "git-push-force", "gh-api-secrets"))
ENV_READ = BY_ID["env-files-read"]


class Home:
    def __init__(self, opencode_dir=True):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name).resolve()
        self.os_home = self.path / "not-this-home"
        if opencode_dir:
            (self.path / ".config/opencode").mkdir(parents=True)

    def close(self):
        self._tmp.cleanup()

    def write(self, rel, text):
        p = self.path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def read(self, rel):
        return (self.path / rel).read_text()

    def config(self, name="opencode.json"):
        return json.loads(self.read(f".config/opencode/{name}"))

    def plan(self, table=(RM,)):
        return reconcile.build(self.path, list(table), self.os_home, {"claude-code": []})

    def apply(self, table=(RM,)):
        plan = self.plan(table)
        reconcile.apply(plan, plan.id)
        return plan


def changes(plan, kind, title="opencode: permissions"):
    return [c for s in plan.sections if s.title == title for c in s.changes if c.kind == kind]


def texts(plan, kind, title="opencode: permissions"):
    return [c.text for c in changes(plan, kind, title)]


class MatchingTest(unittest.TestCase):
    def test_wildcard_reads_patterns_as_opencode_does(self):
        self.assertTrue(opencode.wildcard("rm -rf x", "rm -rf *"))
        self.assertTrue(opencode.wildcard("rm -rf", "rm -rf *"))  # a trailing ` *` matches nothing too
        self.assertFalse(opencode.wildcard("git push --force-with-lease", "git push --force *"))
        self.assertTrue(opencode.wildcard("a/b/.env", "*/.env"))  # `*` crosses `/`
        self.assertTrue(opencode.wildcard("playwright_click", "playwright_*"))
        self.assertFalse(opencode.wildcard("env FOO=1 cmd", "env"))

    def test_entries_per_row_kind(self):
        self.assertIn(("bash", "rm -fr *"), opencode.entries_for(RM))
        self.assertIn(("bash", "/bin/rm -rf *"), opencode.entries_for(RM))
        self.assertEqual(opencode.entries_for(BY_ID["env-dump"])[0], ("bash", "env"))  # bare: the program alone
        self.assertEqual(opencode.entries_for(BY_ID["env-files-commands"]), [])  # paths inside a command: the hook's
        self.assertEqual(opencode.entries_for(BY_ID["env-dump-listed"]), [])  # only flags: the hook's
        self.assertEqual(opencode.entries_for(ENV_READ)[:2], [("read", ".env"), ("read", "*/.env")])
        self.assertEqual(opencode.exceptions_for(ENV_READ), [("read", ".env.example"), ("read", "*/.env.example")])
        self.assertEqual(opencode.entries_for(BY_ID["home-credentials-read"]),
                         [("external_directory", "~/.ssh/*"), ("external_directory", "~/.aws/*")])
        self.assertEqual(opencode.entries_for(BY_ID["mail-send"]), [])

    def test_jsonc_comments_and_trailing_commas(self):
        data, had = opencode.parse_jsonc('{\n  // a note\n  "a": "http://x", /* b */\n  "c": [1, 2,],\n}\n')
        self.assertEqual((data, had), ({"a": "http://x", "c": [1, 2]}, True))
        self.assertEqual(opencode.parse_jsonc('{"a": "//not a comment",}'), ({"a": "//not a comment"}, False))


class ReconcileTest(unittest.TestCase):
    def setUp(self):
        self.home = Home()

    def tearDown(self):
        self.home.close()

    def test_a_home_without_opencode_is_left_alone(self):
        home = Home(opencode_dir=False)
        try:
            plan = home.plan()
            self.assertIn("isn't set up here", texts(plan, "none", "opencode")[0])
            self.assertIn("nothing to turn off", texts(plan, "none", "opencode: memory")[0])
            self.assertFalse((home.path / ".config/opencode").exists())
        finally:
            home.close()

    def test_one_run_sets_everything_up_and_a_second_changes_nothing(self):
        self.home.apply(TABLE)
        perm = self.home.config()["permission"]
        self.assertEqual(perm["bash"]["rm -rf *"], "deny")
        self.assertEqual(perm["bash"]["git push --force *"], "deny")
        self.assertEqual(perm["bash"]["git push --force-with-lease *"], "ask")
        self.assertEqual(perm["bash"]["gh api *"], "allow")
        bash = list(perm["bash"])
        self.assertLess(bash.index("gh api *"), bash.index("rm -rf *"))  # loosest first, so the stricter wins
        read = list(perm["read"])
        self.assertLess(read.index(".env.*"), read.index(".env.example"))  # the exception comes after the deny
        link = self.home.path / ".config/opencode/AGENTS.md"
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), shared.instructions_path(self.home.path).resolve())
        self.assertIn("rm -rf", link.read_text())
        plugin = self.home.read(".config/opencode/plugins/set-up-machine.js")
        self.assertIn('"--harness", "opencode"', plugin)
        self.assertIn(str(shared.hook_config_path(self.home.path)), plugin)

        second = self.home.plan(TABLE)
        self.assertFalse(second.has_changes, render(second))
        self.assertTrue(render(second).rstrip().endswith("No changes."))
        self.assertTrue(texts(second, "wired", "opencode: pre-tool hook"))

    def test_the_last_config_file_opencode_loads_is_the_one_written(self):
        self.home.write(".config/opencode/opencode.json", '{"model": "a"}\n')
        self.home.write(".config/opencode/opencode.jsonc", '{\n  "model": "b",\n  "permission": {"playwright_*": "allow"},\n}\n')
        plan = self.home.apply()
        self.assertEqual(self.home.config(), {"model": "a"})
        cfg = self.home.config("opencode.jsonc")
        self.assertEqual(cfg["model"], "b")
        self.assertEqual(cfg["permission"]["playwright_*"], "allow")
        self.assertIn("playwright_*", texts(plan, "extra"))

    def test_a_config_with_comments_isnt_rewritten(self):
        text = '{\n  // mine\n  "model": "b"\n}\n'
        self.home.write(".config/opencode/opencode.jsonc", text)
        plan = self.home.apply()
        self.assertEqual(self.home.read(".config/opencode/opencode.jsonc"), text)
        self.assertIn("has comments", texts(plan, "gap")[0])
        self.assertEqual(texts(plan, "added"), [])

    def test_a_looser_entry_is_tightened_by_an_entry_after_it(self):
        self.home.write(".config/opencode/opencode.json", json.dumps({"permission": {"bash": {"rm *": "allow"}}}))
        plan = self.home.apply()
        bash = self.home.config()["permission"]["bash"]
        self.assertEqual(list(bash)[0], "rm *")  # the user's entry is kept where it was
        self.assertEqual(bash["rm -rf *"], "deny")
        self.assertIn('bash "rm -rf *"', texts(plan, "tightened"))

    def test_the_same_pattern_at_a_looser_level_is_moved_to_the_end_at_the_stricter(self):
        self.home.write(".config/opencode/opencode.json",
                        json.dumps({"permission": {"bash": {"rm -rf *": "allow", "ls *": "allow"}}}))
        self.home.apply()
        bash = self.home.config()["permission"]["bash"]
        self.assertEqual(bash["rm -rf *"], "deny")
        self.assertGreater(list(bash).index("rm -rf *"), list(bash).index("ls *"))
        self.assertNotIn("rm -rf *", json.loads(self.home.read(".config/agents/set-up-machine.json"))
                         ["harnesses"]["opencode"]["permissions"]["bash"])  # it was the user's pattern
        self.assertFalse(self.home.plan().has_changes)

    def test_a_stricter_or_broader_entry_is_kept_and_counts(self):
        self.home.write(".config/opencode/opencode.json",
                        json.dumps({"permission": {"bash": {"git push *": "deny", "rm *": "deny"}}}))
        plan = self.home.apply((RM, LEASE))
        self.assertIn('bash "git push --force-with-lease *"', texts(plan, "stricter"))
        self.assertNotIn("git push --force-with-lease *", self.home.config()["permission"]["bash"])
        present = [c for c in changes(plan, "present") if c.text == 'bash "rm -rf *"']
        self.assertEqual(present[0].note, 'covered by bash "rm *"')
        self.assertEqual(texts(plan, "extra"), [])

    def test_a_later_tool_wide_entry_moves_the_tools_rules_after_it(self):
        self.home.write(".config/opencode/opencode.json",
                        json.dumps({"permission": {"bash": {"ls *": "allow"}, "*": "allow"}}))
        self.home.apply()
        perm = self.home.config()["permission"]
        self.assertEqual(list(perm), ["*", "bash"])
        self.assertEqual(opencode.effective(perm, "bash", "rm -rf x", self.home.path)[2], "deny")
        self.assertFalse(self.home.plan().has_changes)

    def test_only_its_own_entries_are_removed_when_the_table_drops_a_row(self):
        self.home.write(".config/opencode/opencode.json", json.dumps({"permission": {"bash": {"gh api *": "allow"}}}))
        self.home.apply((RM, GH_API))
        plan = self.home.apply((GH_API,))
        bash = self.home.config()["permission"]["bash"]
        self.assertNotIn("rm -rf *", bash)
        self.assertEqual(bash["gh api *"], "allow")
        self.assertIn('bash "rm -rf *"', texts(plan, "removed"))
        self.assertNotIn('bash "gh api *"', texts(plan, "removed"))

    def test_an_exception_is_reopened_unless_the_users_own_entry_refuses_it(self):
        self.home.apply((ENV_READ,))
        perm = self.home.config()["permission"]
        self.assertEqual(opencode.effective(perm, "read", "sub/.env.example", self.home.path)[2], "allow")
        self.assertEqual(opencode.effective(perm, "read", "sub/.env.local", self.home.path)[2], "deny")

        other = Home()
        try:
            other.write(".config/opencode/opencode.json", json.dumps({"permission": {"read": {"*.env*": "deny"}}}))
            plan = other.apply((ENV_READ,))
            self.assertNotIn(".env.example", other.config()["permission"]["read"])
            self.assertIn('read ".env.example"', texts(plan, "stricter"))
            self.assertFalse(other.plan((ENV_READ,)).has_changes)
        finally:
            other.close()

    def test_row_gaps_and_guards_are_named(self):
        plan = self.home.plan(TABLE)
        gaps = texts(plan, "gap")
        self.assertIn(BY_ID["env-print"].gap, gaps)
        self.assertTrue(any("declaration (`export`" in g for g in gaps))
        self.assertTrue(any("no native entry" in g for g in gaps))  # env-files-commands
        self.assertTrue(any("opencode.json can loosen" in g for g in gaps))
        self.assertTrue(any("Environment Variable Access" in t for t in texts(plan, "none")))
        self.assertIn("no MCP server", texts(plan, "found")[0])

    def test_a_configured_mail_server_is_left_to_the_hook(self):
        self.home.write(".config/opencode/opencode.json", json.dumps({"mcp": {"gmail": {"type": "local"}}}))
        plan = self.home.plan(TABLE)
        self.assertTrue(any("gmail" in g and "pre-tool hook refuses" in g for g in texts(plan, "gap")))


class HookWiringTest(unittest.TestCase):
    def setUp(self):
        self.home = Home()

    def tearDown(self):
        self.home.close()

    def test_someone_elses_plugin_of_that_name_is_kept(self):
        self.home.write(".config/opencode/plugins/set-up-machine.js", "// mine\n")
        plan = self.home.apply()
        self.assertEqual(self.home.read(".config/opencode/plugins/set-up-machine.js"), "// mine\n")
        self.assertIn("someone else's", texts(plan, "gap", "opencode: pre-tool hook")[0])

    def test_a_changed_hook_command_rewrites_its_own_plugin(self):
        self.home.apply()
        table = self.home.path / "table.json"
        table.write_text(rules.DEFAULT_TABLE.read_text())
        plan = reconcile.build(self.home.path, [RM], self.home.os_home, {"claude-code": []}, table)
        self.assertIn("replaces the plugin", changes(plan, "added", "opencode: pre-tool hook")[0].note)
        reconcile.apply(plan, plan.id)
        self.assertIn(str(table), self.home.read(".config/opencode/plugins/set-up-machine.js"))


class InstructionsTest(unittest.TestCase):
    def setUp(self):
        self.home = Home()

    def tearDown(self):
        self.home.close()

    def test_opencodes_own_file_is_kept_and_named(self):
        self.home.write(".config/opencode/AGENTS.md", "# Mine\nA line.\n")
        plan = self.home.apply()
        self.assertFalse((self.home.path / ".config/opencode/AGENTS.md").is_symlink())
        extra = texts(plan, "extra", "opencode: global instructions")
        self.assertIn("2 line(s)", extra[0])
        self.assertIn("until then", texts(plan, "gap", "opencode: global instructions")[0])


class HookReaderTest(unittest.TestCase):
    HOME = Path("/Users/someone")
    DIR = "/Users/someone/project"

    def call(self, tool, **args):
        return hook.read_opencode({"tool": tool, "sessionID": "ses_1", "args": args, "directory": self.DIR})

    def test_bash_read_edit_and_patch_calls(self):
        call = self.call("bash", command="echo a && rm -rf x", workdir="sub")
        self.assertEqual((call.command, call.cwd, call.session), ("echo a && rm -rf x", self.DIR + "/sub", "ses_1"))
        self.assertEqual(self.call("read", filePath=".env").files, ((".env", "read"),))
        self.assertEqual(self.call("write", filePath="a/.env", content="x").files, (("a/.env", "write"),))
        patch = "*** Begin Patch\n*** Update File: src/a.py\n@@\n*** Add File: .env.local\n+X=1\n*** End Patch"
        self.assertEqual(self.call("apply_patch", patchText=patch).files, (("src/a.py", "write"), (".env.local", "write")))

    def test_the_tickets_samples(self):
        def denied(command):
            return sorted({h.rule.id for h in hook.decide(self.call("bash", command=command), TABLE, self.HOME).denials})
        self.assertEqual(denied("rm -rf x"), ["rm-recursive-force"])
        self.assertEqual(denied("a && rm -rf x"), ["rm-recursive-force"])
        self.assertEqual(denied("git push --force"), ["git-push-force"])
        self.assertEqual(denied("git push --force-with-lease"), [])  # ask stays native
        verdict = hook.decide(self.call("bash", command="gh api rate_limit"), TABLE, self.HOME)
        self.assertEqual(([h.rule.id for h in verdict.reports], verdict.denials), (["gh-api-secrets"], []))

    def test_files_and_mcp_tools(self):
        def denied(call):
            return sorted({h.rule.id for h in hook.decide(call, TABLE, self.HOME).denials})
        self.assertEqual(denied(self.call("read", filePath=self.DIR + "/.env")), ["env-files-read"])
        self.assertEqual(denied(self.call("read", filePath=self.DIR + "/.env.example")), [])
        self.assertEqual(denied(self.call("gmail_send_message", to="a")), ["mail-send"])
        self.assertEqual(denied(self.call("gmail_create_draft", to="a")), [])
        self.assertEqual(self.call("apply_patch").mcp_names, ())  # a built-in is never read as an MCP tool

    def test_the_refusal_is_plain_text_and_other_calls_print_nothing(self):
        out = io.StringIO()
        payload = json.dumps({"tool": "bash", "args": {"command": "rm -fr x"}, "directory": self.DIR})
        self.assertEqual(hook.main(["--harness", "opencode"], io.StringIO(payload), out), 0)
        self.assertTrue(out.getvalue().startswith("Refused by the pre-tool hook"))
        self.assertIn("rm-recursive-force", out.getvalue())
        out = io.StringIO()
        payload = json.dumps({"tool": "bash", "args": {"command": "ls"}, "directory": self.DIR})
        self.assertEqual(hook.main(["--harness", "opencode"], io.StringIO(payload), out), 0)
        self.assertEqual(out.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
