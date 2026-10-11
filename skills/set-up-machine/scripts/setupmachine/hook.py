"""The basic pre-tool hook: deny and allow-and-report rows, checked before a tool call runs.

A harness hands the hook one tool call; the hook reads it into a `ToolCall`,
checks it against the rule table, and answers in the harness's own format:

- **deny:** any part of the call a deny row covers refuses the whole call, and
  the answer names each refused part with its rule's reason and instruction;
- **allow-and-report:** otherwise, a call an allow-and-report row covers gets one
  line in the report folder, and the hook says nothing, so the harness's own
  permissions decide;
- **ask:** the verdict names the ask rows a call hits (verify checks them), but the
  hook says nothing for them: the harness's native ask entries do the asking. A row
  with `approver: "user"` is refused instead when the call shows the harness won't
  ask the user, such as Claude Code in bypassPermissions mode. A harness with no ask
  entries of its own but a way to ask (Pi's extension) gets the ask rows in the answer,
  and its wiring asks the user;
- **allow**, a personal permission's level: the verdict names them for verify too, and the
  hook says nothing, so the harness's native allow entries let the call run.

The rows are the rule table's, plus the personal permissions of the repository that
`~/.config/agents/source.md` names (personal.py).

Each harness has a reader (its payload -> ToolCall) and a writer (the denials,
and the ask hits for a writer that asks -> what it prints). A discovered harness setup
supplies both. The report folder comes from the hook's configuration file,
`~/.config/agents/hook.json` by default.
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import shlex
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from . import commands, personal, rules as rule_table

CONFIG_PATH = "~/.config/agents/hook.json"
DEFAULT_REPORT_DIR = "~/.local/state/agents/reports"


@dataclass
class ToolCall:
    tool: str
    command: object = None  # the shell command text, for a tool that runs one
    files: tuple = ()  # (path, access) pairs, access being read or write
    cwd: str = ""
    session: str = ""
    mcp_names: tuple = ()  # the tool's possible `mcp__<server>__<tool>` names, for a harness that names MCP tools otherwise
    searches: tuple = ()  # (folder, glob) pairs a search tool reads the matching files of
    report: bool = True  # False when another hook, wired for the same harness, reports this call
    unattended: str = ""  # why the harness won't ask the user about this call, when it won't
    no_native_ask: bool = False  # the harness has no ask entry of its own, so an unattended call refuses every ask row


@dataclass
class Hit:
    rule: object
    part: str  # the part of the call the rule covers, as the agent would recognise it


@dataclass
class Verdict:
    denials: list = field(default_factory=list)
    reports: list = field(default_factory=list)
    asks: list = field(default_factory=list)  # ask rows the call hits; the harness's native entries do the asking
    allows: list = field(default_factory=list)  # personal allow rows the call hits; the native entries allow it

    @property
    def answer(self) -> str:
        """deny, ask or allow: what the rule table says about the call as a whole."""
        return "deny" if self.denials else "ask" if self.asks else "allow"


def decide(call: ToolCall, table: list, home: Path) -> Verdict:
    verdict = Verdict()
    checked = table
    hits = []
    files = list(call.files)
    if call.command:
        argvs = commands.simple_commands(call.command, files=files)  # redirect targets join the files
        for argv in argvs:
            hits += [Hit(r, shlex.join(argv)) for r in checked if r.kind == "command" and not r.variables
                     and commands.covers(r, argv)
                     and (not r.files or any(path_matches(r, w, call.cwd, home) for w in operand_files(argv)))]
        files += commands.tee_writes(argvs)
        variable_rows = [r for r in checked if r.kind == "command" and r.variables]
        if variable_rows:
            for argv in commands.simple_commands(commands.mark_expansions(call.command)):
                shown = shlex.join(argv).replace(commands.EXPANDS, "$")
                hits += [Hit(r, shown) for r in variable_rows if commands.covers(r, argv)]
    for folder, glob in call.searches:
        files.append((os.path.join(folder, glob) if folder else glob, "read"))
        hits += [Hit(r, f"search {glob}") for r in checked if r.kind == "file" and glob_targets(r, glob)]
    for path, access in files:
        hits += [Hit(r, f"{access} {path}") for r in checked
                 if r.kind == "file" and (r.access == access or r.access == "read")
                 and path_matches(r, path, call.cwd, home)]
    mcp_names = call.mcp_names or ((call.tool,) if rule_table.split_mcp_name(call.tool) else ())
    if mcp_names:
        hits += [Hit(r, call.tool) for r in checked if r.kind == "mcp-tool" and rule_table.matching_tools(r, mcp_names)]
    seen = set()
    for hit in hits:
        key = (hit.rule.id, hit.part)
        if key not in seen:
            seen.add(key)
            {"deny": verdict.denials, "ask": verdict.asks, "allow-and-report": verdict.reports,
             "allow": verdict.allows}[hit.rule.level].append(hit)
    if call.unattended:
        unasked = [h for h in verdict.asks if h.rule.approver == "user" or call.no_native_ask]
        verdict.denials += [Hit(h.rule, f"{h.part} ({call.unattended}, where no one asks the user)") for h in unasked]
    if verdict.denials:
        verdict.reports, verdict.asks, verdict.allows = [], [], []
    return verdict


# --- file rows ----------------------------------------------------------------


def path_matches(rule, path: str, cwd: str, home: Path) -> bool:
    """Whether a file path falls under one of the row's globs (`paths`, or a command row's
    `files`) and none of its `except` globs.

    Globs read as rules.glob_regex says. The path is checked as written and with
    symlinks resolved, and as a folder too (`secrets` counts as inside `secrets/**`).
    """
    base = os.path.normpath(cwd or os.getcwd())
    if path == "~" or path.startswith("~/"):
        path = str(home) + path[1:]
    full = os.path.normpath(os.path.join(base, path))
    candidates = {full, os.path.realpath(full)}

    def under(globs, as_folder):
        names = candidates | {c + "/_" for c in candidates} if as_folder else candidates
        return any(rule_table.glob_regex(g, base, home, commands.FOLD_CASE).match(c) for g in globs for c in names)

    return under(rule.paths or rule.files, True) and not under(rule.excepts, False)


# Names no secret-file row covers: a search glob matching them too is a broad search, not one aimed at the row.
ORDINARY_NAMES = ("README.md", "main.py", "notes.txt")


def glob_targets(rule, glob: str) -> bool:
    """Whether a search glob (`*.env`, `.env*`) picks out a file row's files by name.

    A name the row covers is made from each of its globs' last part (`.env.*` -> `.env.local`);
    a search glob matching one of those, but no ordinary file name, targets the row. A glob
    matching everything (`*`) is a search over the folder, which the hook doesn't expand.
    """
    pattern = glob.rstrip("/").rsplit("/", 1)[-1]
    if not set("*?[") & set(pattern) or any(fnmatch.fnmatchcase(n, pattern) for n in ORDINARY_NAMES):
        return False  # a literal glob is checked as a path; one matching ordinary names too is a broad search
    lasts = [g.rsplit("/", 1)[-1] for g in rule.paths]
    samples = {n.replace("*", "local").replace("?", "x") for n in lasts if n.strip("*?")}
    left_out = {g.rsplit("/", 1)[-1] for g in rule.excepts}
    fold = (lambda t: t.lower()) if commands.FOLD_CASE else (lambda t: t)
    return any(fnmatch.fnmatchcase(fold(n), fold(pattern)) for n in samples - left_out)


def operand_files(argv: list) -> list:
    """The words of a command that could name a file: every word after the program but its flags."""
    return [a for a in argv[1:] if a and not a.startswith("-")]


# --- what the agent reads -------------------------------------------------------


HOOK_SCRIPT_NAME = "pre_tool_hook.py"


def command_script(command: str, harness: str, home: Path):
    """The hook script a wired command runs, when it runs it for this harness; else None."""
    try:
        words = shlex.split(command)
    except ValueError:
        return None
    script = next((w for w in words if w.endswith(HOOK_SCRIPT_NAME)), None)
    if script is None or f"--harness {harness}" not in " ".join(words):
        return None
    return Path(str(home) + script[1:]) if script.startswith("~/") else Path(script)


def refusal(denials: list) -> str:
    lines = [
        "Refused by the pre-tool hook, from the global rule table. Nothing in this call ran. "
        "Only the parts below are refused: run every other step as its own command.",
    ]
    for hit in denials:
        r = hit.rule
        lines.append(f"- `{hit.part}`: denied by rule {r.id} ({_plain(r.summary)}). {r.reason} Instead: {r.instruction}")
    return "\n".join(lines)


def _plain(summary: str) -> str:
    return summary.replace("`", "")


# --- the report ---------------------------------------------------------------


def load_config(path: Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        return {}
    return data if isinstance(data, dict) else {}


def report_dir(config: dict, config_path: Path) -> Path:
    """The configured report folder; a relative one is relative to the configuration file."""
    value = config.get("report_dir")
    if not isinstance(value, str) or not value:
        state = os.environ.get("XDG_STATE_HOME")
        return Path(state) / "agents" / "reports" if state else Path(DEFAULT_REPORT_DIR).expanduser()
    folder = Path(value).expanduser()
    return folder if folder.is_absolute() else config_path.parent / folder


def write_report(folder: Path, call: ToolCall, hits: list, harness: str, now: datetime) -> Path:
    """Append one JSON line for this call to the day's file in the report folder.

    The file is readable by the user alone: a reported command can carry a
    secret's value (`gh secret set NAME --body …`).
    """
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = folder / f"{now.strftime('%Y-%m-%d')}.jsonl"
    line = {
        "time": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "harness": harness,
        "session": call.session,
        "cwd": call.cwd,
        "tool": call.tool,
        "rules": sorted({h.rule.id for h in hits}),
        "parts": [h.part for h in hits],
        "command": call.command,
    }
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    with os.fdopen(fd, "a") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")
    return path


# --- harnesses ------------------------------------------------------------------


def read_claude_code(payload: dict) -> ToolCall:
    """Claude Code's hook payload, read by its harness setup."""
    return harness_io()["claude-code"][0](payload)


def _search(args: dict, folder_key: str, glob_key: str) -> tuple:
    """A search tool's (folder, glob) pair, when it names a glob."""
    glob, folder = args.get(glob_key), args.get(folder_key)
    if not isinstance(glob, str) or not glob:
        return ()
    return ((folder if isinstance(folder, str) else "", glob),)


def write_claude_code(denials: list, asks=()) -> str:
    """Claude Code's hook answer, written by its harness setup. Codex uses the same answer."""
    return harness_io()["claude-code"][1](denials, asks)


# apply_patch's file headers; each names a file the patch writes.
PATCH_FILE = re.compile(r"^\*\*\* (Add File|Update File|Delete File|Move to): (.+?)\s*$", re.M)


def read_codex(payload: dict) -> ToolCall:
    """Codex's hook payload, read by its harness setup."""
    return harness_io()["codex"][0](payload)


def read_pi(payload: dict) -> ToolCall:
    """Pi's hook payload, read by its harness setup."""
    return harness_io()["pi"][0](payload)


def write_pi(denials: list, asks=()) -> str:
    """Pi's hook answer, written by its harness setup."""
    return harness_io()["pi"][1](denials, asks)


def harness_io() -> dict:
    """Reader and writer per harness, from each harness setup that runs the hook."""
    found = {}
    from . import harness_setups
    for setup in harness_setups.load():
        read, write = getattr(setup, "read", None), getattr(setup, "write", None)
        if callable(read) and callable(write):
            found[setup.id] = (read, write)
    return found


def read_opencode(payload: dict) -> ToolCall:
    """opencode's hook payload, read by its harness setup."""
    return harness_io()["opencode"][0](payload)


def write_opencode(denials: list, asks=()) -> str:
    """opencode's hook answer, written by its harness setup."""
    return harness_io()["opencode"][1](denials, asks)


def read_cursor(payload: dict) -> ToolCall:
    """Cursor's hook payload, read by its harness setup."""
    return harness_io()["cursor"][0](payload)


def write_cursor(denials: list, asks=()) -> str:
    """Cursor's hook answer, written by its harness setup."""
    return harness_io()["cursor"][1](denials, asks)


def main(argv=None, stdin=None, stdout=None, now=None) -> int:
    import argparse

    readers = harness_io()
    parser = argparse.ArgumentParser(description="set-up-machine's pre-tool hook: reads one tool call on stdin.")
    parser.add_argument("--harness", choices=sorted(readers), default="claude-code")
    parser.add_argument("--config", type=Path, default=Path(CONFIG_PATH).expanduser(),
                        help=f"the hook's configuration (default: {CONFIG_PATH})")
    parser.add_argument("--rules", type=Path, default=rule_table.DEFAULT_TABLE)
    args = parser.parse_args(argv)
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    read, write = readers[args.harness]

    # A hook that fails never blocks the call: the harness's native deny rules stay underneath.
    # Pi has none, so its extension refuses the call when the hook exits non-zero (references/pi.md).
    try:
        payload = json.loads(stdin.read() or "{}")
        call = read(payload if isinstance(payload, dict) else {})
        table = rule_table.load(args.rules)
    except (ValueError, OSError) as exc:
        print(f"set-up-machine hook: {exc}", file=sys.stderr)
        return 1
    # A broken personal file leaves the rule table's rows in force; verify.py reports it.
    # Catch everything here: a crash would let the call through without the table's rows.
    try:
        table = table + personal.permissions(Path.home(), table)
    except Exception as exc:
        print(f"set-up-machine hook: personal permissions skipped: {exc}", file=sys.stderr)
    try:
        verdict = decide(call, table, Path.home())
    except (ValueError, OSError) as exc:
        print(f"set-up-machine hook: {exc}", file=sys.stderr)
        return 1
    if verdict.denials:
        stdout.write(write(verdict.denials))
        return 0
    if verdict.reports and call.report:
        try:
            config = load_config(args.config)
            write_report(report_dir(config, args.config), call, verdict.reports, args.harness,
                         now or datetime.now(timezone.utc))
        except (ValueError, OSError) as exc:
            print(f"set-up-machine hook: couldn't write the report: {exc}", file=sys.stderr)
            return 1
    stdout.write(write([], verdict.asks))
    return 0
