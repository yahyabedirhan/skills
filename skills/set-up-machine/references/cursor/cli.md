# Cursor CLI

The `cursor-agent` CLI: what only it has. The rules, hooks, plugins and skills it shares with the desktop app are in [index.md](index.md). Docs: [CLI permissions](https://cursor.com/docs/cli/reference/permissions.md), [CLI configuration](https://cursor.com/docs/cli/reference/configuration).

## Found

Found when `~/.cursor/cli-config.json` exists or `cursor-agent` is on `PATH`.

## Guardrails

### Permissions

- **Files:** `~/.cursor/cli-config.json`, key `permissions` with the lists `deny` and `allow`; add `"version": 1` to a new file. The CLI rewrites the rest of the file itself; keep every other key. It also unions in the `allow` and `deny` lists of `~/.claude/settings.json`, and **skips that file unless it has both lists**, so ../claude-code/index.md keeps an `allow` there.
- **Matching:** a glob knows only `*`, which matches anything, `/` and spaces included; every other character is literal: it has no `?`, classes or `**` of its own. `Shell(<prefix>)` matches the prefix alone and followed by a space and anything; `Shell(<prefix>:)` the prefix alone; `Shell(<cmd>:<args>)` a one-word command with arguments matching the glob. Deny wins over allow.
- **Levels:** `deny` rows go to `deny`, `allow-and-report` rows to `allow`. `ask` has no list: under the allowlist mode a command no allow entry covers prompts, but `--force`/`--yolo` runs it, and Auto-review hands it to a classifier that "is not a security boundary" ([run modes](https://cursor.com/docs/agent/security/run-modes)). So the hook refuses every ask row's call, as the item **Ask rows** below says, and each ask row is a `gap` line.
- **Command rows** become `Shell(<prefix>)`, one per spelling, as ../rule-table.md > *Spellings* describes: `Shell(rm -rf)`, `Shell(/bin/rm -rf)`, `Shell(git push --force)`, which refuses `git push --force origin main` but not `git push --force-with-lease`. `arguments: "none"` rows become `Shell(env:)`, which leaves `env FOO=1 cmd` alone. `arguments: "flags"`, `files` and `variables` rows get none: the hook alone refuses them, a `gap`.
- **File rows** become `Read(<glob>)` and `Write(<glob>)` over absolute paths: `Read(**/.env)`, `Read(**/.env.*)`, `Read(~/.ssh/**)`; a glob without `**/`, `~/` or `/` gets `**/` in front. They bind the CLI's file tools only. With only `*`, an `except` can't be expressed, so the CLI refuses `.env.example` too; the hook leaves it open, and the IDE with it. Both are `gap`s.
- **MCP-tool rows** become `Mcp(<server>:<tool>)`, the server being its key in `~/.cursor/mcp.json`. List the tools from an empty folder: `cursor-agent mcp list`, which prints a line per server, `<server>: …`, then `cursor-agent mcp list-tools <server>`, which prints a line per tool, `- <tool>`, for each server a row's `server` regex matches; strip colour codes. A listing that fails is a `gap`: keep the `Mcp(` entries already there.
- **Claude Code plugins Cursor imports:** Cursor's CLI loads every plugin `~/.claude/plugins/installed_plugins.json` lists and a `.claude/settings.json` enables; `false` there leaves it out, in Claude Code too. It names a plugin's server `plugin-<plugin>-<server>`, where Claude Code writes `plugin_<plugin>_<server>`, and `cursor-agent mcp list` doesn't show it. Take its tools from Claude Code's listing, as the item ../claude-code/index.md > *MCP-tool rows* > **List the tools** describes: each `mcp__plugin_<plugin>_<server>__<tool>` a row matches becomes `Mcp(plugin-<plugin>-<server>:<tool>)`, written only when the row's `server` regex also matches the hyphenated name, since the hook checks that name in Cursor. Cursor documents only the skills it imports ([skills](https://cursor.com/docs/skills.md)); the plugin import is in the CLI's code, behind a switch Cursor controls, so an entry for a plugin Cursor doesn't load is harmless, and its absence a `gap`.
- **Ask rows, `approver: "user"` or not:** with no ask list, and run modes that run a tool without asking, Cursor can't promise the user is asked. The hook refuses every ask row's call in Cursor, IDE and CLI alike, and the row's instruction tells the agent to stop and give the user the exact command. Claude Code, which has an ask list, still asks for the same calls.
- **Covered already:** `Shell(x)` or `Bash(x)` covers every entry starting `x `; a trailing-`*` glob covers every entry starting with its stem; `Shell(cmd:*)` covers a one-word command's every use; `Mcp(server:*)` or `Mcp(server)` that server's tools.
- **Gap:** a project's `.cursor/cli.json` replaces these lists, so `"deny": []` there empties them. A project can only add to the Claude settings lists, and the hook still refuses the deny rows.
- **The IDE** reads neither file and has no user-level deny list: its hard blocks are hooks.

### Personal permissions

A personal permission, as the section ../workstation.md > `setup/permissions.json` defines it, becomes CLI entries the way a table row of its kind does above, each marked `personal`; an `allow` row goes to `allow`, as an `allow-and-report` row does, and the hook refuses an `ask` row's calls, as it does a table row's.

- **Its tool exists** for a command row when one of its programs is on `PATH`, for a file row always, and for an MCP-tool row when `cursor-agent mcp list-tools` lists a tool it matches, which becomes `Mcp(<server>:<tool>)`; otherwise the row is `n/a` here.
- **Covered already:** the CLI unions the Claude Code lists, so a personal entry written to `~/.claude/settings.json` that covers this one makes it `present, personal`.
- **It can't loosen a table row:** deny wins over allow.
- **The IDE** has no allow list: an `allow` row is a `gap` there, left to the IDE's own approval settings.

## Sandbox

Auto-review with the sandbox on is the mode this skill sets for anyone who has Cursor. Allowlisted calls run. Other shell commands run in the sandbox when they can. A call that cannot use the sandbox goes to the classifier. The deny list still refuses: Auto-review does not replace it.

- **Files:** the same `~/.cursor/cli-config.json`. Set `approvalMode` to `auto-review`, and `sandbox` > `mode` to `enabled`. Keep every other key, including `sandbox` > `networkAccess` when it is already set. Add `"version": 1` to a new file. Docs: [run modes](https://cursor.com/docs/agent/security/run-modes), [CLI configuration](https://cursor.com/docs/cli/reference/configuration).
- **Audit:** the verifier's `sandbox` cell, as *Checking it* describes.
- **Linux:** the sandbox needs kernel 6.2 or newer with Landlock, and unprivileged user namespaces. On a remote machine or the standalone CLI, the user installs the AppArmor package the run-modes doc names; it needs root. When the sandbox cannot be created, Cursor asks before each command: a `gap`.
- **Steering:** leave `~/.cursor/permissions.json` `autoRun` to the user. `block_instructions` steer the classifier in plain English. The rule table and the hook are the enforcement, and a second prose list of the same calls would drift from them.

## Config

When `setup/harnesses.json` names a Cursor `config`, as ../workstation.md > *A declared config* describes, merge each key it sets, such as `hasChangedDefaultModel`, `model` and `selectedModel`, into `~/.cursor/cli-config.json`, the file that holds the CLI's permissions and run mode too. Write each declared key whole, keep every other key, and add `"version": 1` to a new file. Mark each key `present, personal` or `updated, personal`.

- **Drift:** the CLI rewrites these keys itself when the user picks another model in it, so the `config` cell then fails. Ask the user whether to change the declared file or the machine; don't overwrite the choice silently.
- **Activation:** a new `cursor-agent` session reads it. The IDE keeps its own model choice, which this file doesn't set.

## Checking it

The verifier's `Cursor / cli` row (`--harness cursor --env cli`), from `scripts/setupmachine/harnesses/cursor/cli.py`. Its declared config is the file `setup/harnesses.json` > `harnesses` > `cursor` > `environments` > `cli` > `config` names. The instructions, plugins and skills cells are the shared ones, as index.md > *Checking it* describes.

- **guardrails:** the shared hook check, and each personal deny or allow row has its entry in `cli-config.json` or in Claude Code's lists, which the CLI unions.
- **sandbox:** `cli-config.json` has `approvalMode` `auto-review` and `sandbox.mode` `enabled`.
- **config:** each key the declared Cursor config sets has the same value in `cli-config.json`; a nested object, such as `selectedModel`, must match as a whole. `n/a` without a declared config.

To see Cursor itself enforce the rows, run `cursor-agent -p --trust --force` in a throwaway folder, with `CURSOR_CONFIG_DIR` at a trial `.cursor` and `CURSOR_DATA_DIR` at a scratch folder. `CURSOR_CONFIG_DIR` moves only `cli-config.json`: `hooks.json`, `mcp.json` and `~/.claude/settings.json` are always read from the real home, so a trial puts them in the folder: `.cursor/hooks.json`, `.cursor/mcp.json`, and `.claude/settings.json` at the folder's git root.

- `rm -rf x`, `git push --force <remote> main` and `gh repo delete owner/x` return the native refusal, once from the trial `cli-config.json` and once, with its deny list emptied, from a `.claude/settings.json` holding the Claude Code lists.
- With `approvalMode` `auto-review`, the key `sandbox` > `mode` at `enabled` and without `--force`, those three commands return the same native refusal. `--auto-review` and `--sandbox enabled` set that mode for one run. Run that check, and every other Cursor CLI step here, as `cursor-agent`.
- With the hooks as `.cursor/hooks.json`, `git clean -f -n` and `git push --force-with-lease` are refused by the hook, naming rules `git-clean-force` and `git-push-force-with-lease`.
- With the hooks as `.cursor/hooks.json` and no deny list, `rm -rf x`, `bash -lc 'rm -fr x'`, a read of `.env` and a fake stdio MCP server's `send_message`, run with `--approve-mcps`, are refused by the hook; `gh api rate_limit` runs and gets a report line.
- From a folder inside the trial home, `cursor-agent -p --mode ask "Without tools: quote your rule about rm -rf and the file it came from."` quotes the `rm -rf` fallback.
- `cursor-agent mcp list` doesn't show the plugin servers Cursor imports from Claude Code. To see them, ask a live session to list the MCP servers it can call, as step 7 of ../live-check.md > *3. Send the probe* does.
