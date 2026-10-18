"""Cursor's `cursor-agent` CLI: the checks only the CLI has, its permission lists, run mode and
declared config in `~/.cursor/cli-config.json` (`references/cursor/cli.md`). The shared checks and
the hook payload are in this package's `__init__.py`.
"""
from __future__ import annotations

from pathlib import Path

from . import (FOLDER, check_instructions, check_plugins, check_skills, read, write)  # noqa: F401
from . import check_guardrails as _guardrails
from ...checks import Cell, cell, dig, json_config_cell, on_path, read_json

ID, LABEL = "cursor", "Cursor"
ENV = "cli"


def present(home: Path) -> bool:
    return (home / FOLDER / "cli-config.json").exists() or on_path(home, "cursor-agent")


def check_guardrails(ctx) -> Cell:
    return _guardrails(ctx, cli_lists=True)


def check_sandbox(ctx) -> Cell:
    """The CLI runs in Auto-review with the sandbox on."""
    path = ctx.home / FOLDER / "cli-config.json"
    data = read_json(path) or {}
    problems = []
    if data.get("approvalMode") != "auto-review":
        problems.append(("FAIL", f"{ctx.show(path)} lacks approvalMode auto-review"))
    if dig(data, "sandbox", "mode") != "enabled":
        problems.append(("FAIL", f"{ctx.show(path)} lacks sandbox.mode enabled"))
    return cell(problems)


def check_config(ctx) -> Cell:
    """Each key the declared Cursor config sets, such as `selectedModel`, has its value in `cli-config.json`."""
    return json_config_cell(ctx, ID, LABEL, ctx.home / FOLDER / "cli-config.json", env=ENV)
