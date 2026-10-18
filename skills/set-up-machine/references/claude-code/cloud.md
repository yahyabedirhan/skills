# Claude Code cloud

The cloud environment of Claude Code. This page says what a cloud session is, how it is detected, what reaches it, the two ways it is set up, what each harness row means on it and how the verifier checks it. The CLI and the desktop app are the other environments of this harness, as `index.md` describes.

## Environment

### Cloud VM runtime

One Anthropic-managed Ubuntu VM per session, with a fresh clone of the repo. It starts from claude.ai/code, the Claude app, the desktop app's **Cloud** choice or `claude --cloud`. Docs: [cloud environments](https://code.claude.com/docs/en/cloud-environments), [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web), [hooks](https://code.claude.com/docs/en/hooks).

### Cloud session detection

Present when `CLAUDE_CODE_REMOTE=true`, which a cloud VM sets and the local machine or a remote machine never does. A `--home` fixture on the VM is still detected. On the VM the CLI row is not detected, even though `claude` is on `PATH`.

### VM inputs

- **Repo:**
  - `CLAUDE.md`, `.mcp.json`, `.claude/rules/`, `.claude/skills/`, `.claude/agents/` and `.claude/commands/`.
  - The hooks and permission rules in `.claude/settings.json`, in a session with one repository.
  - Not the plugins it turns on under `enabledPlugins`.
- **User machine:** nothing. `~/.claude/CLAUDE.md`, `~/.claude/skills/`, user hooks and user plugins stay there.
- **Organization:** its server-managed settings.
- **claude.ai account:** its enabled skills and connectors.
- **Cloud environment:** what its setup script leaves on disk, its environment variables, and its network secrets through the proxy.

## Setup routes

A cloud session is set up in one of two ways, and `~/.local/share/agents/environment-setup.json` tells them apart:

- **Repo setup**, without that file: the repo's `SessionStart` install, then the agent's own setup, as *Repo setup* describes.
- **Environment setup**, with that file: the cloud environment's setup script sets the session up, as *Environment setup* describes.

### Repo setup

The repo supplies the setup: a hook installs the skills and tools, and the agent applies the rest at session start.

#### Install

The install puts the skills and tools on the VM. The agent's own setup comes after it.

- **Trigger:** the repo's `.claude/settings.json` runs the install on `SessionStart`, matcher `startup|resume`, behind `CLAUDE_CODE_REMOTE`, so a machine skips it.
- **Installs:** the skills `setup/installs.json` lists, into `~/.agents/skills` with `-a claude-code`, so each is also in `~/.claude/skills`, and the tools the repo needs, such as gitleaks.
- **Out of scope:** writing instructions or harness files, and running an audit. This skill writes the setup; scripts only enforce and check.

- **Why a SessionStart hook, not the environment's setup script:** the setup script lives in the environment dialog on claude.ai, outside the repo, and is skipped when a cached environment exists. The hook is versioned with the repo and runs on every start and resume. It must be safe to run again.
- **Gap:** the hook runs after Claude Code launched. Whether a skill installed then is offered as a slash command in that session is not documented. Reading its `SKILL.md` works.

#### Instructions

The agent applies the setup itself at session start, as on any machine:

- **Entry point:** the repo `CLAUDE.md`, or the `AGENTS.md` it links to or imports, has a section titled 'Claude Code cloud specific instructions'.
- **Cloud section:** it tells the agent, before other work, to follow this skill for harness `claude-code`, environment `cloud`, to run `verify.py --harness claude-code --env cloud`, and to stop and ask when a step needs more access.
- **Cloud instructions file:** the section points at the file named by the key `setup/harnesses.json` > `harnesses` > `claude-code` > `environments` > `cloud` > `instructions`. The agent follows that file's `## Instructions` lines for the session.

- **Written files:** the shared file `~/.config/agents/AGENTS.md`, `~/.claude/CLAUDE.md` as a link to it, `~/.claude/rules/harness-instructions.md` from the harness's `instructions` file, and `"autoMemoryEnabled": false` in `~/.claude/settings.json`, as `index.md` > 'Instructions' describes. The session started before these existed, so the agent reads the shared file itself for this session; a resumed process on the same VM loads the link. Do not append the cloud-only lines to the shared file.
- **Audit:** `ok` when the repo's settings have a `SessionStart` hook, the cloud instructions file has an `## Instructions` section, the repo's cloud section names that file's path, `~/.claude/CLAUDE.md` links to the shared file, the harness instructions file matches its source and memory is off. `FAIL` when cloud instructions are declared and one is missing. `gap` with no clone to read, or when the repo declares no cloud instructions.

#### Guardrails

In a repo setup, hooks are read when the session starts, so the agent's own `~/.claude/settings.json` comes too late for this session. The guardrail is a match-all `PreToolUse` group in the repo's `.claude/settings.json`, behind the same variable:

```json
{"matcher": "*", "hooks": [{"type": "command", "timeout": 10,
  "command": "[ \"$CLAUDE_CODE_REMOTE\" = true ] && [ -f \"$HOME/.claude/skills/set-up-machine/scripts/pre_tool_hook.py\" ] && python3 \"$HOME/.claude/skills/set-up-machine/scripts/pre_tool_hook.py\" --harness claude-code || true"}]}
```

On a machine the variable is unset, so the user-level hook stays the only one, as `index.md` > 'Hook wiring' describes. On the VM in a repo setup, the repo hook is the only one: a user-level hook beside it would report each allow-and-report call twice. An environment setup writes the user-level hook instead, as 'Environment setup' describes. The command fails open until the install has put the script there.

- **Ask rows:** a cloud session has the same permission modes, chosen per session. A permission prompt can stall a cloud session even in auto mode; the hook still refuses `approver: "user"` rows in `auto`, `dontAsk` and `bypassPermissions`.
- **Personal permissions:** a `gap`. The repo's settings hold no personal lists, so the hook alone refuses them.
- **Audit:** `ok` when a match-all group runs an existing installed `pre_tool_hook.py` with `--harness claude-code`, and the settings hold no `"disableAllHooks": true`. The audit reads `$HOME` and `~/` in the command as the home folder.

### Environment setup

The cloud environment's setup script, which `<workstation-repo>` renders, sets the session up. It runs as root before Claude Code launches, on every repo, and the environment caches the disk it leaves as a snapshot. It writes:
  - the same files the agent writes in 'Instructions';
  - `~/.claude/rules/cloud-instructions.md`, from the cloud `instructions` file;
  - a match-all `PreToolUse` hook in `~/.claude/settings.json`;
  - `~/.local/share/agents/environment-setup.json`, the marker that tells the two routes apart, last.

- **Gap:** the docs say a cloud session doesn't read `~/.claude/settings.json` and runs hooks only from the repo and server-managed settings ([settings in cloud sessions](https://code.claude.com/docs/en/settings#settings-in-cloud-sessions)). A script-written `~/.claude/CLAUDE.md` is documented to load. Whether the script-written hook fires is not tested.
- **Re-setup:** when that marker exists, `<workstation-repo>`'s cloud instructions name the command that applies the setup again. Run it instead of writing the files by hand. It changes only the current VM, so read the new instructions and rule files for the rest of the session; new sessions start from the environment's snapshot.
- **Audit:** with the marker, the instructions cell checks the `~/.claude/CLAUDE.md` link, memory off, `harness-instructions.md` and `cloud-instructions.md` against their sources, and not the repo's hook or cloud section. The guardrails cell checks the match-all group in `~/.claude/settings.json`.

## Harness rows

The rows every harness page covers, as they stand on a cloud session.

### Sandbox

`gap`: commands run on the VM. The network level is set on the cloud environment, to None, Trusted, Full or Custom, and nothing on the VM shows it. GitHub goes through a proxy that keeps the credentials off the VM: `gh` is installed, `gh api` works, and GraphQL is blocked, so `gh pr` and `gh issue` fail.

### Plugins

`gap`: a cloud session installs no plugin bundle, from user or repo settings, and an agent never signs a server in. A repo's `.mcp.json` loads. Whether claude.ai connectors load is `not checked`.

### Skills

Each listed skill in `~/.claude/skills` or the repo's `.claude/skills`. Skills enabled on claude.ai load too, and the verifier can't see them.

### Config

The model is picked when the session starts, and environment variables and network secrets are set on the environment. A cloud `config` in `setup/harnesses.json` has no file to land in: each key is a `gap`. The harness's shared config describes `~/.claude/settings.json` on a machine and doesn't apply here.

## Verification

The verifier's `Claude Code / cloud` row (`verify.py --harness claude-code --env cloud`), from `scripts/setupmachine/harnesses/claude_code/cloud.py`:

- **instructions:** the repo's `SessionStart` hook, the repo's cloud section naming the cloud instructions file, that file's `## Instructions` section, the `~/.claude/CLAUDE.md` link, `~/.claude/rules/harness-instructions.md` and memory off. With the environment's marker, it checks the link, memory off and both rule files, as 'Environment setup' describes.
- **guardrails:** the repo's match-all `PreToolUse` group runs the installed hook with `--harness claude-code`, or the one in `~/.claude/settings.json` with the environment's marker. Personal permissions are a `gap`.
- **sandbox:** `gap`.
- **plugins:** `gap`, or `n/a` when `installs.json` lists none for Claude Code.
- **skills:** each listed skill in `~/.claude/skills` or the repo's `.claude/skills`.
- **config:** `n/a`, or a `gap` when a cloud config is declared.

In a cloud session, after the install and the agent's own setup: `rm -rf x` is refused by the hook, and `git status` is allowed.
