# Pi

How to set up and audit Pi, the `pi` coding agent (`@earendil-works/pi-coding-agent`). Docs: the `docs/` folder of the installed package, chiefly `configuration.md`, `settings.md`, `skills.md`, `extensions.md`, `cli.md` and `security.md`. Checked against Pi 1.1.0 and its `dist/` source.

**Found** when `pi` is on `PATH` or the agent folder exists. The agent folder is `PI_CODING_AGENT_DIR`, else `~/.pi/agent`; a leading `~` in the variable means the home folder. Resolve it once, without printing the variable's value, and use that one folder for every path below, written `<agent-dir>`. For a fixture home, `verify.py --home <fixture>` uses `<fixture>/.pi/agent` and ignores the variable; pass `--pi-agent-dir <folder>` to test another layout.

Leave `<agent-dir>/auth.json`, `mcp-auth.json`, `trust.json`, `models-store.json` and `sessions/` unread and unwritten: they hold credentials, trust decisions and runtime state, never a setting this skill owns.

## Words

Pi's own terms, as its docs use them. Every Pi document that follows this skill uses them the same way.

**Agent folder** (`<agent-dir>`):
Where Pi keeps its user-level files: `settings.json`, the context file, `extensions/`, `skills/`, and runtime state. `~/.pi/agent` unless `PI_CODING_AGENT_DIR` says otherwise.

**Settings**:
`<agent-dir>/settings.json` for the user, and `.pi/settings.json` for a project, which loads only once the project is trusted. Defaults, resource paths and the `packages` list live here.

**Context file**:
An `AGENTS.md` (or `CLAUDE.md`) Pi adds to the prompt, from the agent folder and from each folder up from the working one.

**Extension**:
A TypeScript module that adds executable behavior to Pi: tools, commands, shortcuts, event handlers such as `tool_call`, model providers, session state or terminal UI. It runs inside Pi with Pi's operating-system permissions. Pi loads extensions from `<agent-dir>/extensions/`, from a trusted project's `.pi/extensions/`, and from packages. This skill's pre-tool hook is one, `<agent-dir>/extensions/set-up-machine.ts`.

**Built-in extension**:
An extension that ships with Pi and loads by default, such as `builtin:mcp`, `builtin:codemode` and `builtin:tool-search`. `-builtin:<name>` in the `extensions` setting turns one off.

**Package**:
The unit Pi installs and shares: an npm package, a git repository or a folder that bundles extensions, skills, prompt templates and themes. The `packages` setting lists them; `pi install`, `pi list`, `pi update` and `pi remove` manage them. A package is the box; what it adds is usually one or more extensions.
_In this skill_: a package is listed in the `plugins` setup area as a `bundle` for `pi` and called an **extension**, after what it adds. "Package" stays the name of Pi's `packages` setting and its commands.

**Skill, prompt template, theme**:
The other resources a package or the agent folder can hold: a skill is a `SKILL.md` folder, a prompt template a reusable `/command` prompt, a theme the terminal colors.

**Project trust**:
Whether Pi loads a project's own `.pi` settings and resources. Context files load either way. Trust is not a guardrail: it doesn't limit tool calls.

## Global instructions

- Pi loads one context file from `<agent-dir>`, the first that exists of `AGENTS.override.md`, `AGENTS.md`, `AGENTS.MD`, `CLAUDE.md` and `CLAUDE.MD`. It then adds one from each folder from the working folder up. It follows a symlink and skips a broken one. It doesn't follow `@` imports.
- `<agent-dir>/AGENTS.md` becomes a **relative symlink to the shared file**. For the default folder it's `../../.config/agents/AGENTS.md`. For another folder, compute the path from `<agent-dir>` to `~/.config/agents/AGENTS.md`. It's `present` once it's that link.
- An existing `AGENTS.md` there, a file or a link elsewhere, is kept and `extra`, with a `gap`: Pi reads it instead until its lines move into the shared file (global-instructions.md, *Moving a harness's file*) and the user deletes it.
- An `AGENTS.override.md` in `<agent-dir>` is kept and `extra`, with a `gap`: Pi reads it instead of the link. A `CLAUDE.md` there with no `AGENTS.md` is read until the link exists; once the link is written it's `extra`, never read.
- `--no-context-files` (`-nc`) starts a session without any context file: a `gap` line.

## Memory

No memory feature: a `none` line. Pi keeps sessions in `sessions/`, which it reloads only when the user resumes one. Install no persistent-memory extension, since memory stays off in every harness (global-instructions.md).

## Skills

- Pi discovers skills in `~/.agents/skills/` and `<agent-dir>/skills/`, follows symlinks, and loads a skill reached through two links only once, by its real path. So the skills `agents/installs.json` installs into `~/.agents/skills` reach Pi with no extra install and no `-a` flag.
- Older `npx skills` versions left one link per skill in `<agent-dir>/skills/`, pointing into `~/.agents/skills`. A link that resolves is harmless and `extra`. A broken link, such as one left after a skill was removed, is `extra`, for the user to remove: Pi skips it without a word.
- A project's `.agents/skills/` loads only after the user trusts the project.

## Declared defaults

The workstation repo's optional `agents/pi.json` declares Pi settings (workstation.md). Compare each key it declares with `<agent-dir>/settings.json`:

- `present, personal` when the values are equal; otherwise `updated, personal`, showing the current and the declared value.
- Write only the declared keys, and keep every other key as it is. Pi writes runtime state into the same file, such as `lastChangelogVersion` and `deviceId`, and other tools add their own keys.
- A `settings.json` that is a symlink is written at its target. A file that isn't valid JSON stops the change until the user fixes it.
- Back up the file as SKILL.md, *Back up*, says: `.pi/agent/settings.json` under the backup folder for the default folder. For an agent folder outside the home folder, name the destination in the diff, `pi/settings.json` under the backup folder.
- A key the file no longer declares keeps its persisted value, for the user to remove.
- A `packages` key in `agents/pi.json` is a `gap`, never compared or written: Pi extensions come only from the plugins list (*Plugins*), so one file says what Pi loads. Tell the user to move each entry into `plugins`.
- **Activation:** a new session reads the change. A running session reads it after `/reload`.
- **Gaps:** a trusted project's `.pi/settings.json` overrides these keys, and CLI flags such as `--model` override them for one run.

## Permissions

Pi has no permission system. It asks for no approval before a tool call (`docs/security.md`), and has no deny, ask or allow list. The pre-tool hook, wired through an extension, is the only enforcement: it refuses deny rows, asks the user for ask rows in a Pi dialog, and reports allow-and-report rows. Write no native entry for any row.

## Command rows

No native entry. The hook checks the `command` of the `bash` and `powershell` tools. It reads a PowerShell command as a POSIX shell command, so a PowerShell spelling can slip past a row: a `gap` line on Windows.

## File rows

No native entry. The hook checks the `path` of `read`, `edit`, `write` and `ls`, and the search glob of `grep` (`glob`) and `find` (`pattern`).

## MCP-tool rows

No native entry. Pi reads MCP servers from `<agent-dir>/mcp.json` and names their tools `mcp__<server>__<tool>`, the name the rows match, so the hook checks them as they are.

## Personal permissions

Each personal permission is `n/a` here: "Pi has no permission entries". The hook applies a personal `deny`, `ask` or `allow-and-report` row as it applies a table row. A personal `allow` row needs nothing: Pi runs every call the hook lets through.

## Plugins

The plugins setup area, from `plugins` in `agents/installs.json` (workstation.md). Docs: `packages.md` and `mcp.md`.

- **A bundle** is a Pi extension: everything Pi loads from the user or from others, installed as one unit with its tools, skills, prompt templates and themes. Pi delivers extensions through its `packages` setting. The entry names only `pi`, and its `source` is the Pi extension source as Pi's `settings.json` writes it: `npm:<name>@<version>`, `git:<host>/<owner>/<repo>@<ref>`, or an `https://` git URL. Prefer a version or a tag, since Pi keeps such a source pinned.
- **Write a bundle** into the `packages` array of `<agent-dir>/settings.json`. Pi names an extension by its npm name, or by its git host and repository path without the ref, so two sources can name one extension at different versions.
  - `present` when an entry is the exact source, as a string or as the `source` of an object entry. Keep an object entry as it is: its resource filters are the user's.
  - `added` when no entry names the extension: append the source.
  - `updated` when an entry names the same extension at another version or ref: replace that entry with the source.
  - Keep every other entry and key, and write the file as *Declared defaults* says: back it up first, write a symlink at its target, and stop on invalid JSON.
  - **Activation:** a new session installs a missing extension at startup, and reinstalls an npm one whose version differs. It leaves an existing git checkout at its old ref, so after an `updated` git entry run `pi update <source>` with the new source. `pi list` shows the configured extensions.
- **A standalone MCP server:** the entry's `server` under its `name` in `mcpServers` of `<agent-dir>/mcp.json`, keeping every other server and key. `present` when it matches, `added` when it's missing, `updated` when it differs. Back it up like `settings.json`. Pi takes server names of letters, digits, `_` and `-`.
  - A running session reads the change after `/reload`.
  - **Credentials:** a `headers` or `env` value names an environment variable, such as `${DOCS_TOKEN}`, never the secret itself. A server that uses OAuth needs the user's sign-in, with `pi mcp login <server>` or `/mcp` in a session; an agent never signs in. Pi keeps the tokens in `mcp-auth.json`.
- **`verify.py`** prints a `plugin` line per Pi entry: `ok`, or `FAIL` when the extension is missing or at another version, or the server is missing or differs. A pinned git extension is also a `FAIL` when its checkout in `<agent-dir>/git/<host>/<owner>/<repo>` is at another commit than its ref; the line names the `pi update <source>` that fixes it. Pi not set up is `n/a`. A configured extension the list leaves out is `extra`: kept, for the user to add to the list or remove with `pi remove <source>`. A matching server is a `gap` when `extensions` in `settings.json` holds `-builtin:mcp`, since that turns off the built-in MCP client that reads `mcp.json`.
- **Gaps:**
  - A trusted project's `.pi/settings.json` `packages` and `.pi/mcp.json` servers replace a global entry of the same extension or name in that project.
  - An extension that registers `/mcp`, such as `pi-mcp-adapter`, replaces the built-in MCP client, and Pi then ignores `mcp.json`. `verify.py` doesn't detect this.
  - A local path isn't a source the list takes, since one path doesn't name the same extension on every machine.

## Pre-tool hook

- **Wiring:** the extension `<agent-dir>/extensions/set-up-machine.ts`, which Pi loads from its global extension folder. Write it from [pi-extension.ts](pi-extension.ts), with `__HOOK_COMMAND__` replaced by the JSON array `["python3", "<script>", "--harness", "pi"]` (`<script>` as in SKILL.md, *Wiring*). Its `tool_call` handler runs before every tool call, built-in, extension and MCP. Calls that `codemode` scripts make with `tools.<name>(…)` reach it one by one, as nested calls.
- **Fails closed:** Pi has no native rules underneath, so a call the hook can't check is refused. When the script is gone, `python3` can't start, the hook exits non-zero, prints anything but a JSON object or takes over 10 seconds, the extension blocks the call. The agent reads that the guardrail is unavailable and that the user should run `/set-up-machine`. The hook exits non-zero on a call it can't read, a rule table it can't load, and a report line it can't write. The extension catches its own errors and turns them into the same refusal.
- **Audit:** `wired` when the file is the template with the current command. A file there without the template's first line is someone else's: a `gap`, left alone. An extension with an old command is rewritten.
- **Input:** `{"toolName", "input", "cwd", "sessionId", "hasUI"}`. `input` holds the tool's arguments: `command` for `bash` and `powershell`; `path` for the file tools; `pattern`, `path` and `glob` for `grep`; `pattern` (a glob) and `path` for `find`. The outer `codemode` call carries its script in `input.code`, which the hook doesn't read as a command.
- **Answer:** always one JSON line. `{"block": "<refusal>"}` becomes `{ block: true, reason }`, and Pi gives the agent the reason as the tool's result. `{"ask": "<question>"}` names each ask row's part, reason and instruction. `{}` lets the call run.
- **Asking:** with a UI (`ctx.hasUI`, true in the TUI and in RPC mode), the extension shows a notice, then a `ctx.ui.select` dialog with the question and two answers, No first. Pi's `ctx.ui.confirm` is the same dialog with Yes first, so `select` puts the cursor on the safe answer: Enter refuses, and so does Escape. Yes runs the call. No blocks it, and the agent reads that the user declined. Print and JSON mode have no UI, so the hook refuses every ask row there, `approver: "user"` or not.
- **Session host:** while a dialog waits, Pi reports `blocked` to the terminal itself (OSC 7501). A session host's own Pi integration can report a state of its own instead. Herdr's (version 9) reported `working`, so the user got no notice. It listens for a `herdr:blocked` event on Pi's event bus, so the extension emits that event around the dialog, and Herdr then shows the pane as `blocked`. Without that integration nothing listens, and the event does nothing.
- Other extensions in `<agent-dir>/extensions/`, such as a session host's integration, are the user's: leave them.

## Auto mode

None: Pi has no approval prompts to automate.

## Gaps

- **The only layer:** Pi has no native rules underneath, so the extension fails closed: while `python3` or the script is missing, or the hook fails, Pi refuses every tool call until `/set-up-machine` repairs it. `pi --no-extensions` starts a session without the hook in the meantime. The containment Pi offers beyond the hook is the operating system's: a container, a virtual machine or a separate user (`docs/security.md`, `docs/containerization.md`). Name this once in every audit.
- **Started without extensions:** `pi --no-extensions` (`-ne`) skips the extension. Explicit `-e <path>` extensions still load.
- **Handlers after the hook can change the call:** a `tool_call` handler can change `event.input`, and the first handler that blocks wins. Pi 1.1.0 runs the handlers in load order: `-e` extensions first, then a trusted project's extensions (its `.pi/settings.json` entries, then `.pi/extensions/`), then the global settings' entries, then `<agent-dir>/extensions/`, then the extensions from `packages`, then built-in ones. So an extension from `packages`, or a built-in one, runs after the hook and could change a call the hook already passed. Pi offers no way to run last or to check the final input before the tool runs. A project extension runs before the hook: the hook sees what it changed.
- **Child sessions without extensions:** an extension that starts child sessions in the same process can start them with extensions off, and the hook doesn't run there. The `pi-subagents` extension (0.77.0) does this for foreground children; its setting `subagents.defaultSubagentOnlyExtensions`, listing the hook extension's path, loads it there. Check each such extension. A child without a UI gets ask rows refused.
- **The user's own commands:** `!` commands (`user_bash`) aren't tool calls, so the hook doesn't see them, as in Claude Code.
- The hook's own misses are in SKILL.md, *What it can't see*.

## What the agent sees

A refused call's tool result is the hook's refusal: each refused part, its rule, reason and instruction. For an ask row the user declined, the result starts `Refused: the user declined this call when the pre-tool hook asked.`, followed by the question. When the hook can't check the call, the result starts `Refused: the pre-tool hook couldn't check this call`, says why, and asks the agent to stop and have the user run `/set-up-machine`. A refused nested call fails the `codemode` script with the same text. The shared file also gives the agent the rule lines and the rejection guidance.

## Checking it

`verify.py` prints a `pi` line for the link, one per declared default, one per broken skill link, and a `hook` line for the extension. To see Pi read the setup, start it in a sandbox:

1. Make a sandbox folder, with a fresh agent folder in it. Copy `settings.json` and recreate the `AGENTS.md` link there. Copy no credential, trust or session file.
2. Run `PI_CODING_AGENT_DIR=<sandbox agent folder> pi` from an empty folder in the sandbox.
   - Result: the startup `[Context]` section lists the sandbox's `AGENTS.md`, and `[Extensions]` lists `set-up-machine.ts` once you copy the extension in.
3. Quit Pi, then read the sandbox's `settings.json`.
   - Result: the declared keys hold their values, and every other key is still there.

With no login in the sandbox, Pi still starts and shows the listing. It creates its own empty `auth.json` and `sessions/` in the sandbox, and adds `lastChangelogVersion` to its `settings.json`.

A live model turn needs the login, so check the hook with the real agent folder and the extension loaded for one run only:

1. Write the template to a file in a throwaway folder outside any git repository, with the command `["python3", "<script>", "--harness", "pi", "--config", "<temp hook.json>"]`. The temporary `hook.json` holds a `report_dir` in the throwaway folder.
2. From that folder, run `pi --no-session -e <file> --mode json "<prompt>"` for each sample below. Read the `tool_execution_end` events. Use targets that don't exist, so nothing is lost if the hook lets a call through.
   - `rm -rf .scratch/does-not-exist`: Result: refused with rule `rm-recursive-force`'s reason.
   - `git push --force-with-lease origin x`: Result: refused, naming `Pi without a UI`.
   - A `read` of `.env`: Result: refused with rule `env-files-read`. A model may decline to try; say the file doesn't exist and the run tests the guardrail.
   - `gh api rate_limit`: Result: it runs, and the report folder gets a line with `"harness": "pi"`.
   - With `--tools +codemode`, a script calling `tools.bash` with `rm -rf .scratch/does-not-exist`: Result: the nested call is refused, and the script fails with the refusal.
   - With the command's script path changed to one that doesn't exist, `ls`: Result: refused, saying the hook couldn't check the call.
3. In the TUI, `pi --no-session -e <file>`, ask for the `git push --force-with-lease origin x` again.
   - Result: a notice and the dialog appear, with the cursor on No. Under Herdr with its Pi integration, the pane shows `blocked`.
4. Press Enter.
   - Result: the call is refused as declined.
5. Ask again, move to Yes and press Enter.
   - Result: the call runs.
