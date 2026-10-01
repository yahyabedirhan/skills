"""Tests for the verify script: the rule table's samples against the hook, Codex's own
checker, each harness's hook wiring, and the personal repository the pointer names.

python3 -m unittest discover -s skills/set-up-machine/scripts/tests
"""
import io
import json
import os
import re
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


def no_personal_repository(home):
    """The pointer a machine with no personal repository holds, so other checks can pass."""
    pointer = Path(home) / ".config" / "agents" / "source.md"
    pointer.parent.mkdir(parents=True, exist_ok=True)
    pointer.write_text("# Personal repository\n\n- Repository: none\n")


def run(*argv):
    out = io.StringIO()
    code = verify.main(list(argv), out)
    return code, out.getvalue()


class RulesTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        no_personal_repository(self.dir)

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
        self.assertRegex(out, r"rules +ok +37 rows")

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
        no_personal_repository(self.home)

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


INSTRUCTIONS = """# Personal instructions

Notes here stay in this repository.

## Environment defaults

| Role | Tool | Why |
|---|---|---|
| `session-host` | `host-a` | a note that stays here |
| `agent` | `agent-a --flag` | |

## Personal workflow

- First workflow line.
- Second workflow line,
  carried on.
"""

SHARED = """# Global agent instructions

Only what describes this person's own workflow and explains a global rule. Anything a teammate would need goes in the project or a skill.

## Environment defaults

What this person uses for each role. A project's own environment defaults override a row. When a row is `none`, do what its last column says.

| Role | Tool | What it is | When none |
|---|---|---|---|
| `session-host` | {host} | where agent sessions run | Use this session. |
| `worktree-tool` | {worktree} | the tool that makes and frees worktrees | `git worktree add`. |
| `agent` | `agent-a --flag` | the command and flags that start a new agent session | This session's harness. |

<!-- set-up-machine:rules start. Generated by set-up-machine from its rule table and the personal repository's rows: change those, not these lines. -->
## Global rules

- **Denied:** a rule line.
<!-- set-up-machine:rules end -->

## Personal workflow

Rules for how this person works that pass the team test. Anything a project or a skill needs goes there instead.

{workflow}
"""

WORKFLOW = "- First workflow line.\n- Second workflow line,\n  carried on."


class PersonalHome:
    """A home folder copy with a pointer, the personal repository it names, and the shared file."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name).resolve()

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel, text):
        path = self.home / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def pointer(self, repository="`owner-a/personal`", clone="`~/code/personal`"):
        lines = ["# Personal repository", "", f"- Repository: {repository}"]
        if clone is not None:
            lines.append(f"- Clone: {clone}")
        self.write(".config/agents/source.md", "\n".join(lines) + "\n")

    def personal_repository(self, instructions=INSTRUCTIONS):
        self.write("code/personal/agents/instructions.md", instructions)

    def shared(self, host="`host-a`", worktree="`none`", workflow=WORKFLOW):
        self.write(".config/agents/AGENTS.md", SHARED.format(host=host, worktree=worktree, workflow=workflow))

    def lines(self):
        code, out = run("--home", str(self.home), "--rules", str(TABLE), "--no-codex")
        return code, [l for l in out.splitlines() if l.startswith("personal")]


class PersonalTest(PersonalHome, unittest.TestCase):
    """The pointer, the personal repository it names, and the shared file generated from it."""

    def test_a_missing_pointer_is_reported(self):
        code, lines = self.lines()
        self.assertRegex(lines[0], r"personal +FAIL +no pointer at .*/\.config/agents/source\.md")
        self.assertEqual(code, 1)

    def test_a_pointer_that_says_none_passes(self):
        self.pointer(repository="none", clone=None)
        code, lines = self.lines()
        self.assertRegex(lines[0], r"personal +none +no personal repository")
        self.assertEqual(code, 0)

    def test_a_pointer_without_a_repository_line_fails(self):
        self.write(".config/agents/source.md", "# Personal repository\n\nsomething else\n")
        code, lines = self.lines()
        self.assertRegex(lines[0], r"personal +FAIL +.*source\.md.*Repository")
        self.assertEqual(code, 1)

    def test_a_repository_that_is_not_owner_slash_repo_fails(self):
        self.pointer(repository="`just-a-name`")
        code, lines = self.lines()
        self.assertRegex(lines[0], r"personal +FAIL +.*<owner>/<repo>")

    def test_a_repository_without_a_clone_line_fails(self):
        self.pointer(clone=None)
        code, lines = self.lines()
        self.assertRegex(lines[0], r"personal +FAIL +.*Clone")

    def test_a_relative_clone_path_fails(self):
        self.pointer(clone="`code/personal`")
        code, lines = self.lines()
        self.assertRegex(lines[0], r"personal +FAIL +.*clone path `code/personal` doesn't start with `~/` or `/`")

    def test_a_clone_that_is_not_there_fails(self):
        self.pointer()
        code, lines = self.lines()
        self.assertRegex(lines[0], r"personal +FAIL +.*code/personal/agents/instructions\.md doesn't exist")
        self.assertEqual(code, 1)

    def test_the_shared_file_generated_from_the_personal_repository_passes(self):
        self.pointer()
        self.personal_repository()
        self.shared()
        code, lines = self.lines()
        self.assertEqual(len(lines), 1, lines)
        self.assertRegex(lines[0], r"personal +ok +owner-a/personal at .*code/personal: 2 environment defaults, "
                                   r"the personal workflow")
        self.assertEqual(code, 0)

    def test_an_absolute_clone_path_is_read_as_it_is(self):
        self.pointer(clone=f"`{self.home / 'code' / 'personal'}`")
        self.personal_repository()
        self.shared()
        code, lines = self.lines()
        self.assertRegex(lines[0], r"personal +ok")

    def test_a_tool_value_the_personal_repository_does_not_hold_fails(self):
        self.pointer()
        self.personal_repository()
        self.shared(host="`host-b`")
        code, lines = self.lines()
        self.assertIn("`session-host` is `host-b` in", lines[0])
        self.assertIn("`host-a` in", lines[0])
        self.assertEqual(code, 1)

    def test_a_role_the_personal_repository_leaves_out_is_none(self):
        self.pointer()
        self.personal_repository()
        self.shared(worktree="`tool-b`")
        code, lines = self.lines()
        self.assertRegex(lines[0], r"personal +FAIL +.*`worktree-tool` is `tool-b` in .*, `none` in ")

    def test_a_role_missing_from_the_shared_file_fails(self):
        self.pointer()
        self.personal_repository(INSTRUCTIONS.replace("| `agent` |", "| `notification-method` |"))
        self.shared()
        code, lines = self.lines()
        self.assertTrue(any("`notification-method` has no row in" in l for l in lines), lines)
        self.assertEqual(code, 1)

    def test_personal_workflow_lines_that_differ_fail(self):
        self.pointer()
        self.personal_repository()
        self.shared(workflow="- First workflow line.\n- A line written by hand.")
        code, lines = self.lines()
        self.assertRegex(lines[0], r"personal +FAIL +.*Personal workflow` in .* differs from")
        self.assertEqual(code, 1)

    def test_a_missing_shared_file_fails(self):
        self.pointer()
        self.personal_repository()
        code, lines = self.lines()
        self.assertRegex(lines[0], r"personal +FAIL +.*\.config/agents/AGENTS\.md doesn't exist")

    def test_an_instructions_file_without_its_sections_fails(self):
        self.pointer()
        self.personal_repository("# Personal instructions\n\nNothing yet.\n")
        self.shared()
        code, lines = self.lines()
        self.assertRegex(lines[0], r"personal +FAIL +.*instructions\.md has no `## Environment defaults` table")


def personal_row(id, level, match, covers, leaves=()):
    return {"id": id, "level": level, "summary": id, "match": match, "reason": "A reason.",
            "instruction": "Go ahead.", "samples": {"covers": list(covers), "leaves": list(leaves)}}


ALLOW_MCP = personal_row("server-a-read", "allow", {"server": "server-a", "tool": "^read_"},
                         ["mcp__server-a__read_item"], ["mcp__server-a__write_item"])
DENY_MISSING_TOOL = personal_row("tool-missing-wipe", "deny",
                                 {"program": "no-such-tool-for-this-test", "subcommands": [["wipe"]]},
                                 ["no-such-tool-for-this-test wipe all"], ["no-such-tool-for-this-test list"])


class PersonalPermissionsTest(PersonalHome, unittest.TestCase):
    """The personal repository's permissions file: its rows through the hook, and their entries in Claude Code."""

    def setUp(self):
        super().setUp()
        self.pointer()
        self.personal_repository()
        self.shared()

    def permissions(self, rows):
        self.write("code/personal/agents/permissions.json", json.dumps({"version": 1, "rules": rows}))

    def claude(self, permissions):
        hooks = {"PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": wired(HOOK, "claude-code")}]}]}
        self.write(".claude/settings.json", json.dumps({"permissions": permissions, "hooks": hooks}))

    def output(self):
        return run("--home", str(self.home), "--rules", str(TABLE), "--no-codex")

    def test_a_personal_allow_row_for_an_mcp_tool_is_present_in_claude_code_and_not_extra(self):
        self.permissions([ALLOW_MCP])
        self.claude({"deny": [], "allow": ["mcp__server-a__read_item", "mcp__server-a__read_list", "mcp__other__x"]})
        code, out = self.output()
        self.assertEqual(code, 0, out)
        self.assertRegex(out, r"rules +ok +37 rows and 1 personal rows")
        self.assertRegex(out, r"personal +present +Claude Code: server-a-read \(allow, personal\): "
                              r"mcp__server-a__read_item, mcp__server-a__read_list in ")
        self.assertNotIn("mcp__other__x", out)
        self.assertNotIn("extra", out)

    def test_a_personal_row_whose_tool_claude_code_lacks_is_not_applicable_and_says_why(self):
        self.permissions([ALLOW_MCP, DENY_MISSING_TOOL])
        self.claude({"deny": [], "allow": []})
        code, lines = self.lines()
        self.assertEqual(code, 0, lines)
        self.assertTrue(any(re.search(r"personal +n/a +Claude Code: server-a-read .*: no MCP tool in .* matches it", l)
                            for l in lines), lines)
        self.assertTrue(any(re.search(r"personal +n/a +Claude Code: tool-missing-wipe .*: no-such-tool-for-this-test "
                                      r"isn't on PATH", l) for l in lines), lines)

    def test_a_personal_row_claude_code_should_hold_but_lacks_fails(self):
        python = Path(sys.executable).name
        self.permissions([personal_row("python-wipe", "deny", {"program": python, "subcommands": [["wipe"]]},
                                       [f"{python} wipe"]),
                          personal_row("notes-read", "deny", {"paths": ["~/notes/**"], "access": "read"},
                                       ["~/notes/a.md"])])
        self.claude({"deny": ["Read(~/notes/**)"], "allow": []})
        code, lines = self.lines()
        self.assertEqual(code, 1, lines)
        self.assertTrue(any(re.search(r"personal +FAIL +Claude Code: python-wipe .*no entry in permissions\.deny", l)
                            for l in lines), lines)
        self.assertTrue(any(re.search(r"personal +present +Claude Code: notes-read .*Read\(~/notes/\*\*\)", l)
                            for l in lines), lines)
        self.claude({"deny": ["Read(~/notes/**)", f"Bash({python} wipe *)"], "allow": []})
        self.assertEqual(self.lines()[0], 0)

    def test_personal_samples_go_through_the_hook_with_the_rule_table(self):
        loosens = personal_row("rm-allowed", "allow", {"program": "rm", "flags": [["r"]]}, ["rm -rf x"])
        self.permissions([DENY_MISSING_TOOL, loosens])
        code, out = self.output()
        self.assertEqual(code, 1)
        self.assertIn("rm-allowed: `rm -rf x` got deny, expected allow", out)
        self.assertNotIn("tool-missing-wipe:", out.split("rules")[0])
        self.assertRegex(out, r"rules +FAIL +37 rows and 2 personal rows, \d+ samples, 1 wrong")

    def test_a_malformed_personal_row_fails(self):
        self.permissions([personal_row("bad", "block", {"program": "tool-a"}, ["tool-a"])])
        code, lines = self.lines()
        self.assertEqual(code, 1)
        self.assertRegex(lines[1], r"personal +FAIL +.*permissions\.json: rules\[0\]: level must be one of")

    def test_a_permissions_file_that_isnt_text_fails(self):
        path = self.home / "code/personal/agents/permissions.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\xff\xfe\x00binary")
        code, lines = self.lines()
        self.assertEqual(code, 1)
        self.assertRegex(lines[1], r"personal +FAIL +")

    def test_a_personal_row_with_a_table_id_fails(self):
        self.permissions([{**DENY_MISSING_TOOL, "id": "rm-recursive-force"}])
        code, lines = self.lines()
        self.assertEqual(code, 1)
        self.assertRegex(lines[1], r"personal +FAIL +.*'rm-recursive-force' is already a row of the rule table")


if __name__ == "__main__":
    unittest.main()
