"""The basic pre-tool hook: deny and allow-and-report rows, checked before a tool call runs.

A harness hands the hook one tool call; the hook reads it into a `ToolCall`,
checks it against the rule table, and answers in the harness's own format:

- **deny:** any part of the call a deny row covers refuses the whole call, and
  the answer names each refused part with its rule's reason and instruction;
- **allow-and-report:** otherwise, a call an allow-and-report row covers gets one
  line in the report folder, and the hook says nothing, so the harness's own
  permissions decide;
- `ask` rows stay with the harness's native permissions.

Each harness has a reader (its payload -> ToolCall) and a writer (the denials
-> what it prints), in HARNESSES. The report folder comes from the hook's
configuration file, `~/.config/agents/hook.json` by default.
"""
from __future__ import annotations

import json
import os
import shlex
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from . import commands, rules as rule_table

CONFIG_PATH = "~/.config/agents/hook.json"
DEFAULT_REPORT_DIR = "~/.local/state/agents/reports"


@dataclass
class ToolCall:
    tool: str
    command: object = None  # the shell command text, for a tool that runs one
    files: tuple = ()  # (path, access) pairs, access being read or write
    cwd: str = ""
    session: str = ""


@dataclass
class Hit:
    rule: object
    part: str  # the part of the call the rule covers, as the agent would recognise it


@dataclass
class Verdict:
    denials: list = field(default_factory=list)
    reports: list = field(default_factory=list)


def decide(call: ToolCall, table: list, home: Path) -> Verdict:
    verdict = Verdict()
    checked = [r for r in table if r.level in ("deny", "allow-and-report")]
    hits = []
    if call.command:
        for argv in commands.simple_commands(call.command):
            hits += [Hit(r, shlex.join(argv)) for r in checked if r.kind == "command" and commands.covers(r, argv)
                     and (not r.files or any(path_matches(r, w, call.cwd, home) for w in operand_files(argv)))]
    for path, access in call.files:
        hits += [Hit(r, f"{access} {path}") for r in checked
                 if r.kind == "file" and (r.access == access or r.access == "read")
                 and path_matches(r, path, call.cwd, home)]
    if rule_table.split_mcp_name(call.tool):
        hits += [Hit(r, call.tool) for r in checked if r.kind == "mcp-tool" and rule_table.matching_tools(r, [call.tool])]
    seen = set()
    for hit in hits:
        key = (hit.rule.id, hit.part)
        if key not in seen:
            seen.add(key)
            (verdict.denials if hit.rule.level == "deny" else verdict.reports).append(hit)
    if verdict.denials:
        verdict.reports = []
    return verdict


# --- file rows ----------------------------------------------------------------


def path_matches(rule, path: str, cwd: str, home: Path) -> bool:
    """Whether a file path falls under one of the row's globs (`paths`, or a command row's
    `files`) and none of its `except` globs.

    Globs read as rules.glob_regex says. The path is checked as written and with
    symlinks resolved, and as a folder too (`secrets` counts as inside `secrets/**`).
    """
    base = os.path.normpath(cwd or os.getcwd())
    if path == "~" or path.startswith("~/"):
        path = str(home) + path[1:]
    full = os.path.normpath(os.path.join(base, path))
    candidates = {full, os.path.realpath(full)}

    def under(globs, as_folder):
        names = candidates | {c + "/_" for c in candidates} if as_folder else candidates
        return any(rule_table.glob_regex(g, base, home).match(c) for g in globs for c in names)

    return under(rule.paths or rule.files, True) and not under(rule.excepts, False)


def operand_files(argv: list) -> list:
    """The words of a command that could name a file: every word after the program but its flags."""
    return [a for a in argv[1:] if a and not a.startswith("-")]


# --- what the agent reads -------------------------------------------------------


def refusal(denials: list) -> str:
    lines = [
        "Refused by the pre-tool hook, from the global rule table. Nothing in this call ran. "
        "Only the parts below are refused: run every other step as its own command.",
    ]
    for hit in denials:
        r = hit.rule
        lines.append(f"- `{hit.part}`: denied by rule {r.id} ({_plain(r.summary)}). {r.reason} Instead: {r.instruction}")
    return "\n".join(lines)


def _plain(summary: str) -> str:
    return summary.replace("`", "")


# --- the report ---------------------------------------------------------------


def load_config(path: Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        return {}
    return data if isinstance(data, dict) else {}


def report_dir(config: dict, config_path: Path) -> Path:
    """The configured report folder; a relative one is relative to the configuration file."""
    value = config.get("report_dir")
    if not isinstance(value, str) or not value:
        state = os.environ.get("XDG_STATE_HOME")
        return Path(state) / "agents" / "reports" if state else Path(DEFAULT_REPORT_DIR).expanduser()
    folder = Path(value).expanduser()
    return folder if folder.is_absolute() else config_path.parent / folder


def write_report(folder: Path, call: ToolCall, hits: list, harness: str, now: datetime) -> Path:
    """Append one JSON line for this call to the day's file in the report folder.

    The file is readable by the user alone: a reported command can carry a
    secret's value (`gh secret set NAME --body …`).
    """
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = folder / f"{now.strftime('%Y-%m-%d')}.jsonl"
    line = {
        "time": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "harness": harness,
        "session": call.session,
        "cwd": call.cwd,
        "tool": call.tool,
        "rules": sorted({h.rule.id for h in hits}),
        "parts": [h.part for h in hits],
        "command": call.command,
    }
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    with os.fdopen(fd, "a") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")
    return path


# --- harnesses ------------------------------------------------------------------

# Claude Code's file tools: the input field holding the path, and the access it means.
CLAUDE_CODE_FILE_TOOLS = {
    "Read": ("file_path", "read"),
    "Grep": ("path", "read"),
    "Edit": ("file_path", "write"),
    "MultiEdit": ("file_path", "write"),
    "Write": ("file_path", "write"),
    "NotebookEdit": ("notebook_path", "write"),
}


def read_claude_code(payload: dict) -> ToolCall:
    """Claude Code's PreToolUse input. Other shapes that reach the same hook (the Cursor
    CLI runs Claude Code's hooks too) are read as far as they fit: any `command`
    string, top level or in `tool_input`, is checked as a shell command."""
    tool = payload.get("tool_name") if isinstance(payload.get("tool_name"), str) else ""
    tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
    command = tool_input.get("command", payload.get("command"))
    files = []
    field_name, access = CLAUDE_CODE_FILE_TOOLS.get(tool, ("file_path", "read"))
    for key in {field_name, "file_path"}:
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            files.append((value, access))
    return ToolCall(
        tool=tool,
        command=command if isinstance(command, str) else None,
        files=tuple(files),
        cwd=payload.get("cwd") if isinstance(payload.get("cwd"), str) else "",
        session=payload.get("session_id") if isinstance(payload.get("session_id"), str) else "",
    )


def write_claude_code(denials: list) -> str:
    if not denials:
        return ""
    return json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": refusal(denials),
        }
    }) + "\n"


HARNESSES = {"claude-code": (read_claude_code, write_claude_code)}


def main(argv=None, stdin=None, stdout=None, now=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="set-up-machine's pre-tool hook: reads one tool call on stdin.")
    parser.add_argument("--harness", choices=sorted(HARNESSES), default="claude-code")
    parser.add_argument("--config", type=Path, default=Path(CONFIG_PATH).expanduser(),
                        help=f"the hook's configuration (default: {CONFIG_PATH})")
    parser.add_argument("--rules", type=Path, default=rule_table.DEFAULT_TABLE)
    args = parser.parse_args(argv)
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    read, write = HARNESSES[args.harness]

    # A hook that fails never blocks the call: the harness's native deny rules stay underneath.
    try:
        payload = json.loads(stdin.read() or "{}")
        call = read(payload if isinstance(payload, dict) else {})
        table = rule_table.load(args.rules)
        verdict = decide(call, table, Path.home())
    except (ValueError, OSError) as exc:
        print(f"set-up-machine hook: {exc}", file=sys.stderr)
        return 1
    if verdict.denials:
        stdout.write(write(verdict.denials))
        return 0
    if verdict.reports:
        try:
            config = load_config(args.config)
            write_report(report_dir(config, args.config), call, verdict.reports, args.harness,
                         now or datetime.now(timezone.utc))
        except (ValueError, OSError) as exc:
            print(f"set-up-machine hook: couldn't write the report: {exc}", file=sys.stderr)
            return 1
    return 0
