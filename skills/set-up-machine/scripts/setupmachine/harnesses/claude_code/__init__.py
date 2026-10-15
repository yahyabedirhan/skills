"""Claude Code's local environments, the CLI and the desktop app, share `~/.claude/`: its hook
payload, and the checks both environments run (references/claude-code/index.md). Each
environment is a module here: cli.py, desktop.py and cloud.py.

Every local setting lives in `~/.claude/settings.json`, including the declared config's keys; the
instructions are `~/.claude/CLAUDE.md`, a link to the shared file. Cursor reads this harness's
plugins and permission lists too, so cursor/__init__.py imports `plugins_installed` and
`native_lists` from here, and Codex takes this harness's hook answer.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from ...checks import (Cell, any_wired_problem, as_list, cell, dig, json_config_cell, link_problem, na,
                       personal_problems, read_json, skill_problems)
from ...hook import ToolCall, refusal, search_pair

# The harness id: the key in setup/harnesses.json and installs.json, and the hook's --harness.
ID, LABEL = "claude-code", "Claude Code"
FOLDER = Path(".claude")
# Claude Code's file tools: the input field holding the path, and the access it means.
FILE_TOOLS = {"Read": ("file_path", "read"), "Grep": ("path", "read"), "Edit": ("file_path", "write"),
              "MultiEdit": ("file_path", "write"), "Write": ("file_path", "write"),
              "NotebookEdit": ("notebook_path", "write")}
# Permission modes in which an ask entry doesn't reach the user.
UNATTENDED = ("auto", "dontAsk", "bypassPermissions")


# --- the hook ------------------------------------------------------------------------------


def read(payload: dict) -> ToolCall:
    """Claude Code's PreToolUse input. Cursor runs Claude Code's hooks too: its payload carries
    `cursor_version`, and then Cursor's own hook does the reporting, so no call is reported twice."""
    tool = payload.get("tool_name") if isinstance(payload.get("tool_name"), str) else ""
    args = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
    command = args.get("command", payload.get("command"))
    key, access = FILE_TOOLS.get(tool, ("file_path", "read"))
    files = tuple((args[k], access) for k in {key, "file_path"} if isinstance(args.get(k), str) and args[k])
    in_cursor = "cursor_version" in payload
    mode = payload.get("permission_mode")
    return ToolCall(
        tool=tool, command=command if isinstance(command, str) else None, files=files,
        searches=search_pair(args, "path", "glob") if tool == "Grep" else (),
        cwd=payload.get("cwd") if isinstance(payload.get("cwd"), str) else "",
        session=payload.get("session_id") if isinstance(payload.get("session_id"), str) else "",
        report=not in_cursor,
        unattended=f"Claude Code's {mode} mode" if mode in UNATTENDED and not in_cursor else "")


def write(denials: list, asks=()) -> str:
    """A deny, or nothing, which leaves the call to Claude Code's own permissions. Codex takes the same answer."""
    if not denials:
        return ""
    return json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                              "permissionDecisionReason": refusal(denials)}}) + "\n"


# --- the checks both local environments run ---------------------------------------------


def check_instructions(ctx) -> Cell:
    """CLAUDE.md links to the shared file, and auto memory is off."""
    settings = read_json(ctx.home / FOLDER / "settings.json") or {}
    problems = [link_problem(ctx, ctx.home / FOLDER / "CLAUDE.md")]
    if settings.get("autoMemoryEnabled") is not False:
        problems.append(("FAIL", "autoMemoryEnabled isn't false in ~/.claude/settings.json"))
    if ctx.setup.file(ID, "instructions"):
        problems.append(("gap", "setup/harnesses.json names instructions for Claude Code, which has no place for "
                                "them on a machine"))
    return cell([p for p in problems if p])


def check_guardrails(ctx) -> Cell:
    """A match-all PreToolUse group runs the hook, hooks are on, and each personal permission has its entry."""
    path = ctx.home / FOLDER / "settings.json"
    settings = read_json(path)
    if settings is None:
        return cell([("FAIL", f"{ctx.show(path)} isn't valid JSON")])
    groups = [g for g in as_list(dig(settings, "hooks", "PreToolUse")) if isinstance(g, dict)]
    commands = [h.get("command") for g in groups if g.get("matcher") in ("*", "", None)
                for h in as_list(g.get("hooks")) if isinstance(h, dict)]
    problems = [any_wired_problem(ctx, path, commands, ID)]
    if settings.get("disableAllHooks") is True:
        problems.append(("FAIL", f"{ctx.show(path)} sets disableAllHooks, so the hook never runs"))
    return cell([p for p in problems if p] + personal_problems(ctx, native_lists(settings), path))


def check_plugins(ctx) -> Cell:
    """Each bundle is installed and enabled; a standalone MCP server is a gap (its file can hold tokens)."""
    entries = ctx.setup.plugins(ID)
    if not entries:
        return na("installs.json lists no plugin for Claude Code")
    installed = plugins_installed(ctx.home)
    problems = []
    for entry in entries:
        if entry["kind"] == "mcp":
            problems.append(("gap", f"{entry['name']}: a standalone MCP server lives in ~/.claude.json, "
                                    "which the verifier doesn't read"))
        elif entry["source"] not in installed:
            problems.append(("FAIL", f"{entry['source']} isn't installed"))
        elif not installed[entry["source"]]:
            problems.append(("FAIL", f"{entry['source']} isn't enabled in ~/.claude/settings.json"))
    return cell(problems)


def check_skills(ctx) -> Cell:
    return cell(skill_problems(ctx, [ctx.home / FOLDER / "skills"]))


def check_config(ctx, env=None) -> Cell:
    """Each key the declared Claude Code config sets, such as `model`, has its value in settings.json."""
    return json_config_cell(ctx, ID, LABEL, ctx.home / FOLDER / "settings.json", env=env)


# --- shared with Cursor --------------------------------------------------------------------


def plugins_installed(home: Path) -> dict:
    """Each plugin Claude Code installed, as `<plugin>@<marketplace>` -> whether it is enabled."""
    recorded = (read_json(home / FOLDER / "plugins/installed_plugins.json") or {}).get("plugins", {})
    enabled = (read_json(home / FOLDER / "settings.json") or {}).get("enabledPlugins", {})
    return {source: isinstance(enabled, dict) and enabled.get(source) is True for source in recorded}


def native_lists(settings: dict) -> dict:
    """The deny, ask and allow lists of a Claude Code settings file, as (kind, text) entries."""
    lists = {}
    for name in ("deny", "ask", "allow"):
        lists[name] = [parsed for e in dig(settings, "permissions", name) or [] if (parsed := _entry(e))]
    return lists


def _entry(entry):
    """`Bash(rm -rf *)` -> ("command", "rm -rf"); `Read(./.env)` -> ("path", "./.env"); `mcp__…` as is.
    A `Write(...)` entry counts for nothing: Claude Code never checks it (references/claude-code/index.md)."""
    if not isinstance(entry, str):
        return None
    if entry.startswith("mcp__"):
        return ("mcp", entry)
    match = re.fullmatch(r"(Bash|Read|Edit)\((.+)\)", entry, re.S)
    if not match:
        return None
    tool, inner = match.groups()
    if tool == "Bash":
        return ("command", re.sub(r"(:\*| \*)$", "", inner))
    return ("path", inner[1:] if inner.startswith("//") else inner)
