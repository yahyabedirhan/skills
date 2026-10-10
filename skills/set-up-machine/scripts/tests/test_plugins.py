"""Tests for the plugins setup area: the `plugins` list in agents/installs.json against each harness.

python3 -m unittest discover -s skills/set-up-machine/scripts/tests
"""
import io
import json
import re
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
        for line in lines:
            self.assertIn("declaration matches, readiness only", line)
            self.assertIn("latest release is unverified", line)

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
        self.installs({**MCP, "harnesses": ["codex", "opencode", "claude-code"]})
        lines = self.lines()
        for label in ("Codex", "opencode"):
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

    def test_verify_separates_persisted_checks_from_latest_versions(self):
        self.installs(EXA)
        self.claude_has("exa@claude-plugins-official")
        out = io.StringIO()
        verify.main(["--home", str(self.home), "--rules", str(TABLE), "--no-codex"], out)
        self.assertRegex(out.getvalue(), r"freshness +gap +Latest harness, skill, plugin and tool versions")
        self.assertIn("not remote releases", out.getvalue())

    def test_verify_prints_plugin_lines(self):
        self.installs(EXA)
        self.claude_has("exa@claude-plugins-official")
        out = io.StringIO()
        verify.main(["--home", str(self.home), "--rules", str(TABLE), "--no-codex"], out)
        got = [l for l in out.getvalue().splitlines() if l.startswith("plugin ")]
        self.assertEqual(len(got), 2, got)
        self.assertRegex(got[0], r"^plugin +ok +Claude Code: exa")


WEB = {"name": "web", "kind": "bundle", "source": "npm:pi-web-access@latest", "harnesses": ["pi"]}
TOOLS = {"name": "tools", "kind": "bundle", "source": "git:github.com/owner-a/pi-tools", "harnesses": ["pi"]}


class PiPluginsTest(PluginsHome):
    """Pi takes bundles as extensions in <agent-dir>/settings.json `packages`, and standalone servers in <agent-dir>/mcp.json."""

    def setUp(self):
        super().setUp()
        (self.home / ".pi/agent").mkdir(parents=True)

    def pi_has(self, *extensions, **extra):
        self.write(".pi/agent/settings.json", {"defaultModel": "model-a", "packages": list(extensions), **extra})

    def test_a_pi_extension_source_is_valid_only_on_an_entry_for_pi_alone(self):
        for source in ("npm:pi-web-access@latest", "npm:@scope-a/pi-tools", "git:github.com/owner-a/pi-tools",
                       "https://github.com/owner-a/pi-tools"):
            self.installs({**WEB, "source": source})
            self.assertFalse(any(l.startswith("FAIL ") and "plugins[0]" in l for l in self.lines()), source)
        for entry, message in (({**WEB, "harnesses": ["pi", "claude-code"]}, "fits only an entry whose only harness is pi"),
                               ({**EXA, "harnesses": ["pi"]}, "Pi takes a bundle only by its Pi extension source"),
                               ({**EXA, "harnesses": ["claude-code", "pi"]}, "Pi takes a bundle only by its Pi extension source"),
                               ({**WEB, "source": "./pi-tools"}, "source must be"),
                               ({**WEB, "source": "npm:"}, "source must be"),
                               ({**WEB, "source": "git:github.com/owner-a"}, "source must be"),
                               ({**WEB, "marketplace": "owner-a/market"}, "a Pi extension takes no marketplace")):
            self.installs(entry)
            lines = self.lines()
            self.assertEqual(len(lines), 1, (entry, lines))
            self.assertTrue(lines[0].startswith("FAIL "), lines[0])
            self.assertIn(message, lines[0])

    def test_the_same_pi_extension_twice_is_refused(self):
        self.installs(WEB, {**WEB, "name": "web-again", "source": "npm:pi-web-access"})
        lines = self.lines()
        self.assertEqual(len(lines), 1, lines)
        self.assertIn("names the same Pi extension as plugins[0]", lines[0])

    def test_an_extension_in_settings_is_ok_as_a_string_or_an_object(self):
        self.installs(WEB, TOOLS)
        self.pi_has("npm:pi-web-access@latest", {"source": "git:github.com/owner-a/pi-tools", "skills": []})
        lines = self.lines()
        self.assertEqual(len(lines), 2, lines)
        self.assertRegex(lines[0], r"^ok Pi: web \(bundle\) npm:pi-web-access@latest is an extension in .*\.pi/agent/settings\.json")
        self.assertRegex(lines[1], r"^ok Pi: tools \(bundle\) git:github\.com/owner-a/pi-tools is an extension in ")

    def test_moving_sources_do_not_claim_installed_code_is_latest(self):
        for source in ("npm:pi-web-access@latest", "npm:@scope-a/pi-tools",
                       "git:github.com/owner-a/pi-tools"):
            self.installs({**WEB, "source": source})
            self.pi_has(source)
            line = self.lines()[0]
            self.assertEqual(len(self.lines()), 1)
            self.assertTrue(line.startswith("ok "), line)
            self.assertIn("declaration matches", line)
            self.assertIn("installed code and latest release are unverified", line)

    def test_a_missing_extension_or_another_version_fails(self):
        self.installs(WEB, TOOLS)
        self.pi_has("npm:pi-web-access", "https://github.com/owner-a/pi-tools.git")
        lines = self.lines()
        self.assertRegex(lines[0], r"^FAIL Pi: web \(bundle\) .*has npm:pi-web-access instead of npm:pi-web-access@latest")
        self.assertRegex(lines[1], r"^FAIL Pi: tools \(bundle\) .*has https://github\.com/owner-a/pi-tools\.git instead")
        self.pi_has()
        self.assertRegex(self.lines()[0], r"^FAIL Pi: web \(bundle\) npm:pi-web-access@latest isn't an extension in .*settings\.json")
        (self.home / ".pi/agent/settings.json").unlink()
        self.assertRegex(self.lines()[0], r"^FAIL Pi: web \(bundle\) npm:pi-web-access@latest isn't an extension in ")

    def test_a_configured_extension_the_list_leaves_out_is_extra(self):
        self.installs(WEB)
        self.pi_has("npm:pi-web-access@latest", "npm:@scope-a/pi-todo")
        lines = self.lines()
        self.assertIn("extra Pi: npm:@scope-a/pi-todo is an extension in "
                      f"{self.home / '.pi/agent/settings.json'} but not in the plugins list", lines)
        self.assertEqual(len(lines), 2, lines)

    def test_pi_not_set_up_is_not_applicable(self):
        import shutil
        shutil.rmtree(self.home / ".pi")
        self.installs(WEB, {**MCP, "harnesses": ["pi"]})
        lines = self.lines()
        self.assertEqual(len(lines), 2, lines)
        for l in lines:
            self.assertRegex(l, r"^n/a Pi: .* isn't checked; Pi is not set up here")

    def test_another_agent_folder_is_checked_when_given(self):
        import shutil
        shutil.rmtree(self.home / ".pi")
        folder = self.home / "elsewhere/pi"
        self.write("elsewhere/pi/settings.json", {"packages": ["npm:pi-web-access@latest"]})
        self.installs(WEB)
        lines = [f"{s} {t}" for s, t in plugins.check(self.home, folder)]
        self.assertRegex(lines[0], r"^ok Pi: web \(bundle\) .* is an extension in " + re.escape(f"{folder}/settings.json"))

    def test_a_standalone_mcp_server_in_pi(self):
        self.installs({**MCP, "harnesses": ["pi"]})
        self.assertRegex(self.lines()[0], r"^FAIL Pi: docs \(mcp\) has no entry in .*\.pi/agent/mcp\.json")
        self.write(".pi/agent/mcp.json", {"mcpServers": {"docs": {"url": "https://other.example.com/mcp"}}})
        self.assertRegex(self.lines()[0], r"^FAIL Pi: docs \(mcp\) entry in .*mcp\.json differs")
        self.write(".pi/agent/mcp.json", {"mcpServers": {"docs": MCP["server"], "mine": {"command": "x"}}})
        self.assertRegex(self.lines()[0], r"^ok Pi: docs \(mcp\) is in .*\.pi/agent/mcp\.json")
        self.write(".pi/agent/mcp.json", "{not json")
        self.assertRegex(self.lines()[0], r"^FAIL Pi: docs \(mcp\) can't be checked; .*mcp\.json isn't valid JSON")

    def test_an_mcp_server_name_pi_rejects_is_refused(self):
        self.installs({**MCP, "name": "my docs", "harnesses": ["pi"]})
        self.assertIn("Pi takes server names of letters, digits, _ and -", self.lines()[0])

    def test_built_in_mcp_turned_off_is_a_gap(self):
        self.installs({**MCP, "harnesses": ["pi"]})
        self.write(".pi/agent/mcp.json", {"mcpServers": {"docs": MCP["server"]}})
        self.pi_has(extensions=["-builtin:mcp"])
        self.assertRegex(self.lines()[0], r"^gap Pi: docs \(mcp\) is in .*mcp\.json, but -builtin:mcp in .*settings\.json "
                                          r"turns off Pi's built-in MCP")

    def test_a_git_extension_not_installed_yet_is_ok(self):
        self.installs(TOOLS)
        self.pi_has(TOOLS["source"])
        self.assertRegex(self.lines()[0], r"^ok Pi: tools \(bundle\) ")

    def test_verify_prints_pi_plugin_lines_for_the_agent_folder_it_resolves(self):
        folder = self.home / "elsewhere/pi"
        self.write("elsewhere/pi/settings.json", {"packages": ["npm:pi-web-access@latest"]})
        self.installs(WEB)
        out = io.StringIO()
        verify.main(["--home", str(self.home), "--rules", str(TABLE), "--no-codex", "--pi-agent-dir", str(folder)], out)
        got = [l for l in out.getvalue().splitlines() if l.startswith("plugin ")]
        self.assertEqual(len(got), 1, got)
        self.assertRegex(got[0], r"^plugin +ok +Pi: web \(bundle\) .*elsewhere/pi/settings\.json")


if __name__ == "__main__":
    unittest.main()
