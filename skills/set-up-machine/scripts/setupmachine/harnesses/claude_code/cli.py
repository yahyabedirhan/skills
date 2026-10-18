"""Claude Code's CLI, in a terminal or an IDE extension: the checks only the CLI row has, its sandbox and its declared config in `~/.claude/settings.json` , as references/claude-code/cli.md describes. The shared checks and the hook payload are in this package's __init__.py.
"""
from __future__ import annotations

from pathlib import Path

from . import (FOLDER, check_guardrails, check_instructions, check_plugins, check_skills, read, write)  # noqa: F401
from . import check_config as _config
from .cloud import present as _in_cloud
from ...checks import Cell, na, on_path

ID, LABEL = "claude-code", "Claude Code"
ENV = "cli"


def present(home: Path) -> bool:
    """`~/.claude/` or `claude` on PATH, except on a cloud VM, which is the cloud row."""
    return not _in_cloud(home) and ((home / FOLDER).is_dir() or on_path(home, "claude"))


def check_sandbox(ctx) -> Cell:
    return na("set-up-machine declares no sandbox for Claude Code")


def check_config(ctx) -> Cell:
    """Each key the declared config sets, such as `model`, has its value in ~/.claude/settings.json."""
    return _config(ctx, ENV)
