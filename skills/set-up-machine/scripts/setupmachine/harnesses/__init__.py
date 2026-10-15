"""ALL: the one list of harness environments set-up-machine knows, in the order the verifier prints them.

A harness is a package or, until it is migrated, a single module. A package holds one module per
environment (cursor/cli.py, cursor/desktop.py, cursor/cloud.py) and its __init__.py holds what the
environments share. Each environment module exposes the same names: ID, LABEL and ENV; present(home);
read(payload) and write(denials, asks) for the hook; and check_instructions, check_guardrails,
check_sandbox, check_plugins, check_skills and check_config, each taking the run's context and
returning a Cell. HARNESS (the harness id) is the module's package; ENV is None for a module that is
not yet split into environments (claude_code.py, codex.py).
To add an environment, write its module and its reference page, then add it here.
"""
from . import claude_code, codex
from .cursor import cli as cursor_cli, cloud as cursor_cloud, desktop as cursor_desktop
from .grok_bot import desktop as grok_bot_desktop
from .opencode import cli as opencode_cli
from .pi import cli as pi_cli

ALL = (claude_code, codex, cursor_cli, cursor_desktop, cursor_cloud, grok_bot_desktop, opencode_cli, pi_cli)
BY_ID = {h.ID: h for h in ALL}


def harness_of(module) -> str:
    """The harness id an environment module belongs to: `cursor` for cursor/cloud.py."""
    return getattr(module, "HARNESS", None) or module.ID


def env_of(module):
    """The environment name, or None for a harness not yet split into environments."""
    return getattr(module, "ENV", None)
