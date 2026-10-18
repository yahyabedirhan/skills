# Codex CLI

The CLI environment of Codex: terminal and IDE sessions. This page says how it is detected, what its sandbox and config rows mean and how the verifier checks it. The rest is in [index.md](index.md). Preserve the existing installation channel.

## The environment

### Presence detection

The resolved Codex config home exists, or `codex` is on `PATH`. Fixture homes use their own config folder.

## Harness rows

### Sandbox and config

Read `setup/harnesses.json` > `harnesses` > `codex` > `environments` > `cli` > `config`, falling back to the shared `setup/harnesses.json` > `harnesses` > `codex` > `config`.
Apply only its declared keys to the resolved `config.toml`, as `index.md` specifies.

## Checking it

Run `python3 <skill-folder>/scripts/verify.py --harness codex --env cli`.
The CLI adapter checks the shared instructions, guardrails, plugins and skills.
It checks this environment's declared sandbox and other config keys separately.
Run the CLI live check after the file audit passes.
