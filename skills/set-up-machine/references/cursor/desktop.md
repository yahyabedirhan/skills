# Cursor desktop

The desktop app's agent: what differs from the CLI. The rules, hooks, plugins and skills it shares with the CLI are in [index.md](index.md).

## Found

Found when `~/.cursor/argv.json` or `~/.cursor/extensions/` exists, or `cursor` is on `PATH`.

## Guardrails

- The app reads neither `cli-config.json` nor Claude Code's lists, and has no user-level deny list: its hard blocks are the hooks (index.md, *Hook wiring*).
- A personal `allow` row is a `gap` here, left to the app's own approval settings.
- The hook isn't `failClosed`: a crash or timeout lets the call through, and in the app nothing native is left underneath, a `gap`.

## Sandbox and config

The app keeps its run mode and its model choice in its own settings, not in a file. Both cells are `n/a`. The declared Cursor config is the CLI's (cli.md, *Config*).

## Checking it

The verifier's Cursor desktop row, from `scripts/setupmachine/harnesses/cursor/desktop.py`, id `cursor-desktop`. The instructions, plugins and skills cells are the shared ones (index.md, *Checking it*).

- **guardrails:** the shared hook check only.
- **sandbox:** `n/a`.
- **config:** `n/a`.

After the live setup: Customize > Hooks lists the four handlers, and asking the agent to run `rm -rf x` or to send a mail is refused with the hook's message.
