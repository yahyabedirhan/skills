# Claude Code cloud

How to audit a Claude Code cloud session: one Anthropic-managed Ubuntu VM per session, with a fresh clone of the repo, started from claude.ai/code, the Claude app, the desktop app's **Cloud** choice or `claude --cloud`. Docs: [cloud environments](https://code.claude.com/docs/en/cloud-environments), [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web), [hooks](https://code.claude.com/docs/en/hooks). The CLI and the desktop app are the other environments of this harness (index.md).

## Found

Found when `CLAUDE_CODE_REMOTE` is `true`, which a cloud VM sets and a machine never does. A `--home` fixture on the VM is still found. On the VM the CLI row is not found, even though `claude` is on `PATH`.

## What reaches the VM

From the repo: `CLAUDE.md`, `.claude/settings.json` hooks and permission rules (in a session with one repository), `.mcp.json`, `.claude/rules/`, `.claude/skills/`, `.claude/agents/` and `.claude/commands/`. From the user's machine: nothing. `~/.claude/CLAUDE.md`, `~/.claude/skills/`, user hooks and user plugins stay there. Plugins a repo turns on under `enabledPlugins` are not installed either. Organization server-managed settings do arrive.

## Install

The repo's `.claude/settings.json` runs the install on `SessionStart`, matcher `startup|resume`, behind `CLAUDE_CODE_REMOTE`, so a machine skips it. The install only installs: the skills `setup/installs.json` lists, into `~/.agents/skills` with `-a claude-code`, so each is also in `~/.claude/skills`, and the tools the repo needs, such as gitleaks. It writes no instructions or harness files and runs no audit: this skill writes the setup, and scripts only enforce and check.

- **Why a SessionStart hook, not the environment's setup script:** the setup script lives in the environment dialog on claude.ai, outside the repo, and is skipped when a cached environment exists. The hook is versioned with the repo and runs on every start and resume. It must be safe to run again.
- **Gap:** the hook runs after Claude Code launched. Whether a skill installed then is offered as a slash command in that session is not documented. Reading its `SKILL.md` works.

## Instructions

The agent applies the setup itself at session start, as on any machine. It learns this from the repo `CLAUDE.md`, or the `AGENTS.md` it links to or imports: a section titled "Claude Code cloud specific instructions". That section tells the agent, before other work, to follow this skill for harness `claude-code`, environment `cloud`, to run `verify.py --harness claude-code --env cloud`, and to stop and ask when a step needs more access. It points at the `instructions` file `setup/harnesses.json` names for the cloud environment (`harnesses.claude-code.environments.cloud`), whose `## Instructions` lines the agent follows for the session.

- **What the agent writes:** the shared file `~/.config/agents/AGENTS.md`, `~/.claude/CLAUDE.md` as a link to it, `~/.claude/rules/harness-instructions.md` from the harness's `instructions` file, and `"autoMemoryEnabled": false` in `~/.claude/settings.json` (index.md, *Instructions*). The session started before these existed, so the agent reads the shared file itself for this session; a resumed process on the same VM loads the link. Do not append the cloud-only lines to the shared file.
- **Audit:** `ok` when the repo's settings have a `SessionStart` hook, the cloud instructions file has an `## Instructions` section, the repo's cloud section names that file's path, `~/.claude/CLAUDE.md` links to the shared file, the harness instructions file matches its source and memory is off. `FAIL` when cloud instructions are declared and one is missing. `gap` with no clone to read, or when the repo declares no cloud instructions.

## Guardrails

Hooks are read when the session starts, so the agent's own `~/.claude/settings.json` comes too late for this session. The guardrail is a match-all `PreToolUse` group in the repo's `.claude/settings.json`, behind the same variable:

```json
{"matcher": "*", "hooks": [{"type": "command", "timeout": 10,
  "command": "[ \"$CLAUDE_CODE_REMOTE\" = true ] && [ -f \"$HOME/.claude/skills/set-up-machine/scripts/pre_tool_hook.py\" ] && python3 \"$HOME/.claude/skills/set-up-machine/scripts/pre_tool_hook.py\" --harness claude-code || true"}]}
```

On a machine the variable is unset, so the user-level hook (index.md, *Hook wiring*) stays the only one. On the VM, do not add the user-level hook too: two hooks would report each allow-and-report call twice. The command fails open until the install has put the script there.

- **Ask rows:** a cloud session has the same permission modes, chosen per session. A probe on 2026-09-29 saw a permission prompt stall the session even in auto mode; the hook still refuses `approver: "user"` rows in `auto`, `dontAsk` and `bypassPermissions`.
- **Personal permissions:** a `gap`. The repo's settings hold no personal lists, so the hook alone refuses them.
- **Audit:** `ok` when a match-all group runs an existing installed `pre_tool_hook.py` with `--harness claude-code` (`$HOME` and `~/` are expanded) and `disableAllHooks` isn't `true`.

## Sandbox

`gap`: commands run on the VM. The network level (None, Trusted, Full or Custom) is set on the cloud environment, and nothing on the VM shows it. GitHub goes through a proxy that keeps the credentials off the VM: `gh` is installed, `gh api` works, and GraphQL is blocked, so `gh pr` and `gh issue` fail.

## Plugins

`gap`: a cloud session installs no plugin bundle, from user or repo settings, and an agent never signs a server in. A repo's `.mcp.json` loads. Whether claude.ai connectors load is `not checked`.

## Skills

Each listed skill in `~/.claude/skills` or the repo's `.claude/skills`. Skills enabled on claude.ai load too, and the verifier can't see them.

## Config

The model is picked when the session starts, and environment variables and network secrets are set on the environment. A cloud `config` in `setup/harnesses.json` has no file to land in: each key is a `gap`. The harness's shared config describes `~/.claude/settings.json` on a machine and doesn't apply here.

## Checking it

The verifier's `Claude Code / cloud` row (`verify.py --harness claude-code --env cloud`), from `scripts/setupmachine/harnesses/claude_code/cloud.py`:

- **instructions:** the repo's `SessionStart` hook, the repo's cloud section naming the cloud instructions file, that file's `## Instructions` section, the `~/.claude/CLAUDE.md` link, `~/.claude/rules/harness-instructions.md` and memory off.
- **guardrails:** the repo's match-all `PreToolUse` group runs the installed hook with `--harness claude-code`. Personal permissions are a `gap`.
- **sandbox:** `gap`.
- **plugins:** `gap`, or `n/a` when `installs.json` lists none for Claude Code.
- **skills:** each listed skill in `~/.claude/skills` or the repo's `.claude/skills`.
- **config:** `n/a`, or a `gap` when a cloud config is declared.

In a cloud session, after the install and the agent's own setup: `rm -rf x` is refused by the hook, and `git status` is allowed.
