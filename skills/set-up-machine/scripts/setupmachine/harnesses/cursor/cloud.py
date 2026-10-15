"""Cursor cloud agents: one VM per run, project hooks, and the repo AGENTS.md cloud section
(references/cursor/cloud.md).

The hook payload is Cursor's, so read and write are Cursor's. The project hook
calls the script with `--harness cursor`.
"""
from __future__ import annotations

import os
import re
import shlex
from pathlib import Path

from . import read as _read, write as _write
from ...checks import Cell, cell, na, read_json, skill_problems
from ...workstation import HARNESS_SECTION, section

ID, LABEL = "cursor", "Cursor"
ENV = "cloud"
SOCKET = Path("/run/cursor/api.sock")
ENV_FILE = Path(".cursor/environment.json")
AGENTS = Path("AGENTS.md")
# The section Cursor documents for cloud-only instructions in the repo AGENTS.md.
CLOUD_SECTION = "## Cursor Cloud specific instructions"
HOOKS = Path(".cursor/hooks.json")
# A cloud agent runs these. beforeMCPExecution is in the file for the CLI and does not run here.
RAN = ("beforeShellExecution", "beforeReadFile", "preToolUse")
NOT_RAN = "beforeMCPExecution"
# The keys a declared config may set (references/cursor/cloud.md, *Config*).
KEYS = ("secrets",)
_HARNESS = re.compile(r"--harness(?:\s+|=)cursor(?:\s|$)")


def present(home: Path) -> bool:
    """A Cursor cloud VM has the agent API socket. A `--home` fixture on that VM still sees it,
    the same way a CLI on PATH is seen from the real machine."""
    return SOCKET.is_socket()


def read(payload: dict):
    return _read(payload)


def write(denials: list, asks=()) -> str:
    return _write(denials, asks)


# --- the checks ----------------------------------------------------------------------------


def check_instructions(ctx) -> Cell:
    """The clone has an environment file with an install command, and the repo AGENTS.md has
    Cursor's cloud section, which links the cloud instructions file the agent applies itself."""
    if ctx.setup.clone is None:
        return Cell("gap", ["no workstation clone: can't see .cursor/environment.json or AGENTS.md"])
    env_path = ctx.setup.clone / ENV_FILE
    declared = ctx.setup.file(ID, "instructions", ENV)
    if not env_path.is_file():
        if declared is None:
            return Cell("gap", ["this repo has no .cursor/environment.json"])
        return Cell("FAIL", [f"no {ctx.show(env_path)}"])
    data = read_json(env_path)
    problems = []
    if not isinstance(data, dict) or not isinstance(data.get("install"), str) or not data["install"].strip():
        problems.append(("FAIL", f"{ctx.show(env_path)} needs an install command"))
    if declared is None:
        problems.append(("gap", "setup/harnesses.json names no instructions for Cursor's cloud environment"))
        return cell(problems)
    if not section(declared.read_text(), HARNESS_SECTION):
        problems.append(("FAIL", f"{ctx.show(declared)} has no `{HARNESS_SECTION}` section"))
    agents = ctx.setup.clone / AGENTS
    body = section(agents.read_text(), CLOUD_SECTION) if agents.is_file() else ""
    relative = declared.relative_to(ctx.setup.clone).as_posix()
    if not body:
        problems.append(("FAIL", f"{ctx.show(agents)} has no `{CLOUD_SECTION}` section; the agent reads it at start"))
    elif relative not in body:
        problems.append(("FAIL", f"{ctx.show(agents)}'s `{CLOUD_SECTION}` section doesn't point at {relative}"))
    return cell(problems)


def check_guardrails(ctx) -> Cell:
    """The events a cloud agent runs resolve to an existing pre_tool_hook.py. beforeMCPExecution
    does not run here."""
    if ctx.setup.clone is None:
        return Cell("gap", ["no workstation clone: can't see .cursor/hooks.json"])
    path = ctx.setup.clone / HOOKS
    hooks = read_json(path)
    hooks = hooks.get("hooks") if isinstance(hooks, dict) else None
    hooks = hooks if isinstance(hooks, dict) else {}
    problems = []
    for event in RAN:
        commands = [h.get("command") for h in (hooks.get(event) or []) if isinstance(h, dict)]
        problem = _resolves(ctx, path, commands)
        if problem:
            problems.append((problem[0], f"{event}: {problem[1]}"))
    problems.append(("gap", f"{NOT_RAN} does not run on a cloud agent"))
    return cell(problems)


def check_sandbox(ctx) -> Cell:
    return Cell("gap", ["network mode is set in the dashboard; nothing on the VM shows it"])


def check_plugins(ctx) -> Cell:
    return Cell("gap", ["MCP servers are connected in the dashboard; nothing on the VM lists them"])


def check_skills(ctx) -> Cell:
    """Each listed skill is in a folder the cloud agent scans."""
    folders = [ctx.home / ".cursor/skills", ctx.home / ".agents/skills"]
    if ctx.setup.clone is not None:
        folders += [ctx.setup.clone / ".cursor/skills", ctx.setup.clone / ".agents/skills"]
    return cell(skill_problems(ctx, folders))


def check_config(ctx) -> Cell:
    """The declared config's `secrets` are set as environment variables, by name only."""
    source = ctx.setup.file(ID, "config", ENV)
    if source is None:
        return na("setup/harnesses.json names no Cursor cloud config")
    declared = read_json(source)
    if not source.is_file() or declared is None:
        return Cell("FAIL", [f"{ctx.show(source)} isn't a JSON object"])
    problems = []
    for key in declared:
        if key not in KEYS:
            problems.append(("gap", f"{source.name}: `{key}` has no Cursor cloud setting"))
    secrets = [s for s in declared.get("secrets", []) if isinstance(s, str)]
    if secrets and ctx.home != Path.home().resolve():
        problems.append(("gap", "secrets are checked only in the real home"))
    elif secrets:
        missing = [s for s in secrets if not os.environ.get(s)]  # the name only: a value is never read out
        if missing:
            problems.append(("FAIL", f"secret {', '.join(missing)} is not set; add it in the dashboard"))
    return cell(problems)


def _resolves(ctx, path: Path, commands: list):
    """None when one command runs an existing pre_tool_hook.py for Cursor's payload."""
    if not commands or not isinstance(commands[0], str):
        return ("FAIL", f"{ctx.show(path)} has no command")
    command = commands[0]
    script = _script(command)
    if script is None or not _HARNESS.search(command):
        return ("FAIL", f"{ctx.show(path)} does not run pre_tool_hook.py --harness cursor")
    if not script.is_file():
        return ("FAIL", f"{ctx.show(path)} runs {ctx.show(script)}, which doesn't exist")
    return None


def _script(command: str):
    """The pre_tool_hook.py path a command names, with $HOME and ~/ expanded."""
    try:
        words = shlex.split(command)
    except ValueError:
        return None
    raw = next((w for w in words if w.endswith("pre_tool_hook.py")), None)
    if raw is None:
        return None
    home = str(Path.home())
    expanded = raw.replace("${HOME}", home).replace("$HOME", home)
    if expanded.startswith("~/"):
        expanded = home + expanded[1:]
    return Path(expanded)
