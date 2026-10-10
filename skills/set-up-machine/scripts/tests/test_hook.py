"""Tests for the pre-tool hook, fed sample tool calls against the shipped rule table.

python3 -m unittest discover -s skills/set-up-machine/scripts/tests
"""
import io
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from setupmachine import commands, hook, personal, rules  # noqa: E402

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
                        "sudo -u me rm -rf x", "env -S 'rm -rf x'"):
            self.assertDenied(command)

    def test_program_case_follows_the_filesystem(self):
        # macOS's default filesystem runs /bin/rm for `RM`; Linux's finds no such program.
        with mock.patch.object(commands, "FOLD_CASE", True):
            for command in ("RM -rf x", "/BIN/RM -rf x", "Sudo ls"):
                self.assertTrue(denied_by(command), command)
        with mock.patch.object(commands, "FOLD_CASE", False):
            for command in ("RM -rf x", "/BIN/RM -rf x", "Sudo ls"):
                self.assertNotDenied(command)
            self.assertDenied("rm -rf x")

    def test_case_is_folded_where_the_filesystem_folds_it(self):
        self.assertEqual(commands.FOLD_CASE, sys.platform in ("darwin", "win32"))

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
        self.assertEqual(self.ids("Read", ".env", "read"), ["env-files-read"])
        self.assertEqual(self.ids("Read", "/Users/someone/project/sub/.env.local", "read"), ["env-files-read"])
        self.assertEqual(self.ids("Write", "sub/.env", "write"), ["env-files-read", "env-files-write"])
        self.assertEqual(self.ids("Grep", "secrets", "read"), ["secret-files-read"])
        self.assertEqual(self.ids("Edit", "secrets/key", "write"), ["secret-files-read", "secret-files-write"])
        self.assertEqual(self.ids("Read", "~/.ssh/id_ed25519", "read"), ["home-credentials-read"])
        self.assertEqual(self.ids("Write", "/Users/someone/.aws/credentials", "write"), ["home-credentials-read"])
        for path in ("~/.netrc", "~/.git-credentials", "~/.config/gh/hosts.yml", "~/.npmrc", "~/.docker/config.json",
                     "/Users/someone/.kube/config"):
            self.assertEqual(self.ids("Read", path, "read"), ["home-credentials-read"], path)
        for path in ("certs/server.pem", "/Users/someone/Downloads/signing.p12", "build/app.pfx"):
            self.assertEqual(self.ids("Read", path, "read"), ["key-files-read"], path)

    def test_ordinary_files(self):
        for path in (".envrc", "README.md", "src/environment.py", "/Users/someone/.sshx/y", "my-secrets.txt",
                     "app/.npmrc", "~/.config/gh/config.yml", "certs/server.pub", "notes/pem.md"):
            self.assertEqual(self.ids("Read", path, "read"), [], path)

    def test_env_example_stays_readable_and_writable(self):
        for path in (".env.example", "sub/.env.example", "/Users/someone/project/app/.env.example"):
            self.assertEqual(self.ids("Read", path, "read"), [], path)
            self.assertEqual(self.ids("Edit", path, "write"), [], path)
        for path in (".env.examples", ".env.e2e", ".env.", "sub/.env.example.local"):
            self.assertEqual(self.ids("Read", path, "read"), ["env-files-read"], path)


class EnvironmentTest(unittest.TestCase):
    """The env-var family: the environment and `.env` files stay out of the agent's context."""

    def test_commands_that_list_the_environment_are_denied(self):
        for command, rule in (
            ("env", "env-dump"), ("/usr/bin/env", "env-dump"), ("env -0", "env-dump"), ("env -u HOME", "env-dump"),
            ("env FOO=1", "env-dump"), ("env | grep TOKEN", "env-dump"), ("command env", "env-dump"),
            ("export", "env-dump"), ("set", "env-dump"), ("set | less", "env-dump"),
            ("printenv", "env-print"), ("printenv TOKEN", "env-print"), ("/usr/bin/printenv HOME", "env-print"),
            ("export -p", "env-dump-declared"), ("declare -p", "env-dump-declared"),
            ("typeset -p TOKEN", "env-dump-declared"), ("declare -px", "env-dump-declared"),
        ):
            self.assertIn(rule, denied_by(command), command)

    def test_the_hook_reads_them_inside_other_commands(self):
        self.assertIn("env-print", denied_by('bash -c "printenv"'))
        self.assertIn("env-dump", denied_by("sh -c 'env'"))
        self.assertIn("env-dump", denied_by("echo $(env)"))
        self.assertIn("env-print", denied_by("true && printenv TOKEN"))

    def test_setting_a_variable_is_fine(self):
        for command in ("env FOO=1 true", "env -u HOME ls", "/usr/bin/env python3 x.py", "FOO=1 make",
                        "export FOO=1", "set -e", "set -euo pipefail", "declare -x FOO=1", "test -n \"$TOKEN\"",
                        "echo $HOME"):
            self.assertEqual(denied_by(command), [], command)

    def test_reading_a_env_file_through_a_command_is_denied(self):
        for command in ("cat .env", "cat sub/.env.local", "less -R .env.production", "head -1 .env",
                        "tail -f app/.env", "grep TOKEN .env", "source .env", ". ./.env", "set -a; . .env",
                        "cat /Users/someone/project/.env"):
            self.assertIn("env-files-commands", denied_by(command), command)

    def test_the_example_and_other_files_stay_readable(self):
        for command in ("cat .env.example", "grep TOKEN sub/.env.example", "source venv/bin/activate",
                        "cat .envrc", "grep -r TOKEN src", "head README.md"):
            self.assertEqual(denied_by(command), [], command)

    def test_printing_a_secret_looking_variable_is_denied(self):
        for command in ("echo $API_TOKEN", "printf '%s' \"${DB_PASSWORD}\"", 'echo "key: $OPENAI_API_KEY"',
                        "echo $github_token", "print -r -- $AWS_SECRET_ACCESS_KEY", "/bin/echo ${SERVICE_CREDENTIALS:-none}",
                        "true && echo $DB_PASSWD", 'bash -c "echo $API_TOKEN"', "echo $(echo $API_KEY)"):
            self.assertIn("env-print-secret", denied_by(command), command)

    def test_ordinary_variables_and_passing_a_secret_along_are_fine(self):
        for command in ("echo $HOME", "echo $PATH $SHELL", "echo TOKEN", "echo '$API_TOKEN'", "echo \\$API_TOKEN",
                        'curl -H "Authorization: Bearer $TOKEN" https://example.com',
                        "test -n \"$API_TOKEN\"", "echo ${#API_TOKEN}"):
            self.assertNotIn("env-print-secret", denied_by(command), command)

    def test_the_refusal_names_the_rules_instruction(self):
        text = hook.refusal(verdict("/usr/bin/env").denials)
        self.assertIn("env-dump", text)
        self.assertIn("give the user the exact command; never work around it", text)

    def test_mail_tools_by_meaning(self):
        for tool in ("mcp__claude_ai_Gmail__send_message", "mcp__gmail__trash_thread",
                     "mcp__claude_ai_Gmail__apply_sensitive_message_label"):
            self.assertTrue(verdict(tool=tool).denials, tool)
        for tool in ("mcp__claude_ai_Gmail__create_draft", "mcp__slack__send_message", "Read"):
            self.assertFalse(verdict(tool=tool).denials, tool)

    def test_calendar_tools_that_do_anything_but_read_are_denied(self):
        for tool in ("mcp__claude_ai_Google_Calendar__create_event", "mcp__claude_ai_Google_Calendar__respond_to_event",
                     "mcp__google_calendar__delete_event", "mcp__calendar__move_event"):
            self.assertEqual([h.rule.id for h in verdict(tool=tool).denials], ["calendar-write"], tool)
        for tool in ("mcp__claude_ai_Google_Calendar__list_events", "mcp__claude_ai_Google_Calendar__get_event",
                     "mcp__claude_ai_Google_Calendar__find_free_time", "mcp__claude_ai_Google_Calendar__authenticate",
                     "mcp__claude_ai_Gmail__list_drafts"):
            self.assertFalse(verdict(tool=tool).denials, tool)


class UserApprovalTest(unittest.TestCase):
    """Ask rows with `approver: user` need the user themselves to approve each call."""

    def decide(self, tool="Bash", command=None, unattended=""):
        return hook.decide(hook.ToolCall(tool=tool, command=command, cwd=CWD, unattended=unattended), TABLE, HOME)

    def test_draft_writes_ask_when_the_harness_will_ask_the_user(self):
        for tool in ("mcp__claude_ai_Gmail__create_draft", "mcp__claude_ai_Gmail__update_draft",
                     "mcp__claude_ai_Gmail__delete_draft"):
            v = self.decide(tool=tool)
            self.assertEqual(([h.rule.id for h in v.asks], v.denials), (["mail-draft-write"], []), tool)
        v = self.decide(command="spark draft create")
        self.assertEqual(([h.rule.id for h in v.asks], v.denials), (["mail-cli-draft"], []))

    def test_draft_writes_are_refused_where_no_one_is_asked(self):
        v = self.decide(tool="mcp__claude_ai_Gmail__create_draft", unattended="bypassPermissions")
        self.assertEqual([h.rule.id for h in v.denials], ["mail-draft-write"])
        self.assertIn("bypassPermissions", v.denials[0].part)
        v = self.decide(command="spark draft create && ls", unattended="auto")
        self.assertEqual([h.rule.id for h in v.denials], ["mail-cli-draft"])

    def test_other_ask_rows_are_still_left_to_the_harness(self):
        v = self.decide(command="git push --force-with-lease", unattended="bypassPermissions")
        self.assertEqual(([h.rule.id for h in v.asks], v.denials), (["git-push-force-with-lease"], []))

    def test_reads_are_untouched(self):
        for tool in ("mcp__claude_ai_Gmail__get_draft", "mcp__claude_ai_Gmail__list_drafts"):
            v = self.decide(tool=tool, unattended="bypassPermissions")
            self.assertEqual((v.asks, v.denials), ([], []), tool)

    def test_claude_codes_permission_mode_says_when_no_one_is_asked(self):
        for mode, unattended in (("default", ""), ("acceptEdits", ""), ("plan", ""), (None, ""),
                                 ("auto", "auto"), ("dontAsk", "dontAsk"), ("bypassPermissions", "bypassPermissions")):
            payload = {"tool_name": "mcp__claude_ai_Gmail__create_draft", "tool_input": {}}
            if mode:
                payload["permission_mode"] = mode
            got = hook.read_claude_code(payload).unattended
            self.assertEqual(bool(got), bool(unattended), mode)
            self.assertIn(unattended, got, mode)

    def test_codex_with_approval_policy_never(self):
        payload = {"tool_name": "mcp__codex_apps__gmail_create_draft", "tool_input": {}}
        self.assertEqual(hook.read_codex(payload).unattended, "")
        self.assertIn("never", hook.read_codex({**payload, "permission_mode": "bypassPermissions"}).unattended)

    def test_cursor_and_opencode_never_promise_the_user_is_asked(self):
        cursor = {"hook_event_name": "beforeMCPExecution", "mcp_server_name": "gmail", "tool_name": "create_draft"}
        call = hook.read_cursor(cursor)
        self.assertTrue(call.unattended)
        self.assertEqual([h.rule.id for h in hook.decide(call, TABLE, HOME).denials], ["mail-draft-write"])
        call = hook.read_opencode({"tool": "gmail_create_draft", "args": {}})
        self.assertTrue(call.unattended)
        self.assertEqual([h.rule.id for h in hook.decide(call, TABLE, HOME).denials], ["mail-draft-write"])
        call = hook.read_opencode({"tool": "bash", "args": {"command": "git push --force-with-lease"}})
        self.assertEqual(hook.decide(call, TABLE, HOME).denials, [])

    def test_cursor_refuses_every_ask_row(self):
        # Cursor has no native ask list, so an ask row the hook leaves alone would run unasked.
        for command, rule in (("git push --force-with-lease", "git-push-force-with-lease"),
                              ("git push --mirror origin", "git-push-mirror"),
                              ("git clean -fd", "git-clean-force"),
                              ("gh repo edit --description d", "gh-repo-edit")):
            call = hook.read_cursor({"hook_event_name": "beforeShellExecution", "command": command, "cwd": CWD})
            v = hook.decide(call, TABLE, HOME)
            self.assertEqual(([h.rule.id for h in v.denials], v.asks), ([rule], []), command)
            self.assertIn("where no one asks the user", v.denials[0].part, command)
        call = hook.read_cursor({"hook_event_name": "beforeShellExecution", "command": "git clean -n", "cwd": CWD})
        self.assertEqual(hook.decide(call, TABLE, HOME).denials, [])

    def test_claude_code_still_asks_for_ask_rows_in_auto_mode(self):
        payload = {"tool_name": "Bash", "tool_input": {"command": "git clean -f"}, "permission_mode": "auto", "cwd": CWD}
        v = hook.decide(hook.read_claude_code(payload), TABLE, HOME)
        self.assertEqual(([h.rule.id for h in v.asks], v.denials), (["git-clean-force"], []))


class ReviewFindingsTest(unittest.TestCase):
    """The final branch review's findings on the hook."""

    def test_bare_and_flag_only_declarations_list_every_variable(self):
        for command in ("declare", "typeset", "declare -x", "typeset -x", "export -x", "declare -r -x",
                        "typeset +x", "sh -c 'declare'"):
            self.assertTrue(set(denied_by(command)) & {"env-dump", "env-dump-listed"}, command)
        for command in ("declare -x FOO=1", "typeset -i n=3", "export FOO", "declare -a arr"):
            self.assertEqual(denied_by(command), [], command)

    def test_redirect_targets_are_checked_against_the_file_rows(self):
        for command, rule in (("cat < .env", "env-files-read"), ("echo x > .env", "env-files-write"),
                              ("tee .env", "env-files-write"), ("echo x >> sub/.env.local", "env-files-write"),
                              ("echo x | tee -a app/.env", "env-files-write"), ("wc -l <sub/.env", "env-files-read"),
                              ("bash -c 'echo x > .env'", "env-files-write"), ("echo x &> secrets/k", "secret-files-write")):
            self.assertIn(rule, denied_by(command), command)
        for command in ("echo x > out.txt", "cat < .env.example", "echo x 2>&1", "ls >&2", "echo x | tee log.txt",
                        "cat <<EOF > notes.md\n.env\nEOF", "grep x <<< .env"):
            self.assertEqual(denied_by(command), [], command)

    def test_chmod_777_in_other_spellings(self):
        for command in ("chmod -R 0777 .", "chmod -R a+rwx .", "chmod --recursive ugo+rwx x", "chmod -R a=rwx ."):
            self.assertIn("chmod-recursive-777", denied_by(command), command)
        for command in ("chmod -R 0755 .", "chmod -R u+rwx .", "chmod a+rwx file"):
            self.assertEqual(denied_by(command), [], command)

    def test_a_grep_path_or_glob_reaching_an_env_file(self):
        def grep(**tool_input):
            payload = {"tool_name": "Grep", "cwd": CWD, "tool_input": {"pattern": "TOKEN", **tool_input}}
            return sorted({h.rule.id for h in hook.decide(hook.read_claude_code(payload), TABLE, HOME).denials})
        for tool_input in ({"path": ".env"}, {"path": "sub", "glob": ".env"}, {"glob": "**/.env.*"},
                           {"glob": "*.env"}, {"path": "app", "glob": ".env*"}):
            self.assertIn("env-files-read", grep(**tool_input), tool_input)
        for tool_input in ({"path": "src"}, {"glob": "*.py"}, {"glob": ".env.example"}, {"glob": "*"}):
            self.assertEqual(grep(**tool_input), [], tool_input)

    def test_opencode_and_cursor_searches_too(self):
        call = hook.read_opencode({"tool": "grep", "args": {"pattern": "T", "path": "app", "include": "*.env"},
                                   "directory": CWD})
        self.assertTrue(hook.decide(call, TABLE, HOME).denials)
        call = hook.read_cursor({"hook_event_name": "preToolUse", "tool_name": "Grep", "cwd": CWD,
                                 "tool_input": {"pattern": "T", "glob": ".env.*"}})
        self.assertTrue(hook.decide(call, TABLE, HOME).denials)

    def test_path_case_is_folded_where_the_filesystem_folds_it(self):
        with mock.patch.object(commands, "FOLD_CASE", True):
            self.assertIn("env-files-read", sorted({h.rule.id for h in verdict(tool="Read", files=[(".ENV", "read")]).denials}))
            self.assertIn("env-files-commands", denied_by("cat sub/.Env.Local"))
            self.assertEqual(denied_by("cat .ENV.EXAMPLE"), [])
        with mock.patch.object(commands, "FOLD_CASE", False):
            self.assertFalse(verdict(tool="Read", files=[(".ENV", "read")]).denials)



def answer(command):
    """The hook's answer for a shell command: deny, ask or allow."""
    return verdict(command).answer


class BypassesAndFalsePositivesTest(unittest.TestCase):
    """Issue #82: bypasses of the hook and quoted text it refused, each with its expected answer."""

    def assertAnswers(self, expected, commands_):
        for command in commands_:
            self.assertEqual(answer(command), expected, command)

    def test_a_heredoc_marker_inside_quotes_a_comment_or_arithmetic_hides_nothing(self):
        self.assertAnswers("deny", ('echo "<<X"\nrm -rf x', "ls # <<X\nrm -rf x", "echo $((a<<b))\nrm -rf x",
                                    "echo '<<X'\nrm -rf x", 'echo "$((a<<b))"\nrm -rf x', "ls # a comment\nrm -rf x"))

    def test_real_heredocs_still_hide_their_body(self):
        self.assertAnswers("allow", ("cat <<EOF > notes.md\nrm -rf x\nEOF", "cat <<-EOF > n.md\n\trm -rf x\n\tEOF",
                                     "cat << 'EOF' > n.md\nrm -rf x\nEOF\necho done"))
        self.assertAnswers("deny", ("cat <<'EOF' > n.md\nnotes\nEOF\nrm -rf x", "sh <<EOF\nrm -rf x\nEOF"))

    def test_an_unquoted_heredoc_body_runs_its_substitutions(self):
        self.assertAnswers("deny", ("cat <<EOF > n.md\n$(rm -rf x)\nEOF",))
        self.assertAnswers("allow", ("cat <<'EOF' > n.md\n$(rm -rf x)\nEOF",))

    def test_the_wrappers_it_missed(self):
        self.assertAnswers("deny", (
            "setsid rm -rf x", "setsid -f rm -rf x", "busybox rm -rf x", "watch rm -rf x", "watch -n 5 rm -rf x",
            "watch 'rm -rf x'", "flock /tmp/lock rm -rf x", "flock -w 5 /tmp/lock rm -rf x",
            "flock /tmp/lock -c 'rm -rf x'", "parallel rm -rf ::: a b", "parallel -j 4 'rm -rf {}' ::: a",
            "script -q /dev/null rm -rf x", "script -c 'rm -rf x' log", "chronic rm -rf x", "unbuffer rm -rf x",
            "arch -arm64 rm -rf x", "arch -arch x86_64 rm -rf x",
        ))
        self.assertAnswers("allow", ("watch -n 5 ls", "flock /tmp/lock make", "parallel echo ::: a b",
                                     "script -q /dev/null ls", "arch", "chronic make", "busybox ls"))

    def test_the_shells_it_missed(self):
        for command in ("fish -c 'rm -rf x'", "dash -c 'ls'", "ksh -c 'ls'", "fish --command 'ls'",
                        "/usr/local/bin/fish -c ls"):
            self.assertIn("shell-inline-command", denied_by(command), command)
        self.assertIn("rm-recursive-force", denied_by("fish -c 'rm -rf x'"))
        self.assertAnswers("allow", ("fish script.fish", "dash ./install.sh"))

    def test_a_pipe_into_a_shell_joins_the_words_before_it(self):
        self.assertAnswers("deny", ("echo rm -rf x | sh", 'echo "rm -rf x" | sh', "echo rm -rf x | bash",
                                    "printf 'rm -rf x' | zsh", "timeout 5 echo rm -rf x | sh",
                                    "echo rm -rf x | fish"))
        self.assertAnswers("allow", ("echo rm -rf x | cat", "echo ls | sh"))

    def test_deleting_the_main_branch_is_denied(self):
        for command in ("git push origin :main", "git push --delete origin main", "git push -d origin main",
                        "git push origin --delete main", "git push upstream +:main", "git push origin :refs/heads/main",
                        "git push origin feature :main", "git push origin :master"):
            self.assertEqual(answer(command), "deny", command)
            self.assertTrue([r for r in denied_by(command) if r.startswith("git-push-delete-main")], command)
        self.assertAnswers("allow", ("git push origin main", "git push origin HEAD:main", "git push --delete origin feat",
                                     "git push origin :feat"))

    def test_mirror_and_clean_ask(self):
        self.assertAnswers("ask", ("git push --mirror", "git push --mirror origin", "git clean -fdx", "git clean -f",
                                   "git clean --force -d"))
        self.assertAnswers("allow", ("git clean -n", "git clean -nd"))

    def test_find_delete_is_denied_wherever_it_hides(self):
        for command in ("find . -delete", "find . -name '*.pyc' -delete", "timeout 5 find . -type f -delete",
                        "/usr/bin/find /tmp/x -delete", 'bash -c "find . -delete"', "cd x && find . -empty -delete",
                        "echo $(find . -delete)"):
            self.assertEqual(answer(command), "deny", command)
            self.assertIn("find-delete", denied_by(command), command)
        self.assertAnswers("allow", ("find . -name '*.pyc'", "find . -type d", "find . -name delete",
                                     "grep -r -- -delete src"))

    def test_the_process_environment_is_denied(self):
        for command in ("cat /proc/self/environ", "cat /proc/1/environ", "strings /proc/self/environ",
                        "tr '\\0' '\\n' < /proc/self/environ", "xxd /proc/42/task/42/environ"):
            self.assertEqual(answer(command), "deny", command)
        call = hook.ToolCall(tool="Read", files=(("/proc/self/environ", "read"),), cwd=CWD)
        self.assertTrue(hook.decide(call, TABLE, HOME).denials)
        self.assertAnswers("allow", ("cat /proc/cpuinfo", "cat environ.md"))

    def test_known_gaps_are_named_in_the_table(self):
        # A shell glob reaching a .env file, and ps printing environments, pass the hook; the table names them.
        self.assertAnswers("allow", ("cat .env*", "cat .e?v", "ps eww"))
        gaps = {r.id: r.gap for r in TABLE}
        self.assertIn(".env*", gaps["env-files-commands"])
        self.assertIn("ps eww", gaps["proc-environ-read"])

    def test_substitutions_in_single_quotes_or_escaped_are_text(self):
        self.assertAnswers("allow", (
            "git commit -m 'never run `rm -rf` here'", "gh pr create --body 'Mentions `sudo ls`'",
            "echo '$(rm -rf x)'", 'echo "\\$(rm -rf x)"', 'echo "\\`rm -rf x\\`"', "echo \\`rm -rf x\\`",
            "echo $'it\\'s `sudo ls`'",
        ))
        self.assertAnswers("deny", ('echo "$(rm -rf x)"', 'echo "`rm -rf x`"', "echo $(rm -rf x)",
                                    "echo `sudo ls`", "echo \"a $(echo 'b' && rm -rf x) c\""))

    def test_ordinary_env_named_files_are_readable(self):
        for command in ("cat .env.sample", "cat .env.template", "cat docs/.env.md", "cat .env.example"):
            self.assertEqual(answer(command), "allow", command)
        for path in (".env.sample", "app/.env.template", "docs/.env.md"):
            self.assertEqual(verdict(tool="Read", files=[(path, "read")]).answer, "allow", path)
        self.assertAnswers("deny", ("cat .env", "cat .env.local", "cat .env.production"))


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
            capture_output=True, text=True, timeout=30, env={**os.environ, "HOME": str(self.dir)},
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

    def test_a_draft_in_bypass_mode_is_refused(self):
        payload = {"session_id": "s1", "cwd": str(self.dir), "hook_event_name": "PreToolUse",
                   "permission_mode": "bypassPermissions", "tool_name": "mcp__claude_ai_Gmail__create_draft",
                   "tool_input": {"to": ["a@example.com"]}}
        out = json.loads(self.run_hook(payload).stdout)["hookSpecificOutput"]
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("mail-draft-write", out["permissionDecisionReason"])
        payload["permission_mode"] = "default"
        self.assertEqual(self.run_hook(payload).stdout, "")

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
        with mock.patch.dict(os.environ, {"HOME": str(self.dir)}):
            code = hook.main(["--config", str(self.config)], io.StringIO(json.dumps(self.bash("gh secret list"))), out,
                             now=datetime(2026, 9, 29, tzinfo=timezone.utc))
        self.assertEqual((code, out.getvalue()), (0, ""))
        self.assertTrue((self.dir / "reports" / "2026-09-29.jsonl").exists())


PERSONAL_ROWS = [
    {"id": "tool-a-wipe", "level": "deny", "summary": "`tool-a wipe`", "match": {"program": "tool-a", "subcommands": [["wipe"]]},
     "reason": "It wipes the tool's store.", "instruction": "Stop, say why, and give the user the exact command.",
     "samples": {"covers": ["tool-a wipe all"], "leaves": ["tool-a list"]}},
    {"id": "server-a-read", "level": "allow", "summary": "server-a's read tools", "match": {"server": "server-a", "tool": "^read_"},
     "reason": "They only read.", "instruction": "Go ahead.",
     "samples": {"covers": ["mcp__server-a__read_item"], "leaves": ["mcp__server-a__write_item"]}},
    {"id": "tool-b-sync", "level": "allow-and-report", "summary": "`tool-b sync`", "match": {"program": "tool-b", "subcommands": [["sync"]]},
     "reason": "It reaches the network.", "instruction": "Go ahead; each call is logged.",
     "samples": {"covers": ["tool-b sync"]}},
]


class PersonalRowsTest(unittest.TestCase):
    """The rows of the workstation repo the pointer names, checked alongside the rule table."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name).resolve()
        pointer = self.home / ".config" / "agents" / "source.md"
        pointer.parent.mkdir(parents=True)
        pointer.write_text("# Workstation repo\n\n- Repository: `owner-a/personal`\n- Clone: `~/code/personal`\n")
        self.permissions = self.home / "code" / "personal" / "setup" / "permissions.json"
        self.permissions.parent.mkdir(parents=True)
        self.write(PERSONAL_ROWS)
        self.config = self.home / "hook.json"
        self.config.write_text(json.dumps({"report_dir": str(self.home / "reports")}))

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rows):
        self.permissions.write_text(json.dumps({"version": 1, "rules": rows}))

    def decide(self, call):
        table = TABLE + personal.permissions(self.home, TABLE)
        return hook.decide(call, table, self.home)

    def run_hook(self, command):
        payload = {"session_id": "s1", "cwd": str(self.home), "tool_name": "Bash", "tool_input": {"command": command}}
        return subprocess.run([sys.executable, str(SCRIPTS / "pre_tool_hook.py"), "--config", str(self.config)],
                              input=json.dumps(payload), capture_output=True, text=True, timeout=30,
                              env={**os.environ, "HOME": str(self.home)})

    def test_a_personal_deny_row_is_refused_and_its_near_miss_let_through(self):
        denied = self.decide(hook.ToolCall(tool="Bash", command="cd x && tool-a wipe all", cwd=CWD)).denials
        self.assertEqual([h.rule.id for h in denied], ["tool-a-wipe"])
        self.assertEqual(self.decide(hook.ToolCall(tool="Bash", command="tool-a list", cwd=CWD)).answer, "allow")

    def test_the_wired_hook_reads_them_through_the_pointer(self):
        proc = self.run_hook("tool-a wipe all")
        out = json.loads(proc.stdout)["hookSpecificOutput"]
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("tool-a-wipe", out["permissionDecisionReason"])
        self.assertEqual((self.run_hook("tool-a list").stdout, self.run_hook("ls").stdout), ("", ""))

    def test_a_personal_allow_and_report_row_is_reported(self):
        proc = self.run_hook("tool-b sync")
        self.assertEqual((proc.returncode, proc.stdout), (0, ""), proc.stderr)
        [log] = list((self.home / "reports").iterdir())
        self.assertEqual(json.loads(log.read_text())["rules"], ["tool-b-sync"])

    def test_an_allow_row_leaves_the_call_to_the_harness(self):
        verdict = self.decide(hook.ToolCall(tool="mcp__server-a__read_item", cwd=CWD))
        self.assertEqual((verdict.answer, [h.rule.id for h in verdict.allows]), ("allow", ["server-a-read"]))
        self.assertEqual(hook.write_claude_code(verdict.denials), "")

    def test_a_broken_personal_file_leaves_the_rule_table_in_force(self):
        self.permissions.write_text("{nope")
        proc = self.run_hook("tool-a wipe all && rm -rf x")
        reason = json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn("rm-recursive-force", reason)
        self.assertNotIn("tool-a-wipe", reason)
        self.assertIn("personal permissions skipped", proc.stderr)

    def test_a_personal_row_of_the_wrong_shape_leaves_the_rule_table_in_force(self):
        for bad in ({**PERSONAL_ROWS[0], "id": ["tool-a-wipe"]},
                    {**PERSONAL_ROWS[0], "match": {"server": 5, "tool": "^read_"}}):
            self.write([bad])
            proc = self.run_hook("rm -rf /tmp/x")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            reason = json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
            self.assertIn("rm-recursive-force", reason)
            self.assertIn("personal permissions skipped", proc.stderr)

    def test_a_personal_row_cannot_reuse_a_table_id(self):
        self.write([{**PERSONAL_ROWS[0], "id": "rm-recursive-force"}])
        with self.assertRaises(rules.RuleTableError):
            personal.permissions(self.home, TABLE)

    def test_no_pointer_or_no_permissions_file_means_no_personal_rows(self):
        self.permissions.unlink()
        self.assertEqual(personal.permissions(self.home, TABLE), [])
        (self.home / ".config" / "agents" / "source.md").unlink()
        self.assertEqual(personal.permissions(self.home, TABLE), [])



class WiredCommandTest(unittest.TestCase):
    """The fail-open command the references tell the agent to wire: a gone script or a broken
    table lets the call through, and a deny still refuses."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def wired(self, script, harness, *extra):
        q = shlex.quote(str(script))
        tail = "".join(" " + shlex.quote(e) for e in extra)
        return f"[ -f {q} ] && python3 {q} --harness {harness}{tail} || " + ("echo '{}'" if harness == "cursor" else "true")

    def run_wired(self, command, payload):
        return subprocess.run(["/bin/sh", "-c", command], input=json.dumps(payload), capture_output=True,
                              text=True, timeout=30, env={**os.environ, "HOME": str(self.dir)})

    def test_a_missing_script_exits_0_and_says_nothing(self):
        gone = self.dir / "gone" / "pre_tool_hook.py"
        deny = {"tool_name": "Bash", "tool_input": {"command": "rm -rf x"}, "cwd": str(self.dir)}
        for harness in ("claude-code", "codex"):
            proc = self.run_wired(self.wired(gone, harness), deny)
            self.assertEqual((proc.returncode, proc.stdout), (0, ""), harness)
        # Cursor reads an empty answer as invalid JSON, which blocks: it gets `{}`.
        proc = self.run_wired(self.wired(gone, "cursor"), deny)
        self.assertEqual((proc.returncode, proc.stdout.strip()), (0, "{}"))

    def test_a_present_script_still_refuses(self):
        script = SCRIPTS / "pre_tool_hook.py"
        deny = {"tool_name": "Bash", "tool_input": {"command": "rm -rf x"}, "cwd": str(self.dir)}
        proc = self.run_wired(self.wired(script, "claude-code"), deny)
        self.assertEqual(json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")
        cursor = {"hook_event_name": "beforeShellExecution", "command": "rm -rf x", "cwd": str(self.dir)}
        proc = self.run_wired(self.wired(script, "cursor"), cursor)
        self.assertEqual(json.loads(proc.stdout)["permission"], "deny")

    def test_a_broken_table_fails_open_too(self):
        bad = self.dir / "bad.json"
        bad.write_text("{nope")
        payload = {"tool_name": "Bash", "tool_input": {"command": "rm -rf x"}}
        proc = self.run_wired(self.wired(SCRIPTS / "pre_tool_hook.py", "claude-code", "--rules", str(bad)), payload)
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))


class PiTest(unittest.TestCase):
    """What set-up-machine's Pi extension sends, and the one JSON line it gets back."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name).resolve()
        self.config = self.dir / "hook.json"
        self.config.write_text(json.dumps({"report_dir": str(self.dir / "reports")}))

    def tearDown(self):
        self._tmp.cleanup()

    def payload(self, tool, has_ui=True, **args):
        return {"toolName": tool, "input": args, "cwd": CWD, "sessionId": "s1", "hasUI": has_ui}

    def decide(self, tool, has_ui=True, **args):
        return hook.decide(hook.read_pi(self.payload(tool, has_ui, **args)), TABLE, HOME)

    def answer(self, payload):
        out = io.StringIO()
        with mock.patch.dict(os.environ, {"HOME": str(self.dir)}):
            code = hook.main(["--harness", "pi", "--config", str(self.config)], io.StringIO(json.dumps(payload)), out,
                             now=datetime(2026, 10, 10, tzinfo=timezone.utc))
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue().count("\n"), 1, out.getvalue())
        return json.loads(out.getvalue())

    def test_built_in_tools_are_read(self):
        call = hook.read_pi(self.payload("bash", command="rm -rf x", timeout=5))
        self.assertEqual((call.tool, call.command, call.cwd, call.session), ("bash", "rm -rf x", CWD, "s1"))
        self.assertEqual(hook.read_pi(self.payload("powershell", command="ls")).command, "ls")
        for tool, access in (("read", "read"), ("edit", "write"), ("write", "write"), ("ls", "read")):
            self.assertEqual(hook.read_pi(self.payload(tool, path="a.txt")).files, (("a.txt", access),), tool)
        self.assertEqual(hook.read_pi(self.payload("grep", pattern="x", path="src", glob="*.env")).searches, (("src", "*.env"),))
        self.assertEqual(hook.read_pi(self.payload("find", pattern=".env*")).searches, (("", ".env*"),))
        self.assertIsNone(hook.read_pi(self.payload("read", command="rm -rf x")).command)

    def test_deny_rows_refuse(self):
        self.assertEqual([h.rule.id for h in self.decide("bash", command="rm -rf .scratch/x").denials], ["rm-recursive-force"])
        self.assertEqual([h.rule.id for h in self.decide("read", path=".env").denials], ["env-files-read"])
        self.assertEqual(self.decide("read", path=".env.example").denials, [])
        self.assertIn("env-files-read", [h.rule.id for h in self.decide("find", pattern="*.env").denials])
        self.assertEqual([h.rule.id for h in self.decide("mcp__claude_ai_Gmail__send_message").denials], ["mail-send"])
        answer = self.answer(self.payload("bash", command="ls && rm -rf x"))
        self.assertEqual(list(answer), ["block"])
        self.assertIn("`rm -rf x`", answer["block"])
        self.assertNotIn("`ls`", answer["block"])

    def test_ask_rows_are_asked_with_a_ui(self):
        v = self.decide("bash", command="git push --force-with-lease origin x")
        self.assertEqual(([h.rule.id for h in v.asks], v.denials), (["git-push-force-with-lease"], []))
        answer = self.answer(self.payload("bash", command="git push --force-with-lease origin x"))
        self.assertEqual(list(answer), ["ask"])
        self.assertIn("`git push --force-with-lease origin x`", answer["ask"])
        self.assertIn("git-push-force-with-lease", answer["ask"])
        self.assertIn("The agent's instruction:", answer["ask"])

    def test_ask_rows_are_refused_without_a_ui(self):
        for has_ui in (False, None):
            payload = self.payload("bash", command="git push --force-with-lease origin x")
            payload["hasUI"] = has_ui
            answer = self.answer(payload)
            self.assertEqual(list(answer), ["block"], has_ui)
            self.assertIn("Pi without a UI, where no one asks the user", answer["block"])

    def test_user_approver_rows_are_asked_like_any_other(self):
        v = self.decide("mcp__claude_ai_Gmail__create_draft")
        self.assertEqual(([h.rule.id for h in v.asks], v.denials), (["mail-draft-write"], []))
        self.assertEqual([h.rule.id for h in self.decide("mcp__claude_ai_Gmail__create_draft", has_ui=False).denials],
                         ["mail-draft-write"])

    def test_nested_codemode_calls(self):
        # The outer call carries a script, not a command; each nested call arrives as a plain tool call.
        outer = hook.read_pi(self.payload("codemode", code='await tools.bash({command: "rm -rf x"})'))
        self.assertEqual((outer.command, outer.files), (None, ()))
        self.assertEqual(self.answer(self.payload("codemode", code='await tools.bash({command: "rm -rf x"})')), {})
        nested = {**self.payload("bash", command="rm -rf x"), "parentToolCallId": "call_1"}
        self.assertEqual(list(self.answer(nested)), ["block"])

    def test_an_ordinary_call_gets_an_empty_answer_and_a_reported_one_a_report(self):
        self.assertEqual(self.answer(self.payload("bash", command="ls -la")), {})
        self.assertFalse((self.dir / "reports").exists())
        self.assertEqual(self.answer(self.payload("bash", command="gh api rate_limit")), {})
        [log] = list((self.dir / "reports").iterdir())
        line = json.loads(log.read_text())
        self.assertEqual((line["harness"], line["session"], line["rules"]), ("pi", "s1", ["gh-api-secrets"]))

    def test_other_payload_shapes_never_crash(self):
        for payload in ({}, {"toolName": 3, "input": "x"}, {"toolName": "bash", "input": {"command": None}},
                        {"toolName": "read", "input": {"path": 7}}):
            self.assertEqual(self.answer(payload), {}, payload)
        self.assertEqual(hook.write_claude_code([], asks=["x"]), "")
        self.assertEqual(hook.write_cursor([], asks=["x"]), "{}\n")


# Loads the rendered extension as a module, gives it a stand-in for Pi, and prints what its
# tool_call handler returns, with the dialogs it opened. argv: module, event JSON, ctx JSON.
EXTENSION_DRIVER = """
const [mod, eventJson, ctxJson] = process.argv.slice(2);
const { default: factory } = await import(mod);
const handlers = {}, emitted = [], dialogs = [];
factory({ on: (name, fn) => (handlers[name] = fn), events: { emit: (name, data) => emitted.push([name, data]) } });
const spec = JSON.parse(ctxJson);
const ctx = {
  cwd: spec.cwd, hasUI: spec.hasUI, sessionManager: { getSessionId: () => "s1" },
  ui: {
    notify: (message, type) => dialogs.push(["notify", type]),
    select: async (title, options) => { dialogs.push(["select", options]); return spec.pick === "enter" ? options[0] : spec.pick; },
    confirm: async () => { throw new Error("confirm puts the cursor on Yes"); },
  },
};
const result = await handlers.tool_call(JSON.parse(eventJson), ctx);
console.log(JSON.stringify({ result: result ?? null, emitted, dialogs }));
"""


@unittest.skipUnless(shutil.which("node"), "node isn't installed")
class PiExtensionTest(unittest.TestCase):
    """The extension template, run under node against the real hook script."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name).resolve()
        self.config = self.dir / "hook.json"
        self.config.write_text(json.dumps({"report_dir": str(self.dir / "reports")}))
        (self.dir / "driver.mjs").write_text(EXTENSION_DRIVER)

    def tearDown(self):
        self._tmp.cleanup()

    def run_extension(self, command, tool="bash", has_ui=True, pick=None, script=None, python=sys.executable, **args):
        script = str(script or SCRIPTS / "pre_tool_hook.py")
        argv = [python, script, "--harness", "pi", "--config", str(self.config)]
        template = (SCRIPTS.parent / "references" / "pi-extension.ts").read_text()
        module = self.dir / "set-up-machine.mjs"
        module.write_text(template.replace("__HOOK_COMMAND__", json.dumps(argv)))
        event = {"toolName": tool, "input": {"command": command, **args} if command else args, "toolCallId": "c1"}
        ctx = {"cwd": str(self.dir), "hasUI": has_ui, "pick": pick}
        proc = subprocess.run(["node", str(self.dir / "driver.mjs"), str(module), json.dumps(event), json.dumps(ctx)],
                              capture_output=True, text=True, timeout=60, env={**os.environ, "HOME": str(self.dir)})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_a_denied_call_is_blocked_and_an_ordinary_one_runs(self):
        out = self.run_extension("rm -rf .scratch/x")
        self.assertTrue(out["result"]["block"])
        self.assertIn("rm-recursive-force", out["result"]["reason"])
        self.assertIsNone(self.run_extension("ls")["result"])

    def test_an_ask_row_asks_with_no_first(self):
        out = self.run_extension("git push --force-with-lease origin x", pick="enter")
        self.assertTrue(out["result"]["block"])
        self.assertIn("the user declined", out["result"]["reason"])
        [select] = [d for d in out["dialogs"] if d[0] == "select"]
        self.assertTrue(select[1][0].startswith("No"), select)
        self.assertEqual([e[1]["active"] for e in out["emitted"]], [True, False])
        self.assertIsNone(self.run_extension("git push --force-with-lease origin x", pick="Yes, allow this call")["result"])
        self.assertTrue(self.run_extension("git push --force-with-lease origin x", pick=None)["result"]["block"])  # Escape

    def test_an_ask_row_without_a_ui_is_refused_unasked(self):
        out = self.run_extension("git push --force-with-lease origin x", has_ui=False)
        self.assertIn("Pi without a UI", out["result"]["reason"])
        self.assertEqual(out["dialogs"], [])

    def test_it_fails_closed(self):
        for script, why in ((self.dir / "gone" / "pre_tool_hook.py", "its script is missing"),):
            out = self.run_extension("ls", script=script)
            self.assertTrue(out["result"]["block"])
            self.assertIn(why, out["result"]["reason"])
            self.assertIn("/set-up-machine", out["result"]["reason"])
        out = self.run_extension("ls", python=str(self.dir / "no-such-python"))
        self.assertIn("can't start", out["result"]["reason"])
        for body, why in (("import sys; sys.exit(3)", "exited with code 3"), ("print('not json')", "isn't JSON"),
                          ("print('[1]')", "isn't a JSON object")):
            fake = self.dir / "pre_tool_hook.py"
            fake.write_text(body + "\n")
            out = self.run_extension("ls", script=fake)
            self.assertTrue(out["result"]["block"], body)
            self.assertIn(why, out["result"]["reason"], body)


if __name__ == "__main__":
    unittest.main()
