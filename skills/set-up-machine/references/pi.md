# Pi

How to set up and audit Pi, the `pi` coding agent (`@earendil-works/pi-coding-agent`). Docs: the `docs/` folder of the installed package, chiefly `configuration.md`, `settings.md`, `skills.md`, `extensions.md` and `security.md`. Checked against Pi 1.1.0 and its `dist/` source.

**Found** when `pi` is on `PATH` or the agent folder exists. The agent folder is `PI_CODING_AGENT_DIR`, else `~/.pi/agent`; a leading `~` in the variable means the home folder. Resolve it once, without printing the variable's value, and use that one folder for every path below, written `<agent-dir>`. For a fixture home, `verify.py --home <fixture>` uses `<fixture>/.pi/agent` and ignores the variable; pass `--pi-agent-dir <folder>` to test another layout.

Leave `<agent-dir>/auth.json`, `trust.json`, `models-store.json` and `sessions/` unread and unwritten: they hold credentials, trust decisions and runtime state, never a setting this skill owns.

## Global instructions

- Pi loads one context file from `<agent-dir>`, the first that exists of `AGENTS.override.md`, `AGENTS.md`, `AGENTS.MD`, `CLAUDE.md` and `CLAUDE.MD`. It then adds one from each folder from the working folder up. It follows a symlink and skips a broken one. It doesn't follow `@` imports.
- `<agent-dir>/AGENTS.md` becomes a **relative symlink to the shared file**. For the default folder it's `../../.config/agents/AGENTS.md`. For another folder, compute the path from `<agent-dir>` to `~/.config/agents/AGENTS.md`. It's `present` once it's that link.
- An existing `AGENTS.md` there, a file or a link elsewhere, is kept and `extra`, with a `gap`: Pi reads it instead until its lines move into the shared file (global-instructions.md, *Moving a harness's file*) and the user deletes it.
- An `AGENTS.override.md` in `<agent-dir>` is kept and `extra`, with a `gap`: Pi reads it instead of the link. A `CLAUDE.md` there with no `AGENTS.md` is read until the link exists; once the link is written it's `extra`, never read.
- `--no-context-files` (`-nc`) starts a session without any context file: a `gap` line.

## Memory

No memory feature: a `none` line. Pi keeps sessions in `sessions/`, which it reloads only when the user resumes one. Install no persistent-memory package or extension, since memory stays off in every harness (global-instructions.md).

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
- **Activation:** a new session reads the change. A running session reads it after `/reload`.
- **Gaps:** a trusted project's `.pi/settings.json` overrides these keys, and CLI flags such as `--model` override them for one run.

## Permissions

`gap`: Pi has no permission system. It asks for no approval before a tool call (`docs/security.md`), and has no deny, ask or allow list. No rule-table row applies to Pi, the table's or a personal one: name every row once as `gap` in Pi's section, not one line per row.

## Command rows

`gap`, as in *Permissions*.

## File rows

`gap`, as in *Permissions*.

## MCP-tool rows

`gap`, as in *Permissions*. Pi reads MCP servers from `<agent-dir>/mcp.json`.

## Personal permissions

Each personal permission is `n/a` here: "Pi has no permission entries".

## Pre-tool hook

`gap`: not wired. The way in exists: an extension in `<agent-dir>/extensions/` can register `pi.on("tool_call", …)` and return `{ block: true, reason }` to stop a call, and a handler that throws blocks the call too (`docs/extensions.md`). The adapter that would run `pre_tool_hook.py` there isn't designed yet, so write nothing and name the gap: no enforcement in Pi yet, and the rule table doesn't apply.

Other extensions in `<agent-dir>/extensions/`, such as a session host's integration, are the user's: leave them.

## Auto mode

None: Pi has no approval prompts to automate.

## Gaps

Until the adapter exists, Pi runs every tool call with the user's own permissions. The containment it has is the operating system's: a container, a virtual machine or a separate user (`docs/security.md`, `docs/containerization.md`). Name this once in every audit.

## What the agent sees

No refusal: Pi refuses nothing on the rule table's behalf. The shared file still gives the agent the rule lines and the rejection guidance, as guidance only.

## Checking it

`verify.py` prints a `pi` line for the link, one per declared default, and one per broken skill link. To see Pi read the setup, start it in a sandbox:

1. Make a sandbox folder, with a fresh agent folder in it. Copy `settings.json` and recreate the `AGENTS.md` link there. Copy no credential, trust or session file.
2. Run `PI_CODING_AGENT_DIR=<sandbox agent folder> pi` from an empty folder in the sandbox.
   - Result: the startup `[Context]` section lists the sandbox's `AGENTS.md`.
3. Quit Pi, then read the sandbox's `settings.json`.
   - Result: the declared keys hold their values, and every other key is still there.

With no login in the sandbox, Pi still starts and shows the listing. It creates its own empty `auth.json` and `sessions/` in the sandbox, and adds `lastChangelogVersion` to its `settings.json`.
