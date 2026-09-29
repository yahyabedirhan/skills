"""One module per harness. Each exposes NAME, LABEL and
plan(home, rules, owned, shared_file, os_home) -> (sections, writes, owned_after).
"""
from . import claude_code

ADAPTERS = (claude_code,)
