"""Grok Bot, the agent app with one persistent Linux box: its hook payload, and the check of each setup area, as `references/grok-bot/desktop.md` describes.

The app owns most of what other harnesses keep in files: approvals, Auto-review, the model, the connectors and memory. So only skills are checked fully. Each skill is a folder in the shared skill library, `~/agent-data/workflows/<skill>/`, recorded in a lock with the git tree hash of its source folder, so a copy that drifted from its source fails.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

from ...checks import Cell, cell, na, read_json
from ...hook import ToolCall, refusal

ID, LABEL = "grok-bot", "Grok Bot"
ENV = "desktop"
FOLDER = Path("agent-data/workflows")
# Like `~/.agents/.skill-lock.json`: {"skills": {name: {"source", "skillPath", "skillFolderHash"}}}.
LOCK = Path(".local/state/agents/grok-bot-skill-lock.json")
# {"sha", "date", "sources": {"`setup/instructions.md`": [fact]}, "agents": {name: {"sha", "date", "facts", "profile"}}}:
# what user memory and each agent's memory hold, and from which commit. The box is shared, so one lock holds every agent.
INSTRUCTIONS_LOCK = Path(".local/state/agents/grok-bot-instructions-lock.json")


def present(home: Path) -> bool:
    return (home / FOLDER).is_dir()


# --- the hook ------------------------------------------------------------------------------


def read(payload: dict) -> ToolCall:
    """A call the agent checks by hand, since Grok Bot runs no hook: `{"command": …, "cwd": …}` for a shell command, or `{"tool": …}` for an MCP tool. No one is sure to be asked, so every ask row is refused."""
    def text(key):
        return payload.get(key) if isinstance(payload.get(key), str) else ""

    command = text("command")
    return ToolCall(tool="Shell" if command else text("tool"), command=command or None, cwd=text("cwd"),
                    unattended="Grok Bot, whose approvals the hook can't see", no_native_ask=True)


def write(denials: list, asks=()) -> str:
    """JSON: a deny with the refusal, or `{}`."""
    if not denials:
        return "{}\n"
    return json.dumps({"permission": "deny", "reason": refusal(denials)}) + "\n"


# --- the checks ----------------------------------------------------------------------------


def check_instructions(ctx) -> Cell:
    """The facts in memory came from the current instructions sources. Memory itself can't be read, so the check compares the sources at the commit the lock records with the sources now."""
    if not ctx.setup.repository:
        return Cell("gap", ["no workstation repo: the check can't see memory"])
    lock_path = ctx.home / INSTRUCTIONS_LOCK
    lock = read_json(lock_path)
    if not lock or not isinstance(lock.get("sha"), str):
        return Cell("gap", [f"no {ctx.show(lock_path)}: write the facts into memory, then the lock and the applied state page "
                            "(references/grok-bot/desktop.md, *First-time apply*)"])
    agents = lock.get("agents") if isinstance(lock.get("agents"), dict) else {}
    problems = []
    for source in sources(ctx):
        relative = source.relative_to(ctx.setup.clone).as_posix()
        # User memory follows the lock's own commit; each agent's memory follows its entry's commit.
        own = relative != "setup/instructions.md" and agents
        shas = {name: entry.get("sha") for name, entry in agents.items() if isinstance(entry, dict)} if own \
            else {"": lock["sha"]}
        for name, sha in shas.items():
            then = subprocess.run(["git", "-C", str(ctx.setup.clone), "show", f"{sha}:{relative}"],
                                  capture_output=True, text=True) if isinstance(sha, str) else None
            if then is None or then.returncode != 0 or then.stdout != source.read_text():
                who = f" for agent {name}" if name else ""
                problems.append(("FAIL", f"stale: {relative} changed since {str(sha)[:7]}{who}; reconcile memory "
                                         "(references/grok-bot/desktop.md, *Reconcile*)"))
    return cell(problems)


def sources(ctx) -> list:
    """The files memory facts come from: `setup/instructions.md` for user memory, and Grok Bot's own instructions from `setup/harnesses.json` for agent memory."""
    files = [ctx.setup.clone / "setup/instructions.md", ctx.setup.file(ID, "instructions", ENV)]
    return [f for f in files if f is not None and f.is_file()]


def check_guardrails(ctx) -> Cell:
    return Cell("gap", ["Grok Bot runs no hook and has no permission lists: the app's Auto-review and "
                        "approval cards decide each call"])


def check_sandbox(ctx) -> Cell:
    return na("the app sets where commands run and how they are approved; no file holds it")


def check_plugins(ctx) -> Cell:
    """A connector is added in the app, so each one `installs.json` or the declared config names is a gap the user confirms there."""
    names = [e["name"] for e in ctx.setup.plugins(ID)] + [n for n in _declared(ctx).get("connectors", [])
                                                          if isinstance(n, str)]
    if not names:
        return na("no connector is declared for Grok Bot; connectors are added in the app")
    return Cell("gap", [f"{name}: add it and check its sign-in in the app's connectors; no file shows it"
                        for name in dict.fromkeys(names)])


def check_skills(ctx) -> Cell:
    """Each listed skill is in the library, recorded in the lock, and unchanged since its sync."""
    library, lock_path = ctx.home / FOLDER, ctx.home / LOCK
    lock = (read_json(lock_path) or {}).get("skills")
    lock = {n: rec for n, rec in lock.items() if isinstance(rec, dict)} if isinstance(lock, dict) else {}
    problems = []
    for entry in ctx.setup.installs.get("skills", []):
        source = entry["source"]
        names = entry.get("skills") or sorted(n for n, rec in lock.items() if rec.get("source") == source)
        if not names:
            problems.append(("FAIL", f"no skill from {source} is recorded in {ctx.show(lock_path)}"))
            continue
        for name in names:
            folder, record = library / name, lock.get(name)
            if not (folder / "SKILL.md").is_file():
                problems.append(("FAIL", f"{source}: {name} not in {ctx.show(library)}"))
            elif not record or record.get("source") != source:
                problems.append(("FAIL", f"{source}: {name} has no entry from it in {ctx.show(lock_path)}"))
            elif tree_hash(folder) != record.get("skillFolderHash"):
                problems.append(("FAIL", f"{ctx.show(folder)} differs from {source} at its last sync; sync it again"))
    return cell(problems)


def check_config(ctx) -> Cell:
    """The declared config's `secrets` are set as environment variables, by name only; `connectors` are checked in the plugins column; `routines` live in the app."""
    source = ctx.setup.file(ID, "config", ENV)
    if source is None:
        return na("setup/harnesses.json names no Grok Bot config")
    declared = _declared(ctx)
    if not declared:
        return Cell("FAIL", [f"{ctx.show(source)} isn't a JSON object"])
    problems = []
    for key in declared:
        if key not in KEYS:
            problems.append(("gap", f"{source.name}: `{key}` has no Grok Bot setting; it is set in the app"))
    secrets = [s for s in declared.get("secrets", []) if isinstance(s, str)]
    if secrets and ctx.home != Path.home().resolve():
        problems.append(("gap", "secrets are checked only in the real home, where the app sets them"))
    elif secrets:
        missing = [s for s in secrets if not os.environ.get(s)]  # the name only: a value is never read out
        if missing:
            problems.append(("FAIL", f"secret {', '.join(missing)} is not set; add it in the app's secrets"))
    if declared.get("routines"):
        problems.append(("gap", f"{len(declared['routines'])} routines: check each in the app; no file shows them"))
    return cell(problems)


# The keys a declared Grok Bot config may set, as `references/grok-bot/desktop.md` > 'Config' lists them.
KEYS = ("secrets", "connectors", "routines")


def _declared(ctx) -> dict:
    source = ctx.setup.file(ID, "config", ENV)
    data = read_json(source) if source is not None else {}
    return data if isinstance(data, dict) else {}


def review_rules(rows) -> str:
    """The rule table and the personal permissions as Auto-review rules, for the user to paste in the app."""
    groups = {"deny": "Block", "ask": "Ask the user first", "allow-and-report": "Allow", "allow": "Allow"}
    lines = []
    for title in ("Block", "Ask the user first", "Allow"):
        picked = [r for r in rows if groups[r.level] == title]
        if not picked:
            continue
        lines.append(f"{title}:")
        lines += [f"- {r.summary}. {r.reason} Instead: {r.instruction}" if r.level in ("deny", "ask")
                  else f"- {r.summary}. {r.reason}" for r in picked]
        lines.append("")
    return "\n".join(lines)


def tree_hash(folder: Path) -> str:
    """The git tree hash of a folder, the `sha` GitHub's tree API gives the same folder."""
    entries = []
    for path in folder.iterdir():
        if path.name == "__pycache__":  # Python writes it when a skill's script runs; git ignores it
            continue
        if path.is_symlink():
            mode, sha = "120000", _object("blob", str(Path(path.readlink())).encode())
        elif path.is_dir():
            mode, sha = "40000", tree_hash(path)
        else:
            mode = "100755" if path.stat().st_mode & 0o111 else "100644"
            sha = _object("blob", path.read_bytes())
        entries.append((path.name + ("/" if mode == "40000" else ""), mode, path.name, sha))
    body = b"".join(f"{mode} {name}".encode() + b"\0" + bytes.fromhex(sha)
                    for _, mode, name, sha in sorted(entries))
    return _object("tree", body)


def _object(kind: str, data: bytes) -> str:
    return hashlib.sha1(f"{kind} {len(data)}".encode() + b"\0" + data).hexdigest()
