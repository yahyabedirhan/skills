"""Tests for the pre-tool hook, fed sample tool calls against the shipped rule table.

python3 -m unittest discover -s skills/set-up-machine/scripts/tests
"""
import io
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from setupmachine import hook, rules  # noqa: E402

TABLE = rules.load()
HOME = Path("/Users/someone")
CWD = "/Users/someone/project"


def verdict(command=None, tool="Bash", files=()):
    return hook.decide(hook.ToolCall(tool=tool, command=command, files=tuple(files), cwd=CWD), TABLE, HOME)


def denied_by(command):
    return sorted({h.rule.id for h in verdict(command).denials})


def reported_by(command):
    return sorted({h.rule.id for h in verdict(command).reports})


class CommandDenyTest(unittest.TestCase):
    def assertDenied(self, command, rule="rm-recursive-force"):
        self.assertIn(rule, denied_by(command), command)

    def assertNotDenied(self, command):
        self.assertEqual(denied_by(command), [], command)

    def test_the_tickets_samples_are_denied(self):
        for command in ("rm -fr x", "rm -Rf x", "/bin/rm -rf x", 'bash -c "rm -rf x"'):
            self.assertDenied(command)

    def test_flag_order_grouping_and_extra_flags(self):
        for command in ("rm -rf x", "rm -r -f x", "rm -f -r x", "rm --recursive --force x", "rm --force -R x",
                        "rm -rfv x", "rm -vfr x", "rm -r -v -f x", "rm x -rf", "rm -r x -f", "rm -ri x -f"):
            self.assertDenied(command)

    def test_program_paths_and_escapes(self):
        for command in ("/usr/bin/rm -rf x", "/usr/local/bin/rm -rf x", "\\rm -rf x", "'rm' -rf x", "./rm -rf x"):
            self.assertDenied(command)

    def test_shell_strings(self):
        for command in ('sh -c "rm -rf x"', "zsh -c 'rm -rf x'", 'bash -lc "rm -rf x"', '/bin/bash -c "rm -rf x"',
                        'bash -o pipefail -c "cd y && rm -rf x"', 'eval "rm -rf x"', 'bash -c "bash -c \\"rm -rf x\\""'):
            self.assertDenied(command)
            if not command.startswith("eval"):
                self.assertIn("shell-inline-command", denied_by(command), command)

    def test_compound_commands(self):
        for command in ("git add . && rm -rf x", "ls; rm -rf x", "ls | rm -rf x", "false || rm -rf x",
                        "sleep 1 & rm -rf x", "ls\nrm -rf x", "(cd y; rm -rf x)", "{ rm -rf x; }",
                        "if true; then rm -rf x; fi", "for d in a b; do rm -rf $d; done",
                        "echo $(rm -rf x)", 'echo "$(rm -rf x)"', "echo `rm -rf x`", "ls \\\n && rm -rf x"):
            self.assertDenied(command)

    def test_wrappers_and_assignments(self):
        for command in ("timeout 5 rm -rf x", "timeout -s KILL 5 rm -rf x", "nice -n 5 rm -rf x", "nohup rm -rf x",
                        "env FOO=1 rm -rf x", "FOO=1 rm -rf x", "/usr/bin/env rm -rf x", "command rm -rf x",
                        "exec rm -rf x", "time rm -rf x", "find . -name y | xargs rm -rf", "xargs -n 1 rm -rf < list",
                        "find . -type d -exec rm -rf {} +", "find . -exec rm -rf {} \\;", "sudo rm -rf x",
                        "sudo -u me rm -rf x", "env -S 'rm -rf x'", "RM -rf x", "/BIN/RM -rf x"):
            self.assertDenied(command)

    def test_input_fed_to_a_shell(self):
        for command in ("bash <<EOF\nrm -rf x\nEOF", "cat <<'EOF' | sh\nrm -rf x\nEOF",
                        'echo "rm -rf x" | sh', 'bash <<< "rm -rf x"'):
            self.assertDenied(command)

    def test_the_rest_of_the_deny_rows(self):
        cases = {
            "rm --no-preserve-root -r /": "rm-no-preserve-root",
            "dd if=/dev/zero of=/dev/disk2": "disk-write",
            "mkfs.ext4 /dev/sdb1": "disk-write",
            "/sbin/mkfs -t ext4 /dev/sdb1": "disk-write",
            "chmod -R 777 .": "chmod-recursive-777",
            "chmod 777 -R .": "chmod-recursive-777",
            "sudo ls": "privilege-escalation",
            "/usr/bin/sudo ls": "privilege-escalation",
            "su root": "privilege-escalation",
            "bash -c ls": "shell-inline-command",
            "git push --force": "git-push-force",
            "git push -f origin main": "git-push-force",
            "git push origin main --force": "git-push-force",
            "git -C ../repo push --force": "git-push-force",
            "git push --force-with-lease --force": "git-push-force",
            "git reset --hard": "git-reset-hard",
            "git reset HEAD~1 --hard": "git-reset-hard",
            "gh repo delete me/x --yes": "gh-repo-destructive",
            "gh repo archive me/x": "gh-repo-destructive",
            "gh ssh-key add k.pub": "gh-access-keys",
            "gh repo deploy-key add k.pub": "gh-access-keys",
            "spark event create": "calendar-mail-cli-send",
        }
        for command, rule in cases.items():
            self.assertDenied(command, rule)

    def test_normal_work_goes_through(self):
        for command in ("rm -r x", "rm -f x", "rm x", "rmdir x", "grep -rf patterns .", "git push",
                        "git push -u origin feat", "git push --force-with-lease", "git push --follow-tags",
                        "git reset --soft HEAD~1", "git stash push -u -m tag", "gh repo view", "gh repo edit --description d",
                        "gh pr create --title 'rm -rf is denied'", "echo 'rm -rf x'", "grep -r 'rm -rf' .",
                        "chmod -R 755 .", "docker rm -f c", "git clean -fd", "git rm -rf --cached x", "cp -rf a b",
                        "sh ./install.sh --force", "npm run build -- --force", "chmod 777 file", "ddgr x", "ls -la", "mv x .scratch/", "bash script.sh -c",
                        "command -v sudo", "spark events", "find . -name '*.pyc'", "ls 2>&1 | grep -rf x",
                        "cat <<'EOF' > notes.md\nrm -rf x\nEOF",
                        "git commit -m \"$(cat <<'EOF'\nfeat: deny\n\nrm -rf x is refused now\nEOF\n)\""):
            self.assertNotDenied(command)

    def test_an_unclosed_quote_is_still_read(self):
        self.assertDenied('ls && rm -rf "x')


class ReportTest(unittest.TestCase):
    def test_gh_api_secret_and_variable_are_reported(self):
        for command in ("gh api repos/me/x", "gh secret set TOKEN", "gh variable list", "cd x && gh api user",
                        "/opt/homebrew/bin/gh api user"):
            self.assertEqual(reported_by(command), ["gh-api-secrets"], command)
            self.assertEqual(denied_by(command), [], command)

    def test_a_deny_in_the_same_call_wins_and_nothing_is_reported(self):
        v = verdict("gh api user && rm -rf x")
        self.assertEqual([h.rule.id for h in v.denials], ["rm-recursive-force"])
        self.assertEqual(v.reports, [])

    def test_ask_rows_are_left_to_the_harness(self):
        v = verdict("git push --force-with-lease")
        self.assertEqual((v.denials, v.reports), ([], []))


class FileAndMcpTest(unittest.TestCase):
    def ids(self, tool, path, access):
        return sorted({h.rule.id for h in verdict(tool=tool, files=[(path, access)]).denials})

    def test_secret_files(self):
        self.assertEqual(self.ids("Read", ".env", "read"), ["secret-files-read"])
        self.assertEqual(self.ids("Read", "/Users/someone/project/sub/.env.local", "read"), ["secret-files-read"])
        self.assertEqual(self.ids("Grep", "secrets", "read"), ["secret-files-read"])
        self.assertEqual(self.ids("Edit", "secrets/key", "write"), ["secret-files-read", "secret-files-write"])
        self.assertEqual(self.ids("Read", "~/.ssh/id_ed25519", "read"), ["home-credentials-read"])
        self.assertEqual(self.ids("Write", "/Users/someone/.aws/credentials", "write"), ["home-credentials-read"])

    def test_ordinary_files(self):
        for path in (".envrc", "README.md", "src/environment.py", "/Users/someone/.sshx/y", "my-secrets.txt"):
            self.assertEqual(self.ids("Read", path, "read"), [], path)

    def test_mail_tools_by_meaning(self):
        for tool in ("mcp__claude_ai_Gmail__send_message", "mcp__gmail__trash_thread",
                     "mcp__claude_ai_Gmail__apply_sensitive_message_label"):
            self.assertTrue(verdict(tool=tool).denials, tool)
        for tool in ("mcp__claude_ai_Gmail__create_draft", "mcp__slack__send_message", "Read"):
            self.assertFalse(verdict(tool=tool).denials, tool)


class ClaudeCodeHookTest(unittest.TestCase):
    """The script as Claude Code runs it: PreToolUse JSON in, a decision out."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name).resolve()
        self.config = self.dir / "hook.json"
        self.config.write_text(json.dumps({"report_dir": str(self.dir / "reports")}))

    def tearDown(self):
        self._tmp.cleanup()

    def run_hook(self, payload, *extra):
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "pre_tool_hook.py"), "--config", str(self.config), *extra],
            input=payload if isinstance(payload, str) else json.dumps(payload),
            capture_output=True, text=True, timeout=30,
        )
        return proc

    def bash(self, command):
        return {"session_id": "s1", "cwd": str(self.dir), "hook_event_name": "PreToolUse",
                "tool_name": "Bash", "tool_input": {"command": command}}

    def test_a_denied_command_names_the_part_and_the_instruction(self):
        proc = self.run_hook(self.bash("git add . && rm -fr x"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)["hookSpecificOutput"]
        self.assertEqual(out["permissionDecision"], "deny")
        reason = out["permissionDecisionReason"]
        self.assertIn("`rm -fr x`", reason)
        self.assertIn("rm-recursive-force", reason)
        self.assertIn(".scratch/", reason)
        self.assertNotIn("git add", reason)

    def test_a_reported_command_is_logged_and_let_through(self):
        proc = self.run_hook(self.bash("gh api repos/me/x"))
        self.assertEqual((proc.returncode, proc.stdout), (0, ""), proc.stderr)
        [log] = list((self.dir / "reports").iterdir())
        line = json.loads(log.read_text().splitlines()[0])
        self.assertEqual(line["rules"], ["gh-api-secrets"])
        self.assertEqual(line["command"], "gh api repos/me/x")
        self.assertEqual(line["session"], "s1")
        self.assertEqual(log.stat().st_mode & 0o777, 0o600)

    def test_an_ordinary_call_says_nothing_and_logs_nothing(self):
        proc = self.run_hook(self.bash("ls -la"))
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))
        self.assertFalse((self.dir / "reports").exists())

    def test_other_payload_shapes_never_crash(self):
        cursor_shell = {"hook_event_name": "beforeShellExecution", "command": "rm -rf x", "cwd": "/tmp"}
        proc = self.run_hook(cursor_shell)
        self.assertEqual(json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")
        for payload in ({"tool_name": "Shell", "tool_input": {"command": "ls"}}, {}, [], "not json", "",
                        {"tool_name": 3, "tool_input": "x"}, {"tool_input": {"command": None}}):
            proc = self.run_hook(payload)
            self.assertIn(proc.returncode, (0, 1), payload)
            self.assertEqual(proc.stdout, "", payload)
            self.assertNotIn("Traceback", proc.stderr, payload)

    def test_the_report_folder_comes_from_the_configuration(self):
        self.assertEqual(hook.report_dir({"report_dir": "logs"}, self.config), self.dir / "logs")
        self.assertEqual(hook.report_dir({"report_dir": "~/r"}, self.config), Path("~/r").expanduser())
        self.assertEqual(hook.report_dir({}, self.config).parts[-2:], ("agents", "reports"))

    def test_main_in_process(self):
        out = io.StringIO()
        code = hook.main(["--config", str(self.config)], io.StringIO(json.dumps(self.bash("gh secret list"))), out,
                         now=datetime(2026, 9, 29, tzinfo=timezone.utc))
        self.assertEqual((code, out.getvalue()), (0, ""))
        self.assertTrue((self.dir / "reports" / "2026-09-29.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
