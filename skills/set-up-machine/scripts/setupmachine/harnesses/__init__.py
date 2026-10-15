"""ALL: the one list of harness environments set-up-machine knows, in the order the verifier prints them.

A harness is a package or, until it is migrated, a single module. A package holds one module per
environment (cursor/cli.py, cursor/desktop.py, cursor/cloud.py) and its __init__.py holds what the
environments share. Each environment module exposes the same names: ID (the harness id, the same
for every environment of a harness), LABEL (the harness name) and ENV (the environment, None for a
module not yet split into environments: claude_code.py, codex.py); present(home); read(payload)
and write(denials, asks) for the hook; and check_instructions, check_guardrails, check_sandbox,
check_plugins, check_skills and check_config, each taking the run's context and returning a Cell.
To add an environment, write its module and its reference page, then add it here.
"""
from . import claude_code, codex
from . import cursor
from .cursor import cli, cloud, desktop  # noqa: F401  (loads cursor.cli, cursor.cloud, cursor.desktop)
from .grok_bot import desktop as grok_bot_desktop
from .opencode import cli as opencode_cli
from .pi import cli as pi_cli

ALL = (claude_code, codex, cursor.cli, cursor.desktop, cursor.cloud, grok_bot_desktop, opencode_cli, pi_cli)
# Every environment of a harness reads the same hook payload, so the hook takes the harness's first one.
BY_ID = {}
for _module in ALL:
    BY_ID.setdefault(_module.ID, _module)
# {harness id: (environment, ...)}: an empty tuple for a harness not yet split.
ENVIRONMENTS = {h: tuple(m.ENV for m in ALL if m.ID == h and getattr(m, "ENV", None)) for h in BY_ID}


def env_of(module):
    """The environment name, or None for a harness not yet split into environments."""
    return getattr(module, "ENV", None)


def row_label(module) -> str:
    """The verifier's row name: `Cursor / cloud`, or just the harness's name when it isn't split."""
    return f"{module.LABEL} / {module.ENV}" if env_of(module) else module.LABEL
