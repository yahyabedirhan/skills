# Cursor cloud

How to audit a Cursor cloud agent, the VM Cursor starts from a Build. Docs: [setup](https://cursor.com/docs/cloud-agent/setup), [skills](https://cursor.com/docs/skills), [hooks](https://cursor.com/docs/hooks). The IDE and the `cursor-agent` CLI are a different harness (cursor.md).

## Found

Found when `/run/cursor/api.sock` is a socket. That is the VM, so a `--home` fixture on the VM is still found, the same way a CLI on `PATH` is. A laptop has no socket, and this row is not graded there.

## Instructions

Cursor's documented channel for cloud-only instructions is a section of the repo `AGENTS.md` titled "Cursor Cloud specific instructions" ([setup](https://cursor.com/docs/cloud-agent/setup)). A Cursor staff answer on the forum adds `.cursor/CLOUD.md`, read by cloud agents only, after `AGENTS.md` ([forum](https://forum.cursor.com/t/is-there-a-way-to-add-rule-or-agent-md-only-for-cloud-agent/159595)). The public docs don't list that file, and a generated copy has not yet been seen loading. The file is generated and not committed. The install writes it: `setup/instructions.md`, then the text of the `instructions` file `setup/harnesses.json` names for `cursor-cloud`.

`~/.config/agents/AGENTS.md` is still the shared file, and the `setup` line checks it. Do not append the cloud-only lines to the shared file.

- **Audit:** `ok` when `.cursor/environment.json` is a JSON object with an `install` string, and `.cursor/CLOUD.md` contains the text under `## Instructions` of the cloud instructions file. `FAIL` when the harness is declared and either file is missing or the section is absent. `gap` when the repo has no environment file and `setup/harnesses.json` does not name this harness, or when there is no clone to read.

## Guardrails

A cloud agent runs project command hooks from `.cursor/hooks.json` only. It does not load `~/.cursor/hooks.json`. It runs `beforeShellExecution`, `beforeReadFile` and `preToolUse`. It does not run `beforeMCPExecution`. Commands auto-run: there is no ask prompt, and the hook's refusal is the stop.

The command is the same one Cursor's CLI uses, `[ -f <script> ] && python3 <script> --harness cursor || echo '{}'`, with `<script>` the installed `pre_tool_hook.py`. `--harness cursor` is the payload id. `--harness cursor-cloud` is the same reader. The `echo '{}'` matters: an empty answer is invalid JSON, which blocks. When the script is missing the command fails open.

- **Audit:** `ok` for an event whose command names an existing `pre_tool_hook.py` and `--harness cursor` or `--harness cursor-cloud`. `$HOME` and `~/` in the path are expanded. `FAIL` when the command is missing, names no script, or the script is not a file. `beforeMCPExecution` is a `gap`.

## Sandbox

`gap`: commands run on the VM, with no workspace sandbox. Network mode (Default, Default with an allowlist, or Allowlist only) is set in the dashboard. Nothing on the VM shows which mode is on.

## Plugins

`gap`: MCP servers are connected in the dashboard, per user. Nothing on the VM lists them. A bundle in `setup/installs.json` does not reach this harness. An agent never signs a server in.

## Skills

The process scans these folders when it starts: `~/.cursor/skills`, `~/.agents/skills`, `<repo>/.cursor/skills`, `<repo>/.agents/skills`, plus built-in skills and plugins. A folder created after the process has started is not a slash command until the next start. Reading the skill file still works.

Install each skill as workstation.md, *A skill*, says, into `~/.agents/skills`. Also link each installed skill into `~/.cursor/skills`, so both startup folders hold it. Cursor does not copy `~/.agents/skills` onto a cloud VM by itself (cursor.md).

- **Audit:** each listed skill has a `SKILL.md` in one of the four folders above.

## Config

When `setup/harnesses.json` names a Cursor cloud `config`, it is a JSON object. `secrets` is a list of environment variable names the dashboard must set. Check a name with the environment; never print a value. An empty list means none. Any other key is a `gap`: the dashboard holds it, and no file on the VM does.

## Hook wiring

The wiring is the committed `.cursor/hooks.json` (*Guardrails*). This skill does not write it. The hook fails open when the script is missing, except that Cursor treats an empty stdout as invalid JSON, which is why the command prints `{}`.

## Gaps

Network mode, dashboard MCP servers, and whether a skill installed before the process started is offered as a slash command. `beforeMCPExecution` does not run. A cold start is a new VM, which this check cannot start.

## Checking it

The verifier's Cursor cloud row, from `scripts/setupmachine/harnesses/cursor_cloud.py`:

- **instructions:** `.cursor/environment.json` has an `install` string. `.cursor/CLOUD.md` contains the `## Instructions` section. `gap` when the repo has neither the file nor a declared harness.
- **guardrails:** `beforeShellExecution`, `beforeReadFile` and `preToolUse` each run an existing `pre_tool_hook.py` with `--harness cursor` or `--harness cursor-cloud`. `beforeMCPExecution` is a `gap`.
- **sandbox:** `gap`.
- **plugins:** `gap`.
- **skills:** each listed skill is in `~/.cursor/skills`, `~/.agents/skills`, or the repo's `.cursor/skills` or `.agents/skills`.
- **config:** each `secrets` name is set in the real home, by name only. An empty list is `ok`. An unknown key is a `gap`. `n/a` without a declared config.

On a cloud VM, after the install: `rm -rf x` is refused by the hook, and `git status` is allowed. A skill added after the process started is readable as a file and is not a slash command in that process. Whether a skill installed during the Build is a slash command on a cold start has not been observed.
