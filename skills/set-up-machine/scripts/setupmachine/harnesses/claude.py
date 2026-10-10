"""Claude Code plugin adapter: validate, check and propose. It never writes."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from . import policy
from .errors import PluginsError


def validate(entry: dict, where: str):
    policy.validate(entry, where)


def installed(home: Path) -> dict:
    """Each plugin Claude Code installed, as `<plugin>@<marketplace>` -> whether it is enabled."""
    try:
        recorded = json.loads((home / ".claude/plugins/installed_plugins.json").read_text()).get("plugins", {})
    except (OSError, ValueError, AttributeError):
        recorded = {}
    try:
        enabled = json.loads((home / ".claude/settings.json").read_text()).get("enabledPlugins", {})
    except (OSError, ValueError, AttributeError):
        enabled = {}
    return {source: enabled.get(source) is True for source in recorded}


def bundle_servers(home: Path, source: str) -> list:
    """The MCP server names a Claude Code plugin declares, from its install folder."""
    try:
        records = json.loads((home / ".claude/plugins/installed_plugins.json").read_text())["plugins"][source]
        folder = Path(records[0]["installPath"])
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        return []
    for name in (".mcp.json", "mcp.json"):
        try:
            data = json.loads((folder / name).read_text())
        except (OSError, ValueError):
            continue
        servers = data.get("mcpServers", data) if isinstance(data, dict) else {}
        return sorted(k for k, v in servers.items() if isinstance(v, dict))
    return []


def check(ctx, tag: str, entry: dict) -> list:
    home = ctx.home
    if not (home / ".claude").is_dir():
        return [("n/a", f"Claude Code: {tag} isn't checked; Claude Code is not set up here")]
    if entry["kind"] == "mcp":
        return [("gap", f"Claude Code: {tag} is listed, but set-up-machine can't check a standalone MCP server "
                        "there yet; use a bundle")]
    source = entry["source"]
    known = ctx.claude_plugins
    if source not in known:
        return [("FAIL", f"Claude Code: {tag} {source} isn't installed")]
    if not known[source]:
        return [("FAIL", f"Claude Code: {tag} {source} isn't enabled in ~/.claude/settings.json")]
    lines = [("ok", f"Claude Code: {tag} {source} is installed and enabled; declaration matches, readiness only; latest release is unverified")]
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
    missing = [tool for tool in disabled if not denied(deny, entry["name"], tool)]
    if missing:
        return [("FAIL", f"Claude Code: {tag} denies {', '.join(missing)} from the derived tool list, "
                         f"but {path} has no matching deny entry")]
    return [("ok", f"Claude Code: {tag} deny list matches the derived tool list")]


def denied(deny: list, server: str, tool: str) -> bool:
    full = f"mcp__{server}__{tool}"
    for item in deny:
        if not isinstance(item, str):
            continue
        if item in (full, f"mcp__{server}"):
            return True
        if item.endswith("*") and full.startswith(item[:-1]):
            return True
    return False
