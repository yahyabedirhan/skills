"""Tests for the rule table: the shipped rows, and rows the loader refuses.

python3 -m unittest discover -s skills/set-up-machine/scripts/tests
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from setupmachine import rules  # noqa: E402


def row(**over):
    return {"id": "x", "level": "deny", "summary": "s", "reason": "r", "instruction": "i",
            "match": {"program": "rm", "flags": [["r"]]}, "samples": {"covers": ["rm -r x"]}, **over}


class ShippedTableTest(unittest.TestCase):
    def test_every_family_of_the_policy_has_a_row_at_its_level(self):
        levels = {r.id: r.level for r in rules.load()}
        for rule_id in (
            "rm-recursive-force", "rm-no-preserve-root", "disk-write", "chmod-recursive-777", "privilege-escalation",
            "shell-inline-command", "git-push-force", "git-push-delete-main", "git-push-delete-main-refspec",
            "git-reset-hard", "gh-repo-destructive", "gh-access-keys", "calendar-mail-cli-send",
            "secret-files-read", "secret-files-write", "home-credentials-read", "mail-send", "mail-destructive",
            "env-files-read", "env-files-write", "env-files-commands", "env-dump", "env-print", "env-dump-declared",
            "env-dump-listed", "env-print-secret", "proc-environ-read", "proc-environ-commands",
        ):
            self.assertEqual(levels.get(rule_id), "deny", rule_id)
        for rule_id in ("git-push-force-with-lease", "git-push-mirror", "git-clean-force", "find-delete", "gh-repo-edit"):
            self.assertEqual(levels.get(rule_id), "ask", rule_id)
        self.assertEqual(levels["gh-api-secrets"], "allow-and-report")

    def test_every_row_has_samples(self):
        for rule in rules.load():
            self.assertTrue(rule.covers, rule.id)


class BadRowsTest(unittest.TestCase):
    def assertRefused(self, rows):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "rules.json"
            for bad in rows:
                path.write_text(json.dumps({"version": 1, "rules": [bad]}))
                with self.assertRaises(rules.RuleTableError, msg=bad):
                    rules.load(path)

    def test_bad_fields_are_refused(self):
        self.assertRefused([
            {"id": "x"},
            row(level="block"),
            row(match={"program": "/bin/rm", "flags": []}),
            row(match={"program": "rm", "flags": [["-r"]]}),
        ])

    def test_bad_matches_are_refused(self):
        self.assertRefused([row(match=m) for m in (
            {"paths": ["./.env"], "access": "read"},
            {"paths": [".env"], "access": "execute"},
            {"server": "mail", "tool": "("},
            {"server": "mail"},
            {"program": "gh", "subcommands": [["repo delete"]]},
            {"program": "rm", "paths": [".env"], "access": "read"},
            {"program": "env", "arguments": "some"},
            {"program": "env", "arguments": "none", "flags": [["p"]]},
            {"program": "cat", "except": ["**/.env.example"]},
            {"paths": [".env"], "access": "read", "except": ["./x"]},
            {"program": "git", "operands": ["x"], "any_operand": ["y"]},
        )])

    def test_variables_are_name_globs_on_a_command_row(self):
        self.assertRefused([row(match={"program": "echo", "variables": "TOKEN"}),
                            row(match={"program": "echo", "variables": []}),
                            row(match={"program": "echo", "variables": ["$TOKEN"]}),
                            row(match={"program": "echo", "variables": ["*TOKEN*"], "arguments": "none"})])

    def test_samples_need_covers(self):
        self.assertRefused([row(samples={}), row(samples={"covers": []}), row(samples={"leaves": ["x"]}),
                            row(samples={"covers": ["x"], "other": ["y"]}), {k: v for k, v in row().items() if k != "samples"}])


if __name__ == "__main__":
    unittest.main()
