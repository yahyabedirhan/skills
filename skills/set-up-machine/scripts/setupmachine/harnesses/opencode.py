"""opencode: its hook payload, and the check of each setup area (references/opencode.md).

Its global folder is `~/.config/opencode`. The hook runs through a plugin there, and the
permissions are the `permission` key of its config file. set-up-machine delivers no plugins
entries to opencode yet, so that area is a gap.
"""
from __future__ import annotations

import json
import os
import re
import shlex
from pathlib import Path

from ..checks import Cell, cell, link_problem, na, personal_problems, read_json, skill_problems, wiring_problem
from ..hook import PATCH_FILE, ToolCall, refusal, search_pair

ID, LABEL = "opencode", "opencode"
FOLDER = Path(".config/opencode")
# Built-in tools that take a path: the argument holding it, and the access it means.
FILE_TOOLS = {"read": ("filePath", "read"), "grep": ("path", "read"), "glob": ("path", "read"),
              "list": ("path", "read"), "edit": ("filePath", "write"), "write": ("filePath", "write")}
# Every other tool is an MCP tool, named `<server>_<tool>`.
BUILTINS = {"invalid", "question", "bash", "task", "webfetch", "websearch", "todowrite", "todoread", "skill", "lsp",
            "codesearch", "apply_patch", "patch", "plan_enter", "plan_exit", *FILE_TOOLS}
LEVELS = {"deny": "deny", "ask": "ask", "allow": "allow"}


def present(home: Path) -> bool:
    return (home / FOLDER).is_dir()


# --- the hook ------------------------------------------------------------------------------


def read(payload: dict) -> ToolCall:
    """What the opencode plugin sends from `tool.execute.before`: `tool`, `sessionID`, `args` and `directory`.
    Auto-approve can answer an ask for the user, and the plugin can't tell it's on, so every call is unattended."""
    tool = payload.get("tool") if isinstance(payload.get("tool"), str) else ""
    args = payload.get("args") if isinstance(payload.get("args"), dict) else {}
    directory = payload.get("directory") if isinstance(payload.get("directory"), str) else ""
    files = []
    if tool in FILE_TOOLS and isinstance(args.get(FILE_TOOLS[tool][0]), str) and args[FILE_TOOLS[tool][0]]:
        files.append((args[FILE_TOOLS[tool][0]], FILE_TOOLS[tool][1]))
    if isinstance(args.get("patchText"), str):
        files += [(m.group(2), "write") for m in PATCH_FILE.finditer(args["patchText"])]
    workdir = args.get("workdir")
    return ToolCall(
        tool=tool, command=args.get("command") if isinstance(args.get("command"), str) else None,
        files=tuple(files), searches=search_pair(args, "path", "include") if tool == "grep" else (),
        cwd=os.path.join(directory, workdir) if isinstance(workdir, str) and workdir else directory,
        session=payload.get("sessionID") if isinstance(payload.get("sessionID"), str) else "",
        mcp_names=() if tool in BUILTINS else _mcp_names(tool),
        unattended="opencode, whose auto-approve can answer for the user")


def write(denials: list, asks=()) -> str:
    """The refusal as plain text, which the plugin throws; nothing lets the call go on."""
    return refusal(denials) + "\n" if denials else ""


# --- the checks ----------------------------------------------------------------------------


def check_instructions(ctx) -> Cell:
    """AGENTS.md links to the shared file. opencode has no memory feature."""
    problems = [link_problem(ctx, ctx.home / FOLDER / "AGENTS.md")]
    if ctx.setup.file(ID, "instructions"):
        problems.append(("gap", "setup/harnesses.json names instructions for opencode, which has no place for them"))
    return cell([p for p in problems if p])


def check_guardrails(ctx) -> Cell:
    """The plugin runs the hook; personal permissions are patterns in the config's `permission` key."""
    plugin = ctx.home / FOLDER / "plugins/set-up-machine.js"
    text = plugin.read_text() if plugin.is_file() else ""
    match = re.search(r"^const COMMAND = (\[.*\]);$", text, re.M)
    command = shlex.join(json.loads(match.group(1))) if match else None
    problems = [wiring_problem(ctx, plugin, command, ID)] if text else [("FAIL", f"no plugin at {ctx.show(plugin)}")]
    config = _config_path(ctx.home)
    lists = _native_lists((read_json(config) or {}).get("permission"))
    return cell([p for p in problems if p] + personal_problems(ctx, lists, config))


def check_sandbox(ctx) -> Cell:
    return na("opencode has no sandbox setting set-up-machine declares")


def check_plugins(ctx) -> Cell:
    entries = ctx.setup.plugins(ID)
    if not entries:
        return na("installs.json lists no plugin for opencode")
    return cell([("gap", f"{e['name']}: set-up-machine can't deliver plugins to opencode yet") for e in entries])


def check_skills(ctx) -> Cell:
    folders = [ctx.home / FOLDER / "skills", ctx.home / ".claude/skills", ctx.home / ".agents/skills"]
    return cell(skill_problems(ctx, folders))


def _mcp_names(tool: str) -> tuple:
    """Either part of `<server>_<tool>` may hold `_`, so every split is a candidate name."""
    return tuple(f"mcp__{tool[:i]}__{tool[i + 1:]}" for i in range(1, len(tool) - 1) if tool[i] == "_")


def _config_path(home: Path) -> Path:
    """The last of the global config files that exists; opencode.json when none does."""
    found = [home / FOLDER / n for n in ("config.json", "opencode.json", "opencode.jsonc") if (home / FOLDER / n).is_file()]
    return found[-1] if found else home / FOLDER / "opencode.json"


def _native_lists(permission) -> dict:
    """The `permission` key as deny, ask and allow lists of (kind, text) entries."""
    lists = {name: [] for name in LEVELS}
    for tool, value in (permission if isinstance(permission, dict) else {}).items():
        patterns = value if isinstance(value, dict) else {"*": value}
        for pattern, level in patterns.items():
            if level not in lists:
                continue
            if tool == "bash":
                lists[level].append(("command", re.sub(r" \*$", "", pattern)))
            elif tool in ("read", "edit", "external_directory"):
                lists[level].append(("path", pattern))
            elif pattern == "*":
                lists[level] += [("mcp", name) for name in _mcp_names(tool)]
    return lists
