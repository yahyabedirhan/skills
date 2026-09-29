"""The project audit: which project files weaken a global rule, harness by harness.

Global rules are the machine's safety rails; a project's own harness files may
only add convenience (allow entries for its own commands). This module reads
each harness's project files and reports, per entry:

- `weakens`: a global rule is weaker in some harness because of it (the audit fails);
- `overlaps`: a project allow covers a global rule's command, and the rule still
  holds everywhere (listed for the user to narrow or drop);
- `extra`: a project deny or ask, a rail kept in the project instead of the table;
- `gap`: something the audit can't judge, such as a project plugin.

It reads set-up-machine's rule table and adapters, so a rule covers the same
commands here as on the machine. The facts per harness are in
references/project-files.md.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from setupmachine import rules as rule_table
from setupmachine.adapters import opencode
from setupmachine.plan import Change, Section

GUARDED = ("deny", "ask")  # the levels a project can weaken
SKIP_DIRS = {".git", "node_modules", ".scratch", ".venv", "venv", "__pycache__", "worktrees"}

_TOOL = re.compile(r"^\s*([A-Za-z_]+)\s*(?:\((.*)\))?\s*$", re.S)


# --- what a rule covers, as concrete samples ------------------------------------


def file_samples(globs) -> list:
    """Paths a glob list is written to cover, relative to the project or starting `~/`."""
    out = []
    for glob in globs:
        variants = [glob[3:], "sub/" + glob[3:]] if glob.startswith("**/") else [glob]
        out += [v.replace("**", "key").replace("*", "local").replace("?", "x") for v in variants]
    return out


def command_samples(rule) -> list:
    """Command lines the row covers: every spelling it expands to, with an operand after it."""
    if rule.files:
        return [f"{p} {f}" for p in rule.programs for f in file_samples(rule.files)]
    tail = "" if rule.bare else " x"
    return [" ".join(prefix) + tail for prefix in rule_table.command_prefixes(rule)]


def _glob(text: str, pattern: str) -> bool:
    """A glob where `*` matches anything, `/` and spaces included, and nothing else is special."""
    rx = "".join(".*" if c == "*" else re.escape(c) for c in pattern)
    return re.fullmatch(rx, text, re.S) is not None


def _mcp_hits(rule, server: str, tool: str) -> bool:
    """Whether an MCP pattern (server part, tool part; `*` wildcards) can name a tool the row covers."""
    def hits(regex, part):
        return part in ("", "*") or re.search(regex, part.replace("*", ""), re.I) is not None
    return hits(rule.server, server) and hits(rule.tool, tool)


def _parse_entry(entry: str):
    m = _TOOL.match(entry) if isinstance(entry, str) else None
    return (m.group(1), m.group(2)) if m else (None, None)


# --- Claude Code entries (read by Claude Code and by the Cursor CLI) ------------------


def claude_entry_covers(entry: str, rule, home: Path) -> bool:
    """Whether a Claude Code permission entry covers something the row covers."""
    if rule.kind == "mcp-tool":
        name = entry.strip()
        if not name.startswith("mcp__"):
            return False
        server, _, tool_part = name[len("mcp__"):].partition("__")
        return _mcp_hits(rule, server, tool_part)  # `mcp__<server>` alone names every tool
    tool, inner = _parse_entry(entry)
    if tool is None:
        return False
    if rule.kind == "file":
        wanted = {"read": ("Read",), "write": ("Edit", "Write")}[rule.access]
        if tool not in wanted:
            return False
        if inner is None or inner.strip() in ("", "*", "**"):
            return True
        return any(_claude_path_covers(inner.strip(), p, home) for p in file_samples(rule.paths))
    if tool != "Bash":
        return False
    if inner is None or inner.strip() in ("", "*"):
        return True
    pattern = inner.strip()
    if pattern.endswith(":*"):
        pattern = pattern[:-2] + " *"
    return any(opencode.wildcard(s, pattern) for s in command_samples(rule))


def _claude_path_covers(pattern: str, sample: str, home: Path) -> bool:
    if pattern.startswith("~/") != sample.startswith("~/"):
        return False
    if pattern.startswith("~/"):
        return rule_table.glob_regex(pattern, "/", home).match(str(home) + sample[1:]) is not None
    glob = pattern[2:] if pattern.startswith("./") else pattern.lstrip("/")
    if "/" not in glob.rstrip("/"):
        glob = "**/" + glob  # no slash: any depth, as in .gitignore
    return rule_table.glob_regex(glob, "/project", home).match("/project/" + sample) is not None


# --- Cursor CLI entries ---------------------------------------------------------------


def cursor_entry_covers(entry: str, rule, home: Path) -> bool:
    """Whether a Cursor CLI permission entry (`Shell(…)`, `Bash(…)`, `Read`, `Write`, `Mcp`) covers the row."""
    tool, inner = _parse_entry(entry)
    if tool is None:
        return False
    inner = (inner or "").strip()
    if rule.kind == "mcp-tool":
        if tool != "Mcp":
            return False
        server, _, name = inner.partition(":")
        return _mcp_hits(rule, server.strip(), name.strip())
    if rule.kind == "file":
        wanted = {"read": ("Read",), "write": ("Write",)}[rule.access]
        if tool not in wanted:
            return False
        pattern = str(home) + inner[1:] if inner.startswith("~/") else inner
        return any(_glob(str(home) + s[1:] if s.startswith("~/") else "/project/" + s, pattern)
                   for s in file_samples(rule.paths))
    if tool not in ("Shell", "Bash"):
        return False
    return any(cursor_shell_matches(inner, s) for s in command_samples(rule))


def cursor_shell_matches(pattern: str, text: str) -> bool:
    """The CLI's Shell matching (references/cursor.md): `p` is `p` alone or followed by a space,
    `p:` is `p` alone, `cmd:args` a one-word command whose arguments match the glob."""
    if ":" in pattern:
        command, _, args = pattern.partition(":")
        command, args = command.strip(), args.strip()
        if " " in command:
            return text == command  # `Bash(rm -rf:*)` matches only the bare command there
        first, _, rest = text.partition(" ")
        if not _glob(first, command):
            return False
        return rest == "" if args == "" else _glob(rest, args)
    return _glob(text, pattern) or _glob(text, pattern + " *")


# --- reading project files ------------------------------------------------------------


def _read_json(path: Path, section: Section, jsonc: bool = False):
    try:
        text = path.read_text()
    except OSError as exc:
        section.changes.append(Change("gap", f"can't read {path.name}: {exc}"))
        return None
    try:
        data = opencode.parse_jsonc(text)[0] if jsonc else json.loads(text)
    except (json.JSONDecodeError, ValueError) as exc:
        section.changes.append(Change("gap", f"{path.name} isn't valid JSON ({exc}); the audit can't read it"))
        return None
    if not isinstance(data, dict):
        section.changes.append(Change("gap", f"{path.name} doesn't hold a JSON object; the audit can't read it"))
        return None
    return data


def _entries(value) -> list:
    return [e for e in value if isinstance(e, str)] if isinstance(value, list) else []


def _nested(project: Path, rel: str) -> list:
    """Every `<folder>/<rel>` from the project root down, skipping dependency and scratch folders."""
    found = []
    for folder, dirs, _ in os.walk(project):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        candidate = Path(folder) / rel
        if candidate.is_file():
            found.append(candidate)
    return found


# --- per harness ----------------------------------------------------------------------


def audit(project: Path, home: Path, rules: list) -> list:
    """One Section per project file that a harness reads for permissions, hooks or memory."""
    sections = []
    sections += audit_claude(project, home, rules)
    sections += audit_cursor(project, home, rules)
    sections += audit_opencode(project, home, rules)
    sections += audit_codex(project)
    return sections


def _classifies_all_shell(home: Path) -> bool:
    try:
        settings = json.loads((home / ".claude" / "settings.json").read_text())
    except (OSError, json.JSONDecodeError):
        return False
    auto = settings.get("autoMode") if isinstance(settings, dict) else None
    return isinstance(auto, dict) and auto.get("classifyAllShell") is True


def audit_claude(project: Path, home: Path, rules: list) -> list:
    sections = []
    classify_all = _classifies_all_shell(home)
    for rel in (".claude/settings.json", ".claude/settings.local.json"):
        path = project / rel
        if not path.is_file():
            continue
        cursor_reads = rel == ".claude/settings.json"  # the Cursor CLI reads this one, not the local file
        section = Section("Claude Code and the Cursor CLI" if cursor_reads else "Claude Code", path)
        sections.append(section)
        data = _read_json(path, section)
        if data is None:
            continue
        if data.get("disableAllHooks") is True:
            section.changes.append(Change(
                "weakens", '"disableAllHooks": true',
                note="turns off every hook in Claude Code, the pre-tool hook included, so only native entries hold"))
        if data.get("autoMemoryEnabled") is True:
            section.changes.append(Change(
                "weakens", '"autoMemoryEnabled": true', note="turns Claude Code's auto memory back on; memory stays off"))
        if data.get("disableAutoMode") not in (None, False):
            section.changes.append(Change(
                "weakens", f'"disableAutoMode": {json.dumps(data["disableAutoMode"])}',
                note="turns off auto mode and its guard, the second net for what deny patterns can't list"))
        if "autoMode" in data:
            section.changes.append(Change(
                "gap", '"autoMode"', note="Claude Code reads autoMode only from user settings; this block does nothing"))
        perms = data.get("permissions") if isinstance(data.get("permissions"), dict) else {}
        for entry in _entries(perms.get("allow")):
            for rule in rules:
                if rule.level in GUARDED and claude_entry_covers(entry, rule, home):
                    section.changes.append(_claude_allow(entry, rule, classify_all, cursor_reads))
        for name in ("deny", "ask"):
            for entry in _entries(perms.get(name)):
                section.changes.append(Change(
                    "extra", entry, name, note="a project rail; kept. A rail every project needs is a row in the rule table"))
    return sections


def _claude_allow(entry: str, rule, classify_all: bool, cursor_reads: bool) -> Change:
    weak, held = [], []
    guarded_shell = rule.kind == "command" and rule.level == "deny"
    if guarded_shell and not classify_all:
        weak.append("in Claude Code's auto mode it resolves before the classifier, since the user settings "
                    "lack `autoMode.classifyAllShell: true` (run set-up-machine)")
    else:
        held.append(f"Claude Code: the user {rule.level} entry wins over a project allow"
                    + (", and classifyAllShell keeps auto mode's classifier on it" if guarded_shell else ""))
    if cursor_reads and rule.kind == "command" and rule.level == "ask":
        weak.append("the Cursor CLI reads this allow list and has no ask level, so the command runs without the prompt")
    elif cursor_reads and rule.kind in ("command", "file"):
        held.append("the Cursor CLI reads this allow list too, and deny wins over allow there")
    kind = "weakens" if weak else "overlaps"
    return Change(kind, entry, "allow", rule.id, "; ".join(weak or held))


def _cursor_global(home: Path) -> dict:
    try:
        data = json.loads((home / ".cursor" / "cli-config.json").read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    perms = data.get("permissions") if isinstance(data, dict) else None
    return perms if isinstance(perms, dict) else {}


def audit_cursor(project: Path, home: Path, rules: list) -> list:
    sections = []
    global_perms = _cursor_global(home)
    global_deny = _entries(global_perms.get("deny"))
    for path in _nested(project, ".cursor/cli.json"):
        section = Section("Cursor CLI", path)
        sections.append(section)
        data = _read_json(path, section)
        if data is None:
            continue
        perms = data.get("permissions") if isinstance(data.get("permissions"), dict) else {}
        deny_replaced = "deny" in perms
        project_deny = _entries(perms.get("deny"))
        dropped = [e for e in global_deny if e not in project_deny] if deny_replaced else []
        if deny_replaced:
            if dropped:
                shown = ", ".join(dropped[:3]) + (f" and {len(dropped) - 3} more" if len(dropped) > 3 else "")
                section.changes.append(Change(
                    "weakens", f'"deny": {len(project_deny)} entr{"y" if len(project_deny) == 1 else "ies"}', "deny",
                    note=f"replaces the {len(global_deny)} deny entries in ~/.cursor/cli-config.json, dropping {shown}; "
                         "the lists in ~/.claude/settings.json and the pre-tool hook still hold"))
            for entry in project_deny:
                if entry not in global_deny:
                    section.changes.append(Change("extra", entry, "deny", note="a project rail; kept"))
        for entry in _entries(perms.get("allow")):
            for rule in rules:
                if rule.level not in GUARDED or not cursor_entry_covers(entry, rule, home):
                    continue
                if rule.level == "ask":
                    section.changes.append(Change(
                        "weakens", entry, "allow", rule.id,
                        "Cursor has no ask level: an allowed command runs without the prompt the ask rule wants"))
                elif deny_replaced and dropped:
                    section.changes.append(Change(
                        "overlaps", entry, "allow", rule.id,
                        "deny wins over allow, but this file's deny list replaced the global one: "
                        "only ~/.claude/settings.json and the pre-tool hook still deny it"))
                else:
                    section.changes.append(Change("overlaps", entry, "allow", rule.id, "deny wins over allow"))
    return sections


# --- opencode ---------------------------------------------------------------------------

OPENCODE_PROJECT_FILES = ("opencode.json", "opencode.jsonc", ".opencode/opencode.json", ".opencode/opencode.jsonc")


def merge(base: dict, over: dict) -> dict:
    """opencode's config merge: objects merge key by key (a key already there keeps its place,
    a new key goes last), anything else is replaced."""
    out = dict(base)
    for key, value in over.items():
        out[key] = merge(out[key], value) if isinstance(value, dict) and isinstance(out.get(key), dict) else value
    return out


def _opencode_global(home: Path) -> dict:
    merged = {}
    for name in opencode.CONFIG_FILES:
        path = opencode.config_dir(home) / name
        try:
            data = opencode.parse_jsonc(path.read_text())[0]
        except (OSError, json.JSONDecodeError, ValueError):
            continue
        if isinstance(data, dict):
            merged = merge(merged, data)
    return merged


def audit_opencode(project: Path, home: Path, rules: list) -> list:
    sections = []
    global_perm = _opencode_global(home).get("permission") or {}
    if not isinstance(global_perm, dict):
        global_perm = {"*": global_perm} if isinstance(global_perm, str) else {}
    for rel in OPENCODE_PROJECT_FILES:
        path = project / rel
        if not path.is_file():
            continue
        section = Section("opencode", path)
        sections.append(section)
        data = _read_json(path, section, jsonc=True)
        if data is None:
            continue
        own = data.get("permission")
        if isinstance(own, str):
            own = {"*": own}
        if isinstance(own, dict):
            _opencode_weakening(section, global_perm, merge(global_perm, own), rules, home, "")
        agents = data.get("agent") if isinstance(data.get("agent"), dict) else {}
        for name, agent in agents.items():
            perm = agent.get("permission") if isinstance(agent, dict) else None
            if isinstance(perm, str):
                perm = {"*": perm}
            if isinstance(perm, dict):
                base = merge(global_perm, own) if isinstance(own, dict) else global_perm
                _opencode_weakening(section, global_perm, merge(base, perm), rules, home, f"agent {name}: ")
        if data.get("plugin"):
            section.changes.append(Change(
                "gap", '"plugin"', note="a project plugin runs after the global pre-tool hook and can rewrite a call's "
                                        "arguments once the hook has passed them; read it"))
    for folder in (".opencode/plugin", ".opencode/plugins"):
        plugins = project / folder
        if plugins.is_dir() and any(p.is_file() for p in plugins.iterdir()):
            section = Section("opencode", plugins)
            section.changes.append(Change(
                "gap", folder + "/", note="a project plugin runs after the global pre-tool hook and can rewrite a "
                                          "call's arguments once the hook has passed them; read it"))
            sections.append(section)
    return sections


def _rank(found) -> int:
    """How strict a matched (tool, pattern, level) is; no match is opencode's default, allow."""
    return opencode.LEVELS.index(found[2]) if found and found[2] in opencode.LEVELS else 0


def _opencode_entry(found) -> str:
    if not found:
        return "(the default, allow)"
    tool, pattern, level = found
    return (tool if pattern == "*" else f"{tool} {json.dumps(pattern)}") + f": {level}"


def _opencode_weakening(section: Section, global_perm: dict, merged: dict, rules: list, home: Path, prefix: str):
    """A rule the project leaves looser than the global config does, by opencode's last-match-wins."""
    seen = set()
    for rule in rules:
        if rule.level not in GUARDED:
            continue
        for tool, pattern in opencode.entries_for(rule):
            for sample in opencode.samples(pattern):
                before = opencode.effective(global_perm, tool, sample, home)
                after = opencode.effective(merged, tool, sample, home)
                before_rank = _rank(before)
                after_rank = _rank(after)
                if after_rank >= before_rank:
                    continue
                culprit = _opencode_entry(after)
                key = (rule.id, culprit)
                if key in seen:
                    continue
                seen.add(key)
                section.changes.append(Change(
                    "weakens", prefix + culprit, after[2] if after else "allow", rule.id,
                    f"`{sample}` for {tool} is {before[2] if before else 'allow'} globally, "
                    f"{after[2] if after else 'allow'} here: the last matching rule wins, and a project's rules merge over the global ones"))


# --- Codex ----------------------------------------------------------------------------------

_TABLE = re.compile(r"^\s*\[\s*([^\[\]]+?)\s*\]\s*(#.*)?$")
_KEY = re.compile(r"^\s*([A-Za-z0-9_.\"-]+)\s*=\s*([^#]+?)\s*(#.*)?$")


def codex_features(text: str) -> dict:
    """The `[features]` keys a config.toml sets, from the table or dotted keys (`features.hooks = false`)."""
    out, table = {}, ""
    for line in text.splitlines():
        m = _TABLE.match(line)
        if m:
            table = m.group(1).replace(" ", "")
            continue
        m = _KEY.match(line)
        if not m:
            continue
        key = m.group(1).replace('"', "")
        full = f"{table}.{key}" if table else key
        if full.startswith("features."):
            out[full[len("features."):]] = m.group(2).strip().lower()
    return out


def audit_codex(project: Path) -> list:
    path = project / ".codex" / "config.toml"
    if not path.is_file():
        return []
    section = Section("Codex", path)
    try:
        features = codex_features(path.read_text())
    except OSError as exc:
        section.changes.append(Change("gap", f"can't read config.toml: {exc}"))
        return [section]
    if features.get("hooks") == "false":
        section.changes.append(Change(
            "weakens", "[features] hooks = false",
            note="in a trusted project, turns off every Codex hook, the pre-tool hook included; the rules still hold"))
    if features.get("memories") == "true":
        section.changes.append(Change(
            "weakens", "[features] memories = true", note="in a trusted project, turns Codex memories back on; memory stays off"))
    return [section]
