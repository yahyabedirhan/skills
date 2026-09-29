"""The rule table: loading, validation, and the command forms each row covers.

Every harness adapter and the pre-tool hook read the table through this module,
so a row means the same thing everywhere.
"""
from __future__ import annotations

import itertools
import json
from dataclasses import dataclass
from pathlib import Path

LEVELS = ("allow-and-report", "ask", "deny")

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
    program: str
    flags: tuple  # tuple of flag groups; each group is a tuple of spellings
    reason: str
    instruction: str


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
    program = match.get("program")
    if not isinstance(program, str) or not program or "/" in program or " " in program:
        raise RuleTableError(f"{where}: match.program must be a bare program name")
    groups = match.get("flags", [])
    if not isinstance(groups, list) or not all(
        isinstance(g, list) and g and all(isinstance(s, str) and s and not s.startswith("-") for s in g)
        for g in groups
    ):
        raise RuleTableError(f"{where}: match.flags must be a list of non-empty lists of flag names without dashes")
    return Rule(
        id=row["id"],
        level=row["level"],
        summary=row["summary"],
        program=program,
        flags=tuple(tuple(g) for g in groups),
        reason=row["reason"],
        instruction=row["instruction"],
    )


def program_spellings(rule: Rule) -> list:
    """The program as typed: bare, then by each common absolute path."""
    return [rule.program] + [f"{d}/{rule.program}" for d in PROGRAM_DIRS]


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
    """Every argv prefix the rule covers: program spelling x flag form."""
    return [[p] + f for p in program_spellings(rule) for f in flag_forms(rule)]


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
