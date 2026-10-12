"""What every harness check shares: the cell it returns, the run's context, and small helpers.

A harness module checks one setup area at a time and returns a `Cell`: one of the four
statuses, with a detail sentence for each problem it found. A check collects its problems
as (status, sentence) pairs and calls `cell`, which picks the worst status:

- `FAIL`: the machine lacks what setup/ asks for;
- `gap`: the harness can't do it, or the check can't see it;
- `ok`: nothing is missing;
- `n/a`: the area does not apply to this harness (`na`).

The helpers below read a file the same way for every harness: JSON, TOML, a link to the
shared file, the hook script a wired command runs, the skills a harness can see, and the
personal permission entries a harness's native lists hold.
"""
from __future__ import annotations

import json
import os
import shlex
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from . import commands, rules as rule_table, workstation

try:
    import tomllib  # Python 3.11+; an older Python reports a TOML check as a gap
except ImportError:
    tomllib = None

HOOK_SCRIPT = "pre_tool_hook.py"
LOCK = Path(".agents/.skill-lock.json")
# Which native list a personal permission's entries go to, by the row's level.
LISTS = {"deny": "deny", "ask": "ask", "allow-and-report": "allow", "allow": "allow"}


@dataclass
class Cell:
    status: str
    details: list = field(default_factory=list)


@dataclass
class Context:
    """One verifier run: the home folder, what setup/ asks for, and the resolved harness folders."""
    home: Path
    setup: workstation.Setup
    rows: list  # the rule table and the personal permissions
    codex_home: Path
    pi_dir: Path

    @property
    def shared(self) -> Path:
        return self.home / workstation.SHARED

    def show(self, path) -> str:
        """A path as the report prints it: the home folder as `~`."""
        text = str(path)
        return "~" + text[len(str(self.home)):] if text.startswith(str(self.home) + "/") else text


def cell(problems: list) -> Cell:
    """The cell for a list of (status, sentence) problems: FAIL over gap over ok."""
    statuses = {status for status, _ in problems}
    status = "FAIL" if "FAIL" in statuses else "gap" if "gap" in statuses else "ok"
    return Cell(status, [text for _, text in problems])


def na(reason: str) -> Cell:
    return Cell("n/a", [reason])


def read_json(path: Path):
    """The JSON object in a file: {} when the file is missing, None when it isn't a JSON object."""
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        return {}
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def read_toml(path: Path):
    """The TOML table in a file: {} when missing, None when malformed or this Python has no tomllib."""
    if tomllib is None:
        return None
    try:
        return tomllib.loads(path.read_text())
    except FileNotFoundError:
        return {}
    except (OSError, ValueError):
        return None


def dig(data, *keys):
    """data[k1][k2]…, or None where a level is missing or isn't a table."""
    for key in keys:
        data = data.get(key) if isinstance(data, dict) else None
    return data


def link_problem(ctx: Context, link: Path):
    """A problem when `link` isn't a symlink to the shared file; None when it is."""
    if link.is_symlink() and link.resolve() == ctx.shared.resolve():
        return None
    if link.exists() or link.is_symlink():
        return ("FAIL", f"{ctx.show(link)} isn't a link to the shared file; move its lines there, then link it")
    return ("FAIL", f"no {ctx.show(link)}; link it to the shared file")


def hook_script(command: str, harness: str, home: Path):
    """The hook script a wired command runs for this harness, or None when it runs none."""
    try:
        words = shlex.split(command)
    except ValueError:
        return None
    script = next((w for w in words if w.endswith(HOOK_SCRIPT)), None)
    if script is None or f"--harness {harness}" not in " ".join(words):
        return None
    return Path(str(home) + script[1:]) if script.startswith("~/") else Path(script)


def wiring_problem(ctx: Context, where: Path, command, harness: str):
    """A problem when `command` doesn't run an existing hook script for this harness; None when it does."""
    script = hook_script(command, harness, ctx.home) if isinstance(command, str) else None
    if script is None:
        return ("FAIL", f"{ctx.show(where)} doesn't run the pre-tool hook with --harness {harness}")
    if not script.is_file():
        return ("FAIL", f"{ctx.show(where)} runs {ctx.show(script)}, which doesn't exist")
    return None


def any_wired_problem(ctx: Context, where: Path, commands: list, harness: str):
    """None when one of the commands runs the hook; else why the first one doesn't, or that none is there."""
    problems = [wiring_problem(ctx, where, c, harness) for c in commands]
    if None in problems:
        return None
    return problems[0] if problems else ("FAIL", f"{ctx.show(where)} has no pre-tool hook for every tool")


def skill_problems(ctx: Context, folders: list) -> list:
    """A problem per installs.json skills entry whose skills this harness can't see in its folders.

    An entry naming skills wants each name. An entry without names wants every skill
    `~/.agents/.skill-lock.json` records from that source, and at least one.
    """
    lock = (read_json(ctx.home / LOCK) or {}).get("skills", {})
    problems = []
    for entry in ctx.setup.installs.get("skills", []):
        source = entry["source"]
        names = entry.get("skills") or sorted(n for n, rec in lock.items() if rec.get("source") == source)
        if not names:
            problems.append(("FAIL", f"no skill from {source} is installed ({ctx.show(ctx.home / LOCK)})"))
            continue
        missing = [n for n in names if not any((folder / n / "SKILL.md").is_file() for folder in folders)]
        if missing:
            where = " or ".join(ctx.show(f) for f in folders)
            problems.append(("FAIL", f"{source}: {', '.join(missing)} not in {where}"))
    return problems


def personal_problems(ctx: Context, lists: dict, where: Path) -> list:
    """A problem per personal permission with no entry in the native list its level goes to.

    `lists` maps a list name (deny, ask, allow) to its entries, each a (kind, text) pair:
    ("command", "rm -rf"), ("path", "~/.ssh/**") or ("mcp", "mcp__server__tool"). A list
    the harness lacks is left out of `lists`, and its rows are skipped. A row with no native
    entry by its harness reference (an MCP row before a tool listing names its tools, a command
    whose program isn't on PATH, or a kind of command row no prefix can express) is skipped too.
    """
    problems = []
    for row in ctx.setup.rows:
        name = LISTS[row.level]
        if name not in lists or any(_entry_of(row, kind, text, ctx.home) for kind, text in lists[name]):
            continue
        if row.kind == "mcp-tool" or not native_command_row(row):
            continue
        problems.append(("FAIL", f"personal permission {row.id} has no `{name}` entry in {ctx.show(where)}"))
    return problems


def native_command_row(row) -> bool:
    """Whether a row gets native entries: every file row, and a command row a prefix can express
    whose program is on PATH."""
    if row.kind != "command":
        return True
    plain = not (row.bare or row.flags_only or row.variables or row.files)
    return plain and any(shutil.which(p) for p in row.programs)


def _entry_of(row, kind: str, text: str, home: Path) -> bool:
    """Whether a native entry is one this row produces: what the entry names, the row covers."""
    if kind == "mcp" and row.kind == "mcp-tool":
        return bool(rule_table.matching_tools(row, [text]))
    if kind == "command" and row.kind == "command":
        argvs = commands.simple_commands(text)
        return len(argvs) == 1 and commands.covers(row, argvs[0])
    if kind == "path" and row.kind == "file":
        cwd = str(home / "project")
        path = str(home) + text[1:] if text.startswith("~/") else text if text.startswith(("/", "**/")) else \
            os.path.join(cwd, text[2:] if text.startswith("./") else text)
        return any(rule_table.glob_regex(g, cwd, home).match(path) for g in row.paths)
    return False
