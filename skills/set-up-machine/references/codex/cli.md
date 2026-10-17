# Codex CLI

Set up terminal and IDE sessions with [index.md](index.md). Preserve the existing installation channel.

## Found

The resolved Codex config home exists, or `codex` is on `PATH`. Fixture homes use their own config folder.

## Config and sandbox

Read `codex.environments.cli.config` from `setup/harnesses.json`, falling back to the shared `codex.config`.
Apply only its declared keys to the resolved `config.toml`, as index.md specifies.

## Checking it

Run `python3 <skill-folder>/scripts/verify.py --harness codex --env cli`.
The CLI adapter checks the shared instructions, guardrails, plugins and skills.
It checks this environment's declared sandbox and other config keys separately.
Run the CLI live check after the file audit passes.
