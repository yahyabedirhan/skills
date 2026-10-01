#!/usr/bin/env python3
"""set-up-machine's check that the rules work on this machine. It writes nothing.

usage: verify.py [--home DIR] [--rules FILE] [--codex PATH | --no-codex]
       verify.py --codex-trust-hash COMMAND

- rules: every row's `covers` samples get the row's level from the pre-tool hook
  (deny, ask or allow-and-report), and its `leaves` samples pass the row; the
  personal repository's rows too, an `allow` row's samples passing every other row;
- codex: each plain command sample through `codex execpolicy check` against the
  machine's Codex rules, listed as `same`, `stricter` (another rules file is
  stricter, and kept) or `differs` from the row's level (a row Codex can't
  express, in references/codex.md, or a mistake to fix);
- hook: each harness found has its pre-tool hook wired to a script that exists
  (Codex's also trusted);
- personal: the pointer, ~/.config/agents/source.md, is there, and when it names a
  personal repository, the shared global instructions file carries that repository's
  environment defaults and personal workflow (references/personal-repository.md);
  and each personal row's entries in Claude Code's settings, `present`, `n/a` when
  Claude Code lacks the row's tool, `gap` when the row has no native entry there.

Exits 1 when a rules, hook or personal line fails. --codex-trust-hash prints the
`trusted_hash` Codex records for a PreToolUse hook running COMMAND with matcher
`*` and timeout 10. Python 3.9+, standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setupmachine import commands, hook, personal, rules as rule_table  # noqa: E402

HOOK_SCRIPT = "pre_tool_hook.py"
CURSOR_EVENTS = ("beforeShellExecution", "beforeMCPExecution", "beforeReadFile", "preToolUse")
CODEX_DECISION = {"forbidden": "deny", "prompt": "ask", "allow": "allow-and-report"}
SHELL_SYNTAX = set(";&|<>$`()\n")
STRICTNESS = {"allow-and-report": 0, "ask": 1, "deny": 2}


@dataclass
class Result:
    rule: object
    sample: str
    expected: str  # the row's level, or "pass" for a near miss
    answer: str  # the row's level when the hook's verdict holds the row, else "allow" (or "pass");
    # for an allow row, "allow" when it holds the row and no other row asks or denies, else "no match" or that level


# --- the rule table against the hook ------------------------------------------


def check_rules(table: list, home: Path) -> list:
    """Every sample of every row, the rule table's and the personal ones, through the hook's decision, as Results."""
    cwd = str(home / "project")
    results = []
    for rule in table:
        for sample in rule.covers:
            verdict = _verdict(rule, sample, table, home, cwd)
            hit = _holds(verdict, rule)
            if rule.level == "allow":
                answer = verdict.answer if verdict.answer != "allow" else "allow" if hit else "no match"
            else:
                answer = rule.level if hit else "allow"
            results.append(Result(rule, sample, rule.level, answer))
        for sample in rule.leaves:
            hit = _holds(_verdict(rule, sample, table, home, cwd), rule)
            results.append(Result(rule, sample, "pass", "caught" if hit else "pass"))
    return results


def _verdict(rule, sample: str, table: list, home: Path, cwd: str):
    if rule.kind == "file":
        call = hook.ToolCall(tool="Read" if rule.access == "read" else "Write", files=((sample, rule.access),), cwd=cwd)
    elif rule.kind == "mcp-tool":
        call = hook.ToolCall(tool=sample, cwd=cwd)
    else:
        call = hook.ToolCall(tool="Bash", command=sample, cwd=cwd)
    return hook.decide(call, table, home)


def _holds(verdict, rule) -> bool:
    return any(h.rule.id == rule.id for h in verdict.denials + verdict.asks + verdict.reports + verdict.allows)


# --- Codex's own checker --------------------------------------------------------


def check_codex(table: list, home: Path, codex: str) -> list:
    """(row, sample, Codex's decision as a level or "no match") for each plain command sample."""
    rules_dir = home / ".codex" / "rules"
    files = sorted(rules_dir.glob("*.rules")) if rules_dir.is_dir() else []
    if not files:
        return []
    out = []
    for rule in table:
        if rule.kind != "command":
            continue
        for sample in rule.covers:
            if SHELL_SYNTAX & set(sample):
                continue  # a compound isn't one argv
            argv = [codex, "execpolicy", "check", "--resolve-host-executables"]
            for f in files:
                argv += ["--rules", str(f)]
            done = subprocess.run(argv + ["--", *shlex.split(sample)], capture_output=True, text=True, timeout=60)
            try:
                decision = json.loads(done.stdout or "{}").get("decision")
            except ValueError:
                decision = None
            out.append((rule, sample, CODEX_DECISION.get(decision, "no match")))
    return out


# --- hook wiring ------------------------------------------------------------------


def codex_trust_hash(command: str, matcher: str = "*", timeout: int = 10) -> str:
    """The hash Codex records when a PreToolUse command hook is trusted in /hooks: sha256 over the
    canonical JSON of the hook's identity (codex-rs/hooks, discovery)."""
    identity = {
        "event_name": "pre_tool_use",
        "matcher": matcher,
        "hooks": [{"type": "command", "command": command, "timeout": timeout, "async": False}],
    }
    text = json.dumps(identity, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(text.encode()).hexdigest()


def _json(path: Path):
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _script(command: str, harness: str, home: Path):
    """The hook script a wired command runs, when it runs it for this harness; else None."""
    try:
        words = shlex.split(command)
    except ValueError:
        return None
    script = next((w for w in words if w.endswith(HOOK_SCRIPT)), None)
    if script is None or f"--harness {harness}" not in " ".join(words):
        return None
    return Path(str(home) + script[1:]) if script.startswith("~/") else Path(script)


def _pre_tool_commands(settings: dict) -> list:
    """(group index, handler index, matcher, command) for every PreToolUse command handler."""
    hooks = settings.get("hooks") if isinstance(settings.get("hooks"), dict) else {}
    groups = hooks.get("PreToolUse") if isinstance(hooks.get("PreToolUse"), list) else []
    out = []
    for g, group in enumerate(groups):
        handlers = group.get("hooks") if isinstance(group, dict) and isinstance(group.get("hooks"), list) else []
        for h, handler in enumerate(handlers):
            if isinstance(handler, dict) and isinstance(handler.get("command"), str):
                out.append((g, h, group.get("matcher"), handler["command"], handler.get("timeout", 10)))
    return out


def _script_line(label: str, where: Path, script: Path, extra: str = ""):
    if not script.is_file():
        return ("FAIL", f"{label}: {where} runs {script}, which doesn't exist")
    return ("wired", f"{label}: {where} -> {script}{extra}")


def _claude_code(home: Path, folder: Path):
    path = folder / "settings.json"
    for _, _, matcher, command, _ in _pre_tool_commands(_json(path) or {}):
        script = _script(command, "claude-code", home)
        if script and matcher in ("*", "", None):
            return _script_line("Claude Code", path, script)
    return ("FAIL", f"Claude Code: no pre-tool hook for every tool in {path}")


def _codex(home: Path, folder: Path):
    path = folder / "hooks.json"
    config = (folder / "config.toml")
    for g, h, matcher, command, timeout in _pre_tool_commands(_json(path) or {}):
        script = _script(command, "codex", home)
        if not (script and matcher in ("*", "", None)):
            continue
        status, text = _script_line("Codex", path, script)
        if status != "wired":
            return status, text
        key = f"{path}:pre_tool_use:{g}:{h}"
        if _toml_trust(config, key) != codex_trust_hash(command, matcher or "*", timeout):
            return ("FAIL", f"Codex: the hook in {path} is not trusted: config.toml needs "
                            f"[hooks.state.\"{key}\"] trusted_hash = \"{codex_trust_hash(command, matcher or '*', timeout)}\"")
        return status, text + ", trusted"
    return ("FAIL", f"Codex: no pre-tool hook for every tool in {path}")


def _toml_trust(config: Path, key: str):
    try:
        lines = config.read_text().split("\n")
    except OSError:
        return None
    header = f"[hooks.state.{json.dumps(key)}]"
    for i, line in enumerate(lines):
        if line.strip() == header:
            for body in lines[i + 1:]:
                if body.lstrip().startswith("["):
                    break
                m = re.match(r'^\s*trusted_hash\s*=\s*"([^"]*)"', body)
                if m:
                    return m.group(1)
    return None


def _opencode(home: Path, folder: Path):
    path = folder / "plugins" / "set-up-machine.js"
    try:
        text = path.read_text()
    except OSError:
        return ("FAIL", f"opencode: no plugin at {path}")
    m = re.search(r"^const COMMAND = (\[.*\]);$", text, re.M)
    command = json.loads(m.group(1)) if m else []
    script = _script(shlex.join(command), "opencode", home) if command else None
    if script is None:
        return ("FAIL", f"opencode: {path} doesn't run the pre-tool hook with --harness opencode")
    return _script_line("opencode", path, script)


def _cursor(home: Path, folder: Path):
    path = folder / "hooks.json"
    hooks = (_json(path) or {}).get("hooks")
    hooks = hooks if isinstance(hooks, dict) else {}
    missing, scripts = [], set()
    for event in CURSOR_EVENTS:
        found = [_script(h["command"], "cursor", home) for h in hooks.get(event) or []
                 if isinstance(h, dict) and isinstance(h.get("command"), str)]
        found = [s for s in found if s]
        if found:
            scripts.add(found[0])
        else:
            missing.append(event)
    if missing:
        return ("FAIL", f"Cursor: {path} has no pre-tool hook on {', '.join(missing)}")
    gone = [s for s in scripts if not s.is_file()]
    if gone:
        return ("FAIL", f"Cursor: {path} runs {gone[0]}, which doesn't exist")
    return ("wired", f"Cursor: {path} -> {', '.join(str(s) for s in sorted(scripts))} on all four events")


HARNESSES = (
    ("Claude Code", ".claude", _claude_code),
    ("Codex", ".codex", _codex),
    ("opencode", ".config/opencode", _opencode),
    ("Cursor", ".cursor", _cursor),
)


def check_wiring(home: Path) -> list:
    """(status, text) per harness: wired, FAIL, or none when the harness isn't set up here."""
    out = []
    for label, rel, check in HARNESSES:
        folder = home / rel
        if not folder.is_dir():
            out.append(("none", f"{label}: not set up here (no ~/{rel})"))
        else:
            out.append(check(home, folder))
    return out


# --- personal rows in Claude Code's settings -------------------------------------

CLAUDE_LISTS = {"deny": "deny", "ask": "ask", "allow-and-report": "allow", "allow": "allow"}


def check_personal_entries(home: Path, rows: list) -> list:
    """(status, text) per personal row: its entries in Claude Code's settings, as references/claude-code.md writes them.

    `present` names them; with none, `gap` for a row Claude Code has no entry for, `n/a` when
    Claude Code lacks the row's tool (no MCP tool it matches, or no program on PATH), else FAIL.
    """
    folder = home / ".claude"
    if not rows or not folder.is_dir():
        return []
    path = folder / "settings.json"
    permissions = (_json(path) or {}).get("permissions")
    permissions = permissions if isinstance(permissions, dict) else {}
    out = []
    for rule in rows:
        name = CLAUDE_LISTS[rule.level]
        listed = permissions.get(name) if isinstance(permissions.get(name), list) else []
        entries = [e for e in listed if isinstance(e, str) and _claude_entry_of(rule, e, home)]
        label = f"Claude Code: {rule.id} ({rule.level}, personal)"
        if entries:
            out.append(("present", f"{label}: {', '.join(entries)} in {path}"))
        elif rule.kind == "command" and (rule.bare or rule.flags_only or rule.variables or rule.files):
            out.append(("gap", f"{label}: Claude Code has no entry for this kind of command row; the hook covers "
                               "deny and allow-and-report rows"))
        elif rule.kind == "mcp-tool":
            out.append(("n/a", f"{label}: no MCP tool in {path} matches it, so it's written only once Claude Code "
                               "lists a tool it matches"))
        elif rule.kind == "command" and not any(shutil.which(p) for p in rule.programs):
            out.append(("n/a", f"{label}: {', '.join(rule.programs)} isn't on PATH, so there's no tool to write it for"))
        else:
            out.append(("FAIL", f"{label}: no entry in permissions.{name} of {path}"))
    return out


def _claude_entry_of(rule, entry: str, home: Path) -> bool:
    """Whether a Claude Code permission entry is one this row produces: what the entry names, the row covers."""
    if rule.kind == "mcp-tool":
        return bool(rule_table.matching_tools(rule, [entry]))
    m = re.fullmatch(r"(Bash|Read|Edit|Write)\((.+)\)", entry, re.S)
    if not m:
        return False
    tool, inner = m.groups()
    if rule.kind == "command":
        if tool != "Bash":
            return False
        argvs = commands.simple_commands(re.sub(r"(:\*| \*)$", "", inner))
        return len(argvs) == 1 and commands.covers(rule, argvs[0])
    if tool not in (("Read",) if rule.access == "read" else ("Edit", "Write")):
        return False
    cwd = str(home / "project")
    if inner.startswith("//"):
        path = inner[1:]
    elif inner.startswith("~/") or inner.startswith("**/"):
        path = inner
    else:
        path = f"{cwd}/{inner[2:] if inner.startswith('./') else inner}"
    path = str(home) + path[1:] if path.startswith("~/") else path
    return any(rule_table.glob_regex(g, cwd, home).match(path) for g in rule.paths)


# --- the report -------------------------------------------------------------------


def main(argv=None, stdout=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--home", type=Path, default=Path.home(), help="the home folder to check (default: $HOME)")
    parser.add_argument("--rules", type=Path, default=rule_table.DEFAULT_TABLE)
    parser.add_argument("--codex", help="the codex program (default: codex on PATH)")
    parser.add_argument("--no-codex", action="store_true", help="skip codex execpolicy check")
    parser.add_argument("--codex-trust-hash", metavar="COMMAND", help="print Codex's trusted_hash for this hook command")
    args = parser.parse_args(argv)
    out = stdout or sys.stdout

    def line(check, status, text):
        out.write(f"{check:<8} {status:<8} {text}\n")

    if args.codex_trust_hash is not None:
        out.write(codex_trust_hash(args.codex_trust_hash) + "\n")
        return 0
    home = args.home.expanduser().resolve()
    failed = False
    try:
        table = rule_table.load(args.rules)
    except rule_table.RuleTableError as exc:
        line("rules", "FAIL", str(exc))
        return 1
    own_lines = []
    try:
        own = personal.permissions(home, table)
    except rule_table.RuleTableError as exc:
        own, own_lines = [], [("FAIL", str(exc))]
    table = table + own

    results = check_rules(table, home)
    wrong = [r for r in results if r.answer != r.expected]
    for r in wrong:
        if r.expected == "pass":
            line("rules", "FAIL", f"{r.rule.id}: `{r.sample}` should pass, but the row catches it")
        else:
            line("rules", "FAIL", f"{r.rule.id}: `{r.sample}` got {r.answer}, expected {r.expected}")
    rows = f"{len(table) - len(own)} rows" + (f" and {len(own)} personal rows" if own else "")
    line("rules", "FAIL" if wrong else "ok", f"{rows}, {len(results)} samples, {len(wrong)} wrong")
    failed |= bool(wrong)

    codex = None if args.no_codex else (args.codex or shutil.which("codex"))
    if codex:
        checked = check_codex(table, home, codex)
        if not checked:
            line("codex", "skipped", f"no rules files in {home / '.codex' / 'rules'}")
        for rule, sample, level in checked:
            want = "allow-and-report" if rule.level == "allow" else rule.level  # Codex has one allow decision
            if level == want:
                line("codex", "same", f"{rule.id}: {sample} -> {_decision(level)}")
            elif STRICTNESS.get(level, -1) > STRICTNESS[want]:
                line("codex", "stricter", f"{rule.id}: {sample} -> {_decision(level)}, the row is {rule.level}")
            else:
                line("codex", "differs", f"{rule.id}: {sample} -> {_decision(level)}, the row is {rule.level}")
    elif not args.no_codex:
        line("codex", "skipped", "codex isn't on PATH")

    for status, text in check_wiring(home):
        line("hook", status, text)
        failed |= status == "FAIL"

    for status, text in personal.check(home) + own_lines + check_personal_entries(home, own):
        line("personal", status, text)
        failed |= status == "FAIL"
    return 1 if failed else 0


def _decision(level: str) -> str:
    return {v: k for k, v in CODEX_DECISION.items()}.get(level, level)


if __name__ == "__main__":
    sys.exit(main())
