"""Codex: its hook payload, and the check of each setup area , as references/codex/index.md describes.

Every path is under the Codex config home: `CODEX_HOME`, else `~/.codex`, which verify.py resolves once. Its `config.toml` holds memory, hook trust, the declared config and plugins. TOML checks need Python 3.11's tomllib; on an older Python they are a gap.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

from .. import claude_code
from ... import checks
from ...checks import (Cell, any_wired_problem, as_list, cell, declared_problems, dig, link_problem, na,
                      native_command_row, on_path, read_json, read_toml, skill_problems, wiring_problem)
from ...hook import PATCH_FILE, ToolCall

ID, LABEL = "codex", "Codex"
# The keys of the declared Codex config the sandbox column checks; the config column checks the rest.
SANDBOX_KEYS = ("sandbox_mode", "approval_policy", "approvals_reviewer")
NO_TOML = ("gap", "this Python has no tomllib (3.11+), so config.toml isn't checked")


def config_home(home: Path) -> Path:
    """The Codex config home. Only the real home honors CODEX_HOME; a fixture home uses its own."""
    custom = os.environ.get("CODEX_HOME") if home == Path.home().resolve() else None
    return (Path(custom) if custom else home / ".codex").expanduser().resolve()


def present(home: Path) -> bool:
    return config_home(home).is_dir() or on_path(home, "codex")


# --- the hook ------------------------------------------------------------------------------


def read(payload: dict) -> ToolCall:
    """Codex's PreToolUse input: `Bash` with the command as the model wrote it, `apply_patch` with the patch in `tool_input.command`, or `mcp__<server>__<tool>`."""
    tool = payload.get("tool_name") if isinstance(payload.get("tool_name"), str) else ""
    args = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
    command = args.get("command") if isinstance(args.get("command"), str) else None
    files = ()
    if tool == "apply_patch":
        files, command = tuple((m.group(2), "write") for m in PATCH_FILE.finditer(command or "")), None
    return ToolCall(
        tool=tool, command=command, files=files,
        cwd=payload.get("cwd") if isinstance(payload.get("cwd"), str) else "",
        session=payload.get("session_id") if isinstance(payload.get("session_id"), str) else "",
        # Codex reports bypassPermissions when its approval policy is never. A reviewer doesn't show.
        unattended="Codex with approval policy never" if payload.get("permission_mode") == "bypassPermissions" else "")


def write(denials: list, asks=()) -> str:
    return claude_code.write(denials, asks)


def trust_hash(command: str, matcher: str = "*", timeout: int = 10) -> str:
    """The `trusted_hash` Codex records for a PreToolUse hook: sha256 over its identity's canonical JSON."""
    identity = {"event_name": "pre_tool_use", "matcher": matcher,
                "hooks": [{"type": "command", "command": command, "timeout": timeout, "async": False}]}
    text = json.dumps(identity, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(text.encode()).hexdigest()


# --- the checks ----------------------------------------------------------------------------


def check_instructions(ctx, env=None) -> Cell:
    """`AGENTS.md` links to the shared file, no override file wins over it, and memories are off."""
    folder = ctx.codex_home
    problems = [link_problem(ctx, folder / "AGENTS.md")]
    override = folder / "AGENTS.override.md"
    if override.is_file() and override.read_text().strip():
        problems.append(("gap", f"{ctx.show(override)} is read instead of AGENTS.md"))
    config, problem = _toml(ctx, folder / "config.toml")
    problems.append(problem)
    if config is not None and dig(config, "features", "memories") is not False:
        problems.append(("FAIL", "memories isn't false in [features] of config.toml"))
    if ctx.setup.file(ID, "instructions", env):
        problems.append(("gap", "setup/harnesses.json names instructions for Codex, which has no place for them"))
    return cell([p for p in problems if p])


def check_guardrails(ctx) -> Cell:
    """A match-all PreToolUse group runs the hook and is trusted; personal command rows are in the rules file."""
    path = ctx.codex_home / "hooks.json"
    groups = as_list(dig(read_json(path) or {}, "hooks", "PreToolUse"))
    handlers = [(g, h, group.get("matcher"), handler.get("command"), handler.get("timeout", 10))
                for g, group in enumerate(groups) if isinstance(group, dict) and group.get("matcher") in ("*", "", None)
                for h, handler in enumerate(as_list(group.get("hooks"))) if isinstance(handler, dict)]
    wired = [h for h in handlers if wiring_problem(ctx, path, h[3], ID) is None]
    problems = [] if wired else [any_wired_problem(ctx, path, [h[3] for h in handlers], ID)]
    config, problem = _toml(ctx, ctx.codex_home / "config.toml")
    if problem:
        problems.append(problem)
    elif dig(config, "features", "hooks") is False:
        problems.append(("FAIL", "config.toml turns hooks off: [features] hooks = false, so the hook never runs"))
    if wired:
        g, h, matcher, command, timeout = wired[0]
        key, want = f"{path}:pre_tool_use:{g}:{h}", trust_hash(command, matcher or "*", timeout)
        if _trusted_hash(ctx.codex_home / "config.toml", key) != want:
            problems.append(("FAIL", f"the hook isn't trusted: config.toml needs "
                                     f"[hooks.state.\"{key}\"] trusted_hash = \"{want}\""))
    rules = ctx.codex_home / "rules/set-up-machine.rules"
    text = rules.read_text() if rules.is_file() else ""
    for row in ctx.setup.rows:
        if row.kind == "command" and native_command_row(row) and f"personal rule {row.id})" not in text:
            problems.append(("FAIL", f"personal permission {row.id} has no rule in {ctx.show(rules)}"))
    return cell(problems)


def check_sandbox(ctx, env=None) -> Cell:
    """The sandbox and approval keys the declared Codex config sets have the same value in `config.toml`."""
    return _declared_cell(ctx, sandbox=True, env=env)


def check_plugins(ctx) -> Cell:
    """Each bundle is enabled in `config.toml` and has a cached manifest; each MCP server is configured."""
    entries = ctx.setup.plugins(ID)
    if not entries:
        return na("installs.json lists no plugin for Codex")
    config, problem = _toml(ctx, ctx.codex_home / "config.toml")
    if problem:
        return cell([problem])
    problems = []
    for entry in entries:
        if entry["kind"] == "mcp":
            if dig(config, "mcp_servers", entry["name"]) is None:
                problems.append(("FAIL", f"{entry['name']} has no [mcp_servers.{entry['name']}] in config.toml"))
            if dig(config, "mcp_servers", entry["name"], "enabled") is False:
                problems.append(("gap", f"{entry['name']} is disabled; enable it only after any required sign-in"))
            continue
        plugin, _, market = entry["source"].partition("@")
        cache = ctx.codex_home / "plugins/cache" / market / plugin
        if dig(config, "plugins", entry["source"], "enabled") is not True or not any(cache.glob("**/plugin.json")):
            problems.append(("FAIL", f"{entry['source']} isn't installed and enabled"))
    return cell(problems)


def check_skills(ctx) -> Cell:
    return cell(skill_problems(ctx, [ctx.home / ".agents/skills", ctx.codex_home / "skills"]))


def check_config(ctx, env=None) -> Cell:
    """Every other key the declared Codex config sets, such as `model`, has the same value in `config.toml`."""
    return _declared_cell(ctx, sandbox=False, env=env)


def _declared_cell(ctx, sandbox: bool, env=None) -> Cell:
    """One of the declared Codex config's two cells: its SANDBOX_KEYS (sandbox), or the rest (config). Each key is checked in one cell only, so one wrong value is one FAIL. n/a when the cell has no key."""
    source = ctx.setup.file(ID, "config", env)
    if source is None:
        return na("setup/harnesses.json names no Codex config")
    (declared, bad_source), (config, bad_config) = _toml(ctx, source), _toml(ctx, ctx.codex_home / "config.toml")
    if bad_source or bad_config:
        return cell([bad_source or bad_config])
    keys = [key for key in declared if (key in SANDBOX_KEYS) == sandbox]
    if not keys:
        return na(f"the declared Codex config sets no {'sandbox' if sandbox else 'other'} key")
    return cell(declared_problems(ctx, source, declared, ctx.codex_home / "config.toml", config, keys))


def _toml(ctx, path: Path) -> tuple:
    """(the TOML table in a file, None), or (None, the problem): no tomllib, or a malformed file."""
    if checks.tomllib is None:
        return None, NO_TOML
    data = read_toml(path)
    return (data, None) if data is not None else (None, ("FAIL", f"{ctx.show(path)} isn't valid TOML"))


def _trusted_hash(config: Path, key: str):
    """The trusted_hash under [hooks.state."<key>"] in config.toml, read line by line, without a TOML parser."""
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
                match = re.match(r'^\s*trusted_hash\s*=\s*"([^"]*)"', body)
                if match:
                    return match.group(1)
    return None
