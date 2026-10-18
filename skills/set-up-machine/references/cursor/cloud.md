# Cursor cloud

The cloud environment of Cursor, the VM Cursor starts from a Build. This page says how it is detected, what each harness row means on it, which gaps stay and how the verifier checks it. Docs: [setup](https://cursor.com/docs/cloud-agent/setup), [skills](https://cursor.com/docs/skills), [hooks](https://cursor.com/docs/hooks). The desktop app and the `cursor-agent` CLI are the other environments of this harness, as `index.md` describes.

## The environment

### Presence detection

Present when `/run/cursor/api.sock` is a socket. That is the VM, so a `--home` fixture on the VM is still detected, the same way a CLI on `PATH` is. A laptop has no socket, and this row is not graded there.

## Harness rows

### Instructions

- **Build:** the repo's environment file runs an install that puts the skills and tools on the VM. It writes no instructions and no harness files except the hook file, as 'Guardrails' describes, and it runs no audit.
- **Agent setup:** the agent applies the setup itself at session start, as on any machine. This skill writes the setup; scripts only enforce and check.
- **Entry point:** a section of the repo `AGENTS.md` titled "Cursor Cloud specific instructions", Cursor's documented channel for cloud-only instructions ([setup](https://cursor.com/docs/cloud-agent/setup)). This skill doesn't use a `.cursor/CLOUD.md` file: Cursor's docs don't name it, and a test saw no cloud agent load it.
- **Cloud section:** tells the agent, before other work, to follow this skill for harness `cursor`, environment `cloud`, as a first-time setup or a reconcile; to run `verify.py --harness cursor --env cloud`; and to stop and ask when a step needs more access.
- **Cloud instructions file:** the file the key `setup/harnesses.json` > `harnesses` > `cursor` > `environments` > `cloud` > `instructions` names. The agent follows its `## Instructions` lines for the session.

`~/.config/agents/AGENTS.md` is the shared file, written by the agent as on any machine, and the `setup` line checks it. Do not append the cloud-only lines to the shared file.

- **Audit:** `ok` when `.cursor/environment.json` is a JSON object with an `install` string, the cloud instructions file has an `## Instructions` section, and the repo `AGENTS.md` has a 'Cursor Cloud specific instructions' section that names that file's path. `FAIL` when the environment is declared and one of those is missing. `gap` when the repo has no environment file and `setup/harnesses.json` names no cloud instructions, or when there is no clone to read.

### Guardrails

- **Hook file:** a cloud agent runs command hooks from one file, `/agent/.cursor/hooks.json`. Its exec daemon runs from `/agent`, the first workspace folder, and loads project hooks from there only, and only at session startup. There is no file watcher; a later edit loads only through the daemon's skill reload. In a multi-repo environment, none of `<repo>/.cursor/hooks.json`, `~/.cursor/hooks.json`, `/agent/repos/.cursor/hooks.json` or `/etc/cursor/hooks.json` runs. Cursor's [hooks](https://cursor.com/docs/hooks) page agrees that user-level hooks don't reach a cloud agent.
- **Writer:** the Build writes the file, the one exception to the rule that the Build only installs: the hook is the enforcement tool, not setup, and the agent's own setup at session start comes after the daemon has read it. `/agent` is root-owned; the install writes with `sudo -n`, which works on the VM. A repo's own `.cursor/hooks.json` stays, for single-repo environments and the CLI.
- **Events:** `beforeShellExecution`, `beforeReadFile` and `preToolUse`. `beforeMCPExecution` doesn't run. Commands auto-run: there is no ask prompt, and the hook's refusal is the stop.
- **Command:** the same one Cursor's CLI uses, `[ -f <script> ] && python3 <script> --harness cursor || echo '{}'`, with `<script>` the installed `pre_tool_hook.py`. `--harness cursor` is the harness id; every Cursor environment reads the same payload. The `echo '{}'` matters: an empty answer is invalid JSON, which blocks. When the script is missing the command fails open.

- **Audit:** `FAIL` when `/agent/.cursor/hooks.json` is missing. `ok` for an event whose command names an existing `pre_tool_hook.py` and `--harness cursor`. `$HOME` and `~/` in the path are expanded. `FAIL` when the command is missing, names no script, or the script is not a file. `beforeMCPExecution` is a `gap`.

### Sandbox

`gap`: commands run on the VM, with no workspace sandbox. The network mode, Default, Default with an allowlist, or Allowlist only, is set in the dashboard. Nothing on the VM shows which mode is on.

### Plugins

`gap`: MCP servers are connected in the dashboard, per user. Nothing on the VM lists them. A bundle in `setup/installs.json` does not reach this harness. An agent never signs a server in.

### Skills

The process scans these folders when it starts: `~/.cursor/skills`, `~/.agents/skills`, `<repo>/.cursor/skills`, `<repo>/.agents/skills`, plus built-in skills and plugins. A folder created after the process has started is not a slash command until the next start. Reading the skill file still works.

Install each skill as the item `../workstation.md` > `setup/installs.json` > **A skill** says, into `~/.agents/skills`. Also link each installed skill into `~/.cursor/skills`, so both startup folders hold it. Cursor does not copy `~/.agents/skills` onto a cloud VM by itself, as `index.md` > 'Skills' describes.

- **Audit:** each listed skill has a `SKILL.md` in one of the four folders above.

### Config

When `setup/harnesses.json` names a Cursor cloud `config`, it is a JSON object. `secrets` is a list of environment variable names the dashboard must set. Check a name with the environment; never print a value. An empty list means none. Any other key is a `gap`: the dashboard holds it, and no file on the VM does.

### Hook wiring

The wiring is `/agent/.cursor/hooks.json`, which the Build writes, as 'Guardrails' describes. The agent does not write it: a file written after startup is not loaded. The hook fails open when the script is missing, except that Cursor treats an empty stdout as invalid JSON, which is why the command prints `{}`.

## Known limits

### Gaps

- **Network mode:** set in the dashboard; nothing on the VM shows it.
- **MCP servers:** connected in the dashboard; nothing on the VM shows them.
- **Slash commands:** whether a skill installed before the process started is offered as a slash command, such as one installed during the Build on a cold start.
- **MCP hook:** `beforeMCPExecution` doesn't run.
- **Cold start:** a new VM, which this check can't start.
- **Build snapshot:** whether a file under `/agent` written during the Build survives into the Build snapshot is unknown.

### Notes

- The hook files a multi-repo cloud agent runs were tested on 2026-10-15.

## Checking it

The verifier's `Cursor / cloud` row (`verify.py --harness cursor --env cloud`), from `scripts/setupmachine/harnesses/cursor/cloud.py`:

- **instructions:** `.cursor/environment.json` has an `install` string, and the repo `AGENTS.md` cloud section names the cloud instructions file, which has an `## Instructions` section. `gap` when the repo has neither the environment file nor declared cloud instructions.
- **guardrails:** `/agent/.cursor/hooks.json` exists, and `beforeShellExecution`, `beforeReadFile` and `preToolUse` each run an existing `pre_tool_hook.py` with `--harness cursor`. `beforeMCPExecution` is a `gap`.
- **sandbox:** `gap`.
- **plugins:** `gap`.
- **skills:** each listed skill is in `~/.cursor/skills`, `~/.agents/skills`, or the repo's `.cursor/skills` or `.agents/skills`.
- **config:** each `secrets` name is set in the real home, by name only. An empty list is `ok`. An unknown key is a `gap`. `n/a` without a declared config.

On a cloud VM, after the install and the agent's own setup: `rm -rf x` is refused by the hook, and `git status` is allowed. A skill added after the process started is readable as a file and is not a slash command in that process.
