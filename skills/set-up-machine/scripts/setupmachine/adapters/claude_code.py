"""Claude Code adapter: permissions in settings.json, global instructions in CLAUDE.md.

Facts it relies on (see references/claude-code.md):
- `~/.claude/settings.json` holds `permissions.{allow, ask, deny}`; deny is checked
  first, then ask, then allow, so adding a stricter entry wins without removing a looser one.
- A `Bash(<prefix>:*)` rule matches the command text as written, so each spelling
  of a command needs its own entry.
- `~/.claude/CLAUDE.md` loads in every session and follows `@path` imports.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from .. import rules as rule_table
from ..plan import Change, FileWrite, Section
from ..shared import read_text

NAME = "claude-code"
LABEL = "Claude Code"

# Rule level -> the settings.json list that expresses it natively.
NATIVE_LIST = {"deny": "deny", "ask": "ask"}
# Settings lists, strictest first.
LISTS = ("deny", "ask", "allow")


def config_dir(home: Path) -> Path:
    return home / ".claude"


def entries_for(rule) -> list:
    return [f"Bash({' '.join(prefix)}:*)" for prefix in rule_table.command_prefixes(rule)]


def gaps_for(rule) -> list:
    if rule.level not in NATIVE_LIST:
        return [f"{rule.level} needs the pre-tool hook; Claude Code has no native {rule.level} level"]
    canonical = " ".join(rule_table.command_prefixes(rule)[0])
    return [
        "Bash rules match the text as written, so these get through: "
        f"more flags in one token (`{canonical}v`), flags after the operands, "
        f"and a quoted inner command (`bash -c \"{canonical} …\"`)"
    ]


def import_line(home: Path, os_home: Path, shared_file: Path) -> str:
    """`@~/…` when home is the user's own home, so the line reads the same on every machine."""
    try:
        if home.resolve() == os_home.resolve():
            return "@~/" + str(shared_file.relative_to(home))
    except ValueError:
        pass
    return "@" + str(shared_file.resolve())


def plan(home: Path, rules: list, owned: dict, shared_file: Path, os_home: Path):
    """Returns (sections, writes, owned_after) for Claude Code."""
    perm_section, perm_write, owned_perms = _plan_permissions(home, rules, owned.get("permissions", {}))
    md_section, md_write, owned_imports = _plan_instructions(home, owned.get("imports", []), shared_file, os_home)
    owned_after = {}
    if any(owned_perms.values()):
        owned_after["permissions"] = owned_perms
    if owned_imports:
        owned_after["imports"] = owned_imports
    return [perm_section, md_section], [perm_write, md_write], owned_after


def _plan_permissions(home: Path, rules: list, owned: dict):
    path = config_dir(home) / "settings.json"
    old = read_text(path)
    try:
        settings = json.loads(old) if old is not None else {}
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} isn't valid JSON ({exc}); fix it by hand, then run the plan again") from exc
    perms = settings.get("permissions", {})
    existing = {name: list(perms.get(name, [])) for name in LISTS}
    section = Section(f"{LABEL}: permissions", path)

    # Desired native entries, per list; where two rules overlap, the stricter level wins.
    desired, rule_of = {}, {}
    for rule in rules:
        for gap in gaps_for(rule):
            section.changes.append(Change("gap", gap, rule.level, rule.id))
        if rule.level not in NATIVE_LIST:
            continue
        for entry in entries_for(rule):
            level = NATIVE_LIST[rule.level]
            if entry not in desired or LISTS.index(level) < LISTS.index(desired[entry]):
                desired[entry], rule_of[entry] = level, rule.id

    add = {name: [] for name in LISTS}
    for entry, level in desired.items():
        found = [name for name in LISTS if entry in existing[name]]
        if any(LISTS.index(name) <= LISTS.index(level) for name in found):
            section.changes.append(Change("present", entry, level, rule_of[entry]))
        elif found:
            add[level].append(entry)
            section.changes.append(Change("tightened", entry, level, rule_of[entry], f"was {found[0]}; {level} wins"))
        else:
            add[level].append(entry)
            section.changes.append(Change("added", entry, level, rule_of[entry]))

    # Entries this skill wrote that the table no longer wants are its own to remove.
    remove = {name: [] for name in LISTS}
    owned_after = {name: [] for name in NATIVE_LIST.values()}
    for name in NATIVE_LIST.values():
        for entry in owned.get(name, []):
            if desired.get(entry) == name:
                owned_after[name].append(entry)
            elif entry in existing[name]:
                remove[name].append(entry)
                section.changes.append(Change("removed", entry, name, note="written by set-up-machine, no longer in the table"))
        owned_after[name].extend(e for e in add[name] if e not in owned_after[name])

    owned_all = {e for name in NATIVE_LIST.values() for e in owned.get(name, [])}
    for name in LISTS:
        for entry in existing[name]:
            if entry not in desired and entry not in owned_all:
                section.changes.append(Change("extra", entry, name, note="not in the table; kept"))

    new = old
    if any(add.values()) or any(remove.values()):
        new_settings = copy.deepcopy(settings)
        new_perms = new_settings.setdefault("permissions", {})
        for name in LISTS:
            if add[name] or remove[name]:
                kept = [e for e in new_perms.get(name, []) if e not in remove[name]]
                new_perms[name] = kept + add[name]
        new = json.dumps(new_settings, indent=2, ensure_ascii=False) + "\n"
    return section, FileWrite(path, old, new), {k: v for k, v in owned_after.items() if v}


def _plan_instructions(home: Path, owned_imports: list, shared_file: Path, os_home: Path):
    path = config_dir(home) / "CLAUDE.md"
    old = read_text(path)
    line = import_line(home, os_home, shared_file)
    accepted = {line, "@" + str(shared_file.resolve()), "@" + str(shared_file)}
    section = Section(f"{LABEL}: global instructions", path)
    present = old is not None and any(l.strip() in accepted for l in old.splitlines())
    if present:
        section.changes.append(Change("present", f"import of {shared_file.name}"))
        return section, FileWrite(path, old, old), [i for i in owned_imports if i in (old or "")]
    section.changes.append(Change("added", line, note="imports the shared global instructions"))
    new = (old.rstrip("\n") + "\n\n" if old and old.strip() else "") + line + "\n"
    return section, FileWrite(path, old, new), sorted(set(owned_imports) | {line})
