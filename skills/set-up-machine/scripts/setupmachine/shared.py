"""The shared global instructions file, and the manifest of what set-up-machine wrote.

Both live in one harness-neutral folder, `<home>/.config/agents/`, which every
adapter reaches: Claude Code by an `@` import, harnesses without imports by a
symlink to the file.
"""
from __future__ import annotations

import json
from pathlib import Path

from .plan import Change, FileWrite, Section

BEGIN = "<!-- set-up-machine:rules start. Generated from set-up-machine's rule table: change the table, not these lines. -->"
END = "<!-- set-up-machine:rules end -->"

TITLE = "# Global agent instructions"
RULE_LINE = (
    "Only what describes this person's own workflow and explains a global rule. "
    "Anything a teammate would need goes in the project or a skill."
)

# The Defaults table: one row per role a skill may name. Values are the user's;
# set-up-machine only adds a missing row, with NO_DEFAULT as its value.
DEFAULTS_HEADING = "## Defaults"
DEFAULTS_INTRO = "Skills name a role; this table names this person's tool for it. `none` means the skill's own fallback."
ROLES = ("Session host", "Worktree tool", "Notifications", "Agent to start", "Skills repo")
NO_DEFAULT = "none"

# The personal-workflow section: the user's, never rewritten.
WORKFLOW_HEADING = "## Personal workflow"
WORKFLOW_INTRO = "Rules for how this person works that pass the team test. Anything a project or a skill needs goes there instead."

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


def defaults_table() -> str:
    rows = [f"| {role} | {NO_DEFAULT} |" for role in ROLES]
    return "\n".join(["| Role | Default |", "|---|---|", *rows])


def new_file(block: str) -> str:
    return "\n\n".join([
        TITLE, RULE_LINE, DEFAULTS_HEADING, DEFAULTS_INTRO, defaults_table(), block, WORKFLOW_HEADING, WORKFLOW_INTRO,
    ]) + "\n"


def _role_row(line: str):
    """The role a Defaults table row names, or None for any other line."""
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells[0].lower() if line.lstrip().startswith("|") and cells else None


def ensure_shape(text: str):
    """Add what the file's shape lacks: the rule line, the Defaults section and its
    role rows, and the personal-workflow section. Adds only; returns (text, what was added)."""
    lines = text.split("\n")
    added = []
    if not any(l.strip() == RULE_LINE for l in lines):
        at = 1 if lines and lines[0].startswith("# ") else 0
        lines[at:at] = ([""] if at else []) + [RULE_LINE] + ([""] if not at else [])
        added.append("the rule line at the top")
    if not any(l.strip() == DEFAULTS_HEADING for l in lines):
        at = next((i for i, l in enumerate(lines) if l.strip() == BEGIN), None)
        section = [DEFAULTS_HEADING, "", DEFAULTS_INTRO, "", *defaults_table().split("\n"), ""]
        if at is None:
            lines = _trim_end(lines) + [""] + section
        else:
            lines[at:at] = section
        added.append("the Defaults table, every role `none`")
    else:
        start = next(i for i, l in enumerate(lines) if l.strip() == DEFAULTS_HEADING)
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("#") or lines[i].strip() == BEGIN), len(lines))
        rows = [i for i in range(start + 1, end) if _role_row(lines[i]) is not None]
        have = {_role_row(lines[i]) for i in rows}
        missing = [r for r in ROLES if r.lower() not in have]
        if missing:
            new_rows = [f"| {r} | {NO_DEFAULT} |" for r in missing]
            if rows:
                lines[rows[-1] + 1:rows[-1] + 1] = new_rows
            else:
                lines[start + 1:start + 1] = ["", "| Role | Default |", "|---|---|", *new_rows]
            added.extend(f"the Defaults row {r}, `none`" for r in missing)
    if not any(l.strip() == WORKFLOW_HEADING for l in lines):
        lines = _trim_end(lines) + ["", WORKFLOW_HEADING, "", WORKFLOW_INTRO, ""]
        added.append("the personal workflow section")
    return "\n".join(lines), added


def _trim_end(lines: list) -> list:
    while lines and not lines[-1].strip():
        lines = lines[:-1]
    return lines


def plan_instructions(home: Path, rules: list):
    """The shared file with its shape completed and its generated block brought up to date.
    Outside the block it only adds what the shape lacks; nothing there is rewritten."""
    path = instructions_path(home)
    old = read_text(path)
    block = render_block(rules)
    section = Section("Shared global instructions", path, show_diff=True)
    if old is None:
        return section, FileWrite(path, old, new_file(block))
    text, added = ensure_shape(old)
    for what in added:
        section.changes.append(Change("added", what, note="the file's shape; the rest of the file is kept"))
    if BEGIN in text:
        before, rest = text.split(BEGIN, 1)
        if END not in rest:
            raise ValueError(f"{path} has the rules start marker without its end marker; restore it by hand")
        new = before + block + rest.split(END, 1)[1]
    else:
        # No block yet: it goes before the personal workflow section.
        before, after = text.split(WORKFLOW_HEADING, 1)
        new = before.rstrip("\n") + "\n\n" + block + "\n\n" + WORKFLOW_HEADING + after
    if not new.endswith("\n"):
        new += "\n"
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
