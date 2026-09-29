"""One module per harness. Each exposes NAME, LABEL and
plan(home, rules, owned, shared_file, os_home, tools) -> (sections, writes, owned_after),
where tools is the list of MCP tool names to match, or None to ask the harness.
"""
from . import claude_code, codex

ADAPTERS = (claude_code, codex)
