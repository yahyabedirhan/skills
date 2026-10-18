# Codex desktop

The desktop environment of Codex: local chats in the desktop app. This page says how it is detected, what each harness row means on it and how the verifier checks it. The rest is in [index.md](index.md). The app and CLI share MCP configuration on the same host ([official MCP guide](https://learn.chatgpt.com/docs/extend/mcp)).

## The environment

### Presence detection

On macOS, find `~/Library/Application Support/Codex/` or `~/Library/Application Support/com.openai.codex/`. On the real machine, also check `/Applications/ChatGPT.app` and `/Applications/Codex.app` for a fresh install. System applications never establish presence in a fixture home. Other operating systems need a verified app marker before this adapter can detect them.

## Harness rows

### Instructions, guardrails, plugins and skills

Apply the shared procedure once for the selected Codex host. Keep the shared `AGENTS.md` link, native rules, trusted hook, memory setting and skill directories. Keep authentication and project trust on that machine. Configure portable plugin bundles and standalone MCP servers through Codex's own client. Treat account plugins and connected services as a separate sign-in step. An installed Claude component does not prove Codex support.

### Sandbox and config

Read `setup/harnesses.json` > `harnesses` > `codex` > `environments` > `desktop` > `config`, falling back to the shared `setup/harnesses.json` > `harnesses` > `codex` > `config`. Merge its declared keys into the same resolved `config.toml`. Use the same source file for CLI and desktop defaults when they share those choices. Report conflicting declarations before writing them. Preserve app preferences, project trust and current chats. A running chat can retain its selected model and permissions after persisted defaults change. Verify effective settings in a fresh desktop chat.

## Checking it

Run `python3 <skill-folder>/scripts/verify.py --harness codex --env desktop`. All six columns check this environment, including config when the standalone CLI is absent. The file audit cannot prove the active desktop model, hook execution, OAuth or tool availability. Use an authorized desktop chat for the live check. Record unavailable interactive checks as gaps.
