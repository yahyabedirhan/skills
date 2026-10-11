"""opencode's harness setup. It audits opencode and translates one hook payload.

It copies the operations Cursor established: `id`, `label`, `present`, `audit`, `read`, and `write`.
opencode takes no plugins yet, so it omits `validate`, `check`, and `propose`.
`audit` returns `(channel, status, text)` for the hook wiring. When the harnesses file
points at instructions, it returns the same gap the shared checker used to print, because
opencode has no generated instructions file yet. The printed hook word stays `hook`.
"""
from __future__ import annotations

import json
import os
import re
import shlex
from pathlib import Path

from .. import layout, personal
from ..hook import PATCH_FILE, ToolCall, _search, command_script, refusal

id = "opencode"
label = "opencode"
HOME_DIR = Path(".config/opencode")
PLUGIN = Path("plugins/set-up-machine.js")

# Built-in tools that take a path: the argument holding it, and the access it means.
FILE_TOOLS = {
    "read": ("filePath", "read"),
    "grep": ("path", "read"),
    "glob": ("path", "read"),
    "list": ("path", "read"),
    "edit": ("filePath", "write"),
    "write": ("filePath", "write"),
}
# Other built-in tools. Every other tool is an MCP tool, named `<server>_<tool>`.
BUILTINS = {
    "invalid", "question", "bash", "task", "webfetch", "websearch", "todowrite", "todoread", "skill", "lsp",
    "codesearch", "apply_patch", "patch", "plan_enter", "plan_exit", *FILE_TOOLS,
}
# Auto-approve (`--auto`, or its toggle) answers ask entries for the user, and the plugin can't tell it's on.
UNATTENDED = "opencode, whose auto-approve can answer for the user"


def present(home: Path) -> bool:
    """Whether opencode is set up on this machine: `~/.config/opencode` exists."""
    return (home / HOME_DIR).is_dir()


def audit(home: Path) -> list:
    """`(channel, status, text)` for opencode's hook wiring, and for instructions it can't take yet."""
    lines = [("hook", *_wiring(home))]
    lines.extend(("harness", status, text) for status, text in _instructions(home))
    return lines


def read(payload: dict) -> ToolCall:
    """What set-up-machine's opencode plugin sends from `tool.execute.before`:
    `tool`, `sessionID`, `args` (the tool's arguments) and `directory` (the session's folder)."""
    tool = payload.get("tool") if isinstance(payload.get("tool"), str) else ""
    args = payload.get("args") if isinstance(payload.get("args"), dict) else {}
    directory = payload.get("directory") if isinstance(payload.get("directory"), str) else ""
    command, workdir = args.get("command"), args.get("workdir")
    files = []
    if tool in FILE_TOOLS:
        key, access = FILE_TOOLS[tool]
        if isinstance(args.get(key), str) and args[key]:
            files.append((args[key], access))
    patch = args.get("patchText")
    if isinstance(patch, str):
        files += [(m.group(2), "write") for m in PATCH_FILE.finditer(patch)]
    searches = _search(args, "path", "include") if tool == "grep" else ()
    mcp_names = ()
    if tool not in BUILTINS:
        # Either part of `<server>_<tool>` may hold `_`, so every split is a candidate.
        mcp_names = tuple(f"mcp__{tool[:i]}__{tool[i + 1:]}" for i in range(1, len(tool) - 1) if tool[i] == "_")
    return ToolCall(
        tool=tool,
        command=command if isinstance(command, str) else None,
        files=tuple(files),
        cwd=os.path.join(directory, workdir) if isinstance(workdir, str) and workdir else directory,
        session=payload.get("sessionID") if isinstance(payload.get("sessionID"), str) else "",
        mcp_names=mcp_names,
        unattended=UNATTENDED,
        searches=searches,
    )


def write(denials: list, asks=()) -> str:
    """The refusal as plain text: the plugin throws it, and opencode gives the agent the message as the tool's error."""
    return refusal(denials) + "\n" if denials else ""


def _wiring(home: Path):
    if not present(home):
        return ("none", f"{label}: not set up here (no ~/{HOME_DIR})")
    path = home / HOME_DIR / PLUGIN
    try:
        text = path.read_text()
    except OSError:
        return ("FAIL", f"{label}: no plugin at {path}")
    match = re.search(r"^const COMMAND = (\[.*\]);$", text, re.M)
    command = json.loads(match.group(1)) if match else []
    script = command_script(shlex.join(command), id, home) if command else None
    if script is None:
        return ("FAIL", f"{label}: {path} doesn't run the pre-tool hook with --harness {id}")
    if not script.is_file():
        return ("FAIL", f"{label}: {path} runs {script}, which doesn't exist")
    return ("wired", f"{label}: {path} -> {script}")


def _instructions(home: Path) -> list:
    """`(status, text)` when the harnesses file points at instructions opencode can't take yet.

    A malformed harnesses file is the shared reader's line, so this returns nothing for it.
    """
    try:
        pointer = personal.read_pointer(home)
    except personal.PersonalError:
        return []
    if not pointer.repository:
        return []
    try:
        pointed = layout.harness_files(pointer.clone)
    except layout.LayoutError:
        return []
    if "instructions" not in pointed.get(id, {}):
        return []
    try:
        path = layout.harness_file(pointer.clone, id, "instructions")
    except layout.LayoutError as exc:
        return [("FAIL", f"{id}: {exc}")]
    return [("gap", f"{id}: {path} has instructions, but set-up-machine "
                    f"can't deliver them to {id} yet")]
