# Codex MCP

How a plugin entry becomes Codex MCP settings. The steps are in `codex.md`, *Plugins*. Read this when an entry has `mcp_policy`, a standalone server, or `require_oauth`.

Docs: [MCP configuration](https://learn.chatgpt.com/docs/extend/mcp), [developer commands](https://learn.chatgpt.com/docs/developer-commands), [plugin formats](https://developers.openai.com/plugins/build/plugins).

## What gets written

The server id is the entry's `name`.

- A bundle's policy goes in `[plugins."<plugin>@<marketplace>".mcp_servers.<name>]`.
- A standalone server's `server` object goes in `[mcp_servers.<name>]`, with the policy keys beside it.
- `enabled_tools` and `disabled_tools` are written as those keys. `approval_mode` is written as `default_tools_approval_mode`. `require_oauth` is not written: it is only an audit flag.

Tool names come from `agents/permissions.json` and the rule table (workstation.md). `propose` unions those names with any list still on `mcp_policy`. A deny row wins over an allow row for the same tool.

`propose(text, entry)` in `scripts/setupmachine/harnesses/codex.py` returns the TOML and writes nothing. It keeps undeclared keys and comments, because the file holds choices this skill does not own. It keeps a stricter tool list already in the file: more disabled tools, or a shorter enabled list. It refuses an unfamiliar TOML form instead of rewriting the file. Apply the skill's backup and approval steps to the diff it returns.

## OAuth

When `require_oauth` is true, keep the server disabled until `codex mcp login <name>` shows the server connected. Never test the exclusion by calling the tool. A disabled server reports `unsupported` in `codex mcp list --json`. You may enable it only for that listing, then restore the disabled state unless the login is connected. Codex 0.162.1 reports a connected login as `o_auth`.

On a headless machine, the browser callback opens on the wrong machine. Leave the login process running. The user forwards the callback to the listener on the machine that runs Codex. Treat that URL as a secret. Never put it in a repository, a log, or shell history.

`verify.py` reads the resolved Codex home. With a CLI it reads `codex mcp list --json` and no credential file. A missing login is a `gap` that names the login command. The file check does not prove which tools the current session can see.

## What an install does not prove

Codex 0.162.1 accepts a portable Claude-compatible bundle. A Claude LSP declaration or a harness-specific mod API does not establish working Codex tools. Read the bundle's manifest before claiming parity. Report an unsupported component as a gap even when the install succeeds.

Never call an excluded tool, including as a capability test. The exclusion comes from the permission row. It does not depend on the approval reviewer.
