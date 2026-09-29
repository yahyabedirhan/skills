"""Tests for set-up-machine's reconcile, run against throwaway home folders.

python3 -m unittest discover -s skills/set-up-machine/scripts/tests
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from setupmachine import reconcile, rules, shared  # noqa: E402
from setupmachine.adapters import claude_code, codex  # noqa: E402
from setupmachine.plan import render  # noqa: E402

RM = rules.Rule(
    id="rm-recursive-force",
    level="deny",
    summary="`rm -rf` and its variants",
    program="rm",
    flags=(("r", "R", "recursive"), ("f", "force")),
    reason="Can't be undone.",
    instruction="Move it into `.scratch/`.",
)


def ask_rule(**kw):
    return rules.Rule(**{**RM.__dict__, "id": "rm-ask", "level": "ask", **kw})


class Home:
    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name).resolve()
        self.os_home = self.path / "not-this-home"

    def close(self):
        self._tmp.cleanup()

    def write(self, rel, text):
        p = self.path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def read(self, rel):
        return (self.path / rel).read_text()

    def settings(self, **permissions):
        self.write(".claude/settings.json", json.dumps({"model": "x", "permissions": permissions}, indent=2) + "\n")

    def perms(self):
        return json.loads(self.read(".claude/settings.json"))["permissions"]

    def plan(self, table=(RM,), tools=None):
        return reconcile.build(self.path, list(table), self.os_home, {"claude-code": tools} if tools is not None else None)

    def apply(self, table=(RM,), tools=None):
        plan = self.plan(table, tools)
        reconcile.apply(plan, plan.id)
        return plan


def kinds(plan, kind):
    return [c.text for s in plan.sections for c in s.changes if c.kind == kind]


class RuleTableTest(unittest.TestCase):
    def test_the_shipped_table_loads(self):
        ids = [r.id for r in rules.load()]
        self.assertIn("rm-recursive-force", ids)

    def test_flag_forms_cover_every_order_and_spelling(self):
        forms = [" ".join(f) for f in rules.flag_forms(RM)]
        self.assertEqual(forms[0], "-rf")
        for want in ("-fr", "-Rf", "-r -f", "-f -r", "--recursive --force", "--force -R"):
            self.assertIn(want, forms)
        self.assertEqual(len(forms), len(set(forms)))

    def test_prefixes_include_absolute_paths(self):
        firsts = {p[0] for p in rules.command_prefixes(RM)}
        self.assertEqual(firsts, {"rm", "/bin/rm", "/usr/bin/rm"})

    def test_bad_rows_are_refused(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "rules.json"
            for row in (
                {"id": "x"},
                {**_row(), "level": "block"},
                {**_row(), "match": {"program": "/bin/rm", "flags": []}},
                {**_row(), "match": {"program": "rm", "flags": [["-r"]]}},
            ):
                path.write_text(json.dumps({"version": 1, "rules": [row]}))
                with self.assertRaises(rules.RuleTableError):
                    rules.load(path)


def _row():
    return {
        "id": "x", "level": "deny", "summary": "s", "reason": "r", "instruction": "i",
        "match": {"program": "rm", "flags": [["r"]]},
    }


class ReconcileTest(unittest.TestCase):
    def setUp(self):
        self.home = Home()

    def tearDown(self):
        self.home.close()

    def test_empty_home_gets_everything_then_a_second_run_has_no_changes(self):
        first = self.home.apply()
        # Every rm spelling, the CLAUDE.md import, auto memory off, and the hook.
        self.assertEqual(len(kinds(first, "added")), len(rules.command_prefixes(RM)) + 3)
        self.assertIn("Bash(rm -rf:*)", self.home.perms()["deny"])
        self.assertIn("rm -rf", self.home.read(".config/agents/AGENTS.md"))
        self.assertIn("Move it into `.scratch/`.", self.home.read(".config/agents/AGENTS.md"))
        self.assertIn("@" + str(self.home.path / ".config/agents/AGENTS.md"), self.home.read(".claude/CLAUDE.md"))

        second = self.home.plan()
        self.assertFalse(second.has_changes)
        self.assertEqual(kinds(second, "added"), [])
        self.assertTrue(render(second).rstrip().endswith("No changes."))

    def test_existing_entries_are_kept_in_order_and_listed_as_extra(self):
        self.home.settings(deny=["Bash(dd:*)", "Bash(rm -rf:*)"], allow=["Bash(ls:*)"])
        plan = self.home.apply()
        deny = self.home.perms()["deny"]
        self.assertEqual(deny[:2], ["Bash(dd:*)", "Bash(rm -rf:*)"])
        self.assertEqual(self.home.perms()["allow"], ["Bash(ls:*)"])
        self.assertEqual(sorted(kinds(plan, "extra")), ["Bash(dd:*)", "Bash(ls:*)"])
        self.assertIn("Bash(rm -rf:*)", kinds(plan, "present"))
        self.assertEqual(json.loads(self.home.read(".claude/settings.json"))["model"], "x")
        # An entry that was already there isn't the skill's, so the manifest doesn't claim it.
        owned = json.loads(self.home.read(".config/agents/set-up-machine.json"))["harnesses"]["claude-code"]
        self.assertNotIn("Bash(rm -rf:*)", owned["permissions"]["deny"])

    def test_a_looser_entry_is_tightened_by_adding_the_stricter_one(self):
        self.home.settings(allow=["Bash(rm -fr:*)"], ask=["Bash(rm -rf:*)"])
        plan = self.home.apply()
        perms = self.home.perms()
        self.assertEqual(sorted(kinds(plan, "tightened")), ["Bash(rm -fr:*)", "Bash(rm -rf:*)"])
        self.assertIn("Bash(rm -rf:*)", perms["deny"])
        self.assertEqual(perms["ask"], ["Bash(rm -rf:*)"])
        self.assertEqual(perms["allow"], ["Bash(rm -fr:*)"])

    def test_a_stricter_existing_entry_is_never_loosened(self):
        self.home.settings(deny=["Bash(rm -rf:*)"])
        plan = self.home.apply(table=(ask_rule(),))
        self.assertIn("Bash(rm -rf:*)", kinds(plan, "stricter"))
        self.assertEqual(self.home.perms()["deny"], ["Bash(rm -rf:*)"])
        self.assertNotIn("Bash(rm -rf:*)", self.home.perms()["ask"])

    def test_overlapping_rules_keep_the_stricter_level(self):
        self.home.apply(table=(ask_rule(), RM))
        self.assertIn("Bash(rm -rf:*)", self.home.perms()["deny"])
        self.assertNotIn("ask", self.home.perms())

    def test_only_its_own_entries_are_removed_when_the_table_drops_a_rule(self):
        self.home.settings(deny=["Bash(dd:*)"])
        self.home.apply()
        plan = self.home.apply(table=())
        self.assertEqual(self.home.perms()["deny"], ["Bash(dd:*)"])
        self.assertEqual(len(kinds(plan, "removed")), len(rules.command_prefixes(RM)))
        self.assertFalse(self.home.plan(table=()).has_changes)

    def test_instructions_outside_the_generated_block_are_kept(self):
        self.home.write(".config/agents/AGENTS.md", "# Mine\n\nMy workflow.\n")
        self.home.write(".claude/CLAUDE.md", "# Personal\n\nKeep me.\n")
        self.home.apply()
        self.home.write(
            ".config/agents/AGENTS.md", self.home.read(".config/agents/AGENTS.md") + "\nAdded after the block.\n"
        )
        self.home.apply(table=(ask_rule(summary="changed"),))
        agents = self.home.read(".config/agents/AGENTS.md")
        self.assertTrue(agents.startswith("# Mine\n\n" + shared.RULE_LINE + "\n\nMy workflow.\n"))
        self.assertIn("Added after the block.", agents)
        self.assertIn("**Asks first:** changed.", agents)
        self.assertEqual(agents.count(shared.BEGIN), 1)
        claude_md = self.home.read(".claude/CLAUDE.md")
        self.assertTrue(claude_md.startswith("# Personal\n\nKeep me.\n"))
        self.assertEqual(claude_md.count("/.config/agents/AGENTS.md"), 1)

    def test_the_import_uses_tilde_in_the_users_own_home(self):
        self.home.os_home = self.home.path
        self.home.apply()
        self.assertIn("@~/.config/agents/AGENTS.md\n", self.home.read(".claude/CLAUDE.md"))
        self.assertFalse(self.home.plan().has_changes)

    def test_apply_refuses_a_plan_that_no_longer_matches(self):
        plan = self.home.plan()
        self.home.settings(deny=["Bash(dd:*)"])
        with self.assertRaises(reconcile.PlanMismatch):
            reconcile.apply(self.home.plan(), plan.id)
        self.assertFalse((self.home.path / ".config/agents/AGENTS.md").exists())

    def test_apply_backs_up_what_it_changes(self):
        self.home.settings(deny=["Bash(dd:*)"])
        before = self.home.read(".claude/settings.json")
        plan = self.home.plan()
        backup = reconcile.apply(plan, plan.id)
        self.assertEqual((backup / ".claude/settings.json").read_text(), before)

    def test_a_symlinked_file_stays_a_symlink(self):
        self.home.write("dotfiles/CLAUDE.md", "# Linked\n")
        (self.home.path / ".claude").mkdir()
        (self.home.path / ".claude/CLAUDE.md").symlink_to(self.home.path / "dotfiles/CLAUDE.md")
        self.home.apply()
        self.assertTrue((self.home.path / ".claude/CLAUDE.md").is_symlink())
        self.assertIn("/.config/agents/AGENTS.md", self.home.read("dotfiles/CLAUDE.md"))

    def test_a_broken_generated_block_stops_the_plan(self):
        self.home.write(".config/agents/AGENTS.md", "# Mine\n" + shared.BEGIN + "\n- a rule\n")
        with self.assertRaises(ValueError):
            self.home.plan()

    def test_invalid_settings_json_stops_the_plan(self):
        self.home.write(".claude/settings.json", "{not json")
        with self.assertRaises(ValueError):
            self.home.plan()



def table_rule(rule_id):
    return next(r for r in rules.load() if r.id == rule_id)


MAIL_TOOLS = [
    "mcp__claude_ai_Gmail__send_message",
    "mcp__claude_ai_Gmail__reply",
    "mcp__claude_ai_Gmail__forward",
    "mcp__claude_ai_Gmail__create_draft",
    "mcp__claude_ai_Gmail__trash_thread",
    "mcp__claude_ai_Gmail__untrash_thread",
    "mcp__claude_ai_Gmail__mark_message_spam",
    "mcp__claude_ai_Gmail__unmark_message_spam",
    "mcp__claude_ai_Gmail__apply_sensitive_message_label",
    "mcp__claude_ai_Gmail__batch_apply_sensitive_thread_labels",
    "mcp__game__send_message",
    "mcp__claude_ai_Claude_Docs__create",
]


class FullTableTest(unittest.TestCase):
    def test_every_family_of_the_policy_has_a_row(self):
        levels = {r.id: r.level for r in rules.load()}
        for rule_id in (
            "rm-recursive-force", "rm-no-preserve-root", "disk-write", "chmod-recursive-777", "privilege-escalation",
            "shell-inline-command", "git-push-force", "git-reset-hard", "gh-repo-destructive", "gh-access-keys",
            "calendar-mail-cli-send", "secret-files-read", "secret-files-write", "home-credentials-read",
            "mail-send", "mail-destructive",
        ):
            self.assertEqual(levels.get(rule_id), "deny", rule_id)
        self.assertEqual(levels["git-push-force-with-lease"], "ask")
        self.assertEqual(levels["gh-repo-edit"], "ask")
        self.assertEqual(levels["gh-api-secrets"], "allow-and-report")

    def test_subcommands_and_operands_sit_around_the_flags(self):
        entries = claude_code.entries_for(table_rule("git-push-force"))
        for want in ("Bash(git push --force:*)", "Bash(git push -f:*)", "Bash(/usr/bin/git push --force:*)"):
            self.assertIn(want, entries)
        self.assertIn("Bash(chmod -R 777:*)", claude_code.entries_for(table_rule("chmod-recursive-777")))
        shells = claude_code.entries_for(table_rule("shell-inline-command"))
        for want in ("Bash(bash -c:*)", "Bash(sh -c:*)", "Bash(zsh -c:*)", "Bash(/bin/zsh -c:*)"):
            self.assertIn(want, shells)
        gh = claude_code.entries_for(table_rule("gh-repo-destructive"))
        self.assertIn("Bash(gh repo delete:*)", gh)
        self.assertIn("Bash(gh repo archive:*)", gh)

    def test_file_rules_use_the_kinds_claude_code_checks(self):
        self.assertEqual(
            claude_code.entries_for(table_rule("secret-files-write")),
            ["Edit(./**/.env)", "Edit(./**/.env.*)", "Edit(./**/secrets/**)"],
        )
        self.assertIn("Read(./**/.env)", claude_code.entries_for(table_rule("secret-files-read")))
        self.assertEqual(claude_code.entries_for(table_rule("home-credentials-read")), ["Read(~/.ssh/**)", "Read(~/.aws/**)"])

    def test_mail_rules_match_mail_tools_by_meaning(self):
        send = claude_code.entries_for(table_rule("mail-send"), MAIL_TOOLS)
        self.assertEqual(send, sorted([
            "mcp__claude_ai_Gmail__send_message", "mcp__claude_ai_Gmail__reply", "mcp__claude_ai_Gmail__forward",
        ]))
        destructive = claude_code.entries_for(table_rule("mail-destructive"), MAIL_TOOLS)
        self.assertEqual(destructive, sorted([
            "mcp__claude_ai_Gmail__trash_thread", "mcp__claude_ai_Gmail__mark_message_spam",
            "mcp__claude_ai_Gmail__apply_sensitive_message_label",
            "mcp__claude_ai_Gmail__batch_apply_sensitive_thread_labels",
        ]))

    def test_bad_rows_of_the_new_kinds_are_refused(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "rules.json"
            base = {k: v for k, v in _row().items() if k != "match"}
            for match in (
                {"paths": ["/etc/x"], "access": "read"},
                {"paths": ["./.env"], "access": "read"},
                {"paths": [".env"], "access": "execute"},
                {"server": "mail", "tool": "("},
                {"server": "mail"},
                {"program": "gh", "subcommands": [["repo delete"]]},
                {"program": "rm", "paths": [".env"], "access": "read"},
            ):
                path.write_text(json.dumps({"version": 1, "rules": [{**base, "match": match}]}))
                with self.assertRaises(rules.RuleTableError, msg=match):
                    rules.load(path)


class CoversTest(unittest.TestCase):
    def test_bash_coverage_respects_word_boundaries(self):
        self.assertTrue(claude_code.covers("Bash(gh repo delete*)", "Bash(gh repo delete:*)"))
        self.assertTrue(claude_code.covers("Bash(git push --force *)", "Bash(git push --force:*)"))
        self.assertTrue(claude_code.covers("Bash(git push:*)", "Bash(git push --force:*)"))
        self.assertFalse(claude_code.covers("Bash(git push --force:*)", "Bash(git push --force-with-lease:*)"))
        self.assertFalse(claude_code.covers("Bash(su:*)", "Bash(sudo:*)"))
        self.assertFalse(claude_code.covers("Bash(rm -rf)", "Bash(rm -rf:*)"))

    def test_mcp_coverage_by_server_or_glob(self):
        tool = "mcp__claude_ai_Gmail__send_message"
        self.assertTrue(claude_code.covers("mcp__claude_ai_Gmail", tool))
        self.assertTrue(claude_code.covers("mcp__claude_ai_Gmail__*", tool))
        self.assertFalse(claude_code.covers("mcp__other__send_message", tool))


class FullTableReconcileTest(unittest.TestCase):
    def setUp(self):
        self.home = Home()
        self.table = rules.load()

    def tearDown(self):
        self.home.close()

    def test_the_full_table_applies_then_a_second_run_has_no_changes(self):
        first = self.home.apply(self.table, MAIL_TOOLS)
        perms = self.home.perms()
        self.assertIn("Bash(git push --force-with-lease:*)", perms["ask"])
        self.assertIn("Bash(gh api:*)", perms["allow"])
        self.assertIn("Edit(./**/.env)", perms["deny"])
        self.assertIn("mcp__claude_ai_Gmail__send_message", perms["deny"])
        self.assertNotIn("mcp__game__send_message", perms["deny"])
        found = kinds(first, "found")
        self.assertIn("mcp__claude_ai_Gmail__forward, mcp__claude_ai_Gmail__reply, mcp__claude_ai_Gmail__send_message", found)
        self.assertFalse(self.home.plan(self.table, MAIL_TOOLS).has_changes)

    def test_rule_lines_cover_deny_and_ask_and_say_instead_only_for_deny(self):
        self.home.apply(self.table, [])
        agents = self.home.read(".config/agents/AGENTS.md")
        for rule in self.table:
            self.assertEqual(agents.count(f"{rule.summary}. {rule.reason}"), 1, rule.id)
        self.assertIn("**Denied:** `git push --force`.", agents)
        self.assertIn("Instead: Push normally", agents)
        self.assertIn("**Asks first:** `gh repo edit`. It changes a repository's settings, such as its visibility, for everyone. Say", agents)

    def test_a_covering_entry_counts_as_present_and_isnt_extra(self):
        self.home.settings(deny=["Bash(gh repo delete*)"])
        plan = self.home.plan(self.table, [])
        self.assertNotIn("Bash(gh repo delete:*)", kinds(plan, "added"))
        self.assertNotIn("Bash(gh repo delete*)", kinds(plan, "extra"))

    def test_an_ask_rule_already_denied_is_reported_stricter_and_left(self):
        self.home.settings(deny=["Bash(gh repo edit*)"])
        plan = self.home.apply(self.table, [])
        self.assertIn("Bash(gh repo edit:*)", kinds(plan, "stricter"))
        self.assertNotIn("Bash(gh repo edit:*)", self.home.perms().get("ask", []))

    def test_an_inert_write_rule_is_named_as_such(self):
        self.home.settings(deny=["Write(./.env)"])
        plan = self.home.plan(self.table, [])
        notes = [c.note for s in plan.sections for c in s.changes if c.kind == "extra" and c.text == "Write(./.env)"]
        self.assertEqual(len(notes), 1)
        self.assertIn("never checks Write rules", notes[0])

    def test_a_mail_tool_that_disappears_is_removed_only_when_the_list_was_read(self):
        self.home.apply(self.table, MAIL_TOOLS)
        original = claude_code.discover_tools
        claude_code.discover_tools = lambda: (None, "not logged in")
        try:
            plan = self.home.plan(self.table)
        finally:
            claude_code.discover_tools = original
        self.assertEqual(kinds(plan, "removed"), [])
        self.assertTrue(any("not logged in" in g for g in kinds(plan, "gap")))
        plan = self.home.apply(self.table, [])
        self.assertIn("mcp__claude_ai_Gmail__send_message", kinds(plan, "removed"))
        self.assertNotIn("mcp__claude_ai_Gmail__send_message", self.home.perms()["deny"])


class SharedFileShapeTest(unittest.TestCase):
    def setUp(self):
        self.home = Home()

    def tearDown(self):
        self.home.close()

    def test_a_new_file_has_the_rule_line_defaults_rules_and_workflow_in_order(self):
        self.home.apply()
        text = self.home.read(".config/agents/AGENTS.md")
        order = [shared.RULE_LINE, shared.DEFAULTS_HEADING, shared.BEGIN, shared.WORKFLOW_HEADING]
        self.assertEqual([text.index(x) for x in order], sorted(text.index(x) for x in order))
        for role in shared.ROLES:
            self.assertIn(f"| {role} | none |", text)

    def test_missing_pieces_are_added_and_the_users_values_kept(self):
        self.home.write(".config/agents/AGENTS.md", "\n".join([
            "# Mine", "", shared.RULE_LINE, "", "## Defaults", "", "| Role | Default |", "|---|---|",
            "| Session host | tmux |", "", "## Personal workflow", "", "- I like short reports.", "",
        ]))
        plan = self.home.apply()
        text = self.home.read(".config/agents/AGENTS.md")
        self.assertIn("| Session host | tmux |\n| Worktree tool | none |", text)
        self.assertIn("the Defaults row Skills repo, `none`", kinds(plan, "added"))
        # The rules block goes before the workflow section, which keeps its lines.
        self.assertLess(text.index(shared.BEGIN), text.index(shared.WORKFLOW_HEADING))
        self.assertTrue(text.endswith("## Personal workflow\n\n- I like short reports.\n"))
        self.assertFalse(self.home.plan().has_changes)

    def test_a_file_without_any_shape_gets_every_piece(self):
        self.home.write(".config/agents/AGENTS.md", "Old notes.\n")
        plan = self.home.apply()
        text = self.home.read(".config/agents/AGENTS.md")
        self.assertTrue(text.startswith(shared.RULE_LINE + "\n\nOld notes.\n"))
        self.assertIn(shared.WORKFLOW_HEADING, text)
        self.assertIn("the personal workflow section", kinds(plan, "added"))
        self.assertFalse(self.home.plan().has_changes)

    def test_lines_besides_the_import_in_claude_md_are_reported(self):
        self.home.write(".claude/CLAUDE.md", "# Personal\n\nKeep me.\n")
        self.assertIn("2 line(s) besides the import", kinds(self.home.plan(), "extra"))


class MemoryTest(unittest.TestCase):
    def setUp(self):
        self.home = Home()

    def tearDown(self):
        self.home.close()

    def test_claude_code_memory_is_turned_off_and_its_files_removed_with_a_backup(self):
        self.home.write(".claude/projects/-a-project/memory/MEMORY.md", "- a note\n")
        self.home.write(".claude/projects/-a-project/memory/note.md", "the note\n")
        plan = self.home.plan()
        self.assertIn("<home>/.claude/projects/-a-project/memory/note.md", kinds(plan, "removed"))
        self.assertIn("<home>/.claude/projects/-a-project/memory/note.md", render(plan))
        backup = reconcile.apply(plan, plan.id)
        self.assertIs(json.loads(self.home.read(".claude/settings.json"))["autoMemoryEnabled"], False)
        self.assertFalse((self.home.path / ".claude/projects/-a-project/memory/note.md").exists())
        self.assertEqual((backup / ".claude/projects/-a-project/memory/note.md").read_text(), "the note\n")
        second = self.home.plan()
        self.assertFalse(second.has_changes)
        self.assertIn("autoMemoryEnabled: false", kinds(second, "present"))

    def test_claude_code_memory_on_is_tightened_and_other_settings_kept(self):
        self.home.write(".claude/settings.json", json.dumps({"model": "x", "autoMemoryEnabled": True}))
        plan = self.home.apply()
        self.assertIn("autoMemoryEnabled: false", kinds(plan, "tightened"))
        settings = json.loads(self.home.read(".claude/settings.json"))
        self.assertEqual((settings["model"], settings["autoMemoryEnabled"]), ("x", False))

    def test_a_memory_file_changed_after_the_plan_stops_apply(self):
        self.home.write(".claude/projects/p/memory/note.md", "one\n")
        plan = self.home.plan()
        self.home.write(".claude/projects/p/memory/note.md", "two\n")
        with self.assertRaises(reconcile.PlanMismatch):
            reconcile.apply(self.home.plan(), plan.id)
        self.assertEqual(self.home.read(".claude/projects/p/memory/note.md"), "two\n")

    def test_codex_without_a_config_folder_is_skipped(self):
        plan = self.home.apply()
        self.assertIn("Codex isn't set up here (no ~/.codex); nothing to turn off", kinds(plan, "none"))
        self.assertFalse((self.home.path / ".codex").exists())

    def test_codex_memories_are_turned_off_and_their_files_removed(self):
        self.home.write(".codex/config.toml", 'model = "m"\n\n[features]\nhooks = true\n\n[mcp_servers.x]\nargs = []\n')
        self.home.write(".codex/memories/MEMORY.md", "a memory\n")
        plan = self.home.apply()
        self.assertEqual(
            self.home.read(".codex/config.toml"),
            'model = "m"\n\n[features]\nmemories = false\nhooks = true\n\n[mcp_servers.x]\nargs = []\n',
        )
        self.assertIn("<home>/.codex/memories/MEMORY.md", kinds(plan, "removed"))
        self.assertFalse((self.home.path / ".codex/memories/MEMORY.md").exists())
        self.assertFalse(self.home.plan().has_changes)

    def test_codex_config_forms(self):
        cases = {
            "": ("[features]\nmemories = false\n", "added"),
            'model = "m"\n': ('model = "m"\n\n[features]\nmemories = false\n', "added"),
            "[features]\nmemories = true # on\n": ("[features]\nmemories = false\n", "tightened"),
            "[features]\nmemories = false\n": ("[features]\nmemories = false\n", "present"),
            "features.memories = true\n[x]\n": ("features.memories = false\n[x]\n", "tightened"),
            "[[a]]\nmemories = true\n": ("[[a]]\nmemories = true\n\n[features]\nmemories = false\n", "added"),
        }
        for text, (want, kind) in cases.items():
            got, change = codex.set_memories_off(text)
            self.assertEqual((got, change.kind), (want, kind), text)
        with self.assertRaises(ValueError):
            codex.set_memories_off("features = { memories = true }\n")

    def test_harnesses_without_memory_say_so(self):
        texts = {s.title: s.changes[0].text for s in self.home.plan().sections if s.title.endswith(": memory")}
        self.assertIn("nothing to turn off", texts["opencode: memory"])
        self.assertIn("nothing to turn off", texts["Cursor: memory"])


class HookWiringTest(unittest.TestCase):
    def setUp(self):
        self.home = Home()

    def tearDown(self):
        self.home.close()

    def pre_tool_hooks(self):
        return json.loads(self.home.read(".claude/settings.json"))["hooks"]["PreToolUse"]

    def test_the_hook_is_wired_with_its_configuration_then_reported_as_wired(self):
        self.home.apply()
        [group] = self.pre_tool_hooks()
        self.assertEqual(group["matcher"], "*")
        [handler] = group["hooks"]
        command = handler["command"]
        self.assertIn("pre_tool_hook.py", command)
        self.assertIn("--harness claude-code", command)
        self.assertIn(str(self.home.path / ".config/agents/hook.json"), command)
        config = json.loads(self.home.read(".config/agents/hook.json"))
        self.assertEqual(config["report_dir"], str(self.home.path / ".local/state/agents/reports"))

        second = self.home.plan()
        self.assertFalse(second.has_changes)
        self.assertTrue(any("hook wired" in w for w in kinds(second, "wired")), render(second))
        self.assertIn("wired", render(second))

    def test_in_the_users_own_home_the_hook_reads_the_default_configuration(self):
        plan = reconcile.build(self.home.path, [RM], self.home.path)
        reconcile.apply(plan, plan.id)
        [group] = self.pre_tool_hooks()
        self.assertNotIn("--config", group["hooks"][0]["command"])
        self.assertEqual(json.loads(self.home.read(".config/agents/hook.json"))["report_dir"], "~/.local/state/agents/reports")

    def test_the_users_hooks_and_configuration_are_kept(self):
        self.home.write(".claude/settings.json", json.dumps({"hooks": {"PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": "my-hook"}]}]}}))
        self.home.write(".config/agents/hook.json", json.dumps({"report_dir": "/elsewhere"}))
        plan = self.home.apply()
        groups = self.pre_tool_hooks()
        self.assertEqual(groups[0], {"matcher": "Bash", "hooks": [{"type": "command", "command": "my-hook"}]})
        self.assertEqual(len(groups), 2)
        self.assertEqual(json.loads(self.home.read(".config/agents/hook.json")), {"report_dir": "/elsewhere"})
        self.assertTrue(any("/elsewhere" in w for w in kinds(self.home.plan(), "wired")))

    def test_a_moved_hook_is_rewired_and_only_its_own_entry_removed(self):
        self.home.apply()
        original = claude_code.HOOK_SCRIPT
        claude_code.HOOK_SCRIPT = Path("/moved/scripts/pre_tool_hook.py")
        try:
            plan = self.home.apply()
        finally:
            claude_code.HOOK_SCRIPT = original
        self.assertEqual(len(kinds(plan, "removed")), 1)
        [group] = self.pre_tool_hooks()
        self.assertIn("/moved/scripts/pre_tool_hook.py", group["hooks"][0]["command"])

    def test_hooks_turned_off_in_the_file_are_a_gap(self):
        self.home.write(".claude/settings.json", json.dumps({"disableAllHooks": True}))
        plan = self.home.plan()
        self.assertTrue(any("disableAllHooks" in g and "this file" in g for g in kinds(plan, "gap")))

    def test_invalid_hook_configuration_stops_the_plan(self):
        self.home.write(".config/agents/hook.json", "{nope")
        with self.assertRaises(ValueError):
            self.home.plan()

    def test_a_table_other_than_the_skills_own_is_passed_to_the_hook(self):
        other = self.home.path / "rules.json"
        other.write_text(rules.DEFAULT_TABLE.read_text())
        plan = reconcile.build(self.home.path, [RM], self.home.os_home, None, other)
        reconcile.apply(plan, plan.id)
        [group] = self.pre_tool_hooks()
        self.assertIn(f"--rules {other}", group["hooks"][0]["command"])


if __name__ == "__main__":
    unittest.main()
