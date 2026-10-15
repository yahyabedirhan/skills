# Cursor cloud

How to audit a Cursor cloud agent, the VM Cursor starts from a Build. Docs: [setup](https://cursor.com/docs/cloud-agent/setup), [skills](https://cursor.com/docs/skills), [hooks](https://cursor.com/docs/hooks). The desktop app and the `cursor-agent` CLI are the other environments of this harness (index.md).

## Found

Found when `/run/cursor/api.sock` is a socket. That is the VM, so a `--home` fixture on the VM is still found, the same way a CLI on `PATH` is. A laptop has no socket, and this row is not graded there.

## Instructions

The Build only installs: the repo's environment file runs an install that puts the skills and tools on the VM. It writes no instructions and no harness files, and it runs no audit. The agent applies the setup itself at session start, as on any machine: this skill writes the setup, and scripts only enforce and check.

The agent learns this at start from Cursor's documented channel for cloud-only instructions, a section of the repo `AGENTS.md` titled "Cursor Cloud specific instructions" ([setup](https://cursor.com/docs/cloud-agent/setup)). That section tells the agent, before other work, to follow this skill for harness `cursor`, environment `cloud` (first-time setup, or a reconcile), to run `verify.py --harness cursor --env cloud`, and to stop and ask when a step needs more access. It points at the `instructions` file `setup/harnesses.json` names for the cloud environment (`harnesses.cursor.environments.cloud`), whose `## Instructions` lines the agent follows for the session. A `.cursor/CLOUD.md` file, which a Cursor staff answer on the forum mentions, was not seen loading, so this skill does not use it.

`~/.config/agents/AGENTS.md` is the shared file, written by the agent as on any machine, and the `setup` line checks it. Do not append the cloud-only lines to the shared file.

- **Audit:** `ok` when `.cursor/environment.json` is a JSON object with an `install` string, the cloud instructions file has an `## Instructions` section, and the repo `AGENTS.md` has a "Cursor Cloud specific instructions" section that names that file's path. `FAIL` when the environment is declared and one of those is missing. `gap` when the repo has no environment file and `setup/harnesses.json` names no cloud instructions, or when there is no clone to read.

## Guardrails

A cloud agent runs project command hooks from `.cursor/hooks.json` only. It does not load `~/.cursor/hooks.json`. It runs `beforeShellExecution`, `beforeReadFile` and `preToolUse`. It does not run `beforeMCPExecution`. Commands auto-run: there is no ask prompt, and the hook's refusal is the stop.

The command is the same one Cursor's CLI uses, `[ -f <script> ] && python3 <script> --harness cursor || echo '{}'`, with `<script>` the installed `pre_tool_hook.py`. `--harness cursor` is the harness id; every Cursor environment reads the same payload. The `echo '{}'` matters: an empty answer is invalid JSON, which blocks. When the script is missing the command fails open.

- **Audit:** `ok` for an event whose command names an existing `pre_tool_hook.py` and `--harness cursor`. `$HOME` and `~/` in the path are expanded. `FAIL` when the command is missing, names no script, or the script is not a file. `beforeMCPExecution` is a `gap`.

## Sandbox

`gap`: commands run on the VM, with no workspace sandbox. Network mode (Default, Default with an allowlist, or Allowlist only) is set in the dashboard. Nothing on the VM shows which mode is on.

## Plugins

`gap`: MCP servers are connected in the dashboard, per user. Nothing on the VM lists them. A bundle in `setup/installs.json` does not reach this harness. An agent never signs a server in.

## Skills

The process scans these folders when it starts: `~/.cursor/skills`, `~/.agents/skills`, `<repo>/.cursor/skills`, `<repo>/.agents/skills`, plus built-in skills and plugins. A folder created after the process has started is not a slash command until the next start. Reading the skill file still works.

Install each skill as ../workstation.md, *A skill*, says, into `~/.agents/skills`. Also link each installed skill into `~/.cursor/skills`, so both startup folders hold it. Cursor does not copy `~/.agents/skills` onto a cloud VM by itself (index.md, *Skills*).

- **Audit:** each listed skill has a `SKILL.md` in one of the four folders above.

## Config

When `setup/harnesses.json` names a Cursor cloud `config`, it is a JSON object. `secrets` is a list of environment variable names the dashboard must set. Check a name with the environment; never print a value. An empty list means none. Any other key is a `gap`: the dashboard holds it, and no file on the VM does.

## Hook wiring

The wiring is the committed `.cursor/hooks.json` (*Guardrails*). This skill does not write it. The hook fails open when the script is missing, except that Cursor treats an empty stdout as invalid JSON, which is why the command prints `{}`.

## Gaps

Network mode, dashboard MCP servers, and whether a skill installed before the process started is offered as a slash command. `beforeMCPExecution` does not run. A cold start is a new VM, which this check cannot start.

## Checking it

The verifier's `Cursor / cloud` row (`verify.py --harness cursor --env cloud`), from `scripts/setupmachine/harnesses/cursor/cloud.py`:

- **instructions:** `.cursor/environment.json` has an `install` string, and the repo `AGENTS.md` cloud section names the cloud instructions file, which has an `## Instructions` section. `gap` when the repo has neither the environment file nor declared cloud instructions.
- **guardrails:** `beforeShellExecution`, `beforeReadFile` and `preToolUse` each run an existing `pre_tool_hook.py` with `--harness cursor`. `beforeMCPExecution` is a `gap`.
- **sandbox:** `gap`.
- **plugins:** `gap`.
- **skills:** each listed skill is in `~/.cursor/skills`, `~/.agents/skills`, or the repo's `.cursor/skills` or `.agents/skills`.
- **config:** each `secrets` name is set in the real home, by name only. An empty list is `ok`. An unknown key is a `gap`. `n/a` without a declared config.

On a cloud VM, after the install and the agent's own setup: `rm -rf x` is refused by the hook, and `git status` is allowed. A skill added after the process started is readable as a file and is not a slash command in that process. Whether a skill installed during the Build is a slash command on a cold start has not been observed.
