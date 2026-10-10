"""The plugins setup area: the `plugins` list in the workstation repo's agents/installs.json, checked
against each harness.

A plugin is a plugin bundle (MCP servers, skills and hooks installed as one unit, such as
`exa@claude-plugins-official`) or a standalone MCP server. Each entry names the harnesses that
should have it:

    {"name": "exa", "kind": "bundle", "source": "exa@claude-plugins-official",
     "harnesses": ["claude-code", "cursor"]}
    {"name": "docs", "kind": "mcp", "server": {"url": "https://..."}, "harnesses": ["cursor"]}

What each harness can take (references/workstation.md, and each harness reference's Plugins section):

- Claude Code: bundles, installed with `claude plugin install`. Standalone MCP servers are a gap:
  checking them means reading ~/.claude.json, which can hold tokens.
- Cursor: bundles by importing Claude Code's enabled plugins, and standalone MCP servers in
  ~/.cursor/mcp.json.
- Codex, opencode and Pi: a gap for now.

`check` only reads files; the agent installs and writes, as SKILL.md says.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from .personal import PersonalError, read_pointer

INSTALLS = Path("agents/installs.json")
KINDS = ("bundle", "mcp")
KEYS = {"name", "kind", "source", "marketplace", "server", "harnesses", "os"}
LABELS = {"claude-code": "Claude Code", "cursor": "Cursor", "codex": "Codex", "opencode": "opencode", "pi": "Pi"}
OSES = {"macos": "darwin", "linux": "linux"}
SOURCE = re.compile(r"^[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+$")
MARKETPLACE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class PluginsError(ValueError):
    pass


def check(home: Path) -> list:
    """(status, text) lines for the plugins list; none when there is no list to check."""
    try:
        pointer = read_pointer(home)
    except PersonalError:
        return []
    if not pointer.repository:
        return []
    path = pointer.clone / INSTALLS
    try:
        entries = load(path)
    except PluginsError as exc:
        return [("FAIL", str(exc))]
    if not entries:
        return []
    claude = _claude_plugins(home)
    lines = []
    for entry in entries:
        name, kind = entry["name"], entry["kind"]
        tag = f"{name} ({kind})"
        oses = entry.get("os")
        if oses and not any(OSES[o] == _platform() for o in oses):
            lines.append(("n/a", f"{name}: for {', '.join(oses)} only"))
            continue
        for harness in entry["harnesses"]:
            label = LABELS[harness]
            if harness == "claude-code":
                lines.append(_claude_code(home, tag, entry, claude))
            elif harness == "cursor":
                lines.append(_cursor(home, tag, entry, claude))
            else:
                lines.append(("gap", f"{label}: {tag} is listed, but set-up-machine can't deliver plugins to "
                                     f"{label} yet"))
    for source in sorted(s for s, on in claude.items() if on):
        if not any(e["kind"] == "bundle" and e["source"] == source for e in entries):
            lines.append(("extra", f"Claude Code: {source} is enabled but not in the plugins list; "
                                   "Cursor imports it too"))
    return lines


def load(path: Path) -> list:
    """The `plugins` entries of an installs.json, checked; [] when the file or the list is absent."""
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise PluginsError(f"{path} isn't valid JSON: {exc}") from None
    entries = data.get("plugins", []) if isinstance(data, dict) else None
    if not isinstance(entries, list):
        raise PluginsError(f"{path}: `plugins` must be a list")
    seen = set()
    for i, entry in enumerate(entries):
        where = f"{path}: plugins[{i}]"
        if not isinstance(entry, dict):
            raise PluginsError(f"{where} must be an object")
        for key in entry:
            if key not in KEYS:
                raise PluginsError(f"{where}: unknown key {key!r}")
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            raise PluginsError(f"{where}: name is required")
        if name in seen:
            raise PluginsError(f"{where}: name {name!r} is used twice")
        seen.add(name)
        kind = entry.get("kind")
        if kind not in KINDS:
            raise PluginsError(f"{where}: kind must be bundle or mcp")
        if kind == "bundle":
            if not isinstance(entry.get("source"), str) or not SOURCE.match(entry["source"]):
                raise PluginsError(f"{where}: source must be <plugin>@<marketplace>")
            if "server" in entry:
                raise PluginsError(f"{where}: a bundle takes no server")
            market = entry.get("marketplace")
            if market is not None and (not isinstance(market, str) or not MARKETPLACE.match(market)):
                raise PluginsError(f"{where}: marketplace must be <owner>/<repo>")
        else:
            server = entry.get("server")
            if not isinstance(server, dict) or not (isinstance(server.get("url"), str)
                                                    or isinstance(server.get("command"), str)):
                raise PluginsError(f"{where}: server needs url or command")
            if "source" in entry or "marketplace" in entry:
                raise PluginsError(f"{where}: an mcp entry takes server, not source or marketplace")
        harnesses = entry.get("harnesses")
        if not isinstance(harnesses, list) or not harnesses:
            raise PluginsError(f"{where}: harnesses can't be empty")
        for h in harnesses:
            if h not in LABELS:
                raise PluginsError(f"{where}: unknown harness {h!r}")
        oses = entry.get("os")
        if oses is not None and (not isinstance(oses, list) or any(o not in OSES for o in oses)):
            raise PluginsError(f"{where}: os takes macos and linux")
    return entries


def cursor_server_name(source: str, server: str) -> str:
    """The name Cursor gives an MCP server of a Claude Code plugin it imports."""
    return f"plugin-{source.split('@', 1)[0]}-{server}"


def _claude_code(home: Path, tag: str, entry: dict, claude: dict):
    if not (home / ".claude").is_dir():
        return ("n/a", f"Claude Code: {tag} isn't checked; Claude Code is not set up here")
    if entry["kind"] == "mcp":
        return ("gap", f"Claude Code: {tag} is listed, but set-up-machine can't check a standalone MCP server "
                       "there yet; use a bundle")
    source = entry["source"]
    if source not in claude:
        return ("FAIL", f"Claude Code: {tag} {source} isn't installed")
    if not claude[source]:
        return ("FAIL", f"Claude Code: {tag} {source} isn't enabled in ~/.claude/settings.json")
    return ("ok", f"Claude Code: {tag} {source} is installed and enabled")


def _cursor(home: Path, tag: str, entry: dict, claude: dict):
    folder = home / ".cursor"
    if not folder.is_dir():
        return ("n/a", f"Cursor: {tag} isn't checked; Cursor is not set up here")
    if entry["kind"] == "bundle":
        source = entry["source"]
        if not claude.get(source):
            return ("FAIL", f"Cursor: {tag} needs {source} installed and enabled in Claude Code, since Cursor "
                            "imports bundles only from Claude Code")
        names = [cursor_server_name(source, s) for s in _bundle_servers(home, source)]
        how = f"as {', '.join(names)}" if names else "(skills only; no MCP server)"
        return ("ok", f"Cursor: {tag} is imported from Claude Code {how}")
    path = folder / "mcp.json"
    try:
        servers = json.loads(path.read_text()).get("mcpServers", {}) if path.is_file() else {}
    except (OSError, ValueError, AttributeError):
        return ("FAIL", f"Cursor: {tag} can't be checked; {path} isn't valid JSON")
    if entry["name"] not in servers:
        return ("FAIL", f"Cursor: {tag} has no entry in {path}")
    if servers[entry["name"]] != entry["server"]:
        return ("FAIL", f"Cursor: {tag} entry in {path} differs from installs.json")
    return ("ok", f"Cursor: {tag} is in {path}")


def _claude_plugins(home: Path) -> dict:
    """Each plugin Claude Code installed, as `<plugin>@<marketplace>` -> whether it is enabled."""
    try:
        installed = json.loads((home / ".claude/plugins/installed_plugins.json").read_text()).get("plugins", {})
    except (OSError, ValueError, AttributeError):
        installed = {}
    try:
        enabled = json.loads((home / ".claude/settings.json").read_text()).get("enabledPlugins", {})
    except (OSError, ValueError, AttributeError):
        enabled = {}
    return {source: enabled.get(source) is True for source in installed}


def _bundle_servers(home: Path, source: str) -> list:
    """The MCP server names a Claude Code plugin declares, from its install folder's mcp.json or .mcp.json."""
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


def _platform() -> str:
    return "darwin" if sys.platform == "darwin" else "linux" if sys.platform.startswith("linux") else sys.platform
