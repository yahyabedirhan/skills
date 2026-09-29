#!/usr/bin/env python3
"""Rule probes that need no login: sample tool calls fed to the pre-tool hook as each
harness sends them, and the command samples through `codex execpolicy check`.

Prints one line per probe, so a run on one machine diffs against a run on another:

    python3 probe.py --skill <set-up-machine folder> [--codex-rules <home>/.codex/rules/set-up-machine.rules]

Reports go to a throwaway folder, never the real one.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

COMMANDS = [
    "rm -rf x", "rm x -rf", "/bin/rm -fr x", "RM -rf x", "rm -r x", "bash -lc 'rm -rf x'",
    "echo a && rm -rf x", "find . -exec rm -rf {} +", "xargs rm -rf", "eval 'rm -rf x'",
    "rm --no-preserve-root -r /", "dd if=/dev/zero of=x", "mkfs.ext4 /dev/sda", "chmod -R 777 x",
    "sudo ls", "su -", "sh -c 'ls'",
    "git push --force origin main", "git push origin main --force", "git push -f", "git reset --hard",
    "git push --force-with-lease origin main", "git push origin main",
    "gh repo delete o/x", "gh repo archive o/x", "gh ssh-key list", "gh repo edit o/x", "gh api rate_limit",
    "gh secret set X", "gh pr list",
    "spark event list",
    "cat .env", "cat sub/.env.local", "cat .env.example", "source .env", ". .env", "less .env",
    "env", "env FOO=1 true", "env -u X", "export", "export FOO=1", "export -p", "declare -p", "set", "set -e",
    "printenv", "printenv HOME",
    "ls", "echo hi",
]
FILES = [
    (".env", "read"), ("sub/.env.local", "read"), ("sub/.env.example", "read"), (".env", "write"),
    (".env.example", "write"), ("secrets/k", "read"), ("secrets/k", "write"), ("~/.ssh/id_ed25519", "read"),
    ("~/.aws/credentials", "read"), ("README.md", "read"), ("README.md", "write"),
]
MCP = [("gmail", "send_message"), ("gmail", "trash_message"), ("gmail", "search_threads"), ("github", "create_issue")]


def payloads(harness: str, cwd: str):
    """(label, payload) for every sample, in the harness's own shape."""
    for command in COMMANDS:
        if harness in ("claude-code", "codex"):
            yield command, {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": cwd}
        elif harness == "opencode":
            yield command, {"tool": "bash", "args": {"command": command}, "directory": cwd}
        else:
            yield command, {"hook_event_name": "beforeShellExecution", "command": command, "cwd": cwd}
    for path, access in FILES:
        label = f"{access} {path}"
        if harness == "claude-code":
            yield label, {"tool_name": "Read" if access == "read" else "Write", "tool_input": {"file_path": path}, "cwd": cwd}
        elif harness == "codex":
            if access == "write":
                yield label, {"tool_name": "apply_patch", "cwd": cwd,
                              "tool_input": {"command": f"*** Begin Patch\n*** Add File: {path}\n+x\n*** End Patch"}}
        elif harness == "opencode":
            yield label, {"tool": access if access == "read" else "write", "args": {"filePath": path}, "directory": cwd}
        elif access == "read":
            yield label, {"hook_event_name": "beforeReadFile", "file_path": path, "cwd": cwd}
        else:
            yield label, {"hook_event_name": "preToolUse", "tool_name": "Write", "tool_input": {"file_path": path}, "cwd": cwd}
    for server, tool in MCP:
        label = f"mcp {server} {tool}"
        if harness in ("claude-code", "codex"):
            yield label, {"tool_name": f"mcp__{server}__{tool}", "tool_input": {}, "cwd": cwd}
        elif harness == "opencode":
            yield label, {"tool": f"{server}_{tool}", "args": {}, "directory": cwd}
        else:
            yield label, {"hook_event_name": "beforeMCPExecution", "mcp_server_name": server, "tool_name": tool, "cwd": cwd}


def verdict(hook: Path, harness: str, payload: dict, config: Path, reports: Path) -> str:
    before = sum(1 for f in reports.glob("*.jsonl") for _ in f.open()) if reports.exists() else 0
    done = subprocess.run([sys.executable, str(hook), "--harness", harness, "--config", str(config)],
                          input=json.dumps(payload), capture_output=True, text=True)
    out = done.stdout.strip()
    if done.returncode:
        return f"error {done.stderr.strip()}"
    rules = sorted(set(re.findall(r"denied by rule ([\w-]+)", out)))
    if rules:
        return "deny " + ",".join(rules)
    after = sum(1 for f in reports.glob("*.jsonl") for _ in f.open()) if reports.exists() else 0
    return "report" if after > before else "pass"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skill", type=Path, required=True, help="the installed set-up-machine folder")
    parser.add_argument("--codex-rules", type=Path, help="a generated set-up-machine.rules to check with codex execpolicy")
    args = parser.parse_args()
    hook = args.skill / "scripts" / "pre_tool_hook.py"
    with tempfile.TemporaryDirectory() as tmp:
        cwd = Path(tmp) / "project"
        cwd.mkdir()
        reports = Path(tmp) / "reports"
        config = Path(tmp) / "hook.json"
        config.write_text(json.dumps({"report_dir": str(reports)}))
        for harness in ("claude-code", "codex", "opencode", "cursor"):
            for label, payload in payloads(harness, str(cwd)):
                print(f"hook {harness:<11} {label:<40} {verdict(hook, harness, payload, config, reports)}")
    codex = shutil.which("codex")
    if args.codex_rules and codex:
        for command in COMMANDS:
            done = subprocess.run([codex, "execpolicy", "check", "--resolve-host-executables",
                                   "--rules", str(args.codex_rules), "--", *shlex.split(command)],
                                  capture_output=True, text=True)
            try:
                decision = json.loads(done.stdout).get("decision") or "none"
            except ValueError:
                decision = f"error {done.stderr.strip()[:80]}"
            print(f"codex-execpolicy {command:<40} {decision}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
