"""Claude Code's harness setup. It audits Claude Code, translates one hook payload, and adapts one plugin entry.

The operations are the ones Cursor established: `id`, `label`, `present`, `audit`, `read`, `write`,
`validate`, `check`, and `propose`. `audit` returns `(channel, status, text)` for the hook wiring
and for each personal permission's entries. The printed words stay `hook`, `personal`, and `plugin`.
"""
from __future__ import annotations

import copy
import json
import re
import shutil
from pathlib import Path

from .. import commands, personal, rules as rule_table
from ..harnesses import claude, policy
from ..harnesses.errors import PluginsError
from ..hook import ToolCall, _search, command_script, refusal

id = "claude-code"
label = "Claude Code"
HOME_DIR = Path(".claude")
LISTS = {"deny": "deny", "ask": "ask", "allow-and-report": "allow", "allow": "allow"}
# Claude Code's file tools: the input field holding the path, and the access it means.
FILE_TOOLS = {
    "Read": ("file_path", "read"),
    "Grep": ("path", "read"),
    "Edit": ("file_path", "write"),
    "MultiEdit": ("file_path", "write"),
    "Write": ("file_path", "write"),
    "NotebookEdit": ("notebook_path", "write"),
}
# Claude Code's permission modes in which an ask entry doesn't reach the user: dontAsk denies it,
# bypassPermissions isn't documented to keep it, and auto mode stays in until a probe shows its ask entries reach the user.
UNATTENDED = {mode: f"Claude Code's {mode} mode" for mode in ("auto", "dontAsk", "bypassPermissions")}


def present(home: Path) -> bool:
    """Whether Claude Code is set up on this machine: `~/.claude` exists."""
    return (home / HOME_DIR).is_dir()


def audit(home: Path, rows=None) -> list:
    """`(channel, status, text)` for Claude Code's wiring and personal permission entries.

    rows are the personal permissions the rules check already loaded, so a `--rules` file and
    this check share one list. When omitted, this loads them from the default rule table.
    A broken permissions file yields no entry lines: the shared check reports that file.
    """
    if rows is None:
        rows = _loaded_rows(home)
    lines = [("hook", *_wiring(home))]
    lines.extend(("personal", status, text) for status, text in _entries(home, rows))
    return lines


def read(payload: dict) -> ToolCall:
    """Claude Code's PreToolUse input. Other shapes that reach the same hook (Cursor runs
    Claude Code's hooks too) are read as far as they fit: any `command` string, top level
    or in `tool_input`, is checked as a shell command. Under Cursor (its payload carries
    `cursor_version`) a call is still refused, but reporting it is left to the hook wired
    in Cursor's own hooks.json, so no call is reported twice."""
    tool = payload.get("tool_name") if isinstance(payload.get("tool_name"), str) else ""
    tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
    command = tool_input.get("command", payload.get("command"))
    files = []
    field_name, access = FILE_TOOLS.get(tool, ("file_path", "read"))
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
        unattended="" if "cursor_version" in payload else UNATTENDED.get(payload.get("permission_mode"), ""),
    )


def write(denials: list, asks=()) -> str:
    """Claude Code's JSON answer: a deny, or nothing, which leaves the call to its own permissions."""
    if not denials:
        return ""
    return json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": refusal(denials),
        }
    }) + "\n"


def validate(entry: dict, where: str):
    policy.validate(entry, where)


def check(ctx, tag: str, entry: dict) -> list:
    home = ctx.home
    if not present(home):
        return [("n/a", f"{label}: {tag} isn't checked; Claude Code is not set up here")]
    if entry["kind"] == "mcp":
        return [("gap", f"{label}: {tag} is listed, but set-up-machine can't check a standalone MCP server "
                        "there yet; use a bundle")]
    source = entry["source"]
    known = ctx.claude_plugins
    if source not in known:
        return [("FAIL", f"{label}: {tag} {source} isn't installed")]
    if not known[source]:
        return [("FAIL", f"{label}: {tag} {source} isn't enabled in ~/.claude/settings.json")]
    lines = [("ok", f"{label}: {tag} {source} is installed and enabled; declaration matches, readiness only; latest release is unverified")]
    lines.extend(_tool_lines(home, tag, entry, policy.effective(entry, ctx.rules)))
    return lines


def propose(settings: dict, entry: dict, rules=()) -> dict:
    """Settings with a deny entry for each disabled tool. Other keys stay. It never writes."""
    validate(entry, "plugin")
    result = copy.deepcopy(settings or {})
    disabled = policy.effective(entry, rules).get("disabled_tools") or []
    if not disabled:
        return result
    permissions = result.setdefault("permissions", {})
    if not isinstance(permissions, dict):
        raise PluginsError("permissions must be an object; preserve it for guided review")
    deny = permissions.setdefault("deny", [])
    if not isinstance(deny, list):
        raise PluginsError("permissions.deny must be a list; preserve it for guided review")
    permissions.setdefault("allow", [])
    for tool in disabled:
        name = f"mcp__{entry['name']}__{tool}"
        if name not in deny:
            deny.append(name)
    return result


def _wiring(home: Path):
    folder = home / HOME_DIR
    if not folder.is_dir():
        return ("none", f"{label}: not set up here (no ~/{HOME_DIR})")
    path = folder / "settings.json"
    for _, _, matcher, command, _ in _pre_tool_commands(_json(path) or {}):
        script = command_script(command, id, home)
        if script and matcher in ("*", "", None):
            if not script.is_file():
                return ("FAIL", f"{label}: {path} runs {script}, which doesn't exist")
            return ("wired", f"{label}: {path} -> {script}")
    return ("FAIL", f"{label}: no pre-tool hook for every tool in {path}")


def _entries(home: Path, rows: list) -> list:
    """`(status, text)` per personal permission: its entries in Claude Code's settings.

    `present` names them; with none, `gap` for a row Claude Code has no entry for, `n/a` when
    Claude Code lacks the row's tool (no MCP tool it matches, or no program on PATH), else FAIL.
    """
    folder = home / HOME_DIR
    if not rows or not folder.is_dir():
        return []
    path = folder / "settings.json"
    permissions = (_json(path) or {}).get("permissions")
    permissions = permissions if isinstance(permissions, dict) else {}
    out = []
    for rule in rows:
        name = LISTS[rule.level]
        listed = permissions.get(name) if isinstance(permissions.get(name), list) else []
        entries = [e for e in listed if isinstance(e, str) and _entry_of(rule, e, home)]
        text = f"{label}: {rule.id} ({rule.level}, personal)"
        if entries:
            out.append(("present", f"{text}: {', '.join(entries)} in {path}"))
        elif rule.kind == "command" and (rule.bare or rule.flags_only or rule.variables or rule.files):
            out.append(("gap", f"{text}: Claude Code has no entry for this kind of command row; the hook covers "
                               "deny and allow-and-report rows"))
        elif rule.kind == "mcp-tool":
            out.append(("n/a", f"{text}: no MCP tool in {path} matches it, so it's written only once Claude Code "
                               "lists a tool it matches"))
        elif rule.kind == "command" and not any(shutil.which(p) for p in rule.programs):
            out.append(("n/a", f"{text}: {', '.join(rule.programs)} isn't on PATH, so there's no tool to write it for"))
        else:
            out.append(("FAIL", f"{text}: no entry in permissions.{name} of {path}"))
    return out


def _entry_of(rule, entry: str, home: Path) -> bool:
    """Whether a Claude Code permission entry is one this row produces: what the entry names, the row covers."""
    if rule.kind == "mcp-tool":
        return bool(rule_table.matching_tools(rule, [entry]))
    m = re.fullmatch(r"(Bash|Read|Edit|Write)\((.+)\)", entry, re.S)
    if not m:
        return False
    tool, inner = m.groups()
    if rule.kind == "command":
        if tool != "Bash":
            return False
        argvs = commands.simple_commands(re.sub(r"(:\*| \*)$", "", inner))
        return len(argvs) == 1 and commands.covers(rule, argvs[0])
    if tool not in (("Read",) if rule.access == "read" else ("Edit", "Write")):
        return False
    cwd = str(home / "project")
    if inner.startswith("//"):
        path = inner[1:]
    elif inner.startswith("~/") or inner.startswith("**/"):
        path = inner
    else:
        path = f"{cwd}/{inner[2:] if inner.startswith('./') else inner}"
    path = str(home) + path[1:] if path.startswith("~/") else path
    return any(rule_table.glob_regex(g, cwd, home).match(path) for g in rule.paths)


def _loaded_rows(home: Path) -> list:
    try:
        return personal.permissions(home, rule_table.load())
    except ValueError:
        return []


def _tool_lines(home: Path, tag: str, entry: dict, chosen: dict) -> list:
    disabled = chosen.get("disabled_tools") or []
    if not disabled:
        return []
    path = home / ".claude/settings.json"
    try:
        permissions = json.loads(path.read_text()).get("permissions", {})
    except (OSError, ValueError, AttributeError):
        permissions = {}
    deny = permissions.get("deny") if isinstance(permissions, dict) else None
    deny = deny if isinstance(deny, list) else []
    missing = [tool for tool in disabled if not claude.denied(deny, entry["name"], tool)]
    if missing:
        return [("FAIL", f"{label}: {tag} denies {', '.join(missing)} from the derived tool list, "
                         f"but {path} has no matching deny entry")]
    return [("ok", f"{label}: {tag} deny list matches the derived tool list")]


def _pre_tool_commands(settings: dict) -> list:
    """(group index, handler index, matcher, command, timeout) for every PreToolUse command handler."""
    hooks = settings.get("hooks") if isinstance(settings.get("hooks"), dict) else {}
    groups = hooks.get("PreToolUse") if isinstance(hooks.get("PreToolUse"), list) else []
    out = []
    for g, group in enumerate(groups):
        handlers = group.get("hooks") if isinstance(group, dict) and isinstance(group.get("hooks"), list) else []
        for h, handler in enumerate(handlers):
            if isinstance(handler, dict) and isinstance(handler.get("command"), str):
                out.append((g, h, group.get("matcher"), handler["command"], handler.get("timeout", 10)))
    return out


def _json(path: Path):
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None
