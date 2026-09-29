"""The rule table: loading, validation, and what each row covers.

Every harness adapter and the pre-tool hook read the table through this module,
so a row means the same thing everywhere. A row's `match` takes one of three
kinds, told apart by its keys:

- command: `program` (one name or a list), optional `subcommands`, `flags`, `operands`;
- file: `paths` (globs, relative to the project or `~/`) and `access` (`read` or `write`);
- mcp-tool: `server` and `tool`, two case-insensitive regular expressions matched
  against the tool names the harness exposes on the machine.
"""
from __future__ import annotations

import itertools
import json
import re
from dataclasses import dataclass
from pathlib import Path

LEVELS = ("allow-and-report", "ask", "deny")
KINDS = ("command", "file", "mcp-tool")
ACCESS = ("read", "write")

DEFAULT_TABLE = Path(__file__).resolve().parents[2] / "rules.json"

# Directories a program is commonly invoked from by absolute path.
PROGRAM_DIRS = ("/bin", "/usr/bin")


class RuleTableError(ValueError):
    pass


@dataclass(frozen=True)
class Rule:
    id: str
    level: str
    summary: str
    reason: str
    instruction: str
    program: object = ""  # command: a name, or a tuple of names
    flags: tuple = ()  # command: flag groups; each group is a tuple of spellings
    subcommands: tuple = ((),)  # command: alternative word sequences after the program
    operands: tuple = ()  # command: words after the flags
    paths: tuple = ()  # file: globs, relative to the project or starting `~/`
    access: str = ""  # file: read or write
    server: str = ""  # mcp-tool: regex over the server part of the tool name
    tool: str = ""  # mcp-tool: regex over the tool part

    @property
    def kind(self) -> str:
        if self.paths:
            return "file"
        if self.server:
            return "mcp-tool"
        return "command"

    @property
    def programs(self) -> tuple:
        return (self.program,) if isinstance(self.program, str) else tuple(self.program)


def load(path: Path = DEFAULT_TABLE) -> list:
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise RuleTableError(f"can't read the rule table {path}: {exc}") from exc
    if data.get("version") != 1:
        raise RuleTableError(f"{path}: unsupported table version {data.get('version')!r}")
    rules, seen = [], set()
    for i, row in enumerate(data.get("rules", [])):
        rule = _parse_row(row, f"{path}: rules[{i}]")
        if rule.id in seen:
            raise RuleTableError(f"{path}: duplicate rule id {rule.id!r}")
        seen.add(rule.id)
        rules.append(rule)
    return rules


def _parse_row(row: dict, where: str) -> Rule:
    for key in ("id", "level", "summary", "match", "reason", "instruction"):
        if not row.get(key):
            raise RuleTableError(f"{where}: missing {key!r}")
    if row["level"] not in LEVELS:
        raise RuleTableError(f"{where}: level must be one of {', '.join(LEVELS)}")
    match = row["match"]
    common = {k: row[k] for k in ("id", "level", "summary", "reason", "instruction")}
    kinds = [k for k, key in (("command", "program"), ("file", "paths"), ("mcp-tool", "server")) if key in match]
    if len(kinds) != 1:
        raise RuleTableError(f"{where}: match needs exactly one of program, paths or server")
    parse = {"command": _parse_command, "file": _parse_file, "mcp-tool": _parse_mcp_tool}[kinds[0]]
    return Rule(**common, **parse(match, where))


def _words(value, where: str, what: str) -> tuple:
    if not isinstance(value, list) or not all(isinstance(w, str) and w and " " not in w for w in value):
        raise RuleTableError(f"{where}: {what} must be a list of single words")
    return tuple(value)


def _parse_command(match: dict, where: str) -> dict:
    program = match["program"]
    names = [program] if isinstance(program, str) else program
    if not isinstance(names, list) or not names or not all(
        isinstance(p, str) and p and "/" not in p and " " not in p for p in names
    ):
        raise RuleTableError(f"{where}: match.program must be a bare program name, or a list of them")
    groups = match.get("flags", [])
    if not isinstance(groups, list) or not all(
        isinstance(g, list) and g and all(isinstance(s, str) and s and not s.startswith("-") for s in g)
        for g in groups
    ):
        raise RuleTableError(f"{where}: match.flags must be a list of non-empty lists of flag names without dashes")
    subs = match.get("subcommands", [[]])
    if not isinstance(subs, list) or not subs:
        raise RuleTableError(f"{where}: match.subcommands must be a non-empty list of word lists")
    return {
        "program": program if isinstance(program, str) else tuple(program),
        "flags": tuple(tuple(g) for g in groups),
        "subcommands": tuple(_words(s, where, "each of match.subcommands") for s in subs),
        "operands": _words(match.get("operands", []), where, "match.operands"),
    }


def _parse_file(match: dict, where: str) -> dict:
    paths = match["paths"]
    if not isinstance(paths, list) or not paths or not all(
        isinstance(p, str) and p and not p.startswith(("/", "./")) and (p.startswith("~/") or not p.startswith("~"))
        for p in paths
    ):
        raise RuleTableError(f"{where}: match.paths must be globs relative to the project (`**/.env`) or starting `~/`")
    if match.get("access") not in ACCESS:
        raise RuleTableError(f"{where}: match.access must be one of {', '.join(ACCESS)}")
    return {"paths": tuple(paths), "access": match["access"]}


def _parse_mcp_tool(match: dict, where: str) -> dict:
    for key in ("server", "tool"):
        try:
            re.compile(match.get(key) or "")
        except re.error as exc:
            raise RuleTableError(f"{where}: match.{key} isn't a regular expression: {exc}") from exc
        if not match.get(key):
            raise RuleTableError(f"{where}: match.{key} is missing")
    return {"server": match["server"], "tool": match["tool"]}


# --- command rows -------------------------------------------------------------


def program_spellings(rule: Rule) -> list:
    """Each program as typed: bare, then by each common absolute path."""
    return [s for p in rule.programs for s in [p] + [f"{d}/{p}" for d in PROGRAM_DIRS]]


def flag_forms(rule: Rule) -> list:
    """Every way to write the rule's flags as leading arguments, one token list each.

    A one-letter name is a short flag (`-r`), a longer one a long flag
    (`--recursive`). When every group has a short flag, the short flags also
    combine into one token in any order (`-rf`, `-fr`). The canonical form
    (each group's first spelling, clustered, in table order) comes first.
    """
    groups = rule.flags
    if not groups:
        return [[]]
    forms = []
    shorts = [[s for s in g if len(s) == 1] for g in groups]
    if all(shorts):
        for order in itertools.permutations(range(len(groups))):
            for choice in itertools.product(*(shorts[i] for i in order)):
                forms.append(["-" + "".join(choice)])
    spelled = [[_flag(s) for s in g] for g in groups]
    for order in itertools.permutations(range(len(groups))):
        for choice in itertools.product(*(spelled[i] for i in order)):
            forms.append(list(choice))
    return _dedupe(forms)


def command_prefixes(rule: Rule) -> list:
    """Every argv prefix the rule covers: program spelling x subcommand x flag form, then the operands."""
    return _dedupe(
        [[p, *s, *f, *rule.operands] for p in program_spellings(rule) for s in rule.subcommands for f in flag_forms(rule)]
    )


def _flag(name: str) -> str:
    return f"-{name}" if len(name) == 1 else f"--{name}"


def _dedupe(forms: list) -> list:
    seen, out = set(), []
    for f in forms:
        key = tuple(f)
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out


# --- mcp-tool rows ------------------------------------------------------------


def split_mcp_name(name: str):
    """`mcp__<server>__<tool>` -> (server, tool), or None for a tool that isn't an MCP tool."""
    if not name.startswith("mcp__"):
        return None
    server, sep, tool = name[len("mcp__"):].partition("__")
    return (server, tool) if sep and server and tool else None


def matching_tools(rule: Rule, tool_names) -> list:
    """The harness's MCP tools this row covers, in sorted order."""
    found = []
    for name in tool_names:
        parts = split_mcp_name(name)
        if parts and re.search(rule.server, parts[0], re.I) and re.search(rule.tool, parts[1], re.I):
            found.append(name)
    return sorted(set(found))
