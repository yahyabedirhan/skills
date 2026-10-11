"""Codex's harness setup. It audits Codex, translates one hook payload, and adapts one plugin entry.

It uses the operations Cursor established: `id`, `label`, `present`, `audit`, `read`, `write`,
`validate`, `check`, and `propose`. `audit` returns `(channel, status, text)` for the hook
wiring, the execpolicy comparison, and the declared defaults. The printed words stay
`hook`, `codex`, `config`, and `plugin`. Instructions Codex cannot take yet stay a gap
on the shared checker.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shlex
import subprocess
from pathlib import Path

from .. import codex_config
from ..codex_config import ConfigError, parse
from ..harnesses import policy
from ..harnesses.errors import PluginsError
from ..hook import PATCH_FILE, ToolCall, command_script, write_claude_code

id = "codex"
label = "Codex"
HOME_DIR = Path(".codex")
DECISION = {"forbidden": "deny", "prompt": "ask", "allow": "allow-and-report"}
SHELL_SYNTAX = set(";&|<>$`()\n")
STRICTNESS = {"allow-and-report": 0, "ask": 1, "deny": 2}

PluginError = PluginsError


def present(home: Path) -> bool:
    """Whether Codex is set up on this machine: `~/.codex` exists."""
    return (home / HOME_DIR).is_dir()


def audit(home: Path, codex_home: Path | None = None, codex: str | None = None,
          rules: list | None = None, no_codex: bool = False) -> list:
    """`(channel, status, text)` for Codex's wiring, execpolicy, and defaults.

    `codex` is the program path. `codex_home` is the resolved config home, including `CODEX_HOME`
    when the verifier honored it. `no_codex` skips the execpolicy lines. The config check still
    runs, and a missing program skips its parser probe.
    """
    folder = codex_home or (home / HOME_DIR)
    lines = [_wiring(home, folder)]
    if not no_codex:
        lines.extend(_execpolicy(rules or [], home, codex, folder))
    for status, text in codex_config.audit(home, folder, codex):
        lines.append(("config", status, text))
    return lines


def trust_hash(command: str, matcher: str = "*", timeout: int = 10) -> str:
    """The hash Codex records when a PreToolUse command hook is trusted in /hooks: sha256 over the
    canonical JSON of the hook's identity (codex-rs/hooks, discovery)."""
    identity = {
        "event_name": "pre_tool_use",
        "matcher": matcher,
        "hooks": [{"type": "command", "command": command, "timeout": timeout, "async": False}],
    }
    text = json.dumps(identity, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(text.encode()).hexdigest()


def check_codex(table: list, home: Path, codex: str, codex_home: Path | None = None) -> list:
    """(row, sample, Codex's decision as a level or "no match") for each plain command sample."""
    rules_dir = (codex_home or home / HOME_DIR) / "rules"
    files = sorted(rules_dir.glob("*.rules")) if rules_dir.is_dir() else []
    if not files:
        return []
    out = []
    for rule in table:
        if rule.kind != "command":
            continue
        for sample in rule.covers:
            if SHELL_SYNTAX & set(sample):
                continue  # a compound isn't one argv
            argv = [codex, "execpolicy", "check", "--resolve-host-executables"]
            for f in files:
                argv += ["--rules", str(f)]
            done = subprocess.run(argv + ["--", *shlex.split(sample)], capture_output=True, text=True, timeout=60)
            try:
                decision = json.loads(done.stdout or "{}").get("decision")
            except ValueError:
                decision = None
            out.append((rule, sample, DECISION.get(decision, "no match")))
    return out


def read(payload: dict) -> ToolCall:
    """Codex's PreToolUse input: `tool_name` is `Bash` for the shell tools (the command as
    the model wrote it, before Codex wraps it in `<shell> -lc`), `apply_patch` for file
    edits (`tool_input.command` holds the patch), or `mcp__<server>__<tool>`."""
    tool = payload.get("tool_name") if isinstance(payload.get("tool_name"), str) else ""
    tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
    command = tool_input.get("command")
    command = command if isinstance(command, str) else None
    files = ()
    if tool == "apply_patch":
        files = tuple((m.group(2), "write") for m in PATCH_FILE.finditer(command or ""))
        command = None
    return ToolCall(
        tool=tool,
        command=command,
        files=files,
        cwd=payload.get("cwd") if isinstance(payload.get("cwd"), str) else "",
        session=payload.get("session_id") if isinstance(payload.get("session_id"), str) else "",
        # Codex reports `bypassPermissions` when its approval policy is never. An automatic
        # reviewer doesn't show in the payload: references/codex.md names that gap.
        unattended="Codex with approval policy never" if payload.get("permission_mode") == "bypassPermissions" else "",
    )


def write(denials: list, asks=()) -> str:
    """Codex's hook answer: the same deny JSON Claude Code prints."""
    return write_claude_code(denials, asks)


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
            out.append(("ok", f"Codex: {tag} {source} is installed and enabled; declaration matches, readiness only; "
                               "latest release is unverified; server sign-in is checked separately"))
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


def _wiring(home: Path, folder: Path):
    """`(channel, status, text)` for Codex's pre-tool hook, including its trust hash."""
    if not folder.is_dir():
        return ("hook", "none", f"{label}: not set up here (no ~/{HOME_DIR})")
    path = folder / "hooks.json"
    config = folder / "config.toml"
    for g, h, matcher, command, timeout in _pre_tool_commands(_json(path) or {}):
        script = command_script(command, id, home)
        if not (script and matcher in ("*", "", None)):
            continue
        status, text = _script_line(path, script)
        if status != "wired":
            return ("hook", status, text)
        key = f"{path}:pre_tool_use:{g}:{h}"
        if _toml_trust(config, key) != trust_hash(command, matcher or "*", timeout):
            return ("hook", "FAIL", f"{label}: the hook in {path} is not trusted: config.toml needs "
                    f"[hooks.state.\"{key}\"] trusted_hash = \"{trust_hash(command, matcher or '*', timeout)}\"")
        return ("hook", status, text + ", trusted")
    return ("hook", "FAIL", f"{label}: no pre-tool hook for every tool in {path}")


def _execpolicy(table: list, home: Path, codex: str | None, folder: Path) -> list:
    if not codex:
        return [("codex", "skipped", "codex isn't on PATH; from a non-login shell, such as one without nvm loaded, pass --codex PATH")]
    checked = check_codex(table, home, codex, folder)
    if not checked:
        return [("codex", "skipped", "no rules files in the resolved Codex config home's rules folder")]
    lines = []
    for rule, sample, level in checked:
        want = "allow-and-report" if rule.level == "allow" else rule.level  # Codex has one allow decision
        shown = _decision(level)
        if level == want:
            lines.append(("codex", "same", f"{rule.id}: {sample} -> {shown}"))
        elif STRICTNESS.get(level, -1) > STRICTNESS[want]:
            lines.append(("codex", "stricter", f"{rule.id}: {sample} -> {shown}, the row is {rule.level}"))
        else:
            lines.append(("codex", "differs", f"{rule.id}: {sample} -> {shown}, the row is {rule.level}"))
    return lines


def _decision(level: str) -> str:
    return {v: k for k, v in DECISION.items()}.get(level, level)


def _json(path: Path):
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _pre_tool_commands(settings: dict) -> list:
    """(group index, handler index, matcher, command, timeout) for every PreToolUse command handler."""
    hooks = settings.get("hooks") if isinstance(settings.get("hooks"), dict) else {}
    groups = hooks.get("PreToolUse") if isinstance(hooks.get("PreToolUse"), list) else []
    out = []
    for g, group in enumerate(groups):
        handlers = group.get("hooks") if isinstance(group, dict) and isinstance(group.get("hooks"), list) else []
        for h, handler in enumerate(handlers):
            if isinstance(handler, dict) and isinstance(handler.get("command"), str):
                out.append((g, h, group.get("matcher"), handler["command"], handler.get("timeout", 10)))
    return out


def _script_line(where: Path, script: Path):
    if not script.is_file():
        return ("FAIL", f"{label}: {where} runs {script}, which doesn't exist")
    return ("wired", f"{label}: {where} -> {script}")


def _toml_trust(config: Path, key: str):
    try:
        lines = config.read_text().split("\n")
    except OSError:
        return None
    header = f"[hooks.state.{json.dumps(key)}]"
    for i, line in enumerate(lines):
        if line.strip() == header:
            for body in lines[i + 1:]:
                if body.lstrip().startswith("["):
                    break
                m = re.match(r'^\s*trusted_hash\s*=\s*"([^"]*)"', body)
                if m:
                    return m.group(1)
    return None
