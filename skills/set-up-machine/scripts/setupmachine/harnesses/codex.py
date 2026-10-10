"""Codex plugin adapter: validate, check and propose. It never reads credential stores or writes."""
from __future__ import annotations

import copy
import json
import os
import re
import subprocess
from pathlib import Path

from ..codex_config import parse, ConfigError
from . import policy
from .errors import PluginsError

PluginError = PluginsError


def validate(entry: dict, where: str):
    policy.validate(entry, where)


def check(ctx, tag: str, entry: dict) -> list:
    state = getattr(ctx, "codex_state", None)
    if state is None:
        state = ctx.codex_state = Codex(ctx.codex_home, ctx.codex_program)
    return state.check(tag, entry, ctx.rules)


def propose(text: str, entry: dict, rules=()) -> str:
    """A reviewed policy edit that preserves every undeclared key and comment.

    Refuse unusual TOML forms rather than rewrite an entire settings file.
    Never changes plugin enablement or starts an installer.
    """
    chosen = policy.effective(entry, rules)
    shaped = {**entry, "mcp_policy": chosen} if chosen else entry
    validate(shaped, "plugin")
    old = parse(text)
    expected = copy.deepcopy(old)
    for parts, _ in _targets(shaped, chosen):
        node = old
        for part in parts:
            if part not in node:
                break
            node = node[part]
            if not isinstance(node, dict):
                raise PluginError("owned TOML table has an unexpected shape; preserve it for guided review")
    edits = []
    for parts, values in _targets(shaped, chosen):
        for table, key, value in _leaves(parts, values):
            current = _get(old, table)
            if current.get(key) == value:
                continue
            if key in ("disabled_tools", "enabled_tools") and key in current and not _tool_list(current[key]):
                raise PluginError("owned tool list has an unexpected shape; preserve it for guided review")
            if key == "disabled_tools" and key in current:
                value = sorted(set(current[key]) | set(value))
            if key == "enabled_tools" and key in current:
                value = [item for item in value if item in current[key]]
            edits.append((table, key, value))
            node = expected
            for part in table:
                if part in node and not isinstance(node[part], dict):
                    raise PluginError("owned TOML table has an unexpected shape; use a guided edit")
                node = node.setdefault(part, {})
            node[key] = value
    if not edits:
        return text
    if '"""' in text or "'''" in text:
        raise PluginError("multiline TOML requires a guided edit; preserve the file")
    lines = text.splitlines(keepends=True)
    for table, key, value in edits:
        starts = []
        for i, line in enumerate(lines):
            if line.lstrip().startswith("["):
                try:
                    heading = parse(line + "__setup_probe__ = true\n")
                    if _get(heading, table).get("__setup_probe__") is True:
                        starts.append(i)
                except ConfigError:
                    raise PluginError("unfamiliar TOML heading requires a guided edit") from None
        newline = "\r\n" if "\r\n" in text else "\n"
        rendered = json.dumps(value) if not isinstance(value, bool) else str(value).lower()
        assignment = f"{key} = {rendered}{newline}"
        if not starts:
            lines.append(newline + "[" + ".".join(json.dumps(x) for x in table) + "]" + newline + assignment)
            lines = "".join(lines).splitlines(keepends=True)
            continue
        if len(starts) != 1:
            raise PluginError("duplicate TOML heading requires a guided edit")
        start = starts[0] + 1
        end = next((i for i in range(start, len(lines)) if lines[i].lstrip().startswith("[")), len(lines))
        found = [i for i in range(start, end) if re.match(rf"\s*{re.escape(key)}\s*=", lines[i])]
        if key in _get(old, table) and len(found) != 1:
            raise PluginError("unfamiliar TOML assignment requires a guided edit")
        if found:
            i = found[0]
            try:
                parse(lines[i])
            except ConfigError:
                raise PluginError("multiline TOML value requires a guided edit") from None
            comment = _trailing_comment(lines[i])
            lines[i] = assignment.rstrip("\r\n") + (" " + comment if comment else "") + newline
        else:
            lines.insert(end, assignment)
    result = "".join(lines)
    if parse(result) != expected:
        raise PluginError("proposal did not preserve unrelated configuration; use a guided edit")
    return result


class Codex:
    def __init__(self, folder: Path, program: str | None = None):
        self.folder, self.program = folder, program
        self.error, self.auth = None, None
        try:
            path = folder / "config.toml"
            self.config = parse(path.read_text()) if path.exists() else {}
        except (ConfigError, OSError, UnicodeError):
            self.config = {}
            self.error = "cannot inspect Codex config.toml; preserve it for guided review"

    def check(self, tag: str, entry: dict, rules=()):
        if not self.folder.is_dir() and not self.program:
            return [("n/a", f"Codex: {tag} is not checked; Codex is not set up here")]
        if self.error:
            return [("FAIL", f"Codex: {tag}: {self.error}")]
        chosen = policy.effective(entry, rules)
        shaped = {**entry, "mcp_policy": chosen} if chosen else entry
        out = []
        if entry["kind"] == "bundle":
            source = entry["source"]
            plugin, market = source.split("@", 1)
            enabled = _get(self.config, ("plugins", source)).get("enabled")
            cache = self.folder / "plugins/cache" / market / plugin
            patterns = ("*/.codex-plugin/plugin.json", "*/.claude-plugin/plugin.json", "*/plugin.json")
            manifests = [path for pattern in patterns for path in cache.glob(pattern)]
            valid = False
            for path in manifests:
                try:
                    valid |= json.loads(path.read_text()).get("name") == plugin
                except (OSError, ValueError, AttributeError):
                    pass
            if enabled is not True or not valid:
                return [("FAIL", f"Codex: {tag} {source} is missing, disabled or has no valid installed manifest")]
            out.append(("ok", f"Codex: {tag} {source} is installed and enabled; server sign-in is checked separately"))
        for parts, wanted in _targets(shaped, chosen):
            for table, key, value in _leaves(parts, wanted):
                have = _get(self.config, table).get(key)
                if have == value:
                    continue
                stricter = ((key == "disabled_tools" and _tool_list(have) and set(value) <= set(have))
                            or (key == "enabled_tools" and _tool_list(have) and set(have) <= set(value)))
                if stricter:
                    out.append(("stricter", f"Codex: {tag}: {key} is stricter than declared; kept"))
                else:
                    out.append(("FAIL", f"Codex: {tag}: declared {key} is missing or differs"))
            if wanted and all(_get(self.config, table).get(key) == value for table, key, value in _leaves(parts, wanted)):
                out.append(("ok", f"Codex: {tag}: declared MCP configuration and tool policy match"))
        if chosen.get("require_oauth"):
            status = self.auth_status(entry["name"])
            if status == "o_auth":
                out.append(("ok", f"Codex: {tag}: {entry['name']} OAuth is connected"))
            else:
                out.append(("gap", f"Codex: {tag}: {entry['name']} OAuth is {status}; the user must run "
                                   f"codex mcp login {entry['name']}; keep the server disabled until connected"))
        return out

    def auth_status(self, server):
        if not self.program:
            return "unverified (no CLI supplied)"
        if self.auth is None:
            try:
                result = subprocess.run([self.program, "mcp", "list", "--json"], capture_output=True, text=True,
                                        timeout=20, cwd=self.folder,
                                        env={**os.environ, "CODEX_HOME": str(self.folder)})
                rows = json.loads(result.stdout) if result.returncode == 0 else []
                self.auth = {row["name"]: row.get("auth_status") for row in rows} if isinstance(rows, list) else {}
            except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
                self.auth = {}
        return self.auth.get(server, "unverified")


def _targets(entry: dict, chosen: dict):
    values = policy.codex_values(chosen)
    if entry["kind"] == "mcp":
        merged = dict(entry["server"])
        merged.update(values)
        return [(("mcp_servers", entry["name"]), merged)]
    if not values:
        return []
    return [(("plugins", entry["source"], "mcp_servers", entry["name"]), values)]


def _get(config: dict, parts):
    for part in parts:
        if not isinstance(config, dict):
            return {}
        config = config.get(part, {})
    return config if isinstance(config, dict) else {}


def _leaves(parts, values):
    for key, value in values.items():
        if isinstance(value, dict):
            yield from _leaves((*parts, key), value)
        else:
            yield parts, key, value


def _tool_list(value):
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _trailing_comment(line):
    quote, escaped = None, False
    for i, char in enumerate(line):
        if escaped:
            escaped = False
        elif quote == '"' and char == "\\":
            escaped = True
        elif quote and char == quote:
            quote = None
        elif not quote and char in ('"', "'"):
            quote = char
        elif not quote and char == "#":
            return line[i:].rstrip("\r\n")
    return None
