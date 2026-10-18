"""ALL: the one list of harness environments set-up-machine knows, in the order the verifier prints them.

Each harness is a package. It holds one module per environment and shared code in `__init__.py`.
Each environment exposes ID, LABEL, ENV, present(home), read(payload), write(denials, asks), and
one check per setup area plus check_config. Add environments to ALL to expose them in --env.
"""
from . import claude_code, codex
from .codex import cli as codex_cli, desktop as codex_desktop
from .claude_code import cli as claude_code_cli, cloud as claude_code_cloud, desktop as claude_code_desktop
from . import cursor
from .cursor import cli, cloud, desktop  # noqa: F401  (loads cursor.cli, cursor.cloud, cursor.desktop)
from .grok_bot import desktop as grok_bot_desktop
from .opencode import cli as opencode_cli
from .pi import cli as pi_cli

ALL = (claude_code_cli, claude_code_desktop, claude_code_cloud, codex_cli, codex_desktop, cursor.cli, cursor.desktop, cursor.cloud,
       grok_bot_desktop, opencode_cli, pi_cli)
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
