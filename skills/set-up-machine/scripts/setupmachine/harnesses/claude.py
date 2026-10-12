"""Claude Code's install record and deny matching. Cursor's harness setup reads both.

The plugin adapter, validate, check and propose, lives in the Claude Code harness setup.
"""
from __future__ import annotations

import json
from pathlib import Path


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
