"""Codex adapter: memory so far. Its global instructions, rules and hook come with its own ticket.

Facts it relies on (docs/research/harness-capabilities.md, Codex: 2.5 and 2.8):
- Codex keeps its user config in `~/.codex/config.toml`; `[features] memories = false`
  keeps local memories off (they're off by default, and a user `true` turns them on).
- Memories are written under `~/.codex/memories/`.
- A trusted project's `.codex/config.toml` can turn memories back on; only a
  system `requirements.toml` pins them off.
"""
from __future__ import annotations

import re
from pathlib import Path

from .. import memory
from ..plan import Change, FileWrite, Section
from ..shared import read_text

NAME = "codex"
LABEL = "Codex"

FEATURE_LINE = "memories = false"
_TABLE = re.compile(r"^\s*\[\s*([^\[\]]+?)\s*\]\s*(#.*)?$")
_MEMORIES = re.compile(r"^\s*memories\s*=\s*(\S+)")
_DOTTED = re.compile(r"^\s*features\s*\.\s*memories\s*=\s*(\S+)")


def config_dir(home: Path) -> Path:
    return home / ".codex"


def plan(home: Path, rules: list, owned: dict, shared_file: Path, os_home: Path, tools=None, rules_path=None):
    path = config_dir(home) / "config.toml"
    section = Section(f"{LABEL}: memory", path)
    if not config_dir(home).is_dir():
        section.changes.append(Change("none", "Codex isn't set up here (no ~/.codex); nothing to turn off"))
        return [section], [], {}
    old = read_text(path)
    new, change = set_memories_off(old or "")
    section.changes.append(change)
    section.changes.append(Change(
        "gap", "a trusted project's .codex/config.toml can set memories = true and win over this; "
        "only a system requirements.toml pins it, which the project audit relies on instead",
    ))
    writes = [FileWrite(path, old, new if change.kind != "present" else old)]
    writes += memory.remove_files(home, [config_dir(home) / "memories"], section)
    return [section], writes, {}


def set_memories_off(text: str):
    """config.toml with `memories = false` in its [features] table, and the change that says so.

    Edits the one line it needs and keeps every other line as written.
    """
    lines = text.split("\n")
    table, features_at = None, None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("[["):
            table = "[[array]]"
            continue
        m = _TABLE.match(line)
        if m:
            table = m.group(1).strip().strip('"')
            if table == "features":
                features_at = i
            continue
        found = (_MEMORIES.match(line) if table == "features" else None) or (_DOTTED.match(line) if table is None else None)
        if found:
            value = found.group(1)
            if value == "false":
                return text, Change("present", "[features] memories = false")
            lines[i] = (line[: line.index("features")] + "features.memories = false") if table is None else FEATURE_LINE
            return "\n".join(lines), Change("tightened", "[features] memories = false", note=f"was {value}")
        if table is None and re.match(r"^\s*features\s*=\s*\{", line):
            raise ValueError("~/.codex/config.toml sets features as an inline table; add memories = false to it by hand")
    if features_at is not None:
        lines.insert(features_at + 1, FEATURE_LINE)
        return "\n".join(lines), Change("added", "[features] memories = false", note="memories off")
    body = text.rstrip("\n")
    return (body + "\n\n" if body else "") + "[features]\n" + FEATURE_LINE + "\n", Change(
        "added", "[features] memories = false", note="memories off")
