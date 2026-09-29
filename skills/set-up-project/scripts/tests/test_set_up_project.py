"""Tests for set-up-project, run against throwaway projects and a throwaway home set up by set-up-machine.

python3 -m unittest discover -s skills/set-up-project/scripts/tests
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from setupproject import use_machine_skill  # noqa: E402

use_machine_skill()

from setupmachine import reconcile, rules  # noqa: E402
from setupproject import audit, project, scaffold  # noqa: E402

TABLE = rules.load()
TOOLS = ["mcp__claude_ai_Gmail__send_message", "mcp__claude_ai_Gmail__get_thread"]
CLI = SCRIPTS / "set_up_project.py"


def make_home(root: Path) -> Path:
    """A home with every harness folder, set up by set-up-machine from the shipped table."""
    home = root / "home"
    for folder in (".claude", ".codex", ".config/opencode", ".cursor"):
        (home / folder).mkdir(parents=True)
    tools = {name: TOOLS for name in ("claude-code", "codex", "opencode", "cursor")}
    plan = reconcile.build(home, TABLE, home, tools)
    reconcile.apply(plan, plan.id)
    assert not reconcile.build(home, TABLE, home, tools).has_changes
    return home


class Fixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls._tmp.name).resolve()
        cls.home = make_home(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def setUp(self):
        self._proj = tempfile.TemporaryDirectory()
        self.project = Path(self._proj.name).resolve()

    def tearDown(self):
        self._proj.cleanup()

    def write(self, rel, text):
        path = self.project / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def read(self, rel):
        return (self.project / rel).read_text()

    def plan(self):
        return project.build(self.project, self.home, TABLE)

    def found(self, kind):
        return [(c.text, c.rule) for s in self.plan().sections for c in s.changes if c.kind == kind]


class ScaffoldTest(Fixture):
    def finish_by_hand(self):
        """What the skill's steps write from the templates."""
        self.write("AGENTS.md", self.read("AGENTS.md") + "\n## Agent skills\n\n### Issue tracker\n\nGitHub.\n")
        self.write("docs/agents/issue-tracker.md", "# Issue tracker: GitHub\n")
        self.write("docs/agents/domain.md", "# Domain Docs\n")

    def test_an_empty_project_gets_agents_md_claude_import_and_gitignore(self):
        plan = self.plan()
        project.apply(plan, plan.id)
        self.assertEqual(self.read("CLAUDE.md"), "@AGENTS.md\n")
        self.assertEqual(self.read("AGENTS.md"), "# Agent instructions\n")
        self.assertEqual(self.read(".gitignore"), ".scratch/\n.claude/worktrees/\n")
        todos = [t for t, _ in self.found("todo")]
        self.assertEqual(todos, ["AGENTS.md: ## Agent skills", "docs/agents/issue-tracker.md", "docs/agents/domain.md"])

    def test_a_second_run_reports_no_changes(self):
        plan = self.plan()
        project.apply(plan, plan.id)
        self.finish_by_hand()
        again = self.plan()
        self.assertFalse(again.has_changes)
        self.assertIn("No changes.", project.render(again))
        self.assertIn("Audit: passed.", project.render(again))

    def test_claude_md_alone_moves_into_agents_md(self):
        self.write("CLAUDE.md", "# Rules\n\nUse pnpm.\n")
        plan = self.plan()
        project.apply(plan, plan.id)
        self.assertEqual(self.read("AGENTS.md"), "# Rules\n\nUse pnpm.\n")
        self.assertEqual(self.read("CLAUDE.md"), "@AGENTS.md\n")

    def test_claude_md_beside_agents_md_gets_the_import_and_its_lines_listed(self):
        self.write("AGENTS.md", "# Agent instructions\n")
        self.write("CLAUDE.md", "Use pnpm.\n")
        plan = self.plan()
        project.apply(plan, plan.id)
        self.assertEqual(self.read("CLAUDE.md"), "@AGENTS.md\n\nUse pnpm.\n")
        self.assertIn(("CLAUDE.md: Use pnpm.", ""), self.found("todo"))
        self.assertEqual(self.read("AGENTS.md"), "# Agent instructions\n")

    def test_claude_md_linked_to_agents_md_is_in_place(self):
        self.write("AGENTS.md", "# Agent instructions\n")
        (self.project / "CLAUDE.md").symlink_to("AGENTS.md")
        plan = self.plan()
        self.assertFalse(any(w.path.name in ("CLAUDE.md", "AGENTS.md") and w.changed for w in plan.writes))

    def test_gitignore_spellings_count_and_missing_lines_are_appended(self):
        self.write(".gitignore", "node_modules\n/.scratch")
        plan = self.plan()
        project.apply(plan, plan.id)
        self.assertEqual(self.read(".gitignore"), "node_modules\n/.scratch\n.claude/worktrees/\n")

    def test_apply_refuses_a_changed_project(self):
        plan = self.plan()
        self.write("AGENTS.md", "# Mine\n")
        with self.assertRaises(project.PlanMismatch):
            project.apply(self.plan(), plan.id)


class AuditTest(Fixture):
    def test_nothing_to_audit_passes(self):
        self.assertEqual(self.found("weakens"), [])

    def test_opencode_project_rule_overrides_a_global_deny(self):
        self.write("opencode.json", json.dumps({"permission": {"bash": {"rm -rf *": "allow", "npm *": "allow"}}}))
        self.assertIn(('bash "rm -rf *": allow', "rm-recursive-force"), self.found("weakens"))
        self.assertFalse(any("npm" in t for t, _ in self.found("weakens")))

    def test_opencode_new_broad_key_wins_by_coming_last(self):
        self.write("opencode.jsonc", '{\n  // project\n  "permission": {"bash": {"git push *": "allow"}},\n}\n')
        weak = self.found("weakens")
        self.assertIn(('bash "git push *": allow', "git-push-force"), weak)
        self.assertIn(('bash "git push *": allow', "git-push-force-with-lease"), weak)

    def test_opencode_tool_wide_string_replaces_the_global_rules(self):
        self.write("opencode.json", json.dumps({"permission": {"read": "allow"}}))
        self.assertIn(("read: allow", "env-files-read"), self.found("weakens"))

    def test_opencode_agent_permission_is_checked(self):
        self.write("opencode.json", json.dumps({"agent": {"build": {"permission": {"bash": {"printenv *": "allow"}}}}}))
        self.assertIn(('agent build: bash "printenv *": allow', "env-print"), self.found("weakens"))

    def test_opencode_project_plugin_is_a_gap(self):
        self.write(".opencode/plugins/x.js", "export default async () => ({})\n")
        self.assertIn((".opencode/plugins/", ""), self.found("gap"))

    def test_cursor_empty_deny_list_drops_the_global_one(self):
        self.write(".cursor/cli.json", json.dumps({"permissions": {"deny": []}}))
        self.assertEqual([t for t, _ in self.found("weakens")], ['"deny": 0 entries'])

    def test_cursor_allow_covering_an_ask_rule(self):
        self.write(".cursor/cli.json", json.dumps({"permissions": {"allow": ["Shell(git)", "Shell(npm)"]}}))
        self.assertEqual(self.found("weakens"), [("Shell(git)", "git-push-force-with-lease")])
        self.assertIn(("Shell(git)", "git-reset-hard"), self.found("overlaps"))

    def test_cursor_nested_cli_json_is_read(self):
        self.write("pkg/.cursor/cli.json", json.dumps({"permissions": {"allow": ["Shell(gh:repo *)"]}}))
        self.assertIn(("Shell(gh:repo *)", "gh-repo-edit"), self.found("weakens"))

    def test_claude_allow_is_held_where_classify_all_shell_is_on(self):
        self.write(".claude/settings.json", json.dumps({"permissions": {"allow": ["Bash(printenv *)", "Bash(npm test *)"]}}))
        self.assertEqual(self.found("weakens"), [])
        self.assertEqual(self.found("overlaps"), [("Bash(printenv *)", "env-print")])

    def test_claude_allow_routes_around_auto_mode_without_classify_all_shell(self):
        self.write(".claude/settings.json", json.dumps({"permissions": {"allow": ["Bash(printenv:*)"]}}))
        weak = audit.audit_claude(self.project, self.root / "bare-home", TABLE)
        self.assertEqual([(c.kind, c.rule) for s in weak for c in s.changes], [("weakens", "env-print")])

    def test_claude_allow_over_an_ask_rule_weakens_it_in_cursor(self):
        self.write(".claude/settings.json", json.dumps({"permissions": {"allow": ["Bash(git push *)"]}}))
        self.assertIn(("Bash(git push *)", "git-push-force-with-lease"), self.found("weakens"))

    def test_claude_local_settings_are_not_read_by_cursor(self):
        self.write(".claude/settings.local.json", json.dumps({"permissions": {"allow": ["Bash(git push *)"]}}))
        self.assertEqual(self.found("weakens"), [])

    def test_claude_switches(self):
        self.write(".claude/settings.json", json.dumps(
            {"disableAllHooks": True, "autoMemoryEnabled": True, "disableAutoMode": "disable",
             "permissions": {"deny": ["Bash(make deploy *)"]}}))
        self.assertEqual([t for t, _ in self.found("weakens")],
                         ['"disableAllHooks": true', '"autoMemoryEnabled": true', '"disableAutoMode": "disable"'])
        self.assertEqual(self.found("extra"), [("Bash(make deploy *)", "")])

    def test_claude_mcp_allow_over_mail_tools(self):
        self.write(".claude/settings.json", json.dumps({"permissions": {"allow": ["mcp__claude_ai_Gmail"]}}))
        rules_hit = {r for _, r in self.found("overlaps")}
        self.assertEqual(rules_hit, {"mail-send", "mail-destructive"})

    def test_claude_mcp_glob_allow(self):
        self.write(".claude/settings.json", json.dumps({"permissions": {"allow": ["mcp__claude_ai_Gmail__send_*"]}}))
        self.assertEqual({r for _, r in self.found("overlaps")}, {"mail-send"})

    def test_a_write_allow_doesnt_cover_a_read_rule(self):
        self.write(".cursor/cli.json", json.dumps({"permissions": {"allow": ["Write(**/.env)"]}}))
        self.assertEqual({r for _, r in self.found("overlaps")}, {"env-files-write"})

    def test_codex_hooks_off_and_memories_on(self):
        self.write(".codex/config.toml", "model = \"x\"\n[features]\nhooks = false  # off\nmemories = true\n")
        self.assertEqual([t for t, _ in self.found("weakens")],
                         ["[features] hooks = false", "[features] memories = true"])

    def test_codex_dotted_feature_key(self):
        self.write(".codex/config.toml", "features.hooks = false\n")
        self.assertEqual([t for t, _ in self.found("weakens")], ["[features] hooks = false"])


class CliTest(unittest.TestCase):
    def run_cli(self, home: Path, *args):
        tools = home.parent / "tools.txt"
        tools.write_text("\n".join(TOOLS) + "\n")
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home)}
        return subprocess.run([sys.executable, str(CLI), *args, "--home", str(home), "--tool-names", str(tools)],
                              env=env, capture_output=True, text=True)

    def test_a_drifted_machine_stops_the_project_plan(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            home = make_home(root)
            settings = json.loads((home / ".claude/settings.json").read_text())
            settings["permissions"]["deny"].remove("Bash(rm -rf *)")
            (home / ".claude/settings.json").write_text(json.dumps(settings))
            (root / "proj").mkdir()
            done = self.run_cli(home, "plan", "--project", str(root / "proj"))
            self.assertEqual(done.returncode, 3, done.stderr)
            self.assertIn("set-up-machine plan for", done.stdout)
            self.assertIn("Bash(rm -rf *)", done.stdout)
            self.assertIn("set_up_machine.py apply --plan-id", done.stdout)
            self.assertFalse((root / "proj" / "AGENTS.md").exists())

    def test_plan_apply_and_audit_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            home = make_home(root)
            proj = root / "proj"
            (proj / ".codex").mkdir(parents=True)
            (proj / ".codex" / "config.toml").write_text("[features]\nhooks = false\n")
            done = self.run_cli(home, "plan", "--project", str(proj))
            self.assertEqual(done.returncode, 2, done.stderr)
            plan_id = next(l.split(": ")[1] for l in done.stdout.splitlines() if l.startswith("Plan id: "))
            applied = self.run_cli(home, "apply", "--plan-id", plan_id, "--project", str(proj))
            self.assertEqual(applied.returncode, 0, applied.stderr)
            self.assertEqual((proj / "CLAUDE.md").read_text(), "@AGENTS.md\n")


if __name__ == "__main__":
    unittest.main()
