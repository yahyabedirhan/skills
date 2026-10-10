"""The neutral `mcp_policy` object on an installs.json plugin entry.

Fields are `enabled_tools`, `disabled_tools`, `approval_mode` and `require_oauth`.
Tool exclusions come from the rule table and `agents/permissions.json`. This module
derives those lists and unions them with anything the entry still declares.
"""
from __future__ import annotations

import re

from .. import rules as rule_table
from .errors import PluginsError

FIELDS = {"enabled_tools", "disabled_tools", "approval_mode", "require_oauth"}
MODES = {"auto", "prompt", "writes", "approve"}
NAME = re.compile(r"^[A-Za-z0-9_.-]+$")
LITERAL = re.compile(r"^\^([A-Za-z0-9_.-]+)\$$")


def validate(entry: dict, where: str):
    """Refuse an `mcp_policy` whose fields are not the four neutral ones."""
    if "mcp_policy" not in entry:
        return
    policy = entry["mcp_policy"]
    if not isinstance(policy, dict):
        raise PluginsError(f"{where}: mcp_policy must be an object")
    unknown = set(policy) - FIELDS
    if unknown:
        raise PluginsError(f"{where}: unknown mcp_policy field {sorted(unknown)[0]!r}")
    for key in ("enabled_tools", "disabled_tools"):
        value = policy.get(key)
        if value is None:
            continue
        if not isinstance(value, list) or any(not isinstance(x, str) or not NAME.fullmatch(x) for x in value):
            raise PluginsError(f"{where}: {key} must be a list of tool names")
    mode = policy.get("approval_mode")
    if "approval_mode" in policy and (not isinstance(mode, str) or mode not in MODES):
        raise PluginsError(f"{where}: approval_mode must be auto, prompt, writes or approve")
    if "require_oauth" in policy and not isinstance(policy["require_oauth"], bool):
        raise PluginsError(f"{where}: require_oauth must be a boolean")


def effective(entry: dict, rules) -> dict:
    """The policy adapters write. Permission rows supply tool names; the entry fills the rest.

    A deny row adds to `disabled_tools`. An allow row adds to `enabled_tools`, except a tool
    a deny row already names. `approval_mode` and `require_oauth` come only from the entry.
    """
    declared = entry.get("mcp_policy") if isinstance(entry.get("mcp_policy"), dict) else {}
    policy = {key: (list(value) if isinstance(value, list) else value) for key, value in declared.items()}
    disabled = set(policy.get("disabled_tools") or [])
    disabled |= set(tools_for(rules, entry, "deny"))
    enabled = set(policy.get("enabled_tools") or [])
    enabled |= set(tools_for(rules, entry, "allow"))
    enabled -= disabled
    if disabled or "disabled_tools" in declared:
        policy["disabled_tools"] = sorted(disabled)
    if enabled or "enabled_tools" in declared:
        policy["enabled_tools"] = sorted(enabled)
    return policy


def tools_for(rules, entry: dict, level: str) -> list:
    """Tool names a `level` row assigns to this entry's server, in sorted order.

    A row matches when its server regex matches the entry's name. A tool name comes from a
    literal `^name$` regex, or from a `mcp__<server>__<tool>` sample the row covers.
    """
    server = entry.get("name")
    if not isinstance(server, str) or not rules:
        return []
    found = set()
    for rule in rules:
        if rule.level != level or rule.kind != "mcp-tool":
            continue
        if not re.search(rule.server, server, re.I):
            continue
        literal = LITERAL.fullmatch(rule.tool)
        if literal:
            found.add(literal.group(1))
        for sample in rule.covers:
            parts = rule_table.split_mcp_name(sample)
            if not parts or not re.search(rule.server, parts[0], re.I):
                continue
            if parts[0].lower() == server.lower() and re.search(rule.tool, parts[1], re.I):
                found.add(parts[1])
    return sorted(found)


def codex_values(policy: dict) -> dict:
    """The policy keys Codex stores. `require_oauth` is an audit flag, not a setting."""
    values = {}
    if "enabled_tools" in policy:
        values["enabled_tools"] = policy["enabled_tools"]
    if "disabled_tools" in policy:
        values["disabled_tools"] = policy["disabled_tools"]
    if "approval_mode" in policy:
        values["default_tools_approval_mode"] = policy["approval_mode"]
    return values
