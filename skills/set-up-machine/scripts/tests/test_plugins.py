"""Tests for the plugins setup area: the `plugins` list in agents/installs.json against each harness.

python3 -m unittest discover -s skills/set-up-machine/scripts/tests
"""
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

import verify  # noqa: E402
from setupmachine import plugins  # noqa: E402

TABLE = SCRIPTS.parent / "rules.json"
EXA = {"name": "exa", "kind": "bundle", "source": "exa@claude-plugins-official",
       "harnesses": ["claude-code", "cursor"]}
MCP = {"name": "docs", "kind": "mcp", "server": {"url": "https://mcp.example.com/mcp"}, "harnesses": ["cursor"]}


class PluginsHome(unittest.TestCase):
    """A home folder with a pointer, a workstation repo with installs.json, and harness folders."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name).resolve()
        self.write(".config/agents/source.md",
                   "# Workstation repo\n\n- Repository: `owner-a/personal`\n- Clone: `~/code/personal`\n")
        (self.home / ".claude").mkdir()
        (self.home / ".cursor").mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel, text):
        path = self.home / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text if isinstance(text, str) else json.dumps(text))
        return path

    def installs(self, *entries, **extra):
        self.write("code/personal/agents/installs.json", {"plugins": list(entries), **extra})

    def claude_has(self, *sources, enabled=True):
        records = {}
        for s in sources:
            folder = self.home / ".claude/plugins/cache" / s.replace("@", "/")
            self.write(str(folder.relative_to(self.home) / "mcp.json"),
                       {"mcpServers": {s.split("@")[0]: {"type": "http", "url": "https://x"}}} if s.startswith("exa@") else {})
            records[s] = [{"scope": "user", "version": "1", "installPath": str(folder)}]
        self.write(".claude/plugins/installed_plugins.json", {"version": 2, "plugins": records})
        self.write(".claude/settings.json", {"enabledPlugins": {s: enabled for s in sources}})

    def lines(self):
        return [f"{status} {text}" for status, text in plugins.check(self.home)]


class PluginsTest(PluginsHome):
    def test_no_plugins_list_says_nothing(self):
        self.write("code/personal/agents/installs.json", {"skills": []})
        self.assertEqual(self.lines(), [])

    def test_an_installed_and_enabled_bundle_is_ok_in_claude_code_and_imported_by_cursor(self):
        self.installs(EXA)
        self.claude_has("exa@claude-plugins-official")
        lines = self.lines()
        self.assertEqual(len(lines), 2, lines)
        self.assertRegex(lines[0], r"^ok Claude Code: exa \(bundle\) exa@claude-plugins-official is installed and enabled")
        self.assertRegex(lines[1], r"^ok Cursor: exa \(bundle\) is imported from Claude Code as plugin-exa-exa")

    def test_a_missing_or_disabled_bundle_fails_in_both(self):
        self.installs(EXA)
        lines = self.lines()
        self.assertRegex(lines[0], r"^FAIL Claude Code: exa \(bundle\) exa@claude-plugins-official isn't installed")
        self.assertRegex(lines[1], r"^FAIL Cursor: exa \(bundle\) .*imports bundles only from Claude Code")
        self.claude_has("exa@claude-plugins-official", enabled=False)
        self.assertRegex(self.lines()[0], r"^FAIL Claude Code: .*isn't enabled")

    def test_cursor_without_claude_code_in_the_list_still_needs_the_claude_code_install(self):
        self.installs({**EXA, "harnesses": ["cursor"]})
        self.claude_has("exa@claude-plugins-official")
        self.assertRegex(self.lines()[0], r"^ok Cursor: exa \(bundle\) is imported from Claude Code")

    def test_a_standalone_mcp_server_in_cursor(self):
        self.installs(MCP)
        self.assertRegex(self.lines()[0], r"^FAIL Cursor: docs \(mcp\) has no entry in .*\.cursor/mcp\.json")
        self.write(".cursor/mcp.json", {"mcpServers": {"docs": {"url": "https://other.example.com/mcp"}}})
        self.assertRegex(self.lines()[0], r"^FAIL Cursor: docs \(mcp\) .*mcp\.json differs")
        self.write(".cursor/mcp.json", {"mcpServers": {"docs": MCP["server"], "mine": {"url": "x"}}})
        self.assertRegex(self.lines()[0], r"^ok Cursor: docs \(mcp\) is in .*mcp\.json")

    def test_a_harness_not_set_up_is_not_applicable(self):
        (self.home / ".cursor").rmdir()
        self.installs(MCP)
        self.assertRegex(self.lines()[0], r"^n/a Cursor: docs \(mcp\) .*not set up here")

    def test_harnesses_without_delivery_are_gaps(self):
        self.installs({**MCP, "harnesses": ["codex", "opencode", "pi", "claude-code"]})
        lines = self.lines()
        for label in ("Codex", "opencode", "Pi"):
            self.assertTrue(any(l.startswith(f"gap {label}: docs (mcp)") for l in lines), (label, lines))
        self.assertTrue(any(l.startswith("gap Claude Code: docs (mcp)") for l in lines), lines)

    def test_an_entry_for_another_os_is_not_applicable(self):
        other = "linux" if sys.platform == "darwin" else "macos"
        self.installs({**MCP, "os": [other]})
        self.assertRegex(self.lines()[0], rf"^n/a docs: for {other} only")

    def test_enabled_bundles_the_list_leaves_out_are_extra(self):
        self.installs(EXA)
        self.claude_has("exa@claude-plugins-official", "skill-creator@claude-plugins-official")
        lines = self.lines()
        self.assertIn("extra Claude Code: skill-creator@claude-plugins-official is enabled but not in the plugins list; "
                      "Cursor imports it too", lines)

    def test_a_malformed_list_fails_and_checks_nothing(self):
        for entry, message in (({**EXA, "colour": "red"}, "unknown key 'colour'"),
                               ({**EXA, "kind": "app"}, "kind must be bundle or mcp"),
                               ({**EXA, "source": "exa"}, "source must be <plugin>@<marketplace>"),
                               ({**MCP, "server": {}}, "server needs url or command"),
                               ({**EXA, "harnesses": ["cursorr"]}, "unknown harness 'cursorr'"),
                               ({**EXA, "harnesses": []}, "harnesses can't be empty")):
            self.installs(entry)
            lines = self.lines()
            self.assertEqual(len(lines), 1, lines)
            self.assertIn(message, lines[0])
            self.assertTrue(lines[0].startswith("FAIL "), lines[0])
        self.installs(EXA, EXA)
        self.assertIn("name 'exa' is used twice", self.lines()[0])

    def test_no_workstation_repo_says_nothing(self):
        self.write(".config/agents/source.md", "# Workstation repo\n\n- Repository: none\n")
        self.assertEqual(self.lines(), [])

    def test_verify_prints_plugin_lines(self):
        self.installs(EXA)
        self.claude_has("exa@claude-plugins-official")
        out = io.StringIO()
        verify.main(["--home", str(self.home), "--rules", str(TABLE), "--no-codex"], out)
        got = [l for l in out.getvalue().splitlines() if l.startswith("plugin ")]
        self.assertEqual(len(got), 2, got)
        self.assertRegex(got[0], r"^plugin +ok +Claude Code: exa")


if __name__ == "__main__":
    unittest.main()
