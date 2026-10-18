"""opencode: its hook payload, and the check of each setup area, as `references/opencode/cli.md` describes.

Its global folder is `~/.config/opencode`. The hook runs through a plugin there, and the permissions and the declared config's keys are in its config file. set-up-machine delivers no plugins entries to opencode, so that area is a gap.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from ...checks import (Cell, cell, json_config_cell, link_problem, na, on_path, personal_problems, read_json,
                      skill_problems, template_problem)
from ...hook import PATCH_FILE, ToolCall, refusal, search_pair

ID, LABEL = "opencode", "opencode"
ENV = "cli"
FOLDER = Path(".config/opencode")
# Built-in tools that take a path: the argument holding it, and the access it means.
FILE_TOOLS = {"read": ("filePath", "read"), "grep": ("path", "read"), "glob": ("path", "read"),
              "list": ("path", "read"), "edit": ("filePath", "write"), "write": ("filePath", "write")}
# Every other tool is an MCP tool, named `<server>_<tool>`.
BUILTINS = {"invalid", "question", "bash", "task", "webfetch", "websearch", "todowrite", "todoread", "skill", "lsp",
            "codesearch", "apply_patch", "patch", "plan_enter", "plan_exit", *FILE_TOOLS}
LEVELS = {"deny": "deny", "ask": "ask", "allow": "allow"}


def present(home: Path) -> bool:
    return (home / FOLDER).is_dir() or on_path(home, "opencode")


# --- the hook ------------------------------------------------------------------------------


def read(payload: dict) -> ToolCall:
    """What the opencode plugin sends from `tool.execute.before`: `tool`, `sessionID`, `args` and `directory`. Auto-approve can answer an ask for the user, and the plugin can't tell it's on, so every call is unattended."""
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
    """`AGENTS.md` links to the shared file. opencode has no memory feature."""
    problems = [link_problem(ctx, ctx.home / FOLDER / "AGENTS.md")]
    if ctx.setup.file(ID, "instructions", ENV):
        problems.append(("gap", "setup/harnesses.json names instructions for opencode, which has no place for them"))
    return cell([p for p in problems if p])


def check_guardrails(ctx) -> Cell:
    """The plugin runs the hook; personal permissions are patterns in the config's `permission` key."""
    plugin = ctx.home / FOLDER / "plugins/set-up-machine.js"
    problems = [template_problem(ctx, plugin, "opencode/opencode-plugin.js", ID) if plugin.is_file() else
                ("FAIL", f"no plugin at {ctx.show(plugin)}")]
    config = _config_path(ctx.home)
    data = _read_config(config)
    if data is None:
        return cell([p for p in problems if p] + [("FAIL", f"{ctx.show(config)} isn't a valid JSON object")])
    lists = _native_lists(data.get("permission"))
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


def check_config(ctx) -> Cell:
    """Each key the declared opencode config sets, such as `model`, has its value in the config file opencode reads last; an opencode.jsonc is read without its comments."""
    return json_config_cell(ctx, ID, LABEL, _config_path(ctx.home), read=_read_config, env=ENV)


def _mcp_names(tool: str) -> tuple:
    """Either part of `<server>_<tool>` may hold `_`, so every split is a candidate name."""
    return tuple(f"mcp__{tool[:i]}__{tool[i + 1:]}" for i in range(1, len(tool) - 1) if tool[i] == "_")


def _config_path(home: Path) -> Path:
    """The last of the global config files that exists; `opencode.json` when none does."""
    found = [home / FOLDER / n for n in ("config.json", "opencode.json", "opencode.jsonc") if (home / FOLDER / n).is_file()]
    return found[-1] if found else home / FOLDER / "opencode.json"


def _read_config(path: Path):
    """The config file as read_json reads it; a .jsonc file loses its comments and trailing commas first."""
    if path.suffix != ".jsonc":
        return read_json(path)
    try:
        data = json.loads(_jsonc_as_json(path.read_text()))
    except FileNotFoundError:
        return {}
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _jsonc_as_json(text: str) -> str:
    """JSONC as JSON: `//` and `/* */` comments, then commas before `}` or `]`, removed outside strings."""
    def outside_strings(pattern, text):
        return re.sub(rf'"(?:\\.|[^"\\])*"|{pattern}', lambda m: m.group(0) if m.group(0)[0] == '"' else " ",
                      text, flags=re.S)
    return outside_strings(r",(?=\s*[}\]])", outside_strings(r"//[^\n]*|/\*.*?\*/", text))


def _native_lists(permission) -> dict:
    """The `permission` key as deny, ask and allow lists of (kind, text) entries."""
    lists = {name: [] for name in LEVELS}
    for tool, value in (permission if isinstance(permission, dict) else {}).items():
        patterns = value if isinstance(value, dict) else {"*": value}
        for pattern, level in patterns.items():
            if not isinstance(level, str) or level not in lists:
                continue
            if tool == "bash":
                lists[level].append(("command", re.sub(r" \*$", "", pattern)))
            elif tool in ("read", "edit", "external_directory"):
                lists[level].append(("path", pattern))
            elif pattern == "*":
                lists[level] += [("mcp", name) for name in _mcp_names(tool)]
    return lists
