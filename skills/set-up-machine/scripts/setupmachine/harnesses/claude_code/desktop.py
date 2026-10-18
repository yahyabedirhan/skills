"""Claude Code in the Claude desktop app, a local session: it reads the same `~/.claude/` as the
CLI, and keeps its permission mode and worktree settings in the app (`references/claude-code/desktop.md`).
"""
from __future__ import annotations

from pathlib import Path

from . import (check_guardrails, check_instructions, check_plugins, check_skills, read, write)  # noqa: F401
from ...checks import Cell, na

ID, LABEL = "claude-code", "Claude Code"
ENV = "desktop"
# Where the desktop app keeps the Claude Code it downloads: macOS, then Windows.
MARKS = (Path("Library/Application Support/Claude/claude-code"), Path("AppData/Roaming/Claude/claude-code"))


def present(home: Path) -> bool:
    return any((home / mark).is_dir() for mark in MARKS)


def check_sandbox(ctx) -> Cell:
    return na("set-up-machine declares no sandbox for Claude Code; the app's permission mode is its own setting")


def check_config(ctx) -> Cell:
    return na("the declared config is ~/.claude/settings.json, which the Claude Code / cli row checks")
