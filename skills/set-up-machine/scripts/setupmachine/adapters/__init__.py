"""One module per harness. Each exposes NAME, LABEL and
plan(home, rules, owned, shared_file, os_home, tools, rules_path) -> (sections, writes, owned_after),
where tools is the list of MCP tool names to match, or None to ask the harness, and
rules_path is the table the pre-tool hook reads (None: the skill's own).
"""
from . import claude_code, codex, opencode

ADAPTERS = (claude_code, codex, opencode)
