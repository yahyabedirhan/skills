"""Tests for the default-tools audit, run against throwaway skill folders.

python3 -m unittest discover -s skills/maintain-environment/scripts/tests
"""
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import default_tools  # noqa: E402

GLOBAL = """# Global instructions

## Defaults

| Role | Default |
|---|---|
| session-host | Hive |
| worktree-tool | `grove` (pre-warmed pool) |
| notification-method | `osascript -e 'display notification'` |
| agent-to-start | `claude --model x` |
| skills-repo | someone/skills |
"""


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class DefaultToolsTest(unittest.TestCase):
    def test_tools_come_from_the_tool_roles_only(self):
        self.assertEqual(default_tools.tools_from_defaults(GLOBAL), ["hive", "grove", "osascript"])

    def test_none_and_missing_table_name_no_tool(self):
        self.assertEqual(default_tools.tools_from_defaults("| session-host | none |"), [])
        self.assertEqual(default_tools.tools_from_defaults("# No table here"), [])

    def test_flags_a_skill_naming_a_tool_outside_its_how_to_skill(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write(root, "handover/SKILL.md", "# Handover\n\nOpen a Hive tab by default.\n")
            write(root, "handover-to-hive/SKILL.md", "hive tab create\n")
            write(root, "grove/SKILL.md", "grove get\n")
            write(root, "init-effort/agents/openai.yaml", "short_description: \"with Grove\"\n")
            write(root, "init-effort/scripts/x.py", "grove = 1\n")
            hits = default_tools.scan(root, ["hive", "grove"])
        self.assertEqual(
            [(h.skill, h.path, h.line, h.tool) for h in hits],
            [("handover", "handover/SKILL.md", 3, "hive"),
             ("init-effort", "init-effort/agents/openai.yaml", 1, "grove")],
        )

    def test_a_line_routing_to_the_tools_skill_is_not_a_default(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write(root, "handover-to-hive/SKILL.md", "hive tab create\n")
            write(root, "grove/SKILL.md", "grove get\n")
            write(root, "init-effort/SKILL.md",
                  "- **Hive**: start it with the **handover-to-hive** skill.\n"
                  "- **Grove**: through the **grove** skill.\n"
                  "Then open a Hive tab.\n")
            hits = default_tools.scan(root, ["hive", "grove"])
        self.assertEqual([(h.path, h.line, h.tool) for h in hits], [("init-effort/SKILL.md", 3, "hive")])

    def test_matches_whole_words_only(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write(root, "a/SKILL.md", "a hives word and groves\n")
            self.assertEqual(default_tools.scan(root, ["hive", "grove"]), [])

    def test_report_is_tolerated_not_blocking(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write(root, "a/SKILL.md", "Use Hive.\n")
            write(root, "global.md", GLOBAL)
            out = io.StringIO()
            with redirect_stdout(out):
                code = default_tools.main(["--skills", str(root), "--global", str(root / "global.md")])
        self.assertEqual(code, 0)
        self.assertIn("a/SKILL.md:1 hive: Use Hive.", out.getvalue())
        self.assertIn("1 line in 1 skill", out.getvalue())

    def test_no_tools_named_says_so(self):
        with tempfile.TemporaryDirectory() as d:
            out = io.StringIO()
            with redirect_stdout(out):
                code = default_tools.main(["--skills", d, "--global", str(Path(d) / "missing.md")])
        self.assertEqual(code, 0)
        self.assertIn("No default tool named", out.getvalue())
        self.assertIn("missing.md doesn't exist", out.getvalue())
        self.assertNotIn("has no tool in its Defaults table", out.getvalue())

    def test_a_file_without_tools_says_so(self):
        with tempfile.TemporaryDirectory() as d:
            write(Path(d), "global.md", "| session-host | none |\n")
            out = io.StringIO()
            with redirect_stdout(out):
                default_tools.main(["--skills", d, "--global", str(Path(d) / "global.md")])
        self.assertIn("global.md has no tool in its Defaults table", out.getvalue())

    def test_flags_defaults_mentions_outside_the_parameters_section(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write(root, "a/SKILL.md", "\n".join([
                "# A", "",
                "## Parameters", "",
                "Each comes from the Defaults table in the environment's instructions.", "",
                "## 1. Do it", "",
                "Read the Defaults table.",
                "Follow the user's global instructions.",
            ]))
            write(root, "a/reference.md", "The Defaults table says so.\n")
            write(root, "set-up-machine/references/global-instructions.md", "The global instructions file.\n")
            hits = default_tools.scan_mentions(root)
        self.assertEqual(
            [(h.path, h.line, h.tool) for h in hits],
            [("a/SKILL.md", 9, "Defaults table"), ("a/SKILL.md", 10, "global instructions"),
             ("a/reference.md", 1, "Defaults table")],
        )

    def test_mentions_are_reported_even_with_no_tool_named(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write(root, "a/SKILL.md", "Read the Defaults table.\n")
            out = io.StringIO()
            with redirect_stdout(out):
                code = default_tools.main(["--skills", d, "--global", str(root / "missing.md")])
        self.assertEqual(code, 0)
        self.assertIn("a/SKILL.md:1 Defaults table: Read the Defaults table.", out.getvalue())


if __name__ == "__main__":
    unittest.main()
