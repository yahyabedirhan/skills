"""Tests for the verify script: the rule table's samples against the hook, Codex's own
checker, each harness's hook wiring, and the workstation repo the pointer names.

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
    """The pointer a machine with no workstation repo holds, so other checks can pass."""
    pointer = Path(home) / ".config" / "agents" / "source.md"
    pointer.parent.mkdir(parents=True, exist_ok=True)
    pointer.write_text("# Workstation repo\n\n- Repository: none\n")


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
        self.assertRegex(out, r"rules +ok +38 rows")

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
        self.write(".cursor/cli-config.json", {
            "version": 1, "editor": {"vimMode": False},
            "permissions": {"allow": [], "deny": ["Shell(rm -rf)"]},
            "approvalMode": "auto-review",
            "sandbox": {"mode": "enabled", "networkAccess": "user_config_with_defaults"}})
        code, lines = self.lines("Cursor")
        self.assertRegex(lines[0], r"hook +wired +Cursor")
        self.assertEqual(code, 0)

    def cursor_lines(self):
        code, out = run("--home", str(self.home), "--rules", str(TABLE), "--no-codex")
        return code, [line for line in out.splitlines() if line.startswith("cursor")]

    def test_cursor_without_a_folder_is_not_set_up(self):
        code, lines = self.cursor_lines()
        self.assertRegex(lines[0], r"cursor +none +Cursor: not set up here")
        self.assertEqual(code, 0)

    def test_cursor_run_mode_must_be_auto_review_with_the_sandbox(self):
        self.write(".cursor/cli-config.json", {"version": 1, "permissions": {"allow": [], "deny": []}})
        code, lines = self.cursor_lines()
        self.assertEqual(code, 1)
        self.assertRegex(lines[0], r"cursor +FAIL +Cursor: .*lacks approvalMode auto-review, sandbox.mode enabled")

        self.write(".cursor/cli-config.json", {"approvalMode": "allowlist", "sandbox": {"mode": "enabled"}})
        code, lines = self.cursor_lines()
        self.assertRegex(lines[0], r"lacks approvalMode auto-review")
        self.assertNotIn("sandbox.mode enabled", lines[0])

        self.write(".cursor/cli-config.json", {"approvalMode": "auto-review", "sandbox": "enabled"})
        code, lines = self.cursor_lines()
        self.assertRegex(lines[0], r"lacks sandbox.mode enabled")
        self.assertNotIn("approvalMode auto-review", lines[0])

        self.write(".cursor/cli-config.json", {
            "approvalMode": "auto-review", "model": {"modelId": "example"},
            "sandbox": {"mode": "enabled", "networkAccess": "user_config_with_defaults"}})
        code, lines = self.cursor_lines()
        self.assertRegex(lines[0], r"cursor +ok +Cursor: .*approvalMode auto-review and sandbox.mode enabled")

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
| `workstation-repo` | {repo} | this person's own repo for their personal agent setup | Keep personal lines in the shared file. |
| `path-to-workstation-repo` | {clone} | where that repo is cloned | Keep personal lines in the shared file. |

<!-- set-up-machine:rules start. Generated by set-up-machine from its rule table and the workstation repo's rows: change those, not these lines. -->
## Global rules

- **Denied:** a rule line.
<!-- set-up-machine:rules end -->

## Personal workflow

Rules for how this person works that pass the team test. Anything a project or a skill needs goes there instead.

{workflow}
"""

WORKFLOW = "- First workflow line.\n- Second workflow line,\n  carried on."
AGREEMENT = "- Ask before merging.\n- Report in short lines."
GLOSSARY = "- **Effort**: one piece of work, from spec to merged pull request.\n- **Session**: one agent at work."
TOOL_GLOSSARIES = ("### Host-a glossary\n\n- **Session**: a tab in host-a.\n\n"
                   "### Agent-a glossary\n\n- **Session**: one agent-a conversation.")
RULES_START = "<!-- set-up-machine:rules start"


class PersonalHome:
    """A home folder copy with a pointer, the workstation repo it names, and the shared file."""

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
        lines = ["# Workstation repo", "", f"- Repository: {repository}"]
        if clone is not None:
            lines.append(f"- Clone: {clone}")
        self.write(".config/agents/source.md", "\n".join(lines) + "\n")

    def personal_repository(self, instructions=INSTRUCTIONS):
        self.write("code/personal/agents/instructions.md", instructions)

    def shared(self, host="`host-a`", worktree="`none`", workflow=WORKFLOW,
               repo="`owner-a/personal`", clone="`~/code/personal`"):
        self.write(".config/agents/AGENTS.md", SHARED.format(host=host, worktree=worktree, workflow=workflow,
                                                             repo=repo, clone=clone))

    def lines(self):
        code, out = run("--home", str(self.home), "--rules", str(TABLE), "--no-codex")
        return code, [l for l in out.splitlines() if l.startswith("personal")]


class PersonalTest(PersonalHome, unittest.TestCase):
    """The pointer, the workstation repo it names, and the shared file generated from it."""

    def test_a_missing_pointer_is_reported(self):
        code, lines = self.lines()
        self.assertRegex(lines[0], r"personal +FAIL +no pointer at .*/\.config/agents/source\.md")
        self.assertEqual(code, 1)

    def test_a_pointer_that_says_none_passes(self):
        self.pointer(repository="none", clone=None)
        code, lines = self.lines()
        self.assertRegex(lines[0], r"personal +none +no workstation repo")
        self.assertEqual(code, 0)

    def test_a_pointer_without_a_repository_line_fails(self):
        self.write(".config/agents/source.md", "# Workstation repo\n\nsomething else\n")
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
        self.assertRegex(lines[0], r"personal +ok +owner-a/personal at .*code/personal: 4 environment defaults, "
                                   r"the personal workflow")
        self.assertEqual(code, 0)

    def test_an_absolute_clone_path_is_read_as_it_is(self):
        self.pointer(clone=f"`{self.home / 'code' / 'personal'}`")
        self.personal_repository()
        self.shared(clone=f"`{self.home / 'code' / 'personal'}`")
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

    def test_the_workstation_repo_roles_come_from_the_pointer(self):
        self.pointer()
        self.personal_repository()
        self.shared(repo="`owner-a/other`", clone="`~/code/other`")
        code, lines = self.lines()
        self.assertTrue(any("`workstation-repo` is `owner-a/other` in" in l and "`owner-a/personal` in" in l
                            for l in lines), lines)
        self.assertTrue(any("`path-to-workstation-repo` is `~/code/other` in" in l for l in lines), lines)
        self.assertEqual(code, 1)

    def test_a_shared_file_without_the_workstation_repo_roles_fails(self):
        self.pointer()
        self.personal_repository()
        self.shared()
        shared = self.home / ".config/agents/AGENTS.md"
        shared.write_text("\n".join(l for l in shared.read_text().split("\n") if "workstation-repo` |" not in l))
        code, lines = self.lines()
        self.assertTrue(any("`workstation-repo` has no row in" in l for l in lines), lines)
        self.assertTrue(any("`path-to-workstation-repo` has no row in" in l for l in lines), lines)
        self.assertEqual(code, 1)

    def test_a_workstation_repo_role_the_repository_sets_otherwise_fails(self):
        self.pointer()
        self.personal_repository(INSTRUCTIONS.replace("| `agent` |", "| `workstation-repo` | `owner-a/old` | |\n| `agent` |"))
        self.shared()
        code, lines = self.lines()
        self.assertTrue(any("`workstation-repo` is `owner-a/old` in" in l and "the pointer gives `owner-a/personal`" in l
                            for l in lines), lines)
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

    def with_sections(self, text, agreement=AGREEMENT, glossary=GLOSSARY, tools=TOOL_GLOSSARIES):
        """Text with a working agreement and a glossary before Environment defaults, and tool glossaries at its end."""
        head, rest = text.split("## Environment defaults", 1)
        marker = RULES_START if RULES_START in rest else "## Personal workflow"
        defaults, tail = rest.split(marker, 1)
        before = "".join(f"## {name}\n\n{body}\n\n" for name, body in (("Working agreement", agreement),
                                                                         ("Glossary", glossary)) if body)
        after = f"{tools}\n\n" if tools else ""
        return f"{head}{before}## Environment defaults{defaults.rstrip()}\n\n{after}{marker}{tail}"

    def test_the_working_agreement_glossary_and_tool_glossaries_pass_when_copied(self):
        self.pointer()
        self.personal_repository(self.with_sections(INSTRUCTIONS))
        self.shared()
        shared = self.home / ".config/agents/AGENTS.md"
        shared.write_text(self.with_sections(shared.read_text()))
        code, lines = self.lines()
        self.assertEqual(len(lines), 1, lines)
        self.assertRegex(lines[0], r"personal +ok +.*4 environment defaults, the working agreement, the glossary, "
                                   r"2 tool glossaries, the personal workflow")
        self.assertEqual(code, 0)

    def test_a_glossary_that_differs_fails(self):
        self.pointer()
        self.personal_repository(self.with_sections(INSTRUCTIONS))
        self.shared()
        shared = self.home / ".config/agents/AGENTS.md"
        shared.write_text(self.with_sections(shared.read_text(), glossary="- **Effort**: a word changed by hand."))
        code, lines = self.lines()
        self.assertEqual(len(lines), 1, lines)
        self.assertRegex(lines[0], r"personal +FAIL +`## Glossary` in .* differs from")
        self.assertEqual(code, 1)

    def test_a_working_agreement_missing_from_the_shared_file_fails(self):
        self.pointer()
        self.personal_repository(self.with_sections(INSTRUCTIONS))
        self.shared()
        shared = self.home / ".config/agents/AGENTS.md"
        shared.write_text(self.with_sections(shared.read_text(), agreement=None))
        code, lines = self.lines()
        self.assertRegex(lines[0], r"personal +FAIL +.*AGENTS\.md lacks `## Working agreement` from")
        self.assertEqual(code, 1)

    def test_a_section_the_personal_repository_lacks_fails(self):
        self.pointer()
        self.personal_repository()
        self.shared()
        shared = self.home / ".config/agents/AGENTS.md"
        shared.write_text(self.with_sections(shared.read_text(), agreement=None, glossary=None))
        code, lines = self.lines()
        self.assertRegex(lines[0], r"personal +FAIL +.*AGENTS\.md has the `### <tool-name> glossary` subsections, "
                                   r"which .*instructions\.md doesn't")
        self.assertEqual(code, 1)

    def test_a_tool_glossary_that_differs_fails(self):
        self.pointer()
        self.personal_repository(self.with_sections(INSTRUCTIONS))
        self.shared()
        shared = self.home / ".config/agents/AGENTS.md"
        shared.write_text(self.with_sections(shared.read_text(), tools="### Host-a glossary\n\n- **Session**: a pane."))
        code, lines = self.lines()
        self.assertRegex(lines[0], r"personal +FAIL +the `### <tool-name> glossary` subsections in .* differs from")
        self.assertEqual(code, 1)

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
    """The workstation repo's permissions file: its rows through the hook, and their entries in Claude Code."""

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
        self.assertRegex(out, r"rules +ok +38 rows and 1 personal permissions")
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
        self.assertRegex(out, r"rules +FAIL +38 rows and 2 personal permissions, \d+ samples, 1 wrong")

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


CURSOR_SOURCE = """# Cursor instructions

Notes for me, not copied.

## Instructions

- Rule one for Cursor.
- Rule two.

## Why

More notes.
"""
CURSOR_RULE = """---
alwaysApply: true
---
<!-- Generated by set-up-machine from the workstation repo's agents/harnesses/cursor.md. Edit that file and run `/set-up-machine`; changes here are overwritten. -->

- Rule one for Cursor.
- Rule two.
"""


class HarnessInstructionsTest(PersonalHome, unittest.TestCase):
    """Instructions for one harness, from the workstation repo's agents/harnesses/<harness>.md."""

    def setUp(self):
        super().setUp()
        self.pointer()
        self.personal_repository()
        self.shared()
        (self.home / ".cursor").mkdir()

    def harness_lines(self):
        code, out = run("--home", str(self.home), "--rules", str(TABLE), "--no-codex")
        return code, [l for l in out.splitlines() if l.startswith("harness ")]

    def test_no_source_and_no_generated_file_says_nothing(self):
        self.assertEqual(self.harness_lines()[1], [])

    def test_the_generated_cursor_rule_passes(self):
        self.write("code/personal/agents/harnesses/cursor.md", CURSOR_SOURCE)
        self.write(".cursor/rules/harness-instructions.mdc", CURSOR_RULE)
        code, lines = self.harness_lines()
        self.assertEqual(len(lines), 1, lines)
        self.assertRegex(lines[0], r"harness +ok +Cursor: .*harness-instructions\.mdc matches .*agents/harnesses/cursor\.md")

    def test_the_text_cursor_should_get_is_the_instructions_section_only(self):
        self.assertEqual(verify.personal.harness_rule("cursor", CURSOR_SOURCE), CURSOR_RULE)

    def test_a_missing_or_different_rule_fails(self):
        self.write("code/personal/agents/harnesses/cursor.md", CURSOR_SOURCE)
        code, lines = self.harness_lines()
        self.assertRegex(lines[0], r"harness +FAIL +Cursor: .*harness-instructions\.mdc doesn't exist")
        self.assertEqual(code, 1)
        self.write(".cursor/rules/harness-instructions.mdc", CURSOR_RULE.replace("Rule two", "Rule 2"))
        code, lines = self.harness_lines()
        self.assertRegex(lines[0], r"harness +FAIL +Cursor: .*harness-instructions\.mdc differs from")

    def test_a_source_without_an_instructions_section_fails(self):
        self.write("code/personal/agents/harnesses/cursor.md", "# Cursor instructions\n\nNotes only.\n")
        code, lines = self.harness_lines()
        self.assertRegex(lines[0], r"harness +FAIL +.*cursor\.md has no `## Instructions` section")

    def test_a_generated_rule_left_after_its_source_went_fails(self):
        self.write(".cursor/rules/harness-instructions.mdc", CURSOR_RULE)
        code, lines = self.harness_lines()
        self.assertRegex(lines[0], r"harness +FAIL +Cursor: .*harness-instructions\.mdc was generated, "
                                   r"but .*cursor\.md doesn't exist")

    def test_a_rule_someone_else_wrote_is_left_alone(self):
        self.write(".cursor/rules/harness-instructions.mdc", "---\nalwaysApply: true\n---\nMine.\n")
        code, lines = self.harness_lines()
        self.assertRegex(lines[0], r"harness +gap +Cursor: .*harness-instructions\.mdc wasn't written by set-up-machine")

    def test_cursor_not_set_up_is_not_applicable(self):
        (self.home / ".cursor").rmdir()
        self.write("code/personal/agents/harnesses/cursor.md", CURSOR_SOURCE)
        code, lines = self.harness_lines()
        self.assertRegex(lines[0], r"harness +n/a +Cursor: not set up here")
        self.assertEqual(code, 0)

    def test_a_harness_without_delivery_yet_is_a_gap(self):
        self.write("code/personal/agents/harnesses/codex.md", "# Codex\n\n## Instructions\n\n- x\n")
        code, lines = self.harness_lines()
        self.assertRegex(lines[0], r"harness +gap +codex: .*codex\.md has instructions, but set-up-machine "
                                   r"can't deliver them to codex yet")

    def test_no_workstation_repo_says_nothing(self):
        self.pointer(repository="none", clone=None)
        self.write(".cursor/rules/harness-instructions.mdc", CURSOR_RULE)
        self.assertEqual(self.harness_lines()[1], [])


if __name__ == "__main__":
    unittest.main()


class PiTest(unittest.TestCase):
    """Pi's instructions link, its declared defaults from agents/pi.json, and its extension."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name).resolve()
        self.agent = self.home / ".pi" / "agent"
        self.shared = self.home / ".config" / "agents" / "AGENTS.md"
        self.shared.parent.mkdir(parents=True)
        self.shared.write_text("# Global agent instructions\n")
        self.agent.mkdir(parents=True)
        self.extension()

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel, text):
        path = self.home / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text if isinstance(text, str) else json.dumps(text))
        return path

    def extension(self, command=None):
        """The extension set-up-machine writes, running the hook script."""
        template = (SCRIPTS.parent / "references" / "pi-extension.ts").read_text()
        command = command or ["python3", str(HOOK), "--harness", "pi"]
        return self.write(".pi/agent/extensions/set-up-machine.ts", template.replace("__HOOK_COMMAND__", json.dumps(command)))

    def link(self, target="../../.config/agents/AGENTS.md"):
        (self.agent / "AGENTS.md").symlink_to(target)

    def workstation(self, declared=None):
        self.write(".config/agents/source.md", "- Repository: `owner-a/personal`\n- Clone: `~/code/personal`\n")
        if declared is not None:
            self.write("code/personal/agents/pi.json", declared)

    def lines(self, *extra):
        code, out = run("--home", str(self.home), "--rules", str(TABLE), "--no-codex", *extra)
        return code, [l for l in out.splitlines() if l.startswith("pi ")]

    def test_no_agent_folder_is_not_set_up(self):
        import shutil
        shutil.rmtree(self.agent)
        no_personal_repository(self.home)
        code, lines = self.lines()
        self.assertEqual(len(lines), 1)
        self.assertRegex(lines[0], r"pi +none +Pi: not set up here")
        self.assertEqual(code, 0)

    def test_the_link_to_the_shared_file_passes(self):
        no_personal_repository(self.home)
        self.link()
        code, lines = self.lines()
        self.assertRegex(lines[0], r"pi +ok +Pi: .*AGENTS\.md -> .*\.config/agents/AGENTS\.md")
        self.assertEqual(code, 0)

    def test_a_missing_or_broken_link_fails(self):
        no_personal_repository(self.home)
        code, lines = self.lines()
        self.assertRegex(lines[0], r"pi +FAIL +Pi: no .*AGENTS\.md; link it to the shared file: \.\./\.\./\.config/agents/AGENTS\.md")
        self.assertEqual(code, 1)
        self.link("../../nowhere/AGENTS.md")
        code, lines = self.lines()
        self.assertRegex(lines[0], r"pi +FAIL +Pi: .*AGENTS\.md is a broken link")
        self.assertEqual(code, 1)

    def test_a_file_set_up_machine_did_not_write_is_a_gap(self):
        no_personal_repository(self.home)
        self.write(".pi/agent/AGENTS.md", "# my own\n")
        code, lines = self.lines()
        self.assertRegex(lines[0], r"pi +gap +Pi: .*AGENTS\.md isn't a link to the shared file")
        self.assertEqual(code, 0)

    def test_an_override_file_is_a_gap_beside_the_link(self):
        no_personal_repository(self.home)
        self.link()
        self.write(".pi/agent/AGENTS.override.md", "# override\n")
        code, lines = self.lines()
        self.assertTrue(any(re.search(r"pi +gap +Pi: .*AGENTS\.override\.md .*instead of the shared file", l) for l in lines), lines)
        self.assertTrue(any(re.search(r"pi +ok ", l) for l in lines), lines)
        self.assertEqual(code, 0)

    def test_the_link_for_an_agent_folder_elsewhere_is_computed_from_it(self):
        no_personal_repository(self.home)
        folder = self.home / "elsewhere" / "pi"
        folder.mkdir(parents=True)
        code, lines = self.lines("--pi-agent-dir", str(folder))
        self.assertRegex(lines[0], r"link it to the shared file: \.\./\.\./\.config/agents/AGENTS\.md")
        (folder / "AGENTS.md").symlink_to("../../.config/agents/AGENTS.md")
        code, lines = self.lines("--pi-agent-dir", str(folder))
        self.assertRegex(lines[0], r"pi +ok ")

    def test_declared_defaults_match_settings_and_other_keys_are_ignored(self):
        self.link()
        self.workstation({"defaultThinkingLevel": "high", "enableInstallTelemetry": False})
        self.write(".pi/agent/settings.json", {"defaultThinkingLevel": "high", "enableInstallTelemetry": False,
                                               "deviceId": "runtime-state", "lastChangelogVersion": "1.1.0"})
        _, lines = self.lines()
        same = [l for l in lines if re.match(r"pi +same ", l)]
        self.assertEqual(len(same), 2, lines)
        self.assertFalse(any("deviceId" in l or "runtime-state" in l for l in lines))

    def test_a_declared_default_that_differs_fails_without_printing_values(self):
        self.link()
        self.workstation({"defaultModel": "model-a"})
        self.write(".pi/agent/settings.json", {"defaultModel": "model-b"})
        code, lines = self.lines()
        self.assertTrue(any(re.match(r"pi +FAIL +Pi: defaultModel in .*settings\.json is missing or differs", l) for l in lines), lines)
        self.assertFalse(any("model-a" in l or "model-b" in l for l in lines))
        self.assertEqual(code, 1)

    def test_packages_declared_in_pi_json_are_a_gap_for_the_plugins_list(self):
        self.link()
        self.workstation({"defaultModel": "model-a", "packages": ["npm:pi-web-access@0.38.0"]})
        self.write(".pi/agent/settings.json", {"defaultModel": "model-a", "packages": []})
        code, lines = self.lines()
        self.assertTrue(any(re.match(r"pi +gap +Pi: agents/pi\.json declares packages; move each one into `plugins` "
                                     r"in agents/installs\.json", l) for l in lines), lines)
        self.assertFalse(any("packages" in l and re.match(r"pi +(FAIL|same) ", l) for l in lines), lines)

    def test_settings_read_through_a_symlink(self):
        self.link()
        self.workstation({"defaultModel": "model-a"})
        target = self.write("dotfiles/pi-settings.json", {"defaultModel": "model-a"})
        (self.agent / "settings.json").symlink_to(target)
        _, lines = self.lines()
        self.assertTrue(any(re.match(r"pi +same +Pi: defaultModel", l) for l in lines), lines)

    def test_no_declared_defaults_says_none(self):
        self.link()
        self.workstation()
        _, lines = self.lines()  # the personal check fails here: the fixture has no agents/instructions.md
        self.assertTrue(any(re.match(r"pi +none +Pi: no declared defaults", l) for l in lines), lines)
        self.assertFalse(any(re.match(r"pi +FAIL ", l) for l in lines), lines)

    def test_a_declared_file_that_is_not_an_object_or_settings_that_are_not_json_fail(self):
        self.link()
        self.workstation(["defaultModel"])
        code, lines = self.lines()
        self.assertTrue(any(re.match(r"pi +FAIL +.*agents/pi\.json", l) for l in lines), lines)
        self.assertEqual(code, 1)
        self.write("code/personal/agents/pi.json", {"defaultModel": "model-a"})
        self.write(".pi/agent/settings.json", "{not json")
        code, lines = self.lines()
        self.assertTrue(any(re.match(r"pi +FAIL +Pi: .*settings\.json isn't valid JSON", l) for l in lines), lines)
        self.assertEqual(code, 1)

    def test_a_broken_skill_link_is_extra(self):
        no_personal_repository(self.home)
        self.link()
        (self.agent / "skills").mkdir()
        (self.agent / "skills" / "gone").symlink_to("../../../.agents/skills/gone")
        (self.home / ".agents" / "skills" / "kept").mkdir(parents=True)
        (self.agent / "skills" / "kept").symlink_to("../../../.agents/skills/kept")
        code, lines = self.lines()
        extra = [l for l in lines if re.match(r"pi +extra ", l)]
        self.assertEqual(len(extra), 1, lines)
        self.assertIn("gone is a broken link", extra[0])
        self.assertEqual(code, 0)

    def hook_line(self):
        code, out = run("--home", str(self.home), "--rules", str(TABLE), "--no-codex")
        return code, [l for l in out.splitlines() if l.startswith("hook") and "Pi" in l][0]

    def test_the_extension_wires_the_hook(self):
        no_personal_repository(self.home)
        self.link()
        code, line = self.hook_line()
        self.assertRegex(line, r"hook +wired +Pi: .*extensions/set-up-machine\.ts -> .*pre_tool_hook\.py")
        self.assertEqual(code, 0, line)

    def test_a_missing_extension_or_script_fails(self):
        no_personal_repository(self.home)
        self.link()
        (self.agent / "extensions" / "set-up-machine.ts").unlink()
        code, line = self.hook_line()
        self.assertRegex(line, r"hook +FAIL +Pi: no extension at ")
        self.assertEqual(code, 1)
        self.extension(["python3", "/gone/pre_tool_hook.py", "--harness", "pi"])
        code, line = self.hook_line()
        self.assertRegex(line, r"hook +FAIL +Pi: .*doesn't exist")
        self.extension(["python3", str(HOOK), "--harness", "opencode"])
        code, line = self.hook_line()
        self.assertRegex(line, r"hook +FAIL +Pi: .*doesn't run the pre-tool hook with --harness pi")

    def test_someone_elses_extension_is_a_gap_left_alone(self):
        no_personal_repository(self.home)
        self.link()
        self.write(".pi/agent/extensions/set-up-machine.ts", "export default function (pi) {}\n")
        code, line = self.hook_line()
        self.assertRegex(line, r"hook +gap +Pi: .*wasn't written by set-up-machine")
        self.assertEqual(code, 0, line)

    def test_actual_home_honors_the_agent_dir_variable_without_printing_it(self):
        from unittest.mock import patch
        no_personal_repository(self.home)
        folder = self.home / "custom-pi"
        folder.mkdir()
        (folder / "AGENTS.md").symlink_to(os.path.relpath(self.shared, folder))
        out = io.StringIO()
        with patch.object(Path, "home", return_value=self.home), patch.dict(os.environ, {"PI_CODING_AGENT_DIR": str(folder)}):
            verify.main(["--home", str(self.home), "--rules", str(TABLE), "--no-codex"], out)
        lines = [l for l in out.getvalue().splitlines() if l.startswith("pi")]
        self.assertRegex(lines[0], r"pi +ok ")
        self.assertIn("<Pi agent dir>", out.getvalue())
        self.assertNotIn(str(folder), out.getvalue())

    def test_a_fixture_home_ignores_the_agent_dir_variable(self):
        from unittest.mock import patch
        no_personal_repository(self.home)
        self.link()
        with patch.dict(os.environ, {"PI_CODING_AGENT_DIR": str(self.home / "ambient")}):
            _, lines = self.lines()
        self.assertRegex(lines[0], r"pi +ok ")
