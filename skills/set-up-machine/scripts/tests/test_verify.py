"""Tests for the verify script: the rule table's samples against the hook, Codex's own
checker, and each harness's hook wiring.

python3 -m unittest discover -s skills/set-up-machine/scripts/tests
"""
import io
import json
import os
import shlex
import stat
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

import verify  # noqa: E402

HOOK = SCRIPTS / "pre_tool_hook.py"
TABLE = SCRIPTS.parent / "rules.json"


def wired(script, harness):
    """The fail-open command the references tell the agent to write."""
    q = shlex.quote(str(script))
    fallback = "echo '{}'" if harness == "cursor" else "true"
    return f"[ -f {q} ] && python3 {q} --harness {harness} || {fallback}"


def run(*argv):
    out = io.StringIO()
    code = verify.main(list(argv), out)
    return code, out.getvalue()


class RulesTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def table(self, rows):
        path = self.dir / "rules.json"
        path.write_text(json.dumps({"version": 1, "rules": rows}))
        return path

    def row(self, **samples):
        return {"id": "rm-recursive-force", "level": "deny", "summary": "s", "reason": "r", "instruction": "i",
                "match": {"program": "rm", "flags": [["r"], ["f"]]}, "samples": samples}

    def test_every_sample_in_the_shipped_table_gets_its_rows_answer(self):
        code, out = run("--home", str(self.dir), "--rules", str(TABLE), "--no-codex")
        self.assertEqual(code, 0, out)
        self.assertRegex(out, r"rules +ok +33 rows")

    def test_a_sample_the_hook_misses_fails(self):
        path = self.table([self.row(covers=["rm -rf x", "rm -r x"])])
        code, out = run("--home", str(self.dir), "--rules", str(path), "--no-codex")
        self.assertEqual(code, 1)
        self.assertIn("rm-recursive-force: `rm -r x` got allow, expected deny", out)

    def test_a_near_miss_the_row_catches_fails(self):
        path = self.table([self.row(covers=["rm -rf x"], leaves=["rm -fr y"])])
        code, out = run("--home", str(self.dir), "--rules", str(path), "--no-codex")
        self.assertEqual(code, 1)
        self.assertIn("rm-recursive-force: `rm -fr y` should pass, but the row catches it", out)

    def test_ask_and_report_rows_are_checked_at_their_level(self):
        code, out = run("--home", str(self.dir), "--rules", str(TABLE), "--no-codex")
        self.assertEqual(code, 0, out)
        results = verify.check_rules(verify.rule_table.load(TABLE), self.dir)
        answers = {r.rule.id: r.answer for r in results if r.expected != "pass"}
        self.assertEqual(answers["git-push-mirror"], "ask")
        self.assertEqual(answers["gh-api-secrets"], "allow-and-report")
        self.assertEqual(answers["mail-send"], "deny")


class CodexTest(unittest.TestCase):
    """`codex execpolicy check` over the machine's Codex rules, with a stand-in `codex`."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)
        rules = self.home / ".codex" / "rules"
        rules.mkdir(parents=True)
        (rules / "set-up-machine.rules").write_text('prefix_rule(pattern=["rm", "-rf"], decision="forbidden")\n')
        self.codex = self.home / "codex"
        # Answers forbidden for `rm -rf …` and nothing else, as Codex would for that one rule.
        self.codex.write_text("#!/bin/sh\n"
                              "for a in \"$@\"; do case \"$a\" in --) shift; break;; *) shift;; esac; done\n"
                              "if [ \"$1 $2\" = \"rm -rf\" ]; then echo '{\"decision\":\"forbidden\"}'; else echo '{}'; fi\n")
        self.codex.chmod(self.codex.stat().st_mode | stat.S_IEXEC)

    def tearDown(self):
        self._tmp.cleanup()

    def test_each_plain_command_sample_is_checked_and_differences_are_listed(self):
        code, out = run("--home", str(self.home), "--rules", str(TABLE), "--codex", str(self.codex))
        self.assertIn("codex", out)
        self.assertRegex(out, r"codex +same +rm-recursive-force: rm -rf x -> forbidden")
        self.assertRegex(out, r"codex +differs +rm-recursive-force: rm -fr x -> no match, the row is deny")
        self.assertNotIn("git status && rm -rf x", out)  # a compound isn't an argv Codex can check
        # A difference is for the agent to read against references/codex.md, never a failure.
        self.assertFalse([l for l in out.splitlines() if l.startswith("codex") and "FAIL" in l], out)

    def test_no_codex_rules_skips_the_check(self):
        for f in (self.home / ".codex" / "rules").iterdir():
            f.unlink()
        code, out = run("--home", str(self.home), "--rules", str(TABLE), "--codex", str(self.codex))
        self.assertRegex(out, r"codex +skipped +no rules files in ")


class WiringTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name).resolve()

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel, data):
        path = self.home / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data if isinstance(data, str) else json.dumps(data))
        return path

    def lines(self, harness):
        code, out = run("--home", str(self.home), "--rules", str(TABLE), "--no-codex")
        return code, [l for l in out.splitlines() if l.startswith("hook") and harness in l]

    def claude(self, command, matcher="*"):
        self.write(".claude/settings.json", {"hooks": {"PreToolUse": [
            {"matcher": matcher, "hooks": [{"type": "command", "command": command, "timeout": 10}]}]}})

    def test_a_harness_without_its_folder_is_not_set_up(self):
        code, lines = self.lines("Codex")
        self.assertRegex(lines[0], r"hook +none +Codex: not set up here")
        self.assertEqual(code, 0)

    def test_claude_code_wired_to_a_script_that_exists(self):
        self.claude(wired(HOOK, "claude-code"))
        code, lines = self.lines("Claude Code")
        self.assertRegex(lines[0], r"hook +wired +Claude Code")
        self.assertEqual(code, 0)

    def test_a_script_that_is_gone_fails(self):
        self.claude(wired(self.home / "old" / "pre_tool_hook.py", "claude-code"))
        code, lines = self.lines("Claude Code")
        self.assertRegex(lines[0], r"hook +FAIL +Claude Code: .*doesn't exist")
        self.assertEqual(code, 1)

    def test_a_hook_on_some_tools_only_or_missing_fails(self):
        self.claude(wired(HOOK, "claude-code"), matcher="Bash")
        code, lines = self.lines("Claude Code")
        self.assertRegex(lines[0], r"hook +FAIL +Claude Code: no pre-tool hook for every tool")
        self.write(".claude/settings.json", {"permissions": {"deny": []}})
        self.assertEqual(self.lines("Claude Code")[0], 1)

    def test_codex_needs_the_trust_hash_of_its_hook(self):
        command = wired(HOOK, "codex")
        hooks = self.write(".codex/hooks.json", {"hooks": {"PreToolUse": [
            {"matcher": "*", "hooks": [{"type": "command", "command": command, "timeout": 10}]}]}})
        code, lines = self.lines("Codex")
        self.assertRegex(lines[0], r"hook +FAIL +Codex: .*not trusted")
        key = f"{hooks}:pre_tool_use:0:0"
        digest = verify.codex_trust_hash(command)
        self.write(".codex/config.toml", f'model = "x"\n\n[hooks.state."{key}"]\ntrusted_hash = "{digest}"\n')
        code, lines = self.lines("Codex")
        self.assertRegex(lines[0], r"hook +wired +Codex")
        self.assertEqual(code, 0)

    def test_the_trust_hash_is_codexs(self):
        # Worked out by hand from codex-rs/hooks: sha256 over the canonical JSON of the hook's identity.
        identity = ('{"event_name":"pre_tool_use","hooks":[{"async":false,"command":"x","timeout":10,'
                    '"type":"command"}],"matcher":"*"}')
        import hashlib
        self.assertEqual(verify.codex_trust_hash("x"), "sha256:" + hashlib.sha256(identity.encode()).hexdigest())
        code, out = run("--codex-trust-hash", "x")
        self.assertEqual((code, out.strip()), (0, verify.codex_trust_hash("x")))

    def test_opencode_plugin_names_a_script_that_exists(self):
        template = (SCRIPTS.parent / "references" / "opencode-plugin.js").read_text()
        command = json.dumps(["python3", str(HOOK), "--harness", "opencode"])
        self.write(".config/opencode/plugins/set-up-machine.js", template.replace("__HOOK_COMMAND__", command))
        code, lines = self.lines("opencode")
        self.assertRegex(lines[0], r"hook +wired +opencode")
        self.write(".config/opencode/plugins/set-up-machine.js", template.replace(
            "__HOOK_COMMAND__", json.dumps(["python3", "/gone/pre_tool_hook.py", "--harness", "opencode"])))
        code, lines = self.lines("opencode")
        self.assertRegex(lines[0], r"hook +FAIL +opencode: .*doesn't exist")

    def test_opencode_without_the_plugin_fails(self):
        (self.home / ".config" / "opencode").mkdir(parents=True)
        code, lines = self.lines("opencode")
        self.assertRegex(lines[0], r"hook +FAIL +opencode: no plugin")

    def test_cursor_needs_all_four_events(self):
        command = wired(HOOK, "cursor")
        events = {e: [{"command": command, "timeout": 10}] for e in
                  ("beforeShellExecution", "beforeMCPExecution", "beforeReadFile")}
        self.write(".cursor/hooks.json", {"version": 1, "hooks": events})
        code, lines = self.lines("Cursor")
        self.assertRegex(lines[0], r"hook +FAIL +Cursor: .*preToolUse")
        events["preToolUse"] = [{"command": command, "timeout": 10, "matcher": "^(Write|Delete|Grep)$"}]
        self.write(".cursor/hooks.json", {"version": 1, "hooks": events})
        code, lines = self.lines("Cursor")
        self.assertRegex(lines[0], r"hook +wired +Cursor")

    def test_the_script_runs_as_a_command(self):
        import subprocess
        proc = subprocess.run([sys.executable, str(SCRIPTS / "verify.py"), "--home", str(self.home), "--no-codex"],
                              capture_output=True, text=True, timeout=60, env={**os.environ})
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("rules", proc.stdout)


if __name__ == "__main__":
    unittest.main()
