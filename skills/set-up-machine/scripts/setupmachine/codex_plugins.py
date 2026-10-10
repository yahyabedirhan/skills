"""Codex plugin inspection and a pure TOML proposal. Never reads credential stores."""
from __future__ import annotations

import copy
import json
import os
import re
import subprocess
from pathlib import Path

from .codex_config import parse, ConfigError

POLICY_KEYS = {"enabled", "enabled_tools", "disabled_tools", "default_tools_approval_mode", "tools", "require_oauth"}
MODES = {"auto", "prompt", "writes", "approve"}
NAME = re.compile(r"^[A-Za-z0-9_.-]+$")


class PluginError(ValueError):
    pass


def validate(entry: dict, where: str):
    policies = entry.get("codex_mcp", {})
    if "codex_mcp" in entry and ("codex" not in entry["harnesses"] or entry["kind"] != "bundle"):
        raise PluginError(f"{where}: codex_mcp requires a bundle that names codex")
    if not isinstance(policies, dict):
        raise PluginError(f"{where}: codex_mcp must be an object")
    for name, policy in policies.items():
        if not NAME.fullmatch(name) or not isinstance(policy, dict) or set(policy) - POLICY_KEYS:
            raise PluginError(f"{where}: invalid Codex MCP server or policy key")
        for key, value in policy.items():
            if key in ("enabled", "require_oauth") and not isinstance(value, bool):
                raise PluginError(f"{where}: {key} must be a boolean")
            if key in ("enabled_tools", "disabled_tools") and (not isinstance(value, list) or any(not isinstance(x, str) or not NAME.fullmatch(x) for x in value)):
                raise PluginError(f"{where}: {key} must be a list of tool names")
            if key == "default_tools_approval_mode" and (not isinstance(value, str) or value not in MODES):
                raise PluginError(f"{where}: unsupported Codex approval mode")
            if key == "tools":
                if not isinstance(value, dict):
                    raise PluginError(f"{where}: tools must be an object")
                for tool, settings in value.items():
                    if not NAME.fullmatch(tool) or not isinstance(settings, dict) or set(settings) != {"approval_mode"} or not isinstance(settings["approval_mode"], str) or settings["approval_mode"] not in MODES:
                        raise PluginError(f"{where}: tools takes tool names with approval_mode only")


def targets(entry: dict):
    if entry["kind"] == "mcp":
        return [(('mcp_servers', entry['name']), entry['server'])]
    return [(('plugins', entry['source'], 'mcp_servers', name), {k: v for k, v in policy.items() if k != 'require_oauth'})
            for name, policy in entry.get('codex_mcp', {}).items()]


def get(config: dict, parts):
    for part in parts:
        if not isinstance(config, dict):
            return {}
        config = config.get(part, {})
    return config if isinstance(config, dict) else {}


def leaves(parts, values):
    for key, value in values.items():
        if isinstance(value, dict):
            yield from leaves((*parts, key), value)
        else:
            yield parts, key, value


def propose(text: str, entry: dict) -> str:
    """Return a reviewed policy edit that preserves every undeclared key and comment.

    Refuse unusual TOML forms rather than rewrite an entire settings file.
    Never changes plugin enablement or starts an installer.
    """
    validate(entry, 'plugin')
    old = parse(text)
    expected = copy.deepcopy(old)
    for parts, _ in targets(entry):
        node = old
        for part in parts:
            if part not in node:
                break
            node = node[part]
            if not isinstance(node, dict):
                raise PluginError('owned TOML table has an unexpected shape; preserve it for guided review')
    edits = []
    for parts, values in targets(entry):
        for table, key, value in leaves(parts, values):
            current = get(old, table)
            if current.get(key) == value:
                continue
            if key in ('disabled_tools', 'enabled_tools') and key in current and not tool_list(current[key]):
                raise PluginError('owned tool list has an unexpected shape; preserve it for guided review')
            if key == 'disabled_tools' and key in current:
                value = sorted(set(current[key]) | set(value))
            if key == 'enabled_tools' and key in current:
                value = [x for x in value if x in current[key]]
            edits.append((table, key, value))
            node = expected
            for part in table:
                if part in node and not isinstance(node[part], dict):
                    raise PluginError('owned TOML table has an unexpected shape; use a guided edit')
                node = node.setdefault(part, {})
            node[key] = value
    if not edits:
        return text
    if '"""' in text or "'''" in text:
        raise PluginError('multiline TOML requires a guided edit; preserve the file')
    lines = text.splitlines(keepends=True)
    for table, key, value in edits:
        # Parse each table heading to support both quoted and bare components.
        starts = []
        for i, line in enumerate(lines):
            if line.lstrip().startswith('['):
                try:
                    heading = parse(line + '__setup_probe__ = true\n')
                    if get(heading, table).get('__setup_probe__') is True:
                        starts.append(i)
                except ConfigError:
                    raise PluginError('unfamiliar TOML heading requires a guided edit') from None
        newline = '\r\n' if '\r\n' in text else '\n'
        rendered = json.dumps(value) if not isinstance(value, bool) else str(value).lower()
        assignment = f'{key} = {rendered}{newline}'
        if not starts:
            lines.append(newline + '[' + '.'.join(json.dumps(x) for x in table) + ']' + newline + assignment)
            # Split the appended heading so the next edit finds it.
            lines = ''.join(lines).splitlines(keepends=True)
            continue
        if len(starts) != 1:
            raise PluginError('duplicate TOML heading requires a guided edit')
        start = starts[0] + 1
        end = next((i for i in range(start, len(lines)) if lines[i].lstrip().startswith('[')), len(lines))
        found = [i for i in range(start, end) if re.match(rf'\s*{re.escape(key)}\s*=', lines[i])]
        if key in get(old, table) and len(found) != 1:
            raise PluginError('unfamiliar TOML assignment requires a guided edit')
        if found:
            i = found[0]
            # A multi-line value cannot be replaced safely by one line.
            try:
                parse(lines[i])
            except ConfigError:
                raise PluginError('multiline TOML value requires a guided edit') from None
            comment = trailing_comment(lines[i])
            lines[i] = assignment.rstrip('\r\n') + (' ' + comment if comment else '') + newline
        else:
            lines.insert(end, assignment)
    result = ''.join(lines)
    if parse(result) != expected:
        raise PluginError('proposal did not preserve unrelated configuration; use a guided edit')
    return result


def tool_list(value):
    return isinstance(value, list) and all(isinstance(x, str) for x in value)


def trailing_comment(line):
    quote, escaped = None, False
    for i, char in enumerate(line):
        if escaped:
            escaped = False
        elif quote == '"' and char == '\\':
            escaped = True
        elif quote and char == quote:
            quote = None
        elif not quote and char in ('"', "'"):
            quote = char
        elif not quote and char == '#':
            return line[i:].rstrip('\r\n')
    return None


class Codex:
    def __init__(self, folder: Path, program: str | None = None):
        self.folder, self.program = folder, program
        self.error, self.auth = None, None
        try:
            path = folder / 'config.toml'
            self.config = parse(path.read_text()) if path.exists() else {}
        except (ConfigError, OSError, UnicodeError):
            self.config = {}
            self.error = 'cannot inspect Codex config.toml; preserve it for guided review'

    def check(self, tag: str, entry: dict):
        if not self.folder.is_dir() and not self.program:
            return [('n/a', f"Codex: {tag} is not checked; Codex is not set up here")]
        if self.error:
            return [('FAIL', f'Codex: {tag}: {self.error}')]
        out = []
        if entry['kind'] == 'bundle':
            source = entry['source']
            plugin, market = source.split('@', 1)
            enabled = get(self.config, ('plugins', source)).get('enabled')
            cache = self.folder / 'plugins/cache' / market / plugin
            manifests = [p for pattern in ('*/.codex-plugin/plugin.json', '*/.claude-plugin/plugin.json', '*/plugin.json') for p in cache.glob(pattern)]
            valid = False
            for path in manifests:
                try:
                    valid |= json.loads(path.read_text()).get('name') == plugin
                except (OSError, ValueError, AttributeError):
                    pass
            if enabled is not True or not valid:
                return [('FAIL', f'Codex: {tag} {source} is missing, disabled or has no valid installed manifest')]
            out.append(('ok', f'Codex: {tag} {source} is installed and enabled; server sign-in is checked separately'))
        for parts, wanted in targets(entry):
            actual = get(self.config, parts)
            for table, key, value in leaves(parts, wanted):
                have = get(self.config, table).get(key)
                if have == value:
                    continue
                stricter = (key == 'disabled_tools' and tool_list(have) and set(value) <= set(have)) or (key == 'enabled_tools' and tool_list(have) and set(have) <= set(value))
                out.append(('stricter' if stricter else 'FAIL', f'Codex: {tag}: {key} is stricter than declared; kept' if stricter else f'Codex: {tag}: declared {key} is missing or differs'))
            if actual and all(get(self.config, t).get(k) == v for t, k, v in leaves(parts, wanted)):
                out.append(('ok', f'Codex: {tag}: declared MCP configuration and tool policy match'))
        for server, policy in entry.get('codex_mcp', {}).items():
            if not policy.get('require_oauth'):
                continue
            status = self.auth_status(server)
            if status == 'o_auth':
                out.append(('ok', f'Codex: {tag}: {server} OAuth is connected'))
            else:
                out.append(('gap', f'Codex: {tag}: {server} OAuth is {status}; the user must run codex mcp login {server}; keep the server disabled until connected'))
        return out

    def auth_status(self, server):
        if not self.program:
            return 'unverified (no CLI supplied)'
        if self.auth is None:
            try:
                result = subprocess.run([self.program, 'mcp', 'list', '--json'], capture_output=True, text=True, timeout=20, cwd=self.folder, env={**os.environ, 'CODEX_HOME': str(self.folder)})
                rows = json.loads(result.stdout) if result.returncode == 0 else []
                self.auth = {x['name']: x.get('auth_status') for x in rows} if isinstance(rows, list) else {}
            except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
                self.auth = {}
        return self.auth.get(server, 'unverified')
