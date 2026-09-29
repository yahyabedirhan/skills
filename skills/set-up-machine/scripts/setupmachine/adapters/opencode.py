"""opencode adapter: permission rules in opencode.json, the hook as a plugin, global instructions by symlink.

Facts it relies on (see references/opencode.md):
- The global config folder is `~/.config/opencode/`; `config.json`, `opencode.json` and
  `opencode.jsonc` there all load, in that order, so the last one that exists wins.
- `permission` maps a tool name (a wildcard) to a level, or to `{pattern: level}`; rules are
  flattened in the order written and the last match wins. `*` matches anything, and a
  trailing ` *` also matches the bare command.
- Bash patterns are matched against each command of a compound (`a && rm -rf x`), as written.
- `read` and `edit` patterns match the path relative to the project; paths outside it go
  through `external_directory`, where `~/` is expanded.
- MCP tools are named `<server>_<tool>`, and opencode lists them only in a running session.
- A plugin's `tool.execute.before` runs before every tool call; a throw refuses the call,
  and the agent reads the error's message as the tool's result.
- `~/.config/opencode/AGENTS.md` is the global instructions file (else `~/.claude/CLAUDE.md`);
  it doesn't follow `@` imports, so it's a symlink to the shared file.
- opencode has no memory feature.
"""
from __future__ import annotations

import copy
import json
import os
import re
import shlex
from pathlib import Path

from .. import rules as rule_table
from ..plan import Change, FileWrite, Section, link_text
from ..shared import read_text
from . import claude_code

NAME = "opencode"
LABEL = "opencode"

# Global config files, in the order opencode loads them.
CONFIG_FILES = ("config.json", "opencode.json", "opencode.jsonc")
LEVELS = ("allow", "ask", "deny")  # loosest first
NATIVE_LEVEL = {"deny": "deny", "ask": "ask", "allow-and-report": "allow"}
FILE_GROUP = {"read": "read", "write": "edit"}
# Builtins tree-sitter-bash parses as declarations, which opencode's bash check never matches (probed: `export -p`).
DECLARATIONS = {"export", "declare", "typeset", "local", "readonly"}

PLUGIN_NAME = "set-up-machine.js"
PLUGIN_MARKER = "// set-up-machine: the pre-tool hook, as an opencode plugin."
HOOK_TIMEOUT_MS = 10_000

SHARED_LINK = Path("..") / "agents" / "AGENTS.md"  # from ~/.config/opencode/ to ~/.config/agents/


def config_dir(home: Path) -> Path:
    return home / ".config" / "opencode"


def config_path(home: Path) -> Path:
    """The global config file set-up-machine writes: the last one opencode loads, else a new opencode.json."""
    existing = [config_dir(home) / n for n in CONFIG_FILES if (config_dir(home) / n).exists()]
    return existing[-1] if existing else config_dir(home) / "opencode.json"


# --- native rules ---------------------------------------------------------------


def entries_for(rule) -> list:
    """(tool, pattern) pairs expressing a row in opencode's permission config."""
    if rule.kind == "command":
        if rule.files:
            return []  # bash patterns match the command text, not the paths in it; the hook covers these
        tail = "" if rule.bare else " *"  # a bare row is the program alone; ` *` also matches it alone
        return [("bash", " ".join(prefix) + tail) for prefix in rule_table.command_prefixes(rule)]
    if rule.kind == "file":
        return [entry for glob in rule.paths for entry in _file_entries(rule, glob)]
    return []  # MCP tools: see _found


def exceptions_for(rule) -> list:
    """(tool, pattern) pairs that reopen a file row's `except` globs: opencode has no negation,
    but the last matching rule wins, so an `allow` after the deny entries leaves them out."""
    return [entry for glob in rule.excepts for entry in _file_entries(rule, glob)] if rule.kind == "file" else []


def _file_entries(rule, glob: str) -> list:
    if glob.startswith("~/"):
        return [("external_directory", _flatten_glob(glob))]
    tool = FILE_GROUP[rule.access]
    if glob.startswith("**/"):
        rest = _flatten_glob(glob[3:])
        return [(tool, rest), (tool, "*/" + rest)]  # `*/` alone would miss the project's own folder
    return [(tool, _flatten_glob(glob))]


def _flatten_glob(glob: str) -> str:
    """opencode's `*` already crosses `/`, so `**` is `*`."""
    return glob.replace("**", "*")


def wildcard(text: str, pattern: str) -> bool:
    """opencode's pattern match (util/wildcard.ts): `*` any text, `?` one character,
    and a trailing ` *` that also matches nothing."""
    rx = "".join(".*" if c == "*" else "." if c == "?" else re.escape(c) for c in pattern)
    if rx.endswith(r"\ .*"):
        rx = rx[: -len(r"\ .*")] + "( .*)?"
    return re.fullmatch(rx, text, re.S) is not None


def samples(pattern: str) -> list:
    """Texts a pattern is written to match, to ask which rule opencode would apply to them."""
    if pattern.endswith(" *"):
        return [pattern[:-2], pattern[:-1] + "x"]
    return [pattern.replace("*", "x").replace("?", "x")]


def flatten(permission: dict) -> list:
    """(tool, pattern, level) in opencode's order."""
    out = []
    for tool, value in permission.items():
        if isinstance(value, str):
            out.append((tool, "*", value))
        elif isinstance(value, dict):
            out += [(tool, p, v) for p, v in value.items() if isinstance(v, str)]
    return out


def effective(permission: dict, tool: str, text: str, home: Path):
    """The (tool, pattern, level) opencode applies to `text` for `tool`: the last that matches."""
    text = _expand(text, home)
    for rule in reversed(flatten(permission)):
        if rule[2] in LEVELS and wildcard(tool, rule[0]) and wildcard(text, _expand(rule[1], home)):
            return rule
    return None


def _expand(pattern: str, home: Path) -> str:
    return str(home) + pattern[1:] if pattern == "~" or pattern.startswith("~/") else pattern


def _rank(level) -> int:
    return LEVELS.index(level) if level in LEVELS else -1


def _shown(tool: str, pattern: str) -> str:
    return tool if pattern == "*" else f"{tool} {json.dumps(pattern)}"


# --- JSON with comments -----------------------------------------------------------


def parse_jsonc(text: str):
    """opencode's config as data, and whether it held comments (which a rewrite would drop)."""
    out, i, had_comments, n = [], 0, False, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1])
            i = j + 1
        elif text.startswith("//", i):
            had_comments = True
            i = text.find("\n", i) if "\n" in text[i:] else n
        elif text.startswith("/*", i):
            had_comments = True
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
        else:
            out.append(c)
            i += 1
    stripped = re.sub(r",(\s*[}\]])", r"\1", "".join(out))  # trailing commas; strings are intact
    return json.loads(stripped) if stripped.strip() else {}, had_comments


# --- plan -------------------------------------------------------------------------


def plan(home: Path, rules: list, owned: dict, shared_file: Path, os_home: Path, tools=None, rules_path=None):
    """Returns (sections, writes, owned_after) for opencode. `tools` isn't used: opencode
    lists its MCP tools only inside a session, so mail rows are matched against the
    configured MCP servers and left to the pre-tool hook."""
    mem_section = Section(f"{LABEL}: memory", config_dir(home))
    mem_section.changes.append(Change("none", "no memory feature; nothing to turn off"))
    if not config_dir(home).is_dir():
        section = Section(LABEL, config_dir(home))
        section.changes.append(Change("none", "opencode isn't set up here (no ~/.config/opencode); nothing to set"))
        return [section, mem_section], [], {}
    path = config_path(home)
    old = read_text(path)
    try:
        config, had_comments = parse_jsonc(old) if old is not None else ({}, False)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} isn't valid JSON ({exc}); fix it by hand, then run the plan again") from exc
    if not isinstance(config, dict):
        raise ValueError(f"{path} must hold a JSON object; fix it by hand, then run the plan again")

    new_config = copy.deepcopy(config)
    perm_section, owned_perms = _plan_permissions(home, path, config, new_config, rules, owned.get("permissions", {}))
    writes = []
    if new_config != config and had_comments:
        perm_section.changes = [c for c in perm_section.changes if c.kind not in ("added", "tightened", "removed")]
        perm_section.changes.insert(0, Change(
            "gap", f"{path.name} has comments, which rewriting it would drop, so these rules aren't applied; "
                   "move the comments out (or into a `$comment` key) and run the plan again"))
        owned_perms = owned.get("permissions", {})
    else:
        new = old if new_config == config else json.dumps(new_config, indent=2, ensure_ascii=False) + "\n"
        writes.append(FileWrite(path, old, new))

    hook_section, hook_write, owned_plugin = _plan_hook(home, os_home, rules_path, owned.get("plugin", []))
    md_section, md_write, owned_links = _plan_instructions(home, shared_file, owned.get("links", []))

    owned_after = {}
    if owned_perms:
        owned_after["permissions"] = owned_perms
    if owned_plugin:
        owned_after["plugin"] = owned_plugin
    if owned_links:
        owned_after["links"] = owned_links
    writes += [w for w in (hook_write, md_write) if w is not None]
    return [perm_section, hook_section, mem_section, md_section], writes, owned_after


def _plan_permissions(home: Path, path: Path, config: dict, new_config: dict, rules: list, owned: dict):
    section = Section(f"{LABEL}: permissions", path)
    perm = config.get("permission", {})
    if isinstance(perm, str):
        perm = {"*": perm}
    if not isinstance(perm, dict):
        raise ValueError(f"{path}: `permission` must be a level or a JSON object; fix it by hand, then run the plan again")
    current = copy.deepcopy(perm)

    # Desired entries; where two rows overlap, the stricter level wins.
    desired, rule_of, exceptions = {}, {}, {}
    for rule in rules:
        if rule.kind == "mcp-tool":
            section.changes.append(_found(rule, config))
        for gap in gaps_for(rule):
            section.changes.append(Change("gap", gap, rule.level, rule.id))
        if rule.guard:
            section.changes.append(Change(
                "none", f"no semantic guard to hold this row's `{rule.guard.split(':', 1)[0]}` rule; "
                        "the deny rules and the hook are the whole cover", rule.level, rule.id))
        level = NATIVE_LEVEL[rule.level]
        for entry in entries_for(rule):
            if _rank(level) > _rank(desired.get(entry)):
                desired[entry], rule_of[entry] = level, rule.id
        for entry in exceptions_for(rule):
            exceptions[entry] = rule.id
    wanted = set(desired) | set(exceptions)

    # Entries this skill wrote that the table no longer wants are its own to remove.
    for tool, patterns in owned.items():
        for pattern in patterns:
            if (tool, pattern) not in wanted and isinstance(current.get(tool), dict) and pattern in current[tool]:
                section.changes.append(Change("removed", _shown(tool, pattern), current[tool][pattern],
                                              note="written by set-up-machine, no longer in the table"))
                del current[tool][pattern]

    # Loosest first, so where entries overlap the stricter one sits later and wins.
    owned_after, covering = {}, set()
    for (tool, pattern), level in sorted(desired.items(), key=lambda kv: _rank(kv[1])):
        rule_id = rule_of[(tool, pattern)]
        mine = pattern in owned.get(tool, [])
        hits = [effective(current, tool, s, home) for s in samples(pattern)]
        if all(h is not None and _rank(h[2]) >= _rank(level) for h in hits):
            covering.update((h[0], h[1]) for h in hits)
            loosest = min(hits, key=lambda h: _rank(h[2]))
            if loosest[2] == level:
                note = "" if (loosest[0], loosest[1]) == (tool, pattern) else f"covered by {_shown(loosest[0], loosest[1])}"
                section.changes.append(Change("present", _shown(tool, pattern), level, rule_id, note))
            else:
                section.changes.append(Change(
                    "stricter", _shown(tool, pattern), level, rule_id,
                    f"the machine has {_shown(loosest[0], loosest[1])} at {loosest[2]}; kept, since set-up-machine "
                    f"never loosens. Remove it by hand to get the table's {level}"))
            if mine:
                owned_after.setdefault(tool, []).append(pattern)
            continue
        group = current.get(tool)
        existed = isinstance(group, dict) and pattern in group
        looser = next((h for h in hits if h is not None and _rank(h[2]) < _rank(level)), None)
        if existed and group[pattern] == level:
            kind, note = "tightened", "a later entry overrode it; moved to the end"
        elif existed:
            kind, note = "tightened", f"was {group[pattern]}; moved to the end at {level}"
        elif looser is not None:
            kind, note = "tightened", f"{_shown(looser[0], looser[1])} allowed it at {looser[2]}; this entry comes after it and wins"
        else:
            kind, note = "added", ""
        _append(current, tool, pattern, level)
        if not all(_rank(effective(current, tool, s, home)[2]) >= _rank(level) for s in samples(pattern)):
            current[tool] = current.pop(tool)  # a later tool-wide entry overrides it: move this tool's rules after it
            note = (note + "; " if note else "") + f"`{tool}` moved to the end, after the entries that overrode it"
        section.changes.append(Change(kind, _shown(tool, pattern), level, rule_id, note))
        if mine or not existed:
            owned_after.setdefault(tool, []).append(pattern)

    # A row's exceptions: an `allow` after its deny entries reopens them, as opencode's own
    # defaults do for `.env.example`. Where the user's own entry refuses one, it stays refused.
    owned_all = {(t, p) for t, ps in owned.items() for p in ps}
    ours = wanted | owned_all
    for (tool, pattern), rule_id in exceptions.items():
        hits = [effective(current, tool, s, home) for s in samples(pattern)]
        blocking = [h for h in hits if h is not None and h[2] != "allow"]
        if not blocking:
            covering.update((h[0], h[1]) for h in hits if h is not None)
            section.changes.append(Change("present", _shown(tool, pattern), "allow", rule_id))
            if pattern in owned.get(tool, []):
                owned_after.setdefault(tool, []).append(pattern)
            continue
        theirs = next((h for h in blocking if (h[0], h[1]) not in ours), None)
        if theirs is not None:
            section.changes.append(Change(
                "stricter", _shown(tool, pattern), "allow", rule_id,
                f"the row leaves it open, but the machine's {_shown(theirs[0], theirs[1])} refuses it at {theirs[2]}; "
                "kept, since set-up-machine never loosens. Remove that entry by hand to open it"))
            continue
        _append(current, tool, pattern, "allow")
        section.changes.append(Change("added", _shown(tool, pattern), "allow", rule_id,
                                      "the row's exception, after its deny entries so it wins"))
        owned_after.setdefault(tool, []).append(pattern)

    for tool, pattern, level in flatten(perm):
        if (tool, pattern) not in wanted and (tool, pattern) not in owned_all and (tool, pattern) not in covering:
            section.changes.append(Change("extra", _shown(tool, pattern), level, note="not in the table; kept"))

    section.changes.append(Change(
        "gap", "a project's opencode.json can loosen any of these: a pattern new to the project comes after them "
               "and wins, and the same pattern there replaces the level; only managed config holds. "
               "set-up-project's audit checks each project"))
    section.changes.append(Change(
        "gap", "an agent's own `permission` (in a config's `agent` key or an agent file) comes after these and wins"))
    if current != perm:
        new_config["permission"] = current
    return section, owned_after


def _append(permission: dict, tool: str, pattern: str, level: str):
    group = permission.get(tool)
    if isinstance(group, str):
        group = {"*": group}  # the same rule, written as a pattern, so the new one can follow it
    elif not isinstance(group, dict):
        group = {}
    group.pop(pattern, None)
    group[pattern] = level
    permission[tool] = group


# What still gets past the pre-tool hook's reading of a command.
HOOK_MISSES = claude_code.HOOK_MISSES


def gaps_for(rule) -> list:
    """What gets through once these rules and the pre-tool hook are in place, the row's own gap last."""
    return _native_gaps(rule) + ([rule.gap] if rule.gap else [])


def _native_gaps(rule) -> list:
    if rule.kind == "file":
        if all(g.startswith("~/") for g in rule.paths):
            return ["`external_directory` covers opencode's file tools and the file arguments of bash commands "
                    "outside the project; a session whose project is the home folder itself, or a program that opens "
                    "the file on its own, gets through"]
        tool = FILE_GROUP[rule.access]
        return [f"`{tool}` rules and the pre-tool hook cover opencode's file tools; a bash command "
                "(`sed`, `echo … >`), a script or another program opening the file gets through"]
    if rule.kind == "command" and rule.files:
        return ["bash patterns match the command text, not the paths in it, so this row has no native entry: "
                "only the pre-tool hook refuses it, and with the hook off (`--pure`) it runs"]
    declared = [p for p in rule.programs if p in DECLARATIONS]
    if rule.kind == "command" and declared:
        return [f"opencode checks plain commands only, so a declaration ({', '.join(f'`{p}`' for p in declared)}) "
                "never meets these patterns: only the pre-tool hook refuses it, and with the hook off (`--pure`) it runs"]
    if rule.kind == "mcp-tool" or rule.level in ("deny", "allow-and-report"):
        return []  # the pre-tool hook reads every spelling and every tool; its misses are in its own section
    canonical = " ".join(rule_table.command_prefixes(rule)[0])
    through = []
    if rule.flags:
        through.append("flags combined with others or placed after the operands")
    if any(rule.subcommands):
        through.append(f"options before the subcommand (`{rule.programs[0]} <option> {' '.join(rule.subcommands[0])}`)")
    through.append(f"the command inside another program's string (`bash -lc \"{canonical} …\"`, `eval`, a script)")
    return ["ask stays native, and opencode matches each command's text as written, so these get through: "
            + "; ".join(through)]


def _found(rule, config: dict) -> Change:
    servers = sorted(config.get("mcp", {})) if isinstance(config.get("mcp"), dict) else []
    matched = [s for s in servers if re.search(rule.server, s, re.I)]
    if not matched:
        return Change("found", f"no MCP server in opencode's global config matches `{rule.server}`", rule.level, rule.id)
    return Change(
        "gap", f"MCP server(s) {', '.join(matched)} match; opencode lists their tools only inside a session, "
               "so there's no native entry, and the pre-tool hook refuses the matching tools when called",
        rule.level, rule.id)


# --- pre-tool hook ------------------------------------------------------------------


def plugin_source(command: list) -> str:
    """A plugin that hands every tool call to the pre-tool hook and throws its refusal."""
    return f"""{PLUGIN_MARKER}
// Generated by set-up-machine; apply rewrites it. Change the skill, not this file.
// Every tool call goes to the hook first; a refusal is thrown, which stops the call and shows the agent why.
// The hook fails open: if it can't run or read the call, opencode's own permission rules still decide.
import {{ spawn }} from "node:child_process";

const COMMAND = {json.dumps(command)};
const TIMEOUT_MS = {HOOK_TIMEOUT_MS};

function runHook(payload) {{
  return new Promise((resolve) => {{
    let out = "";
    let child;
    try {{
      child = spawn(COMMAND[0], COMMAND.slice(1), {{ stdio: ["pipe", "pipe", "ignore"] }});
    }} catch {{
      return resolve({{ code: null, out: "" }});
    }}
    const timer = setTimeout(() => child.kill(), TIMEOUT_MS);
    child.stdout.on("data", (chunk) => (out += chunk));
    child.on("error", () => {{ clearTimeout(timer); resolve({{ code: null, out: "" }}); }});
    child.on("close", (code) => {{ clearTimeout(timer); resolve({{ code, out }}); }});
    child.stdin.on("error", () => {{}});
    child.stdin.end(payload);
  }});
}}

export const SetUpMachinePreToolHook = async ({{ directory }}) => ({{
  "tool.execute.before": async (input, output) => {{
    const payload = JSON.stringify({{ tool: input.tool, sessionID: input.sessionID, args: output.args, directory }});
    const {{ code, out }} = await runHook(payload);
    if (code === 0 && out.trim()) throw new Error(out.trim());
  }},
}});
"""


def _plan_hook(home: Path, os_home: Path, rules_path, owned: list):
    path = config_dir(home) / "plugins" / PLUGIN_NAME
    command = claude_code.hook_command(home, os_home, rules_path, harness=NAME)
    wanted = plugin_source(shlex.split(command))
    old = read_text(path)
    section = Section(f"{LABEL}: pre-tool hook", path)
    shown = "<home>/" + str(path.relative_to(home))
    write = None
    if old == wanted:
        section.changes.append(Change("wired", f"pre-tool hook wired for every tool, as the plugin {shown}: {command}"))
    elif old is not None and not old.startswith(PLUGIN_MARKER) and str(path) not in owned:
        section.changes.append(Change(
            "gap", f"{shown} is someone else's file, so the hook isn't wired; rename it and run the plan again"))
        return section, None, []
    else:
        note = "refuses the table's deny rules however a command is spelled, and reports allow-and-report calls"
        if old is not None:
            note = "replaces the plugin set-up-machine wrote before; the hook command changed"
        section.changes.append(Change("added", f"pre-tool hook plugin {shown}: {command}", note=note))
        write = FileWrite(path, old, wanted)
    section.changes.append(Change("gap", f"the hook reads every spelling of a command, but can't see {HOOK_MISSES}"))
    section.changes.append(Change(
        "gap", "a project's plugin runs after this one and can rewrite a call's arguments once the hook has passed "
               "them, and `--pure` or OPENCODE_PURE starts opencode without plugins; the native rules still hold"))
    return section, write, [str(path)]


# --- global instructions --------------------------------------------------------------


def _plan_instructions(home: Path, shared_file: Path, owned: list):
    path = config_dir(home) / "AGENTS.md"
    section = Section(f"{LABEL}: global instructions", path)
    target = os.path.relpath(shared_file, path.parent)
    if path.is_symlink() and path.resolve() == shared_file.resolve():
        section.changes.append(Change("present", f"AGENTS.md links to {shared_file.name}"))
        return section, None, [str(path)] if str(path) in owned else []
    if path.is_symlink() or path.exists():
        text = read_text(path) if path.exists() else None
        count = len([l for l in (text or "").splitlines() if l.strip()])
        section.changes.append(Change(
            "extra", f"opencode's own AGENTS.md ({count} line(s)" + (f", a link to {os.readlink(path)}" if path.is_symlink() else "") + ")",
            note="kept; move its lines into the shared file (references/global-instructions.md), "
                 "then delete it and run the plan again to link it"))
        section.changes.append(Change("gap", "until then opencode reads that file, not the shared global instructions"))
        return section, None, []
    section.changes.append(Change(
        "added", f"AGENTS.md -> {target}",
        note="opencode reads the shared global instructions instead of falling back to ~/.claude/CLAUDE.md, "
             "whose `@` import it wouldn't follow"))
    return section, FileWrite(path, None, link_text(Path(target)), link_to=Path(target)), [str(path)]
