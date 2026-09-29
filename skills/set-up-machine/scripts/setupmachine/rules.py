"""The rule table: loading, validation, and what each row covers.

Every harness adapter and the pre-tool hook read the table through this module,
so a row means the same thing everywhere. A row's `match` takes one of three
kinds, told apart by its keys:

- command: `program` (one name or a list), optional `subcommands`, `flags`, `operands`
  (words after the flags, or a list of alternative word lists), `arguments: "none"` (the
  program run with nothing after it) or `arguments: "flags"` (with flags and nothing else
  after it), and `files` (globs one of its operands matches, read as a file row's paths, with an
  optional `except`);
- file: `paths` (globs, relative to the project or `~/`), `access` (`read` or `write`)
  and an optional `except` (globs the row leaves out, such as `**/.env.example`);
- mcp-tool: `server` and `tool`, two case-insensitive regular expressions matched
  against the tool names the harness exposes on the machine.

Any row may carry a `gap`: what no harness can catch for it, which every
harness's audit names. A deny row may carry a `guard` (`label` and `rule`): a
prose rule for a harness's semantic guard, covering the row's family, for what
its patterns can't list.
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
# Shell builtins: they have no absolute path to spell.
BUILTINS = {".", "source", "set", "export", "declare", "typeset", "unset", "eval", "alias"}
# What a positive character class lists when a harness has no negated one (see without()).
CLASS_RANGES = ("0-9", "A-Z", "a-z")
CLASS_SINGLES = "_."


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
    operands: tuple = ((),)  # command: alternative word sequences after the flags
    bare: bool = False  # command: the program with nothing after it (`arguments: "none"`)
    flags_only: bool = False  # command: the program with one or more flags and nothing else (`arguments: "flags"`)
    files: tuple = ()  # command: globs one of its operands matches
    paths: tuple = ()  # file: globs, relative to the project or starting `~/`
    access: str = ""  # file: read or write
    excepts: tuple = ()  # file, or command with files: globs left out
    gap: str = ""  # what no harness can catch for this row
    guard: str = ""  # `<label>: <rule>`, prose for a harness's semantic guard (Claude Code's auto mode)
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
    if "gap" in row:
        if not isinstance(row["gap"], str) or not row["gap"]:
            raise RuleTableError(f"{where}: gap must be a sentence")
        common["gap"] = row["gap"]
    if "guard" in row:
        guard = row["guard"]
        if not (isinstance(guard, dict) and set(guard) == {"label", "rule"}
                and all(isinstance(v, str) and v for v in guard.values())):
            raise RuleTableError(f"{where}: guard must hold a `label` and a `rule`, both text")
        if row["level"] != "deny":
            raise RuleTableError(f"{where}: only a deny row can carry a guard")
        common["guard"] = f"{guard['label']}: {guard['rule']}"
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
    arguments = match.get("arguments")
    if arguments not in (None, "none", "flags"):
        raise RuleTableError(f'{where}: match.arguments can only be "none" or "flags"')
    if arguments and (groups or subs != [[]] or match.get("operands") or "files" in match):
        raise RuleTableError(f'{where}: match.arguments takes no flags, subcommands, operands or files')
    if "except" in match and "files" not in match:
        raise RuleTableError(f"{where}: match.except needs match.files")
    return {
        "program": program if isinstance(program, str) else tuple(program),
        "flags": tuple(tuple(g) for g in groups),
        "subcommands": tuple(_words(s, where, "each of match.subcommands") for s in subs),
        "operands": _operands(match.get("operands", []), where),
        "bare": arguments == "none",
        "flags_only": arguments == "flags",
        "files": _globs(match["files"], where, "match.files") if "files" in match else (),
        "excepts": _globs(match["except"], where, "match.except") if "except" in match else (),
    }


def _operands(value, where: str) -> tuple:
    """A list of words is one sequence; a list of word lists is alternative sequences (`777`, `a+rwx`)."""
    if isinstance(value, list) and value and all(isinstance(v, list) for v in value):
        return tuple(_words(v, where, "each of match.operands") for v in value)
    return (_words(value, where, "match.operands"),)


def _globs(paths, where: str, what: str) -> tuple:
    if not isinstance(paths, list) or not paths or not all(
        isinstance(p, str) and p and not p.startswith(("/", "./")) and (p.startswith("~/") or not p.startswith("~"))
        for p in paths
    ):
        raise RuleTableError(f"{where}: {what} must be globs relative to the project (`**/.env`) or starting `~/`")
    return tuple(paths)


def _parse_file(match: dict, where: str) -> dict:
    if match.get("access") not in ACCESS:
        raise RuleTableError(f"{where}: match.access must be one of {', '.join(ACCESS)}")
    return {
        "paths": _globs(match["paths"], where, "match.paths"),
        "access": match["access"],
        "excepts": _globs(match["except"], where, "match.except") if "except" in match else (),
    }


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
    """Each program as typed: bare, then by each common absolute path (a shell builtin has none)."""
    return [s for p in rule.programs for s in [p] + ([] if p in BUILTINS else [f"{d}/{p}" for d in PROGRAM_DIRS])]


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
    """Every argv prefix the rule covers: program spelling x subcommand x flag form x operands."""
    return _dedupe(
        [[p, *s, *f, *o] for p in program_spellings(rule) for s in rule.subcommands for f in flag_forms(rule)
         for o in rule.operands]
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


# --- globs --------------------------------------------------------------------


def glob_regex(glob: str, cwd: str, home, fold_case: bool = False):
    """A path glob as a regex over absolute paths.

    `**/x` matches at any depth, even outside the project; other relative globs
    are anchored at the working directory, and `~/` globs at the home folder.
    With `fold_case`, as where the filesystem ignores case, `.ENV` matches `.env`.
    """
    if glob.startswith("~/"):
        anchor, glob = re.escape(str(home).rstrip("/")) + "/", glob[2:]
    elif glob.startswith("**/"):
        anchor = ""
    else:
        anchor = re.escape(cwd.rstrip("/")) + "/"
    out, i = [], 0
    while i < len(glob):
        if glob.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif glob.startswith("**", i):
            out.append(".*")
            i += 2
        elif glob[i] == "*":
            out.append("[^/]*")
            i += 1
        elif glob[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(glob[i]))
            i += 1
    return re.compile("^" + anchor + "".join(out) + "$", re.I if fold_case else 0)


def without(glob: str, excepts) -> list:
    """Globs covering what `glob` covers minus an exception, for a harness with no negation.

    Works when `glob` ends in one `*` and the exception is the same text with a
    literal in its place (`**/.env.*` minus `**/.env.example`): each shorter
    prefix of the literal, each name that leaves it at some character, through a
    positive class (Claude Code reads `[!x]` and `[^x]` as plain classes), and
    each longer name. A class lists letters in both cases, digits, `_` and `.`,
    so a name leaving the literal through any other character isn't covered.
    A glob no exception applies to comes back as it is.
    """
    stem = glob[:-1]
    if not glob.endswith("*") or stem.endswith("*"):
        return [glob]
    literals = [e[len(stem):] for e in excepts if e.startswith(stem) and len(e) > len(stem)]
    literals = [lit for lit in literals if not set("*?[") & set(lit) and "/" not in lit]
    if not literals:
        return [glob]
    if len(literals) > 1:
        raise RuleTableError(f"{glob}: only one exception per glob can be expressed without negation")
    lit = literals[0]
    return ([stem + lit[:i] for i in range(len(lit))]
            + [stem + lit[:i] + class_without(lit[i]) + "*" for i in range(len(lit))]
            + [stem + lit + "?*"])


def class_without(char: str) -> str:
    """A positive character class of letters, digits, `_` and `.`, leaving out one character in both cases."""
    left_out = {char.lower(), char.upper()}
    parts = []
    for rng in CLASS_RANGES:
        chars = [chr(c) for c in range(ord(rng[0]), ord(rng[2]) + 1) if chr(c) not in left_out]
        parts += _runs(chars)
    parts += [c for c in CLASS_SINGLES if c not in left_out]
    return "[" + "".join(parts) + "]"


def _runs(chars: list) -> list:
    """Consecutive characters as ranges: a, b, c, e -> `a-c`, `e`."""
    runs, start = [], 0
    for k in range(1, len(chars) + 1):
        if k == len(chars) or ord(chars[k]) != ord(chars[k - 1]) + 1:
            run = chars[start:k]
            runs.append(run[0] if len(run) == 1 else "".join(run) if len(run) == 2 else f"{run[0]}-{run[-1]}")
            start = k
    return runs


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
