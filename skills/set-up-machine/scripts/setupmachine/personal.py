"""The personal repository, found through the pointer, against the shared file made from it.

The pointer, `~/.config/agents/source.md`, names the person's personal repository and where
it is cloned, or says there is none:

    - Repository: `<owner>/<repo>`      or      - Repository: none
    - Clone: `<path>`

The repository's `agents/instructions.md` holds an `## Environment defaults` table (its Role
and Tool columns are read; any other column is notes) and a `## Personal workflow` section.
The shared global instructions file, `~/.config/agents/AGENTS.md`, should carry those Tool
values (`none` for a role the repository leaves out) and that workflow section's text.

Its `agents/permissions.json` holds personal rows in the rule table's format, which may
also take the level `allow`; `permissions` loads them for the hook and the verify script.
references/personal-repository.md is the layout for agents; this module only reads it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from . import rules as rule_table

POINTER = Path(".config/agents/source.md")
SHARED = Path(".config/agents/AGENTS.md")
INSTRUCTIONS = Path("agents/instructions.md")
PERMISSIONS = Path("agents/permissions.json")
DEFAULTS = "## Environment defaults"
WORKFLOW = "## Personal workflow"
WORKFLOW_INTRO = ("Rules for how this person works that pass the team test. "
                  "Anything a project or a skill needs goes there instead.")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class PersonalError(ValueError):
    pass


@dataclass(frozen=True)
class Pointer:
    repository: str  # `<owner>/<repo>`, or "" for none
    clone: Path | None


def check(home: Path) -> list:
    """(status, text) lines: `none` or `ok` when the shared file matches the source, else FAIL lines."""
    try:
        pointer = read_pointer(home)
    except PersonalError as exc:
        return [("FAIL", str(exc))]
    if not pointer.repository:
        return [("none", f"no personal repository (the pointer at {home / POINTER} says none)")]
    instructions_path = pointer.clone / INSTRUCTIONS
    shared_path = home / SHARED
    try:
        tools, workflow = _read_instructions(instructions_path)
        shared = _read(shared_path)
    except PersonalError as exc:
        return [("FAIL", str(exc))]

    fails = []
    shared_tools = _tools(shared)
    if shared_tools is None:
        fails.append(f"{shared_path} has no `{DEFAULTS}` table with Role and Tool columns")
        shared_tools = {}
    for role in tools:
        if role not in shared_tools and shared_tools:
            fails.append(f"`{role}` has no row in {shared_path}, but {instructions_path} gives it `{tools[role]}`")
    for role, value in shared_tools.items():
        want = tools.get(role, "none")
        if value != want:
            fails.append(f"`{role}` is `{value}` in {shared_path}, `{want}` in {instructions_path}")
    shared_workflow = _section(shared, WORKFLOW)
    if shared_workflow is None:
        fails.append(f"{shared_path} has no `{WORKFLOW}` section")
    elif _drop_intro(shared_workflow) != workflow:
        fails.append(f"`{WORKFLOW}` in {shared_path} differs from {instructions_path}")
    if fails:
        return [("FAIL", text) for text in fails]
    lines = len(workflow.splitlines()) if workflow else 0
    return [("ok", f"{pointer.repository} at {pointer.clone}: {len(tools)} environment defaults, "
                   f"the personal workflow ({lines} lines) match {shared_path}")]


def permissions(home: Path, table: list) -> list:
    """The personal rows, as Rules, from the repository the pointer names.

    No rows when the pointer is missing, malformed or says none (`check` reports those), or
    when the repository has no permissions file. A malformed row, or one reusing an id of
    the rule table, raises RuleTableError.
    """
    try:
        pointer = read_pointer(home)
    except PersonalError:
        return []
    if not pointer.repository or not (pointer.clone / PERMISSIONS).is_file():
        return []
    rows = rule_table.load(pointer.clone / PERMISSIONS, personal=True)
    taken = {r.id for r in table}
    for row in rows:
        if row.id in taken:
            raise rule_table.RuleTableError(f"{pointer.clone / PERMISSIONS}: the id {row.id!r} is already "
                                            "a row of the rule table")
    return rows


def read_pointer(home: Path) -> Pointer:
    path = home / POINTER
    if not path.is_file():
        raise PersonalError(f"no pointer at {path}: ask the user which repository holds their personal setup, "
                            "or whether they have none, and write it")
    text = path.read_text()
    repository = _field(text, "Repository")
    if repository is None:
        raise PersonalError(f"{path} has no `- Repository:` line")
    if repository.lower() == "none":
        return Pointer("", None)
    if not REPOSITORY.match(repository):
        raise PersonalError(f"{path}: the repository `{repository}` isn't `<owner>/<repo>`")
    clone = _field(text, "Clone")
    if not clone:
        raise PersonalError(f"{path} names {repository} but has no `- Clone:` line")
    if not clone.startswith(("~/", "/")):
        raise PersonalError(f"{path}: the clone path `{clone}` doesn't start with `~/` or `/`")
    clone_path = Path(str(home) + clone[1:]) if clone.startswith("~/") else Path(clone)
    return Pointer(repository, clone_path)


def _field(text: str, name: str):
    m = re.search(rf"^\s*[-*]\s*{name}:\s*(.*?)\s*$", text, re.M)
    return _plain(m.group(1)) if m else None


def _plain(cell: str) -> str:
    cell = cell.strip()
    if len(cell) >= 2 and cell.startswith("`") and cell.endswith("`"):
        cell = cell[1:-1].strip()
    return cell


def _read(path: Path) -> str:
    try:
        return path.read_text()
    except OSError:
        raise PersonalError(f"{path} doesn't exist") from None


def _read_instructions(path: Path):
    text = _read(path)
    tools = _tools(text)
    if tools is None:
        raise PersonalError(f"{path} has no `{DEFAULTS}` table with Role and Tool columns")
    workflow = _section(text, WORKFLOW)
    if workflow is None:
        raise PersonalError(f"{path} has no `{WORKFLOW}` section")
    return {role: value for role, value in tools.items() if value != "none"}, workflow


def _section(text: str, heading: str):
    """The text under a `## ` heading, up to the next `## ` heading or generated block, stripped."""
    lines = text.split("\n")
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == heading)
    except StopIteration:
        return None
    body = []
    for line in lines[start + 1:]:
        if line.startswith("## ") or line.startswith("<!-- set-up-machine:"):
            break
        body.append(line)
    return "\n".join(body).strip()


def _drop_intro(body: str) -> str:
    return body[len(WORKFLOW_INTRO):].strip() if body.startswith(WORKFLOW_INTRO) else body


def _tools(text: str):
    """{role: Tool value} from the Environment defaults table, or None without one."""
    body = _section(text, DEFAULTS)
    rows = [_cells(l) for l in (body or "").split("\n") if l.strip().startswith("|")]
    if not rows:
        return None
    header = [_plain(c).lower() for c in rows[0]]
    if "role" not in header or "tool" not in header:
        return None
    role_at, tool_at = header.index("role"), header.index("tool")
    tools = {}
    for row in rows[1:]:
        if all(set(c.strip()) <= set("-: ") for c in row):
            continue  # the separator row
        if len(row) > max(role_at, tool_at):
            tools[_plain(row[role_at])] = _plain(row[tool_at]) or "none"
    return tools


def _cells(line: str) -> list:
    """A table row's cells; a `|` inside backticks or escaped belongs to its cell."""
    cells, cell, code, i = [], "", False, 0
    line = line.strip()
    while i < len(line):
        ch = line[i]
        if ch == "\\" and i + 1 < len(line) and line[i + 1] == "|":
            cell += "|"
            i += 2
            continue
        if ch == "`":
            code = not code
        if ch == "|" and not code:
            cells.append(cell)
            cell = ""
        else:
            cell += ch
        i += 1
    cells.append(cell)
    return cells[1:-1] if len(cells) >= 2 else cells
