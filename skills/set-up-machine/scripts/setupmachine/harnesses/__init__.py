"""ALL: the one list of harnesses set-up-machine knows, in the order the verifier prints them.

Each module exposes the same names: ID and LABEL; present(home); read(payload) and
write(denials, asks) for the hook; and check_instructions, check_guardrails, check_sandbox,
check_plugins, check_skills and check_config, each taking the run's context and returning a Cell.
To add a harness, write its module and its reference, then add it here.
"""
from . import claude_code, codex, cursor, cursor_cloud, grok_bot, opencode, pi

ALL = (claude_code, codex, cursor, cursor_cloud, grok_bot, opencode, pi)
BY_ID = {h.ID: h for h in ALL}
