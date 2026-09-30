# What each harness can and can't do: Claude Code, Codex, opencode, Cursor

Facts for [Settle what each harness can and can't do (#50)](https://github.com/yahyabedirhan/skills/issues/50), under [Spec: every harness and project is set up and audited from the skills (#49)](https://github.com/yahyabedirhan/skills/issues/49). The harness adapters in set-up-machine and set-up-project are built on this page. Researched 2026-09-29.

Whether each harness's auto mode can act as a semantic guard for rules patterns can't express is on a sibling page, [Can auto mode block what rules can't?](auto-mode-semantic-guard.md).

Versions checked: Claude Code 2.1.284, codex-cli 0.157.1, opencode 1.18.33, cursor-agent 2026.09.18-9a7762b.

Evidence tags:

- **[doc]** the harness's official documentation, linked per section.
- **[src]** the harness's official source: `openai/codex` at commit `0462dcc`, `anomalyco/opencode` (formerly `sst/opencode`) branch `dev` at commit `7945de2`.
- **[bin]** the installed release, read-only: the Claude Code binary, or the `cursor-agent` JavaScript bundle (`index.js` and its chunks).
- **[check]** a read-only command run for this research against a throwaway config in a scratch folder, never a real one: `codex execpolicy check`, `codex features list`, `codex debug prompt-input`, `opencode debug config` and `opencode debug agent`, and a copy of Cursor's matcher functions run under the bundled Node.
- **[probe]** a real session run against a throwaway config in a scratch folder, with fake data, by the harness's adapter ticket (opencode: `opencode run --format json`, the tool result read from its JSON events).
- **To confirm** says what is still open and the exact check that would settle it.

Main sources:

- Claude Code: [permissions](https://code.claude.com/docs/en/permissions), [memory](https://code.claude.com/docs/en/memory), [hooks](https://code.claude.com/docs/en/hooks), [settings](https://code.claude.com/docs/en/settings), [settings reference](https://code.claude.com/docs/en/settings-reference), [environment variables](https://code.claude.com/docs/en/env-vars), [errors](https://code.claude.com/docs/en/errors).
- Codex: [rules](https://learn.chatgpt.com/docs/agent-configuration/rules), [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [config reference](https://learn.chatgpt.com/docs/config-file/config-reference), [permissions](https://learn.chatgpt.com/docs/permissions), [hooks](https://learn.chatgpt.com/docs/hooks), [memories](https://learn.chatgpt.com/docs/customization/memories), [managed configuration](https://learn.chatgpt.com/docs/enterprise/managed-configuration). (`developers.openai.com/codex/...` redirects to these.) Source: `codex-rs/execpolicy/README.md`, `codex-rs/core/src/exec_policy.rs`, `codex-rs/core/src/agents_md.rs`, `codex-rs/shell-command/src/bash.rs`, `codex-rs/shell-command/src/command_safety/is_dangerous_command.rs`.
- opencode: [rules](https://opencode.ai/docs/rules/), [permissions](https://opencode.ai/docs/permissions/), [config](https://opencode.ai/docs/config/), [plugins](https://opencode.ai/docs/plugins/), [MCP servers](https://opencode.ai/docs/mcp-servers/). Source: `packages/opencode/src/permission/index.ts`, `packages/opencode/src/util/wildcard.ts`, `packages/opencode/src/tool/shell.ts`, `packages/opencode/src/tool/read.ts`, `packages/opencode/src/tool/external-directory.ts`, `packages/opencode/src/session/instruction.ts`, `packages/opencode/src/session/tools.ts`, `packages/opencode/src/plugin/index.ts`, `packages/opencode/src/config/config.ts`, `packages/core/src/v1/permission.ts`.
- Cursor: [CLI usage](https://cursor.com/docs/cli/using.md), [CLI permissions](https://cursor.com/docs/cli/reference/permissions.md), [CLI configuration](https://cursor.com/docs/cli/reference/configuration.md), [rules](https://cursor.com/docs/rules.md), [rules help](https://cursor.com/help/customization/rules.md), [hooks](https://cursor.com/docs/hooks.md), [third-party hooks](https://cursor.com/docs/reference/third-party-hooks.md), [run modes](https://cursor.com/docs/agent/security/run-modes.md), [IDE permissions](https://cursor.com/docs/reference/permissions.md), [sandbox](https://cursor.com/docs/reference/sandbox.md), [ignore files](https://cursor.com/help/customization/ignore-files.md).

---

## 1. Claude Code (CLI)

### 1.1 Global instructions

- **Global file:** `~/.claude/CLAUDE.md`, plus `~/.claude/rules/*.md`, plus a managed `CLAUDE.md` when one exists. [doc memory]
- **No global `AGENTS.md`.** Claude Code reads `AGENTS.md` (since v2.1.277) only as a project file, and by default only when no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` sits in the working directory or above. `~/.claude/CLAUDE.md` doesn't count for that check. The `pluginConfigs["agents-md@builtin"].options.instructionFiles` user setting changes this (`claude-md-or-agents-md` by default, `claude-md-and-agents-md`, `claude-md`, `managed-only`). [doc memory, "When Claude Code reads AGENTS.md"]
- **Imports:** `@path/to/file` anywhere outside code spans and fenced blocks; relative to the importing file, absolute, or `~/`; at most 4 hops. Imports in user-scope files load without a dialog. [doc memory, "Import additional files"]
- **Symlinks:** supported (the docs show `ln -s AGENTS.md CLAUDE.md`, and symlinks in `.claude/rules/`). Edit and Write refuse to write through a symlink. [doc memory]
- **Precedence:** every file is concatenated, none overrides another. Order is managed, user, then project from the root down. On a conflict "Claude may follow either one". [doc memory]

### 1.2 Project instructions

- `./CLAUDE.md` or `./.claude/CLAUDE.md`, `./CLAUDE.local.md`, `.claude/rules/**/*.md` (path-scoped with `paths:` frontmatter). Ancestors load at launch; subdirectories load when Claude reads a file there. `AGENTS.md` follows the rule in 1.1. `AGENTS.local.md`, `AGENTS.override.md` and `.agents/` aren't read. [doc memory]

### 1.3 Permission files, format and levels

- **Global:** `~/.claude/settings.json`, key `permissions.{allow, ask, deny}`. Three levels. [doc settings, permissions]
- **Project:** `.claude/settings.json` (shared) and `.claude/settings.local.json` (personal). Project `allow` rules apply only after the workspace-trust dialog. [doc permissions, "Project allow rules and workspace trust"]
- **Evaluation:** deny, then ask, then allow; the first match wins and specificity doesn't matter. An allow can't carve an exception out of a deny. [doc permissions, "Manage permissions"]

### 1.4 How commands are matched

- `Bash(...)` matches the whole command text with a glob `*` that can span spaces. `Bash(x:*)` equals `Bash(x *)`. Everything before the first `*` must match as written, so matching isn't argument-aware: `Bash(rm -rf:*)` misses `rm -fr`, `rm -Rf`, `rm -f -r` and `rm --recursive --force`. [doc permissions, "Wildcard patterns"]
- Commands are split on `&&`, `||`, `;`, `|`, `|&`, `&` and newlines. Deny and ask rules apply when any subcommand matches, including one nested in a subshell, a command substitution or a control-flow body. [doc permissions, "Compound commands"]
- Wrappers `timeout`, `time`, `nice`, `nohup`, `stdbuf`, `command`, `builtin`, `noglob` and bare `xargs` are stripped before matching; a deny also matches past a leading `VAR=value`. [doc permissions, "Wrappers"]
- Not matched: a program by absolute path (`/bin/rm`), and the script inside `bash -c '…'`. The docs say a Bash deny "isn't a security boundary around the program". A separate `Bash(bash -c:*)` rule blocks `bash -c` itself, but not `bash -lc`, `zsh -c` or `/bin/bash -c`. [doc permissions, "What a Bash rule doesn't match"]
- A built-in set of read-only commands (`ls`, `cat`, `grep`, `find`, …) runs without a prompt; deny rules still apply to them. [doc permissions, "Read-only commands"]

### 1.5 Can a project override the global rules?

- **Permissions: no.** "If a tool is denied at any level, no other level can allow it … a user-level deny blocks a project-level allow." [doc permissions, "Settings precedence"]
- **Hooks: yes, all at once.** A project's `.claude/settings.json` can set `"disableAllHooks": true`, which turns off user, project, local and plugin hooks (not managed ones). A project's `"disableAllHooks": false` also overrides a user `true`. Only managed settings can disable managed hooks. There's no way to disable one hook and keep the rest. [doc hooks, "Disable or remove hooks"; doc settings-reference, `disableAllHooks`]
- **Memory: yes.** `autoMemoryEnabled` is read from any settings file, and project settings outrank user settings, so a project can turn it back on. The environment variable `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` outranks the key "for one session, in either direction". [doc settings-reference, `autoMemoryEnabled`; doc env-vars]
- **What holds against a project:** managed settings, `managed-settings.json` in `/Library/Application Support/ClaudeCode/` (macOS) or `/etc/claude-code/` (Linux), a system directory that needs admin rights to write. [doc settings; doc [managed-settings](https://code.claude.com/docs/en/managed-settings)]

### 1.6 File, MCP and network rules

- **Files:** `Read(path)` and `Edit(path)` with gitignore-style paths (`//abs`, `~/home`, `/relative-to-settings-file`, `./cwd`). A Read deny also blocks Edit and Write on that path. They apply to the built-in file tools, recognised Bash file commands (`cat`, `head`, `tail`, `sed`, `tee`) and redirect targets, and they follow symlinks. [doc permissions, "Read and Edit", "Symlinks"]
- **`Write(path)` rules are never consulted.** "If you write a path rule for `Write`, `NotebookEdit`, `Glob`, or the legacy `MultiEdit` tool instead, Claude Code accepts the rule but never consults it, and warns at startup." Use `Edit(path)`. [doc permissions, "Read and Edit"]
- Reads by arbitrary subprocesses (a Python script) aren't covered unless the OS sandbox is on; the sandbox applies to Bash, PowerShell and Monitor. [doc permissions; doc sandboxing]
- **MCP:** `mcp__<server>__<tool>`, `mcp__<server>` or `mcp__<server>__*`. Deny and ask rules accept tool-name globs that must match the full name (`mcp__*`). Tools from claude.ai connectors that Claude Code fetches itself appear as `mcp__claude_ai_<server>__<tool>`, so a rule must use that name in the CLI; a rule naming the server any other way matches nothing there. Settings files skip any `mcp__` rule with parentheses, so MCP arguments can't be matched. [doc permissions, "MCP", "Tool name wildcards"]
- **Network:** `WebFetch(domain:host)` with wildcards; the sandbox has its own network allowlist. [doc permissions]

### 1.7 Hooks

- `PreToolUse` runs before every tool call and can block it: exit code 2 (stderr is the reason), or JSON `hookSpecificOutput.permissionDecision: "deny"` with `permissionDecisionReason`. Exit code 1 is a non-blocking error. `permissionDecision` also takes `allow`, `ask` and `defer`. [doc hooks, "Exit code 2", "PreToolUse decision control"]
- Hooks live under `hooks` in any settings file; entries from user, project and local settings are merged, not replaced. [doc hooks]

### 1.8 Memory

- **Auto memory** is on by default and stores notes in `~/.claude/projects/<project>/memory/`.
- Turn it off with `"autoMemoryEnabled": false` in `~/.claude/settings.json` (the `/memory` toggle writes this key), or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` in the environment. When off, Claude doesn't read or write the memory directory. [doc memory, "Enable or disable auto memory"; doc settings-reference]
- Subagents can keep their own memory through the subagent `memory` field. [doc memory]

### 1.9 What the agent sees when refused

- A Bash deny rule returns `Permission to use Bash with command <command> has been denied.`. The rule isn't named; in the compound path `<command>` is the refused subcommand in some branches and the full command in others. [bin: message templates in the 2.1.284 binary]
- An Edit or Write on a Read-denied path returns "File is covered by a Read deny rule in your permission settings and cannot be edited." [doc errors]
- A `PreToolUse` hook's deny reason is shown to Claude. (For `ask`, the reason goes to the user only.) [doc hooks, PreToolUse decision control table]

---

## 2. OpenAI Codex (CLI)

### 2.1 Global instructions

- **Global file:** `$CODEX_HOME/AGENTS.override.md` if non-empty, else `$CODEX_HOME/AGENTS.md` (`CODEX_HOME` defaults to `~/.codex`). [doc agents-md]
- **`CLAUDE.md` isn't read** unless listed in `project_doc_fallback_filenames`, which applies per project directory. [doc agents-md] [check: a project `CLAUDE.md` didn't reach the prompt without the fallback]
- **Symlinks work.** A `CODEX_HOME/AGENTS.md` symlinked to a shared file reached the model prompt. [check: `codex debug prompt-input`]
- **No imports.** A line `@imported.md` in the global file reached the prompt as literal text; the imported file's content didn't. [check: `codex debug prompt-input`]
- **Precedence:** global first, then project files from root to working directory, joined by blank lines; later files win by appearing later. Cap `project_doc_max_bytes` (32 KiB). [doc agents-md]

### 2.2 Project instructions

- From the project root (found by `project_root_markers`, default `.git`) down to the working directory, one file per directory: `AGENTS.override.md`, else `AGENTS.md`, else a fallback name. It never walks above the project root. [src core/src/agents_md.rs module doc]
- **A project marked `trust_level = "untrusted"` loses its `AGENTS.md` too,** not only its `.codex/` config. With no trust entry at all, `AGENTS.md` loads but `.codex/config.toml` doesn't. [check: `codex debug prompt-input` with trusted, untrusted and absent entries]

### 2.3 Permission files, format and levels

- **Command rules:** Starlark `.rules` files, `~/.codex/rules/*.rules` globally and `<repo>/.codex/rules/*.rules` per project, each holding `prefix_rule(pattern=[...], decision=..., justification=..., match=..., not_match=...)`. [doc rules; src execpolicy/README.md]
- **Levels:** `allow` (runs outside the sandbox without a prompt), `prompt`, `forbidden`. The most restrictive matching decision wins. [doc rules]
- **Other config:** `~/.codex/config.toml` for `approval_policy`, `sandbox_mode`, permission profiles, MCP and features. [doc config-reference]
- **Admin layer:** `/etc/codex/requirements.toml` (Unix) constrains security-sensitive settings, can pin `[features]`, can add `[rules]` (`prompt` or `forbidden` only) and managed `[hooks]`. Users and projects can't override it. [doc managed-configuration]

### 2.4 How commands are matched

- Token-exact prefix over the argv. Any pattern element can be a list of alternatives. No globs or regex. [src execpolicy/README.md]
- **Absolute paths are resolved.** The harness evaluates with `resolve_host_executables: true`, so `/bin/rm -rf x` falls back to an `rm` rule (restricted to listed paths when a `host_executable()` entry exists). `codex execpolicy check` does this only with `--resolve-host-executables`. [src core/src/exec_policy.rs; src execpolicy/README.md] [check: `/bin/rm -rf x` is `forbidden` with the flag, no match without it]
- **Shell wrappers:** `bash -c`/`-lc` and the `sh` and `zsh` forms are parsed with tree-sitter. A plain linear chain (`&&`, `||`, `;`, `|` of plain words) is split and each part evaluated. Scripts with redirection, `$(…)`, `VAR=`, globs or control flow aren't split; they're evaluated as the single argv `["bash","-lc","<script>"]`. [doc rules; src core/src/exec_policy.rs, shell-command/src/bash.rs]
- **Built-in danger check:** any `rm` with a force flag (`-f` inside any short-flag group, or `--force`, anywhere) and `sudo`/`env` in front of one count as dangerous. An unmatched dangerous command prompts, or is forbidden under `approval_policy = never`. [src is_dangerous_command.rs, exec_policy.rs]
- Probes against a throwaway rules file [check: `codex execpolicy check`]:

  | Rule | Command | Result |
  |---|---|---|
  | `["rm", ["-rf","-fr","-Rf","-rF","-fR","-RF"]]` forbidden, with justification | `rm -fr x` | forbidden, justification returned |
  | same | `rm --recursive --force x` | no match |
  | `["rm","-r","-f"]` forbidden | `rm -f -r x` | no match |
  | `["bash","-c"]` forbidden | `bash -c "rm -rf x"` | forbidden |
  | `["gh","repo","edit"]` prompt | `gh repo edit --visibility public` | prompt |

### 2.5 Can a project override the global rules?

- **Rules: no.** All layers' rules merge and the strictest decision wins. [doc rules; src exec_policy.rs]
- **Config: yes, for a trusted project.** A trusted project's `.codex/config.toml` can set `sandbox_mode`, `approval_policy` and `[features]`; only provider, auth, notification, profile and telemetry keys are ignored there. [doc config-reference, config.toml section]
- **Hooks: yes, all at once.** Hooks from every layer run, and "higher-precedence config layers don't replace lower-precedence hooks", but a trusted project's `[features] hooks = false` turns every hook off, the user's included. [doc hooks] [check: `codex features list` shows `hooks false` in a trusted project that sets it, `true` in an untrusted one]
- **Memory: yes.** A trusted project's `[features] memories = true` turns memories on over a user `false`. [check: `codex features list`]
- **What holds against a project:** `requirements.toml`: pin `[features] hooks = true` and `memories = false`, define managed hooks, or set `allow_managed_hooks_only`. [doc hooks, "Managed hooks from requirements.toml"; doc managed-configuration]

### 2.6 File, MCP and network rules

- **No per-tool file rules.** Codex reads through the shell and writes through the shell and `apply_patch`. [doc rules]
- **Sandbox:** `sandbox_mode = read-only | workspace-write | danger-full-access`, `sandbox_workspace_write.writable_roots` and `.network_access`. [doc config-reference]
- **Permission profiles (beta):** `[permissions.<name>.filesystem]` maps a path or glob to `read`, `write` or `deny`; a deny covers reads and writes (`"**/*.env" = "deny"`, `~/path`, `:workspace_roots`). `[permissions.<name>.network.domains]` needs the network proxy. They bind sandboxed commands; a command a rule `allow`s runs outside the sandbox. [doc permissions; doc rules]
- **MCP:** `mcp_servers.<id>.enabled_tools` / `disabled_tools`, and `approval_mode` per server or per tool. Hooks see MCP tools as `mcp__<server>__<tool>`. [doc config-reference; doc hooks, "Matcher patterns"]

### 2.7 Hooks

- **Codex has a pre-tool hook.** `hooks.json` or inline `[hooks]` in `config.toml`, at `~/.codex/` and `<repo>/.codex/`; the `hooks` feature is stable and on by default. [doc hooks] [check: `codex features list`]
- **Shape:** event → matcher group (regex on the tool name) → handlers (`type = "command"` or `mcp_tool`). `PreToolUse` covers shell (`Bash`), unified exec (`Bash`), `apply_patch` (matchable as `apply_patch`, `Edit` or `Write`), MCP tools and other local function tools; hosted tools such as web search aren't covered. Input on stdin carries `tool_name`, `tool_use_id`, `tool_input` (`tool_input.command` for Bash and `apply_patch`). [doc hooks, "PreToolUse", "Tool coverage"]
- **Blocking:** `hookSpecificOutput.permissionDecision: "deny"` with `permissionDecisionReason`, the older `{"decision": "block", "reason": …}`, or exit code 2 with the reason on stderr. `allow` with `updatedInput` rewrites the call. `ask` is parsed but not supported yet: the hook run is marked failed and the tool call continues. [doc hooks, "PreToolUse"]
- **Trust:** non-managed hooks must be reviewed and trusted in `/hooks` before they run; trust is recorded against the hook's hash, so a changed hook is skipped until trusted again. `--dangerously-bypass-hook-trust` skips this for one run. [doc hooks, "Review and trust hooks"]
- Matching hooks from all files run, concurrently; one hook can't stop another from starting. The docs call tool hooks "a useful guardrail, not a complete enforcement boundary". [doc hooks]

### 2.8 Memory

- **Local memories exist and are off by default:** `[features] memories = true` turns them on; files live in `~/.codex/memories/`. Finer keys: `memories.generate_memories`, `memories.use_memories`, `memories.disable_on_external_context`. `/memories` controls one chat. [doc memories; doc config-reference] [check: `codex features list` shows `memories stable false` with an empty config]
- To keep it off: `[features] memories = false` in `~/.codex/config.toml`, and pin it in `requirements.toml` if a project mustn't turn it on (2.5).

### 2.9 What the agent sees when refused

- `` `<command>` rejected: <justification> `` when the matched `forbidden` rule has a justification; otherwise `` `<command>` rejected: policy forbids commands starting with `<prefix>` `` (the longest matching forbidden prefix). [src core/src/exec_policy.rs `derive_forbidden_reason`]
- A hook deny passes its reason to the model. [doc hooks]

---

## 3. opencode

### 3.1 Global instructions

- **Global file:** the first that exists of `~/.config/opencode/AGENTS.md` and `~/.claude/CLAUDE.md`. `OPENCODE_DISABLE_CLAUDE_CODE_PROMPT=1` (or `OPENCODE_DISABLE_CLAUDE_CODE=1`) drops the Claude fallback. [doc rules; src session/instruction.ts `globalFiles`]
- **No imports.** "opencode doesn't automatically parse file references in AGENTS.md"; files are read as plain text, so `@AGENTS.md` inside a `CLAUDE.md` isn't expanded. Use `"instructions": ["path", "glob/*.md", "https://…"]` in `opencode.json`. [doc rules; src session/instruction.ts]
- **Symlinks work:** files are checked with an exists call and read with a plain file read, both of which follow symlinks. [src session/instruction.ts]

### 3.2 Project instructions

- Upward search from the working directory to the worktree root for `AGENTS.md`, else `CLAUDE.md` ("if you have both … only AGENTS.md is used"); every match of the winning name between the two is loaded. [doc rules; src session/instruction.ts `systemPaths`]
- **Nested files load on demand:** when the agent reads a file, `AGENTS.md`/`CLAUDE.md` files in the directories between it and the project root are attached once per message. [src session/instruction.ts `resolve`]
- `OPENCODE_DISABLE_PROJECT_CONFIG` turns off project instructions as well as project config. [src session/instruction.ts, config/config.ts]
- Some models get a system prompt telling them to keep a memory file in the repo (`.github/instructions/memory.instruction.md`): model IDs containing `gpt-4`, `o1` or `o3`. [src session/system.ts, session/prompt/beast.txt]

### 3.3 Permission files, format and levels

- **File:** `~/.config/opencode/opencode.json(c)` globally, `opencode.json` and `.opencode/` per project; key `permission`, levels `allow`, `ask`, `deny`. [doc permissions, config]
- **Keys:** `read`, `edit` (edit, write and patch), `glob`, `grep`, `bash`, `task`, `skill`, `lsp`, `question`, `webfetch`, `websearch`, `external_directory`, `doom_loop`, plus tool names including MCP tools. [doc permissions]
- **Defaults:** most are `allow`; `external_directory` and `doom_loop` are `ask`; `read` has `*.env` and `*.env.*` at `ask` and `*.env.example` at `allow`. [doc permissions; check: `opencode debug agent build` lists them at those levels, where the docs say deny]

### 3.4 How commands are matched

- **Last matching rule wins.** `*` matches anything (spaces and `/` included), `?` one character; patterns compile to anchored regexes, and a trailing `" *"` also matches the bare command. The ruleset is flattened in config order and evaluated with `findLast`. [doc permissions; src util/wildcard.ts, permission/index.ts]
- **Every command node is checked:** the command is parsed with tree-sitter-bash, and each `command` node (inside `&&` chains, pipes, `$(…)`, subshells) is matched separately by its source text. The string inside `bash -c "…"` isn't re-parsed, so only a rule on `bash -c*` itself catches it. [src tool/shell.ts]
- A `"rm -rf*": "deny"` rule therefore misses `rm -fr`, `rm -r -f` and `/bin/rm -rf`; it catches `a && rm -rf x`. [src, from the matching rules above; probe: `"rm -rf *": "deny"` refuses `echo a && rm -rf x`, and nothing in the call runs]
- **Declarations aren't checked:** `export -p` runs under `"export -p *": "deny"`; tree-sitter-bash parses `export`, `declare` and `typeset` as declarations, not `command` nodes. [probe]
- **Global config files:** `config.json`, `opencode.json` and `opencode.jsonc` in the global folder all load, in that order. [check: the log's `loading path=` lines]

### 3.5 Can a project override the global rules?

- **Permissions: yes.** Config sources merge ("later configs override earlier ones only for conflicting keys", project over global); only managed config holds. [doc config]
  - A project that sets an existing pattern key changes its level in place. A project key that's new is appended after the global keys and, by last-match-wins, beats them. [check: `opencode debug agent build` shows global `"git push --force*": "deny"` followed by the project's `"git push*": "allow"`, and a project's `"rm -rf*": "allow"` replacing the global deny]
  - A project's `"*": "allow"` keeps the position of the global `"*"` key, so it doesn't defeat global rules listed after it. [check: same]
  - Agent definitions can override permissions too ("agent rules take precedence"). [doc permissions]
- **Hooks (plugins): yes, in effect.** Global and project plugins all load (global config, project config, global plugin folder, project plugin folder, in that order) and all hooks run in sequence; plugin arrays concatenate, so a project can't remove a global plugin by config. But a project plugin runs after the global one and can rewrite `output.args` after the global check has passed. [doc plugins, "Load order"; src plugin/index.ts `trigger`, config/config.ts `mergeConfigConcatArrays`] `--pure` / `OPENCODE_PURE` runs without external plugins, the global plugin folder's files included. [src; probe: with `--pure`, a command the global plugin refuses runs]
- **What holds against a project:** managed config (`/Library/Application Support/opencode/` on macOS, or MDM). [doc config]

### 3.6 File, MCP and network rules

- `read` and `edit` patterns match the path relative to the worktree, so `"secrets/*": "deny"` works but `~/.ssh/*` in `read` doesn't. [src tool/read.ts, tool/edit.ts]
- Paths outside the worktree go through `external_directory`, matched as `<absolute dir>/*`; `{"~/.ssh/*": "deny"}` blocks the file tools and bash commands whose file arguments point there. [src tool/external-directory.ts; doc permissions]
- `read` rules don't apply to `cat .env` in bash: bash checks only the command text and external directories. [src tool/shell.ts]
- **No OS sandbox** for bash; the source has none. [src tool/shell.ts]
- **MCP:** tools are named `<server>_<tool>`: `"myserver_*": "deny"`. [doc mcp-servers]
- **Network:** `webfetch` (URL patterns) and `websearch`. [doc permissions]

### 3.7 Hooks

- **The pre-tool hook is a plugin hook, `tool.execute.before`,** signature `(input: {tool, sessionID, callID}, output: {args})`. It runs for built-in tools and MCP tools, before the permission check. [src packages/plugin/src/index.ts, session/tools.ts]
- **It can block:** a thrown error stops the call. The docs' `.env`-protection example throws `new Error("Do not read .env files")`. It can also rewrite `output.args`. [doc plugins, ".env protection"; src session/tools.ts; probe: a global plugin that throws refuses `rm -rf x`, and `x` stays]
- MCP tools don't appear in `opencode debug agent` or the server's `/experimental/tool/ids` list, even with the server connected; only a session lists them. [probe]
- Plugins are JavaScript or TypeScript files in `~/.config/opencode/plugins/` or `.opencode/plugins/`, or npm packages in `plugin`. [doc plugins]
- A `permission.ask` hook is declared in the plugin types but nothing in the opencode package triggers it. [src packages/plugin/src/index.ts; no trigger in packages/opencode/src]

### 3.8 Memory

- **No memory feature.** Nothing in the source stores or loads memories between sessions; the only "memory" is the model prompt in 3.2 that asks certain models to keep a file in the repo. Nothing to turn off. [src: no memory store in packages/opencode/src]

### 3.9 What the agent sees when refused

- A deny rule: "The user has specified a rule which prevents you from using this specific tool call. Here are some of the relevant rules <JSON of the ruleset for that permission>". The agent sees the rules, not which subcommand or rule matched. [src packages/core/src/v1/permission.ts]
- A user rejection: "The user rejected permission to use this specific tool call." (plus the feedback, if any). [src same file] `opencode run` has no one to ask, so it auto-rejects an `ask` rule with this message and prints `permission requested: bash (<command>); auto-rejecting` on stderr. [probe]
- A plugin throw: the tool part is marked as an error whose text is the error's message, unwrapped and with its line breaks, and that is the tool result the model reads. [probe: a plugin throwing `new Error("…line one.\nLine two…")` on `echo BLOCKME`; the tool part's `state.error` and the model's quote of its tool result both hold exactly the two lines]
- `opencode run` takes the session's folder from `PWD`, not the process's working directory. [probe]

---

## 4. Cursor (`cursor-agent` CLI and the Cursor IDE agent)

### 4.1 Global instructions

- **CLI: no dedicated global file; it walks up the directory tree.** From the working directory up to the filesystem root, in every directory, the CLI loads `.cursor/rules/**/*.mdc`, `AGENTS.md`, and `CLAUDE.md` and `CLAUDE.local.md`. A project under the home folder therefore gets `~/.cursor/rules/*.mdc`, `~/AGENTS.md` and `~/CLAUDE.md`. `AGENTS.md`/`CLAUDE.md` load as always-applied; `.mdc` files follow their frontmatter. `~/.claude/CLAUDE.md` isn't read (it isn't in an ancestor directory). [bin: `LocalCursorRulesService.loadRulesFromDirAndAncestors`]
- The CLAUDE files are gated by a "third-party extensibility" switch, hard-wired on in the CLI. [bin: the rules service is constructed with `()=>!0`]
- The CLI's `/rule` command offers "User Rule — Applies to all your projects" and writes it to `~/.cursor/rules/<name>.mdc`. [bin]
- **Account User Rules** (Settings, synced with the account) are documented for the IDE's Agent. The CLI bundle has no code that fetches them. Still unconfirmed whether Cursor's server adds them to CLI sessions (check: add a User Rule with a marker word in the IDE, then ask `cursor-agent` to repeat its instructions). Moot for set-up-machine, which reaches both through `~/.cursor/rules/` instead (#57); a `.mdc` file there with `alwaysApply: true` reached a CLI session under the home folder [check].
- **IDE:** account User Rules and local user rule files in `~/.cursor/rules`; conflicts resolve Team, then Project, then User. [doc rules help]
- **Imports:** `@file` in a rule is a context reference, not an include. [doc rules]
- **Symlinks:** rule folders are walked with `followSymlinks: true`; `AGENTS.md`/`CLAUDE.md` are read with a plain stat and read. [bin]

### 4.2 Project instructions

- `.cursor/rules/**/*.mdc` (frontmatter `alwaysApply`, `globs`, `description`; a plain `.md` there is ignored), nested `AGENTS.md` ("combined with parent directories, with more specific instructions taking precedence"), `CLAUDE.md`, and the deprecated `.cursorrules` at the git root. [doc rules; bin]

### 4.3 Permission files, format and levels

**CLI**

- **Files:** `~/.cursor/cli-config.json` and `<project>/.cursor/cli.json`, key `permissions.{allow, deny}`. Under `approvalMode: "allowlist"` anything not allowed prompts, so the levels are allow, prompt and deny. [doc cli configuration, permissions]
- **Also read: Claude Code's settings.** The CLI loads `permissions` from `<git root>/.claude/settings.json` and `~/.claude/settings.json` and unions their `allow` and `deny` lists with its own. A file whose `permissions` lacks either list fails the CLI's schema and is skipped whole. [bin: `cli/willLoadClaudePermissions`, `MergedPermissionsProvider`, the `cursor-config` schema; check: a project `.claude/settings.json` with only `deny` refused nothing, with both lists it refused]
- **Tokens:** `Shell(cmd)` or `Shell(cmd:argsGlob)` (and `Bash(…)`, parsed the same way), `Read(glob)`, `Write(glob)`, `WebFetch(domain)`, `Mcp(server:tool)`. Deny beats allow. [doc cli permissions; bin: the token parser matches `^(Shell|Bash)\(`]
- `--force` / `--yolo` runs every command "unless explicitly denied": deny still applies, prompts don't. [bin: `cursor-agent --help`]
- File-deletion protection defaults to on in the CLI bundle: while it's on, a command containing `rm` isn't auto-run from the allowlist. [bin: the default team-settings stub returns `true` from `getDeleteFileProtection`, and the auto-run check returns false when any parsed command is `rm`]

**IDE**

- No user-level command deny file. `~/.cursor/permissions.json` holds `terminalAllowlist`, `mcpAllowlist` and `autoRun.{allow_instructions, block_instructions}`; the instructions steer the Auto-review classifier and are "steering, not enforcement". [doc IDE permissions]
- Run modes Auto-review, Allowlist and Run Everything; allowlists are "not a security boundary". File-Deletion, External-File and Browser protections are toggles. [doc run-modes]
- A hard command denylist exists only as a team-admin setting. [bin: `adminCommandDenylist`]

### 4.4 How commands are matched (CLI)

- The command is parsed into its executable commands; a deny applies when any of them matches. [bin: `hasHardDeny`]
- `Shell(x)` matches the base command or the whole text as a glob; `Shell(cmd:args)` globs the command part and the text after the first space. The glob `ut` escapes every character but `*`, which becomes `.*`: it spans spaces and `/`, and there are no `?`, classes or `**` of its own; path rules use the same function. `Shell(x:)` (empty argument pattern) matches `x` with nothing after it only. [bin: `matchesShell`, glob `ut`, `matchesPathEntry`; check: a deny of `Shell(pwd:)` refused `pwd` and ran `pwd -P`; `Write(**/.env.[0-9A-Za-z]*)` didn't refuse `.env.local`]
- Probes, running the bundle's own matcher functions [check: copied `Pd`, `ut`, `matchesShell` run under the bundled Node]:

  | Rule | Matches | Misses |
  |---|---|---|
  | `Shell(rm)` | every `rm`, any flags | `/bin/rm …` |
  | `Shell(rm:-rf*)` | `rm -rf x` | `rm -fr x`, `rm -r -f x` |
  | `Shell(git:push --force*)` | `git push --force`, `git push --force origin main` | `git push origin main --force` |
  | `Bash(rm -rf:*)` (Claude form) | only the bare `rm -rf` | `rm -rf x` |
  | `Bash(git push --force:*)` | only the bare `git push --force` | `git push --force origin main` |
  | `Bash(gh repo delete*)`, `Bash(sudo:*)` | `gh repo delete foo`, `sudo ls` | — |
  | `Bash(bash -c:*)` | nothing | `bash -c "rm -rf x"` |

  So Claude-form rules whose command part has a space (`Bash(rm -rf:*)`) are read but only match the bare command, while one-word ones (`Bash(sudo:*)`) and colon-free globs work.
- `bash -c "…"`: not unwrapped. With `Shell(rm)` denied, `rm victim` was refused but `bash -c 'rm victim'` and `sh -c "rm victim"` ran. [check]

### 4.5 Can a project override the global rules?

- **CLI permissions: partly.** `.cursor/cli.json` files from the git root down to the working directory are deep-merged into the user config, and arrays are replaced, so a project's `"permissions": {"deny": []}` empties the `cli-config.json` deny list. The Claude settings deny lists are unioned separately (4.3), so rules in `~/.claude/settings.json` survive, and a project `.claude/settings.json` can only add. A hidden `--disable-project-configs` flag skips project files. [bin: the `cli.json` loader and its merge function; `MergedPermissionsProvider`]
- **Hooks: no.** "All matching hooks from every source run", and a `deny` from any source wins. [doc hooks, "Configuration"] Project hooks run only in trusted workspaces. [doc hooks]
- **IDE:** `permissions.json` per-repo arrays are concatenated with per-user ones; `sandbox.json` denies are unioned and `default: "deny"` wins. [doc IDE permissions, sandbox]

### 4.6 File, MCP and network rules

- **CLI:** `Read(glob)` and `Write(glob)` are checked by the file tools only, against the resolved absolute path (`~` expanded). A relative pattern such as Claude's `Read(./.env)` never matches an absolute path; `Read(**/.env)` and `Read(~/.ssh/**)` do. Shell commands such as `cat .env` aren't checked against them. [bin: `shouldBlockReadInternal`, `shouldBlockWrite`, `matchesPathEntry`]
- **CLI MCP:** `Mcp(server:tool)` deny is checked first for every MCP call; the server is its key in `mcp.json`. [bin: `shouldBlockMcp`, "BLOCKED (explicitly denied)"] Claude's `mcp__…` rule strings aren't in this format and are ignored.
- **CLI network:** `WebFetch(domain)` for the fetch tool. [doc cli permissions]
- **IDE:** `.cursorignore`/`.gitignore` hide files (`.env` by default), but "Terminal commands and MCP tools run outside of Cursor's file access controls". `sandbox.json` has no read-deny paths, and "SSL certificate paths and `~/.ssh` are always readable". [doc ignore-files, sandbox]

### 4.7 Hooks

- **Files:** `~/.cursor/hooks.json` (user), `<project>/.cursor/hooks.json` (project), enterprise and team sources, and Claude Code's hooks from `~/.claude/settings.json`, `.claude/settings.json` and `.claude/settings.local.json` when "Include Third-Party Plugins, Skills, and Other Configs" is on (the default). The CLI loads all of these paths. [doc hooks, third-party hooks; bin: hooks loader in chunk `190.index.js`]
- **Pre-tool events:** `preToolUse` (every tool: Shell, Read, Write, MCP, Task), `beforeShellExecution`, `beforeMCPExecution`, `beforeReadFile`. [doc hooks]
- **Blocking:** exit code 2, or JSON `permission: "deny"` with `user_message` and `agent_message`. For permission hooks, invalid JSON blocks; crashes, timeouts and other exit codes fail open unless the hook sets `failClosed: true`. `ask` is accepted by the schema but not enforced for `preToolUse`. [doc hooks]
- **Claude-format output is mapped:** `permissionDecision` → `permission`, `permissionDecisionReason` → `user_message` (not `agent_message`), `updatedInput` → `updated_input`; Claude tool names map `Bash` → `Shell`, `Edit` → `Write`. [doc third-party hooks; bin: the name map]

### 4.8 Memory

- **No memory feature in the local IDE or CLI.** Cursor staff: "The Memories feature was intentionally removed starting from version 2.1.x" (with an "Export memories" command to move them into rules). [[Cursor forum, staff reply, 2025-11-25](https://forum.cursor.com/t/are-my-memories-gone/144057)] The CLI bundle only carries a `memory_enabled` field on cloud automations. [bin] Nothing to turn off.

### 4.9 What the agent sees when refused

- **CLI deny rule:** `permissionDenied` with "Command blocked by permissions configuration", or `rejected` with "Command is not allowed". No rule or subcommand named. [bin]
- **Team admin denylist:** "Denied: this command was blocked by administrator policy (denylist rule: <pattern>) and was not executed…". [bin]
- **Hook deny:** in the CLI the agent sees `user_message`, as `Rejected: Command execution was blocked by a hook: <user_message>` ("File read was blocked by a hook" for reads), and not `agent_message`; a Claude-format hook's reason becomes `user_message`, so it reaches the agent there. [check] The IDE is unchecked.

---

## 5. Comparison

| | Claude Code | Codex | opencode | Cursor CLI |
|---|---|---|---|---|
| Global instructions | `~/.claude/CLAUDE.md`, `@` imports | `~/.codex/AGENTS.md`, symlink OK, no imports | `~/.config/opencode/AGENTS.md`, else `~/.claude/CLAUDE.md`; no imports | none as such; ancestors' `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/*.mdc` up to `/` |
| Permission file | `settings.json` | `rules/*.rules` + `config.toml` | `opencode.json` | `cli-config.json` + `.claude/settings.json` |
| Levels | allow / ask / deny | allow / prompt / forbidden | allow / ask / deny | allow / (prompt) / deny |
| Matching | text glob, literal prefix | argv prefix, alternatives, abs paths resolved | text glob per command node, last match wins | base command or `cmd:args` glob |
| `rm -fr` caught by an `rm -rf` rule | no | only with an alternatives list | no | only with `Shell(rm)` |
| `/bin/rm -rf` | no | yes | no | no |
| `bash -c "rm -rf x"` | only by a `bash -c` rule | yes if plain; no with `$()`, redirects | only by a `bash -c*` rule | no (checked) |
| Project loosens a global deny | no | no (rules); yes (sandbox, approvals) | yes | yes for `cli-config.json`; no for Claude-settings denies |
| Project turns hooks off | yes (`disableAllHooks`) | yes (`features.hooks = false`, trusted) | yes in effect (a later plugin rewrites args) | no |
| Pre-tool hook | `PreToolUse` | `PreToolUse` | plugin `tool.execute.before` (throw) | `preToolUse`, `beforeShellExecution`, … |
| Memory | auto memory, on by default | local memories, off by default | none | none (removed in 2.1) |
| Turn memory off | `autoMemoryEnabled: false` or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` | `[features] memories = false` | — | — |
| Agent sees on deny | command, no rule | prefix or justification | the ruleset | generic message |
| Hardening against a project | managed settings | `requirements.toml` | managed config | union via `~/.claude/settings.json` |

---

## 6. Gaps: the current deny rules each harness can't express

The rule table starts from the current Claude Code deny list (spec #49). Its rules, in groups:

1. `rm -rf` and variants (`Bash(rm -rf:*)`, `Bash(rm -r -f:*)`, `Bash(rm --no-preserve-root:*)`)
2. `dd`, `mkfs`, `chmod -R 777`
3. `git push --force`, `git push --force-with-lease` (becomes ask), `git reset --hard`
4. `gh repo delete|edit|archive|unarchive|rename|deploy-key|autolink`, `gh ssh-key`, `gh gpg-key`
5. `sudo`, `su`
6. `bash -c`, `sh -c`
7. Reads of `.env`, `.env.*`, `secrets/**`, `~/.ssh/**`, `~/.aws/**`
8. Writes of `.env`, `.env.local`, `secrets/**`
9. The mail connector's send, reply, forward, trash, mark-spam and sensitive-label tools
10. The mail CLI's `spark event` and `spark comment`

A gap is a rule the harness's native permissions can't enforce as meant. The basic hook (spec #49) can cover a gap only where the harness has a pre-tool hook that a project can't switch off; that's noted per harness.

### Claude Code

- **`rm -rf` variants:** flag order (`rm -fr`, `rm -Rf`, `rm -f -r`, `rm --recursive --force`), `/bin/rm`, and `rm` inside `bash -lc`, `zsh -c`, `/bin/bash -c`. Each spelling needs its own rule, and absolute paths and shell strings can't be matched at all. (1.4)
- **Flags after arguments:** `git push origin main --force`, `git -C dir push --force`, `git reset HEAD~1 --hard`, `chmod 777 -R`. A mid-pattern glob (`Bash(git push *--force*)`) catches some, with over-match risk. (1.4)
- **`sudo`/`su` by absolute path** (`/usr/bin/sudo`). (1.4)
- **`bash -c`/`sh -c`:** only those exact prefixes; `bash -lc`, `zsh -c` and absolute-path shells need their own rules or aren't matchable. (1.4)
- **Reads by other programs:** the Read rules bind the file tools and recognised Bash file commands, not a script's own reads, unless the sandbox is on. (1.6)
- **Writes:** `Write(...)` rules are ignored; they must be written as `Edit(...)`. Expressible, but the current three rules do nothing. (1.6)
- **Mail tools:** expressible, but only by the name the session exposes (`mcp__claude_ai_<server>__<tool>` for connectors in the CLI); a rule naming the server another way matches nothing. A glob such as `mcp__*__send_message` should cover every naming, since deny rules take tool-name globs; **to confirm** by adding it through `--settings` in a throwaway session and checking the tool is gone from `/permissions`. (1.6)
- **Hook cover:** `PreToolUse` closes the command gaps, but a project's `disableAllHooks: true` turns it off, unless it's installed as a managed hook. (1.5)

### Codex

- **`rm -rf` variants:** combined flags are expressible as alternatives (`-rf`, `-fr`, `-Rf`, …); separated or long flags (`rm -f -r`, `rm -r x -f`, `rm --recursive --force`) are prefixes only in their exact order. The built-in danger check prompts for any forced `rm`, but doesn't forbid it. (2.4)
- **Flags after arguments:** `git push origin main --force`, `git -C dir push --force`, `chmod 777 -R`: prefix rules can't reach them. (2.4)
- **Shell strings that aren't plain** (`bash -lc 'x=$(…); rm -rf y'`): evaluated whole, so inner rules don't apply. A `["bash","-lc"]` forbidden rule would catch them, but it isn't usable: Codex's own shell tool sends every command as `[<user shell>, "-lc", <command>]` (`-c` when the model passes `login: false` or `allow_login_shell = false`; the model may also pick the shell), so the rule refuses Codex's own wrapper around any non-plain command, and a `["zsh","-c"]` rule does the same with login off. [src core/src/shell.rs `derive_exec_args`, core/src/tools/handlers/unified_exec.rs `get_command`] [check: a real `codex exec` session reported `` `/bin/zsh -lc 'rm -fr x'` rejected: … ``; `codex execpolicy check -- /bin/zsh -c "ls > out"` against `["zsh","-c"]` is `forbidden`] (2.4)
- **Reads and writes of `.env`, `secrets/`, `~/.ssh`, `~/.aws`:** no per-tool file rule. A permission-profile `filesystem` deny (beta) binds sandboxed commands only; a command a rule allows runs outside the sandbox. **To confirm** whether `apply_patch` honours a profile deny. (2.6)
- **Mail tools:** only if the same server is configured in Codex (`disabled_tools`); claude.ai connectors aren't Codex MCP servers. A `PreToolUse` hook matching `mcp__<server>__<tool>` covers it once the server exists. (2.6, 2.7)
- **Hook and memory cover:** `PreToolUse` closes the command gaps, but a trusted project can set `hooks = false` or `memories = true` unless `requirements.toml` pins them, and each hook must be trusted in `/hooks` before it runs. Trust is `[hooks.state."<hooks.json path>:<event>:<group>:<handler>"] trusted_hash` in `config.toml`: sha256 over the canonical JSON (sorted keys, no spaces) of `{event_name, matcher, hooks: [handler]}`, the handler normalised with `type`, `command`, `timeout`, `async`. [src hooks/src/engine/discovery.rs `hook_hash`, config/src/fingerprint.rs] [check: the app-server's `hooks/list` reports the computed hash as `currentHash`, and a hook with that entry as `trusted`] (2.5, 2.7)

### opencode

- **`rm -rf` variants:** every spelling needs its own pattern (`rm -fr*`, `rm -r -f*`, `/bin/rm*`); order-insensitive flags can only be approximated with broad globs (`rm *-r*`) that over-match. (3.4)
- **`bash -c` inner commands:** not parsed; only `bash -c*` itself can be denied. (3.4)
- **Reads through bash:** `read` rules and the default `.env` deny bind the read tool, not `cat .env`; bash rules on text (`"cat *.env*"`) are a partial cover. `~/.ssh` and `~/.aws` need `external_directory`, which still misses programs that read them on their own. (3.6)
- **Writes through bash:** `edit` rules bind the edit tools, not `echo … > .env`. (3.6)
- **Mail tools:** only if the server is configured in opencode (`<server>_<tool>`). (3.6)
- **Precedence gap:** any global rule can be loosened by a project's `opencode.json`, except through managed config. (3.5)
- **Hook cover:** `tool.execute.before` can block every command gap, but a project plugin runs later and can rewrite the arguments. (3.5, 3.7)

### Cursor CLI

- **`rm -rf` variants:** only `Shell(rm)`, which blocks every `rm`, catches all flag orders; `/bin/rm` isn't caught by it. The Claude-form rules it reads from `~/.claude/settings.json` (`Bash(rm -rf:*)`, `Bash(git push --force:*)`) match only the bare command. (4.4)
- **Flags after arguments:** `Shell(git:push *--force*)` style globs reach them, with over-match risk. (4.4)
- **`bash -c` inner commands:** not unwrapped (checked, 4.4); `Shell(bash)` blocks all of `bash`.
- **Reads and writes:** `Read(...)`/`Write(...)` bind the file tools only, not shell commands. Claude's relative `./.env` patterns never match; they must be written `**/.env`. (4.6)
- **Mail tools:** only if the server is in Cursor's `mcp.json` (`Mcp(server:tool)`). (4.6)
- **Precedence gap:** a project `cli.json` can empty the `cli-config.json` deny list; rules kept in `~/.claude/settings.json` survive. (4.5)
- **Hook cover:** hooks can't be turned off by a project; `beforeShellExecution` with `failClosed: true` closes the command gaps. A hook wired only in Claude Code's settings also runs here, and its reason goes to `user_message`. (4.5, 4.7)

### Cursor IDE

- **Every command rule:** no user-level hard deny outside hooks; `block_instructions` are advisory and File-Deletion Protection only prompts. A `beforeShellExecution` hook or a team admin denylist are the hard options. (4.3)
- **`~/.ssh` reads:** can't be denied; the sandbox always allows them and `.cursorignore` doesn't bind the terminal or MCP. (4.6)
- **Other reads and writes:** `.cursorignore` binds the agent's file tools only. (4.6)
- **Mail tools:** allowlist only; a hard deny needs a `beforeMCPExecution` hook. (4.3, 4.7)

---

## 7. The ticket's open points, answered

| Open point | Answer |
|---|---|
| Which global rules the Cursor CLI reads | No single global file: it loads `.cursor/rules/**/*.mdc`, `AGENTS.md`, `CLAUDE.md` and `CLAUDE.local.md` from every directory from the working directory up to `/`, so `~/.cursor/rules/*.mdc` and `~/AGENTS.md` apply to projects under the home folder. Account User Rules: unconfirmed, and not relied on (4.1). |
| Claude Code memory setting | `"autoMemoryEnabled": false`, or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, which outranks settings (1.8). |
| Codex, opencode, Cursor memory | Codex: local memories, off by default, `[features] memories = false` (2.8). opencode: none (3.8). Cursor: removed in 2.1 (4.8). |
| Codex pre-tool hook | Yes: `PreToolUse` in `hooks.json` or `[hooks]`, deny by JSON or exit 2, hooks trusted per hash (2.7). |
| opencode pre-tool hook | Plugin `tool.execute.before`; it blocks by throwing and can rewrite arguments (3.7). |
| Can a project turn off a global hook | Claude Code: yes, all hooks (`disableAllHooks`). Codex: yes, all hooks (`features.hooks = false`, trusted project). opencode: no config switch, but a project plugin can undo the global one's effect. Cursor: no. Each has a managed layer that holds (1.5, 2.5, 3.5, 4.5). |

## 8. Corrections to the first pass

- Codex resolves absolute program paths in the harness (`/bin/rm -rf` matches `rm` rules); the first pass read only the `check` CLI's default. (2.4)
- Codex skips a project's `AGENTS.md` too when the project is explicitly untrusted. (2.2)
- In opencode, a project's `"*": "allow"` doesn't override global rules listed after `"*"`; new project keys do. (3.5)
- The Cursor CLI reads and unions Claude Code's permission lists and hooks, and accepts `Bash(...)` tokens. (4.3, 4.7)
- The Cursor CLI reads project `cli.json` files from the git root down, not from every ancestor. (4.5)
