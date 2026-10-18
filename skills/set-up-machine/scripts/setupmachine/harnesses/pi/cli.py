"""Pi, the `pi` coding agent: its hook payload, and the check of each setup area , as references/pi/cli.md describes.

Every path is under Pi's agent folder: `PI_CODING_AGENT_DIR`, else `~/.pi/agent` (`agent_dir`). Pi has no permission system, so the hook, run through an extension, is its only guardrail. Pi has no sandbox either, so that column is n/a; the declared Pi settings are the config column.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from ...checks import (Cell, cell, declared_problems, dig, link_problem, na, on_path, read_json, skill_problems,
                      template_problem)
from ...hook import ToolCall, plain, refusal, search_pair

ID, LABEL = "pi", "Pi"
ENV = "cli"
# Pi's built-in tools that take a path: the input field holding it, and the access it means.
FILE_TOOLS = {"read": "read", "edit": "write", "write": "write", "grep": "read", "find": "read", "ls": "read"}
SEARCH_GLOB = {"grep": "glob", "find": "pattern"}


def agent_dir(home: Path) -> Path:
    """Pi's agent folder. Only the real home honors PI_CODING_AGENT_DIR; a fixture home uses its own."""
    custom = os.environ.get("PI_CODING_AGENT_DIR") if home == Path.home().resolve() else None
    return (Path(custom) if custom else home / ".pi/agent").expanduser().resolve()


def present(home: Path) -> bool:
    return agent_dir(home).is_dir() or on_path(home, "pi")


# --- the hook ------------------------------------------------------------------------------


def read(payload: dict) -> ToolCall:
    """What the Pi extension sends from `tool_call`: `toolName`, `input`, `cwd`, `sessionId` and `hasUI`. Without a UI no one can answer an ask, so the call is unattended."""
    tool = payload.get("toolName") if isinstance(payload.get("toolName"), str) else ""
    args = payload.get("input") if isinstance(payload.get("input"), dict) else {}
    command = args.get("command") if tool in ("bash", "powershell") else None
    path = args.get("path")
    return ToolCall(
        tool=tool, command=command if isinstance(command, str) else None,
        files=((path, FILE_TOOLS[tool]),) if tool in FILE_TOOLS and isinstance(path, str) and path else (),
        searches=search_pair(args, "path", SEARCH_GLOB[tool]) if tool in SEARCH_GLOB else (),
        cwd=payload.get("cwd") if isinstance(payload.get("cwd"), str) else "",
        session=payload.get("sessionId") if isinstance(payload.get("sessionId"), str) else "",
        unattended="" if payload.get("hasUI") is True else "Pi without a UI",
        no_native_ask=True)  # the extension does the asking


def write(denials: list, asks=()) -> str:
    """Always one JSON line: `{"block": …}`, `{"ask": …}` with the question the extension asks, or `{}`."""
    if denials:
        return json.dumps({"block": refusal(denials)}) + "\n"
    if asks:
        lines = ["The global rule table asks you before this call runs. Allow it?"]
        lines += [f"- `{h.part}`: ask rule {h.rule.id} ({plain(h.rule.summary)}). {h.rule.reason} "
                  f"The agent's instruction: {h.rule.instruction}" for h in asks]
        return json.dumps({"ask": "\n".join(lines)}) + "\n"
    return "{}\n"


# --- the checks ----------------------------------------------------------------------------


def check_instructions(ctx) -> Cell:
    """`AGENTS.md` links to the shared file, and no override file wins over it. Pi has no memory feature."""
    problems = [link_problem(ctx, ctx.pi_dir / "AGENTS.md")]
    if (ctx.pi_dir / "AGENTS.override.md").exists():
        problems.append(("gap", "AGENTS.override.md in Pi's agent folder is read instead of AGENTS.md"))
    if ctx.setup.file(ID, "instructions", ENV):
        problems.append(("gap", "setup/harnesses.json names instructions for Pi, which has no place for them"))
    return cell([p for p in problems if p])


def check_guardrails(ctx) -> Cell:
    """The set-up-machine extension runs the hook. With no native rules, personal permissions need no entry."""
    path = ctx.pi_dir / "extensions/set-up-machine.ts"
    if not path.is_file():
        return cell([("FAIL", f"no extension at {ctx.show(path)}; nothing enforces the rule table in Pi")])
    return cell([p for p in [template_problem(ctx, path, "pi/pi-extension.ts", ID)] if p])


def check_sandbox(ctx) -> Cell:
    return na("Pi has no sandbox or approval setting")


def check_plugins(ctx) -> Cell:
    """A bundle is in `settings.json` `packages`; an MCP server is in `mcp.json`, with Pi's MCP client on."""
    entries = ctx.setup.plugins(ID)
    if not entries:
        return na("installs.json lists no plugin for Pi")
    settings = read_json(ctx.pi_dir / "settings.json") or {}
    packages = {_unversioned(p.get("source") if isinstance(p, dict) else p) for p in settings.get("packages") or []}
    servers = dig(read_json(ctx.pi_dir / "mcp.json") or {}, "mcpServers") or {}
    problems = []
    for entry in entries:
        if entry["kind"] == "bundle" and _unversioned(entry["source"]) not in packages:
            problems.append(("FAIL", f"{entry['source']} isn't in packages of Pi's settings.json"))
        elif entry["kind"] == "mcp" and servers.get(entry["name"]) != entry["server"]:
            problems.append(("FAIL", f"{entry['name']} is missing or differs in Pi's mcp.json"))
        elif entry["kind"] == "mcp" and "-builtin:mcp" in (settings.get("extensions") or []):
            problems.append(("gap", f"{entry['name']}: -builtin:mcp turns off the MCP client that reads mcp.json"))
    return cell(problems)


def check_skills(ctx) -> Cell:
    return cell(skill_problems(ctx, [ctx.home / ".agents/skills", ctx.pi_dir / "skills"]))


def check_config(ctx) -> Cell:
    """Each key the declared Pi config sets has its value in settings.json. A `packages` key is a gap: Pi extensions come from installs.json plugins, so it is never compared."""
    source = ctx.setup.file(ID, "config", ENV)
    if source is None:
        return na("setup/harnesses.json names no Pi config")
    declared, target = read_json(source), ctx.pi_dir / "settings.json"
    problems = [("gap", f"{source.name} declares packages; move Pi extensions into installs.json plugins")
                ] if isinstance(declared, dict) and "packages" in declared else []
    keys = [key for key in declared if key != "packages"] if isinstance(declared, dict) else None
    return cell(problems + declared_problems(ctx, source, declared, target, read_json(target), keys))


def _unversioned(source) -> str:
    """A package source without its `@<version>` or `@<ref>`, as Pi names one extension: `npm:pi-web-access@0.38.0` and `npm:pi-web-access@latest` are the same extension."""
    if not isinstance(source, str):
        return ""
    head, at, tail = source.rpartition("@")
    return head if at and "/" not in tail and not head.endswith(":") else source
