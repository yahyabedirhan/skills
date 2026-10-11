"""Codex plugin policies, custom config homes and credential-free audit fixtures."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from setupmachine import plugins
from setupmachine.codex_config import parse
from setupmachine.harnesses import codex as codex_plugins

ENTRY = {"name": "search", "kind": "bundle", "source": "search@catalog", "harnesses": ["codex"],
         "mcp_policy": {"require_oauth": True, "approval_mode": "prompt",
             "enabled_tools": ["search", "fetch"], "disabled_tools": ["paid"]}}

class CodexPluginsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name) / "custom-codex"
        self.folder.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def installed(self, text=''):
        text += '\n[plugins."search@catalog"]\nenabled = true\n'
        (self.folder / 'config.toml').write_text(codex_plugins.propose(text, ENTRY))
        p = self.folder / 'plugins/cache/catalog/search/1/.claude-plugin/plugin.json'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({'name': 'search'}))

    def test_missing_disabled_or_uncached_bundle_fails(self):
        state = codex_plugins.Codex(self.folder)
        self.assertEqual(state.check('search', ENTRY)[0][0], 'FAIL')
        self.installed()
        p = self.folder / 'config.toml'
        p.write_text(p.read_text().replace('enabled = true', 'enabled = false', 1))
        self.assertEqual(codex_plugins.Codex(self.folder).check('search', ENTRY)[0][0], 'FAIL')

    def test_policy_and_installation_pass_but_missing_oauth_is_a_gap(self):
        self.installed()
        with patch.object(codex_plugins.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='[{"name":"search","auth_status":"not_logged_in"}]')):
            lines = codex_plugins.Codex(self.folder, 'codex').check('search', ENTRY)
        self.assertFalse(any(s == 'FAIL' for s, _ in lines), lines)
        self.assertTrue(any(s == 'gap' and 'OAuth' in t for s, t in lines), lines)

    def test_oauth_uses_cli_status_without_reading_credentials(self):
        self.installed()
        with patch.object(codex_plugins.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='[{"name":"search","auth_status":"o_auth"}]')) as run:
            state = codex_plugins.Codex(self.folder, 'codex')
            self.assertTrue(any(s == 'ok' and 'OAuth' in t for s, t in state.check('search', ENTRY)))
            state.check('search', ENTRY)
            self.assertEqual(run.call_count, 1)
            self.assertEqual(run.call_args.args[0], ['codex', 'mcp', 'list', '--json'])

    def test_drift_in_paid_tool_restriction_fails(self):
        self.installed()
        p = self.folder / 'config.toml'
        p.write_text(p.read_text().replace('disabled_tools = ["paid"]', 'disabled_tools = []'))
        self.assertTrue(any(s == 'FAIL' for s, _ in codex_plugins.Codex(self.folder).check('search', ENTRY)))

    def test_proposal_preserves_unrelated_settings_comments_and_repeat_run(self):
        text = '# user comment\nmodel = "chosen"\n[plugins."search@catalog"]\nenabled = true # keep\n[plugins."search@catalog".mcp_servers.search]\ndisabled_tools = ["other"] # keep too\n[unrelated]\nvalue = "unchanged"\n'
        result = codex_plugins.propose(text, ENTRY)
        self.assertIn('enabled = true # keep', result)
        self.assertIn('# keep too', result)
        self.assertEqual(parse(result)['unrelated'], {'value': 'unchanged'})
        self.assertEqual(parse(result)['plugins']['search@catalog']['mcp_servers']['search']['disabled_tools'], ['other', 'paid'])
        self.assertEqual(codex_plugins.propose(result, ENTRY), result)

    def test_stricter_allowlist_is_preserved(self):
        text = '[plugins."search@catalog".mcp_servers.search]\nenabled_tools = ["search"]\n'
        result = codex_plugins.propose(text, ENTRY)
        self.assertEqual(parse(result)['plugins']['search@catalog']['mcp_servers']['search']['enabled_tools'], ['search'])

    def test_multiline_toml_and_unknown_policy_are_refused(self):
        with self.assertRaises(codex_plugins.PluginError):
            codex_plugins.propose('note = """long\ntext"""\n', ENTRY)
        with self.assertRaises(codex_plugins.PluginError):
            codex_plugins.validate({**ENTRY, 'mcp_policy': {'url': 'unowned'}}, 'fixture')

    def test_malformed_approval_modes_report_validation_errors(self):
        for value in ([], {}, 1, None, 'on-request'):
            with self.assertRaises(codex_plugins.PluginError):
                codex_plugins.validate({**ENTRY, 'mcp_policy': {'approval_mode': value}}, 'fixture')

    def test_scalar_owned_tables_are_refused_without_crashing_audit(self):
        text = '[plugins."search@catalog".mcp_servers]\nsearch = false\n'
        with self.assertRaises(codex_plugins.PluginError):
            codex_plugins.propose(text, ENTRY)
        self.installed()
        (self.folder / 'config.toml').write_text('[plugins]\n"search@catalog" = false\n')
        self.assertEqual(codex_plugins.Codex(self.folder).check('search', ENTRY)[0][0], 'FAIL')

    def test_hash_inside_value_does_not_replace_real_comment(self):
        entry = {'name': 'docs', 'kind': 'mcp', 'harnesses': ['codex'], 'server': {'url': 'https://example.com/mcp'}}
        text = '[mcp_servers.docs]\nurl = "https://old.example/a # fragment" # real comment\n'
        result = codex_plugins.propose(text, entry)
        self.assertIn('url = "https://example.com/mcp" # real comment', result)
        self.assertNotIn('fragment', result)

    def test_standalone_mcp_transport_is_compared(self):
        entry = {'name': 'docs', 'kind': 'mcp', 'harnesses': ['codex'], 'server': {'url': 'https://example.com/mcp'}}
        self.assertTrue(any(s == 'FAIL' for s, _ in codex_plugins.Codex(self.folder).check('docs', entry)))
        (self.folder / 'config.toml').write_text(codex_plugins.propose('', entry))
        self.assertEqual(codex_plugins.Codex(self.folder).check('docs', entry)[0][0], 'ok')

    def test_malformed_existing_tool_lists_need_guided_review(self):
        for value in ('false', '[{}]', '"paid"'):
            text = '[plugins."search@catalog".mcp_servers.search]\ndisabled_tools = ' + value + '\n'
            with self.assertRaises(codex_plugins.PluginError):
                codex_plugins.propose(text, ENTRY)
            self.installed()
            p = self.folder / 'config.toml'
            p.write_text(p.read_text().replace('disabled_tools = ["paid"]', 'disabled_tools = ' + value))
            lines = codex_plugins.Codex(self.folder).check('search', ENTRY)
            self.assertTrue(any(s == 'FAIL' for s, _ in lines), lines)

    def test_plugin_checker_honors_explicit_codex_home(self):
        self.installed()
        home = Path(self.tmp.name) / 'fixture-home'
        pointer = home / '.config/agents/source.md'
        pointer.parent.mkdir(parents=True)
        pointer.write_text('- Repository: `fixture/workstation`\n- Clone: `~/workstation`\n')
        source = home / 'workstation/setup/installs.json'
        source.parent.mkdir(parents=True)
        source.write_text(json.dumps({'plugins': [ENTRY]}))
        lines = plugins.check(home, codex_home=self.folder)
        self.assertTrue(any(s == 'ok' and 'installed and enabled' in t for s, t in lines), lines)

    def test_a_permission_deny_supplies_a_tool_the_policy_omits(self):
        from setupmachine import rules as rule_table
        path = Path(self.tmp.name) / 'permissions.json'
        path.write_text(json.dumps({'version': 1, 'rules': [{
            'id': 'search-agent', 'level': 'deny', 'summary': 'the agent tool',
            'reason': 'It spends credit.', 'instruction': 'Use search and fetch.',
            'match': {'server': '^search$', 'tool': '^agent$'},
            'samples': {'covers': ['mcp__search__agent'], 'leaves': ['mcp__search__search']}}]}))
        rows = rule_table.load(path, personal=True)
        entry = {**ENTRY, 'mcp_policy': {'enabled_tools': ['search', 'fetch'], 'require_oauth': True,
                                         'disabled_tools': ['paid']}}
        result = codex_plugins.propose('', entry, rows)
        tools = parse(result)['plugins']['search@catalog']['mcp_servers']['search']['disabled_tools']
        self.assertEqual(tools, ['agent', 'paid'])

if __name__ == '__main__':
    unittest.main()
