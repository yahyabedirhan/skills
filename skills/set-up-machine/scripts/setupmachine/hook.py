"""The basic pre-tool hook: deny and allow-and-report rows, checked before a tool call runs.

A harness hands the hook one tool call; the hook reads it into a `ToolCall`,
checks it against the rule table, and answers in the harness's own format:

- **deny:** any part of the call a deny row covers refuses the whole call, and
  the answer names each refused part with its rule's reason and instruction;
- **allow-and-report:** otherwise, a call an allow-and-report row covers gets one
  line in the report folder, and the hook says nothing, so the harness's own
  permissions decide;
- **ask:** the verdict names the ask rows a call hits (verify checks them), but the
  hook says nothing for them: the harness's native ask entries do the asking.

Each harness has a reader (its payload -> ToolCall) and a writer (the denials
-> what it prints), in HARNESSES. The report folder comes from the hook's
configuration file, `~/.config/agents/hook.json` by default.
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
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
    mcp_names: tuple = ()  # the tool's possible `mcp__<server>__<tool>` names, for a harness that names MCP tools otherwise
    searches: tuple = ()  # (folder, glob) pairs a search tool reads the matching files of
    report: bool = True  # False when another hook, wired for the same harness, reports this call


@dataclass
class Hit:
    rule: object
    part: str  # the part of the call the rule covers, as the agent would recognise it


@dataclass
class Verdict:
    denials: list = field(default_factory=list)
    reports: list = field(default_factory=list)
    asks: list = field(default_factory=list)  # ask rows the call hits; the harness's native entries do the asking

    @property
    def answer(self) -> str:
        """deny, ask or allow: what the rule table says about the call as a whole."""
        return "deny" if self.denials else "ask" if self.asks else "allow"


def decide(call: ToolCall, table: list, home: Path) -> Verdict:
    verdict = Verdict()
    checked = table
    hits = []
    files = list(call.files)
    if call.command:
        argvs = commands.simple_commands(call.command, files=files)  # redirect targets join the files
        for argv in argvs:
            hits += [Hit(r, shlex.join(argv)) for r in checked if r.kind == "command" and commands.covers(r, argv)
                     and (not r.files or any(path_matches(r, w, call.cwd, home) for w in operand_files(argv)))]
        files += commands.tee_writes(argvs)
    for folder, glob in call.searches:
        files.append((os.path.join(folder, glob) if folder else glob, "read"))
        hits += [Hit(r, f"search {glob}") for r in checked if r.kind == "file" and glob_targets(r, glob)]
    for path, access in files:
        hits += [Hit(r, f"{access} {path}") for r in checked
                 if r.kind == "file" and (r.access == access or r.access == "read")
                 and path_matches(r, path, call.cwd, home)]
    mcp_names = call.mcp_names or ((call.tool,) if rule_table.split_mcp_name(call.tool) else ())
    if mcp_names:
        hits += [Hit(r, call.tool) for r in checked if r.kind == "mcp-tool" and rule_table.matching_tools(r, mcp_names)]
    seen = set()
    for hit in hits:
        key = (hit.rule.id, hit.part)
        if key not in seen:
            seen.add(key)
            {"deny": verdict.denials, "ask": verdict.asks, "allow-and-report": verdict.reports}[hit.rule.level].append(hit)
    if verdict.denials:
        verdict.reports, verdict.asks = [], []
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
        return any(rule_table.glob_regex(g, base, home, commands.FOLD_CASE).match(c) for g in globs for c in names)

    return under(rule.paths or rule.files, True) and not under(rule.excepts, False)


# Names no secret-file row covers: a search glob matching them too is a broad search, not one aimed at the row.
ORDINARY_NAMES = ("README.md", "main.py", "notes.txt")


def glob_targets(rule, glob: str) -> bool:
    """Whether a search glob (`*.env`, `.env*`) picks out a file row's files by name.

    A name the row covers is made from each of its globs' last part (`.env.*` -> `.env.local`);
    a search glob matching one of those, but no ordinary file name, targets the row. A glob
    matching everything (`*`) is a search over the folder, which the hook doesn't expand.
    """
    pattern = glob.rstrip("/").rsplit("/", 1)[-1]
    if not set("*?[") & set(pattern) or any(fnmatch.fnmatchcase(n, pattern) for n in ORDINARY_NAMES):
        return False  # a literal glob is checked as a path; one matching ordinary names too is a broad search
    lasts = [g.rsplit("/", 1)[-1] for g in rule.paths]
    samples = {n.replace("*", "local").replace("?", "x") for n in lasts if n.strip("*?")}
    left_out = {g.rsplit("/", 1)[-1] for g in rule.excepts}
    fold = (lambda t: t.lower()) if commands.FOLD_CASE else (lambda t: t)
    return any(fnmatch.fnmatchcase(fold(n), fold(pattern)) for n in samples - left_out)


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
    """Claude Code's PreToolUse input. Other shapes that reach the same hook (Cursor runs
    Claude Code's hooks too) are read as far as they fit: any `command` string, top level
    or in `tool_input`, is checked as a shell command. Under Cursor (its payload carries
    `cursor_version`) a call is still refused, but reporting it is left to the hook wired
    in Cursor's own hooks.json, so no call is reported twice."""
    tool = payload.get("tool_name") if isinstance(payload.get("tool_name"), str) else ""
    tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
    command = tool_input.get("command", payload.get("command"))
    files = []
    field_name, access = CLAUDE_CODE_FILE_TOOLS.get(tool, ("file_path", "read"))
    for key in {field_name, "file_path"}:
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            files.append((value, access))
    searches = _search(tool_input, "path", "glob") if tool == "Grep" else ()
    return ToolCall(
        tool=tool,
        command=command if isinstance(command, str) else None,
        files=tuple(files),
        searches=searches,
        cwd=payload.get("cwd") if isinstance(payload.get("cwd"), str) else "",
        session=payload.get("session_id") if isinstance(payload.get("session_id"), str) else "",
        report="cursor_version" not in payload,
    )


def _search(args: dict, folder_key: str, glob_key: str) -> tuple:
    """A search tool's (folder, glob) pair, when it names a glob."""
    glob, folder = args.get(glob_key), args.get(folder_key)
    if not isinstance(glob, str) or not glob:
        return ()
    return ((folder if isinstance(folder, str) else "", glob),)


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


# apply_patch's file headers; each names a file the patch writes.
PATCH_FILE = re.compile(r"^\*\*\* (Add File|Update File|Delete File|Move to): (.+?)\s*$", re.M)


def read_codex(payload: dict) -> ToolCall:
    """Codex's PreToolUse input: `tool_name` is `Bash` for the shell tools (the command as
    the model wrote it, before Codex wraps it in `<shell> -lc`), `apply_patch` for file
    edits (`tool_input.command` holds the patch), or `mcp__<server>__<tool>`."""
    tool = payload.get("tool_name") if isinstance(payload.get("tool_name"), str) else ""
    tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
    command = tool_input.get("command")
    command = command if isinstance(command, str) else None
    files = ()
    if tool == "apply_patch":
        files = tuple((m.group(2), "write") for m in PATCH_FILE.finditer(command or ""))
        command = None
    return ToolCall(
        tool=tool,
        command=command,
        files=files,
        cwd=payload.get("cwd") if isinstance(payload.get("cwd"), str) else "",
        session=payload.get("session_id") if isinstance(payload.get("session_id"), str) else "",
    )


# opencode's built-in tools that take a path: the argument holding it, and the access it means.
OPENCODE_FILE_TOOLS = {
    "read": ("filePath", "read"),
    "grep": ("path", "read"),
    "glob": ("path", "read"),
    "list": ("path", "read"),
    "edit": ("filePath", "write"),
    "write": ("filePath", "write"),
}
# Its other built-in tools. Every other tool is an MCP tool, named `<server>_<tool>`.
OPENCODE_BUILTINS = {
    "invalid", "question", "bash", "task", "webfetch", "websearch", "todowrite", "todoread", "skill", "lsp",
    "codesearch", "apply_patch", "patch", "plan_enter", "plan_exit", *OPENCODE_FILE_TOOLS,
}
def read_opencode(payload: dict) -> ToolCall:
    """What set-up-machine's opencode plugin sends from `tool.execute.before`:
    `tool`, `sessionID`, `args` (the tool's arguments) and `directory` (the session's folder)."""
    tool = payload.get("tool") if isinstance(payload.get("tool"), str) else ""
    args = payload.get("args") if isinstance(payload.get("args"), dict) else {}
    directory = payload.get("directory") if isinstance(payload.get("directory"), str) else ""
    command, workdir = args.get("command"), args.get("workdir")
    files = []
    if tool in OPENCODE_FILE_TOOLS:
        key, access = OPENCODE_FILE_TOOLS[tool]
        if isinstance(args.get(key), str) and args[key]:
            files.append((args[key], access))
    patch = args.get("patchText")
    if isinstance(patch, str):
        files += [(m.group(2), "write") for m in PATCH_FILE.finditer(patch)]
    searches = _search(args, "path", "include") if tool == "grep" else ()
    mcp_names = ()
    if tool not in OPENCODE_BUILTINS:
        # Either part of `<server>_<tool>` may hold `_`, so every split is a candidate.
        mcp_names = tuple(f"mcp__{tool[:i]}__{tool[i + 1:]}" for i in range(1, len(tool) - 1) if tool[i] == "_")
    return ToolCall(
        tool=tool,
        command=command if isinstance(command, str) else None,
        files=tuple(files),
        cwd=os.path.join(directory, workdir) if isinstance(workdir, str) and workdir else directory,
        session=payload.get("sessionID") if isinstance(payload.get("sessionID"), str) else "",
        mcp_names=mcp_names,
        searches=searches,
    )


def write_opencode(denials: list) -> str:
    """The refusal as plain text: the plugin throws it, and opencode gives the agent the message as the tool's error."""
    return refusal(denials) + "\n" if denials else ""


# Cursor sends each hook event its own payload (references/cursor.md). preToolUse is wired
# only for the tools the other events don't cover: writes, deletes and searches.
CURSOR_FILE_TOOLS = {"Read": "read", "Grep": "read", "Write": "write", "Delete": "write"}


def read_cursor(payload: dict) -> ToolCall:
    def text(key, source=payload):
        value = source.get(key)
        return value if isinstance(value, str) else ""

    event = text("hook_event_name")
    roots = payload.get("workspace_roots")
    cwd = text("cwd") or (roots[0] if isinstance(roots, list) and roots and isinstance(roots[0], str) else "")
    session = text("conversation_id") or text("session_id")
    if event == "beforeShellExecution":
        return ToolCall(tool="Shell", command=text("command") or None, cwd=cwd, session=session)
    if event == "beforeMCPExecution":
        server, tool = text("mcp_server_name"), text("tool_name")
        return ToolCall(tool=f"mcp__{server}__{tool}" if server and tool else tool, cwd=cwd, session=session)
    if event == "beforeReadFile":
        path = text("file_path")
        return ToolCall(tool="Read", files=((path, "read"),) if path else (), cwd=cwd, session=session)
    tool = text("tool_name")
    tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
    files = ()
    if tool in CURSOR_FILE_TOOLS:
        path = text("file_path", tool_input) or text("path", tool_input)
        files = ((path, CURSOR_FILE_TOOLS[tool]),) if path else ()
    command = text("command", tool_input) if tool == "Shell" else ""
    searches = _search(tool_input, "path", "glob") if tool == "Grep" else ()
    return ToolCall(tool=tool, command=command or None, files=files, cwd=cwd, session=session, searches=searches)


def write_cursor(denials: list) -> str:
    """Cursor always gets a JSON answer: a deny, or `{}`, which leaves the call to its own
    permissions. The CLI shows the agent `user_message`; `agent_message` carries the same text."""
    if not denials:
        return "{}\n"
    reason = refusal(denials)
    return json.dumps({"permission": "deny", "user_message": reason, "agent_message": reason}) + "\n"


HARNESSES = {
    "claude-code": (read_claude_code, write_claude_code),
    "codex": (read_codex, write_claude_code),  # Codex reads the same deny answer as Claude Code
    "opencode": (read_opencode, write_opencode),
    "cursor": (read_cursor, write_cursor),
}


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
    if verdict.reports and call.report:
        try:
            config = load_config(args.config)
            write_report(report_dir(config, args.config), call, verdict.reports, args.harness,
                         now or datetime.now(timezone.utc))
        except (ValueError, OSError) as exc:
            print(f"set-up-machine hook: couldn't write the report: {exc}", file=sys.stderr)
            return 1
    stdout.write(write([]))
    return 0
