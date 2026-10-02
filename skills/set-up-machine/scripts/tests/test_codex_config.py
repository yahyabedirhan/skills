"""Synthetic setup proposals and persisted audits: no login or live config."""
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import verify
from setupmachine import codex_config as config

PREFERENCES = {"sandbox_mode": "workspace-write", "approval_policy": "on-request", "approvals_reviewer": "auto_review"}


@unittest.skipIf(config.tomllib is None, "Codex TOML fixtures require Python 3.11+")
class ConfigurationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name).resolve()
        self.clone = self.home / "personal"
        self.folder = self.home / "custom-codex"
        self.folder.mkdir()
        self.write(".config/agents/source.md", f"- Repository: owner/private\n- Clone: `{self.clone}`\n")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, relative, text):
        path = self.home / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def source(self, text=None):
        return self.write("personal/agents/codex.toml", text or '\n'.join(f'{key} = "{value}"' for key, value in PREFERENCES.items()))

    def test_fresh_setup_repeat_audit_and_missing_reviewer_drift(self):
        self.source()
        preferences = config.load(self.home)
        target = self.folder / "config.toml"
        target.write_text(config.propose("", preferences))
        first = target.read_text()
        self.assertEqual(config.propose(first, preferences), first)
        self.assertEqual([status for status, _ in config.audit(self.home, self.folder) if status == "same"], ["same"] * 3)
        target.write_text(first.replace('approvals_reviewer = "auto_review"\n', ""))
        self.assertIn(("FAIL", "persisted approvals_reviewer is missing or differs from the declared source"), config.audit(self.home, self.folder))
        target.write_text(first.replace('"auto_review"', '"user"'))
        self.assertTrue(any(status == "FAIL" and "approvals_reviewer" in text for status, text in config.audit(self.home, self.folder)))

    def test_unrelated_comments_tables_profiles_hooks_and_newlines_preserved(self):
        text = '# A comment\r\nmodel = "example"\r\napproval_policy = \'never\' # keep comment\r\n\r\n[features]\r\nhooks = true\r\n[hooks.state."example"]\r\ntrusted_hash = "hash"\r\n'
        proposal = config.propose(text, {"approval_policy": "on-request", "approvals_reviewer": "user"})
        self.assertIn('approval_policy = "on-request" # keep comment\r\n', proposal)
        self.assertTrue(proposal.endswith(text[text.index("[features]"):]))
        self.assertEqual(config.parse(proposal)["model"], "example")
        self.assertNotIn("sandbox_mode", config.parse(proposal))

    def test_no_final_newline_is_preserved_for_replacements(self):
        self.assertEqual(config.propose('approvals_reviewer = "user"', {"approvals_reviewer": "auto_review"}), 'approvals_reviewer = "auto_review"')

    def test_additions_go_at_root_even_when_config_starts_with_table(self):
        proposal = config.propose('[features]\nhooks = true\n', {"approvals_reviewer": "user"})
        self.assertEqual(config.parse(proposal), {"approvals_reviewer": "user", "features": {"hooks": True}})

    def test_missing_source_and_omitted_preferences_remain_user_managed(self):
        self.assertEqual(config.load(self.home), {})
        self.source('approval_policy = "on-request"')
        self.assertEqual(config.load(self.home), {"approval_policy": "on-request"})
        self.assertEqual(config.propose('model = "example"\n', {}), 'model = "example"\n')

    def test_invalid_input_rejected_without_echoing_values(self):
        for text in ('model = "PRIVATE_SENTINEL"', 'approval_policy = "untrusted"', 'approval_policy = "on-failure"',
                     'approvals_reviewer = true', '[approval_policy]\nsandbox_approval = true',
                     'sandbox_mode = "workspace-write"\nsandbox_mode = "read-only"', 'approvals_reviewer = PRIVATE_SENTINEL',
                     '[nested]\nvalue = "PRIVATE_SENTINEL"'):
            with self.subTest(text=text):
                self.source(text)
                lines = config.audit(self.home, self.folder)
                self.assertEqual(lines[0][0], "FAIL")
                self.assertNotIn("PRIVATE_SENTINEL", str(lines))

    def test_conflicting_and_stricter_configuration_stays_untouched(self):
        for text in ('default_permissions = "profile"\n', 'sandbox_mode = "read-only"\n',
                     '[approval_policy]\nsandbox_approval = false\n', '[profiles.old]\nsandbox_mode = "read-only"\n'):
            with self.subTest(text=text):
                target = self.write("custom-codex/config.toml", text)
                with self.assertRaises(config.ConfigError):
                    config.propose(text, PREFERENCES)
                self.assertEqual(target.read_text(), text)

    def test_unfamiliar_root_syntax_is_a_gap_rather_than_lossy_rewrite(self):
        for text in ('"approvals_reviewer" = "user"\n', 'model = """text\n[features]\n"""\n'):
            with self.assertRaises(config.ConfigError):
                config.propose(text, {"approvals_reviewer": "auto_review"})

    def test_default_permissions_preserved_when_only_reviewer_is_owned(self):
        text = 'default_permissions = "profile"\n'
        self.assertEqual(config.parse(config.propose(text, {"approvals_reviewer": "user"})),
                         {"default_permissions": "profile", "approvals_reviewer": "user"})

    def test_overrides_and_effective_support_are_separate_from_matching_defaults(self):
        self.source()
        profile = self.write("custom-codex/work.config.toml", '# Preserve profile comment\napprovals_reviewer = "user"\n')
        before = profile.read_bytes()
        self.write("custom-codex/config.toml", config.propose('profile = "work"\n[projects."/example"]\ntrust_level = "trusted"\n', PREFERENCES))
        lines = config.audit(self.home, self.folder)
        self.assertEqual(sum(status == "same" for status, _ in lines), 3)
        self.assertEqual(sum(status == "override" for status, _ in lines), 2)
        self.assertTrue(any(status == "gap" and "top-level profile" in text for status, text in lines))
        self.assertTrue(any("managed requirements" in text and "unverified" in text for _, text in lines))
        self.assertEqual(profile.read_bytes(), before)

    def test_actual_home_honors_codex_home_without_printing_its_value(self):
        self.source()
        command = f"python3 {SCRIPTS / 'pre_tool_hook.py'} --harness codex"
        # An untrusted hook's error contains both the folder and its trust key.
        # Redaction must cover every occurrence of the environment path.
        self.write("custom-codex/hooks.json", json.dumps({"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"command": command}]}]}}))
        out = io.StringIO()
        with patch.object(Path, "home", return_value=self.home), patch.dict(os.environ, {"CODEX_HOME": str(self.folder)}), patch.object(config, "audit", return_value=[]) as audit:
            verify.main(["--home", str(self.home), "--no-codex"], out)
        self.assertEqual(audit.call_args.args[1], self.folder)
        self.assertIn("<Codex config home>", out.getvalue())
        self.assertNotIn(str(self.folder), out.getvalue())

    def test_custom_home_is_used_for_rules_hooks_and_preferences(self):
        self.source()
        command = f"python3 {SCRIPTS / 'pre_tool_hook.py'} --harness codex"
        hooks = self.write("custom-codex/hooks.json", json.dumps({"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"command": command}]}]}}))
        text = f'[hooks.state."{hooks}:pre_tool_use:0:0"]\ntrusted_hash = "{verify.codex_trust_hash(command)}"\n'
        self.write("custom-codex/config.toml", config.propose(text, PREFERENCES))
        self.write("custom-codex/rules/example.rules", "fixture")
        self.assertEqual([status for status, text in verify.check_wiring(self.home, self.folder) if text.startswith("Codex")], ["wired"])
        with patch.object(verify.subprocess, "run") as run:
            run.return_value.stdout = '{"decision":"forbidden"}'
            verify.check_codex(verify.rule_table.load(), self.home, "codex", self.folder)
            self.assertTrue(all(str(self.folder / "rules/example.rules") in call.args[0] for call in run.call_args_list))
        out = io.StringIO()
        with patch.dict(os.environ, {"CODEX_HOME": str(self.home / "ambient")}), patch.object(config, "audit", return_value=[]) as audit:
            verify.main(["--home", str(self.home), "--no-codex"], out)
            self.assertEqual(audit.call_args.args[1], self.home / ".codex")
            verify.main(["--home", str(self.home), "--codex-home", str(self.folder), "--no-codex"], out)
            self.assertEqual(audit.call_args.args[1], self.folder)


class SupportTest(unittest.TestCase):
    def test_old_python_reports_gap_without_affecting_hook_imports(self):
        with patch.object(config, "tomllib", None):
            with self.assertRaisesRegex(config.ConfigError, "Python 3.11"):
                config.parse("")

    def test_support_requires_negative_control_and_isolates_environment(self):
        from subprocess import CompletedProcess
        with patch.object(config.subprocess, "run", side_effect=[
                CompletedProcess([], 1, "", "Error: failed to load bootstrap configuration\nunknown variant `set-up-machine-invalid-value`, expected user\nin `approvals_reviewer`"),
                CompletedProcess([], 0, "", "")]) as run:
            self.assertEqual(config.support({"approvals_reviewer": "user"}, "/example/codex")[0][0], "supported")
            for call in run.call_args_list:
                self.assertEqual(set(call.kwargs["env"]), {"HOME", "CODEX_HOME", "PATH"})
                self.assertTrue(call.kwargs["cwd"].startswith(tempfile.gettempdir()))
        with patch.object(config.subprocess, "run", return_value=CompletedProcess([], 0, "", "")):
            self.assertEqual(config.support({"approvals_reviewer": "user"}, "codex")[0][0], "gap")

    def test_probe_finds_an_interpreter_beside_the_codex_program_or_its_link_target(self):
        # An npm-installed codex under nvm starts with `#!/usr/bin/env node`, and
        # node sits in nvm's bin folder, not in os.defpath. The fake node acts as Codex.
        node = ("#!/bin/sh\n"
                "if grep -q set-up-machine-invalid-value \"$CODEX_HOME/config.toml\"; then\n"
                "  key=$(cut -d' ' -f1 \"$CODEX_HOME/config.toml\")\n"
                "  printf 'failed to load bootstrap configuration\\nunknown variant `set-up-machine-invalid-value`\\nin `%s`\\n' \"$key\" >&2\n"
                "  exit 1\n"
                "fi\n")
        for beside in ("link", "target"):
            with self.subTest(node_beside=beside), tempfile.TemporaryDirectory() as tmp:
                bin_folder, package = Path(tmp) / "bin", Path(tmp) / "lib" / "codex" / "bin"
                bin_folder.mkdir()
                package.mkdir(parents=True)
                script = package / "codex.js"
                script.write_text("#!/usr/bin/env node\n")
                (bin_folder / "codex").symlink_to(script)
                interpreter = (bin_folder if beside == "link" else package) / "node"
                interpreter.write_text(node)
                for program in (script, interpreter):
                    program.chmod(0o755)
                lines = config.support({"approvals_reviewer": "user"}, str(bin_folder / "codex"))
                self.assertEqual(lines[0][0], "supported", lines)

    def test_random_probe_failure_is_not_recognition(self):
        from subprocess import CompletedProcess
        for diagnostic in ("unrelated failure", "wrapper failed for set-up-machine-invalid-value",
                           "failed to load bootstrap configuration\nunknown variant `set-up-machine-invalid-value`\nin `other_key`"):
            with patch.object(config.subprocess, "run", return_value=CompletedProcess([], 1, "", diagnostic)):
                self.assertEqual(config.support({"approvals_reviewer": "user"}, "codex")[0][0], "gap")

    def test_positive_combination_rejection_fails_even_after_recognition(self):
        from subprocess import CompletedProcess
        with patch.object(config.subprocess, "run", side_effect=[
                CompletedProcess([], 1, "", "failed to load bootstrap configuration\nunknown variant `set-up-machine-invalid-value`\nin `approvals_reviewer`"),
                CompletedProcess([], 1, "", "rejected combination")]):
            lines = config.support({"approvals_reviewer": "user"}, "codex")
            self.assertEqual(lines[0][0], "FAIL")
            self.assertIn("rejected", lines[0][1])


if __name__ == "__main__":
    unittest.main()
