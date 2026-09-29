"""The shared global instructions file, and the manifest of what set-up-machine wrote.

Both live in one harness-neutral folder, `<home>/.config/agents/`, which every
adapter reaches: Claude Code by an `@` import, harnesses without imports by a
symlink to the file.
"""
from __future__ import annotations

import json
from pathlib import Path

from .plan import FileWrite, Section

BEGIN = "<!-- set-up-machine:rules start. Generated from set-up-machine's rule table: change the table, not these lines. -->"
END = "<!-- set-up-machine:rules end -->"

NEW_FILE_HEAD = """# Global agent instructions

Only what describes this person's own workflow and explains a global rule. Anything a teammate would need goes in the project or a skill.
"""

BLOCK_INTRO = """## Global rules

Every harness on this machine enforces these as far as it can. A harness refuses the whole command when any part of it matches a rule, so run each risky step as its own command, and read a refusal as a refusal of that step only.
"""

LEVEL_LABEL = {"deny": "Denied", "ask": "Asks first", "allow-and-report": "Allowed and reported"}

MANIFEST_VERSION = 1


def folder(home: Path) -> Path:
    return home / ".config" / "agents"


def instructions_path(home: Path) -> Path:
    return folder(home) / "AGENTS.md"


def manifest_path(home: Path) -> Path:
    return folder(home) / "set-up-machine.json"


def backups_path(home: Path) -> Path:
    return folder(home) / "backups"


def read_text(path: Path):
    try:
        return path.read_text()
    except FileNotFoundError:
        return None


def rule_lines(rules: list) -> list:
    return [
        f"- **{LEVEL_LABEL[r.level]}:** {r.summary}. {r.reason} {'Instead: ' if r.level == 'deny' else ''}{r.instruction}"
        for r in rules
    ]


def render_block(rules: list) -> str:
    return "\n".join([BEGIN, BLOCK_INTRO, *rule_lines(rules), END])


def plan_instructions(home: Path, rules: list):
    """The shared file with its generated block brought up to date; everything outside the block is kept."""
    path = instructions_path(home)
    old = read_text(path)
    block = render_block(rules)
    if old is None:
        new = f"{NEW_FILE_HEAD}\n{block}\n"
    elif BEGIN in old:
        before, rest = old.split(BEGIN, 1)
        if END not in rest:
            raise ValueError(f"{path} has the rules start marker without its end marker; restore it by hand")
        new = before + block + rest.split(END, 1)[1]
    else:
        new = old.rstrip("\n") + ("\n\n" if old.strip() else "") + block + "\n"
    section = Section("Shared global instructions", path, show_diff=True)
    return section, FileWrite(path, old, new)


def load_manifest(home: Path) -> dict:
    text = read_text(manifest_path(home))
    if text is None:
        return {"version": MANIFEST_VERSION, "harnesses": {}}
    data = json.loads(text)
    if data.get("version") != MANIFEST_VERSION:
        raise ValueError(f"{manifest_path(home)}: unsupported manifest version {data.get('version')!r}")
    data.setdefault("harnesses", {})
    return data


def manifest_write(home: Path, old_manifest_text, harnesses: dict) -> FileWrite:
    data = {
        "version": MANIFEST_VERSION,
        "about": "Entries set-up-machine wrote into each harness's files. It removes or loosens only these; anything else there is someone else's.",
        "harnesses": harnesses,
    }
    return FileWrite(manifest_path(home), old_manifest_text, json.dumps(data, indent=2) + "\n")
