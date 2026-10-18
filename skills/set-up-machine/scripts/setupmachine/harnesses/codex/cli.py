"""Codex / cli: audit the shared local configuration for this client.

The shared module owns instructions, hooks, rules, plugins and skills. This adapter selects the environment's declared config; it never infers a running chat's effective settings.
"""
from pathlib import Path

from ...checks import Cell

from . import present as shared_present

from . import (check_guardrails, check_plugins, check_skills, read, write)
from . import check_config as shared_config, check_instructions as shared_instructions, check_sandbox as shared_sandbox

ID, LABEL, ENV = "codex", "Codex", "cli"


def present(home: Path) -> bool:
    return shared_present(home)


def check_sandbox(ctx) -> Cell:
    return shared_sandbox(ctx, ENV)


def check_config(ctx) -> Cell:
    return shared_config(ctx, ENV)


def check_instructions(ctx) -> Cell:
    return shared_instructions(ctx, ENV)
