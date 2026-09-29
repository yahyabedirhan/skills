# Cursor adapter

What set-up-machine writes for Cursor, the IDE agent and the `cursor-agent` CLI, and why. The code is `scripts/setupmachine/adapters/cursor.py`. Sources: Cursor's docs on [rules](https://cursor.com/help/customization/rules.md), [CLI permissions](https://cursor.com/docs/cli/reference/permissions.md) and [hooks](https://cursor.com/docs/hooks.md), the repo's research, `docs/research/harness-capabilities.md` (section 4), and probes of `cursor-agent` 2026.09.18 and its bundle.

With no `~/.cursor` folder the adapter writes nothing and the plan says Cursor isn't set up here.

## Global instructions

- Both read **user rule files**, `~/.cursor/rules/*.mdc`: the IDE as user rules in every project, the CLI by walking up from its working folder, so only for a folder inside the home folder. The CLI has no other global file.
- An `.mdc` file reaches every chat only with `alwaysApply: true` frontmatter, and `@file` in a rule is a context reference, not an include. So the adapter writes `~/.cursor/rules/global-instructions.mdc`: that frontmatter, a generated-file comment, and a **copy** of the shared file. Each apply refreshes it; after an edit to the shared file the plan shows the copy being refreshed until the next apply.
- A `global-instructions.mdc` that set-up-machine didn't write is kept and reported as a gap. Any other `.mdc` there is `extra`: its lines belong in the shared file.
- **Gaps:** a CLI session whose working folder is outside the home folder gets no global instructions. Account User Rules (Customize > Rules) live on the Cursor account, out of the skill's reach, so lines kept there are invisible to the audit; whether CLI sessions receive them is unconfirmed, and nothing here relies on them.

## Memory

Cursor has none: Memories were removed in 2.1, and the CLI has no memory feature. The plan says `none`.

## Permissions (CLI)

- **Files:** `~/.cursor/cli-config.json`, key `permissions` with the lists `deny` and `allow`. The CLI rewrites the rest of the file itself; the adapter keeps every other key. The CLI also unions in the `allow` and `deny` lists of `~/.claude/settings.json`, which the Claude Code adapter writes in a form Cursor matches (below).
- **Matching:** a glob knows only `*`, which matches anything, `/` and spaces included; every other character is literal (no `?`, classes or `**` of its own). `Shell(<prefix>)` matches the prefix alone and anything after a space; `Shell(<prefix>:)` the prefix alone; `Shell(<cmd>:<args>)` a one-word command with arguments matching the glob. Deny wins over allow.
- **Levels:** `deny` rows go to `deny`, `allow-and-report` rows to `allow` (the hook reports). `ask` rows have no list: under the CLI's allowlist mode a command no allow entry covers prompts, but `--force`/`--yolo` runs it, so each ask row is a gap.
- **Command rows** become `Shell(<prefix>)`, one per spelling the row expands to, the same prefixes as Claude Code's: `Shell(git push --force)` refuses `git push --force origin main` but not `git push --force-with-lease`. A row with `arguments: "none"` becomes `Shell(env:)`, which leaves `env FOO=1 cmd` alone. A row with `files` (`cat` on a `.env` file) gets none: Shell rules match text, not paths, and the CLI's Read rules don't bind shell commands, so the hook alone refuses it.
- **File rows** become `Read(<glob>)` and `Write(<glob>)` over absolute paths: `**/.env`, `~/.ssh/**`. They bind the CLI's file tools only. With no classes, an `except` can't be expressed, so the CLI also refuses `.env.example`; the hook leaves it open, and the IDE with it.
- **MCP-tool rows** become `Mcp(<server>:<tool>)`, the server being its key in `~/.cursor/mcp.json`. The plan asks `cursor-agent mcp list`, then `mcp list-tools` for each server a row could match, from an empty folder.
- **Covered already:** `Shell(x)` or `Bash(x)` covers every entry starting `x `; a trailing-`*` glob every entry starting with its stem; `Bash(sudo:*)` every `sudo` entry; `Mcp(server:*)` or `Mcp(server)` that server's tools.
- **Claude Code's entries, read here:** the CLI skips `~/.claude/settings.json` unless its `permissions` has both `allow` and `deny`, so the Claude Code adapter adds an empty `allow` beside a `deny`. Its `Bash(<prefix> *)` entries match every use with something after the prefix, which is why that adapter writes ` *` rather than the equivalent `:*`: `Bash(rm -rf:*)` matches only the bare `rm -rf` here. An exact `Bash(env)` would match `env` with any arguments here, so that adapter writes none for a bare row; the `Shell(env:)` entries in `cli-config.json` cover the bare command. Its `./` Read and Edit entries never match; its plain `Write(**/…)` entries do.
- **Gap:** a project's `.cursor/cli.json` replaces the `cli-config.json` lists, so `"deny": []` there empties them. A project can only add to the Claude settings lists, and the hook, which a project can't turn off, still refuses the deny rows.
- **The IDE** reads neither file and has no user-level deny list: its hard blocks are hooks.

## Pre-tool hook

- **Wiring:** `~/.cursor/hooks.json` (`"version": 1`), one handler, `python3 <skill>/scripts/pre_tool_hook.py --harness cursor`, timeout 10 seconds, on four events: `beforeShellExecution`, `beforeMCPExecution`, `beforeReadFile`, and `preToolUse` with matcher `^(Write|Delete|Grep)$`. Each call reaches exactly one of them, so nothing is reported twice. `preToolUse` names an MCP tool `MCP:<tool>` without its server, so MCP goes through `beforeMCPExecution`. The `--config` and `--rules` arguments follow Claude Code's rules. The IDE and the CLI both read this file, and a project can't switch it off.
- **Audit:** `wired` when all four events run exactly that command. The manifest records the command; when the skill moves, the old handlers are removed. Other hooks are the user's and stay.
- **Input:** `beforeShellExecution` has `command` and `cwd` (often empty; the hook falls back to `workspace_roots[0]`); `beforeMCPExecution` has `mcp_server_name` and `tool_name`, read as `mcp__<server>__<tool>`; `beforeReadFile` has `file_path`; `preToolUse` has `tool_name` and `tool_input.file_path`. The session is `conversation_id`.
- **Answer:** always JSON. A deny is `{"permission": "deny", "user_message": …, "agent_message": …}`, both carrying the refusal: the CLI shows the agent `user_message`. Otherwise `{}`, which leaves the call to Cursor's own permissions; a hook `allow` wouldn't override a native deny or the allowlist prompt anyway. On an unreadable input or table it exits 1, and Cursor lets the call through (the hook isn't `failClosed`).
- **Claude Code's hook runs here too:** Cursor loads `~/.claude/settings.json` hooks by default (Claude's `PreToolUse` becomes `preToolUse` for every tool). That hook still refuses what it recognises, but leaves the report to this one when the payload carries `cursor_version`.
- **Gaps:** the hook's own misses (Claude Code's list); a crash or timeout lets the call through, and in the IDE nothing native is left underneath.

## What the agent sees

- A native CLI deny: `Permission denied: Command blocked by permissions configuration`, or `Write permission denied:`, naming no rule. The shared file's rule line, in the copied user rule, carries the instruction.
- A hook deny: `Rejected: Command execution was blocked by a hook: Refused by the pre-tool hook, …` with each refused part, its rule, reason and instruction. File reads and MCP calls read the same, with "File read" or "MCP tool execution".

## Checking it

Run `cursor-agent -p --trust --force` in a throwaway folder with `CURSOR_CONFIG_DIR` at a trial home's `.cursor` and `CURSOR_DATA_DIR` at a scratch folder, so no transcript lands in the real one. `CURSOR_CONFIG_DIR` moves only `cli-config.json`: user `hooks.json`, `mcp.json` and `~/.claude/settings.json` are always read from the real home, so a trial puts them in the folder instead (`.cursor/hooks.json`, `.cursor/mcp.json`, and `.claude/settings.json` at the folder's git root, or the folder itself outside a repository).

- **Commands:** `rm -rf x`, `git push --force <remote> main` and `gh repo delete owner/x` return the native refusal, once from the trial `cli-config.json` and once, with its deny list emptied, from a `.claude/settings.json` holding the Claude Code adapter's lists.
- **Hook:** with the generated `hooks.json` as the folder's `.cursor/hooks.json` and no deny list, `rm -rf x`, `bash -lc 'rm -fr x'`, a read of `.env`, and a fake stdio MCP server's `send_message` (with `--approve-mcps`) are refused by the hook, while `gh api rate_limit` runs and gets a report line.
- **Instructions:** from a folder inside the trial home, `cursor-agent -p --mode ask "Without tools: quote your rule about rm -rf and the file it came from."` quotes the rule line from `global-instructions.mdc`.
- **IDE:** after the live apply, the Customize > Hooks tab lists the four handlers, and asking the agent to run `rm -rf x` or to send a mail is refused with the hook's message.
