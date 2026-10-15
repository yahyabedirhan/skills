"""Cursor's desktop app, the IDE agent: it reads the same rules, hooks, MCP servers and skills as
the CLI, but no permission lists and no run mode from a file (references/cursor/desktop.md).
"""
from __future__ import annotations

from pathlib import Path

from . import (FOLDER, check_instructions, check_plugins, check_skills, read, write)  # noqa: F401
from . import check_guardrails as _guardrails
from ...checks import Cell, na, on_path

ID, LABEL = "cursor", "Cursor"
ENV = "desktop"
# What the desktop app writes. cli-config.json is the CLI's.
MARKS = ("argv.json", "extensions")


def present(home: Path) -> bool:
    return any((home / FOLDER / mark).exists() for mark in MARKS) or on_path(home, "cursor")


def check_guardrails(ctx) -> Cell:
    """The hook only: the desktop app has no allow or deny list."""
    return _guardrails(ctx, cli_lists=False)


def check_sandbox(ctx) -> Cell:
    return na("the desktop app's run mode is in its own settings, not in a file")


def check_config(ctx) -> Cell:
    return na("the declared Cursor config is the CLI's cli-config.json; the desktop app keeps its own model choice")
