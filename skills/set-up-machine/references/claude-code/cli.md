# Claude Code CLI

The CLI environment of Claude Code, in a terminal or an IDE extension. This page says how it is detected, what its sandbox and config rows mean and how the verifier checks it. The VS Code and JetBrains extensions read the same settings files ([settings](https://code.claude.com/docs/en/settings)). The instructions, guardrails, plugins, skills and hook wiring are in `index.md`; this page holds what only the CLI row has.

## The environment

### Presence detection

Present when `~/.claude/` exists or `claude` is on `PATH`, except on a cloud VM with `CLAUDE_CODE_REMOTE=true`, which is the cloud row, as `cloud.md` describes.

## Harness rows

### Sandbox

set-up-machine declares no sandbox or approval setting for Claude Code, so the verifier's `sandbox` cell is `n/a`.

### Config

When `setup/harnesses.json` names a Claude Code `config` for this environment, or for the harness, as `../workstation.md` > 'A declared config' describes, merge each key it sets, such as `model` and `effortLevel`, into `~/.claude/settings.json`, as that file's other keys are written: back it up, write through a symlink at its target, and keep every key the declared file doesn't name, including the hooks and permission lists this skill writes. Mark each key `present, personal` or `updated, personal`. The desktop app reads the same file, so this one merge serves both local environments.

- **Activation:** a new session reads it. `/model` in a running session, the `--model` flag, the `ANTHROPIC_MODEL` environment variable and a project's `.claude/settings.json` override it: name an override you find as a `gap`.

## Checking it

The verifier's `Claude Code / cli` row (`verify.py --harness claude-code --env cli`), from `scripts/setupmachine/harnesses/claude_code/cli.py`:

- **instructions, guardrails, plugins, skills:** the shared checks, as `index.md` > 'Checking it' describes.
- **sandbox:** `n/a`.
- **config:** each key the declared Claude Code config sets has the same value in `~/.claude/settings.json`. `n/a` without a declared config.

To see Claude Code itself enforce the rows, in a throwaway folder with `--setting-sources project,local --settings <a copy of settings.json>`:

- `claude -p "Run exactly: rm -fr x" --allowedTools Bash` leaves `x` and quotes the hook's refusal; allowing `Bash` proves a rule refused it. With a settings file holding only `hooks`, `bash -lc "rm -rf x"` is refused too, which proves the hook.
- `gh api rate_limit` runs, and its line appears in the report folder.
- Writes to `.env` and `secrets/k` with `--allowedTools Write` leave them unchanged, and the session starts with no warning about a `Write(...)` rule; a Read of `sub/.env.example` works.
- For environment rows, use fake `.env` files and a fake variable, and start the session with a scrubbed environment that holds only `HOME`, `PATH`, `USER` and the fake variable, since a sample that gets through prints whatever the shell holds.
- Against the real login, `claude -p "Without tools: quote your rule about rm -rf and the file it came from."` quotes the `rm -rf` fallback from the shared file.
