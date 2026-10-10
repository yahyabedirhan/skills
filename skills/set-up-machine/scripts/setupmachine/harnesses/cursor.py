"""Cursor plugin adapter: validate, check and propose. It never writes."""
from __future__ import annotations

import copy
import json

from . import claude, policy


def validate(entry: dict, where: str):
    policy.validate(entry, where)


def server_name(source: str, server: str) -> str:
    """The name Cursor gives an MCP server of a Claude Code plugin it imports."""
    return f"plugin-{source.split('@', 1)[0]}-{server}"


def check(ctx, tag: str, entry: dict) -> list:
    home = ctx.home
    folder = home / ".cursor"
    if not folder.is_dir():
        return [("n/a", f"Cursor: {tag} isn't checked; Cursor is not set up here")]
    if entry["kind"] == "bundle":
        source = entry["source"]
        if not ctx.claude_plugins.get(source):
            return [("FAIL", f"Cursor: {tag} needs {source} installed and enabled in Claude Code, since Cursor "
                             "imports bundles only from Claude Code")]
        names = [server_name(source, s) for s in claude.bundle_servers(home, source)]
        how = f"as {', '.join(names)}" if names else "(skills only; no MCP server)"
        lines = [("ok", f"Cursor: {tag} is imported from Claude Code {how}")]
        lines.extend(_tool_lines(home, tag, entry, policy.effective(entry, ctx.rules)))
        return lines
    path = folder / "mcp.json"
    try:
        servers = json.loads(path.read_text()).get("mcpServers", {}) if path.is_file() else {}
    except (OSError, ValueError, AttributeError):
        return [("FAIL", f"Cursor: {tag} can't be checked; {path} isn't valid JSON")]
    if not isinstance(servers, dict) or entry["name"] not in servers:
        return [("FAIL", f"Cursor: {tag} has no entry in {path}")]
    if servers[entry["name"]] != entry["server"]:
        return [("FAIL", f"Cursor: {tag} entry in {path} differs from installs.json")]
    return [("ok", f"Cursor: {tag} is in {path}")]


def propose(document: dict, entry: dict, rules=()) -> dict:
    """mcp.json with this standalone server merged. A bundle has nothing to write here."""
    validate(entry, "plugin")
    if entry["kind"] != "mcp":
        return copy.deepcopy(document or {})
    result = copy.deepcopy(document or {})
    servers = result.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        servers = {}
        result["mcpServers"] = servers
    servers[entry["name"]] = dict(entry["server"])
    return result


def _tool_lines(home, tag, entry, chosen) -> list:
    """Cursor imports Claude Code's deny list, so the derived tools are checked there."""
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
        return [("FAIL", f"Cursor: {tag} denies {', '.join(missing)} from the derived tool list; "
                         "Cursor imports Claude Code's deny list, which lacks them")]
    return [("ok", f"Cursor: {tag} tool list matches the derived tool list through Claude Code's deny list")]
