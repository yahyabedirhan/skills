"""Claude Code adapter: permissions in settings.json, global instructions in CLAUDE.md.

Facts it relies on (see references/claude-code.md):
- `~/.claude/settings.json` holds `permissions.{allow, ask, deny}`; deny is checked
  first, then ask, then allow, so adding a stricter entry wins without removing a looser one.
- A `Bash(<prefix>:*)` rule matches the command text as written, so each spelling
  of a command needs its own entry.
- File rules are `Read(path)` and `Edit(path)`; `Write(path)` rules are accepted and never checked.
- MCP tools are named `mcp__<server>__<tool>`, and only the running harness knows
  which ones exist, so the adapter asks it at plan time.
- `~/.claude/CLAUDE.md` loads in every session and follows `@path` imports.
- Auto memory is on by default and writes `~/.claude/projects/<project>/memory/`;
  `"autoMemoryEnabled": false` in settings.json turns it off.
- `hooks.PreToolUse` runs before every tool call; a `deny` answer with a reason
  refuses it and shows the agent the reason, and an `allow` answer would skip the
  permission check, so the hook answers only `deny`.
"""
from __future__ import annotations

import copy
import fnmatch
import json
import shlex
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path

from .. import memory, shared
from .. import rules as rule_table
from ..plan import Change, FileWrite, Section
from ..shared import read_text

NAME = "claude-code"
LABEL = "Claude Code"

# Rule level -> the settings.json list that expresses it natively.
NATIVE_LIST = {"deny": "deny", "ask": "ask", "allow-and-report": "allow"}
# Settings lists, strictest first.
LISTS = ("deny", "ask", "allow")
# File access -> the rule kind Claude Code checks for it.
FILE_RULE = {"read": "Read", "write": "Edit"}
MEMORY_KEY = "autoMemoryEnabled"

DISCOVERY_TIMEOUT = 90

# The pre-tool hook this skill ships, and how long Claude Code gives it, in seconds.
HOOK_SCRIPT = Path(__file__).resolve().parents[2] / "pre_tool_hook.py"
HOOK_TIMEOUT = 10


def config_dir(home: Path) -> Path:
    return home / ".claude"


def entries_for(rule, tools=()) -> list:
    if rule.kind == "file":
        return [f"{FILE_RULE[rule.access]}({p if p.startswith('~/') else './' + p})" for p in rule.paths]
    if rule.kind == "mcp-tool":
        return rule_table.matching_tools(rule, tools)
    return [f"Bash({' '.join(prefix)}:*)" for prefix in rule_table.command_prefixes(rule)]


# What still gets past the pre-tool hook's reading of a command.
HOOK_MISSES = (
    "a command inside a script file or another interpreter (`python -c`), one built from variables (`$cmd`), "
    "an alias or function defined elsewhere, an abbreviated long option (`--recur`), "
    "or a force push by refspec (`git push origin +main`)"
)


def gaps_for(rule) -> list:
    """What gets through once this adapter's entries and the pre-tool hook are in place."""
    if rule.kind == "file":
        return [
            "Read and Edit rules cover Claude Code's file tools and the file commands it recognises in Bash "
            "(`cat`, `sed`, redirects), and the pre-tool hook the file tools; a script or another program "
            "opening the file gets through"
        ]
    if rule.kind == "mcp-tool":
        return []  # the native entries cover the tools found now, and the hook matches tools connected later
    if rule.level in ("deny", "allow-and-report"):
        return []  # the pre-tool hook reads every spelling; what it can't see is one gap in its own section
    canonical = " ".join(rule_table.command_prefixes(rule)[0])
    through = []
    if rule.flags:
        through.append("flags combined with others or placed after the operands")
    if any(rule.subcommands):
        through.append(f"options before the subcommand (`{rule.programs[0]} <option> {' '.join(rule.subcommands[0])}`)")
    through.append(f"the command inside another program's string (`bash -lc \"{canonical} …\"`, `eval`, a script)")
    return ["ask stays native, and Bash rules match the text as written, so these get through: " + "; ".join(through)]


def discover_tools():
    """The MCP tool names a Claude Code session on this machine exposes, from its init event.

    Returns (names, None), or (None, reason) when Claude Code can't be asked. The
    session is stopped as soon as it reports its tools, before it calls the model.
    """
    exe = shutil.which("claude")
    if not exe:
        return None, "the `claude` command isn't on PATH"
    cmd = [exe, "-p", "List nothing.", "--output-format", "stream-json", "--verbose",
           "--tools", "", "--no-session-persistence", "--max-turns", "1"]
    with tempfile.TemporaryDirectory() as cwd:
        try:
            proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        except OSError as exc:
            return None, f"couldn't start `claude`: {exc}"
        timer = threading.Timer(DISCOVERY_TIMEOUT, proc.kill)
        timer.start()
        try:
            for line in proc.stdout:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("type") == "system" and event.get("subtype") == "init":
                    return sorted(t for t in event.get("tools", []) if rule_table.split_mcp_name(t)), None
            return None, "`claude` ended without reporting its tools (is it logged in?)"
        finally:
            timer.cancel()
            proc.kill()
            proc.wait(timeout=DISCOVERY_TIMEOUT)


def covers(existing: str, wanted: str) -> bool:
    """Whether an entry already on the machine matches everything a wanted entry does."""
    if existing == wanted:
        return True
    if wanted.startswith("Bash(") and existing.startswith("Bash(") and existing.endswith(")"):
        want = _bash_literal(wanted)
        pattern = existing[len("Bash("):-1]
        if want is None:
            return False
        for suffix in (":*", " *"):
            if pattern.endswith(suffix) and "*" not in pattern[: -len(suffix)]:
                lit = pattern[: -len(suffix)]
                return want == lit or want.startswith(lit + " ")
        if pattern.endswith("*") and "*" not in pattern[:-1]:
            return want.startswith(pattern[:-1])
        return False
    if wanted.startswith("mcp__") and existing.startswith("mcp__"):
        parts = rule_table.split_mcp_name(wanted)
        if parts and existing == f"mcp__{parts[0]}":
            return True
        return "*" in existing and fnmatch.fnmatchcase(wanted, existing)
    return False


def _bash_literal(entry: str):
    """`Bash(rm -rf:*)` -> `rm -rf`, for the entries this adapter writes."""
    inner = entry[len("Bash("):-1]
    return inner[:-2] if inner.endswith(":*") and "*" not in inner[:-2] else None


def import_line(home: Path, os_home: Path, shared_file: Path) -> str:
    """`@~/…` when home is the user's own home, so the line reads the same on every machine."""
    try:
        if home.resolve() == os_home.resolve():
            return "@~/" + str(shared_file.relative_to(home))
    except ValueError:
        pass
    return "@" + str(shared_file.resolve())


def plan(home: Path, rules: list, owned: dict, shared_file: Path, os_home: Path, tools=None, rules_path=None):
    """Returns (sections, writes, owned_after) for Claude Code.

    `tools` is the list of MCP tool names to match mcp-tool rules against; when
    None and the table has such rules, Claude Code is asked for them. `rules_path`
    is the table the hook reads, when it isn't the skill's own.
    """
    tools_error = None
    if tools is None and any(r.kind == "mcp-tool" for r in rules):
        tools, tools_error = discover_tools()
    path = config_dir(home) / "settings.json"
    old = read_text(path)
    try:
        settings = json.loads(old) if old is not None else {}
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} isn't valid JSON ({exc}); fix it by hand, then run the plan again") from exc
    if not isinstance(settings, dict):
        raise ValueError(f"{path} must hold a JSON object; fix it by hand, then run the plan again")
    new_settings = copy.deepcopy(settings)
    perm_section, owned_perms = _plan_permissions(
        path, settings, new_settings, rules, owned.get("permissions", {}), tools or [], tools_error
    )
    hook_section, owned_hooks = _plan_hook(
        path, settings, new_settings, owned.get("hooks", []), hook_command(home, os_home, rules_path)
    )
    mem_section, mem_writes = _plan_memory(home, path, new_settings)
    new = old if new_settings == settings else json.dumps(new_settings, indent=2, ensure_ascii=False) + "\n"
    md_section, md_write, owned_imports = _plan_instructions(home, owned.get("imports", []), shared_file, os_home)
    owned_after = {}
    if any(owned_perms.values()):
        owned_after["permissions"] = owned_perms
    if owned_hooks:
        owned_after["hooks"] = owned_hooks
    if owned_imports:
        owned_after["imports"] = owned_imports
    return ([perm_section, hook_section, mem_section, md_section],
            [FileWrite(path, old, new), md_write, *mem_writes], owned_after)


def _plan_permissions(path: Path, settings: dict, new_settings: dict, rules: list, owned: dict, tools: list, tools_error):
    perms = settings.get("permissions", {})
    existing = {name: list(perms.get(name, [])) for name in LISTS}
    section = Section(f"{LABEL}: permissions", path)

    # Desired native entries, per list; where two rules overlap, the stricter level wins.
    desired, rule_of = {}, {}
    for rule in rules:
        if rule.kind == "mcp-tool":
            section.changes.append(_found(rule, tools, tools_error))
        for gap in gaps_for(rule):
            section.changes.append(Change("gap", gap, rule.level, rule.id))
        level = NATIVE_LIST[rule.level]
        for entry in entries_for(rule, tools):
            if entry not in desired or LISTS.index(level) < LISTS.index(desired[entry]):
                desired[entry], rule_of[entry] = level, rule.id

    add = {name: [] for name in LISTS}
    covering = set()
    for entry, level in desired.items():
        found = {}
        for name in LISTS:
            hit = next((e for e in existing[name] if covers(e, entry)), None)
            if hit is not None:
                found[name] = hit
        covering.update(found.values())
        at_or_above = [n for n in found if LISTS.index(n) <= LISTS.index(level)]
        if level in found:
            note = "" if found[level] == entry else f"covered by {found[level]}"
            section.changes.append(Change("present", entry, level, rule_of[entry], note))
        elif at_or_above:
            stricter = at_or_above[0]
            section.changes.append(Change(
                "stricter", entry, level, rule_of[entry],
                f"the machine has {found[stricter]} in {stricter}; kept, since set-up-machine never loosens. "
                f"Remove it by hand to get the table's {level}",
            ))
        elif found:
            add[level].append(entry)
            looser = next(iter(found))
            section.changes.append(Change("tightened", entry, level, rule_of[entry], f"was {looser}; {level} wins"))
        else:
            add[level].append(entry)
            section.changes.append(Change("added", entry, level, rule_of[entry]))

    # Entries this skill wrote that the table no longer wants are its own to remove.
    # When the tool list couldn't be read, the mail entries it wrote before stay.
    remove = {name: [] for name in LISTS}
    owned_after = {name: [] for name in LISTS}
    for name in LISTS:
        for entry in owned.get(name, []):
            if desired.get(entry) == name or (tools_error and entry.startswith("mcp__")):
                owned_after[name].append(entry)
            elif entry in existing[name]:
                remove[name].append(entry)
                section.changes.append(Change("removed", entry, name, note="written by set-up-machine, no longer in the table"))
        owned_after[name].extend(e for e in add[name] if e not in owned_after[name])

    owned_all = {e for name in LISTS for e in owned.get(name, [])}
    for name in LISTS:
        for entry in existing[name]:
            if entry not in desired and entry not in owned_all and entry not in covering:
                note = "not in the table; kept"
                if entry.startswith("Write("):
                    note = "Claude Code never checks Write rules, so this does nothing; the table's Edit rules do; kept"
                section.changes.append(Change("extra", entry, name, note=note))

    if any(add.values()) or any(remove.values()):
        new_perms = new_settings.setdefault("permissions", {})
        for name in LISTS:
            if add[name] or remove[name]:
                kept = [e for e in new_perms.get(name, []) if e not in remove[name]]
                new_perms[name] = kept + add[name]
    return section, {k: v for k, v in owned_after.items() if v}


def hook_command(home: Path, os_home: Path, rules_path=None) -> str:
    """The command that runs the pre-tool hook. Outside the user's own home it names that
    home's configuration, and with a table other than the skill's own it names that table."""
    parts = ["python3", str(HOOK_SCRIPT), "--harness", "claude-code"]
    if home.resolve() != os_home.resolve():
        parts += ["--config", str(shared.hook_config_path(home))]
    if rules_path is not None and Path(rules_path).resolve() != rule_table.DEFAULT_TABLE:
        parts += ["--rules", str(Path(rules_path).resolve())]
    return shlex.join(parts)


def _plan_hook(path: Path, settings: dict, new_settings: dict, owned: list, wanted: str):
    """Wire the pre-tool hook for every tool; replace only a hook command this skill wrote before."""
    section = Section(f"{LABEL}: pre-tool hook", path)
    if not isinstance(settings.get("hooks", {}), dict):
        raise ValueError(f"{path}: `hooks` must be a JSON object; fix it by hand, then run the plan again")
    groups = _pre_tool_groups(settings)
    wired = any(
        g.get("matcher") in ("*", "", None) and any(h.get("command") == wanted for h in _handlers(g)) for g in groups
    )
    stale = {c for c in owned if c != wanted}
    present = {h.get("command") for g in groups for h in _handlers(g)}
    if (stale & present) or not wired:
        new_groups = []
        for g in _pre_tool_groups(new_settings):
            handlers = [h for h in _handlers(g) if h.get("command") not in stale]
            if len(handlers) != len(_handlers(g)):
                g = {**g, "hooks": handlers}
            if handlers:
                new_groups.append(g)
        for command in sorted(stale & present):
            section.changes.append(Change("removed", f"pre-tool hook: {command}",
                                          note="written by set-up-machine; the hook script moved"))
        if not wired:
            new_groups.append({"matcher": "*", "hooks": [{"type": "command", "command": wanted, "timeout": HOOK_TIMEOUT}]})
            section.changes.append(Change(
                "added", f"pre-tool hook: {wanted}",
                note="refuses the table's deny rules however a command is spelled, and reports allow-and-report calls",
            ))
        new_settings.setdefault("hooks", {})["PreToolUse"] = new_groups
    else:
        section.changes.append(Change("wired", f"pre-tool hook wired for every tool: {wanted}"))
    if settings.get("disableAllHooks") is True:
        section.changes.append(Change(
            "gap", "`disableAllHooks` is true in this file, so no hook runs, this one included; set-up-machine leaves it to you"
        ))
    section.changes.append(Change("gap", f"the hook reads every spelling of a command, but can't see {HOOK_MISSES}"))
    section.changes.append(Change(
        "gap", "a project's `.claude/settings.json` can set `disableAllHooks: true`, which turns the hook off there; "
               "the native permissions still hold"
    ))
    return section, [wanted]


def _pre_tool_groups(settings: dict) -> list:
    hooks = settings.get("hooks")
    groups = hooks.get("PreToolUse") if isinstance(hooks, dict) else None
    return [g for g in groups if isinstance(g, dict)] if isinstance(groups, list) else []


def _handlers(group: dict) -> list:
    handlers = group.get("hooks")
    return [h for h in handlers if isinstance(h, dict)] if isinstance(handlers, list) else []




def _found(rule, tools: list, tools_error) -> Change:
    if tools_error:
        return Change("gap", f"couldn't list Claude Code's MCP tools: {tools_error}; this rule isn't applied",
                      rule.level, rule.id)
    names = rule_table.matching_tools(rule, tools)
    text = ", ".join(names) if names else f"none among the {len(tools)} MCP tools Claude Code exposes"
    return Change("found", text, rule.level, rule.id)


def _plan_memory(home: Path, path: Path, new_settings: dict):
    """Auto memory off in the same settings.json write as the permissions and the hook, and every memory file removed."""
    section = Section(f"{LABEL}: memory", path)
    value = new_settings.get(MEMORY_KEY)
    if value is False:
        section.changes.append(Change("present", f"{MEMORY_KEY}: false"))
    else:
        kind, note = ("added", "auto memory off") if value is None else ("tightened", f"was {json.dumps(value)}")
        section.changes.append(Change(kind, f"{MEMORY_KEY}: false", note=note))
        new_settings[MEMORY_KEY] = False
    section.changes.append(Change(
        "gap", f"a project's .claude/settings.json can set {MEMORY_KEY}: true and win over this; the project audit checks it",
    ))
    folders = sorted((config_dir(home) / "projects").glob("*/memory"))
    return section, memory.remove_files(home, folders, section)


def _plan_instructions(home: Path, owned_imports: list, shared_file: Path, os_home: Path):
    path = config_dir(home) / "CLAUDE.md"
    old = read_text(path)
    line = import_line(home, os_home, shared_file)
    accepted = {line, "@" + str(shared_file.resolve()), "@" + str(shared_file)}
    section = Section(f"{LABEL}: global instructions", path)
    present = old is not None and any(l.strip() in accepted for l in old.splitlines())
    others = [l for l in (old or "").splitlines() if l.strip() and l.strip() not in accepted]
    if others:
        section.changes.append(Change(
            "extra", f"{len(others)} line(s) besides the import", note="kept; move them into the shared file, "
            "which every harness reads: references/global-instructions.md",
        ))
    if present:
        section.changes.append(Change("present", f"import of {shared_file.name}"))
        return section, FileWrite(path, old, old), [i for i in owned_imports if i in (old or "")]
    section.changes.append(Change("added", line, note="imports the shared global instructions"))
    new = (old.rstrip("\n") + "\n\n" if old and old.strip() else "") + line + "\n"
    return section, FileWrite(path, old, new), sorted(set(owned_imports) | {line})
