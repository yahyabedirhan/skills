"""Grok Bot, the agent app with one persistent Linux box: its hook payload, and the check of each
setup area (references/grok-bot.md).

The app owns most of what other harnesses keep in files: approvals, Auto-review, the model, the
connectors and memory. So only skills are checked fully. Each skill is a folder in the shared
skill library, `~/agent-data/workflows/<skill>/`, recorded in a lock with the git tree hash of its
source folder, so a copy that drifted from its source fails.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ..checks import Cell, cell, na, read_json
from ..hook import ToolCall, refusal

ID, LABEL = "grok-bot", "Grok Bot"
FOLDER = Path("agent-data/workflows")
# Like ~/.agents/.skill-lock.json: {"skills": {name: {"source", "skillPath", "skillFolderHash"}}}.
LOCK = Path(".local/state/agents/grok-bot-skill-lock.json")


def present(home: Path) -> bool:
    return (home / FOLDER).is_dir()


# --- the hook ------------------------------------------------------------------------------


def read(payload: dict) -> ToolCall:
    """A call the agent checks by hand, since Grok Bot runs no hook: `{"command": …, "cwd": …}` for a
    shell command, or `{"tool": …}` for an MCP tool. No one is sure to be asked, so every ask row
    is refused."""
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
    """Grok Bot loads no instructions file: the user writes the lines into its memory, which no file shows."""
    return Cell("gap", ["Grok Bot loads no instructions file; the shared file's lines go into its memory "
                        "by hand, and the check can't see memory (references/grok-bot.md)"])


def check_guardrails(ctx) -> Cell:
    return Cell("gap", ["Grok Bot runs no hook and has no permission lists: the app's Auto-review and "
                        "approval cards decide each call"])


def check_sandbox(ctx) -> Cell:
    return na("the app sets where commands run and how they are approved; no file holds it")


def check_plugins(ctx) -> Cell:
    """A connector is added in the app, so a listed one is a gap the user confirms there."""
    entries = ctx.setup.plugins(ID)
    if not entries:
        return na("installs.json lists no plugin for Grok Bot; connectors are added in the app")
    return Cell("gap", [f"{e['name']}: add and check it in the app's connectors; no file shows it" for e in entries])


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
    if ctx.setup.file(ID, "config") is not None:
        return Cell("gap", ["Grok Bot's model is picked in the app; a declared config can't be written"])
    return na("setup/harnesses.json names no Grok Bot config")


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
