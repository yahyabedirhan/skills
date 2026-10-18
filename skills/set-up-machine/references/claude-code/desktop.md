# Claude Code desktop

The desktop environment of Claude Code: its local sessions in the Claude desktop app, on macOS and Windows. This page says how it is detected, what differs from the CLI, what its sandbox and config rows mean and how the verifier checks it. Docs: [desktop](https://code.claude.com/docs/en/desktop). The app's local sessions read the same settings files as the CLI ([settings](https://code.claude.com/docs/en/settings)) and load personal skills from `~/.claude/skills`, so `index.md` applies as written. A session started as **Cloud** in the app is a cloud session, as `cloud.md` describes.

## The environment

### Presence detection

Present when the app's own Claude Code folder exists: `~/Library/Application Support/Claude/claude-code/` on macOS, `~/AppData/Roaming/Claude/claude-code/` on Windows. The app downloads its Claude Code there; `claude` on `PATH` is the CLI's.

### What differs from the CLI

- **Permission mode:** the app's mode selector, with Manual, Accept edits, Plan, Auto and Bypass permissions, is remembered per folder and wins over `~/.claude/settings.json` > `permissions` > `defaultMode`. A session in Auto or Bypass permissions is unattended, so the hook refuses `approver: "user"` rows there as it does in the CLI, as `index.md` > 'Guardrails' > 'Auto mode' describes.
- **Worktrees:** location, branch prefix and auto-archive are app settings, in Settings > Claude Code, not keys this skill writes.
- **Plugins:** installed plugins show under **+** > **Plugins** in a local session. They are not available in WSL.
- **Instructions:** the desktop page doesn't name `~/.claude/CLAUDE.md`. It loads as user instructions in every session ([memory](https://code.claude.com/docs/en/memory)); a probe in the app is the check: `/context` lists it under memory files.

## Harness rows

### Sandbox and config

Nothing to write: the app has no sandbox setting of its own, and the declared config is `~/.claude/settings.json`, which the CLI row merges and checks, as `cli.md` > 'Config' describes.

## Verification

The verifier's `Claude Code / desktop` row (`verify.py --harness claude-code --env desktop`), from `scripts/setupmachine/harnesses/claude_code/desktop.py`:

- **instructions, guardrails, plugins, skills:** the shared checks, as `index.md` > 'Verification' describes. They read the same files as the CLI row.
- **sandbox:** `n/a`.
- **config:** `n/a`: the CLI row checks the same file.
