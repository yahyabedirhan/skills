"""Tests for the Codex adapter, run against throwaway home folders.

python3 -m unittest discover -s skills/set-up-machine/scripts/tests
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from setupmachine import hook, reconcile, rules, shared  # noqa: E402
from setupmachine.adapters import codex  # noqa: E402
from setupmachine.plan import FileWrite, Plan, Run  # noqa: E402

TABLE = rules.load()
BY_ID = {r.id: r for r in TABLE}
CONTEXT7 = "<!-- context7 -->\nUse the `ctx7` CLI to fetch current documentation.\n<!-- context7 -->\n"


class Home:
    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name).resolve()
        self.os_home = self.path / "not-this-home"
        (self.path / ".codex").mkdir()

    def close(self):
        self._tmp.cleanup()

    def write(self, rel, text):
        p = self.path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def read(self, rel):
        return (self.path / rel).read_text()

    def plan(self, table=TABLE):
        return reconcile.build(self.path, list(table), self.os_home, {"claude-code": []})

    def apply(self, table=TABLE):
        plan = self.plan(table)
        reconcile.apply(plan, plan.id)
        return plan


def codex_changes(plan, kind, title=None):
    return [c.text for s in plan.sections if s.title.startswith("Codex")
            and (title is None or s.title == f"Codex: {title}") for c in s.changes if c.kind == kind]


class PatternTest(unittest.TestCase):
    def test_rm_rf_becomes_one_pattern_for_clusters_and_one_per_flag_order(self):
        self.assertEqual(codex.patterns_for(BY_ID["rm-recursive-force"]), [
            ["rm", ["-rf", "-Rf", "-fr", "-fR"]],
            ["rm", ["-r", "-R", "--recursive"], ["-f", "--force"]],
            ["rm", ["-f", "--force"], ["-r", "-R", "--recursive"]],
        ])

    def test_subcommands_flags_and_operands(self):
        self.assertEqual(codex.patterns_for(BY_ID["git-push-force"]), [["git", "push", ["-f", "--force"]]])
        self.assertEqual(codex.patterns_for(BY_ID["chmod-recursive-777"]), [["chmod", ["-R", "--recursive"], "777"]])
        self.assertEqual(codex.patterns_for(BY_ID["disk-write"]), [["dd"], ["mkfs"]])

    def test_shell_file_and_mcp_rows_get_no_rule_but_a_gap(self):
        for rule_id in ("shell-inline-command", "secret-files-read", "mail-send"):
            self.assertEqual(codex.patterns_for(BY_ID[rule_id]), [], rule_id)
            self.assertTrue(codex.gaps_for(BY_ID[rule_id]), rule_id)

    def test_bare_rows_and_rows_on_files_are_left_to_the_hook(self):
        for rule_id in ("env-dump", "env-files-commands"):
            self.assertEqual(codex.patterns_for(BY_ID[rule_id]), [], rule_id)
            self.assertIn("only the pre-tool hook enforces this row", codex.gaps_for(BY_ID[rule_id])[0], rule_id)

    def test_a_rendered_rule_parses_back(self):
        rule = BY_ID["rm-recursive-force"]
        text = "\n".join(codex.render_rule(p, rule) for p in codex.patterns_for(rule))
        self.assertEqual(codex.parse_rules(text), [(p, "forbidden") for p in codex.patterns_for(rule)])
        self.assertIn("Instead: Move", codex.justification(rule))

    def test_matching_and_covering(self):
        self.assertTrue(codex.matches(["rm", ["-rf", "-fr"]], ["rm", "-fr", "x"]))
        self.assertFalse(codex.matches(["rm", "-rf", "/"], ["rm", "-rf", "x"]))
        self.assertTrue(codex.covers(["git", "push", ["-f", "--force"]], ["git", "push", "--force"]))
        self.assertFalse(codex.covers(["git", "push", "--force"], ["git", "push", ["-f", "--force"]]))

    def test_the_trust_hash_is_the_one_codex_computes(self):
        # currentHash from Codex 0.157.1's app-server `hooks/list` for this hooks.json group.
        self.assertEqual(codex.trust_hash("python3 /opt/skills/pre_tool_hook.py --harness codex"),
                         "sha256:6f59665afd86ee5e927128f17e0615406473d26563602530242d82b14c2e2bf9")


class RulesTest(unittest.TestCase):
    def setUp(self):
        self.home = Home()

    def tearDown(self):
        self.home.close()

    def test_one_run_writes_the_whole_table_and_a_second_reports_nothing(self):
        plan = self.home.apply()
        written = codex.parse_rules(self.home.read(".codex/rules/set-up-machine.rules"))
        want = [(p, codex.DECISION[r.level]) for r in TABLE for p in codex.patterns_for(r)]
        self.assertEqual(written, want)
        self.assertIn("rm [-rf|-Rf|-fr|-fR]", codex_changes(plan, "added", "rules"))
        self.assertFalse(self.home.plan().has_changes)

    def test_the_other_rules_files_are_compared_and_kept(self):
        user = ('prefix_rule(pattern=["gh", "ssh-key"], decision="prompt")\n'
                'prefix_rule(pattern=["gh", "repo", "edit"], decision="forbidden")\n'
                'prefix_rule(pattern=["rm", "-rf", "/"], decision="forbidden")\n'
                'prefix_rule(pattern=["curl"], decision="allow")\n')
        self.home.write(".codex/rules/default.rules", user)
        plan = self.home.apply()
        self.assertIn("gh ssh-key", codex_changes(plan, "tightened", "rules"))
        self.assertIn("gh repo edit", codex_changes(plan, "stricter", "rules"))
        extras = codex_changes(plan, "extra", "rules")
        self.assertIn("curl: allow", extras)
        self.assertFalse(any(e.startswith("rm -rf /") for e in extras), extras)
        self.assertEqual(self.home.read(".codex/rules/default.rules"), user)

    def test_a_rows_own_gap_and_its_missing_guard_are_named(self):
        plan = self.home.plan()
        rule = BY_ID["env-print"]
        self.assertIn(rule.gap, codex_changes(plan, "gap", "rules"))
        label = rule.guard.split(":", 1)[0]
        self.assertIn(f"no semantic guard in Codex for {label}", codex_changes(plan, "none", "rules"))

    def test_a_machine_rule_on_an_env_file_is_covered_and_the_example_is_not(self):
        self.home.write(".codex/rules/default.rules", 'prefix_rule(pattern=["cat", ".env"], decision="forbidden")\n'
                                                      'prefix_rule(pattern=["cat", ".env.example"], decision="forbidden")\n')
        extras = codex_changes(self.home.plan(), "extra", "rules")
        self.assertNotIn("cat .env: forbidden", extras)
        self.assertIn("cat .env.example: forbidden", extras)

    def test_an_unreadable_rules_file_is_a_gap(self):
        self.home.write(".codex/rules/default.rules", "prefix_rule(pattern=[\n")
        self.assertTrue(any("couldn't read default.rules" in g for g in codex_changes(self.home.plan(), "gap", "rules")))


class InstructionsTest(unittest.TestCase):
    def setUp(self):
        self.home = Home()

    def tearDown(self):
        self.home.close()

    def link(self):
        return self.home.path / ".codex/AGENTS.md"

    def test_no_file_becomes_a_link_to_the_shared_file(self):
        self.home.apply()
        self.assertTrue(self.link().is_symlink())
        self.assertEqual(self.link().resolve(), shared.instructions_path(self.home.path).resolve())
        self.assertIn("present", [c.kind for s in self.home.plan().sections
                                  if s.title == "Codex: global instructions" for c in s.changes])

    def test_a_line_not_in_the_shared_file_keeps_the_file(self):
        self.home.write(".codex/AGENTS.md", "## Mine\n\n- Reports are short.\n")
        plan = self.home.apply()
        self.assertEqual(codex_changes(plan, "extra", "global instructions"), ["- Reports are short."])
        self.assertFalse(self.link().is_symlink())
        # Moved into the shared file, the line no longer holds the link back.
        path = shared.instructions_path(self.home.path)
        path.write_text(path.read_text() + "- Reports are short.\n")
        plan = self.home.apply()
        self.assertIn("<home>/.codex/AGENTS.md as a file", codex_changes(plan, "removed", "global instructions"))
        self.assertTrue(self.link().is_symlink())
        self.assertFalse(self.home.plan().has_changes)

    def test_a_context7_block_becomes_an_external_skill_install(self):
        self.home.write(".codex/AGENTS.md", CONTEXT7)
        plan = self.home.plan()
        runs = [w for w in plan.writes if isinstance(w, Run)]
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0].argv[:7], ["npx", "--yes", "skills", "add", "upstash/context7", "-s", "find-docs"])
        self.assertEqual(runs[0].env, {"HOME": str(self.home.path)})
        self.assertIn("external skill find-docs from upstash/context7", codex_changes(plan, "added", "global instructions"))
        self.assertIn(link_added(plan), codex_changes(plan, "added", "global instructions"))
        # Once installed, the block isn't needed and nothing is run.
        self.home.write(".agents/skills/find-docs/SKILL.md", "---\nname: find-docs\n---\n")
        self.assertFalse([w for w in self.home.plan().writes if isinstance(w, Run)])

    def test_the_install_reaches_claude_code_only_when_its_skills_folder_isnt_the_shared_one(self):
        self.home.write(".codex/AGENTS.md", CONTEXT7)
        (self.home.path / ".agents/skills").mkdir(parents=True)
        (self.home.path / ".claude").mkdir()
        (self.home.path / ".claude/skills").symlink_to(self.home.path / ".agents/skills")
        run = next(w for w in self.home.plan().writes if isinstance(w, Run))
        self.assertNotIn("claude-code", run.argv)

    def test_a_non_empty_override_is_a_gap(self):
        self.home.write(".codex/AGENTS.override.md", "override\n")
        self.assertTrue(any("AGENTS.override.md" in g for g in codex_changes(self.home.plan(), "gap", "global instructions")))


def link_added(plan):
    return next(t for t in codex_changes(plan, "added", "global instructions") if t.startswith("link to "))


class HookWiringTest(unittest.TestCase):
    def setUp(self):
        self.home = Home()

    def tearDown(self):
        self.home.close()

    def test_the_hook_is_wired_and_trusted_beside_the_users_hooks(self):
        theirs = {"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "their-hook"}]}]}}
        self.home.write(".codex/hooks.json", json.dumps(theirs))
        self.home.write(".codex/config.toml", 'model = "m"\n\n[hooks.state."elsewhere:session_start:0:0"]\ntrusted_hash = "x"\n')
        self.home.apply()
        data = json.loads(self.home.read(".codex/hooks.json"))
        self.assertEqual(data["hooks"]["SessionStart"], theirs["hooks"]["SessionStart"])
        group = data["hooks"]["PreToolUse"][0]
        command = group["hooks"][0]["command"]
        self.assertEqual((group["matcher"], group["hooks"][0]["timeout"]), ("*", 10))
        self.assertIn("--harness codex", command)
        config = self.home.read(".codex/config.toml")
        key = codex.trust_key(self.home.path / ".codex/hooks.json", 0)
        self.assertEqual(codex.hook_trust(config, key), codex.trust_hash(command))
        self.assertEqual(codex.hook_trust(config, "elsewhere:session_start:0:0"), "x")
        plan = self.home.plan()
        self.assertFalse(plan.has_changes)
        self.assertTrue(any(t.startswith("pre-tool hook wired and trusted") for t in codex_changes(plan, "wired")))

    def test_a_moved_hook_script_replaces_the_old_command_and_its_trust(self):
        self.home.apply()
        manifest = shared.load_manifest(self.home.path)
        old_command = manifest["harnesses"]["codex"]["hooks"][0]
        moved = old_command.replace("pre_tool_hook.py", "old/pre_tool_hook.py")
        data = json.loads(self.home.read(".codex/hooks.json"))
        data["hooks"]["PreToolUse"][0]["hooks"][0]["command"] = moved
        self.home.write(".codex/hooks.json", json.dumps(data))
        manifest["harnesses"]["codex"]["hooks"] = [moved]
        shared.manifest_path(self.home.path).write_text(json.dumps(manifest))
        plan = self.home.apply()
        self.assertIn(f"pre-tool hook: {moved}", codex_changes(plan, "removed", "pre-tool hook"))
        groups = json.loads(self.home.read(".codex/hooks.json"))["hooks"]["PreToolUse"]
        self.assertEqual([g["hooks"][0]["command"] for g in groups], [old_command])
        self.assertFalse(self.home.plan().has_changes)

    def test_hooks_turned_off_in_config_is_a_gap(self):
        self.home.write(".codex/config.toml", "[features]\nhooks = false\n")
        self.assertTrue(any("hooks = false` in config.toml" in g for g in codex_changes(self.home.plan(), "gap")))

    def test_trust_entries_edit_only_their_own_table(self):
        text = 'a = 1\n\n[hooks.state."k"]\nenabled = true\n\n[x]\ny = 2\n'
        with_hash = codex.set_hook_trust(text, "k", "sha256:1")
        self.assertEqual(with_hash, 'a = 1\n\n[hooks.state."k"]\ntrusted_hash = "sha256:1"\nenabled = true\n\n[x]\ny = 2\n')
        self.assertEqual(codex.set_hook_trust(with_hash, "k", "sha256:2").count("sha256:2"), 1)
        self.assertEqual(codex.drop_hook_trust(with_hash, "k"), 'a = 1\n\n[x]\ny = 2\n')


class CodexHookInputTest(unittest.TestCase):
    def read(self, **payload):
        return hook.read_codex({"session_id": "s", "cwd": "/p", **payload})

    def test_a_shell_call_is_read_as_its_command(self):
        call = self.read(tool_name="Bash", tool_input={"command": "rm -fr x"})
        self.assertEqual((call.tool, call.command, call.files), ("Bash", "rm -fr x", ()))

    def test_apply_patch_names_every_file_it_writes(self):
        patch = ("*** Begin Patch\n*** Add File: .env\n+A=1\n*** Update File: src/a.py\n*** Move to: secrets/k\n"
                 "*** Delete File: old.txt\n*** End Patch\n")
        call = self.read(tool_name="apply_patch", tool_input={"command": patch})
        self.assertIsNone(call.command)
        self.assertEqual([p for p, _ in call.files], [".env", "src/a.py", "secrets/k", "old.txt"])
        denied = {h.rule.id for h in hook.decide(call, TABLE, Path("/Users/someone")).denials}
        self.assertIn("secret-files-write", denied)

    def test_the_codex_harness_answers_a_deny_in_json(self):
        import io
        out = io.StringIO()
        payload = {"tool_name": "Bash", "tool_input": {"command": "git push origin main --force"}, "cwd": "/p"}
        self.assertEqual(hook.main(["--harness", "codex"], io.StringIO(json.dumps(payload)), out), 0)
        answer = json.loads(out.getvalue())["hookSpecificOutput"]
        self.assertEqual(answer["permissionDecision"], "deny")
        self.assertIn("git-push-force", answer["permissionDecisionReason"])


class RunTest(unittest.TestCase):
    def test_apply_runs_commands_before_writing_and_stops_on_a_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve()
            made, written = home / "made.txt", home / "written.txt"
            ok = Run(made, [sys.executable, "-c", f"open({str(made)!r}, 'w').write('x')"])
            plan = Plan(home, [], [ok, FileWrite(written, None, "y\n")])
            reconcile.apply(plan, plan.id)
            self.assertTrue(made.exists() and written.exists())
            failing = Run(home / "never.txt", [sys.executable, "-c", "raise SystemExit(3)"])
            other = home / "other.txt"
            plan = Plan(home, [], [failing, FileWrite(other, None, "z\n")])
            with self.assertRaises(reconcile.RunFailed):
                reconcile.apply(plan, plan.id)
            self.assertFalse(other.exists())


if __name__ == "__main__":
    unittest.main()
