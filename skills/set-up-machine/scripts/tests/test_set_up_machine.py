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

    def plan(self, table=(RM,)):
        return reconcile.build(self.path, list(table), self.os_home)

    def apply(self, table=(RM,)):
        plan = self.plan(table)
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
        self.assertEqual(len(kinds(first, "added")), len(rules.command_prefixes(RM)) + 1)
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
        self.assertIn("Bash(rm -rf:*)", kinds(plan, "present"))
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
        self.assertTrue(agents.startswith("# Mine\n\nMy workflow.\n"))
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


if __name__ == "__main__":
    unittest.main()
