"""The plugins setup area: the `plugins` list in the workstation repo's agents/installs.json.

A plugin is a plugin bundle (MCP servers, skills and hooks installed as one unit, such as
`exa@claude-plugins-official`) or a standalone MCP server. Each entry names the harnesses that
should have it:

    {"name": "exa", "kind": "bundle", "source": "exa@claude-plugins-official",
     "harnesses": ["claude-code", "cursor"],
     "mcp_policy": {"require_oauth": true, "approval_mode": "prompt"}}
    {"name": "docs", "kind": "mcp", "server": {"url": "https://..."}, "harnesses": ["cursor"]}
    {"name": "web", "kind": "bundle", "source": "npm:pi-web-access@0.38.0", "harnesses": ["pi"]}

`mcp_policy` is optional and harness-neutral. Its fields are `enabled_tools`, `disabled_tools`,
`approval_mode` and `require_oauth`. Tool exclusions come from the rule table and
`agents/permissions.json`; each adapter derives its list from those rows.

What each harness can take is in references/workstation.md and that harness's Plugins section.
One adapter per harness lives in `harnesses/<harness>.py` and exposes validate, check and propose.
This module dispatches through ADAPTERS. opencode has no adapter yet.

`check` inspects files and read-only CLI metadata; the agent installs and writes, as SKILL.md says.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from . import rules as rule_table
from .harnesses import claude, codex, cursor, pi
from .harnesses import policy
from .harnesses.errors import PluginsError
from .personal import PersonalError, permissions, read_pointer

INSTALLS = Path("agents/installs.json")
KINDS = ("bundle", "mcp")
KEYS = {"name", "kind", "source", "marketplace", "server", "harnesses", "os", "mcp_policy"}
LABELS = {"claude-code": "Claude Code", "cursor": "Cursor", "codex": "Codex", "opencode": "opencode", "pi": "Pi"}
OSES = {"macos": "darwin", "linux": "linux"}
SOURCE = re.compile(r"^[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+$")
MARKETPLACE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")

ADAPTERS = {
    "claude-code": claude,
    "cursor": cursor,
    "pi": pi,
    "codex": codex,
}


class Context:
    """What one check run shares across adapters."""

    def __init__(self, home: Path, pi_dir: Path, codex_home: Path, codex_program, rules: list):
        self.home = home
        self.pi_dir = pi_dir
        self.codex_home = codex_home
        self.codex_program = codex_program
        self.rules = rules
        self.claude_plugins = claude.installed(home)


def check(home: Path, pi_dir: Path | None = None, codex_home: Path | None = None, codex_program: str | None = None,
          rules: list | None = None) -> list:
    """(status, text) lines for the plugins list; none when there is no list to check.

    pi_dir is Pi's agent folder, as verify.py resolves it; home/.pi/agent when not given.
    rules are the rule table plus personal permissions. When omitted, this loads both.
    """
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
    if rules is None:
        rules = _rules(home)
    ctx = Context(home, pi_dir or home / ".pi/agent", codex_home or home / ".codex", codex_program, rules)
    lines = []
    for entry in entries:
        name, kind = entry["name"], entry["kind"]
        tag = f"{name} ({kind})"
        oses = entry.get("os")
        if oses and not any(OSES[item] == _platform() for item in oses):
            lines.append(("n/a", f"{name}: for {', '.join(oses)} only"))
            continue
        for harness in entry["harnesses"]:
            adapter = ADAPTERS.get(harness)
            if adapter is None:
                label = LABELS[harness]
                lines.append(("gap", f"{label}: {tag} is listed, but set-up-machine can't deliver plugins to "
                                     f"{label} yet"))
                continue
            lines.extend(adapter.check(ctx, tag, entry))
    for source in sorted(item for item, on in ctx.claude_plugins.items() if on):
        if not any(entry["kind"] == "bundle" and entry["source"] == source for entry in entries):
            lines.append(("extra", f"Claude Code: {source} is enabled but not in the plugins list; "
                                   "Cursor imports it too"))
    lines.extend(pi.extras(ctx, entries))
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
    pi_seen = {}
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
        harnesses = entry.get("harnesses")
        if not isinstance(harnesses, list) or not harnesses:
            raise PluginsError(f"{where}: harnesses can't be empty")
        for harness in harnesses:
            if harness not in LABELS:
                raise PluginsError(f"{where}: unknown harness {harness!r}")
        policy.validate(entry, where)
        if kind == "bundle":
            if "server" in entry:
                raise PluginsError(f"{where}: a bundle takes no server")
            source = entry.get("source") if isinstance(entry.get("source"), str) else ""
            pi.validate(entry, where, pi_seen, i)
            if harnesses != ["pi"]:
                if not SOURCE.match(source):
                    raise PluginsError(f"{where}: source must be <plugin>@<marketplace>")
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
            pi.validate(entry, where, pi_seen, i)
        for harness in harnesses:
            adapter = ADAPTERS.get(harness)
            if adapter is not None and adapter is not pi:
                adapter.validate(entry, where)
        oses = entry.get("os")
        if oses is not None and (not isinstance(oses, list) or any(item not in OSES for item in oses)):
            raise PluginsError(f"{where}: os takes macos and linux")
    return entries


def _rules(home: Path) -> list:
    """The rule table plus personal permissions. A broken personal file contributes no rows."""
    try:
        table = rule_table.load()
    except rule_table.RuleTableError:
        return []
    try:
        return table + permissions(home, table)
    except rule_table.RuleTableError:
        return table


def _platform() -> str:
    return "darwin" if sys.platform == "darwin" else "linux" if sys.platform.startswith("linux") else sys.platform
